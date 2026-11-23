# Day 2, Lesson 2: a complete row can still belong to an incomplete sequence

We chose one source date and hour as the meaning of an observation. Suppose an invented hourly row has a count of 120: that means 120 rentals in that hour. An invented daily row with 960 means rentals across the whole day. Combining those meanings would give the model an inconsistent question. We use only `hour.csv`. The learner answered "Don't know" to the first grain question; this explanation is guided reinforcement, not evidence that the check passed.

Now we ask whether the hourly table is complete. That sounds like one question, but it hides two different questions: do existing rows have their cells filled, and are all the expected rows present?

## Two kinds of absence

Consider this invented metadata example. It contains no rental counts:

| Source date | Hour code | Humidity |
|---|---:|---:|
| 2011-01-01 | 8 | 0.50 |
| 2011-01-01 | 10 | 0.60 |

Every displayed cell is filled. Nevertheless, if we expected hours 8, 9, and 10, hour 9 has no row. An empty humidity cell in an existing row would be **cell missingness**. The absent hour is a **missing record** relative to our expected calendar. Looking only for empty cells cannot find a row that is absent altogether.

Absence also differs from an explicit zero. A row reporting zero rentals would assert an observed count. An absent row supplies no such count. Filling it with zero would invent an outcome unless we had evidence supporting that interpretation. We do not have that evidence.

Another possible repair is interpolation: estimating an absent value from nearby values. That introduces assumptions too, and an invented label could contaminate later evaluation. Our choice at this stage is to preserve original observations, report gaps, and make no repair. This protects reproducibility without claiming that the observed hours form a representative sample of all hours.

## What the actual file tells us

The audit verified the original byte hashes before analyzing `hour.csv`. These measurements belong to that pinned source version:

| Measurement | Observed result |
|---|---:|
| Data rows, excluding the header | 17,379 |
| Distinct source dates, 2011-01-01 through 2012-12-31 | 731 |
| Empty or whitespace-only cells across the 14 metadata columns | 0 |
| Extra occurrences of source IDs | 0 |
| Extra occurrences of date/hour pairs | 0 |
| Nominal date/hour slots: 731 × 24 | 17,544 |
| Absent nominal slots: 17,544 − 17,379 | 165 |

Every date occurs at least once, and rows are already in nondecreasing date/hour order. For example, source date 2011-01-02 has no hour-code-5 row. We did not display or examine any corresponding rental outcome.

The gap calculation uses a **nominal grid**: a simple checklist containing hour codes 0–23 for each source date. We have not established a timezone or daylight-saving policy. Therefore, 165 is a measured count of absent source-calendar combinations under that assumption, not proof of 165 lost physical hours or a diagnosis of why the rows are absent. No timezone conversion or gap correction was performed.

The actual row count agrees with the bundled README's 17,379 claim and differs from the UCI page's 17,389 claim recorded on 21 November. For this project we use our file measurement. This settles the count for our snapshot, not the other documentation disagreements about season names or temperature conversion.

The report also stores category frequencies as raw codes. For example, `weathersit` codes 1, 2, 3, and 4 occur 11,413, 4,544, 1,419, and 3 times. A rare code is not automatically an invalid code. We have not removed it or selected monitoring thresholds from these frequencies. Season codes retain anonymous numeric meanings until the conflicting descriptions are addressed. The four weather fields contain no nonblank values that fail numeric conversion or are nonfinite; full range/semantic validation belongs to the later schema lesson.

## Trace the implementation

`scripts/audit_bike_metadata.py` is an offline preparation tool. It does not add an API route, train a model, or change the hosted service. It uses Python's existing standard library.

1. `audit_source` loads the published source record and calls `verify_cache`. A changed raw file causes a checksum error; it is not silently replaced.
2. `audit_hourly` requires the exact hourly header, including `hr`. A daily file is rejected instead of being mixed in.
3. Each CSV row is split into fields, but only the 14 metadata cells are accessed. `casual`, `registered`, and `cnt` are never converted, compared, summarized, or displayed. This metadata-only inspection includes the future final period; its outcomes remain unexamined.
4. The code counts blank metadata cells, raw categories, and invalid/nonfinite weather values. It builds a key `(source_date, hour)` for each row. A key identifies the source-calendar bucket; an occurrence counter reveals duplicates without dropping anything. Duplicate counts mean occurrences beyond the first, rather than the number of affected groups.
5. It enumerates 24 nominal keys per date and checks which keys never occurred. Observed unique keys, rather than row count alone, are used, so a duplicate cannot disguise an absent hour.
6. It saves the report with source/script fingerprints. An identical rerun reuses the report; changed output refuses to overwrite it. Raw source bytes are never edited.

For our snapshot, unique nonblank source IDs also prove there cannot be identical full rows: identical rows would necessarily share an ID. We therefore report zero full-row duplicates without comparing outcome cells. If IDs were duplicated or blank, this proof would be unavailable and full-row duplication would remain unknown in this audit.

The command below uses Git Bash syntax from the repository root:

```bash
./.venv/Scripts/python.exe scripts/audit_bike_metadata.py \
  --report reports/day02/metadata-2026-11-23/audit.json
```

The Python invocation and arguments were executed through PowerShell; a learner Git Bash run is not claimed. `--report` names the JSON evidence file. The default input paths are the cached raw folder and the published source record from Lesson 1. The command prints a short summary while the JSON retains per-column counts, gap locations, category counts, assumptions, and hashes.

Five new tests use invented fixtures: daily-grain rejection, blank-cell versus missing-hour separation, duplicate/order visibility, protected-outcome access, and invalid-key/nonfinite-weather behavior. The outcome-access test wraps each invented row in a guard that raises immediately if an outcome index is accessed. All 14 project tests passed locally; the Linux CI outcome is recorded separately in the report notes when available. CI never downloads or analyzes the real source rows.

## One taught check

If every cell in the two-row example above is filled, can hour 9 still be missing, and does that absence tell us its rental count was zero?

This check is pending. The audit is implemented; the learner's understanding and the rest of Day 2 remain separate open work. This lesson is part of the existing six-lesson day, not an additional day or permission to begin model training.
