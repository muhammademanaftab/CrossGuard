"""Consolidated HTML element detection tests.

Covers: semantic elements (html5semantic), interactive elements (dialog, details, template),
form elements (datalist, meter, progress), media elements (video, audio, picture, track),
and special elements (canvas, svg, slot, wbr, ruby, menu, portal, math).
"""

import pytest


# ---------------------------------------------------------------------------
# Semantic elements -> html5semantic
# ---------------------------------------------------------------------------

class TestSemanticElements:
    """All semantic elements map to html5semantic."""

    @pytest.mark.parametrize("html", [
        "<main>Content</main>",
        "<section>Content</section>",
        "<article>Blog post</article>",
        "<aside>Sidebar</aside>",
        "<header>Header</header>",
        "<footer>Footer</footer>",
        "<nav><a href='/'>Home</a></nav>",
        "<figure><img src='i.jpg' alt='t'></figure>",
        "<figure><figcaption>Caption</figcaption></figure>",
        "<time datetime='2024-01-15'>Jan 15</time>",
        "<p><mark>highlighted</mark></p>",
    ], ids=[
        "main", "section", "article", "aside", "header", "footer",
        "nav", "figure", "figcaption", "time", "mark",
    ])
    @pytest.mark.unit
    def test_semantic_element(self, parse_features, html):
        assert 'html5semantic' in parse_features(html)

    @pytest.mark.unit
    def test_full_page_structure(self, parse_features):
        """All semantic elements in a complete page."""
        html = """
        <header><nav><a href="/">Home</a></nav></header>
        <main>
            <article>
                <header><h1>Title</h1><time datetime="2024">2024</time></header>
                <section><p>Text with <mark>highlight</mark></p>
                    <figure><img src="i.jpg" alt="t"><figcaption>Cap</figcaption></figure>
                </section>
            </article>
            <aside><h2>Related</h2></aside>
        </main>
        <footer><p>Copyright</p></footer>
        """
        assert 'html5semantic' in parse_features(html)

    @pytest.mark.unit
    def test_no_semantic_elements(self, parse_features):
        html = '<div class="header"><div class="content">Hi</div></div>'
        assert 'html5semantic' not in parse_features(html)


# ---------------------------------------------------------------------------
# Interactive elements
# ---------------------------------------------------------------------------

class TestDialogElement:

    @pytest.mark.parametrize("html", [
        "<dialog>Content</dialog>",
        "<dialog open>Visible</dialog>",
        "<dialog><form method='dialog'><button>OK</button></form></dialog>",
    ])
    @pytest.mark.unit
    def test_dialog(self, parse_features, html):
        assert 'dialog' in parse_features(html)


class TestDetailsElement:

    @pytest.mark.parametrize("html", [
        "<details>Content</details>",
        "<details><summary>Expand</summary><p>Body</p></details>",
        "<details open><summary>Open</summary><p>Visible</p></details>",
        "<details><details><summary>Nested</summary></details></details>",
    ])
    @pytest.mark.unit
    def test_details(self, parse_features, html):
        assert 'details' in parse_features(html)

    @pytest.mark.unit
    def test_summary_maps_to_details(self, parse_features):
        html = "<details><summary>Summary text</summary></details>"
        assert 'details' in parse_features(html)


class TestTemplateElement:

    @pytest.mark.parametrize("html", [
        "<template>Template content</template>",
        "<template id='t'><div class='card'><h2>T</h2></div></template>",
    ])
    @pytest.mark.unit
    def test_template(self, parse_features, html):
        assert 'template' in parse_features(html)

    @pytest.mark.unit
    def test_template_with_slot_detects_shadowdom(self, parse_features):
        html = """
        <template id="t">
            <slot name="user">Default</slot>
        </template>
        """
        features = parse_features(html)
        assert 'template' in features
        assert 'shadowdomv1' in features

    @pytest.mark.unit
    def test_no_interactive_elements(self, parse_features):
        html = "<div><p>Text</p><button>Click</button></div>"
        features = parse_features(html)
        assert 'dialog' not in features
        assert 'details' not in features
        assert 'template' not in features


# ---------------------------------------------------------------------------
# Form elements
# ---------------------------------------------------------------------------

class TestDatalistElement:

    @pytest.mark.parametrize("html", [
        '<datalist id="b"><option value="Chrome"></datalist>',
        '<input list="b"><datalist id="b"><option value="Chrome"></datalist>',
        '<datalist id="e"></datalist>',
    ])
    @pytest.mark.unit
    def test_datalist(self, parse_features, html):
        assert 'datalist' in parse_features(html)


class TestMeterElement:

    @pytest.mark.parametrize("html", [
        '<meter value="0.6">60%</meter>',
        '<meter min="0" max="100" value="75">75%</meter>',
        '<meter min="0" max="100" low="25" high="75" optimum="50" value="80">80%</meter>',
    ])
    @pytest.mark.unit
    def test_meter(self, parse_features, html):
        assert 'meter' in parse_features(html)


class TestProgressElement:

    @pytest.mark.parametrize("html", [
        '<progress value="70" max="100">70%</progress>',
        '<progress>Loading...</progress>',
    ])
    @pytest.mark.unit
    def test_progress(self, parse_features, html):
        assert 'progress' in parse_features(html)

    @pytest.mark.unit
    def test_meter_vs_progress_no_cross(self, parse_features):
        assert 'progress' not in parse_features('<meter value="0.5">50%</meter>')
        assert 'meter' not in parse_features('<progress value="50" max="100">50%</progress>')

    @pytest.mark.unit
    def test_no_form_elements(self, parse_features):
        html = '<form><input type="text"><button>Go</button></form>'
        features = parse_features(html)
        assert 'datalist' not in features
        assert 'meter' not in features
        assert 'progress' not in features


# ---------------------------------------------------------------------------
# Media elements
# ---------------------------------------------------------------------------

class TestVideoElement:

    @pytest.mark.parametrize("html", [
        '<video src="v.mp4"></video>',
        '<video><source src="v.mp4" type="video/mp4"></video>',
        '<video src="v.mp4" controls autoplay loop muted></video>',
    ])
    @pytest.mark.unit
    def test_video(self, parse_features, html):
        assert 'video' in parse_features(html)


class TestAudioElement:

    @pytest.mark.parametrize("html", [
        '<audio src="a.mp3"></audio>',
        '<audio><source src="a.mp3" type="audio/mpeg"></audio>',
        '<audio src="a.mp3" controls autoplay loop muted></audio>',
    ])
    @pytest.mark.unit
    def test_audio(self, parse_features, html):
        assert 'audio' in parse_features(html)


class TestPictureElement:

    @pytest.mark.parametrize("html", [
        '<picture><img src="f.jpg" alt="t"></picture>',
        '<picture><source srcset="i.webp" type="image/webp"><img src="i.jpg" alt="t"></picture>',
        '<picture><source media="(min-width:800px)" srcset="l.jpg"><img src="s.jpg" alt="t"></picture>',
    ])
    @pytest.mark.unit
    def test_picture(self, parse_features, html):
        assert 'picture' in parse_features(html)


class TestSourceFalsePositives:
    """CRITICAL: <source> inside <video>/<audio> must NOT trigger picture."""

    @pytest.mark.unit
    def test_source_in_video_no_picture(self, parse_features):
        html = '<video><source src="v.mp4" type="video/mp4"></video>'
        features = parse_features(html)
        assert 'video' in features
        assert 'picture' not in features

    @pytest.mark.unit
    def test_source_in_audio_no_picture(self, parse_features):
        html = '<audio><source src="a.mp3" type="audio/mpeg"></audio>'
        features = parse_features(html)
        assert 'audio' in features
        assert 'picture' not in features

    @pytest.mark.unit
    def test_video_multiple_sources_no_picture(self, parse_features):
        html = """
        <video controls>
            <source src="v.webm" type="video/webm">
            <source src="v.mp4" type="video/mp4">
            <source src="v.ogv" type="video/ogg">
        </video>
        """
        features = parse_features(html)
        assert 'video' in features
        assert 'picture' not in features


class TestTrackElement:

    @pytest.mark.parametrize("html", [
        '<video><track src="c.vtt" kind="captions" srclang="en"></video>',
        '<video><track kind="subtitles" src="s.vtt" srclang="es"></video>',
        '<video><track kind="chapters" src="ch.vtt"></video>',
        '<audio><track kind="captions" src="t.vtt"></audio>',
    ])
    @pytest.mark.unit
    def test_track_detects_webvtt(self, parse_features, html):
        assert 'webvtt' in parse_features(html)

    @pytest.mark.unit
    def test_video_with_track_detects_videotracks(self, parse_features):
        html = '<video src="m.mp4"><track kind="captions" src="c.vtt"></video>'
        features = parse_features(html)
        assert 'videotracks' in features

    @pytest.mark.unit
    def test_video_without_track_no_videotracks(self, parse_features):
        assert 'videotracks' not in parse_features('<video src="m.mp4"></video>')

    @pytest.mark.unit
    def test_audio_with_track_detects_audiotracks(self, parse_features):
        html = '<audio src="p.mp3"><track kind="captions" src="t.vtt"></audio>'
        assert 'audiotracks' in parse_features(html)

    @pytest.mark.unit
    def test_audio_without_track_no_audiotracks(self, parse_features):
        assert 'audiotracks' not in parse_features('<audio src="a.mp3"></audio>')


class TestCombinedMedia:

    @pytest.mark.unit
    def test_all_media(self, parse_features):
        html = """
        <video src="v.mp4" controls></video>
        <audio src="a.mp3" controls></audio>
        <picture><source srcset="i.webp" type="image/webp"><img src="i.jpg" alt="t"></picture>
        """
        features = parse_features(html)
        assert 'video' in features
        assert 'audio' in features
        assert 'picture' in features

    @pytest.mark.unit
    def test_video_sources_and_tracks(self, parse_features):
        html = """
        <video poster="p.jpg" controls>
            <source src="v.webm" type="video/webm">
            <source src="v.mp4" type="video/mp4">
            <track kind="captions" src="en.vtt" srclang="en" default>
            <track kind="captions" src="es.vtt" srclang="es">
        </video>
        """
        features = parse_features(html)
        assert 'video' in features
        assert 'webvtt' in features
        assert 'videotracks' in features

    @pytest.mark.unit
    def test_no_media(self, parse_features):
        html = '<div><p>No media</p><img src="i.jpg" alt="Just img"></div>'
        features = parse_features(html)
        assert 'video' not in features
        assert 'audio' not in features
        assert 'picture' not in features


# ---------------------------------------------------------------------------
# Special elements
# ---------------------------------------------------------------------------

class TestCanvasElement:

    @pytest.mark.parametrize("html", [
        "<canvas></canvas>",
        '<canvas width="500" height="300"></canvas>',
        '<canvas id="chart">Fallback text</canvas>',
    ])
    @pytest.mark.unit
    def test_canvas(self, parse_features, html):
        assert 'canvas' in parse_features(html)


class TestSvgElement:

    @pytest.mark.parametrize("html", [
        "<svg></svg>",
        '<svg viewBox="0 0 100 100"></svg>',
        '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>',
    ])
    @pytest.mark.unit
    def test_svg(self, parse_features, html):
        assert 'svg' in parse_features(html)


class TestSlotElement:

    @pytest.mark.parametrize("html", [
        "<template><slot></slot></template>",
        '<template><slot name="content"></slot></template>',
    ])
    @pytest.mark.unit
    def test_slot_detects_shadowdomv1(self, parse_features, html):
        assert 'shadowdomv1' in parse_features(html)


class TestOtherSpecialElements:

    @pytest.mark.parametrize("html, feature_id", [
        ("<p>long<wbr>word</p>", "wbr-element"),
        ("<ruby>漢<rt>kan</rt></ruby>", "ruby"),
        ("<ruby>漢<rp>(</rp><rt>kan</rt><rp>)</rp></ruby>", "ruby"),
        ("<math><mi>x</mi><mo>=</mo><mn>1</mn></math>", "mathml"),
    ])
    @pytest.mark.unit
    def test_special_element(self, parse_features, html, feature_id):
        assert feature_id in parse_features(html)
