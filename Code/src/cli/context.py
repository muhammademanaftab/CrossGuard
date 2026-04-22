"""CLI context — shared state passed to all subcommands."""

import os
import sys
from dataclasses import dataclass


@dataclass
class CliContext:
    """Shared state for all CLI commands (verbosity, color, timing)."""
    verbosity: int = 1
    color: bool = True
    timing: bool = False

    @staticmethod
    def detect_color(no_color_flag: bool = False) -> bool:
        """Respect NO_COLOR, FORCE_COLOR, and TTY detection."""
        if no_color_flag:
            return False
        if os.environ.get('NO_COLOR', '') != '':
            return False
        if os.environ.get('FORCE_COLOR', '') != '':
            return True
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    @staticmethod
    def resolve_verbosity(
        verbose_count: int = 0,
        quiet: bool = False,
        debug: bool = False,
    ) -> int:
        """Collapse -v, -q, --debug into 0=quiet / 1=normal / 2=verbose / 3=debug."""
        if debug:
            return 3
        if quiet:
            return 0
        return min(1 + verbose_count, 3)
