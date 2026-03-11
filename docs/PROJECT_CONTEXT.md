# Cross Guard — Complete Project Context

> **Purpose of this document**: This file contains everything an AI agent, developer, or contributor needs to understand Cross Guard — what it does, how it works, what rules to follow, and what to avoid. If you read only this file, you should be able to work on any part of the codebase correctly.

---

## 1. What Is Cross Guard?

Cross Guard is a **static analysis tool** that checks HTML, CSS, and JavaScript source files for **browser compatibility issues**. It is a thesis project (university level).

**The problem it solves**: Web platform features (CSS Grid, Promises, `<dialog>`, etc.) have different support levels across browsers. A feature that works in Chrome may be broken in Safari. Developers normally check this manually or use Can I Use one feature at a time. Cross Guard automates this — it scans source files, extracts every web feature used, looks each one up in the Can I Use database, and produces a report showing what's unsupported.

**What it produces per analysis**:
- A compatibility score (0-100)
- A letter grade (A+ through F)
- A per-feature breakdown showing support status across Chrome, Firefox, Safari, and Edge
- Polyfill suggestions for unsupported features
- Optional ML-based risk prediction

**Two frontends, one backend**:
- **Desktop GUI** (CustomTkinter) — for interactive use
- **Production CLI** (Click) — for automation and CI/CD pipelines
- Both share the same analysis backend through `src/api/service.py` (facade pattern), so results are always identical

## 2. How It Works (Data Flow)

```
Input File (HTML/CSS/JS)
    │
    ▼
┌─────────────────────────────┐
│  Parser (src/parsers/)      │  Extracts web features:
│  - HTML: BeautifulSoup4     │    elements, attributes, input types
│  - CSS:  tinycss2 AST       │    properties, selectors, at-rules, values
│  - JS:   tree-sitter AST    │    APIs, syntax, methods, constructors
│          + regex fallback    │    + custom rules overlay
└─────────────┬───────────────┘
              │ Set of Can I Use feature IDs (e.g. "css-grid", "promises")
              ▼
┌─────────────────────────────┐
│  Analyzer (src/analyzer/)   │  For each feature × target browser:
│  - compatibility.py         │    looks up support in Can I Use DB
│  - scorer.py                │    classifies: supported / partial / unsupported
│  - version_ranges.py        │    computes weighted compatibility score
└─────────────┬───────────────┘
              │ Report dict (score, grade, per-browser breakdown)
              ▼
┌─────────────────────────────┐
│  Output                     │
│  - GUI: results dashboard   │  Score card, issue cards, browser cards
│  - CLI: table/json/sarif    │  Terminal table or machine-readable output
│  - Export: PDF/CSV/JUnit    │  Report files for CI or documentation
│  - Database: SQLite         │  Persistent history + statistics
└─────────────────────────────┘
```

### Parser Details

| Parser | Library | Features Mapped | Strategy |
|--------|---------|-----------------|----------|
| HTML | BeautifulSoup4 + lxml | 100+ elements, attributes, input types | DOM traversal, tag/attribute lookup |
| CSS | tinycss2 | 150+ properties, selectors, at-rules | AST parsing, regex on serialized nodes |
| JS | tree-sitter 0.21.3 + tree-sitter-languages 1.10.2 | 278 Can I Use feature IDs | 3-tier: AST node types → AST identifiers → regex on AST-cleaned text |

**JS parser 3-tier strategy**:
1. **AST node types** — detects syntax features (optional chaining `?.`, nullish coalescing `??`, private fields `#x`)
2. **AST identifiers/calls** — detects API usage (method calls, constructors, property access)
3. **Regex on AST-cleaned text** — catches patterns missed by AST (comments and strings already stripped)

**Critical version pin**: tree-sitter **must** be pinned to `0.21.3`. Version 0.23+ breaks the `Language()` API with tree-sitter-languages 1.10.2.

## 3. Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.9+ (tested up to 3.12) |
| GUI | CustomTkinter + TkinterDnD2 | 5.2+ |
| CLI | Click | 8.1+ |
| HTML parsing | BeautifulSoup4 + lxml | 4.12+ |
| CSS parsing | tinycss2 | 1.4.0 |
| JS parsing | tree-sitter + tree-sitter-languages | 0.21.3 + 1.10.2 (pinned) |
| Compatibility data | Can I Use database (local JSON) | Updatable via CLI |
| Persistence | SQLite | Built-in |
| PDF export | reportlab | 4.0+ |
| ML (optional) | scikit-learn | 1.0+ |
| Distribution | pyproject.toml | Optional deps: gui, cli, ml, dev |

## 4. Project Structure

```
src/
├── api/                    # Service facade (single entry point for GUI + CLI)
│   ├── schemas.py          # Typed dataclasses for all frontend-backend communication
│   └── service.py          # AnalyzerService — 59 methods covering all operations
├── cli/                    # CLI (Click-based, 8 commands)
│   ├── main.py             # Commands: analyze, export, history, stats, config, update-db, init-ci, init-hooks
│   ├── formatters.py       # Terminal output formatting (tables, colors)
│   ├── context.py          # CliContext dataclass (verbosity, color, timing)
│   ├── gates.py            # Quality gate evaluation (ThresholdConfig, evaluate_gates)
│   └── generators.py       # CI config generators (GitHub Actions, GitLab CI, pre-commit)
├── config/                 # Configuration file support
│   └── config_manager.py   # crossguard.config.json + package.json fallback
├── export/                 # Report export (6 formats, GUI-independent)
│   ├── json_exporter.py
│   ├── pdf_exporter.py
│   ├── sarif_exporter.py   # SARIF 2.1.0 (GitHub Code Scanning)
│   ├── junit_exporter.py   # JUnit XML (Jenkins/GitLab CI)
│   ├── checkstyle_exporter.py  # Checkstyle XML (SonarQube)
│   └── csv_exporter.py
├── analyzer/               # Compatibility analysis engine
│   ├── main.py             # CrossGuardAnalyzer (main entry point, run_analysis method)
│   ├── compatibility.py    # Browser compatibility checker
│   ├── database.py         # Can I Use database wrapper
│   ├── database_updater.py # npm-based database updates
│   ├── scorer.py           # Weighted compatibility scoring
│   └── version_ranges.py   # Browser version handling
├── database/               # SQLite persistence (8 tables, schema v2)
│   ├── connection.py       # Thread-safe singleton connection
│   ├── migrations.py       # Schema versioning (v1 → v2)
│   ├── models.py           # Data models
│   ├── repositories.py     # 4 repository classes (Analysis, Settings, Bookmarks, Tags)
│   └── statistics.py       # Aggregation queries
├── gui/                    # Desktop GUI (CustomTkinter)
│   ├── app.py              # Application entry point
│   ├── main_window.py      # Main window (views: upload, results, history)
│   ├── theme.py            # Dark blue theme (all colors in COLORS dict)
│   ├── config.py           # GUI configuration
│   ├── file_selector.py    # File selection with drag-and-drop
│   ├── export_manager.py   # GUI export dialogs
│   └── widgets/            # 23 reusable UI widgets
├── ml/                     # Machine learning risk prediction (optional, scikit-learn)
├── polyfill/               # Polyfill recommendations
│   ├── polyfill_generator.py
│   ├── polyfill_loader.py
│   ├── polyfill_map.json   # Feature-to-polyfill mapping data
│   └── polyfill_service.py
├── parsers/                # File parsers + feature maps
│   ├── html_parser.py      # HTML feature extraction
│   ├── css_parser.py       # CSS feature extraction (tinycss2 AST)
│   ├── js_parser.py        # JS feature extraction (tree-sitter AST + regex)
│   ├── html_feature_maps.py
│   ├── css_feature_maps.py
│   ├── js_feature_maps.py
│   ├── custom_rules.json   # User-defined detection rules
│   └── custom_rules_loader.py
└── utils/
    ├── config.py           # Logging, constants, paths (PROJECT_ROOT, CANIUSE_DIR, etc.)
    ├── exceptions.py       # Custom exception hierarchy (CrossGuardError base + 15 subclasses)
    ├── feature_names.py    # Human-readable feature name lookup
    └── types.py            # Type definitions

data/caniuse/               # Can I Use database (local JSON, updatable via CLI)
tests/                      # 2,359 tests (pytest)
examples/                   # Sample files for demos
docs/thesis/                # Thesis chapters and references
```

## 5. Architecture Rules (CRITICAL)

### Layer Separation — Do NOT Break This

```
┌──────────────┐  ┌──────────────┐
│   GUI        │  │   CLI        │    Frontends
│ (CustomTkinter) │  (Click)     │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌─────────────────────────────────┐
│   API Facade (src/api/)         │    Service layer
│   AnalyzerService + schemas     │
└──────────────┬──────────────────┘
               │
       ┌───────┼───────┬───────────┐
       ▼       ▼       ▼           ▼
   Parsers  Analyzer  Database  Export     Backend
```

- **GUI** imports ONLY from `src/api/` (AnalyzerService, schemas). Never from parsers, analyzer, database, or export.
- **CLI** imports ONLY from `src/api/` (AnalyzerService) + `src/config/`. Never from parsers, analyzer, or database.
- **Backend modules** never import from GUI or CLI.
- **Logging** goes to stderr (never stdout) — this keeps piped CLI output (SARIF, JSON) clean.

### Design Patterns In Use

| Pattern | Where | Why |
|---------|-------|-----|
| **Facade** | `src/api/service.py` | Single `AnalyzerService` (59 methods) serves both GUI and CLI |
| **Repository** | `src/database/repositories.py` | 4 repo classes abstract all SQLite operations |
| **Singleton** | `src/database/connection.py` | Thread-safe DB connection with auto-initialization |
| **Dependency Injection** | Repository constructors | Optional `conn` param for test isolation |
| **Lazy Loading** | `AnalyzerService._get_analyzer()` | Heavy backend loaded on first use only |
| **Layered Config** | `src/config/config_manager.py` | Precedence: CLI flags > config file > package.json > defaults |
| **Data Contracts** | `src/api/schemas.py` | Typed dataclasses define all frontend-backend communication |

## 6. Running the Application

### GUI
```bash
python run_gui.py
```

### CLI
```bash
# Analyze a single file
python -m src.cli.main analyze path/to/file.js --format table

# Analyze a directory (recursively finds HTML/CSS/JS files)
python -m src.cli.main analyze path/to/project/ --format json

# Custom browsers
python -m src.cli.main analyze file.css --browsers "chrome:120,firefox:121"

# CI output formats
python -m src.cli.main analyze src/ --format sarif -o results.sarif
python -m src.cli.main analyze src/ --format junit -o results.xml

# Quality gates (exit 1 on failure)
python -m src.cli.main analyze src/ --fail-on-score 80
python -m src.cli.main analyze src/ --fail-on-errors 5 --fail-on-warnings 10

# Multiple simultaneous outputs
python -m src.cli.main analyze src/ --format table --output-sarif r.sarif --output-junit r.xml

# Stdin support
echo "const x = Promise.resolve();" | python -m src.cli.main analyze --stdin --stdin-filename app.js

# Global options (placed BEFORE the command)
python -m src.cli.main -v analyze file.js          # verbose
python -m src.cli.main -vv analyze file.js         # more verbose
python -m src.cli.main -vvv analyze file.js        # debug
python -m src.cli.main -q analyze file.js          # quiet (suppress log messages, NOT the report)
python -m src.cli.main --no-color analyze file.js   # no ANSI colors
python -m src.cli.main --timing analyze file.js     # show elapsed time

# Other commands
python -m src.cli.main history                      # past analyses
python -m src.cli.main stats                        # aggregated statistics
python -m src.cli.main export 42 --format pdf -o report.pdf
python -m src.cli.main config                       # show current config
python -m src.cli.main config --init                # create crossguard.config.json
python -m src.cli.main update-db                    # update Can I Use database
python -m src.cli.main init-ci --provider github    # generate CI workflow
python -m src.cli.main init-hooks --type pre-commit # generate pre-commit hook
```

### CLI Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success (or quality gate passed) |
| 1 | Compatibility issues found (or quality gate failed) |
| 2 | Error (invalid input, missing file, etc.) |

### Config Precedence
1. CLI flags (highest priority)
2. `crossguard.config.json`
3. `package.json` `"crossguard"` key
4. Built-in defaults (lowest)

## 7. Database Schema (SQLite)

8 tables, schema version 2. Auto-created on first run at `crossguard.db`.

```sql
-- V1 tables
analyses (id, file_name, file_path, file_type, overall_score, grade,
          total_features, analyzed_at, browsers_json)
analysis_features (id, analysis_id FK, feature_id, feature_name, category)
browser_results (id, analysis_feature_id FK, browser, version, support_status)

-- V2 tables
settings (key PK, value, updated_at)
bookmarks (id, analysis_id FK UNIQUE, note, created_at)
tags (id, name UNIQUE, color, created_at)
analysis_tags (analysis_id FK, tag_id FK, created_at)
schema_version (version PK, applied_at)
```

If the database becomes corrupted, delete `crossguard.db` and restart the app. It will be recreated automatically.

## 8. Custom Rules System

Users can extend feature detection without modifying source code.

### Detection Mechanism
- **CSS/JS**: Regex pattern matching (`re.search(pattern, source_code)`) — same as built-in rules
- **HTML**: BeautifulSoup DOM lookup — simple dict mapping (tag name → caniuse ID), no regex

### Merging
At parser init, custom rules merge with built-in rules via dict unpacking:
```python
self._all_features = {**ALL_CSS_FEATURES, **get_custom_css_rules()}
```
Custom rules override built-in rules with the same key. After merging, all rules are treated identically.

### Custom Rules JSON Format
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

### Via GUI
Click "Custom Rules" in the sidebar. Custom rules show a "Custom" badge with Edit/Delete buttons.

## 9. Testing

**2,359 tests** across all modules (pytest). Data-driven via `@pytest.mark.parametrize`.

### Run Tests
```bash
pytest tests/                       # Full suite
pytest tests/ -m unit               # Unit tests only
pytest tests/ -m integration        # Integration tests only
pytest tests/parsers/css/ -v        # CSS parser (520 tests)
pytest tests/parsers/html/ -v       # HTML parser (496 tests)
pytest tests/parsers/js/ -v         # JS parser (284 tests)
pytest tests/parsers/custom_rules/  # Custom rules loader (42 tests)
pytest tests/analyzer/ -v           # Compatibility engine (287 tests)
pytest tests/api/ -v                # API service layer (200 tests)
pytest tests/database/ -v           # Database layer (175 tests)
pytest tests/cli/ -v                # CLI (162 tests)
pytest tests/polyfill/ -v           # Polyfill (158 tests)
pytest tests/export/ -v             # Export module (43 tests)
pytest tests/config/ -v             # Config module (25 tests)
```

### Test Markers
Defined in root `conftest.py`:
- `unit` — Pure unit tests (no I/O)
- `component` — Component tests with real dependencies
- `integration` — End-to-end pipeline tests

### Test Conventions
- Parser conftest fixtures: `parse_features` (returns set), `get_detailed_report`, `get_feature_details` (JS only)
- API tests mock `CrossGuardAnalyzer` and check `run_analysis` calls
- Database tests use `tmp_path` fixtures for isolated SQLite instances
- CLI tests use Click's `CliRunner` for isolated command invocation

## 10. Exception Hierarchy

All custom exceptions inherit from `CrossGuardError` (in `src/utils/exceptions.py`):

```
CrossGuardError
├── ParserError
│   ├── HTMLParserError
│   ├── CSSParserError
│   └── JavaScriptParserError
├── DatabaseError
│   ├── DatabaseLoadError
│   ├── FeatureNotFoundError
│   └── DatabaseUpdateError
├── AnalysisError
│   ├── ValidationError
│   ├── CompatibilityCheckError
│   └── ScoringError
├── ExportError
│   ├── JSONExportError
│   ├── PDFExportError
│   └── HTMLExportError
├── FileError
│   ├── FileNotFoundError
│   ├── FileReadError
│   └── FileWriteError
└── ConfigurationError
    ├── InvalidBrowserError
    └── InvalidVersionError
```

All exceptions carry a `.details` dict and a `.to_dict()` method for JSON serialization.

## 11. Key Features Summary

### GUI Features
1. Drag-and-drop file upload (TkinterDnD2)
2. Results dashboard: score card, browser cards, issue cards (collapsible)
3. Browser selector: choose target browsers and versions
4. Analysis history: browse, bookmark, tag past analyses
5. Statistics panel: aggregated insights, top problematic features
6. Custom rules manager: visual editor for detection rules
7. Export reports: PDF and JSON from GUI
8. Settings: database update, preferences, default browsers

### CLI Features
1. 8 commands: `analyze`, `export`, `history`, `stats`, `config`, `update-db`, `init-ci`, `init-hooks`
2. 7 output formats: table, summary, json, sarif, junit, checkstyle, csv
3. Quality gates: `--fail-on-score`, `--fail-on-errors`, `--fail-on-warnings`
4. Stdin support: pipe file content via `--stdin --stdin-filename`
5. CI config generation: GitHub Actions, GitLab CI, pre-commit hooks
6. Global options: `-v`/`-vv`/`-vvv`, `-q`, `--no-color`, `--timing`
7. Config file support: `crossguard.config.json` or `package.json`

### Analysis Features
1. Multi-format parsing (HTML, CSS, JS) using AST-based parsers
2. Weighted compatibility scoring (0-100) with letter grades
3. Custom rules system (JSON or GUI editor)
4. Polyfill suggestions for unsupported features
5. ML risk prediction (optional, scikit-learn)
6. Baseline status integration (Web Features dataset)

## 12. Code Style and Conventions

- **Comments**: Concise, human-sounding. Explain *why*, not *what*. One-liner docstrings preferred. Section headers use `# --- Section ---` in long files.
- **Tkinter event bindings**: Always use `lambda e=None:` (not `lambda e:`). CustomTkinter can invoke bindings without the event argument.
- **Logging**: Always to stderr. Use `logging.getLogger(__name__)`. Never print to stdout from backend code.
- **Imports**: Frontend (GUI/CLI) imports only from `src/api/`. Backend modules never import from frontend.
- **Tests**: Use `@pytest.mark.parametrize` for data-driven testing. Return sets/dicts for diagnosable failures.

## 13. What NOT To Do

1. **Do NOT import from parsers/analyzer/database in GUI or CLI code** — always go through `src/api/service.py`
2. **Do NOT print to stdout in backend code** — use `logging` (goes to stderr)
3. **Do NOT upgrade tree-sitter beyond 0.21.3** — breaks compatibility with tree-sitter-languages 1.10.2
4. **Do NOT add project-level scanning, framework detection, or .crossguardignore features** — these were deliberately removed from the codebase
5. **Do NOT create `src/scanner/` or `src/api/project_schemas.py`** — these modules were removed and should not be recreated
6. **Do NOT add verbose docstrings** — keep them as one-liners
7. **Do NOT commit `crossguard.db`** — it's auto-created and gitignored
8. **Do NOT add `ignore` or `ignore_patterns` to config** — this feature was removed

## 14. Common Development Tasks

### Adding a New Feature Detection Rule
- CSS: Edit `src/parsers/css_feature_maps.py`
- JS: Edit `src/parsers/js_feature_maps.py`
- HTML: Edit `src/parsers/html_feature_maps.py`

### Adding a New Export Format
1. Create `src/export/<format>_exporter.py` with `export_<format>(report, output_path)` function
2. Register in `src/export/__init__.py`
3. Add format to `--format` choices in `src/cli/main.py`
4. Add tests in `tests/export/test_<format>_exporter.py`

### Adding a New GUI Widget
1. Create file in `src/gui/widgets/`
2. Import theme colors from `..theme`
3. Export from `src/gui/widgets/__init__.py`

### Modifying the Theme
Edit `src/gui/theme.py` — all colors are in the `COLORS` dict.

### Database Operations
- Connection: `src/database/connection.py`
- CRUD: `src/database/repositories.py`
- Stats: `src/database/statistics.py`

## 15. CI/CD Integration Examples

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

## 16. Thesis Context

This is a **university thesis project**. The documentation lives in `docs/thesis/`:
- `chapters/chapter1.md` — Introduction, motivation, goals, scope
- `chapters/chapter2.md` — User documentation (GUI features, CLI commands, setup guide)
- `chapters/chapter3.md` — Developer documentation (architecture, design patterns, implementation)
- `references/` — Supporting reference documents

The thesis covers the full software engineering lifecycle: requirements analysis, architecture design, implementation, testing, and documentation. The project demonstrates competency in Python development, AST-based parsing, database design, GUI development, CLI design, CI/CD integration, and software testing.
