"""Tests for Modern Web API features.

Tests features: webgl, webgl2, webgpu, rtcpeerconnection, web-animation,
                view-transitions, web-share, notifications, clipboard,
                history, matchmedia, getcomputedstyle
"""

import pytest


class TestWebGL:
    """Tests for WebGL detection.

    Note: String content is stripped during parsing, so use
    WebGLRenderingContext instead of getContext("webgl").
    """

    def test_webgl_rendering_context(self, parse_and_check):
        """Test WebGLRenderingContext."""
        js = "const ctx = new WebGLRenderingContext();"
        assert parse_and_check(js, 'webgl')

    def test_webgl_context_reference(self, parse_and_check):
        """Test WebGLRenderingContext type check."""
        js = "if (gl instanceof WebGLRenderingContext) {}"
        assert parse_and_check(js, 'webgl')


class TestWebGL2:
    """Tests for WebGL 2 detection."""

    def test_webgl2_rendering_context(self, parse_and_check):
        """Test WebGL2RenderingContext."""
        js = "const ctx = new WebGL2RenderingContext();"
        assert parse_and_check(js, 'webgl2')

    def test_webgl2_context_reference(self, parse_and_check):
        """Test WebGL2RenderingContext type check."""
        js = "if (gl instanceof WebGL2RenderingContext) {}"
        assert parse_and_check(js, 'webgl2')


class TestWebGPU:
    """Tests for WebGPU detection."""

    def test_webgpu_adapter(self, parse_and_check):
        """Test navigator.gpu."""
        js = "const adapter = await navigator.gpu.requestAdapter();"
        assert parse_and_check(js, 'webgpu')


class TestRTCPeerConnection:
    """Tests for WebRTC detection."""

    def test_rtc_peer_connection(self, parse_and_check):
        """Test RTCPeerConnection."""
        js = "const pc = new RTCPeerConnection(config);"
        assert parse_and_check(js, 'rtcpeerconnection')


class TestWebAnimation:
    """Tests for Web Animations API detection."""

    def test_element_animate(self, parse_and_check):
        """Test element.animate()."""
        js = "element.animate([{ opacity: 0 }, { opacity: 1 }], 1000);"
        assert parse_and_check(js, 'web-animation')

    def test_animation_object(self, parse_and_check):
        """Test Animation object."""
        js = "const anim = new Animation(keyframeEffect);"
        assert parse_and_check(js, 'web-animation')


class TestViewTransitions:
    """Tests for View Transitions API detection."""

    def test_start_view_transition(self, parse_and_check):
        """Test document.startViewTransition()."""
        js = "document.startViewTransition(() => updateDOM());"
        assert parse_and_check(js, 'view-transitions')


class TestWebShare:
    """Tests for Web Share API detection."""

    def test_navigator_share(self, parse_and_check):
        """Test navigator.share()."""
        js = "navigator.share({ title: 'Title', url: 'https://example.com' });"
        assert parse_and_check(js, 'web-share')


class TestNotifications:
    """Tests for Notifications API detection."""

    def test_new_notification(self, parse_and_check):
        """Test new Notification."""
        js = "const notification = new Notification('Hello', { body: 'World' });"
        assert parse_and_check(js, 'notifications')

    def test_notification_permission(self, parse_and_check):
        """Test Notification.permission."""
        js = "if (Notification.permission === 'granted') {}"
        assert parse_and_check(js, 'notifications')


class TestClipboard:
    """Tests for Clipboard API detection."""

    def test_clipboard_write_text(self, parse_and_check):
        """Test navigator.clipboard.writeText()."""
        js = "navigator.clipboard.writeText('copied text');"
        assert parse_and_check(js, 'clipboard')

    def test_clipboard_read_text(self, parse_and_check):
        """Test navigator.clipboard.readText()."""
        js = "const text = await navigator.clipboard.readText();"
        assert parse_and_check(js, 'clipboard')


class TestAsyncClipboard:
    """Tests for Async Clipboard API detection."""

    def test_clipboard_read(self, parse_and_check):
        """Test navigator.clipboard.read()."""
        js = "const items = await navigator.clipboard.read();"
        assert parse_and_check(js, 'async-clipboard')


class TestHistory:
    """Tests for History API detection.

    Note: Pattern detects pushState, replaceState, onpopstate.
    """

    def test_push_state(self, parse_and_check):
        """Test history.pushState()."""
        js = "history.pushState({ page: 1 }, 'Title', '/page1');"
        assert parse_and_check(js, 'history')

    def test_replace_state(self, parse_and_check):
        """Test history.replaceState()."""
        js = "history.replaceState({}, '', '/new-url');"
        assert parse_and_check(js, 'history')

    def test_onpopstate(self, parse_and_check):
        """Test onpopstate event handler."""
        js = "window.onpopstate = function(event) { console.log(event); };"
        assert parse_and_check(js, 'history')


class TestMatchMedia:
    """Tests for matchMedia detection."""

    def test_match_media(self, parse_and_check):
        """Test window.matchMedia()."""
        js = "const mq = window.matchMedia('(prefers-color-scheme: dark)');"
        assert parse_and_check(js, 'matchmedia')

    def test_match_media_query(self, parse_and_check):
        """Test matchMedia with change listener."""
        js = """
        const mq = matchMedia('(max-width: 600px)');
        mq.addEventListener('change', handler);
        """
        assert parse_and_check(js, 'matchmedia')


class TestGetComputedStyle:
    """Tests for getComputedStyle detection."""

    def test_get_computed_style(self, parse_and_check):
        """Test getComputedStyle()."""
        js = "const styles = getComputedStyle(element);"
        assert parse_and_check(js, 'getcomputedstyle')

    def test_window_get_computed_style(self, parse_and_check):
        """Test window.getComputedStyle()."""
        js = "const color = window.getComputedStyle(el).color;"
        assert parse_and_check(js, 'getcomputedstyle')
