"""Audit hourly source metadata without examining any rental outcome values."""

import argparse
from collections import Counter
import csv
from datetime import date, timedelta
import json
import math
from pathlib import Path

from fetch_bike_source import digest, verify_cache


METADATA = (
    "instant", "dteday", "season", "yr", "mnth", "hr", "holiday", "weekday",
    "workingday", "weathersit", "temp", "atemp", "hum", "windspeed",
)
OUTCOMES = ("casual", "registered", "cnt")
CATEGORIES = ("season", "yr", "mnth", "hr", "holiday", "weekday", "workingday", "weathersit")
WEATHER = ("temp", "atemp", "hum", "windspeed")


def audit_hourly(rows) -> dict:
    """Project non-outcome cells first; never compare, convert, or summarize labels."""
    rows = iter(rows)
    header = next(rows, None)
    if header != list(METADATA + OUTCOMES):
        raise ValueError("Expected the pinned hourly header, including hr; daily rows are unsupported")
    indexes = {name: header.index(name) for name in METADATA}
    blanks = Counter({name: 0 for name in METADATA})
    categories = {name: Counter() for name in CATEGORIES}
    invalid_weather = Counter({name: 0 for name in WEATHER})
    ids, hours = Counter(), Counter()
    row_count, previous, chronological = 0, None, True

    for line_number, row in enumerate(rows, start=2):
        if len(row) != len(header):
            raise ValueError(f"Wrong column count at CSV line {line_number}; no values logged")
        # Do not construct a full row dictionary: outcome cells stay unaccessed.
        metadata = {name: row[index].strip() for name, index in indexes.items()}
        row_count += 1
        for name, value in metadata.items():
            blanks[name] += value == ""
        for name in CATEGORIES:
            if metadata[name] != "":
                categories[name][metadata[name]] += 1
        for name in WEATHER:
            if metadata[name] != "":
                try:
                    finite = math.isfinite(float(metadata[name]))
                except ValueError:
                    finite = False
                invalid_weather[name] += not finite
        try:
            source_date = date.fromisoformat(metadata["dteday"])
            hour = int(metadata["hr"])
            if not 0 <= hour <= 23:
                raise ValueError
        except ValueError:
            raise ValueError(f"Invalid date/hour at CSV line {line_number}; no values logged") from None
        key = (source_date, hour)
        if previous is not None and key < previous:
            chronological = False
        previous = key
        hours[key] += 1
        if metadata["instant"] != "":
            ids[metadata["instant"]] += 1

    if not row_count:
        raise ValueError("Hourly file contains no observations")
    first, last = min(hours)[0], max(hours)[0]
    calendar_days = (last - first).days + 1
    missing_by_date = {}
    for offset in range(calendar_days):
        source_date = first + timedelta(days=offset)
        missing = [hour for hour in range(24) if (source_date, hour) not in hours]
        if missing:
            missing_by_date[source_date.isoformat()] = missing
    duplicate_ids = sum(count - 1 for count in ids.values())
    unique_ids_prove_unique_rows = blanks["instant"] == 0 and duplicate_ids == 0
    return {
        "scope": {
            "analyzed_columns": list(METADATA),
            "outcome_columns_not_examined": list(OUTCOMES),
            "csv_parsing": "CSV fields are split; only metadata cells are accessed or analyzed",
            "calendar_assumption": "Naive source-calendar date/hour labels; nominal 24 hours per date, no timezone/DST inference",
            "purpose": "Schema/quality inventory only; no learned bins, fitted preprocessing, model, or threshold selection",
        },
        "row_count": row_count,
        "blank_cells_by_metadata_column": dict(blanks),
        "nonblank_invalid_or_nonfinite_weather_by_column": dict(invalid_weather),
        "duplicates": {
            "excess_source_ids": duplicate_ids,
            "excess_date_hour_keys": row_count - len(hours),
            "full_row_duplicates": 0 if unique_ids_prove_unique_rows else None,
            "full_row_method": "Zero follows from unique nonblank source IDs; otherwise unknown without inspecting outcomes",
        },
        "calendar": {
            "first_date": first.isoformat(),
            "last_date": last.isoformat(),
            "distinct_observed_dates": len({key[0] for key in hours}),
            "inclusive_calendar_dates": calendar_days,
            "nominal_hour_slots": calendar_days * 24,
            "unique_observed_date_hour_keys": len(hours),
            "absent_nominal_hour_slots": sum(map(len, missing_by_date.values())),
            "source_order_nondecreasing": chronological,
            "missing_hour_codes_by_date": missing_by_date,
            "gap_interpretation": "Absent source rows; cause and rental count unknown. No rows inserted or zero counts assumed.",
        },
        "category_frequencies_raw_codes": {
            name: dict(sorted(counts.items())) for name, counts in categories.items()
        },
    }


def audit_source(raw_dir: Path, source_record: Path, report_path: Path) -> dict:
    # The public record pins the original snapshot rather than trusting a changed cache manifest.
    record = json.loads(source_record.read_text(encoding="utf-8"))
    verify_cache(raw_dir, record)
    with (raw_dir / "hour.csv").open(encoding="utf-8-sig", newline="") as stream:
        report = audit_hourly(csv.reader(stream))
    report["provenance"] = {
        "source_record_sha256": digest(source_record.read_bytes()),
        "archive_sha256": record["archive"]["sha256"],
        "hour_csv_sha256": record["members"]["hour.csv"]["sha256"],
        "audit_script_sha256": digest(Path(__file__).read_bytes()),
    }
    rendered = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    if report_path.exists():
        if report_path.read_bytes() != rendered:
            raise ValueError("Audit report changed; preserve existing evidence and choose a new path")
    else:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("xb") as output:
            output.write(rendered)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/bike-sharing"))
    parser.add_argument("--source-record", type=Path, default=Path("reports/day02/source-2026-11-21/source.json"))
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = audit_source(args.raw_dir, args.source_record, args.report)
    print(json.dumps({
        "report": args.report.as_posix(),
        "row_count": result["row_count"],
        "blank_metadata_cells": sum(result["blank_cells_by_metadata_column"].values()),
        "absent_nominal_hour_slots": result["calendar"]["absent_nominal_hour_slots"],
        "outcomes_examined": False,
    }, indent=2))
