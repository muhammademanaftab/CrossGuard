# CLI AI-gating flags + key management

## Problem

Today, `crossguard analyze` automatically calls the paid AI API whenever any key is
available (via `--api-key`, `CROSSGUARD_AI_KEY` env var, or the `ai_api_key` saved
in SQLite). The user has no per-run opt-out. This is a surprise-billing risk and a
UX mismatch with the GUI, which requires an explicit "Get AI Suggestions" button
click every time.

## Goal

Make AI suggestions an **explicit opt-in** on the CLI, and give the CLI a clean way
to save / clear / inspect the API key and provider.

## Non-goals

- No changes to the GUI.
- No changes to the `AIFixService` backend logic.
- No config-file layout changes.

## Design

### 1. New `--ai` flag on `analyze`

Strict opt-in. If `--ai` is not passed, the AI path is skipped regardless of any
saved key / env var / inline `--api-key`.

```
crossguard analyze style.css                      # no AI
crossguard analyze style.css --ai                 # AI, uses saved key / env
crossguard analyze style.css --ai --api-key sk-   # AI, inline key override
```

If `--ai` is passed and no key is resolvable from any source, the CLI prints a
warning and skips AI. The analysis itself still completes.

### 2. New flags on `config`

| Flag | Effect |
|---|---|
| `--set-api-key VALUE` | Save key directly to SQLite settings (`ai_api_key`). |
| `--set-api-key` (no value) | Interactive hidden-input prompt, then save. |
| `--set-ai-provider {anthropic,openai}` | Save provider to SQLite settings. |
| `--clear-api-key` | Delete `ai_api_key` from SQLite settings. |

Default `crossguard config` (no flags) additionally shows the saved key as
`sk-...XXXX` (masked) and the saved provider.

### 3. Storage

SQLite `settings` table, using the existing `service.set_setting()` /
`get_setting()` API. Keys: `ai_api_key`, `ai_provider`. Shared with the GUI — a
user who saves the key via CLI sees it in the GUI Settings page and vice versa.

### 4. Backend (no changes)

`service.get_ai_fix_suggestions()` already reads from SQLite when no inline
`api_key` is passed and returns `[]` on missing key. The gate lives purely in the
CLI layer: skip the call unless `--ai` is set.

## Tests

Add 5 black-box tests in `tests/cli/`:

1. `test_analyze_without_ai_flag_skips_ai` — env var set, no `--ai` → no call.
2. `test_analyze_with_ai_flag_runs_ai` — `--ai` passed → service called.
3. `test_analyze_ai_flag_no_key_warns` — `--ai` without any key → warning printed.
4. `test_config_set_api_key_direct` — `config --set-api-key sk-X` saves it.
5. `test_config_clear_api_key` — `config --clear-api-key` removes it.

Expected test total after: 111 → 116.

## Docs

- `user.tex` §AI Fix Suggestions (CLI): document `--ai` requirement and the new
  `config` flags. (Prepared in `thesis_doc_updates.md`, not auto-edited.)
- `impl.tex`: bump test count 111 → 116; one-line note that AI is gated on
  `--ai`.

## Out-of-scope / known limitations

- Env var `CROSSGUARD_AI_KEY` will continue to be read as a key source when
  `--ai` is passed, but no longer implies "run AI automatically" — this is the
  behavior change users relying on env-var-only-automation need to be aware of.
