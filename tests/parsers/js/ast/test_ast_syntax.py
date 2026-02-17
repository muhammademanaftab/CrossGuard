"""Tier 1 tests: AST syntax node detection.

Tests that tree-sitter correctly identifies syntax features by node type.
These should have zero false positives.
"""

import pytest


class TestASTArrowFunctions:
    """Arrow function detection via AST."""

    def test_simple_arrow(self, parse_and_check):
        assert parse_and_check("const fn = () => 1;", 'arrow-functions')

    def test_arrow_with_body(self, parse_and_check):
        assert parse_and_check("const fn = (x) => { return x; };", 'arrow-functions')

    def test_arrow_in_callback(self, parse_and_check):
        assert parse_and_check("[1,2].map(x => x * 2);", 'arrow-functions')


class TestASTTemplateLiterals:
    """Template literal detection via AST."""

    def test_template_with_expression(self, parse_and_check):
        assert parse_and_check("const s = `hello ${name}`;", 'template-literals')

    def test_tagged_template(self, parse_and_check):
        assert parse_and_check("const s = html`<div>${x}</div>`;", 'template-literals')


class TestASTClasses:
    """Class declaration detection via AST."""

    def test_class_declaration(self, parse_and_check):
        assert parse_and_check("class Foo {}", 'es6-class')

    def test_class_with_extends(self, parse_and_check):
        assert parse_and_check("class Bar extends Foo {}", 'es6-class')

    def test_class_expression(self, parse_and_check):
        assert parse_and_check("const Foo = class {};", 'es6-class')


class TestASTGenerators:
    """Generator function detection via AST."""

    def test_generator_declaration(self, parse_and_check):
        assert parse_and_check("function* gen() { yield 1; }", 'es6-generators')

    def test_yield_expression(self, parse_and_check):
        assert parse_and_check("function* g() { yield 42; }", 'es6-generators')


class TestASTConstLet:
    """const/let detection via AST."""

    def test_const(self, parse_and_check):
        assert parse_and_check("const x = 1;", 'const')

    def test_let(self, parse_and_check):
        assert parse_and_check("let y = 2;", 'let')

    def test_const_destructuring(self, parse_and_check):
        js = "const { a, b } = obj;"
        features = parse_and_check(js, 'es6')
        assert features  # destructuring detected


class TestASTSpreadRest:
    """Spread and rest parameter detection via AST."""

    def test_spread_in_call(self, parse_and_check):
        assert parse_and_check("foo(...args);", 'es6')

    def test_spread_in_array(self, parse_and_check):
        assert parse_and_check("const arr = [...a, ...b];", 'es6')

    def test_rest_parameter(self, parse_and_check):
        assert parse_and_check("function foo(...args) {}", 'rest-parameters')


class TestASTAsync:
    """Async/await detection via AST."""

    def test_async_function(self, parse_and_check):
        assert parse_and_check("async function fetchData() {}", 'async-functions')

    def test_await_expression(self, parse_and_check):
        assert parse_and_check("async function f() { await fetch('/api'); }", 'async-functions')

    def test_async_arrow(self, parse_and_check):
        assert parse_and_check("const fn = async () => { await x; };", 'async-functions')


class TestASTModernSyntax:
    """Modern ES2020+ syntax features detected by AST."""

    def test_nullish_coalescing(self, parse_and_check):
        assert parse_and_check(
            "const x = a ?? b;",
            'mdn-javascript_operators_nullish_coalescing'
        )

    def test_optional_chaining(self, parse_and_check):
        assert parse_and_check(
            "const x = obj?.prop;",
            'mdn-javascript_operators_optional_chaining'
        )

    def test_optional_chaining_call(self, parse_and_check):
        assert parse_and_check(
            "obj?.method();",
            'mdn-javascript_operators_optional_chaining'
        )

    def test_private_class_field(self, parse_and_check):
        js = """
        class Foo {
            #value = 42;
            get() { return this.#value; }
        }
        """
        assert parse_and_check(js, 'mdn-javascript_classes_private_class_fields')
