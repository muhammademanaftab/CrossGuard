"""Tests for PDF export module."""

import os
import pytest

from src.export.pdf_exporter import export_pdf


@pytest.fixture
def sample_report():
    return {
        'success': True,
        'summary': {
            'total_features': 5, 'html_features': 1,
            'css_features': 2, 'js_features': 2, 'critical_issues': 1,
        },
        'scores': {
            'grade': 'B', 'risk_level': 'medium',
            'simple_score': 82.5, 'weighted_score': 80.0,
        },
        'browsers': {
            'chrome': {
                'version': '120', 'supported': 4, 'partial': 1, 'unsupported': 0,
                'compatibility_percentage': 90.0,
                'unsupported_features': [], 'partial_features': ['css-grid'],
            },
            'safari': {
                'version': '17', 'supported': 3, 'partial': 0, 'unsupported': 2,
                'compatibility_percentage': 60.0,
                'unsupported_features': ['dialog', 'css-nesting'], 'partial_features': [],
            },
        },
        'recommendations': ['Consider polyfills for dialog element'],
    }


class TestExportPdf:
    """export_pdf() creates a valid PDF file."""

    def test_creates_file(self, sample_report, tmp_path):
        out = str(tmp_path / "report.pdf")
        result = export_pdf(sample_report, out)
        assert result == out
        assert os.path.isfile(out)

    def test_file_has_pdf_header(self, sample_report, tmp_path):
        out = str(tmp_path / "report.pdf")
        export_pdf(sample_report, out)
        with open(out, 'rb') as f:
            header = f.read(5)
        assert header == b'%PDF-'

    def test_file_not_empty(self, sample_report, tmp_path):
        out = str(tmp_path / "report.pdf")
        export_pdf(sample_report, out)
        assert os.path.getsize(out) > 1000  # PDF should be reasonably sized

    def test_empty_report_raises(self, tmp_path):
        with pytest.raises(ValueError, match="No analysis report"):
            export_pdf({}, str(tmp_path / "report.pdf"))

    def test_none_report_raises(self, tmp_path):
        with pytest.raises(ValueError, match="No analysis report"):
            export_pdf(None, str(tmp_path / "report.pdf"))

    def test_minimal_report(self, tmp_path):
        """A report with minimal data should still produce a PDF."""
        report = {
            'success': True,
            'summary': {},
            'scores': {},
            'browsers': {},
            'recommendations': [],
        }
        out = str(tmp_path / "minimal.pdf")
        export_pdf(report, out)
        assert os.path.isfile(out)

    def test_no_browsers_report(self, tmp_path):
        """Report with scores but no browsers should work."""
        report = {
            'success': True,
            'summary': {'total_features': 3},
            'scores': {'grade': 'A', 'simple_score': 100.0, 'weighted_score': 100.0},
            'browsers': {},
            'recommendations': [],
        }
        out = str(tmp_path / "no_browsers.pdf")
        export_pdf(report, out)
        assert os.path.isfile(out)

    def test_many_recommendations(self, tmp_path):
        """Report with many recommendations should not crash."""
        report = {
            'success': True,
            'summary': {},
            'scores': {},
            'browsers': {},
            'recommendations': [f"Recommendation #{i}" for i in range(20)],
        }
        out = str(tmp_path / "many_recs.pdf")
        export_pdf(report, out)
        assert os.path.isfile(out)
