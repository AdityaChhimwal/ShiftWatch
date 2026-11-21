# Day 1: guided introduction to ShiftWatch

Updated 2026-11-12 (Asia/Calcutta). Lesson prepared; learner understanding has not yet been checked.

The earlier independent design assignment was premature for the learner's first actual project. It is withdrawn, not failed. Its original text is preserved in `reports/day01/kickoff-snapshot/docs/day01-problem-design.md`.

## How we will learn

The assistant mentors, teaches, and takes the initial design/implementation heavy lifting. Explain a concept, demonstrate a worked example, recommend a choice with its reasons, implement a small piece together, then check one thing just taught. Move gradually toward independent design, coding, and debugging. Book reading supplements the lesson; it is not a prerequisite for receiving explanations.

Teach the problem, architecture, folder structure, commands, implementation, testing, evaluation, and deployment as they become relevant. Do not present the whole stack at once or expect unfamiliar design decisions from the learner. Independent checkpoints remain learning outcomes after practice.

## The problem in ordinary terms

We will build a model that estimates hourly bike-rental counts from calendar information and weather observed for those hours. These inputs are called features. The actual count we later compare against the estimate is called a label or target. Using observed weather makes this a retrospective estimate; it does not establish an advance forecast using future weather.

The model produces estimates. ShiftWatch helps an engineer maintaining that model investigate whether incoming records are valid, whether their patterns differ from an earlier comparison sample, and how inaccurate the estimates are once actual counts arrive.

A batch is a group of records processed together. A reference is an earlier comparison sample that we keep fixed for the planned monitoring workflow. A distribution describes the pattern of values across many records, such as whether recent batches contain many more warm hours.

## Worked example (invented teaching numbers, not dataset results)

Suppose the model estimates 120 rentals for one hour. If the actual count later arrives as 150, its absolute error for that record is 30 rentals: `|150 - 120| = 30`. Before the actual count arrives, that error is unknown. We save the original estimate so that later evaluation measures the prediction actually made.

Across a batch, three different observations answer three different questions:

| Panel | Question | Example and interpretation |
|---|---|---|
| Data quality | Do records satisfy the declared input rules? | A required numeric field contains text: an input-rule violation, regardless of how the model would perform. Passing checks means only that the declared rules passed. |
| Distribution change | Do current value patterns differ from the fixed reference? | Current inputs contain more warm hours. That warrants investigation, but a model that handles warm hours well need not become less accurate. |
| Observed performance | How large are errors where actual outcomes are available? | Once actual counts arrive, compare them with saved estimates. With none available, show unknown performance. Partial labels need coverage and caveats. |

We separate these panels because valid inputs, familiar input patterns, and accurate predictions are different properties. Combining them into one unexplained green/red light could hide what is actually known.

In our replay, we deliberately delay labels by two batch steps to test the system's behavior. This is a simulation rule, not a claim about how an actual bike operator supplies outcomes. Detailed delay handling will be taught later.

## One small comprehension check

A new batch passes the input checks and looks similar to the reference. None of its actual rental counts have arrived. Can ShiftWatch mark its model performance as good? Explain in one or two sentences.

This checks only the distinction just taught. If it is unclear, work through another example together before moving on. Learner answer and feedback: pending.

## Confirmed working arrangements

- Interview deadline: explicitly removed by the learner on 2026-11-12; do not request it again.
- Available focused hours per day: six confirmed, including reading, review, implementation, and verification.
- Learner terminal: Git Bash confirmed.
- Measured learner time spent: unknown.

The fourteen days are milestone labels rather than a fixed deadline. The learner's priority is end-to-end completion and deep understanding. Teach and guide practice before requiring independent explanations, traces, changes, and debugging.

## Reading inside today's budget

Allocate at most 45 minutes to Designing Machine Learning Systems, Chapter 2, focusing on objectives, system requirements, and problem framing. The publisher contents were checked on 2026-11-12: <https://www.oreilly.com/library/view/designing-machine-learning-systems/9781098107956/>.

After the guided introduction, we will discuss how the predictor's count estimate differs from the engineer's investigation task. Reading is supplementary, not a replacement for mentoring; completion is unverified.

## What must be true by the end of Day 1

- Actual daily capacity and schedule priorities are recorded (six hours/day; no interview deadline), with verification and reproduction time protected. This scheduling clarification is complete.
- The learner explains the problem, alert-enabled investigation, three statuses, and information available before labels; explains why feature drift alone cannot establish deterioration.
- A reviewed problem statement, draft batch/label contracts, and architecture sketch exist. Data assumptions requiring the Day 2 archive audit remain explicit.
- A project environment and Git repository exist, compatible dependencies are pinned from a verified environment, and the health-only FastAPI service responds at a hosted URL. A local response alone does not satisfy the hosted deliverable.
- Hosting eligibility/access, temporary storage, limits, and billing choices are checked before an authorized deployment; unresolved access is a recorded blocker.
- Day 11 tester availability/invitation is addressed by the learner, with Day 12 as fallback; if unavailable, the external-validation gap is recorded. No messages are sent on the learner's behalf without explicit instruction.
- The files/checks and learning checkpoint are reviewed against the plan and `PROJECT_STATE.md` is updated. Creating these documents does not complete Day 1.
