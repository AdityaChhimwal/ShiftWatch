"""Distribution statistics and the two frozen alert policies."""

from collections import Counter

import numpy as np
from scipy.stats import chi2_contingency, ks_2samp

NUMERIC_MONITORS = ("temp", "hum", "windspeed", "prediction")
CATEGORY_MONITORS = ("workingday", "weathersit")
MIN_SAMPLE = 100


def make_reference(rows, predictions):
    numeric = {name: [row[name] for row in rows] for name in NUMERIC_MONITORS[:-1]}
    numeric["prediction"] = predictions
    return {
        "numeric": {
            name: {"values": values, "edges": quantile_edges(values)}
            for name, values in numeric.items()
        },
        "categorical": {
            name: dict(Counter(str(row[name]) for row in rows)) for name in CATEGORY_MONITORS
        },
    }


def quantile_edges(reference):
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, 11)))
    return edges[1:-1].tolist()


def psi(reference, current, edges):
    if not edges:
        return None
    bins = [-np.inf, *edges, np.inf]
    before = np.histogram(reference, bins)[0] + 0.5
    after = np.histogram(current, bins)[0] + 0.5
    before, after = before / before.sum(), after / after.sum()
    return float(np.sum((after - before) * np.log(after / before)))


def numeric_stats(reference, current):
    values = reference["values"]
    result = {"reference_n": len(values), "current_n": len(current), "eligible": False}
    if min(len(values), len(current)) < MIN_SAMPLE:
        return {**result, "reason": "insufficient sample"}
    if min(values) == max(values):
        return {**result, "reason": "constant reference"}
    statistic = ks_2samp(values, current, method="asymp")
    return {**result, "eligible": True, "effect": float(statistic.statistic),
            "p": float(statistic.pvalue), "psi": psi(values, current, reference["edges"])}


def categorical_stats(reference, current):
    counts = Counter(map(str, current))
    total = sum(reference.values())
    result = {"reference_n": total, "current_n": len(current), "eligible": False,
              "unseen": sum(count for code, count in counts.items() if code not in reference)}
    if min(total, len(current)) < MIN_SAMPLE:
        return {**result, "reason": "insufficient sample"}
    codes = sorted(reference)
    before = [reference[code] for code in codes]
    after = [counts[code] for code in codes]
    if result["unseen"]:
        before.append(0)
        after.append(result["unseen"])
    result["effect"] = sum(abs(a / total - b / len(current)) for a, b in zip(before, after)) / 2
    if len(before) < 2:
        return {**result, "reason": "constant categories"}
    statistic = chi2_contingency([before, after], correction=False)
    if np.any(statistic.expected_freq < 5):
        return {**result, "reason": "expected count below 5"}
    return {**result, "eligible": True, "p": float(statistic.pvalue)}


def compare(reference, rows, predictions):
    current = {name: [row[name] for row in rows] for name in NUMERIC_MONITORS[:-1]}
    current["prediction"] = predictions
    results = {
        name: numeric_stats(ref, current[name]) for name, ref in reference["numeric"].items()
    }
    results.update({
        name: categorical_stats(ref, [row[name] for row in rows])
        for name, ref in reference["categorical"].items()
    })
    return results


def apply_policy(results, effect=None, previous=None):
    previous = previous or {}
    streak, alerted = {}, []
    for name, result in results.items():
        eligible = result["eligible"]
        significant = eligible and result["p"] < 0.05
        qualifies = effect is not None and significant and result["effect"] >= effect
        streak[name] = previous.get(name, 0) + 1 if qualifies else 0
        divergence = result.get("psi")
        if effect is None:
            alarm = eligible and (significant or (divergence is not None and divergence >= 0.2))
        else:
            alarm = streak[name] >= 2
        if alarm:
            alerted.append(name)
    return {"eligible": any(result["eligible"] for result in results.values()),
            "alert": bool(alerted), "features": alerted, "streak": streak}
