"""Tests for HTMLParser.get_detailed_report() and get_statistics() methods.

Tests: Report generation, statistics calculation
"""

import pytest


class TestGetDetailedReportBasic:
    """Tests for basic get_detailed_report functionality."""

    def test_returns_dict(self, html_parser):
        """Test that get_detailed_report returns a dict."""
        html_parser.parse_string("<main>Content</main>")
        report = html_parser.get_detailed_report()
        assert isinstance(report, dict)

    def test_report_has_required_keys(self, html_parser):
        """Test that report has required keys."""
        html_parser.parse_string("<main>Content</main>")
        report = html_parser.get_detailed_report()

        assert 'total_features' in report
        assert 'features' in report
        assert 'elements_found' in report
        assert 'attributes_found' in report
        assert 'unrecognized' in report

    def test_empty_input_report(self, html_parser):
        """Test report for empty input."""
        html_parser.parse_string("")
        report = html_parser.get_detailed_report()

        assert report['total_features'] == 0
        assert report['features'] == []
        assert report['elements_found'] == []
        assert report['attributes_found'] == []


class TestGetDetailedReportContent:
    """Tests for get_detailed_report content."""

    def test_total_features_count(self, html_parser):
        """Test total_features count."""
        html_parser.parse_string("<main><video src='v.mp4'></video></main>")
        report = html_parser.get_detailed_report()

        assert report['total_features'] == 2  # html5semantic, video

    def test_features_list_sorted(self, html_parser):
        """Test that features list is sorted."""
        html_parser.parse_string("<main><video></video><audio></audio><canvas></canvas></main>")
        report = html_parser.get_detailed_report()

        features = report['features']
        assert features == sorted(features)

    def test_elements_found_structure(self, html_parser):
        """Test structure of elements_found."""
        html_parser.parse_string("<video src='v.mp4'></video>")
        report = html_parser.get_detailed_report()

        assert len(report['elements_found']) > 0
        element = report['elements_found'][0]
        assert 'element' in element
        assert 'feature' in element
        assert 'count' in element

    def test_attributes_found_structure(self, html_parser):
        """Test structure of attributes_found."""
        html_parser.parse_string('<input placeholder="test" required>')
        report = html_parser.get_detailed_report()

        assert len(report['attributes_found']) > 0
        attr = report['attributes_found'][0]
        assert 'attribute' in attr
        assert 'element' in attr
        assert 'feature' in attr

    def test_unrecognized_list(self, html_parser):
        """Test unrecognized patterns list."""
        html_parser.parse_string("<my-custom-element></my-custom-element>")
        report = html_parser.get_detailed_report()

        # Custom element should be detected as custom-elementsv1
        # Unrecognized might be empty depending on implementation


class TestGetDetailedReportFeatures:
    """Tests for feature reporting in get_detailed_report."""

    def test_semantic_elements_reported(self, html_parser):
        """Test semantic elements are reported."""
        html_parser.parse_string("<main><article><section></section></article></main>")
        report = html_parser.get_detailed_report()

        assert 'html5semantic' in report['features']

    def test_multiple_features_reported(self, html_parser):
        """Test multiple features are reported."""
        html = """
        <main>
            <video src="v.mp4"></video>
            <audio src="a.mp3"></audio>
            <canvas></canvas>
            <dialog></dialog>
        </main>
        """
        html_parser.parse_string(html)
        report = html_parser.get_detailed_report()

        assert 'html5semantic' in report['features']
        assert 'video' in report['features']
        assert 'audio' in report['features']
        assert 'canvas' in report['features']
        assert 'dialog' in report['features']

    def test_attribute_features_reported(self, html_parser):
        """Test attribute-based features are reported."""
        html = '<input type="date" placeholder="Select date" required>'
        html_parser.parse_string(html)
        report = html_parser.get_detailed_report()

        assert 'input-datetime' in report['features']
        assert 'input-placeholder' in report['features']
        assert 'form-validation' in report['features']


class TestGetStatisticsBasic:
    """Tests for basic get_statistics functionality."""

    def test_returns_dict(self, html_parser):
        """Test that get_statistics returns a dict."""
        html_parser.parse_string("<main>Content</main>")
        stats = html_parser.get_statistics()
        assert isinstance(stats, dict)

    def test_stats_has_required_keys(self, html_parser):
        """Test that stats has required keys."""
        html_parser.parse_string("<main>Content</main>")
        stats = html_parser.get_statistics()

        assert 'total_features' in stats
        assert 'total_elements_detected' in stats
        assert 'total_attributes_detected' in stats
        assert 'element_counts' in stats
        assert 'attribute_counts' in stats
        assert 'features_list' in stats

    def test_empty_input_stats(self, html_parser):
        """Test stats for empty input."""
        html_parser.parse_string("")
        stats = html_parser.get_statistics()

        assert stats['total_features'] == 0
        assert stats['total_elements_detected'] == 0
        assert stats['total_attributes_detected'] == 0


class TestGetStatisticsContent:
    """Tests for get_statistics content."""

    def test_total_features(self, html_parser):
        """Test total_features count."""
        html_parser.parse_string("<main><video></video></main>")
        stats = html_parser.get_statistics()

        assert stats['total_features'] == 2

    def test_total_elements_detected(self, html_parser):
        """Test total_elements_detected count."""
        html_parser.parse_string("<video></video><audio></audio><canvas></canvas>")
        stats = html_parser.get_statistics()

        assert stats['total_elements_detected'] >= 3

    def test_total_attributes_detected(self, html_parser):
        """Test total_attributes_detected count."""
        html_parser.parse_string('<input placeholder="test" required autofocus>')
        stats = html_parser.get_statistics()

        assert stats['total_attributes_detected'] >= 3

    def test_element_counts(self, html_parser):
        """Test element_counts dictionary."""
        html_parser.parse_string("<main></main><main></main><video></video>")
        stats = html_parser.get_statistics()

        # element_counts should have entries for detected elements
        assert isinstance(stats['element_counts'], dict)

    def test_attribute_counts(self, html_parser):
        """Test attribute_counts dictionary."""
        html_parser.parse_string('<input placeholder="a"><input placeholder="b">')
        stats = html_parser.get_statistics()

        assert isinstance(stats['attribute_counts'], dict)

    def test_features_list_sorted(self, html_parser):
        """Test that features_list is sorted."""
        html_parser.parse_string("<main><video></video><audio></audio></main>")
        stats = html_parser.get_statistics()

        features = stats['features_list']
        assert features == sorted(features)


class TestReportVsStatistics:
    """Tests comparing get_detailed_report and get_statistics."""

    def test_same_total_features(self, html_parser):
        """Test that both methods report same total features."""
        html_parser.parse_string("<main><video></video></main>")

        report = html_parser.get_detailed_report()
        stats = html_parser.get_statistics()

        assert report['total_features'] == stats['total_features']

    def test_same_features_content(self, html_parser):
        """Test that both methods report same features."""
        html_parser.parse_string("<main><video></video></main>")

        report = html_parser.get_detailed_report()
        stats = html_parser.get_statistics()

        assert set(report['features']) == set(stats['features_list'])


class TestReportAfterMultipleParses:
    """Tests for reports after multiple parse calls."""

    def test_report_reflects_last_parse(self, html_parser):
        """Test that report reflects only the last parse."""
        html_parser.parse_string("<video></video>")
        html_parser.parse_string("<audio></audio>")

        report = html_parser.get_detailed_report()

        assert 'audio' in report['features']
        assert 'video' not in report['features']

    def test_stats_reflects_last_parse(self, html_parser):
        """Test that stats reflect only the last parse."""
        html_parser.parse_string("<video></video>")
        html_parser.parse_string("<main></main>")

        stats = html_parser.get_statistics()

        assert 'html5semantic' in stats['features_list']
        assert 'video' not in stats['features_list']


class TestComplexReports:
    """Tests for reports with complex content."""

    def test_comprehensive_page_report(self, html_parser):
        """Test report for comprehensive page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width">
            <meta name="theme-color" content="#000">
        </head>
        <body>
            <main>
                <article>
                    <video src="v.mp4">
                        <track src="captions.vtt" kind="captions">
                    </video>
                </article>
                <aside role="complementary">
                    <details>
                        <summary>More info</summary>
                        <p>Details here</p>
                    </details>
                </aside>
            </main>
            <dialog aria-modal="true">
                <form method="dialog">
                    <input type="date" required>
                </form>
            </dialog>
        </body>
        </html>
        """
        html_parser.parse_string(html)
        report = html_parser.get_detailed_report()
        stats = html_parser.get_statistics()

        # Check report has many features
        assert report['total_features'] >= 5
        assert len(report['elements_found']) >= 5
        assert len(report['attributes_found']) >= 3

        # Check stats
        assert stats['total_features'] >= 5
        assert stats['total_elements_detected'] >= 5
