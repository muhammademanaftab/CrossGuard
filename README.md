# Cross Guard

> A static analysis tool that checks whether HTML, CSS, and JavaScript source files will work across modern web browsers.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Tests: 96](https://img.shields.io/badge/tests-96%20passing-brightgreen.svg)
![Status: Beta](https://img.shields.io/badge/status-beta-yellow.svg)

Cross Guard parses HTML, CSS, and JavaScript files, extracts the web platform features they use (e.g. CSS Grid, Promises, the `<dialog>` element), looks each one up in the [Can I Use](https://caniuse.com/) compatibility database, and reports which features are supported, partially supported, or unsupported in the user's chosen target browsers.

It runs both as a **desktop GUI** and as a **command-line tool** that integrates into CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, pre-commit hooks).

This repository also contains the **BSc thesis manuscript** describing the design and implementation of the tool, written for Eötvös Loránd University, Faculty of Informatics.

---

## Table of contents

- [About](#about)
- [Features](#features)
- [Repository structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Tech stack](#tech-stack)
- [Building the thesis](#building-the-thesis)
- [Common tasks](#common-tasks)
- [License](#license)
- [Author](#author)

---

## About

Modern web development depends on HTML, CSS, and JavaScript features that are not uniformly supported across browsers. A feature that works in recent Chrome may fail in older Safari, and a Container Query in 2023 Chrome will not run in Internet Explorer at all. Cross Guard automates this check.

Each analysis produces:

- a **compatibility score** from 0 to 100,
- a **letter grade** from A to F,
- a **per-browser breakdown** for Chrome, Firefox, Safari, and Edge,
- **polyfill recommendations** for unsupported features, and
- optional **AI-generated code fix suggestions** through OpenAI or Anthropic.

The tool is aimed at web developers who want a fast local check before shipping, and at CI/CD pipelines that need machine-readable compatibility reports.

---

## Features

### Analysis
- **Multi-format parsing** — HTML (BeautifulSoup), CSS (tinycss2 AST), JavaScript (tree-sitter AST + regex fallback)
- **Compatibility scoring** — weighted score from 0 to 100, letter grade A through F
- **Custom rules** — user-defined feature detection through a JSON file or a GUI editor
- **Polyfill suggestions** — recommends npm packages or `@supports`-based CSS fallbacks for unsupported features
- **AI fix suggestions** — optional LLM-powered code fixes through OpenAI or Anthropic

### Desktop GUI
- Drag-and-drop file upload
- Results dashboard with score cards, browser cards, and issue cards
- Analysis history with bookmarks and tags
- Aggregated statistics (score trends, top problematic features)
- Visual editor for custom detection rules

### CLI and CI/CD
- Four export formats: **JSON**, **PDF**, **SARIF 2.1.0**, **JUnit XML**
- Quality gates: `--fail-on-score`, `--fail-on-errors`, `--fail-on-warnings` (exit code 1 on failure)
- CI scaffolding: `init-ci` generates GitHub Actions or GitLab CI workflows
- Pre-commit hooks: `init-hooks` generates a pre-commit hook config
- Stdin support for piping file content

---

## Repository structure

```
Thesis/
├── code/        Cross Guard application (Python project: CLI + desktop GUI)
└── latex/       Thesis manuscript source (LaTeX, ELTE template)
```

The two directories are independent. The thesis cites and screenshots the code; the code does not depend on the thesis.

---

## Installation

Cross Guard requires **Python 3.9 or newer**, **pip**, and **Git**.

```bash
# Clone the repository
git clone <repository-url>
cd Thesis/code

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt
```

To use only the GUI or only the CLI, install just those extras through `pyproject.toml`:

```bash
pip install -e ".[gui]"   # GUI only
pip install -e ".[cli]"   # CLI only
```

---

## Usage

### Desktop GUI

```bash
python run_gui.py
```

The window opens on the upload page. Drag files in or click to pick them, choose target browsers from the right-hand selector, and click **Analyze**. Results appear in a dashboard with a score card, browser cards, an issues list, and polyfill recommendations.

### Command line

```bash
# Analyse a single file with table output (the default)
python -m src.cli.main analyze path/to/file.js --format table

# Analyse a directory, target specific browser versions
python -m src.cli.main analyze src/ --browsers "chrome:120,firefox:121"

# Generate a SARIF report for GitHub Code Scanning
python -m src.cli.main analyze src/ --format sarif -o results.sarif

# Apply quality gates (exit 1 if score drops below 80)
python -m src.cli.main analyze src/ --fail-on-score 80

# Generate a GitHub Actions workflow file
python -m src.cli.main init-ci --provider github

# Pipe content via stdin
echo "const x = Promise.resolve();" | \
  python -m src.cli.main analyze --stdin --stdin-filename app.js --format sarif
```

Run `python -m src.cli.main --help` for the full command list.

### CI/CD example (GitHub Actions)

```yaml
- name: Check browser compatibility
  run: crossguard analyze src/ --format sarif --output-sarif results.sarif --fail-on-score 80

- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

---

## Tech stack

| Area | Library |
|---|---|
| GUI | CustomTkinter 5.2+, tkinterdnd2-universal 1.7+ |
| CLI | Click 8.1+ |
| HTML parsing | BeautifulSoup4 4.12+, lxml 5.0+ |
| CSS parsing | tinycss2 1.2+ (AST-based) |
| JavaScript parsing | tree-sitter 0.21.3, tree-sitter-languages 1.10.2 |
| Persistence | SQLite (Python standard library) |
| PDF reports | reportlab 4.0+ |
| Charts | matplotlib 3.8+ |
| HTTP / API | requests 2.31+ |
| Testing | pytest 7.0+ |

### Project layout

```
code/
├── src/
│   ├── ai/         AI fix-suggestion service (OpenAI / Anthropic)
│   ├── analyzer/   Compatibility checker, scorer, Can I Use database loader
│   ├── api/        AnalyzerService facade and shared dataclass schemas
│   ├── cli/        Click commands, formatters, gates, CI generators
│   ├── config/     Layered configuration loader
│   ├── database/   SQLite connection singleton, repositories, migrations
│   ├── export/     JSON, PDF, SARIF, JUnit XML exporters
│   ├── gui/        CustomTkinter application, widgets, theme
│   ├── parsers/    HTML, CSS, JS parsers and feature maps
│   ├── polyfill/   Polyfill loader, recommendation service, generator
│   └── utils/      Logging configuration, feature-name lookups
├── tests/          96 tests (black box, white box, integration)
├── data/caniuse/   Local Can I Use database (downloaded via update-db)
├── examples/       Sample inputs and example reports
├── run_gui.py      GUI entry point
└── pyproject.toml  Package metadata and dependencies
```

The full architecture, design patterns, and module-by-module walkthrough are described in Chapter 3 of the thesis (*Developer Documentation*).

---

## Building the thesis

The `latex/` directory contains the LaTeX source for the thesis manuscript, built on the official **ELTE Faculty of Informatics** template (`elteikthesis` document class, 2024/04/26).

```bash
cd latex
latexmk -pdf -xelatex elteikthesis_en.tex
```

Or run the steps manually:

```bash
xelatex elteikthesis_en
biber elteikthesis_en
xelatex elteikthesis_en
xelatex elteikthesis_en
```

The `elteikthesis` class is **not vendored** in this repository. It must be installed in your TeX tree (TeX Live or MiKTeX) or placed alongside `elteikthesis_en.tex` as `elteikthesis.cls`.

---

## Common tasks

| Task | Command (run from repository root) |
|---|---|
| Launch GUI | `cd code && python run_gui.py` |
| Analyse a file (table output) | `cd code && python -m src.cli.main analyze file.js --format table` |
| Generate a SARIF report for CI | `cd code && python -m src.cli.main analyze src/ --format sarif -o results.sarif` |
| Generate GitHub Actions workflow | `cd code && python -m src.cli.main init-ci --provider github` |
| Run all tests | `cd code && pytest tests/ -q` |
| Update Can I Use database | `cd code && python -m src.cli.main update-db` |
| Build the thesis PDF | `cd latex && latexmk -pdf -xelatex elteikthesis_en.tex` |

---

## License

The Cross Guard codebase under `code/` is released under the **MIT License** (see `code/pyproject.toml`).

The thesis manuscript under `latex/` is the author's own academic work and is subject to the policies of Eötvös Loránd University, Faculty of Informatics. Reproduction beyond fair academic use requires the author's permission.

---

## Author

| | |
|---|---|
| **Author** | Aftab Muhammad Eman |
| **Neptun code** | IJE4R1 |
| **Supervisor** | Dr. Dávid Szabó (Department of Media and Educational Technology) |
| **Institution** | Eötvös Loránd University, Faculty of Informatics |
| **Programme** | Computer Science BSc |
| **Year of defence** | 2026 |
