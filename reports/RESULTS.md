# Model card and evaluation

## Model and intended use

ShiftWatch demonstrates monitoring for retrospective estimates of hourly Capital Bikeshare rentals. The model uses the same hour's observed weather and calendar fields. Use this workload to compare validation, distribution, and delayed error signals. Deployment uses a static reference and a frozen model. Its evidence covers one historical hourly source and a simulated incident workload.

The inputs are hour, weekday, working-day flag, month, normalized temperature, humidity and wind speed, and weather category. Date/time and record ID are metadata. Rental outcome components are excluded. The candidate is a histogram gradient boosting regressor with native categorical splits, 100 iterations, at most 15 leaves per tree, learning rate 0.1, L2 regularization 0.1, and early stopping disabled. The comparator always predicts the training median. Both train on the first 6,897 observations. Observed rows retain their original hourly grain and missing calendar slots stay absent. [Source audit](source-audit.json) · [Split manifest](../configs/splits.json) · [Artifact manifest](../src/shiftwatch/artifacts/manifest.json)

## Regression error

MAE averages the absolute differences between predictions and actual counts. RMSE takes the square root of the mean squared difference. Each comparison uses identical hours for both models.

| Period | Rows | Median MAE | Candidate MAE | Median RMSE | Candidate RMSE |
|---|---:|---:|---:|---:|---:|
| Validation | 1,748 | 94.61 | 32.95 | 122.19 | 52.20 |
| Locked final | 3,488 | 188.63 | 95.99 | 260.41 | 132.62 |

The candidate beat the median baseline in both periods, and its MAE was almost three times as high in the later one. The final period is August 7 through December 31, 2012. [Validation predictions](development/predictions.csv) · [Final predictions](final/predictions.csv) · [Frozen revision and hashes](freeze.json)

## Controlled policy comparison

Each scenario and strength uses 20 paired seeds. Development seeds are 100–119 and final seeds are 200–219. Each run draws a 14-day reference and seven whole days per batch with replacement from its assigned period. The run uses eight pre-event, eight event, and eight post-event batches, then two label-flush steps. Covariate stress gives days in the warmest quartile three or nine times the normal sampling weight during the event. Quality stress sets humidity to −1 for a sample of 15% of event rows. Target stress uses rounded `1.25 × y + 20` or `1.5 × y + 40` with the same inputs and predictions as its paired stable run.

| Development policy | No-injection distribution alerts | Covariate events detected | Median delay among detections |
|---|---:|---:|---:|
| P0 | 476 / 480 (99.17%) | 40 / 40 | 0 batches |
| P1, effect ≥ 0.1 | 432 / 480 (90.00%) | 40 / 40 | 0 batches |
| P1, effect ≥ 0.2 | 230 / 480 (47.92%) | 40 / 40 | 0 batches |

Neither P1 variant met the 5% no-injection gate, so P0 stayed as the measured comparator. Its high event recall is accompanied by alerts on nearly every stable batch. Treat these distribution alerts as diagnostics. Tests operate across correlated features and temporally dependent observations. The replay respects within-day order and changes dependence between days. [Development summary](development/summary.json) · [Seed-level alert burden](development/replay_metrics.csv) · [Development events](development/event_metrics.csv)

The frozen final run scored 120 replays using P0. Distribution alerted on **479 of 480** eligible no-injection batches. The quality channel alerted on **0 of 480** and performance on **7 of 480**. Relevant alerts occurred within the event window for all 40 covariate events, all 20 quality events and all 40 target events. Median detection delay from onset was zero batches for the first two channels and two batches for target events. The target delay reflects simulated label availability. The performance threshold of 115.317 MAE came from the 95th percentile of 480 fully labeled no-injection development batches. [Final summary](final/summary.json) · [Per-event windows, detections, delays and misses](final/event_metrics.csv) · [Paired observed and original errors](final/performance_metrics.csv.gz)

## Natural replay

The final chronological period produces 21 groups of seven observed dates each, scored against the historical reference. P0 raised 21 distribution alerts in 21 eligible groups. All 21 groups eventually had sufficient label coverage and none crossed the frozen performance threshold. Incident truth is unavailable for this run. [Chronological batch log](final/natural_replay.csv)

## Verification and operating limits

The application passed 22 unit tests, HTTP replay and custom upload lifecycle checks, and browser checks in Edge. A clean copy of the committed tree reproduced the source audit, split manifest, development metrics and artifact fingerprints using the pinned source cache. Local Windows timings use 30 accepted 500-row requests at concurrency one. Peak server-process working set and time from process launch to the first successful health response are recorded alongside the raw round-trip timings. Those measurements are local to the tested workload. [CI and browser verification](verification.json) · [Reproduction record](reproduction.json) · [Local measurements](runtime/local-windows/runtime.json) · [Raw local timings](runtime/local-windows/timings.csv)

External tester feedback and hosted measurements are pending. The existing Render service requires a separate release action. Free hosting may spin down and discard SQLite data. [Render Free limits](https://render.com/docs/free)
