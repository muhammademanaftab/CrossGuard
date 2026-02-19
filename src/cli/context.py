"""CLI context object for Cross Guard.

Stores global options (verbosity, color, timing) and passes them
to all subcommands via Click's context mechanism.
"""

import os
import sys
from dataclasses import dataclass


@dataclass
class CliContext:
    """Shared state for all CLI commands.

    Attributes:
        verbosity: 0=quiet, 1=normal, 2=verbose, 3=debug.
        color: Whether to emit ANSI color codes.
        timing: Whether to print elapsed time after commands.
    """
    verbosity: int = 1
    color: bool = True
    timing: bool = False

    @staticmethod
    def detect_color(no_color_flag: bool = False) -> bool:
        """Determine whether to use color output.

        Respects the de-facto ``NO_COLOR`` env var (https://no-color.org/)
        and falls back to TTY detection on stdout.
        """
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
        """Collapse ``-v``, ``-q``, and ``--debug`` flags into a single int.

        Returns:
            0 (quiet), 1 (normal), 2 (verbose), or 3 (debug).
        """
        if debug:
            return 3
        if quiet:
            return 0
        return min(1 + verbose_count, 3)
