"""Exercise the session HTTP API, or measure 30 warm maximum-row requests."""

import argparse
import csv
import io
import json
from pathlib import Path
from statistics import median, quantiles
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def client(base):
    def call(path, data=None, token=None, expected=200):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        body = json.dumps(data).encode() if data is not None else None
        if body:
            headers["Content-Type"] = "application/json"
        try:
            response = urlopen(Request(base + path, body, headers), timeout=30)
        except HTTPError as error:
            response = error
        with response:
            payload = response.read()
            if response.status != expected:
                raise AssertionError(f"{path}: expected {expected}, got {response.status}")
            return json.loads(payload) if response.headers.get_content_type() == "application/json" else payload
    return call


def row(record_id):
    return {"record_id": record_id, "event_time": "2012-06-04T08:00:00", "hr": 8,
            "weekday": 1, "workingday": 1, "mnth": 6, "temp": 0.55, "hum": 0.61,
            "windspeed": 0.15, "weathersit": 1}


def create(call, mode):
    info = call("/sessions", {"mode": mode}, expected=201)
    return "/sessions/" + info["session_id"], info["token"]


def verify(call):
    assert b"Batch timeline" in call("/")
    assert len(call("/scenarios")) == 6
    assert b"record_id,event_time" in call("/assets/example-batch.csv")
    base, token = create(call, "custom")
    other, other_token = create(call, "stable")
    bad = {**row("bad"), "hum": None}
    body = {"batch_id": "batch-1", "rows": [row("=safe"), row("b"), bad]}
    batch = call(base + "/batches", body, token)["timeline"][0]
    assert batch["quality"]["rejected"] == 1 and not batch["distribution"]["eligible"]
    assert batch["performance"]["status"] == "unknown"
    assert len(call(base + "/batches", body, token)["timeline"]) == 1
    call(base + "/batches", {**body, "rows": [row("changed")]}, token, 409)
    call(base + "/batches", {"batch_id": "new", "rows": [row("b")]}, token, 409)
    labels = {"rows": [{"record_id": "b", "cnt": 27}, {"record_id": "bad", "cnt": 19}]}
    call(base + "/labels", labels, token, 422)
    assert call(base + "/report", token=token)["timeline"][0]["performance"]["labeled"] == 0
    labels["rows"][1]["record_id"] = "=safe"
    assert call(base + "/labels", labels, token)["new_labels"] == 2
    assert call(base + "/labels", labels, token)["new_labels"] == 0
    call(base + "/labels", {"rows": [{"record_id": "b", "cnt": 23}]}, token, 409)
    export = call(base + "/export", token=token)
    assert {record["id"]: record["actual"] for record in export["predictions"]} == {"b": 27, "=safe": 19}
    assert b"'=safe" in call(base + "/export?format=csv", token=token)
    for path in ("report", "export"):
        call(base + "/" + path, token=other_token, expected=404)
    call(base + "/batches", body, other_token, 404)
    call(base + "/batches", {"batch_id": "too-big", "rows": ["x" * 256_000]}, token, 413)
    call(base + "/batches", {"batch_id": "too-many", "rows": [None] * 501}, token, 422)
    call(other + "/step", {"step": 2}, other_token, 409)
    for index in range(26):
        report = call(other + "/step", {"step": index}, other_token)
        assert report["step"] == index + 1
        if index < 2:
            assert report["timeline"][0]["performance"]["status"] == "unknown"
        if index == 2:
            assert report["timeline"][0]["performance"]["coverage"] == 1
            assert report["timeline"][0]["performance"]["label_step"] == 2
            assert call(other + "/step", {"step": index}, other_token)["step"] == 3
    assert report["incident"] is None and len(report["timeline"]) == 24
    assert report["timeline"][-1]["performance"]["coverage"] == 1
    print(json.dumps({"dashboard": "passed", "custom_lifecycle": "passed", "session_isolation": "passed",
                      "limits": "passed", "replay_steps_and_flush": 26}, indent=2))


def benchmark(call, directory, host):
    timings = []
    for group in range(2):
        base, token = create(call, "custom")
        for batch in range(16 if group == 0 else 15):
            rows = [row(f"row-{batch}-{index}") for index in range(500)]
            body = {"batch_id": str(batch), "rows": rows}
            before = perf_counter()
            report = call(base + "/batches", body, token)
            elapsed = (perf_counter() - before) * 1000
            assert report["timeline"][-1]["quality"]["accepted"] == 500
            if group or batch:
                timings.append(elapsed)
    directory.mkdir(parents=True, exist_ok=True)
    table = io.StringIO(newline="")
    writer = csv.writer(table, lineterminator="\n")
    writer.writerow(["request", "elapsed_ms"])
    writer.writerows(enumerate(timings, 1))
    (directory / "timings.csv").write_bytes(table.getvalue().encode())
    summary = {"host": host, "requests": len(timings), "rows": 500, "concurrency": 1,
               "p50_ms": median(timings), "p95_ms": quantiles(timings, n=100, method="inclusive")[94]}
    (directory / "runtime.json").write_bytes((json.dumps(summary, indent=2) + "\n").encode())
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--benchmark", type=Path)
    parser.add_argument("--host", default="local")
    args = parser.parse_args()
    call = client(args.url.rstrip("/"))
    if args.benchmark:
        benchmark(call, args.benchmark, args.host)
    else:
        verify(call)
