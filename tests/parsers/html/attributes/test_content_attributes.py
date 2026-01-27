"""Tests for HTML5 content attribute detection.

Tests attributes: contenteditable, draggable, spellcheck, translate, hidden, download
"""

import pytest


class TestContenteditableAttribute:
    """Tests for contenteditable attribute detection."""

    def test_contenteditable_true(self, parse_and_check):
        """Test contenteditable=true."""
        html = '<div contenteditable="true">Edit me</div>'
        assert parse_and_check(html, 'contenteditable')

    def test_contenteditable_empty(self, parse_and_check):
        """Test contenteditable with empty value (treated as true)."""
        html = '<div contenteditable="">Edit me</div>'
        assert parse_and_check(html, 'contenteditable')

    def test_contenteditable_boolean(self, parse_and_check):
        """Test contenteditable as boolean attribute."""
        html = '<div contenteditable>Edit me</div>'
        assert parse_and_check(html, 'contenteditable')

    def test_contenteditable_false(self, parse_and_check):
        """Test contenteditable=false (still detects attribute)."""
        html = '<div contenteditable="false">Not editable</div>'
        assert parse_and_check(html, 'contenteditable')

    def test_contenteditable_on_paragraph(self, parse_and_check):
        """Test contenteditable on paragraph."""
        html = '<p contenteditable="true">Editable paragraph</p>'
        assert parse_and_check(html, 'contenteditable')

    def test_contenteditable_rich_editor(self, parse_and_check):
        """Test contenteditable in rich text editor context."""
        html = """
        <div class="editor">
            <div class="toolbar">
                <button>Bold</button>
                <button>Italic</button>
            </div>
            <div contenteditable="true" class="content">
                Type here...
            </div>
        </div>
        """
        assert parse_and_check(html, 'contenteditable')


class TestDraggableAttribute:
    """Tests for draggable attribute detection."""

    def test_draggable_true(self, parse_and_check):
        """Test draggable=true."""
        html = '<div draggable="true">Drag me</div>'
        assert parse_and_check(html, 'dragndrop')

    def test_draggable_false(self, parse_and_check):
        """Test draggable=false (still detects attribute)."""
        html = '<div draggable="false">Not draggable</div>'
        assert parse_and_check(html, 'dragndrop')

    def test_draggable_on_list_item(self, parse_and_check):
        """Test draggable on list items for reordering."""
        html = """
        <ul>
            <li draggable="true">Item 1</li>
            <li draggable="true">Item 2</li>
            <li draggable="true">Item 3</li>
        </ul>
        """
        assert parse_and_check(html, 'dragndrop')

    def test_draggable_card(self, parse_and_check):
        """Test draggable on card element."""
        html = """
        <div class="card" draggable="true">
            <h3>Task</h3>
            <p>Description</p>
        </div>
        """
        assert parse_and_check(html, 'dragndrop')


class TestSpellcheckAttribute:
    """Tests for spellcheck attribute detection."""

    def test_spellcheck_true(self, parse_and_check):
        """Test spellcheck=true."""
        html = '<textarea spellcheck="true"></textarea>'
        assert parse_and_check(html, 'spellcheck-attribute')

    def test_spellcheck_false(self, parse_and_check):
        """Test spellcheck=false."""
        html = '<input type="text" spellcheck="false">'
        assert parse_and_check(html, 'spellcheck-attribute')

    def test_spellcheck_on_contenteditable(self, parse_html):
        """Test spellcheck on contenteditable element."""
        html = '<div contenteditable="true" spellcheck="true">Type here</div>'
        features = parse_html(html)
        assert 'spellcheck-attribute' in features
        assert 'contenteditable' in features

    def test_spellcheck_code_editor(self, parse_and_check):
        """Test spellcheck disabled for code."""
        html = '<textarea spellcheck="false" class="code-editor"></textarea>'
        assert parse_and_check(html, 'spellcheck-attribute')


class TestTranslateAttribute:
    """Tests for translate attribute detection."""

    def test_translate_yes(self, parse_and_check):
        """Test translate=yes."""
        html = '<p translate="yes">Translate this</p>'
        assert parse_and_check(html, 'internationalization')

    def test_translate_no(self, parse_and_check):
        """Test translate=no."""
        html = '<span translate="no">BrandName</span>'
        assert parse_and_check(html, 'internationalization')

    def test_translate_empty(self, parse_and_check):
        """Test translate with empty value."""
        html = '<span translate="">Text</span>'
        assert parse_and_check(html, 'internationalization')

    def test_translate_on_brand(self, parse_and_check):
        """Test translate=no on brand name."""
        html = """
        <p>Visit <span translate="no">TechCorp Inc.</span> for more info.</p>
        """
        assert parse_and_check(html, 'internationalization')

    def test_translate_on_code(self, parse_and_check):
        """Test translate=no on code snippets."""
        html = '<code translate="no">console.log("Hello")</code>'
        assert parse_and_check(html, 'internationalization')


class TestHiddenAttribute:
    """Tests for hidden attribute detection."""

    def test_hidden_boolean(self, parse_and_check):
        """Test hidden as boolean attribute."""
        html = '<div hidden>Hidden content</div>'
        assert parse_and_check(html, 'hidden')

    def test_hidden_empty_value(self, parse_and_check):
        """Test hidden with empty value."""
        html = '<div hidden="">Hidden content</div>'
        assert parse_and_check(html, 'hidden')

    def test_hidden_value(self, parse_and_check):
        """Test hidden=hidden."""
        html = '<div hidden="hidden">Hidden content</div>'
        assert parse_and_check(html, 'hidden')

    def test_hidden_until_found(self, parse_and_check):
        """Test hidden=until-found (new value)."""
        html = '<div hidden="until-found">Searchable but hidden</div>'
        assert parse_and_check(html, 'hidden')

    def test_hidden_on_template_content(self, parse_and_check):
        """Test hidden on template-like content."""
        html = """
        <div id="loading" hidden>Loading...</div>
        <div id="error" hidden>An error occurred</div>
        <div id="content">Main content</div>
        """
        assert parse_and_check(html, 'hidden')


class TestDownloadAttribute:
    """Tests for download attribute detection."""

    def test_download_boolean(self, parse_and_check):
        """Test download as boolean attribute."""
        html = '<a href="file.pdf" download>Download PDF</a>'
        assert parse_and_check(html, 'download')

    def test_download_with_filename(self, parse_and_check):
        """Test download with custom filename."""
        html = '<a href="report.pdf" download="annual-report-2024.pdf">Download</a>'
        assert parse_and_check(html, 'download')

    def test_download_image(self, parse_and_check):
        """Test download for image."""
        html = '<a href="photo.jpg" download="vacation-photo.jpg">Download Photo</a>'
        assert parse_and_check(html, 'download')

    def test_download_blob_url(self, parse_and_check):
        """Test download with blob URL pattern."""
        html = '<a href="#" download="generated.txt">Download Generated File</a>'
        assert parse_and_check(html, 'download')

    def test_download_in_gallery(self, parse_and_check):
        """Test download links in image gallery."""
        html = """
        <div class="gallery">
            <img src="img1.jpg" alt="Image 1">
            <a href="img1-full.jpg" download>Download Full Size</a>

            <img src="img2.jpg" alt="Image 2">
            <a href="img2-full.jpg" download>Download Full Size</a>
        </div>
        """
        assert parse_and_check(html, 'download')


class TestCombinedContentAttributes:
    """Tests for combined content attributes."""

    def test_interactive_element(self, parse_html):
        """Test element with multiple content attributes."""
        html = """
        <div contenteditable="true"
             spellcheck="true"
             translate="no"
             draggable="true">
            Interactive content
        </div>
        """
        features = parse_html(html)
        assert 'contenteditable' in features
        assert 'spellcheck-attribute' in features
        assert 'internationalization' in features
        assert 'dragndrop' in features

    def test_page_with_hidden_and_download(self, parse_html):
        """Test page with hidden and download."""
        html = """
        <div hidden id="modal">Modal content</div>
        <a href="file.pdf" download>Download</a>
        """
        features = parse_html(html)
        assert 'hidden' in features
        assert 'download' in features

    def test_rich_text_editor(self, parse_html):
        """Test rich text editor setup."""
        html = """
        <div class="editor-container">
            <div class="toolbar" hidden id="format-toolbar">
                <button>B</button>
                <button>I</button>
            </div>
            <div contenteditable="true"
                 spellcheck="true"
                 class="editor-content">
                Start typing...
            </div>
        </div>
        """
        features = parse_html(html)
        assert 'contenteditable' in features
        assert 'spellcheck-attribute' in features
        assert 'hidden' in features


class TestNoContentAttributes:
    """Tests for HTML without content attributes."""

    def test_no_content_attributes(self, parse_html):
        """Test HTML without content attributes."""
        html = """
        <div>
            <p>Regular paragraph</p>
            <a href="link.html">Regular link</a>
        </div>
        """
        features = parse_html(html)
        assert 'contenteditable' not in features
        assert 'dragndrop' not in features
        assert 'spellcheck-attribute' not in features
        assert 'hidden' not in features
        assert 'download' not in features


class TestScopedStyleAttribute:
    """Tests for scoped style attribute detection (deprecated but in CIU)."""

    def test_scoped_on_style(self, parse_and_check):
        """Test scoped attribute on style element."""
        html = """
        <div>
            <style scoped>
                p { color: red; }
            </style>
            <p>This will be red</p>
        </div>
        """
        assert parse_and_check(html, 'style-scoped')

    def test_scoped_boolean(self, parse_and_check):
        """Test scoped as boolean attribute."""
        html = '<style scoped="scoped">.local { color: blue; }</style>'
        assert parse_and_check(html, 'style-scoped')

    def test_scoped_in_component(self, parse_and_check):
        """Test scoped style in component context."""
        html = """
        <div class="component">
            <style scoped>
                .component { border: 1px solid; }
                h2 { font-size: 1.5rem; }
            </style>
            <h2>Component Title</h2>
            <p>Component content</p>
        </div>
        """
        assert parse_and_check(html, 'style-scoped')

    def test_no_scoped(self, parse_html):
        """Test style without scoped attribute."""
        html = '<style>body { margin: 0; }</style>'
        features = parse_html(html)
        assert 'style-scoped' not in features


class TestDirectoryInputAttributes:
    """Tests for directory input attributes (webkitdirectory/directory)."""

    def test_webkitdirectory(self, parse_and_check):
        """Test webkitdirectory attribute on file input."""
        html = '<input type="file" webkitdirectory>'
        assert parse_and_check(html, 'input-file-directory')

    def test_webkitdirectory_boolean(self, parse_and_check):
        """Test webkitdirectory as boolean value."""
        html = '<input type="file" webkitdirectory="webkitdirectory">'
        assert parse_and_check(html, 'input-file-directory')

    def test_directory_attribute(self, parse_and_check):
        """Test directory attribute on file input."""
        html = '<input type="file" directory>'
        assert parse_and_check(html, 'input-file-directory')

    def test_both_directory_attributes(self, parse_and_check):
        """Test both webkitdirectory and directory attributes."""
        html = '<input type="file" webkitdirectory directory multiple>'
        assert parse_and_check(html, 'input-file-directory')

    def test_folder_upload_form(self, parse_html):
        """Test folder upload form context."""
        html = """
        <form>
            <label>
                Upload Folder:
                <input type="file" webkitdirectory multiple>
            </label>
            <button type="submit">Upload</button>
        </form>
        """
        features = parse_html(html)
        assert 'input-file-directory' in features
        assert 'input-file-multiple' in features

    def test_no_directory_attribute(self, parse_html):
        """Test file input without directory attributes."""
        html = '<input type="file" multiple>'
        features = parse_html(html)
        assert 'input-file-directory' not in features


class TestManifestAttribute:
    """Tests for manifest attribute (offline apps, deprecated)."""

    def test_manifest_on_html(self, parse_and_check):
        """Test manifest attribute on html element."""
        html = '<html manifest="app.appcache"><body>App</body></html>'
        assert parse_and_check(html, 'offline-apps')

    def test_manifest_with_path(self, parse_and_check):
        """Test manifest with full path."""
        html = '<html manifest="/cache/app.manifest"><body>Content</body></html>'
        assert parse_and_check(html, 'offline-apps')

    def test_no_manifest(self, parse_html):
        """Test html without manifest attribute."""
        html = '<html><body>Content</body></html>'
        features = parse_html(html)
        assert 'offline-apps' not in features


class TestPingAttribute:
    """Tests for ping attribute detection."""

    def test_ping_on_anchor(self, parse_and_check):
        """Test ping attribute on anchor element."""
        html = '<a href="https://example.com" ping="/track">Link</a>'
        assert parse_and_check(html, 'ping')

    def test_ping_multiple_urls(self, parse_and_check):
        """Test ping with multiple URLs."""
        html = '<a href="#" ping="/track1 /track2">Tracked Link</a>'
        assert parse_and_check(html, 'ping')

    def test_ping_analytics(self, parse_and_check):
        """Test ping for analytics tracking."""
        html = """
        <a href="https://external.com"
           ping="/analytics?event=click&target=external">
            External Site
        </a>
        """
        assert parse_and_check(html, 'ping')

    def test_no_ping(self, parse_html):
        """Test anchor without ping attribute."""
        html = '<a href="https://example.com">Link</a>'
        features = parse_html(html)
        assert 'ping' not in features


class TestTabindexAttribute:
    """Tests for tabindex attribute detection."""

    def test_tabindex_positive(self, parse_and_check):
        """Test tabindex with positive value."""
        html = '<div tabindex="1">Focusable</div>'
        assert parse_and_check(html, 'tabindex-attr')

    def test_tabindex_zero(self, parse_and_check):
        """Test tabindex=0."""
        html = '<span tabindex="0">Focusable in order</span>'
        assert parse_and_check(html, 'tabindex-attr')

    def test_tabindex_negative(self, parse_and_check):
        """Test tabindex=-1."""
        html = '<div tabindex="-1">Programmatically focusable</div>'
        assert parse_and_check(html, 'tabindex-attr')

    def test_tabindex_on_custom_button(self, parse_and_check):
        """Test tabindex on custom button element."""
        html = '<div role="button" tabindex="0">Custom Button</div>'
        assert parse_and_check(html, 'tabindex-attr')
