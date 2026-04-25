# Cross Guard — BSc Thesis

**Author:** Aftab Muhammad Eman · **Neptun:** IJE4R1
**Supervisor:** Dr. Dávid Szabó (Dept. of Media and Educational Technology)
**Institution:** Eötvös Loránd University, Faculty of Informatics
**Programme:** Computer Science BSc · **Year of defence:** 2026

> Cross Guard is a desktop static-analysis tool that checks whether an HTML/CSS/JavaScript project will work across Chrome, Firefox, Safari, and Edge. It parses source code, extracts web-platform features, looks them up in the Can I Use database, and produces a compatibility report.

## Repository layout

This workspace has three sibling folders. They are loosely coupled: the LaTeX document cites and screenshots the code, the reference folder informs both but is never compiled into anything.

```
Thesis/
├── code/        # the CrossGuard Python project (separate git repo)
├── latex/       # the thesis document source (elteikthesis class)
└── reference/   # submission paperwork, grading rubric, sample theses
```

Each folder has its own README with details.

### `code/` — CrossGuard v1.0.0

Python 3.9+ package with a CLI (`click`) and a desktop GUI (`customtkinter`). Parsers for HTML (BeautifulSoup), CSS (tinycss2), and JS (tree-sitter) extract web-platform feature usage; the analyzer cross-references against a local Can I Use snapshot in SQLite; results export to PDF, JSON, SARIF, JUnit, Checkstyle, or CSV.

```bash
cd code
pip install -e .
python run_gui.py              # desktop app
python -m src.cli.main --help  # CLI
pytest                         # test suite (~500 tests)
```

See `code/CLAUDE.md` for the full architecture walkthrough and module map.

### `latex/` — thesis document source

Four chapters wired into `elteikthesis_en.tex`: Introduction, User Documentation, Implementation, Conclusion. Bibliography in `elteikthesis.bib` (biblatex + biber). Figures in `images/` (prefixed `cg_`).

```bash
cd latex
latexmk -pdf -xelatex elteikthesis_en.tex
```

Requires the `elteikthesis` document class (ELTE IK template, 2024/04/26) installed in your TeX tree.

### `reference/` — supporting documents

Your topic declaration form, abstract draft, two sample theses for structural reference (BME ASR + ELTE MoodFlicks), and the official ELTE IK BSc grading rubric. Nothing here is compiled — these are inputs to your writing process.

## Naming conventions

- **Files & folders:** lower `snake_case` throughout (`sample_thesis_*.pdf`, `user_documentation.tex`).
- **Python modules:** `snake_case.py`. Classes `PascalCase`, functions/methods `snake_case`.
- **LaTeX chapters:** descriptive (`implementation.tex`, not `impl.tex`).
- **Figures:** prefixed `cg_` + area + subtopic (e.g. `cg_gui_dashboard.png`, `cg_cli_analyze.png`).
- **Reference docs:** `<scope>_<topic>_<qualifier>.<ext>`. Scope prefix tells you who owns it: `crossguard_` = yours, `sample_thesis_` = exemplar, `elte_` = institutional.

## Organisation history

The workspace was reorganised on **2026-04-22**:

- **reference/** — all five documents renamed to descriptive names; added `README.md` index.
- **latex/chapters/** — renamed `intro.tex`/`user.tex`/`impl.tex`/`sum.tex` to full descriptive names; updated `\input` paths in `elteikthesis_en.tex`; added `latex/README.md`.
- **code/examples/** — flat bag of 6 files regrouped into `sample_project/`, `test_fixtures/`, `sample_output/` via `git mv` (history preserved); added `examples/README.md`; updated `CLAUDE.md` layout diagram.
- **code/src/** and **code/tests/** — left untouched. They were already clean, fully `snake_case`, and any rename there would break imports across 85+ files with zero benefit.

If you pulled this on a branch with the old filenames, rename your local references before merging.
