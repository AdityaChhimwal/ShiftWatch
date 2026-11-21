# Lesson 3: turn our input agreement into executable rules

18 November 2026 · Day 1 · One draft label schema

## Correct the distinction before adding code

You correctly chose prediction 90 for the actual count 100 in Lesson 2. Your explanation also suggested matching by the predicted/actual values. That alternative is incorrect: identity matching uses `record_id`; afterward, the two numerical values are used to measure error.

Two different records can have identical predicted values, and an actual count can differ substantially from its own prediction. Similar or equal numbers cannot tell us which record they belong to. This point has been explained again but not yet independently retested; we do not mark the identity checkpoint passed from an ambiguous explanation.

## Why reading JSON is not enough

Our first examples use JSON text that Python reads into dictionaries and lists. Parsing JSON establishes that the message can be read. It does not establish that its contents make sense for our operation.

For example, both of these messages can be read as JSON:

```json
{"record_id":"hour-10","cnt":100}
```

```json
{"record_id":"hour-10","cnt":-5}
```

The second describes a negative number of rentals. We need an explicit rule to reject it before attaching it to a prediction or calculating performance. The written contract tells a caller what to send; an executable schema lets the program check it. A schema describes expected fields, types, and constraints.

We will use Pydantic, already installed as part of our web-service environment. It supplies the mechanics for checking these declarations and reporting failures. In its class name `BaseModel`, model means a data-validation model; it is unrelated to the future trained rental predictor.

## The small piece we implemented

`src/shiftwatch/contracts.py` contains:

```python
from pydantic import BaseModel, ConfigDict, Field


class LabelRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    record_id: str = Field(min_length=1, max_length=64, pattern=r"^\S+$")
    cnt: int = Field(ge=0)
```

The class groups the rules for one label. By inheriting from `BaseModel`, it uses Pydantic's checking machinery. `record_id: str` declares a text ID. `cnt: int` declares an integer actual count. Neither has a default value, so both are required.

`Field` adds constraints. The ID must contain 1–64 characters and no whitespace; the pattern expresses that last condition. The length bound is a proposed application rule, not something we discovered in the unaudited dataset. `ge=0` means greater than or equal to zero, so zero rentals are allowed and negative counts are rejected. The complete source-data schema remains Day 2 work.

The configuration makes two deliberate choices. `strict=True` rejects a value of the wrong type instead of automatically converting it. Thus `100` is accepted but the text `"100"`, a decimal `100.0`, or a boolean is rejected for this integer count. We want incoming data problems to be visible. `extra="forbid"` rejects fields we did not declare instead of silently ignoring them. For instance, the label sender cannot add an unexplained `prediction` field to this schema.

These are recommended draft rules for this slice. Changing them later is a contract change and needs a reason plus targeted checks. Validation does not strip or silently repair incoming values.

## Trace success and failure

To check a dictionary, call:

```python
label = LabelRecord.model_validate({"record_id": "hour-10", "cnt": 100})
```

Pydantic checks the fields. If the rules pass, it returns a validated `LabelRecord` object. The value can be read as `label.record_id` or `label.cnt`; `label.model_dump()` returns its fields as a dictionary.

For invalid input, Pydantic raises `ValidationError`. An exception means the normal successful path is interrupted; our caller must handle it explicitly. The trace script uses `try` for the attempted validation and `except ValidationError` to collect the failure explanation. It does not replace the bad value or pretend that validation succeeded.

The intended order is: parse the message, validate its shape, check that its session/record ID belongs to saved history, then apply the label with duplicate/conflict rules. We have implemented only the small shape-checking component. A correctly formatted `unseen-42` passes this schema because it has no access to saved prediction history. The later lifecycle must reject that unknown ID; do not confuse a valid format with a valid association.

The service still exposes only GET `/health`. This schema is exercised directly in Python and is not yet wired into a label HTTP route, storage, or prediction error calculation.

## Run what we built

From Git Bash in the project root:

```bash
PYTHONPATH=src ./.venv/Scripts/python.exe examples/contracts/trace_validation.py
```

`PYTHONPATH=src` tells Python where to look for our `shiftwatch` package. It serves the same package-location purpose that `--app-dir src` served in the earlier Uvicorn command. The rest selects the project interpreter and runs the demonstration file.

The assistant executed the interpreter command with PYTHONPATH set in host PowerShell. The Git Bash syntax above expresses that same environment setting; a learner run is unobserved. The trace checks an ordinary valid message, text instead of an integer, a negative count, a missing ID, an unexpected field, and a well-formed but unknown ID. Raw results are saved in `reports/day01/validation-2026-11-18/validation-trace.json`.

Four assistant-authored standard-library tests pass. They verify that valid fields/zero counts survive unchanged; count values cannot be silently coerced; IDs meet their stated constraints; and missing/unexpected fields are not silently ignored. Test output is saved in `unittest.txt` in the same report directory. These are request-schema tests, not learner debugging evidence or complete delayed-label tests.

## One check to resolve the earlier ambiguity

Saved predictions are `hour-09 → 90` and `hour-10 → 120`. A valid label arrives as `{"record_id":"hour-10","cnt":90}`. Which saved prediction belongs to this label—90 or 120—and which field determines the match?

Learner answer on 18 November: "lebel-120 belongs to this because it matches record_id."

Assessment: the selected saved prediction (120) and ID-based reasoning are correct. Clarified terminology: the actual label is 90; 120 is the saved prediction. The absolute error is 30. The narrow ID-matching counterexample is passed after correction/retest. This does not complete the later independent duplicate-label join exercise or establish validation understanding, which remains to be checked in guided traces.

## Reference

Checked against the installed Pydantic 2.14.3 and the official [strict-mode](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/), [configuration](https://pydantic.dev/docs/validation/latest/api/pydantic/config/), and [field](https://pydantic.dev/docs/validation/latest/concepts/fields/) documentation on 18 November 2026. The tests verify the behavior we actually use rather than relying only on documentation.
