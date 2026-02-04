"""
Framework Detector - Detect project frameworks and build tools.

This module provides functionality to detect what framework (React, Vue, Angular, etc.)
and build tools (Vite, Webpack, etc.) a project uses.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class FrameworkInfo:
    """Information about a detected framework."""
    name: str
    version: str = "unknown"
    icon: str = ""
    color: str = "#58a6ff"

    def __str__(self) -> str:
        if self.version and self.version != "unknown":
            return f"{self.name} {self.version}"
        return self.name


@dataclass
class BuildToolInfo:
    """Information about a detected build tool."""
    name: str
    version: str = "unknown"
    config_file: str = ""

    def __str__(self) -> str:
        if self.version and self.version != "unknown":
            return f"{self.name} {self.version}"
        return self.name


@dataclass
class ProjectInfo:
    """Complete project detection information."""
    framework: Optional[FrameworkInfo] = None
    build_tool: Optional[BuildToolInfo] = None
    package_manager: str = "npm"  # npm, yarn, pnpm
    has_typescript: bool = False
    is_monorepo: bool = False
    additional_libraries: List[str] = None

    def __post_init__(self):
        if self.additional_libraries is None:
            self.additional_libraries = []


class FrameworkDetector:
    """Detects project frameworks and build tools."""

    # Framework detection rules: (dependency_name, framework_name, icon, color)
    FRAMEWORK_RULES: List[Tuple[str, str, str, str]] = [
        ('react', 'React', '\u269B', '#61dafb'),      # Atom symbol
        ('react-dom', 'React', '\u269B', '#61dafb'),
        ('next', 'Next.js', '\u25B2', '#000000'),     # Triangle
        ('vue', 'Vue', '\u2618', '#42b883'),          # Shamrock
        ('nuxt', 'Nuxt', '\u2618', '#00dc82'),
        ('@angular/core', 'Angular', '\u2B21', '#dd0031'),  # Hexagon
        ('svelte', 'Svelte', '\U0001F525', '#ff3e00'),  # Fire
        ('@sveltejs/kit', 'SvelteKit', '\U0001F525', '#ff3e00'),
        ('solid-js', 'Solid', '\u25CF', '#2c4f7c'),    # Circle
        ('preact', 'Preact', '\u269B', '#673ab8'),
        ('ember-cli', 'Ember', '\U0001F525', '#e04e39'),
        ('jquery', 'jQuery', '\U0001F4E6', '#0769ad'),  # Package
        ('backbone', 'Backbone', '\U0001F9B4', '#0071b5'),  # Bone
    ]

    # Build tool detection rules: (dependency_name, tool_name, config_files)
    BUILD_TOOL_RULES: List[Tuple[str, str, List[str]]] = [
        ('vite', 'Vite', ['vite.config.js', 'vite.config.ts', 'vite.config.mjs']),
        ('webpack', 'Webpack', ['webpack.config.js', 'webpack.config.ts']),
        ('rollup', 'Rollup', ['rollup.config.js', 'rollup.config.mjs']),
        ('parcel', 'Parcel', []),
        ('esbuild', 'esbuild', []),
        ('turbo', 'Turborepo', ['turbo.json']),
        ('gulp', 'Gulp', ['gulpfile.js', 'gulpfile.ts']),
        ('grunt', 'Grunt', ['Gruntfile.js']),
    ]

    # Additional library detection
    NOTABLE_LIBRARIES = [
        'tailwindcss',
        'bootstrap',
        'styled-components',
        '@emotion/react',
        'sass',
        'less',
        'redux',
        '@reduxjs/toolkit',
        'mobx',
        'zustand',
        'axios',
        'graphql',
        '@apollo/client',
        'prisma',
        'mongoose',
        'sequelize',
        'jest',
        'vitest',
        'cypress',
        'playwright',
        'storybook',
    ]

    def __init__(self):
        """Initialize the framework detector."""
        pass

    def detect(self, project_path: str) -> ProjectInfo:
        """
        Detect framework and build tools for a project.

        Args:
            project_path: Path to the project root directory

        Returns:
            ProjectInfo with detected information
        """
        project_path = Path(project_path)
        info = ProjectInfo()

        # Check for package.json
        package_json_path = project_path / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)

                # Combine dependencies
                deps = {}
                deps.update(package_data.get('dependencies', {}))
                deps.update(package_data.get('devDependencies', {}))

                # Detect framework
                info.framework = self._detect_framework(deps)

                # Detect build tool
                info.build_tool = self._detect_build_tool(deps, project_path)

                # Detect TypeScript
                info.has_typescript = 'typescript' in deps or self._has_ts_config(project_path)

                # Detect additional libraries
                info.additional_libraries = self._detect_libraries(deps)

            except (json.JSONDecodeError, IOError):
                pass

        # Detect package manager
        info.package_manager = self._detect_package_manager(project_path)

        # Check for monorepo
        info.is_monorepo = self._is_monorepo(project_path)

        return info

    def _detect_framework(self, deps: Dict[str, str]) -> Optional[FrameworkInfo]:
        """Detect the primary framework from dependencies."""
        for dep_name, framework_name, icon, color in self.FRAMEWORK_RULES:
            if dep_name in deps:
                version = self._clean_version(deps[dep_name])
                return FrameworkInfo(
                    name=framework_name,
                    version=version,
                    icon=icon,
                    color=color
                )
        return None

    def _detect_build_tool(
        self,
        deps: Dict[str, str],
        project_path: Path
    ) -> Optional[BuildToolInfo]:
        """Detect the build tool from dependencies and config files."""
        for dep_name, tool_name, config_files in self.BUILD_TOOL_RULES:
            if dep_name in deps:
                version = self._clean_version(deps[dep_name])
                config_file = ""

                # Find config file
                for cfg in config_files:
                    if (project_path / cfg).exists():
                        config_file = cfg
                        break

                return BuildToolInfo(
                    name=tool_name,
                    version=version,
                    config_file=config_file
                )

        # Check for config files even without dependency
        for _, tool_name, config_files in self.BUILD_TOOL_RULES:
            for cfg in config_files:
                if (project_path / cfg).exists():
                    return BuildToolInfo(name=tool_name, config_file=cfg)

        return None

    def _detect_libraries(self, deps: Dict[str, str]) -> List[str]:
        """Detect notable additional libraries."""
        found = []
        for lib in self.NOTABLE_LIBRARIES:
            if lib in deps:
                found.append(lib)
        return found

    def _detect_package_manager(self, project_path: Path) -> str:
        """Detect which package manager is used."""
        if (project_path / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (project_path / 'yarn.lock').exists():
            return 'yarn'
        elif (project_path / 'bun.lockb').exists():
            return 'bun'
        return 'npm'

    def _is_monorepo(self, project_path: Path) -> bool:
        """Check if the project is a monorepo."""
        # Check for common monorepo indicators
        monorepo_files = [
            'pnpm-workspace.yaml',
            'lerna.json',
            'turbo.json',
            'nx.json',
        ]
        for f in monorepo_files:
            if (project_path / f).exists():
                return True

        # Check for workspaces in package.json
        package_json_path = project_path / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'workspaces' in data:
                        return True
            except (json.JSONDecodeError, IOError):
                pass

        return False

    def _has_ts_config(self, project_path: Path) -> bool:
        """Check if project has TypeScript config."""
        ts_configs = ['tsconfig.json', 'tsconfig.base.json', 'jsconfig.json']
        for cfg in ts_configs:
            if (project_path / cfg).exists():
                return True
        return False

    def _clean_version(self, version: str) -> str:
        """Clean version string from package.json."""
        if not version:
            return "unknown"
        # Remove leading ^ or ~
        version = version.lstrip('^~>=<')
        # Take first part if range
        if ' ' in version:
            version = version.split()[0]
        return version

    def is_minified(self, file_path: str) -> bool:
        """
        Check if a file appears to be minified.

        Uses a simple heuristic based on line length vs file size.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file appears to be minified
        """
        try:
            path = Path(file_path)

            # Check filename first
            name_lower = path.name.lower()
            if '.min.' in name_lower or '-min.' in name_lower or '.bundle.' in name_lower:
                return True

            # Skip large files for performance
            stat = path.stat()
            if stat.st_size > 500_000:  # 500KB
                return True  # Assume minified

            if stat.st_size < 100:  # Very small files
                return False

            # Read first few KB
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10_000)

            if not content:
                return False

            # Count lines and average line length
            lines = content.split('\n')
            if len(lines) < 2:
                # Single line file > 1000 chars is likely minified
                return len(content) > 1000

            # Calculate average line length (excluding empty lines)
            non_empty = [l for l in lines if l.strip()]
            if not non_empty:
                return False

            avg_length = sum(len(l) for l in non_empty) / len(non_empty)

            # If average line > 200 chars, likely minified
            return avg_length > 200

        except (IOError, OSError):
            return False

    def get_framework_badge(self, info: ProjectInfo) -> Tuple[str, str]:
        """
        Get a badge string for displaying framework info.

        Args:
            info: ProjectInfo from detect()

        Returns:
            Tuple of (badge_text, badge_color)
        """
        if info.framework:
            badge_text = str(info.framework)
            badge_color = info.framework.color
        else:
            badge_text = "No framework detected"
            badge_color = "#6e7681"

        if info.build_tool:
            badge_text += f" | {info.build_tool.name}"

        return badge_text, badge_color
