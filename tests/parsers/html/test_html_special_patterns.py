"""Consolidated HTML special pattern detection tests.

Covers: responsive images (srcset), SVG patterns (svg-img, svg-fragment),
media patterns (media-fragments, webvtt, videotracks, audiotracks),
custom elements (custom-elementsv1, is attr, declarative-shadow-dom),
data attributes (dataset), and misc patterns (datauri, xhtml, meta-theme-color,
fieldset-disabled, viewport-units).
"""

import pytest


# ---------------------------------------------------------------------------
# Responsive images -> srcset
# ---------------------------------------------------------------------------

class TestResponsiveImages:

    @pytest.mark.parametrize("html", [
        '<img src="s.jpg" srcset="m.jpg 2x, l.jpg 3x" alt="t">',
        '<img src="s.jpg" srcset="s.jpg 320w, m.jpg 640w, l.jpg 1024w" alt="t">',
        '<img src="i.jpg" srcset="i.jpg 1x, i@2x.jpg 2x" alt="t">',
        '<picture><source srcset="i.webp" type="image/webp"><img src="i.jpg" alt="t"></picture>',
        '<img src="s.jpg" srcset="s.jpg 320w, l.jpg 1024w" sizes="(max-width:600px) 100vw, 50vw" alt="t">',
    ], ids=["density", "width-desc", "pixel-density", "picture-source", "with-sizes"])
    @pytest.mark.unit
    def test_srcset(self, parse_features, html):
        assert 'srcset' in parse_features(html)

    @pytest.mark.unit
    def test_picture_with_srcset(self, parse_features):
        html = """
        <picture>
            <source srcset="hero.avif" type="image/avif">
            <source srcset="hero.webp" type="image/webp">
            <img src="hero.jpg" alt="Hero">
        </picture>
        """
        features = parse_features(html)
        assert 'picture' in features
        assert 'srcset' in features

    @pytest.mark.unit
    def test_no_srcset(self, parse_features):
        assert 'srcset' not in parse_features('<img src="i.jpg" alt="t">')


# ---------------------------------------------------------------------------
# SVG patterns -> svg-img, svg-fragment
# ---------------------------------------------------------------------------

class TestSvgPatterns:

    @pytest.mark.parametrize("html", [
        '<img src="icon.svg" alt="Icon">',
        '<img src="/images/logo.svg" alt="Logo">',
        '<img src="https://example.com/i.svg" alt="Icon">',
        '<img src="icon.svg?v=1.2.3" alt="Icon">',
        '<img src="icon.SVG" alt="Icon">',
    ], ids=["basic", "path", "absolute-url", "query-string", "uppercase"])
    @pytest.mark.unit
    def test_svg_img(self, parse_features, html):
        assert 'svg-img' in parse_features(html)

    @pytest.mark.parametrize("html", [
        '<svg><use href="#icon-home"></use></svg>',
        '<svg><use xlink:href="#icon-menu"></use></svg>',
        '<svg><use href="icons.svg#home"></use></svg>',
        '<img src="sprites.svg#icon-user" alt="User">',
    ], ids=["href-hash", "xlink-hash", "external-hash", "img-fragment"])
    @pytest.mark.unit
    def test_svg_fragment(self, parse_features, html):
        assert 'svg-fragment' in parse_features(html)

    @pytest.mark.unit
    def test_svg_img_and_inline_svg(self, parse_features):
        html = """
        <img src="logo.svg" alt="Logo">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg>
        """
        features = parse_features(html)
        assert 'svg-img' in features
        assert 'svg' in features

    @pytest.mark.unit
    def test_svg_all_patterns(self, parse_features):
        html = """
        <img src="hero.svg" alt="Hero">
        <svg viewBox="0 0 100 100"><rect width="100" height="100"/></svg>
        <svg class="icon"><use href="icons.svg#menu"></use></svg>
        """
        features = parse_features(html)
        assert 'svg-img' in features
        assert 'svg' in features
        assert 'svg-fragment' in features

    @pytest.mark.unit
    def test_no_svg_img(self, parse_features):
        assert 'svg-img' not in parse_features('<img src="photo.jpg" alt="t">')

    @pytest.mark.unit
    def test_inline_svg_no_fragment(self, parse_features):
        html = '<svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5z"/></svg>'
        features = parse_features(html)
        assert 'svg' in features
        assert 'svg-fragment' not in features

    @pytest.mark.unit
    def test_svg_text_not_detected(self, parse_features):
        html = '<p>Download the file icon.svg from the server.</p>'
        assert 'svg-img' not in parse_features(html)

    @pytest.mark.unit
    def test_svg_favicon(self, parse_features):
        html = '<link rel="icon" type="image/svg+xml" href="favicon.svg">'
        assert 'link-icon-svg' in parse_features(html)


# ---------------------------------------------------------------------------
# Media patterns -> media-fragments, webvtt, videotracks, audiotracks
# ---------------------------------------------------------------------------

class TestMediaPatterns:

    @pytest.mark.parametrize("html", [
        '<video src="v.mp4#t=10,20"></video>',
        '<audio src="p.mp3#t=60"></audio>',
        '<video src="v.mp4#t=npt:10,20"></video>',
        '<video src="v.mp4#xywh=0,0,640,360"></video>',
        '<video src="v.mp4#id=chapter1"></video>',
        '<video><source src="v.mp4#t=5,30" type="video/mp4"></video>',
    ], ids=["video-time", "audio-time", "npt-format", "spatial", "id-frag", "source-frag"])
    @pytest.mark.unit
    def test_media_fragments(self, parse_features, html):
        assert 'media-fragments' in parse_features(html)

    @pytest.mark.unit
    def test_accessible_video(self, parse_features):
        """Fully accessible video with multiple track types."""
        html = """
        <video src="v.mp4" controls>
            <track kind="captions" src="c.vtt" srclang="en" default>
            <track kind="subtitles" src="s.vtt" srclang="es">
            <track kind="descriptions" src="d.vtt" srclang="en">
            <track kind="chapters" src="ch.vtt" srclang="en">
        </video>
        """
        features = parse_features(html)
        assert 'video' in features
        assert 'webvtt' in features
        assert 'videotracks' in features

    @pytest.mark.unit
    def test_video_with_fragment_and_tracks(self, parse_features):
        html = """
        <video src="v.mp4#t=10,60" controls>
            <track kind="captions" src="c.vtt">
        </video>
        """
        features = parse_features(html)
        assert 'media-fragments' in features
        assert 'webvtt' in features
        assert 'videotracks' in features

    @pytest.mark.unit
    def test_podcast_with_transcript(self, parse_features):
        html = """
        <audio src="ep42.mp3" controls>
            <track kind="captions" src="ep42-transcript.vtt" srclang="en">
        </audio>
        """
        features = parse_features(html)
        assert 'audio' in features
        assert 'webvtt' in features
        assert 'audiotracks' in features

    @pytest.mark.unit
    def test_no_media_patterns(self, parse_features):
        html = '<video src="v.mp4" controls></video>'
        features = parse_features(html)
        assert 'video' in features
        assert 'media-fragments' not in features
        assert 'webvtt' not in features
        assert 'videotracks' not in features


# ---------------------------------------------------------------------------
# Custom elements -> custom-elementsv1
# ---------------------------------------------------------------------------

class TestCustomElements:

    @pytest.mark.parametrize("html", [
        '<my-component></my-component>',
        '<my-card>Card content</my-card>',
        '<user-profile name="John"></user-profile>',
        '<app-container><app-header></app-header></app-container>',
        '<my-very-long-component-name></my-very-long-component-name>',
        '<my-icon/>',
        '<paper-button>Click me</paper-button>',
        '<sl-button>Click me</sl-button>',
        '<ion-app><ion-content>X</ion-content></ion-app>',
    ], ids=[
        "basic", "with-content", "with-attrs", "nested",
        "multi-hyphen", "self-closing", "polymer", "shoelace", "ionic",
    ])
    @pytest.mark.unit
    def test_custom_element(self, parse_features, html):
        assert 'custom-elementsv1' in parse_features(html)

    @pytest.mark.parametrize("html", [
        '<button is="fancy-button">Click me</button>',
        '<input is="enhanced-input" type="text">',
        '<div is="expandable-container">Content</div>',
    ])
    @pytest.mark.unit
    def test_is_attribute(self, parse_features, html):
        assert 'custom-elementsv1' in parse_features(html)

    @pytest.mark.unit
    def test_declarative_shadow_dom(self, parse_features):
        html = """
        <my-component>
            <template shadowrootmode="open">
                <style>:host { display: block; }</style>
                <slot></slot>
            </template>
        </my-component>
        """
        features = parse_features(html)
        assert 'custom-elementsv1' in features
        assert 'declarative-shadow-dom' in features

    @pytest.mark.unit
    def test_no_custom_element_standard_tags(self, parse_features):
        html = '<header>H</header><main>M</main><footer>F</footer>'
        assert 'custom-elementsv1' not in parse_features(html)

    @pytest.mark.unit
    def test_no_custom_element_no_hyphen(self, parse_features):
        html = '<mycomponent>Content</mycomponent>'
        assert 'custom-elementsv1' not in parse_features(html)


# ---------------------------------------------------------------------------
# Data attributes -> dataset
# ---------------------------------------------------------------------------

class TestDataAttributes:

    @pytest.mark.parametrize("html", [
        '<div data-id="123">Content</div>',
        '<div data-id="1" data-name="test" data-value="abc">X</div>',
        '<div data-empty="">Content</div>',
        '<div data-active>Content</div>',
        '<div data-user-id="123">Content</div>',
        '<div data-config=\'{"key":"val"}\'>X</div>',
    ], ids=["single", "multiple", "empty-val", "no-val", "hyphenated", "json-val"])
    @pytest.mark.unit
    def test_dataset(self, parse_features, html):
        assert 'dataset' in parse_features(html)

    @pytest.mark.unit
    def test_data_with_custom_element(self, parse_features):
        html = '<my-component data-config="{}"></my-component>'
        features = parse_features(html)
        assert 'dataset' in features
        assert 'custom-elementsv1' in features

    @pytest.mark.unit
    def test_no_dataset(self, parse_features):
        html = '<div id="main" class="container"><h1>Title</h1></div>'
        assert 'dataset' not in parse_features(html)

    @pytest.mark.unit
    def test_aria_not_data(self, parse_features):
        html = '<div aria-label="Label" aria-hidden="false">X</div>'
        features = parse_features(html)
        assert 'wai-aria' in features
        assert 'dataset' not in features


# ---------------------------------------------------------------------------
# Misc patterns -> datauri, xhtml, meta-theme-color, fieldset-disabled, viewport-units
# ---------------------------------------------------------------------------

class TestMiscPatterns:

    @pytest.mark.parametrize("html, feature_id", [
        ('<img src="data:image/png;base64,iVBOR..." alt="t">', 'datauri'),
        ('<img src="data:image/svg+xml,<svg>...</svg>" alt="t">', 'datauri'),
        ('<a href="data:text/html,<h1>Hi</h1>" target="_blank">Open</a>', 'datauri'),
        ('<html xmlns="http://www.w3.org/1999/xhtml"><body></body></html>', 'xhtml'),
        ('<meta name="theme-color" content="#4285f4">', 'meta-theme-color'),
        ('<meta name="theme-color" content="#fff" media="(prefers-color-scheme: light)">', 'meta-theme-color'),
        ('<meta name="viewport" content="width=device-width, initial-scale=1.0">', 'viewport-units'),
        ('<meta name="viewport" content="width=device-width">', 'viewport-units'),
        ('<fieldset disabled><input type="text"></fieldset>', 'fieldset-disabled'),
        ('<fieldset disabled="disabled"><input></fieldset>', 'fieldset-disabled'),
    ], ids=[
        "datauri-base64", "datauri-svg", "datauri-href",
        "xhtml-ns",
        "theme-color-hex", "theme-color-media",
        "viewport-full", "viewport-simple",
        "fieldset-disabled-bool", "fieldset-disabled-val",
    ])
    @pytest.mark.unit
    def test_misc_pattern(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)

    @pytest.mark.unit
    def test_pwa_head(self, parse_features):
        html = """
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="theme-color" content="#4285f4">
            <link rel="icon" type="image/svg+xml" href="icon.svg">
        </head>
        """
        features = parse_features(html)
        assert 'viewport-units' in features
        assert 'meta-theme-color' in features
        assert 'link-icon-svg' in features

    @pytest.mark.unit
    def test_no_misc_patterns(self, parse_features):
        html = '<!DOCTYPE html><html><head><title>Basic</title></head><body><p>Hello</p></body></html>'
        features = parse_features(html)
        assert 'datauri' not in features
        assert 'xhtml' not in features
        assert 'meta-theme-color' not in features
        assert 'fieldset-disabled' not in features

    @pytest.mark.unit
    def test_no_xhtml(self, parse_features):
        assert 'xhtml' not in parse_features('<html><body></body></html>')

    @pytest.mark.unit
    def test_fieldset_not_disabled(self, parse_features):
        html = '<fieldset><legend>Active</legend><input></fieldset>'
        assert 'fieldset-disabled' not in parse_features(html)
