# Day 2: six lessons, then a fixed close-out

Started on 21 November 2026, Asia/Calcutta, at the learner's request. This is learning milestone Day 2; it does not reset the calendar or deadlines.

The day's question is: **what exactly are our observations, and how can we use them without contaminating evaluation?** The assistant implements the audit/preparation code while teaching its assumptions, alternatives, worked examples, and traces. We deepen the reasoning within the existing scope rather than adding tools or models.

| Lesson | Concept and working result | Planned focused minutes | Actual stage |
|---|---|---:|---|
| 1 | Source provenance, original bytes, and what one observation means | 35 | Acquisition verified locally/in Linux CI. Learner answered "Don't know" to the grain check; re-taught with hourly versus daily examples. Guided reinforcement remains open. |
| 2 | Data quality: measure counts, missingness, duplicates, calendar gaps, and categories | 65 | Target-blind audit implemented on 23 November: 17,379 rows, zero blank metadata cells, 165 absent nominal hours, zero duplicate IDs/hour keys. Fourteen local tests passed; Linux CI and learner check tracked separately. |
| 3 | Leakage and feature availability: decide what may enter a prediction | 45 | Not started; no frozen feature allowlist yet. |
| 4 | Five chronological roles: why one train/test split is insufficient here | 70 | Not started; exact whole-date boundaries not assigned. |
| 5 | Turn audited assumptions into a data contract and reproducible preparation command | 50 | Not started; final schema/preparation artifacts pending. |
| 6 | Verify leakage/date-boundary guards, reproduce outputs, and close Day 2 | 50 | Not started; the full Day 2 pass criteria are not met. |

These are assistant planning allocations, not measured learner time or a guarantee. The 315 minutes above plus the plan's 45 minutes of focused DMLS reading total six hours. Explanation, practice, coding, debugging, tests, and review all count. Corrections stay inside the lesson rather than becoming extra numbered lessons. If a lesson overruns, report the effect rather than silently extending the deadline or skipping correctness/learning checks.

The Day 2 reading selection is from DMLS Chapter 3 on data formats/batch processing and Chapter 5 on feature leakage. It supports the lessons; it is not a prerequisite for receiving their explanations. No Day 2 reading completion is recorded yet.

## The conceptual depth we will develop

For each consequential choice, connect its purpose to a concrete example, then trace the code and one alternative. For example: how mixing hourly and daily rows changes the target's meaning; why a column can exist but still be an invalid predictor; how a shuffled split can reveal the future; why model validation and policy development need different roles; and why an integrity hash says nothing about data quality. Ask one taught reasoning check per bounded piece, with more guided practice where necessary. No new unaided design prerequisite is introduced.

## Exact Day 2 stopping point

Stop after Lesson 6 when the actual source audit, exact whole-date role manifest (`configs/splits.json`), feature allowlist/schema, preparation command, relevant checks, and learner review are verified. Counts must come from the file, dates must not cross roles, and `casual`/`registered` must not enter model features. Final outcomes remain uninspected. Save raw outputs/hashes and update the handoff.

Model training starts in Day 3. This roadmap does not authorize inspecting final targets, tuning against the final period, or adding models/services. Current status and exactly one next task remain in `PROJECT_STATE.md`.
