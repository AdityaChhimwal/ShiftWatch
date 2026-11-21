"""Prevent startup transport errors from making container checks fail early."""

import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from smoke_health import check_health


class SmokeHealthTests(unittest.TestCase):
    def test_transient_startup_errors_are_retried_then_responses_are_checked(self):
        errors = (URLError("not ready"), ConnectionResetError(), ConnectionRefusedError(), TimeoutError())
        for error in errors:
            with self.subTest(error=type(error).__name__):
                response = io.BytesIO(b'{"status":"ok"}')
                response.status = 200
                replies = [
                    error,
                    response,
                    HTTPError("http://example.test/health", 405, "Method Not Allowed", {}, None),
                    HTTPError("http://example.test/missing", 404, "Not Found", {}, None),
                ]
                with patch("smoke_health.urlopen", side_effect=replies) as request:
                    with patch("smoke_health.time.sleep") as sleep:
                        report = check_health("http://example.test")
                self.assertEqual([item["status"] for item in report["checks"]], [200, 405, 404])
                self.assertEqual(request.call_count, 4)
                sleep.assert_called_once_with(0.5)

    def test_real_http_error_is_reported_without_startup_retry(self):
        error = HTTPError("http://example.test/health", 503, "Unavailable", {}, None)
        with patch("smoke_health.urlopen", side_effect=error) as request:
            with patch("smoke_health.time.sleep") as sleep:
                with self.assertRaises(HTTPError):
                    check_health("http://example.test")
        request.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
