"""Tests for HTMLParser.parse_file() method.

Tests: File parsing, file not found, encoding errors
"""

import pytest
from pathlib import Path


class TestParseFileBasic:
    """Tests for basic parse_file functionality."""

    def test_parse_file_returns_set(self, html_parser, create_html_file):
        """Test that parse_file returns a set."""
        filepath = create_html_file("<main>Content</main>")
        result = html_parser.parse_file(str(filepath))
        assert isinstance(result, set)

    def test_parse_file_finds_features(self, html_parser, create_html_file):
        """Test that parse_file finds features in file."""
        filepath = create_html_file("<main><video src='v.mp4'></video></main>")
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features
        assert 'video' in features

    def test_parse_file_with_path_object(self, html_parser, create_html_file):
        """Test parse_file with Path object."""
        filepath = create_html_file("<dialog>Content</dialog>")
        features = html_parser.parse_file(filepath)  # Path object, not string
        assert 'dialog' in features

    def test_parse_file_empty_file(self, html_parser, create_html_file):
        """Test parsing empty file."""
        filepath = create_html_file("")
        features = html_parser.parse_file(str(filepath))
        assert features == set()


class TestParseFileContent:
    """Tests for parse_file with various content."""

    def test_parse_file_complete_document(self, html_parser, create_html_file):
        """Test parsing complete HTML document."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test</title>
        </head>
        <body>
            <main>
                <video src="video.mp4" controls></video>
            </main>
        </body>
        </html>
        """
        filepath = create_html_file(html)
        features = html_parser.parse_file(str(filepath))
        assert 'viewport-units' in features
        assert 'html5semantic' in features
        assert 'video' in features

    def test_parse_file_fragment(self, html_parser, create_html_file):
        """Test parsing HTML fragment (not complete document)."""
        html = "<main><article><section>Content</section></article></main>"
        filepath = create_html_file(html)
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features

    def test_parse_file_with_unicode(self, html_parser, create_html_file):
        """Test parsing file with Unicode content."""
        html = "<main>Hello 世界 🌍</main>"
        filepath = create_html_file(html)
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features


class TestParseFileNotFound:
    """Tests for parse_file with missing files."""

    def test_file_not_found(self, html_parser):
        """Test FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            html_parser.parse_file("/nonexistent/path/to/file.html")

    def test_file_not_found_message(self, html_parser):
        """Test that FileNotFoundError has useful message."""
        try:
            html_parser.parse_file("/nonexistent/file.html")
        except FileNotFoundError as e:
            assert "file.html" in str(e) or "not found" in str(e).lower()

    def test_directory_instead_of_file(self, html_parser, temp_dir):
        """Test error when path is directory."""
        with pytest.raises((FileNotFoundError, ValueError, IsADirectoryError)):
            html_parser.parse_file(str(temp_dir))


class TestParseFileEncoding:
    """Tests for parse_file encoding handling."""

    def test_utf8_file(self, html_parser, create_html_file):
        """Test UTF-8 encoded file."""
        html = "<main>UTF-8: äöü ñ 中文</main>"
        filepath = create_html_file(html)
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features

    def test_file_with_bom(self, html_parser, temp_dir):
        """Test file with UTF-8 BOM."""
        filepath = temp_dir / "bom.html"
        content = "\ufeff<main>Content with BOM</main>"
        filepath.write_text(content, encoding='utf-8')
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features


class TestParseFileExtensions:
    """Tests for parse_file with various file extensions."""

    def test_html_extension(self, html_parser, create_temp_file):
        """Test .html extension."""
        filepath = create_temp_file("test.html", "<main>Content</main>")
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features

    def test_htm_extension(self, html_parser, create_temp_file):
        """Test .htm extension."""
        filepath = create_temp_file("test.htm", "<main>Content</main>")
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features

    def test_no_extension(self, html_parser, create_temp_file):
        """Test file without extension."""
        filepath = create_temp_file("testfile", "<main>Content</main>")
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features

    def test_other_extension(self, html_parser, create_temp_file):
        """Test file with non-HTML extension but HTML content."""
        filepath = create_temp_file("test.txt", "<main>Content</main>")
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features


class TestParseFilePaths:
    """Tests for parse_file with various path formats."""

    def test_absolute_path(self, html_parser, create_html_file):
        """Test absolute path."""
        filepath = create_html_file("<main>Content</main>")
        abs_path = filepath.absolute()
        features = html_parser.parse_file(str(abs_path))
        assert 'html5semantic' in features

    def test_path_with_spaces(self, html_parser, temp_dir):
        """Test path with spaces in directory/filename."""
        spaced_dir = temp_dir / "path with spaces"
        spaced_dir.mkdir()
        filepath = spaced_dir / "test file.html"
        filepath.write_text("<main>Content</main>", encoding='utf-8')
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features

    def test_path_with_unicode(self, html_parser, temp_dir):
        """Test path with Unicode characters."""
        unicode_dir = temp_dir / "директория"
        unicode_dir.mkdir()
        filepath = unicode_dir / "файл.html"
        filepath.write_text("<main>Content</main>", encoding='utf-8')
        features = html_parser.parse_file(str(filepath))
        assert 'html5semantic' in features


class TestParseFileStateUpdate:
    """Tests for parse_file state updates."""

    def test_elements_found_populated(self, html_parser, create_html_file):
        """Test that elements_found is populated after parse_file."""
        filepath = create_html_file("<main><video src='v.mp4'></video></main>")
        html_parser.parse_file(str(filepath))
        assert len(html_parser.elements_found) > 0

    def test_attributes_found_populated(self, html_parser, create_html_file):
        """Test that attributes_found is populated after parse_file."""
        filepath = create_html_file('<input type="text" placeholder="test" required>')
        html_parser.parse_file(str(filepath))
        assert len(html_parser.attributes_found) > 0

    def test_features_found_populated(self, html_parser, create_html_file):
        """Test that features_found is populated after parse_file."""
        filepath = create_html_file("<main>Content</main>")
        html_parser.parse_file(str(filepath))
        assert 'html5semantic' in html_parser.features_found


class TestParseHtmlFileConvenienceFunction:
    """Tests for parse_html_file convenience function."""

    def test_function_exists(self):
        """Test that parse_html_file function exists."""
        from src.parsers.html_parser import parse_html_file
        assert callable(parse_html_file)

    def test_returns_set(self, create_html_file):
        """Test that parse_html_file returns a set."""
        from src.parsers.html_parser import parse_html_file
        filepath = create_html_file("<main>Content</main>")
        result = parse_html_file(str(filepath))
        assert isinstance(result, set)

    def test_finds_features(self, create_html_file):
        """Test that parse_html_file finds features."""
        from src.parsers.html_parser import parse_html_file
        filepath = create_html_file("<video src='v.mp4'></video>")
        result = parse_html_file(str(filepath))
        assert 'video' in result

    def test_file_not_found(self):
        """Test that parse_html_file raises FileNotFoundError."""
        from src.parsers.html_parser import parse_html_file
        import pytest
        with pytest.raises(FileNotFoundError):
            parse_html_file("/nonexistent/file.html")

    def test_complete_document(self, create_html_file):
        """Test with complete HTML document."""
        from src.parsers.html_parser import parse_html_file
        html = """
        <!DOCTYPE html>
        <html>
        <body>
            <main>
                <dialog>Dialog content</dialog>
            </main>
        </body>
        </html>
        """
        filepath = create_html_file(html)
        result = parse_html_file(str(filepath))
        assert 'html5semantic' in result
        assert 'dialog' in result
