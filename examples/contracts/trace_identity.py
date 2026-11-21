"""Trace invented teaching data; this is not the production label store."""

import json
from pathlib import Path


def main() -> None:
    example_dir = Path(__file__).resolve().parent
    batch = json.loads((example_dir / "batch.json").read_text(encoding="utf-8"))
    labels = json.loads((example_dir / "labels.json").read_text(encoding="utf-8"))

    # Hand-written estimates illustrate saved predictions; no model is run here.
    saved_predictions = {"hour-09": 120, "hour-10": 90}
    matches = []
    for label in labels["labels"]:
        record_id = label["record_id"]
        prediction = saved_predictions[record_id]
        matches.append({
            "record_id": record_id,
            "prediction": prediction,
            "actual_count": label["cnt"],
            "absolute_error": abs(label["cnt"] - prediction),
        })

    print(json.dumps({
        "evidence_scope": "Invented teaching values; not model evaluation results.",
        "input_order": [record["record_id"] for record in batch["records"]],
        "label_order": [label["record_id"] for label in labels["labels"]],
        "matches": matches,
    }, indent=2))


if __name__ == "__main__":
    main()
