"""Polyfill recommendation module."""

from .polyfill_loader import PolyfillLoader, get_polyfill_loader
from .polyfill_service import PolyfillService, PolyfillRecommendation
from .polyfill_generator import generate_polyfills_file

__all__ = [
    'PolyfillLoader',
    'get_polyfill_loader',
    'PolyfillService',
    'PolyfillRecommendation',
    'generate_polyfills_file',
]
