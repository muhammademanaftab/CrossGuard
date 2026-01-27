"""Tests for HTML5 semantic element detection.

Tests elements: main, section, article, aside, header, footer, nav, figure, figcaption, time, mark
All map to feature ID: html5semantic
"""

import pytest


class TestMainElement:
    """Tests for <main> element detection."""

    def test_main_basic(self, parse_and_check):
        """Test basic main element detection."""
        html = "<main>Content</main>"
        assert parse_and_check(html, 'html5semantic')

    def test_main_with_attributes(self, parse_and_check):
        """Test main element with attributes."""
        html = '<main id="content" class="main-area">Content</main>'
        assert parse_and_check(html, 'html5semantic')

    def test_main_nested_content(self, parse_and_check):
        """Test main element with nested content."""
        html = """
        <main>
            <h1>Title</h1>
            <p>Paragraph</p>
        </main>
        """
        assert parse_and_check(html, 'html5semantic')


class TestSectionElement:
    """Tests for <section> element detection."""

    def test_section_basic(self, parse_and_check):
        """Test basic section element detection."""
        html = "<section>Content</section>"
        assert parse_and_check(html, 'html5semantic')

    def test_section_with_heading(self, parse_and_check):
        """Test section element with heading."""
        html = """
        <section>
            <h2>Section Title</h2>
            <p>Section content</p>
        </section>
        """
        assert parse_and_check(html, 'html5semantic')

    def test_multiple_sections(self, parse_html):
        """Test multiple section elements."""
        html = """
        <section>First</section>
        <section>Second</section>
        <section>Third</section>
        """
        features = parse_html(html)
        assert 'html5semantic' in features


class TestArticleElement:
    """Tests for <article> element detection."""

    def test_article_basic(self, parse_and_check):
        """Test basic article element detection."""
        html = "<article>Blog post content</article>"
        assert parse_and_check(html, 'html5semantic')

    def test_article_complete(self, parse_and_check):
        """Test article element with complete structure."""
        html = """
        <article>
            <header>
                <h1>Article Title</h1>
                <time datetime="2024-01-15">January 15, 2024</time>
            </header>
            <p>Article content here.</p>
            <footer>
                <p>Author info</p>
            </footer>
        </article>
        """
        assert parse_and_check(html, 'html5semantic')

    def test_nested_articles(self, parse_and_check):
        """Test nested article elements (comments in article)."""
        html = """
        <article>
            <h1>Main Article</h1>
            <p>Content</p>
            <article>
                <h2>Comment</h2>
                <p>Comment content</p>
            </article>
        </article>
        """
        assert parse_and_check(html, 'html5semantic')


class TestAsideElement:
    """Tests for <aside> element detection."""

    def test_aside_basic(self, parse_and_check):
        """Test basic aside element detection."""
        html = "<aside>Sidebar content</aside>"
        assert parse_and_check(html, 'html5semantic')

    def test_aside_with_content(self, parse_and_check):
        """Test aside element with various content."""
        html = """
        <aside>
            <h3>Related Links</h3>
            <ul>
                <li><a href="#">Link 1</a></li>
                <li><a href="#">Link 2</a></li>
            </ul>
        </aside>
        """
        assert parse_and_check(html, 'html5semantic')


class TestHeaderElement:
    """Tests for <header> element detection."""

    def test_header_basic(self, parse_and_check):
        """Test basic header element detection."""
        html = "<header>Header content</header>"
        assert parse_and_check(html, 'html5semantic')

    def test_header_with_nav(self, parse_and_check):
        """Test header element with navigation."""
        html = """
        <header>
            <h1>Site Title</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
            </nav>
        </header>
        """
        assert parse_and_check(html, 'html5semantic')


class TestFooterElement:
    """Tests for <footer> element detection."""

    def test_footer_basic(self, parse_and_check):
        """Test basic footer element detection."""
        html = "<footer>Footer content</footer>"
        assert parse_and_check(html, 'html5semantic')

    def test_footer_with_copyright(self, parse_and_check):
        """Test footer element with copyright info."""
        html = """
        <footer>
            <p>&copy; 2024 Company Name</p>
            <nav>
                <a href="/privacy">Privacy</a>
                <a href="/terms">Terms</a>
            </nav>
        </footer>
        """
        assert parse_and_check(html, 'html5semantic')


class TestNavElement:
    """Tests for <nav> element detection."""

    def test_nav_basic(self, parse_and_check):
        """Test basic nav element detection."""
        html = "<nav><a href='/'>Home</a></nav>"
        assert parse_and_check(html, 'html5semantic')

    def test_nav_with_list(self, parse_and_check):
        """Test nav element with unordered list."""
        html = """
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
        """
        assert parse_and_check(html, 'html5semantic')


class TestFigureElement:
    """Tests for <figure> element detection."""

    def test_figure_basic(self, parse_and_check):
        """Test basic figure element detection."""
        html = "<figure><img src='img.jpg' alt='test'></figure>"
        assert parse_and_check(html, 'html5semantic')

    def test_figure_with_caption(self, parse_and_check):
        """Test figure element with figcaption."""
        html = """
        <figure>
            <img src="photo.jpg" alt="A photo">
            <figcaption>Caption for the photo</figcaption>
        </figure>
        """
        assert parse_and_check(html, 'html5semantic')

    def test_figure_with_code(self, parse_and_check):
        """Test figure element wrapping code."""
        html = """
        <figure>
            <pre><code>console.log('Hello');</code></pre>
            <figcaption>Example code</figcaption>
        </figure>
        """
        assert parse_and_check(html, 'html5semantic')


class TestFigcaptionElement:
    """Tests for <figcaption> element detection."""

    def test_figcaption_basic(self, parse_and_check):
        """Test basic figcaption element detection."""
        html = "<figure><figcaption>Caption</figcaption></figure>"
        assert parse_and_check(html, 'html5semantic')

    def test_figcaption_at_start(self, parse_and_check):
        """Test figcaption at start of figure."""
        html = """
        <figure>
            <figcaption>Caption first</figcaption>
            <img src="img.jpg" alt="test">
        </figure>
        """
        assert parse_and_check(html, 'html5semantic')


class TestTimeElement:
    """Tests for <time> element detection."""

    def test_time_basic(self, parse_and_check):
        """Test basic time element detection."""
        html = "<time>January 15, 2024</time>"
        assert parse_and_check(html, 'html5semantic')

    def test_time_with_datetime(self, parse_and_check):
        """Test time element with datetime attribute."""
        html = '<time datetime="2024-01-15">January 15, 2024</time>'
        assert parse_and_check(html, 'html5semantic')

    def test_time_with_datetime_time(self, parse_and_check):
        """Test time element with date and time."""
        html = '<time datetime="2024-01-15T14:30:00">3:30 PM on Jan 15</time>'
        assert parse_and_check(html, 'html5semantic')

    def test_time_duration(self, parse_and_check):
        """Test time element with duration."""
        html = '<time datetime="PT2H30M">2 hours 30 minutes</time>'
        assert parse_and_check(html, 'html5semantic')


class TestMarkElement:
    """Tests for <mark> element detection."""

    def test_mark_basic(self, parse_and_check):
        """Test basic mark element detection."""
        html = "<p>This is <mark>highlighted</mark> text.</p>"
        assert parse_and_check(html, 'html5semantic')

    def test_mark_multiple(self, parse_and_check):
        """Test multiple mark elements."""
        html = "<p><mark>First</mark> and <mark>second</mark> highlights.</p>"
        assert parse_and_check(html, 'html5semantic')


class TestCombinedSemanticElements:
    """Tests for combinations of semantic elements."""

    def test_full_page_structure(self, parse_html):
        """Test complete page structure with multiple semantic elements."""
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            <header>
                <nav>
                    <a href="/">Home</a>
                </nav>
            </header>
            <main>
                <article>
                    <header>
                        <h1>Article Title</h1>
                        <time datetime="2024-01-15">Jan 15</time>
                    </header>
                    <section>
                        <p>Content with <mark>highlight</mark></p>
                        <figure>
                            <img src="img.jpg" alt="test">
                            <figcaption>Caption</figcaption>
                        </figure>
                    </section>
                </article>
                <aside>
                    <h2>Related</h2>
                </aside>
            </main>
            <footer>
                <p>Copyright</p>
            </footer>
        </body>
        </html>
        """
        features = parse_html(html)
        assert 'html5semantic' in features

    def test_all_semantic_elements_together(self, parse_html):
        """Test that page with all semantic elements is detected."""
        html = """
        <main></main>
        <section></section>
        <article></article>
        <aside></aside>
        <header></header>
        <footer></footer>
        <nav></nav>
        <figure></figure>
        <figcaption></figcaption>
        <time></time>
        <mark></mark>
        """
        features = parse_html(html)
        assert 'html5semantic' in features


class TestNoSemanticElements:
    """Tests for HTML without semantic elements."""

    def test_no_semantic_elements(self, parse_html):
        """Test HTML without any semantic elements."""
        html = """
        <div>
            <div class="header">Header</div>
            <div class="content">Content</div>
            <div class="footer">Footer</div>
        </div>
        """
        features = parse_html(html)
        assert 'html5semantic' not in features

    def test_empty_html(self, parse_html):
        """Test empty HTML document."""
        html = "<!DOCTYPE html><html><head></head><body></body></html>"
        features = parse_html(html)
        assert 'html5semantic' not in features
