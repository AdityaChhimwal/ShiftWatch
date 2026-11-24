"""Validate observations before prediction or distribution checks."""

from collections import Counter
from datetime import datetime
import math
import re

from .model import CATEGORIES, FEATURES, NUMERIC

ID = re.compile(r"[!-~]{1,64}")
MAX_COUNT = 1_000_000_000


def check_rows(rows):
    ids = Counter(
        row["record_id"] for row in rows
        if isinstance(row, dict) and isinstance(row.get("record_id"), str)
    )
    good, issues = [], []
    for index, row in enumerate(rows):
        errors = []
        if not isinstance(row, dict):
            issues.append({"row": index + 1, "issues": ["Expected an object"]})
            continue
        record_id = row.get("record_id")
        if not isinstance(record_id, str) or not ID.fullmatch(record_id):
            errors.append("Invalid record_id")
        elif ids[record_id] > 1:
            errors.append("Duplicate record_id")
        try:
            event_time = row.get("event_time")
            if not isinstance(event_time, str) or len(event_time) != 19:
                raise ValueError
            parsed_time = datetime.fromisoformat(event_time)
            if event_time != parsed_time.isoformat() or parsed_time.minute or parsed_time.second:
                raise ValueError
            if parsed_time.hour != row.get("hr") or parsed_time.month != row.get("mnth"):
                errors.append("event_time disagrees with hr or mnth")
        except ValueError:
            errors.append("event_time must be YYYY-MM-DDTHH:00:00")
        for name, (low, high) in CATEGORIES.items():
            value = row.get(name)
            if type(value) is not int or not low <= value <= high:
                errors.append(f"{name} must be an integer in [{low}, {high}]")
        for name in NUMERIC:
            value = row.get(name)
            if type(value) not in (int, float) or not 0 <= value <= 1:
                errors.append(f"{name} must be finite and in [0, 1]")
        if set(row) - {*FEATURES, "record_id", "event_time"}:
            errors.append("Unexpected fields")
        if errors:
            issues.append({"row": index + 1, "issues": errors})
        else:
            good.append(row)
    return good, {"submitted": len(rows), "accepted": len(good), "rejected": len(issues),
                  "alert": bool(issues), "issues": issues}


def observed_error(predictions, labels, threshold):
    errors = [labels[key] - value for key, value in predictions.items() if key in labels]
    count, total = len(errors), len(predictions)
    mae = sum(map(abs, errors)) / count if count else None
    rmse = math.sqrt(sum(error * error for error in errors) / count) if count else None
    eligible = count == total and count >= 100
    return {"labeled": count, "predictions": total, "coverage": count / total if total else None,
            "mae": mae, "rmse": rmse, "eligible": eligible,
            "alert": eligible and threshold is not None and mae > threshold,
            "status": "unknown" if not count else "partial" if count < total else
                      "insufficient data" if not eligible else "observed"}
