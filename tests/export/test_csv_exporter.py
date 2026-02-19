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
    def test_has_header_row(self):
        csv_text = export_csv(_SAMPLE_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        header = next(reader)
        assert header == ['feature_id', 'feature_name', 'browser', 'version', 'status', 'file_path']

    def test_correct_row_count(self):
        csv_text = export_csv(_SAMPLE_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        # Header + 2 unsupported chrome + 1 partial chrome + 1 unsupported firefox = 5
        assert len(rows) == 5

    def test_unsupported_status(self):
        csv_text = export_csv(_SAMPLE_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        next(reader)  # skip header
        for row in reader:
            assert row[4] in ('unsupported', 'partial')

    def test_feature_id_normalized(self):
        csv_text = export_csv(_SAMPLE_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        next(reader)  # skip header
        row = next(reader)
        assert row[0] == 'css-grid'  # normalized from 'CSS Grid'


class TestCsvFileOutput:
    def test_write_to_file(self, tmp_path):
        out = tmp_path / 'report.csv'
        result = export_csv(_SAMPLE_REPORT, output_path=str(out))
        assert result == str(out)
        assert out.exists()
        content = out.read_text()
        assert 'feature_id' in content

    def test_empty_report_raises(self):
        with pytest.raises(ValueError):
            export_csv({})

    def test_none_report_raises(self):
        with pytest.raises(ValueError):
            export_csv(None)


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

    def test_file_path_in_rows(self):
        csv_text = export_csv(_SAMPLE_REPORT)
        reader = csv.reader(io.StringIO(csv_text))
        next(reader)
        for row in reader:
            assert row[5] == 'src/style.css'
