# Lesson 2: keep the prediction and its actual outcome connected

18 November 2026 · Day 1 · Draft contracts and a runnable teaching example

## Start where the first lesson left us

Our `/health` function always returns the same small dictionary. It does not load a model or compare predictions with actual outcomes. Therefore, a successful response tells us that the application answered this request. Your independent explanation of that distinction is still unassessed; asking to continue did not count as a passed answer.

Now imagine replacing that simple request with a useful one: send several hours of weather/calendar inputs and ask for estimated bike rentals. Before writing more routes, we need to agree on what the request contains. That agreement is called a contract. It lets the caller know what to send and lets the application know what to expect.

## Give each record a lasting identity

An hourly observation is one record. Several records submitted together form a batch. We need both a batch ID and a record ID because they identify different things: the group that was submitted and one particular item inside that group. IDs are metadata that help the software organize its work; the predictor does not use them to estimate rental counts.

Consider two invented input records called `hour-09` and `hour-10`. Suppose we save estimates of 120 and 90 rentals respectively. These numbers are hand-written for teaching; no trained model has produced them.

Later, actual outcomes arrive in the opposite order:

| Arrival order | Record ID | Actual rentals |
|---|---|---:|
| First | `hour-10` | 95 |
| Second | `hour-09` | 150 |

If we paired the first arriving label with the first saved prediction, we would compare 95 with 120. Those values describe different hours. The program could still calculate a number, but that number would be the wrong record's error. An arithmetic result can look reasonable while its underlying match is wrong.

We will use the stable record ID to find the corresponding original prediction. This gives `hour-10`: 95 versus 90, error 5; and `hour-09`: 150 versus 120, error 30. Arrival order no longer changes which records are compared. The real system must also isolate each visitor's records inside a session, so two visitors can use the same visible ID without sharing history. We will implement and teach that boundary later.

## Separate what arrives now from what arrives later

The batch message contains input features and record metadata. The label message contains actual outcomes and the IDs they belong to. They travel separately because the service must work before outcomes are available.

Our draft input shape is saved in `examples/contracts/batch.json`. Here is one of its records:

```json
{
  "record_id": "hour-09",
  "event_time": "2012-01-01T09:00:00",
  "features": {"temp": 0.4, "hum": 0.6}
}
```

`record_id` supplies identity. `event_time` says which hour the record describes; the time our server receives it is a separate fact. `features` contains the values the model will use. The sample uses two provisional names from the plan and invented values; it is deliberately incomplete. Day 2's archive audit will determine the real complete feature list and how its values/timestamps must be interpreted. The timestamp above makes no claim to be UTC.

The later outcome message can be much smaller:

```json
{"record_id": "hour-09", "cnt": 150}
```

Here `cnt` means the actual rental count. It belongs to the outcome message. In our replay, labels will be deliberately withheld for two batch steps so we can test this behavior. That is a simulation rule, not a real operator integration.

## Run the small piece we built

`examples/contracts/trace_identity.py` reads the two JSON examples and demonstrates matching by ID. Run it from the project root:

```bash
./.venv/Scripts/python.exe examples/contracts/trace_identity.py
```

The important lines are:

```python
saved_predictions = {"hour-09": 120, "hour-10": 90}

for label in labels["labels"]:
    record_id = label["record_id"]
    prediction = saved_predictions[record_id]
    absolute_error = abs(label["cnt"] - prediction)
```

The dictionary associates each ID with its hand-written estimate. The loop reads each arriving label. `label["record_id"]` retrieves its ID, and `saved_predictions[record_id]` retrieves the estimate associated with that same ID. Python's `abs` returns the nonnegative size of the difference. The full script collects these values into a printable result; it never trains or calls a model.

The script also reads JSON from files: `Path(__file__)` starts with the script's own path, so its sibling example files can be found reliably; `read_text` reads their text, and `json.loads` converts that text into Python dictionaries/lists. `main()` groups the steps. The final `if __name__ == "__main__"` block runs them when this file is executed directly.

The assistant executed the script and saved its output under `reports/day01/contract-draft-2026-11-18/identity-trace.json`. It reports errors 5 and 30 for the correctly matched invented records. These are teaching arithmetic, not predictive-baseline results or incident metrics. Learner execution has not been observed.

This demonstration uses an in-memory dictionary. Persistent storage, duplicate/conflicting labels, unknown IDs, timestamps, coverage, and delayed availability need later lessons and tests. It does not complete the eventual independent duplicate-label exercise.

The fuller draft is in `docs/batch-label-contract.md`, including the intended architecture and the decisions still open. The HTTP API continues to expose only the health operation; these examples are a contract sketch, not working prediction endpoints.

## One small check

The saved estimates are `hour-09 → 120` and `hour-10 → 90`. A label arrives containing `{"record_id":"hour-10","cnt":100}`. Which saved estimate should we compare with 100, and what tells the program to choose it?

Learner answer on 18 November: "90 will be compared with 100(the actual value against the predicted value). We compare them by comparing the record_id or the predicted value and the real value."

Assessment: choosing 90 is correct. The proposed alternative of matching by predicted/actual values is incorrect. Match identity using record_id, then compare the values to measure error. Explained again with a counterexample; the retest is in Lesson 3, so the identity explanation is not yet marked independently passed. The later duplicate-label checkpoint remains unattempted.
