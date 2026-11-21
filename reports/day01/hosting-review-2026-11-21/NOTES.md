# Render creation review — awaiting launch approval

21 November 2026, Asia/Calcutta. Read-only account review and an unsubmitted creation form.

- Authenticated Render dashboard access was observed after the learner completed sign-in. Workspace quota, spending controls, and billing configuration were inspected without changing them. Detailed account/billing observations are retained only in ignored local evidence and are not published in this repository.
- The existing GitHub integration listed `AdityaChhimwal/ShiftWatch`; no new credential or integration permission was requested or granted.
- Connected that repository to the new Blueprint review, selected `main`, kept the default root `render.yaml` path, and entered the Blueprint name `ShiftWatch`. Render displayed `Specified configurations` and `Create web service shiftwatch` without a visible configuration error.
- The reviewed proposal requests one free Docker web service in Singapore, internal port 8000, GET `/health`, and manual service deployments. Its file SHA-256 is `305794fa63c2452bd4fb35ceb227ef07a3eba075ee858c95a2e0a00bb2afc9b0`; its initial published source revision was `15719b157120a0d35c1130c79d292ea6e3c98ea5`. Subsequent review-document changes do not alter that proposal or the previously tested runtime files.
- The UI warns that future Blueprint-file updates sync automatically and can change costs. This is distinct from `autoDeployTrigger: "off"`, which controls ordinary source-commit service deployments. Review future configuration changes before pushing them; that setting alone does not disable Blueprint configuration sync.
- Stopped before the `Deploy Blueprint` button. No service, public endpoint, paid resource, or new deployment was created. Existing services and all workspace settings were untouched. This is a creation-form review, not a successful host deployment or a formal Render API validation response.
- The prepared creation screen was captured locally for the learner's launch review and the tab was retained for continuation. Launch authorization remains the next task under the working agreement; public-health verification follows an approved deployment.

Current sources: [Render terms](https://render.com/terms), [free-service limits](https://render.com/docs/free), [Blueprint fields](https://render.com/docs/blueprint-spec). Public docs do not establish future measured model capacity or application availability.
