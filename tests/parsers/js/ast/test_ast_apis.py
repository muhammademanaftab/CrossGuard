"""Tier 2 tests: AST API detection.

Tests that tree-sitter correctly identifies API features from
constructor calls, function calls, member expressions, and identifiers.
"""

import pytest


class TestASTNewExpressions:
    """Constructor call detection via AST."""

    def test_new_promise(self, parse_and_check):
        assert parse_and_check("new Promise((resolve) => resolve());", 'promises')

    def test_new_worker(self, parse_and_check):
        assert parse_and_check("const w = new Worker('worker.js');", 'webworkers')

    def test_new_websocket(self, parse_and_check):
        assert parse_and_check("const ws = new WebSocket('ws://host');", 'websockets')

    def test_new_intersection_observer(self, parse_and_check):
        assert parse_and_check("new IntersectionObserver(cb);", 'intersectionobserver')

    def test_new_mutation_observer(self, parse_and_check):
        assert parse_and_check("new MutationObserver(cb);", 'mutationobserver')

    def test_new_resize_observer(self, parse_and_check):
        assert parse_and_check("new ResizeObserver(cb);", 'resizeobserver')

    def test_new_broadcast_channel(self, parse_and_check):
        assert parse_and_check("new BroadcastChannel('ch');", 'broadcastchannel')

    def test_new_abort_controller(self, parse_and_check):
        assert parse_and_check("const ctrl = new AbortController();", 'abortcontroller')

    def test_new_url(self, parse_and_check):
        assert parse_and_check("const u = new URL('https://example.com');", 'url')

    def test_new_text_encoder(self, parse_and_check):
        assert parse_and_check("const enc = new TextEncoder();", 'textencoder')

    def test_new_text_decoder(self, parse_and_check):
        assert parse_and_check("const dec = new TextDecoder();", 'textencoder')

    def test_new_blob(self, parse_and_check):
        assert parse_and_check("new Blob(['data']);", 'blobbuilder')

    def test_new_custom_event(self, parse_and_check):
        assert parse_and_check("new CustomEvent('test');", 'customevent')

    def test_new_map(self, parse_and_check):
        assert parse_and_check("const m = new Map();", 'es6')

    def test_new_set(self, parse_and_check):
        assert parse_and_check("const s = new Set();", 'es6')


class TestASTCallExpressions:
    """Direct function call detection via AST."""

    def test_fetch(self, parse_and_check):
        assert parse_and_check("fetch('/api/data');", 'fetch')

    def test_request_animation_frame(self, parse_and_check):
        assert parse_and_check("requestAnimationFrame(loop);", 'requestanimationframe')

    def test_request_idle_callback(self, parse_and_check):
        assert parse_and_check("requestIdleCallback(cb);", 'requestidlecallback')

    def test_atob(self, parse_and_check):
        assert parse_and_check("const x = atob(encoded);", 'atob-btoa')

    def test_btoa(self, parse_and_check):
        assert parse_and_check("const x = btoa(data);", 'atob-btoa')

    def test_match_media(self, parse_and_check):
        assert parse_and_check("matchMedia('(max-width: 600px)');", 'matchmedia')

    def test_create_image_bitmap(self, parse_and_check):
        assert parse_and_check("createImageBitmap(img);", 'createimagebitmap')


class TestASTMemberExpressions:
    """Member expression detection via AST."""

    def test_navigator_geolocation(self, parse_and_check):
        assert parse_and_check("navigator.geolocation.getCurrentPosition(cb);", 'geolocation')

    def test_navigator_service_worker(self, parse_and_check):
        assert parse_and_check("navigator.serviceWorker.register('/sw.js');", 'serviceworkers')

    def test_navigator_clipboard(self, parse_and_check):
        assert parse_and_check("navigator.clipboard.writeText('hi');", 'clipboard')

    def test_crypto_subtle(self, parse_and_check):
        assert parse_and_check("crypto.subtle.encrypt(algo, key, data);", 'cryptography')

    def test_document_hidden(self, parse_and_check):
        assert parse_and_check("if (document.hidden) { /* pause */ }", 'pagevisibility')

    def test_history_push_state(self, parse_and_check):
        assert parse_and_check("history.pushState({}, '', '/new');", 'history')

    def test_performance_now(self, parse_and_check):
        assert parse_and_check("const t = performance.now();", 'high-resolution-time')

    def test_promise_all(self, parse_and_check):
        assert parse_and_check("Promise.all([p1, p2]);", 'promises')

    def test_object_entries(self, parse_and_check):
        assert parse_and_check("Object.entries(obj);", 'object-entries')

    def test_object_values(self, parse_and_check):
        assert parse_and_check("Object.values(obj);", 'object-values')

    def test_navigator_share(self, parse_and_check):
        assert parse_and_check("navigator.share({ title: 'Hi' });", 'web-share')

    def test_navigator_gpu(self, parse_and_check):
        assert parse_and_check("const adapter = navigator.gpu.requestAdapter();", 'webgpu')

    def test_css_supports(self, parse_and_check):
        assert parse_and_check("CSS.supports('display', 'grid');", 'css-supports-api')


class TestASTIdentifiers:
    """Standalone identifier detection via AST."""

    def test_shared_array_buffer(self, parse_and_check):
        assert parse_and_check("const buf = SharedArrayBuffer;", 'sharedarraybuffer')

    def test_readable_stream(self, parse_and_check):
        assert parse_and_check("const s = new ReadableStream({});", 'stream')

    def test_writable_stream(self, parse_and_check):
        assert parse_and_check("const s = new WritableStream({});", 'stream')

    def test_speech_recognition(self, parse_and_check):
        assert parse_and_check("const sr = new SpeechRecognition();", 'speech-recognition')

    def test_public_key_credential(self, parse_and_check):
        assert parse_and_check("PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();", 'webauthn')

    def test_dom_parser(self, parse_and_check):
        assert parse_and_check("const parser = new DOMParser();", 'xml-serializer')

    def test_pointer_event(self, parse_and_check):
        assert parse_and_check("new PointerEvent('pointerdown');", 'pointer')
