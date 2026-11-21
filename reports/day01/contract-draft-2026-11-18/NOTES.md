# Day 1 contract/identity lesson — 18 November 2026

The learner requested "Next" after the health lesson. This authorizes continuing guided teaching; it does not demonstrate an answer to the health comprehension question. The missing-label check remains the only independently answered/passed check so far.

Prepared an assistant-proposed contract with a problem statement, intended architecture, metadata/feature/label separation, provisional request examples, identity decision, and unresolved schema/validation choices. No batch or label API route, model, storage, detector, or replay lifecycle was implemented.

Executed `./.venv/Scripts/python.exe examples/contracts/trace_identity.py` from the project root (host PowerShell invocation). Both synthetic matches were checked against the hand-worked values despite reversed label order: hour-10 uses 90 and has illustrative error 5; hour-09 uses 120 and has illustrative error 30. Raw JSON is in `identity-trace.json`. The script's source and raw output explicitly label these invented teaching values. The learner's own execution is unobserved.

This example does not handle duplicate/conflicting labels or delayed availability, and does not pass the eventual independent duplicate-label checkpoint. Actual feature/schema/terms audit remains Day 2 work. Existing service verification was not rerun because the service code did not change.

Day 1 stays partial. Contract/architecture learner review, other explanation checks, public health deployment/access, tester availability, and remaining setup deliverables are pending. Measured learner hours remain unknown. Next task: the single stable-ID question in Lesson 2.

`before-state.md` preserves the preceding state; `before-state.sha256` records its original bytes. `after.sha256` records the lesson, contract, examples, trace, output, README/state, and these notes at this revision. Prior session manifests remain historical.
