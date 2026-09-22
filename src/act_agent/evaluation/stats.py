"""Paired estimators for clustered synthetic task evaluation."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from math import sqrt
from statistics import mean

from scipy.stats import binomtest, norm  # type: ignore[import-untyped]


@dataclass(frozen=True)
class PairedOutcome:
    task_id: str
    family: str
    baseline: bool
    candidate: bool


@dataclass(frozen=True)
class PairedSummary:
    n: int
    baseline_rate: float
    candidate_rate: float
    difference: float
    ci_low: float
    ci_high: float
    mcnemar_p: float


def paired_cluster_bootstrap(
    rows: list[PairedOutcome], *, repetitions: int = 2000, seed: int = 20260920
) -> PairedSummary:
    if not rows or repetitions < 100:
        raise ValueError("need paired rows and at least 100 bootstrap replicates")
    ids = [r.task_id for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate task_id; aggregate training seeds separately")
    groups: dict[str, list[PairedOutcome]] = defaultdict(list)
    for row in rows:
        groups[row.family].append(row)
    families = sorted(groups)
    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(repetitions):
        sampled: list[PairedOutcome] = []
        for _ in families:
            family = rng.choice(families)
            members = groups[family]
            sampled.extend(rng.choice(members) for _ in members)
        draws.append(mean(int(r.candidate) - int(r.baseline) for r in sampled))
    draws.sort()
    discordant_a = sum(r.candidate and not r.baseline for r in rows)
    discordant_b = sum(r.baseline and not r.candidate for r in rows)
    discordant = discordant_a + discordant_b
    p = (
        float(binomtest(min(discordant_a, discordant_b), discordant, 0.5).pvalue)
        if discordant
        else 1.0
    )
    return PairedSummary(
        len(rows),
        mean(int(r.baseline) for r in rows),
        mean(int(r.candidate) for r in rows),
        mean(int(r.candidate) - int(r.baseline) for r in rows),
        draws[int(0.025 * repetitions)],
        draws[int(0.975 * repetitions) - 1],
        p,
    )


def wilson_interval(events: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    if total <= 0 or not 0 <= events <= total:
        raise ValueError("invalid event count")
    z = float(norm.ppf((1 + confidence) / 2))
    p = events / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    radius = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return center - radius, center + radius
