# EOTVOS LORAND UNIVERSITY
# FACULTY OF INFORMATICS
## DEPT. OF [Your Department]

---

# Cross Guard: Browser Compatibility Checker for Web Development

**Supervisor:** [Supervisor Name]
[Supervisor Title]

**Author:** [Your Name]
B.Sc Computer Science

Budapest, 2026

---

## Thesis Topic Registration Form

**Student's Data:**
- Student's Name: [Your Name]
- Student's Neptun code: [Your Neptun Code]

**Educational Information:**
- Training programme: Computer Science BSc

**Internal Supervisor's Name:** [Supervisor Name]
**Supervisor's Home Institution:** [Department Name]
**Address:** 1117, Budapest, Pazmany Peter setany 1/C.
**Supervisor's Position and Degree:** [Position and Degree]

**Thesis Title:** Cross Guard: Browser Compatibility Checker for Web Development

**Topic of the Thesis:**

"Cross Guard" is a static analysis tool designed to check HTML, CSS, and JavaScript source files for browser compatibility issues. The tool parses web source files, extracts the platform features they use (such as CSS Grid, Promises, or the `<dialog>` element), and looks up each feature in the Can I Use database to determine support status across major browsers.

The system employs Abstract Syntax Tree (AST) parsing techniques for accurate feature extraction: tinycss2 for CSS stylesheets, tree-sitter for JavaScript, and BeautifulSoup4 for HTML. Each analysis produces a weighted compatibility score (0-100), a letter grade, and a per-feature breakdown showing support status across Chrome, Firefox, Safari, and Edge.

Cross Guard provides two frontends sharing a single backend through a service facade pattern: a desktop GUI built with CustomTkinter featuring drag-and-drop file upload, results dashboard, analysis history, and a custom rules editor; and a production CLI built with Click that integrates into CI/CD pipelines with quality gates, SARIF output for GitHub Code Scanning, JUnit XML for Jenkins, and 4 additional export formats.

The tool addresses a real-world need in web development where cross-browser compatibility remains a significant challenge. By providing automated static analysis with actionable reports, Cross Guard helps developers identify compatibility issues before deployment, reducing the cost and effort of cross-browser testing.

Budapest, 2026. [Month]. [Day].

---

## Contents

- Chapter 1: Introduction
  - 1.1 Motivation
  - 1.2 Goals
  - 1.3 Scope of the Project
- Chapter 2: User Documentation
  - 2.1 Introduction
  - 2.2 Used Methods and Tools
  - 2.3 User Guide
  - 2.4 Setting Up Cross Guard Locally
  - 2.5 Features of Cross Guard: GUI
  - 2.6 Features of Cross Guard: CLI
- Chapter 3: Developer Documentation
  - 3.1 Problem Specification
  - 3.2 Tools and Methods Used
  - 3.3 System Architecture
  - 3.4 Data Flow Diagram
  - 3.5 Database Schema
  - 3.6 Design Patterns
  - 3.7 Developer Setup
  - 3.8 Core Components
  - 3.9 Testing
- Chapter 4: Conclusion and Future Work
  - 4.1 Conclusion
  - 4.2 Future Work
- Bibliography
- List of Figures
- Acknowledgment

---

# Chapter 1

## 1. Introduction

### 1.1 Motivation

The web platform today has thousands of features spread across HTML, CSS, and JavaScript. Each of these features has different levels of support in different browsers. Even though browsers have become more similar over the years, there are still many differences, especially with newer features like CSS Container Queries, the `<dialog>` element, or JavaScript's `structuredClone()`. Something that works fine in Chrome might not work at all in Safari, or it might need a special vendor prefix in Firefox.

This is a big problem for web developers. They need to make sure that the code they write works correctly for all of their users, no matter which browser those users have. The usual way to deal with this is to test manually in different browsers, check the Can I Use website one feature at a time, or just rely on experience to know what is safe to use. But all of these methods take a lot of time, are easy to get wrong, and do not work well for large projects with many files.

Cross Guard was built to solve this problem through automation. Instead of checking each feature by hand, Cross Guard reads the source files, finds all the web features used in the code, and looks up each one in the Can I Use database. This way, it can find every compatibility issue in a file, a folder, or a whole project in just a few seconds, turning what used to be hours of manual work into an automatic process.

On top of that, more and more development teams are using CI/CD (Continuous Integration / Continuous Deployment) pipelines to build and deploy their code automatically. These teams need tools that can check for problems on every commit without human intervention. Just like linters check code quality and type checkers verify types, Cross Guard can check browser compatibility automatically, stopping compatibility problems from reaching production.

### 1.2 Goals

The main goal of this project is to build a tool that automatically finds browser compatibility issues in HTML, CSS, and JavaScript source files. More specifically, Cross Guard aims to:

1. **Parse web source files accurately** by using AST-based (Abstract Syntax Tree) parsing with tinycss2 for CSS, tree-sitter for JavaScript, and BeautifulSoup4 for HTML. The parsers extract the web platform features used in the code while keeping false positives to a minimum through careful filtering.

2. **Analyze compatibility** by looking up each detected feature in the Can I Use database and checking its support status in the target browsers (Chrome, Firefox, Safari, Edge). The tool then calculates a weighted compatibility score from 0 to 100 and assigns a letter grade.

3. **Provide two frontends** with a desktop GUI for interactive use and a production CLI for automated pipelines. Both share the same backend through a service facade, so the results are always the same no matter which interface is used.

4. **Work with CI/CD pipelines** by supporting standard output formats like SARIF 2.1.0 (for GitHub Code Scanning), JUnit XML (for Jenkins and GitLab CI), and Checkstyle XML (for SonarQube). It also provides quality gates that can fail a build when compatibility drops below a set threshold.

5. **Be extensible** through a custom rules system that lets users define their own feature detection patterns without changing the source code. Users can also configure which browsers and versions to target.

6. **Save analysis history** in a local SQLite database, so users can look back at past results, bookmark important analyses, and organize them with tags.

### 1.3 Scope of the Project

The scope of Cross Guard covers the following areas:

1. **Multi-Language Source Parsing**
   The tool parses three web languages (HTML, CSS, and JavaScript) using dedicated parsers. Each parser uses AST (Abstract Syntax Tree) techniques to accurately extract features from the code. The HTML parser can detect over 100 elements, attributes, and input types. The CSS parser detects over 150 properties, selectors, and at-rules. The JavaScript parser can detect 278 Can I Use feature IDs using a 3-tier strategy: AST node types, AST identifiers, and regex fallback.

2. **Compatibility Analysis Engine**
   For each detected feature, the analyzer looks it up in the Can I Use database and calculates a weighted compatibility score. Features are sorted into three categories for each target browser: supported, partially supported, or unsupported. The scoring algorithm takes into account browser importance, prefix-only support, features that are disabled by default, and partial implementations.

3. **Desktop GUI Application**
   A desktop application built with CustomTkinter that includes drag-and-drop file upload, a results dashboard with score cards, browser cards, and issue cards. It also has analysis history with bookmarks and tags, a statistics panel, and a visual editor for custom rules.

4. **Production CLI with CI/CD Integration**
   A command-line interface built with Click that supports 6 export formats (JSON, PDF, SARIF, JUnit XML, Checkstyle XML, CSV). It includes quality gates for automated builds, stdin support for piped content, `.crossguardignore` file exclusion, and CI configuration generators for GitHub Actions, GitLab CI, and pre-commit hooks.

5. **Project-Level Analysis**
   The tool can scan entire project directories recursively. It detects which frameworks are being used (React, Vue, Angular, etc.) and produces an aggregated compatibility report for the whole project.

6. **Polyfill Recommendations**
   When the tool finds unsupported features, it automatically suggests polyfills that can fix the compatibility issues. This helps developers find solutions quickly.

7. **Machine Learning Risk Prediction**
   An optional ML module built with scikit-learn that predicts compatibility risk levels based on the patterns of feature usage in the code. This gives developers a heads-up about potential problems before they become real issues.

8. **Data Persistence**
   A SQLite database with 8 tables that stores analysis history, user settings, bookmarks, and tags. The database has schema versioning and handles migrations automatically when upgrading.

---

# Chapter 2

## 2. User Documentation

### 2.1 Introduction

Welcome to Cross Guard, a browser compatibility checker for web development. Cross Guard analyzes HTML, CSS, and JavaScript source files and reports which web platform features may not work correctly in your target browsers.

Cross Guard is designed for two types of users:

- **GUI users**: Web developers who want to quickly check individual files or small projects through an interactive desktop application with drag-and-drop support, visual results, and analysis history.

- **CLI users**: DevOps engineers and teams who want to integrate compatibility checking into their CI/CD pipelines, enforcing compatibility standards on every commit with machine-readable output formats.

Both interfaces share the same analysis backend, ensuring identical results regardless of how the tool is used.

### 2.2 Used Methods and Tools

The system integrates a combination of parsing libraries, analysis techniques, and frameworks to provide accurate browser compatibility checking:

1. **Python 3.9+**: The core programming language, chosen for its rich ecosystem of parsing libraries and cross-platform compatibility.

2. **BeautifulSoup4 + lxml**: HTML parsing library used to traverse the DOM tree and detect HTML elements, attributes, and input types that correspond to Can I Use features.

3. **tinycss2**: A CSS parsing library that produces an Abstract Syntax Tree (AST) from CSS stylesheets, enabling accurate detection of CSS properties, selectors, at-rules, and values.

4. **tree-sitter 0.21.3 + tree-sitter-languages 1.10.2**: An incremental parsing library that produces ASTs for JavaScript code, enabling detection of syntax features (optional chaining, nullish coalescing), API usage (Promises, Fetch, IntersectionObserver), and modern language constructs (private fields, class properties).

5. **Can I Use Database**: A comprehensive community-maintained database of browser support data for web platform features. Cross Guard uses a local JSON copy that can be updated to reflect the latest browser releases.

6. **CustomTkinter**: A modern-looking UI framework for Python based on Tkinter, used to build the desktop GUI with a dark theme and responsive layout.

7. **TkinterDnD2**: Drag-and-drop extension for Tkinter, enabling file upload by dragging files onto the application window.

8. **Click**: A Python package for creating command-line interfaces, used for the production CLI with support for nested commands, options, and help text.

9. **SQLite**: A lightweight embedded database used for persistent storage of analysis history, bookmarks, tags, and user settings.

10. **reportlab**: A PDF generation library used to create professional analysis reports with score cards, browser breakdowns, and feature details.

11. **scikit-learn**: A machine learning library used in the optional ML module for compatibility risk prediction based on feature usage patterns.

12. **Git**: Version control system used throughout development.

### 2.3 User Guide

#### Hardware Requirements

Cross Guard is a desktop application and CLI tool that can run on systems with the following hardware configurations:

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Processor | 2.0 GHz dual-core | 3.0 GHz or faster quad-core |
| Memory | 4 GB RAM | 8 GB RAM or more |
| Disk Space | 100 MB (application + database) | 500 MB (with Can I Use data) |
| Display | 1024 x 768 resolution | 1920 x 1080 resolution |

Table 1: Hardware Requirements

#### Software Requirements

| Component | Required Version |
|-----------|-----------------|
| Operating System | Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+) |
| Python | 3.9 or higher (3.9, 3.10, 3.11, 3.12 supported) |
| pip | Latest version |

Table 2: Software Requirements

#### Optional Dependencies

Cross Guard uses optional dependency groups to minimize the installation footprint:

| Group | Purpose | Install Command |
|-------|---------|----------------|
| `gui` | Desktop GUI (CustomTkinter, drag-and-drop, PDF export, charts) | `pip install crossguard[gui]` |
| `cli` | Command-line interface (Click) | `pip install crossguard[cli]` |
| `ml` | Machine learning risk prediction (scikit-learn) | `pip install crossguard[ml]` |
| `dev` | Development tools (pytest, coverage) | `pip install crossguard[dev]` |

Table 3: Optional Dependency Groups

### 2.4 Setting Up Cross Guard Locally

This guide walks through setting up and running Cross Guard on a local machine.

#### 1. Prerequisites

Before you begin, ensure the following are installed:

- **Python 3.9+**: Download from https://www.python.org/downloads/
- **pip**: Included with Python. Verify with: `pip --version`
- **Git**: Download from https://git-scm.com/ (optional, for cloning)

#### 2. Installation

##### 2.1 Clone the Repository

Open a terminal and run:

```bash
git clone [repository-url]
cd cross-guard
```

##### 2.2 Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

##### 2.3 Install Dependencies

For GUI usage:
```bash
pip install -e ".[gui]"
```

For CLI usage:
```bash
pip install -e ".[cli]"
```

For all features (GUI + CLI + ML):
```bash
pip install -e ".[gui,cli,ml]"
```

For development (includes testing tools):
```bash
pip install -e ".[gui,cli,ml,dev]"
```

#### 3. Running the Application

##### 3.1 Starting the GUI

```bash
python run_gui.py
```

The GUI window will open with the file upload view. You can now drag-and-drop files or use the file picker to select files for analysis.

[Figure 1: Cross Guard GUI — Main Upload View]

##### 3.2 Using the CLI

Analyze a single file:
```bash
python -m src.cli.main analyze path/to/file.js --format table
```

Analyze a directory:
```bash
python -m src.cli.main analyze path/to/project/ --format json
```

View all available commands:
```bash
python -m src.cli.main --help
```

[Figure 2: Cross Guard CLI — Terminal Output]

#### 4. Troubleshooting

##### 4.1 Common Errors

- **ModuleNotFoundError**: Ensure all dependencies are installed with the correct optional group (e.g., `pip install -e ".[gui]"` for GUI).
- **tree-sitter version conflict**: Cross Guard requires `tree-sitter==0.21.3` specifically. If you have a different version, uninstall and reinstall: `pip install tree-sitter==0.21.3 tree-sitter-languages==1.10.2`.
- **tkinter not found (Linux)**: On Linux, install the system package: `sudo apt-get install python3-tk`.

##### 4.2 Database Issues

- The SQLite database (`crossguard.db`) is auto-created on first run. If it becomes corrupted, simply delete it and it will be recreated.
- Database schema is automatically migrated when upgrading Cross Guard.

### 2.5 Features of Cross Guard: GUI

The Cross Guard GUI provides an interactive desktop application for analyzing web files.

#### 1. File Upload (Drag-and-Drop)

- **What It Does**: Allows users to upload HTML, CSS, and JavaScript files for analysis by dragging them onto the application window or using a file picker dialog.
- **How to Use It**:
  1. Open Cross Guard by running `python run_gui.py`.
  2. Drag files from your file explorer onto the drop zone, or click "Browse Files" to open a file picker.
  3. Selected files appear in the file table with their type and path.
  4. Click "Analyze" to start the compatibility check.

[Figure 3: File Upload — Drop Zone]

[Figure 4: File Upload — File Table with Selected Files]

#### 2. Results Dashboard

- **What It Does**: Displays the analysis results with a compatibility score, letter grade, and detailed breakdown of features and their support status.
- **Components**:
  - **Score Card**: Shows the overall compatibility score (0-100) and letter grade (A+ through F).
  - **Browser Cards**: Shows support status for each target browser (Chrome, Firefox, Safari, Edge) with version numbers.
  - **Issue Cards**: Lists each detected feature with its support status, collapsible for detailed information.
  - **Quick Stats**: Summary showing total features, supported count, partial count, and unsupported count.

[Figure 5: Results Dashboard — Score Card]

[Figure 6: Results Dashboard — Browser Cards]

[Figure 7: Results Dashboard — Issue Cards (Collapsed)]

[Figure 8: Results Dashboard — Issue Card (Expanded)]

#### 3. Browser Selector

- **What It Does**: Allows users to choose which browsers and versions to check compatibility against.
- **How to Use It**:
  1. Click the browser selector in the header area.
  2. Select or deselect browsers (Chrome, Firefox, Safari, Edge).
  3. Optionally change browser versions.
  4. The analysis will use the selected browsers as targets.

[Figure 9: Browser Selector Panel]

#### 4. Analysis History

- **What It Does**: Stores all past analyses in a local SQLite database, allowing users to browse, search, and revisit previous results.
- **How to Use It**:
  1. Click "History" in the sidebar to view past analyses.
  2. Each history card shows the file name, score, grade, and date.
  3. Click on a history card to view the full analysis results.
  4. Use the bookmark button to mark important analyses.
  5. Add tags to categorize analyses (e.g., "production", "v2.0", "critical").

[Figure 10: Analysis History View]

[Figure 11: History Card with Bookmark and Tags]

#### 5. Statistics Panel

- **What It Does**: Shows aggregated insights from all past analyses, including score trends, most common problematic features, and file type distribution.
- **How to Use It**:
  1. Click "Statistics" in the sidebar.
  2. View score trend charts, top problematic features, and summary statistics.

[Figure 12: Statistics Panel — Score Trends]

[Figure 13: Statistics Panel — Top Problematic Features]

#### 6. Custom Rules Manager

- **What It Does**: Allows users to add, edit, and delete custom feature detection rules without modifying source code. This is useful for project-specific patterns or features not yet covered by the built-in rules.
- **How to Use It**:
  1. Click "Custom Rules" in the header bar.
  2. Select the language (CSS, JavaScript, or HTML).
  3. Click "Add Rule" to create a new rule.
  4. Enter the Can I Use feature ID, regex pattern, and description.
  5. Click "Save" to apply the rule.

[Figure 14: Custom Rules Manager]

#### 7. Export Reports

- **What It Does**: Exports analysis results as PDF or JSON reports.
- **How to Use It**:
  1. After analyzing a file, click "Export" in the results view.
  2. Choose the export format (PDF or JSON).
  3. Select the output location and file name.
  4. The report is generated and saved.

[Figure 15: PDF Export Report]

#### 8. Project Scanning

- **What It Does**: Analyzes an entire project directory recursively, detecting frameworks used and providing a project-level compatibility report.
- **How to Use It**:
  1. Click "Scan Project" or select a directory for analysis.
  2. Configure scan settings (exclude patterns, target browsers).
  3. The scanner detects all HTML, CSS, and JS files and analyzes them.
  4. Results show a project tree with per-file scores and an aggregated project score.

[Figure 16: Project Scan — Configuration Panel]

[Figure 17: Project Scan — Results with File Tree]

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

[Figure 18: CLI — Table Output Format]

#### 2. CI/CD Output Formats

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

#### 3. Quality Gates

Quality gates allow CI/CD pipelines to fail when compatibility standards are not met:

```bash
# Fail if score drops below 80%
python -m src.cli.main analyze src/ --fail-on-score 80

# Fail if more than 5 unsupported features
python -m src.cli.main analyze src/ --fail-on-errors 5

# Fail if more than 10 partially supported features
python -m src.cli.main analyze src/ --fail-on-warnings 10

# Combine multiple gates
python -m src.cli.main analyze src/ --fail-on-score 80 --fail-on-errors 5
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

#### 7. Configuration File

Cross Guard supports layered configuration:

```bash
# Initialize a configuration file
python -m src.cli.main config --init

# Show current configuration
python -m src.cli.main config
```

Configuration is loaded with the following precedence (highest to lowest):
1. CLI flags
2. `crossguard.config.json` (in current or parent directories)
3. `package.json` "crossguard" key (for JavaScript projects)
4. Built-in defaults

#### 8. .crossguardignore

Create a `.crossguardignore` file to exclude files from analysis (gitignore-compatible syntax):

```
node_modules/
dist/
*.min.js
*.test.js
```

---

# Chapter 3

## 3. Developer Documentation

### 3.1 Problem Specification

Cross Guard is a static analysis tool that detects browser compatibility issues in web source files. The core problem is:

**Given** a set of HTML, CSS, and/or JavaScript source files and a set of target browsers (e.g., Chrome 120, Firefox 121, Safari 17, Edge 120),
**Detect** all web platform features used in those files,
**Determine** the support status of each feature in each target browser using the Can I Use database,
**Produce** a compatibility score, letter grade, and detailed per-feature breakdown.

The system must handle:

- **HTML features**: Elements (`<dialog>`, `<details>`, `<picture>`), attributes (`loading="lazy"`, `inputmode`), input types (`date`, `color`, `range`).
- **CSS features**: Properties (`container-type`, `aspect-ratio`), selectors (`:has()`, `:is()`), at-rules (`@layer`, `@container`), values (`fit-content`, `dvh` units).
- **JavaScript features**: APIs (`IntersectionObserver`, `ResizeObserver`), syntax (`?.`, `??`, `#privateField`), methods (`.at()`, `.replaceAll()`), constructors (`new URL()`, `new AbortController()`).

Each feature must be mapped to its corresponding Can I Use feature ID for lookup. False positives must be minimized through contextual analysis (e.g., distinguishing between a CSS property named `grid` and a JavaScript variable named `grid`).

### 3.2 Tools and Methods Used

#### 3.2.1 Parsing Methods

**HTML Parsing — BeautifulSoup4 + lxml**

BeautifulSoup4 with the lxml backend is used to parse HTML into a DOM tree. The parser traverses all elements and checks element names, attribute names, and attribute values against a mapping of Can I Use feature IDs defined in `html_feature_maps.py`.

**CSS Parsing — tinycss2 (AST-Based)**

tinycss2 parses CSS stylesheets into an Abstract Syntax Tree, providing structured access to:
- `QualifiedRule` nodes (selectors + declaration blocks)
- `AtRule` nodes (`@media`, `@keyframes`, `@container`, etc.)
- `Declaration` nodes (property-value pairs within blocks)

The CSS parser uses `tinycss2.parse_stylesheet()` with `skip_comments=True` and `skip_whitespace=True`, then walks the AST to extract properties, selectors, and at-rules. Each is matched against the mappings in `css_feature_maps.py` (150+ features).

**JavaScript Parsing — tree-sitter (AST-Based) + Regex Fallback**

The JavaScript parser uses a 3-tier detection strategy:

1. **Tier 1 — AST Node Types**: tree-sitter produces an AST where syntax features correspond to specific node types. For example, optional chaining (`?.`) produces an `optional_chain` child of a `member_expression`, and nullish coalescing (`??`) appears as a `binary_expression` with a `??` operator.

2. **Tier 2 — AST Identifiers and Calls**: The parser walks the AST to find `member_expression`, `call_expression`, and `new_expression` nodes, then matches identifier names against the API mappings in `js_feature_maps.py` (278 features).

3. **Tier 3 — Regex on AST-Cleaned Text**: For patterns not easily captured by AST walking, the parser falls back to regex matching on the source text with comments and string literals stripped (to prevent false positives from code appearing inside strings or comments).

#### 3.2.2 Compatibility Analysis

The analyzer takes the list of detected Can I Use feature IDs and, for each feature, looks up the support data in the Can I Use database. Support statuses are:

| Status Code | Meaning | Score Value |
|-------------|---------|-------------|
| `y` | Fully supported | 100 |
| `a` | Almost supported | 100 |
| `x` | Requires prefix | 70 |
| `p` | Partial support | 50 |
| `d` | Disabled by default | 30 |
| `n` | Not supported | 0 |
| `u` | Unknown | 0 |

Table 4: Can I Use Support Status Codes and Score Values

The compatibility scorer computes a weighted score using configurable browser weights (default: all browsers weighted equally at 1.0).

#### 3.2.3 Development Tools

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Core programming language |
| CustomTkinter 5.2+ | Desktop GUI framework |
| Click 8.1+ | CLI framework |
| SQLite | Persistent storage (analysis history, settings) |
| reportlab | PDF report generation |
| scikit-learn | ML risk prediction (optional) |
| pytest | Testing framework |
| Git | Version control |

Table 5: Development Tools

### 3.3 System Architecture

Cross Guard follows a layered architecture with strict dependency rules:

```
┌──────────────────┐  ┌──────────────────┐
│      GUI         │  │      CLI         │     Frontends
│  (CustomTkinter) │  │    (Click)       │     Import only from src/api/
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────┐
│         API Facade (src/api/)           │     Service Layer
│  AnalyzerService — 59 methods           │     Data contracts (schemas.py)
│  schemas.py + project_schemas.py        │     Single entry point for all operations
└────────────────┬────────────────────────┘
                 │
     ┌───────────┼───────────┬──────────────┐
     ▼           ▼           ▼              ▼
 Parsers     Analyzer     Database       Export      Backend
(HTML/CSS/JS) (scoring)  (SQLite)    (6 formats)    No frontend imports
```

Figure 19: System Architecture — Layer Diagram

**Key architectural rules:**
- The GUI imports only from `src/api/` (AnalyzerService, schemas)
- The CLI imports only from `src/api/` (AnalyzerService) and `src/config/`
- Neither frontend imports directly from parsers, analyzer, or database modules
- All logging goes to stderr (never stdout) to keep piped CLI output clean

#### Class Diagram — AnalyzerService (Facade)

The `AnalyzerService` class acts as the central facade, providing 59 methods organized into functional groups:

| Method Group | Count | Examples |
|-------------|-------|---------|
| Analysis | 5 | `analyze()`, `analyze_files()`, `analyze_project()` |
| History | 6 | `save_analysis_to_history()`, `get_analysis_history()`, `delete_from_history()` |
| Statistics | 3 | `get_statistics()`, `get_score_trend()`, `get_top_problematic_features()` |
| Settings | 5 | `get_setting()`, `set_setting()`, `get_all_settings()` |
| Bookmarks | 7 | `add_bookmark()`, `remove_bookmark()`, `toggle_bookmark()` |
| Tags | 8 | `create_tag()`, `delete_tag()`, `add_tag_to_analysis()` |
| Export | 4 | `export_json()`, `export_pdf()`, `export_report()` |
| Database | 3 | `get_database_info()`, `update_database()`, `reload_custom_rules()` |
| Config | 2 | `get_default_browsers()`, `get_available_browsers()` |
| Custom Rules | 5 | `get_custom_rules()`, `save_custom_rule()`, `delete_custom_rule()` |
| Polyfills | 2 | `get_polyfill_suggestions()` |
| ML | 2 | `predict_risk()`, `get_risk_summary()` |
| Project | 2 | `scan_project()`, `detect_frameworks()` |

Table 6: AnalyzerService Method Groups

[Figure 20: Class Diagram — AnalyzerService]

#### Use Case Diagram

The system supports two primary actors:

1. **GUI User**: Uploads files via drag-and-drop, views results, manages history/bookmarks/tags, exports reports, edits custom rules.
2. **CLI User / CI Pipeline**: Analyzes files/directories, applies quality gates, generates CI configs, exports in machine-readable formats.

[Figure 21: Use Case Diagram]

#### Sequence Diagram — File Analysis

```
User              GUI/CLI           AnalyzerService      Parser          Analyzer        Database
 │                  │                    │                  │                │               │
 │── Upload file ──>│                    │                  │                │               │
 │                  │── analyze() ──────>│                  │                │               │
 │                  │                    │── parse_file() ──>│               │               │
 │                  │                    │                  │── extract ────>│               │
 │                  │                    │<─ feature_ids ───│               │               │
 │                  │                    │── check_compat() ────────────────>│               │
 │                  │                    │                                   │── lookup ────>│
 │                  │                    │<── scores, grades ────────────────│               │
 │                  │                    │── save_history() ─────────────────────────────────>│
 │                  │<── AnalysisResult ─│                                                   │
 │<── Display ──────│                    │                                                   │
```

Figure 22: Sequence Diagram — File Analysis Flow

### 3.4 Data Flow Diagram

```
Input File (HTML/CSS/JS)
    │
    ▼
┌─────────────────────────────────┐
│  Parser (src/parsers/)          │
│  - HTML: BeautifulSoup4         │  Extracts web platform features
│  - CSS:  tinycss2 AST           │  Maps to Can I Use feature IDs
│  - JS:   tree-sitter AST       │  Merges custom rules
│          + regex fallback        │
└──────────────┬──────────────────┘
               │ List[str] — Can I Use feature IDs
               ▼
┌─────────────────────────────────┐
│  Analyzer (src/analyzer/)       │
│  - compatibility.py             │  Looks up each feature in Can I Use DB
│  - scorer.py                    │  Classifies: supported / partial / unsupported
│  - version_ranges.py            │  Computes weighted compatibility score
└──────────────┬──────────────────┘
               │ AnalysisResult dataclass
               ▼
┌─────────────────────────────────┐
│  Output (multiple destinations) │
│  - GUI: Score card, issues      │  Visual dashboard
│  - CLI: table / json / sarif    │  Terminal or machine-readable
│  - Export: PDF / CSV / JUnit    │  Report files
│  - Database: SQLite             │  Persistent history
└─────────────────────────────────┘
```

Figure 23: Data Flow Diagram

### 3.5 Database Schema

Cross Guard uses SQLite with 8 tables across 2 schema versions. Schema migrations are applied automatically on first connection.

#### Entity-Relationship Diagram

```
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────┐
│    analyses      │──1:N──│  analysis_features    │──1:N──│  browser_results  │
│─────────────────│       │──────────────────────│       │──────────────────│
│ id (PK)         │       │ id (PK)              │       │ id (PK)          │
│ file_name       │       │ analysis_id (FK)     │       │ analysis_feat_id │
│ file_path       │       │ feature_id           │       │   (FK)           │
│ file_type       │       │ feature_name         │       │ browser          │
│ overall_score   │       │ category             │       │ version          │
│ grade           │       │                      │       │ support_status   │
│ total_features  │       └──────────────────────┘       └──────────────────┘
│ analyzed_at     │
│ browsers_json   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐  ┌─▼──────────────┐     ┌──────────┐
│bookmarks│ │ analysis_tags  │────>│   tags    │
│────────│  │───────────────│     │──────────│
│ id (PK)│  │ analysis_id   │     │ id (PK)  │
│ analysis│  │   (FK, PK)   │     │ name     │
│  _id(FK)│ │ tag_id(FK,PK)│     │ color    │
│ note   │  │ created_at   │     │created_at│
│created │  └──────────────┘     └──────────┘
│  _at   │
└────────┘

┌──────────┐     ┌─────────────────┐
│ settings │     │ schema_version  │
│──────────│     │─────────────────│
│ key (PK) │     │ version (PK)    │
│ value    │     │ applied_at      │
│updated_at│     └─────────────────┘
└──────────┘
```

Figure 24: Entity-Relationship Diagram

#### Table Descriptions

**V1 Tables (Core Analysis Storage)**

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `analyses` | Stores each analysis run | file_name, overall_score, grade, analyzed_at |
| `analysis_features` | Features detected per analysis | feature_id, feature_name, category |
| `browser_results` | Per-feature, per-browser support status | browser, version, support_status |

**V2 Tables (User Features)**

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `settings` | Key-value configuration store | key, value, updated_at |
| `bookmarks` | Bookmarked analyses with notes | analysis_id (unique), note |
| `tags` | User-defined tag categories | name (unique), color |
| `analysis_tags` | Many-to-many junction table | analysis_id, tag_id |
| `schema_version` | Tracks applied migrations | version, applied_at |

Table 7: Database Tables

### 3.6 Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Facade** | `src/api/service.py` | Single `AnalyzerService` provides unified API for both GUI and CLI, hiding backend complexity |
| **Repository** | `src/database/repositories.py` | 4 repository classes (Analysis, Settings, Bookmarks, Tags) abstract all database operations with CRUD methods |
| **Singleton** | `src/database/connection.py` | Thread-safe SQLite connection manager with automatic table initialization on first use |
| **Dependency Injection** | Repository constructors | Optional `conn` parameter allows passing test database connections, enabling isolated unit testing |
| **Lazy Loading** | `AnalyzerService._get_analyzer()` | Heavy backend components loaded only on first use, ensuring fast application startup |
| **Layered Configuration** | `src/config/config_manager.py` | Configuration loaded with precedence: CLI flags > config file > package.json > defaults |
| **Data Contracts** | `src/api/schemas.py` | Typed dataclasses define all frontend-backend communication, preventing coupling |
| **Custom Exception Hierarchy** | `src/utils/exceptions.py` | `CrossGuardError` base class with 8 typed subclasses for structured error handling |

Table 8: Design Patterns Used

### 3.7 Developer Setup

#### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Git (version control)

#### Clone and Install

```bash
git clone [repository-url]
cd cross-guard
python -m venv venv
source venv/bin/activate    # macOS/Linux
pip install -e ".[gui,cli,ml,dev]"
```

#### Directory Structure

```
src/
├── api/           # Service facade (59 methods) + data contracts
├── cli/           # Click CLI (8 commands + quality gates + CI generators)
├── config/        # Config file support (crossguard.config.json)
├── export/        # 6 export formats (JSON, PDF, SARIF, JUnit, Checkstyle, CSV)
├── analyzer/      # Compatibility engine (scoring, Can I Use lookup)
├── database/      # SQLite persistence (4 repositories, migrations)
├── gui/           # CustomTkinter GUI (27 widgets)
├── ml/            # ML risk prediction (scikit-learn)
├── scanner/       # Project scanner + framework detector
├── polyfill/      # Polyfill recommendation engine
├── parsers/       # HTML/CSS/JS parsers + feature maps
└── utils/         # Logging, exceptions, types, constants
```

Figure 25: Source Directory Structure

#### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific module tests
pytest tests/parsers/css/ -v    # CSS parser tests (532)
pytest tests/parsers/js/ -v     # JS parser tests (332)
pytest tests/database/ -v       # Database tests (168)
pytest tests/analyzer/ -v       # Analyzer tests (282)
pytest tests/api/ -v            # API service tests (226)
pytest tests/cli/ -v            # CLI tests (165)
pytest tests/export/ -v         # Export tests (61)
pytest tests/config/ -v         # Config tests (27)
```

### 3.8 Core Components

#### 3.8.1 HTML Parser (`src/parsers/html_parser.py`)

The HTML parser uses BeautifulSoup4 to traverse the DOM tree and detect web platform features. It checks:

- **Element names**: Maps HTML elements (e.g., `<dialog>`, `<details>`, `<picture>`, `<template>`) to their Can I Use feature IDs.
- **Attribute names**: Maps attributes (e.g., `loading`, `inputmode`, `decoding`) to features.
- **Attribute values**: Maps specific attribute-value pairs (e.g., `type="date"`, `type="color"`) to features.

Feature mappings are defined in `html_feature_maps.py` (100+ features).

#### 3.8.2 CSS Parser (`src/parsers/css_parser.py`)

The CSS parser uses tinycss2 to parse stylesheets into an AST, then walks the tree to detect:

- **Properties**: CSS properties (e.g., `display: grid`, `container-type`, `aspect-ratio`)
- **Selectors**: CSS selectors (e.g., `:has()`, `:is()`, `::backdrop`)
- **At-rules**: CSS at-rules (e.g., `@container`, `@layer`, `@supports`)
- **Values**: Specific property values (e.g., `gap` within a flex context, `dvh` units)

Feature mappings are defined in `css_feature_maps.py` (150+ features).

Key implementation details:
- `tinycss2.parse_stylesheet()` with `skip_comments=True, skip_whitespace=True`
- `tinycss2.parse_blocks_contents()` extracts declarations from rule blocks
- `tinycss2.serialize()` converts AST nodes back to text for regex matching
- Block structure (`{ }`) is preserved in matchable text for patterns that reference it

#### 3.8.3 JavaScript Parser (`src/parsers/js_parser.py`)

The JavaScript parser uses a 3-tier detection strategy:

**Tier 1 — AST Syntax Node Detection**:
tree-sitter produces AST nodes for syntax features:
- `optional_chain` child of `member_expression` detects optional chaining (`?.`)
- `binary_expression` with `??` operator detects nullish coalescing
- `private_property_identifier` detects private class fields (`#field`)
- Arrow functions, async/await, destructuring, spread, template literals

**Tier 2 — AST Identifier/Call Detection**:
Walks AST to find API usage:
- `member_expression` nodes detect method calls (e.g., `promise.then()`, `array.flatMap()`)
- `new_expression` nodes detect constructors (e.g., `new IntersectionObserver()`)
- `call_expression` nodes detect function calls (e.g., `fetch()`, `structuredClone()`)

**Tier 3 — Regex Fallback on Cleaned Text**:
For patterns missed by AST:
- Source text has comments replaced with spaces and string literals emptied
- Regex patterns match against this cleaned text
- Catches edge cases and complex patterns

Additional safeguards:
- **Parent feature handling**: Methods like `.then()` and `.resolve()` are mapped to the parent feature (Promises)
- **False positive prevention**: Common programming verbs (e.g., `find`, `filter`, `map`) and React component names are filtered out
- **Directive detection**: `"use strict"` and `"use asm"` are detected before string content is removed

Feature mappings are defined in `js_feature_maps.py` (278 Can I Use feature IDs).

#### 3.8.4 Compatibility Analyzer (`src/analyzer/`)

The analyzer takes detected feature IDs and checks each against the Can I Use database:

1. **Database lookup** (`database.py`): Loads the Can I Use JSON data and provides lookup methods for feature support by browser and version.
2. **Compatibility check** (`compatibility.py`): For each feature x browser combination, determines the support status code (y, a, x, p, d, n, u).
3. **Scoring** (`scorer.py`): Computes a weighted compatibility score (0-100) using configurable browser weights and support status values.
4. **Version ranges** (`version_ranges.py`): Handles browser version comparisons and range queries.

#### 3.8.5 Export Module (`src/export/`)

Six export formats, each implemented as an independent module:

| Format | File | Lines | Standard |
|--------|------|-------|----------|
| JSON | `json_exporter.py` | 46 | JSON with metadata enrichment |
| PDF | `pdf_exporter.py` | 633 | Professional ReportLab-based report |
| SARIF | `sarif_exporter.py` | 183 | SARIF 2.1.0 (OASIS/GitHub standard) |
| JUnit | `junit_exporter.py` | 97 | JUnit XML (Jenkins/GitLab CI) |
| Checkstyle | `checkstyle_exporter.py` | 67 | Checkstyle XML (SonarQube) |
| CSV | `csv_exporter.py` | 77 | Tabular CSV |

Table 9: Export Formats

#### 3.8.6 Database Layer (`src/database/`)

The database layer follows the Repository pattern:

- **Connection** (`connection.py`): Thread-safe singleton with automatic table initialization, foreign key enforcement, and Row factory for dict-like access.
- **Migrations** (`migrations.py`): Schema versioning with v1 (core tables) and v2 (settings, bookmarks, tags) migrations applied automatically.
- **Models** (`models.py`): Dataclass-based models (Analysis, AnalysisFeature, BrowserResult, etc.).
- **Repositories** (`repositories.py`): 4 repository classes with dependency injection for testability:
  - `AnalysisRepository` — Save/retrieve/delete analyses with nested features and browser results, using transactions with rollback on error.
  - `SettingsRepository` — Key-value configuration storage.
  - `BookmarksRepository` — Analysis bookmarking with notes.
  - `TagsRepository` — Tag creation, deletion, and analysis association.
- **Statistics** (`statistics.py`): Aggregation queries for score trends, top problematic features, and summary statistics.

#### 3.8.7 CLI Module (`src/cli/`)

The CLI is built with Click and includes:

- **main.py** (600 lines): 8 commands (analyze, export, history, stats, config, update-db, init-ci, init-hooks) with browser validation and helpful "Did you mean?" suggestions for typos.
- **context.py**: `CliContext` dataclass managing verbosity (0-3), color detection (respects `NO_COLOR` env var), and timing.
- **gates.py**: `ThresholdConfig` and `evaluate_gates()` for CI/CD quality gate evaluation.
- **ignore.py**: `.crossguardignore` file support with gitignore-compatible pattern matching.
- **generators.py**: CI configuration generators producing GitHub Actions YAML, GitLab CI YAML, and pre-commit hook configs.
- **formatters.py**: Output formatting for all 7 output modes (table, json, sarif, junit, checkstyle, csv, pdf).

### 3.9 Testing

Cross Guard has a comprehensive test suite with **3,108 tests** across all modules, all passing.

#### 3.9.1 Test Architecture

Tests are organized by module, mirroring the source structure:

| Module | Tests | What's Covered |
|--------|-------|----------------|
| CSS Parser | 532 | Properties, selectors, at-rules, tinycss2 AST |
| HTML Parser | ~1,373 | Elements, attributes, input types |
| JS Parser | 332 | APIs, syntax, tree-sitter AST, custom rules |
| Database | 168 | Models (44), migrations (16), repositories (83), statistics (25) |
| Analyzer | 282 | Compatibility engine |
| API Service | 226 | Facade layer (analysis, history, settings, bookmarks, tags, export) |
| Export | 61 | JSON, PDF, SARIF, JUnit, Checkstyle, CSV |
| Config | 27 | Config loading, merging, defaults, package.json fallback |
| CLI | 165 | Commands, gates, context, ignore, formatters, integration |

Table 10: Test Coverage Summary

#### 3.9.2 Testing Methods

**Unit Tests**: Test individual functions and classes in isolation. For example, dataclass model tests verify field defaults and serialization, scorer tests verify score calculation with known inputs.

**Integration Tests**: Test the interaction between modules. CLI integration tests use Click's `CliRunner` to invoke commands and verify output and exit codes. Parser + analyzer integration tests verify the full pipeline from source code to compatibility results.

**Parametrized Tests**: Used to test the same logic across multiple inputs:

```python
@pytest.mark.parametrize("browser,version", [
    ("chrome", "120"),
    ("firefox", "121"),
    ("safari", "17"),
    ("edge", "120"),
])
def test_compatibility_for_browser(browser, version):
    ...
```

**Fixture Architecture**: 80 pytest fixtures provide test isolation:
- Factory fixtures for creating temporary files (`create_temp_file`, `create_html_file`)
- In-memory SQLite connections for database test isolation
- Mock data fixtures for parser and analyzer tests

**Manual Validation Tests**: 14 directories of JavaScript test files (`tests/validation/js/`) covering syntax features, Promises/async, DOM APIs, and real-world patterns, with a checklist (`CHECKLIST.md`) for manual verification.

#### 3.9.3 Test Results

All 3,108 tests pass in approximately 8.5 seconds:

```
$ pytest tests/ -q
3108 passed in 8.51s
```

[Figure 26: Pytest Results — All Tests Passing]

#### 3.9.4 Manual CLI Testing

A 30-step manual test script (`test_cli_manual.sh`) verifies all CLI functionality including:
- Basic analysis (table, JSON, SARIF output)
- Quiet mode log suppression
- Quality gate exit codes
- Stdin piping
- CI config generation
- History and statistics commands

All 30 manual tests pass with correct exit codes and clean output.

---

# Chapter 4

## 4. Conclusion and Future Work

### 4.1 Conclusion

Cross Guard successfully provides automated browser compatibility analysis for HTML, CSS, and JavaScript source files. The tool addresses a real gap in the web development workflow by transforming a manual, time-consuming process into an automated check that completes in seconds.

Key accomplishments:

1. **Accurate Feature Detection**: Using AST-based parsing (tinycss2 for CSS, tree-sitter for JavaScript, BeautifulSoup4 for HTML), Cross Guard detects 500+ web platform features with high accuracy and low false positive rates. The 3-tier JavaScript detection strategy (AST nodes, AST identifiers, regex fallback) handles the complexity of JavaScript's diverse API surface.

2. **Dual Frontend Architecture**: The service facade pattern enables both a desktop GUI and a production CLI to share the same backend with 59 methods, ensuring consistent analysis results regardless of the interface used. This architecture cleanly separates concerns and supports independent frontend evolution.

3. **CI/CD Integration**: Support for SARIF 2.1.0, JUnit XML, Checkstyle XML, and CSV output formats, combined with quality gates and CI configuration generators, makes Cross Guard ready for integration into professional development workflows.

4. **Comprehensive Testing**: With 3,108 automated tests covering all modules and a 30-step manual test suite, the tool is well-tested and reliable.

5. **Extensibility**: The custom rules system, configurable browser targets, and layered configuration support allow users to adapt Cross Guard to their specific needs without modifying source code.

### 4.2 Future Work

To enhance Cross Guard further, the following features can be implemented in the future:

1. **Web API / REST Interface**
   Expose the analysis backend as a REST API, enabling integration with web-based code editors, browser extensions, and third-party tools.

2. **Language Server Protocol (LSP) Integration**
   Implement an LSP server to provide real-time compatibility warnings directly in code editors like VS Code, showing inline diagnostics as developers type.

3. **TypeScript and JSX Support**
   Extend the JavaScript parser to handle TypeScript (`.ts`) and JSX/TSX files, which are widely used in modern React and Angular projects.

4. **CSS Preprocessor Support**
   Add parsing for SCSS, Less, and Stylus files, extracting the CSS features they compile to.

5. **Collaborative Team Dashboard**
   Build a web dashboard where teams can view project-level compatibility trends, set team-wide browser targets, and share analysis results.

6. **Auto-Fix Suggestions**
   Beyond detecting issues, automatically suggest code transformations (vendor prefixes, fallback properties, alternative APIs) that resolve compatibility problems.

7. **Enhanced ML Model**
   Train the risk prediction model on a larger dataset of real-world projects to improve accuracy and provide more actionable risk assessments.

8. **Browser Extension**
   Create a browser extension that analyzes the current page's source and highlights compatibility issues directly in the browser's developer tools.

---

## Bibliography

1. Can I Use. (2026). Can I Use — Browser Support Tables for Modern Web Technologies. Retrieved from https://caniuse.com/
2. Python Software Foundation. (2026). Python Programming Language. Retrieved from https://www.python.org/
3. BeautifulSoup Documentation. (2024). Beautiful Soup 4 Documentation. Retrieved from https://www.crummy.com/software/BeautifulSoup/bs4/doc/
4. tinycss2 Documentation. (2024). tinycss2 — Low-level CSS Parser. Retrieved from https://doc.courtbouillon.org/tinycss2/
5. tree-sitter Documentation. (2024). tree-sitter — An Incremental Parsing System. Retrieved from https://tree-sitter.github.io/tree-sitter/
6. OASIS. (2023). Static Analysis Results Interchange Format (SARIF) Version 2.1.0. Retrieved from https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
7. Click Documentation. (2024). Click — Python Package for Creating CLI Applications. Retrieved from https://click.palletsprojects.com/
8. CustomTkinter Documentation. (2024). CustomTkinter — A Modern UI Framework for Python. Retrieved from https://customtkinter.tomschimansky.com/
9. SQLite Documentation. (2024). SQLite — Serverless SQL Database Engine. Retrieved from https://www.sqlite.org/docs.html
10. scikit-learn Developers. (2024). scikit-learn — Machine Learning in Python. Retrieved from https://scikit-learn.org/
11. reportlab Documentation. (2024). ReportLab — PDF Generation Library. Retrieved from https://www.reportlab.com/documentation/
12. Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley.
13. Martin, R. C. (2008). Clean Code: A Handbook of Agile Software Craftsmanship. Prentice Hall.
14. GitHub. (2024). GitHub Code Scanning — SARIF Upload. Retrieved from https://docs.github.com/en/code-security/code-scanning
15. JUnit. (2024). JUnit XML Format Specification. Retrieved from https://junit.org/
16. pytest Documentation. (2024). pytest — Testing Framework for Python. Retrieved from https://docs.pytest.org/
17. Fowler, M. (2002). Patterns of Enterprise Application Architecture. Addison-Wesley.

---

## List of Figures

- Figure 1: Cross Guard GUI — Main Upload View
- Figure 2: Cross Guard CLI — Terminal Output
- Figure 3: File Upload — Drop Zone
- Figure 4: File Upload — File Table with Selected Files
- Figure 5: Results Dashboard — Score Card
- Figure 6: Results Dashboard — Browser Cards
- Figure 7: Results Dashboard — Issue Cards (Collapsed)
- Figure 8: Results Dashboard — Issue Card (Expanded)
- Figure 9: Browser Selector Panel
- Figure 10: Analysis History View
- Figure 11: History Card with Bookmark and Tags
- Figure 12: Statistics Panel — Score Trends
- Figure 13: Statistics Panel — Top Problematic Features
- Figure 14: Custom Rules Manager
- Figure 15: PDF Export Report
- Figure 16: Project Scan — Configuration Panel
- Figure 17: Project Scan — Results with File Tree
- Figure 18: CLI — Table Output Format
- Figure 19: System Architecture — Layer Diagram
- Figure 20: Class Diagram — AnalyzerService
- Figure 21: Use Case Diagram
- Figure 22: Sequence Diagram — File Analysis Flow
- Figure 23: Data Flow Diagram
- Figure 24: Entity-Relationship Diagram
- Figure 25: Source Directory Structure
- Figure 26: Pytest Results — All Tests Passing

---

## List of Tables

- Table 1: Hardware Requirements
- Table 2: Software Requirements
- Table 3: Optional Dependency Groups
- Table 4: Can I Use Support Status Codes and Score Values
- Table 5: Development Tools
- Table 6: AnalyzerService Method Groups
- Table 7: Database Tables
- Table 8: Design Patterns Used
- Table 9: Export Formats
- Table 10: Test Coverage Summary

---

## Acknowledgment

[Write your personal acknowledgment here. Thank your supervisor, family, and anyone who helped with the thesis.]
