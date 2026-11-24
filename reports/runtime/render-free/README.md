# Hosted verification

ShiftWatch is live on the existing Render Free service in Singapore. The deployed revision is `47dbd03`, the exact source pinned by the final evaluation. Render reported 58.8 seconds for the deployment. [Public dashboard](https://shiftwatch-iejl.onrender.com/) · [Deployment record](deployment.json) · [Evaluation freeze](../../freeze.json)

The HTTPS checks covered health, bad requests, session isolation, idempotent retries, label conflicts, and all 26 stable replay steps including the label flush. The browser test completed the quality replay and verified a JSON export containing 24 prediction batches. It also uploaded the two bundled template CSVs and verified the two actual rental counts in the exported CSV. [API checks](acceptance.json) · [Browser checks](browser.json)

## Warm requests

| Requests | Rows per request | Client concurrency | Median | 95th percentile |
|---:|---:|---:|---:|---:|
| 30 | 500 | 1 | 571 ms | 977 ms |

Each sample measures a public HTTPS round trip for one accepted synthetic batch. The client used two sessions and excluded the initial warm-up request. This run measures the specified workload, client location, and instance. [Runtime summary](runtime.json) · [All 30 samples](timings.csv)

Render showed a 512 MB instance memory limit. The usage chart displayed no samples during verification, so peak hosted memory is unavailable. The separate Windows benchmark includes the measured local process working set. [Render memory observation](memory.json) · [Local measurements](../local-windows/runtime.json)

Run the same benchmark from a working Python environment using the bundled script:

```bash
python scripts/smoke_app.py --url https://shiftwatch-iejl.onrender.com \
  --benchmark .tmp/hosted-benchmark --host "Render Free, Singapore"
```

## Wake-up after idle shutdown

After 16 minutes without test traffic, the service returned Render's sleep marker on `/robots.txt`. The first subsequent `GET /health` returned HTTP 200 with the app's expected JSON after **22.4 seconds**. This is one measured wake-up. The deployment duration and warm batch timings measure different operations. [Cold-start sample](cold-start.json) · [How Render serves robots.txt during idle shutdown](https://render.com/docs/free#automatic-robotstxt-responses)

The service stores session data temporarily. Export results before leaving the session. Render Free may discard SQLite data on idle shutdown, restart, or redeploy. [Render Free limits](https://render.com/docs/free)
