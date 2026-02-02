"""Tests for Observer API features.

Tests features: intersectionobserver, mutationobserver, resizeobserver,
                intersectionobserver-v2
"""

import pytest


class TestIntersectionObserver:
    """Tests for Intersection Observer detection."""

    def test_new_intersection_observer(self, parse_and_check):
        """Test new IntersectionObserver."""
        js = "const observer = new IntersectionObserver(callback);"
        assert parse_and_check(js, 'intersectionobserver')

    def test_intersection_observer_with_options(self, parse_and_check):
        """Test IntersectionObserver with options."""
        js = """
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => console.log(entry.isIntersecting));
        }, { threshold: 0.5 });
        """
        assert parse_and_check(js, 'intersectionobserver')

    def test_intersection_observer_observe(self, parse_and_check):
        """Test IntersectionObserver usage."""
        js = """
        const io = new IntersectionObserver(cb);
        io.observe(element);
        """
        assert parse_and_check(js, 'intersectionobserver')


class TestIntersectionObserverV2:
    """Tests for Intersection Observer V2 detection."""

    def test_is_visible(self, parse_and_check):
        """Test isVisible property."""
        js = "if (entry.isVisible) { console.log('visible'); }"
        assert parse_and_check(js, 'intersectionobserver-v2')


class TestMutationObserver:
    """Tests for Mutation Observer detection."""

    def test_new_mutation_observer(self, parse_and_check):
        """Test new MutationObserver."""
        js = "const observer = new MutationObserver(callback);"
        assert parse_and_check(js, 'mutationobserver')

    def test_mutation_observer_observe(self, parse_and_check):
        """Test MutationObserver with observe."""
        js = """
        const mo = new MutationObserver(mutations => {
            mutations.forEach(m => console.log(m.type));
        });
        mo.observe(document.body, { childList: true });
        """
        assert parse_and_check(js, 'mutationobserver')


class TestResizeObserver:
    """Tests for Resize Observer detection."""

    def test_new_resize_observer(self, parse_and_check):
        """Test new ResizeObserver."""
        js = "const observer = new ResizeObserver(callback);"
        assert parse_and_check(js, 'resizeobserver')

    def test_resize_observer_with_entries(self, parse_and_check):
        """Test ResizeObserver with entries."""
        js = """
        const ro = new ResizeObserver(entries => {
            entries.forEach(entry => console.log(entry.contentRect));
        });
        ro.observe(element);
        """
        assert parse_and_check(js, 'resizeobserver')
