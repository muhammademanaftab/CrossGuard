"""False positive prevention tests.

Verifies that features mentioned inside comments and strings
are NOT detected when using tree-sitter AST.
"""

import pytest
from src.parsers.js_parser import _TREE_SITTER_AVAILABLE


@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositiveComments:
    """Features inside comments should not be detected."""

    def test_feature_in_single_line_comment(self, parse_and_check_not):
        js = """
        // We might use navigator.bluetooth later
        var x = 1;
        """
        assert parse_and_check_not(js, 'web-bluetooth')

    def test_feature_in_multi_line_comment(self, parse_and_check_not):
        js = """
        /*
         * TODO: add navigator.geolocation support
         * navigator.clipboard.writeText
         */
        var x = 1;
        """
        assert parse_and_check_not(js, 'geolocation')

    def test_api_in_block_comment(self, parse_and_check_not):
        js = """
        /* new WebSocket('ws://host') */
        var x = 1;
        """
        assert parse_and_check_not(js, 'websockets')

    def test_fetch_in_comment(self, parse_and_check_not):
        js = """
        // fetch('/api/data')
        var x = 1;
        """
        assert parse_and_check_not(js, 'fetch')


@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositiveStrings:
    """Features inside string literals should not be detected."""

    def test_api_in_string(self, parse_and_check_not):
        js = '''const msg = "navigator.bluetooth is not supported";'''
        assert parse_and_check_not(js, 'web-bluetooth')

    def test_api_in_single_quote_string(self, parse_and_check_not):
        js = "const msg = 'WebSocket connection failed';"
        assert parse_and_check_not(js, 'websockets')

    def test_constructor_in_string(self, parse_and_check_not):
        js = '''const msg = "Use new IntersectionObserver for lazy loading";'''
        assert parse_and_check_not(js, 'intersectionobserver')

    def test_navigator_in_template_text(self, parse_and_check_not):
        js = "const msg = `navigator.gpu is ${status}`;"
        assert parse_and_check_not(js, 'webgpu')


@pytest.mark.skipif(not _TREE_SITTER_AVAILABLE, reason="tree-sitter not available")
class TestFalsePositiveMixed:
    """Mixed scenarios with real code and strings/comments."""

    def test_real_fetch_not_string_fetch(self, parse_js):
        js = '''
        const label = "fetch data from server";
        fetch('/api/real');
        '''
        features = parse_js(js)
        assert 'fetch' in features  # Real fetch is detected

    def test_comment_doesnt_mask_real_code(self, parse_js):
        js = '''
        // This uses Proxy
        const p = new Proxy(target, handler);
        '''
        features = parse_js(js)
        assert 'proxy' in features  # Real Proxy is detected

    def test_multiple_false_positives(self, parse_and_check_not):
        js = '''
        // navigator.bluetooth, navigator.serial, navigator.usb
        /* SharedArrayBuffer, WebTransport, WebGPU */
        const msg = "We support ReadableStream and WritableStream";
        var x = 1;
        '''
        assert parse_and_check_not(js, 'web-bluetooth')
        assert parse_and_check_not(js, 'web-serial')
        assert parse_and_check_not(js, 'webusb')
