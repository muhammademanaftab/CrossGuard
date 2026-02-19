"""Tests for JSON export module."""

import json
import os
import pytest

from src.export.json_exporter import export_json


@pytest.fixture
def sample_report():
    return {
        'success': True,
        'summary': {'total_features': 5, 'html_features': 1, 'css_features': 2, 'js_features': 2},
        'scores': {'grade': 'B', 'simple_score': 82.5},
        'browsers': {'chrome': {'version': '120', 'compatibility_percentage': 90.0}},
    }


class TestExportJsonDict:
    """export_json() without output_path returns enriched dict."""

    def test_returns_dict(self, sample_report):
        result = export_json(sample_report)
        assert isinstance(result, dict)

    def test_adds_generated_by(self, sample_report):
        result = export_json(sample_report)
        assert result['generated_by'] == 'Cross Guard'

    def test_adds_generated_at(self, sample_report):
        result = export_json(sample_report)
        assert 'generated_at' in result

    def test_preserves_original_data(self, sample_report):
        result = export_json(sample_report)
        assert result['success'] is True
        assert result['scores']['grade'] == 'B'

    def test_empty_report_raises(self):
        with pytest.raises(ValueError, match="No analysis report"):
            export_json({})

    def test_none_report_raises(self):
        with pytest.raises(ValueError, match="No analysis report"):
            export_json(None)


class TestExportJsonFile:
    """export_json() with output_path writes file."""

    def test_writes_file(self, sample_report, tmp_path):
        out = str(tmp_path / "report.json")
        result = export_json(sample_report, output_path=out)
        assert result == out
        assert os.path.isfile(out)

    def test_file_is_valid_json(self, sample_report, tmp_path):
        out = str(tmp_path / "report.json")
        export_json(sample_report, output_path=out)
        with open(out) as f:
            data = json.load(f)
        assert data['success'] is True
        assert data['generated_by'] == 'Cross Guard'

    def test_file_has_enriched_data(self, sample_report, tmp_path):
        out = str(tmp_path / "report.json")
        export_json(sample_report, output_path=out)
        with open(out) as f:
            data = json.load(f)
        assert 'generated_at' in data

    def test_pretty_printed(self, sample_report, tmp_path):
        out = str(tmp_path / "report.json")
        export_json(sample_report, output_path=out)
        with open(out) as f:
            text = f.read()
        # indent=2 means newlines and spaces
        assert '\n' in text
        assert '  ' in text
