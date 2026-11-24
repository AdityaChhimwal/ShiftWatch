"""Regression cases for model boundaries, change signals, and replay scoring."""

import unittest
from pathlib import Path
import tempfile

from shiftwatch.drift import apply_policy, categorical_stats, numeric_stats, psi
from shiftwatch.evaluation import detect_event, recall, select_policy
from shiftwatch.model import FEATURES
from shiftwatch.quality import check_rows, observed_error
from shiftwatch.replay import due_labels, make_replay, PRE
from shiftwatch.storage import SessionError, Store
from train import assign_dates


def example(row_id="a"):
    return {"record_id": row_id, "event_time": "2012-06-04T08:00:00",
            "hr": 8, "weekday": 1, "workingday": 1, "mnth": 6,
            "temp": 0.55, "hum": 0.61, "windspeed": 0.15, "weathersit": 1}


class MonitorTests(unittest.TestCase):
    def test_dates_are_disjoint_and_outcomes_are_rejected_as_features(self):
        result = list(assign_dates({f"2012-01-{i:02}": i for i in range(1, 21)}).values())
        self.assertEqual(sum(role["rows"] for role in result), 210)
        self.assertTrue(all(a["last"] < b["first"] for a, b in zip(result, result[1:])))
        for target in ("cnt", "casual", "registered", "instant"):
            self.assertNotIn(target, FEATURES)
            valid, quality = check_rows([{**example(), target: 42}])
            self.assertFalse(valid)
            self.assertTrue(quality["alert"])

    def test_histogram_and_sparse_category_evidence(self):
        self.assertEqual(psi([0, 0], [0, 0], [0.5]), 0)
        self.assertGreater(psi([0, 0], [1, 1], [0.5]), 0)
        self.assertFalse(numeric_stats({"values": [0] * 100, "edges": []}, [1] * 100)["eligible"])
        stats = categorical_stats({"1": 99, "2": 1}, [1] * 99 + [3])
        self.assertEqual(stats["unseen"], 1)
        self.assertFalse(stats["eligible"])
        self.assertNotIn("p", stats)
        self.assertFalse(numeric_stats({"values": list(range(100)), "edges": [50]}, [0])["eligible"])

    def test_persistence_breaks_on_ineligible_batch(self):
        evidence = {"temp": {"eligible": True, "p": 0.01, "effect": 0.2}}
        first = apply_policy(evidence, 0.1)
        self.assertTrue(first["eligible"])
        self.assertFalse(first["alert"])
        second = apply_policy(evidence, 0.1, first["streak"])
        self.assertTrue(second["alert"])
        broken = apply_policy({"temp": {"eligible": False}}, 0.1, second["streak"])
        self.assertFalse(apply_policy(evidence, 0.1, broken["streak"])["alert"])

    def test_delays_exclude_misses_but_recall_counts_them(self):
        truth = {"channel": "performance", "onset": 2, "end": 3}
        timeline = [{"step": i, "performance": {"eligible": True, "alert": i in (2, 5, 6)}} for i in range(7)]
        detected = detect_event(timeline, truth)
        missed = detect_event(timeline[:5], truth)
        self.assertEqual((detected["delay"], detected["eligible_delay"], detected["lingering_alert_batches"]), (3, 1, 1))
        self.assertIsNone(missed["delay"])
        self.assertEqual(recall([detected, missed])["recall"], 0.5)
        self.assertIsNone(recall([])["recall"])

    def test_target_stress_preserves_inputs_and_withholds_labels(self):
        examples = [(example(), 100)]
        _, stable, _ = make_replay(examples, "stable", 7)
        _, stressed, _ = make_replay(examples, "target-high", 7)
        self.assertEqual([b["rows"] for b in stable], [b["rows"] for b in stressed])
        self.assertNotEqual(stable[PRE]["labels"], stressed[PRE]["labels"])
        self.assertEqual(due_labels(stressed, 1), (None, {}))
        self.assertEqual(due_labels(stressed, 2)[0], 0)
        self.assertEqual(due_labels(stressed, len(stressed) + 1)[0], len(stressed) - 1)

    def test_performance_remains_partial_even_with_large_labeled_subset(self):
        forecasts = {i: 10 for i in range(101)}
        labels = {i: 15 for i in range(100)}
        error = observed_error(forecasts, labels, 1)
        self.assertEqual((error["status"], error["mae"], error["alert"]), ("partial", 5, False))

    def test_policy_selection_accepts_only_candidates_meeting_all_gates(self):
        def metrics(rate, recall_value, delay):
            return {"null_rate": rate, "recall": recall_value, "median_delay": delay}
        results = {"P0": metrics(0.5, 0.9, 1), "P1-0.1": metrics(0.06, 0.9, 1),
                   "P1-0.2": metrics(0.04, 0.85, 2)}
        self.assertEqual(select_policy(results), 0.2)
        results["P1-0.2"]["median_delay"] = None
        self.assertIsNone(select_policy(results))

    def test_sqlite_restart_preserves_session_and_rejects_a_new_artifact_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sessions.sqlite3"
            store = Store(path, None, {}, {}, {"model.joblib": "v1"})
            user = store.create("custom")
            arguments = user["session_id"], user["token"]
            restarted = Store(path, None, {}, {}, {"model.joblib": "v1"})
            with restarted.transaction(write=False) as db:
                self.assertEqual(restarted.authorize(db, *arguments)["mode"], "custom")
            changed = Store(path, None, {}, {}, {"model.joblib": "v2"})
            with changed.transaction(write=False) as db, self.assertRaisesRegex(SessionError, "version changed"):
                changed.authorize(db, *arguments)
