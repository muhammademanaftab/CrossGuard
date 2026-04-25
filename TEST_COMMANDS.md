# Cross Guard — Thesis CLI Command Tests

Every command from Chapter 2 of the thesis, with real file paths so you can copy-paste and test end-to-end.

**Before you start** — open a terminal and `cd` into the project, and activate the venv:

```bash
cd /Users/home/Documents/Educational/Thesis/code
source .venv/bin/activate
```

The sample files used throughout are:

```
examples/sample_project/sample.html
examples/sample_project/sample.css
examples/sample_project/sample.js
```

All outputs written by the tests go into `/tmp/` so they don't clutter the project.

---

## 1. Setup verification (Code 2.1 / 2.2 / 2.3)

You've already installed everything, but to verify:

```bash
python --version
```

Launch the GUI or show CLI help:

```bash
python run_gui.py
```

```bash
python -m src.cli.main --help
```

---

## 2. Basic analysis (Code 2.4)

Analyze each sample file in table format:

```bash
python -m src.cli.main analyze examples/sample_project/sample.html --format table
```

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --format table
```

```bash
python -m src.cli.main analyze examples/sample_project/sample.js --format table
```

Analyze the whole sample project directory:

```bash
python -m src.cli.main analyze examples/sample_project/ --format table
```

---

## 3. Analyze against specific browsers (Code 2.5)

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --browsers "chrome:120,firefox:121"
```

With older browsers (score should drop):

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --browsers "chrome:80,firefox:70,safari:13"
```

---

## 4. AI fix suggestions (Code 2.6) — needs API key

**Save an API key once** (replace `sk-...` with your real key):

```bash
python -m src.cli.main config --set-api-key sk-REPLACE-WITH-REAL-KEY
python -m src.cli.main config --set-ai-provider anthropic
```

**Run an analysis with AI suggestions enabled:**

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --format table --ai
```

**Override the saved key for one run:**

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --format table --ai --api-key sk-OTHER-KEY
```

**Clear the saved key:**

```bash
python -m src.cli.main config --clear-api-key
```

> ⚠️ If no key is configured, `--ai` just prints a warning and the analysis runs without AI suggestions — this is safe to test even without a real key.

---

## 5. History and statistics (Code 2.7)

First make sure you have a few analyses in history by running a few of the analyze commands above, then:

```bash
python -m src.cli.main history
```

```bash
python -m src.cli.main stats
```

---

## 6. Export past analysis (Code 2.9)

> 📌 The number `42` in the thesis is an **example** — replace it with a real ID from your history output.
>
> ⚠️ Do **NOT** type angle brackets (`<` `>`) in the terminal — zsh interprets those as file redirection. Wherever you see `ID_HERE` below, just type the plain number (e.g. `281`).

**Step 1: find an ID from history**
```bash
python -m src.cli.main history
```
Take note of the first column (the ID).

**Step 2: export that ID**

Replace `ID_HERE` below with the number you saw (e.g. `1`, `2`, …):

```bash
python -m src.cli.main export ID_HERE --format json --output /tmp/report.json
```

```bash
python -m src.cli.main export ID_HERE --format pdf --output /tmp/report.pdf
```

Open them to verify:

```bash
open /tmp/report.json
open /tmp/report.pdf
```

---

## 7. Config and database update (Code 2.10)

**Show current config** (API keys are masked — only first/last 4 chars shown):

```bash
python -m src.cli.main config
```

**Initialise a new `crossguard.config.json` in the current directory:**

```bash
python -m src.cli.main config --init
```

> 📌 This creates `crossguard.config.json` in `code/`. Delete it afterwards if you don't want it: `rm crossguard.config.json`

**Update the Can I Use database from npm** (requires internet):

```bash
python -m src.cli.main update-db
```

---

## 8. CI workflows and Git hooks (Code 2.11)

> 📌 These commands **write files into the current directory** — run them from `/tmp/ci-test/` so they don't pollute the project.

```bash
mkdir -p /tmp/ci-test && cd /tmp/ci-test
```

Generate a GitHub Actions workflow:

```bash
python -m src.cli.main init-ci --provider github
```

Generate a GitLab CI config:

```bash
python -m src.cli.main init-ci --provider gitlab
```

Generate a pre-commit hook config:

```bash
python -m src.cli.main init-hooks --type pre-commit
```

Check what got created:

```bash
ls -la .github/workflows/ .gitlab-ci.yml .pre-commit-config.yaml 2>/dev/null
```

**Return to the project:**

```bash
cd /Users/home/Documents/Educational/Thesis/code
```

---

## 9. Quality gates (Code 2.12)

The thesis listing omits the target file — you need to give it one. Using the sample project:

**Fail if the compatibility score drops below 80:**

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --fail-on-score 80
```

**Limit errors and warnings independently:**

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --fail-on-errors 5
```

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --fail-on-warnings 10
```

**Combine multiple gates in a single command:**

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --fail-on-score 80 --fail-on-errors 5
```

**Check the exit code after each run** (0 = pass, 1 = gate failed, 2 = error):

```bash
echo $?
```

**Force a gate FAILURE to see it in action** — use a high threshold:

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --fail-on-score 99
echo $?   # should print 1
```

---

## 10. All export formats (bonus — from CLAUDE.md)

> ⚠️ **Important**: `analyze --format` accepts **`table | json | summary | sarif | junit`** — but **NOT `pdf`**. PDF is only available via the `export` command (post-analysis), so it's covered separately below.

Test the 3 machine-readable live formats:

```bash
python -m src.cli.main analyze examples/sample_project/sample.css --format json  -o /tmp/report.json
python -m src.cli.main analyze examples/sample_project/sample.css --format sarif -o /tmp/report.sarif
python -m src.cli.main analyze examples/sample_project/sample.css --format junit -o /tmp/report.xml
```

For PDF, use the `export` command on the most-recent analysis:

```bash
LATEST=$(python -m src.cli.main history | awk 'NR==3 {print $1}')
python -m src.cli.main export $LATEST --format pdf --output /tmp/report.pdf
open /tmp/report.pdf
```

Multiple outputs at once (one run, three files):

```bash
python -m src.cli.main analyze examples/sample_project/sample.css \
    --format table \
    --output-sarif /tmp/multi.sarif \
    --output-junit /tmp/multi.xml
```

Pipe content via stdin:

```bash
echo "const x = Promise.resolve();" | python -m src.cli.main analyze --stdin --stdin-filename app.js --format json
```

Verbosity / color / timing flags:

```bash
python -m src.cli.main -v analyze examples/sample_project/sample.js
python -m src.cli.main -q analyze examples/sample_project/sample.js
python -m src.cli.main --no-color analyze examples/sample_project/sample.js
python -m src.cli.main --timing analyze examples/sample_project/sample.js
```

---

## 11. Cleanup (optional)

Remove the test artifacts:

```bash
rm -f /tmp/report.* /tmp/multi.*
rm -rf /tmp/ci-test
rm -f crossguard.config.json   # only if you ran `config --init`
```

---

## Quick sanity check — run everything that doesn't need API keys

Copy-paste this whole block to run a full smoke test:

```bash
cd /Users/home/Documents/Educational/Thesis/code
source .venv/bin/activate

echo "=== 1. Help ==="
python -m src.cli.main --help | head -20

echo "=== 2. Analyze each file ==="
python -m src.cli.main analyze examples/sample_project/sample.html --format summary
python -m src.cli.main analyze examples/sample_project/sample.css --format summary
python -m src.cli.main analyze examples/sample_project/sample.js --format summary

echo "=== 3. Analyze with specific browsers ==="
python -m src.cli.main analyze examples/sample_project/sample.css --browsers "chrome:120,firefox:121" --format summary

echo "=== 4. History and stats ==="
python -m src.cli.main history
python -m src.cli.main stats

echo "=== 5. All export formats (PDF is via 'export', not 'analyze') ==="
python -m src.cli.main analyze examples/sample_project/sample.css --format json  -o /tmp/r.json
python -m src.cli.main analyze examples/sample_project/sample.css --format sarif -o /tmp/r.sarif
python -m src.cli.main analyze examples/sample_project/sample.css --format junit -o /tmp/r.xml
LATEST=$(python -m src.cli.main history | awk 'NR==3 {print $1}')
python -m src.cli.main export $LATEST --format pdf --output /tmp/r.pdf
ls -la /tmp/r.*

echo "=== 6. Export from history ==="
LAST_ID=$(python -m src.cli.main history | awk 'NR==3 {print $1}')
python -m src.cli.main export $LAST_ID --format json --output /tmp/export.json
python -m src.cli.main export $LAST_ID --format pdf  --output /tmp/export.pdf
ls -la /tmp/export.*

echo "=== 7. Config ==="
python -m src.cli.main config

echo "=== 8. CI workflows (in /tmp) ==="
mkdir -p /tmp/ci-test && cd /tmp/ci-test
python -m src.cli.main init-ci --provider github
python -m src.cli.main init-ci --provider gitlab
python -m src.cli.main init-hooks --type pre-commit
ls -la .github/workflows/ .gitlab-ci.yml .pre-commit-config.yaml 2>/dev/null
cd /Users/home/Documents/Educational/Thesis/code

echo "=== 9. Quality gates ==="
python -m src.cli.main analyze examples/sample_project/sample.css --fail-on-score 80  && echo "gate PASSED (exit 0)"
python -m src.cli.main analyze examples/sample_project/sample.css --fail-on-score 99  || echo "gate FAILED as expected (exit $?)"

echo "=== ALL DONE ==="
```
