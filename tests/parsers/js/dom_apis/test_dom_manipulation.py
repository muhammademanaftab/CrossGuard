"""Tests for DOM manipulation features.

Tests features: insertadjacenthtml, insert-adjacent, childnode-remove,
                dom-manip-convenience, dom-range, scrollintoview, element-scroll-methods
"""

import pytest


class TestInsertAdjacentHTML:
    """Tests for insertAdjacentHTML detection."""

    def test_insert_beforeend(self, parse_and_check):
        """Test insertAdjacentHTML beforeend."""
        js = "element.insertAdjacentHTML('beforeend', '<span>New</span>');"
        assert parse_and_check(js, 'insertadjacenthtml')

    def test_insert_afterbegin(self, parse_and_check):
        """Test insertAdjacentHTML afterbegin."""
        js = "element.insertAdjacentHTML('afterbegin', '<div>First</div>');"
        assert parse_and_check(js, 'insertadjacenthtml')

    def test_insert_beforebegin(self, parse_and_check):
        """Test insertAdjacentHTML beforebegin."""
        js = "element.insertAdjacentHTML('beforebegin', '<hr/>');"
        assert parse_and_check(js, 'insertadjacenthtml')


class TestInsertAdjacent:
    """Tests for insertAdjacentElement/Text detection."""

    def test_insert_adjacent_element(self, parse_and_check):
        """Test insertAdjacentElement."""
        js = "element.insertAdjacentElement('beforebegin', newElement);"
        assert parse_and_check(js, 'insert-adjacent')

    def test_insert_adjacent_text(self, parse_and_check):
        """Test insertAdjacentText."""
        js = "element.insertAdjacentText('afterend', 'Text node');"
        assert parse_and_check(js, 'insert-adjacent')


class TestChildNodeRemove:
    """Tests for ChildNode.remove() detection."""

    def test_element_remove(self, parse_and_check):
        """Test element.remove()."""
        js = "element.remove();"
        assert parse_and_check(js, 'childnode-remove')


class TestDOMManipConvenience:
    """Tests for DOM manipulation convenience methods."""

    def test_append(self, parse_and_check):
        """Test append method."""
        js = "parent.append(child1, child2);"
        assert parse_and_check(js, 'dom-manip-convenience')

    def test_prepend(self, parse_and_check):
        """Test prepend method."""
        js = "parent.prepend(firstChild);"
        assert parse_and_check(js, 'dom-manip-convenience')

    def test_before(self, parse_and_check):
        """Test before method."""
        js = "element.before(sibling);"
        assert parse_and_check(js, 'dom-manip-convenience')

    def test_after(self, parse_and_check):
        """Test after method."""
        js = "element.after(nextSibling);"
        assert parse_and_check(js, 'dom-manip-convenience')


class TestDOMRange:
    """Tests for DOM Range API detection."""

    def test_create_range(self, parse_and_check):
        """Test document.createRange()."""
        js = "const range = document.createRange();"
        assert parse_and_check(js, 'dom-range')

    def test_new_range(self, parse_and_check):
        """Test new Range()."""
        js = "const range = new Range();"
        assert parse_and_check(js, 'dom-range')


class TestScrollIntoView:
    """Tests for scrollIntoView detection."""

    def test_scroll_into_view(self, parse_and_check):
        """Test scrollIntoView()."""
        js = "element.scrollIntoView();"
        assert parse_and_check(js, 'scrollintoview')

    def test_scroll_into_view_options(self, parse_and_check):
        """Test scrollIntoView with options."""
        js = "element.scrollIntoView({ behavior: 'smooth', block: 'center' });"
        assert parse_and_check(js, 'scrollintoview')


class TestScrollIntoViewIfNeeded:
    """Tests for scrollIntoViewIfNeeded detection."""

    def test_scroll_if_needed(self, parse_and_check):
        """Test scrollIntoViewIfNeeded()."""
        js = "element.scrollIntoViewIfNeeded();"
        assert parse_and_check(js, 'scrollintoviewifneeded')

    def test_scroll_if_needed_center(self, parse_and_check):
        """Test scrollIntoViewIfNeeded with center."""
        js = "element.scrollIntoViewIfNeeded(true);"
        assert parse_and_check(js, 'scrollintoviewifneeded')


class TestElementScrollMethods:
    """Tests for element scroll methods detection."""

    def test_scroll_method(self, parse_and_check):
        """Test scroll method."""
        js = "element.scroll({ top: 100, behavior: 'smooth' });"
        assert parse_and_check(js, 'element-scroll-methods')

    def test_scroll_to(self, parse_and_check):
        """Test scrollTo method."""
        js = "element.scrollTo(0, 500);"
        assert parse_and_check(js, 'element-scroll-methods')

    def test_scroll_by(self, parse_and_check):
        """Test scrollBy method."""
        js = "element.scrollBy({ top: 50, left: 0 });"
        assert parse_and_check(js, 'element-scroll-methods')
