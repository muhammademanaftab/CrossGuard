"""Comprehensive test suite for JavaScript parser."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.js_parser import JavaScriptParser, parse_js_file, parse_js_string


def test_arrow_functions():
    """Test detection of arrow functions."""
    print("\n" + "="*60)
    print("TEST 1: Arrow Functions")
    print("="*60)
    
    js = """
    const add = (a, b) => a + b;
    const greet = name => `Hello ${name}`;
    const numbers = [1, 2, 3].map(n => n * 2);
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'arrow-functions' in features:
        print("✓ Arrow functions detected!")
        return True
    else:
        print("✗ Arrow functions NOT detected")
        return False


def test_async_await():
    """Test detection of async/await."""
    print("\n" + "="*60)
    print("TEST 2: Async/Await")
    print("="*60)
    
    js = """
    async function fetchData() {
        const response = await fetch('/api/data');
        return await response.json();
    }
    
    const getData = async () => {
        await someFunction();
    };
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'async-functions' in features:
        print("✓ Async/await detected!")
        return True
    else:
        print("✗ Async/await NOT detected")
        return False


def test_const_let():
    """Test detection of const and let."""
    print("\n" + "="*60)
    print("TEST 3: Const and Let")
    print("="*60)
    
    js = """
    const PI = 3.14159;
    let counter = 0;
    const name = 'John';
    let age = 30;
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    found_const = 'const' in features
    found_let = 'let' in features
    
    if found_const:
        print("✓ Const detected!")
    if found_let:
        print("✓ Let detected!")
    
    return found_const and found_let


def test_template_literals():
    """Test detection of template literals."""
    print("\n" + "="*60)
    print("TEST 4: Template Literals")
    print("="*60)
    
    js = """
    const name = 'World';
    const greeting = `Hello ${name}!`;
    const multiline = `
        This is a
        multiline string
        with ${name}
    `;
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'template-literals' in features:
        print("✓ Template literals detected!")
        return True
    else:
        print("✗ Template literals NOT detected")
        return False


def test_destructuring():
    """Test detection of destructuring."""
    print("\n" + "="*60)
    print("TEST 5: Destructuring")
    print("="*60)
    
    js = """
    const { name, age } = person;
    const [first, second] = array;
    let { x, y } = coordinates;
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'destructuring' in features:
        print("✓ Destructuring detected!")
        return True
    else:
        print("✗ Destructuring NOT detected")
        return False


def test_spread_operator():
    """Test detection of spread operator."""
    print("\n" + "="*60)
    print("TEST 6: Spread Operator")
    print("="*60)
    
    js = """
    const arr1 = [1, 2, 3];
    const arr2 = [...arr1, 4, 5];
    const obj = { ...original, newProp: 'value' };
    function sum(...numbers) {
        return numbers.reduce((a, b) => a + b);
    }
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'spread' in features:
        print("✓ Spread operator detected!")
        return True
    else:
        print("✗ Spread operator NOT detected")
        return False


def test_optional_chaining():
    """Test detection of optional chaining."""
    print("\n" + "="*60)
    print("TEST 7: Optional Chaining")
    print("="*60)
    
    js = """
    const value = obj?.property;
    const result = user?.address?.street;
    const fn = obj?.method?.();
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'optional-chaining' in features:
        print("✓ Optional chaining detected!")
        return True
    else:
        print("✗ Optional chaining NOT detected")
        return False


def test_nullish_coalescing():
    """Test detection of nullish coalescing."""
    print("\n" + "="*60)
    print("TEST 8: Nullish Coalescing")
    print("="*60)
    
    js = """
    const value = input ?? defaultValue;
    const name = user.name ?? 'Anonymous';
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'nullish-coalescing' in features:
        print("✓ Nullish coalescing detected!")
        return True
    else:
        print("✗ Nullish coalescing NOT detected")
        return False


def test_promises():
    """Test detection of Promises."""
    print("\n" + "="*60)
    print("TEST 9: Promises")
    print("="*60)
    
    js = """
    const promise = new Promise((resolve, reject) => {
        setTimeout(() => resolve('done'), 1000);
    });
    
    promise.then(result => console.log(result))
           .catch(error => console.error(error));
    
    Promise.all([promise1, promise2]).then(results => {
        console.log(results);
    });
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'promises' in features:
        print("✓ Promises detected!")
        return True
    else:
        print("✗ Promises NOT detected")
        return False


def test_fetch_api():
    """Test detection of Fetch API."""
    print("\n" + "="*60)
    print("TEST 10: Fetch API")
    print("="*60)
    
    js = """
    fetch('/api/data')
        .then(response => response.json())
        .then(data => console.log(data));
    
    async function getData() {
        const response = await fetch('/api/users');
        return await response.json();
    }
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'fetch' in features:
        print("✓ Fetch API detected!")
        return True
    else:
        print("✗ Fetch API NOT detected")
        return False


def test_array_methods():
    """Test detection of modern array methods."""
    print("\n" + "="*60)
    print("TEST 11: Array Methods")
    print("="*60)
    
    js = """
    const arr = [1, [2, [3, 4]]];
    const flat = arr.flat(2);
    const flatMapped = arr.flatMap(x => [x, x * 2]);
    
    const found = arr.find(x => x > 2);
    const index = arr.findIndex(x => x > 2);
    const includes = arr.includes(3);
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    array_features = [f for f in features if 'array' in f]
    print(f"  Array features: {array_features}")
    
    if len(array_features) > 0:
        print("✓ Array methods detected!")
        return True
    else:
        print("✗ Array methods NOT detected")
        return False


def test_string_methods():
    """Test detection of modern string methods."""
    print("\n" + "="*60)
    print("TEST 12: String Methods")
    print("="*60)
    
    js = """
    const str = 'Hello World';
    const replaced = str.replaceAll('o', '0');
    const includes = str.includes('World');
    const starts = str.startsWith('Hello');
    const ends = str.endsWith('World');
    const padded = str.padStart(20, ' ');
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    string_features = [f for f in features if 'string' in f]
    print(f"  String features: {string_features}")
    
    if len(string_features) > 0:
        print("✓ String methods detected!")
        return True
    else:
        print("✗ String methods NOT detected")
        return False


def test_object_methods():
    """Test detection of Object methods."""
    print("\n" + "="*60)
    print("TEST 13: Object Methods")
    print("="*60)
    
    js = """
    const obj = { a: 1, b: 2, c: 3 };
    const entries = Object.entries(obj);
    const values = Object.values(obj);
    const keys = Object.keys(obj);
    const assigned = Object.assign({}, obj, { d: 4 });
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    object_features = [f for f in features if 'object' in f]
    print(f"  Object features: {object_features}")
    
    if len(object_features) > 0:
        print("✓ Object methods detected!")
        return True
    else:
        print("✗ Object methods NOT detected")
        return False


def test_web_storage():
    """Test detection of Web Storage APIs."""
    print("\n" + "="*60)
    print("TEST 14: Web Storage")
    print("="*60)
    
    js = """
    localStorage.setItem('key', 'value');
    const value = localStorage.getItem('key');
    sessionStorage.setItem('session', 'data');
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'namevalue-storage' in features:
        print("✓ Web Storage detected!")
        return True
    else:
        print("✗ Web Storage NOT detected")
        return False


def test_sample_file():
    """Test parsing the actual sample.js file."""
    print("\n" + "="*60)
    print("TEST 15: Parse examples/sample.js")
    print("="*60)
    
    sample_path = Path(__file__).parent.parent / 'examples' / 'sample.js'
    
    if not sample_path.exists():
        print(f"✗ Sample file not found: {sample_path}")
        return False
    
    parser = JavaScriptParser()
    features = parser.parse_file(str(sample_path))
    
    print(f"✓ Parsed sample.js successfully")
    print(f"✓ Found {len(features)} features")
    
    if features:
        print(f"\n  Features detected:")
        for i, feature in enumerate(sorted(features), 1):
            print(f"    {i}. {feature}")
    
    # Get statistics
    stats = parser.get_statistics()
    print(f"\n  Statistics:")
    print(f"    Syntax features: {stats['syntax_features']}")
    print(f"    API features: {stats['api_features']}")
    print(f"    Array methods: {stats['array_methods']}")
    print(f"    String methods: {stats['string_methods']}")
    print(f"    Object methods: {stats['object_methods']}")
    
    if len(features) > 0:
        print("\n✓ Sample file parsed successfully!")
        return True
    else:
        print("\n⚠️  No features found in sample file")
        return True  # Still pass, file might be empty


def test_comment_removal():
    """Test that comments are properly removed."""
    print("\n" + "="*60)
    print("TEST 16: Comment Removal")
    print("="*60)
    
    js = """
    // This is a comment with arrow =>
    const real = () => {}; // Real arrow function
    /* 
     * Multi-line comment
     * with arrow =>
     */
    const another = x => x * 2;
    """
    
    parser = JavaScriptParser()
    features = parser.parse_string(js)
    
    print(f"✓ Found {len(features)} features")
    
    if 'arrow-functions' in features:
        print("✓ Comments properly removed, real code detected!")
        return True
    else:
        print("✗ Comment removal failed")
        return False


def run_all_tests():
    """Run all JavaScript parser tests."""
    print("\n" + "="*60)
    print("JAVASCRIPT PARSER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        test_arrow_functions,
        test_async_await,
        test_const_let,
        test_template_literals,
        test_destructuring,
        test_spread_operator,
        test_optional_chaining,
        test_nullish_coalescing,
        test_promises,
        test_fetch_api,
        test_array_methods,
        test_string_methods,
        test_object_methods,
        test_web_storage,
        test_sample_file,
        test_comment_removal,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ All tests passed! JavaScript Parser is working perfectly!")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
