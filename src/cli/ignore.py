"""Gitignore-style file exclusion via .crossguardignore."""

from fnmatch import fnmatch
from pathlib import Path
from typing import List, Optional


IGNORE_FILENAME = '.crossguardignore'


def find_ignore_file(start: Path) -> Optional[Path]:
    """Walk up from start looking for a .crossguardignore file."""
    current = start.resolve()
    for _ in range(20):  # don't climb forever
        candidate = current / IGNORE_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_ignore_patterns(path: Path) -> List[str]:
    """Read patterns from file. Blank lines and # comments are skipped."""
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
    """Match filepath against patterns. Supports globs, !negation, and trailing /."""
    ignored = False
    basename = Path(filepath).name
    posix = filepath.replace('\\', '/')

    for pattern in patterns:
        negate = False
        pat = pattern

        if pat.startswith('!'):
            negate = True
            pat = pat[1:]

        if pat.endswith('/'):  # directory pattern
            segment = pat.rstrip('/')
            matched = f"/{segment}/" in f"/{posix}/" or posix.startswith(f"{segment}/")
        else:
            matched = fnmatch(posix, pat) or fnmatch(basename, pat)

        if matched:
            ignored = not negate

    return ignored
