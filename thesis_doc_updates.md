# Thesis update log — analyzer + api + cli + config module cleanup

This file tracks the changes made to `Code/src/analyzer/`, `Code/src/api/`, `Code/src/cli/`, and `Code/src/config/` during the audit, and lists exactly what needs to be updated in the LaTeX thesis so the written chapters + diagrams match the new code. **No LaTeX file has been touched by the automation** — everything below is yours to apply when ready.

---

## 1. What changed in the code (`Code/src/analyzer/`)

### 1.1 `CompatibilityAnalyzer` was wired into the pipeline
Previously the class was instantiated on `CrossGuardAnalyzer` but never actually called — `CrossGuardAnalyzer._check_compatibility()` had its own inline duplicate of the classification loop. The class was also carrying two dead private methods (`_calculate_severity`, `_extreme_browser`) and five dead `SEVERITY_*` string constants.

**After:**
- `CompatibilityAnalyzer` now has a single public method: `classify_features(features, target_browsers) → Dict` which returns `{browser: {supported, partial, unsupported, unknown}}`.
- `CrossGuardAnalyzer._check_compatibility` is a one-liner that delegates to it.
- The inline duplicate is gone; the two dead private methods and all `SEVERITY_*` constants are gone.

### 1.2 `CompatibilityScorer` rewired around `STATUS_SCORES`
The scorer previously hard-coded the numbers `100` and `50` inside `per_browser_percentage` while also advertising a parallel `STATUS_SCORES` lookup table that nothing read. That made `STATUS_SCORES` dead and put the scoring weights in two places. A later cleanup deleted `STATUS_SCORES` and the `score_for_status()` helper that used it.

**After:** `STATUS_SCORES` is restored as the single source of truth for per-status point contribution and is now load-bearing. A new method `score_statuses(statuses: List[str]) → float` looks up each Can I Use status code in the table and returns the average. `CrossGuardAnalyzer._calculate_scores` calls `score_statuses` directly on the raw status codes that `CompatibilityAnalyzer.classify_features` now produces, instead of counting buckets. The old `per_browser_percentage(supported, partial, total)` method is gone — its job is covered by `score_statuses`.

Final public surface: one class attribute (`STATUS_SCORES`) + four methods (`score_statuses`, `overall_score`, `grade`, `risk_level`).

### 1.2.1 `CompatibilityAnalyzer.classify_features` now also returns raw status codes
To make Arch B work, `classify_features` returns an extra `statuses` key alongside the four UI buckets. The per-browser dict is now `{'supported', 'partial', 'unsupported', 'unknown', 'statuses'}`, where `statuses` is the raw Can I Use code (`y`/`a`/`x`/`n`/`p`/`d`/`u`) for every feature, in the same order `classify_features` iterated. The UI consumers that only reach for `supported`/`partial`/`unsupported`/`unknown` continue to work unchanged; the scorer consumes `statuses`.

### 1.3 `CrossGuardAnalyzer.analyze_single_file` removed
Unused public method (0 external callers). GUI and CLI both go through `run_analysis()` with a single-file list.

**After:** `CrossGuardAnalyzer` has one public method, `run_analysis()`, plus 11 private helpers.

### 1.4 `CanIUseDatabase` trimmed from 6 → 3 public methods
Three of the six advertised methods had 0 callers: `get_all_features`, `get_feature_info`, `get_browser_versions`.

**After:** Database exposes only `load`, `get_feature`, `check_support` (plus 5 private helpers). `self.database` on `CrossGuardAnalyzer` is gone too — only `CompatibilityAnalyzer` talks to the DB now.

### 1.5 `version_ranges.py` — removed 2 dead functions
- `get_all_browser_ranges(feature_id)` — 0 callers
- `format_ranges_for_display(feature_id, browser)` — 0 callers

**After:** module keeps `get_version_ranges`, `get_support_summary`, `_get_status_text`, and the `BROWSER_NAMES` lookup — all still used.

### 1.6 `web_features.py` — removed 1 dead method
- `WebFeaturesManager.get_feature_count()` — 0 callers.

### 1.7 Unused imports removed
- `typing.Tuple` from `src/analyzer/main.py`
- `typing.List` and `functools.lru_cache` from `src/analyzer/database.py` (they were only used by the deleted `get_all_features` / `get_browser_versions`)

### 1.8 Module-level `run_analysis()` wrapper deleted (`main.py`)
A top-level `def run_analysis(html_files, css_files, js_files, target_browsers)` function sat at the bottom of `main.py` and simply instantiated `CrossGuardAnalyzer()` and forwarded to the instance method of the same name. Zero callers anywhere in `src/`, `tests/`, or `run_gui.py` — everything routes through `AnalyzerService`, which instantiates the class directly. Deleted. (Not shown on any diagram — class methods are what the diagrams depict, and the class method is untouched.)

### 1.9 `version_ranges.get_version_ranges` — dedup via inner helper
The function had the same five-line `ranges.append({"start": ..., "end": ..., "status": ..., "status_text": ...})` block in two places (once at each status-boundary inside the loop, once after the loop to flush the final range). Extracted as a local `_flush(status, start, end)` closure inside `get_version_ranges`. Behaviour identical; no public API change.

### 1.10 Code-side diagram re-rendered
`Code/docs/diagrams/images/3.6_analysis_pipeline.png` has been regenerated from the updated script so it matches the code exactly. Additionally, two comparison copies were saved next to the existing LaTeX diagram so nothing gets overwritten:
- `LaTeX/images/cg_pipeline_before.png` — copy of the pre-refactor image (same as the still-untouched `cg_pipeline.png`)
- `LaTeX/images/cg_pipeline_after.png` — the new rendered image

The original `LaTeX/images/cg_pipeline.png` was **not** modified — see section 2.

### 1.11 Tests
Three test files were updated to use the new `classify_features` + `CompatibilityScorer` API instead of the old `analyze()` / `per_browser_percentage()` APIs:
- `tests/analyzer/test_analyzer_blackbox.py` — test helper now uses `classify_features` + `score_statuses`; `test_per_browser_percentage_formula` replaced with `test_score_statuses_formula` that exercises `STATUS_SCORES` directly via status-code inputs.
- `tests/analyzer/test_analyzer_integration.py` — scoring helper updated; bucket-sum assertion now iterates only the four bucket keys so the new `statuses` key is ignored for that check.
- `tests/polyfill/test_polyfill_integration.py` — uses `classify_features` buckets instead of the old `report['browser_scores']` structure.

Full suite: **129 tests pass**. Vulture at 80% confidence: **0 hits**.

---

## 1b. What changed in the code (`Code/src/api/`)

### 1b.1 Enforced the facade rule — rewired `rules_manager.py`
The GUI's `RulesManagerDialog` was bypassing the facade by importing four helpers directly from `src/parsers/custom_rules_loader`, violating the thesis's own architectural rule ("GUI imports only from src/api/"). Of those four, only `load_raw_custom_rules` (1 call) and `save_custom_rules` (4 calls) were actually used — the other two imports were dead.

**After:**
- Removed the deep import block from `src/gui/widgets/rules_manager.py`.
- Added `from ...api import get_analyzer_service` and `self._service = get_analyzer_service()` in `RulesManagerDialog.__init__`.
- `load_raw_custom_rules()` → `self._service.get_custom_rules()`.
- `save_custom_rules(...)` × 4 → `self._service.save_custom_rules(...)`.
- Net effect on `AnalyzerService`: `get_custom_rules` (1 caller now) and `save_custom_rules` (4 callers now) become live. The `self._analyzer = None` reset done inside `AnalyzerService.save_custom_rules` is now actually triggered whenever the GUI saves a custom rule — fixes a latent stale-analyzer bug where a just-edited rule wouldn't take effect until the app restarted.

### 1b.2 Deleted 17 aspirational methods from `AnalyzerService`
Confirmed via exhaustive grep: zero callers anywhere in `src/`, `tests/`, or `run_gui.py`. All removed from `src/api/service.py`:

| Category | Methods removed |
|---|---|
| Browsers | `get_default_browsers`, `get_available_browsers` |
| Statistics | `get_score_trend`, `get_top_problematic_features` |
| Settings | `get_all_settings` |
| Bookmarks | `update_bookmark_note`, `get_bookmarks_count` |
| Tags | `update_tag`, `add_tag_to_analysis`, `remove_tag_from_analysis`, `get_analyses_by_tag`, `get_tag_counts` |
| Web features | `update_web_features`, `has_web_features_data` |
| Config | `load_config` (CLI uses `src.config.load_config` directly, which returns a `ConfigManager`, not a dict — the facade version had divergent semantics and no consumer) |
| Misc | `classify_file`, `is_user_rule` |

**Public method count on `AnalyzerService` drops from 57 → 40.**

### 1b.3 Deleted dead schemas
All had zero consumers anywhere in `Code/`:

- `AnalysisStatus` enum + 3 values (`SUCCESS`, `FAILED`, `NO_FILES`) — success is expressed via `AnalysisResult.success: bool` instead.
- `RiskLevel` enum + 4 values (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) — code uses the string literals `'none'/'low'/'medium'/'high'` from `CompatibilityScorer.risk_level()` instead.
- `ExportRequest` dataclass — declared and re-exported but never constructed. The real export methods take raw args.
- `AnalysisResult.ai_suggestions` field — never set, never read via attribute access. AI suggestions flow through the `result_dict['ai_suggestions']` dict key (set in `src/cli/main.py`, consumed in `src/export/sarif_exporter.py`).
- `from enum import Enum` — no longer imported (both enums removed).

### 1b.4 `src/api/__init__.py` trimmed
Removed re-exports for the three deleted schemas. The `__all__` list shrinks from 11 to 8 symbols.

### 1b.5 Pipeline diagram re-rendered
`Code/docs/diagrams/scripts/3.6_analysis_pipeline.py`: the `AnalyzerService` annotation changed from `"(57 public methods total)"` → `"(40 public methods total)"`. Regenerated `Code/docs/diagrams/images/3.6_analysis_pipeline.png` and refreshed `LaTeX/images/cg_pipeline_after.png`.

### 1b.6 Tests
No test changes needed. All 129/129 still pass. End-to-end analyze via `AnalyzerService.analyze_files` on a sample CSS file still returns a successful result with a correct grade.

---

## 1c. What changed in the code (`Code/src/cli/`)

### 1c.1 Added four CI-export facade wrappers to `AnalyzerService`
The CLI was importing `export_sarif`, `export_junit`, `export_checkstyle`, and `export_csv` directly from `src/export/` — violating the facade rule. The facade had wrappers for `export_to_json` and `export_to_pdf` but not for the four CI formats.

**Added to `src/api/service.py`** (mirrors the existing `export_to_json` pattern):

| Method | Returns |
|---|---|
| `export_to_sarif(analysis_id_or_result, output_path=None)` | JSON-encoded SARIF string (or `output_path` if written to file) |
| `export_to_junit(analysis_id_or_result, output_path=None)` | JUnit XML string (or `output_path`) |
| `export_to_checkstyle(analysis_id_or_result, output_path=None)` | Checkstyle XML string (or `output_path`) |
| `export_to_csv(analysis_id_or_result, output_path=None)` | CSV string (or `output_path`) |

`AnalyzerService` public method count: **40 → 44**.

### 1c.2 Rewired `src/cli/main.py` — eliminated 3 facade bypasses + deduped dispatch
The CLI had two helpers (`_write_secondary_outputs`, `_format_ci_output`) with nearly-identical if-elif dispatch tables over the five export formats. Both imported the exporter functions from `src/export/` directly inside the function body.

**After:**
- Removed all three `from src.export import ...` imports from CLI code.
- Introduced a single module-level dispatch table `_EXPORT_METHOD_BY_FORMAT` mapping each format name to the corresponding `AnalyzerService` method name.
- `_write_secondary_outputs` and `_format_ci_output` are now tiny functions that look up the method name and call `getattr(service, method_name)(...)` — both go through the facade.
- Updated all three call sites in `analyze` to pass `service` through.

### 1c.3 Removed unused `Any` import (`src/cli/formatters.py`)
`from typing import Any, Dict, List` → `from typing import Dict, List`. Trivial cleanup.

### 1c.4 Pipeline diagram re-rendered
`Code/docs/diagrams/scripts/3.6_analysis_pipeline.py`: the `AnalyzerService` annotation changed from `"(40 public methods total)"` → `"(44 public methods total)"`. Regenerated `Code/docs/diagrams/images/3.6_analysis_pipeline.png` and refreshed `LaTeX/images/cg_pipeline_after.png`.

### 1c.5 Verification
- **129/129 tests pass** (no test changes were needed).
- CLI no longer imports from `src/export/` — `grep "from src\.export" src/cli/` → 0 hits.
- End-to-end: `crossguard analyze file.css --format sarif --output-junit r.xml --output-csv r.csv` produces valid SARIF 2.1.0 on stdout and writes both secondary outputs correctly.
- Vulture on `src/cli/` at 80% confidence: 0 hits.

---

## 1d. What changed in the code (`Code/src/config/`)

### 1d.1 Deleted 4 truly-dead items
Confirmed by exhaustive grep: zero callers anywhere.

| Removed | Location | Reason |
|---|---|---|
| `ConfigManager.rules_path` property | `config_manager.py:76-78` | No code reads it |
| `ConfigManager.get(key, default)` method | `config_manager.py:84-85` | Generic getter, no external callers; internal code uses the dict's `.get()` directly |
| `get_default_config()` module function | `config_manager.py:105-106` | Re-exported in `__init__.py` but no one imports it |
| `DEFAULT_CONFIG['rules']` key | `config_manager.py:17` | Its only reader (`rules_path`) was itself dead |

Also removed `get_default_config` from `src/config/__init__.py`'s import block and `__all__` list. Public surface of the module is now `ConfigManager` + `load_config`.

### 1d.2 Wired `config.output_format` into the CLI's `--format` priority chain
The `output_format` property was **tested but unused in production**. Users could set `"output": "json"` in `crossguard.config.json` and the CLI silently ignored it — a latent bug. Fixed properly:

**`src/cli/main.py` — `analyze` command:**
- Changed `--format` Click option from `default='table'` to `default=None`.
- After loading config, added:
  ```python
  if fmt is None:
      fmt = config.output_format
  if fmt not in ('table', 'json', 'summary', 'sarif', 'junit', 'checkstyle', 'csv'):
      click.echo(f"Error: invalid output format '{fmt}' from config. ...", err=True)
      sys.exit(2)
  ```
- Help text on `--format` updated to mention the fallback chain.

**Resulting priority chain** (highest to lowest):
1. `--format` / `-f` CLI flag
2. `CROSSGUARD_FORMAT` environment variable
3. `"output"` key in `crossguard.config.json` (or `package.json` → `"crossguard"."output"`)
4. Hardcoded default `'table'`

### 1d.3 Added 3 integration tests
`tests/cli/test_cli_integration.py` gains a new `TestConfigOutputFormat` class:

- `test_config_output_json_drives_format` — verifies that with `crossguard.config.json = {"output": "json"}` and no `--format` flag, the CLI emits valid JSON.
- `test_explicit_format_flag_overrides_config` — verifies that `--format summary` wins over the config's `"output": "json"`.
- `test_invalid_config_output_exits_with_error` — verifies that `"output": "wat"` exits with code 2 and prints "invalid output format".

### 1d.4 Verification
- **132/132 tests pass** (129 original + 3 new).
- Vulture on `src/config/` at 80% confidence: 0 hits.
- The `output_format` property and its tests are now load-bearing rather than cargo-cult.

---

## 2. What needs to change in LaTeX (your call)

### 2.1 `LaTeX/images/cg_pipeline.png` — replace with the new PNG

The original `cg_pipeline.png` is currently missing from the working tree (shown as `deleted:` in `git status`). Two comparison copies still sit in `LaTeX/images/`:

- `cg_pipeline_before.png` — what the image looked like before the analyzer + api refactors
- `cg_pipeline_after.png` — what the image looks like after the refactors (matches current code); regenerated from `Code/docs/diagrams/images/3.6_analysis_pipeline.png`

To make `\includegraphics{cg_pipeline}` resolve again, rename or copy `cg_pipeline_after.png` → `cg_pipeline.png`. You can then remove `_before.png` and `_after.png` if you don't want them in the repo long-term. **The after-PNG now reflects both the analyzer-module changes (§1) and the api-module changes (§1b)** — including the "(40 public methods total)" annotation on the `AnalyzerService` block.

**Concretely, the new image shows these differences vs. the old:**

| Element | Old diagram says | New diagram says |
|---|---|---|
| `CrossGuardAnalyzer` public methods | `run_analysis(...)` + *(2 public methods total)* | `run_analysis(...)` only (single public method) |
| `CrossGuardAnalyzer` private count | *(10 private methods total)* | *(11 private methods total)* |
| `CompatibilityAnalyzer` methods | `+ analyze(features, browsers) : Dict` · `- _calculate_severity(status, total) : str` · *(6 private methods total)* | `+ classify_features(features, browsers) : Dict` only |
| `CompatibilityScorer` members | 5 methods including `+ score_for_status(status) : int`, `+ per_browser_percentage(sup, par, tot) : float` + class attr `+ STATUS_SCORES : Dict` | `+ STATUS_SCORES : Dict` still there; 4 methods: `+ score_statuses(statuses) : float`, `+ overall_score(browser_pcts) : float`, `+ grade(score) : str`, `+ risk_level(score, unsup) : str` |
| `CanIUseDatabase` methods | `load`, `check_support`, `get_feature_info`, *(6 public methods total)* | `load`, `get_feature`, `check_support` (3 public, no total-count footer) |
| Edges | dashed edge `CrossGuardAnalyzer — uses → CanIUseDatabase` | (removed — only `CompatibilityAnalyzer` queries the DB now) |

### 2.2 `LaTeX/images/cg_sequence.png` — needs two fixes

The sequence diagram currently shows two messages that don't match the code:

1. `CrossGuardAnalyzer → CompatibilityAnalyzer: analyze(features, browsers)`
   → **should be** `classify_features(features, browsers)`
2. `CrossGuardAnalyzer → CompatibilityScorer: calculate_weighted_score(status)`
   → this method **never existed** in the current scorer. Under Arch B the scorer is driven by `STATUS_SCORES` and exposes four methods: `score_statuses`, `overall_score`, `grade`, `risk_level`. The orchestrator calls all four during the scoring phase. Replace the single arrow with either:
   - a simplified single arrow labelled `score_statuses / overall_score / grade / risk_level` returning `score + grade`, or
   - four arrows (one per helper) — the thesis-level simplification is fine.

`Code/docs/diagrams/scripts/` does not currently contain a source for `cg_sequence.png` (it's the one diagram that was authored externally), so this one needs to be edited in whichever tool produced it — or regenerated.

### 2.3 `LaTeX/chapters/impl.tex` line 106 — text edit

**FIND:**
```
The scoring module in \texttt{src/analyzer/main.py} then takes these results and calculates a score from 0 to 100 along with a letter grade from A to F. The \texttt{calculate\_simple\_score()} helper on \texttt{CompatibilityScorer} exposes the per-browser contribution logic used during this computation.
```

**REPLACE with:**
```
After gathering these results, the scoring work is delegated to the \texttt{CompatibilityScorer} class in \texttt{src/analyzer/scorer.py}. At its core is a \texttt{STATUS\_SCORES} lookup table that maps each Can I Use status code to a point contribution out of 100 ('y' = 100, 'a'/'x' = 50, everything else = 0), making the scoring policy a single edit away. \texttt{score\_statuses()} averages those points over all checked features for one browser, \texttt{overall\_score()} averages across browsers into a single number from 0 to 100, \texttt{grade()} maps that score to a letter grade from A to F, and \texttt{risk\_level()} tags the analysis as \texttt{none}, \texttt{low}, \texttt{medium}, or \texttt{high}.
```

### 2.4 Anywhere else in LaTeX that still looks fine
I scanned `LaTeX/chapters/*.tex` for every removed / renamed symbol. Only `impl.tex:106` needs edits. The surrounding paragraphs (pipeline overview, parser descriptions, severity-based GUI grouping, scoring formula description on impl.tex:170-194, grade scale, user.tex scoring section) are all still accurate.

---

## 3. Quick checklist

```
[ ] Rename LaTeX/images/cg_pipeline_after.png → cg_pipeline.png (old one currently deleted)
[ ] Update LaTeX/images/cg_sequence.png (2 message changes — see section 2.2)
[ ] Edit LaTeX/chapters/impl.tex line 106 (replace the scoring sentence — see section 2.3)
```

## 4. So, are the analyzer, api, cli, and config modules "fixed"?

Yes. After the changes in sections 1, 1b, 1c, and 1d:
- **No dead code**: every public and private method has at least one caller (verified by grep + vulture). `AnalyzerService` is at 44 public methods, all live. `ConfigManager` surface trimmed to what's used.
- **No duplicates**: the classification loop lives in one place (`CompatibilityAnalyzer.classify_features`), the scoring math in one place (`CompatibilityScorer`), one dispatch table for CI-format exports in the CLI, no parallel/shadow APIs on the facade.
- **No broken references**: `CompatibilityAnalyzer` is called from the pipeline, `AnalyzerService` is honoured by `RulesManagerDialog` and by the CLI for all export formats, `config.output_format` is now actually wired into the CLI's `--format` priority chain.
- **No dead schemas**: `AnalysisStatus`, `RiskLevel`, `ExportRequest`, `ai_suggestions` field, `ConfigManager.rules_path`/`get`/`get_default_config` are all gone.
- **Facade enforced** for analyzer + database + export flows: GUI has 0 deep imports from `src/analyzer/`, `src/database/`, or `src/export/`; CLI has 0 deep imports from `src/export/`. (Three minor peripheral bypasses remain in GUI widgets for static-data browsing.)
- **Tests**: 132/132 pass (129 original + 3 new for config-to-CLI wiring).

The only outstanding inconsistency is the three LaTeX items listed in section 2 — because the automation is not permitted to edit the thesis source.
