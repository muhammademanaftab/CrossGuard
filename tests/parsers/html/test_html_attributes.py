"""Consolidated HTML attribute detection tests.

Covers: ARIA (wai-aria), form validation, content attributes, event attributes,
loading attributes, input attributes, iframe attributes, and more.
"""

import pytest


# ---------------------------------------------------------------------------
# ARIA attributes -> wai-aria  (collapsed from ~59 tests)
# ---------------------------------------------------------------------------

class TestAriaAttributes:
    """All ARIA-related attributes map to wai-aria."""

    @pytest.mark.parametrize("html", [
        # roles
        '<div role="button">Click</div>',
        '<div role="navigation">Nav</div>',
        '<div role="main">Main</div>',
        '<form role="search"><input type="text"></form>',
        '<div role="dialog">Dialog</div>',
        '<div role="alert">Alert</div>',
        '<div role="tablist"><div role="tab">T</div></div>',
        # aria-label / aria-labelledby / aria-describedby
        '<button aria-label="Close">X</button>',
        '<section aria-labelledby="title"><h2 id="title">T</h2></section>',
        '<input aria-describedby="hint"><span id="hint">Hint</span>',
        # aria-hidden / aria-live / aria-expanded
        '<div aria-hidden="true">Hidden</div>',
        '<div aria-live="polite">Status</div>',
        '<button aria-expanded="false">Expand</button>',
        # state / property / value / relationship attrs
        '<button aria-pressed="false">Toggle</button>',
        '<div aria-atomic="true">Atomic</div>',
    ], ids=[
        "role-button", "role-navigation", "role-main", "role-search",
        "role-dialog", "role-alert", "role-tablist",
        "aria-label", "aria-labelledby", "aria-describedby",
        "aria-hidden", "aria-live", "aria-expanded",
        "aria-pressed", "aria-atomic",
    ])
    @pytest.mark.unit
    def test_aria_detected(self, parse_features, html):
        assert 'wai-aria' in parse_features(html)

    @pytest.mark.unit
    def test_combined_aria(self, parse_features):
        html = """
        <nav role="navigation" aria-label="Main">
            <ul role="menubar">
                <li role="none"><a role="menuitem" aria-current="page" href="/">Home</a></li>
                <li role="none"><button role="menuitem" aria-haspopup="true" aria-expanded="false">More</button></li>
            </ul>
        </nav>
        """
        assert 'wai-aria' in parse_features(html)

    @pytest.mark.unit
    def test_no_aria(self, parse_features):
        html = '<div class="main"><p>No ARIA here</p></div>'
        assert 'wai-aria' not in parse_features(html)


# ---------------------------------------------------------------------------
# Form validation attributes -> form-validation / input-pattern / etc.
# ---------------------------------------------------------------------------

class TestFormValidationAttributes:

    @pytest.mark.parametrize("html", [
        '<input type="text" required>',
        '<select required><option>Choose</option></select>',
        '<textarea required></textarea>',
        '<input type="number" min="0">',
        '<input type="number" max="100">',
        '<input type="number" step="0.01">',
        '<form novalidate><input type="email"></form>',
        '<button type="submit" formnovalidate>Skip</button>',
    ], ids=[
        "required-input", "required-select", "required-textarea",
        "min", "max", "step", "novalidate", "formnovalidate",
    ])
    @pytest.mark.unit
    def test_form_validation(self, parse_features, html):
        assert 'form-validation' in parse_features(html)

    @pytest.mark.parametrize("html", [
        '<input type="text" pattern="[A-Za-z]{3}">',
        '<input type="tel" pattern="[0-9]{3}-[0-9]{4}">',
    ])
    @pytest.mark.unit
    def test_input_pattern(self, parse_features, html):
        assert 'input-pattern' in parse_features(html)

    @pytest.mark.parametrize("html", [
        '<input type="text" minlength="3">',
        '<textarea minlength="10"></textarea>',
        '<input type="password" minlength="8">',
    ])
    @pytest.mark.unit
    def test_input_minlength(self, parse_features, html):
        assert 'input-minlength' in parse_features(html)

    @pytest.mark.parametrize("html", [
        '<input type="text" maxlength="100">',
        '<textarea maxlength="500"></textarea>',
    ])
    @pytest.mark.unit
    def test_maxlength(self, parse_features, html):
        assert 'maxlength' in parse_features(html)

    @pytest.mark.unit
    def test_comprehensive_form(self, parse_features):
        html = """
        <form>
            <input type="text" required minlength="2" maxlength="50">
            <input type="tel" pattern="[0-9]{10}">
            <input type="number" min="18" max="120">
            <button type="submit" formnovalidate>Draft</button>
        </form>
        """
        features = parse_features(html)
        assert 'form-validation' in features
        assert 'input-pattern' in features
        assert 'input-minlength' in features
        assert 'maxlength' in features

    @pytest.mark.unit
    def test_no_form_validation(self, parse_features):
        html = '<form><input type="text" name="n"><input type="submit"></form>'
        features = parse_features(html)
        assert 'form-validation' not in features
        assert 'input-pattern' not in features


# ---------------------------------------------------------------------------
# Form submit attributes -> form-submit-attributes
# ---------------------------------------------------------------------------

class TestFormSubmitAttributes:

    @pytest.mark.parametrize("html", [
        '<button type="submit" formaction="/alt">Alt</button>',
        '<input type="submit" formaction="/draft" value="Draft">',
        '<button type="submit" formmethod="get">Get</button>',
        '<button type="submit" formenctype="multipart/form-data">Upload</button>',
        '<button type="submit" formtarget="_blank">New Tab</button>',
    ])
    @pytest.mark.unit
    def test_form_submit_attrs(self, parse_features, html):
        assert 'form-submit-attributes' in parse_features(html)


# ---------------------------------------------------------------------------
# form attribute -> form-attribute
# ---------------------------------------------------------------------------

class TestFormAttribute:

    @pytest.mark.parametrize("html", [
        '<form id="f"></form><input type="text" form="f">',
        '<form id="f"><input type="text"></form><button type="submit" form="f">Go</button>',
        '<form id="f"></form><select form="f"><option>A</option></select>',
        '<form id="f"></form><textarea form="f"></textarea>',
    ])
    @pytest.mark.unit
    def test_form_attribute(self, parse_features, html):
        assert 'form-attribute' in parse_features(html)


# ---------------------------------------------------------------------------
# ol reversed -> ol-reversed
# ---------------------------------------------------------------------------

class TestReversedAttribute:

    @pytest.mark.parametrize("html", [
        '<ol reversed><li>A</li><li>B</li></ol>',
        '<ol reversed="reversed"><li>Item</li></ol>',
        '<ol reversed start="10"><li>Ten</li></ol>',
    ])
    @pytest.mark.unit
    def test_ol_reversed(self, parse_features, html):
        assert 'ol-reversed' in parse_features(html)

    @pytest.mark.unit
    def test_no_reversed(self, parse_features):
        assert 'ol-reversed' not in parse_features('<ol><li>One</li></ol>')


# ---------------------------------------------------------------------------
# Content attributes
# ---------------------------------------------------------------------------

class TestContentAttributes:

    @pytest.mark.parametrize("html, feature_id", [
        ('<div contenteditable="true">Edit</div>', 'contenteditable'),
        ('<div contenteditable>Edit</div>', 'contenteditable'),
        ('<div draggable="true">Drag</div>', 'dragndrop'),
        ('<textarea spellcheck="true"></textarea>', 'spellcheck-attribute'),
        ('<span translate="no">Brand</span>', 'internationalization'),
        ('<div hidden>Hidden</div>', 'hidden'),
        ('<div hidden="until-found">Searchable</div>', 'hidden'),
        ('<a href="f.pdf" download>Download</a>', 'download'),
        ('<a href="f.pdf" download="report.pdf">Download</a>', 'download'),
    ], ids=[
        "contenteditable-true", "contenteditable-bool", "draggable",
        "spellcheck", "translate", "hidden-bool", "hidden-until-found",
        "download-bool", "download-filename",
    ])
    @pytest.mark.unit
    def test_content_attribute(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)

    @pytest.mark.unit
    def test_combined_content_attrs(self, parse_features):
        html = '<div contenteditable="true" spellcheck="true" translate="no" draggable="true">X</div>'
        features = parse_features(html)
        assert 'contenteditable' in features
        assert 'spellcheck-attribute' in features
        assert 'internationalization' in features
        assert 'dragndrop' in features

    @pytest.mark.unit
    def test_no_content_attrs(self, parse_features):
        html = '<div><p>Plain</p><a href="x.html">Link</a></div>'
        features = parse_features(html)
        for f in ('contenteditable', 'dragndrop', 'spellcheck-attribute', 'hidden', 'download'):
            assert f not in features


# ---------------------------------------------------------------------------
# Scoped style / directory input / manifest / ping / tabindex
# ---------------------------------------------------------------------------

class TestMiscAttributes:

    @pytest.mark.parametrize("html, feature_id", [
        ('<div><style scoped>p { color: red; }</style><p>Red</p></div>', 'style-scoped'),
        ('<input type="file" webkitdirectory>', 'input-file-directory'),
        ('<input type="file" directory>', 'input-file-directory'),
        ('<html manifest="app.appcache"><body>App</body></html>', 'offline-apps'),
        ('<a href="https://example.com" ping="/track">Link</a>', 'ping'),
        ('<div tabindex="0">Focusable</div>', 'tabindex-attr'),
        ('<div tabindex="-1">Programmatic</div>', 'tabindex-attr'),
    ], ids=[
        "style-scoped", "webkitdirectory", "directory",
        "manifest", "ping", "tabindex-0", "tabindex-neg1",
    ])
    @pytest.mark.unit
    def test_misc_attribute(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)

    @pytest.mark.unit
    def test_no_scoped(self, parse_features):
        assert 'style-scoped' not in parse_features('<style>body { margin: 0; }</style>')

    @pytest.mark.unit
    def test_no_directory(self, parse_features):
        assert 'input-file-directory' not in parse_features('<input type="file" multiple>')

    @pytest.mark.unit
    def test_no_manifest(self, parse_features):
        assert 'offline-apps' not in parse_features('<html><body>Content</body></html>')

    @pytest.mark.unit
    def test_no_ping(self, parse_features):
        assert 'ping' not in parse_features('<a href="https://example.com">Link</a>')


# ---------------------------------------------------------------------------
# Event attributes
# ---------------------------------------------------------------------------

class TestEventAttributes:

    @pytest.mark.parametrize("html, feature_id", [
        ('<input oninput="handle()">', 'input-event'),
        ('<div ontouchstart="handle()">Touch</div>', 'touch'),
        ('<div ontouchmove="handle()">Touch</div>', 'touch'),
        ('<div ontouchend="handle()">Touch</div>', 'touch'),
        ('<div ontouchcancel="handle()">Touch</div>', 'touch'),
        ('<div onpointerdown="handle()">Ptr</div>', 'pointer'),
        ('<div onpointerup="handle()">Ptr</div>', 'pointer'),
        ('<div onpointermove="handle()">Ptr</div>', 'pointer'),
        ('<div onpointerenter="handle()">Ptr</div>', 'pointer'),
        ('<div onfocusin="handle()">Focus</div>', 'focusin-focusout-events'),
        ('<body onhashchange="route()">App</body>', 'hashchange'),
        ('<body onpagehide="save()">App</body>', 'page-transition-events'),
        ('<body onbeforeprint="prep()">App</body>', 'beforeafterprint'),
    ], ids=[
        "oninput", "touchstart", "touchmove", "touchend", "touchcancel",
        "pointerdown", "pointerup", "pointermove", "pointerenter",
        "focusin", "hashchange", "pagehide", "beforeprint",
    ])
    @pytest.mark.unit
    def test_event_attribute(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)


# ---------------------------------------------------------------------------
# Loading / resource-hint attributes
# ---------------------------------------------------------------------------

class TestLoadingAttributes:

    @pytest.mark.parametrize("html, feature_id", [
        ('<img src="i.jpg" loading="lazy" alt="t">', 'loading-lazy-attr'),
        ('<iframe src="p.html" loading="lazy"></iframe>', 'loading-lazy-attr'),
        ('<script src="a.js" async></script>', 'script-async'),
        ('<script src="a.js" defer></script>', 'script-defer'),
        ('<link rel="stylesheet" href="s.css" integrity="sha256-abc" crossorigin>', 'subresource-integrity'),
        ('<script src="a.js" integrity="sha384-xyz" crossorigin></script>', 'subresource-integrity'),
        ('<input type="file" capture="environment">', 'html-media-capture'),
    ], ids=[
        "img-lazy", "iframe-lazy", "script-async", "script-defer",
        "sri-link", "sri-script", "media-capture",
    ])
    @pytest.mark.unit
    def test_loading_attribute(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)


# ---------------------------------------------------------------------------
# Input attributes
# ---------------------------------------------------------------------------

class TestInputAttributes:

    @pytest.mark.parametrize("html, feature_id", [
        ('<input placeholder="Enter name">', 'input-placeholder'),
        ('<textarea placeholder="Type here"></textarea>', 'input-placeholder'),
        ('<input autocomplete="email">', 'input-autocomplete-onoff'),
        ('<input autocomplete="off">', 'input-autocomplete-onoff'),
        ('<input autofocus>', 'autofocus'),
        ('<input inputmode="numeric">', 'input-inputmode'),
        ('<input type="file" multiple>', 'input-file-multiple'),
        ('<input type="file" accept="image/*">', 'input-file-accept'),
        ('<input readonly>', 'readonly-attr'),
        ('<textarea readonly></textarea>', 'readonly-attr'),
    ], ids=[
        "placeholder-input", "placeholder-textarea",
        "autocomplete-email", "autocomplete-off",
        "autofocus", "inputmode", "file-multiple", "file-accept",
        "readonly-input", "readonly-textarea",
    ])
    @pytest.mark.unit
    def test_input_attribute(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)


# ---------------------------------------------------------------------------
# Iframe attributes
# ---------------------------------------------------------------------------

class TestIframeAttributes:

    @pytest.mark.parametrize("html, feature_id", [
        ('<iframe sandbox src="p.html"></iframe>', 'iframe-sandbox'),
        ('<iframe sandbox="allow-scripts" src="p.html"></iframe>', 'iframe-sandbox'),
        ('<iframe srcdoc="<p>Hello</p>"></iframe>', 'iframe-srcdoc'),
    ], ids=["sandbox-bool", "sandbox-value", "srcdoc"])
    @pytest.mark.unit
    def test_iframe_attribute(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)
