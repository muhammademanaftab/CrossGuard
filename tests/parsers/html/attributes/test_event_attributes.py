"""Tests for HTML5 event attribute detection.

Tests attributes: oninput, ontouchstart/move/end, onpointerdown/up/move,
                  onfocusin/out, onhashchange, onpageshow/hide, onbeforeprint/afterprint
"""

import pytest


class TestInputEventAttribute:
    """Tests for oninput event attribute detection."""

    def test_oninput_on_input(self, parse_and_check):
        """Test oninput on input element."""
        html = '<input type="text" oninput="handleInput()">'
        assert parse_and_check(html, 'input-event')

    def test_oninput_on_textarea(self, parse_and_check):
        """Test oninput on textarea element."""
        html = '<textarea oninput="updatePreview()"></textarea>'
        assert parse_and_check(html, 'input-event')

    def test_oninput_with_inline_code(self, parse_and_check):
        """Test oninput with inline JavaScript."""
        html = '<input type="text" oninput="this.value = this.value.toUpperCase()">'
        assert parse_and_check(html, 'input-event')

    def test_oninput_range_slider(self, parse_and_check):
        """Test oninput on range input for real-time updates."""
        html = '<input type="range" oninput="output.value = this.value">'
        assert parse_and_check(html, 'input-event')


class TestTouchEventAttributes:
    """Tests for touch event attribute detection."""

    def test_ontouchstart(self, parse_and_check):
        """Test ontouchstart attribute."""
        html = '<div ontouchstart="handleTouchStart(event)">Touch me</div>'
        assert parse_and_check(html, 'touch')

    def test_ontouchmove(self, parse_and_check):
        """Test ontouchmove attribute."""
        html = '<div ontouchmove="handleTouchMove(event)">Swipe area</div>'
        assert parse_and_check(html, 'touch')

    def test_ontouchend(self, parse_and_check):
        """Test ontouchend attribute."""
        html = '<div ontouchend="handleTouchEnd(event)">Touch area</div>'
        assert parse_and_check(html, 'touch')

    def test_ontouchcancel(self, parse_and_check):
        """Test ontouchcancel attribute."""
        html = '<div ontouchcancel="handleTouchCancel()">Touch area</div>'
        assert parse_and_check(html, 'touch')

    def test_all_touch_events(self, parse_html):
        """Test element with all touch events."""
        html = '''
        <div ontouchstart="start()"
             ontouchmove="move()"
             ontouchend="end()"
             ontouchcancel="cancel()">
            Touch Area
        </div>
        '''
        features = parse_html(html)
        assert 'touch' in features

    def test_touch_swipe_element(self, parse_and_check):
        """Test touch events for swipe gesture."""
        html = '''
        <div class="carousel"
             ontouchstart="recordStart(event)"
             ontouchend="handleSwipe(event)">
            Swipeable content
        </div>
        '''
        assert parse_and_check(html, 'touch')


class TestPointerEventAttributes:
    """Tests for pointer event attribute detection."""

    def test_onpointerdown(self, parse_and_check):
        """Test onpointerdown attribute."""
        html = '<button onpointerdown="handlePointerDown()">Press</button>'
        assert parse_and_check(html, 'pointer')

    def test_onpointermove(self, parse_and_check):
        """Test onpointermove attribute."""
        html = '<canvas onpointermove="draw(event)"></canvas>'
        assert parse_and_check(html, 'pointer')

    def test_onpointerup(self, parse_and_check):
        """Test onpointerup attribute."""
        html = '<button onpointerup="handleRelease()">Release</button>'
        assert parse_and_check(html, 'pointer')

    def test_onpointercancel(self, parse_and_check):
        """Test onpointercancel attribute."""
        html = '<div onpointercancel="handleCancel()">Interactive</div>'
        assert parse_and_check(html, 'pointer')

    def test_onpointerenter(self, parse_and_check):
        """Test onpointerenter attribute."""
        html = '<div onpointerenter="highlight()">Hover area</div>'
        assert parse_and_check(html, 'pointer')

    def test_onpointerleave(self, parse_and_check):
        """Test onpointerleave attribute."""
        html = '<div onpointerleave="unhighlight()">Hover area</div>'
        assert parse_and_check(html, 'pointer')

    def test_onpointerover(self, parse_and_check):
        """Test onpointerover attribute."""
        html = '<div onpointerover="showTooltip()">Info</div>'
        assert parse_and_check(html, 'pointer')

    def test_onpointerout(self, parse_and_check):
        """Test onpointerout attribute."""
        html = '<div onpointerout="hideTooltip()">Info</div>'
        assert parse_and_check(html, 'pointer')

    def test_ongotpointercapture(self, parse_and_check):
        """Test ongotpointercapture attribute."""
        html = '<div ongotpointercapture="onCapture()">Capture</div>'
        assert parse_and_check(html, 'pointer')

    def test_onlostpointercapture(self, parse_and_check):
        """Test onlostpointercapture attribute."""
        html = '<div onlostpointercapture="onRelease()">Release</div>'
        assert parse_and_check(html, 'pointer')

    def test_drawing_canvas(self, parse_html):
        """Test pointer events for drawing canvas."""
        html = '''
        <canvas id="draw"
                onpointerdown="startDraw(event)"
                onpointermove="draw(event)"
                onpointerup="endDraw(event)">
        </canvas>
        '''
        features = parse_html(html)
        assert 'pointer' in features


class TestFocusEventAttributes:
    """Tests for focus event attribute detection."""

    def test_onfocusin(self, parse_and_check):
        """Test onfocusin attribute."""
        html = '<input type="text" onfocusin="showHelper()">'
        assert parse_and_check(html, 'focusin-focusout-events')

    def test_onfocusout(self, parse_and_check):
        """Test onfocusout attribute."""
        html = '<input type="text" onfocusout="validate()">'
        assert parse_and_check(html, 'focusin-focusout-events')

    def test_focus_events_on_form(self, parse_html):
        """Test focus events on form for delegation."""
        html = '''
        <form onfocusin="showFieldHelp(event)"
              onfocusout="validateField(event)">
            <input type="text" name="name">
            <input type="email" name="email">
        </form>
        '''
        features = parse_html(html)
        assert 'focusin-focusout-events' in features


class TestHashchangeEventAttribute:
    """Tests for onhashchange event attribute detection."""

    def test_onhashchange_on_body(self, parse_and_check):
        """Test onhashchange on body element."""
        html = '<body onhashchange="handleHashChange()"></body>'
        assert parse_and_check(html, 'hashchange')

    def test_onhashchange_spa_routing(self, parse_and_check):
        """Test onhashchange for SPA routing."""
        html = '''
        <body onhashchange="router.navigate(location.hash)">
            <nav>
                <a href="#home">Home</a>
                <a href="#about">About</a>
            </nav>
        </body>
        '''
        assert parse_and_check(html, 'hashchange')


class TestPageTransitionEventAttributes:
    """Tests for page transition event attribute detection."""

    def test_onpageshow(self, parse_and_check):
        """Test onpageshow attribute."""
        html = '<body onpageshow="onPageShow(event)"></body>'
        assert parse_and_check(html, 'page-transition-events')

    def test_onpagehide(self, parse_and_check):
        """Test onpagehide attribute."""
        html = '<body onpagehide="saveState()"></body>'
        assert parse_and_check(html, 'page-transition-events')

    def test_page_transitions_bfcache(self, parse_html):
        """Test page transition events for bfcache handling."""
        html = '''
        <body onpageshow="if(event.persisted) refreshContent()"
              onpagehide="saveFormData()">
        </body>
        '''
        features = parse_html(html)
        assert 'page-transition-events' in features


class TestPrintEventAttributes:
    """Tests for print event attribute detection."""

    def test_onbeforeprint(self, parse_and_check):
        """Test onbeforeprint attribute."""
        html = '<body onbeforeprint="prepareForPrint()"></body>'
        assert parse_and_check(html, 'beforeafterprint')

    def test_onafterprint(self, parse_and_check):
        """Test onafterprint attribute."""
        html = '<body onafterprint="restoreAfterPrint()"></body>'
        assert parse_and_check(html, 'beforeafterprint')

    def test_print_events_for_layout(self, parse_html):
        """Test print events for layout adjustments."""
        html = '''
        <body onbeforeprint="showPrintVersion()"
              onafterprint="showScreenVersion()">
        </body>
        '''
        features = parse_html(html)
        assert 'beforeafterprint' in features


class TestCombinedEventAttributes:
    """Tests for combined event attributes."""

    def test_interactive_element(self, parse_html):
        """Test element with multiple event types."""
        html = '''
        <div class="interactive"
             ontouchstart="touchStart()"
             onpointerdown="pointerDown()"
             onfocusin="focusIn()">
            Interactive content
        </div>
        '''
        features = parse_html(html)
        assert 'touch' in features
        assert 'pointer' in features
        assert 'focusin-focusout-events' in features

    def test_spa_body(self, parse_html):
        """Test SPA body with multiple events."""
        html = '''
        <body onhashchange="route()"
              onpageshow="restore()"
              onpagehide="save()"
              onbeforeprint="printMode()"
              onafterprint="screenMode()">
        </body>
        '''
        features = parse_html(html)
        assert 'hashchange' in features
        assert 'page-transition-events' in features
        assert 'beforeafterprint' in features

    def test_form_with_input_event(self, parse_html):
        """Test form with input and focus events."""
        html = '''
        <form onfocusin="highlight(event.target)"
              onfocusout="validate(event.target)">
            <input type="text" oninput="updateCount()">
            <textarea oninput="updatePreview()"></textarea>
        </form>
        '''
        features = parse_html(html)
        assert 'input-event' in features
        assert 'focusin-focusout-events' in features


class TestNoEventAttributes:
    """Tests for HTML without event attributes."""

    def test_no_event_attributes(self, parse_html):
        """Test HTML without event attributes."""
        html = """
        <div>
            <input type="text">
            <button>Click</button>
        </div>
        """
        features = parse_html(html)
        assert 'input-event' not in features
        assert 'touch' not in features
        assert 'pointer' not in features
        assert 'focusin-focusout-events' not in features

    def test_common_events_not_tracked(self, parse_html):
        """Test that common events like onclick are not tracked."""
        html = '<button onclick="doSomething()">Click</button>'
        features = parse_html(html)
        # onclick is basic, not tracked as special feature
        assert 'touch' not in features
        assert 'pointer' not in features
