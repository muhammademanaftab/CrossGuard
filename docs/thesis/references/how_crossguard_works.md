# How Cross Guard Works — The Complete Picture

This document explains the entire Cross Guard software from start to finish. It covers what the tool does, how every piece fits together, and follows a file all the way through the system. If you've read the individual parser study files (html_parser_explained.md, css_parser_explained.md, js_parser_explained.md), this builds on that knowledge and shows the bigger picture.

---

## Table of Contents

1. [What is Cross Guard?](#1-what-is-cross-guard)
2. [The Big Picture (Architecture)](#2-the-big-picture-architecture)
3. [What is Can I Use?](#3-what-is-can-i-use)
4. [The Three Parsers (Quick Summary)](#4-the-three-parsers-quick-summary)
5. [The Analyzer (How Scores Are Calculated)](#5-the-analyzer-how-scores-are-calculated)
6. [The API Service Layer (The Facade)](#6-the-api-service-layer-the-facade)
7. [The CLI (Terminal Commands)](#7-the-cli-terminal-commands)
8. [The GUI (Desktop App)](#8-the-gui-desktop-app)
9. [The Database (SQLite Persistence)](#9-the-database-sqlite-persistence)
10. [The Export System (6 Formats)](#10-the-export-system-6-formats)
11. [Extra Features](#11-extra-features)
12. [Complete Example Walkthrough](#12-complete-example-walkthrough)

---

## 1. What is Cross Guard?

Cross Guard is a **browser compatibility checker**. It's a static analysis tool — meaning it reads your source code without running it — and tells you which web features in your HTML, CSS, or JavaScript might not work in certain browsers.

### The Problem It Solves

Web browsers (Chrome, Firefox, Safari, Edge) don't all support the same features. A CSS property like `backdrop-filter` works perfectly in Chrome but might not work in Firefox. A JavaScript API like `IntersectionObserver` works everywhere now but didn't work in older Safari.

If you're building a website, you need to know: **"Will my code work for all my users?"** Checking this manually across hundreds of features and multiple browsers is nearly impossible.

### What Cross Guard Does

1. **Reads** your source file (HTML, CSS, or JavaScript)
2. **Finds** every web feature the file uses (like CSS Grid, Promises, `<dialog>` element)
3. **Looks up** each feature in the Can I Use database to check browser support
4. **Reports** which features are unsupported or only partially supported
5. **Scores** the file (0–100) and assigns a letter grade (A+ through F)

### Two Ways to Use It

- **GUI (Desktop App)**: A graphical window where you drag-and-drop files, click buttons, and see visual results with score cards and charts
- **CLI (Command Line)**: A terminal tool you type commands into, useful for automation and CI/CD pipelines

Both use the exact same backend — they just present results differently.

---

## 2. The Big Picture (Architecture)

### The Data Flow

This is what happens every time you analyze a file:

```
Your File (e.g., styles.css)
    │
    ▼
┌──────────────────────────────────────────────┐
│  PARSER                                      │
│  Reads the file and finds web features       │
│  Output: a set of Can I Use feature IDs      │
│  Example: {"css-grid", "flexbox", "css-filters"}│
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  CAN I USE DATABASE                          │
│  Looks up each feature to check support      │
│  For each feature × browser:                 │
│    "css-grid" + Chrome 120 → supported ✓     │
│    "css-grid" + Safari 15  → partial ◐       │
│    "css-filters" + Edge 110 → unsupported ✗  │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  ANALYZER                                    │
│  Calculates a compatibility score            │
│  Counts: 8 supported, 2 partial, 1 unsupported│
│  Score: 81.8 / 100  →  Grade: B-            │
│  Risk: Medium                                │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  OUTPUT                                      │
│  Shows results to you via:                   │
│  - GUI: score cards, issue lists, charts     │
│  - CLI: terminal table or JSON/SARIF output  │
│  - Export: PDF, CSV, JUnit XML, etc.         │
│  - Database: saves to history for later      │
└──────────────────────────────────────────────┘
```

### The Layer Diagram

Cross Guard is organized into layers. Each layer only talks to the layer directly below it:

```
┌─────────────────────────────────────────────────┐
│           FRONTEND LAYER (what you see)          │
│                                                  │
│   ┌──────────────┐      ┌──────────────┐        │
│   │   GUI         │      │   CLI         │        │
│   │ (CustomTkinter│      │ (Click)       │        │
│   │  desktop app) │      │  terminal     │        │
│   └──────┬───────┘      └──────┬───────┘        │
│          │                     │                 │
└──────────┼─────────────────────┼─────────────────┘
           │                     │
           ▼                     ▼
┌─────────────────────────────────────────────────┐
│          API LAYER (the middleman)                │
│                                                   │
│     AnalyzerService (59 methods)                  │
│     - One class serves BOTH frontends             │
│     - Handles: analysis, history, export,         │
│       settings, bookmarks, tags, config           │
└───────────────────────┬───────────────────────────┘
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
┌─────────────────────────────────────────────────┐
│          BACKEND LAYER (the real work)            │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Parsers  │  │ Analyzer │  │ Database │       │
│  │ HTML     │  │ Scoring  │  │ SQLite   │       │
│  │ CSS      │  │ Compat.  │  │ History  │       │
│  │ JS       │  │ Grading  │  │ Settings │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Export   │  │ Polyfill │  │ Scanner  │       │
│  │ 6 formats│  │ Suggest. │  │ Projects │       │
│  └──────────┘  └──────────┘  └──────────┘       │
└───────────────────────────────────────────────────┘
```

### Why Layers Matter

The key rule is: **the GUI and CLI never import directly from the backend**. They always go through the API layer (AnalyzerService).

This means:
- You could delete the entire GUI and the CLI would still work perfectly
- You could add a web interface and it would just call the same AnalyzerService methods
- Changes to how parsing works don't require any changes to the GUI or CLI

This design pattern is called a **Facade** — the API layer is one simple "front door" that hides all the complexity behind it.

---

## 3. What is Can I Use?

### The Website

[Can I Use](https://caniuse.com) is a website that tracks browser support for web platform features. Web developers use it every day to check things like "Does Safari support CSS Grid?" or "Which browsers support the `dialog` element?"

### The Database

Behind the website is a **database** — a structured collection of data about every web feature and which browser versions support it. This database is publicly available as JSON files.

Cross Guard keeps a **local copy** of this database so it can check features without needing an internet connection.

### How the Data is Organized

Each feature in Can I Use has:

- **Feature ID**: A unique identifier like `css-grid`, `promises`, `dialog`, `flexbox`
- **Title**: A human-readable name like "CSS Grid Layout (level 1)"
- **Description**: What the feature does
- **Stats**: Support data for every browser version

The support data looks like this (simplified):

```
Feature: "css-grid"
├── Chrome
│   ├── version 56: "n"  (not supported)
│   ├── version 57: "a"  (almost — partial support)
│   ├── version 58: "y"  (yes — fully supported)
│   └── ...
├── Firefox
│   ├── version 52: "y"  (yes — fully supported)
│   └── ...
├── Safari
│   ├── version 10.1: "a" (almost — with prefix)
│   ├── version 11: "y"   (yes)
│   └── ...
└── Edge
    ├── version 16: "y"   (yes)
    └── ...
```

### Support Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| `y` | **Yes** — Fully supported | CSS Grid in Chrome 120 |
| `a` | **Almost** — Supported with minor issues | Some features have small bugs in certain browsers |
| `n` | **No** — Not supported at all | `dialog` element in older Firefox |
| `p` | **Partial** — Only some aspects work | Feature works but missing sub-features |
| `x` | **Prefix** — Needs vendor prefix (`-webkit-`, `-moz-`) | Older browsers needed `-webkit-flex` instead of `flex` |
| `d` | **Disabled** — Available but turned off by default | Experimental features behind flags |
| `u` | **Unknown** — No data available | Very rare |

### How Cross Guard Loads It

The `CanIUseDatabase` class (`src/analyzer/database.py`) handles loading:

1. **Lazy loading**: The database isn't loaded until the first time something needs it (saves startup time)
2. **Singleton**: Only one copy exists in memory, shared by everything that needs it
3. **Index**: When loading, it builds a search index so lookups are instant (by feature ID, keywords, or title words)
4. **Version matching**: If an exact browser version isn't in the database, it finds the closest version

To check a feature:
```python
db = get_database()
status = db.check_support("css-grid", "chrome", "120")  # Returns "y"
status = db.check_support("dialog", "firefox", "90")     # Returns "n"
```

---

## 4. The Three Parsers (Quick Summary)

Each parser reads one type of file and outputs a **set of Can I Use feature IDs** — the features that file uses. For detailed explanations of each parser, see the dedicated study files.

### HTML Parser

- **File**: `src/parsers/html_parser.py`
- **Parsing tool**: BeautifulSoup4 (reads HTML into a tree of elements)
- **Strategy**: Dictionary lookups — maps element names, attribute names, and attribute values to Can I Use IDs
- **Features detected**: ~100+ (elements like `<dialog>`, `<details>`, `<picture>`; attributes like `loading="lazy"`, `inputmode`; input types like `type="date"`, `type="color"`)
- **Detailed study**: [html_parser_explained.md](html_parser_explained.md)

### CSS Parser

- **File**: `src/parsers/css_parser.py`
- **Parsing tool**: tinycss2 (reads CSS into an Abstract Syntax Tree)
- **Strategy**: Regex pattern matching against CSS properties, values, selectors, and at-rules
- **Features detected**: ~150+ (properties like `display: grid`, selectors like `:has()`, at-rules like `@container`)
- **Detailed study**: [css_parser_explained.md](css_parser_explained.md)

### JavaScript Parser

- **File**: `src/parsers/js_parser.py`
- **Parsing tool**: tree-sitter (reads JS into an Abstract Syntax Tree) with regex fallback
- **Strategy**: 3-tier detection — (1) AST node types for syntax, (2) AST identifiers for API calls, (3) regex on cleaned text for anything missed
- **Features detected**: ~278 Can I Use feature IDs (APIs like `fetch`, `Promise`, `IntersectionObserver`; syntax like `?.`, `??`, `async/await`)
- **Detailed study**: [js_parser_explained.md](js_parser_explained.md)

### What Every Parser Outputs

All three parsers produce the same type of output: a Python `set` of strings.

```python
# HTML parser might return:
{"dialog", "details", "loading-lazy-attr", "input-color"}

# CSS parser might return:
{"css-grid", "flexbox", "css-filters", "css-variables"}

# JS parser might return:
{"promises", "fetch", "intersectionobserver", "arrow-functions"}
```

These strings are **Can I Use feature IDs** — they directly correspond to entries in the Can I Use database, which is how the system connects "what features does my code use?" to "which browsers support them?"

---

## 5. The Analyzer (How Scores Are Calculated)

The analyzer takes the feature IDs from the parsers and produces a compatibility score, a letter grade, and a detailed breakdown. This is the core logic of Cross Guard.

### Step 1: Collect All Features

When you analyze a file, the system first determines the file type and calls the right parser:

```
styles.css  →  CSSParser.parse_file()   →  {"css-grid", "flexbox", "css-filters"}
index.html  →  HTMLParser.parse_file()   →  {"dialog", "details", "picture"}
app.js      →  JSParser.parse_file()     →  {"promises", "fetch", "arrow-functions"}
```

If analyzing a project (multiple files), the features from all files are combined.

### Step 2: Check Each Feature Against Each Browser

For every feature the parser found, the analyzer checks support in every target browser:

```
Feature: "css-grid"
├── Chrome 120:  y (supported)      → 100 points
├── Firefox 121: y (supported)      → 100 points
├── Safari 17:   y (supported)      → 100 points
└── Edge 120:    y (supported)      → 100 points

Feature: "css-filters"
├── Chrome 120:  y (supported)      → 100 points
├── Firefox 121: y (supported)      → 100 points
├── Safari 17:   a (almost)         → 100 points
└── Edge 120:    y (supported)      → 100 points

Feature: "dialog"
├── Chrome 120:  y (supported)      → 100 points
├── Firefox 121: y (supported)      → 100 points
├── Safari 17:   y (supported)      → 100 points
└── Edge 120:    y (supported)      → 100 points
```

### Step 3: Assign Points

Each support status is worth a different number of points:

| Status | Points | Meaning |
|--------|--------|---------|
| `y` (yes) | 100 | Fully works |
| `a` (almost) | 100 | Works with minor issues |
| `x` (prefix) | 70 | Works but needs `-webkit-` or `-moz-` prefix |
| `p` (partial) | 50 | Only partly works |
| `d` (disabled) | 30 | Available but off by default |
| `n` (no) | 0 | Doesn't work at all |
| `u` (unknown) | 0 | No data |

### Step 4: Calculate the Score

The score formula is straightforward. For each browser:

```
Browser Score = (supported × 100 + partial × 50) / total_features
```

Where:
- **supported** = count of features with status `y` or `a`
- **partial** = count of features with status `x` or `p`
- **total_features** = total number of features checked

Then the **overall score** is the average across all browsers:

```
Overall Score = sum(all browser scores) / number of browsers
```

#### Concrete Example

Say we have 3 features and 4 target browsers (Chrome, Firefox, Safari, Edge):

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| css-grid | y | y | y | y |
| dialog | y | y | n | y |
| css-filters | y | y | p | y |

**Chrome score**: (3 supported × 100 + 0 partial × 50) / 3 = **100.0**
**Firefox score**: (3 supported × 100 + 0 partial × 50) / 3 = **100.0**
**Safari score**: (1 supported × 100 + 1 partial × 50) / 3 = **50.0**
**Edge score**: (3 supported × 100 + 0 partial × 50) / 3 = **100.0**

**Overall score**: (100 + 100 + 50 + 100) / 4 = **87.5**

### Step 5: Assign a Grade

The score maps to a letter grade. Cross Guard uses a fine-grained 13-grade system:

| Score Range | Grade |
|-------------|-------|
| 97–100 | A+ |
| 93–96 | A |
| 90–92 | A- |
| 87–89 | B+ |
| 83–86 | B |
| 80–82 | B- |
| 77–79 | C+ |
| 73–76 | C |
| 70–72 | C- |
| 67–69 | D+ |
| 63–66 | D |
| 60–62 | D- |
| 0–59 | F |

From our example: score 87.5 → grade **B+**.

### Step 6: Determine Risk Level

Each feature also gets a risk/severity level based on how many browsers don't support it:

| Level | Rule |
|-------|------|
| **Critical** | Not supported in ANY browser (all browsers say `n`) |
| **High** | Not supported in ≥50% of target browsers |
| **Medium** | Some browsers unsupported, or partial support exists |
| **Low** | All browsers support it (minor issues at most) |
| **None** | No compatibility issues at all |

The overall risk level is based on the weighted score:
- Score ≥ 80 with 0 unsupported features → **None** or **Low**
- Score 60–79 → **Medium**
- Score < 60 → **High**

### Step 7: Generate the Report

The final report contains:

```
Report
├── Summary
│   ├── Total features found: 3
│   ├── Grade: B+
│   ├── Score: 87.5
│   └── Risk: Low
│
├── Browser Breakdown
│   ├── Chrome 120: 100% compatible (3/3 supported)
│   ├── Firefox 121: 100% compatible (3/3 supported)
│   ├── Safari 17: 50% compatible (1/3 supported, 1 partial, 1 unsupported)
│   └── Edge 120: 100% compatible (3/3 supported)
│
├── Feature Breakdown
│   ├── css-grid: ✓ all browsers
│   ├── dialog: ✗ not supported in Safari 17
│   └── css-filters: ◐ partial in Safari 17
│
├── Issues
│   ├── Errors: ["dialog not supported in Safari 17"]
│   └── Warnings: ["css-filters partial support in Safari 17"]
│
└── Recommendations
    └── ["Consider using a polyfill for dialog element"]
```

### Where the Code Lives

| File | What It Does |
|------|-------------|
| `src/analyzer/main.py` | Entry point — orchestrates parsing, checking, scoring, reporting |
| `src/analyzer/compatibility.py` | Browser support lookups, severity classification |
| `src/analyzer/scorer.py` | Score calculation, grade assignment |
| `src/analyzer/database.py` | Can I Use data loading and querying |
| `src/analyzer/version_ranges.py` | Browser version parsing and comparison |

---

## 6. The API Service Layer (The Facade)

### What is a Facade?

Imagine a restaurant. As a customer, you talk to one person: the waiter. You don't go into the kitchen to talk to the chef, you don't go to the storeroom to get ingredients, and you don't wash your own dishes. The waiter is your **single point of contact** — they handle everything behind the scenes.

The `AnalyzerService` class works exactly like that waiter. The GUI and CLI only talk to `AnalyzerService`, and it handles all the behind-the-scenes work: calling parsers, running the analyzer, saving to the database, generating exports, etc.

### The AnalyzerService Class

**File**: `src/api/service.py`

This is one class with **59 methods** organized into categories:

| Category | Example Methods | What They Do |
|----------|----------------|-------------|
| **Analysis** | `analyze()`, `analyze_files()` | Run compatibility analysis on files |
| **History** | `get_history()`, `search_history()`, `delete_analysis()` | Browse and manage past analyses |
| **Bookmarks** | `add_bookmark()`, `remove_bookmark()`, `get_bookmarks()` | Save favorite analyses |
| **Tags** | `create_tag()`, `tag_analysis()`, `get_tags()` | Organize analyses with labels |
| **Settings** | `get_setting()`, `set_setting()`, `get_all_settings()` | Store user preferences |
| **Export** | `export_analysis()`, `export_to_format()` | Generate PDF, JSON, SARIF, etc. |
| **Database** | `get_database_info()`, `update_database()` | Can I Use DB info and updates |
| **Custom Rules** | `get_custom_rules()`, `save_custom_rule()` | Manage user-defined feature rules |
| **Config** | `get_config()`, `get_default_browsers()` | Read configuration settings |
| **Statistics** | `get_statistics()`, `get_score_distribution()` | Aggregated analysis data |
| **Polyfills** | `get_polyfill_recommendations()` | Suggest fixes for unsupported features |
| **Scanner** | `scan_project()`, `get_framework_info()` | Project-level directory scanning |

### Lazy Loading

The AnalyzerService doesn't load the heavy backend components (parsers, Can I Use database) until the first time they're actually needed. This is called **lazy loading**:

```python
class AnalyzerService:
    def __init__(self):
        self._analyzer = None     # Not loaded yet
        self._db_updater = None   # Not loaded yet

    def _get_analyzer(self):
        if self._analyzer is None:
            self._analyzer = CrossGuardAnalyzer()  # Load on first use
        return self._analyzer
```

This means the GUI opens instantly (no waiting for the database to load), and the CLI doesn't waste time loading things it won't use.

### Data Contracts (Schemas)

The API layer uses **dataclasses** as data contracts — they define the exact shape of data passed between the frontends and the backend.

**File**: `src/api/schemas.py`

Key schemas include:
- `AnalysisRequest` — what the frontend sends to start an analysis (file paths, target browsers)
- `AnalysisResult` — what comes back (score, grade, feature breakdown, issues)
- `ExportRequest` — what the frontend sends to generate a report (analysis ID, format, output path)
- `DatabaseInfo` — information about the Can I Use database (version, feature count)

This is like a contract: both sides agree on what data looks like, so if the backend changes internally, the frontends don't need to change as long as the contract stays the same.

### Why This Design Works

```
WITHOUT facade:                    WITH facade:
┌─────┐                            ┌─────┐
│ GUI │──→ Parser                   │ GUI │──→ AnalyzerService ──→ Parser
│     │──→ Analyzer                 │     │                    ──→ Analyzer
│     │──→ Database                 │     │                    ──→ Database
│     │──→ Export                   └─────┘                    ──→ Export
└─────┘──→ Config
                                   ┌─────┐
┌─────┐                            │ CLI │──→ AnalyzerService ──→ (same)
│ CLI │──→ Parser                   └─────┘
│     │──→ Analyzer
│     │──→ Database
│     │──→ Export
└─────┘──→ Config
```

Without the facade, both frontends need to know about every backend component. With the facade, they only know about one thing: `AnalyzerService`.

---

## 7. The CLI (Terminal Commands)

The CLI (Command Line Interface) lets you use Cross Guard from the terminal. It's built with the **Click** library, which makes it easy to define commands, options, and help text.

**File**: `src/cli/main.py`

### The 8 Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `analyze` | Analyze a file or directory | `crossguard analyze styles.css` |
| `export` | Export a past analysis to a file | `crossguard export 42 --format pdf` |
| `history` | List past analyses | `crossguard history --limit 10` |
| `stats` | Show aggregated statistics | `crossguard stats` |
| `config` | Show or create configuration | `crossguard config --init` |
| `update-db` | Update the Can I Use database | `crossguard update-db` |
| `init-ci` | Generate CI/CD workflow config | `crossguard init-ci --provider github` |
| `init-hooks` | Generate pre-commit hook config | `crossguard init-hooks --type pre-commit` |

### How the Analyze Command Works (Step by Step)

When you run `crossguard analyze styles.css --browsers "chrome:120,firefox:121"`:

```
1. Click parses the command line arguments
   ├── TARGET = "styles.css"
   ├── browsers = "chrome:120,firefox:121"
   └── format = "table" (default)

2. CLI creates an AnalysisRequest
   └── Passes file path + browsers to AnalyzerService.analyze()

3. AnalyzerService delegates to the backend
   ├── Detects file type: .css → CSS
   ├── Calls CSSParser.parse_file("styles.css")
   │   └── Returns: {"css-grid", "flexbox", "css-variables"}
   ├── Looks up each feature in Can I Use database
   ├── Calculates scores per browser
   └── Returns AnalysisResult

4. CLI formats the output
   ├── format=table → pretty terminal table with colors
   ├── format=json  → raw JSON to stdout
   ├── format=sarif → SARIF 2.1.0 JSON to stdout
   └── etc.

5. CLI checks quality gates (if configured)
   ├── --fail-on-score 80: Is score ≥ 80? If not, exit 1
   ├── --fail-on-errors 5: Are there ≤ 5 unsupported features? If not, exit 1
   └── --fail-on-warnings 10: Are there ≤ 10 partial features? If not, exit 1

6. CLI saves to history database
   └── AnalyzerService stores the result in SQLite

7. CLI exits
   └── Exit code: 0 (pass) or 1 (fail) or 2 (error)
```

### Output Formats

The `--format` flag controls what the CLI prints to stdout:

| Format | Description | Typical Use |
|--------|-------------|-------------|
| `table` | Colored terminal table with score, grade, issues | Human reading in terminal |
| `json` | Raw JSON object | Piping to other tools |
| `summary` | Condensed one-line summary | Quick checks |
| `sarif` | SARIF 2.1.0 JSON | GitHub Code Scanning |
| `junit` | JUnit XML | Jenkins, GitLab CI test reports |
| `checkstyle` | Checkstyle XML | SonarQube, code quality tools |
| `csv` | Comma-separated values | Spreadsheets, data analysis |

### Quality Gates

Quality gates are thresholds that make the CLI exit with code 1 (failure) if the analysis results don't meet your standards. This is designed for CI/CD pipelines — if compatibility is too low, the build fails.

```bash
# Fail if overall score is below 80
crossguard analyze src/ --fail-on-score 80

# Fail if more than 5 features are completely unsupported
crossguard analyze src/ --fail-on-errors 5

# Fail if more than 10 features have only partial support
crossguard analyze src/ --fail-on-warnings 10

# Combine multiple gates (ALL must pass)
crossguard analyze src/ --fail-on-score 80 --fail-on-errors 5 --fail-on-warnings 10
```

The gate logic (`src/cli/gates.py`) is simple:
1. Compare actual values against thresholds
2. If any threshold is violated, record a failure message
3. If any failures exist, print them to stderr and exit 1

### Exit Codes

| Code | Meaning |
|------|---------|
| **0** | Success — analysis complete, all quality gates passed |
| **1** | Failure — quality gate failed, or compatibility issues found |
| **2** | Error — bad input, file not found, unsupported file type |

### Multiple Simultaneous Outputs

You can write multiple export files in a single run:

```bash
crossguard analyze src/ \
  --format table \
  --output-sarif results.sarif \
  --output-junit results.xml \
  --output-csv results.csv
```

This prints a table to the terminal AND writes SARIF, JUnit, and CSV files all at once.

### Stdin Support

You can pipe file content directly into Cross Guard:

```bash
echo "const x = Promise.resolve();" | crossguard analyze --stdin --stdin-filename app.js
```

### Global CLI Options

| Option | Effect |
|--------|--------|
| `-v` / `-vv` / `-vvv` | Increasing verbosity (more log output to stderr) |
| `-q` / `--quiet` | Suppress non-essential output |
| `--debug` | Maximum verbosity (same as `-vvv`) |
| `--no-color` | Disable colored output (for piping to files) |
| `--timing` | Show elapsed time after completion |

Important: **logging goes to stderr, output goes to stdout**. This means you can pipe the JSON/SARIF output to a file while still seeing log messages in the terminal.

### Where the CLI Code Lives

| File | What It Does |
|------|-------------|
| `src/cli/main.py` | Command definitions (Click decorators) |
| `src/cli/formatters.py` | Terminal output formatting (tables, colors) |
| `src/cli/context.py` | `CliContext` dataclass (verbosity, color, timing settings) |
| `src/cli/gates.py` | Quality gate evaluation logic |
| `src/cli/generators.py` | CI config generators (GitHub Actions, GitLab CI YAML) |
| `src/cli/ignore.py` | `.crossguardignore` file support |

---

## 8. The GUI (Desktop App)

The GUI is a desktop application built with **CustomTkinter** (a modern-looking wrapper around Python's built-in Tkinter toolkit). You run it with `python run_gui.py`.

**File**: `src/gui/main_window.py`

### The Four Views

The GUI has a sidebar on the left (like VS Code) that lets you switch between views:

```
┌──────┬───────────────────────────────────────────┐
│      │                                           │
│  📁  │     FILES VIEW (default)                  │
│      │     - Drag-and-drop upload zone           │
│  📊  │     - File table showing selected files   │
│      │     - Browser selector (Chrome, Firefox,  │
│  📜  │       Safari, Edge + versions)            │
│      │     - "Analyze" button                    │
│  ⚙️  │                                           │
│      │                                           │
└──────┴───────────────────────────────────────────┘
```

| Icon | View | What It Shows |
|------|------|--------------|
| 📁 | **Files** | File upload area, browser selector, analyze button |
| 📊 | **Results** | Score card, browser cards, issue cards, polyfill suggestions |
| 📜 | **History** | Past analyses list, bookmarks, tags, statistics panel |
| ⚙️ | **Settings** | Database info, custom rules editor, configuration |

### Files View — How You Start an Analysis

1. **Add files**: Either drag-and-drop files onto the drop zone, or click "Browse" to open a file picker
2. **Select browsers**: Choose which browsers and versions to check against (defaults: latest Chrome, Firefox, Safari, Edge)
3. **Click "Analyze"**: The GUI calls `AnalyzerService.analyze()` and waits for results

### Results View — What You See After Analysis

After analysis completes, the GUI switches to the Results view:

```
┌──────────────────────────────────────────────────────┐
│  SCORE CARD                                          │
│  ┌──────────────────┐                                │
│  │  Score: 87.5     │  Grade: B+  Risk: Low          │
│  │  ██████████░░░░  │  Features: 12 total            │
│  └──────────────────┘  Supported: 9 | Partial: 2     │
│                        Unsupported: 1                 │
├──────────────────────────────────────────────────────┤
│  BROWSER CARDS                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │Chrome 120│ │Firefox121│ │Safari 17 │ │Edge 120  ││
│  │  100%    │ │  100%    │ │  75%     │ │  100%    ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘│
├──────────────────────────────────────────────────────┤
│  ISSUE CARDS (collapsible)                           │
│  ▼ ✗ dialog — Not supported in Safari 17             │
│    "The <dialog> element is not supported..."        │
│  ▼ ◐ css-filters — Partial support in Safari 17     │
│    "CSS filter() function has limited support..."    │
├──────────────────────────────────────────────────────┤
│  POLYFILL SUGGESTIONS                                │
│  📦 dialog-polyfill (npm install dialog-polyfill)    │
│     Adds <dialog> support to unsupported browsers    │
└──────────────────────────────────────────────────────┘
```

### History View — Past Analyses

Every analysis is automatically saved to the SQLite database. The History view lets you:

- **Browse** past analyses (sorted by date)
- **Search** by file name
- **Bookmark** important analyses (star icon)
- **Tag** analyses with colored labels (e.g., "production", "needs-fix", "approved")
- **View statistics**: aggregated data like average scores, most common issues, score trends over time

### Settings View

- **Database info**: Shows Can I Use database version, total features, last update date
- **Update database**: Button to download the latest Can I Use data
- **Custom rules**: Visual editor for adding custom feature detection rules
- **Configuration**: View and edit default settings

### The 27 Widgets

The GUI is built from reusable widget components (in `src/gui/widgets/`). Key ones include:

| Widget | Purpose |
|--------|---------|
| `score_card.py` | Big score display with progress bar and grade |
| `browser_card.py` | Per-browser compatibility percentage card |
| `issue_card.py` | Collapsible card showing one compatibility issue |
| `drop_zone.py` | Drag-and-drop file upload area |
| `polyfill_card.py` | Polyfill recommendation with install command |
| `history_card.py` | Single analysis in the history list |
| `statistics_panel.py` | Aggregated statistics display |
| `rules_manager.py` | Custom rules editor interface |
| `sidebar.py` | VS Code-style navigation sidebar |
| `bookmark_button.py` | Star/unstar toggle for bookmarks |
| `tag_widget.py` | Colored tag chips |
| `charts.py` | Simple chart visualizations |

### Important Architecture Note

The main window (`main_window.py`) imports ONLY from `src.api`. It never directly imports from parsers, analyzer, database, or export modules. Everything goes through `AnalyzerService`.

---

## 9. The Database (SQLite Persistence)

Cross Guard uses **SQLite** to store analysis history, user preferences, bookmarks, and tags. SQLite is a file-based database — all data lives in a single file called `crossguard.db`.

### Why SQLite?

- **Zero configuration**: No database server to install or configure
- **Single file**: Everything in one `.db` file, easy to back up or delete
- **Built into Python**: The `sqlite3` module comes with Python, no extra installation needed
- **Fast enough**: For a desktop app's needs, SQLite is more than fast enough

### The 8 Tables

The database has 8 tables organized into two groups: the original V1 tables and the V2 additions.

#### Core Tables (V1) — Analysis Storage

```
┌─────────────────────┐
│     analyses         │  One row per analyzed file
│─────────────────────│
│ id (auto-increment) │
│ file_name            │  "styles.css"
│ file_path            │  "/Users/me/project/styles.css"
│ file_type            │  "css"
│ overall_score        │  87.5
│ grade                │  "B+"
│ total_features       │  12
│ analyzed_at          │  "2026-02-25 14:30:00"
│ browsers_json        │  '{"chrome":"120","firefox":"121"}'
└─────────┬───────────┘
          │ one-to-many
          ▼
┌─────────────────────┐
│  analysis_features   │  One row per feature found
│─────────────────────│
│ id                   │
│ analysis_id (FK)     │  → analyses.id
│ feature_id           │  "css-grid"
│ feature_name         │  "CSS Grid Layout"
│ category             │  "css"
└─────────┬───────────┘
          │ one-to-many
          ▼
┌─────────────────────┐
│  browser_results     │  One row per feature × browser
│─────────────────────│
│ id                   │
│ analysis_feature_id  │  → analysis_features.id
│   (FK)               │
│ browser              │  "chrome"
│ version              │  "120"
│ support_status       │  "y"
└─────────────────────┘
```

This creates a **three-level hierarchy**: each **Analysis** has many **Features**, and each Feature has many **BrowserResults**. So a single analysis of a file with 10 features checked against 4 browsers would create:
- 1 row in `analyses`
- 10 rows in `analysis_features`
- 40 rows in `browser_results`

#### Organization Tables (V2) — User Features

```
┌─────────────────────┐     ┌──────────────────────┐
│     settings         │     │     bookmarks         │
│─────────────────────│     │──────────────────────│
│ key (PK)            │     │ id                    │
│ value               │     │ analysis_id (FK, UNIQUE) │
│ updated_at          │     │ note                  │
│                     │     │ created_at            │
└─────────────────────┘     └──────────────────────┘

┌─────────────────────┐     ┌──────────────────────┐
│       tags           │     │   analysis_tags       │
│─────────────────────│     │──────────────────────│
│ id                   │     │ analysis_id (FK)      │
│ name (UNIQUE)        │     │ tag_id (FK)           │
│ color                │     │ created_at            │
│ created_at           │     │ (composite PK)        │
└─────────────────────┘     └──────────────────────┘

┌─────────────────────┐
│  schema_version      │  Tracks database version
│─────────────────────│
│ version (PK)         │  Currently: 2
│ applied_at           │
└─────────────────────┘
```

- **settings**: Key-value store for user preferences (like default browsers, theme settings)
- **bookmarks**: Star an analysis so you can find it later, with an optional note
- **tags**: Colored labels like "production", "needs-fix" — can be applied to multiple analyses
- **analysis_tags**: Junction table connecting analyses to tags (many-to-many relationship)
- **schema_version**: Tracks which version of the database schema is installed

### The Repository Pattern

Direct SQL queries are hidden behind **repository classes** (`src/database/repositories.py`). Each repository handles one area of the database:

| Repository | Tables It Manages | Key Methods |
|-----------|-------------------|-------------|
| `AnalysisRepository` | analyses, analysis_features, browser_results | `save_analysis()`, `get_all_analyses()`, `get_analysis_by_id()`, `delete_analysis()`, `search_analyses()` |
| `SettingsRepository` | settings | `get()`, `set()`, `get_all()`, `get_as_bool()`, `get_as_int()` |
| `BookmarksRepository` | bookmarks | `add_bookmark()`, `remove_bookmark()`, `is_bookmarked()`, `get_all_bookmarks()` |
| `TagsRepository` | tags, analysis_tags | `create_tag()`, `tag_analysis()`, `get_tags_for_analysis()`, `get_analyses_by_tag()` |

This means no other code in the project writes raw SQL. If you want to save an analysis, you call `AnalysisRepository.save_analysis(analysis)` and it handles all the INSERT statements for you.

### Thread Safety and Singleton

The database connection is managed as a **singleton** (`src/database/connection.py`):
- Only one connection exists at a time
- It's thread-safe (multiple threads can use it safely)
- Tables are automatically created on first connection (via migrations)

### Migrations

When the database schema needs to change (like adding the bookmarks and tags tables in V2), the migration system handles it:

1. Check the current schema version from the `schema_version` table
2. If it's V1 but the code expects V2, run the V2 migration (create new tables)
3. Record the new version in `schema_version`

This means users can update Cross Guard without losing their existing data.

### Where the Database Code Lives

| File | What It Does |
|------|-------------|
| `src/database/connection.py` | Singleton connection manager |
| `src/database/migrations.py` | Table creation and schema versioning |
| `src/database/models.py` | Dataclass models (Analysis, Feature, BrowserResult, etc.) |
| `src/database/repositories.py` | CRUD operations (4 repository classes) |
| `src/database/statistics.py` | Aggregation queries (score averages, trends, top issues) |

---

## 10. The Export System (6 Formats)

Cross Guard can export analysis results in 6 different formats. Each format serves a different purpose.

### The 6 Formats

| Format | File Extension | Primary Use | Consumer |
|--------|---------------|-------------|----------|
| **JSON** | `.json` | Machine-readable raw data | Scripts, APIs, custom tools |
| **PDF** | `.pdf` | Human-readable printed report | Stakeholders, documentation |
| **SARIF** | `.sarif` | Static analysis standard | GitHub Code Scanning, VS Code |
| **JUnit XML** | `.xml` | Test result standard | Jenkins, GitLab CI |
| **Checkstyle XML** | `.xml` | Code quality standard | SonarQube, linters |
| **CSV** | `.csv` | Spreadsheet data | Excel, Google Sheets, data analysis |

### How Each Format Works

#### JSON Export (`src/export/json_exporter.py`)

The simplest format — just converts the analysis result to a JSON file:

```json
{
  "file": "styles.css",
  "score": 87.5,
  "grade": "B+",
  "features": [
    {
      "id": "css-grid",
      "name": "CSS Grid Layout",
      "browsers": {
        "chrome": {"version": "120", "support": "y"},
        "safari": {"version": "17", "support": "y"}
      }
    }
  ]
}
```

#### PDF Export (`src/export/pdf_exporter.py`)

Generates a formatted PDF report using the **reportlab** library. Includes:
- Title page with file name and date
- Score summary with grade
- Browser compatibility table
- Feature-by-feature breakdown
- Recommendations section

#### SARIF Export (`src/export/sarif_exporter.py`)

SARIF (Static Analysis Results Interchange Format) is a standard JSON format used by security and code quality tools. GitHub Code Scanning understands SARIF natively.

Structure:
```json
{
  "$schema": "https://...sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "CrossGuard",
        "rules": [...]
      }
    },
    "results": [
      {
        "ruleId": "css-grid",
        "level": "error",
        "message": {"text": "css-grid is not supported in Safari 15"},
        "locations": [{"physicalLocation": {"artifactLocation": {"uri": "styles.css"}}}]
      }
    ]
  }]
}
```

When uploaded to GitHub, these results appear as annotations on your pull request — each unsupported feature shows up as a warning or error on the relevant file.

#### JUnit XML Export (`src/export/junit_exporter.py`)

JUnit is a testing framework standard that CI systems understand. Cross Guard maps compatibility checks to "test cases":

```xml
<testsuites name="CrossGuard">
  <testsuite name="chrome 120" tests="3" failures="0">
    <testcase name="3 features fully supported" classname="crossguard.chrome"/>
  </testsuite>
  <testsuite name="safari 17" tests="3" failures="1">
    <testcase name="dialog" classname="crossguard.safari">
      <failure type="unsupported">dialog is not supported in safari 17</failure>
    </testcase>
    <testcase name="css-filters" classname="crossguard.safari">
      <failure type="partial">css-filters is only partially supported in safari 17</failure>
    </testcase>
    <testcase name="1 features fully supported" classname="crossguard.safari"/>
  </testsuite>
</testsuites>
```

Each browser becomes a "test suite" and each unsupported feature becomes a "failed test". CI systems display this as a familiar pass/fail test report.

#### Checkstyle XML Export (`src/export/checkstyle_exporter.py`)

Checkstyle is a code quality format understood by SonarQube and many linters:

```xml
<checkstyle version="8.0">
  <file name="styles.css">
    <error severity="error" message="dialog not supported in safari 17"
           source="crossguard.compatibility"/>
  </file>
</checkstyle>
```

#### CSV Export (`src/export/csv_exporter.py`)

Simple comma-separated values, one row per feature × browser combination:

```csv
file,feature_id,feature_name,browser,version,support_status
styles.css,css-grid,CSS Grid Layout,chrome,120,y
styles.css,css-grid,CSS Grid Layout,safari,17,y
styles.css,dialog,Dialog Element,chrome,120,y
styles.css,dialog,Dialog Element,safari,17,n
```

### Where the Export Code Lives

Each format has its own file in `src/export/`:

```
src/export/
├── json_exporter.py       # JSON export
├── pdf_exporter.py        # PDF export (uses reportlab)
├── sarif_exporter.py      # SARIF 2.1.0 export
├── junit_exporter.py      # JUnit XML export
├── checkstyle_exporter.py # Checkstyle XML export
└── csv_exporter.py        # CSV export
```

All exporters follow the same pattern:
```python
def export_<format>(report: Dict, output_path: Optional[str] = None):
    # If output_path provided: write to file, return path
    # If output_path is None: return the formatted data (string or dict)
```

---

## 11. Extra Features

### Custom Rules

Users can teach Cross Guard to detect features it doesn't know about by default. This is done through **custom rules** — JSON patterns that tell the parsers what to look for.

**File**: `src/parsers/custom_rules.json`

Example: If your project uses a new CSS feature that Cross Guard doesn't detect yet:

```json
{
  "css": {
    "css-anchor-positioning": {
      "patterns": ["anchor\\s*\\(", "position-anchor\\s*:"],
      "description": "CSS Anchor Positioning"
    }
  }
}
```

This tells the CSS parser: "When you see `anchor(` or `position-anchor:`, that's the `css-anchor-positioning` Can I Use feature."

Custom rules can be added via:
- The **GUI**: Click the "Custom Rules" button in the header to open a visual editor
- **JSON file**: Directly edit `custom_rules.json`

### Polyfill Recommendations

When Cross Guard finds an unsupported feature, it can suggest **polyfills** — code libraries that add support for modern features in older browsers.

**File**: `src/polyfill/polyfill_service.py`

The flow:
1. Analysis finds unsupported/partial features
2. Polyfill service looks up each feature in a mapping file (`polyfill_map.json`)
3. For each match, it creates a recommendation with:
   - **npm package name** (e.g., `dialog-polyfill`)
   - **Import statement** (e.g., `import 'dialog-polyfill'`)
   - **CDN URL** (alternative to npm)
   - **Bundle size** (how much extra code this adds)
   - **Fallback code** (CSS workarounds when no npm package exists)

The polyfill service also provides helper methods:
- `get_aggregate_install_command()` → `npm install dialog-polyfill core-js whatwg-fetch`
- `get_aggregate_imports()` → list of all import statements needed
- `get_total_size_kb()` → total bundle size impact

### Project Scanning

Instead of analyzing one file at a time, you can point Cross Guard at an entire project directory. The **project scanner** handles this.

**File**: `src/scanner/project_scanner.py`

What it does:
1. **Recursively walks** the directory tree
2. **Filters** by file type (HTML, CSS, JS — configurable)
3. **Excludes** common non-source directories by default: `node_modules`, `dist`, `build`, `.git`, `__pycache__`, `.next`, `.nuxt`, `coverage`, `.cache`, `vendor`
4. **Safety limits**: max 1000 files by default, configurable depth limit
5. **Builds a file tree** structure for the GUI to display
6. **Optionally skips minified files** (compressed production code)

### Framework Detection

**File**: `src/scanner/framework_detector.py`

When scanning a project, Cross Guard can detect which frameworks are in use (React, Vue, Angular, Svelte, etc.) by looking at:
- `package.json` dependencies
- Import statements in JS files
- File naming conventions (`.vue`, `.jsx`, `.tsx`, `.svelte` files)

This information is shown as a hint card in the GUI, helping users understand their project's context.

### Configuration System

Cross Guard supports layered configuration with this precedence (highest to lowest):

```
1. CLI flags          (e.g., --browsers "chrome:120")
         ↓ overrides
2. crossguard.config.json   (project-level config file)
         ↓ overrides
3. package.json "crossguard" key   (fallback for JS projects)
         ↓ overrides
4. Built-in defaults   (latest browser versions, table output, standard excludes)
```

**File**: `src/config/config_manager.py`

A typical `crossguard.config.json`:

```json
{
  "browsers": {
    "chrome": "120",
    "firefox": "121",
    "safari": "17",
    "edge": "120"
  },
  "output": "table",
  "ignore": ["node_modules", "dist", "build"],
  "rules": null
}
```

The config manager searches for this file starting in the current directory and walking up to 10 parent directories. If not found, it checks `package.json` for a `"crossguard"` key. If that's also missing, it uses built-in defaults.

### .crossguardignore

Like `.gitignore`, but for Cross Guard. Lets you exclude files from analysis:

**File**: `src/cli/ignore.py`

```
# .crossguardignore
node_modules/
dist/
*.min.js
*.min.css
vendor/
test/fixtures/
```

Supports the same glob patterns as `.gitignore`.

### CI/CD Integration

Cross Guard can generate ready-to-use CI configuration files:

**GitHub Actions** (`crossguard init-ci --provider github`):
```yaml
name: Browser Compatibility Check
on: [push, pull_request]
jobs:
  compatibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install crossguard
      - run: crossguard analyze src/ --format sarif -o results.sarif --fail-on-score 80
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

**GitLab CI** (`crossguard init-ci --provider gitlab`):
```yaml
compatibility:
  script:
    - pip install crossguard
    - crossguard analyze src/ --format junit -o results.xml --fail-on-score 80
  artifacts:
    reports:
      junit: results.xml
```

### ML Risk Prediction (Optional)

**Files**: `src/ml/` directory

An optional machine learning module that predicts compatibility risk levels. Uses scikit-learn to train a model on past analysis data. This is an advanced feature that requires:
- The `ml` optional dependency (`pip install crossguard[ml]`)
- Enough historical analysis data to train on

---

## 12. Complete Example Walkthrough

Let's trace a complete analysis from start to finish with a real example.

### The Input File

Imagine we have a file called `modern-page.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .container {
      display: grid;
      grid-template-columns: 1fr 2fr;
      gap: 16px;
    }
    .card {
      backdrop-filter: blur(10px);
    }
  </style>
</head>
<body>
  <dialog id="modal">
    <p>Hello World</p>
  </dialog>
  <div class="container">
    <div class="card">Content</div>
  </div>
  <script>
    const data = fetch('/api/data')
      .then(response => response.json());
    const observer = new IntersectionObserver(callback);
  </script>
</body>
</html>
```

This file uses HTML, CSS, and JavaScript features all in one file.

### Step 1: User Triggers Analysis

**Via GUI**: User drags `modern-page.html` onto the drop zone, selects target browsers (Chrome 120, Firefox 121, Safari 17, Edge 120), and clicks "Analyze".

**Via CLI**: User runs:
```bash
crossguard analyze modern-page.html --browsers "chrome:120,firefox:121,safari:17,edge:120"
```

Both call `AnalyzerService.analyze()` with the file path and browser targets.

### Step 2: AnalyzerService Delegates to Backend

The service detects the file type (`.html`) and calls `CrossGuardAnalyzer.analyze_single_file("modern-page.html")`.

The analyzer sees it's an HTML file. HTML files can contain inline `<style>` and `<script>` blocks, so it:
1. Calls the **HTML parser** on the full file
2. Extracts inline CSS from `<style>` tags and calls the **CSS parser**
3. Extracts inline JS from `<script>` tags and calls the **JS parser**

### Step 3: HTML Parser Runs

The HTML parser uses BeautifulSoup to find elements and attributes:

```
Found elements: <dialog>, <html>, <head>, <body>, <div>, <p>, <style>, <script>
↓ Check against feature map
Only <dialog> maps to a Can I Use feature: "dialog"
```

**HTML features found**: `{"dialog"}`

### Step 4: CSS Parser Runs

The CSS parser uses tinycss2 to parse the inline `<style>` content, then checks regex patterns:

```
Declarations found:
  display: grid         → matches pattern for "css-grid"
  grid-template-columns → matches pattern for "css-grid" (already found)
  gap: 16px             → matches pattern for "flexbox-gap" (gap in grid/flex contexts)
  backdrop-filter       → matches pattern for "css-backdrop-filter"
```

**CSS features found**: `{"css-grid", "flexbox-gap", "css-backdrop-filter"}`

### Step 5: JS Parser Runs

The JS parser uses tree-sitter to build an AST of the inline `<script>` content:

```
AST analysis:
  fetch('/api/data')              → identifier "fetch" maps to "fetch"
  .then(...)                      → method "then" maps to parent feature "promises"
  .json()                         → standard method, no mapping
  new IntersectionObserver(...)   → constructor maps to "intersectionobserver"
  const                           → maps to "const" feature
  Arrow function (callback)       → maps to "arrow-functions"
```

**JS features found**: `{"fetch", "promises", "intersectionobserver", "const", "arrow-functions"}`

### Step 6: Combine All Features

```
All features = HTML ∪ CSS ∪ JS
= {"dialog", "css-grid", "flexbox-gap", "css-backdrop-filter",
   "fetch", "promises", "intersectionobserver", "const", "arrow-functions"}

Total: 9 features
```

### Step 7: Look Up Each Feature in Can I Use

For each of the 9 features, check support in all 4 target browsers:

| Feature | Chrome 120 | Firefox 121 | Safari 17 | Edge 120 |
|---------|-----------|------------|----------|---------|
| dialog | y | y | y | y |
| css-grid | y | y | y | y |
| flexbox-gap | y | y | y | y |
| css-backdrop-filter | y | y | y | y |
| fetch | y | y | y | y |
| promises | y | y | y | y |
| intersectionobserver | y | y | y | y |
| const | y | y | y | y |
| arrow-functions | y | y | y | y |

(Note: With modern browser versions, most features are fully supported. The issues become visible when targeting older versions or less common browsers.)

### Step 8: Calculate Scores

For each browser:
```
Chrome 120:  9 supported, 0 partial, 0 unsupported → (9×100) / 9 = 100.0
Firefox 121: 9 supported, 0 partial, 0 unsupported → (9×100) / 9 = 100.0
Safari 17:   9 supported, 0 partial, 0 unsupported → (9×100) / 9 = 100.0
Edge 120:    9 supported, 0 partial, 0 unsupported → (9×100) / 9 = 100.0
```

Overall score: (100 + 100 + 100 + 100) / 4 = **100.0**

Grade: **A+**
Risk: **None**

### Step 9: Generate Report

The analyzer packages everything into an `AnalysisResult`:

```
AnalysisResult:
  file: "modern-page.html"
  score: 100.0
  grade: "A+"
  risk: "none"
  total_features: 9
  html_features: 1 (dialog)
  css_features: 3 (css-grid, flexbox-gap, css-backdrop-filter)
  js_features: 5 (fetch, promises, intersectionobserver, const, arrow-functions)
  issues: [] (empty — no problems!)
  browsers:
    chrome: {version: "120", compatibility: 100%, supported: 9, partial: 0, unsupported: 0}
    firefox: {version: "121", compatibility: 100%, supported: 9, partial: 0, unsupported: 0}
    safari: {version: "17", compatibility: 100%, supported: 9, partial: 0, unsupported: 0}
    edge: {version: "120", compatibility: 100%, supported: 9, partial: 0, unsupported: 0}
```

### Step 10: Save to Database

The result is saved to SQLite:
- 1 row in `analyses` (score=100, grade=A+, total_features=9)
- 9 rows in `analysis_features` (one per feature)
- 36 rows in `browser_results` (9 features × 4 browsers)

### Step 11: Display Results

**GUI**: Switches to the Results view showing a green A+ score card, four browser cards all at 100%, and no issue cards (clean bill of health!).

**CLI** (table format):
```
╔══════════════════════════════════════════════════════════╗
║  Cross Guard Analysis: modern-page.html                  ║
╠══════════════════════════════════════════════════════════╣
║  Score: 100.0 / 100    Grade: A+    Risk: None           ║
║  Features: 9 total (1 HTML, 3 CSS, 5 JS)                ║
║  Supported: 9 | Partial: 0 | Unsupported: 0             ║
╠══════════════════════════════════════════════════════════╣
║  Browser         Version    Compatibility                ║
║  Chrome          120        100.0%                       ║
║  Firefox         121        100.0%                       ║
║  Safari          17         100.0%                       ║
║  Edge            120        100.0%                       ║
╠══════════════════════════════════════════════════════════╣
║  ✓ No compatibility issues found!                        ║
╚══════════════════════════════════════════════════════════╝
```

### What If There WERE Issues?

If the user had targeted older browsers (e.g., Safari 13), some features would be unsupported. The report would then include:
- Issue cards for each unsupported feature
- A lower score (maybe 75.0, grade C+)
- Polyfill recommendations (e.g., "Install `dialog-polyfill` to fix `<dialog>` in Safari 13")
- A higher risk level (Medium or High)

---

## Summary: How All the Pieces Connect

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  USER gives a file ──→ FRONTEND (GUI or CLI)                             │
│                              │                                           │
│                              ▼                                           │
│                    ANALYZERSERVICE (API facade)                           │
│                              │                                           │
│                    ┌─────────┼──────────┐                                │
│                    ▼         ▼          ▼                                 │
│              HTML Parser  CSS Parser  JS Parser                          │
│              (BS4)        (tinycss2)  (tree-sitter)                      │
│                    │         │          │                                 │
│                    └─────────┼──────────┘                                │
│                              ▼                                           │
│                    Set of Can I Use feature IDs                          │
│                    {"css-grid", "promises", "dialog", ...}               │
│                              │                                           │
│                              ▼                                           │
│                    CAN I USE DATABASE lookup                             │
│                    For each feature × browser → support status           │
│                              │                                           │
│                              ▼                                           │
│                    SCORER                                                │
│                    (supported×100 + partial×50) / total = score          │
│                    Score → Grade (A+ through F)                          │
│                    Unsupported count → Risk level                        │
│                              │                                           │
│                              ▼                                           │
│                    ANALYSIS RESULT                                       │
│                    Score, grade, risk, feature breakdown, issues          │
│                              │                                           │
│              ┌───────────────┼───────────────┐                           │
│              ▼               ▼               ▼                           │
│         SQLITE DB       FRONTEND        EXPORT                          │
│         (history)       (display)       (PDF, SARIF, JUnit, ...)        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

This is Cross Guard: a pipeline that reads your code, identifies the web features it uses, checks if those features work in your target browsers, and tells you the result with a score, grade, and actionable recommendations.
