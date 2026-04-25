"""Cross Guard CLI. Exit codes: 0=ok, 1=issues/gate fail, 2=error."""

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
)
from .gates import ThresholdConfig, evaluate_gates


_KNOWN_BROWSERS = set(LATEST_VERSIONS.keys())


def _parse_browsers(browsers_str: Optional[str]) -> Optional[dict]:
    """Parses 'chrome:120,firefox:121' — gives a close-match suggestion on unknown browser names."""
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


def _count_issues(report: dict) -> tuple[int, int]:
    errors = 0
    warnings = 0
    browsers = report.get('browsers', {})
    for data in browsers.values():
        if isinstance(data, dict):
            errors += data.get('unsupported', 0)
            warnings += data.get('partial', 0)
    return errors, warnings


# Facade methods on AnalyzerService that serialize a report for each export format.
_EXPORT_METHOD_BY_FORMAT = {
    'sarif': 'export_to_sarif',
    'junit': 'export_to_junit',
    'json': 'export_to_json',
}


def _write_secondary_outputs(service: AnalyzerService, report: dict, **kwargs):
    for fmt_name, path in kwargs.items():
        if path is None:
            continue
        method_name = _EXPORT_METHOD_BY_FORMAT.get(fmt_name)
        if method_name:
            getattr(service, method_name)(report, output_path=path)
            click.echo(f"  {fmt_name.upper()} saved to {path}", err=True)


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

    if verbosity == 0:
        set_log_level('WARNING')
    elif verbosity >= 3:
        set_log_level('DEBUG')
    else:
        set_log_level('INFO')


@cli.command()
@click.argument('target', required=False)
@click.option('--browsers', '-b', default=None, envvar='CROSSGUARD_BROWSERS',
              help='Target browsers (e.g., "chrome:120,firefox:121")')
@click.option('--format', '-f', 'fmt', default=None, envvar='CROSSGUARD_FORMAT',
              type=click.Choice(['table', 'json', 'summary', 'sarif', 'junit']),
              help='Output format (falls back to "output" in crossguard.config.json, else "table")')
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
@click.option('--output-sarif', default=None,
              help='Write SARIF output to this file (independent of --format).')
@click.option('--output-junit', default=None,
              help='Write JUnit XML to this file (independent of --format).')
@click.option('--output-json', 'output_json_path', default=None,
              help='Write JSON output to this file (independent of --format).')
@click.option('--ai', 'ai_enabled', is_flag=True, default=False,
              help='Enable AI fix suggestions (requires a saved or passed API key).')
@click.option('--api-key', default=None, envvar='CROSSGUARD_AI_KEY',
              help='API key for AI fix suggestions (Anthropic or OpenAI). Only used when --ai is set.')
@click.option('--ai-provider', default=None,
              type=click.Choice(['anthropic', 'openai']),
              help='AI provider for fix suggestions (default: anthropic). Only used when --ai is set.')
@click.pass_context
def analyze(ctx, target, browsers, fmt, output, config_path,
            fail_on_score, fail_on_errors, fail_on_warnings,
            use_stdin, stdin_filename,
            output_sarif, output_junit, output_json_path,
            ai_enabled, api_key, ai_provider):
    """Analyze a file for browser compatibility.

    TARGET is a single HTML, CSS, or JavaScript file.
    Use --stdin to read from standard input.
    """
    cli_ctx: CliContext = ctx.obj['cli_ctx']
    start_time = time.perf_counter()

    config = load_config(config_path=config_path)
    service = AnalyzerService(config=config.to_dict())

    # Priority for --format: CLI flag > CROSSGUARD_FORMAT env > config.output_format > 'table'
    if fmt is None:
        fmt = config.output_format
    if fmt not in ('table', 'json', 'summary', 'sarif', 'junit'):
        click.echo(
            f"Error: invalid output format '{fmt}' from config. "
            f"Valid formats: table, json, summary, sarif, junit",
            err=True,
        )
        sys.exit(2)

    browser_dict = _parse_browsers(browsers) or config.browsers

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

        if target_path.is_dir():
            click.echo("Error: Directory analysis is not supported. Please provide a single file.", err=True)
            sys.exit(2)

        html, css, js = _classify_files([str(target_path)])

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

        if fmt in ('sarif', 'junit'):
            result_dict['file_path'] = str(target_path)  # CI exporters need this
            result_text = _format_ci_output(service, result_dict, fmt)
        else:
            result_text = format_result(result_dict, fmt, color=cli_ctx.color)

        score = result.scores['simple_score'] if result.scores else 0.0
        error_count, warning_count = _count_issues(result_dict)

        # Priority: CLI flag/env var > config file > SQLite settings
        ai_key = (api_key
                  or config.ai_config.get('api_key', '')
                  or service.get_setting('ai_api_key', '')
                  or None)
        ai_prov = (ai_provider
                   or config.ai_config.get('provider', '')
                   or service.get_setting('ai_provider', '')
                   or None)

        ai_suggestions = []
        if ai_enabled and not ai_key:
            click.echo(
                "Warning: --ai requires an API key. None found via --api-key, "
                "CROSSGUARD_AI_KEY, or saved settings. "
                "Save one with: crossguard config --set-api-key",
                err=True,
            )
        elif ai_enabled and result.success:
            file_type = 'css' if css else ('js' if js else 'html')
            unsupported = []
            partial = []
            for bdata in result_dict.get('browsers', {}).values():
                unsupported.extend(bdata.get('unsupported_features', []))
                partial.extend(bdata.get('partial_features', []))
            if unsupported or partial:
                ai_suggestions = service.get_ai_fix_suggestions(
                    unsupported_features=list(set(unsupported)),
                    partial_features=list(set(partial)),
                    file_type=file_type,
                    browsers=browser_dict or service.DEFAULT_BROWSERS,
                    api_key=ai_key,
                    provider=ai_prov,
                )

        if ai_suggestions:
            ai_data = [
                {
                    "feature_id": s.feature_id,
                    "feature_name": s.feature_name,
                    "suggestion": s.suggestion,
                    "code_example": s.code_example,
                    "browsers_affected": s.browsers_affected,
                }
                for s in ai_suggestions
            ]

            # Always add to result_dict so secondary outputs get AI data
            result_dict['ai_suggestions'] = ai_data

            if fmt in ('json', 'sarif', 'junit'):
                if fmt in ('sarif', 'junit'):
                    result_text = _format_ci_output(service, result_dict, fmt)
                else:
                    result_text = format_result(result_dict, fmt, color=cli_ctx.color)
            else:
                result_text += "\n\n--- AI Fix Suggestions ---\n"
                for s in ai_suggestions:
                    result_text += f"\n{s.feature_name} ({s.feature_id}):\n"
                    result_text += f"  {s.suggestion}\n"
                    if s.code_example:
                        result_text += f"  Example: {s.code_example}\n"

        # Save to history if enabled (same setting the GUI uses).
        if result.success and service.get_setting_as_bool('auto_save_history', True):
            if use_stdin:
                save_name = stdin_filename
                save_path_str = ''
                save_type = os.path.splitext(stdin_filename)[1].lstrip('.') or 'mixed'
            else:
                save_name = target_path.name
                save_path_str = str(target_path)
                save_type = 'css' if css else ('js' if js else 'html')
            service.save_analysis_to_history(
                result=result,
                file_name=save_name,
                file_path=save_path_str,
                file_type=save_type,
            )

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(result_text)
            if cli_ctx.verbosity >= 1:
                click.echo(f"Report saved to {output}", err=True)
        else:
            click.echo(result_text)

        _write_secondary_outputs(
            service,
            result_dict,
            sarif=output_sarif,
            junit=output_junit,
            json=output_json_path,
        )

        if cli_ctx.timing:
            elapsed = time.perf_counter() - start_time
            click.echo(f"Elapsed: {elapsed:.2f}s", err=True)

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

        has_issues = error_count > 0 or warning_count > 0
        sys.exit(1 if has_issues else 0)

    finally:
        if tmp_file and os.path.exists(tmp_file.name):
            os.unlink(tmp_file.name)


def _format_ci_output(service: AnalyzerService, report: dict, fmt: str) -> str:
    method_name = _EXPORT_METHOD_BY_FORMAT.get(fmt)
    if not method_name:
        return ''
    return getattr(service, method_name)(report)


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


@cli.command()
@click.pass_context
def stats(ctx):
    """Show aggregated statistics from all analyses."""
    cli_ctx: CliContext = ctx.obj['cli_ctx']
    service = AnalyzerService()
    statistics = service.get_statistics()
    click.echo(format_stats(statistics, color=cli_ctx.color))


@cli.command('config')
@click.option('--init', 'do_init', is_flag=True,
              help='Create a default crossguard.config.json')
@click.option('--path', 'config_path', default=None,
              help='Path to config file to display')
@click.option('--set-api-key', 'set_api_key',
              is_flag=False, flag_value='__PROMPT__', default=None,
              help='Save an AI API key. Pass the key directly, or omit the value for a hidden prompt.')
@click.option('--set-ai-provider', 'set_ai_provider', default=None,
              type=click.Choice(['anthropic', 'openai']),
              help='Save the AI provider.')
@click.option('--clear-api-key', 'clear_api_key', is_flag=True,
              help='Remove the saved AI API key.')
def config_cmd(do_init, config_path, set_api_key, set_ai_provider, clear_api_key):
    """Show or manage configuration."""
    service = AnalyzerService()

    did_manage = False

    if set_api_key is not None:
        key = click.prompt('Enter API key', hide_input=True) if set_api_key == '__PROMPT__' else set_api_key
        if not key or not key.strip():
            click.echo('Error: empty API key', err=True)
            sys.exit(2)
        service.set_setting('ai_api_key', key.strip())
        click.echo('API key saved.')
        did_manage = True

    if set_ai_provider is not None:
        service.set_setting('ai_provider', set_ai_provider)
        click.echo(f'AI provider saved: {set_ai_provider}')
        did_manage = True

    if clear_api_key:
        service.set_setting('ai_api_key', '')
        click.echo('API key cleared.')
        did_manage = True

    if did_manage:
        return

    if do_init:
        from src.config import ConfigManager
        path = ConfigManager.create_default_config()
        click.echo(f"Created {path}")
        return

    import json
    config = load_config(config_path=config_path)
    click.echo(json.dumps(config.to_dict(), indent=2))

    saved_key = service.get_setting('ai_api_key', '')
    saved_prov = service.get_setting('ai_provider', '')
    if saved_key or saved_prov:
        click.echo('\nSaved AI settings:')
        if saved_key:
            click.echo(f'  api_key:  {_mask_api_key(saved_key)}')
        if saved_prov:
            click.echo(f'  provider: {saved_prov}')

    if config.config_path:
        click.echo(f"\n(Loaded from {config.config_path})", err=True)
    else:
        click.echo("\n(Using defaults — no config file found)", err=True)


def _mask_api_key(key: str) -> str:
    if not key:
        return '(not set)'
    if len(key) < 8:
        return '****'
    return f'{key[:4]}...{key[-4:]}'


@cli.command('update-db')
@click.option('--check', 'check_only', is_flag=True,
              help='Check for updates without downloading.')
def update_db(check_only):
    """Update the Can I Use database (npm preferred, git fallback)."""
    service = AnalyzerService()

    if check_only:
        info = service.get_database_info()
        click.echo(f"Local version:  {info.npm_version or 'unknown'}")
        click.echo(f"Latest version: {info.npm_latest or 'unknown'}")
        if info.update_available:
            click.echo("Update available! Run 'crossguard update-db' to download.")
        else:
            click.echo("Database is up to date.")
        return

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


@cli.command('init-ci')
@click.option('--provider', '-p', required=True,
              type=click.Choice(['github', 'gitlab']),
              help='CI provider to generate config for.')
def init_ci(provider):
    """Generate a ready-to-use CI workflow configuration."""
    from .generators import generate_ci_config
    click.echo(generate_ci_config(provider))


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
