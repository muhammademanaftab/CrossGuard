# Chapter 3

## Developer Documentation

### 3.1 Problem Specification

Modern web development uses many HTML, CSS, and JavaScript features. However, browser support for these features is not always the same. A feature that works in one browser may be unsupported or partially supported in another browser.

Developers often check compatibility manually using the Can I Use website. This approach works for a single feature but becomes slow and error prone for large projects.

Cross Guard solves this problem by automatically analyzing source code and checking browser compatibility.

The tool performs the following steps:

1. Parse HTML, CSS, and JavaScript files to detect web platform features.
2. Look up each feature in the Can I Use database.
3. Check support across selected browsers.
4. Calculate a compatibility score from 0 to 100.
5. Assign a letter grade from A+ to F.
6. Produce a detailed report showing supported, partially supported, and unsupported features.

Cross Guard provides two ways to use the system:

* Desktop GUI for interactive use.
* Command Line Interface for automation and CI pipelines.

Both interfaces use the same backend through a service facade.

Results can be exported in several formats including JSON, PDF, SARIF, JUnit XML, Checkstyle XML, and CSV.

---

### 3.2 Tools and Methods Used

#### Parsing Libraries

This system uses different parsers for HTML, CSS, and JavaScript files. Each parser follows a similar process: read the file, parse its structure, detect web features, and map them to Can I Use feature IDs.

---

**HTML Parser (BeautifulSoup4 + lxml)**

Used for parsing HTML files. HTML is often not perfectly structured, and BeautifulSoup can handle broken or incomplete markup. It converts HTML code into a DOM tree which can be inspected programmatically.

HTML parser workflow:

1. Read the HTML file as text.
2. Parse the file using BeautifulSoup with the lxml backend.
3. Traverse the DOM tree and inspect elements.
4. Detect features using element names, attributes, and attribute values.
5. Map detected patterns to Can I Use feature IDs.

Example:

* `<dialog>` - dialog feature
* `<input type="date">` - input date feature
* `loading="lazy"` - lazy loading feature

---

**CSS Parser (tinycss2)**

Used for parsing CSS stylesheets. tinycss2 converts CSS code into an Abstract Syntax Tree (AST). This allows the program to understand CSS structure such as selectors, declarations, and rules.

CSS parser workflow:

1. Read the CSS file as text.
2. Parse the stylesheet using tinycss2.
3. Convert the CSS into AST nodes such as rules and declarations.
4. Extract selectors, properties, values, and at rules.
5. Match extracted patterns against feature detection rules.
6. Map the detected patterns to Can I Use feature IDs.

Example:

* `display: flex` - flexbox
* `display: grid` - css grid
* `@media (...)` - media queries

Using AST parsing avoids false detections that can occur when only using simple regex patterns.

---

**JavaScript Parser (tree sitter)**

JavaScript parsing is more complex because the language contains many syntax features and APIs. Tree sitter is used to build a detailed Abstract Syntax Tree that represents the structure of the code.

The JavaScript parser uses a 3-tier detection strategy:

**Tier 1 - AST Syntax Node Detection** (catches ~10 features):
Tree sitter produces AST nodes for syntax features. The parser walks the tree and checks node types directly. For example, `arrow_function` nodes detect arrow functions, `optional_chain` nodes detect optional chaining (`?.`), and `private_property_identifier` nodes detect private class fields (`#field`).

**Tier 2 - AST Identifier and Call Detection** (catches ~200 features):
The parser walks the AST to read names inside `member_expression`, `call_expression`, and `new_expression` nodes. This catches API usage like `fetch()`, `new Promise()`, `navigator.clipboard`, and similar calls.

**Tier 3 - Regex Fallback** (catches ~70 features + custom rules):
For patterns not captured by the AST, regex matching runs on cleaned text where comments and strings have been removed. This catches aliased variables, custom user rules, and features that do not have AST map entries yet.

If tree sitter is not installed, the parser falls back to regex only mode where all 278 features are checked using regex patterns.

Example:

* `fetch()` - Fetch API
* `new Promise()` - Promises
* `?.` - Optional chaining

Using a combination of AST detection and regex fallback ensures both accuracy and broad coverage of JavaScript features.

---

### 3.3 Can I Use Database

Cross Guard relies on a local copy of the Can I Use compatibility database.

The database contains information about browser support for web platform features.

Important files include:

* `data.json` containing compatibility tables
* `features-json` containing detailed feature descriptions
* `region-usage-json` containing browser usage statistics

The database can be updated using a CLI command or from the GUI.

---

### 3.4 Frameworks and Libraries

Cross Guard is implemented in Python and uses several supporting libraries.

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.9+ | Core programming language |
| CustomTkinter | 5.2+ | Desktop GUI framework with dark theme |
| TkinterDnD2 | 0.3+ | Drag and drop file upload for the GUI |
| Click | 8.1+ | CLI framework with nested commands |
| SQLite | Built-in | Persistent storage for history and settings |
| reportlab | 4.0+ | PDF report generation |
| scikit-learn | 1.0+ | Machine learning risk prediction (optional) |
| requests | 2.31+ | HTTP client for database updates |
| matplotlib | 3.8+ | Chart generation for statistics |
| pytest | 7.0+ | Testing framework |
| Git | - | Version control |

Table 1: Frameworks and Libraries

---

### 3.5 System Architecture

The system follows a layered architecture that separates the user interfaces from the backend logic.

```
FRONTEND LAYER
    +-----------------+    +-----------------+
    |      GUI        |    |      CLI        |
    | (CustomTkinter  |    |    (Click       |
    |  desktop app)   |    |    terminal)    |
    +-----------------+    +-----------------+
            |                      |
            v                      v
SERVICE LAYER
    +------------------------------------------+
    |      AnalyzerService (59 methods)        |
    |  One class serves BOTH frontends         |
    |  Handles: analysis, history, export,     |
    |  settings, bookmarks, tags, config       |
    +------------------------------------------+
            |              |              |
            v              v              v
BACKEND LAYER
    +-----------+  +-----------+  +-----------+
    | Parsers   |  | Analyzer  |  | Database  |
    | HTML      |  | Scoring   |  | SQLite    |
    | CSS       |  | Compat.   |  | History   |
    | JS        |  | Grading   |  | Settings  |
    +-----------+  +-----------+  +-----------+

    +-----------+  +-----------+
    | Export    |  | Polyfill  |
    | 6 formats|  | Suggest.  |
    +-----------+  +-----------+
```

[Figure 16: System Architecture - Layer Diagram]

The GUI and CLI only communicate with the backend through the AnalyzerService class.

This design provides several benefits:

* Clear separation of responsibilities.
* Easier testing since each layer can be tested independently.
* Consistent results across both interfaces.
* All logging goes to stderr so piped CLI output stays clean.

---

### 3.6 Full Analysis Flow

This is what happens every time you analyze a file:

```
Your File (e.g., styles.css)
    |
    v
PARSER
    Reads the file and finds web features
    Output: a set of Can I Use feature IDs
    Example: {"css-grid", "flexbox", "css-filters"}
    |
    v
CAN I USE DATABASE
    Looks up each feature to check support
    For each feature x browser:
      "css-grid" + Chrome 120  ->  supported
      "css-grid" + Safari 15   ->  partial
      "css-filters" + Edge 110 ->  unsupported
    |
    v
ANALYZER
    Calculates a compatibility score
    Counts: 8 supported, 2 partial, 1 unsupported
    Score: 81.8 / 100   Grade: B-
    Risk: Medium
    |
    v
OUTPUT
    Shows results to you via:
    - GUI: score cards, issue lists, charts
    - CLI: terminal table or JSON/SARIF output
    - Export: PDF, CSV, JUnit XML, etc.
    - Database: saves to history for later
```

[Figure 17: Full Analysis Flow]

The parser is the most important part because it determines what features get checked. Each language has its own parser with a different approach. The following sections show the internal flow for each parser.

---

### 3.7 Parser Flow Diagrams

#### HTML Parser Flow

```
Your HTML file
    |
    v
Read the file as a string
    |
    v
BeautifulSoup parses the string into a tree of Python objects
    |
    v
5 detection methods run on every element:
    |
    |-- 1. Element names      <dialog>            -> 'dialog'
    |-- 2. Input types        <input type="date"> -> 'input-datetime'
    |-- 3. Attribute names    loading="lazy"       -> 'loading-lazy-attr'
    |-- 4. Attribute values   rel="preload"        -> 'link-rel-preload'
    |-- 5. Special patterns   srcset, SVG, custom elements, etc.
    |
    v
Set of Can I Use feature IDs
{'dialog', 'input-datetime', 'loading-lazy-attr', ...}
    |
    v
Goes to the Analyzer for browser compatibility checking
```

[Figure 18: HTML Parser Flow]

#### CSS Parser Flow

```
Your CSS file
    |
    v
Read the file as a string
    |
    v
tinycss2 parses the string into AST objects
(QualifiedRule, AtRule, Declaration, etc.)
    |
    v
_extract_components walks the AST recursively:
    |
    |-- Declarations: (property, value, selector, block_id)
    |-- At-rules: (keyword, prelude)
    |-- Selectors: selector strings
    |
    v
_build_matchable_text rebuilds clean text:
    selector { property: value; property: value; }
    @keyword prelude
    |
    v
_detect_features runs 150+ regex patterns:
    |
    |-- r'display\s*:\s*(?:inline-)?flex'  -> 'flexbox'
    |-- r'@media\s*\('                     -> 'css-mediaqueries'
    |-- r'\d+\.?\d*rem'                    -> 'rem'
    |-- r'var\(--'                         -> 'css-variables'
    |-- ... 150+ more patterns
    |
    v
Set of Can I Use feature IDs
{'flexbox', 'css-mediaqueries', 'rem', 'css-variables', ...}
    |
    v
Goes to the Analyzer for browser compatibility checking
```

[Figure 19: CSS Parser Flow]

#### JavaScript Parser Flow

```
JavaScript text
    |
    v
Pre-detection (on ORIGINAL text, before any cleaning):
    |-- _detect_directives()       -> "use strict", "use asm"
    |-- _detect_event_listeners()  -> addEventListener('eventName')
    |
    v
Try tree-sitter: _parse_with_tree_sitter()
    |
    |-- SUCCESS (tree-sitter available) -- PATH A
    |   |
    |   |-- Tier 1: _detect_ast_syntax_features()
    |   |   Walk tree, check node TYPES
    |   |   arrow_function -> 'arrow-functions'
    |   |   template_string -> 'template-literals'
    |   |   optional_chain -> optional chaining
    |   |   Catches ~10 features
    |   |
    |   |-- Tier 2: _detect_ast_api_features()
    |   |   Walk tree, READ NAMES inside nodes
    |   |   new Promise -> 'promises'
    |   |   fetch() -> 'fetch'
    |   |   navigator.clipboard -> 'clipboard'
    |   |   Catches ~200 features
    |   |
    |   |-- Build clean text: _build_matchable_text_from_ast()
    |   |   Comments -> spaces
    |   |   String content -> removed (quotes kept)
    |   |   Template text -> removed (backticks + ${x} kept)
    |   |
    |   |-- Tier 3: _detect_features(clean_text)
    |       Regex patterns on clean text
    |       Catches ~70 remaining features + custom rules
    |
    |-- FAILURE (tree-sitter not installed) -- PATH B
        |
        |-- _remove_comments_and_strings()
        |   Manual character-by-character cleaning
        |
        |-- Tier 3: _detect_features(clean_text)
            Regex patterns only (all ~278 features checked)
    |
    v
Final: _find_unrecognized_patterns()
    Safety net - finds API calls that no rule matched
    |
    v
Output: Set of Can I Use feature IDs
{'fetch', 'promises', 'arrow-functions', 'const', 'intersectionobserver', ...}
    |
    v
Goes to the Analyzer for browser compatibility checking
```

[Figure 20: JavaScript Parser Flow]

---

### 3.8 Use Case Diagram

The system supports two types of users:

**GUI User** (web developer using the desktop application):

* Upload files via drag and drop or file picker
* Run compatibility analysis
* View results dashboard with score card, browser cards, and issue cards
* Browse and search analysis history
* Bookmark and tag analyses
* View aggregated statistics
* Edit custom detection rules
* Export reports as PDF or JSON
* Configure target browsers

**CLI User or CI Pipeline** (developer or automated system):

* Analyze files and directories
* Analyze piped stdin content
* Apply quality gates that fail on score, errors, or warnings
* Export in machine readable formats (SARIF, JUnit XML, Checkstyle XML, CSV)
* Generate CI configuration files for GitHub Actions, GitLab CI, or pre-commit
* View history and statistics
* Update the Can I Use database

Both actors share the same backend through AnalyzerService so results are always consistent.

[Insert Figure: Use Case Diagram]
[Caption: Figure 21. Use Case Diagram]

---

### 3.9 Sequence Diagram

The following shows the flow of a file analysis from user input to displayed results.

```
User              GUI/CLI           AnalyzerService      Parser          Analyzer        Database
 |                  |                    |                  |                |               |
 |-- Upload file -->|                    |                  |                |               |
 |                  |-- analyze() ------>|                  |                |               |
 |                  |                    |-- parse_file() ->|                |               |
 |                  |                    |                  |-- extract ---->|               |
 |                  |                    |                  |   features     |               |
 |                  |                    |<- feature_ids ---|                |               |
 |                  |                    |-- check_compat()---------------->|               |
 |                  |                    |                                  |-- lookup ---->|
 |                  |                    |                                  |   Can I Use   |
 |                  |                    |<-- scores, grade ----------------|               |
 |                  |                    |-- save_history()------------------------------- >|
 |                  |<-- AnalysisResult -|                                                  |
 |<-- Display ------|                    |                                                  |
```

[Figure 22: Sequence Diagram - File Analysis Flow]

**Step by step:**

1. The user uploads a file through the GUI or passes a file path to the CLI.
2. The frontend creates an AnalysisRequest and sends it to AnalyzerService.
3. Based on the file extension, the appropriate parser is called.
4. The parser reads the source code and extracts all web platform features.
5. The analyzer looks up each feature in the Can I Use database.
6. The scorer calculates a weighted score and assigns a letter grade.
7. If auto save is enabled, results are stored in the SQLite database.
8. An AnalysisResult is returned to the frontend for display.

---

### 3.10 Database Design

Cross Guard uses SQLite to store analysis history and user data.

#### Entity Relationship Diagram

```
+------------------+       +----------------------+       +------------------+
|    analyses      |--1:N--|  analysis_features   |--1:N--|  browser_results |
|------------------|       |----------------------|       |------------------|
| id (PK)          |       | id (PK)              |       | id (PK)          |
| file_name        |       | analysis_id (FK)     |       | analysis_feat_id |
| file_path        |       | feature_id           |       |   (FK)           |
| file_type        |       | feature_name         |       | browser          |
| overall_score    |       | category             |       | version          |
| grade            |       |                      |       | support_status   |
| total_features   |       +----------------------+       +------------------+
| analyzed_at      |
| browsers_json    |
+--------+---------+
         |
    +----+----+
    |         |
+---v----+ +--v--------------+     +----------+
|bookmarks| | analysis_tags  |---->|   tags   |
|--------| |----------------|     |----------|
| id (PK)| | analysis_id    |     | id (PK)  |
|analysis | |   (FK, PK)    |     | name     |
| _id(FK)| | tag_id(FK,PK)  |     | color    |
| note   | | created_at     |     |created_at|
|created | +----------------+     +----------+
|  _at   |
+--------+

+----------+     +-----------------+
| settings |     | schema_version  |
|----------|     |-----------------|
| key (PK) |     | version (PK)    |
| value    |     | applied_at      |
|updated_at|     +-----------------+
+----------+
```

[Figure 23: Entity Relationship Diagram]

#### Table Descriptions

**V1 Tables** - core analysis storage:

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `analyses` | Stores each analysis run | file_name, overall_score, grade, analyzed_at |
| `analysis_features` | Features detected per analysis | analysis_id (FK), feature_id, category |
| `browser_results` | Per feature per browser support status | analysis_feature_id (FK), browser, support_status |

**V2 Tables** - user features:

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `settings` | Key value configuration store | key (PK), value |
| `bookmarks` | Bookmarked analyses with notes | analysis_id (FK, unique), note |
| `tags` | User defined label categories | name (unique), color |
| `analysis_tags` | Many to many junction table | analysis_id (FK), tag_id (FK) |
| `schema_version` | Tracks applied migrations | version (PK), applied_at |

Table 2: Database Tables

Schema versioning ensures that database updates are applied automatically when the application starts. All foreign keys use `ON DELETE CASCADE` so deleting an analysis removes its related features, browser results, bookmarks, and tags.

---

### 3.11 Export Formats

Cross Guard supports 6 export formats for analysis results:

| Format | Use Case |
|--------|----------|
| JSON | Machine readable output with full analysis metadata |
| PDF | Professional report with score cards and browser breakdowns |
| SARIF 2.1.0 | GitHub Code Scanning integration |
| JUnit XML | Jenkins and GitLab CI test reporting |
| Checkstyle XML | SonarQube integration |
| CSV | Spreadsheet friendly tabular output |

Table 3: Export Formats

Each exporter receives an analysis report and writes the formatted output to a file. The SARIF format is especially useful because GitHub recognizes it and shows compatibility issues as inline annotations in pull requests.

---

### 3.12 CLI Commands

The CLI is built with Click and provides 8 commands:

| Command | Purpose |
|---------|---------|
| `analyze` | Analyze files or directories for compatibility issues |
| `export` | Export a past analysis by ID in any format |
| `history` | List past analyses with optional search |
| `stats` | Show aggregated statistics |
| `config` | Show or initialize configuration |
| `update-db` | Update the Can I Use database |
| `init-ci` | Generate CI configuration for GitHub Actions or GitLab CI |
| `init-hooks` | Generate pre-commit hook configuration |

Table 4: CLI Commands

The CLI also supports quality gates for CI/CD pipelines:

* `--fail-on-score 80` fails the build if the compatibility score drops below 80.
* `--fail-on-errors 5` fails the build if more than 5 unsupported features are found.
* `--fail-on-warnings 10` fails the build if more than 10 partially supported features are found.

Exit codes: 0 means passed, 1 means gate failed, 2 means error.

---

### 3.13 Design Patterns

Several design patterns are used in the system.

| Pattern | Location | Purpose |
|---------|----------|---------|
| Facade | `src/api/service.py` | AnalyzerService provides a single interface that hides backend complexity |
| Repository | `src/database/repositories.py` | 4 repository classes isolate all SQL logic |
| Singleton | `src/database/connection.py` | Ensures only one database connection during runtime |
| Dependency Injection | Repository constructors | Optional conn parameter allows tests to use isolated databases |
| Lazy Loading | `AnalyzerService._get_analyzer()` | Heavy components are created only when first needed |
| Layered Configuration | `src/config/config_manager.py` | CLI flags > config file > package.json > defaults |
| Data Contracts | `src/api/schemas.py` | Typed dataclasses define all frontend backend communication |
| Custom Exceptions | `src/utils/exceptions.py` | CrossGuardError base class with typed subclasses per module |

Table 5: Design Patterns

---

### 3.14 Developer Setup

To set up the development environment the following tools are required:

* Python 3.9 or newer
* pip
* Git

Steps to set up the project:

1. Clone the repository

```
git clone <repository>
cd cross-guard
```

2. Create a virtual environment

```
python -m venv venv
```

3. Activate the environment

Linux or macOS

```
source venv/bin/activate
```

Windows

```
venv\Scripts\activate
```

4. Install dependencies

```
pip install -e ".[gui,cli,ml,dev]"
```

5. Run the GUI

```
python run_gui.py
```

6. Run the CLI

```
python -m src.cli.main analyze example.js --format table
```

7. Run all tests

```
pytest tests/ -q
```

#### Directory Structure

```
src/
+-- api/           # Service facade (59 methods) + data contracts
+-- cli/           # Click CLI (8 commands + quality gates + CI generators)
+-- config/        # Config file support (crossguard.config.json)
+-- export/        # 6 export formats (JSON, PDF, SARIF, JUnit, Checkstyle, CSV)
+-- analyzer/      # Compatibility engine (scoring, Can I Use lookup)
+-- database/      # SQLite persistence (4 repositories, migrations)
+-- gui/           # CustomTkinter GUI (23 widgets)
+-- ml/            # ML risk prediction (scikit-learn, optional)
+-- polyfill/      # Polyfill recommendation engine
+-- parsers/       # HTML/CSS/JS parsers + feature maps
+-- utils/         # Logging, exceptions, types, constants
```

[Figure 24: Source Directory Structure]

---

### 3.15 Testing

Cross Guard includes a comprehensive automated test suite with **2,394 tests** implemented using pytest.

#### Test Coverage

| Module | Tests | Coverage | What is Covered |
|--------|-------|----------|-----------------|
| CSS Parser | 520 | 90% | Property detection, selectors, at-rules, tinycss2 AST, edge cases |
| HTML Parser | 496 | 95% | Elements, attributes, input types, false positive prevention |
| JS Parser | 284 | 84% | API detection, syntax features, tree-sitter AST, custom rules |
| Custom Rules | 42 | 89% | Loader singleton, save and reload, edge cases |
| Analyzer | 287 | 83-100% | Scorer (100%), compatibility checker (100%), version ranges |
| API Service | 200 | 82% | All 59 service methods, schema validation |
| Database | 175 | 83-95% | Models, migrations, 4 repositories, statistics |
| CLI | 162 | 79-100% | Commands, quality gates, formatters, stdin support |
| Polyfill | 158 | 89-100% | Loader, service, generator, integration |
| Export | 43 | 94-100% | All 6 formats |
| Config | 27 | 99% | Config loading, merging, defaults |

Table 6: Test Coverage Summary

#### Testing Methods

**Unit tests** test individual functions and classes in isolation. For example, scorer tests verify score calculation with known inputs and expected outputs.

**Component tests** test the interaction between related modules. For example, parser plus feature map tests verify that the parser correctly uses the feature maps.

**Integration tests** test the full pipeline from input to output. CLI integration tests use Click's CliRunner to invoke commands and verify output format and exit codes.

**Parametrized tests** are used extensively to test the same logic across many inputs:

```python
@pytest.mark.parametrize("css_code, expected_feature", [
    ("display: grid;", "css-grid"),
    ("display: flex;", "flexbox"),
    ("container-type: inline-size;", "css-container-queries"),
])
def test_css_property_detection(parse_features, css_code, expected_feature):
    features = parse_features(css_code)
    assert expected_feature in features
```

#### Test Results

All 2,394 tests pass:

```
$ pytest tests/ -q
2394 passed in 8.5s
```

[Figure 25: Pytest Results]

Tests can also be run by module:

```
pytest tests/parsers/css/ -v     # 520 CSS parser tests
pytest tests/parsers/html/ -v    # 496 HTML parser tests
pytest tests/parsers/js/ -v      # 284 JS parser tests
pytest tests/analyzer/ -v        # 287 analyzer tests
pytest tests/api/ -v             # 200 API service tests
pytest tests/database/ -v        # 175 database tests
pytest tests/cli/ -v             # 162 CLI tests
pytest tests/polyfill/ -v        # 158 polyfill tests
pytest tests/export/ -v          # 43 export tests
pytest tests/config/ -v          # 27 config tests
```

---

### 3.16 Summary

Cross Guard is designed as a modular system that separates user interfaces, analysis logic, and data storage.

The system automatically detects web platform features, evaluates browser compatibility using the Can I Use database, and produces detailed compatibility reports.

The architecture allows the tool to support both interactive desktop use and automated CI workflows while maintaining consistent analysis results.
