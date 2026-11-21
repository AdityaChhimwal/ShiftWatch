# Initial container packaging

Date: 21 November 2026, Asia/Calcutta. Assistant implemented; learner's image/container check is not yet assessed.

- Git retest answer: "It is now recorded in the local Git history." Correct after correction/retest; Lesson 5A's narrow check passed.
- Local default-context Docker access was denied. With approved engine access, `docker info --format '{{.ServerVersion}}'` returned:

```text
request returned 500 Internal Server Error for API route and version http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.55/info, check if the server supports the requested API version
```

- `docker buildx imagetools inspect python:3.13-slim` independently reached the image registry and reported the multi-platform index digest `sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90`. Linux amd64 metadata reported Python `3.13.18-slim-trixie`, with manifest digest `sha256:48d884813cf44e927cf64c5529dd630dd3b18338c6dc727991eef9b71e934a20`. That index digest is pinned in the Dockerfile.
- GitHub's official checkout v7 ref resolved to `3d3c42e5aac5ba805825da76410c181273ba90b1`; the workflow pins this revision.
- Added a minimal image recipe, strict build-context allowlist, real-HTTP checker, and standard Ubuntu CI workflow. No application behavior, monitoring algorithm, model, or schema changed.
- At initial publication, the CI outcome is pending. Local container operation, public deployment, ML compatibility, and later persistence behavior are not claimed.

## First run and startup-checker correction

Run [44899180692](https://github.com/AdityaChhimwal/ShiftWatch/actions/runs/44899180692), source revision `8437daaebb519677a7790df1d6c997d02da0f515`, built the image, passed dependency consistency, reported Python 3.13.18, and passed all four schema tests. Its HTTP step failed on `ConnectionResetError: [Errno 104] Connection reset by peer` immediately after container creation. The job cleaned up before server startup completed, so it did not establish a passing HTTP service.

The checker retried `URLError` but did not catch this direct transport exception. Extend the bounded startup retry to `ConnectionError` and `TimeoutError`, retaining immediate failure for actual HTTP errors and incorrect response bodies. Add two regression tests covering startup transport recovery and immediate HTTP-error failure. CI mounts the checker scripts read-only alongside the tests; they remain outside the runtime image. Preserve this failed result and its raw log; the corrected run is still pending at this revision.
