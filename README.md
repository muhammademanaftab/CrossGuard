# Cross Guard - Browser Compatibility Checker

A desktop application that analyzes HTML, CSS, and JavaScript files for cross-browser compatibility issues.

## Overview

Cross Guard helps developers check if their code will work properly across different web browsers (Chrome, Firefox, Safari, Edge). It automatically scans your HTML, CSS, and JavaScript files and generates detailed compatibility reports.

## Features

- ✅ **Offline Analysis** - Works completely offline using local Can I Use database
- ✅ **Multi-Format Support** - Analyzes HTML, CSS, and JavaScript files
- ✅ **Visual Reports** - Charts and tables showing compatibility scores
- ✅ **Export Options** - Save reports as PDF or JSON
- ✅ **Detailed Issues** - Lists all compatibility problems with severity levels
- ✅ **Browser Selection** - Choose which browsers to test against

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python src/main.py
```

## Project Structure

```
Project/
├── caniuse/              # Can I Use database (already included)
├── src/                  # Application source code
│   ├── gui/             # User interface components
│   ├── parsers/         # HTML/CSS/JS parsers
│   ├── analyzer/        # Compatibility analysis engine
│   ├── reporters/       # Report generation
│   └── utils/           # Configuration and utilities
├── tests/               # Unit tests
├── examples/            # Sample files for testing
└── requirements.txt     # Python dependencies
```

## Usage

1. Launch the application
2. Select your HTML, CSS, and JavaScript files
3. Choose target browsers
4. Click "Analyze"
5. View results and export reports

## Development Status

🚧 **Currently in development** - Version 0.1.0

## License

This project uses the Can I Use database under CC BY 4.0 license.
Source: https://caniuse.com/
