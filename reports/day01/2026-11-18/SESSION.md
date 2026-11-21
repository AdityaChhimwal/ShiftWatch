# Day 1 session — 18 November 2026 (Asia/Calcutta)

## Learner evidence

Prompt: a batch passes input checks and resembles the reference, but actual counts are unavailable. Can its performance be marked good?

Learner answer: "We can't measure its prediction performance without labels."

Assessment: correct; the narrow missing-label check is passed. This does not establish the remaining Day 1 explanations or any implementation proficiency. Other independent checkpoints are unattempted, not failed. Learner hours spent: unknown.

## Latest instructions and schedule

The learner requested simpler, connected teaching like a book while building simultaneously, and said deadlines are strict. They clarified the deadline as "12-14 days to make the project live and understand it really really deep and intuitively."

The assistant explicitly counts today as Day 1: release target 29 November (Day 12), outer deadline 1 December (Day 14). This is the working interpretation of the relative duration, not a separately supplied calendar date. Six focused hours/day remains confirmed. Keep final verification/understanding time protected and raise overruns explicitly; do not silently extend. The earlier interview date remains out of scope.

## Implemented and observed

- Created `.venv` from Python 3.13.3; verified its pip reports the project-local installation.
- Installed FastAPI 0.163.2 and Uvicorn 0.54.0, with dependencies selected by pip. Saved actual resolved versions to `requirements.txt`; `pip check` returned "No broken requirements found."
- Initialized the local Git repository on `main`; no commit, remote, publication, or account changes.
- Added package marker and one `GET /health` handler in `src/shiftwatch/api.py`, plus `.gitignore`, README, and the first service lesson.
- Real HTTP check: GET health 200 with JSON, missing path 404, unsupported method 405, generated API description with only the health operation. Raw evidence: `health-smoke.json`; server log: `uvicorn.log`.
- The local server was terminated after the check. No service is claimed to remain running. No hosted health URL, Docker build, dataset audit, model, monitor, delayed-label store, or final evaluation exists.
- Dependencies are pinned for this slice; clean-environment reproduction and compatibility with the later ML stack remain to be verified.

## Debugging record

### Temporary installation files

- Symptom/reproduction: `python -m venv .venv` failed while bootstrapping pip; direct `ensurepip` reproduced a permission error writing a temporary wheel in the execution sandbox's temp folder.
- Hypothesis: the temp location, rather than the health application, was inaccessible.
- Smallest check/fix: set TEMP/TMP for that process to the project's `.tmp` folder and rerun environment creation.
- Result: project-local `pip --version` succeeded.

### Network restrictions

- Symptom: package downloads failed DNS resolution in sandbox execution; the first local HTTP smoke check could not connect.
- Smallest check: a local TCP listener/client experiment failed its connection with WinError 10013, independently of FastAPI.
- Fix: approved execution outside the network restrictions for package installation and the local-only smoke check. No application logic changed to hide the restriction.
- Result: installation and the actual HTTP checks succeeded. This is not a fix to the learner's terminal or operating system; their own run remains unobserved.

## Provenance and review

Five prior documents are preserved in `before/`, with original bytes recorded by `before.sha256`. Earlier kickoff and 13 November records are preserved. `after.sha256` records the updated documents, code, requirements, lesson, and raw HTTP outputs at this revision. This is file-hash provenance; there is not yet a code commit or model/evaluation run.

Day 1 remains **partial**: environment/local health/Git initialization are done; hosted response, draft contracts and architecture, hosting access/constraints, tester availability, and the remaining taught explanations are pending. Next learning task: trace the health request using the single check in Lesson 1.
