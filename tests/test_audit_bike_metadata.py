"""Invented fixtures protect grain, missingness, identity, and holdout boundaries."""

import unittest

from audit_bike_metadata import METADATA, OUTCOMES, audit_hourly


def fixture_row(hour, identifier=None):
    metadata = {
        "instant": str(hour + 1) if identifier is None else identifier,
        "dteday": "2011-01-01", "season": "1", "yr": "0", "mnth": "1", "hr": str(hour),
        "holiday": "0", "weekday": "6", "workingday": "0", "weathersit": "1",
        "temp": "0.4", "atemp": "0.3", "hum": "0.5", "windspeed": "0.1",
    }
    return [metadata[name] for name in METADATA] + ["UNEXAMINED"] * len(OUTCOMES)


def audit(rows):
    return audit_hourly(iter([list(METADATA + OUTCOMES), *rows]))


class MetadataAuditTests(unittest.TestCase):
    def test_daily_grain_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "hourly header"):
            audit_hourly(iter([[name for name in METADATA + OUTCOMES if name != "hr"]]))

    def test_blank_cell_and_absent_hour_are_separate_without_imputation(self):
        rows = [fixture_row(hour) for hour in range(24) if hour != 9]
        rows[0][METADATA.index("hum")] = " "
        report = audit(rows)
        self.assertEqual(report["row_count"], 23)
        self.assertEqual(report["blank_cells_by_metadata_column"]["hum"], 1)
        self.assertEqual(report["calendar"]["absent_nominal_hour_slots"], 1)
        self.assertEqual(report["calendar"]["missing_hour_codes_by_date"], {"2011-01-01": [9]})

    def test_duplicates_remain_counted_and_out_of_order_is_visible(self):
        report = audit([fixture_row(2), fixture_row(1), fixture_row(1)])
        self.assertEqual(report["row_count"], 3)
        self.assertEqual(report["duplicates"]["excess_source_ids"], 1)
        self.assertEqual(report["duplicates"]["excess_date_hour_keys"], 1)
        self.assertIsNone(report["duplicates"]["full_row_duplicates"])
        self.assertFalse(report["calendar"]["source_order_nondecreasing"])

    def test_outcome_cells_are_never_accessed(self):
        class GuardedRow(list):
            def __getitem__(self, index):
                if not isinstance(index, int) or index >= len(METADATA):
                    raise AssertionError("Audit attempted to access a protected outcome")
                return super().__getitem__(index)

        report = audit([GuardedRow(fixture_row(8))])
        self.assertEqual(report["row_count"], 1)
        self.assertEqual(report["duplicates"]["full_row_duplicates"], 0)

    def test_bad_key_stops_audit_and_nonfinite_weather_is_reported(self):
        bad = fixture_row(24)
        with self.assertRaisesRegex(ValueError, "Invalid date/hour"):
            audit([bad])
        row = fixture_row(8)
        row[METADATA.index("temp")] = "nan"
        row[METADATA.index("windspeed")] = "bad"
        report = audit([row])
        self.assertEqual(report["nonblank_invalid_or_nonfinite_weather_by_column"]["temp"], 1)
        self.assertEqual(report["nonblank_invalid_or_nonfinite_weather_by_column"]["windspeed"], 1)


if __name__ == "__main__":
    unittest.main()
