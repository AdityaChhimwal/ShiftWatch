# Day 1: problem-design checkpoint

Status: assigned, not attempted. Date: 2026-11-12 (Asia/Calcutta).

Purpose: define what an engineer can investigate from monitoring evidence available now. The first component is the problem/status contract; no monitoring code is being implemented before this explanation.

## First exercise (10–15 minutes, independently)

You maintain a model that estimates hourly bike-rental counts using calendar and contemporaneous weather inputs. At replay step 5, a batch of 240 records passes all declared schema, range, missingness, and ID checks. The distribution monitor flags a temperature shift against the reference. Predictions have been saved, but none of this batch's actual rental counts are available until step 7.

What should ShiftWatch tell the engineer at step 5, and what investigation should that enable?

Respond with:

1. One sentence naming the user, their problem, and the decision this tool supports.
2. The status and supporting evidence for each panel: data quality, distribution change, observed performance.
3. One concrete next investigation and one conclusion the evidence does not justify. Explain why.
4. One plausible situation where the temperature shift occurs but prediction error does not increase.

Do not calculate a drift statistic or assume an error measurement that is not available. Your explanation will be reviewed before drafting the application contracts. A short counterexample/trace will follow; merely copying terminology does not pass.

Learner answer: pending.
Review/correction: pending.
Follow-up trace: pending.
Checkpoint result: not passed; no attempt yet.

## Schedule facts to confirm

- Interview deadline: explicitly removed by the learner on 2026-11-12; do not request it again.
- Available focused hours per day: six confirmed, including reading, review, implementation, and verification.
- Learner terminal: Git Bash confirmed.
- Measured learner time spent: unknown.

The fourteen days are milestone labels rather than a fixed deadline. The learner's priority is end-to-end completion and deep understanding. Require explanations, traces, independent changes, and debugging; preserve honest authorship and technical evidence.

## Reading inside today's budget

Allocate at most 45 minutes to Designing Machine Learning Systems, Chapter 2, focusing on objectives, system requirements, and problem framing. The publisher contents were checked on 2026-11-12: <https://www.oreilly.com/library/view/designing-machine-learning-systems/9781098107956/>.

Tie the reading to this exercise: distinguish the predictor's numerical objective from the investigation the monitoring user needs to perform. Save three brief notes: a concept, its place in ShiftWatch, and a failure it can prevent. Reading completion is unverified.

## What must be true by the end of Day 1

- Actual daily capacity and schedule priorities are recorded (six hours/day; no interview deadline), with verification and reproduction time protected. This scheduling clarification is complete.
- The learner explains the problem, alert-enabled investigation, three statuses, and information available before labels; explains why feature drift alone cannot establish deterioration.
- A reviewed problem statement, draft batch/label contracts, and architecture sketch exist. Data assumptions requiring the Day 2 archive audit remain explicit.
- A project environment and Git repository exist, compatible dependencies are pinned from a verified environment, and the health-only FastAPI service responds at a hosted URL. A local response alone does not satisfy the hosted deliverable.
- Hosting eligibility/access, temporary storage, limits, and billing choices are checked before an authorized deployment; unresolved access is a recorded blocker.
- Day 11 tester availability/invitation is addressed by the learner, with Day 12 as fallback; if unavailable, the external-validation gap is recorded. No messages are sent on the learner's behalf without explicit instruction.
- The files/checks and learning checkpoint are reviewed against the plan and `PROJECT_STATE.md` is updated. Creating these documents does not complete Day 1.
