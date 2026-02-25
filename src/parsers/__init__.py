"""Parsers for extracting browser features from HTML, CSS, and JS files."""

from .html_parser import HTMLParser
from .css_parser import CSSParser
from .js_parser import JavaScriptParser

__all__ = [
    'HTMLParser',
    'CSSParser',
    'JavaScriptParser',
]
