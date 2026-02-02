"""Tests for Object and String method features.

Tests features: object-entries, object-values, es6-string-includes,
                pad-start-end, bigint, proxy, es6
"""

import pytest


class TestObjectEntries:
    """Tests for Object.entries detection."""

    def test_object_entries(self, parse_and_check):
        """Test Object.entries()."""
        js = "const entries = Object.entries({ a: 1, b: 2 });"
        assert parse_and_check(js, 'object-entries')

    def test_object_entries_iteration(self, parse_and_check):
        """Test Object.entries() in for-of."""
        js = "for (const [key, value] of Object.entries(obj)) {}"
        assert parse_and_check(js, 'object-entries')


class TestObjectValues:
    """Tests for Object.values detection."""

    def test_object_values(self, parse_and_check):
        """Test Object.values()."""
        js = "const values = Object.values({ a: 1, b: 2 });"
        assert parse_and_check(js, 'object-values')


class TestStringIncludes:
    """Tests for String.includes detection."""

    def test_string_includes(self, parse_and_check):
        """Test String.includes()."""
        js = "const has = 'hello world'.includes('world');"
        assert parse_and_check(js, 'es6-string-includes')


class TestPadStartEnd:
    """Tests for String.padStart/padEnd detection."""

    def test_pad_start(self, parse_and_check):
        """Test String.padStart()."""
        js = "const padded = '5'.padStart(3, '0');"
        assert parse_and_check(js, 'pad-start-end')

    def test_pad_end(self, parse_and_check):
        """Test String.padEnd()."""
        js = "const padded = 'hi'.padEnd(5, '!');"
        assert parse_and_check(js, 'pad-start-end')


class TestBigInt:
    """Tests for BigInt detection."""

    def test_bigint_constructor(self, parse_and_check):
        """Test BigInt() constructor."""
        js = "const big = BigInt(9007199254740991);"
        assert parse_and_check(js, 'bigint')

    def test_bigint_literal(self, parse_and_check):
        """Test BigInt literal."""
        js = "const big = 9007199254740991n;"
        assert parse_and_check(js, 'bigint')


class TestProxy:
    """Tests for Proxy detection."""

    def test_new_proxy(self, parse_and_check):
        """Test new Proxy."""
        js = "const proxy = new Proxy(target, handler);"
        assert parse_and_check(js, 'proxy')

    def test_proxy_with_traps(self, parse_and_check):
        """Test Proxy with traps."""
        js = """
        const proxy = new Proxy(target, {
            get(target, prop) { return target[prop]; },
            set(target, prop, value) { target[prop] = value; return true; }
        });
        """
        assert parse_and_check(js, 'proxy')


class TestES6BuiltIns:
    """Tests for ES6 built-in objects detection."""

    def test_new_map(self, parse_and_check):
        """Test new Map."""
        js = "const map = new Map();"
        assert parse_and_check(js, 'es6')

    def test_new_set(self, parse_and_check):
        """Test new Set."""
        js = "const set = new Set([1, 2, 3]);"
        assert parse_and_check(js, 'es6')

    def test_new_weakmap(self, parse_and_check):
        """Test new WeakMap."""
        js = "const wm = new WeakMap();"
        assert parse_and_check(js, 'es6')

    def test_new_weakset(self, parse_and_check):
        """Test new WeakSet."""
        js = "const ws = new WeakSet();"
        assert parse_and_check(js, 'es6')

    def test_symbol(self, parse_and_check):
        """Test Symbol()."""
        js = "const sym = Symbol('description');"
        assert parse_and_check(js, 'es6')

    def test_reflect(self, parse_and_check):
        """Test Reflect."""
        js = "Reflect.get(obj, 'prop');"
        assert parse_and_check(js, 'es6')


class TestURL:
    """Tests for URL API detection."""

    def test_new_url(self, parse_and_check):
        """Test new URL."""
        js = "const url = new URL('https://example.com');"
        assert parse_and_check(js, 'url')


class TestURLSearchParams:
    """Tests for URLSearchParams detection."""

    def test_new_url_search_params(self, parse_and_check):
        """Test new URLSearchParams."""
        js = "const params = new URLSearchParams('?a=1&b=2');"
        assert parse_and_check(js, 'urlsearchparams')

    def test_url_search_params_get(self, parse_and_check):
        """Test URLSearchParams methods."""
        js = """
        const params = new URLSearchParams(location.search);
        const value = params.get('key');
        """
        assert parse_and_check(js, 'urlsearchparams')
