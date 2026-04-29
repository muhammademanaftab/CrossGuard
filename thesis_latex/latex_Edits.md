# Thesis LaTeX edits — what to change, what to leave alone

Each entry lists the file, the exact line, what the text currently says, what
to replace it with, and a short reason. The list is short on purpose — only
edits that genuinely matter.

All thesis paths live under `thesis_latex/samples_en/`.

---

## Already done (no action needed)

These were updated in earlier passes:

- `user.tex:368` — "or GitLab CI" removed from init-ci description.
- `user.tex:381` — `init-ci --provider gitlab` line removed from listing.
- `impl.tex:235` — "Jenkins for test reporting" (GitLab already removed).
- Test count updated to **101** in `impl.tex:478` and `:541`.

---

## Edits to make (4 in total)

### 1. `sum.tex:22` — Project-Level Analysis is no longer future work

**Why:** The paragraph claims "Cross Guard analyzes individual files or small
groups of files" and lists full project scanning as a future-work item. But
this was shipped — `crossguard analyze src/` now walks directories
recursively, and the GitHub Actions integration depends on it. A reviewer
reading the conclusion will think the feature isn't done when it is.

**Old (line 22):**

> \textbf{Project-Level Analysis.} Currently, Cross Guard analyzes individual files or small groups of files. A natural next step would be to support full project scanning, where the tool recursively processes all HTML, CSS, and JavaScript files in a directory. This would include respecting ignore patterns similar to \texttt{.gitignore}, aggregating results across files into a single project-level report, and identifying which features are used most frequently across the codebase.

**New (line 22):**

> \textbf{Project-Level Analysis.} Cross Guard can now scan a whole project, not just one file at a time. Pointing it at a folder makes it walk through every HTML, CSS, and JavaScript file inside, skip noise folders like \texttt{.git} and \texttt{node\_modules} automatically, and produce one combined report. This is what makes the GitHub Actions integration work: the CI runs a single command on the project folder and uploads one SARIF file with all the findings. There is still room to grow. Cross Guard does not yet read a project's own \texttt{.gitignore} file, so any custom ignore patterns are not honoured. The combined report does not break down scores per file, so the worst-offending file is hidden inside the overall average. And there is no view yet that shows which web features are used most often across the codebase, which would help teams decide where to focus first.

---

### 2. `user.tex:204–214` — add one sentence about overriding built-in rules

**Why:** The thesis describes adding, editing, and deleting custom rules — but
not the new Override-as-custom feature, which lets users replace a built-in
rule's patterns when they produce false positives. This is the practical
answer to "how does a user fix a false positive?" — without it, the section
leaves an obvious gap.

**Where to paste:** Add a new paragraph at the end of subsection
"Custom Rules Manager", just after the existing paragraph that ends with
"...full rule-format specification in Chapter~\ref{ch:impl}."

**New paragraph (paste verbatim):**

> Built-in rules can also be overridden directly. Clicking \emph{Override as custom} on any built-in rule pre-fills the editor with that rule's patterns and saves the modified version as a custom rule that takes precedence over the built-in one. Deleting the override later restores the original. This gives users a clear way to silence false positives in a built-in detection without losing the option to revert.

---

### 3. `user.tex:280` — drop "Jenkins or GitLab" from the JUnit XML row

**Why:** The JUnit XML output format itself was tested (the CLI produces valid
XML and there is a unit test for it). But the integration with Jenkins and
GitLab — actually feeding the file into those CI systems and watching them
display results — was never tested end-to-end. Naming specific systems would
be claiming integration that was not verified.

**Old (line 280):**

```latex
JUnit XML & Compatibility with CI systems such as Jenkins or GitLab. \\ \hline
```

**New:**

```latex
JUnit XML & Standard test-reporting format consumable by many CI systems. \\ \hline
```

---

### 4. `impl.tex:235` — same fix in the narrative paragraph

**Why:** Same reason as edit #3 — keep the wording consistent across the
thesis and avoid claiming Jenkins integration that was not tested.

**Old (mid-paragraph, line 235):**

> ...JUnit XML is compatible with CI systems such as Jenkins for test reporting.

**New:**

> ...JUnit XML follows a widely-supported test-reporting format used by many CI systems for surfacing failures.

---

## Things to leave alone (explicit "do not change")

Tempting candidates, but each has a good reason to stay as-is:

| Candidate | Why I'm leaving it |
|---|---|
| `user.tex:253` ("when a single file is provided") | Still accurate. Single-file mode works exactly as described. The paragraph is incomplete (doesn't mention dir mode) but not wrong. Cosmetic. |
| `impl.tex:315`, `:317` (Chrome 148, Firefox 151, Edge 145 in example output) | Just illustrative SARIF text — not behaviour claims. Out of date but not wrong in context. |
| `user.tex:89` (`# Analyze a single file from the command line`) | An example comment in a code listing. Not a claim that single-file is the only mode. |
| All other JUnit XML mentions (in `intro.tex`, `impl.tex`, `user.tex`, the CLI flag list, etc.) | These describe the format itself, which is real and tested. Only the Jenkins/GitLab name-drops were unverified. |
| `user.tex:368` ("init-ci command creates an example workflow configuration for GitHub Actions") | Already correct — GitLab mention was removed earlier. |
| `intro.tex:32` ("JSON, PDF, SARIF, JUnit XML, Checkstyle XML, and CSV") | Slightly aspirational — Cross Guard ships JSON, PDF, SARIF, and JUnit XML. Checkstyle and CSV are not implemented. **Worth checking** — see note at bottom. |
| Anything about TypeScript, PHP, or framework support not being there | Already framed as future work in `sum.tex`. Accurate. |

---

## One thing worth double-checking yourself

**`intro.tex:32` lists Checkstyle XML and CSV as supported export formats.**
The currently-shipped formats are JSON, PDF, SARIF, and JUnit XML — that's
**4**, matching what `CLAUDE.md` and `impl.tex` say (`4 Export Formats`).
If Checkstyle and CSV were planned but not implemented, that line in `intro.tex`
contradicts the rest of the thesis.

**Suggested fix if needed (line 32):**

```latex
The fifth goal is to support multiple export formats including JSON, PDF, SARIF, and JUnit XML so that results can be used in different contexts, from scripts to CI systems to spreadsheets.
```

(Drops Checkstyle XML and CSV. Only do this if you confirm those formats are
not actually shipped.)

---

## Checklist

| # | File | Line | Status |
|---|---|---|---|
| 1 | `sum.tex` | 22 | ☐ Replace Project-Level Analysis paragraph |
| 2 | `user.tex` | end of 204–214 subsection | ☐ Add Override-as-custom paragraph |
| 3 | `user.tex` | 280 | ☐ Replace JUnit row text |
| 4 | `impl.tex` | 235 | ☐ Replace mid-paragraph Jenkins sentence |
| 5 (optional) | `intro.tex` | 32 | ☐ Drop Checkstyle/CSV if not implemented |

That's the complete list. Edits 1 and 2 are the most important — they
describe behaviour that no longer matches what the thesis says. Edits 3 and 4
correct unverified integration claims. Edit 5 is conditional on a quick check
of what the code actually exports.
