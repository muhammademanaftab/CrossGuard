"""Fallback tests: verify regex-only path works when tree-sitter is unavailable."""

import pytest
from unittest.mock import patch
from src.parsers.js_parser import JavaScriptParser


class TestRegexFallback:
    """Verify the parser works without tree-sitter."""

    def test_fallback_detects_arrow_functions(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string("const fn = () => 1;")
            assert 'arrow-functions' in features

    def test_fallback_detects_fetch(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string("fetch('/api');")
            assert 'fetch' in features

    def test_fallback_detects_promises(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string("new Promise((resolve) => resolve());")
            assert 'promises' in features

    def test_fallback_detects_const(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string("const x = 1;")
            assert 'const' in features

    def test_fallback_detects_template_literals(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string("const s = `hello ${name}`;")
            assert 'template-literals' in features

    def test_fallback_detects_async(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string("async function f() { await x; }")
            assert 'async-functions' in features

    def test_fallback_detects_class(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string("class Foo {}")
            assert 'es6-class' in features

    def test_fallback_directives_work(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string('"use strict"; var x = 1;')
            assert 'use-strict' in features

    def test_fallback_event_listeners_work(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            features = parser.parse_string(
                "window.addEventListener('hashchange', handler);"
            )
            assert 'hashchange' in features

    def test_fallback_detailed_report(self):
        with patch('src.parsers.js_parser._TREE_SITTER_AVAILABLE', False):
            parser = JavaScriptParser()
            parser.parse_string("fetch('/api'); const x = 1;")
            report = parser.get_detailed_report()
            assert report['total_features'] > 0
            assert 'fetch' in report['features']

    def test_tree_sitter_parse_failure_falls_back(self):
        """Verify fallback when tree-sitter parse returns None."""
        parser = JavaScriptParser()
        with patch.object(parser, '_parse_with_tree_sitter', return_value=None):
            features = parser.parse_string("const x = () => 1; fetch('/api');")
            assert 'arrow-functions' in features
            assert 'fetch' in features
