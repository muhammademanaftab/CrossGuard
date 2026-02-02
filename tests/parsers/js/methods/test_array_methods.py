"""Tests for Array method features.

Tests features: array-flat, array-includes, array-find, array-find-index, es5
"""

import pytest


class TestArrayFlat:
    """Tests for Array.flat/flatMap detection."""

    def test_array_flat(self, parse_and_check):
        """Test Array.flat()."""
        js = "const flat = nested.flat();"
        assert parse_and_check(js, 'array-flat')

    def test_array_flat_depth(self, parse_and_check):
        """Test Array.flat() with depth."""
        js = "const deepFlat = arr.flat(2);"
        assert parse_and_check(js, 'array-flat')

    def test_array_flatmap(self, parse_and_check):
        """Test Array.flatMap()."""
        js = "const result = arr.flatMap(x => [x, x * 2]);"
        assert parse_and_check(js, 'array-flat')


class TestArrayIncludes:
    """Tests for Array.includes detection."""

    def test_array_includes(self, parse_and_check):
        """Test Array.includes()."""
        js = "const hasItem = [1, 2, 3].includes(2);"
        assert parse_and_check(js, 'array-includes')

    def test_array_includes_from_index(self, parse_and_check):
        """Test Array.includes() with fromIndex."""
        js = "const has = arr.includes(1, 1);"
        assert parse_and_check(js, 'array-includes')


class TestArrayFind:
    """Tests for Array.find/findIndex/findLast detection."""

    def test_array_find(self, parse_and_check):
        """Test Array.find()."""
        js = "const found = arr.find(x => x > 1);"
        assert parse_and_check(js, 'array-find')

    def test_array_find_index(self, parse_and_check):
        """Test Array.findIndex()."""
        js = "const idx = arr.findIndex(x => x > 1);"
        assert parse_and_check(js, 'array-find')

    def test_array_find_last(self, parse_and_check):
        """Test Array.findLast()."""
        js = "const last = arr.findLast(x => x === 2);"
        assert parse_and_check(js, 'array-find')

    def test_array_find_last_index(self, parse_and_check):
        """Test Array.findLastIndex()."""
        js = "const lastIdx = arr.findLastIndex(x => x === 2);"
        assert parse_and_check(js, 'array-find')


class TestArrayFindIndex:
    """Tests for Array.findIndex (separate feature) detection."""

    def test_find_index(self, parse_and_check):
        """Test findIndex specifically."""
        js = "const idx = ['a', 'b'].findIndex(x => x === 'b');"
        assert parse_and_check(js, 'array-find-index')


class TestES5ArrayMethods:
    """Tests for ES5 Array methods detection."""

    def test_foreach(self, parse_and_check):
        """Test forEach()."""
        js = "[1, 2, 3].forEach(x => console.log(x));"
        assert parse_and_check(js, 'es5')

    def test_map(self, parse_and_check):
        """Test map()."""
        js = "const doubled = arr.map(x => x * 2);"
        assert parse_and_check(js, 'es5')

    def test_filter(self, parse_and_check):
        """Test filter()."""
        js = "const evens = arr.filter(x => x % 2 === 0);"
        assert parse_and_check(js, 'es5')

    def test_reduce(self, parse_and_check):
        """Test reduce()."""
        js = "const sum = arr.reduce((a, b) => a + b, 0);"
        assert parse_and_check(js, 'es5')

    def test_some(self, parse_and_check):
        """Test some()."""
        js = "const hasEven = arr.some(x => x % 2 === 0);"
        assert parse_and_check(js, 'es5')

    def test_every(self, parse_and_check):
        """Test every()."""
        js = "const allPositive = arr.every(x => x > 0);"
        assert parse_and_check(js, 'es5')
