"""Generates AI-powered fix suggestions using LLM APIs."""

import json
from typing import Dict, List, Set, Optional

import requests

from .schemas import AIFixSuggestion
from src.utils.feature_names import get_feature_name
from src.utils.config import get_logger

logger = get_logger('ai.service')


class AIFixService:
    """Calls an LLM API to suggest code fixes for unsupported browser features."""

    ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
    OPENAI_URL = "https://api.openai.com/v1/chat/completions"

    DEFAULT_MODELS = {
        "anthropic": "claude-sonnet-4-20250514",
        "openai": "gpt-4o-mini",
    }

    def __init__(self, api_key: str = None, provider: str = "anthropic",
                 model: str = None, max_features: int = 10, priority: str = "unsupported_first"):
        self._api_key = api_key or ""
        self._provider = provider
        self._model = model  # None means fall back to DEFAULT_MODELS for the provider
        self._max_features = max_features  # 0 = no limit
        self._priority = priority  # "unsupported_first" or "all_equal"

    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_fix_suggestions(
        self,
        unsupported_features: Set[str],
        partial_features: Set[str],
        file_type: str,
        browsers: Dict[str, str],
    ) -> List[AIFixSuggestion]:
        if not self.is_available():
            return []

        all_features = unsupported_features | partial_features
        if not all_features:
            return []

        if self._priority == "unsupported_first":
            ordered = sorted(unsupported_features) + sorted(partial_features - unsupported_features)
        else:
            ordered = sorted(all_features)

        limited = ordered[:self._max_features] if self._max_features > 0 else ordered

        feature_list = []
        for fid in limited:
            name = get_feature_name(fid)
            status = "unsupported" if fid in unsupported_features else "partial"
            affected = [f"{b} {v}" for b, v in browsers.items()]
            feature_list.append({
                "id": fid,
                "name": name,
                "status": status,
                "browsers": affected,
            })

        prompt = self._build_prompt(feature_list, file_type)

        try:
            raw = self._call_api(prompt)
            return self._parse_response(raw, feature_list)
        except Exception as e:
            logger.error(f"AI fix suggestion failed: {e}")
            return []

    def _build_prompt(self, features: List[Dict], file_type: str) -> str:
        lines = []
        for f in features:
            browsers_str = ", ".join(f["browsers"])
            lines.append(f'- {f["name"]} ({f["id"]}): {f["status"]} in {browsers_str}')

        feature_block = "\n".join(lines)

        return f"""You are a web compatibility expert. The following {file_type.upper()} features have browser support issues.

For each feature, suggest a specific code fix or fallback using widely supported alternatives.

Features:
{feature_block}

Respond ONLY with a JSON array. Each item must have:
- "feature_id": the Can I Use feature ID
- "suggestion": a brief description of the fix (1-2 sentences)
- "code_example": a short code snippet showing the fix

Example response format:
[
  {{
    "feature_id": "css-container-queries",
    "suggestion": "Use media queries with min-width as a fallback for container queries.",
    "code_example": "@media (min-width: 400px) {{ .card {{ display: flex; }} }}"
  }}
]"""

    def _call_api(self, prompt: str) -> str:
        if self._provider == "anthropic":
            return self._call_anthropic(prompt)
        elif self._provider == "openai":
            return self._call_openai(prompt)
        else:
            raise ValueError(f"Unknown AI provider: {self._provider}")

    def _call_anthropic(self, prompt: str) -> str:
        model = self._model or self.DEFAULT_MODELS["anthropic"]
        resp = requests.post(
            self.ANTHROPIC_URL,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]

    def _call_openai(self, prompt: str) -> str:
        model = self._model or self.DEFAULT_MODELS["openai"]
        resp = requests.post(
            self.OPENAI_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2048,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _parse_response(
        self, raw: str, features: List[Dict]
    ) -> List[AIFixSuggestion]:
        text = raw.strip()
        if text.startswith("```"):
            # LLMs often wrap the response in markdown code fences
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        items = json.loads(text)
        if not isinstance(items, list):
            return []

        feature_map = {f["id"]: f for f in features}

        suggestions = []
        for item in items:
            fid = item.get("feature_id", "")
            if fid not in feature_map:
                continue

            info = feature_map[fid]
            suggestions.append(AIFixSuggestion(
                feature_id=fid,
                feature_name=info["name"],
                suggestion=item.get("suggestion", ""),
                code_example=item.get("code_example", ""),
                browsers_affected=info["browsers"],
            ))

        return suggestions
