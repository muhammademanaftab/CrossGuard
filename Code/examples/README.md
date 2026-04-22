# Examples

Demo inputs and sample outputs for CrossGuard. None of these files are referenced by the test suite — they exist for manual exploration, screenshots, and demos.

## Structure

### `sample_project/`
A tiny, clean HTML/CSS/JS site used as the canonical "happy path" demo. Point the GUI or CLI at this folder to see a typical run.

```
sample_project/sample.html   # minimal page wiring CSS + JS
sample_project/sample.css    # modern features (grid, flexbox, variables)
sample_project/sample.js     # modern JS (arrow fns, optional chaining, etc.)
```

### `test_fixtures/`
Edge-case inputs for stressing the analyzer. Use these when validating parser changes or debugging false positives/negatives.

```
test_fixtures/test_all_features.html    # dense kitchen-sink document
test_fixtures/test_custom_rule.css      # exercises the custom-rules loader
```

### `sample_output/`
Real output produced by running CrossGuard against `sample_project/`. Useful reference for what the PDF exporter emits.

```
sample_output/compatibility_report_sample.pdf
```

## Regenerating the sample report

```bash
python -m src.cli.main analyze examples/sample_project \
    --export pdf \
    --output examples/sample_output/compatibility_report_sample.pdf
```
