# Cross Guard CLI Commands

> **All commands assume you are already inside the `code/` directory** of this repository.

## First-time setup (run once)

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows (PowerShell or CMD)
pip install -r requirements.txt
```

## Returning to the project later (every new terminal session)

You only need to re-activate the virtual environment, not reinstall:

```bash
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows
```

After activation, every command below works exactly as written.

> On macOS the system command is `python3`, not `python`. Once the venv is activated, both work because the venv exposes a `python` symlink. The commands below use `python3` so they keep working **before, during, and after** activation.

> The commands use `python3 -m src.cli.main` because that always works without installing the package as a script. If you ran `pip install -e .` you can replace it with `crossguard` everywhere.

The example files used (`examples/sample_project/sample.html`, etc.) already exist in this repository.

---

## Table of contents

**Thesis section 2.5**
- [2.5.1 — Running an analysis](#251--running-an-analysis)
- [2.5.2 — Custom browser targets](#252--custom-browser-targets)
- [2.5.3 — AI fix suggestions](#253--ai-fix-suggestions)
- [2.5.4 — Working with previous analyses](#254--working-with-previous-analyses)
- [2.5.5 — Exporting reports](#255--exporting-reports)
- [2.5.6 — Configuration and database updates](#256--configuration-and-database-updates)
- [2.5.7 — CI and automation support](#257--ci-and-automation-support)
- [2.5.8 — Quality gates and exit codes](#258--quality-gates-and-exit-codes)

**Bonus commands (not in the thesis)**
- [Global options (verbosity, color, timing)](#global-options)
- [Multiple output files in one run](#multiple-output-files-in-one-run)
- [Reading from stdin](#reading-from-stdin)
- [Filtering history](#filtering-history)
- [Checking for database updates without downloading](#checking-for-database-updates-without-downloading)

---

## 2.5.1 — Running an analysis

The `analyze` command is the main one. It detects features in a file and prints a compatibility report.

### Default table output

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.js --format table
```

### All five `--format` values

```bash
# Human-readable, fits in the terminal (default)
python3 -m src.cli.main analyze examples/sample_project/sample.js --format table

# One-line summary (handy for shell scripts)
python3 -m src.cli.main analyze examples/sample_project/sample.js --format summary

# Machine-readable JSON
python3 -m src.cli.main analyze examples/sample_project/sample.js --format json

# SARIF 2.1.0 for GitHub Code Scanning
python3 -m src.cli.main analyze examples/sample_project/sample.js --format sarif

# JUnit XML for Jenkins / GitLab CI test reports
python3 -m src.cli.main analyze examples/sample_project/sample.js --format junit
```

### Save the output to a file with `--output`

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css --format json --output report.json
```

---

## 2.5.2 — Custom browser targets

By default Cross Guard checks against the latest versions of Chrome, Firefox, Safari, and Edge. The `--browsers` flag overrides this.

```bash
# One specific Chrome version
python3 -m src.cli.main analyze examples/sample_project/sample.css --browsers "chrome:120"

# Multiple browsers and versions, comma-separated
python3 -m src.cli.main analyze examples/sample_project/sample.css --browsers "chrome:120,firefox:121"

# Add Safari and Edge
python3 -m src.cli.main analyze examples/sample_project/sample.css --browsers "chrome:120,firefox:121,safari:17,edge:120"

# Combine with any output format
python3 -m src.cli.main analyze examples/sample_project/sample.css --browsers "chrome:115,safari:15" --format json
```

> **Important:** the version number is **required** for every browser. The format is always `name:version`. If you don't pass `--browsers` at all, Cross Guard uses the latest versions of Chrome, Firefox, Safari, and Edge by default.
```

---

## 2.5.3 — AI fix suggestions

AI suggestions are off by default. Turn them on per-run with `--ai`, after saving an API key once.

### Save the key once (recommended)

```bash
# Save your API key to the local settings table
python3 -m src.cli.main config --set-api-key sk-your-real-key-here

# Choose the provider (default is anthropic)
python3 -m src.cli.main config --set-ai-provider anthropic
# or
python3 -m src.cli.main config --set-ai-provider openai
```

### Run an analysis with AI

```bash
# Uses the saved key
python3 -m src.cli.main analyze examples/sample_project/sample.css --format table --ai
```

### Override the saved key for a single run

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css --format table --ai --api-key sk-other-key
```

### Override the provider for a single run

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css --format table --ai --ai-provider openai
```

### Use the environment variable instead of saving the key

```bash
export CROSSGUARD_AI_KEY=sk-your-real-key-here
python3 -m src.cli.main analyze examples/sample_project/sample.css --ai
```

### Remove the saved key

```bash
python3 -m src.cli.main config --clear-api-key
```

### Write a PDF report that includes the AI suggestions

Use `--output-pdf` together with `--ai`. This writes a single PDF that contains the full analysis plus the AI fix suggestions section.

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css \
    --ai \
    --output-pdf report.pdf
```

> Note: the `export <ID> --format pdf` command does **not** include AI suggestions. AI is only added to the PDF when the analysis and the export happen in the same `analyze` run, because AI suggestions are not stored in the database. Always use `analyze --ai --output-pdf` if you want AI in the PDF.

---

## 2.5.4 — Working with previous analyses

Every analysis is automatically saved to a local SQLite database (unless auto-save is disabled).

### List recent analyses

```bash
python3 -m src.cli.main history
```

### Show aggregated statistics

```bash
python3 -m src.cli.main stats
```

---

## 2.5.5 — Exporting reports

Use `export <ID> --format <fmt> --output <path>` to export a previously saved analysis. The ID comes from the `history` command.

```bash
# Export analysis #1 as a JSON file
python3 -m src.cli.main export 1 --format json --output report.json

# Export analysis #1 as a PDF file
python3 -m src.cli.main export 1 --format pdf --output report.pdf
```

> The `export` command only supports `json` and `pdf`. SARIF and JUnit XML are produced by the `analyze` command via `--format`.
>
> The `export` command does **not** include AI fix suggestions, because AI data is not stored in the database. To get a PDF with AI suggestions, use `analyze --ai --output-pdf` instead (see Section 2.5.3).

---

## 2.5.6 — Configuration and database updates

### Show the current config

```bash
python3 -m src.cli.main config
```

### Create a default `crossguard.config.json` in the current directory

```bash
python3 -m src.cli.main config --init
```

### Update the local Can I Use database

```bash
python3 -m src.cli.main update-db
```

### Use a config file at a custom path

```bash
python3 -m src.cli.main config --path ./my-custom-config.json
```

---

## 2.5.7 — CI and automation support

### Generate a GitHub Actions workflow

```bash
python3 -m src.cli.main init-ci --provider github
```

This prints a ready-to-use `.github/workflows/crossguard.yml` to stdout. To save it directly:

```bash
mkdir -p .github/workflows
python3 -m src.cli.main init-ci --provider github > .github/workflows/crossguard.yml
```

### Generate a GitLab CI config

```bash
python3 -m src.cli.main init-ci --provider gitlab
```

Save it:

```bash
python3 -m src.cli.main init-ci --provider gitlab > .gitlab-ci.yml
```

### Generate a Git pre-commit hook

```bash
python3 -m src.cli.main init-hooks --type pre-commit
```

Save it:

```bash
python3 -m src.cli.main init-hooks --type pre-commit > .pre-commit-config.yaml
```

---

## 2.5.8 — Quality gates and exit codes

Quality gates make the command fail (exit code 1) if compatibility drops below a threshold. Useful for CI pipelines.

### Fail if score drops below a threshold

```bash
# Fails (exit 1) if the score is below 80
python3 -m src.cli.main analyze examples/sample_project/sample.css --fail-on-score 80
```

### Limit the number of unsupported features

```bash
# Fails if more than 5 features are unsupported
python3 -m src.cli.main analyze examples/sample_project/sample.css --fail-on-errors 5
```

### Limit the number of partial-support features

```bash
# Fails if more than 10 features have partial support
python3 -m src.cli.main analyze examples/sample_project/sample.css --fail-on-warnings 10
```

### Combine multiple gates

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css \
    --fail-on-score 80 \
    --fail-on-errors 5 \
    --fail-on-warnings 10
```

### Exit codes used by Cross Guard

| Code | Meaning |
|---|---|
| `0` | Success — analysis ran and all gates passed |
| `1` | Compatibility issues found, or a quality gate failed |
| `2` | Execution error — invalid argument, missing file, unreadable input |

### Use the exit code in a shell script

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css --fail-on-score 80
if [ $? -eq 0 ]; then
    echo "Build OK"
else
    echo "Compatibility issues — blocking the build"
fi
```

---

## Bonus commands (not in the thesis)

The following commands and flags exist in the CLI but are not described in the thesis. They are still fully supported.

### Global options

> ⚠ **Position matters.** Global flags like `-v`, `-q`, `--debug`, `--no-color`, and `--timing` must come **before** the command name (e.g. before `analyze`, `export`, `history`). They are not options of the individual commands.
>
> ✅ Correct:&nbsp;&nbsp;`python3 -m src.cli.main -v analyze file.js`
> ❌ Wrong:&nbsp;&nbsp;&nbsp;&nbsp;`python3 -m src.cli.main analyze file.js -v` → "No such option: -v"

```bash
# Verbose output (-v info, -vv debug, -vvv trace)
python3 -m src.cli.main -v analyze examples/sample_project/sample.js

# Maximum verbosity (same as -vvv)
python3 -m src.cli.main --debug analyze examples/sample_project/sample.js

# Quiet mode — suppress all non-essential output
python3 -m src.cli.main -q analyze examples/sample_project/sample.js

# Disable colored output
python3 -m src.cli.main --no-color analyze examples/sample_project/sample.js

# Print elapsed time to stderr
python3 -m src.cli.main --timing analyze examples/sample_project/sample.js

# Works on every subcommand, not just analyze:
python3 -m src.cli.main -v export 1 --format pdf --output report.pdf
python3 -m src.cli.main --no-color history --limit 5
python3 -m src.cli.main --timing stats
```

You can stack them:

```bash
python3 -m src.cli.main -v --timing --no-color analyze examples/sample_project/sample.js
```

### Multiple output files in one run

Save the same analysis to several files at once.

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css \
    --format table \
    --output-sarif results.sarif \
    --output-junit results.xml \
    --output-json results.json \
    --output-pdf results.pdf
```

This is useful in CI: print the table to the build log, save SARIF for GitHub, save JUnit for the test report, save JSON for any custom tooling, and save a PDF for human review, all in a single run.

### Reading from stdin

Pipe file content directly into Cross Guard. The `--stdin-filename` is needed so the parser knows which language to use.

```bash
# JavaScript via stdin
echo "const x = Promise.resolve();" | python3 -m src.cli.main analyze --stdin --stdin-filename app.js --format table

# CSS via stdin
echo ".container { display: grid; }" | python3 -m src.cli.main analyze --stdin --stdin-filename style.css --format json

# HTML via stdin
echo "<dialog open>Hello</dialog>" | python3 -m src.cli.main analyze --stdin --stdin-filename index.html --format summary
```

You can pipe a real file too:

```bash
cat examples/sample_project/sample.js | python3 -m src.cli.main analyze --stdin --stdin-filename sample.js --format table
```

### Filtering history

```bash
# Show only the last 5 entries
python3 -m src.cli.main history --limit 5

# Show only CSS analyses
python3 -m src.cli.main history --type css

# Combine both
python3 -m src.cli.main history --limit 10 --type js
```

### Checking for database updates without downloading

```bash
python3 -m src.cli.main update-db --check
```

### Use a custom config file for a single run

```bash
python3 -m src.cli.main analyze examples/sample_project/sample.css --config ./my-config.json --format table
```

### Set the format through an environment variable

```bash
export CROSSGUARD_FORMAT=json
python3 -m src.cli.main analyze examples/sample_project/sample.css
```

### Set browsers through an environment variable

```bash
export CROSSGUARD_BROWSERS="chrome:120,firefox:121"
python3 -m src.cli.main analyze examples/sample_project/sample.css
```

---

## Quick reference card

| Command | What it does |
|---|---|
| `analyze <file>` | Run a compatibility analysis |
| `export <id>` | Export a saved analysis to JSON or PDF |
| `history` | List previously saved analyses |
| `stats` | Show aggregated statistics |
| `config` | Show, init, or modify configuration and saved API key |
| `update-db` | Refresh the local Can I Use database |
| `init-ci` | Generate a GitHub Actions or GitLab CI workflow |
| `init-hooks` | Generate a Git pre-commit hook |

| Useful global flag | Effect |
|---|---|
| `-v` / `-vv` / `-vvv` | Increase verbosity |
| `-q` | Quiet mode |
| `--no-color` | Disable colored output |
| `--timing` | Print elapsed time to stderr |

| Important `analyze` flag | Effect |
|---|---|
| `--format <fmt>` | `table`, `summary`, `json`, `sarif`, or `junit` |
| `--browsers "<list>"` | e.g. `"chrome:120,firefox:121"` |
| `--ai` | Enable AI fix suggestions |
| `--output <path>` | Save the result to a file |
| `--fail-on-score <n>` | Exit 1 if score is below `n` |
| `--fail-on-errors <n>` | Exit 1 if more than `n` features are unsupported |
| `--fail-on-warnings <n>` | Exit 1 if more than `n` features have partial support |

---

## Need help

To see the help for any command:

```bash
python3 -m src.cli.main --help
python3 -m src.cli.main analyze --help
python3 -m src.cli.main config --help
python3 -m src.cli.main export --help
```
