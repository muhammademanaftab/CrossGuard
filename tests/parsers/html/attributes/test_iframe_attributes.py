"""Tests for HTML5 iframe attribute detection.

Tests attributes: sandbox, srcdoc
"""

import pytest


class TestSandboxAttribute:
    """Tests for sandbox attribute detection."""

    def test_sandbox_empty(self, parse_and_check):
        """Test sandbox with no value (most restrictive)."""
        html = '<iframe src="content.html" sandbox></iframe>'
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_allow_scripts(self, parse_and_check):
        """Test sandbox with allow-scripts."""
        html = '<iframe src="content.html" sandbox="allow-scripts"></iframe>'
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_allow_same_origin(self, parse_and_check):
        """Test sandbox with allow-same-origin."""
        html = '<iframe src="content.html" sandbox="allow-same-origin"></iframe>'
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_allow_forms(self, parse_and_check):
        """Test sandbox with allow-forms."""
        html = '<iframe src="form.html" sandbox="allow-forms"></iframe>'
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_allow_popups(self, parse_and_check):
        """Test sandbox with allow-popups."""
        html = '<iframe src="content.html" sandbox="allow-popups"></iframe>'
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_multiple_permissions(self, parse_and_check):
        """Test sandbox with multiple permissions."""
        html = '''
        <iframe src="app.html"
                sandbox="allow-scripts allow-same-origin allow-forms">
        </iframe>
        '''
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_allow_modals(self, parse_and_check):
        """Test sandbox with allow-modals."""
        html = '<iframe src="content.html" sandbox="allow-modals"></iframe>'
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_allow_top_navigation(self, parse_and_check):
        """Test sandbox with allow-top-navigation."""
        html = '<iframe src="content.html" sandbox="allow-top-navigation"></iframe>'
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_comprehensive(self, parse_and_check):
        """Test sandbox with many permissions."""
        html = '''
        <iframe src="embed.html"
                sandbox="allow-scripts
                         allow-same-origin
                         allow-forms
                         allow-popups
                         allow-modals
                         allow-orientation-lock
                         allow-pointer-lock
                         allow-presentation
                         allow-top-navigation">
        </iframe>
        '''
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_user_content(self, parse_and_check):
        """Test sandbox for user-generated content."""
        html = '''
        <div class="user-content">
            <iframe sandbox="allow-scripts allow-same-origin"
                    src="user-embed.html">
            </iframe>
        </div>
        '''
        assert parse_and_check(html, 'iframe-sandbox')

    def test_sandbox_third_party_widget(self, parse_and_check):
        """Test sandbox for third-party widget."""
        html = '''
        <iframe sandbox="allow-scripts allow-forms allow-popups"
                src="https://widget.example.com/embed">
        </iframe>
        '''
        assert parse_and_check(html, 'iframe-sandbox')


class TestSrcdocAttribute:
    """Tests for srcdoc attribute detection."""

    def test_srcdoc_basic(self, parse_and_check):
        """Test srcdoc with basic HTML."""
        html = '<iframe srcdoc="<p>Hello World</p>"></iframe>'
        assert parse_and_check(html, 'iframe-srcdoc')

    def test_srcdoc_complete_document(self, parse_and_check):
        """Test srcdoc with complete HTML document."""
        html = '''
        <iframe srcdoc="<!DOCTYPE html><html><body><h1>Title</h1></body></html>">
        </iframe>
        '''
        assert parse_and_check(html, 'iframe-srcdoc')

    def test_srcdoc_with_styles(self, parse_and_check):
        """Test srcdoc with inline styles."""
        html = '''
        <iframe srcdoc="<style>body{color:red;}</style><p>Styled text</p>">
        </iframe>
        '''
        assert parse_and_check(html, 'iframe-srcdoc')

    def test_srcdoc_escaped_html(self, parse_and_check):
        """Test srcdoc with escaped HTML entities."""
        html = '<iframe srcdoc="&lt;p&gt;Escaped HTML&lt;/p&gt;"></iframe>'
        assert parse_and_check(html, 'iframe-srcdoc')

    def test_srcdoc_with_fallback_src(self, parse_and_check):
        """Test srcdoc with fallback src attribute."""
        html = '''
        <iframe srcdoc="<p>Primary content</p>"
                src="fallback.html">
        </iframe>
        '''
        assert parse_and_check(html, 'iframe-srcdoc')

    def test_srcdoc_preview(self, parse_and_check):
        """Test srcdoc for HTML preview (like code editors)."""
        html = '''
        <div class="preview-panel">
            <iframe srcdoc="<h1>Preview</h1><p>Your content here</p>">
            </iframe>
        </div>
        '''
        assert parse_and_check(html, 'iframe-srcdoc')


class TestCombinedIframeAttributes:
    """Tests for combined sandbox and srcdoc."""

    def test_sandbox_and_srcdoc(self, parse_html):
        """Test iframe with both sandbox and srcdoc."""
        html = '''
        <iframe sandbox="allow-scripts"
                srcdoc="<script>alert('test')</script>">
        </iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' in features
        assert 'iframe-srcdoc' in features

    def test_sandboxed_preview(self, parse_html):
        """Test sandboxed content preview."""
        html = '''
        <iframe sandbox="allow-scripts allow-same-origin"
                srcdoc="<p>User content preview</p>"
                width="100%"
                height="300">
        </iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' in features
        assert 'iframe-srcdoc' in features

    def test_secure_embed(self, parse_html):
        """Test secure embed with minimal permissions."""
        html = '''
        <iframe sandbox=""
                srcdoc="<p>Fully sandboxed content</p>">
        </iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' in features
        assert 'iframe-srcdoc' in features

    def test_multiple_iframes_mixed(self, parse_html):
        """Test multiple iframes with different attributes."""
        html = '''
        <iframe src="external.html" sandbox="allow-scripts"></iframe>
        <iframe srcdoc="<p>Inline content</p>"></iframe>
        <iframe sandbox srcdoc="<p>Both</p>"></iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' in features
        assert 'iframe-srcdoc' in features


class TestIframeSecurityPatterns:
    """Tests for common iframe security patterns."""

    def test_untrusted_content(self, parse_html):
        """Test iframe for untrusted content."""
        html = '''
        <iframe sandbox
                src="https://untrusted-site.example.com/embed"
                width="300"
                height="200">
        </iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' in features

    def test_payment_widget(self, parse_html):
        """Test iframe for payment widget with specific permissions."""
        html = '''
        <iframe sandbox="allow-scripts allow-forms allow-same-origin"
                src="https://payment.example.com/checkout"
                width="400"
                height="600">
        </iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' in features

    def test_social_embed(self, parse_html):
        """Test iframe for social media embed."""
        html = '''
        <iframe sandbox="allow-scripts allow-same-origin allow-popups"
                src="https://social.example.com/post/12345/embed"
                width="500"
                height="400">
        </iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' in features


class TestNoIframeAttributes:
    """Tests for iframes without special attributes."""

    def test_basic_iframe(self, parse_html):
        """Test basic iframe without sandbox or srcdoc."""
        html = '<iframe src="content.html" width="600" height="400"></iframe>'
        features = parse_html(html)
        assert 'iframe-sandbox' not in features
        assert 'iframe-srcdoc' not in features

    def test_youtube_embed(self, parse_html):
        """Test typical YouTube embed (no sandbox)."""
        html = '''
        <iframe width="560" height="315"
                src="https://www.youtube.com/embed/VIDEO_ID"
                frameborder="0"
                allowfullscreen>
        </iframe>
        '''
        features = parse_html(html)
        assert 'iframe-sandbox' not in features
        assert 'iframe-srcdoc' not in features
