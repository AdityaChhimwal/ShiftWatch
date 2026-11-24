# ShiftWatch

ShiftWatch monitors batches for an hourly bike-rental regression model. The dashboard shows row validation, distribution tests, and observed prediction error. Run a controlled incident replay or upload a CSV and attach the outcomes later.

[Open the live dashboard](https://shiftwatch-iejl.onrender.com/) · [Hosted verification and timings](reports/runtime/render-free/)

## Run locally

Use Python 3.13. In Git Bash on Windows, from the repository root:

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 ./.venv/Scripts/python.exe -m uvicorn shiftwatch.api:app --app-dir src --port 8000
```

Open [the dashboard](http://127.0.0.1:8000/). On Linux, replace `./.venv/Scripts/python.exe` with `./.venv/bin/python`. The image serves the same app:

```bash
docker build -t shiftwatch .
docker run --rm -p 127.0.0.1:8000:8000 shiftwatch
```

The bundled model and replay pool are ready at startup. Select a replay, advance two batches, and watch the first labels arrive on the third step. Finish the replay to reveal the injected incident. JSON export includes checks and predictions. CSV export includes one row per saved prediction and its joined outcome, where available.

## CSV uploads

Choose **Upload my own CSV** and download the templates from the dashboard. Batch rows contain `record_id,event_time,hr,weekday,workingday,mnth,temp,hum,windspeed,weathersit`. Use unique IDs per session and an hourly timestamp such as `2012-06-04T08:00:00` in the source calendar. Hour and month must match the timestamp. Weekday uses Sunday=0 through Saturday=6. Working day is 0 or 1. Weather situation uses source codes 1–4. The three continuous weather fields use the UCI normalized values in [0, 1]. Upload labels with `record_id,cnt`; `cnt` is the nonnegative integer hourly total.

Requests allow up to 500 rows and 256,000 JSON bytes. Use 1–64 printable ASCII characters without spaces for IDs. Each session allows 24 batches and expires after two hours. The service supports up to 12 active sessions and two in-flight session requests in one worker. Repeating an identical batch ID and payload or an identical label is safe. Conflicting data returns an error. Use the bearer token returned by `POST /sessions` for subsequent API calls. SQLite defaults to the OS temporary directory. Set `SHIFTWATCH_DB` to a writable file path to choose a local database. Render Free can spin down and discard session data. Export anything you want to keep. [Render Free limits](https://render.com/docs/free)

## Model and evaluation

The model estimates rentals for an observed hour using its measured weather. The median baseline and one histogram gradient boosting model use the same training period. [Exact split boundaries](configs/splits.json) reserve consecutive whole dates for training, validation, reference, policy development, and final evaluation. [Source record](reports/source.json) · [Source audit](reports/source-audit.json) · [Dataset attribution](DATA_SOURCE_NOTICE.md)

Validation MAE was **32.95** rentals per hour for the candidate and **94.61** for the median baseline over 1,748 rows. Neither tested persistence rule satisfied the policy selection gate. The dashboard uses P0 as a comparator. Its distribution alerts were frequent even on stable simulated inputs. [Validation metrics](reports/development/model_metrics.json) · [Development comparisons](reports/development/summary.json)

On the locked final period, candidate MAE was **95.99** against baseline **188.63** over 3,488 hours. P0 raised distribution alerts on **479 of 480** eligible no-injection final batches. [Model card, experiment results, and evidence](reports/RESULTS.md)

## Reproduce development

Use a separate checkout to preserve the published artifacts. The source hash check pins the original UCI archive contents.

```bash
export PYTHONPATH=src
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
./.venv/Scripts/python.exe scripts/fetch_bike_source.py --report data/source-local.json
./.venv/Scripts/python.exe scripts/audit_bike_metadata.py --source-record reports/source.json --report data/audit.json
./.venv/Scripts/python.exe scripts/train.py
./.venv/Scripts/python.exe scripts/evaluate.py develop
```

From Git Bash with Windows Python, set `PYTHONPATH='src;scripts'` for unit tests. Linux Python uses `src:scripts`.

```bash
PYTHONPATH='src;scripts' ./.venv/Scripts/python.exe -m unittest discover -s tests -v
./.venv/Scripts/python.exe scripts/smoke_app.py --url http://127.0.0.1:8000
```

The [final evaluation record](reports/freeze.json) pins the source revision, dependency and artifact hashes, and seed lists. To reproduce the final results, use a separate checkout at that exact revision, acquire the pinned source, copy `reports/freeze.json` into that checkout, and run `scripts/evaluate.py final` with the environment above. The command reserves a fresh output directory so an existing final run remains intact.
