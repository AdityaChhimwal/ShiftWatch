"""Calibrate on development data and evaluate a locked final period."""

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess

import joblib
import numpy as np

from shiftwatch.drift import apply_policy
from shiftwatch.evaluation import (
    alert_counts, apply_timeline, detect_event, inspect_batch, inspect_replay, rate, recall, select_policy,
)
from shiftwatch.model import ARTIFACTS, load_artifacts, sha
from shiftwatch.quality import observed_error
from shiftwatch.replay import DEV_SEEDS, FINAL_SEEDS, LABEL_DELAY, SCENARIOS, due_labels, days_by_date
from train import ROOT, SPLITS, model_metrics, read_roles, write_json

POLICIES = {"P0": None, "P1-0.1": 0.1, "P1-0.2": 0.2}
FREEZE = ROOT / "reports/freeze.json"


def write_csv(path, rows):
    with io.StringIO(newline="") as buffer:
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        data = buffer.getvalue().encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == ".gz" else data)


def compare_policies(raw_runs, threshold, policies, directory):
    batches, alerts, events, paired, run_metrics = [], [], [], [], []
    for scenario, seed, raw, truth in raw_runs:
        for row in raw:
            if row["label_batch"] is not None:
                performance = row["performance"]
                paired.append({"scenario": scenario, "seed": seed, "step": row["step"],
                               "batch": row["label_batch"], "coverage": performance["coverage"],
                               "labeled": performance["labeled"], "original_mae": row["original"]["mae"],
                               "original_rmse": row["original"]["rmse"], "observed_mae": performance["mae"],
                               "observed_rmse": performance["rmse"]})
        for name, effect in policies.items():
            timeline = apply_timeline(raw, effect, threshold)
            prefix = {"policy": name, "scenario": scenario, "seed": seed}
            if truth:
                events.append({**prefix, **detect_event(timeline, truth)})
            for channel in ("quality", "distribution", "performance"):
                run_metrics.append({**prefix, "channel": channel, **alert_counts(timeline, channel)})
            for row in timeline:
                for channel in ("quality", "distribution", "performance"):
                    status = row[channel]
                    line = {**prefix, "step": row["step"], "channel": channel,
                            "eligible": status["eligible"], "alert": status["alert"],
                            "label_batch": row["label_batch"],
                            "details": json.dumps(row["stats"] if channel == "distribution" else status)}
                    batches.append(line)
                    if status["alert"]:
                        alerts.append({**prefix, "step": row["step"], "channel": channel,
                                       "features": ",".join(status.get("features", []))})
    summary = {}
    for name in policies:
        own_events = [event for event in events if event["policy"] == name]
        aggregate = recall([event for event in own_events if event["channel"] == "distribution"])
        null = {}
        for channel in ("quality", "distribution", "performance"):
            rows = [row for row in run_metrics
                    if row["policy"] == name and row["scenario"] == "stable" and row["channel"] == channel]
            eligible, alerted = (sum(row[key] for row in rows) for key in ("eligible", "alerted"))
            rates = [row["alert_rate"] for row in rows if row["alert_rate"] is not None]
            null[channel] = {"eligible": eligible, "alerted": alerted, "rate": rate(alerted, eligible),
                             "seed_rate_min": min(rates, default=None), "seed_rate_max": max(rates, default=None)}
        summary[name] = {**aggregate, "null_rate": null["distribution"]["rate"], "null_by_channel": null,
                         "events_by_scenario": {scenario: recall([e for e in own_events if e["scenario"] == scenario])
                                                for scenario in SCENARIOS if scenario != "stable"}}
    write_csv(directory / "batch_metrics.csv.gz", batches)
    if alerts:
        write_csv(directory / "alerts.csv.gz", alerts)
    write_csv(directory / "event_metrics.csv", events)
    write_csv(directory / "performance_metrics.csv.gz", paired)
    write_csv(directory / "replay_metrics.csv", run_metrics)
    return summary


def run_controlled(model, examples, seeds):
    return [(scenario, seed, *inspect_replay(model, examples, scenario, seed))
            for scenario in SCENARIOS for seed in seeds]


def natural_replay(model, reference, policy, examples):
    days = days_by_date(examples)
    groups = [sum(days[i:i + 7], []) for i in range(0, len(days), 7)]
    batches = [{"rows": [row for row, _ in group],
                "labels": {row["record_id"]: y for row, y in group}} for group in groups]
    history, predictions, streak = [], [], {}
    for step in range(len(batches) + LABEL_DELAY):
        stats, quality = {}, None
        if step < len(batches):
            forecasts, quality, stats = inspect_batch(model, reference, batches[step]["rows"])
            predictions.append(forecasts)
        distribution = apply_policy(stats, policy["effect"], streak)
        streak = distribution["streak"]
        index, labels = due_labels(batches, step)
        error = observed_error(predictions[index] if index is not None else {}, labels, policy["performance_mae"])
        history.append({"step": step, "first_date": batches[step]["rows"][0]["event_time"][:10]
                        if step < len(batches) else None, "label_batch": index,
                        "quality": json.dumps(quality), "distribution": json.dumps(distribution),
                        "feature_stats": json.dumps(stats), **error})
    return history


def develop():
    manifest = json.loads((ARTIFACTS / "manifest.json").read_text())
    if sha(ARTIFACTS / "model.joblib") != manifest["files"]["model.joblib"]:
        raise ValueError("Model checksum mismatch")
    model = joblib.load(ARTIFACTS / "model.joblib")["candidate"]
    with gzip.open(ARTIFACTS / "demo.json.gz", "rt") as stream:
        examples = json.load(stream)
    runs = run_controlled(model, examples, DEV_SEEDS)
    stable_maes = [row["performance"]["mae"] for scenario, _, rows, _ in runs if scenario == "stable"
                   for row in rows if row["performance"]["eligible"]]
    threshold = float(np.quantile(stable_maes, 0.95))
    directory = ROOT / "reports/development"
    results = compare_policies(runs, threshold, POLICIES, directory)
    effect = select_policy(results)
    policy = {"name": f"P1-{effect}" if effect is not None else "P0",
              "effect": effect, "performance_mae": threshold}
    write_json(ARTIFACTS / "policy.json", policy)
    manifest["files"]["policy.json"] = sha(ARTIFACTS / "policy.json")
    write_json(ARTIFACTS / "manifest.json", manifest)
    write_json(directory / "summary.json", {"seeds": DEV_SEEDS, "controlled_runs": len(runs),
                                          "calibration_batches": len(stable_maes), "selected": policy,
                                          "comparisons": results})
    print(json.dumps(policy))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def frozen_paths():
    return git("ls-files", "src", "configs", "scripts", "requirements.txt", "Dockerfile",
               ".dockerignore", "render.yaml", ".github/workflows/verify.yml",
               "reports/source.json").decode().splitlines()


def frozen_hash(path):
    if path == "scripts/fetch_bike_source.py":
        # Allow trailing-space edits in the acquisition helper while pinning its
        # original committed bytes, which are also recorded in the source manifest.
        subprocess.run(["git", "diff", "HEAD", "--ignore-space-at-eol", "--exit-code", "--", path],
                       cwd=ROOT, check=True, capture_output=True)
        return hashlib.sha256(git("show", "HEAD:" + path)).hexdigest()
    return sha(ROOT / path)


def freeze():
    files = {name: frozen_hash(name) for name in frozen_paths()}
    if not files or any(hashlib.sha256(git("show", "HEAD:" + name)).hexdigest() != expected
                        for name, expected in files.items()):
        raise ValueError("Commit the evaluated code and artifacts first")
    if FREEZE.exists():
        raise ValueError("Freeze already exists")
    write_json(FREEZE, {"commit": git("rev-parse", "HEAD").decode().strip(),
                        "files": files, "development_seeds": DEV_SEEDS, "final_seeds": FINAL_SEEDS})
    print(FREEZE)


def final():
    record = json.loads(FREEZE.read_text())
    if set(record["files"]) != set(frozen_paths()) or any(
        frozen_hash(name) != expected for name, expected in record["files"].items()
    ):
        raise ValueError("Frozen code or artifacts changed")
    if record["final_seeds"] != list(FINAL_SEEDS):
        raise ValueError("Frozen final seeds mismatch")
    models, reference, policy, _ = load_artifacts()
    directory = ROOT / "reports/final"
    # An interrupted attempt stays visible and requires an explicit disposition.
    directory.mkdir(exist_ok=False)
    write_json(directory / "run.json", {"freeze_sha256": sha(FREEZE), "code": record["commit"]})
    examples = read_roles(json.loads(SPLITS.read_text()), ("final",))["final"]
    metrics = model_metrics(models, examples, directory / "predictions.csv")
    write_json(directory / "model_metrics.json", metrics)
    runs = run_controlled(models["candidate"], examples, FINAL_SEEDS)
    policies = {"P0": None, policy["name"]: policy["effect"]}
    results = compare_policies(runs, policy["performance_mae"], policies, directory)
    write_csv(directory / "natural_replay.csv", natural_replay(models["candidate"], reference, policy, examples))
    write_json(directory / "summary.json", {"seeds": FINAL_SEEDS, "controlled_runs": len(runs),
                                          "selected": policy, "comparisons": results})
    hashes = "".join(f"{sha(path)}  {path.name}\n" for path in sorted(directory.iterdir()))
    (directory / "artifacts.sha256").write_bytes(hashes.encode())
    print(json.dumps(metrics))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("develop", "freeze", "final"))
    args = parser.parse_args()
    {"develop": develop, "freeze": freeze, "final": final}[args.stage]()
