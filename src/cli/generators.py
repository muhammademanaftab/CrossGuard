"""CI configuration generators for Cross Guard.

Prints ready-to-use workflow/config snippets for popular CI systems.
"""

_GITHUB_ACTIONS = """\
# .github/workflows/crossguard.yml
name: Browser Compatibility Check

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

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
        run: pip install crossguard

      - name: Check browser compatibility
        run: crossguard analyze src/ --format sarif --output-sarif results.sarif --fail-on-score 80

      - name: Upload SARIF results
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
"""

_GITLAB_CI = """\
# Add to .gitlab-ci.yml
crossguard:
  stage: test
  image: python:3.11
  before_script:
    - pip install crossguard
  script:
    - crossguard analyze src/ --format junit -o results.xml --fail-on-score 80
  artifacts:
    reports:
      junit: results.xml
    when: always
"""

_PRE_COMMIT = """\
# Add to .pre-commit-config.yaml
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
    """Return a CI config snippet for the given provider.

    Args:
        provider: One of 'github', 'gitlab'.

    Returns:
        YAML string.

    Raises:
        ValueError: If *provider* is not supported.
    """
    if provider not in ('github', 'gitlab'):
        raise ValueError(f"Unsupported CI provider: {provider}. "
                         f"Supported: github, gitlab")
    return TEMPLATES[provider]


def generate_hooks_config(hook_type: str) -> str:
    """Return a hooks config snippet.

    Args:
        hook_type: Currently only 'pre-commit' is supported.

    Returns:
        YAML string.

    Raises:
        ValueError: If *hook_type* is not supported.
    """
    if hook_type != 'pre-commit':
        raise ValueError(f"Unsupported hook type: {hook_type}. "
                         f"Supported: pre-commit")
    return TEMPLATES['pre-commit']
