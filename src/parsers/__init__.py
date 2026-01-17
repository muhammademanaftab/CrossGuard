"""
Cross Guard Parsers - Code Feature Extraction.

This package contains parsers for extracting browser-relevant features
from HTML, CSS, and JavaScript code.

IMPORTANT: This is a backend module. Frontend code should NOT import
directly from here. Use the API layer (src.api) instead.

Internal Usage (for backend development):
    from src.parsers import HTMLParser, CSSParser, JavaScriptParser

    html_parser = HTMLParser()
    features = html_parser.parse_file('index.html')
"""

from .html_parser import HTMLParser
from .css_parser import CSSParser
from .js_parser import JavaScriptParser

__all__ = [
    'HTMLParser',
    'CSSParser',
    'JavaScriptParser',
]
