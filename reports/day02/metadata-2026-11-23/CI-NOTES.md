# Completed Linux verification

The earlier `NOTES.md` and local artifact manifest describe the pre-CI snapshot and remain unchanged. Linux CI subsequently passed on source `2db67033e52ee6874697fd53331ab1c457bfbceb`.

- Run: [45201977061](https://github.com/AdityaChhimwal/ShiftWatch/actions/runs/45201977061), job `137787566203`, completed successfully.
- Clean Linux Docker build and dependency consistency passed; runtime Python was 3.13.18.
- All 14 offline tests passed inside the image, including the five metadata audit regressions. Fixtures are invented; CI does not download or inspect real UCI outcomes.
- Real container HTTP checks observed GET `/health` 200 with `{"status":"ok"}`, POST `/health` 405, and missing route 404.
- The built image ID is in `ci-verification.json`; it identifies this CI image, not a newly deployed Render image.

`ci-passed.log` preserves the decoded job log; `ci-verification.json` records actual run, source, job, steps, Python, image, test count, and HTTP evidence. `ci-artifacts.sha256` fingerprints these files and this note. The local evidence manifest still fingerprints its original five files. No hosting configuration or deployment changed.
