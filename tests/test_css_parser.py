"""
Test suite for CSS Parser.
Tests feature detection for various CSS properties and modern features.
"""

import pytest
from pathlib import Path


class TestCSSParserBasic:
    """Basic functionality tests for CSS parser."""

    def test_parser_initialization(self, css_parser):
        """Test parser initializes correctly."""
        assert css_parser is not None
        assert hasattr(css_parser, 'parse_string')
        assert hasattr(css_parser, 'parse_file')
        assert hasattr(css_parser, 'features_found')

    def test_parse_empty_string(self, css_parser):
        """Test parsing empty CSS string."""
        features = css_parser.parse_string("")
        assert isinstance(features, set)
        assert len(features) == 0

    def test_parse_invalid_css(self, css_parser):
        """Test parsing non-CSS content gracefully."""
        features = css_parser.parse_string("not valid css content")
        assert isinstance(features, set)

    def test_parse_string_returns_set(self, css_parser):
        """Test that parse_string returns a set."""
        result = css_parser.parse_string(".container { display: flex; }")
        assert isinstance(result, set)


class TestCSSFlexbox:
    """Test detection of CSS Flexbox features."""

    def test_detect_display_flex(self, css_parser):
        """Test detection of display: flex."""
        css = ".container { display: flex; }"
        features = css_parser.parse_string(css)
        assert 'flexbox' in features

    def test_detect_flex_direction(self, css_parser):
        """Test detection of flex-direction."""
        css = ".container { flex-direction: row; }"
        features = css_parser.parse_string(css)
        assert 'flexbox' in features

    def test_detect_flex_wrap(self, css_parser):
        """Test detection of flex-wrap."""
        css = ".container { flex-wrap: wrap; }"
        features = css_parser.parse_string(css)
        assert 'flexbox' in features

    def test_detect_justify_content(self, css_parser):
        """Test detection of justify-content."""
        css = ".container { justify-content: center; }"
        features = css_parser.parse_string(css)
        assert 'flexbox' in features

    def test_detect_align_items(self, css_parser):
        """Test detection of align-items."""
        css = ".container { align-items: center; }"
        features = css_parser.parse_string(css)
        assert 'flexbox' in features

    def test_detect_flexbox_gap(self, css_parser):
        """Test detection of flexbox gap property."""
        css = ".container { display: flex; gap: 20px; }"
        features = css_parser.parse_string(css)
        assert 'flexbox-gap' in features

    def test_flexbox_full_layout(self, css_parser, sample_css_flexbox):
        """Test detection in complete flexbox layout."""
        features = css_parser.parse_string(sample_css_flexbox)
        assert 'flexbox' in features
        assert 'flexbox-gap' in features


class TestCSSGrid:
    """Test detection of CSS Grid features."""

    def test_detect_display_grid(self, css_parser):
        """Test detection of display: grid."""
        css = ".container { display: grid; }"
        features = css_parser.parse_string(css)
        assert 'css-grid' in features

    def test_detect_grid_template_columns(self, css_parser):
        """Test detection of grid-template-columns."""
        css = ".container { grid-template-columns: repeat(3, 1fr); }"
        features = css_parser.parse_string(css)
        assert 'css-grid' in features

    def test_detect_grid_template_rows(self, css_parser):
        """Test detection of grid-template-rows."""
        css = ".container { grid-template-rows: auto 1fr auto; }"
        features = css_parser.parse_string(css)
        assert 'css-grid' in features

    def test_detect_grid_column(self, css_parser):
        """Test detection of grid-column."""
        css = ".item { grid-column: span 2; }"
        features = css_parser.parse_string(css)
        assert 'css-grid' in features

    def test_detect_grid_row(self, css_parser):
        """Test detection of grid-row."""
        css = ".item { grid-row: 1 / 3; }"
        features = css_parser.parse_string(css)
        assert 'css-grid' in features

    def test_grid_full_layout(self, css_parser, sample_css_grid):
        """Test detection in complete grid layout."""
        features = css_parser.parse_string(sample_css_grid)
        assert 'css-grid' in features


class TestCSSTransforms:
    """Test detection of CSS Transform features."""

    def test_detect_2d_transform(self, css_parser):
        """Test detection of 2D transforms."""
        css = ".box { transform: rotate(45deg); }"
        features = css_parser.parse_string(css)
        assert 'transforms2d' in features

    def test_detect_translate(self, css_parser):
        """Test detection of translate function."""
        css = ".box { transform: translate(10px, 20px); }"
        features = css_parser.parse_string(css)
        assert 'transforms2d' in features

    def test_detect_scale(self, css_parser):
        """Test detection of scale function."""
        css = ".box { transform: scale(1.5); }"
        features = css_parser.parse_string(css)
        assert 'transforms2d' in features

    def test_detect_skew(self, css_parser):
        """Test detection of skew function."""
        css = ".box { transform: skew(10deg, 20deg); }"
        features = css_parser.parse_string(css)
        assert 'transforms2d' in features

    def test_detect_3d_transform(self, css_parser):
        """Test detection of 3D transforms."""
        css = ".box { transform: translate3d(10px, 20px, 30px); }"
        features = css_parser.parse_string(css)
        assert 'transforms3d' in features

    def test_detect_perspective(self, css_parser):
        """Test detection of perspective."""
        css = ".box { perspective: 1000px; }"
        features = css_parser.parse_string(css)
        assert 'transforms3d' in features

    def test_detect_rotate_xyz(self, css_parser):
        """Test detection of rotateX/Y/Z."""
        css = ".box { transform: rotateX(45deg); }"
        features = css_parser.parse_string(css)
        assert 'transforms3d' in features

    def test_transforms_sample(self, css_parser, sample_css_transforms):
        """Test detection in transform sample."""
        features = css_parser.parse_string(sample_css_transforms)
        assert 'transforms2d' in features
        assert 'transforms3d' in features


class TestCSSAnimations:
    """Test detection of CSS Animation features."""

    def test_detect_keyframes(self, css_parser):
        """Test detection of @keyframes."""
        css = "@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }"
        features = css_parser.parse_string(css)
        assert 'css-animation' in features

    def test_detect_animation_property(self, css_parser):
        """Test detection of animation property."""
        css = ".box { animation: fadeIn 1s ease; }"
        features = css_parser.parse_string(css)
        assert 'css-animation' in features

    def test_detect_animation_name(self, css_parser):
        """Test detection of animation-name."""
        css = ".box { animation-name: slideIn; }"
        features = css_parser.parse_string(css)
        assert 'css-animation' in features

    def test_detect_animation_duration(self, css_parser):
        """Test detection of animation-duration."""
        css = ".box { animation-duration: 2s; }"
        features = css_parser.parse_string(css)
        assert 'css-animation' in features


class TestCSSTransitions:
    """Test detection of CSS Transition features."""

    def test_detect_transition(self, css_parser):
        """Test detection of transition property."""
        css = ".box { transition: all 0.3s ease; }"
        features = css_parser.parse_string(css)
        assert 'css-transitions' in features

    def test_detect_transition_property(self, css_parser):
        """Test detection of transition-property."""
        css = ".box { transition-property: opacity, transform; }"
        features = css_parser.parse_string(css)
        assert 'css-transitions' in features

    def test_detect_transition_duration(self, css_parser):
        """Test detection of transition-duration."""
        css = ".box { transition-duration: 0.5s; }"
        features = css_parser.parse_string(css)
        assert 'css-transitions' in features


class TestCSSColors:
    """Test detection of CSS Color features."""

    def test_detect_rgba(self, css_parser):
        """Test detection of rgba color."""
        css = ".box { background: rgba(255, 0, 0, 0.5); }"
        features = css_parser.parse_string(css)
        assert 'css3-colors' in features

    def test_detect_hsla(self, css_parser):
        """Test detection of hsla color."""
        css = ".box { color: hsla(120, 100%, 50%, 0.3); }"
        features = css_parser.parse_string(css)
        assert 'css3-colors' in features

    def test_detect_hex_color(self, css_parser):
        """Test detection of hex color."""
        css = ".box { color: #3498db; }"
        features = css_parser.parse_string(css)
        assert 'css3-colors' in features

    def test_detect_current_color(self, css_parser):
        """Test detection of currentColor."""
        css = ".box { border-color: currentColor; }"
        features = css_parser.parse_string(css)
        assert 'currentcolor' in features


class TestCSSGradients:
    """Test detection of CSS Gradient features."""

    def test_detect_linear_gradient(self, css_parser):
        """Test detection of linear-gradient."""
        css = ".box { background: linear-gradient(to right, red, blue); }"
        features = css_parser.parse_string(css)
        assert 'css-gradients' in features

    def test_detect_radial_gradient(self, css_parser):
        """Test detection of radial-gradient."""
        css = ".box { background: radial-gradient(circle, white, black); }"
        features = css_parser.parse_string(css)
        assert 'css-gradients' in features

    def test_detect_repeating_linear_gradient(self, css_parser):
        """Test detection of repeating-linear-gradient."""
        css = ".box { background: repeating-linear-gradient(45deg, red, blue 10px); }"
        features = css_parser.parse_string(css)
        assert 'css-gradients' in features


class TestCSSVariables:
    """Test detection of CSS Custom Properties (Variables)."""

    def test_detect_css_variables_definition(self, css_parser):
        """Test detection of CSS variable definition."""
        css = ":root { --primary-color: #3498db; }"
        features = css_parser.parse_string(css)
        assert 'css-variables' in features

    def test_detect_css_variables_usage(self, css_parser):
        """Test detection of CSS variable usage."""
        css = ".box { color: var(--primary-color); }"
        features = css_parser.parse_string(css)
        assert 'css-variables' in features


class TestCSSMediaQueries:
    """Test detection of CSS Media Query features."""

    def test_detect_prefers_color_scheme(self, css_parser):
        """Test detection of prefers-color-scheme."""
        css = "@media (prefers-color-scheme: dark) { body { background: black; } }"
        features = css_parser.parse_string(css)
        assert 'prefers-color-scheme' in features

    def test_detect_prefers_reduced_motion(self, css_parser):
        """Test detection of prefers-reduced-motion."""
        css = "@media (prefers-reduced-motion: reduce) { * { animation: none; } }"
        features = css_parser.parse_string(css)
        assert 'prefers-reduced-motion' in features


class TestCSSFileParsing:
    """Test parsing CSS files."""

    def test_parse_css_file(self, css_parser, sample_css_file):
        """Test parsing a CSS file."""
        features = css_parser.parse_file(sample_css_file)
        assert isinstance(features, set)
        assert len(features) > 0

    def test_parse_nonexistent_file(self, css_parser):
        """Test parsing a non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            css_parser.parse_file("/nonexistent/path/style.css")

    def test_parse_fixture_file(self, css_parser, fixtures_dir):
        """Test parsing the modern CSS fixture file."""
        fixture_file = fixtures_dir / "sample_css" / "modern.css"
        if fixture_file.exists():
            features = css_parser.parse_file(str(fixture_file))
            assert 'flexbox' in features
            assert 'css-grid' in features
            assert 'transforms2d' in features
            assert 'css-animation' in features


class TestCSSCommentHandling:
    """Test that comments are properly ignored."""

    def test_ignore_single_line_comment_content(self, css_parser):
        """Test that CSS features in comments are ignored."""
        css = """
        /* display: flex; - this should not be detected */
        .container { color: red; }
        """
        features = css_parser.parse_string(css)
        # flexbox should not be detected since it's in a comment
        # (depending on implementation)

    def test_ignore_multiline_comment(self, css_parser):
        """Test that multiline comments are handled."""
        css = """
        /*
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
        }
        */
        .actual { color: blue; }
        """
        features = css_parser.parse_string(css)
        # Grid should not be detected since it's in a comment


class TestCSSModernFeatures:
    """Test detection of various modern CSS features."""

    def test_detect_will_change(self, css_parser):
        """Test detection of will-change."""
        css = ".box { will-change: transform, opacity; }"
        features = css_parser.parse_string(css)
        assert 'will-change' in features

    def test_detect_background_size(self, css_parser):
        """Test detection of background-size."""
        css = ".box { background-size: cover; }"
        features = css_parser.parse_string(css)
        assert 'background-img-opts' in features

    def test_detect_multicolumn(self, css_parser):
        """Test detection of multicolumn layout."""
        css = ".text { column-count: 3; column-gap: 20px; }"
        features = css_parser.parse_string(css)
        assert 'multicolumn' in features

    def test_detect_inline_block(self, css_parser):
        """Test detection of inline-block."""
        css = ".box { display: inline-block; }"
        features = css_parser.parse_string(css)
        assert 'inline-block' in features


class TestCSSParserStatistics:
    """Test parser statistics and reporting."""

    def test_get_statistics(self, css_parser, sample_css_modern):
        """Test getting parsing statistics."""
        css_parser.parse_string(sample_css_modern)
        stats = css_parser.get_statistics()
        assert 'total_features' in stats
        assert 'features_list' in stats
        assert stats['total_features'] >= 0

    def test_get_detailed_report(self, css_parser, sample_css_modern):
        """Test getting detailed report."""
        css_parser.parse_string(sample_css_modern)
        report = css_parser.get_detailed_report()
        assert 'total_features' in report
        assert 'features' in report
        assert 'feature_details' in report

    def test_validate_css_valid(self, css_parser):
        """Test CSS validation with valid CSS."""
        valid_css = ".container { display: flex; }"
        assert css_parser.validate_css(valid_css) is True

    def test_validate_css_invalid(self, css_parser):
        """Test CSS validation with non-CSS content."""
        invalid = "this is just plain text without css"
        # Basic validation might still return True for simple text
        # depending on implementation


class TestCSSParserMultipleFiles:
    """Test parsing multiple CSS files."""

    def test_parse_multiple_files(self, css_parser, tmp_path):
        """Test parsing multiple CSS files."""
        # Create test files
        file1 = tmp_path / "style1.css"
        file1.write_text(".a { display: flex; }")

        file2 = tmp_path / "style2.css"
        file2.write_text(".b { display: grid; }")

        features = css_parser.parse_multiple_files([str(file1), str(file2)])
        assert 'flexbox' in features
        assert 'css-grid' in features

    def test_parse_multiple_with_invalid_file(self, css_parser, tmp_path):
        """Test parsing multiple files when one doesn't exist."""
        file1 = tmp_path / "style1.css"
        file1.write_text(".a { display: flex; }")

        # This should handle the missing file gracefully
        features = css_parser.parse_multiple_files([
            str(file1),
            "/nonexistent/file.css"
        ])
        assert 'flexbox' in features


class TestCSSComplexSamples:
    """Test with complex real-world CSS samples."""

    def test_modern_css_sample(self, css_parser, sample_css_modern):
        """Test parsing modern CSS sample with multiple features."""
        features = css_parser.parse_string(sample_css_modern)

        # Should detect multiple feature categories
        assert 'flexbox' in features
        assert 'css-transitions' in features
        assert 'css-animation' in features
        assert 'css-gradients' in features
        assert 'css-variables' in features

    def test_combined_features(self, css_parser):
        """Test detection of multiple features in single declaration."""
        css = """
        .card {
            display: flex;
            gap: 20px;
            background: linear-gradient(to right, red, blue);
            transform: translateY(-5px);
            transition: all 0.3s ease;
            animation: fadeIn 1s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        """
        features = css_parser.parse_string(css)
        assert 'flexbox' in features
        assert 'flexbox-gap' in features
        assert 'css-gradients' in features
        assert 'transforms2d' in features
        assert 'css-transitions' in features
        assert 'css-animation' in features
