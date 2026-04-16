"""Blackbox tests for the JavaScript parser.

Tests public API only: input string -> parse_features/get_detailed_report -> assert output.
No mocking, no internal imports. One representative test per unique caniuse feature ID,
plus all edge case and combined-feature tests.
"""

import pytest


# --- Core Feature Detection (1 per caniuse ID) ---

CORE_FEATURES = [
    pytest.param("const msg = `Hello, ${name}!`;", "template-literals", id="template-literals"),
    pytest.param(
        "const p = new Promise((resolve, reject) => { resolve('done'); });",
        "promises", id="promises"
    ),
    pytest.param(
        "const x = obj?.prop;",
        "mdn-javascript_operators_optional_chaining", id="optional-chaining"
    ),
    pytest.param(
        "const x = a ?? b;",
        "mdn-javascript_operators_nullish_coalescing", id="nullish-coalescing"
    ),
]


@pytest.mark.blackbox
@pytest.mark.parametrize("js_input,expected_id", CORE_FEATURES)
def test_core_feature_detection(parse_features, js_input, expected_id):
    assert expected_id in parse_features(js_input)


# --- Combined Feature Tests ---

@pytest.mark.blackbox
def test_modern_js_file_detects_multiple_features(parse_features):
    """Modern JS file should detect multiple ES6+ features."""
    js = """
    const add = (a, b) => a + b;
    let counter = 0;
    class Calculator extends Base {
        constructor() { super(); }
    }
    async function compute() { return await Promise.resolve(42); }
    """
    features = parse_features(js)
    for expected in ['arrow-functions', 'const', 'let', 'es6-class', 'async-functions']:
        assert expected in features


# --- Edge Cases ---

class TestEdgeCases:

    @pytest.mark.blackbox
    def test_multiple_features_combined(self, parse_features):
        js = """
        const fetchData = async () => {
            const response = await fetch('/api');
            return response.json();
        };

        document.querySelector('.btn').addEventListener('click', () => {
            localStorage.setItem('clicked', 'true');
        });
        """
        features = parse_features(js)
        for expected in [
            'const', 'arrow-functions', 'async-functions', 'fetch',
            'queryselector', 'addeventlistener', 'namevalue-storage'
        ]:
            assert expected in features
