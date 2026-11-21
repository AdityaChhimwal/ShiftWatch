# ShiftWatch project state

Last updated: 2026-11-12 (Asia/Calcutta).
Current milestone: Day 1 — define the problem and remove access risk.
Status: **partial**. Initial discovery and teaching setup only; no learner checkpoint passed.

## Verified facts and evidence

- Initial project inventory contained only `ShiftWatch-14-Day-Plan-shiftwatch` (57,158 bytes). `AGENTS.md`, `PROJECT_STATE.md`, and the canonical plan filename were absent. No parent `AGENTS.md` was found at `D:\` or `D:\good_projects`.
- Read the supplied fourteen-day plan. Renamed it to `ShiftWatch-14-Day-Plan.md`, corrected the stale seven-day filename in its proposed layout, and added the learner's subsequent schedule/learning-priority override. Technical scope and evaluation requirements are retained. The historical statement that it supersedes the seven-day plan is intentional.
- Original plan SHA-256 before this edit: `D024AFFCC4C36F70AE391CC255AE7404C06AF7DC0E97A8EB7C660D8DCA5BD19D`.
- Created the ShiftWatch-specific `AGENTS.md` and assigned `docs/day01-problem-design.md`. These are documentation, not implemented or validated product behavior.
- Python 3.13.3 and pip 25.0.1 execute; Git 2.47.1.windows.2 executes. No project environment/dependency manifest or Git repository existed at initial inspection; none has been created in this kickoff.
- Docker CLI 29.7.2 exists, but its `desktop-linux` engine was unavailable (`dockerDesktopLinuxEngine` named pipe missing). Container execution is not verified.
- Git Bash executables exist, but Bash is absent from the tool shell PATH and explicit invocation failed with an MSYS access-denied error. This does not establish failure in the learner's own terminal.
- Tool commands/observations are saved in `reports/day01/tool-audit.md`. Kickoff document hashes are saved in `reports/day01/kickoff-artifacts.sha256`.
- Verified DMLS Chapter 2 reading topics against the publisher contents and inspected current Render free-service documentation. Sources and access limitations: `reports/day01/source-checks.md`.
- No dataset downloaded/audited, model trained, policies implemented/tuned, final evaluation inspected, frontend implemented, or service deployed. There are no application tests or result claims yet.

## Decisions and existing constraints

- Use only `D:\good_projects\shiftwatch`; CatalogLink/VisionGuard are outside this task.
- The fourteen-day plan is the scope/evaluation contract. In the 2026-11-12 clarification, the learner explicitly removed the interview deadline and confirmed six focused hours/day and Git Bash. End-to-end implementation and deep independent understanding take priority over schedule. Day labels now define milestone order; 72/84 hours remain original estimates, not promises. Preserve the frontend/backend/final-freeze order and defect/reproduction work; extend milestones as needed.
- Understanding must be demonstrated through design justification, code/state tracing, independent modifications, and debugging. Accurate assistant attribution remains required. No mastery is claimed from generating or reading code.
- Core implementation follows the learner's design explanation and a bounded review/checkpoint. First checkpoint concerns the problem and status meanings.
- Keep the plan's audited workload, leakage exclusions, chronological roles, dummy/candidate comparison, separate channels/replays, P0/P1 evaluation, delayed-label guarantees, and final freeze.
- Render remains the plan's first hosting candidate; no host/account/billing choice has been made. Hosting changes, publication, and tester messages need appropriate authorization when concrete.

## Unresolved assumptions, defects, and learning gaps

- Interview date/time is intentionally out of scope following the learner's clarification; do not ask again. Six hours/day is confirmed availability, not measured effort or a guarantee of completion in fourteen days.
- Git Bash is confirmed as the learner terminal. Measured learner hours are unknown; assistant runtime is not learner effort.
- Project environment, pinned compatible dependencies, Git setup, health route, hosted health URL, and reviewed batch/label contracts/architecture remain outstanding Day 1 deliverables.
- Docker engine access and Bash execution in this sandbox are setup limitations, not diagnosed application defects.
- Render account access/eligibility, available quota, effective resources, payment/spend settings, and deployment authorization are unverified. Public docs do not establish these account facts.
- Day 11 tester availability and invitation have not been established. No external validation exists.
- Dataset archive/schema/terms audit and exact boundaries remain Day 2 work. No source counts, feature allowlist, split boundaries, or results have been invented.
- Learner understanding of problem/status meanings is untested. Python/SQL/statistics implementation proficiency is unassessed. PSI calculation, event recall/delay, duplicate-label join, and independent core-test repair remain unattempted.
- `ShiftWatch-Project-Chat-Prompt.md`, referenced by the plan, is absent. The attached kickoff request supplies instructions for this chat; the missing file has not been fabricated.

## Review against Day 1 pass criteria

- File/tool discovery: checked; limitations recorded.
- Problem-design explanation: assigned, awaiting independent answer.
- Environment and Git setup: not done.
- Draft contracts and architecture review: not done.
- Hosted health response: not done.
- Schedule/terminal clarification: done; no interview deadline, six hours/day, Git Bash.
- Hosting access uncertainty resolved: not done.
- Milestone conclusion: **partial**, with no claim of Day 1 completion.

## Next task

Complete the first problem-design exercise in `docs/day01-problem-design.md` for review.
