# ShiftWatch project state

Last updated: 2026-11-18 (Asia/Calcutta).
Current milestone: Day 1 — define the problem and remove access risk.
Status: **partial**. The missing-label comprehension check passed; a project environment, local Git repository, and verified local health endpoint now exist. Hosted service and other Day 1 deliverables remain pending.

## Verified facts and evidence

- Initial project inventory contained only `ShiftWatch-14-Day-Plan-shiftwatch` (57,158 bytes). `AGENTS.md`, `PROJECT_STATE.md`, and the canonical plan filename were absent. No parent `AGENTS.md` was found at `D:\` or `D:\good_projects`.
- Read the supplied fourteen-day plan. Renamed it to `ShiftWatch-14-Day-Plan.md`, corrected the stale seven-day filename in its proposed layout, and added the learner's subsequent schedule/learning-priority override. Technical scope and evaluation requirements are retained. The historical statement that it supersedes the seven-day plan is intentional.
- Original plan SHA-256 before this edit: `D024AFFCC4C36F70AE391CC255AE7404C06AF7DC0E97A8EB7C660D8DCA5BD19D`.
- Created the ShiftWatch-specific `AGENTS.md` and initially assigned an independent problem-design exercise. Following the learner's correction, replaced `docs/day01-problem-design.md` with a guided introduction and one small check after a worked example. The earlier assignment was premature; it was not a learner failure. These are documentation, not implemented or validated product behavior.
- Kickoff facts: Python 3.13.3, pip 25.0.1, and Git 2.47.1.windows.2 executed. No environment/dependency manifest or Git repository existed then. On 18 November, created `.venv`, saved actual resolved packages to `requirements.txt`, and initialized local branch `main`. No commit or remote exists.
- Docker CLI 29.7.2 exists, but its `desktop-linux` engine was unavailable (`dockerDesktopLinuxEngine` named pipe missing). Container execution is not verified.
- Git Bash executables exist, but Bash is absent from the tool shell PATH and explicit invocation failed with an MSYS access-denied error. This does not establish failure in the learner's own terminal.
- Tool commands/observations are saved in `reports/day01/tool-audit.md`. The original six kickoff documents and their verified original hashes are preserved in `reports/day01/kickoff-snapshot/`. `reports/day01/kickoff-artifacts.sha256` and `reports/day01/mentoring-update-artifacts.sha256` describe their respective historical revisions; later document edits do not overwrite these manifests.
- On 2026-11-13, integrated the confirmed schedule/teaching updates throughout the plan, including daily learning outcomes, test instruction, reading, verification, and handoff. Removed stale interview scheduling and unaided-design prerequisites. Added the missing `ShiftWatch-Project-Chat-Prompt.md` with continuation instructions. This changed documentation only; no lesson was answered, runtime setup completed, or product result generated. The preceding plan/state/agreement are preserved under `reports/plan-revision-2026-11-13/before/`; the revision record and artifact hashes are in that report directory.
- Verified DMLS Chapter 2 reading topics against the publisher contents and inspected current Render free-service documentation. Sources and access limitations: `reports/day01/source-checks.md`.
- On 18 November, the learner answered "We can't measure its prediction performance without labels." Correct; that narrow check is passed. Broader model-monitoring understanding is not inferred from it.
- Implemented `src/shiftwatch/api.py`: GET `/health` returns `{"status":"ok"}`. Installed FastAPI 0.163.2/Uvicorn 0.54.0 and their dependencies; `pip check` passed. Exact resolved versions are in `requirements.txt`. Clean-environment reproduction and later ML-dependency compatibility remain unverified.
- A real local HTTP check observed health 200/JSON, missing route 404, unsupported method 405, and an API description with only `/health`. Saved raw responses in `reports/day01/2026-11-18/health-smoke.json` and server log in that directory. The temporary server was stopped after verification. This checks liveness only.
- Added `docs/lessons/01-first-service.md` with connected explanation, code/command trace, and one comprehension check. It is prepared teaching material; that new answer and the learner's own terminal/browser run have not been assessed.
- No dataset downloaded/audited, model trained, policies implemented/tuned, final evaluation inspected, frontend implemented, or service publicly deployed. No model/evaluator tests or results exist yet.
- Latest revision evidence, setup failure/fix notes, and exact instruction changes are in `reports/day01/2026-11-18/SESSION.md`. The five preceding documents and hashes are preserved in `before/`/`before.sha256`; current artifact hashes are in `after.sha256`. Earlier historical evidence is retained.
- After the learner requested "Next", prepared Lesson 2 (`docs/lessons/02-records-and-labels.md`), the assistant-proposed `docs/batch-label-contract.md`, and synthetic batch/label examples with a runnable identity trace under `examples/contracts/`. The draft includes a problem statement, field purposes, intended architecture, and open decisions. It is not a frozen schema or implemented batch/label API.
- Executed `examples/contracts/trace_identity.py`: input order hour-09/hour-10, label order hour-10/hour-09; ID lookup selected hand-written estimates 90/120 and produced illustrative absolute errors 5/30. Verified both matches against the hand-worked example; saved raw output in `reports/day01/contract-draft-2026-11-18/identity-trace.json`. These are invented teaching values, not model metrics. No new dependencies or service routes were added.
- The previous state and its hash are preserved in `reports/day01/contract-draft-2026-11-18/before-state.md` and `before-state.sha256`; `after.sha256` records this draft/lesson/code/output revision. Earlier evidence manifests remain historical.

## Decisions and existing constraints

- Use only `D:\good_projects\shiftwatch`; CatalogLink/VisionGuard are outside this task.
- The fourteen-day plan remains the scope/evaluation contract. Latest user update, 18 November: deadlines are strict; 12–14 days for a live project and deep intuitive understanding, six focused hours/day. Working interpretation counts 18 November as Day 1, targets release 29 November (Day 12), and sets the outer deadline 1 December (Day 14), Asia/Calcutta. This calendar is explicitly stated by the assistant from the relative duration; do not silently extend it. Preserve frontend/backend/final-freeze order and final defect/reproduction work. Raise forecast overruns and apply allowed optional cuts; no false acceptance or mastery claims. The removed interview date remains out of scope.
- Latest learner clarification: this is their first actual project; the assistant is the project mentor/teacher and must carry initial design/implementation heavy lifting while teaching every project layer. The earlier expectation of learner-led design before teaching has been superseded in the agreement and plan.
- Teach with explanation and worked examples, then guided practice, then independent practice. The latest style request is simple, connected prose like a book with simultaneous construction: explain the problem and reason for the design, work an example, implement a small piece, and trace it before one small taught check. The assistant leads initial core designs. Only the missing-label distinction has demonstrated understanding so far.
- Opening lesson/check: the missing-label question is passed; do not repeat it. The earlier multi-part independent design exercise remains withdrawn. The learner asked to continue after Lesson 1, which is not evidence of passing its health explanation. Lesson 2 demonstrates stable IDs and separate label messages, with its one taught question pending. This is guided progression within Day 1, not advancement to a completed milestone.
- Proposed identity design: record IDs are stable and unique within a session; attach labels to original saved predictions by session/record ID instead of row position. The teaching trace demonstrates reordered matches only. Production storage, duplicate/conflict/retry rules, availability enforcement, and session isolation are still pending.
- Keep the plan's audited workload, leakage exclusions, chronological roles, dummy/candidate comparison, separate channels/replays, P0/P1 evaluation, delayed-label guarantees, and final freeze.
- Render remains the plan's first hosting candidate; no host/account/billing choice has been made. Hosting changes, publication, and tester messages need appropriate authorization when concrete.

## Unresolved assumptions, defects, and learning gaps

- Interview date/time is intentionally out of scope following the learner's clarification; do not ask again. Six hours/day is confirmed availability, not measured effort or a guarantee of completion in fourteen days.
- Git Bash is confirmed as the learner terminal. Measured learner hours are unknown; assistant runtime is not learner effort.
- Environment, pinned web-service dependencies, local Git initialization, and local health response are verified. Draft contracts, a problem statement, and an architecture sketch now exist but have not been reviewed by the learner. Hosted health URL and remaining Day 1 learning outcomes are outstanding. No initial Git commit or clean-machine reproduction yet.
- The example features/timestamps are synthetic and incomplete. Day 2 must establish the actual allowlist, units/ranges/categories, time-zone treatment, and CSV mapping. Whole-batch versus partial-row rejection and the final response schema remain guided design decisions before later implementation.
- Docker engine access and Bash execution in this sandbox are setup limitations, not diagnosed application defects.
- Render account access/eligibility, available quota, effective resources, payment/spend settings, and deployment authorization are unverified. Public docs do not establish these account facts.
- Day 11 tester availability and invitation have not been established. No external validation exists.
- Dataset archive/schema/terms audit and exact boundaries remain Day 2 work. No source counts, feature allowlist, split boundaries, or results have been invented.
- This is the learner's first actual project. Missing-label performance distinction is passed; other problem/status meanings and Python/SQL/statistics implementation proficiency remain unassessed. PSI calculation, event recall/delay, duplicate-label join, and independent core-test repair are unattempted and require teaching/guided practice. No failed understanding check has been observed.
- Tool sandbox restricted temporary installation files, network package resolution, and loopback connections. Using a project-local temp directory and approved execution for installs/local HTTP checks resolved this session's setup obstacles. See SESSION.md. These are execution-environment observations, not learner-terminal defects.
- The previously missing `ShiftWatch-Project-Chat-Prompt.md` was created on 2026-11-13 from the confirmed working agreement and user clarifications. Its dated Day 1 snapshot is not evidence of progress beyond the state recorded here.

## Review against Day 1 pass criteria

- File/tool discovery: checked; limitations recorded.
- Problem-design learning: missing-label check passed; remaining explanations unassessed. Service lesson/check prepared.
- Environment and Git setup: project-local Python/pip and web dependencies verified; Git initialized, no commit/remote.
- Draft contracts/problem statement/architecture: assistant-proposed draft saved; learner review pending. Reordered-ID teaching example executed and checked, not a production join implementation.
- Hosted health response: not done.
- Local health response: verified; hosted response still pending.
- Schedule/terminal clarification: strict 12–14 days, working calendar 18 November–1 December with release target 29 November; six hours/day, Git Bash, no interview date needed. Measured learner hours unknown.
- Hosting access uncertainty resolved: not done.
- Milestone conclusion: **partial**, with no claim of Day 1 completion.

## Next task

Work through Lesson 2 and answer its single question about choosing the saved prediction by record ID in `docs/lessons/02-records-and-labels.md`.
