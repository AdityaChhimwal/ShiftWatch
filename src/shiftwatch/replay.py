"""Deterministic replay inputs, hidden incident truth, and delayed label release."""

from collections import defaultdict
import random

PRE, DURATION, POST, LABEL_DELAY = 8, 8, 8, 2
BATCHES = PRE + DURATION + POST
DEV_SEEDS = tuple(range(100, 120))
FINAL_SEEDS = tuple(range(200, 220))
SCENARIOS = {
    "stable": ("Stable inputs", None),
    "covariate-low": ("Temperature mix · low", "distribution"),
    "covariate-high": ("Temperature mix · high", "distribution"),
    "quality": ("Invalid humidity", "quality"),
    "target-low": ("Rental counts change · low", "performance"),
    "target-high": ("Rental counts change · high", "performance"),
}


def days_by_date(examples):
    grouped = defaultdict(list)
    for row, label in examples:
        grouped[row["event_time"][:10]].append((row, label))
    return [grouped[day] for day in sorted(grouped)]


def sample(days, rng, count, weights=None):
    return [example for day in rng.choices(days, weights=weights, k=count) for example in day]


def make_replay(examples, scenario, seed):
    days = days_by_date(examples)
    draw, corruption = random.Random(seed), random.Random(seed + 10_000)
    shifted = None
    if scenario.startswith("covariate"):
        strength = 3 if scenario.endswith("low") else 9
        ranked = sorted(range(len(days)), key=lambda i: sum(row["temp"] for row, _ in days[i]) / len(days[i]))
        warm = set(ranked[len(days) * 3 // 4:])
        shifted = [strength if index in warm else 1 for index in range(len(days))]
    reference = sample(days, draw, 14)
    batches = []
    for step in range(BATCHES):
        incident = PRE <= step < PRE + DURATION
        selected = sample(days, draw, 7, shifted if incident else None)
        broken = set()
        if incident and scenario == "quality":
            broken = set(corruption.sample(range(len(selected)), round(len(selected) * 0.15)))
        rows, labels, original = [], {}, {}
        for index, (row, y) in enumerate(selected):
            key = f"r{step:02d}-{index:03d}"
            event = {**row, "record_id": key}
            if index in broken:
                event["hum"] = -1
            rows.append(event)
            original[key] = y
            if incident and scenario == "target-low":
                y = round(1.25 * y + 20)
            if incident and scenario == "target-high":
                y = round(1.5 * y + 40)
            labels[key] = y
        batches.append({"rows": rows, "labels": labels, "original": original})
    channel = SCENARIOS[scenario][1]
    truth = {"channel": channel, "onset": PRE, "end": PRE + DURATION - 1} if channel else None
    return reference, batches, truth


def due_labels(batches, step):
    index = step - LABEL_DELAY
    if 0 <= index < len(batches):
        return index, batches[index]["labels"]
    return None, {}
