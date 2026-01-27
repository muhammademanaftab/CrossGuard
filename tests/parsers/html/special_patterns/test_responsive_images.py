"""Tests for responsive image pattern detection.

Tests patterns: srcset, sizes, picture element with sources
"""

import pytest


class TestSrcsetAttribute:
    """Tests for srcset attribute detection."""

    def test_srcset_basic(self, parse_and_check):
        """Test basic srcset attribute."""
        html = '<img src="small.jpg" srcset="medium.jpg 2x, large.jpg 3x" alt="test">'
        assert parse_and_check(html, 'srcset')

    def test_srcset_width_descriptors(self, parse_and_check):
        """Test srcset with width descriptors."""
        html = '''
        <img src="small.jpg"
             srcset="small.jpg 320w, medium.jpg 640w, large.jpg 1024w"
             alt="test">
        '''
        assert parse_and_check(html, 'srcset')

    def test_srcset_pixel_density(self, parse_and_check):
        """Test srcset with pixel density descriptors."""
        html = '<img src="image.jpg" srcset="image.jpg 1x, image@2x.jpg 2x, image@3x.jpg 3x" alt="test">'
        assert parse_and_check(html, 'srcset')

    def test_srcset_on_source(self, parse_and_check):
        """Test srcset on source element."""
        html = '''
        <picture>
            <source srcset="image.webp" type="image/webp">
            <img src="image.jpg" alt="test">
        </picture>
        '''
        assert parse_and_check(html, 'srcset')

    def test_srcset_with_sizes(self, parse_html):
        """Test srcset with sizes attribute."""
        html = '''
        <img src="small.jpg"
             srcset="small.jpg 320w, medium.jpg 640w, large.jpg 1024w"
             sizes="(max-width: 320px) 280px, (max-width: 640px) 600px, 1000px"
             alt="test">
        '''
        features = parse_html(html)
        assert 'srcset' in features


class TestSizesAttribute:
    """Tests for sizes attribute detection."""

    def test_sizes_viewport_width(self, parse_and_check):
        """Test sizes with viewport width."""
        html = '''
        <img src="image.jpg"
             srcset="small.jpg 320w, medium.jpg 640w, large.jpg 1024w"
             sizes="100vw"
             alt="test">
        '''
        assert parse_and_check(html, 'srcset')

    def test_sizes_media_conditions(self, parse_and_check):
        """Test sizes with media conditions."""
        html = '''
        <img src="image.jpg"
             srcset="small.jpg 320w, medium.jpg 640w, large.jpg 1024w"
             sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 33vw"
             alt="test">
        '''
        assert parse_and_check(html, 'srcset')

    def test_sizes_fixed_width(self, parse_and_check):
        """Test sizes with fixed pixel width."""
        html = '''
        <img src="image.jpg"
             srcset="thumb.jpg 160w, small.jpg 320w"
             sizes="160px"
             alt="Thumbnail">
        '''
        assert parse_and_check(html, 'srcset')

    def test_sizes_calc(self, parse_and_check):
        """Test sizes with calc()."""
        html = '''
        <img src="image.jpg"
             srcset="small.jpg 320w, large.jpg 1024w"
             sizes="calc(100vw - 2rem)"
             alt="test">
        '''
        assert parse_and_check(html, 'srcset')


class TestPictureElement:
    """Tests for picture element pattern detection."""

    def test_picture_with_type_switching(self, parse_html):
        """Test picture element for format switching."""
        html = """
        <picture>
            <source srcset="image.avif" type="image/avif">
            <source srcset="image.webp" type="image/webp">
            <img src="image.jpg" alt="test">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features
        assert 'srcset' in features

    def test_picture_art_direction(self, parse_html):
        """Test picture element for art direction."""
        html = """
        <picture>
            <source media="(min-width: 1200px)" srcset="hero-wide.jpg">
            <source media="(min-width: 800px)" srcset="hero-medium.jpg">
            <source media="(min-width: 400px)" srcset="hero-narrow.jpg">
            <img src="hero-mobile.jpg" alt="Hero image">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features
        assert 'srcset' in features

    def test_picture_orientation(self, parse_html):
        """Test picture element for orientation-based switching."""
        html = """
        <picture>
            <source media="(orientation: portrait)" srcset="portrait.jpg">
            <source media="(orientation: landscape)" srcset="landscape.jpg">
            <img src="default.jpg" alt="Responsive to orientation">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features
        assert 'srcset' in features

    def test_picture_combined_conditions(self, parse_html):
        """Test picture with combined media and type."""
        html = """
        <picture>
            <source media="(min-width: 800px)"
                    srcset="large.avif"
                    type="image/avif">
            <source media="(min-width: 800px)"
                    srcset="large.webp"
                    type="image/webp">
            <source srcset="small.avif" type="image/avif">
            <source srcset="small.webp" type="image/webp">
            <img src="fallback.jpg" alt="test">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features
        assert 'srcset' in features


class TestResponsiveImagePatterns:
    """Tests for common responsive image patterns."""

    def test_hero_image_pattern(self, parse_html):
        """Test hero image with responsive pattern."""
        html = """
        <header>
            <picture>
                <source media="(min-width: 1400px)"
                        srcset="hero-2800.jpg 2800w, hero-1400.jpg 1400w"
                        sizes="100vw">
                <source media="(min-width: 800px)"
                        srcset="hero-1600.jpg 1600w, hero-800.jpg 800w"
                        sizes="100vw">
                <img src="hero-400.jpg"
                     srcset="hero-800.jpg 800w, hero-400.jpg 400w"
                     sizes="100vw"
                     alt="Hero image">
            </picture>
        </header>
        """
        features = parse_html(html)
        assert 'picture' in features
        assert 'srcset' in features

    def test_gallery_thumbnails(self, parse_html):
        """Test gallery thumbnails with srcset."""
        html = """
        <div class="gallery">
            <img src="thumb1.jpg" srcset="thumb1.jpg 1x, thumb1@2x.jpg 2x" alt="Image 1">
            <img src="thumb2.jpg" srcset="thumb2.jpg 1x, thumb2@2x.jpg 2x" alt="Image 2">
            <img src="thumb3.jpg" srcset="thumb3.jpg 1x, thumb3@2x.jpg 2x" alt="Image 3">
        </div>
        """
        features = parse_html(html)
        assert 'srcset' in features

    def test_article_images(self, parse_html):
        """Test article images with responsive srcset."""
        html = """
        <article>
            <figure>
                <img src="article-image.jpg"
                     srcset="article-image-400.jpg 400w,
                             article-image-800.jpg 800w,
                             article-image-1200.jpg 1200w"
                     sizes="(max-width: 800px) 100vw, 800px"
                     alt="Article illustration">
                <figcaption>Figure 1: Illustration</figcaption>
            </figure>
        </article>
        """
        features = parse_html(html)
        assert 'srcset' in features
        assert 'html5semantic' in features  # figure/figcaption

    def test_logo_retina(self, parse_html):
        """Test logo with retina support."""
        html = """
        <header>
            <img src="logo.png"
                 srcset="logo.png 1x, logo@2x.png 2x, logo@3x.png 3x"
                 alt="Company Logo"
                 width="200"
                 height="50">
        </header>
        """
        features = parse_html(html)
        assert 'srcset' in features


class TestNoResponsiveImages:
    """Tests for images without responsive features."""

    def test_basic_img(self, parse_html):
        """Test basic img without srcset."""
        html = '<img src="image.jpg" alt="test">'
        features = parse_html(html)
        assert 'srcset' not in features

    def test_picture_without_srcset(self, parse_html):
        """Test picture element without srcset on sources."""
        # Note: This is unusual but possible
        html = """
        <picture>
            <source src="image.webp" type="image/webp">
            <img src="image.jpg" alt="test">
        </picture>
        """
        features = parse_html(html)
        assert 'picture' in features
        # srcset might not be detected without srcset attribute
