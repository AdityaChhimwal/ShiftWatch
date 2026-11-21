# Hosting preparation, not a deployment

21 November 2026, Asia/Calcutta. Assistant-led implementation/teaching.

- Learner's combined Docker retest: "docker run starts the container, with mapping 9000:8000, the browser connects to port 9000." Correct after correction/retest. This passes the narrow build/run and port-mapping check, not independent Docker troubleshooting.
- Prepared `render.yaml`: one free Docker web service, proposed Singapore region, canonical repository/main, existing Dockerfile/context, automatic deployment off, `/health`, and configured port 8000 matching the tested startup command. No cloud resource was created.
- `validation.json` records the real YAML parse and nine project-specific consistency checks. Temporary validation tools were installed under ignored `.tmp/`; production requirements were unchanged. Only PyYAML and local consistency checks were used. This is not validation by Render's API or its full JSON schema.
- Direct schema download from `https://render.com/schema/render.yaml.json` was blocked by a Cloudflare challenge. No challenge was solved or bypassed. Public Render documentation was available through the web reader.
- Browser inventory was available, but the attempt to inspect the existing Windows browser stopped because the tool could not determine its current URL confidently enough to enforce its policy. Browser control was stopped and summarized. No Render page/account was inspected and no authentication, billing, creation, or deployment action occurred.
- An account-status question is pending with the learner. Account/workspace access, free eligibility, remaining quota, effective resources, payment/spend settings, and launch approval are unverified. The proposed service must be reviewed against actual account state before creation.
- Current official docs describe 0.1 CPU/512 MB for free web compute, idle spin-down, temporary local filesystem changes, shared free instance hours, and bandwidth/build usage rules. These are source facts, not observations of this account or measured application capacity. The free-compute choice alone does not establish all workspace billing behavior.
- Source/validation file hashes are recorded in `artifacts.sha256`. Existing Docker/runtime files are unchanged from the successful CI source `a4e4ad4`.

Sources: [Blueprint fields](https://render.com/docs/blueprint-spec), [web service ports](https://render.com/docs/web-services), [free services](https://render.com/docs/free), [health checks](https://render.com/docs/health-checks).
