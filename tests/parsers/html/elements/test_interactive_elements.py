"""Tests for HTML5 interactive element detection.

Tests elements: dialog, details, summary, template
"""

import pytest


class TestDialogElement:
    """Tests for <dialog> element detection."""

    def test_dialog_basic(self, parse_and_check):
        """Test basic dialog element detection."""
        html = "<dialog>Dialog content</dialog>"
        assert parse_and_check(html, 'dialog')

    def test_dialog_open(self, parse_and_check):
        """Test dialog element with open attribute."""
        html = '<dialog open>Visible dialog</dialog>'
        assert parse_and_check(html, 'dialog')

    def test_dialog_with_form(self, parse_and_check):
        """Test dialog element with form inside."""
        html = """
        <dialog>
            <form method="dialog">
                <p>Are you sure?</p>
                <button value="cancel">Cancel</button>
                <button value="confirm">Confirm</button>
            </form>
        </dialog>
        """
        assert parse_and_check(html, 'dialog')

    def test_dialog_modal(self, parse_and_check):
        """Test dialog element styled as modal."""
        html = """
        <dialog id="modal">
            <h2>Modal Title</h2>
            <p>Modal content</p>
            <button>Close</button>
        </dialog>
        """
        assert parse_and_check(html, 'dialog')


class TestDetailsElement:
    """Tests for <details> element detection."""

    def test_details_basic(self, parse_and_check):
        """Test basic details element detection."""
        html = "<details>Content</details>"
        assert parse_and_check(html, 'details')

    def test_details_with_summary(self, parse_and_check):
        """Test details element with summary."""
        html = """
        <details>
            <summary>Click to expand</summary>
            <p>Hidden content revealed on click.</p>
        </details>
        """
        assert parse_and_check(html, 'details')

    def test_details_open(self, parse_and_check):
        """Test details element with open attribute."""
        html = """
        <details open>
            <summary>Already open</summary>
            <p>Visible content</p>
        </details>
        """
        assert parse_and_check(html, 'details')

    def test_details_nested(self, parse_and_check):
        """Test nested details elements."""
        html = """
        <details>
            <summary>Outer</summary>
            <details>
                <summary>Inner</summary>
                <p>Nested content</p>
            </details>
        </details>
        """
        assert parse_and_check(html, 'details')

    def test_details_as_accordion(self, parse_and_check):
        """Test multiple details elements as accordion."""
        html = """
        <details name="accordion">
            <summary>Section 1</summary>
            <p>Content 1</p>
        </details>
        <details name="accordion">
            <summary>Section 2</summary>
            <p>Content 2</p>
        </details>
        <details name="accordion">
            <summary>Section 3</summary>
            <p>Content 3</p>
        </details>
        """
        assert parse_and_check(html, 'details')


class TestSummaryElement:
    """Tests for <summary> element detection."""

    def test_summary_basic(self, parse_and_check):
        """Test basic summary element detection."""
        html = """
        <details>
            <summary>Summary text</summary>
        </details>
        """
        assert parse_and_check(html, 'details')  # summary maps to details

    def test_summary_with_elements(self, parse_and_check):
        """Test summary element with child elements."""
        html = """
        <details>
            <summary>
                <span class="icon">+</span>
                <span class="title">Expandable Section</span>
            </summary>
            <p>Content</p>
        </details>
        """
        assert parse_and_check(html, 'details')

    def test_summary_with_heading(self, parse_and_check):
        """Test summary element containing heading."""
        html = """
        <details>
            <summary><h3>FAQ Question</h3></summary>
            <p>FAQ Answer</p>
        </details>
        """
        assert parse_and_check(html, 'details')


class TestTemplateElement:
    """Tests for <template> element detection."""

    def test_template_basic(self, parse_and_check):
        """Test basic template element detection."""
        html = "<template>Template content</template>"
        assert parse_and_check(html, 'template')

    def test_template_with_id(self, parse_and_check):
        """Test template element with id."""
        html = """
        <template id="my-template">
            <div class="card">
                <h2>Title</h2>
                <p>Content</p>
            </div>
        </template>
        """
        assert parse_and_check(html, 'template')

    def test_template_for_list_item(self, parse_and_check):
        """Test template element for list rendering."""
        html = """
        <template id="list-item-template">
            <li class="item">
                <span class="name"></span>
                <span class="value"></span>
            </li>
        </template>
        """
        assert parse_and_check(html, 'template')

    def test_template_with_slot(self, parse_html):
        """Test template element with slot for web components."""
        html = """
        <template id="user-card-template">
            <style>
                .card { border: 1px solid gray; }
            </style>
            <div class="card">
                <slot name="username">Default Name</slot>
                <slot name="email">Default Email</slot>
            </div>
        </template>
        """
        features = parse_html(html)
        assert 'template' in features
        assert 'shadowdomv1' in features  # slot detected

    def test_template_for_table_row(self, parse_and_check):
        """Test template element for table row cloning."""
        html = """
        <table>
            <thead><tr><th>Name</th><th>Value</th></tr></thead>
            <tbody></tbody>
        </table>
        <template id="row-template">
            <tr>
                <td class="name"></td>
                <td class="value"></td>
            </tr>
        </template>
        """
        assert parse_and_check(html, 'template')


class TestCombinedInteractiveElements:
    """Tests for combinations of interactive elements."""

    def test_dialog_with_details(self, parse_html):
        """Test dialog containing details elements."""
        html = """
        <dialog>
            <h2>Options</h2>
            <details>
                <summary>Advanced Settings</summary>
                <p>Settings content</p>
            </details>
            <button>Close</button>
        </dialog>
        """
        features = parse_html(html)
        assert 'dialog' in features
        assert 'details' in features

    def test_all_interactive_elements(self, parse_html):
        """Test page with all interactive elements."""
        html = """
        <dialog id="modal">Modal content</dialog>
        <details><summary>Expandable</summary><p>Content</p></details>
        <template id="tmpl">Template content</template>
        """
        features = parse_html(html)
        assert 'dialog' in features
        assert 'details' in features
        assert 'template' in features

    def test_faq_page_structure(self, parse_html):
        """Test realistic FAQ page structure."""
        html = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>FAQ</h1>
            <details>
                <summary>What is this?</summary>
                <p>This is a FAQ section.</p>
            </details>
            <details>
                <summary>How does it work?</summary>
                <p>Click to expand/collapse.</p>
            </details>

            <template id="faq-template">
                <details>
                    <summary></summary>
                    <p></p>
                </details>
            </template>
        </body>
        </html>
        """
        features = parse_html(html)
        assert 'details' in features
        assert 'template' in features


class TestNoInteractiveElements:
    """Tests for HTML without interactive elements."""

    def test_no_interactive_elements(self, parse_html):
        """Test HTML without any interactive elements."""
        html = """
        <div>
            <p>Regular content</p>
            <a href="#">Link</a>
            <button>Button</button>
        </div>
        """
        features = parse_html(html)
        assert 'dialog' not in features
        assert 'details' not in features
        assert 'template' not in features
