"""Protect source reproducibility with small invented archives, never real labels."""

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from fetch_bike_source import ARCHIVE_NAME, fetch_source


def fixture_archive(include_hour=True):
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("Readme.txt", "Invented test fixture; not UCI observations.")
        archive.writestr("day.csv", "dteday,cnt\n2011-01-01,7\n")
        if include_hour:
            archive.writestr("hour.csv", "dteday,hr,cnt\n2011-01-01,0,7\n")
    return buffer.getvalue()


class SourceSnapshotTests(unittest.TestCase):
    def test_repeated_fetch_verifies_cache_without_downloading_or_changing_record(self):
        payload = fixture_archive()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, report = root / "raw", root / "report.json"
            with patch("fetch_bike_source.urlopen", return_value=io.BytesIO(payload)) as request:
                first, downloaded = fetch_source(raw, report)
                second, downloaded_again = fetch_source(raw, report)
            self.assertTrue(downloaded)
            self.assertFalse(downloaded_again)
            request.assert_called_once()
            self.assertEqual(first, second)
            self.assertEqual((raw / ARCHIVE_NAME).read_bytes(), payload)
            self.assertEqual(first["members"]["hour.csv"]["columns"], ["dteday", "hr", "cnt"])

    def test_changed_raw_file_fails_without_replacing_the_recorded_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw, report = root / "raw", root / "report.json"
            with patch("fetch_bike_source.urlopen", return_value=io.BytesIO(fixture_archive())):
                fetch_source(raw, report)
            original_report = report.read_bytes()
            (raw / "hour.csv").write_text("changed", encoding="utf-8")
            with patch("fetch_bike_source.urlopen") as request:
                with self.assertRaises(ValueError):
                    fetch_source(raw, report)
            request.assert_not_called()
            self.assertEqual(report.read_bytes(), original_report)
            self.assertEqual(json.loads(original_report)["selected_file"], "hour.csv")

    def test_wrong_archive_layout_fails_before_a_snapshot_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("fetch_bike_source.urlopen", return_value=io.BytesIO(fixture_archive(include_hour=False))):
                with self.assertRaises(ValueError):
                    fetch_source(root / "raw", root / "report.json")
            self.assertFalse((root / "raw").exists())
            self.assertFalse((root / "report.json").exists())


if __name__ == "__main__":
    unittest.main()
