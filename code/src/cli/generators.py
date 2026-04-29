"""Ready-to-use CI config snippets (GitHub Actions, pre-commit)."""

_GITHUB_ACTIONS = """\
# .github/workflows/crossguard.yml
name: Browser Compatibility Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Required so github/codeql-action/upload-sarif can write findings.
permissions:
  security-events: write
  contents: read

jobs:
  compatibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Cross Guard
        # Installs Cross Guard from the public source repository.
        # The [cli] extra brings in click, which the `crossguard` command needs.
        run: pip install "crossguard[cli] @ git+https://github.com/muhammademanaftab/CrossGuard.git#subdirectory=code"

      - name: Run compatibility analysis
        run: |
          crossguard analyze src/ \\
            --format sarif \\
            --output-sarif results.sarif \\
            --fail-on-score 80

      - name: Upload SARIF results to Code Scanning
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
          category: crossguard

      - name: Upload SARIF as build artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: crossguard-sarif
          path: results.sarif
"""

_PRE_COMMIT = """\
# Add to .pre-commit-config.yaml
# Requires Cross Guard to be installed in your environment:
#     pip install "crossguard[cli] @ git+https://github.com/muhammademanaftab/CrossGuard.git#subdirectory=code"
repos:
  - repo: local
    hooks:
      - id: crossguard
        name: Cross Guard compatibility check
        entry: crossguard analyze --fail-on-score 80
        language: system
        types_or: [html, css, javascript]
        pass_filenames: true
"""

TEMPLATES = {
    'github': _GITHUB_ACTIONS,
    'pre-commit': _PRE_COMMIT,
}


def generate_ci_config(provider: str) -> str:
    if provider != 'github':
        raise ValueError(f"Unsupported CI provider: {provider}. "
                         f"Supported: github")
    return TEMPLATES[provider]


def generate_hooks_config(hook_type: str) -> str:
    if hook_type != 'pre-commit':
        raise ValueError(f"Unsupported hook type: {hook_type}. "
                         f"Supported: pre-commit")
    return TEMPLATES['pre-commit']
