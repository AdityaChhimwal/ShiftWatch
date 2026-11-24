"""Score only eligible batches and keep misses in the event denominator."""

from statistics import median

from .drift import apply_policy, compare, make_reference
from .model import predict
from .quality import check_rows, observed_error
from .replay import LABEL_DELAY, due_labels, make_replay


def detect_event(timeline, truth):
    channel = truth["channel"]
    offset = LABEL_DELAY if channel == "performance" else 0
    start, end = truth["onset"] + offset, truth["end"] + offset
    eligible = [row["step"] for row in timeline
                if start <= row["step"] <= end and row[channel]["eligible"]]
    alerted = [row["step"] for row in timeline if row["step"] in eligible and row[channel]["alert"]]
    first = min(alerted, default=None)
    first_eligible = min(eligible, default=None)
    return {**truth, "window_start": start, "window_end": end, "eligible": bool(eligible),
            "first_eligible": first_eligible, "first_alert": first, "detected": first is not None,
            "delay": first - truth["onset"] if first is not None else None,
            "eligible_delay": first - first_eligible if first is not None else None,
            "lingering_alert_batches": sum(row["step"] > end and row[channel]["alert"] for row in timeline)}


def rate(numerator, denominator):
    return numerator / denominator if denominator else None


def alert_counts(timeline, channel):
    eligible = alerts = episodes = 0
    was_alert = False
    for row in timeline:
        status = row[channel]
        eligible += bool(status["eligible"])
        alarm = status["eligible"] and status["alert"]
        alerts += bool(alarm)
        episodes += bool(alarm and not was_alert)
        was_alert = alarm
    return {"eligible": eligible, "alerted": alerts, "episodes": episodes,
            "episodes_per_100": rate(100 * episodes, eligible), "alert_rate": rate(alerts, eligible)}


def inspect_batch(model, reference, rows):
    valid, quality = check_rows(rows)
    forecasts = predict(model, valid)
    return dict(zip((row["record_id"] for row in valid), forecasts)), quality, compare(reference, valid, forecasts)


def inspect_replay(model, examples, scenario, seed):
    reference, batches, truth = make_replay(examples, scenario, seed)
    reference_rows = [row for row, _ in reference]
    reference = make_reference(reference_rows, predict(model, reference_rows))
    predictions, timeline = [], []
    for step in range(len(batches) + LABEL_DELAY):
        stats, quality = {}, {"eligible": False, "alert": False}
        if step < len(batches):
            output, quality, stats = inspect_batch(model, reference, batches[step]["rows"])
            predictions.append(output)
            quality["eligible"] = True
        source, labels = due_labels(batches, step)
        original = batches[source]["original"] if source is not None else {}
        prior = predictions[source] if source is not None else {}
        timeline.append({"step": step, "stats": stats, "quality": quality, "label_batch": source,
                         "performance": observed_error(prior, labels, None),
                         "original": observed_error(prior, original, None)})
    return timeline, truth


def apply_timeline(raw, effect, performance_threshold):
    streak = {}
    timeline = []
    for row in raw:
        distribution = apply_policy(row["stats"], effect, streak)
        streak = distribution["streak"]
        performance = {**row["performance"]}
        performance["alert"] = performance["eligible"] and performance["mae"] > performance_threshold
        timeline.append({**row, "distribution": distribution, "performance": performance})
    return timeline


def recall(events):
    eligible = [event for event in events if event["eligible"]]
    delays = [event["delay"] for event in eligible if event["detected"]]
    return {"events": len(events), "eligible": len(eligible), "detected": len(delays),
            "missed": len(eligible) - len(delays), "recall": rate(len(delays), len(eligible)),
            "median_delay": median(delays) if delays else None}


def select_policy(results):
    baseline = results["P0"]
    qualified = []
    for name, effect in (("P1-0.1", 0.1), ("P1-0.2", 0.2)):
        candidate = results[name]
        if all(candidate[key] is not None and baseline[key] is not None
               for key in ("recall", "median_delay", "null_rate")) and (
            candidate["null_rate"] <= 0.05
            and candidate["recall"] >= baseline["recall"] - 0.10
            and candidate["median_delay"] <= baseline["median_delay"] + 1
        ):
            qualified.append((-candidate["recall"], candidate["median_delay"], candidate["null_rate"], effect))
    return min(qualified)[-1] if qualified else None
