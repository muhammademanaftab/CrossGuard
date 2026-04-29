# Cross Guard — Final Test Walkthrough

End-to-end manual test of every Cross Guard feature using the three sample files in this folder (`example.html`, `example.css`, `example.js`).

The samples were written to be realistic and to trigger a wide mix of features:
- **HTML**: `<dialog>`, `<picture>`, `<video>` with `<track>`, `loading="lazy"`, `data-*` attributes, custom element `<my-widget>`, `<input type="email|search|date|color">`, `meta-theme-color`, `link rel="preload"`, ES module script.
- **CSS**: Grid, Flexbox, `gap`, custom properties, `clamp()`, `aspect-ratio`, container queries, `:has()` selector, `color-mix()`, `backdrop-filter`, `prefers-color-scheme`, `accent-color`.
- **JS**: `async/await`, `fetch()`, optional chaining (`?.`), nullish coalescing (`??`), private class fields (`#x`), `Map`, `Set`, spread operator, template literals, `IntersectionObserver`, `localStorage`, `FormData`, `Object.fromEntries`.

The folder layout looks like this:

```
Thesis/
├── code/                    ← the Cross Guard project
│   ├── Launcher.command     ← Mac launcher
│   ├── Launcher.bat         ← Windows launcher
│   └── ...
└── final_test/              ← you are here
    ├── example.html
    ├── example.css
    ├── example.js
    └── TEST_GUIDE.md
```

Paths in the commands below assume you run them from `code/`. Adjust if you're running from somewhere else.

---

## Part 1 — GUI Tests

### 1.1 Launch the app
- **Mac**: double-click `code/Launcher.command`
- **Windows**: double-click `code/Launcher.bat`
- First run will install Python and the libraries (2-5 minutes). After that it opens straight away.

**Expect:** The Cross Guard window opens with the upload screen. No errors in the terminal.

### 1.2 Drag-and-drop a single file
1. Drag `example.html` into the drop zone.
2. Click **Analyze**.

**Expect:** A results screen with a score card (number + grade), four browser cards (Safari, Firefox, Chrome, Edge), and a list of detected features. HTML count should be around 15-20 features.

### 1.3 Repeat with CSS and JS
1. Go back, drag `example.css`, analyze.
2. Go back, drag `example.js`, analyze.

**Expect:** CSS gives 25-30 features, JS gives 15-20 features. Modern features (`:has()`, container queries, private fields) may appear as "partial" or "unsupported" on older Safari versions.

### 1.4 Multi-file analysis
1. Drop all three files (`example.html`, `example.css`, `example.js`) at once.
2. Analyze.

**Expect:** Combined results, ~50-60 features total, breakdown shows HTML/CSS/JS counts separately.

### 1.5 Change browser targets
1. Click the browser-selector area.
2. Lower the Chrome version to 90 (or whatever the oldest option is).
3. Re-analyze.

**Expect:** The score drops, more features show as "unsupported" or "partial".

### 1.6 Look at issue cards
1. Click any feature in the issues list.
2. Should expand to show: which browsers don't support it, what version it became supported, and a polyfill suggestion if available.

### 1.7 Export to PDF
1. After analyzing all three files, click **Export → PDF**.
2. Save to `final_test/report.pdf`.
3. Open the PDF.

**Expect:** Browser compatibility table, baseline counts, feature inventory split by HTML/CSS/JS with per-browser color indicators.

### 1.8 Export to JSON
1. Click **Export → JSON**.
2. Open the file and check it has `scores`, `summary`, `browsers`, `feature_details`.

### 1.9 History
1. Click the **History** tab in the sidebar.
2. Your past analyses should be there.
3. Click any one — the result loads back.
4. Bookmark one (star icon) and add a tag.

### 1.10 Statistics panel
1. Click the **Statistics** tab.
2. Should show aggregate score over time, top problematic features, file-type breakdown.

### 1.11 Custom rules
1. Click **Custom Rules** in the sidebar.
2. Add a new CSS rule:
   - Feature ID: `my-fancy-feature`
   - Pattern: `\.my-fancy`
   - Description: "My custom feature"
3. Save, then re-analyze `example.css` (it has no `.my-fancy` class, so no detection should fire — that's expected).
4. Add a class `.my-fancy { color: red; }` to `example.css` and re-analyze. Now it should detect it.

### 1.12 AI fix suggestions (optional)
- Only works if you have an `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in your env.
- After analyzing, click on any unsupported feature → **Get AI fix**.
- **Expect:** A code suggestion card.

---

## Part 2 — CLI Tests

Run all commands from inside `code/` with the venv active:

**Mac:**
```bash
cd code
source .venv/bin/activate
```

**Windows:**
```cmd
cd code
.venv\Scripts\activate
```

In the commands below, `../final_test/` refers to this test folder.

### 2.1 Basic analyze (table format, default)
```bash
python -m src.cli.main analyze ../final_test/example.html
python -m src.cli.main analyze ../final_test/example.css
python -m src.cli.main analyze ../final_test/example.js
```
**Expect:** Each prints a colored table with score, grade, browser breakdown, top issues.

### 2.2 JSON format
```bash
python -m src.cli.main analyze ../final_test/example.html --format json
```
**Expect:** JSON to stdout. Pipe through `jq` to inspect: `... --format json | jq '.scores'`.

### 2.3 Save JSON to file
```bash
python -m src.cli.main analyze ../final_test/example.css --format json -o report.json
```
**Expect:** File `report.json` created.

### 2.4 PDF export
```bash
python -m src.cli.main analyze ../final_test/example.html --format pdf -o report.pdf
```
**Expect:** A PDF report written. Open it and check feature inventory.

### 2.5 SARIF (for GitHub Code Scanning)
```bash
python -m src.cli.main analyze ../final_test/example.js --format sarif -o results.sarif
```
**Expect:** Valid SARIF 2.1.0 JSON.

### 2.6 JUnit (for Jenkins / GitLab CI)
```bash
python -m src.cli.main analyze ../final_test/example.css --format junit -o results.xml
```
**Expect:** Valid JUnit XML.

### 2.7 Multiple simultaneous outputs
```bash
python -m src.cli.main analyze ../final_test/example.html \
    --format table \
    --output-sarif results.sarif \
    --output-junit results.xml \
    --output-json results.json \
    --output-pdf report.pdf
```
**Expect:** All four files appear, terminal also shows the table.

### 2.8 Analyze the whole folder
```bash
python -m src.cli.main analyze ../final_test/ --format table
```
**Expect:** All three files analyzed together.

### 2.9 Custom browser targets
```bash
python -m src.cli.main analyze ../final_test/example.css --browsers "chrome:90,safari:14,firefox:88"
```
**Expect:** Lower score because older browsers fail more features.

### 2.10 Quality gates (CI fail conditions)
```bash
# This should pass (grade A territory)
python -m src.cli.main analyze ../final_test/example.html --fail-on-score 60
echo $?   # 0

# This should fail
python -m src.cli.main analyze ../final_test/example.css --fail-on-score 99
echo $?   # 1
```
**Expect:** Exit code 0 (pass) vs 1 (fail). On Windows use `echo %errorlevel%`.

### 2.11 Stdin support
```bash
cat ../final_test/example.js | python -m src.cli.main analyze --stdin --stdin-filename app.js --format table
```
**Expect:** Same analysis as if the file were on disk.

### 2.12 Verbosity flags
```bash
python -m src.cli.main -v analyze ../final_test/example.html       # verbose logs
python -m src.cli.main -q analyze ../final_test/example.html       # quiet
python -m src.cli.main --no-color analyze ../final_test/example.html
python -m src.cli.main --timing analyze ../final_test/example.html
```

### 2.13 Generate CI configs
```bash
python -m src.cli.main init-ci --provider github > github-actions.yml
python -m src.cli.main init-ci --provider gitlab > gitlab-ci.yml
python -m src.cli.main init-hooks --type pre-commit > .pre-commit-config.yaml
```
**Expect:** Three valid config files for each CI provider.

### 2.14 Show config and history
```bash
python -m src.cli.main config        # show effective config
python -m src.cli.main history       # list past analyses
python -m src.cli.main stats         # aggregate statistics
```

### 2.15 Export a past analysis
```bash
python -m src.cli.main history       # find an ID, e.g. 42
python -m src.cli.main export 42 --format pdf -o old_report.pdf
```

### 2.16 Update the Can I Use database
```bash
python -m src.cli.main update-db
```
**Expect:** Downloads the latest Can I Use data (needs internet).

---

## Part 3 — Sanity Checks

### 3.1 Run the test suite
```bash
pytest tests/
```
**Expect:** All 101 tests pass.

### 3.2 GUI ↔ CLI parity
1. Analyze `example.html` in the GUI, note the score.
2. Run `python -m src.cli.main analyze ../final_test/example.html --format json | jq '.scores.weighted_score'`.
3. The two numbers should match.

### 3.3 PDF inventory dedup
1. Analyze all three files in the GUI, export PDF.
2. Open the PDF → Feature inventory section.
3. Each feature should appear **only once** per category, even if used in multiple places.

### 3.4 No silent crashes
- Try a deliberately broken file: create `bad.html` with `<div><span>` (unclosed) and analyze it.
- **Expect:** Cross Guard reports what it could detect, doesn't crash.

---

## What "passing" looks like

| Area | What to look for |
|---|---|
| GUI | Loads, drag-and-drop works, results display, exports succeed, history persists, custom rules apply |
| CLI | All formats produce valid output, quality gates set correct exit codes, stdin works |
| Detection | Each example file detects roughly the right number of features (HTML ~15-20, CSS ~25-30, JS ~15-20) |
| Consistency | GUI and CLI give the same score for the same file |
| PDF | Feature inventory is deduplicated, color indicators appear per browser |
| Tests | `pytest` shows 101 passed |

If any of these fail, note the exact command and output — that's the bug to file.
