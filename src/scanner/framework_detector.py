"""Detect frameworks and build tools in a project."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FrameworkInfo:
    """Detected frontend framework."""
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
    """Detected build tool."""
    name: str
    version: str = "unknown"
    config_file: str = ""

    def __str__(self) -> str:
        if self.version and self.version != "unknown":
            return f"{self.name} {self.version}"
        return self.name


@dataclass
class ProjectInfo:
    """Summary of the project's toolchain."""
    framework: Optional[FrameworkInfo] = None
    build_tool: Optional[BuildToolInfo] = None
    package_manager: str = "npm"
    has_typescript: bool = False
    is_monorepo: bool = False
    additional_libraries: List[str] = None

    def __post_init__(self):
        if self.additional_libraries is None:
            self.additional_libraries = []


class FrameworkDetector:
    """Sniffs package.json and config files to figure out what a project uses."""

    FRAMEWORK_RULES: List[Tuple[str, str, str, str]] = [
        ('react', 'React', '\u269B', '#61dafb'),
        ('react-dom', 'React', '\u269B', '#61dafb'),
        ('next', 'Next.js', '\u25B2', '#000000'),
        ('vue', 'Vue', '\u2618', '#42b883'),
        ('nuxt', 'Nuxt', '\u2618', '#00dc82'),
        ('@angular/core', 'Angular', '\u2B21', '#dd0031'),
        ('svelte', 'Svelte', '\U0001F525', '#ff3e00'),
        ('@sveltejs/kit', 'SvelteKit', '\U0001F525', '#ff3e00'),
        ('solid-js', 'Solid', '\u25CF', '#2c4f7c'),
        ('preact', 'Preact', '\u269B', '#673ab8'),
        ('ember-cli', 'Ember', '\U0001F525', '#e04e39'),
        ('jquery', 'jQuery', '\U0001F4E6', '#0769ad'),
        ('backbone', 'Backbone', '\U0001F9B4', '#0071b5'),
    ]

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
        pass

    def detect(self, project_path: str) -> ProjectInfo:
        """Inspect a project directory and figure out what's in it."""
        project_path = Path(project_path)
        info = ProjectInfo()

        package_json_path = project_path / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)

                # merge deps + devDeps so we check both
                deps = {}
                deps.update(package_data.get('dependencies', {}))
                deps.update(package_data.get('devDependencies', {}))

                info.framework = self._detect_framework(deps)
                info.build_tool = self._detect_build_tool(deps, project_path)
                info.has_typescript = 'typescript' in deps or self._has_ts_config(project_path)
                info.additional_libraries = self._detect_libraries(deps)

            except (json.JSONDecodeError, IOError):
                pass

        info.package_manager = self._detect_package_manager(project_path)
        info.is_monorepo = self._is_monorepo(project_path)

        return info

    def _detect_framework(self, deps: Dict[str, str]) -> Optional[FrameworkInfo]:
        """First match wins, so rule order matters."""
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
        for dep_name, tool_name, config_files in self.BUILD_TOOL_RULES:
            if dep_name in deps:
                version = self._clean_version(deps[dep_name])
                config_file = ""

                for cfg in config_files:
                    if (project_path / cfg).exists():
                        config_file = cfg
                        break

                return BuildToolInfo(
                    name=tool_name,
                    version=version,
                    config_file=config_file
                )

        # config file exists but the tool isn't in deps -- still counts
        for _, tool_name, config_files in self.BUILD_TOOL_RULES:
            for cfg in config_files:
                if (project_path / cfg).exists():
                    return BuildToolInfo(name=tool_name, config_file=cfg)

        return None

    def _detect_libraries(self, deps: Dict[str, str]) -> List[str]:
        found = []
        for lib in self.NOTABLE_LIBRARIES:
            if lib in deps:
                found.append(lib)
        return found

    def _detect_package_manager(self, project_path: Path) -> str:
        """Lockfile tells us which package manager they use."""
        if (project_path / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        elif (project_path / 'yarn.lock').exists():
            return 'yarn'
        elif (project_path / 'bun.lockb').exists():
            return 'bun'
        return 'npm'

    def _is_monorepo(self, project_path: Path) -> bool:
        monorepo_files = [
            'pnpm-workspace.yaml',
            'lerna.json',
            'turbo.json',
            'nx.json',
        ]
        for f in monorepo_files:
            if (project_path / f).exists():
                return True

        # "workspaces" in package.json is also a dead giveaway
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
        ts_configs = ['tsconfig.json', 'tsconfig.base.json', 'jsconfig.json']
        for cfg in ts_configs:
            if (project_path / cfg).exists():
                return True
        return False

    def _clean_version(self, version: str) -> str:
        """Strip semver range prefixes like ^, ~, >= to get the bare version."""
        if not version:
            return "unknown"
        version = version.lstrip('^~>=<')
        if ' ' in version:
            version = version.split()[0]
        return version

    def is_minified(self, file_path: str) -> bool:
        """Best-effort guess based on filename and avg line length."""
        try:
            path = Path(file_path)

            name_lower = path.name.lower()
            if '.min.' in name_lower or '-min.' in name_lower or '.bundle.' in name_lower:
                return True

            stat = path.stat()
            if stat.st_size > 500_000:  # >500KB -- almost certainly minified
                return True

            if stat.st_size < 100:
                return False

            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10_000)

            if not content:
                return False

            lines = content.split('\n')
            if len(lines) < 2:
                return len(content) > 1000

            non_empty = [l for l in lines if l.strip()]
            if not non_empty:
                return False

            avg_length = sum(len(l) for l in non_empty) / len(non_empty)
            return avg_length > 200

        except (IOError, OSError):
            return False

    def get_framework_badge(self, info: ProjectInfo) -> Tuple[str, str]:
        """Badge text and color for the GUI."""
        if info.framework:
            badge_text = str(info.framework)
            badge_color = info.framework.color
        else:
            badge_text = "No framework detected"
            badge_color = "#6e7681"

        if info.build_tool:
            badge_text += f" | {info.build_tool.name}"

        return badge_text, badge_color

    def get_scanning_hint(self, project_info: ProjectInfo, project_path: str) -> Optional[Dict[str, Any]]:
        """Suggest next steps, like "build first" for framework projects."""
        FRAMEWORK_HINTS = {
            'React': {
                'hint_type': 'build_required',
                'title': 'React project detected',
                'message': 'Source files (.jsx, .tsx) cannot be analyzed directly.\nRun your build command and scan the output folder.',
                'build_command': 'npm run build',
                'build_folder': 'build',
                'icon': 'info',
            },
            'Next.js': {
                'hint_type': 'build_required',
                'title': 'Next.js project detected',
                'message': 'Source files cannot be analyzed directly.\nBuild the project and scan the output folder.',
                'build_command': 'npm run build',
                'build_folder': 'out',  # "out" for static export, ".next" for SSR
                'icon': 'info',
            },
            'Vue': {
                'hint_type': 'build_required',
                'title': 'Vue project detected',
                'message': 'Single-file components (.vue) cannot be analyzed directly.\nBuild and scan the dist folder.',
                'build_command': 'npm run build',
                'build_folder': 'dist',
                'icon': 'info',
            },
            'Nuxt': {
                'hint_type': 'build_required',
                'title': 'Nuxt project detected',
                'message': 'Vue components cannot be analyzed directly.\nBuild and scan the output folder.',
                'build_command': 'npm run build',
                'build_folder': 'dist',
                'icon': 'info',
            },
            'Angular': {
                'hint_type': 'build_required',
                'title': 'Angular project detected',
                'message': 'TypeScript source cannot be analyzed directly.\nBuild and scan the dist folder.',
                'build_command': 'ng build',
                'build_folder': 'dist',
                'icon': 'info',
            },
            'Svelte': {
                'hint_type': 'build_required',
                'title': 'Svelte project detected',
                'message': 'Svelte components (.svelte) cannot be analyzed directly.\nBuild and scan the output folder.',
                'build_command': 'npm run build',
                'build_folder': 'build',
                'icon': 'info',
            },
            'SvelteKit': {
                'hint_type': 'build_required',
                'title': 'SvelteKit project detected',
                'message': 'Svelte components cannot be analyzed directly.\nBuild and scan the output folder.',
                'build_command': 'npm run build',
                'build_folder': '.svelte-kit',
                'icon': 'info',
            },
            'Solid': {
                'hint_type': 'build_required',
                'title': 'Solid.js project detected',
                'message': 'JSX source files cannot be analyzed directly.\nBuild and scan the output folder.',
                'build_command': 'npm run build',
                'build_folder': 'dist',
                'icon': 'info',
            },
            'Preact': {
                'hint_type': 'build_required',
                'title': 'Preact project detected',
                'message': 'JSX source files cannot be analyzed directly.\nBuild and scan the output folder.',
                'build_command': 'npm run build',
                'build_folder': 'build',
                'icon': 'info',
            },
        }

        if project_info.framework and project_info.framework.name in FRAMEWORK_HINTS:
            return FRAMEWORK_HINTS[project_info.framework.name]

        if project_info.has_typescript and not project_info.framework:
            return {
                'hint_type': 'build_required',
                'title': 'TypeScript project detected',
                'message': 'TypeScript files (.ts) cannot be analyzed directly.\nCompile to JavaScript first.',
                'build_command': 'tsc',
                'build_folder': 'dist',
                'icon': 'info',
            }

        if self._is_server_side_project(project_path, project_info):
            return {
                'hint_type': 'server_side',
                'title': 'Server-side code detected',
                'message': 'This appears to be a Node.js server project.\nBrowser compatibility analysis may show irrelevant warnings for server-only APIs.',
                'build_command': None,
                'build_folder': None,
                'icon': 'info',
            }

        return None

    def _is_server_side_project(self, project_path: str, project_info: ProjectInfo) -> bool:
        """True if this looks like a backend-only Node project."""
        path = Path(project_path)

        # if there's a frontend framework, it's not purely server-side
        if project_info.framework:
            return False

        package_json_path = path / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)

                deps = {}
                deps.update(data.get('dependencies', {}))
                deps.update(data.get('devDependencies', {}))

                server_packages = [
                    'express', 'fastify', 'koa', 'hapi', 'nestjs',
                    '@nestjs/core', 'socket.io', 'ws', 'mongodb',
                    'mongoose', 'sequelize', 'prisma', '@prisma/client',
                    'pg', 'mysql', 'mysql2', 'redis', 'ioredis',
                ]

                browser_packages = [
                    'react', 'react-dom', 'vue', '@angular/core',
                    'svelte', 'preact', 'solid-js', 'jquery',
                ]

                has_server_deps = any(pkg in deps for pkg in server_packages)
                has_browser_deps = any(pkg in deps for pkg in browser_packages)

                if has_server_deps and not has_browser_deps:
                    return True

            except (json.JSONDecodeError, IOError):
                pass

        return False

    def check_build_folders(self, project_path: str) -> Dict[str, bool]:
        """Check which build output folders exist and aren't empty."""
        path = Path(project_path)
        folders = ['build', 'dist', '.next', '.nuxt', '.svelte-kit', 'out']

        result = {}
        for folder in folders:
            folder_path = path / folder
            try:
                result[folder] = folder_path.exists() and any(folder_path.iterdir())
            except (PermissionError, OSError):
                result[folder] = False

        return result
