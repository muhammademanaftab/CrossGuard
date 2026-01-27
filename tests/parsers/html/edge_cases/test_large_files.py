"""Tests for large file and performance handling.

Tests: Large content, deeply nested structures, many elements
"""

import pytest


class TestLargeContent:
    """Tests for large content handling."""

    def test_large_text_content(self, parse_html):
        """Test large text content."""
        large_text = "Lorem ipsum " * 10000
        html = f"<main>{large_text}</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_many_paragraphs(self, parse_html):
        """Test document with many paragraphs."""
        paragraphs = "<p>Paragraph content here.</p>" * 1000
        html = f"<main>{paragraphs}</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_large_attribute_value(self, parse_html):
        """Test large attribute value."""
        large_value = "x" * 10000
        html = f'<div data-content="{large_value}">Content</div>'
        features = parse_html(html)
        assert 'dataset' in features


class TestManyElements:
    """Tests for documents with many elements."""

    def test_1000_div_elements(self, parse_html):
        """Test 1000 div elements."""
        divs = "<div>Content</div>" * 1000
        html = f"<body>{divs}</body>"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_many_semantic_elements(self, parse_html):
        """Test many semantic elements."""
        articles = """
        <article>
            <header><h2>Title</h2></header>
            <section><p>Content</p></section>
            <footer><time>2024-01-01</time></footer>
        </article>
        """ * 100
        html = f"<main>{articles}</main>"
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_many_input_elements(self, parse_html):
        """Test many input elements."""
        inputs = """
        <input type="text" placeholder="Name">
        <input type="email" required>
        <input type="date">
        <input type="number" min="0" max="100">
        """ * 100
        html = f"<form>{inputs}</form>"
        features = parse_html(html)
        assert 'input-placeholder' in features
        assert 'form-validation' in features
        assert 'input-datetime' in features
        assert 'input-number' in features

    def test_many_different_features(self, parse_html):
        """Test document with many different features."""
        html = """
        <main>
            <video src="v.mp4"></video>
            <audio src="a.mp3"></audio>
            <canvas></canvas>
            <dialog></dialog>
            <details><summary>S</summary></details>
            <meter value="0.5"></meter>
            <progress value="50" max="100"></progress>
        </main>
        """ * 50
        features = parse_html(html)
        assert 'video' in features
        assert 'audio' in features
        assert 'canvas' in features
        assert 'dialog' in features
        assert 'details' in features
        assert 'meter' in features
        assert 'progress' in features


class TestDeeplyNested:
    """Tests for deeply nested structures."""

    def test_deeply_nested_divs(self, parse_html):
        """Test deeply nested div elements."""
        depth = 100
        open_tags = "<div>" * depth
        close_tags = "</div>" * depth
        html = f"{open_tags}Content{close_tags}"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_deeply_nested_semantic(self, parse_html):
        """Test deeply nested semantic elements."""
        html = """
        <main>
            <article>
                <section>
                    <figure>
                        <figcaption>
                            <time>2024-01-01</time>
                        </figcaption>
                    </figure>
                </section>
            </article>
        </main>
        """ * 20
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_nested_lists(self, parse_html):
        """Test deeply nested lists."""
        depth = 50
        html = "<ul>" + "<li><ul>" * depth + "<li>Item</li>" + "</ul></li>" * depth + "</ul>"
        features = parse_html(html)
        assert isinstance(features, set)

    def test_nested_tables(self, parse_html):
        """Test nested tables."""
        html = """
        <table>
            <tr><td>
                <table>
                    <tr><td>
                        <table>
                            <tr><td>Deep</td></tr>
                        </table>
                    </td></tr>
                </table>
            </td></tr>
        </table>
        """ * 10
        features = parse_html(html)
        assert isinstance(features, set)


class TestComplexDocuments:
    """Tests for complex document structures."""

    def test_complex_form(self, parse_html):
        """Test complex form with many fields."""
        fields = """
        <fieldset>
            <legend>Section</legend>
            <label>Name: <input type="text" required minlength="2" maxlength="50"></label>
            <label>Email: <input type="email" required autocomplete="email"></label>
            <label>Phone: <input type="tel" pattern="[0-9]{10}"></label>
            <label>Date: <input type="date" min="2024-01-01"></label>
            <label>Color: <input type="color"></label>
            <label>Range: <input type="range" min="0" max="100"></label>
            <label>File: <input type="file" accept="image/*" multiple></label>
        </fieldset>
        """ * 10
        html = f"<form>{fields}</form>"
        features = parse_html(html)
        assert 'form-validation' in features
        assert 'input-email-tel-url' in features
        assert 'input-datetime' in features
        assert 'input-color' in features
        assert 'input-range' in features
        assert 'input-file-accept' in features

    def test_complex_media_page(self, parse_html):
        """Test page with many media elements."""
        media = """
        <figure>
            <video poster="poster.jpg">
                <source src="video.webm" type="video/webm">
                <source src="video.mp4" type="video/mp4">
                <track kind="captions" src="captions.vtt" srclang="en">
            </video>
            <figcaption>Video caption</figcaption>
        </figure>
        <figure>
            <picture>
                <source srcset="image.avif" type="image/avif">
                <source srcset="image.webp" type="image/webp">
                <img src="image.jpg" srcset="image-2x.jpg 2x" loading="lazy" alt="Image">
            </picture>
            <figcaption>Image caption</figcaption>
        </figure>
        """ * 20
        html = f"<main>{media}</main>"
        features = parse_html(html)
        assert 'video' in features
        assert 'webm' in features
        assert 'picture' in features
        assert 'webvtt' in features
        assert 'srcset' in features
        assert 'loading-lazy-attr' in features

    def test_complex_accessible_page(self, parse_html):
        """Test page with many ARIA attributes."""
        accessible = """
        <nav aria-label="Main navigation">
            <ul role="menubar">
                <li role="none">
                    <a role="menuitem" href="/" aria-current="page">Home</a>
                </li>
                <li role="none">
                    <button role="menuitem" aria-haspopup="true" aria-expanded="false">
                        Menu
                    </button>
                </li>
            </ul>
        </nav>
        <main aria-labelledby="page-title">
            <h1 id="page-title">Page Title</h1>
            <div role="region" aria-live="polite">Live content</div>
        </main>
        """ * 10
        html = f"<body>{accessible}</body>"
        features = parse_html(html)
        assert 'wai-aria' in features


class TestPerformanceEdgeCases:
    """Tests for performance edge cases."""

    def test_repeated_same_feature(self, parse_html):
        """Test many repetitions of same feature."""
        # Should not cause issues even with many of the same element
        html = "<main></main>" * 1000
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_many_unique_data_attributes(self, parse_html):
        """Test many unique data attributes."""
        attrs = " ".join([f'data-attr{i}="value{i}"' for i in range(100)])
        html = f'<div {attrs}>Content</div>'
        features = parse_html(html)
        assert 'dataset' in features

    def test_wide_document(self, parse_html):
        """Test wide document (many siblings)."""
        siblings = "".join([
            f'<section id="s{i}"><h2>Section {i}</h2><p>Content</p></section>'
            for i in range(200)
        ])
        html = f"<main>{siblings}</main>"
        features = parse_html(html)
        assert 'html5semantic' in features
