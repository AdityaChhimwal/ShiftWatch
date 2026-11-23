# ShiftWatch

Batch ML monitoring and reliability evaluation, built alongside guided lessons.

Current stage: **Day 1 foundation complete; Day 2 metadata audit implemented, milestone partial**. A health-only FastAPI service is deployed on Render Free: [public health endpoint](https://shiftwatch-iejl.onrender.com/health). Real HTTPS checks observed health 200/JSON, unsupported method 405, and missing route 404. The original dataset is fingerprinted and its non-outcome metadata audited; role/schema freeze, model, monitoring, storage, replay evaluation, and frontend remain pending. The project is assistant-led with learner understanding checked progressively. [Day 1 close-out](docs/day01-closeout.md) preserves its completed boundary and open follow-ups.

Read [the first service lesson](docs/lessons/01-first-service.md) for the purpose, code walkthrough, and setup explanation. Current evidence and exactly one next task are in [PROJECT_STATE.md](PROJECT_STATE.md). The detailed scope/evaluation contract is [ShiftWatch-14-Day-Plan.md](ShiftWatch-14-Day-Plan.md).

Continue with [Lesson 2: records and labels](docs/lessons/02-records-and-labels.md) and the [draft batch/label contract](docs/batch-label-contract.md). The runnable examples contain invented teaching values and an incomplete feature set; they are not model-ready API uploads or evaluation results.

Day 1 has a [six-lesson teaching roadmap](docs/day01-roadmap.md). [Lesson 3](docs/lessons/03-input-rules.md) adds a draft label-shape validator with four passing assistant-authored tests. The validator is not yet connected to an HTTP route or label storage.

[Lesson 4](docs/lessons/04-system-flow.md) reviews the intended architecture and separate monitoring statuses. Its JSON report example is explicitly synthetic, not a working monitor response.

[Lesson 5A](docs/lessons/05-version-history.md) traces working files, staging, local commits, and pushing to the existing GitHub repository. The published baseline is `b801aa1`; its narrow learner check passed after correction and retest.

[Lesson 5B](docs/lessons/05b-packaging-the-service.md) adds a pinned Docker recipe and automated container checks. A [clean Linux CI run passed](https://github.com/AdityaChhimwal/ShiftWatch/actions/runs/44899459409): dependency consistency, six tests (four schema/two startup-checker), and real HTTP responses 200/405/404. Raw failed/passing logs, image identity, and hashes are retained in the [packaging report](reports/day01/packaging-2026-11-21/). The narrow learner build/run/port check passed after correction/retest. The local Windows Docker engine remains unavailable; container execution was verified on Linux CI and the host.

[Lesson 6](docs/lessons/06-public-health-service.md) traces the public deployment. After account review and launch approval, [render.yaml](render.yaml) created one free Docker web service with manual source deployments and `/health`. The [hosted verification report](reports/day01/hosted-2026-11-21/) records source `5ccc2a4`, actual deployment identity, HTTP observations, screenshot, and hashes. Render Free can sleep when idle; later local SQLite/session data will be temporary. The narrow guided hosting retest is now correct; deeper independent practice remains future work.

Day 2 has a [six-lesson roadmap](docs/day02-roadmap.md). [Lesson 1](docs/lessons/day02-01-source-and-observation.md) adds an offline source snapshot with original-byte hashes and cache verification. [Source evidence](reports/day02/source-2026-11-21/) contains metadata/headers and open documentation questions. [Lesson 2](docs/lessons/day02-02-missing-cells-and-hours.md) measures 17,379 hourly rows with zero blank metadata cells but 165 absent nominal hourly slots; [audit evidence](reports/day02/metadata-2026-11-23/) retains assumptions, category counts, and hashes without examining rental outcomes. See [dataset attribution](DATA_SOURCE_NOTICE.md). The feature/schema choice, chronological roles, learner checks, and Day 2 acceptance remain incomplete.

## Run the current local service

From Git Bash opened in this project folder, using the environment already installed here:

```bash
./.venv/Scripts/python.exe -m uvicorn shiftwatch.api:app --app-dir src --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/health>. Expected response: `{"status":"ok"}`. Press Ctrl+C in the terminal to stop the server. The Python/Uvicorn invocation was verified via local HTTP; a learner Git Bash/browser run is not yet recorded. This address is local only.

Verified locally with Python 3.13.3 and in a clean Linux amd64 Docker build with Python 3.13.18. Exact library versions are saved in `requirements.txt`; dependency consistency passed in both environments. This verifies the current small service, not later ML dependencies or all platforms. The canonical GitHub repository is [AdityaChhimwal/ShiftWatch](https://github.com/AdityaChhimwal/ShiftWatch). Changes are committed and pushed in meaningful lesson-sized steps with relevant checks.

## Schedule

Latest user instruction: 12–14 days, six focused hours/day including teaching. Working calendar: Day 1 is 18 November 2026, release target 29 November, outer deadline 1 December, Asia/Calcutta. Protect the final two days for defects, reproduction, and understanding checks. Calendar targets do not establish acceptance or mastery.
