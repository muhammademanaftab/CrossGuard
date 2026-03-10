# Chapter 1

## 1. Introduction

### 1.1 Motivation

The web platform has thousands of features across HTML, CSS, and JavaScript, each with varying levels of browser support. A feature that works in Chrome may be unsupported in Safari or require a vendor prefix in Firefox. Developers typically handle this by testing manually, checking Can I Use one feature at a time, or relying on experience, all of which are slow, error-prone, and impractical for large projects.

The motivation for this project stems from the desire to automate this process. By leveraging modern parsing technologies such as tinycss2, tree-sitter, and BeautifulSoup4, Cross Guard can extract web features from source files and look up each one in the Can I Use database, finding every compatibility issue in seconds. It also integrates into CI/CD pipelines, letting teams check browser compatibility on every commit, just like linters check code quality or type checkers verify types.

### 1.2 Goals

The primary goal of this project is to build a static analysis tool that automatically detects browser compatibility issues in HTML, CSS, and JavaScript source files. Specifically, Cross Guard aims to achieve the following objectives:

1. **Accurate source file parsing.** Parse web source files using Abstract Syntax Tree (AST) based techniques to extract the web platform features used in the code. The parsers use tinycss2 for CSS stylesheets, tree-sitter for JavaScript, and BeautifulSoup4 for HTML. AST-based parsing is preferred over pure regex matching because it understands the structure of the code, reducing false positives from features appearing inside comments, strings, or unrelated contexts.

2. **Comprehensive compatibility analysis.** Look up each detected feature in the Can I Use database and determine its support status across the target browsers (Chrome, Firefox, Safari, and Edge by default). The tool classifies each feature as fully supported, partially supported, or not supported in each browser, then computes a weighted compatibility score from 0 to 100 and assigns a letter grade (A+ through F).

3. **Dual frontend architecture.** Provide two interfaces, a desktop GUI for interactive use and a production CLI for automated pipelines, both sharing the same analysis backend through a service facade pattern. This ensures that results are identical regardless of which frontend is used, and that the backend logic is tested and maintained in one place.

4. **CI/CD pipeline integration.** Support standard output formats that are recognized by popular CI/CD platforms: SARIF 2.1.0 for GitHub Code Scanning, JUnit XML for Jenkins and GitLab CI, Checkstyle XML for SonarQube, and CSV/JSON for custom tooling. The CLI also provides quality gates (`--fail-on-score`, `--fail-on-errors`, `--fail-on-warnings`) that return appropriate exit codes to fail builds when compatibility drops below a configured threshold.

5. **Extensibility through custom rules.** Allow users to define their own feature detection patterns without modifying the source code. Custom rules can be written in a JSON file or managed through the GUI's visual editor. This enables teams to add detection for proprietary features, internal libraries, or features not yet covered by the built-in rules.

6. **Persistent analysis history.** Store analysis results in a local SQLite database, enabling users to review past analyses, track compatibility trends over time, bookmark important results, and organize analyses with tags.

### 1.3 Scope of the Project

Cross Guard covers the following functional areas:

1. **Multi-Language Source Parsing**
   The tool parses three web languages using dedicated parsers. The HTML parser uses BeautifulSoup4 to traverse the DOM tree and detects over 100 elements, attributes, input types, and attribute values. The CSS parser uses tinycss2 to build an AST and detects over 150 properties, selectors, at-rules, and values. The JavaScript parser uses tree-sitter to build an AST and detects 278 Can I Use feature IDs through a 3-tier strategy: AST node types for syntax features, AST identifiers for API usage, and regex matching on AST-cleaned text as a fallback. All three parsers support custom rule overlays that extend the built-in detection mappings.

2. **Compatibility Analysis Engine**
   For each detected feature, the analyzer queries the Can I Use database and evaluates support status across the configured target browsers. The scoring algorithm produces a weighted score (0 to 100) that accounts for browser importance, prefix-only support, features disabled by default, and partial implementations. Features are classified into severity levels (critical, high, medium, low) based on the extent of non-support across the target browsers.

3. **Desktop GUI Application**
   A desktop application built with CustomTkinter that provides drag-and-drop file upload (via TkinterDnD2), a results dashboard with score cards, browser support cards, and collapsible issue cards. The GUI includes an analysis history panel with bookmarks and tags, a statistics panel showing aggregated trends, a polyfill recommendations view, and a visual custom rules editor. The interface uses a dark blue theme and is designed for interactive exploration of compatibility results.

4. **Production CLI with CI/CD Integration**
   A command-line interface built with Click that supports 6 export formats (JSON, PDF, SARIF 2.1.0, JUnit XML, Checkstyle XML, CSV), quality gates for automated builds, stdin support for piped content, `.crossguardignore` file exclusion patterns, configurable target browsers, and CI configuration generators for GitHub Actions, GitLab CI, and pre-commit hooks. The CLI is designed for non-interactive use in CI/CD environments, with logging directed to stderr to keep stdout clean for piped output.

5. **Project-Level Analysis**
   The tool can recursively scan entire project directories, automatically detecting file types and applying the appropriate parser. It includes a framework detector that identifies popular frameworks (React, Vue, Angular, Svelte, etc.) based on project configuration files, and produces aggregated compatibility reports for multi-file projects.

6. **Polyfill Recommendations**
   When the tool finds unsupported or partially supported features, it consults a built-in polyfill mapping to suggest packages and scripts that can restore compatibility. This helps developers fix issues quickly without having to research each feature individually.

7. **Machine Learning Risk Prediction**
   An optional module built with scikit-learn that analyzes patterns in feature usage across a codebase and predicts compatibility risk levels. This experimental feature provides an early warning system for files that are likely to have compatibility problems based on their feature profile.

8. **Data Persistence**
   A SQLite database with 8 tables that stores analysis history, per-feature results, browser support status, user settings, bookmarks, and tags. The database uses schema versioning with automatic migrations, ensuring that upgrades preserve existing data.

