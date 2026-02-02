"""Tests for Web Worker features.

Tests features: webworkers, sharedworkers, serviceworkers,
                websockets, eventsource, broadcastchannel
"""

import pytest


class TestWebWorkers:
    """Tests for Web Workers detection."""

    def test_new_worker(self, parse_and_check):
        """Test new Worker."""
        js = "const worker = new Worker('worker.js');"
        assert parse_and_check(js, 'webworkers')

    def test_worker_post_message(self, parse_and_check):
        """Test Worker with postMessage."""
        js = """
        const worker = new Worker('worker.js');
        worker.postMessage({ data: 'hello' });
        worker.onmessage = e => console.log(e.data);
        """
        assert parse_and_check(js, 'webworkers')


class TestSharedWorkers:
    """Tests for Shared Workers detection."""

    def test_new_shared_worker(self, parse_and_check):
        """Test new SharedWorker."""
        js = "const worker = new SharedWorker('shared.js');"
        assert parse_and_check(js, 'sharedworkers')

    def test_shared_worker_port(self, parse_and_check):
        """Test SharedWorker port."""
        js = """
        const sw = new SharedWorker('shared.js');
        sw.port.start();
        sw.port.postMessage('hello');
        """
        assert parse_and_check(js, 'sharedworkers')


class TestServiceWorkers:
    """Tests for Service Workers detection."""

    def test_service_worker_register(self, parse_and_check):
        """Test navigator.serviceWorker.register()."""
        js = "navigator.serviceWorker.register('/sw.js');"
        assert parse_and_check(js, 'serviceworkers')

    def test_service_worker_check(self, parse_and_check):
        """Test serviceWorker feature detection."""
        js = """
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }
        """
        assert parse_and_check(js, 'serviceworkers')


class TestWebSockets:
    """Tests for WebSocket detection."""

    def test_new_websocket(self, parse_and_check):
        """Test new WebSocket."""
        js = "const socket = new WebSocket('wss://example.com');"
        assert parse_and_check(js, 'websockets')

    def test_websocket_events(self, parse_and_check):
        """Test WebSocket event handlers."""
        js = """
        const ws = new WebSocket('wss://example.com');
        ws.onopen = () => ws.send('Hello');
        ws.onmessage = e => console.log(e.data);
        ws.onclose = () => console.log('Closed');
        """
        assert parse_and_check(js, 'websockets')


class TestEventSource:
    """Tests for EventSource/SSE detection."""

    def test_new_event_source(self, parse_and_check):
        """Test new EventSource."""
        js = "const source = new EventSource('/events');"
        assert parse_and_check(js, 'eventsource')

    def test_event_source_handlers(self, parse_and_check):
        """Test EventSource event handlers."""
        js = """
        const es = new EventSource('/events');
        es.onmessage = e => console.log(e.data);
        es.onerror = () => console.error('SSE error');
        """
        assert parse_and_check(js, 'eventsource')


class TestBroadcastChannel:
    """Tests for BroadcastChannel detection."""

    def test_new_broadcast_channel(self, parse_and_check):
        """Test new BroadcastChannel."""
        js = "const channel = new BroadcastChannel('my-channel');"
        assert parse_and_check(js, 'broadcastchannel')

    def test_broadcast_channel_message(self, parse_and_check):
        """Test BroadcastChannel messaging."""
        js = """
        const bc = new BroadcastChannel('channel');
        bc.postMessage({ type: 'update' });
        bc.onmessage = e => console.log(e.data);
        """
        assert parse_and_check(js, 'broadcastchannel')
