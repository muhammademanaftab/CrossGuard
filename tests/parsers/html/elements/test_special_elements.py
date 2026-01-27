"""Tests for special HTML element detection.

Tests elements: canvas, svg, slot, wbr, ruby/rt/rp/rb/rtc, menu, portal, math
"""

import pytest


class TestCanvasElement:
    """Tests for <canvas> element detection."""

    def test_canvas_basic(self, parse_and_check):
        """Test basic canvas element detection."""
        html = '<canvas></canvas>'
        assert parse_and_check(html, 'canvas')

    def test_canvas_with_dimensions(self, parse_and_check):
        """Test canvas element with width and height."""
        html = '<canvas width="500" height="300"></canvas>'
        assert parse_and_check(html, 'canvas')

    def test_canvas_with_id(self, parse_and_check):
        """Test canvas element with id for JavaScript access."""
        html = '<canvas id="myCanvas" width="640" height="480"></canvas>'
        assert parse_and_check(html, 'canvas')

    def test_canvas_with_fallback(self, parse_and_check):
        """Test canvas element with fallback content."""
        html = """
        <canvas id="chart">
            Your browser does not support the canvas element.
        </canvas>
        """
        assert parse_and_check(html, 'canvas')


class TestSvgElement:
    """Tests for <svg> element detection."""

    def test_svg_basic(self, parse_and_check):
        """Test basic SVG element detection."""
        html = '<svg></svg>'
        assert parse_and_check(html, 'svg')

    def test_svg_with_viewbox(self, parse_and_check):
        """Test SVG element with viewBox."""
        html = '<svg viewBox="0 0 100 100"></svg>'
        assert parse_and_check(html, 'svg')

    def test_svg_with_shapes(self, parse_and_check):
        """Test SVG element with shapes."""
        html = """
        <svg width="100" height="100">
            <circle cx="50" cy="50" r="40" fill="red"/>
            <rect x="10" y="10" width="30" height="30" fill="blue"/>
        </svg>
        """
        assert parse_and_check(html, 'svg')

    def test_svg_with_path(self, parse_and_check):
        """Test SVG element with path."""
        html = """
        <svg viewBox="0 0 24 24">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
        """
        assert parse_and_check(html, 'svg')

    def test_svg_inline_icon(self, parse_and_check):
        """Test inline SVG icon."""
        html = """
        <button>
            <svg class="icon" width="24" height="24" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            </svg>
            Submit
        </button>
        """
        assert parse_and_check(html, 'svg')


class TestSlotElement:
    """Tests for <slot> element detection (Shadow DOM)."""

    def test_slot_basic(self, parse_and_check):
        """Test basic slot element detection."""
        html = '<slot></slot>'
        assert parse_and_check(html, 'shadowdomv1')

    def test_slot_named(self, parse_and_check):
        """Test named slot element."""
        html = '<slot name="header"></slot>'
        assert parse_and_check(html, 'shadowdomv1')

    def test_slot_with_fallback(self, parse_and_check):
        """Test slot element with fallback content."""
        html = '<slot name="content">Default content</slot>'
        assert parse_and_check(html, 'shadowdomv1')

    def test_slot_in_template(self, parse_html):
        """Test slot element inside template."""
        html = """
        <template id="my-component">
            <style>:host { display: block; }</style>
            <div class="container">
                <slot name="title">Default Title</slot>
                <slot>Default content</slot>
            </div>
        </template>
        """
        features = parse_html(html)
        assert 'shadowdomv1' in features
        assert 'template' in features


class TestWbrElement:
    """Tests for <wbr> element detection (Word Break Opportunity)."""

    def test_wbr_basic(self, parse_and_check):
        """Test basic wbr element detection."""
        html = '<p>super<wbr>califragilistic<wbr>expialidocious</p>'
        assert parse_and_check(html, 'wbr-element')

    def test_wbr_in_url(self, parse_and_check):
        """Test wbr element in long URL."""
        html = '<p>https://example.com/<wbr>path/<wbr>to/<wbr>resource</p>'
        assert parse_and_check(html, 'wbr-element')

    def test_wbr_in_filename(self, parse_and_check):
        """Test wbr element in long filename."""
        html = '<p>very_long_<wbr>filename_<wbr>with_<wbr>underscores.txt</p>'
        assert parse_and_check(html, 'wbr-element')


class TestRubyElements:
    """Tests for ruby annotation elements."""

    def test_ruby_basic(self, parse_and_check):
        """Test basic ruby element detection."""
        html = '<ruby>kanji<rt>reading</rt></ruby>'
        assert parse_and_check(html, 'ruby')

    def test_ruby_with_rp(self, parse_and_check):
        """Test ruby element with rp fallback."""
        html = """
        <ruby>
            漢<rp>(</rp><rt>kan</rt><rp>)</rp>
            字<rp>(</rp><rt>ji</rt><rp>)</rp>
        </ruby>
        """
        assert parse_and_check(html, 'ruby')

    def test_rt_element(self, parse_and_check):
        """Test rt element detection."""
        html = '<ruby>東京<rt>とうきょう</rt></ruby>'
        assert parse_and_check(html, 'ruby')

    def test_rp_element(self, parse_and_check):
        """Test rp element detection."""
        html = '<ruby>A<rp>(</rp><rt>annotation</rt><rp>)</rp></ruby>'
        assert parse_and_check(html, 'ruby')

    def test_rb_element(self, parse_and_check):
        """Test rb element detection."""
        html = '<ruby><rb>base</rb><rt>annotation</rt></ruby>'
        assert parse_and_check(html, 'ruby')

    def test_rtc_element(self, parse_and_check):
        """Test rtc element detection (ruby text container)."""
        html = """
        <ruby>
            <rb>旧</rb><rb>金</rb><rb>山</rb>
            <rtc><rt>jiù</rt><rt>jīn</rt><rt>shān</rt></rtc>
            <rtc><rt>San Francisco</rt></rtc>
        </ruby>
        """
        assert parse_and_check(html, 'ruby')

    def test_ruby_japanese_text(self, parse_and_check):
        """Test ruby element with Japanese text."""
        html = """
        <ruby>
            日本語<rt>にほんご</rt>
        </ruby>
        """
        assert parse_and_check(html, 'ruby')


class TestMenuElement:
    """Tests for <menu> element detection."""

    def test_menu_basic(self, parse_and_check):
        """Test basic menu element detection."""
        html = '<menu></menu>'
        assert parse_and_check(html, 'menu')

    def test_menu_with_items(self, parse_and_check):
        """Test menu element with list items."""
        html = """
        <menu>
            <li><button>Cut</button></li>
            <li><button>Copy</button></li>
            <li><button>Paste</button></li>
        </menu>
        """
        assert parse_and_check(html, 'menu')

    def test_menu_type_toolbar(self, parse_and_check):
        """Test menu element with type toolbar."""
        html = """
        <menu type="toolbar">
            <li><button>Bold</button></li>
            <li><button>Italic</button></li>
        </menu>
        """
        assert parse_and_check(html, 'menu')


class TestPortalElement:
    """Tests for <portal> element detection (prerendering)."""

    def test_portal_basic(self, parse_and_check):
        """Test basic portal element detection."""
        html = '<portal src="https://example.com"></portal>'
        assert parse_and_check(html, 'portals')

    def test_portal_with_id(self, parse_and_check):
        """Test portal element with id."""
        html = '<portal id="preview" src="https://example.com/page"></portal>'
        assert parse_and_check(html, 'portals')


class TestMathElement:
    """Tests for <math> element detection (MathML)."""

    def test_math_basic(self, parse_and_check):
        """Test basic math element detection."""
        html = '<math></math>'
        assert parse_and_check(html, 'mathml')

    def test_math_simple_equation(self, parse_and_check):
        """Test math element with simple equation."""
        html = """
        <math>
            <mi>x</mi>
            <mo>=</mo>
            <mn>5</mn>
        </math>
        """
        assert parse_and_check(html, 'mathml')

    def test_math_fraction(self, parse_and_check):
        """Test math element with fraction."""
        html = """
        <math>
            <mfrac>
                <mi>a</mi>
                <mi>b</mi>
            </mfrac>
        </math>
        """
        assert parse_and_check(html, 'mathml')

    def test_math_quadratic_formula(self, parse_and_check):
        """Test math element with quadratic formula."""
        html = """
        <math>
            <mi>x</mi>
            <mo>=</mo>
            <mfrac>
                <mrow>
                    <mo>-</mo>
                    <mi>b</mi>
                    <mo>&pm;</mo>
                    <msqrt>
                        <msup><mi>b</mi><mn>2</mn></msup>
                        <mo>-</mo>
                        <mn>4</mn><mi>a</mi><mi>c</mi>
                    </msqrt>
                </mrow>
                <mrow>
                    <mn>2</mn><mi>a</mi>
                </mrow>
            </mfrac>
        </math>
        """
        assert parse_and_check(html, 'mathml')

    def test_math_with_namespace(self, parse_and_check):
        """Test math element with namespace."""
        html = """
        <math xmlns="http://www.w3.org/1998/Math/MathML">
            <mi>y</mi>
            <mo>=</mo>
            <mi>m</mi>
            <mi>x</mi>
            <mo>+</mo>
            <mi>b</mi>
        </math>
        """
        assert parse_and_check(html, 'mathml')


class TestCombinedSpecialElements:
    """Tests for combinations of special elements."""

    def test_all_special_elements(self, parse_html):
        """Test page with multiple special elements."""
        html = """
        <canvas id="chart" width="400" height="300"></canvas>
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg>
        <ruby>漢字<rt>かんじ</rt></ruby>
        <p>Long<wbr>Word</p>
        <math><mi>x</mi><mo>=</mo><mn>5</mn></math>
        """
        features = parse_html(html)
        assert 'canvas' in features
        assert 'svg' in features
        assert 'ruby' in features
        assert 'wbr-element' in features
        assert 'mathml' in features

    def test_web_component_structure(self, parse_html):
        """Test web component structure with template and slot."""
        html = """
        <template id="user-card">
            <style>
                .card { border: 1px solid #ccc; }
            </style>
            <div class="card">
                <slot name="avatar"></slot>
                <slot name="username">Anonymous</slot>
            </div>
        </template>
        """
        features = parse_html(html)
        assert 'template' in features
        assert 'shadowdomv1' in features

    def test_graphics_heavy_page(self, parse_html):
        """Test page with both canvas and svg."""
        html = """
        <div class="dashboard">
            <canvas id="line-chart" width="400" height="200"></canvas>
            <svg class="icon" viewBox="0 0 24 24">
                <path d="M12 2L2 12h3v8h6v-6h2v6h6v-8h3L12 2z"/>
            </svg>
        </div>
        """
        features = parse_html(html)
        assert 'canvas' in features
        assert 'svg' in features


class TestNoSpecialElements:
    """Tests for HTML without special elements."""

    def test_no_special_elements(self, parse_html):
        """Test HTML without any special elements."""
        html = """
        <div>
            <p>Regular paragraph</p>
            <img src="image.jpg" alt="Image">
        </div>
        """
        features = parse_html(html)
        assert 'canvas' not in features
        assert 'svg' not in features
        assert 'ruby' not in features
        assert 'wbr-element' not in features
        assert 'mathml' not in features
        assert 'menu' not in features
        assert 'portals' not in features
