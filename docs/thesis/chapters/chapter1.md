# Chapter 1

## 1. Introduction

### 1.1 Motivation

The web platform has thousands of features across HTML, CSS, and JavaScript, each with varying levels of browser support. A feature that works in Chrome may be unsupported in Safari or require a vendor prefix in Firefox. Developers typically handle this by testing manually, checking Can I Use one feature at a time, or relying on experience — all of which are slow, error-prone, and impractical for large projects.

Cross Guard automates this process. It parses source files, extracts the web features used in the code, and looks up each one in the Can I Use database — finding every compatibility issue in seconds. It also integrates into CI/CD pipelines, letting teams check browser compatibility on every commit, just like linters check code quality or type checkers verify types.

### 1.2 Goals

The main goal of this project is to build a tool that automatically detects browser compatibility issues in HTML, CSS, and JavaScript source files. Specifically, Cross Guard aims to:

1. **Parse source files accurately** using AST-based parsing (tinycss2 for CSS, tree-sitter for JavaScript, BeautifulSoup4 for HTML) to extract web features with minimal false positives.

2. **Analyze compatibility** by looking up each feature in the Can I Use database, classifying its support status per browser, and computing a weighted score (0–100) with a letter grade.

3. **Provide two frontends** — a desktop GUI for interactive use and a CLI for automated pipelines — both sharing the same backend through a service facade.

4. **Integrate with CI/CD** through standard output formats (SARIF, JUnit XML, Checkstyle XML) and quality gates that fail builds when compatibility drops below a threshold.

5. **Support extensibility** via custom detection rules and configurable target browsers.

6. **Persist analysis history** in a local SQLite database with bookmarks and tags.

### 1.3 Scope of the Project

The scope of Cross Guard covers the following areas:

1. **Multi-Language Parsing** — Parses HTML, CSS, and JavaScript using AST-based parsers. Detects 100+ HTML elements/attributes, 150+ CSS properties/selectors, and 278 JavaScript feature IDs via a 3-tier strategy (AST node types, AST identifiers, regex fallback).

2. **Compatibility Analysis Engine** — Looks up each detected feature in Can I Use and computes a weighted compatibility score. Features are classified as supported, partially supported, or unsupported per target browser.

3. **Desktop GUI** — A CustomTkinter application with drag-and-drop upload, results dashboard (score cards, browser cards, issue cards), analysis history with bookmarks/tags, statistics, and a visual custom rules editor.

4. **Production CLI** — A Click-based CLI supporting 6 export formats (JSON, PDF, SARIF, JUnit XML, Checkstyle XML, CSV), quality gates, stdin input, `.crossguardignore` file exclusion, and CI config generators for GitHub Actions, GitLab CI, and pre-commit hooks.

5. **Project-Level Analysis** — Recursive directory scanning with framework detection (React, Vue, Angular, etc.) and aggregated compatibility reports.

6. **Polyfill Recommendations** — Automatic suggestions for polyfills that can fix detected compatibility issues.

7. **Data Persistence** — SQLite database (8 tables) storing analysis history, settings, bookmarks, and tags, with automatic schema migrations.