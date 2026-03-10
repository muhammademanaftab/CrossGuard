# Chapter 2

## 2. User Documentation

### 2.1 Introduction

Welcome to Cross Guard, a browser compatibility checker for web development. This application analyzes HTML, CSS, and JavaScript source files and reports which web platform features may not work correctly in the target browsers. The system offers two interfaces, a desktop GUI for interactive use and a production CLI for CI/CD pipelines, both sharing the same analysis backend, ensuring identical results regardless of how the tool is used.

### 2.2 Used Methods and Tools

The system integrates a combination of parsing libraries, analysis techniques, and frameworks to provide accurate browser compatibility checking:

1. **Python 3.9+**: The core programming language, chosen for its rich ecosystem of parsing libraries and cross-platform compatibility.

2. **BeautifulSoup4 + lxml**: HTML parsing library used to traverse the DOM tree and detect HTML elements, attributes, and input types that correspond to Can I Use features.

3. **tinycss2**: A CSS parsing library that produces an Abstract Syntax Tree (AST) from CSS stylesheets, enabling accurate detection of CSS properties, selectors, at-rules, and values.

4. **tree-sitter 0.21.3 + tree-sitter-languages 1.10.2**: An incremental parsing library that produces ASTs for JavaScript code, enabling detection of syntax features, API usage, and modern language constructs.

5. **Can I Use Database**: A comprehensive community-maintained database of browser support data for web platform features. Cross Guard uses a local JSON copy that can be updated via the CLI.

6. **CustomTkinter**: A modern UI framework for Python based on Tkinter, used to build the desktop GUI with a dark theme and responsive layout.

7. **TkinterDnD2**: Drag-and-drop extension for Tkinter, enabling file upload by dragging files onto the application window.

8. **Click**: A Python package for creating command-line interfaces, used for the production CLI with support for nested commands, options, and help text.

9. **SQLite**: A lightweight embedded database used for persistent storage of analysis history, bookmarks, tags, and user settings.

10. **reportlab**: A PDF generation library used to create professional analysis reports.

11. **Git**: Version control system used throughout development.

### 2.3 User Guide

#### Hardware Requirements

Cross Guard can run on systems with the following hardware configurations as shown in Table 1 below.

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Processor | 2.0 GHz dual-core | 3.0 GHz or faster quad-core |
| Memory | 4 GB RAM | 8 GB RAM or more |
| Disk Space | 100 MB | 500 MB (with Can I Use data) |
| Display | 1024 x 768 resolution | Full HD (1920 x 1080 resolution) |

*Table 1: Hardware Requirements*

Running the application on computers that do not meet the minimum requirements may lead to performance issues. Acceptable performance may be achieved on systems with alternative hardware configurations, such as recent quad-core processors with lower clock speeds and more RAM.

#### Software Requirements

| Component | Required Version |
|-----------|-----------------|
| Operating System | Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+) |
| Python | 3.9 or higher (3.9, 3.10, 3.11, 3.12 supported) |
| pip | Latest version |

*Table 2: Software Requirements*

### 2.4 Setting Up Cross Guard Locally

This guide will help you set up and run Cross Guard on your local machine. Follow these steps carefully to get the project up and running.

#### 1. Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Python** (3.9 to 3.12): Required to run the application.
- **pip**: Python package manager (included with Python).
- **Git**: To clone the repository (optional).

##### 1.1 Installing Python

1. Download and install Python 3.9+ from the official Python website.
2. After installation, verify by opening a terminal and running:

```bash
python --version
```

This should return Python 3.9+.

#### 2. Setting Up the Project Locally

##### 2.1 Cloning the Repository

1. Open your terminal (Command Prompt, Git Bash, or Terminal on Mac).
2. Navigate to the directory where you want to clone the project:

```bash
cd ~/projects
```

3. Clone the repository using Git:

```bash
git clone [repository-url]
```

4. After cloning, navigate into the project directory:

```bash
cd cross-guard
```

##### 2.2 Installing Dependencies

1. Inside the project directory, ensure you have Python 3.9+ installed.
2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies by running:

```bash
pip install -r requirements.txt
```

Alternatively, install with optional dependency groups:

```bash
pip install -e ".[gui]"       # For GUI usage
pip install -e ".[cli]"       # For CLI usage
pip install -e ".[gui,cli]"   # For both GUI and CLI
```

#### 3. Running the Application

##### 3.1 Starting the GUI

1. In your terminal, ensure you are in the project directory.
2. Run the following command to start the GUI:

```bash
python run_gui.py
```

3. The GUI window will open with the file upload view. You can now drag-and-drop files or use the file picker to select files for analysis.

##### 3.2 Using the CLI

Once set up, you can analyze files from the command line:

```bash
# Analyze a single file
python -m src.cli.main analyze path/to/file.js --format table

# Analyze a directory
python -m src.cli.main analyze path/to/project/ --format json

# View all available commands
python -m src.cli.main --help
```

#### 4. Troubleshooting

##### 4.1 Common Errors

- **Missing Dependencies**: If you get errors like ModuleNotFoundError, ensure that all dependencies are installed correctly using `pip install -r requirements.txt`.
- **tree-sitter version conflict**: Cross Guard requires `tree-sitter==0.21.3` specifically. If you have a different version, uninstall and reinstall: `pip install tree-sitter==0.21.3 tree-sitter-languages==1.10.2`.
- **tkinter not found (Linux)**: On Linux, install the system package: `sudo apt-get install python3-tk`.

##### 4.2 Database Issues

- The SQLite database (`crossguard.db`) is auto-created on first run. If it becomes corrupted, simply delete it and it will be recreated.
- Database schema is automatically migrated when upgrading Cross Guard.

### 2.5 Features of Cross Guard: GUI

The Cross Guard GUI provides an interactive desktop application for analyzing web files. The app includes the following key features:

#### 1. File Upload (Drag-and-Drop)

- **What It Does**: Allows users to upload HTML, CSS, and JavaScript files for analysis by dragging them onto the application window or using a file picker dialog.
- **How to Use It**:
  1. Open Cross Guard by running `python run_gui.py`.
  2. Drag files from your file explorer onto the drop zone, or click "Browse Files" to open a file picker.
  3. Selected files appear in the file table with their type and path.
  4. Click "Analyze" to start the compatibility check.

[Figure 1: File Upload - Drop Zone]

[Figure 2: File Upload - File Table with Selected Files]

#### 2. Results Dashboard

- **What It Does**: Displays the analysis results with a compatibility score, letter grade, and detailed breakdown of features and their support status. As shown in fig. 3 and 4.
- **Components**:
  - **Score Card**: Shows the overall compatibility score (0-100) and letter grade (A+ through F).
  - **Browser Cards**: Shows support status for each target browser (Chrome, Firefox, Safari, Edge) with version numbers.
  - **Issue Cards**: Lists each detected feature with its support status, collapsible for detailed information.
  - **Quick Stats**: Summary showing total features, supported count, partial count, and unsupported count.

[Figure 3: Results Dashboard - Score Card and Browser Cards]

[Figure 4: Results Dashboard - Issue Cards]

#### 3. Browser Selector

- **What It Does**: Allows users to choose which browsers and versions to check compatibility against. As shown in fig. 5.
- **How to Use It**:
  1. Click the browser selector in the header area.
  2. Select or deselect browsers (Chrome, Firefox, Safari, Edge).
  3. Optionally change browser versions.
  4. The analysis will use the selected browsers as targets.

[Figure 5: Browser Selector Panel]

#### 4. Analysis History

- **What It Does**: Stores all past analyses in a local SQLite database, allowing users to browse and revisit previous results. As shown in fig. 6 and 7.
- **How to Use It**:
  1. Click "History" in the sidebar to view past analyses.
  2. Each history card shows the file name, score, grade, and date.
  3. Click on a history card to view the full analysis results.
  4. Use the bookmark button to mark important analyses.
  5. Add tags to categorize analyses (e.g., "production", "v2.0", "critical").

[Figure 6: Analysis History View]

[Figure 7: History Card with Bookmark and Tags]

#### 5. Statistics Panel

- **What It Does**: Shows aggregated insights from all past analyses, including score trends, most common problematic features, and file type distribution. As shown in fig. 8.
- **How to Use It**:
  1. Click "Statistics" in the sidebar.
  2. View score trend charts, top problematic features, and summary statistics.

[Figure 8: Statistics Panel]

#### 6. Custom Rules Manager

- **What It Does**: Allows users to add, edit, and delete custom feature detection rules without modifying source code. As shown in fig. 9.
- **How to Use It**:
  1. Click "Custom Rules" in the header bar.
  2. Select the language (CSS, JavaScript, or HTML).
  3. Click "Add Rule" to create a new rule.
  4. Enter the Can I Use feature ID, regex pattern, and description.
  5. Click "Save" to apply the rule. Custom rules show a "Custom" badge with Edit/Delete buttons.

[Figure 9: Custom Rules Manager]

#### 7. Export Reports

- **What It Does**: Exports analysis results as PDF or JSON reports. As shown in fig. 10.
- **How to Use It**:
  1. After analyzing a file, click "Export" in the results view.
  2. Choose the export format (PDF or JSON).
  3. Select the output location and file name.
  4. The report is generated and saved.

[Figure 10: PDF Export Report]

#### 8. Project Scanning

- **What It Does**: Analyzes an entire project directory recursively, detecting frameworks used and providing a project-level compatibility report. As shown in fig. 11 and 12.
- **How to Use It**:
  1. Click "Scan Project" or select a directory for analysis.
  2. Configure scan settings (exclude patterns, target browsers).
  3. The scanner detects all HTML, CSS, and JS files and analyzes them.
  4. Results show a project tree with per-file scores and an aggregated project score.

[Figure 11: Project Scan - Configuration Panel]

[Figure 12: Project Scan - Results with File Tree]

### 2.6 Features of Cross Guard: CLI

The CLI provides a command-line interface for automated analysis, CI/CD integration, and scripting.

#### 1. File and Directory Analysis

```bash
# Analyze a single file
python -m src.cli.main analyze file.js --format table

# Analyze a directory
python -m src.cli.main analyze src/ --format json

# Specify target browsers
python -m src.cli.main analyze file.css --browsers "chrome:120,firefox:121"
```

[Figure 13: CLI - Table Output Format]

#### 2. CI/CD Output Formats

Cross Guard supports 6 output formats for integration with different CI/CD platforms:

```bash
# SARIF for GitHub Code Scanning
python -m src.cli.main analyze src/ --format sarif -o results.sarif

# JUnit XML for Jenkins/GitLab CI
python -m src.cli.main analyze src/ --format junit -o results.xml

# Checkstyle XML for SonarQube
python -m src.cli.main analyze src/ --format checkstyle -o results.xml

# CSV for spreadsheets
python -m src.cli.main analyze src/ --format csv -o results.csv

# Multiple simultaneous outputs
python -m src.cli.main analyze src/ --format table --output-sarif r.sarif --output-junit r.xml
```

[Figure 14: CLI - SARIF Output (first 30 lines)]

#### 3. Quality Gates

Quality gates allow CI/CD pipelines to fail when compatibility standards are not met:

```bash
# Fail if score drops below 80%
python -m src.cli.main analyze src/ --fail-on-score 80

# Fail if more than 5 unsupported features
python -m src.cli.main analyze src/ --fail-on-errors 5

# Fail if more than 10 partially supported features
python -m src.cli.main analyze src/ --fail-on-warnings 10
```

Exit codes: `0` = passed, `1` = gate failed, `2` = error.

#### 4. Stdin Support

Pipe file content directly from other tools:

```bash
echo "const x = Promise.resolve();" | python -m src.cli.main analyze --stdin --stdin-filename app.js --format sarif
```

#### 5. CI Configuration Generators

Automatically generate CI/CD configuration files:

```bash
# GitHub Actions workflow
python -m src.cli.main init-ci --provider github

# GitLab CI configuration
python -m src.cli.main init-ci --provider gitlab

# Pre-commit hook configuration
python -m src.cli.main init-hooks --type pre-commit
```

#### 6. Verbosity and Color Control

```bash
python -m src.cli.main -v analyze file.js          # verbose
python -m src.cli.main -q analyze file.js          # quiet mode
python -m src.cli.main --no-color analyze file.js   # no ANSI colors
python -m src.cli.main --timing analyze file.js     # show elapsed time
```

#### 7. Configuration

Cross Guard supports layered configuration with the following precedence (highest to lowest):

1. CLI flags
2. `crossguard.config.json` (in current or parent directories)
3. `package.json` "crossguard" key (for JavaScript projects)
4. Built-in defaults

```bash
# Initialize a configuration file
python -m src.cli.main config --init

# Show current configuration
python -m src.cli.main config
```

#### 8. .crossguardignore

Create a `.crossguardignore` file to exclude files from analysis (gitignore-compatible syntax):

```
node_modules/
dist/
*.min.js
*.test.js
```

---

#### Troubleshooting and FAQs

- **Q: I get ModuleNotFoundError when running Cross Guard. What should I do?**
  - Ensure all dependencies are installed with `pip install -r requirements.txt`.

- **Q: The CLI is not producing any output.**
  - Make sure you have specified a `--format` option (e.g., `--format table` or `--format json`).

- **Q: How do I update the Can I Use database?**
  - Run `python -m src.cli.main update-db` to fetch the latest browser support data.
