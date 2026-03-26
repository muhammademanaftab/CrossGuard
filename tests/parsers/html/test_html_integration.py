"""HTML parser integration tests.

File I/O, real-world multi-feature scenarios, reports, statistics,
and complex parsing scenarios.
"""

import pytest


# =====================================================================
# File Operations
# =====================================================================

@pytest.mark.integration
class TestParseFile:
    def test_returns_set(self, html_parser, create_html_file):
        filepath = create_html_file("<main>Content</main>")
        assert isinstance(html_parser.parse_file(str(filepath)), set)

    def test_finds_features(self, html_parser, create_html_file):
        filepath = create_html_file("<main><video src='v.mp4'></video></main>")
        features = html_parser.parse_file(str(filepath))
        assert "html5semantic" in features
        assert "video" in features

    def test_empty_file(self, html_parser, create_html_file):
        assert html_parser.parse_file(str(create_html_file(""))) == set()

    def test_file_not_found(self, html_parser):
        with pytest.raises(FileNotFoundError):
            html_parser.parse_file("/nonexistent/path/to/file.html")

    def test_utf8_with_bom(self, html_parser, temp_dir):
        filepath = temp_dir / "bom.html"
        filepath.write_text("\ufeff<main>Content with BOM</main>", encoding="utf-8")
        assert "html5semantic" in html_parser.parse_file(str(filepath))

    def test_path_with_spaces(self, html_parser, temp_dir):
        spaced_dir = temp_dir / "path with spaces"
        spaced_dir.mkdir()
        filepath = spaced_dir / "test file.html"
        filepath.write_text("<main>Content</main>", encoding="utf-8")
        assert "html5semantic" in html_parser.parse_file(str(filepath))


@pytest.mark.integration
class TestParseMultipleFiles:
    def test_combines_features(self, html_parser, create_temp_file):
        f1 = create_temp_file("f1.html", "<video src='v.mp4'></video>")
        f2 = create_temp_file("f2.html", "<audio src='a.mp3'></audio>")
        f3 = create_temp_file("f3.html", "<canvas></canvas>")
        result = html_parser.parse_multiple_files([str(f1), str(f2), str(f3)])
        assert "video" in result
        assert "audio" in result
        assert "canvas" in result

    def test_empty_list(self, html_parser):
        assert html_parser.parse_multiple_files([]) == set()

    def test_continues_after_missing_file(self, html_parser, create_html_file):
        valid = create_html_file("<main>Valid</main>")
        result = html_parser.parse_multiple_files([str(valid), "/nonexistent/file.html"])
        assert "html5semantic" in result

    def test_project_files(self, html_parser, temp_dir):
        (temp_dir / "pages").mkdir()
        index = temp_dir / "pages" / "index.html"
        index.write_text('<html><body><main><video src="hero.mp4"></video></main></body></html>', encoding="utf-8")
        component = temp_dir / "dialog.html"
        component.write_text("<dialog><slot></slot></dialog>", encoding="utf-8")
        result = html_parser.parse_multiple_files([str(index), str(component)])
        assert "video" in result
        assert "dialog" in result
        assert "shadowdomv1" in result


@pytest.mark.integration
class TestConvenienceFileFunction:
    def test_parse_html_file(self, create_html_file):
        from src.parsers.html_parser import parse_html_file
        assert "video" in parse_html_file(str(create_html_file("<video src='v.mp4'></video>")))

    def test_file_not_found(self):
        from src.parsers.html_parser import parse_html_file
        with pytest.raises(FileNotFoundError):
            parse_html_file("/nonexistent/file.html")


# =====================================================================
# Reports & Statistics
# =====================================================================

@pytest.mark.integration
class TestDetailedReport:
    def test_has_required_keys(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        report = html_parser.get_detailed_report()
        for key in ("total_features", "features", "elements_found", "attributes_found", "unrecognized"):
            assert key in report

    def test_empty_report(self, html_parser):
        html_parser.parse_string("")
        report = html_parser.get_detailed_report()
        assert report["total_features"] == 0

    def test_feature_count(self, html_parser):
        html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert html_parser.get_detailed_report()["total_features"] == 2

    def test_features_sorted(self, html_parser):
        html_parser.parse_string("<main><video></video><audio></audio><canvas></canvas></main>")
        report = html_parser.get_detailed_report()
        assert report["features"] == sorted(report["features"])

    def test_report_reflects_last_parse(self, html_parser):
        html_parser.parse_string("<video></video>")
        html_parser.parse_string("<audio></audio>")
        report = html_parser.get_detailed_report()
        assert "audio" in report["features"]
        assert "video" not in report["features"]


@pytest.mark.integration
class TestStatistics:
    def test_has_required_keys(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        stats = html_parser.get_statistics()
        for key in ("total_features", "total_elements_detected", "features_list"):
            assert key in stats

    def test_empty_stats(self, html_parser):
        html_parser.parse_string("")
        assert html_parser.get_statistics()["total_features"] == 0

    def test_features_list_sorted(self, html_parser):
        html_parser.parse_string("<main><video></video><audio></audio></main>")
        stats = html_parser.get_statistics()
        assert stats["features_list"] == sorted(stats["features_list"])

    def test_report_and_stats_agree(self, html_parser):
        html_parser.parse_string("<main><video></video></main>")
        report = html_parser.get_detailed_report()
        stats = html_parser.get_statistics()
        assert report["total_features"] == stats["total_features"]


# =====================================================================
# Real-World Scenarios
# =====================================================================

@pytest.mark.integration
class TestRealWorldScenarios:
    def test_landing_page(self, parse_features):
        html = """
        <!DOCTYPE html><html lang="en"><head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="theme-color" content="#4285f4">
            <link rel="icon" type="image/svg+xml" href="favicon.svg">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preload" href="hero.jpg" as="image">
        </head><body>
            <header><nav aria-label="Main"><a href="/">Home</a></nav></header>
            <main>
                <picture>
                    <source srcset="hero.avif" type="image/avif">
                    <source srcset="hero.webp" type="image/webp">
                    <img src="hero.jpg" alt="Hero" loading="lazy">
                </picture>
                <video controls><source src="i.mp4" type="video/mp4">
                    <track kind="captions" src="c.vtt" srclang="en">
                </video>
            </main>
            <footer><a href="/privacy" rel="noopener">Privacy</a></footer>
        </body></html>
        """
        features = parse_features(html)
        assert "viewport-units" in features
        assert "meta-theme-color" in features
        assert "link-icon-svg" in features
        assert "html5semantic" in features
        assert "wai-aria" in features
        assert "picture" in features
        assert "avif" in features
        assert "webp" in features
        assert "loading-lazy-attr" in features
        assert "video" in features
        assert "webvtt" in features
        assert "rel-noopener" in features

    def test_spa_shell(self, parse_features):
        html = """
        <html><head>
            <meta http-equiv="content-security-policy" content="default-src 'self'">
            <script type="module" src="app.js" defer></script>
        </head><body>
            <my-app-shell>
                <nav slot="navigation" aria-label="Main"><a href="#/">Home</a></nav>
            </my-app-shell>
            <template id="t"><slot name="content"></slot></template>
            <dialog id="modal" aria-modal="true">
                <form method="dialog"><button>Close</button></form>
            </dialog>
        </body></html>
        """
        features = parse_features(html)
        assert "contentsecuritypolicy2" in features
        assert "es6-module" in features
        assert "custom-elementsv1" in features
        assert "shadowdomv1" in features
        assert "template" in features
        assert "dialog" in features
        assert "wai-aria" in features

    def test_checkout_form(self, parse_features):
        html = """
        <form id="checkout">
            <input type="email" required autocomplete="email" inputmode="email" placeholder="you@ex.com">
            <input type="tel" pattern="[0-9]{10}">
            <input type="text" required minlength="16" maxlength="16">
            <input type="month" required>
            <button type="submit">Pay</button>
        </form>
        """
        features = parse_features(html)
        assert "input-email-tel-url" in features
        assert "form-validation" in features
        assert "input-pattern" in features
        assert "input-placeholder" in features
        assert "input-minlength" in features
        assert "maxlength" in features
        assert "input-datetime" in features

    def test_video_gallery(self, parse_features):
        html = """
        <main>
            <video controls crossorigin="anonymous">
                <source src="f.webm" type="video/webm">
                <source src="f.mp4" type="video/mp4">
                <track kind="captions" src="en.vtt" srclang="en" default>
            </video>
            <img src="t.jpg" srcset="t.jpg 1x, t@2x.jpg 2x" loading="lazy" alt="V1">
            <audio controls>
                <source src="a.opus" type="audio/opus">
                <track kind="captions" src="transcript.vtt">
            </audio>
        </main>
        """
        features = parse_features(html)
        assert "video" in features
        assert "cors" in features
        assert "webm" in features
        assert "webvtt" in features
        assert "srcset" in features
        assert "loading-lazy-attr" in features
        assert "audio" in features
        assert "opus" in features

    def test_dashboard(self, parse_features):
        html = """
        <main>
            <meter min="0" max="100" value="45">45%</meter>
            <progress value="30" max="100">30%</progress>
            <canvas id="chart" width="800" height="400" aria-label="Chart" role="img"></canvas>
            <svg viewBox="0 0 400 200" aria-label="Pie" role="img">
                <circle cx="100" cy="100" r="80" fill="blue"/>
            </svg>
        </main>
        """
        features = parse_features(html)
        assert "meter" in features
        assert "progress" in features
        assert "canvas" in features
        assert "svg" in features
        assert "wai-aria" in features

    def test_full_page_all_rule_types(self, html_parser):
        html = """
        <!DOCTYPE html><html><head>
            <link rel="preload" href="s.css" as="style">
            <script type="module" src="app.js"></script>
        </head><body>
            <main>
                <video src="v.mp4"></video>
                <form>
                    <input type="date" required placeholder="Select date">
                    <input type="email" autocomplete="email">
                </form>
                <div contenteditable="true" role="textbox" aria-label="Editor">Edit</div>
            </main>
        </body></html>
        """
        features = html_parser.parse_string(html)
        assert "html5semantic" in features
        assert "video" in features
        assert "input-datetime" in features
        assert "form-validation" in features
        assert "contenteditable" in features
        assert "wai-aria" in features
        assert "link-rel-preload" in features
        assert "es6-module" in features


# =====================================================================
# Encoding & Large Files
# =====================================================================

@pytest.mark.integration
class TestEncoding:
    def test_unicode_content(self, parse_features):
        assert "html5semantic" in parse_features("<main>Hello, 世界! Привет мир!</main>")

    def test_emoji_content(self, parse_features):
        features = parse_features("<main>Hello 👋 World 🌍</main>")
        assert isinstance(features, set)
        assert len(features) > 0

    def test_html_entities(self, parse_features):
        assert "html5semantic" in parse_features("<main>&copy; 2024 &mdash; All &amp; reserved</main>")

    def test_unicode_in_media(self, parse_features):
        features = parse_features('<video src="视频.mp4"></video><audio src="音频.mp3"></audio>')
        assert "video" in features
        assert "audio" in features


@pytest.mark.integration
class TestLargeFiles:
    def test_large_text(self, parse_features):
        assert "html5semantic" in parse_features(f"<main>{'Lorem ipsum ' * 10000}</main>")

    def test_many_different_features(self, parse_features):
        html = """
        <main><video src="v.mp4"></video><audio src="a.mp3"></audio>
        <canvas></canvas><dialog></dialog><details><summary>S</summary></details>
        <meter value="0.5"></meter><progress value="50" max="100"></progress></main>
        """ * 50
        features = parse_features(html)
        for f in ("video", "audio", "canvas", "dialog", "details", "meter", "progress"):
            assert f in features

    def test_deeply_nested(self, parse_features):
        html = "<div>" * 100 + "Content" + "</div>" * 100
        assert isinstance(parse_features(html), set)
