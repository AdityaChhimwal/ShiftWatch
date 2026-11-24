"""Feature contract and trusted, versioned runtime artifacts."""

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np

FEATURES = ("hr", "weekday", "workingday", "mnth", "temp", "hum", "windspeed", "weathersit")
CATEGORIES = {"hr": (0, 23), "weekday": (0, 6), "workingday": (0, 1), "mnth": (1, 12), "weathersit": (1, 4)}
NUMERIC = ("temp", "hum", "windspeed")
ARTIFACTS = Path(__file__).with_name("artifacts")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix(rows):
    return np.array([[row[name] for name in FEATURES] for row in rows], dtype=float)


def predict(model, rows):
    return np.maximum(0, model.predict(matrix(rows))).tolist() if rows else []


def load_artifacts(directory=ARTIFACTS):
    record = json.loads((directory / "manifest.json").read_text())
    if record["features"] != list(FEATURES):
        raise RuntimeError("Artifact feature contract mismatch")
    for name in ("model.joblib", "reference.json", "demo.json.gz", "policy.json"):
        if sha(directory / name) != record["files"][name]:
            raise RuntimeError(f"Artifact checksum mismatch: {name}")
    import sklearn

    if record["scikit_learn"] != sklearn.__version__:
        raise RuntimeError("Artifact scikit-learn version mismatch")
    # Only bundled release artifacts reach the deserializer.
    models = joblib.load(directory / "model.joblib")
    reference = json.loads((directory / "reference.json").read_text())
    policy = json.loads((directory / "policy.json").read_text())
    return models, reference, policy, record["files"]
