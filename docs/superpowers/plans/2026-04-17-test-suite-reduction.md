# Test Suite Reduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the test suite from 281 tests to ~112 tests while preserving the black-box / white-box / integration three-tier structure, per `docs/superpowers/specs/2026-04-17-test-suite-reduction-design.md`.

**Architecture:** One task per module. Each task collects the current test list, applies the survival rules from the design spec, deletes non-surviving tests by editing the relevant `test_*.py` file, verifies the module still passes, and commits. CSS goes first as a pilot to validate the approach. A final task cleans up orphaned fixtures and verifies the global counts.

**Tech Stack:** Python 3.9+, pytest with markers (`blackbox`, `whitebox`, `integration`), git for per-module commits. No production code changes; `src/` is untouched.

---

## Ground Rules (Apply to Every Task)

- **No production code changes.** Only files under `tests/` are edited.
- **Keep the file structure.** Do not rename, move, or create test files. Only delete test functions/classes inside existing files.
- **Keep markers intact.** `@pytest.mark.blackbox/whitebox/integration` decorators stay on surviving tests.
- **Keep fixtures defined inline** in the same file unless they are in `conftest.py`. A final sweep removes orphaned conftest fixtures.
- **After every module cut:** run the module's tests (must pass), then run the full suite (must pass), then commit.
- **Commit style:** `test(<module>): reduce to <N> tests` (matches the existing repo commit style of short subject lines).
- **If a cut breaks a passing test:** stop, diagnose, and either reinstate the test or fix the fixture.

---

### Task 0: Baseline measurement

**Files:**
- Create: (none)
- Modify: (none)
- Test: (none)

- [ ] **Step 1: Record current test totals**

Run:
```bash
cd /Users/home/Documents/Educational/Thesis/Project
source .venv/bin/activate
pytest tests/ --collect-only -q 2>&1 | tail -1
pytest tests/ -m blackbox --collect-only -q 2>&1 | tail -1
pytest tests/ -m whitebox --collect-only -q 2>&1 | tail -1
pytest tests/ -m integration --collect-only -q 2>&1 | tail -1
```

Expected output (baseline):
```
281 tests collected
134/281 tests collected
89/281 tests collected
58/281 tests collected
```

- [ ] **Step 2: Confirm working tree is clean except for known non-test changes**

Run: `git status --short`

Expected: no modifications under `tests/` and no untracked files under `tests/`. The pre-existing `data/caniuse` submodule change is unrelated to this work and stays untouched.

- [ ] **Step 3: No commit** (measurement only)

---

### Task 1: CSS parser — 39 → 14 (pilot)

**Files:**
- Modify: `tests/parsers/css/test_css_blackbox.py`
- Modify: `tests/parsers/css/test_css_whitebox.py`
- Modify: `tests/parsers/css/test_css_integration.py`

**Selection:** From the existing 39 CSS tests, keep exactly these 14. Delete every other test function in these three files.

Keep (blackbox, 6):
- `TestFeatureDetection::test_feature_detected[css-grid]`
- `TestFeatureDetection::test_feature_detected[flexbox]`
- `TestFeatureDetection::test_feature_detected[container-queries]`
- `TestFeatureDetection::test_feature_detected[css-variables]`
- `TestCombinedFeatures::test_flex_and_gap_both_detected`
- `TestMalformedCSS::test_missing_closing_brace`

Keep (whitebox, 5):
- `TestBlockBoundaryPreservation::test_flex_and_gap_same_block`
- `TestBlockBoundaryPreservation::test_flex_and_gap_different_blocks`
- `TestPatternPrecision::test_transform_property_triggers_2d_for_3d_value`
- `TestCSSCustomDetection::test_custom_property_detected`
- `TestCSSCustomDetection::test_custom_rule_merged_with_builtin`

Keep (integration, 3):
- `TestParseFile::test_parse_valid_file`
- `TestRealWorldScenarios::test_modern_css_reset`
- `TestRealWorldScenarios::test_flexbox_card_layout`

- [ ] **Step 1: Edit `test_css_blackbox.py`**

Using the Edit tool, delete:
- All rows of the `test_feature_detected` parametrize decorator EXCEPT `css-grid`, `flexbox`, `container-queries`, `css-variables` (trim the `@pytest.mark.parametrize` list to these 4 rows).
- The entire `TestEmptyInput` class.
- The `TestMalformedCSS::test_unclosed_string` method.
- The entire `TestValidateCSS` class.

Leave: `TestFeatureDetection` (with the 4-row parametrize), `TestCombinedFeatures::test_flex_and_gap_both_detected`, `TestMalformedCSS::test_missing_closing_brace`.

- [ ] **Step 2: Edit `test_css_whitebox.py`**

Delete:
- Entire `TestStateReset` class.
- `TestBlockBoundaryPreservation::test_grid_gap_not_detected_as_flexbox_gap`.
- Entire `TestUnrecognizedPatterns` class.
- Entire `TestWoffPatternOverlap` class.
- `TestPatternPrecision::test_filter_triggers_both_features`.
- `TestPatternPrecision::test_transition_all_does_not_trigger_css_all`.
- `TestCSSCustomDetection::test_custom_rule_not_triggered_on_unrelated_css`.
- `TestCSSCustomDetection::test_empty_custom_rules_no_effect`.
- Entire `TestCSSCustomReport` class.

- [ ] **Step 3: Edit `test_css_integration.py`**

Delete:
- `TestParseFile::test_file_not_found_raises`.
- Entire `TestParseMultipleFiles` class.
- Entire `TestGetStatistics` class.
- Entire `TestDetailedReport` class.
- `TestRealWorldScenarios::test_dark_mode_support`.

- [ ] **Step 4: Run CSS module tests**

Run: `pytest tests/parsers/css -v`

Expected: `14 passed` (6 blackbox + 5 whitebox + 3 integration).

- [ ] **Step 5: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `256 passed` (281 − 25).

- [ ] **Step 6: Commit**

```bash
git add tests/parsers/css/
git commit -m "test(css): reduce to 14 tests

Drop parametrize variants and redundant whitebox cases per
docs/superpowers/specs/2026-04-17-test-suite-reduction-design.md."
```

---

### Task 2: HTML parser — 45 → 14

**Files:**
- Modify: `tests/parsers/html/test_html_blackbox.py`
- Modify: `tests/parsers/html/test_html_whitebox.py`
- Modify: `tests/parsers/html/test_html_integration.py`

**Selection criterion:** Keep 7 blackbox, 4 whitebox, 3 integration. See spec §"What Survives — HTML parser".

- [ ] **Step 1: List current HTML tests**

Run: `pytest tests/parsers/html --collect-only -q`

Record the full list so you can mark each as keep/cut.

- [ ] **Step 2: Decide which tests to keep**

Apply the spec's HTML survival list. Target retained behaviors:
- Blackbox (7): semantic element detection (one test, not a whole parametrize block of elements), a single input-type mapping (not eight), attribute detection (e.g. `hidden` or `draggable`), custom attribute value, custom-rule merge, `validate()` hook, full-page scan.
- Whitebox (4): DOM traversal state reset, attribute-value lookup internals, custom-rule dict merge, parser `_init_features` internals.
- Integration (3): file I/O parse, real-world page sample, detailed-report generation.

Where a parametrize block exists, trim it to 1–2 representative rows rather than deleting the function outright.

- [ ] **Step 3: Edit blackbox file**

Use Edit to delete non-surviving test functions and trim parametrize decorators to 1 row each (pick one representative value per block). Do not edit fixture helpers that surviving tests use.

- [ ] **Step 4: Edit whitebox file**

Use Edit to delete non-surviving tests. Leave the 4 retained ones.

- [ ] **Step 5: Edit integration file**

Use Edit to delete non-surviving tests. Leave the 3 retained ones.

- [ ] **Step 6: Run HTML module tests**

Run: `pytest tests/parsers/html -v`

Expected: `14 passed` (with marker split 7 / 4 / 3).

- [ ] **Step 7: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `225 passed` (256 − 31).

- [ ] **Step 8: Commit**

```bash
git add tests/parsers/html/
git commit -m "test(html): reduce to 14 tests"
```

---

### Task 3: JS parser — 40 → 14

**Files:**
- Modify: `tests/parsers/js/test_js_blackbox.py`
- Modify: `tests/parsers/js/test_js_whitebox.py`
- Modify: `tests/parsers/js/test_js_integration.py`

**Selection criterion:** Keep 6 blackbox, 5 whitebox, 3 integration. See spec §"What Survives — JS parser".

- [ ] **Step 1: List current JS tests**

Run: `pytest tests/parsers/js --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Apply the spec's JS survival list:
- Blackbox (6): optional chaining `?.`, nullish coalescing `??`, private fields `#x`, promise method → parent feature (e.g. `.then` → `promises`), directive detection (`"use strict"`), template literal `${}` handling.
- Whitebox (5): tree-sitter AST comment/string cleaning, AST node-type detection, regex-on-cleaned-text pass, custom-rule merge, React-component false-positive filter.
- Integration (3): end-to-end single file parse, mixed-feature source parse, real-world script sample.

- [ ] **Step 3: Edit blackbox file**

Delete all non-surviving tests. Trim parametrize blocks to 1 row each.

- [ ] **Step 4: Edit whitebox file**

Delete all non-surviving tests.

- [ ] **Step 5: Edit integration file**

Delete all non-surviving tests.

- [ ] **Step 6: Run JS module tests**

Run: `pytest tests/parsers/js -v`

Expected: `14 passed` (6 / 5 / 3).

- [ ] **Step 7: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `199 passed` (225 − 26).

- [ ] **Step 8: Commit**

```bash
git add tests/parsers/js/
git commit -m "test(js): reduce to 14 tests"
```

---

### Task 4: Custom rules — 9 → 5

**Files:**
- Modify: `tests/parsers/custom_rules/test_custom_rules_blackbox.py`
- Modify: `tests/parsers/custom_rules/test_custom_rules_whitebox.py`

**Selection criterion:** Keep 3 blackbox, 2 whitebox.

- [ ] **Step 1: List current tests**

Run: `pytest tests/parsers/custom_rules --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors:
- Blackbox (3): load rules from JSON, CSS/JS custom rule applied in parser output, HTML custom element/attribute mapping applied.
- Whitebox (2): singleton loader returns same instance, save+reload round-trip preserves data.

- [ ] **Step 3: Edit blackbox file**

Delete non-surviving tests.

- [ ] **Step 4: Edit whitebox file**

Delete non-surviving tests.

- [ ] **Step 5: Run module tests**

Run: `pytest tests/parsers/custom_rules -v`

Expected: `5 passed`.

- [ ] **Step 6: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `195 passed` (199 − 4).

- [ ] **Step 7: Commit**

```bash
git add tests/parsers/custom_rules/
git commit -m "test(custom_rules): reduce to 5 tests"
```

---

### Task 5: Analyzer — 30 → 12

**Files:**
- Modify: `tests/analyzer/test_analyzer_blackbox.py`
- Modify: `tests/analyzer/test_analyzer_whitebox.py`
- Modify: `tests/analyzer/test_analyzer_integration.py`

**Selection criterion:** Keep 6 blackbox, 4 whitebox, 2 integration.

- [ ] **Step 1: List current tests**

Run: `pytest tests/analyzer --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors:
- Blackbox (6): compatibility score math on a known feature set, support classification (full / partial / unsupported), unknown-feature handling, weighted score across browsers, grade-letter boundary (A/B/C/D/F), per-browser breakdown structure.
- Whitebox (4): Can I Use DB loader reads `data.json`, web-features overlay applied, scorer threshold internals, version parser internals.
- Integration (2): full pipeline parse→analyze→score on a fixture file, multi-file directory run.

- [ ] **Step 3: Edit blackbox file**

Delete non-surviving tests. Trim parametrize blocks to 1–2 rows.

- [ ] **Step 4: Edit whitebox file**

Delete non-surviving tests.

- [ ] **Step 5: Edit integration file**

Delete non-surviving tests.

- [ ] **Step 6: Run module tests**

Run: `pytest tests/analyzer -v`

Expected: `12 passed`.

- [ ] **Step 7: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `177 passed` (195 − 18).

- [ ] **Step 8: Commit**

```bash
git add tests/analyzer/
git commit -m "test(analyzer): reduce to 12 tests"
```

---

### Task 6: API service — 26 → 10

**Files:**
- Modify: `tests/api/test_api_blackbox.py`
- Modify: `tests/api/test_api_whitebox.py`
- Modify: `tests/api/test_api_integration.py`

**Selection criterion:** Keep 5 blackbox, 3 whitebox, 2 integration.

- [ ] **Step 1: List current tests**

Run: `pytest tests/api --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors:
- Blackbox (5): analyze single file, analyze directory, export request, CRUD for analyses, bookmark/tag CRUD.
- Whitebox (3): singleton service, lazy analyzer load, baseline-feature handling.
- Integration (2): end-to-end analyze + persist + retrieve, export via API.

- [ ] **Step 3: Edit blackbox file**

Delete non-surviving tests.

- [ ] **Step 4: Edit whitebox file**

Delete non-surviving tests.

- [ ] **Step 5: Edit integration file**

Delete non-surviving tests.

- [ ] **Step 6: Run module tests**

Run: `pytest tests/api -v`

Expected: `10 passed`.

- [ ] **Step 7: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `161 passed` (177 − 16).

- [ ] **Step 8: Commit**

```bash
git add tests/api/
git commit -m "test(api): reduce to 10 tests"
```

---

### Task 7: Database — 18 → 7

**Files:**
- Modify: `tests/database/test_database_blackbox.py`
- Modify: `tests/database/test_database_whitebox.py`

**Note:** `tests/database/test_database_blackbox.py` contains tests marked as integration (file-name vs marker mismatch exists in the current repo). Do not rename files — just keep the markers as they are on surviving tests.

**Selection criterion:** Keep 3 blackbox-marked, 2 whitebox-marked, 2 integration-marked.

- [ ] **Step 1: List current tests**

Run: `pytest tests/database --collect-only -q`

Also run each marker filter:
```bash
pytest tests/database -m blackbox --collect-only -q
pytest tests/database -m whitebox --collect-only -q
pytest tests/database -m integration --collect-only -q
```

- [ ] **Step 2: Decide which tests to keep**

Target behaviors:
- Blackbox (3): analysis insert/fetch round trip, bookmark round trip, tag CRUD.
- Whitebox (2): schema migration v1 → v2 applies, singleton connection returns same object.
- Integration (2): full analysis lifecycle (insert → update → delete), statistics aggregation.

- [ ] **Step 3: Edit blackbox file**

Delete non-surviving tests (both blackbox-marked and integration-marked tests live here).

- [ ] **Step 4: Edit whitebox file**

Delete non-surviving tests.

- [ ] **Step 5: Run module tests**

Run: `pytest tests/database -v`

Expected: `7 passed`.

- [ ] **Step 6: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `150 passed` (161 − 11).

- [ ] **Step 7: Commit**

```bash
git add tests/database/
git commit -m "test(database): reduce to 7 tests"
```

---

### Task 8: CLI — 25 → 10

**Files:**
- Modify: `tests/cli/test_cli_blackbox.py`
- Modify: `tests/cli/test_cli_whitebox.py`
- Modify: `tests/cli/test_cli_integration.py`

**Selection criterion:** Keep 4 blackbox, 4 whitebox, 2 integration.

- [ ] **Step 1: List current tests**

Run: `pytest tests/cli --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors:
- Blackbox (4): `analyze` exit codes, `--format` flag handling (one representative case, not every format), quality-gate flag (`--fail-on-score`), browser-string validation.
- Whitebox (4): formatter table layout with color, `CliContext` verbosity/timing, gate evaluation (`evaluate_gates`), one CI generator (GitHub Actions YAML).
- Integration (2): CliRunner end-to-end for `analyze`, CliRunner for `export`.

- [ ] **Step 3: Edit blackbox file**

Delete non-surviving tests.

- [ ] **Step 4: Edit whitebox file**

Delete non-surviving tests.

- [ ] **Step 5: Edit integration file**

Delete non-surviving tests.

- [ ] **Step 6: Run module tests**

Run: `pytest tests/cli -v`

Expected: `10 passed`.

- [ ] **Step 7: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `135 passed` (150 − 15).

- [ ] **Step 8: Commit**

```bash
git add tests/cli/
git commit -m "test(cli): reduce to 10 tests"
```

---

### Task 9: Polyfill — 16 → 7

**Files:**
- Modify: `tests/polyfill/test_polyfill_blackbox.py`
- Modify: `tests/polyfill/test_polyfill_whitebox.py`
- Modify: `tests/polyfill/test_polyfill_integration.py`

**Selection criterion:** Keep 3 blackbox, 2 whitebox, 2 integration.

- [ ] **Step 1: List current tests**

Run: `pytest tests/polyfill --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors:
- Blackbox (3): NPM feature returns npm recommendation, CSS fallback feature returns fallback code, install-command aggregation.
- Whitebox (2): singleton factory, reload preserves data.
- Integration (2): full pipeline (IE11 + fetch polyfill), file generation produces valid header/imports.

- [ ] **Step 3: Edit blackbox file**

Delete non-surviving tests.

- [ ] **Step 4: Edit whitebox file**

Delete non-surviving tests.

- [ ] **Step 5: Edit integration file**

Delete non-surviving tests.

- [ ] **Step 6: Run module tests**

Run: `pytest tests/polyfill -v`

Expected: `7 passed`.

- [ ] **Step 7: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `126 passed` (135 − 9).

- [ ] **Step 8: Commit**

```bash
git add tests/polyfill/
git commit -m "test(polyfill): reduce to 7 tests"
```

---

### Task 10: Export — 11 → 7

**Files:**
- Modify: `tests/export/test_export_blackbox.py`

**Selection criterion:** Keep 7 blackbox (one per format + round-trip).

- [ ] **Step 1: List current tests**

Run: `pytest tests/export --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors (7):
- JSON export produces valid JSON.
- PDF export writes a non-empty file with correct MIME-like first bytes (`%PDF`).
- SARIF 2.1.0 export has required top-level schema keys (`version`, `runs`).
- JUnit XML export is parseable and has `<testsuite>`.
- Checkstyle XML export has `<checkstyle>` root.
- CSV export has a header row plus data rows.
- JSON round-trip: export + re-parse preserves score and grade.

- [ ] **Step 3: Edit the blackbox file**

Delete the four non-surviving tests (extra parametrize rows or redundant "missing field" cases). Keep exactly one test function per target behavior above.

- [ ] **Step 4: Run module tests**

Run: `pytest tests/export -v`

Expected: `7 passed`.

- [ ] **Step 5: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `122 passed` (126 − 4).

- [ ] **Step 6: Commit**

```bash
git add tests/export/
git commit -m "test(export): reduce to 7 tests"
```

---

### Task 11: Config — 8 → 5

**Files:**
- Modify: `tests/config/test_config_blackbox.py`

**Selection criterion:** Keep 5 blackbox.

- [ ] **Step 1: List current tests**

Run: `pytest tests/config --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors (5):
- Load `crossguard.config.json`.
- Fall back to `package.json` "crossguard" key when main file absent.
- CLI flag overrides config file value.
- Defaults applied when no config present.
- Invalid config file raises the expected exception.

- [ ] **Step 3: Edit the file**

Delete the three non-surviving tests.

- [ ] **Step 4: Run module tests**

Run: `pytest tests/config -v`

Expected: `5 passed`.

- [ ] **Step 5: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `119 passed` (122 − 3).

- [ ] **Step 6: Commit**

```bash
git add tests/config/
git commit -m "test(config): reduce to 5 tests"
```

---

### Task 12: AI — 14 → 7

**Files:**
- Modify: `tests/ai/test_ai_blackbox.py`
- Modify: `tests/ai/test_ai_whitebox.py`

**Selection criterion:** Keep 4 blackbox, 3 whitebox.

- [ ] **Step 1: List current tests**

Run: `pytest tests/ai --collect-only -q`

- [ ] **Step 2: Decide which tests to keep**

Target behaviors:
- Blackbox (4): prompt built correctly for a feature, OpenAI response parsed into `AIFixSuggestion`, Anthropic response parsed into `AIFixSuggestion`, `AIFixSuggestion` dataclass holds the expected fields.
- Whitebox (3): OpenAI API call uses mocked client with expected args, Anthropic API call uses mocked client with expected args, prompt template includes feature name and browser list.

- [ ] **Step 3: Edit blackbox file**

Delete non-surviving tests.

- [ ] **Step 4: Edit whitebox file**

Delete non-surviving tests.

- [ ] **Step 5: Run module tests**

Run: `pytest tests/ai -v`

Expected: `7 passed`.

- [ ] **Step 6: Run the full suite**

Run: `pytest tests/ -q 2>&1 | tail -1`

Expected: `112 passed` (119 − 7).

- [ ] **Step 7: Commit**

```bash
git add tests/ai/
git commit -m "test(ai): reduce to 7 tests"
```

---

### Task 13: Final verification and orphaned-fixture sweep

**Files:**
- Modify (if orphans found): `tests/conftest.py`

- [ ] **Step 1: Verify the global count**

Run:
```bash
pytest tests/ -q 2>&1 | tail -1
pytest tests/ -m blackbox --collect-only -q 2>&1 | tail -1
pytest tests/ -m whitebox --collect-only -q 2>&1 | tail -1
pytest tests/ -m integration --collect-only -q 2>&1 | tail -1
```

Expected (targets, ±2 tolerance per the spec):
- Total: `112 passed`
- Blackbox: `59/112`
- Whitebox: `34/112`
- Integration: `19/112`

If the actual numbers are within ±2 of each target, proceed to step 2. If any module is off, go back to that module's task and adjust.

- [ ] **Step 2: Search for orphaned fixtures in `tests/conftest.py`**

Read `tests/conftest.py` and grep the test tree for each fixture name it defines:

```bash
grep -rE "def\s+\w+\s*\(.*<fixture_name>.*\)" tests/
```

For each fixture that no surviving test references, delete its definition from `conftest.py`.

- [ ] **Step 3: Run the full suite one final time**

Run: `pytest tests/ -q`

Expected: all tests pass (same count as step 1).

- [ ] **Step 4: Record the per-module breakdown for the thesis §3.19 rewrite**

Run:
```bash
for dir in parsers/css parsers/html parsers/js parsers/custom_rules analyzer api database cli polyfill export config ai; do
  for m in blackbox whitebox integration; do
    n=$(pytest "tests/$dir" -m $m --collect-only -q 2>&1 | grep -oE "^[0-9]+" | head -1)
    echo "$dir $m $n"
  done
done
```

Save this output — it becomes the new §3.19 table.

- [ ] **Step 5: Commit conftest changes (if any)**

If step 2 removed fixtures:
```bash
git add tests/conftest.py
git commit -m "test: remove orphaned fixtures after suite reduction"
```

If no changes, skip the commit.

- [ ] **Step 6: Summary commit to close the work (optional)**

No action required unless the user asks for a tag or summary commit.

---

## Rollback

If something goes wrong mid-plan:

```bash
# Revert a single module task
git revert <sha-of-that-module's-commit>

# Or reset the whole effort back to the spec commit
git reset --hard 06ea8b8      # the spec commit from brainstorming
```

The spec itself stays — only the test deletions are undone.
