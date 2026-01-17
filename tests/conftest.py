"""
Pytest configuration and shared fixtures for Cross Guard tests.
"""

import sys
import pytest
from pathlib import Path

# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.parsers.css_parser import CSSParser
from src.parsers.js_parser import JavaScriptParser
from src.parsers.html_parser import HTMLParser
from src.analyzer.database import CanIUseDatabase, get_database
from src.analyzer.compatibility import CompatibilityAnalyzer
from src.analyzer.scorer import CompatibilityScorer
from src.analyzer.main import CrossGuardAnalyzer


# ============================================================================
# Parser Fixtures
# ============================================================================

@pytest.fixture
def css_parser():
    """Create a fresh CSS parser instance."""
    return CSSParser()


@pytest.fixture
def js_parser():
    """Create a fresh JavaScript parser instance."""
    return JavaScriptParser()


@pytest.fixture
def html_parser():
    """Create a fresh HTML parser instance."""
    return HTMLParser()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def database():
    """Get the Can I Use database (session-scoped for efficiency)."""
    db = get_database()
    return db


@pytest.fixture
def fresh_database():
    """Create a fresh database instance (not cached)."""
    db = CanIUseDatabase()
    db.load()
    return db


# ============================================================================
# Analyzer Fixtures
# ============================================================================

@pytest.fixture
def compatibility_analyzer():
    """Create a compatibility analyzer instance."""
    return CompatibilityAnalyzer()


@pytest.fixture
def scorer():
    """Create a compatibility scorer instance."""
    return CompatibilityScorer()


@pytest.fixture
def main_analyzer():
    """Create the main Cross Guard analyzer instance."""
    return CrossGuardAnalyzer()


# ============================================================================
# Target Browser Fixtures
# ============================================================================

@pytest.fixture
def default_browsers():
    """Default target browsers for testing."""
    return {
        'chrome': '120',
        'firefox': '121',
        'safari': '17',
        'edge': '120'
    }


@pytest.fixture
def all_browsers():
    """Extended browser list including older versions."""
    return {
        'chrome': '120',
        'firefox': '121',
        'safari': '17',
        'edge': '120',
        'opera': '106',
        'ie': '11'
    }


# ============================================================================
# Sample Code Fixtures
# ============================================================================

@pytest.fixture
def sample_css_flexbox():
    """Sample CSS using flexbox."""
    return """
    .container {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }
    """


@pytest.fixture
def sample_css_grid():
    """Sample CSS using CSS Grid."""
    return """
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: auto;
        grid-gap: 10px;
    }

    .item {
        grid-column: span 2;
        grid-row: 1;
    }
    """


@pytest.fixture
def sample_css_modern():
    """Sample CSS using various modern features."""
    return """
    :root {
        --primary-color: #3498db;
        --secondary-color: rgba(52, 152, 219, 0.5);
    }

    .card {
        display: flex;
        background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .animated {
        animation: fadeIn 0.5s ease-in;
    }

    @media (prefers-color-scheme: dark) {
        .card {
            background: #1a1a1a;
        }
    }
    """


@pytest.fixture
def sample_css_transforms():
    """Sample CSS using transforms and animations."""
    return """
    .box {
        transform: rotate(45deg) scale(1.2);
        transition: transform 0.3s ease;
    }

    .box-3d {
        transform: translate3d(10px, 20px, 30px);
        perspective: 1000px;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    """


@pytest.fixture
def sample_js_es6():
    """Sample JavaScript using ES6+ features."""
    return """
    const greeting = 'Hello';
    let count = 0;

    const add = (a, b) => a + b;

    const user = { name: 'John', age: 30 };
    const { name, age } = user;

    const numbers = [1, 2, 3];
    const doubled = [...numbers, 4, 5];

    class Person {
        constructor(name) {
            this.name = name;
        }

        greet() {
            return `Hello, ${this.name}!`;
        }
    }
    """


@pytest.fixture
def sample_js_async():
    """Sample JavaScript using async/await and Promises."""
    return """
    async function fetchData(url) {
        try {
            const response = await fetch(url);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error:', error);
        }
    }

    const getData = async () => {
        const result = await fetchData('/api/data');
        return result;
    };

    new Promise((resolve, reject) => {
        setTimeout(() => resolve('done'), 1000);
    }).then(result => console.log(result));
    """


@pytest.fixture
def sample_js_modern_apis():
    """Sample JavaScript using modern Web APIs."""
    return """
    // Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    });

    // Resize Observer
    const resizeObserver = new ResizeObserver((entries) => {
        entries.forEach(entry => {
            console.log('Size changed:', entry.contentRect);
        });
    });

    // Mutation Observer
    const mutationObserver = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            console.log('DOM changed:', mutation);
        });
    });

    // LocalStorage
    localStorage.setItem('key', 'value');
    const stored = localStorage.getItem('key');

    // Map and Set
    const map = new Map();
    map.set('key', 'value');

    const set = new Set([1, 2, 3]);
    """


@pytest.fixture
def sample_js_array_methods():
    """Sample JavaScript using array methods."""
    return """
    const numbers = [1, 2, 3, 4, 5];

    const doubled = numbers.map(n => n * 2);
    const evens = numbers.filter(n => n % 2 === 0);
    const sum = numbers.reduce((acc, n) => acc + n, 0);
    const found = numbers.find(n => n > 3);
    const hasEven = numbers.some(n => n % 2 === 0);
    const allPositive = numbers.every(n => n > 0);
    const index = numbers.findIndex(n => n === 3);
    const includes = numbers.includes(3);
    const flat = [[1, 2], [3, 4]].flat();
    const flatMapped = numbers.flatMap(n => [n, n * 2]);
    """


@pytest.fixture
def sample_html_modern():
    """Sample HTML using modern HTML5 features."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Modern HTML5</title>
    </head>
    <body>
        <header>
            <nav>
                <a href="/">Home</a>
            </nav>
        </header>

        <main>
            <article>
                <h1>Article Title</h1>
                <section>
                    <p>Content here</p>
                </section>
            </article>

            <aside>
                <details>
                    <summary>More info</summary>
                    <p>Hidden content</p>
                </details>
            </aside>

            <figure>
                <picture>
                    <source srcset="image.webp" type="image/webp">
                    <img src="image.jpg" alt="Image" loading="lazy">
                </picture>
                <figcaption>Image caption</figcaption>
            </figure>

            <form>
                <input type="email" placeholder="Email" required>
                <input type="date">
                <input type="range" min="0" max="100">
                <input type="color">
                <datalist id="options">
                    <option value="Option 1">
                    <option value="Option 2">
                </datalist>
                <output></output>
                <button type="submit">Submit</button>
            </form>

            <dialog id="modal">
                <p>Dialog content</p>
            </dialog>

            <video controls>
                <source src="video.mp4" type="video/mp4">
            </video>

            <audio controls>
                <source src="audio.mp3" type="audio/mpeg">
            </audio>

            <canvas id="canvas"></canvas>

            <template id="template">
                <div class="card">Card content</div>
            </template>
        </main>

        <footer>
            <p>Footer content</p>
        </footer>

        <script src="app.js" type="module" defer></script>
    </body>
    </html>
    """


# ============================================================================
# Test File Path Fixtures
# ============================================================================

@pytest.fixture
def fixtures_dir():
    """Path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_html_file(fixtures_dir, tmp_path):
    """Create a temporary HTML file for testing."""
    html_file = tmp_path / "test.html"
    html_file.write_text("""
    <!DOCTYPE html>
    <html>
    <head><title>Test</title></head>
    <body>
        <header><nav></nav></header>
        <main><article></article></main>
        <footer></footer>
    </body>
    </html>
    """)
    return str(html_file)


@pytest.fixture
def sample_css_file(tmp_path):
    """Create a temporary CSS file for testing."""
    css_file = tmp_path / "test.css"
    css_file.write_text("""
    .container {
        display: flex;
        gap: 20px;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
    }
    """)
    return str(css_file)


@pytest.fixture
def sample_js_file(tmp_path):
    """Create a temporary JavaScript file for testing."""
    js_file = tmp_path / "test.js"
    js_file.write_text("""
    const add = (a, b) => a + b;

    async function fetchData() {
        const response = await fetch('/api');
        return response.json();
    }

    class Calculator {
        add(a, b) { return a + b; }
    }
    """)
    return str(js_file)


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def assert_features():
    """Helper to assert features are detected."""
    def _assert_features(detected: set, expected: list):
        for feature in expected:
            assert feature in detected, f"Expected feature '{feature}' not found in {detected}"
    return _assert_features


@pytest.fixture
def assert_no_features():
    """Helper to assert features are NOT detected."""
    def _assert_no_features(detected: set, unexpected: list):
        for feature in unexpected:
            assert feature not in detected, f"Unexpected feature '{feature}' found in {detected}"
    return _assert_no_features
