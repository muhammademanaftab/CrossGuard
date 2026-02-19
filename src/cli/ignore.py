""".crossguardignore file support.

Provides gitignore-compatible pattern matching for excluding files
from analysis when scanning directories.
"""

from fnmatch import fnmatch
from pathlib import Path
from typing import List, Optional


IGNORE_FILENAME = '.crossguardignore'


def find_ignore_file(start: Path) -> Optional[Path]:
    """Walk up directories from *start* looking for a .crossguardignore file.

    Args:
        start: Directory to begin searching from.

    Returns:
        Path to the ignore file, or None.
    """
    current = start.resolve()
    for _ in range(20):  # safety limit
        candidate = current / IGNORE_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_ignore_patterns(path: Path) -> List[str]:
    """Load patterns from a .crossguardignore file.

    Supports:
      - Blank lines and ``#`` comments (skipped).
      - ``!`` prefix for negation (kept as-is for ``should_ignore``).
      - Leading/trailing whitespace stripped.

    Args:
        path: Path to the ignore file.

    Returns:
        List of pattern strings.
    """
    patterns: List[str] = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                patterns.append(stripped)
    except (IOError, OSError):
        pass
    return patterns


def should_ignore(filepath: str, patterns: List[str]) -> bool:
    """Decide whether *filepath* should be ignored based on *patterns*.

    Pattern semantics (gitignore-compatible subset):
      - Plain glob matched against the full path AND the basename.
      - ``!pattern`` negates a previous match.
      - Patterns ending with ``/`` match directories only (approximated
        by checking whether *filepath* contains the segment).

    Args:
        filepath: Relative or absolute file path to test.
        patterns: Ordered list of patterns from ``load_ignore_patterns``.

    Returns:
        True if the file should be excluded.
    """
    ignored = False
    basename = Path(filepath).name
    posix = filepath.replace('\\', '/')

    for pattern in patterns:
        negate = False
        pat = pattern

        if pat.startswith('!'):
            negate = True
            pat = pat[1:]

        # Trailing slash — match as directory segment
        if pat.endswith('/'):
            segment = pat.rstrip('/')
            matched = f"/{segment}/" in f"/{posix}/" or posix.startswith(f"{segment}/")
        else:
            matched = fnmatch(posix, pat) or fnmatch(basename, pat)

        if matched:
            ignored = not negate

    return ignored
