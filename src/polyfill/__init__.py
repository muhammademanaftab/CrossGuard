"""
Polyfill recommendation module for Cross Guard.

This module provides polyfill recommendations based on browser compatibility analysis.
It maintains a curated database of polyfills mapped to Can I Use feature IDs.
"""

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
