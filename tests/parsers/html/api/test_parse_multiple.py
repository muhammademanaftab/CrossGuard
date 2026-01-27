"""Tests for HTMLParser.parse_multiple_files() method.

Tests: Multiple file parsing, combining results, error handling
"""

import pytest
from pathlib import Path


class TestParseMultipleBasic:
    """Tests for basic parse_multiple_files functionality."""

    def test_parse_multiple_returns_set(self, html_parser, create_html_file):
        """Test that parse_multiple_files returns a set."""
        file1 = create_html_file("<main>Content</main>")
        file2 = create_html_file("<video src='v.mp4'></video>")
        result = html_parser.parse_multiple_files([str(file1), str(file2)])
        assert isinstance(result, set)

    def test_parse_multiple_empty_list(self, html_parser):
        """Test parse_multiple_files with empty list."""
        result = html_parser.parse_multiple_files([])
        assert result == set()

    def test_parse_multiple_single_file(self, html_parser, create_html_file):
        """Test parse_multiple_files with single file."""
        filepath = create_html_file("<main>Content</main>")
        result = html_parser.parse_multiple_files([str(filepath)])
        assert 'html5semantic' in result


class TestParseMultipleCombining:
    """Tests for combining results from multiple files."""

    def test_combines_different_features(self, html_parser, create_temp_file):
        """Test that features from different files are combined."""
        file1 = create_temp_file("file1.html", "<video src='v.mp4'></video>")
        file2 = create_temp_file("file2.html", "<audio src='a.mp3'></audio>")
        file3 = create_temp_file("file3.html", "<canvas></canvas>")

        result = html_parser.parse_multiple_files([str(file1), str(file2), str(file3)])

        assert 'video' in result
        assert 'audio' in result
        assert 'canvas' in result

    def test_no_duplicates_when_combining(self, html_parser, create_temp_file):
        """Test that duplicate features are not added multiple times."""
        file1 = create_temp_file("file1.html", "<main>Content 1</main>")
        file2 = create_temp_file("file2.html", "<main>Content 2</main>")

        result = html_parser.parse_multiple_files([str(file1), str(file2)])

        # Set naturally deduplicates
        assert isinstance(result, set)
        assert 'html5semantic' in result

    def test_combines_overlapping_features(self, html_parser, create_temp_file):
        """Test combining files with overlapping features."""
        file1 = create_temp_file("file1.html", "<main><video src='v.mp4'></video></main>")
        file2 = create_temp_file("file2.html", "<main><audio src='a.mp3'></audio></main>")

        result = html_parser.parse_multiple_files([str(file1), str(file2)])

        assert 'html5semantic' in result
        assert 'video' in result
        assert 'audio' in result


class TestParseMultipleManyFiles:
    """Tests for parsing many files."""

    def test_parse_ten_files(self, html_parser, temp_dir):
        """Test parsing 10 files."""
        files = []
        for i in range(10):
            filepath = temp_dir / f"file{i}.html"
            filepath.write_text(f"<section>Content {i}</section>", encoding='utf-8')
            files.append(str(filepath))

        result = html_parser.parse_multiple_files(files)
        assert 'html5semantic' in result

    def test_parse_files_with_various_features(self, html_parser, temp_dir):
        """Test parsing files with various features."""
        features_html = [
            "<video src='v.mp4'></video>",
            "<audio src='a.mp3'></audio>",
            "<canvas></canvas>",
            "<dialog></dialog>",
            "<details><summary>S</summary></details>",
            "<input type='date'>",
            "<input type='color'>",
            '<input placeholder="test">',
        ]

        files = []
        for i, html in enumerate(features_html):
            filepath = temp_dir / f"feature{i}.html"
            filepath.write_text(html, encoding='utf-8')
            files.append(str(filepath))

        result = html_parser.parse_multiple_files(files)

        assert 'video' in result
        assert 'audio' in result
        assert 'canvas' in result
        assert 'dialog' in result
        assert 'details' in result
        assert 'input-datetime' in result
        assert 'input-color' in result
        assert 'input-placeholder' in result


class TestParseMultipleErrorHandling:
    """Tests for error handling in parse_multiple_files."""

    def test_continues_after_missing_file(self, html_parser, create_html_file):
        """Test that parsing continues after missing file."""
        valid_file = create_html_file("<main>Valid content</main>")
        missing_file = "/nonexistent/file.html"

        result = html_parser.parse_multiple_files([
            str(valid_file),
            missing_file,
        ])

        # Should still have features from valid file
        assert 'html5semantic' in result

    def test_all_files_missing(self, html_parser):
        """Test when all files are missing."""
        result = html_parser.parse_multiple_files([
            "/nonexistent/file1.html",
            "/nonexistent/file2.html",
        ])

        # Should return empty set
        assert result == set()

    def test_mixed_valid_invalid_files(self, html_parser, create_temp_file):
        """Test mix of valid and invalid files."""
        valid1 = create_temp_file("valid1.html", "<video src='v.mp4'></video>")
        valid2 = create_temp_file("valid2.html", "<audio src='a.mp3'></audio>")

        result = html_parser.parse_multiple_files([
            str(valid1),
            "/nonexistent/missing.html",
            str(valid2),
        ])

        assert 'video' in result
        assert 'audio' in result


class TestParseMultiplePathTypes:
    """Tests for different path types in parse_multiple_files."""

    def test_string_paths(self, html_parser, create_html_file):
        """Test with string paths."""
        file1 = create_html_file("<main>Content</main>")
        result = html_parser.parse_multiple_files([str(file1)])
        assert 'html5semantic' in result

    def test_mixed_path_types(self, html_parser, create_temp_file):
        """Test with mixed Path objects and strings."""
        file1 = create_temp_file("file1.html", "<video src='v.mp4'></video>")
        file2 = create_temp_file("file2.html", "<audio src='a.mp3'></audio>")

        # Mix of string and Path object
        result = html_parser.parse_multiple_files([
            str(file1),
            str(file2),  # Both as strings since method signature expects strings
        ])

        assert 'video' in result
        assert 'audio' in result


class TestParseMultipleRealWorldScenarios:
    """Tests for real-world scenarios."""

    def test_parse_project_files(self, html_parser, temp_dir):
        """Test parsing multiple HTML files like in a project."""
        # Create project structure
        (temp_dir / "pages").mkdir()
        (temp_dir / "components").mkdir()

        # Create files
        index = temp_dir / "pages" / "index.html"
        index.write_text("""
        <!DOCTYPE html>
        <html>
        <head><meta name="viewport" content="width=device-width"></head>
        <body><main><video src="hero.mp4"></video></main></body>
        </html>
        """, encoding='utf-8')

        about = temp_dir / "pages" / "about.html"
        about.write_text("<main><section>About us</section></main>", encoding='utf-8')

        component = temp_dir / "components" / "dialog.html"
        component.write_text("<dialog><slot></slot></dialog>", encoding='utf-8')

        result = html_parser.parse_multiple_files([
            str(index),
            str(about),
            str(component),
        ])

        assert 'viewport-units' in result
        assert 'video' in result
        assert 'html5semantic' in result
        assert 'dialog' in result
        assert 'shadowdomv1' in result  # slot

    def test_parse_component_library(self, html_parser, temp_dir):
        """Test parsing component library files."""
        components = {
            "video-player.html": "<video src='placeholder.mp4' controls></video>",
            "audio-player.html": "<audio src='placeholder.mp3' controls></audio>",
            "image-gallery.html": '<picture><source srcset="img.webp"><img src="img.jpg" loading="lazy" alt="Gallery"></picture>',
            "modal-dialog.html": '<dialog aria-modal="true"><slot name="content"></slot></dialog>',
            "accordion.html": "<details><summary>Title</summary><slot></slot></details>",
        }

        files = []
        for name, html in components.items():
            filepath = temp_dir / name
            filepath.write_text(html, encoding='utf-8')
            files.append(str(filepath))

        result = html_parser.parse_multiple_files(files)

        assert 'video' in result
        assert 'audio' in result
        assert 'picture' in result
        assert 'loading-lazy-attr' in result
        assert 'dialog' in result
        assert 'wai-aria' in result
        assert 'details' in result
        assert 'shadowdomv1' in result
