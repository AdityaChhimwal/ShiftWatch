"""Check the running service over HTTP; uses only Python's standard library."""

import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check_health(base_url: str) -> dict:
    """Wait briefly for startup, then verify liveness and HTTP failure behavior."""
    base_url = base_url.rstrip("/")
    deadline = time.monotonic() + 30
    while True:
        try:
            with urlopen(f"{base_url}/health", timeout=2) as response:
                status = response.status
                body = json.load(response)
            if status != 200 or body != {"status": "ok"}:
                raise AssertionError(f"Unexpected health response: {status}, {body!r}")
            break
        except HTTPError:
            raise  # A live server returning an HTTP error is a failed check.
        except (URLError, ConnectionError, TimeoutError) as error:
            if time.monotonic() >= deadline:
                raise TimeoutError("Service did not become reachable within 30 seconds") from error
            time.sleep(0.5)

    checks = [{"method": "GET", "path": "/health", "status": status, "body": body}]
    for method, path, expected in (("POST", "/health", 405), ("GET", "/__smoke_missing__", 404)):
        try:
            with urlopen(Request(f"{base_url}{path}", method=method), timeout=2) as response:
                actual = response.status
        except HTTPError as error:
            actual = error.code
            error.close()
        if actual != expected:
            raise AssertionError(f"{method} {path}: expected {expected}, got {actual}")
        checks.append({"method": method, "path": path, "status": actual})
    return {"base_url": base_url, "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    print(json.dumps(check_health(args.url), indent=2))
