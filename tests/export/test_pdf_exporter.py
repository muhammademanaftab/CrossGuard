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

    def test_creates_valid_pdf(self, sample_report, tmp_path):
        out = str(tmp_path / "report.pdf")
        result = export_pdf(sample_report, out)
        assert result == out
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 1000
        with open(out, 'rb') as f:
            assert f.read(5) == b'%PDF-'

    @pytest.mark.parametrize("bad_input", [{}, None])
    def test_invalid_report_raises(self, bad_input, tmp_path):
        with pytest.raises(ValueError, match="No analysis report"):
            export_pdf(bad_input, str(tmp_path / "report.pdf"))

    @pytest.mark.parametrize("report_name,report_data", [
        ("minimal", {'success': True, 'summary': {}, 'scores': {}, 'browsers': {}, 'recommendations': []}),
        ("no_browsers", {'success': True, 'summary': {'total_features': 3}, 'scores': {'grade': 'A', 'simple_score': 100.0, 'weighted_score': 100.0}, 'browsers': {}, 'recommendations': []}),
        ("many_recs", {'success': True, 'summary': {}, 'scores': {}, 'browsers': {}, 'recommendations': [f"Recommendation #{i}" for i in range(20)]}),
    ])
    def test_edge_case_reports(self, report_name, report_data, tmp_path):
        out = str(tmp_path / f"{report_name}.pdf")
        export_pdf(report_data, out)
        assert os.path.isfile(out)
