# Cross Guard CLI — How It Works

## What is a CLI?

CLI stands for Command Line Interface. Instead of clicking buttons in a window (GUI), you type commands in a terminal. You already use CLIs — `git`, `python`, `pip` are all CLI tools.

Cross Guard has both a GUI (desktop app) and a CLI (terminal commands). Both use the same backend, same parsers, same analyzer. Just different ways to interact.

---

## Why Have a CLI?

1. **Automation** — you can't click a button automatically, but you CAN run a command automatically
2. **Speed** — typing a command is faster than opening an app and dragging files
3. **CI/CD** — servers that check your code don't have screens, only terminals

---

## How to Run It

```bash
python -m src.cli.main <command> [options]
```

---

## The 8 Commands

### 1. `analyze` — Check a File for Compatibility

The main command. Used 90% of the time.

```bash
# Analyze a CSS file
python -m src.cli.main analyze examples/sample.css
```
Output: a table showing score (89.1%), grade (B), 16 features found, `css-filter-function` unsupported in Chrome/Firefox/Edge.

```bash
# Analyze a JS file
python -m src.cli.main analyze examples/sample.js
```
Output: score (90.0%), grade (A), 20 features found, all supported.

```bash
# Analyze an HTML file
python -m src.cli.main analyze examples/sample.html
```
Output: score (96.6%), grade (A), 11 features found, `input-datetime` partial in Firefox/Safari.

```bash
# Analyze a whole directory
python -m src.cli.main analyze examples/
```
Output: combined results for all .html, .css, .js files in the folder.

```bash
# Choose specific browsers
python -m src.cli.main analyze examples/sample.css --browsers "chrome:120,safari:13"
```
Output: same file but checked against older Safari — more failures will show up.

```bash
# Change output format
python -m src.cli.main analyze examples/sample.css --format json
python -m src.cli.main analyze examples/sample.css --format summary
python -m src.cli.main analyze examples/sample.css --format sarif
```

```bash
# Save output to a file
python -m src.cli.main analyze examples/sample.css --format json --output report.json
```

```bash
# Multiple outputs at once (table to screen + JSON and CSV to files)
python -m src.cli.main analyze examples/sample.css --format table --output-json report.json --output-csv report.csv
```

```bash
# Pipe content directly (no file needed)
echo "div { display: grid; }" | python -m src.cli.main analyze --stdin --stdin-filename test.css
```

---

### 2. `history` — See Past Analyses

Every analysis is saved to a SQLite database. This command shows them.

```bash
# Show last 20 analyses
python -m src.cli.main history
```
Output: a list of past analyses with ID, file name, score, grade, date.

```bash
# Show only 5
python -m src.cli.main history --limit 5
```

```bash
# Filter by file type
python -m src.cli.main history --type css
```

---

### 3. `stats` — Overall Statistics

```bash
python -m src.cli.main stats
```
Output: total analyses run, average score, most common issues, score trends.

---

### 4. `export` — Export a Past Analysis

First check history to get an ID, then export it.

```bash
# See history to find the ID
python -m src.cli.main history --limit 5

# Export that analysis as JSON
python -m src.cli.main export 111 --format json --output report.json

# Export as PDF
python -m src.cli.main export 111 --format pdf --output report.pdf
```

---

### 5. `config` — View or Create Configuration

```bash
# Show current config (browsers, output format)
python -m src.cli.main config
```
Output: JSON showing default browsers and output format.

```bash
# Create a crossguard.config.json file in your project
python -m src.cli.main config --init
```
Output: creates the file, you can then edit it to set default browsers, output format, etc.

---

### 6. `update-db` — Update Can I Use Database

```bash
python -m src.cli.main update-db
```
Output: downloads the latest Can I Use data so browser support info is up to date.

---

### 7. `init-ci` — Generate CI/CD Config

Generates a ready-to-use config file for automatic checking on every code push.

```bash
# For GitHub Actions
python -m src.cli.main init-ci --provider github
```
Output: prints a YAML workflow file. Save it as `.github/workflows/crossguard.yml` in your project. Now GitHub automatically runs Cross Guard on every push/pull request.

```bash
# For GitLab CI
python -m src.cli.main init-ci --provider gitlab
```
Output: prints a YAML snippet. Add it to `.gitlab-ci.yml`.

---

### 8. `init-hooks` — Generate Git Hook Config

```bash
python -m src.cli.main init-hooks --type pre-commit
```
Output: prints a config snippet. Add it to `.pre-commit-config.yaml`. Now Cross Guard runs before every git commit on your machine — blocks the commit if compatibility is too low.

---

## Global Options

These go BEFORE the command name:

```bash
python -m src.cli.main [option] <command>
```

| Option | What It Does |
|--------|-------------|
| `-v` | Verbose — show logs (what's loading, what's parsing) |
| `-vv` | More verbose |
| `-q` | Quiet — no logs, only output |
| `--no-color` | No colors (useful when saving to files) |
| `--timing` | Show how long the analysis took |

Examples:
```bash
# See what's happening behind the scenes
python -m src.cli.main -v analyze examples/sample.css

# Completely silent except for the result
python -m src.cli.main -q analyze examples/sample.css --format json

# See elapsed time
python -m src.cli.main --timing analyze examples/sample.css
```

---

## Quality Gates

Quality gates make the CLI fail (exit code 1) if results don't meet your standards. Used in CI/CD to block bad code.

```bash
# Fail if score is below 80
python -m src.cli.main analyze examples/sample.css --fail-on-score 80

# Fail if more than 5 unsupported features
python -m src.cli.main analyze examples/sample.css --fail-on-errors 5

# Fail if more than 10 partial features
python -m src.cli.main analyze examples/sample.css --fail-on-warnings 10

# Combine multiple gates
python -m src.cli.main analyze examples/sample.css --fail-on-score 80 --fail-on-errors 5
```

Check the exit code after:
```bash
python -m src.cli.main analyze examples/sample.css --fail-on-score 95
echo "Exit code: $?"
# Output: Exit code: 1  (failed — score 89 is below 95)
```

---

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Table | `--format table` | Reading in terminal (default) |
| JSON | `--format json` | Piping to other tools, saving data |
| Summary | `--format summary` | Quick one-line check |
| SARIF | `--format sarif` | GitHub Code Scanning |
| JUnit | `--format junit` | Jenkins, GitLab CI test reports |
| Checkstyle | `--format checkstyle` | SonarQube |
| CSV | `--format csv` | Spreadsheets |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| **0** | Success — all good, gates passed |
| **1** | Failure — issues found or gate failed |
| **2** | Error — bad input, file not found |

CI/CD systems read these codes: 0 = build passes, 1 or 2 = build fails.

---

## What is CI/CD?

CI/CD = Continuous Integration / Continuous Deployment. It means automatically checking code every time someone pushes to GitHub/GitLab.

**Without CI/CD:** someone writes CSS that doesn't work in Safari → nobody notices → website breaks for Safari users.

**With CI/CD:** someone pushes code → GitHub automatically runs Cross Guard → score is 65 → build fails → developer sees red X → fixes the issue before merging.

The `init-ci` and `init-hooks` commands generate the config files needed to set this up.

---

## Where the CLI Code Lives

```
src/cli/
├── main.py         ← All 8 commands (the main file)
├── context.py      ← Stores verbosity, color, timing settings
├── formatters.py   ← Makes output pretty (colors, tables)
├── gates.py        ← Pass/fail logic (3 if-statements)
└── generators.py   ← CI config YAML templates
```

The CLI imports only from `src/api/` (AnalyzerService) — same as the GUI. It never touches parsers or the analyzer directly.
