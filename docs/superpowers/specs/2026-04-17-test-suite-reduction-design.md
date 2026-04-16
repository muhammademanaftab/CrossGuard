# Test Suite Reduction Design

**Date:** 2026-04-17
**Status:** Approved (pending spec review)
**Scope:** Reduce automated test suite from 281 tests to ~112 tests while preserving thesis-relevant coverage and the existing black-box / white-box / integration three-tier structure.

## Motivation

The current test suite has 281 tests across 12 modules. While runtime is fast (~1.8s), the count and the uniform BB/WB/Int symmetry across every module makes the suite look mechanically generated rather than human-authored. For a thesis artifact, the suite should read as the work of a diligent student who tested the hard parts of the system — not as a machine-produced coverage matrix.

The target is ~100–130 tests. This reduction focuses the suite on distinct behaviors, edge cases, and end-to-end pipelines while removing parametrize-bloat and trivial-variant tests.

## Goals

1. End state: **~112 tests** (within the 100–130 band).
2. Preserve the BB/WB/Integration three-tier structure in every module that already has it.
3. Every module that currently has integration tests retains at least one.
4. All retained tests continue to pass. No production code changes.
5. `@pytest.mark.blackbox`, `@pytest.mark.whitebox`, `@pytest.mark.integration` markers remain the single source of truth for counts.

## Non-Goals

- Not rewriting test infrastructure (`conftest.py`, fixtures, markers) unless a cut leaves it orphaned.
- Not renaming or restructuring test files.
- Not changing production code in `src/`.
- Not adding new tests. This is a pure reduction.
- Not reconciling the existing file-name vs marker mismatch in `tests/database/` beyond what naturally falls out of the cut.

## Selection Principles

Tests are kept or cut according to the following rules, in order of priority:

1. **One test per distinct behavior.** Where a parametrized block has N cases exercising the same code path with trivial variants, keep two representative cases (a typical happy path and a meaningful edge) and delete the rest.
2. **Keep the hard stuff.** Retain tests exercising boundary bugs, AST edge cases, and non-obvious parser logic — e.g. flexbox-gap block-boundary detection, template literal `${}` handling, tree-sitter AST cleaning around comments and strings, version-range overlap, optional chaining detection, custom-rule merge semantics.
3. **Keep integration tests demonstrating pipeline correctness.** Each module with integration tests retains at least one end-to-end test that exercises file I/O and real data.
4. **Cut trivial coverage.** Tautological getter tests, repeated happy-path CRUD, table-driven mappings (e.g. "does `<input type=X>` map to feature Y" repeated eight times), and redundant WB tests that duplicate a BB test's assertion.
5. **Cut narrative-irrelevant tests.** If the thesis chapter doesn't reference the behavior and it isn't a hard case under rule 2, it is a candidate for removal.

## Per-Module Target

| Module | BB now | WB now | Int now | Total now | BB keep | WB keep | Int keep | Total keep | Cut |
|---|---|---|---|---|---|---|---|---|---|
| CSS parser | 14 | 16 | 9 | 39 | 6 | 5 | 3 | 14 | −25 |
| HTML parser | 26 | 10 | 9 | 45 | 7 | 4 | 3 | 14 | −31 |
| JS parser | 17 | 15 | 8 | 40 | 6 | 5 | 3 | 14 | −26 |
| Custom rules | 4 | 5 | – | 9 | 3 | 2 | – | 5 | −4 |
| Analyzer | 15 | 10 | 5 | 30 | 6 | 4 | 2 | 12 | −18 |
| API service | 14 | 6 | 6 | 26 | 5 | 3 | 2 | 10 | −16 |
| Database | 3 | 6 | 9 | 18 | 3 | 2 | 2 | 7 | −11 |
| CLI | 9 | 10 | 6 | 25 | 4 | 4 | 2 | 10 | −15 |
| Polyfill | 5 | 5 | 6 | 16 | 3 | 2 | 2 | 7 | −9 |
| Export | 11 | – | – | 11 | 7 | – | – | 7 | −4 |
| Config | 8 | – | – | 8 | 5 | – | – | 5 | −3 |
| AI | 8 | 6 | – | 14 | 4 | 3 | – | 7 | −7 |
| **Total** | **134** | **89** | **58** | **281** | **59** | **34** | **19** | **112** | **−169** |

Parsers absorb the heaviest cut (39/45/40 → 14/14/14) because they carry the most parametrize-bloat. Analyzer, API, and CLI are trimmed more conservatively because they carry the thesis narrative around the scoring pipeline, service facade, and CI integration.

## What Survives (Module-by-Module)

### CSS parser (14)
- **BB:** grid detection, flex detection, container queries, custom properties, at-rules (keyframes, media), real stylesheet integration.
- **WB:** tinycss2 AST traversal, block boundary preservation (flexbox-gap same-block vs different-block), custom-rule merging, comment handling, selector-level detection.
- **Int:** full-file parse, multi-rule stylesheet, real-world sample.

### HTML parser (14)
- **BB:** semantic elements (`<dialog>`, `<details>`, etc.), input types (one representative, not eight), attribute detection, custom attribute values, custom-rule merge, validate hook, full-page scan.
- **WB:** DOM traversal state, attribute-value lookup, custom-rule dict merge, parser init.
- **Int:** file I/O, real-world page, report generation.

### JS parser (14)
- **BB:** optional chaining `?.`, nullish coalescing `??`, private fields `#x`, promise method → parent feature (`.then` → promises), directive detection (`"use strict"`), template literal `${}` handling.
- **WB:** tree-sitter AST cleaning (comments, strings), AST node-type detection, regex-on-AST-cleaned-text, custom-rule merge, false-positive filter (React component names).
- **Int:** end-to-end file parse, mixed feature source, real-world script.

### Custom rules (5)
- **BB:** load rules from JSON, rules appear in parser output, CSS/JS/HTML sections parse correctly.
- **WB:** singleton loader, save/reload round trip.

### Analyzer (12)
- **BB:** compatibility score math, support classification (full/partial/none), unknown-feature handling, weighted score across browsers, grade letter boundaries, per-browser breakdown.
- **WB:** Can I Use DB loader, web-features overlay, version parsing internals, scorer thresholds.
- **Int:** full pipeline (parse → analyze → score), multi-file run.

### API service (10)
- **BB:** analyze single file, analyze directory, export request, CRUD for analyses, bookmarks, tags.
- **WB:** singleton service, lazy analyzer load, baseline feature handling.
- **Int:** end-to-end analyze + persist + retrieve, export via API.

### Database (7)
- **BB:** analysis insert/fetch, bookmark round trip, tag CRUD.
- **WB:** schema migration v1 → v2, singleton connection.
- **Int:** full analysis lifecycle, statistics aggregation.

### CLI (10)
- **BB:** `analyze` command exit codes, `--format` flag handling, quality gate flags, browser string validation.
- **WB:** formatters (color vs no-color, table layout), CliContext, gate evaluation, CI config generators.
- **Int:** CliRunner end-to-end for `analyze`, CliRunner for export.

### Polyfill (7)
- **BB:** single-feature recommendation, multi-feature aggregation, install-command generation.
- **WB:** singleton loader, reload preserves data.
- **Int:** full pipeline (IE11 + fetch), file generation with valid JS output.

### Export (7)
- **BB:** one test per format — JSON, PDF, SARIF 2.1.0, JUnit XML, Checkstyle XML, CSV — plus a round-trip integrity test that parses a JSON export back and checks field preservation.

### Config (5)
- **BB:** load `crossguard.config.json`, `package.json` "crossguard" key fallback, CLI-flag precedence, defaults when no config, invalid config error path.

### AI (7)
- **BB:** build prompt for a feature, parse OpenAI-style response, parse Anthropic-style response, construct fix suggestion dataclass.
- **WB:** API call mocking (OpenAI), API call mocking (Anthropic), prompt template internals.

## Execution Approach

The reduction will be carried out module by module. For each module:

1. List every current test with its marker.
2. Group tests by the behavior they exercise.
3. Within each behavior group, keep the one test that best demonstrates the behavior (edge case preferred over happy path where both exist).
4. Delete the rest.
5. Run `pytest tests/<module>/ -q` and confirm remaining tests pass.
6. Run the full suite to confirm no cross-module fixtures broke.

A parser module is done first (CSS) as a pilot to validate the approach before committing to the full plan.

## Verification

After all cuts:

```
pytest tests/ -q                        # expect ~112 passed
pytest tests/ -m blackbox --collect-only -q   # expect ~59
pytest tests/ -m whitebox --collect-only -q   # expect ~34
pytest tests/ -m integration --collect-only -q  # expect ~19
```

Per-module counts must land within ±2 of the target table above. The final numbers feed into the §3.19 thesis table rewrite (which is tracked as a separate edit, not part of this spec).

## Risks and Mitigations

- **Risk:** A deleted test was the only one catching a real bug. **Mitigation:** every cut module runs its full remaining test subset before moving on; if a production bug slips, the integration tests retained per module are the safety net.
- **Risk:** Cut leaves an orphaned fixture in `conftest.py`. **Mitigation:** final pass greps for unused fixtures after all module cuts are done.
- **Risk:** Re-running the suite later finds a count slightly off target. **Mitigation:** the ±2 tolerance in verification accepts that; the narrative target is "~112", not "exactly 112".

## Out of Scope

- Rewriting §3.19 of the thesis. Happens after this spec is executed, using real post-cut numbers.
- Adding new tests or refactoring production code.
- Reconciling the `tests/database/` file-name vs marker mismatch beyond what the cut naturally resolves.
