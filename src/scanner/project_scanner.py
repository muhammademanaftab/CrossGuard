"""Walks a project directory and collects analyzable web files."""

import os
import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ScanConfig:
    """Scan filters: what to include/exclude."""

    exclude_patterns: List[str] = field(default_factory=lambda: [
        'node_modules',
        'dist',
        'build',
        '.git',
        '__pycache__',
        '.next',
        '.nuxt',
        'coverage',
        '.cache',
        'vendor',
    ])

    include_html: bool = True
    include_css: bool = True
    include_javascript: bool = True

    skip_minified: bool = False
    max_depth: Optional[int] = None
    max_files: int = 1000  # prevent runaway scans

    def should_include_extension(self, ext: str) -> bool:
        ext = ext.lower()

        if ext in ('.html', '.htm'):
            return self.include_html
        elif ext == '.css':
            return self.include_css
        elif ext == '.js':
            return self.include_javascript

        return False


@dataclass
class FileTreeNode:
    """Single node in the file tree (file or directory)."""
    name: str
    path: str
    is_directory: bool
    file_type: Optional[str] = None  # None for directories
    is_excluded: bool = False
    is_minified: bool = False
    children: List['FileTreeNode'] = field(default_factory=list)
    is_expanded: bool = False
    is_selected: bool = True

    @property
    def file_count(self) -> int:
        if not self.is_directory:
            return 1 if not self.is_excluded else 0
        return sum(child.file_count for child in self.children)

    @property
    def selected_count(self) -> int:
        if not self.is_directory:
            return 1 if self.is_selected and not self.is_excluded else 0
        return sum(child.selected_count for child in self.children)


@dataclass
class ScanResult:
    """Results from a directory scan."""

    files: Dict[str, List[str]] = field(default_factory=lambda: {
        'html': [],
        'css': [],
        'javascript': [],
    })

    file_tree: Optional[FileTreeNode] = None

    total_files: int = 0
    minified_files: int = 0
    excluded_directories: List[str] = field(default_factory=list)

    project_path: str = ''
    scan_depth: int = 0

    @property
    def html_count(self) -> int:
        return len(self.files.get('html', []))

    @property
    def css_count(self) -> int:
        return len(self.files.get('css', []))

    @property
    def js_count(self) -> int:
        return len(self.files.get('javascript', []))

    def get_all_files(self) -> List[str]:
        """All discovered file paths as a flat list."""
        all_files = []
        for file_list in self.files.values():
            all_files.extend(file_list)
        return all_files


class ProjectScanner:
    """Recursively scans a project and collects HTML/CSS/JS files."""

    EXTENSION_MAP = {
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.js': 'javascript',
    }

    MINIFIED_PATTERNS = [
        '*.min.js',
        '*.min.css',
        '*-min.js',
        '*-min.css',
        '*.bundle.js',
        '*.bundle.css',
    ]

    def __init__(self):
        pass

    def scan_directory(
        self,
        path: str,
        config: Optional[ScanConfig] = None,
        progress_callback: Optional[callable] = None
    ) -> ScanResult:
        """Scan a directory and build the file tree."""
        config = config or ScanConfig()
        path = os.path.abspath(path)

        if not os.path.isdir(path):
            return ScanResult(project_path=path)

        result = ScanResult(project_path=path)
        excluded_dirs: Set[str] = set()

        root_node = self._scan_node(
            path=path,
            root_path=path,
            config=config,
            current_depth=0,
            excluded_dirs=excluded_dirs,
            files_dict=result.files,
            progress_callback=progress_callback,
        )

        result.file_tree = root_node
        result.total_files = sum(len(files) for files in result.files.values())
        result.excluded_directories = list(excluded_dirs)
        result.minified_files = self._count_minified(result.files)

        return result

    def _scan_node(
        self,
        path: str,
        root_path: str,
        config: ScanConfig,
        current_depth: int,
        excluded_dirs: Set[str],
        files_dict: Dict[str, List[str]],
        progress_callback: Optional[callable] = None,
    ) -> FileTreeNode:
        """Build the tree recursively, skipping excluded dirs."""
        name = os.path.basename(path) or path
        is_excluded = self._is_excluded(name, config.exclude_patterns)

        node = FileTreeNode(
            name=name,
            path=path,
            is_directory=True,
            is_excluded=is_excluded,
        )

        if is_excluded:
            excluded_dirs.add(path)
            return node

        if config.max_depth is not None and current_depth >= config.max_depth:
            return node

        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return node

        dirs_first = []
        files_list = []

        for entry in entries:
            entry_path = os.path.join(path, entry)

            if os.path.isdir(entry_path):
                dirs_first.append(entry)
            else:
                files_list.append(entry)

        # dirs first so the tree looks cleaner
        for entry in dirs_first:
            entry_path = os.path.join(path, entry)
            child_node = self._scan_node(
                path=entry_path,
                root_path=root_path,
                config=config,
                current_depth=current_depth + 1,
                excluded_dirs=excluded_dirs,
                files_dict=files_dict,
                progress_callback=progress_callback,
            )
            node.children.append(child_node)

        total_files = sum(len(files) for files in files_dict.values())

        for entry in files_list:
            entry_path = os.path.join(path, entry)
            ext = os.path.splitext(entry)[1].lower()

            file_type = self.EXTENSION_MAP.get(ext)
            if file_type is None:
                continue

            if not config.should_include_extension(ext):
                continue

            if total_files >= config.max_files:
                break

            is_minified = self._is_minified(entry)
            if config.skip_minified and is_minified:
                continue

            file_node = FileTreeNode(
                name=entry,
                path=entry_path,
                is_directory=False,
                file_type=file_type,
                is_minified=is_minified,
                is_selected=True,
            )
            node.children.append(file_node)

            files_dict[file_type].append(entry_path)
            total_files += 1

            if progress_callback:
                progress_callback(total_files, config.max_files, f"Found: {entry}")

        return node

    def _is_excluded(self, name: str, patterns: List[str]) -> bool:
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
            if name == pattern:
                return True
        return False

    def _is_minified(self, filename: str) -> bool:
        filename_lower = filename.lower()
        for pattern in self.MINIFIED_PATTERNS:
            if fnmatch.fnmatch(filename_lower, pattern):
                return True
        return False

    def _count_minified(self, files: Dict[str, List[str]]) -> int:
        count = 0
        for file_list in files.values():
            for filepath in file_list:
                if self._is_minified(os.path.basename(filepath)):
                    count += 1
        return count

    def get_file_preview(self, node: FileTreeNode, max_depth: int = 3) -> str:
        """Render the file tree as a printable string."""
        lines = []
        self._build_preview(node, lines, prefix="", max_depth=max_depth, current_depth=0)
        return "\n".join(lines)

    def _build_preview(
        self,
        node: FileTreeNode,
        lines: List[str],
        prefix: str,
        max_depth: int,
        current_depth: int
    ):
        if current_depth > max_depth:
            return

        icon = self._get_node_icon(node)
        status = ""
        if node.is_excluded:
            status = " (excluded)"
        elif node.is_minified:
            status = " (minified)"

        lines.append(f"{prefix}{icon} {node.name}{status}")

        if node.is_directory and node.children:
            for i, child in enumerate(node.children):
                is_last = i == len(node.children) - 1
                child_prefix = prefix + ("    " if is_last else "\u2502   ")
                connector = "\u2514\u2500\u2500 " if is_last else "\u251C\u2500\u2500 "

                child_icon = self._get_node_icon(child)
                child_status = ""
                if child.is_excluded:
                    child_status = " (excluded)"
                elif child.is_minified:
                    child_status = " (minified)"

                lines.append(f"{prefix}{connector}{child_icon} {child.name}{child_status}")

                if child.is_directory and child.children and current_depth < max_depth:
                    self._build_preview(
                        child, lines, child_prefix, max_depth, current_depth + 1
                    )

    def _get_node_icon(self, node: FileTreeNode) -> str:
        if node.is_directory:
            return "\U0001F4C1" if not node.is_excluded else "\U0001F4C1"

        icons = {
            'html': "\U0001F310",
            'css': "\U0001F3A8",
            'javascript': "\u2605",
        }
        return icons.get(node.file_type, "\U0001F4C4")

    def get_selected_files(self, node: FileTreeNode) -> Dict[str, List[str]]:
        """Collect only user-selected files from the tree."""
        files = {'html': [], 'css': [], 'javascript': []}
        self._collect_selected(node, files)
        return files

    def _collect_selected(self, node: FileTreeNode, files: Dict[str, List[str]]):
        if node.is_excluded:
            return

        if not node.is_directory:
            if node.is_selected and node.file_type:
                files[node.file_type].append(node.path)
        else:
            for child in node.children:
                self._collect_selected(child, files)
