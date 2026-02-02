"""Tests for DOM query and selection features.

Tests features: queryselector, classlist, dataset, addeventlistener,
                getelementsbyclassname, textcontent, innertext
"""

import pytest


class TestQuerySelector:
    """Tests for querySelector/querySelectorAll detection."""

    def test_query_selector(self, parse_and_check):
        """Test querySelector."""
        js = "document.querySelector('.my-class');"
        assert parse_and_check(js, 'queryselector')

    def test_query_selector_all(self, parse_and_check):
        """Test querySelectorAll."""
        js = "document.querySelectorAll('div.container');"
        assert parse_and_check(js, 'queryselector')

    def test_nested_query(self, parse_and_check):
        """Test nested querySelector."""
        js = "element.querySelector('span');"
        assert parse_and_check(js, 'queryselector')

    def test_query_with_attribute(self, parse_and_check):
        """Test querySelector with attribute selector."""
        js = "document.querySelectorAll('[data-id]');"
        assert parse_and_check(js, 'queryselector')


class TestClassList:
    """Tests for classList API detection."""

    def test_classlist_add(self, parse_and_check):
        """Test classList.add()."""
        js = "element.classList.add('active');"
        assert parse_and_check(js, 'classlist')

    def test_classlist_remove(self, parse_and_check):
        """Test classList.remove()."""
        js = "element.classList.remove('hidden');"
        assert parse_and_check(js, 'classlist')

    def test_classlist_toggle(self, parse_and_check):
        """Test classList.toggle()."""
        js = "element.classList.toggle('open');"
        assert parse_and_check(js, 'classlist')

    def test_classlist_contains(self, parse_and_check):
        """Test classList.contains()."""
        js = "if (element.classList.contains('selected')) {}"
        assert parse_and_check(js, 'classlist')

    def test_classlist_access(self, parse_and_check):
        """Test classList property access."""
        js = "const classes = element.classList;"
        assert parse_and_check(js, 'classlist')


class TestDataset:
    """Tests for dataset API detection."""

    def test_dataset_set(self, parse_and_check):
        """Test setting dataset property."""
        js = "element.dataset.userId = '123';"
        assert parse_and_check(js, 'dataset')

    def test_dataset_get(self, parse_and_check):
        """Test getting dataset property."""
        js = "const id = element.dataset.userId;"
        assert parse_and_check(js, 'dataset')

    def test_dataset_delete(self, parse_and_check):
        """Test deleting dataset property."""
        js = "delete element.dataset.temp;"
        assert parse_and_check(js, 'dataset')


class TestAddEventListener:
    """Tests for addEventListener detection."""

    def test_add_event_listener(self, parse_and_check):
        """Test addEventListener."""
        js = "element.addEventListener('click', handler);"
        assert parse_and_check(js, 'addeventlistener')

    def test_add_event_listener_options(self, parse_and_check):
        """Test addEventListener with options."""
        js = "element.addEventListener('scroll', handler, { passive: true });"
        assert parse_and_check(js, 'addeventlistener')

    def test_remove_event_listener(self, parse_and_check):
        """Test removeEventListener."""
        js = "element.removeEventListener('click', handler);"
        assert parse_and_check(js, 'addeventlistener')

    def test_document_event_listener(self, parse_and_check):
        """Test document event listener."""
        js = "document.addEventListener('DOMContentLoaded', init);"
        assert parse_and_check(js, 'addeventlistener')


class TestGetElementsByClassName:
    """Tests for getElementsByClassName detection."""

    def test_get_by_class(self, parse_and_check):
        """Test getElementsByClassName."""
        js = "document.getElementsByClassName('item');"
        assert parse_and_check(js, 'getelementsbyclassname')


class TestTextContent:
    """Tests for textContent detection."""

    def test_textcontent_set(self, parse_and_check):
        """Test setting textContent."""
        js = "element.textContent = 'New text';"
        assert parse_and_check(js, 'textcontent')

    def test_textcontent_get(self, parse_and_check):
        """Test getting textContent."""
        js = "const text = element.textContent;"
        assert parse_and_check(js, 'textcontent')


class TestInnerText:
    """Tests for innerText detection."""

    def test_innertext_set(self, parse_and_check):
        """Test setting innerText."""
        js = "element.innerText = 'Visible text';"
        assert parse_and_check(js, 'innertext')

    def test_innertext_get(self, parse_and_check):
        """Test getting innerText."""
        js = "const visible = element.innerText;"
        assert parse_and_check(js, 'innertext')
