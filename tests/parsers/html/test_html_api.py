"""Consolidated HTML parser API and integration tests.

Covers: parse_string, parse_file, parse_multiple_files, validate_html,
get_detailed_report, get_statistics, convenience functions,
custom rules integration, and real-world HTML integration tests.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch


# ---------------------------------------------------------------------------
# parse_string API
# ---------------------------------------------------------------------------

class TestParseString:

    @pytest.mark.unit
    def test_returns_set(self, html_parser):
        assert isinstance(html_parser.parse_string("<div>Content</div>"), set)

    @pytest.mark.unit
    def test_empty_returns_empty_set(self, html_parser):
        assert html_parser.parse_string("") == set()

    @pytest.mark.unit
    def test_finds_features(self, html_parser):
        features = html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert 'html5semantic' in features
        assert 'video' in features

    @pytest.mark.unit
    def test_return_contains_strings(self, html_parser):
        result = html_parser.parse_string("<main>Content</main>")
        for feature in result:
            assert isinstance(feature, str)

    @pytest.mark.unit
    def test_return_matches_features_found(self, html_parser):
        result = html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        assert result == html_parser.features_found

    @pytest.mark.unit
    def test_no_duplicates(self, html_parser):
        result = html_parser.parse_string("<main></main><main></main><main></main>")
        assert sum(1 for f in result if f == 'html5semantic') == 1

    @pytest.mark.unit
    def test_state_updated(self, html_parser):
        html_parser.parse_string("<video src='v.mp4'></video>")
        assert 'video' in html_parser.features_found
        assert any(e['element'] == 'video' for e in html_parser.elements_found)

    @pytest.mark.unit
    def test_attributes_found_updated(self, html_parser):
        html_parser.parse_string('<input placeholder="test">')
        assert any(a['attribute'] == 'placeholder' for a in html_parser.attributes_found)


class TestParseHtmlStringConvenience:

    @pytest.mark.unit
    def test_exists(self):
        from src.parsers.html_parser import parse_html_string
        assert callable(parse_html_string)

    @pytest.mark.unit
    def test_works(self):
        from src.parsers.html_parser import parse_html_string
        result = parse_html_string("<main>Content</main>")
        assert isinstance(result, set)
        assert 'html5semantic' in result


# ---------------------------------------------------------------------------
# parse_file API
# ---------------------------------------------------------------------------

class TestParseFile:

    @pytest.mark.unit
    def test_returns_set(self, html_parser, create_html_file):
        filepath = create_html_file("<main>Content</main>")
        result = html_parser.parse_file(str(filepath))
        assert isinstance(result, set)

    @pytest.mark.unit
    def test_finds_features(self, html_parser, create_html_file):
        filepath = create_html_file("<main><video src='v.mp4'></video></main>")
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features
        assert 'video' in features

    @pytest.mark.unit
    def test_with_path_object(self, html_parser, create_html_file):
        filepath = create_html_file("<dialog>Content</dialog>")
        features = html_parser.parse_file(filepath)
        assert 'dialog' in features

    @pytest.mark.unit
    def test_empty_file(self, html_parser, create_html_file):
        filepath = create_html_file("")
        assert html_parser.parse_file(str(filepath)) == set()

    @pytest.mark.unit
    def test_file_not_found(self, html_parser):
        with pytest.raises(FileNotFoundError):
            html_parser.parse_file("/nonexistent/path/to/file.html")

    @pytest.mark.unit
    def test_directory_instead_of_file(self, html_parser, temp_dir):
        with pytest.raises((FileNotFoundError, ValueError, IsADirectoryError)):
            html_parser.parse_file(str(temp_dir))

    @pytest.mark.unit
    def test_utf8_with_bom(self, html_parser, temp_dir):
        filepath = temp_dir / "bom.html"
        filepath.write_text("\ufeff<main>Content with BOM</main>", encoding='utf-8')
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features

    @pytest.mark.parametrize("filename", ["test.html", "test.htm", "testfile", "test.txt"])
    @pytest.mark.unit
    def test_various_extensions(self, html_parser, create_temp_file, filename):
        filepath = create_temp_file(filename, "<main>Content</main>")
        assert 'html5semantic' in html_parser.parse_file(str(filepath))

    @pytest.mark.unit
    def test_path_with_spaces(self, html_parser, temp_dir):
        spaced_dir = temp_dir / "path with spaces"
        spaced_dir.mkdir()
        filepath = spaced_dir / "test file.html"
        filepath.write_text("<main>Content</main>", encoding='utf-8')
        assert 'html5semantic' in html_parser.parse_file(str(filepath))

    @pytest.mark.unit
    def test_state_populated_after_parse(self, html_parser, create_html_file):
        filepath = create_html_file("<main><video src='v.mp4'></video></main>")
        html_parser.parse_file(str(filepath))
        assert len(html_parser.elements_found) > 0
        assert 'html5semantic' in html_parser.features_found


class TestParseHtmlFileConvenience:

    @pytest.mark.unit
    def test_exists(self):
        from src.parsers.html_parser import parse_html_file
        assert callable(parse_html_file)

    @pytest.mark.unit
    def test_finds_features(self, create_html_file):
        from src.parsers.html_parser import parse_html_file
        filepath = create_html_file("<video src='v.mp4'></video>")
        result = parse_html_file(str(filepath))
        assert isinstance(result, set)
        assert 'video' in result

    @pytest.mark.unit
    def test_file_not_found(self):
        from src.parsers.html_parser import parse_html_file
        with pytest.raises(FileNotFoundError):
            parse_html_file("/nonexistent/file.html")


# ---------------------------------------------------------------------------
# parse_multiple_files API
# ---------------------------------------------------------------------------

class TestParseMultipleFiles:

    @pytest.mark.unit
    def test_returns_set(self, html_parser, create_html_file):
        f1 = create_html_file("<main>Content</main>")
        f2 = create_html_file("<video src='v.mp4'></video>")
        result = html_parser.parse_multiple_files([str(f1), str(f2)])
        assert isinstance(result, set)

    @pytest.mark.unit
    def test_empty_list(self, html_parser):
        assert html_parser.parse_multiple_files([]) == set()

    @pytest.mark.unit
    def test_combines_features(self, html_parser, create_temp_file):
        f1 = create_temp_file("f1.html", "<video src='v.mp4'></video>")
        f2 = create_temp_file("f2.html", "<audio src='a.mp3'></audio>")
        f3 = create_temp_file("f3.html", "<canvas></canvas>")
        result = html_parser.parse_multiple_files([str(f1), str(f2), str(f3)])
        assert 'video' in result
        assert 'audio' in result
        assert 'canvas' in result

    @pytest.mark.unit
    def test_deduplicates(self, html_parser, create_temp_file):
        f1 = create_temp_file("f1.html", "<main>Content 1</main>")
        f2 = create_temp_file("f2.html", "<main>Content 2</main>")
        result = html_parser.parse_multiple_files([str(f1), str(f2)])
        assert isinstance(result, set)
        assert 'html5semantic' in result

    @pytest.mark.unit
    def test_continues_after_missing_file(self, html_parser, create_html_file):
        valid = create_html_file("<main>Valid</main>")
        result = html_parser.parse_multiple_files([str(valid), "/nonexistent/file.html"])
        assert 'html5semantic' in result

    @pytest.mark.unit
    def test_all_files_missing(self, html_parser):
        result = html_parser.parse_multiple_files(["/nonexistent/1.html", "/nonexistent/2.html"])
        assert result == set()

    @pytest.mark.integration
    def test_project_files(self, html_parser, temp_dir):
        (temp_dir / "pages").mkdir()
        (temp_dir / "components").mkdir()

        index = temp_dir / "pages" / "index.html"
        index.write_text('<html><body><main><video src="hero.mp4"></video></main></body></html>', encoding='utf-8')

        component = temp_dir / "components" / "dialog.html"
        component.write_text("<dialog><slot></slot></dialog>", encoding='utf-8')

        result = html_parser.parse_multiple_files([str(index), str(component)])
        assert 'video' in result
        assert 'dialog' in result
        assert 'shadowdomv1' in result


# ---------------------------------------------------------------------------
# validate_html API
# ---------------------------------------------------------------------------

class TestValidateHtml:

    @pytest.mark.unit
    def test_returns_bool(self, html_parser):
        assert isinstance(html_parser.validate_html("<div>Content</div>"), bool)

    @pytest.mark.unit
    def test_valid_html(self, html_parser):
        assert html_parser.validate_html("<html><head></head><body><p>Hello</p></body></html>") is True

    @pytest.mark.unit
    def test_complete_html5(self, html_parser):
        html = """
        <!DOCTYPE html>
        <html><head><meta charset="UTF-8"></head>
        <body><main><article>Content</article></main></body></html>
        """
        assert html_parser.validate_html(html) is True

    @pytest.mark.unit
    def test_fragment(self, html_parser):
        assert html_parser.validate_html("<div><p>Paragraph</p></div>") is True

    @pytest.mark.unit
    def test_self_closing(self, html_parser):
        assert html_parser.validate_html("<br><hr><img src='t.jpg' alt='t'>") is True

    @pytest.mark.parametrize("html", [
        "<div>Unclosed",
        "<div><span></div></span>",
        '<input type=text name=field>',
    ])
    @pytest.mark.unit
    def test_malformed_still_parseable(self, html_parser, html):
        """BeautifulSoup is forgiving - malformed still parses."""
        assert isinstance(html_parser.validate_html(html), bool)


# ---------------------------------------------------------------------------
# get_detailed_report & get_statistics
# ---------------------------------------------------------------------------

class TestDetailedReport:

    @pytest.mark.unit
    def test_returns_dict(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        report = html_parser.get_detailed_report()
        assert isinstance(report, dict)

    @pytest.mark.unit
    def test_has_required_keys(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        report = html_parser.get_detailed_report()
        for key in ('total_features', 'features', 'elements_found', 'attributes_found', 'unrecognized'):
            assert key in report

    @pytest.mark.unit
    def test_empty_report(self, html_parser):
        html_parser.parse_string("")
        report = html_parser.get_detailed_report()
        assert report['total_features'] == 0
        assert report['features'] == []

    @pytest.mark.unit
    def test_feature_count(self, html_parser):
        html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        report = html_parser.get_detailed_report()
        assert report['total_features'] == 2

    @pytest.mark.unit
    def test_features_sorted(self, html_parser):
        html_parser.parse_string("<main><video></video><audio></audio><canvas></canvas></main>")
        report = html_parser.get_detailed_report()
        assert report['features'] == sorted(report['features'])

    @pytest.mark.unit
    def test_elements_found_structure(self, html_parser):
        html_parser.parse_string("<video src='v.mp4'></video>")
        report = html_parser.get_detailed_report()
        assert len(report['elements_found']) > 0
        element = report['elements_found'][0]
        assert 'element' in element
        assert 'feature' in element

    @pytest.mark.unit
    def test_report_reflects_last_parse(self, html_parser):
        html_parser.parse_string("<video></video>")
        html_parser.parse_string("<audio></audio>")
        report = html_parser.get_detailed_report()
        assert 'audio' in report['features']
        assert 'video' not in report['features']


class TestStatistics:

    @pytest.mark.unit
    def test_returns_dict(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        stats = html_parser.get_statistics()
        assert isinstance(stats, dict)

    @pytest.mark.unit
    def test_has_required_keys(self, html_parser):
        html_parser.parse_string("<main>Content</main>")
        stats = html_parser.get_statistics()
        for key in ('total_features', 'total_elements_detected', 'total_attributes_detected',
                     'element_counts', 'attribute_counts', 'features_list'):
            assert key in stats

    @pytest.mark.unit
    def test_empty_stats(self, html_parser):
        html_parser.parse_string("")
        stats = html_parser.get_statistics()
        assert stats['total_features'] == 0

    @pytest.mark.unit
    def test_features_list_sorted(self, html_parser):
        html_parser.parse_string("<main><video></video><audio></audio></main>")
        stats = html_parser.get_statistics()
        assert stats['features_list'] == sorted(stats['features_list'])

    @pytest.mark.unit
    def test_report_and_stats_agree(self, html_parser):
        html_parser.parse_string("<main><video></video></main>")
        report = html_parser.get_detailed_report()
        stats = html_parser.get_statistics()
        assert report['total_features'] == stats['total_features']
        assert set(report['features']) == set(stats['features_list'])


# ---------------------------------------------------------------------------
# Custom rules integration
# ---------------------------------------------------------------------------

class TestCustomRulesIntegration:

    @pytest.mark.unit
    def test_parser_has_rule_dicts(self, html_parser):
        for attr in ('_elements', '_input_types', '_attributes', '_attribute_values'):
            assert hasattr(html_parser, attr)

    @pytest.mark.unit
    def test_builtin_rules_work(self, html_parser):
        assert 'video' in html_parser.parse_string("<video src='v.mp4'></video>")
        assert 'input-placeholder' in html_parser.parse_string('<input placeholder="test">')

    @pytest.mark.unit
    def test_builtin_elements_present(self, html_parser):
        for elem in ('video', 'audio', 'main'):
            assert elem in html_parser._elements

    @pytest.mark.unit
    def test_builtin_input_types_present(self, html_parser):
        for t in ('date', 'email', 'color'):
            assert t in html_parser._input_types

    @pytest.mark.unit
    def test_builtin_not_overwritten(self, html_parser):
        assert html_parser._elements.get('video') == 'video'
        assert html_parser._input_types.get('date') == 'input-datetime'

    @pytest.mark.unit
    def test_rules_independent_of_parsing(self, html_parser):
        elements_before = html_parser._elements.copy()
        html_parser.parse_string("<video></video><my-custom></my-custom>")
        assert elements_before == html_parser._elements

    @pytest.mark.unit
    def test_aria_attributes_merged(self, html_parser):
        for attr in ('role', 'aria-label', 'aria-hidden'):
            assert attr in html_parser._attributes

    @pytest.mark.unit
    def test_attribute_values_format(self, html_parser):
        assert ('rel', 'preload') in html_parser._attribute_values
        assert ('type', 'module') in html_parser._attribute_values


class TestCustomRulesExtended:
    """Custom rules injected via mock."""

    @pytest.fixture
    def custom_html_rules(self):
        return {
            'elements': {'x-widget': 'custom-elementsv1', 'data-grid': 'custom-elementsv1'},
            'attributes': {'x-bind': 'custom-attr-feature'},
            'input_types': {'custom-date': 'custom-input-feature'},
            'attribute_values': {
                'data-mode:advanced': 'custom-value-feature',
                'data-special:val<1>': 'custom-special-feature',
            },
        }

    @pytest.fixture
    def parser_with_custom(self, custom_html_rules):
        with patch('src.parsers.html_parser.get_custom_html_rules', return_value=custom_html_rules):
            parser = __import__('src.parsers.html_parser', fromlist=['HTMLParser']).HTMLParser()
            yield parser

    @pytest.mark.unit
    def test_custom_element_detected(self, parser_with_custom):
        html = '<div><section><x-widget>content</x-widget></section></div>'
        assert 'custom-elementsv1' in parser_with_custom.parse_string(html)

    @pytest.mark.unit
    def test_custom_attribute_detected(self, parser_with_custom):
        html = '<div x-bind="value">text</div>'
        assert 'custom-attr-feature' in parser_with_custom.parse_string(html)

    @pytest.mark.unit
    def test_custom_input_type_detected(self, parser_with_custom):
        html = '<form><input type="custom-date"></form>'
        assert 'custom-input-feature' in parser_with_custom.parse_string(html)

    @pytest.mark.unit
    def test_custom_attribute_value_detected(self, parser_with_custom):
        html = '<div data-mode="advanced">content</div>'
        assert 'custom-value-feature' in parser_with_custom.parse_string(html)

    @pytest.mark.unit
    def test_all_custom_rules_in_one_file(self, parser_with_custom):
        html = """
        <x-widget x-bind="val">text</x-widget>
        <form><input type="custom-date"></form>
        <div data-mode="advanced">content</div>
        """
        features = parser_with_custom.parse_string(html)
        assert 'custom-elementsv1' in features
        assert 'custom-attr-feature' in features
        assert 'custom-input-feature' in features
        assert 'custom-value-feature' in features

    @pytest.mark.unit
    def test_custom_dont_override_builtin(self, parser_with_custom):
        assert parser_with_custom._elements.get('video') == 'video'
        assert parser_with_custom._input_types.get('date') == 'input-datetime'

    @pytest.mark.unit
    def test_custom_and_builtin_mix(self, parser_with_custom):
        html = """
        <video src="v.mp4"></video>
        <x-widget>text</x-widget>
        <input type="email">
        <input type="custom-date">
        """
        features = parser_with_custom.parse_string(html)
        assert 'video' in features
        assert 'custom-elementsv1' in features
        assert 'input-email-tel-url' in features
        assert 'custom-input-feature' in features

    @pytest.mark.unit
    def test_attribute_value_colon_parsing(self, parser_with_custom):
        assert ('data-mode', 'advanced') in parser_with_custom._attribute_values

    @pytest.mark.unit
    def test_attribute_value_special_chars(self, parser_with_custom):
        assert ('data-special', 'val<1>') in parser_with_custom._attribute_values

    @pytest.mark.unit
    def test_empty_custom_rules(self):
        empty = {'elements': {}, 'attributes': {}, 'input_types': {}, 'attribute_values': {}}
        with patch('src.parsers.html_parser.get_custom_html_rules', return_value=empty):
            from src.parsers.html_parser import HTMLParser
            parser = HTMLParser()
            assert 'video' in parser.parse_string("<video src='v.mp4'></video>")

    @pytest.mark.unit
    def test_custom_element_not_in_text(self, parser_with_custom):
        html = "<p>The x-widget component is great</p>"
        assert 'custom-elementsv1' not in parser_with_custom.parse_string(html)

    @pytest.mark.unit
    def test_custom_rules_in_report(self, parser_with_custom):
        parser_with_custom.parse_string('<x-widget>content</x-widget>')
        report = parser_with_custom.get_detailed_report()
        assert 'custom-elementsv1' in report['features']


class TestCustomRulesLoader:

    @pytest.mark.unit
    def test_loader_exists(self):
        from src.parsers.custom_rules_loader import get_custom_html_rules
        assert callable(get_custom_html_rules)

    @pytest.mark.unit
    def test_returns_dict(self):
        from src.parsers.custom_rules_loader import get_custom_html_rules
        rules = get_custom_html_rules()
        assert isinstance(rules, dict)

    @pytest.mark.unit
    def test_has_expected_keys(self):
        from src.parsers.custom_rules_loader import get_custom_html_rules
        rules = get_custom_html_rules()
        for key in rules:
            assert key in ['elements', 'input_types', 'attributes', 'attribute_values']

    @pytest.mark.unit
    def test_fresh_parsers_share_rules(self):
        from src.parsers.html_parser import HTMLParser
        p1 = HTMLParser()
        p2 = HTMLParser()
        assert p1._elements == p2._elements
        assert p1._input_types == p2._input_types


# ---------------------------------------------------------------------------
# Real-world integration tests
# ---------------------------------------------------------------------------

class TestRealWorldIntegration:

    @pytest.mark.integration
    def test_landing_page(self, parse_features):
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="theme-color" content="#4285f4">
            <link rel="icon" type="image/svg+xml" href="favicon.svg">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preload" href="hero.jpg" as="image">
        </head>
        <body>
            <header><nav aria-label="Main"><a href="/">Home</a></nav></header>
            <main>
                <section class="hero">
                    <picture>
                        <source srcset="hero.avif" type="image/avif">
                        <source srcset="hero.webp" type="image/webp">
                        <img src="hero.jpg" alt="Hero" loading="eager">
                    </picture>
                </section>
                <section>
                    <figure>
                        <img src="f.jpg" loading="lazy" alt="Feature">
                        <figcaption>Description</figcaption>
                    </figure>
                </section>
                <section>
                    <video poster="p.jpg" controls>
                        <source src="i.webm" type="video/webm">
                        <source src="i.mp4" type="video/mp4">
                        <track kind="captions" src="c.vtt" srclang="en">
                    </video>
                </section>
            </main>
            <footer><a href="/privacy" rel="noopener">Privacy</a></footer>
        </body>
        </html>
        """
        features = parse_features(html)
        assert 'viewport-units' in features
        assert 'meta-theme-color' in features
        assert 'link-icon-svg' in features
        assert 'link-rel-preconnect' in features
        assert 'link-rel-preload' in features
        assert 'html5semantic' in features
        assert 'wai-aria' in features
        assert 'picture' in features
        assert 'avif' in features
        assert 'webp' in features
        assert 'loading-lazy-attr' in features
        assert 'video' in features
        assert 'webm' in features
        assert 'webvtt' in features
        assert 'rel-noopener' in features

    @pytest.mark.integration
    def test_spa_shell(self, parse_features):
        html = """
        <html><head>
            <meta http-equiv="content-security-policy" content="default-src 'self'">
            <link rel="modulepreload" href="app.js">
            <script type="module" src="app.js" defer></script>
        </head>
        <body onhashchange="router()">
            <my-app-shell>
                <nav slot="navigation" aria-label="Main"><a href="#/">Home</a></nav>
                <main slot="content" aria-live="polite">Loading...</main>
            </my-app-shell>
            <template id="page-template"><slot name="content"></slot></template>
            <dialog id="modal" aria-modal="true">
                <form method="dialog"><button>Close</button></form>
            </dialog>
        </body></html>
        """
        features = parse_features(html)
        assert 'contentsecuritypolicy2' in features
        assert 'link-rel-modulepreload' in features
        assert 'es6-module' in features
        assert 'script-defer' in features
        assert 'hashchange' in features
        assert 'custom-elementsv1' in features
        assert 'shadowdomv1' in features
        assert 'template' in features
        assert 'dialog' in features
        assert 'wai-aria' in features

    @pytest.mark.integration
    def test_checkout_form(self, parse_features):
        html = """
        <form id="checkout">
            <fieldset>
                <legend>Contact</legend>
                <input type="email" required autocomplete="email" inputmode="email" placeholder="you@ex.com">
                <input type="tel" autocomplete="tel" inputmode="tel" pattern="[0-9]{10}">
            </fieldset>
            <fieldset>
                <legend>Payment</legend>
                <input type="text" required autocomplete="cc-number" inputmode="numeric" minlength="16" maxlength="16">
                <input type="month" required autocomplete="cc-exp">
            </fieldset>
            <button type="submit">Pay</button>
        </form>
        """
        features = parse_features(html)
        assert 'input-email-tel-url' in features
        assert 'form-validation' in features
        assert 'input-autocomplete-onoff' in features
        assert 'input-inputmode' in features
        assert 'input-pattern' in features
        assert 'input-placeholder' in features
        assert 'input-minlength' in features
        assert 'maxlength' in features
        assert 'input-datetime' in features

    @pytest.mark.integration
    def test_video_gallery(self, parse_features):
        html = """
        <main>
            <section aria-label="Featured video">
                <video controls crossorigin="anonymous">
                    <source src="featured.webm" type="video/webm">
                    <source src="featured.mp4" type="video/mp4">
                    <track kind="captions" src="en.vtt" srclang="en" default>
                    <track kind="captions" src="es.vtt" srclang="es">
                    <track kind="chapters" src="ch.vtt" srclang="en">
                </video>
            </section>
            <section aria-label="Thumbnails">
                <img src="t1.jpg" srcset="t1.jpg 1x, t1@2x.jpg 2x" loading="lazy" alt="V1">
            </section>
            <section aria-label="Audio playlist">
                <audio controls>
                    <source src="audio.opus" type="audio/opus">
                    <source src="audio.mp3" type="audio/mpeg">
                    <track kind="captions" src="transcript.vtt">
                </audio>
            </section>
        </main>
        """
        features = parse_features(html)
        assert 'video' in features
        assert 'cors' in features
        assert 'webm' in features
        assert 'webvtt' in features
        assert 'videotracks' in features
        assert 'srcset' in features
        assert 'loading-lazy-attr' in features
        assert 'audio' in features
        assert 'opus' in features
        assert 'audiotracks' in features

    @pytest.mark.integration
    def test_dashboard(self, parse_features):
        html = """
        <main>
            <section aria-labelledby="metrics">
                <h2 id="metrics">Metrics</h2>
                <meter min="0" max="100" value="45">45%</meter>
                <progress value="30" max="100">30%</progress>
            </section>
            <section>
                <canvas id="chart" width="800" height="400" aria-label="Chart" role="img"></canvas>
                <svg viewBox="0 0 400 200" aria-label="Pie" role="img">
                    <circle cx="100" cy="100" r="80" fill="blue"/>
                </svg>
            </section>
        </main>
        """
        features = parse_features(html)
        assert 'meter' in features
        assert 'progress' in features
        assert 'canvas' in features
        assert 'svg' in features
        assert 'wai-aria' in features

    @pytest.mark.integration
    def test_full_page_all_rule_types(self, html_parser):
        html = """
        <!DOCTYPE html>
        <html><head>
            <link rel="preload" href="s.css" as="style">
            <script type="module" src="app.js"></script>
        </head><body>
            <main>
                <video src="v.mp4"><source type="video/webm" src="v.webm"></video>
                <form>
                    <input type="date" required placeholder="Select date">
                    <input type="email" autocomplete="email">
                </form>
                <div contenteditable="true" role="textbox" aria-label="Editor">Edit me</div>
            </main>
        </body></html>
        """
        features = html_parser.parse_string(html)
        assert 'html5semantic' in features
        assert 'video' in features
        assert 'input-datetime' in features
        assert 'input-email-tel-url' in features
        assert 'form-validation' in features
        assert 'input-placeholder' in features
        assert 'input-autocomplete-onoff' in features
        assert 'contenteditable' in features
        assert 'wai-aria' in features
        assert 'link-rel-preload' in features
        assert 'es6-module' in features
        assert 'webm' in features
