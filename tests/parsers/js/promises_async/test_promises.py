"""Tests for Promise and async API features.

Tests features: promises, promise-finally, fetch, abortcontroller,
                unhandledrejection, requestanimationframe, requestidlecallback, setimmediate
"""

import pytest


class TestPromises:
    """Tests for Promise API detection."""

    def test_new_promise(self, parse_and_check):
        """Test new Promise constructor."""
        js = "const p = new Promise((resolve, reject) => { resolve('done'); });"
        assert parse_and_check(js, 'promises')

    def test_promise_then(self, parse_and_check):
        """Test Promise.then()."""
        js = "promise.then(result => console.log(result));"
        assert parse_and_check(js, 'promises')

    def test_promise_catch(self, parse_and_check):
        """Test Promise.catch()."""
        js = "promise.catch(error => console.error(error));"
        assert parse_and_check(js, 'promises')

    def test_promise_all(self, parse_and_check):
        """Test Promise.all()."""
        js = "Promise.all([p1, p2, p3]).then(results => console.log(results));"
        assert parse_and_check(js, 'promises')

    def test_promise_race(self, parse_and_check):
        """Test Promise.race()."""
        js = "Promise.race([p1, p2]).then(winner => console.log(winner));"
        assert parse_and_check(js, 'promises')

    def test_promise_resolve(self, parse_and_check):
        """Test Promise.resolve()."""
        js = "Promise.resolve('value').then(console.log);"
        assert parse_and_check(js, 'promises')

    def test_promise_reject(self, parse_and_check):
        """Test Promise.reject()."""
        js = "Promise.reject(new Error('failed')).catch(console.error);"
        assert parse_and_check(js, 'promises')


class TestPromiseFinally:
    """Tests for Promise.finally() detection."""

    def test_promise_finally(self, parse_and_check):
        """Test Promise.finally()."""
        js = "fetch('/api').then(r => r.json()).finally(() => cleanup());"
        assert parse_and_check(js, 'promise-finally')

    def test_finally_chain(self, parse_and_check):
        """Test finally in promise chain."""
        js = """
        promise
            .then(doSomething)
            .catch(handleError)
            .finally(cleanup);
        """
        assert parse_and_check(js, 'promise-finally')


class TestFetch:
    """Tests for Fetch API detection."""

    def test_simple_fetch(self, parse_and_check):
        """Test simple fetch call."""
        js = "fetch('/api/users');"
        assert parse_and_check(js, 'fetch')

    def test_fetch_with_options(self, parse_and_check):
        """Test fetch with options."""
        js = """
        fetch('/api/data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        """
        assert parse_and_check(js, 'fetch')

    def test_fetch_then_chain(self, parse_and_check):
        """Test fetch with then chain."""
        js = "fetch('/api').then(r => r.json()).then(data => console.log(data));"
        assert parse_and_check(js, 'fetch')


class TestAbortController:
    """Tests for AbortController detection."""

    def test_new_abort_controller(self, parse_and_check):
        """Test new AbortController."""
        js = "const controller = new AbortController();"
        assert parse_and_check(js, 'abortcontroller')

    def test_abort_signal(self, parse_and_check):
        """Test AbortSignal."""
        js = "const signal = AbortSignal.timeout(5000);"
        assert parse_and_check(js, 'abortcontroller')

    def test_fetch_with_abort(self, parse_and_check_multiple):
        """Test fetch with AbortController."""
        js = """
        const controller = new AbortController();
        fetch('/api', { signal: controller.signal });
        """
        assert parse_and_check_multiple(js, ['fetch', 'abortcontroller'])


class TestUnhandledRejection:
    """Tests for unhandledrejection event detection.

    Note: Pattern looks for the literal string 'unhandledrejection' or 'rejectionhandled'.
    """

    def test_unhandledrejection_event(self, parse_and_check):
        """Test unhandledrejection event string."""
        js = "window.onunhandledrejection = handler;"
        assert parse_and_check(js, 'unhandledrejection')

    def test_rejectionhandled_event(self, parse_and_check):
        """Test rejectionhandled event string."""
        js = "window.onrejectionhandled = handler;"
        assert parse_and_check(js, 'unhandledrejection')


class TestRequestAnimationFrame:
    """Tests for requestAnimationFrame detection."""

    def test_raf_call(self, parse_and_check):
        """Test requestAnimationFrame call."""
        js = "requestAnimationFrame(animate);"
        assert parse_and_check(js, 'requestanimationframe')

    def test_raf_loop(self, parse_and_check):
        """Test requestAnimationFrame loop."""
        js = """
        function animate() {
            // animation logic
            requestAnimationFrame(animate);
        }
        """
        assert parse_and_check(js, 'requestanimationframe')

    def test_cancel_raf(self, parse_and_check):
        """Test cancelAnimationFrame."""
        js = "const id = requestAnimationFrame(fn); cancelAnimationFrame(id);"
        assert parse_and_check(js, 'requestanimationframe')


class TestRequestIdleCallback:
    """Tests for requestIdleCallback detection."""

    def test_ric_call(self, parse_and_check):
        """Test requestIdleCallback call."""
        js = "requestIdleCallback(doWork);"
        assert parse_and_check(js, 'requestidlecallback')

    def test_ric_with_deadline(self, parse_and_check):
        """Test requestIdleCallback with deadline."""
        js = """
        requestIdleCallback(deadline => {
            while (deadline.timeRemaining() > 0) {
                // do background work
            }
        });
        """
        assert parse_and_check(js, 'requestidlecallback')

    def test_cancel_ric(self, parse_and_check):
        """Test cancelIdleCallback."""
        js = "cancelIdleCallback(idleId);"
        assert parse_and_check(js, 'requestidlecallback')


class TestSetImmediate:
    """Tests for setImmediate detection."""

    def test_set_immediate(self, parse_and_check):
        """Test setImmediate call."""
        js = "setImmediate(() => console.log('immediate'));"
        assert parse_and_check(js, 'setimmediate')

    def test_clear_immediate(self, parse_and_check):
        """Test clearImmediate."""
        js = "clearImmediate(immediateId);"
        assert parse_and_check(js, 'setimmediate')
