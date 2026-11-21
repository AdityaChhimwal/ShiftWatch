# Day 2, Lesson 1: what one row means, and where it came from

Yesterday we made a small service reachable. Today we begin defining the data behind the future model. An algorithm cannot rescue an unclear prediction question, so we first identify what one row represents and preserve the exact source we are using.

## Start with the prediction question

The UCI Bike Sharing archive contains hourly and daily aggregates of Capital Bikeshare rental counts with calendar/weather information. The bundled README identifies `hour.csv` as hourly and `day.csv` as daily. We selected `hour.csv` because our project's prediction is an estimate of the total rental count for one observed hour.

This row is already a summary. It is not one customer's trip. The term **grain** means the unit represented by one row: here, one source date and hour. Choosing the grain chooses what a single prediction means.

Consider these invented teaching values, not observations from either source file:

| Example file | What the row represents | Hypothetical `cnt` | What the count means |
|---|---|---:|---|
| `hour.csv` | One date/hour, such as hour code 8 | 120 | Total rentals in that hourly bucket |
| `day.csv` | One complete date | 960 | Total rentals across that day |

Both counts use the same column name, but they answer different questions. Mixing these rows into our hourly task would make the meaning of the target inconsistent. Before debating model algorithms, we must decide what one model output is supposed to estimate.

The `hr` field is an hour code, not a complete timezone-aware timestamp. We have not yet established timezone/DST/gap handling. Our planned use of observed weather also remains a retrospective estimate for the hour, rather than an advance forecast using weather known beforehand. We will examine availability and leakage more deeply in Lesson 3.

## Preserve evidence before changing data

Suppose a result changes next week. Was it a code change, different input bytes, or a new split? We need a way to separate these possibilities. **Provenance** is the record of where an input came from and which version we used.

Our source record stores the UCI page, direct archive URL, actual retrieval time, dataset citation/license reference, original archive size/hash, and the sizes/hashes/headers of its files. We retain the original ZIP and extracted file bytes under ignored `data/raw/bike-sharing/`. A public metadata record lives under `reports/day02/source-2026-11-21/`; the dataset's CSV values are not committed.

The actual downloaded archive is 279,992 bytes and contains the three expected files. The recorded hourly header has 17 fields and the daily header has 16. These are measurements from our archive inspection, not web-page instance counts. No CSV data rows have been parsed yet; row counts, missingness, duplicates, categories, and date boundaries remain Lesson 2 work.

The ZIP's SHA-256 begins `b70182d0d050` (abbreviated here; the record contains the full identifier). A hash is a deterministic fingerprint of bytes. It helps detect a changed file. It does not establish that a file is correct, complete, unbiased, or suitable for a particular prediction task. Those require the subsequent audit.

UCI currently lists CC BY 4.0. The bundled README also requests citation of the associated paper. `DATA_SOURCE_NOTICE.md` retains both the dataset attribution/license link and that paper reference. Source values are unchanged at acquisition.

## The small implementation

The new offline utility is `scripts/fetch_bike_source.py`. It uses Python's standard library: there is no new serving dependency, and the public API is unchanged.

- `urlopen` retrieves the fixed official archive URL with a timeout and bounded download size.
- `inspect_archive` checks the expected file layout, reads byte fingerprints, and parses only the first CSV row: the column names. It never parses a CSV data row. Raw member bytes are read for identity checks, which does not calculate or reveal their target values.
- `fetch_source` writes the original bytes and source record on the first run. Only the three fixed file names are written, rather than blindly extracting arbitrary archive paths.
- `verify_cache` compares existing raw-file hashes against the recorded snapshot on later runs. A changed file raises an error instead of quietly replacing our evidence.

The verified invocation, written for your Git Bash terminal in the repository root, is:

```bash
./.venv/Scripts/python.exe scripts/fetch_bike_source.py \
  --raw-dir data/raw/bike-sharing \
  --report reports/day02/source-2026-11-21/source.json
```

The Python invocation and arguments ran through the host tools; a learner Git Bash run is not claimed. The first actual run reported `downloaded`. The second reported `verified_cached` with the same archive fingerprint. The source record preserves the original retrieval time.

Three invented-archive regression tests check cache reuse without another download, failure on modified raw bytes without rewriting the record, and rejection of an unexpected archive layout before snapshot creation. All nine current tests passed locally and in [Linux CI](https://github.com/AdityaChhimwal/ShiftWatch/actions/runs/44925455815). CI uses small invented fixtures and does not fetch or analyze the real dataset. Its actual log and metadata are saved with the source evidence.

## Why the source audit still matters

The current UCI page and bundled README disagree on some record-count, season-label, and normalization descriptions. These are documentation claims, not resolved ground truth. We recorded them in the source report notes. We have not converted normalized values to Celsius, assigned descriptive season labels, frozen the feature schema, or accepted a web-page row count as a measurement.

This is the reason for auditing: a familiar column name and a reputable source do not remove the need to verify the actual artifact and make assumptions visible. Seventeen CSV fields also do not mean seventeen valid model inputs. We will classify their roles before fitting any model.

## One reasoning check

If we mixed `hour.csv` and `day.csv` rows into one training table merely because both contain `cnt`, what would become inconsistent about the meaning of one prediction?

This check is unassessed. The acquisition implementation is verified separately from learner understanding; the full Day 2 audit and role freeze are not complete.

Sources: [UCI dataset page](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset), the exact bundled README recorded by hash, and [CC BY 4.0 conditions](https://creativecommons.org/licenses/by/4.0/).
