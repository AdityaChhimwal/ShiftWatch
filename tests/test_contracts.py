"""Check failures that would corrupt or obscure the later label lifecycle."""

import unittest

from pydantic import ValidationError

from shiftwatch.contracts import LabelRecord


class LabelRecordTests(unittest.TestCase):
    def test_valid_fields_are_preserved_including_zero(self):
        for count in (0, 100):
            payload = {"record_id": "hour-10", "cnt": count}
            with self.subTest(count=count):
                self.assertEqual(LabelRecord.model_validate(payload).model_dump(), payload)

    def test_count_rejects_silent_coercion_and_negative_values(self):
        for invalid_count in ("100", True, 100.0, -1, None):
            with self.subTest(value=repr(invalid_count)):
                with self.assertRaises(ValidationError) as caught:
                    LabelRecord.model_validate({"record_id": "hour-10", "cnt": invalid_count})
                self.assertIn(("cnt",), [error["loc"] for error in caught.exception.errors()])

    def test_id_requires_nonempty_bounded_text_without_whitespace(self):
        for invalid_id in ("", " ", "hour 10", "hour-10 ", "x" * 65, 10, None):
            with self.subTest(value=repr(invalid_id)):
                with self.assertRaises(ValidationError) as caught:
                    LabelRecord.model_validate({"record_id": invalid_id, "cnt": 100})
                self.assertIn(("record_id",), [error["loc"] for error in caught.exception.errors()])

    def test_missing_fields_and_unexpected_data_are_not_silently_ignored(self):
        cases = [
            ({"cnt": 100}, "missing"),
            ({"record_id": "hour-10"}, "missing"),
            ({"record_id": "hour-10", "cnt": 100, "prediction": 90}, "extra_forbidden"),
        ]
        for payload, expected_error in cases:
            with self.subTest(payload=payload):
                with self.assertRaises(ValidationError) as caught:
                    LabelRecord.model_validate(payload)
                self.assertIn(expected_error, [error["type"] for error in caught.exception.errors()])


if __name__ == "__main__":
    unittest.main()
