"""Assign whole dates, train the fixed model pair, and build development artifacts."""

import csv
import gzip
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor

from audit_bike_metadata import METADATA, OUTCOMES
from fetch_bike_source import verify_cache
from shiftwatch.drift import make_reference
from shiftwatch.model import ARTIFACTS, CATEGORIES, FEATURES, matrix, predict, sha
from shiftwatch.quality import check_rows, observed_error

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/bike-sharing"
SOURCE = ROOT / "reports/source.json"
SPLITS = ROOT / "configs/splits.json"
ROLES = ("train", "validation", "reference", "development", "final")


def write_json(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(record, indent=2, allow_nan=False) + "\n").encode())


def source_rows():
    with (RAW / "hour.csv").open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        if header != list(METADATA + OUTCOMES):
            raise ValueError("Unexpected hourly source schema")
        yield from reader


def assign_dates(date_counts):
    days = sorted(date_counts)
    if len(days) < 10:
        raise ValueError("At least ten dates are required")
    cuts = [0, *(len(days) * p // 100 for p in (40, 50, 60, 80)), len(days)]
    result = {}
    for role, start, stop in zip(ROLES, cuts[:-1], cuts[1:]):
        dates = days[start:stop]
        result[role] = {"first": dates[0], "last": dates[-1], "dates": len(dates),
                        "rows": sum(date_counts[d] for d in dates)}
    return result


def prepare_splits():
    record = json.loads(SOURCE.read_text())
    verify_cache(RAW, record)
    dates = Counter(row[1] for row in source_rows())
    return {"hour_csv_sha256": record["members"]["hour.csv"]["sha256"],
            "roles": assign_dates(dates), "features": list(FEATURES), "target": "cnt",
            "cut_rule": "Floor cumulative date fractions 40%, 50%, 60%, 80%; whole dates"}


def read_roles(splits, allowed):
    verify_cache(RAW, json.loads(SOURCE.read_text()))
    if sha(RAW / "hour.csv") != splits["hour_csv_sha256"]:
        raise ValueError("Split source checksum mismatch")
    result = {role: [] for role in allowed}
    indexes = {name: METADATA.index(name) for name in FEATURES}
    for cells in source_rows():
        day = cells[1]
        for role in allowed:
            bounds = splits["roles"][role]
            if bounds["first"] <= day <= bounds["last"]:
                row = {name: int(cells[i]) if name in CATEGORIES else float(cells[i])
                       for name, i in indexes.items()}
                row.update(record_id="uci-" + cells[0], event_time=f"{day}T{row['hr']:02}:00:00")
                # The selected role is checked before the target is indexed.
                target = int(cells[-1]) if role != "reference" else None
                result[role].append((row, target))
                break
    for role, examples in result.items():
        examples.sort(key=lambda example: example[0]["event_time"])
        if len(examples) != splits["roles"][role]["rows"]:
            raise ValueError(f"Unexpected row count in {role}")
        _, quality = check_rows([row for row, _ in examples])
        if quality["alert"]:
            raise ValueError(f"Input contract failed in {role}: {quality['issues'][:2]}")
    return result


def model_metrics(models, examples, csv_path):
    rows, targets = zip(*examples)
    predictions = {name: predict(model, rows) for name, model in models.items()}
    actual = dict(enumerate(targets))
    metrics = {}
    for name, values in predictions.items():
        error = observed_error(dict(enumerate(values)), actual, None)
        metrics[name] = {k: error[k] for k in ("predictions", "mae", "rmse")}
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["record_id", "event_time", "actual", *models])
        writer.writerows((row["record_id"], row["event_time"], y, *ys)
                         for row, y, *ys in zip(rows, targets, *predictions.values()))
    return metrics


def train():
    splits = prepare_splits()
    write_json(SPLITS, splits)
    roles = read_roles(splits, ROLES[:-1])
    rows, targets = zip(*roles["train"])
    design = matrix(rows)
    models = {
        "dummy": DummyRegressor(strategy="median"),
        "candidate": HistGradientBoostingRegressor(
            categorical_features=[name in CATEGORIES for name in FEATURES],
            max_iter=100, max_leaf_nodes=15, learning_rate=0.1, l2_regularization=0.1,
            early_stopping=False, random_state=41,
        ),
    }
    for model in models.values():
        model.fit(design, np.array(targets))
    report = ROOT / "reports/development"
    report.mkdir(parents=True, exist_ok=True)
    metrics = model_metrics(models, roles["validation"], report / "predictions.csv")
    write_json(report / "model_metrics.json", metrics)
    if metrics["candidate"]["mae"] >= metrics["dummy"]["mae"]:
        raise RuntimeError("Candidate did not beat the dummy on validation MAE")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(models, ARTIFACTS / "model.joblib", compress=3)
    reference, _ = zip(*roles["reference"])
    write_json(ARTIFACTS / "reference.json", make_reference(reference, predict(models["candidate"], reference)))
    demo = json.dumps(roles["development"], separators=(",", ":"), allow_nan=False).encode()
    (ARTIFACTS / "demo.json.gz").write_bytes(gzip.compress(demo, mtime=0))
    write_json(ARTIFACTS / "manifest.json", {
        "features": list(FEATURES), "scikit_learn": sklearn.__version__,
        "source_sha256": splits["hour_csv_sha256"], "splits_sha256": sha(SPLITS),
        "files": {name: sha(ARTIFACTS / name) for name in ("model.joblib", "reference.json", "demo.json.gz")},
    })
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    train()
