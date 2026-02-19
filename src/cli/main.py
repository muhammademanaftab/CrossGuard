"""Cross Guard CLI — Click-based command-line interface.

Uses the same AnalyzerService backend as the GUI.

Exit codes:
    0 — All features compatible (or command succeeded)
    1 — Compatibility issues found (or quality gate failed)
    2 — Error (bad input, missing file, etc.)
"""

import difflib
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

import click

from src.api.service import AnalyzerService
from src.config import load_config
from src.utils.config import LATEST_VERSIONS, set_log_level

from .context import CliContext
from .formatters import (
    format_result,
    format_history,
    format_stats,
    format_project_result,
)
from .gates import ThresholdConfig, evaluate_gates
from .ignore import find_ignore_file, load_ignore_patterns, should_ignore


# ── Browser validation ────────────────────────────────────────────────

_KNOWN_BROWSERS = set(LATEST_VERSIONS.keys())


def _parse_browsers(browsers_str: Optional[str]) -> Optional[dict]:
    """Parse a 'chrome:120,firefox:121' string into a dict.

    Raises click.BadParameter on invalid input with helpful suggestions.
    """
    if not browsers_str:
        return None
    result = {}
    for pair in browsers_str.split(','):
        pair = pair.strip()
        if not pair:
            continue
        if ':' not in pair:
            raise click.BadParameter(
                f"Invalid format '{pair}'. Expected 'name:version' "
                f"(e.g., 'chrome:120').",
                param_hint="'--browsers'",
            )
        name, version = pair.split(':', 1)
        name = name.strip().lower()
        version = version.strip()

        if name not in _KNOWN_BROWSERS:
            close = difflib.get_close_matches(name, _KNOWN_BROWSERS, n=1, cutoff=0.5)
            suggestion = f" Did you mean '{close[0]}'?" if close else ""
            raise click.BadParameter(
                f"Unknown browser '{name}'.{suggestion} "
                f"Known browsers: {', '.join(sorted(_KNOWN_BROWSERS))}",
                param_hint="'--browsers'",
            )

        # Version should be numeric (e.g. 120 or 18.4)
        try:
            float(version)
        except ValueError:
            raise click.BadParameter(
                f"Invalid version '{version}' for {name}. "
                f"Version must be numeric (e.g., '120' or '18.4').",
                param_hint="'--browsers'",
            )

        result[name] = version
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


def _collect_files(
    target: str,
    ignore_patterns: Optional[list[str]] = None,
) -> list[str]:
    """Collect analyzable files from a path (file or directory).

    Args:
        target: File or directory path.
        ignore_patterns: Optional list of .crossguardignore patterns.
    """
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
                    full_path = os.path.join(root, fname)
                    # Apply .crossguardignore patterns
                    if ignore_patterns:
                        rel_path = os.path.relpath(full_path, str(target_path))
                        if should_ignore(rel_path, ignore_patterns):
                            continue
                    files.append(full_path)
        return sorted(files)

    return []


# ── Issue counting helper ─────────────────────────────────────────────


def _count_issues(report: dict) -> tuple[int, int]:
    """Return (error_count, warning_count) from a report dict.

    error_count = total unsupported across browsers.
    warning_count = total partial across browsers.
    """
    errors = 0
    warnings = 0
    browsers = report.get('browsers', {})
    for data in browsers.values():
        if isinstance(data, dict):
            errors += data.get('unsupported', 0)
            warnings += data.get('partial', 0)
    return errors, warnings


# ── Multi-output helper ───────────────────────────────────────────────


def _write_secondary_outputs(report: dict, **kwargs):
    """Write secondary output files (--output-sarif, --output-junit, etc.).

    Keyword args are {format_name: output_path} pairs.
    Only non-None paths trigger output.
    """
    from src.export import export_sarif, export_junit, export_checkstyle, export_csv

    exporters = {
        'sarif': export_sarif,
        'junit': export_junit,
        'checkstyle': export_checkstyle,
        'csv': export_csv,
        'json': None,  # handled below
    }

    for fmt_name, path in kwargs.items():
        if path is None:
            continue
        exporter = exporters.get(fmt_name)
        if exporter:
            exporter(report, output_path=path)
            click.echo(f"  {fmt_name.upper()} saved to {path}", err=True)
        elif fmt_name == 'json':
            from src.export import export_json
            export_json(report, output_path=path)
            click.echo(f"  JSON saved to {path}", err=True)


# ── CLI group ─────────────────────────────────────────────────────────


@click.group()
@click.version_option(version="1.0.0", prog_name="Cross Guard")
@click.option('-v', '--verbose', count=True,
              help='Increase verbosity (-v, -vv, -vvv).')
@click.option('-q', '--quiet', is_flag=True, help='Suppress non-essential output.')
@click.option('--debug', is_flag=True, help='Maximum verbosity (equals -vvv).')
@click.option('--no-color', is_flag=True, envvar='NO_COLOR',
              help='Disable colored output.')
@click.option('--timing', is_flag=True, help='Print elapsed time to stderr.')
@click.pass_context
def cli(ctx, verbose, quiet, debug, no_color, timing):
    """Cross Guard — Browser Compatibility Checker.

    Analyze HTML, CSS, and JavaScript files for browser compatibility issues
    using the Can I Use database.
    """
    ctx.ensure_object(dict)
    verbosity = CliContext.resolve_verbosity(verbose, quiet, debug)
    ctx.obj['cli_ctx'] = CliContext(
        verbosity=verbosity,
        color=CliContext.detect_color(no_color),
        timing=timing,
    )

    # Configure logging level based on verbosity
    if verbosity == 0:
        set_log_level('WARNING')
    elif verbosity >= 3:
        set_log_level('DEBUG')
    else:
        set_log_level('INFO')


# ── analyze ───────────────────────────────────────────────────────────


@cli.command()
@click.argument('target', required=False)
@click.option('--browsers', '-b', default=None, envvar='CROSSGUARD_BROWSERS',
              help='Target browsers (e.g., "chrome:120,firefox:121")')
@click.option('--format', '-f', 'fmt', default='table', envvar='CROSSGUARD_FORMAT',
              type=click.Choice(['table', 'json', 'summary', 'sarif', 'junit',
                                 'checkstyle', 'csv']),
              help='Output format')
@click.option('--output', '-o', default=None,
              help='Save output to file')
@click.option('--config', '-c', 'config_path', default=None, envvar='CROSSGUARD_CONFIG',
              help='Path to crossguard.config.json')
@click.option('--fail-on-score', type=float, default=None,
              help='Fail (exit 1) if score is below this value.')
@click.option('--fail-on-errors', type=int, default=None,
              help='Fail (exit 1) if unsupported feature count exceeds this.')
@click.option('--fail-on-warnings', type=int, default=None,
              help='Fail (exit 1) if partial feature count exceeds this.')
@click.option('--stdin', 'use_stdin', is_flag=True,
              help='Read file content from stdin.')
@click.option('--stdin-filename', default=None,
              help='Filename for stdin content (required with --stdin).')
@click.option('--ignore-path', default=None,
              help='Path to a custom ignore file.')
@click.option('--output-sarif', default=None,
              help='Write SARIF output to this file (independent of --format).')
@click.option('--output-junit', default=None,
              help='Write JUnit XML to this file (independent of --format).')
@click.option('--output-json', 'output_json_path', default=None,
              help='Write JSON output to this file (independent of --format).')
@click.option('--output-checkstyle', default=None,
              help='Write Checkstyle XML to this file (independent of --format).')
@click.option('--output-csv', default=None,
              help='Write CSV output to this file (independent of --format).')
@click.pass_context
def analyze(ctx, target, browsers, fmt, output, config_path,
            fail_on_score, fail_on_errors, fail_on_warnings,
            use_stdin, stdin_filename, ignore_path,
            output_sarif, output_junit, output_json_path,
            output_checkstyle, output_csv):
    """Analyze files or directories for browser compatibility.

    TARGET can be a single file or a directory.
    Use --stdin to read from standard input.
    """
    cli_ctx: CliContext = ctx.obj['cli_ctx']
    start_time = time.perf_counter()

    # Load config
    config = load_config(config_path=config_path)
    service = AnalyzerService(config=config.to_dict())

    # Parse browser overrides
    browser_dict = _parse_browsers(browsers) or config.browsers

    # ── stdin mode ────────────────────────────────────────────────
    tmp_file = None
    if use_stdin:
        if not stdin_filename:
            click.echo("Error: --stdin-filename is required when using --stdin", err=True)
            sys.exit(2)
        content = click.get_text_stream('stdin').read()
        if not content.strip():
            click.echo("Error: stdin is empty", err=True)
            sys.exit(2)
        ext = os.path.splitext(stdin_filename)[1]
        if not ext:
            click.echo(f"Error: Cannot detect file type from '{stdin_filename}'", err=True)
            sys.exit(2)
        tmp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix=ext, delete=False, encoding='utf-8',
        )
        tmp_file.write(content)
        tmp_file.close()
        target = tmp_file.name

    try:
        if not target:
            click.echo("Error: TARGET argument is required (or use --stdin)", err=True)
            sys.exit(2)

        target_path = Path(target)
        if not target_path.exists():
            click.echo(f"Error: '{target}' not found", err=True)
            sys.exit(2)

        # ── .crossguardignore ────────────────────────────────────
        ignore_pats: Optional[list[str]] = None
        if ignore_path:
            ignore_pats = load_ignore_patterns(Path(ignore_path))
        elif target_path.is_dir():
            ig_file = find_ignore_file(target_path)
            if ig_file:
                ignore_pats = load_ignore_patterns(ig_file)
                if cli_ctx.verbosity >= 2:
                    click.echo(f"Using ignore file: {ig_file}", err=True)

        # ── directory mode ───────────────────────────────────────
        if target_path.is_dir():
            from src.api.project_schemas import ScanConfig
            scan_config = ScanConfig(exclude_patterns=config.ignore_patterns)

            if cli_ctx.verbosity >= 1:
                click.echo(f"Scanning {target}...", err=True)

            scan_result = service.scan_project_directory(str(target_path), scan_config)

            if scan_result.total_files == 0:
                click.echo("No analyzable files found.", err=True)
                sys.exit(2)

            if cli_ctx.verbosity >= 1:
                click.echo(f"Analyzing {scan_result.total_files} files...", err=True)

            project_result = service.analyze_project(
                scan_result,
                target_browsers=browser_dict,
            )

            result_dict = project_result.to_dict()

            if fmt == 'json':
                result_text = format_result(result_dict, 'json')
            elif fmt in ('sarif', 'junit', 'checkstyle', 'csv'):
                result_text = _format_ci_output(result_dict, fmt)
            else:
                result_text = format_project_result(result_dict, color=cli_ctx.color)

            score = project_result.overall_score
            error_count, warning_count = _count_issues(result_dict)

        # ── single-file mode ─────────────────────────────────────
        else:
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

            if fmt in ('sarif', 'junit', 'checkstyle', 'csv'):
                # Add file_path for CI exporters
                result_dict['file_path'] = str(target_path)
                result_text = _format_ci_output(result_dict, fmt)
            else:
                result_text = format_result(result_dict, fmt, color=cli_ctx.color)

            score = result.scores.simple_score if result.scores else 0.0
            error_count, warning_count = _count_issues(result_dict)

        # ── output ───────────────────────────────────────────────
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result_text)
            if cli_ctx.verbosity >= 1:
                click.echo(f"Report saved to {output}", err=True)
        else:
            click.echo(result_text)

        # ── secondary outputs ────────────────────────────────────
        _write_secondary_outputs(
            result_dict,
            sarif=output_sarif,
            junit=output_junit,
            json=output_json_path,
            checkstyle=output_checkstyle,
            csv=output_csv,
        )

        # ── timing ───────────────────────────────────────────────
        if cli_ctx.timing:
            elapsed = time.perf_counter() - start_time
            click.echo(f"Elapsed: {elapsed:.2f}s", err=True)

        # ── quality gates ────────────────────────────────────────
        gate_config = ThresholdConfig(
            min_score=fail_on_score,
            max_errors=fail_on_errors,
            max_warnings=fail_on_warnings,
        )
        has_gates = any(v is not None for v in
                        [fail_on_score, fail_on_errors, fail_on_warnings])

        if has_gates:
            gate_result = evaluate_gates(score, error_count, warning_count, gate_config)
            if not gate_result.passed:
                for failure in gate_result.failures:
                    click.echo(f"GATE FAILED: {failure}", err=True)
                sys.exit(1)
            sys.exit(0)

        # Default: exit 1 if any issues
        has_issues = error_count > 0 or warning_count > 0
        sys.exit(1 if has_issues else 0)

    finally:
        if tmp_file and os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)


def _format_ci_output(report: dict, fmt: str) -> str:
    """Dispatch to CI exporters, returning string output."""
    from src.export import export_sarif, export_junit, export_checkstyle, export_csv

    if fmt == 'sarif':
        import json
        return json.dumps(export_sarif(report), indent=2)
    elif fmt == 'junit':
        return export_junit(report)
    elif fmt == 'checkstyle':
        return export_checkstyle(report)
    elif fmt == 'csv':
        return export_csv(report)
    return ''


# ── export ────────────────────────────────────────────────────────────


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


# ── history ───────────────────────────────────────────────────────────


@cli.command()
@click.option('--limit', '-n', default=20, help='Number of entries to show')
@click.option('--type', '-t', 'file_type', default=None,
              help='Filter by file type (html, css, js)')
@click.pass_context
def history(ctx, limit, file_type):
    """List past analyses from history."""
    cli_ctx: CliContext = ctx.obj['cli_ctx']
    service = AnalyzerService()
    analyses = service.get_analysis_history(limit=limit)

    if file_type:
        analyses = [a for a in analyses
                    if a.get('file_type', '').lower() == file_type.lower()]

    click.echo(format_history(analyses, color=cli_ctx.color))


# ── stats ─────────────────────────────────────────────────────────────


@cli.command()
@click.pass_context
def stats(ctx):
    """Show aggregated statistics from all analyses."""
    cli_ctx: CliContext = ctx.obj['cli_ctx']
    service = AnalyzerService()
    statistics = service.get_statistics()
    click.echo(format_stats(statistics, color=cli_ctx.color))


# ── config ────────────────────────────────────────────────────────────


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


# ── update-db ─────────────────────────────────────────────────────────


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


# ── init-ci ───────────────────────────────────────────────────────────


@cli.command('init-ci')
@click.option('--provider', '-p', required=True,
              type=click.Choice(['github', 'gitlab']),
              help='CI provider to generate config for.')
def init_ci(provider):
    """Generate a ready-to-use CI workflow configuration."""
    from .generators import generate_ci_config
    click.echo(generate_ci_config(provider))


# ── init-hooks ────────────────────────────────────────────────────────


@cli.command('init-hooks')
@click.option('--type', '-t', 'hook_type', required=True,
              type=click.Choice(['pre-commit']),
              help='Hook type to generate config for.')
def init_hooks(hook_type):
    """Generate a hooks configuration snippet."""
    from .generators import generate_hooks_config
    click.echo(generate_hooks_config(hook_type))


if __name__ == '__main__':
    cli()
