# Chapter 2

## 2. User Documentation

### 2.1 Introduction

Cross Guard is a browser compatibility checker for web development. The application analyzes HTML, CSS, and JavaScript source files and reports web platform features that may not work correctly in selected target browsers.

Cross Guard provides two interfaces:

- Desktop Graphical User Interface (GUI) for interactive analysis
- Command Line Interface (CLI) for automation and CI/CD pipelines

Both interfaces share the same analysis backend, ensuring identical results regardless of how the tool is used.

### 2.2 Used Methods and Tools

The system integrates parsing libraries, analysis techniques, and frameworks to perform browser compatibility checking.

1. **Python 3.9+**: Core programming language used to build the application.

2. **BeautifulSoup4 + lxml**: HTML parsing libraries used to traverse the DOM tree and detect HTML elements, attributes, and input types that correspond to Can I Use features.

3. **tinycss2**: CSS parsing library that generates an Abstract Syntax Tree (AST) from stylesheets to detect CSS properties, selectors, at rules, and values.

4. **tree-sitter 0.21.3 + tree-sitter-languages 1.10.2**: JavaScript parsing library that produces AST structures for detecting syntax features, API usage, and modern language constructs.

5. **Regular Expressions (regex)**: Used as a fallback detection method in CSS and JavaScript parsers for pattern matching. Regex is also used as the primary mechanism for defining custom rules.

6. **Can I Use Database**: Community maintained database containing browser compatibility data. Cross Guard uses a local JSON copy that can be updated through the CLI.

7. **CustomTkinter**: Framework used to build the desktop GUI with a modern dark theme interface.

8. **TkinterDnD2**: Provides drag and drop functionality for uploading files.

9. **Click**: Python library used to build the command line interface.

10. **SQLite**: Embedded database used to store analysis history, bookmarks, tags, and user settings.

11. **reportlab**: Library used for PDF report generation.

12. **Git**: Version control system used during development.

### 2.3 User Guide

#### 2.3.1 Hardware Requirements

Cross Guard can run on systems with the following hardware configurations.

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Processor | 2.0 GHz dual core | 3.0 GHz quad core |
| Memory | 4 GB RAM | 8 GB RAM or more |
| Disk Space | 100 MB | 500 MB (with Can I Use data) |
| Display | 1024 x 768 | 1920 x 1080 |

*Table 1: Hardware Requirements*

Running the application on computers that do not meet the minimum requirements may lead to performance issues.

#### 2.3.2 Software Requirements

| Component | Required Version |
|-----------|-----------------|
| Operating System | Windows 10+, macOS 12+, Linux (Ubuntu 20.04+) |
| Python | 3.9 to 3.12 |
| pip | Latest version |

*Table 2: Software Requirements*

### 2.4 Setting Up Cross Guard Locally

This section explains how to install and run Cross Guard locally.

#### 2.4.1 Prerequisites

Ensure the following tools are installed:

- Python 3.9 to 3.12
- pip (included with Python)
- Git (optional)

**Installing Python**

Download Python from the official Python website and verify installation:

```bash
python --version
```

#### 2.4.2 Cloning the Repository

```bash
cd ~/projects
git clone [repository-url]
cd cross-guard
```

#### 2.4.3 Installing Dependencies

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
```

Activate the environment.

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

- **Mac / Linux:**
  ```bash
  source venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional installation modes:

```bash
pip install -e ".[gui]"
pip install -e ".[cli]"
pip install -e ".[gui,cli]"
```

### 2.5 Running the Application

#### 2.5.1 Starting the GUI

Run the following command:

```bash
python run_gui.py
```

The GUI window will open with the file upload interface where users can drag and drop files or select them using the file picker.

#### 2.5.2 Using the CLI

Example commands:

```bash
# Analyze a single file
python -m src.cli.main analyze path/to/file.js --format table

# Analyze a directory
python -m src.cli.main analyze path/to/project/ --format json

# Show CLI help
python -m src.cli.main --help
```

### 2.6 Troubleshooting

#### 2.6.1 Common Errors

**Missing Dependencies**

```bash
pip install -r requirements.txt
```

**tree-sitter version conflict**

```bash
pip install tree-sitter==0.21.3 tree-sitter-languages==1.10.2
```

**tkinter not found (Linux)**

```bash
sudo apt-get install python3-tk
```

#### 2.6.2 Database Issues

The SQLite database crossguard.db is automatically created on first run. If the file becomes corrupted, delete it and restart the application.

### 2.7 Features of Cross Guard: GUI

The Cross Guard GUI provides an interactive desktop application for analyzing web files.

#### 2.7.1 File Upload (Drag and Drop)

**What It Does**

Allows users to upload HTML, CSS, and JavaScript files for compatibility analysis.

**How to Use**

1. Run `python run_gui.py`
2. Drag files onto the drop zone or click Browse Files
3. Click Analyze

[Figure 1: File Upload - Drop Zone]

[Figure 2: File Upload - File Table with Selected Files]

#### 2.7.2 Results Dashboard

**What It Does**

Displays the compatibility results after analysis.

**Components**

- Compatibility Score Card showing pass/fail status, percentage score, and progress bar
- Quick Stats row showing Score, Grade, number of Browsers, and total Features
- Baseline Status row showing counts for Widely Available, Newly Available, and Limited features
- What Needs Your Attention section highlighting critical issues and warnings
- Browser Support section (expandable) showing support status per browser
- Detected Features section (expandable) listing all detected features
- Visualizations section (expandable) with charts
- Recommendations section (expandable) with polyfill suggestions

[Figure 3: Results Dashboard]

#### 2.7.3 Browser Selector

**What It Does**

Allows users to choose target browsers and versions for compatibility checks.

**How to Use**

1. Open the browser selector
2. Select browsers (Chrome, Firefox, Safari, Edge)
3. Configure browser versions

[Figure 5: Browser Selector Panel]

#### 2.7.4 Analysis History

**What It Does**

Stores all previous analyses in the SQLite database.

**Features**

- Your Statistics panel showing Total Analyses, Average Score, and Best Score
- Top Problematic Features list showing the most frequently failing features with failure counts
- Recent Analyses list showing each analysis with file name, score, grade, feature count, and date
- Tags and Bookmarks buttons for organizing analyses
- Bookmark (star icon) and delete (x icon) buttons on each history card
- Clear All option to reset history

[Figure 6: Analysis History View]

#### 2.7.5 Custom Rules Manager

**What It Does**

Allows users to define additional detection rules without modifying source code.

**Rule Structure**

- Can I Use feature ID
- Regex pattern
- Description

[Figure 9: Custom Rules Manager]

#### 2.7.6 Export Reports

**What It Does**

Exports analysis results into downloadable reports.

**Supported Formats**

- PDF
- JSON

**How to Export**

1. Run analysis
2. Click Export
3. Select format
4. Choose destination

[Figure 10: PDF Export Report]

#### 2.7.7 Settings

**What It Does**

Provides application configuration options accessible from the sidebar.

**Settings Sections**

- Can I Use Database: Displays total features and the last updated date, with an Update Database button.
- Custom Detection Rules: Shortcut to the rules manager with a Manage Rules button.
- User Preferences:
  - Auto-save to History toggle (automatically save analyses to history)
  - History Limit dropdown (maximum analyses to keep, default 100)
  - Default Browsers checkboxes (Chrome, Firefox, Safari, Edge, Opera, IE)

[Figure 13: Settings Page]

### 2.8 Features of Cross Guard: CLI

The CLI (Command Line Interface) enables automated analysis and integration into CI/CD pipelines. It is built with the Click library and provides eight commands: `analyze`, `history`, `stats`, `export`, `config`, `update-db`, `init-ci`, and `init-hooks`.

All commands use the same analysis backend as the GUI, ensuring identical results.

#### 2.8.1 Commands

The CLI provides several commands for running analyses and managing results.

**analyze** — Analyzes a file or directory for browser compatibility issues.

```bash
python -m src.cli.main analyze examples/sample.css
python -m src.cli.main analyze examples/
python -m src.cli.main analyze file.css --browsers "chrome:120,safari:13"
```

When a directory is analyzed, the CLI scans files recursively and skips common folders such as `node_modules`, `.git`, `dist`, and `build`.

[Figure 14: CLI - Table Output Format]

**history** — Lists previously saved analyses from the SQLite database.

```bash
python -m src.cli.main history
python -m src.cli.main history --limit 5
python -m src.cli.main history --type css
```

**stats** — Displays aggregated statistics across all saved analyses.

```bash
python -m src.cli.main stats
```

**export** — Exports a saved analysis by database ID.

```bash
python -m src.cli.main export 42 --format json --output report.json
python -m src.cli.main export 42 --format pdf --output report.pdf
```

**config** — Shows or initializes configuration settings.

```bash
python -m src.cli.main config
python -m src.cli.main config --init
```

Configuration priority:

1. CLI flags
2. `crossguard.config.json`
3. `package.json` `"crossguard"`
4. Built-in defaults

**update-db** — Updates the local Can I Use database.

```bash
python -m src.cli.main update-db
```

**init-ci** — Generates CI/CD workflow configurations.

```bash
python -m src.cli.main init-ci --provider github
python -m src.cli.main init-ci --provider gitlab
```

**init-hooks** — Creates Git pre-commit hooks for running Cross Guard automatically.

```bash
python -m src.cli.main init-hooks --type pre-commit
```

#### 2.8.2 Output Formats

The `analyze` command supports multiple output formats for different use cases.

| Format | Flag | Use Case |
|--------|------|----------|
| Table | `--format table` | Human-readable terminal output (default) |
| Summary | `--format summary` | One-line quick check |
| JSON | `--format json` | Machine-readable output |
| SARIF | `--format sarif` | GitHub Code Scanning integration |
| JUnit XML | `--format junit` | Jenkins and GitLab CI reports |
| Checkstyle XML | `--format checkstyle` | SonarQube integration |
| CSV | `--format csv` | Spreadsheet analysis |

*Table 3: CLI Output Formats*

Results can be saved to files using the `--output` flag.

```bash
# Save SARIF output
python -m src.cli.main analyze src/ --format sarif -o results.sarif

# Generate multiple outputs
python -m src.cli.main analyze file.css --format table --output-json report.json --output-csv report.csv
```

#### 2.8.3 Global Options

Global options are placed before the command name.

```bash
python -m src.cli.main [options] <command>
```

| Option | Description |
|--------|-------------|
| `-v` | Verbose output |
| `-vv` | More verbose output |
| `-vvv` / `--debug` | Debug-level output |
| `-q` | Quiet mode |
| `--no-color` | Disable ANSI colors |
| `--timing` | Display elapsed time |

*Table 4: CLI Global Options*

All log messages are written to stderr so that stdout remains clean for piped output.

#### 2.8.4 Quality Gates

Quality gates cause the CLI to exit with code 1 if compatibility thresholds are not met.

```bash
# Fail if score below 80
python -m src.cli.main analyze src/ --fail-on-score 80

# Fail if more than 5 unsupported features
python -m src.cli.main analyze src/ --fail-on-errors 5

# Fail if more than 10 partially supported features
python -m src.cli.main analyze src/ --fail-on-warnings 10

# Combine gates
python -m src.cli.main analyze src/ --fail-on-score 80 --fail-on-errors 5
```

Exit codes:

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Quality gate failed |
| 2 | Error (invalid input or missing file) |

*Table 5: CLI Exit Codes*

CI/CD systems use these exit codes to determine whether a build passes or fails.

### 2.9 FAQ

**Q: I get ModuleNotFoundError when running Cross Guard.**

```bash
pip install -r requirements.txt
```

**Q: The CLI is not producing any output.**

Specify a format option such as `--format table`.

**Q: How do I update the Can I Use database?**

```bash
python -m src.cli.main update-db
```
