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
        found = find_ignore_file(tmp_path)
        assert found == ignore

    def test_finds_in_parent_dir(self, tmp_path):
        ignore = tmp_path / IGNORE_FILENAME
        ignore.write_text("dist/\n")
        child = tmp_path / 'src'
        child.mkdir()
        found = find_ignore_file(child)
        assert found == ignore

    def test_returns_none_when_not_found(self, tmp_path):
        found = find_ignore_file(tmp_path)
        assert found is None

    def test_prefers_closest_file(self, tmp_path):
        (tmp_path / IGNORE_FILENAME).write_text("root\n")
        child = tmp_path / 'sub'
        child.mkdir()
        child_ignore = child / IGNORE_FILENAME
        child_ignore.write_text("child\n")
        found = find_ignore_file(child)
        assert found == child_ignore


class TestLoadIgnorePatterns:
    def test_basic_patterns(self, tmp_path):
        f = tmp_path / IGNORE_FILENAME
        f.write_text("*.min.js\ndist/\n")
        patterns = load_ignore_patterns(f)
        assert patterns == ['*.min.js', 'dist/']

    def test_comments_skipped(self, tmp_path):
        f = tmp_path / IGNORE_FILENAME
        f.write_text("# This is a comment\n*.min.js\n# Another\n")
        patterns = load_ignore_patterns(f)
        assert patterns == ['*.min.js']

    def test_blank_lines_skipped(self, tmp_path):
        f = tmp_path / IGNORE_FILENAME
        f.write_text("*.min.js\n\n\ndist/\n")
        patterns = load_ignore_patterns(f)
        assert patterns == ['*.min.js', 'dist/']

    def test_negation_preserved(self, tmp_path):
        f = tmp_path / IGNORE_FILENAME
        f.write_text("*.js\n!important.js\n")
        patterns = load_ignore_patterns(f)
        assert patterns == ['*.js', '!important.js']

    def test_whitespace_stripped(self, tmp_path):
        f = tmp_path / IGNORE_FILENAME
        f.write_text("  *.min.js  \n  dist/  \n")
        patterns = load_ignore_patterns(f)
        assert patterns == ['*.min.js', 'dist/']

    def test_missing_file_returns_empty(self, tmp_path):
        f = tmp_path / 'nonexistent'
        patterns = load_ignore_patterns(f)
        assert patterns == []


class TestShouldIgnore:
    def test_glob_match(self):
        assert should_ignore('app.min.js', ['*.min.js']) is True

    def test_glob_no_match(self):
        assert should_ignore('app.js', ['*.min.js']) is False

    def test_directory_pattern(self):
        assert should_ignore('dist/bundle.js', ['dist/']) is True

    def test_directory_pattern_nested(self):
        assert should_ignore('src/dist/bundle.js', ['dist/']) is True

    def test_negation(self):
        patterns = ['*.js', '!important.js']
        assert should_ignore('app.js', patterns) is True
        assert should_ignore('important.js', patterns) is False

    def test_path_matching(self):
        assert should_ignore('vendor/lib.js', ['vendor/*']) is True

    def test_basename_matching(self):
        assert should_ignore('src/deep/test.min.js', ['*.min.js']) is True

    def test_empty_patterns(self):
        assert should_ignore('anything.js', []) is False

    def test_windows_path_normalized(self):
        assert should_ignore('dist\\bundle.js', ['dist/']) is True
