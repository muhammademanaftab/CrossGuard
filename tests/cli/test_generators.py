"""Tests for CI configuration generators."""

import pytest

from src.cli.generators import generate_ci_config, generate_hooks_config, TEMPLATES


class TestGenerateCiConfig:
    def test_github_output(self):
        output = generate_ci_config('github')
        assert 'github/codeql-action' in output
        assert 'crossguard analyze' in output
        assert 'sarif' in output

    def test_gitlab_output(self):
        output = generate_ci_config('gitlab')
        assert 'junit' in output
        assert 'crossguard analyze' in output
        assert 'artifacts' in output

    def test_unsupported_provider_raises(self):
        with pytest.raises(ValueError, match="Unsupported CI provider"):
            generate_ci_config('jenkins')


class TestGenerateHooksConfig:
    def test_pre_commit_output(self):
        output = generate_hooks_config('pre-commit')
        assert 'pre-commit' in output
        assert 'crossguard' in output.lower()

    def test_unsupported_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported hook type"):
            generate_hooks_config('husky')


class TestTemplates:
    def test_all_templates_are_non_empty_strings(self):
        for key, tmpl in TEMPLATES.items():
            assert isinstance(tmpl, str)
            assert len(tmpl) > 10, f"Template '{key}' seems too short"
