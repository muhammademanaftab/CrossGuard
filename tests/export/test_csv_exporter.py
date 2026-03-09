"""Tests for CSV exporter."""

import csv
import io
import pytest

from src.export.csv_exporter import export_csv


_SAMPLE_REPORT = {
    'success': True,
    'file_path': 'src/style.css',
    'browsers': {
        'chrome': {
            'version': '120',
            'supported': 8,
            'partial': 1,
            'unsupported': 2,
            'unsupported_features': ['CSS Grid', 'CSS Subgrid'],
            'partial_features': ['Flexbox Gap'],
        },
        'firefox': {
            'version': '121',
            'supported': 10,
            'partial': 0,
            'unsupported': 1,
            'unsupported_features': ['CSS Subgrid'],
            'partial_features': [],
        },
    },
}


class TestCsvStructure:
    def test_header_and_row_count(self):
        csv_text = export_csv(_SAMPLE_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        assert rows[0] == ['feature_id', 'feature_name', 'browser', 'version', 'status', 'file_path']
        # Header + 2 unsupported chrome + 1 partial chrome + 1 unsupported firefox = 5
        assert len(rows) == 5

    def test_statuses_and_normalization(self):
        csv_text = export_csv(_SAMPLE_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        next(reader)  # skip header
        rows = list(reader)
        for row in rows:
            assert row[4] in ('unsupported', 'partial')
            assert row[5] == 'src/style.css'
        # First row should have normalized feature_id
        assert rows[0][0] == 'css-grid'


class TestCsvFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.csv'
        result = export_csv(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()
        assert 'feature_id' in out.read_text()

    @pytest.mark.parametrize("bad_input", [{}, None])
    def test_invalid_report_raises(self, bad_input):
        with pytest.raises(ValueError):
            export_csv(bad_input)


class TestCsvEdgeCases:
    def test_no_issues(self):
        report = {
            'file_path': 'app.js',
            'browsers': {
                'chrome': {
                    'version': '120',
                    'unsupported_features': [],
                    'partial_features': [],
                }
            }
        }
        csv_text = export_csv(report)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) == 1  # header only
