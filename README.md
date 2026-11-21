# ShiftWatch

Batch ML monitoring and reliability evaluation, built alongside guided lessons.

Current stage: **Day 1, partial**. A local health-only FastAPI service works. Data audit, model, monitoring, storage, replay evaluation, and public hosting are pending. The project is assistant-led with learner understanding checked progressively.

Read [the first service lesson](docs/lessons/01-first-service.md) for the purpose, code walkthrough, and setup explanation. Current evidence and exactly one next task are in [PROJECT_STATE.md](PROJECT_STATE.md). The detailed scope/evaluation contract is [ShiftWatch-14-Day-Plan.md](ShiftWatch-14-Day-Plan.md).

Continue with [Lesson 2: records and labels](docs/lessons/02-records-and-labels.md) and the [draft batch/label contract](docs/batch-label-contract.md). The runnable examples contain invented teaching values and an incomplete feature set; they are not model-ready API uploads or evaluation results.

Day 1 has a [six-lesson teaching roadmap](docs/day01-roadmap.md). [Lesson 3](docs/lessons/03-input-rules.md) adds a draft label-shape validator with four passing assistant-authored tests. The validator is not yet connected to an HTTP route or label storage.

[Lesson 4](docs/lessons/04-system-flow.md) reviews the intended architecture and separate monitoring statuses. Its JSON report example is explicitly synthetic, not a working monitor response.

[Lesson 5A](docs/lessons/05-version-history.md) traces working files, staging, local commits, and pushing to the existing GitHub repository. The published baseline is `b801aa1`; Docker packaging and clean-environment reproduction remain pending.

[Lesson 5B](docs/lessons/05b-packaging-the-service.md) adds a pinned Docker recipe and automated container checks. The local Docker engine is unavailable; the first clean Linux CI result is pending. See [Actions](https://github.com/AdityaChhimwal/ShiftWatch/actions) for actual run status. Neither a Dockerfile nor a passing CI run is a public deployment.

## Run the current local service

From Git Bash opened in this project folder, using the environment already installed here:

```bash
./.venv/Scripts/python.exe -m uvicorn shiftwatch.api:app --app-dir src --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/health>. Expected response: `{"status":"ok"}`. Press Ctrl+C in the terminal to stop the server. The Python/Uvicorn invocation was verified via local HTTP; a learner Git Bash/browser run is not yet recorded. This address is local only.

Verified locally with Python 3.13.3. Exact installed library versions are saved in `requirements.txt`; dependency consistency passed. Full clean-environment installation/reproduction is pending. The canonical GitHub repository is [AdityaChhimwal/ShiftWatch](https://github.com/AdityaChhimwal/ShiftWatch). Changes are committed and pushed in meaningful lesson-sized steps with relevant checks; the initial publication captures the existing foundation.

## Schedule

Latest user instruction: 12–14 days, six focused hours/day including teaching. Working calendar: Day 1 is 18 November 2026, release target 29 November, outer deadline 1 December, Asia/Calcutta. Protect the final two days for defects, reproduction, and understanding checks. Calendar targets do not establish acceptance or mastery.
