# Cross Guard - Browser Compatibility Checker

## Project Overview
Cross Guard is a desktop application that analyzes HTML, CSS, and JavaScript files for browser compatibility issues. It uses the Can I Use database to check feature support across major browsers.

## Tech Stack
- **GUI Framework**: CustomTkinter (with TkinterDnD2 for drag-and-drop)
- **Language**: Python 3.9+
- **Database**: SQLite (for analysis history)
- **HTML Parsing**: BeautifulSoup4
- **Data Source**: Can I Use database

## Project Structure
```
src/
├── api/                    # API layer (service facade)
│   ├── schemas.py          # Data schemas
│   └── service.py          # Main service class
├── analyzer/               # Compatibility analysis logic
│   ├── compatibility.py    # Browser compatibility checker
│   ├── database.py         # Can I Use database wrapper
│   ├── database_updater.py # Database update functionality
│   ├── scorer.py           # Compatibility scoring
│   └── version_ranges.py   # Browser version handling
├── database/               # SQLite persistence layer
│   ├── connection.py       # Database connection manager
│   ├── migrations.py       # Table creation/schema
│   ├── models.py           # Data models (Analysis, Feature, etc.)
│   ├── repositories.py     # CRUD operations
│   └── statistics.py       # Aggregation queries
├── gui/                    # GUI components
│   ├── app.py              # Application entry point
│   ├── main_window.py      # Main window (views: upload, results, history)
│   ├── theme.py            # Dark blue theme configuration
│   ├── config.py           # GUI configuration
│   ├── file_selector.py    # File selection with drag-and-drop
│   ├── export_manager.py   # PDF/JSON export
│   └── widgets/            # Reusable UI widgets
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
│       ├── ml_risk_card.py
│       ├── quick_stats.py
│       ├── rules_manager.py    # Custom rules UI
│       ├── score_card.py
│       ├── sidebar.py
│       ├── statistics_panel.py # Aggregated stats display
│       ├── status_bar.py
│       ├── tag_widget.py
│       └── version_range_card.py
├── ml/                     # Machine learning (risk prediction)
│   ├── feature_extractor.py
│   ├── model_evaluator.py
│   ├── model_trainer.py
│   ├── risk_labels.py
│   ├── risk_predictor.py
│   └── visualizations.py
├── parsers/                # File parsers
│   ├── html_parser.py      # HTML feature extraction
│   ├── css_parser.py       # CSS feature extraction
│   ├── js_parser.py        # JavaScript feature extraction
│   ├── html_feature_maps.py
│   ├── css_feature_maps.py
│   ├── js_feature_maps.py
│   ├── custom_rules.json   # User-defined detection rules
│   └── custom_rules_loader.py
└── utils/                  # Utilities
    ├── config.py           # Logging and configuration
    ├── exceptions.py       # Custom exceptions
    ├── feature_names.py    # Human-readable feature names
    └── types.py            # Type definitions

tests/
├── conftest.py             # Shared pytest fixtures
├── parsers/
│   ├── css/                # CSS parser tests (17 test files)
│   ├── html/               # HTML parser tests (25 test files)
│   └── js/                 # JS parser tests (12 test files)
└── validation/
    └── js/                 # Manual JS validation tests
        ├── 01_syntax/
        ├── 02_promises_async/
        ├── 03_dom_apis/
        ├── ...
        ├── 13_edge_cases/
        ├── 14_real_world/
        ├── comprehensive_test.js
        ├── CHECKLIST.md
        └── README.md

crossguard.db               # SQLite database (auto-created)
run_gui.py                  # GUI entry point
```

## How to Run
```bash
python run_gui.py
```

## Key Features
1. **File Analysis**: Upload HTML, CSS, JS files via drag-and-drop or file picker
2. **Compatibility Report**: Shows browser support status with scores and grades
3. **Export**: Export reports as PDF or JSON
4. **Database Updates**: Update Can I Use database from within the app
5. **Custom Rules**: Add user-defined feature detection rules
6. **Analysis History**: Persistent storage of past analyses (SQLite)
7. **Statistics Dashboard**: Aggregated insights from all analyses

## Database Schema
The app uses SQLite with 3 related tables:

```sql
-- Main analysis records
analyses (id, file_name, file_path, file_type, overall_score, grade,
          total_features, analyzed_at, browsers_json)

-- Detected features per analysis
analysis_features (id, analysis_id FK, feature_id, feature_name, category)

-- Browser support status per feature
browser_results (id, analysis_feature_id FK, browser, version, support_status)
```

## Custom Rules System
Users can extend feature detection without modifying source code:

### Via GUI
Click "Custom Rules" button in the header to open the rules manager.

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
    "attribute_values": { "attr:value": "caniuse-feature-id" }
  }
}
```

## Architecture Notes
- **API Layer**: `src/api/` provides a clean facade between GUI and backend
- **Singleton Pattern**: CustomRulesLoader uses singleton to cache rules
- **Repository Pattern**: `src/database/repositories.py` handles all CRUD operations
- **Parser Design**: Each parser merges built-in rules with custom rules on instantiation
- **Theme**: Dark blue color scheme defined in `src/gui/theme.py`

## Testing

### Run All Tests
```bash
pytest tests/
```

### Run Parser Tests Only
```bash
pytest tests/parsers/ -v
```

### Run Specific Parser Tests
```bash
pytest tests/parsers/css/ -v    # CSS parser tests
pytest tests/parsers/html/ -v   # HTML parser tests
pytest tests/parsers/js/ -v     # JS parser tests
```

### Manual JS Validation
See `tests/validation/js/README.md` and `CHECKLIST.md` for manual testing procedures.

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

## Parser Feature Coverage

| Parser | Features Mapped | Notes |
|--------|-----------------|-------|
| HTML   | 100+ elements, attributes, input types | Semantic, form, media elements |
| CSS    | 150+ properties, selectors, at-rules | Grid, flexbox, modern features |
| JS     | 278 Can I Use feature IDs | APIs, methods, syntax features |

## JS Parser Notes
The JS parser includes:
- **Parent feature handling**: Methods like `.then()`, `.resolve()` map to parent features (promises)
- **False positive prevention**: Common programming verbs and React component names are filtered
- **Directive detection**: `"use strict"` and `"use asm"` detected before string removal
- **Template literal handling**: Preserves `${...}` structure for detection
