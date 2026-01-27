"""Tests for Content Security Policy meta tag detection.

Tests http-equiv values: content-security-policy, x-content-security-policy
"""

import pytest


class TestContentSecurityPolicy:
    """Tests for http-equiv=content-security-policy detection."""

    def test_csp_basic(self, parse_and_check):
        """Test basic CSP meta tag."""
        html = '''
        <meta http-equiv="content-security-policy"
              content="default-src 'self'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_with_script_src(self, parse_and_check):
        """Test CSP with script-src directive."""
        html = '''
        <meta http-equiv="content-security-policy"
              content="script-src 'self' https://cdn.example.com">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_with_style_src(self, parse_and_check):
        """Test CSP with style-src directive."""
        html = '''
        <meta http-equiv="content-security-policy"
              content="style-src 'self' 'unsafe-inline'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_with_img_src(self, parse_and_check):
        """Test CSP with img-src directive."""
        html = '''
        <meta http-equiv="content-security-policy"
              content="img-src 'self' data: https:">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_comprehensive(self, parse_and_check):
        """Test comprehensive CSP policy."""
        html = '''
        <meta http-equiv="content-security-policy"
              content="default-src 'self';
                       script-src 'self' https://cdn.example.com;
                       style-src 'self' 'unsafe-inline';
                       img-src 'self' data: https:;
                       font-src 'self' https://fonts.gstatic.com;
                       connect-src 'self' https://api.example.com;
                       frame-ancestors 'none';
                       base-uri 'self';
                       form-action 'self'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_with_nonce(self, parse_and_check):
        """Test CSP with nonce for inline scripts."""
        html = '''
        <meta http-equiv="content-security-policy"
              content="script-src 'nonce-abc123'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_with_hash(self, parse_and_check):
        """Test CSP with hash for inline scripts."""
        html = '''
        <meta http-equiv="content-security-policy"
              content="script-src 'sha256-abc123...'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_report_only(self, parse_and_check):
        """Test CSP report-only mode (still uses same feature)."""
        # Note: report-only via meta tag is not actually supported,
        # but we detect the pattern regardless
        html = '''
        <meta http-equiv="content-security-policy"
              content="default-src 'self'; report-uri /csp-report">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')


class TestXContentSecurityPolicy:
    """Tests for http-equiv=x-content-security-policy detection (legacy)."""

    def test_x_csp_basic(self, parse_and_check):
        """Test legacy X-Content-Security-Policy meta tag."""
        html = '''
        <meta http-equiv="x-content-security-policy"
              content="default-src 'self'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy')

    def test_x_csp_with_directives(self, parse_and_check):
        """Test legacy X-CSP with multiple directives."""
        html = '''
        <meta http-equiv="x-content-security-policy"
              content="default-src 'self'; script-src 'self' 'unsafe-inline'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy')


class TestBothCSPVersions:
    """Tests for pages with both CSP versions."""

    def test_both_csp_headers(self, parse_html):
        """Test page with both modern and legacy CSP."""
        html = """
        <head>
            <meta http-equiv="content-security-policy"
                  content="default-src 'self'">
            <meta http-equiv="x-content-security-policy"
                  content="default-src 'self'">
        </head>
        """
        features = parse_html(html)
        assert 'contentsecuritypolicy2' in features
        assert 'contentsecuritypolicy' in features


class TestCSPInCompleteDocument:
    """Tests for CSP in realistic document structures."""

    def test_csp_in_complete_head(self, parse_html):
        """Test CSP in complete document head."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="content-security-policy"
                  content="default-src 'self'; script-src 'self' https://cdn.example.com">
            <title>Secure Page</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <h1>Hello World</h1>
        </body>
        </html>
        """
        features = parse_html(html)
        assert 'contentsecuritypolicy2' in features

    def test_csp_with_other_security_features(self, parse_html):
        """Test CSP alongside other security features."""
        html = """
        <head>
            <meta http-equiv="content-security-policy"
                  content="default-src 'self'">
            <script src="https://cdn.example.com/lib.js"
                    integrity="sha384-..."
                    crossorigin="anonymous"></script>
            <a href="https://external.com" target="_blank" rel="noopener noreferrer">
                External
            </a>
        </head>
        """
        features = parse_html(html)
        assert 'contentsecuritypolicy2' in features
        assert 'subresource-integrity' in features
        assert 'cors' in features
        assert 'rel-noopener' in features


class TestCSPCaseInsensitivity:
    """Tests for case insensitivity of http-equiv values."""

    def test_csp_uppercase(self, parse_and_check):
        """Test Content-Security-Policy in uppercase."""
        html = '''
        <meta http-equiv="CONTENT-SECURITY-POLICY"
              content="default-src 'self'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_csp_mixed_case(self, parse_and_check):
        """Test Content-Security-Policy in mixed case."""
        html = '''
        <meta http-equiv="Content-Security-Policy"
              content="default-src 'self'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy2')

    def test_x_csp_uppercase(self, parse_and_check):
        """Test X-Content-Security-Policy in uppercase."""
        html = '''
        <meta http-equiv="X-CONTENT-SECURITY-POLICY"
              content="default-src 'self'">
        '''
        assert parse_and_check(html, 'contentsecuritypolicy')


class TestNoCSP:
    """Tests for pages without CSP meta tags."""

    def test_no_csp_meta(self, parse_html):
        """Test page without CSP meta tag."""
        html = """
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width">
            <title>No CSP</title>
        </head>
        """
        features = parse_html(html)
        assert 'contentsecuritypolicy2' not in features
        assert 'contentsecuritypolicy' not in features

    def test_other_http_equiv(self, parse_html):
        """Test other http-equiv values (not CSP)."""
        html = """
        <meta http-equiv="refresh" content="5;url=redirect.html">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        """
        features = parse_html(html)
        assert 'contentsecuritypolicy2' not in features
        assert 'contentsecuritypolicy' not in features
