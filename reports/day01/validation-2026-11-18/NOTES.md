# Day 1 Lesson 3 — 18 November 2026

Learner selected the correct prediction 90 for actual 100, but suggested record_id or predicted/actual values as a match. Corrected: values are not identity keys; matching uses record_id and error calculation follows. ID reasoning remains partially demonstrated pending a new counterexample. The four required later independent exercises remain unattempted.

The learner asked how many Day 1 lessons remain. The assistant grouped existing Day 1 scope into six numbered lessons, with Lesson 3 current and three remaining after it; the prior problem introduction is unnumbered. This is teaching organization, not newly added scope or completed gates.

Added LabelRecord schema, a six-case trace, four focused standard-library unittest methods, Lesson 3, and the roadmap. Installed Pydantic 2.14.3 was reused; no dependency change or new HTTP route. The schema strictly checks integer/nonnegative counts, text/nonempty/bounded/no-whitespace IDs, required fields, and forbidden extra fields. It does not validate ID existence/ownership, label availability, duplicate/conflicting retries, or persistence. Feature/schema/terms audit is still pending.

Executed with PYTHONPATH set to src in host PowerShell:

```text
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe examples/contracts/trace_validation.py
```

Four tests passed. The saved trace had the expected six shape-validity results: true, false, false, false, false, true. The final true result is deliberately an unknown but well-formed ID, demonstrating that existence checking is a separate required stage. Raw results are in unittest.txt and validation-trace.json. Learner execution/understanding of validation is not inferred from assistant tests. The health service was not changed or retested.

Official Pydantic strict-mode, configuration, and fields documentation was consulted; links are in Lesson 3. Behavior was verified with the installed library. Prior state/hashes and historical lesson reports remain preserved. Current revision files are recorded in after.sha256. Day 1 stays partial; measured learner hours remain unknown.
