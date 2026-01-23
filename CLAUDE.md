# Cross Guard - Browser Compatibility Checker

## Project Overview
Cross Guard is a desktop application that analyzes HTML, CSS, and JavaScript files for browser compatibility issues. It uses the Can I Use database to check feature support across major browsers.

## Tech Stack
- **GUI Framework**: CustomTkinter (with TkinterDnD2 for drag-and-drop)
- **Language**: Python 3.9+
- **HTML Parsing**: BeautifulSoup4
- **Data Source**: Can I Use database

## Project Structure
```
src/
├── api/                    # API layer (service facade)
├── analyzer/               # Compatibility analysis logic
│   ├── compatibility.py    # Browser compatibility checker
│   ├── database.py         # Can I Use database wrapper
│   ├── database_updater.py # Database update functionality
│   └── scorer.py           # Compatibility scoring
├── gui/                    # GUI components
│   ├── app.py              # Application entry point
│   ├── main_window.py      # Main window (upload + results pages)
│   ├── theme.py            # Dark blue theme configuration
│   ├── file_selector.py    # File selection with drag-and-drop
│   ├── export_manager.py   # PDF/JSON export
│   └── widgets/            # Reusable UI widgets
│       ├── browser_card.py
│       ├── charts.py
│       ├── drop_zone.py
│       ├── messagebox.py
│       ├── rules_manager.py  # Custom rules UI
│       └── score_card.py
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
    └── types.py            # Type definitions
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

## Custom Rules System
Users can extend feature detection without modifying source code:

### Via GUI
Click "⚙ Custom Rules" button in the header to open the rules manager.

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
- **Parser Design**: Each parser merges built-in rules with custom rules on instantiation
- **Theme**: Dark blue color scheme defined in `src/gui/theme.py`

## Testing
```bash
pytest tests/
```

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
