# Thesis Source (LaTeX)

LaTeX source for *Cross Guard: A Tool to Check if Your Website Works on All Browsers* — BSc thesis, Eötvös Loránd University, Faculty of Informatics.

## Build

```bash
# From this folder
latexmk -pdf -xelatex elteikthesis_en.tex
# or minimally
xelatex elteikthesis_en && biber elteikthesis_en && xelatex elteikthesis_en && xelatex elteikthesis_en
```

The document class `elteikthesis` (version 2024/04/26) is **not vendored** in this folder. It must be installed in your TeX tree (TeX Live / MiKTeX) or placed next to `elteikthesis_en.tex` as `elteikthesis.cls`. Pull it from the faculty template repository if missing.

## Layout

```
LaTeX/
├── elteikthesis_en.tex   # main document — metadata, \input order, front/back matter
├── elteikthesis.bib      # bibliography (17 entries, biber/biblatex)
├── chapters/
│   ├── introduction.tex         # ch. 1 — problem, motivation, contributions
│   ├── user_documentation.tex   # ch. 2 — end-user guide (GUI + CLI)
│   ├── implementation.tex       # ch. 3 — developer docs, architecture, parsers, DB, AI
│   └── conclusion.tex           # ch. 4 — summary and future work
└── images/                       # figures referenced by chapters (cg_*.png)
```

## Figures

All figures live in `images/` and are referenced bare-filename (no path, no extension) via `\includegraphics{cg_...}`. Naming convention: `cg_<area>_<subtopic>.png`.

**Orphan:** `images/cg_directory.png` exists but is not referenced by any chapter. Either wire it into `implementation.tex` or delete it before final submission.

## Renaming note (2026-04-22)

Chapter filenames were changed from cryptic (`intro.tex`, `user.tex`, `impl.tex`, `sum.tex`) to descriptive. If you have local branches or collaborators with the old names, update their `\input` lines to match.
