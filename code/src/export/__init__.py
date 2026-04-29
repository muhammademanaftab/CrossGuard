"""Export formats: JSON, PDF, SARIF, JUnit.

Imports are deferred so users who only need SARIF/JSON/JUnit don't have to
install reportlab (which is in the [gui] extra). Each function loads its
backend on first call.
"""


def export_json(*args, **kwargs):
    from .json_exporter import export_json as _f
    return _f(*args, **kwargs)


def export_pdf(*args, **kwargs):
    from .pdf_exporter import export_pdf as _f
    return _f(*args, **kwargs)


def export_sarif(*args, **kwargs):
    from .sarif_exporter import export_sarif as _f
    return _f(*args, **kwargs)


def export_junit(*args, **kwargs):
    from .junit_exporter import export_junit as _f
    return _f(*args, **kwargs)


__all__ = [
    'export_json',
    'export_pdf',
    'export_sarif',
    'export_junit',
]
