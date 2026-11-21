"""Demonstrate draft shape validation using invented request values."""

import json

from pydantic import ValidationError

from shiftwatch.contracts import LabelRecord


def main() -> None:
    cases = [
        ("valid_label", {"record_id": "hour-10", "cnt": 100}),
        ("numeric_text", {"record_id": "hour-10", "cnt": "100"}),
        ("negative_count", {"record_id": "hour-10", "cnt": -5}),
        ("missing_id", {"cnt": 100}),
        ("unexpected_field", {"record_id": "hour-10", "cnt": 100, "prediction": 90}),
        ("unknown_but_well_formed_id", {"record_id": "unseen-42", "cnt": 100}),
    ]
    observations = []
    for name, payload in cases:
        try:
            label = LabelRecord.model_validate(payload)
        except ValidationError as error:
            observations.append({
                "case": name,
                "shape_valid": False,
                "errors": error.errors(include_input=False, include_url=False),
            })
        else:
            observations.append({
                "case": name,
                "shape_valid": True,
                "validated_fields": label.model_dump(),
            })
    print(json.dumps({
        "evidence_scope": "Synthetic request-shape demonstration; no ID existence lookup or storage.",
        "observations": observations,
    }, indent=2))


if __name__ == "__main__":
    main()
