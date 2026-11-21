# Source acquisition and open audit questions

21 November 2026, Asia/Calcutta. Day 2 Lesson 1, assistant implemented; learner's grain-of-observation check is unassessed.

## Actual source evidence

- Used the download link on the current UCI dataset page. First command retrieved the archive; a second command verified the unchanged cache without another download. Original ZIP: 279,992 bytes, SHA-256 `b70182d0d0508e9abbb79306ce5c0cec34869000f8220175ac83d11dbe845401`.
- Archive inspection found `Readme.txt`, `hour.csv`, and `day.csv`. Original member bytes and header names are recorded in `source.json`. The header has 17 fields in the hourly file, 16 in the daily file. Full raw CSV data is ignored by Git.
- `fetch-first.json` and `fetch-cached.json` retain actual command output. Raw files are unchanged. The fetcher's own source hash is recorded for the acquisition revision.
- Inspected the complete bundled README and CSV headers. Hashing/readback touches raw bytes, but no CSV data rows or outcome statistics were parsed, printed, summarized, or used. No roles have been assigned yet. Final outcomes remain uninspected.
- Source citation/license: UCI lists CC BY 4.0; original README requests the paper citation. Both are retained in `DATA_SOURCE_NOTICE.md`.
- Nine local tests passed: six existing tests and three source-integrity/cache/layout tests using invented archives. Linux CI verification is pending at initial publication. No new runtime dependency, API route, or hosted deployment was added.

## Documentation disagreements to resolve or bound

These are attributed source claims, **not measured CSV results**:

| Topic | Current UCI page | Bundled README | Current treatment |
|---|---|---|---|
| Record count | Lists 17,389 instances | Claims 17,379 hourly records | Do not adopt either as our measured count. Count the actual CSV in Lesson 2. |
| Season code 1 | Calls it winter | Calls it "springer"; other labels also differ | No descriptive season mapping frozen. Audit category/date metadata before choosing a documented treatment. |
| Temperature normalization | Describes a min/max transform with -8 and +39 for hourly data | Describes division by 41 | No inverse Celsius conversion or physical-unit claim. Retain provided normalized numbers until the assumption is resolved or explicitly bounded. |
| Feeling-temperature normalization | Describes -16 and +50 endpoints | Describes division by 50 | Same unresolved conversion question. |

Do not resolve these disagreements using final outcomes or detector results. Metadata/schema inspection is allowed; target-value inspection is not part of this source step. Exact row counts, gaps, duplicates, category frequencies, time handling, allowlist/schema, and split boundaries remain pending.

Sources: [UCI page](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset), [exact archive URL](https://archive.ics.uci.edu/static/public/275/bike%2Bsharing%2Bdataset.zip), bundled README fingerprint in `source.json`, and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
