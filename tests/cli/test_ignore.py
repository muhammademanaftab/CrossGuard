"""Tests for .crossguardignore support."""

import pytest
from pathlib import Path

from src.cli.ignore import (
    find_ignore_file,
    load_ignore_patterns,
    should_ignore,
    IGNORE_FILENAME,
)


class TestFindIgnoreFile:
    def test_finds_in_current_dir(self, tmp_path):
        ignore = tmp_path / IGNORE_FILENAME
        ignore.write_text("*.min.js\n")
        assert find_ignore_file(tmp_path) == ignore

    def test_finds_in_parent_dir(self, tmp_path):
        ignore = tmp_path / IGNORE_FILENAME
        ignore.write_text("dist/\n")
        child = tmp_path / 'src'
        child.mkdir()
        assert find_ignore_file(child) == ignore

    def test_returns_none_when_not_found(self, tmp_path):
        assert find_ignore_file(tmp_path) is None

    def test_prefers_closest_file(self, tmp_path):
        (tmp_path / IGNORE_FILENAME).write_text("root\n")
        child = tmp_path / 'sub'
        child.mkdir()
        child_ignore = child / IGNORE_FILENAME
        child_ignore.write_text("child\n")
        assert find_ignore_file(child) == child_ignore


class TestLoadIgnorePatterns:
    @pytest.mark.parametrize("content, expected", [
        ("*.min.js\ndist/\n", ['*.min.js', 'dist/']),
        ("# comment\n*.min.js\n# another\n", ['*.min.js']),
        ("*.min.js\n\n\ndist/\n", ['*.min.js', 'dist/']),
        ("*.js\n!important.js\n", ['*.js', '!important.js']),
        ("  *.min.js  \n  dist/  \n", ['*.min.js', 'dist/']),
    ])
    def test_pattern_parsing(self, tmp_path, content, expected):
        f = tmp_path / IGNORE_FILENAME
        f.write_text(content)
        assert load_ignore_patterns(f) == expected

    def test_missing_file_returns_empty(self, tmp_path):
        assert load_ignore_patterns(tmp_path / 'nonexistent') == []


class TestShouldIgnore:
    @pytest.mark.parametrize("path, patterns, expected", [
        ('app.min.js', ['*.min.js'], True),
        ('app.js', ['*.min.js'], False),
        ('dist/bundle.js', ['dist/'], True),
        ('src/dist/bundle.js', ['dist/'], True),
        ('vendor/lib.js', ['vendor/*'], True),
        ('src/deep/test.min.js', ['*.min.js'], True),
        ('anything.js', [], False),
        ('dist\\bundle.js', ['dist/'], True),  # windows path
    ])
    def test_pattern_matching(self, path, patterns, expected):
        assert should_ignore(path, patterns) is expected

    def test_negation(self):
        patterns = ['*.js', '!important.js']
        assert should_ignore('app.js', patterns) is True
        assert should_ignore('important.js', patterns) is False
