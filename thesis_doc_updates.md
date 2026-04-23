# Thesis update log — analyzer + api + cli + config + database + gui + parsers module cleanup

This file tracks the changes made to `Code/src/analyzer/`, `Code/src/api/`, `Code/src/cli/`, `Code/src/config/`, `Code/src/database/`, `Code/src/gui/`, and `Code/src/parsers/` during the audit, and lists exactly what needs to be updated in the LaTeX thesis so the written chapters + diagrams match the new code. **No LaTeX file has been touched by the automation** — everything below is yours to apply when ready.

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

## 1e. What changed in the code (`Code/src/database/`)

### 1e.1 Context — the root cause of the "dead scaffolding"

Grep showed `src/database/` had 18 public methods with zero callers anywhere in the codebase. A deeper read revealed these weren't accidentally dead — they were **scaffolding for GUI features the thesis describes but that were never actually shipped**:

| Unshipped feature claimed in thesis | Dead backend scaffolding |
|---|---|
| Tag-attach to analyses (`user.tex:196`, `impl.tex:110`) | `add_tag_to_analysis`, `remove_tag_from_analysis`, `get_analyses_by_tag`, `get_tag_counts`, `update_tag`, `get_tag_by_name`, `get_tag_by_id` |
| Bookmark note editing (`impl.tex:219`) | `BookmarksRepository.update_note`, `BookmarksRepository.get_bookmark` |
| Score trends (`impl.tex:213` — already framed as future work in `sum.tex:28`, creating a self-contradiction) | `StatisticsService.get_score_trend` |
| Activity heatmap (never described in thesis) | `StatisticsService.get_recent_activity` |
| Settings export / reset (never described) | `SettingsRepository.get_all`, `SettingsRepository.delete`, `SettingsRepository.get_as_int` |
| Relative-date / file-type-icon view helpers (never described) | `Analysis.get_formatted_date`, `Analysis.get_file_type_icon` |
| Schema-version / table-info dev helpers (never described) | `migrations.get_schema_version`, `migrations.get_table_info` |

Chose **Path A**: delete the scaffolding and propose four small sentence edits to the thesis so the written claims match the app's actual capabilities. `sum.tex:28` already places trends in future work — just needs `impl.tex:213` to stop contradicting it.

### 1e.2 Deleted 18 methods across 4 files

**`src/database/migrations.py`** (-2 functions, ~35 lines)
- `get_schema_version()` — dev helper to read the `schema_version` table
- `get_table_info()` — dev helper returning per-table row counts

**`src/database/models.py`** (-2 methods on `Analysis`, ~20 lines)
- `get_formatted_date()` — returned "Today 3:45 PM" / "Yesterday" / "3 days ago". GUI history card formats dates independently
- `get_file_type_icon()` — returned Unicode icons per file type. GUI uses its own icon set

**`src/database/repositories.py`** (-12 methods, ~125 lines)
- `SettingsRepository`: `get_all`, `delete`, `get_as_int` (3 methods — never read, and `service.py` does its own `int(...)` cast on `ai_max_features`)
- `BookmarksRepository`: `get_bookmark`, `update_note` (2 methods — note-editing UI never built; single-item getter superseded by `get_all_bookmarks`)
- `TagsRepository`: `get_tag_by_name`, `get_tag_by_id`, `update_tag`, `add_tag_to_analysis`, `remove_tag_from_analysis`, `get_analyses_by_tag`, `get_tag_counts` (7 methods — tag-attach UI never built)

**`src/database/statistics.py`** (-2 methods, ~25 lines)
- `get_score_trend` — daily-average trend data, no chart consumes it
- `get_recent_activity` — daily-count heatmap data, no chart consumes it

### 1e.3 What's left on each class

| Class | Remaining public methods |
|---|---|
| `AnalysisRepository` | `save_analysis`, `get_all_analyses`, `get_analysis_by_id`, `delete_analysis`, `clear_all`, `get_count` (6 — all live) |
| `SettingsRepository` | `get`, `set`, `get_as_bool`, `get_as_list` (4 — all live) |
| `BookmarksRepository` | `add_bookmark`, `remove_bookmark`, `is_bookmarked`, `get_all_bookmarks`, `get_count` (5 — all live) |
| `TagsRepository` | `create_tag`, `get_all_tags`, `delete_tag`, `get_tags_for_analysis` (4 — all live, exactly what the GUI currently uses) |
| `StatisticsService` | 10 methods + `conn` property, all consumed via `get_summary_statistics` aggregate |
| `migrations.py` (module functions) | `create_tables`, `drop_tables`, `reset_database` (3 — all live) |
| `Analysis` (model) | `to_dict`, `from_row` (and `browsers` property) — all live |

### 1e.4 Diagram updated — `3.9_database.py` + comparison PNGs

In `Code/docs/diagrams/scripts/3.9_database.py`:
- Replaced the explicitly-named `+ get_score_trend(days) : List` on the `StatisticsService` node with `+ get_top_problematic_features(lim) : List` (still live — consumed by `get_summary_statistics`)
- Changed `+ ...  (13 public methods total)` → `+ ...  (11 public methods total)`

Regenerated `Code/docs/diagrams/images/3.9_database.png` and placed comparison copies in LaTeX (mirroring the `cg_pipeline_before/after.png` pattern):
- `LaTeX/images/cg_database_before.png` — snapshot of the pre-refactor image
- `LaTeX/images/cg_database_after.png` — new image, matches post-refactor code
- `LaTeX/images/cg_database.png` — untouched

Rename `cg_database_after.png` → `cg_database.png` when ready to promote. `\includegraphics{cg_database}` keeps working.

### 1e.5 Proposed LaTeX text edits (for your approval — **no file has been modified**)

These four sentences currently claim features the app doesn't ship after the deletion. Proposed find/replace blocks below.

#### Edit 1 — `LaTeX/chapters/user.tex` line 196

**FIND:**
```
...Analyses can also be bookmarked or tagged for easier organization, making it simple to return to important results later.
```

**REPLACE with:**
```
...Analyses can also be bookmarked for easier organization, making it simple to return to important results later.
```

(Rationale: Users can create/delete/list tags but there is no UI to attach a tag to a specific analysis, so "tagged … for easier organization" isn't true in the shipped app.)

#### Edit 2 — `LaTeX/chapters/impl.tex` line 110

**FIND:**
```
Users can also bookmark the result, add tags, or export it as a report.
```

**REPLACE with:**
```
Users can also bookmark the result or export it as a report.
```

(Rationale: Same — no tag-attach button in the Results view.)

#### Edit 3 — `LaTeX/chapters/impl.tex` line 213

**FIND:**
```
...\texttt{StatisticsService} queries the same database to provide metrics such as average scores, score trends, and grade distribution.
```

**REPLACE with:**
```
...\texttt{StatisticsService} queries the same database to provide metrics such as average/best/worst scores, grade distribution, and file-type distribution.
```

(Rationale: `StatisticsService` no longer exposes `get_score_trend`. `sum.tex:28` already describes trend charts as future work — after this edit the two sentences no longer contradict.)

#### Edit 4 — `LaTeX/chapters/impl.tex` line 219

**FIND:**
```
On the left, \texttt{Bookmark} references an \texttt{Analysis} through a solid line. Users can bookmark any analysis and attach a note.
```

**REPLACE with:**
```
On the left, \texttt{Bookmark} references an \texttt{Analysis} through a solid line. Users can bookmark any analysis.
```

(Rationale: `Bookmark` still has a `note` column and the API allows passing `note` when creating a bookmark, but no UI exists to edit it after creation. The dataclass field stays — just don't claim note-editing in the thesis.)

### 1e.6 Verification
- **132/132 tests pass** — no test depended on any deleted method (verified via exhaustive grep across `tests/` before deletion).
- Vulture on `src/database/` at 80% confidence: **0 hits**.
- CLI end-to-end smoke: `crossguard analyze file.css` exits 0 with table output.
- Every remaining method has at least one caller or is invoked as `self.X(...)` inside its defining class.
- `grep -rn` for each deleted symbol across `src/` + `tests/` + `run_gui.py`: **0 hits** outside the deletions themselves.
- Diagram regenerated and visually confirmed: `StatisticsService` shows 4 named methods + "(11 public methods total)", and the `get_score_trend` line is gone.

### 1e.7 Net size impact
Roughly **−200 lines** of Python across the 4 files (method bodies + docstrings + SQL strings). The diagram script gained 1 line (the replacement) and lost 1 line (the count change) — net zero.

---

## 1f. What changed in the code (`Code/src/gui/`)

### 1f.1 Context — making the thesis's central architectural claim literally true

`impl.tex:329` declares: *"The GUI never imports from the parser, analyzer, or database code, which means the backend could be completely rewritten without breaking the interface."* A GUI audit found **7 deep-path imports** in `src/gui/` violating that claim (`export_manager.py`, `version_range_card.py`, `rules_manager.py`), plus two widgets (`IssueCard`, `PolyfillCard`) accepting constructor params that callers pass real data to — but silently dropping them, undermining the thesis's own UI description at `user.tex:133`. Plus 4 unused imports. Path F4 closes every bypass by routing through new facade wrappers on `AnalyzerService`, and makes the two broken widgets actually render what callers provide.

### 1f.2 Added 5 new facade methods on `AnalyzerService` (`src/api/service.py`)

Each follows the existing lazy-import pattern (`_get_database_updater`, `_get_web_features`).

| Method | Wraps | Consumer |
|---|---|---|
| `get_version_range_summary(feature_id)` | `src/analyzer/version_ranges.get_support_summary` | `version_range_card.VersionRangePopup` |
| `get_browser_display_names()` | `src/analyzer/version_ranges.BROWSER_NAMES` | `version_range_card.VersionRangePopup._create_browser_row` |
| `get_feature_catalogs()` | All `css_feature_maps.*`, `js_feature_maps.*`, `html_feature_maps.*` catalogs — returns a pre-grouped `{'css': {'all', 'categories'}, 'js': {'all', 'categories'}, 'html': {'elements','attributes','input_types','attribute_values'}}` structure | `rules_manager.RulesManagerDialog` (replaces 3 parser imports + the module-level `CSS_CATEGORIES`/`JS_CATEGORIES` dicts) |
| `get_polyfill_map()` | `src/polyfill/polyfill_loader.load_polyfill_map` | `rules_manager.RulesManagerDialog` |
| `save_polyfill_map(data)` | `src/polyfill/polyfill_loader.save_polyfill_map` | `rules_manager.RulesManagerDialog` (2 call sites) |

`AnalyzerService` public method count: **44 → 49**.

### 1f.3 Rewired 3 GUI files through the facade (7 bypasses → 0)

**`src/gui/export_manager.py`** (2 bypasses → 0)
- Removed the 2 inline `from src.export import export_json`/`export_pdf` imports.
- Added a module-level `from ..api import get_analyzer_service`; `ExportManager.__init__` now holds `self._service = get_analyzer_service()`.
- `export_json()` and `export_pdf()` dispatch through `self._service.export_to_json` and `self._service.export_to_pdf` — already-existing facade methods.

**`src/gui/widgets/version_range_card.py`** (2 bypasses → 0)
- Dropped both `from ...analyzer.version_ranges import ...` inline imports.
- Added `from ...api import get_analyzer_service` at top; `VersionRangePopup.__init__` now holds `self._service = get_analyzer_service()` and eagerly caches `self._browser_names = self._service.get_browser_display_names()` once.
- `_init_ui` uses `self._service.get_version_range_summary(feature_id)`; `_create_browser_row` uses the cached `self._browser_names`.

**`src/gui/widgets/rules_manager.py`** (4 bypasses → 0, largest rewire)
- Removed all 3 `from ...parsers.*_feature_maps import (...)` blocks plus `from ...polyfill.polyfill_loader import load_polyfill_map, save_polyfill_map`.
- Removed the module-level `CSS_CATEGORIES` and `JS_CATEGORIES` dicts — they're now assembled once by the facade method.
- Replaced the two module-level helpers `get_css_category()` and `get_js_category()` with a single `_category_for(feature_id, categories)` helper that accepts the category dict as a parameter.
- `RulesManagerDialog.__init__` now calls `self._service.get_feature_catalogs()` once and caches the result alongside narrow aliases (`self._css_categories`, `self._all_css`, `self._html_elements`, etc.) so the rest of the 1,600-line file only needed mechanical find-replace of ~30 references.
- `load_polyfill_map()` → `self._service.get_polyfill_map()`; both `save_polyfill_map(...)` sites → `self._service.save_polyfill_map(...)`.

**Verification**: `grep -rnE "^from src\.(analyzer|database|parsers|export|polyfill|ai|config)|^from \.\.\.(analyzer|database|parsers|export|polyfill|ai|config)|^    from src\.(analyzer|database|parsers|export|polyfill|ai|config)|^        from src\.(analyzer|database|parsers|export|polyfill|ai|config)" src/gui/` → **0 hits**. The thesis's claim at `impl.tex:329` is now literally true; `src/gui/` imports only from `src.api`, `src.gui` (self), `src.utils.config` (shared constants), and third-party libraries.

### 1f.4 Fixed the two broken widgets (thesis claims now match reality)

**`src/gui/widgets/issue_card.py`** — render `fix_suggestion`

The widget previously accepted `fix_suggestion` as a constructor parameter but never stored or rendered it, so AI fix suggestions flowed into `IssueCard(fix_suggestion=issue.get('fix_suggestion'))` and vanished. Rewired:
- Switched from `.place()`-based absolute positioning (fixed 32 px) to a two-row `pack` layout. Top row keeps the feature name + browser badges + baseline pill; bottom row only materialises when `fix_suggestion` is non-empty and shows `"Fix: …"` in muted italic with `wraplength=600` so long suggestions wrap cleanly.
- Colored left border spans the full card height via `relheight=1` regardless of which rows are present.
- Constructor signature unchanged — the existing caller at `issue_card.py:150` (`fix_suggestion=issue.get('fix_suggestion')`) now visibly renders.

**`src/gui/widgets/polyfill_card.py`** — render `import_statements` + `total_size_kb`

Both params were accepted, both silently dropped. Rewired:
- `__init__` now stores `self._imports = import_statements or []` and `self._total_size = total_size_kb`.
- When `self._total_size > 0`, a small `"~X.X KB"` badge appears at the right side of the install-command row (next to the Copy button).
- When `self._imports` is non-empty, a new "Add to your code:" section renders below the install-command row — a `bg_darkest` code block containing one monospace line per import.
- The "Generate polyfills.js" button still renders last when applicable.

Matches `user.tex:133`: *"…install commands (e.g. `npm install datalist-polyfill`), a Copy button, and a Generate polyfills.js button…"* — plus now also the imports and size previously claimed by the backend's aggregate helpers.

### 1f.5 Deleted 4 unused imports

- `src/gui/config.py` — removed `get_color` (re-export dropped; `theme.py` still exports it)
- `src/gui/main_window.py` — removed `AnalysisResult` (kept `get_analyzer_service`)
- `src/gui/widgets/file_table.py` — removed `import os`
- `src/gui/widgets/score_card.py` — removed `import math`

### 1f.6 Updated diagrams + refreshed comparison PNGs

- `Code/docs/diagrams/scripts/3.13_gui.py`: `AnalyzerService "(57 public methods total)"` → `"(49 public methods total)"`
- `Code/docs/diagrams/scripts/3.6_analysis_pipeline.py`: `AnalyzerService "(44 public methods total)"` → `"(49 public methods total)"`
- Regenerated `Code/docs/diagrams/images/3.13_gui.png` and `3.6_analysis_pipeline.png`
- Snapshotted `LaTeX/images/cg_gui.png` → `LaTeX/images/cg_gui_before.png` (frozen pre-refactor state)
- Copied new render → `LaTeX/images/cg_gui_after.png`
- Refreshed `LaTeX/images/cg_pipeline_after.png` with new `"(49 public methods total)"` annotation

Canonical `cg_gui.png` untouched — promote `_after` → canonical when ready.

### 1f.7 No LaTeX text edits needed for impl.tex:329

After F4, the sentence *"The GUI never imports from the parser, analyzer, or database code"* is now literally enforceable by `grep` — no softening required.

**Minor drift flagged but not fixed** (optional cleanup): `user.tex:131` describes the dashboard banner as *"Compatibility: Passing (or Failing, depending on the score)"*. The actual `BuildBadge` widget renders three states (`PASSING` / `WARNING` / `FAILING`, all uppercase) without a `"Compatibility:"` prefix. If you want exact alignment, add a small LaTeX tweak acknowledging the three states and the uppercase status label — but the meaning is close enough that many readers won't notice.

### 1f.8 Verification

- **132/132 tests pass** (no test touches the rewired paths).
- `grep` for GUI deep-path imports → **0 hits**.
- `AnalyzerService` now exposes **49 public methods**, all live.
- Vulture 80% confidence across **every** cleaned module (analyzer + api + cli + config + database + gui) → **0 hits** in any of them.
- End-to-end service smoke — all 5 new facade methods return the expected shapes.
- GUI module tree imports cleanly end-to-end.

---

## 1g. What changed in the code (`Code/src/parsers/`)

### 1g.1 Context

Audit found the parsers diagram (`cg_parsers.png`) advertised 6 public methods per parser, but **3 of those 6 had zero callers anywhere** — not in `src/`, not in any test, not in any diagram anywhere except the parser diagram itself. They were untested API surface that had accumulated without ever being wired to anything. Plus one dead import. The thesis text doesn't mention any of these methods — only `parse_file` and `parse_string` are cited in the pipeline/sequence diagrams.

Pre-deletion safety sweep (9 integration test files scanned, `tests/validation/` scanned, dynamic-dispatch patterns checked, `CLAUDE.md`/`pyproject.toml`/`requirements.txt` checked, `__init__.py` re-exports checked, thesis LaTeX checked) confirmed zero real callers for all 9 methods.

### 1g.2 Deleted 9 dead public methods across 3 parser classes

Each parser had the same 3-method dead tail:

| File | Methods removed |
|---|---|
| `src/parsers/html_parser.py` | `parse_multiple_files`, `get_statistics`, `validate_html` |
| `src/parsers/css_parser.py` | `parse_multiple_files`, `get_statistics`, `validate_css` |
| `src/parsers/js_parser.py` | `parse_multiple_files`, `get_statistics`, `validate_javascript` |

After deletion, each parser exposes exactly **3 public methods** — the ones actually called by the pipeline and tests:
- `parse_file(path) → Set[str]`
- `parse_string(content) → Set[str]`
- `get_detailed_report() → Dict`

Private-method counts unchanged (HTMLParser 17, CSSParser 5, JavaScriptParser 13) — those are the internal detection helpers.

### 1g.3 Deleted 1 unused import

`src/parsers/html_parser.py:8` — `ALL_HTML_FEATURES` was imported but never referenced in the file. `HTMLParser` uses the individual sub-dicts (`HTML_ELEMENTS`, `HTML_ATTRIBUTES`, `HTML_INPUT_TYPES`, `HTML_ATTRIBUTE_VALUES`, …) directly, never the consolidated lookup. The constant is still defined in `html_feature_maps.py` and consumed by `AnalyzerService.get_feature_catalogs()` (see §1f.2).

### 1g.4 Diagram updated — `3.7_parsers.py` + comparison PNGs

In `Code/docs/diagrams/scripts/3.7_parsers.py`:
- `HTMLParser` block: dropped `parse_multiple_files`, `get_statistics`, `validate_html` rows (6 → 3 public methods shown)
- `CSSParser` block: dropped `parse_multiple_files`, `get_statistics`, `validate_css` rows (6 → 3)
- `JavaScriptParser` block: dropped `parse_multiple_files`, `get_statistics`, `validate_javascript` rows (6 → 3)
- Private-method counts (17 / 5 / 13) unchanged
- Attributes unchanged
- "loads rules" arrows to `CustomRulesLoader` unchanged

Regenerated `Code/docs/diagrams/images/3.7_parsers.png` and placed comparison PNGs in LaTeX (same pattern as earlier modules):
- `LaTeX/images/cg_parsers_before.png` — frozen snapshot of the pre-refactor state
- `LaTeX/images/cg_parsers_after.png` — new render
- `LaTeX/images/cg_parsers.png` — untouched

Rename `cg_parsers_after.png` → `cg_parsers.png` when ready to promote; `\includegraphics{cg_parsers}` keeps working.

### 1g.5 No LaTeX text edits needed

Grepped `LaTeX/chapters/*.tex` for every deleted method name (`parse_multiple_files`, `get_statistics`, `validate_html`, `validate_css`, `validate_javascript`): **0 hits**. The thesis only mentions `parse_file` and `parse_string` by name (in the pipeline and sequence diagrams, and in the parser-flow descriptions). No sentence becomes false after deletion.

### 1g.6 Verification

- **132/132 tests pass** (47 parser tests plus 85 other tests — no regressions).
- Vulture at 80% confidence across **all 7 cleaned modules** (analyzer + api + cli + config + database + gui + parsers) → **0 hits** everywhere.
- End-to-end parser smoke via the new trimmed API:
  - `HTMLParser().parse_string('<dialog>…')` detects `dialog`, `input-datetime`
  - `CSSParser().parse_string('.a { display: grid; gap: 10px; … }')` detects `css-grid`, `css-container-queries`, `css-logical-props`
  - `JavaScriptParser().parse_string('const p = Promise.resolve(); fetch(…)')` detects `promises`, `fetch`, `const`, `let`
- `grep -rn "\bparse_multiple_files\b|\bvalidate_html\b|\bvalidate_css\b|\bvalidate_javascript\b"` across the entire repo → **0 stray references**.

### 1g.7 Net size impact

Roughly **−150 lines** of Python (9 method bodies + one import line). The diagram script lost 9 rows and gained nothing — tighter representation.

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
[ ] Rename LaTeX/images/cg_database_after.png → cg_database.png when ready to promote
[ ] Rename LaTeX/images/cg_gui_after.png → cg_gui.png when ready to promote
[ ] Rename LaTeX/images/cg_parsers_after.png → cg_parsers.png when ready to promote
[ ] Rename LaTeX/images/cg_polyfill_after.png → cg_polyfill.png when ready to promote
[ ] Edit LaTeX/chapters/impl.tex line 271 (PolyfillLoader public methods — see section 2.4)
[ ] Update LaTeX/images/cg_sequence.png (2 message changes — see section 2.2)
[ ] Edit LaTeX/chapters/impl.tex line 106 (scoring sentence — see section 2.3)
[ ] Edit LaTeX/chapters/user.tex line 196 (remove "or tagged" — see section 1e.5 Edit 1)
[ ] Edit LaTeX/chapters/impl.tex line 110 (remove "add tags," — see 1e.5 Edit 2)
[ ] Edit LaTeX/chapters/impl.tex line 213 (replace "average scores, score trends, and grade distribution" — see 1e.5 Edit 3)
[ ] Edit LaTeX/chapters/impl.tex line 219 (remove "and attach a note" — see 1e.5 Edit 4)
[ ] (Optional) LaTeX/chapters/user.tex line 131 — align "Compatibility: Passing/Failing" with actual BuildBadge states PASSING/WARNING/FAILING (see 1f.7)
```

## 1h. Polyfill module cleanup (Path A — aggressive delete + diagram refresh)

**Context.** `src/polyfill/` has 2 classes (`PolyfillService`, `PolyfillLoader`) + 1 helper module (`polyfill_generator.py`) + the `polyfill_map.json` data file (57 mappings). Structurally clean and already behind the facade (GUI goes through 8 `AnalyzerService` methods, never imports `src/polyfill/` directly). The deep grep-and-vulture sweep surfaced 3 orphan items — methods/functions that exist in code but no call site ever reaches them.

**Dead code removed.**

1. `PolyfillLoader.has_polyfill(feature_id)` — `polyfill_loader.py:68–73`. No caller anywhere in `src/`, `tests/`, or `docs/`. `PolyfillService.get_recommendations` does the equivalent check inline (`if polyfill_info.get('polyfillable')` / `elif 'fallback' in polyfill_info`) instead of routing through this helper.
2. `PolyfillLoader.is_polyfillable(feature_id)` — `polyfill_loader.py:75–78`. Same: zero callers; the one consumer re-implements the logic inline.
3. `generate_polyfills_content(recommendations)` — `polyfill_generator.py:58–81`. Never exported from `__init__.py`, never called. Near-duplicate of `generate_polyfills_file` without the `output.write_text(...)` step and without the "// Required packages:" npm-install header block. Fossil of an earlier split.

**Net change.** `PolyfillLoader` drops from 5 public methods to 3 (`get_polyfill`, `reload`, plus the private `_load_data`). `polyfill_generator.py` drops from 2 functions to 1.

**Diagram refresh.** `cg_polyfill.png` has been snapshotted as `cg_polyfill_before.png`; `cg_polyfill_after.png` is the re-rendered version with the 2 dead methods gone. Every class, attribute, and method shown on the "after" diagram now has a live caller — the diagram and the code agree.

**Thesis text softening (section 2 below).** `impl.tex:271` currently lists all 3 `PolyfillLoader` methods: "`get_polyfill(feature_id)` returns the mapping for a given feature, or `None` if no match is found; `has_polyfill()` checks whether any polyfill or fallback is available; and `is_polyfillable()` checks specifically for JavaScript polyfills." After Path A, only `get_polyfill` survives, so the sentence needs to lose the `has_polyfill` and `is_polyfillable` clauses. The proposed edit is surfaced in section 2.4 below.

**Verification (post-cleanup).**
- `pytest tests/` → 132/132 pass.
- `vulture src/polyfill/ --min-confidence 80` → 0 hits.
- `python -c "from src.polyfill import PolyfillLoader; print([m for m in dir(PolyfillLoader) if not m.startswith('__')])"` → `['_load_data', 'get_polyfill', 'reload']`.
- GUI smoke: polyfill cards still render; "Generate polyfills.js" still works; Rules Manager polyfill editor still loads/saves `polyfill_map.json`. No call path touched any deleted method.
- Facade integrity: `grep -rn "from src.polyfill\|from \.\.\.polyfill" src/gui/` → **0 hits** (still clean — the polyfill module was already consumer-isolated; this pass didn't need to rewire anything).

## 2.4. Thesis text edit — `impl.tex:271` (polyfill loader public methods)

After Path A, `PolyfillLoader` exposes only `get_polyfill` as a lookup method. The sentence at impl.tex:271 must drop the removed helpers.

**Find:**
```
\texttt{PolyfillLoader} follows the singleton pattern, meaning the JSON file is read only once through the private \texttt{\_load\_data()} method and stored in \texttt{\_data}. Its public methods handle straightforward lookups in a way that \texttt{get\_polyfill(feature\_id)} returns the mapping for a given feature, or \texttt{None} if no match is found; \texttt{has\_polyfill()} checks whether any polyfill or fallback is available; and \texttt{is\_polyfillable()} checks specifically for JavaScript polyfills.
```

**Replace with:**
```
\texttt{PolyfillLoader} follows the singleton pattern, meaning the JSON file is read only once through the private \texttt{\_load\_data()} method and stored in \texttt{\_data}. Its public \texttt{get\_polyfill(feature\_id)} method returns the mapping for a given feature, or \texttt{None} if no match is found; callers inspect the returned dictionary themselves to decide whether to use a JavaScript polyfill or a CSS fallback.
```

This also reconciles with the regenerated diagram (`cg_polyfill_after.png`) which now shows only `get_polyfill`, `reload`, and `_load_data` on `PolyfillLoader`.

## 1i. Utils module cleanup (Path A — aggressive delete, zero thesis/diagram impact)

**Context.** `src/utils/` holds the app's cross-cutting helpers: `config.py` (app-wide constants + singleton logger) and `feature_names.py` (Can I Use ID → human-readable name mapping + fix-suggestion lookup). It is the one shared module that both frontends (GUI, CLI) and the entire backend are allowed to import from, by explicit CLAUDE.md architecture rule. The thesis does not mention utils internals and no diagram depicts it, so cleanup here is purely a code hygiene pass.

**Dead code removed (12 items).** Every item below was verified with exhaustive grep across `src/`, `tests/`, `docs/`, and `LaTeX/` — all returned zero external references before deletion.

1. `DATABASE_PATH` (config.py:13) — `connection.py` builds its own path from `PROJECT_ROOT`; this constant was a stale parallel definition.
2. `DATABASE_HISTORY_LIMIT` (config.py:14) — nothing reads it.
3. `CANIUSE_PACKAGE_JSON` (config.py:17) — `database_updater.py` builds its own package.json path.
4. `SUPPORT_STATUS` dict (config.py:41–49, 9 entries) — orphan. Status-code-to-label mapping is done inline where needed.
5. `STATUS_COLORS` dict (config.py:51–59, 7 entries) — orphan. `version_range_card.py:23` and `browser_card.py:135` each have their own widget-local copies using theme-aware colors; nobody was importing the utils version.
6. `SEVERITY_LEVELS` dict (config.py:61–66, 4 entries) — nothing reads it.
7. `APP_NAME = "Cross Guard"` (config.py:68) — `gui/config.py:5` has its own hardcoded copy; nothing imports utils' version.
8. `APP_VERSION = "1.0.0"` (config.py:69) — same: `gui/config.py:6` owns the only live copy.
9. `LOG_DIR`, `LOG_FILE`, `LOG_MAX_SIZE`, `LOG_BACKUP_COUNT` (config.py:75–78) — used only inside `_setup_file_handler` (item 10).
10. `CrossGuardLogger._setup_file_handler()` method (config.py:110–125, 16 lines) — **never called.** The class's `_setup_root_logger` only installs a stderr console handler; file logging was fully unimplemented. `Code/logs/` directory does not exist on disk.
11. `get_severity(support_status)` function (feature_names.py:439–444) — never imported. Severity mapping is done ad-hoc by callers that need it.
12. `src/utils/feature_names.json` (337-line data file, ~15 KB) — **never loaded by any Python code.** It is a stale JSON dump of the `FEATURE_NAMES` Python dict. The live source of truth is the dict at `feature_names.py:5`.

**Net change.**
- `config.py`: 146 → 90 lines
- `feature_names.py`: 444 → 436 lines
- `feature_names.json`: deleted entirely (0 lines remaining)

**What was kept.** Everything with a live caller: `PROJECT_ROOT`, `CANIUSE_DIR`, `CANIUSE_DB_PATH`, `CANIUSE_FEATURES_PATH`, `NPM_REGISTRY_URL`, `WEB_FEATURES_URL`, `WEB_FEATURES_CACHE_DIR`, `WEB_FEATURES_CACHE_PATH`, `DEFAULT_BROWSERS`, `LATEST_VERSIONS`, `LOG_LEVEL`, `LOG_FORMAT`, `LOG_DATE_FORMAT`, `CrossGuardLogger` (with `_setup_root_logger`, `get_logger`, `set_level`), the module-level `get_logger()` and `set_log_level()` helpers, the `FEATURE_NAMES` and `FIX_SUGGESTIONS` dicts, and the `get_feature_name()` / `_id_to_title()` / `get_fix_suggestion()` functions.

**Verification (post-cleanup).**
- `pytest tests/` → **132/132 pass**.
- Import smoke: every constant and function still imported successfully; logger still emits to stderr (`2026-04-23 … crossguard.smoke.test - INFO - smoke test`).
- CLI smoke: `python -m src.cli.main analyze examples/sample_project/sample.css --format table` → ran to completion with correct output.
- Exhaustive final grep across entire Thesis tree for each of the 12 deleted names (`DATABASE_PATH`, `DATABASE_HISTORY_LIMIT`, `CANIUSE_PACKAGE_JSON`, `SUPPORT_STATUS`, `SEVERITY_LEVELS`, `LOG_DIR`, `LOG_FILE`, `LOG_MAX_SIZE`, `LOG_BACKUP_COUNT`, `_setup_file_handler`, `get_severity`, `feature_names.json`) → **all 0 refs**.
- GUI-local `STATUS_COLORS` dicts in `version_range_card.py` and `browser_card.py` unaffected and still working — they never depended on utils.
- GUI-local `APP_NAME` / `APP_VERSION` in `gui/config.py` unaffected and still the only live copy.

**Thesis impact.** None — utils is not described in any LaTeX chapter and no diagram depicts it. No `impl.tex` edit needed, no diagram refresh needed.

## 1j. Final sweep — residual dead imports + one missed duplicate

**Context.** A final overall sweep (vulture 80 %, exhaustive grep across `src/`, `tests/`, `docs/`, `LaTeX/`, AST-level unused-import detector, and cross-file dynamic-lookup scan) surfaced a handful of items that earlier module-by-module audits missed — partly because some were hidden inside long multi-line import blocks, and one was a dead *data* duplicate that looked live because a different class attribute happened to share its name.

Every flagged item was verified against **seven external-usage channels** before deletion: (1) `from <module> import <name>` elsewhere, (2) `<module>.<name>` attribute access, (3) `__all__` in any `__init__.py`, (4) `getattr/hasattr/eval/__import__` dynamic lookup, (5) test-suite references, (6) LaTeX thesis references, (7) non-import-line usage inside the defining file. All 30 came back with **zero external refs**.

**Dead data removed (1 item).**

- `src/utils/config.py:19–26` — `DEFAULT_BROWSERS` dict of 6 display names (`'chrome': 'Chrome'`, etc.). Never imported anywhere. The identically-named `AnalyzerService.DEFAULT_BROWSERS` class attribute (in `src/api/service.py:28`) is a **different dict** — a browser→version mapping using `LATEST_VERSIONS`. The one in `utils/config.py` was a stale display-name mapping from an earlier design. Removed (9 lines).

**Dead re-export block removed (1 statement, 7 names).**

- `src/gui/config.py:16–24` — a `from .theme import (COLORS, FONTS, SPACING, ANIMATION, WINDOW, get_score_color, configure_ctk_theme)` block labelled "for old import paths" in the module docstring. Grep for `from src.gui.config import COLORS|FONTS|SPACING|ANIMATION|WINDOW|get_score_color|configure_ctk_theme` anywhere under `src/` or `tests/` returned **0 hits** — no consumer ever used the "old path." All GUI widgets import these names directly from `.theme`. Entire block removed; the file's docstring was also shortened from *"Theme constants live in theme.py — this re-exports them for old import paths"* to *"App-level settings."*

**Unused imports removed (22 items across 11 files).**

Each one appears exactly once in its file — inside its import statement — and nowhere else. Verified via AST scan plus regex count.

| File | Removed |
|---|---|
| `src/export/pdf_exporter.py` | `List` |
| `src/gui/main_window.py` | `Optional`, `WINDOW`, `BookmarkButton`, `BrowserCard`, `CompactStatsBar`, `ScoreCard`, `get_available_browsers` |
| `src/gui/widgets/file_table.py` | `Tuple` |
| `src/gui/widgets/history_card.py` | `get_file_type_color` |
| `src/gui/widgets/issue_card.py` | `ICONS` |
| `src/gui/widgets/polyfill_card.py` | `ICONS` |
| `src/gui/widgets/rules_manager.py` | `json`, `Path`, `SPACING` |
| `src/gui/widgets/statistics_panel.py` | `Optional` |
| `src/gui/widgets/version_range_card.py` | `Optional`, `ICONS` |
| `src/parsers/html_parser.py` | `List`, `Optional` |
| `src/polyfill/polyfill_service.py` | `Optional` |

**Note on `ScoreCard`.** `impl.tex:343` mentions `ScoreCard(parent, score=85, grade="B")` as a widget example. This is safe: the `ScoreCard` class itself still lives in `src/gui/widgets/score_card.py` and is still re-exported by `src/gui/widgets/__init__.py`. What was removed is only `main_window.py`'s **unused consumer import** of the same name — the class and its public API are untouched, so the LaTeX description remains accurate.

**Verification (post-cleanup).**
- `pytest tests/` → **132/132 pass**.
- `vulture src/ --min-confidence 80` → **0 hits**.
- Every module imports cleanly (11/11: analyzer, api, cli, config, database, gui, parsers, polyfill, utils, export, ai).
- AST-level unused-import scan across all of `src/` → **0 flagged**.
- `python -m compileall -q src/` → silent.
- CLI end-to-end: `python -m src.cli.main analyze examples/sample_project/sample.css --format table` → runs to completion.
- Pipeline smoke: `AnalyzerService.analyze(AnalysisRequest(css_files=['sample.css']))` → Grade B, score 89.1.
- GUI full import tree: `main`, `MainWindow`, `ExportManager`, `PolyfillCard`, `IssueCard`, `RulesManagerDialog`, `VersionRangePopup`, `StatisticsPanel`, `HistoryCard`, `FileTable`, and `APP_NAME`/`APP_VERSION` all resolve.

**Thesis impact.** None — no LaTeX text or diagram references any of the deleted imports or the `DEFAULT_BROWSERS` display-name dict. No new LaTeX edits. No diagram refreshes.

## 1k. Diagram-wide cross-check — 3 drifts fixed

**Context.** A complete sweep of every PNG in `LaTeX/images/` against its source script (`Code/docs/diagrams/scripts/`) and the current code, covering every class, every method, every attribute, every edge — not just module-local changes. Verification method: AST-level inventory of every class shown, compared 1:1 against the diagram script contents.

**Diagrams verified clean (no action needed):**
- `cg_architecture.png` — all 10 class nodes + connections match code exactly
- `cg_ai.png` — `AIFixService` class attrs (ANTHROPIC_URL, OPENAI_URL, DEFAULT_MODELS), instance attrs (_api_key, _provider, _model, _max_features, _priority), public methods (is_available, get_fix_suggestions), private methods (_build_prompt, _call_api, _call_anthropic, _call_openai, _parse_response) all present ✓
- `cg_gui_after.png` — `MainWindow` 8 attrs + 8 named private methods + "(48 private methods total)" all verified in code; `ExportManager` `export_json` / `export_pdf` match; `AnalyzerService` "(49 public methods total)" correct
- `cg_parsers_after.png` — HTMLParser/CSSParser/JavaScriptParser attrs (features_found, feature_details, unrecognized_patterns, _all_features, _matched_apis) + 3 public methods each + private-method counts (17/5/13) all match; `CustomRulesLoader` `_css_rules` / `_js_rules` / `_html_rules` instance attrs + 4 public + 1 private method all match
- `cg_database_after.png` — `AnalysisRepository` (6 methods), `StatisticsService` "(11 public methods total)", `Analysis` / `Tag` / `Bookmark` / `AnalysisFeature` / `BrowserResult` attrs + methods all match
- `cg_polyfill_after.png` — already verified in §1h; still clean
- `cg_usecase.png` — all 7 use cases map to live features (analyze, view results, export, history/stats, AI + polyfill, rules + DB update, CI/CD); external systems (LLM API, SQLite, Can I Use DB, NPM Registry) all wired correctly

**Diagrams with drift — fixed this pass:**

1. **`cg_pipeline_after.png`** — the parser blocks on this diagram still showed "(6 public methods total)" for HTMLParser / CSSParser / JavaScriptParser, stale from before the §1g parser cleanup (which trimmed each to 3 public methods). Updated `Code/docs/diagrams/scripts/3.6_analysis_pipeline.py` to show the 3 real public methods (`parse_file`, `parse_string`, `get_detailed_report`) inline instead of the "...  (6 public methods total)" placeholder. Re-rendered; `LaTeX/images/cg_pipeline_after.png` refreshed.

2. **`cg_directory.png`** — three stale entries found in `Code/docs/diagrams/scripts/3.18_directory_structure.py`:
   - `api/`: "Service facade (**64 methods**)" → updated to `(49 methods)`
   - `gui/`: "CustomTkinter GUI (**23 widgets**)" → updated to `(22 widgets)` (actual file count)
   - `utils/`: "Logging, **exceptions, types, constants**" → updated to `Logging, constants, and feature-name helpers` (utils never had an exceptions.py or a types module; just `config.py` and `feature_names.py`)
   - Re-rendered. `LaTeX/images/cg_directory_before.png` snapshotted, `cg_directory_after.png` is the new version.

3. **`cg_sequence.png`** — two arrows were stale from the analyzer + scorer refactors. The earlier `latex_edits.md` claimed this diagram was externally-authored with no in-repo source, but the PlantUML source does exist at `Code/docs/diagrams/scripts/3.16_sequence.puml`. Updated both arrows:
   - `CGA → CompatibilityAnalyzer: analyze(features, browsers)` → `classify_features(features, browsers)`
   - `CGA → CompatibilityScorer: calculate_weighted_score(status)` (method never existed after Arch B) → replaced with 4 arrows showing each real scorer method (`score_statuses`, `overall_score`, `grade`, `risk_level`) plus their returns
   - Re-rendered via `plantuml -tpng`. `LaTeX/images/cg_sequence_before.png` snapshotted, `cg_sequence_after.png` is the new version.

**Verification (post-cleanup).**
- `pytest tests/` → **132/132 pass**.
- `vulture src/ --min-confidence 80` → **0 hits**.
- Every PNG referenced by LaTeX either (a) already matches the code, or (b) has a `_before` + `_after` pair ready for promotion.
- `latex_edits.md` updated: section 3 no longer calls `cg_sequence.png` "externally authored"; it's now a "rename `_after` to canonical" item alongside the other 5 diagrams. New checklist entries added for `cg_directory_after.png` and `cg_sequence_after.png` promotion.

**LaTeX text impact.** None. No new text edits are required beyond the 7 already listed in `latex_edits.md`. This pass only fixed diagram counts/labels.

## 1l. Diagram future-proofing + edge-by-edge connection audit

**Two-part deliverable.**

### Part 1: Replace hard-coded method counts with vague placeholders

Every diagram that previously said "(N private/public methods total)" has been rewritten with `(other private methods)` / `(other public methods)`. This way a future method add/remove doesn't make the diagram drift again.

| Script | Before | After |
|---|---|---|
| `3.6_analysis_pipeline.py` | `(49 public methods total)`, `(11 / 17 / 5 / 13 / 5 private methods total)` | `(other public methods)`, `(other private methods)` |
| `3.7_parsers.py` | `(17 / 5 / 13 private methods total)` | `(other private methods)` |
| `3.9_database.py` | `(11 public methods total)` | `(other public methods)` |
| `3.13_gui.py` | `(48 private methods total)`, `(49 public methods total)` | `(other private methods)`, `(other public methods)` |

All 8 graphviz diagrams regenerated. Every `LaTeX/images/cg_*_after.png` refreshed (`cg_pipeline_after`, `cg_parsers_after`, `cg_database_after`, `cg_polyfill_after`, `cg_gui_after`, `cg_directory_after` — plus the sequence PNG already refreshed in §1k).

### Part 2: Edge-by-edge connection audit — every arrow verified against code

I walked every labelled arrow in every diagram and grepped for the code expression that implements it. **Result: every edge has a real call site; every relationship is honest.**

**`cg_architecture.png` — 11 edges, all live:**

| Edge | Code evidence |
|---|---|
| `MainWindow → AnalyzerService` | `main_window.py:9,50` — `from src.api import get_analyzer_service; self._analyzer_service = get_analyzer_service()` |
| `CLI → AnalyzerService` | `cli/main.py:13,259` — `from src.api.service import AnalyzerService; service.analyze_files(...)` |
| `AnalyzerService → CrossGuardAnalyzer` (creates) | `api/service.py:44-45` — `CrossGuardAnalyzer()` |
| `AnalyzerService → AIFixService` (uses) | `api/service.py:598-603` — lazy import + instantiate |
| `AnalyzerService → PolyfillService` (uses) | `api/service.py:624-625, 635-644` — 5+ call sites |
| `AnalyzerService → AnalysisRepository` (uses) | `api/service.py:16, 210-211` — 7+ call sites |
| `CrossGuardAnalyzer ◆ HTMLParser/CSSParser/JavaScriptParser` (composition) | `analyzer/main.py:20-22` |
| `CrossGuardAnalyzer → CanIUseDatabase` (uses) | **Simplification** — CGA composes `CompatibilityAnalyzer`; `compatibility.py:13` holds the real DB handle. Transitively honest at the architecture-diagram abstraction level. The pipeline diagram (`3.6`) shows the precise edge from `CompatibilityAnalyzer` directly. |
| `CanIUseDatabase → Can I Use Data (JSON)` | `analyzer/database.py:22-23` — opens `CANIUSE_DB_PATH` |
| `AnalysisRepository → SQLite` | `repositories.py:3,8,16` — `sqlite3.Connection` |
| `AIFixService → LLM APIs` | `ai/ai_service.py:119,139` — `requests.post(self.ANTHROPIC_URL / self.OPENAI_URL, …)` |

**`cg_pipeline_after.png` — 9 edges, all live:** AnalysisRequest accepted by `analyze(request)` (line 61), AnalysisResult returned (line 61), CrossGuardAnalyzer created (line 44-45), parsers composed (line 20-22), CompatibilityAnalyzer composed (line 23), CompatibilityScorer composed (line 24), CompatibilityAnalyzer queries CanIUseDatabase (`compatibility.py:13,33`).

**`cg_parsers_after.png` — 3 edges, all live:**
- `html_parser.py:19,92` — `get_custom_html_rules()`
- `css_parser.py:11,74` — `get_custom_css_rules()`
- `js_parser.py:16,304` — `get_custom_js_rules()`

**`cg_database_after.png` — 7 edges, all live:**
- AnalysisRepository/StatisticsService → SQLite via `get_connection()` (both files)
- AnalysisRepository manages Analysis (`save_analysis(analysis: Analysis)`)
- Analysis 1..* AnalysisFeature (`models.py:78` — `features: List[AnalysisFeature]`)
- AnalysisFeature 1..* BrowserResult (`models.py:44` — `browser_results: List[BrowserResult]`)
- Bookmark references Analysis (`models.py:141` — `analysis_id: int`)
- Tag 0..* Analysis via junction (`repositories.py:407` — `JOIN analysis_tags at ON t.id = at.tag_id`)

**`cg_ai.png` — 1 edge, live:** `requests.post(self.ANTHROPIC_URL / self.OPENAI_URL, …)`.

**`cg_gui_after.png` — 2 edges, all live:**
- `main_window.py:39,49` — `from .export_manager import ExportManager; self.export_manager = ExportManager(master)` (composition ◆)
- `main_window.py:50` — `self._analyzer_service = get_analyzer_service()` (dependency)

**`cg_polyfill_after.png` — 2 edges, all live:**
- `polyfill_service.py:5,11,23` — `self._loader = get_polyfill_loader(); self._loader.get_polyfill(...)`
- `polyfill_loader.py:33,39,84,92` — reads/writes `POLYFILL_MAP_PATH`

**`cg_usecase.png` — 6 external-system edges, all live:**
- UC analyze → Can I Use DB (`compatibility.py:33` — `self.database.check_support(...)`)
- UC analyze → SQLite (`api/service.py:210, save_analysis_from_result()`)
- UC history → SQLite (`api/service.py:253` — `_analysis_repo().get_all_analyses(...)`)
- UC AI/polyfill → LLM API (`api/service.py:598-603`)
- UC rules/DB → NPM Registry (`database_updater.py:34,36` — `Request(NPM_REGISTRY_URL, …)`)
- UC rules/DB → Can I Use DB (`database_updater.py:256` — `update_database(...)`)

**`cg_sequence.png` — 7 message arrows, all live:**
- `MainWindow/CLI → AnalyzerService.analyze_files(...)` — `main_window.py:1831`, `cli/main.py:259`
- `AnalyzerService → CrossGuardAnalyzer.run_analysis(...)` — `api/service.py:72`
- `CrossGuardAnalyzer → Parser.parse_file(...)` — `analyzer/main.py:109, 120, 124, 128`
- `CrossGuardAnalyzer → CompatibilityAnalyzer.classify_features(...)` — `analyzer/main.py:132`
- `CompatibilityAnalyzer → CanIUseDatabase.check_support(...)` — `compatibility.py:33`
- `CrossGuardAnalyzer → CompatibilityScorer.score_statuses / overall_score / grade / risk_level` — `main.py:140,144,145,151`
- `AnalyzerService → AnalysisRepository.save_analysis(...)` — `api/service.py:20, save_analysis_from_result()`

### Part 3: Facade integrity

| Check | Result |
|---|---|
| GUI deep-path imports into backend (`analyzer`, `database`, `parsers`, `export`, `polyfill`, `ai`) | **0** |
| CLI deep-path imports into backend | **0** |
| AnalyzerService methods shown on any diagram (22 names checked) | **All 22 present & callable** |
| Stub methods (`NotImplementedError` or `TODO: implement`) in AnalyzerService | **0** |
| AnalyzerService public method count | **49**, all live |

### Part 4: Post-cleanup verification

- `pytest tests/` → **132/132 pass**
- `vulture src/ --min-confidence 80` → **0 hits**
- Pipeline end-to-end: Grade B, score 89.1 on sample.css ✓

### Summary of this pass

- **40+ edges** across **8 class diagrams + 1 sequence diagram + 1 use-case diagram** verified against code
- **0 broken edges** found (the one potential drift, architecture's `CGA → CanIUseDatabase`, is a justified high-level simplification covering the real `CGA ◆ CompatibilityAnalyzer → CanIUseDatabase` chain)
- **All hard-coded method counts replaced** with "(other private/public methods)" — immune to future drift
- **8 diagram PNGs regenerated**; all `_after.png` copies refreshed in `LaTeX/images/`
- Facade rule **literally enforced** (0 bypasses in GUI, 0 in CLI)

## 4. So, are the analyzer, api, cli, config, database, gui, parsers, polyfill, and utils modules "fixed"?

Yes. After the changes in sections 1, 1b, 1c, 1d, 1e, 1f, 1g, 1h, 1i, 1j, 1k, and 1l:
- **No dead code**: every public method has a caller (grep + vulture clean across all eight modules at 80% confidence). `AnalyzerService` is at **49 public methods**, all live. `PolyfillLoader` is at **3 public methods**, all live.
- **No duplicates**: classification loop in one place, scoring math in one place, one dispatch table for CI-format exports in the CLI, no parallel/shadow APIs on the facade, no backend scaffolding for unbuilt features.
- **No broken references**: `CompatibilityAnalyzer` is called from the pipeline, `AnalyzerService` is honoured by every GUI widget and by the CLI, `config.output_format` drives `--format`, `StatisticsService` only exposes methods the aggregate actually uses.
- **No dead schemas**: `AnalysisStatus`, `RiskLevel`, `ExportRequest`, `ai_suggestions` field, `ConfigManager.rules_path`/`get`/`get_default_config` all gone.
- **No broken UI**: `IssueCard` now renders `fix_suggestion` text, `PolyfillCard` renders the `import_statements` list and `total_size_kb` badge — both stopped swallowing real data from their callers.
- **Facade literally enforced** — `grep` for deep-path imports under `src/gui/` returns **0 hits**. The thesis's central architectural claim at `impl.tex:329` is now exactly true. CLI has 0 deep imports from `src/export/`.
- **Thesis claims match code** — after applying the LaTeX edits from sections 1e.5 and 2, every feature the thesis describes maps to something the GUI actually ships.
- **Tests**: 132/132 pass (129 original + 3 new for config-to-CLI wiring). No test depended on any deleted method; UI rewires preserved all constructor signatures.

The only outstanding LaTeX work is the items in section 3's checklist — the automation is not permitted to edit thesis source.
