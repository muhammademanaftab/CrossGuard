# Cross Guard - Browser Compatibility Checker

## Project Overview

Cross Guard is a static analysis tool that checks HTML, CSS, and JavaScript source files for browser compatibility issues. It parses source files, extracts the web platform features they use (e.g. CSS Grid, Promises, `<dialog>` element), looks up each feature in the Can I Use database, and reports which features are unsupported or partially supported in the target browsers. Each analysis produces a compatibility score (0-100), a letter grade, and a per-feature breakdown showing support status across Chrome, Firefox, Safari, and Edge.

The tool provides two frontends — a **desktop GUI** (CustomTkinter) and a **production CLI** (Click) — both sharing a single backend through the `src/api/` service facade. Analysis results can be exported in 6 formats (JSON, PDF, SARIF, JUnit XML, Checkstyle XML, CSV) and the CLI integrates directly into CI/CD pipelines with quality gates. An optional AI module (`src/ai/`) can generate code fix suggestions for unsupported features using OpenAI or Anthropic APIs.

## How It Works (Data Flow)

```
Input File (HTML/CSS/JS)
    │
    ▼
┌─────────────────────────────┐
│  Parser (src/parsers/)      │  Extracts web features using:
│  - HTML: BeautifulSoup4     │    - Element/attribute detection
│  - CSS:  tinycss2 AST       │    - Property/selector/at-rule detection
│  - JS:   tree-sitter AST    │    - API/syntax/method detection
│          + regex fallback    │    - Custom rules overlay
└─────────────┬───────────────┘
              │ List of detected Can I Use feature IDs
              ▼
┌─────────────────────────────┐
│  Analyzer (src/analyzer/)   │  For each feature × target browser:
│  - compatibility.py         │    - Looks up support in Can I Use DB
│  - scorer.py                │    - Classifies: supported / partial / unsupported
│  - version_ranges.py        │    - Computes weighted compatibility score
└─────────────┬───────────────┘
              │ AnalysisResult (score, grade, per-browser breakdown)
              ▼
┌─────────────────────────────┐
│  Output                     │
│  - GUI: results view        │  Score card, issue cards, browser cards
│  - CLI: table/json/sarif    │  Terminal table or machine-readable output
│  - Export: PDF/CSV/JUnit    │  Report files for CI or documentation
│  - Database: SQLite         │  Persistent history + statistics
└─────────────────────────────┘
```

## Tech Stack

- **Language**: Python 3.9+
- **GUI Framework**: CustomTkinter (with TkinterDnD2 for drag-and-drop)
- **CLI Framework**: Click
- **HTML Parsing**: BeautifulSoup4 + lxml
- **CSS Parsing**: tinycss2 (AST-based parsing of stylesheets)
- **JS Parsing**: tree-sitter 0.21.3 + tree-sitter-languages 1.10.2 (AST-based), with regex fallback
- **Data Source**: Can I Use database (local JSON copy, updatable)
- **Database**: SQLite (analysis history, bookmarks, tags, settings)
- **PDF Export**: WeasyPrint + Jinja2 (HTML+CSS → PDF). Requires pango/cairo system libs — on macOS `brew install pango cairo`, on Debian/Ubuntu `apt install libpango-1.0-0 libcairo2`.
- **Distribution**: pyproject.toml with optional deps (gui, cli)

## Key Features

### Analysis
1. **Multi-format Parsing**: Parses HTML, CSS, and JS using AST-based parsers (tinycss2, tree-sitter) with regex fallback
2. **Compatibility Scoring**: Weighted scores (0-100) with letter grades (A+ through F) per file
3. **Custom Rules**: User-defined feature detection rules via JSON or GUI editor
4. **Polyfill Suggestions**: Recommends polyfills for unsupported features
5. **AI Fix Suggestions**: Optional LLM-powered code fix suggestions (OpenAI/Anthropic) for unsupported features

### GUI
6. **Drag-and-Drop Upload**: Upload files via drag-and-drop or file picker
7. **Results Dashboard**: Score cards, browser cards, issue cards with collapsible details
8. **Analysis History**: Browse, bookmark, and tag past analyses
9. **Statistics Panel**: Aggregated insights (score trends, top problematic features)
10. **Custom Rules Manager**: Visual editor for adding/editing detection rules

### CLI & CI/CD
11. **6 Export Formats**: JSON, PDF, SARIF 2.1.0, JUnit XML, Checkstyle XML, CSV
12. **Quality Gates**: `--fail-on-score`, `--fail-on-errors`, `--fail-on-warnings` (exit 1 on failure)
13. **CI Config Generation**: Auto-generate GitHub Actions, GitLab CI, or pre-commit hook configs
14. **Stdin Support**: Pipe file content via `--stdin --stdin-filename`
15. **Config File**: `crossguard.config.json` or `package.json` "crossguard" key

## How to Run

### GUI
```bash
python run_gui.py
```

### CLI
```bash
# Analyze a file
python -m src.cli.main analyze path/to/file.js --format table

# Analyze a directory
python -m src.cli.main analyze path/to/project/ --format json

# With custom browsers
python -m src.cli.main analyze file.css --browsers "chrome:120,firefox:121"

# CI output formats (SARIF, JUnit, Checkstyle, CSV)
python -m src.cli.main analyze src/ --format sarif -o results.sarif
python -m src.cli.main analyze src/ --format junit -o results.xml

# Quality gates (exit 1 on failure)
python -m src.cli.main analyze src/ --fail-on-score 80
python -m src.cli.main analyze src/ --fail-on-errors 5 --fail-on-warnings 10

# Multiple simultaneous outputs
python -m src.cli.main analyze src/ --format table --output-sarif r.sarif --output-junit r.xml

# Stdin support
echo "const x = Promise.resolve();" | python -m src.cli.main analyze --stdin --stdin-filename app.js --format sarif

# Verbosity and color control
python -m src.cli.main -v analyze file.js          # verbose
python -m src.cli.main -q analyze file.js          # quiet (suppress logs)
python -m src.cli.main --no-color analyze file.js   # no ANSI colors
python -m src.cli.main --timing analyze file.js     # show elapsed time

# Generate CI configs
python -m src.cli.main init-ci --provider github    # GitHub Actions YAML
python -m src.cli.main init-ci --provider gitlab    # GitLab CI YAML
python -m src.cli.main init-hooks --type pre-commit # pre-commit hook config

# Export a past analysis
python -m src.cli.main export 42 --format pdf --output report.pdf

# Show config
python -m src.cli.main config

# Initialize config file
python -m src.cli.main config --init
```

## Project Structure

```
src/
├── ai/                     # AI fix suggestions (optional, LLM-powered)
│   ├── __init__.py         # Module exports
│   ├── ai_service.py       # AIFixService (Anthropic/OpenAI API calls)
│   └── schemas.py          # AIFixSuggestion dataclass
├── api/                    # API layer (service facade)
│   ├── schemas.py          # Data schemas (incl. ExportRequest)
│   └── service.py          # Main service class (49 methods)
├── cli/                    # CLI (Click-based)
│   ├── main.py             # CLI commands (analyze, export, history, stats, config, update-db, init-ci, init-hooks)
│   ├── formatters.py       # Terminal output formatting (with color support)
│   ├── context.py          # CliContext dataclass (verbosity, color, timing)
│   ├── gates.py            # Quality gate evaluation (ThresholdConfig, evaluate_gates)
│   └── generators.py       # CI config generators (GitHub Actions, GitLab CI, pre-commit)
├── config/                 # Configuration file support
│   └── config_manager.py   # crossguard.config.json + package.json fallback
├── export/                 # Report export (GUI-independent)
│   ├── json_exporter.py    # JSON export
│   ├── pdf_exporter.py     # PDF export (weasyprint + jinja2; needs pango/cairo system libs)
│   ├── sarif_exporter.py   # SARIF 2.1.0 export (GitHub Code Scanning)
│   ├── junit_exporter.py   # JUnit XML export (Jenkins/GitLab CI)
│   ├── checkstyle_exporter.py  # Checkstyle XML export (SonarQube)
│   └── csv_exporter.py     # CSV export
├── analyzer/               # Compatibility analysis logic
│   ├── main.py             # CrossGuardAnalyzer entry point
│   ├── compatibility.py    # Browser compatibility checker
│   ├── database.py         # Can I Use database wrapper
│   ├── database_updater.py # Database update functionality
│   ├── scorer.py           # Compatibility scoring
│   └── version_ranges.py   # Browser version handling
├── database/               # SQLite persistence layer
│   ├── connection.py       # Database connection manager (thread-safe singleton)
│   ├── migrations.py       # Table creation/schema versioning (v1 → v2)
│   ├── models.py           # Data models (Analysis, Feature, BrowserResult, etc.)
│   ├── repositories.py     # CRUD operations (4 repositories)
│   └── statistics.py       # Aggregation queries
├── gui/                    # GUI components
│   ├── app.py              # Application entry point
│   ├── main_window.py      # Main window (views: upload, results, history)
│   ├── theme.py            # Dark blue theme configuration
│   ├── config.py           # GUI configuration
│   ├── file_selector.py    # File selection with drag-and-drop
│   ├── export_manager.py   # GUI export dialogs (delegates to src/export/)
│   └── widgets/            # Reusable UI widgets (22 widgets)
│       ├── ai_fix_card.py       # AI fix suggestion display
│       ├── bookmark_button.py
│       ├── browser_card.py
│       ├── browser_selector.py
│       ├── build_badge.py
│       ├── charts.py
│       ├── collapsible.py
│       ├── drop_zone.py
│       ├── file_table.py
│       ├── header_bar.py
│       ├── history_card.py     # Analysis history item
│       ├── issue_card.py
│       ├── messagebox.py
│       ├── polyfill_card.py    # Polyfill recommendations
│       ├── quick_stats.py
│       ├── rules_manager.py    # Custom rules UI
│       ├── score_card.py
│       ├── sidebar.py
│       ├── statistics_panel.py # Aggregated stats display
│       ├── status_bar.py
│       ├── tag_widget.py
│       └── version_range_card.py
├── polyfill/               # Polyfill recommendations
│   ├── polyfill_generator.py   # Generate polyfill suggestions
│   ├── polyfill_loader.py  # Load polyfill mapping data
│   ├── polyfill_map.json   # Feature-to-polyfill mapping
│   └── polyfill_service.py # Polyfill recommendation service
├── parsers/                # File parsers
│   ├── html_parser.py      # HTML feature extraction (BeautifulSoup4)
│   ├── css_parser.py       # CSS feature extraction (tinycss2 AST)
│   ├── js_parser.py        # JavaScript feature extraction (tree-sitter AST + regex)
│   ├── html_feature_maps.py    # HTML element/attribute → Can I Use mappings
│   ├── css_feature_maps.py     # CSS property/selector → Can I Use mappings
│   ├── js_feature_maps.py      # JS API/syntax → Can I Use mappings
│   ├── custom_rules.json   # User-defined detection rules
│   └── custom_rules_loader.py  # Singleton loader for custom rules
└── utils/                  # Utilities
    ├── config.py           # Logging configuration and constants
    └── feature_names.py    # Human-readable feature names

data/
└── caniuse/                # Can I Use database (local copy, updatable via CLI)
    ├── data.json           # Main compatibility database
    ├── features-json/      # Per-feature JSON files
    └── region-usage-json/  # Browser usage stats by region

tests/
├── conftest.py             # Shared fixtures + test markers (unit/component/integration)
├── analyzer/               # Compatibility engine tests (24 tests, 3 files)
│   ├── test_analyzer_blackbox.py   # Scoring, compatibility, version ranges (18)
│   ├── test_analyzer_whitebox.py   # DB loading, web features, NPM updater (4)
│   └── test_analyzer_integration.py # Full pipeline (2)
├── api/                    # API service layer tests (10 tests, 3 files)
│   ├── test_api_blackbox.py        # Analyze, CRUD, export (5)
│   ├── test_api_whitebox.py        # Singleton, lazy loading, baseline (3)
│   └── test_api_integration.py     # End-to-end (2)
├── cli/                    # CLI tests (18 tests, 3 files)
│   ├── test_cli_blackbox.py        # Commands, gates, browser validation (9)
│   ├── test_cli_whitebox.py        # Formatters, context, generators (4)
│   └── test_cli_integration.py     # Full command integration (5)
├── config/                 # Config module tests (5 tests, 1 file)
│   └── test_config_blackbox.py     # Loading, merging, defaults, pkg.json
├── database/               # Database layer tests (7 tests, 2 files)
│   ├── test_database_blackbox.py   # CRUD, statistics, models (3)
│   └── test_database_whitebox.py   # Migrations, singleton, schema (2)
├── export/                 # Export module tests (7 tests, 1 file)
│   └── test_export_blackbox.py     # All 6 formats
├── polyfill/               # Polyfill tests (7 tests, 3 files)
│   ├── test_polyfill_blackbox.py   # Recommendations, lookups (3)
│   ├── test_polyfill_whitebox.py   # Singleton, reload, internals (2)
│   └── test_polyfill_integration.py # File generation, multi-feature (2)
├── parsers/
│   ├── css/                # CSS parser tests (14 tests, 3 files)
│   │   ├── test_css_blackbox.py    # Feature detection, edge cases (6)
│   │   ├── test_css_whitebox.py    # tinycss2 internals, bugs, custom rules (5)
│   │   └── test_css_integration.py # File I/O, real-world scenarios (3)
│   ├── html/               # HTML parser tests (14 tests, 3 files)
│   │   ├── test_html_blackbox.py   # Detection, edge cases (7)
│   │   ├── test_html_whitebox.py   # State, custom rules (4)
│   │   └── test_html_integration.py # File I/O, real-world, reports (3)
│   ├── js/                 # JS parser tests (14 tests, 3 files)
│   │   ├── test_js_blackbox.py     # Feature detection, edge cases (6)
│   │   ├── test_js_whitebox.py     # AST internals, custom rules (5)
│   │   └── test_js_integration.py  # End-to-end (3)
│   └── custom_rules/       # Custom rules loader tests (5 tests, 2 files)
│       ├── test_custom_rules_blackbox.py  # Loading, applying (3)
│       └── test_custom_rules_whitebox.py  # Singleton, save, reload (2)
└── validation/             # Manual validation sample files
    ├── css/                # CSS validation samples + checklist
    ├── html/               # HTML validation samples + checklist
    ├── js/                 # JS validation samples + checklist
    └── custom_rules/       # Custom rules validation samples

examples/                   # Sample files for demos and reports
├── sample_project/         # Clean demo site used in docs/screenshots
│   ├── sample.html
│   ├── sample.css
│   └── sample.js
├── test_fixtures/          # Stress/edge-case inputs for manual testing
│   ├── test_all_features.html
│   └── test_custom_rule.css
└── sample_output/          # Example reports produced by CrossGuard
    └── compatibility_report_sample.pdf

docs/
└── diagrams/               # Thesis diagrams (source + rendered PNGs)
    ├── README.md           # Diagram index (prefixed by thesis section)
    ├── uml_explained.md    # Plain-English UML walkthrough
    ├── images/             # Rendered PNGs
    └── scripts/            # Graphviz Python + PlantUML generators

crossguard.db               # SQLite database (auto-created, gitignored)
run_gui.py                  # GUI entry point
```

## Architecture

### Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Facade** | `src/api/service.py` | Single `AnalyzerService` (49 methods) provides unified API for both GUI and CLI |
| **Repository** | `src/database/repositories.py` | 4 repository classes (Analysis, Settings, Bookmarks, Tags) abstract all DB operations |
| **Singleton** | `src/database/connection.py` | Thread-safe SQLite connection with automatic table initialization |
| **Dependency Injection** | Repository constructors | Optional `conn` parameter allows passing test DB connections |
| **Lazy Loading** | `AnalyzerService._get_analyzer()` | Backend loaded only on first use for fast startup |
| **Layered Config** | `src/config/config_manager.py` | Precedence: CLI flags > config file > package.json > defaults |
| **Data Contracts** | `src/api/schemas.py` | Typed dataclasses define all frontend-backend communication |

### Layer Separation

```
┌──────────────┐  ┌──────────────┐
│   GUI        │  │   CLI        │    Frontends — import only from src/api/
│ (CustomTkinter) │  (Click)     │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌─────────────────────────────────┐
│   API Facade (src/api/)         │    Service layer — AnalyzerService
│   schemas.py + service.py       │    Data contracts + 49 methods
└──────────────┬──────────────────┘
               │
       ┌───────┼───────┬───────────┐
       ▼       ▼       ▼           ▼
   Parsers  Analyzer  Database  Export     Backend — no frontend imports
```

- **GUI** imports only from `src/api/` (AnalyzerService, schemas)
- **CLI** imports only from `src/api/` (AnalyzerService) + `src/config/`
- **Neither frontend** imports directly from parsers, analyzer, or database
- **Logging** goes to stderr (never stdout) to keep piped CLI output clean

## Database Schema

The app uses SQLite with 8 tables (schema version 2):

```sql
-- V1 tables
analyses (id, file_name, file_path, file_type, overall_score, grade,
          total_features, analyzed_at, browsers_json)
analysis_features (id, analysis_id FK, feature_id, feature_name, category)
browser_results (id, analysis_feature_id FK, browser, version, support_status)

-- V2 tables (settings, bookmarks, tags)
settings (key PK, value, updated_at)
bookmarks (id, analysis_id FK UNIQUE, note, created_at)
tags (id, name UNIQUE, color, created_at)
analysis_tags (analysis_id FK, tag_id FK, created_at)  -- junction table
schema_version (version PK, applied_at)
```

## Custom Rules System

Users can extend feature detection without modifying source code. See the thesis LaTeX source (Chapter 3, Custom Rules section) for a detailed explanation.

### How Detection Works
- **CSS/JS**: Regex pattern matching (`re.search(pattern, source_code)`) — same as built-in rules
- **HTML**: BeautifulSoup DOM lookup — simple dict mapping (tag name → caniuse ID), no regex

### How Merging Works
At parser init, custom rules merge with built-in rules via dict unpacking:
```python
self._all_features = {**ALL_CSS_FEATURES, **get_custom_css_rules()}  # custom overrides built-in
```
After merging, the parser treats all rules identically.

### Via GUI
Click "Custom Rules" in the sidebar to open the rules manager. Custom rules show a "Custom" badge with Edit/Delete buttons.

### Via JSON
Edit `src/parsers/custom_rules.json`:

```json
{
  "css": {
    "feature-id": {
      "patterns": ["regex-pattern"],
      "description": "Human readable name"
    }
  },
  "javascript": {
    "feature-id": {
      "patterns": ["regex-pattern"],
      "description": "Human readable name"
    }
  },
  "html": {
    "elements": { "element-name": "caniuse-feature-id" },
    "attributes": { "attr-name": "caniuse-feature-id" },
    "input_types": { "type-value": "caniuse-feature-id" },
    "attribute_values": { "attr:value": "caniuse-feature-id" }
  }
}
```

## Testing

**Total: 132 tests** across all modules (pytest), organized into black box / white box / integration files. Each module has `test_<module>_blackbox.py` (public API), `test_<module>_whitebox.py` (internals), and optionally `test_<module>_integration.py` (end-to-end).

### Run All Tests
```bash
pytest tests/                       # Full suite (132 tests)
pytest tests/ -m blackbox           # Black box tests only (76)
pytest tests/ -m whitebox           # White box tests only (34)
pytest tests/ -m integration        # Integration tests only (22)
```

### Run by Module
```bash
pytest tests/parsers/css/ -v        # CSS parser tests (14)
pytest tests/parsers/html/ -v       # HTML parser tests (14)
pytest tests/parsers/js/ -v         # JS parser tests (14)
pytest tests/parsers/custom_rules/  # Custom rules loader tests (5)
pytest tests/analyzer/ -v           # Compatibility engine tests (24)
pytest tests/api/ -v                # API service layer tests (10)
pytest tests/database/ -v           # Database layer tests (7)
pytest tests/cli/ -v                # CLI tests (18)
pytest tests/polyfill/ -v           # Polyfill tests (7)
pytest tests/export/ -v             # Export module tests (7)
pytest tests/config/ -v             # Config module tests (5)
pytest tests/ai/ -v                 # AI fix suggestions tests (7)
```

### Test Coverage Summary

| Module | Tests | BB/WB/Int | What's Covered |
|--------|-------|-----------|----------------|
| CSS parser | 14 | 6/5/3 | Detection, tinycss2 AST, bugs, real-world |
| HTML parser | 14 | 7/4/3 | Detection, DOM, custom rules, real-world |
| JS parser | 14 | 6/5/3 | Detection, tree-sitter AST, custom rules |
| Custom rules | 5 | 3/2/- | Loading, singleton, save/reload |
| Analyzer | 24 | 18/4/2 | Scoring, compatibility, DB, web features |
| API service | 10 | 5/3/2 | Analyze, CRUD, singleton, end-to-end |
| Database | 7 | 3/2/2 | CRUD, statistics, migrations, singleton |
| CLI | 18 | 9/4/5 | Commands, gates, formatters, generators |
| Polyfill | 7 | 3/2/2 | Recommendations, singleton, file gen |
| Export | 7 | 7/-/- | All 6 formats |
| Config | 5 | 5/-/- | Loading, merging, defaults, pkg.json |
| AI | 7 | 4/3/- | API calls, prompt building, response parsing |

### Manual Validation
See `tests/validation/` for manual validation samples and checklists (CSS, HTML, JS, custom rules).

## Parser Feature Coverage

| Parser | Features Mapped | Parsing Method | Notes |
|--------|-----------------|----------------|-------|
| HTML   | 100+ elements, attributes, input types | BeautifulSoup4 DOM traversal | Semantic, form, media elements |
| CSS    | 150+ properties, selectors, at-rules | tinycss2 AST parsing | Grid, flexbox, modern features |
| JS     | 278 Can I Use feature IDs | tree-sitter AST + regex fallback | APIs, methods, syntax features |

### JS Parser Detection Strategy
The JS parser uses a 3-tier detection approach:
1. **AST node types**: Detects syntax features (optional chaining `?.`, nullish coalescing `??`, private fields `#x`)
2. **AST identifiers/calls**: Detects API usage (method calls, constructors, property access)
3. **Regex on AST-cleaned text**: Catches patterns missed by AST (with comments/strings stripped)

Additional parser notes:
- **Parent feature handling**: Methods like `.then()`, `.resolve()` map to parent features (promises)
- **False positive prevention**: Common programming verbs and React component names are filtered
- **Directive detection**: `"use strict"` and `"use asm"` detected before string removal
- **Template literal handling**: Preserves `${...}` structure for detection

## CI/CD Integration

### GitHub Actions
```yaml
- name: Check browser compatibility
  run: crossguard analyze src/ --format sarif --output-sarif results.sarif --fail-on-score 80
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

### GitLab CI
```yaml
compatibility:
  script: crossguard analyze src/ --format junit -o results.xml --fail-on-score 80
  artifacts:
    reports:
      junit: results.xml
```

### Pre-commit Hook
```yaml
- repo: local
  hooks:
    - id: crossguard
      entry: crossguard analyze --fail-on-score 80
      types: [html, css, javascript]
```

### Exit Codes
- `0` — All features compatible (or quality gate passed)
- `1` — Compatibility issues found (or quality gate failed)
- `2` — Error (bad input, missing file, etc.)

### Config Precedence
1. CLI flags (highest)
2. `crossguard.config.json`
3. `package.json` "crossguard" key
4. Built-in defaults (lowest)

## Code Style

- **Comments**: Concise, human-sounding. Only keep comments that explain *why*, not *what*. No verbose Args/Returns docstrings — one-liners preferred. Section headers use `# --- Section ---` style in long files.
- **Tkinter event bindings**: Always use `lambda e=None:` (not `lambda e:`) so the callback works whether called with or without the event argument. CustomTkinter can sometimes invoke bindings without passing the event.

## Common Development Tasks

### Adding a New Built-in Feature Rule
1. CSS: Edit `src/parsers/css_feature_maps.py`
2. JS: Edit `src/parsers/js_feature_maps.py`
3. HTML: Edit `src/parsers/html_feature_maps.py`

### Modifying the Theme
Edit `src/gui/theme.py` - all colors are centralized in the `COLORS` dict.

### Adding a New Widget
1. Create file in `src/gui/widgets/`
2. Import theme colors from `..theme`
3. Export from `src/gui/widgets/__init__.py`

### Database Operations
- Connection: `src/database/connection.py`
- CRUD: `src/database/repositories.py`
- Stats queries: `src/database/statistics.py`

### Adding a New Export Format
1. Create `src/export/<format>_exporter.py` with an `export_<format>(report, output_path)` function
2. Register in `src/export/__init__.py`
3. Add format option to CLI `--format` choices in `src/cli/main.py`
4. Add tests in `tests/export/test_<format>_exporter.py`
