"""Ready-to-use CI config snippets (GitHub Actions, GitLab CI, pre-commit)."""

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
        # Use the [cli] extra so the `crossguard` command-line works.
        # Once Cross Guard is published to PyPI you can simply use
        # `pip install crossguard[cli]`.
        run: pip install "crossguard[cli]"

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

_GITLAB_CI = """\
# Add to .gitlab-ci.yml
crossguard:
  stage: test
  image: python:3.11
  before_script:
    # The [cli] extra installs click, which the command-line entry point needs.
    - pip install "crossguard[cli]"
  script:
    - crossguard analyze src/ --format junit -o results.xml --fail-on-score 80
  artifacts:
    reports:
      junit: results.xml
    when: always
"""

_PRE_COMMIT = """\
# Add to .pre-commit-config.yaml
# Requires Cross Guard to be installed in your environment:
#     pip install "crossguard[cli]"
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
    'gitlab': _GITLAB_CI,
    'pre-commit': _PRE_COMMIT,
}


def generate_ci_config(provider: str) -> str:
    if provider not in ('github', 'gitlab'):
        raise ValueError(f"Unsupported CI provider: {provider}. "
                         f"Supported: github, gitlab")
    return TEMPLATES[provider]


def generate_hooks_config(hook_type: str) -> str:
    if hook_type != 'pre-commit':
        raise ValueError(f"Unsupported hook type: {hook_type}. "
                         f"Supported: pre-commit")
    return TEMPLATES['pre-commit']
