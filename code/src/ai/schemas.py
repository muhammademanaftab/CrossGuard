"""Shape of one AI fix suggestion that flows from the AI service to the UI."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AIFixSuggestion:
    feature_id: str
    feature_name: str
    suggestion: str
    code_example: str
    browsers_affected: List[str] = field(default_factory=list)
