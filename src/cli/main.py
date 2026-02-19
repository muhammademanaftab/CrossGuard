"""Cross Guard CLI — Click-based command-line interface.

Uses the same AnalyzerService backend as the GUI.

Exit codes:
    0 — All features compatible (or command succeeded)
    1 — Compatibility issues found
    2 — Error (bad input, missing file, etc.)
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click

from src.api.service import AnalyzerService
from src.config import load_config

from .formatters import (
    format_result,
    format_history,
    format_stats,
    format_project_result,
)


def _parse_browsers(browsers_str: Optional[str]) -> Optional[dict]:
    """Parse a 'chrome:120,firefox:121' string into a dict."""
    if not browsers_str:
        return None
    result = {}
    for pair in browsers_str.split(','):
        pair = pair.strip()
        if ':' in pair:
            name, version = pair.split(':', 1)
            result[name.strip().lower()] = version.strip()
    return result or None


def _classify_files(paths: list[str]) -> tuple[list, list, list]:
    """Split file paths into HTML, CSS, and JS lists."""
    html, css, js = [], [], []
    ext_map = {
        '.html': html, '.htm': html,
        '.css': css,
        '.js': js, '.mjs': js, '.jsx': js,
        '.ts': js, '.tsx': js,
    }
    for p in paths:
        ext = os.path.splitext(p)[1].lower()
        target = ext_map.get(ext)
        if target is not None:
            target.append(p)
    return html, css, js


def _collect_files(target: str) -> list[str]:
    """Collect analyzable files from a path (file or directory)."""
    target_path = Path(target)
    if target_path.is_file():
        return [str(target_path)]

    if target_path.is_dir():
        extensions = {'.html', '.htm', '.css', '.js', '.mjs', '.jsx', '.ts', '.tsx'}
        files = []
        for root, dirs, filenames in os.walk(target_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', 'dist', 'build', '__pycache__',
                '.next', '.nuxt', 'vendor',
            }]
            for fname in filenames:
                if os.path.splitext(fname)[1].lower() in extensions:
                    files.append(os.path.join(root, fname))
        return sorted(files)

    return []


@click.group()
@click.version_option(version="1.0.0", prog_name="Cross Guard")
def cli():
    """Cross Guard — Browser Compatibility Checker.

    Analyze HTML, CSS, and JavaScript files for browser compatibility issues
    using the Can I Use database.
    """
    pass


@cli.command()
@click.argument('target')
@click.option('--browsers', '-b', default=None,
              help='Target browsers (e.g., "chrome:120,firefox:121")')
@click.option('--format', '-f', 'fmt', default='table',
              type=click.Choice(['table', 'json', 'summary']),
              help='Output format')
@click.option('--output', '-o', default=None,
              help='Save output to file')
@click.option('--config', '-c', 'config_path', default=None,
              help='Path to crossguard.config.json')
def analyze(target, browsers, fmt, output, config_path):
    """Analyze files or directories for browser compatibility.

    TARGET can be a single file or a directory.
    """
    # Load config
    config = load_config(config_path=config_path)
    service = AnalyzerService(config=config.to_dict())

    # Parse browser overrides
    browser_dict = _parse_browsers(browsers) or config.browsers

    # Collect files
    target_path = Path(target)
    if not target_path.exists():
        click.echo(f"Error: '{target}' not found", err=True)
        sys.exit(2)

    if target_path.is_dir():
        # Project scan mode
        from src.api.project_schemas import ScanConfig
        scan_config = ScanConfig(ignore_dirs=config.ignore_patterns)

        click.echo(f"Scanning {target}...", err=True)
        scan_result = service.scan_project_directory(str(target_path), scan_config)

        if scan_result.total_files == 0:
            click.echo("No analyzable files found.", err=True)
            sys.exit(2)

        click.echo(f"Analyzing {scan_result.total_files} files...", err=True)
        project_result = service.analyze_project(
            scan_result,
            target_browsers=browser_dict,
        )

        if fmt == 'json':
            result_text = format_result(project_result.to_dict(), 'json')
        else:
            result_text = format_project_result(project_result.to_dict())

        has_issues = (project_result.unsupported_count > 0
                      or project_result.partial_count > 0)
    else:
        # Single file mode
        files = [str(target_path)]
        html, css, js = _classify_files(files)

        if not (html or css or js):
            click.echo(f"Error: Unsupported file type: {target}", err=True)
            sys.exit(2)

        result = service.analyze_files(
            html_files=html,
            css_files=css,
            js_files=js,
            target_browsers=browser_dict,
        )

        result_dict = result.to_dict()
        result_text = format_result(result_dict, fmt)

        has_issues = False
        if result.success and result.scores:
            has_issues = result.scores.simple_score < 100

    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(result_text)
        click.echo(f"Report saved to {output}", err=True)
    else:
        click.echo(result_text)

    sys.exit(1 if has_issues else 0)


@cli.command('export')
@click.argument('analysis_id', type=int)
@click.option('--format', '-f', 'fmt', default='json',
              type=click.Choice(['json', 'pdf']),
              help='Export format')
@click.option('--output', '-o', required=True,
              help='Output file path')
def export_cmd(analysis_id, fmt, output):
    """Export a past analysis from history.

    ANALYSIS_ID is the numeric ID from the history command.
    """
    service = AnalyzerService()

    try:
        if fmt == 'json':
            service.export_to_json(analysis_id, output_path=output)
        else:
            service.export_to_pdf(analysis_id, output_path=output)

        click.echo(f"Exported to {output}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except ImportError as e:
        click.echo(f"Missing dependency: {e}", err=True)
        click.echo("Install with: pip install crossguard[gui]", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"Export failed: {e}", err=True)
        sys.exit(2)


@cli.command()
@click.option('--limit', '-n', default=20, help='Number of entries to show')
@click.option('--type', '-t', 'file_type', default=None,
              help='Filter by file type (html, css, js)')
def history(limit, file_type):
    """List past analyses from history."""
    service = AnalyzerService()
    analyses = service.get_analysis_history(limit=limit)

    if file_type:
        analyses = [a for a in analyses
                    if a.get('file_type', '').lower() == file_type.lower()]

    click.echo(format_history(analyses))


@cli.command()
def stats():
    """Show aggregated statistics from all analyses."""
    service = AnalyzerService()
    statistics = service.get_statistics()
    click.echo(format_stats(statistics))


@cli.command('config')
@click.option('--init', 'do_init', is_flag=True,
              help='Create a default crossguard.config.json')
@click.option('--path', 'config_path', default=None,
              help='Path to config file to display')
def config_cmd(do_init, config_path):
    """Show or initialize configuration."""
    if do_init:
        from src.config import ConfigManager
        path = ConfigManager.create_default_config()
        click.echo(f"Created {path}")
        return

    import json
    config = load_config(config_path=config_path)
    click.echo(json.dumps(config.to_dict(), indent=2))

    if config.config_path:
        click.echo(f"\n(Loaded from {config.config_path})", err=True)
    else:
        click.echo("\n(Using defaults — no config file found)", err=True)


@cli.command('update-db')
def update_db():
    """Update the Can I Use database."""
    service = AnalyzerService()

    click.echo("Updating Can I Use database...")
    result = service.update_database(
        progress_callback=lambda msg, pct: click.echo(f"  {msg}", err=True)
    )

    if result.success:
        click.echo(result.message)
    else:
        click.echo(f"Error: {result.message}", err=True)
        if result.error:
            click.echo(f"Details: {result.error}", err=True)
        sys.exit(2)


if __name__ == '__main__':
    cli()
