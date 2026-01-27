"""Tests for WAI-ARIA attribute detection.

Tests attributes: role, aria-label, aria-hidden, aria-live, aria-expanded, and many more
All map to feature ID: wai-aria
"""

import pytest


class TestRoleAttribute:
    """Tests for role attribute detection."""

    def test_role_button(self, parse_and_check):
        """Test role=button."""
        html = '<div role="button">Click me</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_role_navigation(self, parse_and_check):
        """Test role=navigation."""
        html = '<div role="navigation">Nav content</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_role_main(self, parse_and_check):
        """Test role=main."""
        html = '<div role="main">Main content</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_role_search(self, parse_and_check):
        """Test role=search."""
        html = '<form role="search"><input type="text"></form>'
        assert parse_and_check(html, 'wai-aria')

    def test_role_dialog(self, parse_and_check):
        """Test role=dialog."""
        html = '<div role="dialog">Dialog content</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_role_alert(self, parse_and_check):
        """Test role=alert."""
        html = '<div role="alert">Important message</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_role_tablist(self, parse_and_check):
        """Test role=tablist."""
        html = '''
        <div role="tablist">
            <div role="tab">Tab 1</div>
            <div role="tab">Tab 2</div>
        </div>
        '''
        assert parse_and_check(html, 'wai-aria')


class TestAriaLabelAttribute:
    """Tests for aria-label attribute detection."""

    def test_aria_label_on_button(self, parse_and_check):
        """Test aria-label on button."""
        html = '<button aria-label="Close dialog">X</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_label_on_icon(self, parse_and_check):
        """Test aria-label on icon button."""
        html = '<button aria-label="Menu"><svg>...</svg></button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_label_on_link(self, parse_and_check):
        """Test aria-label on link."""
        html = '<a href="#" aria-label="Open in new tab">Link</a>'
        assert parse_and_check(html, 'wai-aria')


class TestAriaLabelledbyAttribute:
    """Tests for aria-labelledby attribute detection."""

    def test_aria_labelledby(self, parse_and_check):
        """Test aria-labelledby linking to heading."""
        html = '''
        <h2 id="section-title">Section Title</h2>
        <div aria-labelledby="section-title">Content</div>
        '''
        assert parse_and_check(html, 'wai-aria')

    def test_aria_labelledby_dialog(self, parse_and_check):
        """Test aria-labelledby on dialog."""
        html = '''
        <div role="dialog" aria-labelledby="dialog-title">
            <h2 id="dialog-title">Confirm Action</h2>
        </div>
        '''
        assert parse_and_check(html, 'wai-aria')


class TestAriaDescribedbyAttribute:
    """Tests for aria-describedby attribute detection."""

    def test_aria_describedby(self, parse_and_check):
        """Test aria-describedby for additional description."""
        html = '''
        <input type="password" aria-describedby="pwd-hint">
        <span id="pwd-hint">Must be at least 8 characters</span>
        '''
        assert parse_and_check(html, 'wai-aria')


class TestAriaHiddenAttribute:
    """Tests for aria-hidden attribute detection."""

    def test_aria_hidden_true(self, parse_and_check):
        """Test aria-hidden=true."""
        html = '<span aria-hidden="true">Decorative icon</span>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_hidden_false(self, parse_and_check):
        """Test aria-hidden=false."""
        html = '<div aria-hidden="false">Visible content</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_hidden_icon(self, parse_and_check):
        """Test aria-hidden on decorative icon."""
        html = '''
        <button>
            <span aria-hidden="true">*</span>
            Required
        </button>
        '''
        assert parse_and_check(html, 'wai-aria')


class TestAriaLiveAttribute:
    """Tests for aria-live attribute detection."""

    def test_aria_live_polite(self, parse_and_check):
        """Test aria-live=polite."""
        html = '<div aria-live="polite">Status updates here</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_live_assertive(self, parse_and_check):
        """Test aria-live=assertive."""
        html = '<div aria-live="assertive">Error messages here</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_live_off(self, parse_and_check):
        """Test aria-live=off."""
        html = '<div aria-live="off">Not announced</div>'
        assert parse_and_check(html, 'wai-aria')


class TestAriaExpandedAttribute:
    """Tests for aria-expanded attribute detection."""

    def test_aria_expanded_true(self, parse_and_check):
        """Test aria-expanded=true."""
        html = '<button aria-expanded="true">Collapse</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_expanded_false(self, parse_and_check):
        """Test aria-expanded=false."""
        html = '<button aria-expanded="false">Expand</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_expanded_accordion(self, parse_and_check):
        """Test aria-expanded in accordion."""
        html = '''
        <button aria-expanded="false" aria-controls="panel1">Section 1</button>
        <div id="panel1" hidden>Content</div>
        '''
        assert parse_and_check(html, 'wai-aria')


class TestAriaStateAttributes:
    """Tests for aria state attributes."""

    def test_aria_disabled(self, parse_and_check):
        """Test aria-disabled attribute."""
        html = '<button aria-disabled="true">Disabled Button</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_pressed(self, parse_and_check):
        """Test aria-pressed attribute."""
        html = '<button aria-pressed="true">Toggle On</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_selected(self, parse_and_check):
        """Test aria-selected attribute."""
        html = '<div role="tab" aria-selected="true">Tab 1</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_checked(self, parse_and_check):
        """Test aria-checked attribute."""
        html = '<div role="checkbox" aria-checked="true">Checked</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_invalid(self, parse_and_check):
        """Test aria-invalid attribute."""
        html = '<input type="email" aria-invalid="true">'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_busy(self, parse_and_check):
        """Test aria-busy attribute."""
        html = '<div aria-busy="true">Loading...</div>'
        assert parse_and_check(html, 'wai-aria')


class TestAriaPropertyAttributes:
    """Tests for aria property attributes."""

    def test_aria_controls(self, parse_and_check):
        """Test aria-controls attribute."""
        html = '<button aria-controls="menu">Toggle Menu</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_haspopup(self, parse_and_check):
        """Test aria-haspopup attribute."""
        html = '<button aria-haspopup="true">Menu</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_current(self, parse_and_check):
        """Test aria-current attribute."""
        html = '<a href="/" aria-current="page">Home</a>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_modal(self, parse_and_check):
        """Test aria-modal attribute."""
        html = '<div role="dialog" aria-modal="true">Modal content</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_orientation(self, parse_and_check):
        """Test aria-orientation attribute."""
        html = '<div role="slider" aria-orientation="horizontal"></div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_autocomplete(self, parse_and_check):
        """Test aria-autocomplete attribute."""
        html = '<input type="text" role="combobox" aria-autocomplete="list">'
        assert parse_and_check(html, 'wai-aria')


class TestAriaValueAttributes:
    """Tests for aria value attributes."""

    def test_aria_valuemin(self, parse_and_check):
        """Test aria-valuemin attribute."""
        html = '<div role="slider" aria-valuemin="0"></div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_valuemax(self, parse_and_check):
        """Test aria-valuemax attribute."""
        html = '<div role="slider" aria-valuemax="100"></div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_valuenow(self, parse_and_check):
        """Test aria-valuenow attribute."""
        html = '<div role="slider" aria-valuenow="50"></div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_valuetext(self, parse_and_check):
        """Test aria-valuetext attribute."""
        html = '<div role="slider" aria-valuenow="3" aria-valuetext="Medium"></div>'
        assert parse_and_check(html, 'wai-aria')

    def test_complete_slider(self, parse_html):
        """Test complete slider with all value attributes."""
        html = '''
        <div role="slider"
             aria-valuemin="0"
             aria-valuemax="100"
             aria-valuenow="50"
             aria-valuetext="50 percent">
        </div>
        '''
        features = parse_html(html)
        assert 'wai-aria' in features


class TestAriaRelationshipAttributes:
    """Tests for aria relationship attributes."""

    def test_aria_owns(self, parse_and_check):
        """Test aria-owns attribute."""
        html = '<div aria-owns="menu-items">Menu container</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_flowto(self, parse_and_check):
        """Test aria-flowto attribute."""
        html = '<div aria-flowto="next-section">Read next</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_activedescendant(self, parse_and_check):
        """Test aria-activedescendant attribute."""
        html = '<div role="listbox" aria-activedescendant="option-2"></div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_errormessage(self, parse_and_check):
        """Test aria-errormessage attribute."""
        html = '''
        <input type="email" aria-invalid="true" aria-errormessage="email-error">
        <span id="email-error">Please enter a valid email</span>
        '''
        assert parse_and_check(html, 'wai-aria')

    def test_aria_details(self, parse_and_check):
        """Test aria-details attribute."""
        html = '<img src="chart.png" alt="Sales chart" aria-details="chart-data">'
        assert parse_and_check(html, 'wai-aria')


class TestAriaTextAttributes:
    """Tests for aria text attributes."""

    def test_aria_keyshortcuts(self, parse_and_check):
        """Test aria-keyshortcuts attribute."""
        html = '<button aria-keyshortcuts="Alt+S">Save</button>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_roledescription(self, parse_and_check):
        """Test aria-roledescription attribute."""
        html = '<div role="region" aria-roledescription="slide">Slide 1</div>'
        assert parse_and_check(html, 'wai-aria')


class TestAriaListAttributes:
    """Tests for aria list-related attributes."""

    def test_aria_level(self, parse_and_check):
        """Test aria-level attribute."""
        html = '<div role="heading" aria-level="2">Subheading</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_posinset(self, parse_and_check):
        """Test aria-posinset attribute."""
        html = '<div role="listitem" aria-posinset="3">Item 3</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_setsize(self, parse_and_check):
        """Test aria-setsize attribute."""
        html = '<div role="listitem" aria-setsize="10">Item</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_sort(self, parse_and_check):
        """Test aria-sort attribute."""
        html = '<th aria-sort="ascending">Name</th>'
        assert parse_and_check(html, 'wai-aria')


class TestAriaMultiAttributes:
    """Tests for aria multi-selection attributes."""

    def test_aria_multiline(self, parse_and_check):
        """Test aria-multiline attribute."""
        html = '<div role="textbox" aria-multiline="true">Editable</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_multiselectable(self, parse_and_check):
        """Test aria-multiselectable attribute."""
        html = '<div role="listbox" aria-multiselectable="true"></div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_readonly(self, parse_and_check):
        """Test aria-readonly attribute."""
        html = '<div role="textbox" aria-readonly="true">Read only</div>'
        assert parse_and_check(html, 'wai-aria')

    def test_aria_required(self, parse_and_check):
        """Test aria-required attribute."""
        html = '<input type="text" aria-required="true">'
        assert parse_and_check(html, 'wai-aria')


class TestAriaAtomicAttribute:
    """Tests for aria-atomic attribute detection."""

    def test_aria_atomic(self, parse_and_check):
        """Test aria-atomic attribute."""
        html = '<div aria-live="polite" aria-atomic="true">Live region</div>'
        assert parse_and_check(html, 'wai-aria')


class TestCombinedAriaAttributes:
    """Tests for combinations of ARIA attributes."""

    def test_accessible_modal(self, parse_html):
        """Test fully accessible modal dialog."""
        html = '''
        <div role="dialog"
             aria-modal="true"
             aria-labelledby="dialog-title"
             aria-describedby="dialog-desc">
            <h2 id="dialog-title">Confirm Delete</h2>
            <p id="dialog-desc">Are you sure you want to delete this item?</p>
            <button>Cancel</button>
            <button>Delete</button>
        </div>
        '''
        features = parse_html(html)
        assert 'wai-aria' in features

    def test_accessible_tabs(self, parse_html):
        """Test accessible tab interface."""
        html = '''
        <div role="tablist" aria-label="Sample Tabs">
            <button role="tab" aria-selected="true" aria-controls="panel-1">Tab 1</button>
            <button role="tab" aria-selected="false" aria-controls="panel-2">Tab 2</button>
        </div>
        <div role="tabpanel" id="panel-1" aria-labelledby="tab-1">Content 1</div>
        <div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>Content 2</div>
        '''
        features = parse_html(html)
        assert 'wai-aria' in features

    def test_accessible_navigation(self, parse_html):
        """Test accessible navigation menu."""
        html = '''
        <nav aria-label="Main Navigation">
            <ul role="menubar">
                <li role="none">
                    <a role="menuitem" href="/" aria-current="page">Home</a>
                </li>
                <li role="none">
                    <button role="menuitem" aria-haspopup="true" aria-expanded="false">
                        Products
                    </button>
                </li>
            </ul>
        </nav>
        '''
        features = parse_html(html)
        assert 'wai-aria' in features


class TestNoAriaAttributes:
    """Tests for HTML without ARIA attributes."""

    def test_no_aria(self, parse_html):
        """Test HTML without any ARIA attributes."""
        html = """
        <div>
            <h1>Title</h1>
            <p>Paragraph</p>
            <button>Click</button>
        </div>
        """
        features = parse_html(html)
        assert 'wai-aria' not in features
