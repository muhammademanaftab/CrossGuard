"""Tests for character encoding and special character handling.

Tests: Unicode characters, emojis, HTML entities, special characters
"""

import pytest


class TestUnicodeCharacters:
    """Tests for Unicode character handling."""

    def test_unicode_in_content(self, parse_html):
        """Test Unicode characters in content."""
        html = "<main>Hello, 世界! Привет мир!</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_unicode_in_attribute(self, parse_html):
        """Test Unicode characters in attribute value."""
        html = '<input placeholder="输入您的名字" type="text">'
        features = parse_html(html)
        assert 'input-placeholder' in features

    def test_unicode_in_data_attribute(self, parse_html):
        """Test Unicode in data attribute."""
        html = '<div data-label="日本語">Content</div>'
        features = parse_html(html)
        assert 'dataset' in features

    def test_arabic_text(self, parse_html):
        """Test Arabic text (RTL)."""
        html = "<main>مرحبا بالعالم</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_mixed_scripts(self, parse_html):
        """Test mixed scripts in same document."""
        html = """
        <main>
            <p>English text</p>
            <p>中文文本</p>
            <p>Текст на русском</p>
            <p>טקסט בעברית</p>
        </main>
        """
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_unicode_element_detection(self, parse_html):
        """Test that Unicode doesn't interfere with element detection."""
        html = """
        <video src="视频.mp4"></video>
        <audio src="音频.mp3"></audio>
        """
        features = parse_html(html)
        assert 'video' in features
        assert 'audio' in features


class TestEmojis:
    """Tests for emoji handling."""

    def test_emoji_in_content(self, parse_html):
        """Test emoji in content."""
        html = "<main>Hello 👋 World 🌍</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_emoji_in_attribute(self, parse_html):
        """Test emoji in attribute value."""
        html = '<input placeholder="Search 🔍" type="search">'
        features = parse_html(html)
        assert 'input-placeholder' in features
        assert 'input-search' in features

    def test_emoji_in_data_attribute(self, parse_html):
        """Test emoji in data attribute."""
        html = '<button data-icon="❤️">Like</button>'
        features = parse_html(html)
        assert 'dataset' in features

    def test_complex_emoji(self, parse_html):
        """Test complex emoji (skin tones, ZWJ sequences)."""
        html = "<main>Family: 👨‍👩‍👧‍👦 Waving: 👋🏽</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_emoji_flags(self, parse_html):
        """Test flag emoji."""
        html = "<main>Flags: 🇺🇸 🇬🇧 🇯🇵 🇩🇪</main>"
        features = parse_html(html)
        assert 'html5semantic' in features


class TestHTMLEntities:
    """Tests for HTML entity handling."""

    def test_named_entities(self, parse_html):
        """Test named HTML entities."""
        html = "<main>&copy; 2024 &mdash; All rights &amp; reserved</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_numeric_entities(self, parse_html):
        """Test numeric HTML entities."""
        html = "<main>&#169; &#8212; &#38;</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_hex_entities(self, parse_html):
        """Test hexadecimal HTML entities."""
        html = "<main>&#x00A9; &#x2014;</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_entities_in_attributes(self, parse_html):
        """Test HTML entities in attributes."""
        html = '<input placeholder="Search &amp; Find" type="search">'
        features = parse_html(html)
        assert 'input-placeholder' in features

    def test_lt_gt_entities(self, parse_html):
        """Test less than / greater than entities."""
        html = "<main>&lt;tag&gt; content &lt;/tag&gt;</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_nbsp_entity(self, parse_html):
        """Test non-breaking space entity."""
        html = "<main>Hello&nbsp;World</main>"
        features = parse_html(html)
        assert 'html5semantic' in features


class TestSpecialCharacters:
    """Tests for special character handling."""

    def test_angle_brackets_in_content(self, parse_html):
        """Test angle brackets in text content (escaped)."""
        html = "<main>Use &lt;main&gt; for main content</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_quotes_in_attributes(self, parse_html):
        """Test quotes within attribute values."""
        html = """<input placeholder='Enter "name"' type="text">"""
        features = parse_html(html)
        assert 'input-placeholder' in features

    def test_backslash(self, parse_html):
        """Test backslash in content."""
        html = "<main>Path: C:\\Users\\name</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_null_character(self, parse_html):
        """Test null character handling."""
        html = "<main>Before\x00After</main>"
        features = parse_html(html)
        # Should handle gracefully
        assert isinstance(features, set)

    def test_newlines_in_attributes(self, parse_html):
        """Test newlines within attribute values."""
        html = '''<input placeholder="Line 1
Line 2" type="text">'''
        features = parse_html(html)
        assert 'input-placeholder' in features


class TestBOM:
    """Tests for Byte Order Mark handling."""

    def test_utf8_bom(self, parse_html):
        """Test UTF-8 BOM at start of document."""
        html = "\ufeff<main>Content</main>"
        features = parse_html(html)
        assert 'html5semantic' in features


class TestEncodingDeclaration:
    """Tests for encoding declaration handling."""

    def test_meta_charset_utf8(self, parse_html):
        """Test meta charset UTF-8."""
        html = '<meta charset="UTF-8"><main>Content</main>'
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_meta_charset_other(self, parse_html):
        """Test meta charset with other encoding."""
        html = '<meta charset="ISO-8859-1"><main>Content</main>'
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_content_type_meta(self, parse_html):
        """Test old-style content-type meta."""
        html = '''
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <main>Content</main>
        '''
        features = parse_html(html)
        assert 'html5semantic' in features


class TestMixedEncodings:
    """Tests for mixed encoding scenarios."""

    def test_unicode_with_entities(self, parse_html):
        """Test Unicode mixed with HTML entities."""
        html = "<main>日本 &mdash; Japan &copy; 2024</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_emoji_with_entities(self, parse_html):
        """Test emoji mixed with HTML entities."""
        html = "<main>👋 Hello &amp; Welcome! 🎉</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_all_character_types(self, parse_html):
        """Test all character types together."""
        html = """
        <main data-value="Test 日本語 🎉 &amp; &lt;code&gt;">
            ASCII, Unicode: 中文, Emoji: 🌍, Entities: &copy;
        </main>
        """
        features = parse_html(html)
        assert 'html5semantic' in features
        assert 'dataset' in features
