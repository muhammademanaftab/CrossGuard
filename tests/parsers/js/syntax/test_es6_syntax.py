"""Tests for ES6+ syntax features.

Tests features: arrow-functions, async-functions, const, let, template-literals,
                es6, rest-parameters, es6-class, es6-generators, use-strict
"""

import pytest


class TestArrowFunctions:
    """Tests for arrow function detection."""

    def test_simple_arrow(self, parse_and_check):
        """Test simple arrow function."""
        js = "const fn = () => 1;"
        assert parse_and_check(js, 'arrow-functions')

    def test_arrow_with_params(self, parse_and_check):
        """Test arrow function with parameters."""
        js = "const add = (a, b) => a + b;"
        assert parse_and_check(js, 'arrow-functions')

    def test_arrow_single_param(self, parse_and_check):
        """Test arrow function with single parameter."""
        js = "const square = x => x * x;"
        assert parse_and_check(js, 'arrow-functions')

    def test_arrow_with_block(self, parse_and_check):
        """Test arrow function with block body."""
        js = """
        const fn = (x) => {
            return x * 2;
        };
        """
        assert parse_and_check(js, 'arrow-functions')

    def test_arrow_in_callback(self, parse_and_check):
        """Test arrow function in callback."""
        js = "arr.map(x => x * 2);"
        assert parse_and_check(js, 'arrow-functions')


class TestAsyncFunctions:
    """Tests for async function detection."""

    def test_async_function(self, parse_and_check):
        """Test async function declaration."""
        js = "async function fetchData() { return await fetch('/api'); }"
        assert parse_and_check(js, 'async-functions')

    def test_async_arrow(self, parse_and_check):
        """Test async arrow function."""
        js = "const fn = async () => { await Promise.resolve(); };"
        assert parse_and_check(js, 'async-functions')

    def test_async_method(self, parse_and_check):
        """Test async function declaration."""
        js = "async function getData() { return await fetch('/api'); }"
        assert parse_and_check(js, 'async-functions')


class TestConstDeclaration:
    """Tests for const declaration detection."""

    def test_const_primitive(self, parse_and_check):
        """Test const with primitive value."""
        js = "const PI = 3.14159;"
        assert parse_and_check(js, 'const')

    def test_const_object(self, parse_and_check):
        """Test const with object."""
        js = "const config = { debug: true };"
        assert parse_and_check(js, 'const')

    def test_const_array(self, parse_and_check):
        """Test const with array."""
        js = "const items = [1, 2, 3];"
        assert parse_and_check(js, 'const')

    def test_const_destructuring(self, parse_and_check):
        """Test const with destructuring."""
        js = "const { x, y } = point;"
        assert parse_and_check(js, 'const')


class TestLetDeclaration:
    """Tests for let declaration detection."""

    def test_let_simple(self, parse_and_check):
        """Test simple let declaration."""
        js = "let counter = 0;"
        assert parse_and_check(js, 'let')

    def test_let_in_loop(self, parse_and_check):
        """Test let in for loop."""
        js = "for (let i = 0; i < 10; i++) {}"
        assert parse_and_check(js, 'let')

    def test_let_multiple(self, parse_and_check):
        """Test multiple let declarations."""
        js = "let a, b, c;"
        assert parse_and_check(js, 'let')


class TestTemplateLiterals:
    """Tests for template literal detection."""

    def test_simple_template(self, parse_and_check):
        """Test simple template literal with interpolation."""
        js = "const msg = `Hello, ${name}!`;"
        assert parse_and_check(js, 'template-literals')

    def test_multiline_template(self, parse_and_check):
        """Test multiline template literal."""
        js = """
        const html = `
            <div>
                ${content}
            </div>
        `;
        """
        assert parse_and_check(js, 'template-literals')

    def test_nested_template(self, parse_and_check):
        """Test nested template literals."""
        js = "const msg = `Outer ${`inner ${value}`}`;"
        assert parse_and_check(js, 'template-literals')


class TestES6Destructuring:
    """Tests for ES6 destructuring and spread detection.

    Note: ES6 patterns detect:
    - const { or let { for object destructuring
    - const [ or let [ for array destructuring
    - ... for spread operator
    """

    def test_object_destructuring(self, parse_and_check):
        """Test object destructuring with const {."""
        js = "const {x, y} = point;"  # Pattern: const\s*\{
        assert parse_and_check(js, 'es6')

    def test_object_destructuring_let(self, parse_and_check):
        """Test object destructuring with let {."""
        js = "let {a, b} = obj;"  # Pattern: let\s*\{
        assert parse_and_check(js, 'es6')

    def test_array_destructuring(self, parse_and_check):
        """Test array destructuring with const [."""
        js = "const [first, second] = items;"  # Pattern: const\s*\[
        assert parse_and_check(js, 'es6')

    def test_spread_operator(self, parse_and_check):
        """Test spread operator ... ."""
        js = "const combined = [...arr1];"  # Pattern: \.\.\.
        assert parse_and_check(js, 'es6')

    def test_rest_pattern(self, parse_and_check):
        """Test rest pattern with spread operator."""
        js = "const { a, ...rest } = obj;"  # Pattern: \.\.\.
        assert parse_and_check(js, 'es6')


class TestRestParameters:
    """Tests for rest parameters detection.

    Note: Rest parameter patterns:
    - function name(...args) - function with rest param
    - => (...args) - arrow function with rest param (needs specific pattern)
    """

    def test_rest_in_function(self, parse_and_check):
        """Test rest parameters in function."""
        js = "function sum(...numbers) { return numbers.reduce((a, b) => a + b); }"
        assert parse_and_check(js, 'rest-parameters')

    def test_rest_in_named_function(self, parse_and_check):
        """Test rest parameters in named function."""
        js = "function process(first, ...rest) { return rest; }"
        assert parse_and_check(js, 'rest-parameters')


class TestES6Classes:
    """Tests for ES6 class detection.

    Note: Pattern is 'class ' followed by word character (\bclass\s+\w+).
    Anonymous class expressions (class { }) are NOT detected.
    """

    def test_simple_class(self, parse_and_check):
        """Test simple class declaration."""
        js = "class Animal { constructor(name) { this.name = name; } }"
        assert parse_and_check(js, 'es6-class')

    def test_class_extends(self, parse_and_check):
        """Test class with extends."""
        js = "class Dog extends Animal { bark() { console.log('woof'); } }"
        assert parse_and_check(js, 'es6-class')

    def test_named_class_expression(self, parse_and_check):
        """Test named class expression."""
        js = "const MyClass = class MyClassName { constructor() {} };"
        assert parse_and_check(js, 'es6-class')


class TestES6Generators:
    """Tests for ES6 generator detection."""

    def test_generator_function(self, parse_and_check):
        """Test generator function declaration."""
        js = "function* gen() { yield 1; yield 2; }"
        assert parse_and_check(js, 'es6-generators')

    def test_yield_keyword(self, parse_and_check):
        """Test yield keyword."""
        js = "function* infinite() { let i = 0; while (true) { yield i++; } }"
        assert parse_and_check(js, 'es6-generators')


class TestUseStrict:
    """Tests for 'use strict' directive detection."""

    def test_use_strict_double_quotes(self, parse_and_check):
        """Test 'use strict' with double quotes."""
        js = '"use strict"; var x = 1;'
        assert parse_and_check(js, 'use-strict')

    def test_use_strict_single_quotes(self, parse_and_check):
        """Test 'use strict' with single quotes."""
        js = "'use strict'; var x = 1;"
        assert parse_and_check(js, 'use-strict')

    def test_use_strict_in_function(self, parse_and_check):
        """Test 'use strict' in function."""
        js = 'function fn() { "use strict"; return 1; }'
        assert parse_and_check(js, 'use-strict')


class TestCombinedSyntax:
    """Tests for combined ES6+ syntax features."""

    def test_modern_js_file(self, parse_and_check_multiple):
        """Test modern JS with multiple features."""
        js = """
        const add = (a, b) => a + b;
        let counter = 0;
        class Calculator extends Base {
            constructor() { super(); }
        }
        async function compute() { return await Promise.resolve(42); }
        """
        assert parse_and_check_multiple(js, ['arrow-functions', 'const', 'let', 'es6-class', 'async-functions'])
