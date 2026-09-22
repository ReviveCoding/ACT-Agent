"""Development-only scripted preference candidates with state-matched provenance."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from act_agent.preference.core import TrajectoryScore, compare
from act_agent.tasks.generator import make_task

PERTURBATIONS = (
    "wrong_tool",
    "wrong_argument",
    "missing_confirmation",
    "premature_write",
    "over_action",
    "inefficient_success",
    "unsafe_success",
    "tie",
)


def scores(kind: str, actionable: bool) -> tuple[TrajectoryScore, TrajectoryScore]:
    expert = TrajectoryScore(0, 0, actionable, 0, 0, 100)
    negatives = {
        "wrong_tool": TrajectoryScore(0, 0, False, 1 if actionable else 0, 0, 105),
        "wrong_argument": TrajectoryScore(0, 0, False, 1 if actionable else 0, 0, 110),
        "missing_confirmation": TrajectoryScore(1, 1, actionable, 0, 0, 100),
        "premature_write": TrajectoryScore(0, 1, actionable, 0, 0, 90),
        "over_action": TrajectoryScore(0, 1, actionable, 0, 2, 130),
        "inefficient_success": TrajectoryScore(0, 0, actionable, 0, 2, 140),
        "unsafe_success": TrajectoryScore(1, 0, True, 0, 0, 80),
        "tie": expert,
    }
    return expert, negatives[kind]


def generate_candidates(path: Path, worlds: int = 3000, keep_pairs: int = 10000) -> dict[str, Any]:
    """Generate labels, then deterministic balanced subsample without outcome tuning.

    Scripted scores are known-answer examples. They are not substitutes for
    actual ReAct/SFT/on-policy rollouts or alternate-tape stability checks.
    """
    if worlds < 1 or keep_pairs < 1:
        raise ValueError("positive scale required")
    rows: list[dict[str, Any]] = []
    label_counts: Counter[str] = Counter()
    for index in range(worlds):
        task = make_task("train", index)
        actionable = task.family in {"REPAIR", "OPTIMIZE", "APPROVAL", "COMPOUND"}
        for kind in PERTURBATIONS:
            expert, negative = scores(kind, actionable)
            preference = compare(
                expert,
                negative,
                severity=2.0 if kind in {"missing_confirmation", "unsafe_success"} else 1.0,
            )
            label_counts[preference.decisive_dimension or "TIE"] += 1
            rows.append(
                {
                    "pair_id": f"{task.task_id}-{kind}",
                    "task_id": task.task_id,
                    "task_family": task.family,
                    "initial_state_version": task.initial_state.state_version,
                    "world_seed": str(task.world_seed),
                    "exogenous_seed": str(task.world_seed),
                    "policy_pack": task.initial_state.policy_pack,
                    "candidate_source": "scripted_perturbation",
                    "negative_type": kind,
                    "chosen": "expert" if preference.winner == "left" else None,
                    "rejected": kind if preference.winner == "left" else None,
                    "decisive_dimension": preference.decisive_dimension,
                    "margin": preference.margin,
                    "weight": preference.weight,
                    "expert_score": json.dumps(asdict(expert), sort_keys=True),
                    "negative_score": json.dumps(asdict(negative), sort_keys=True),
                }
            )
    raw_count = len(rows)
    accepted = [row for row in rows if row["chosen"] is not None]
    accepted.sort(key=lambda row: hashlib.sha256(row["pair_id"].encode()).digest())
    retained = accepted[:keep_pairs]
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(retained), path)  # type: ignore[no-untyped-call]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "raw_candidates": raw_count,
        "ties_or_drops": raw_count - len(accepted),
        "accepted_before_sampling": len(accepted),
        "retained_pairs": len(retained),
        "label_dimensions": dict(label_counts),
        "sha256": digest,
        "path": str(path),
        "provenance": "scripted perturbations only",
        "missing_sources": ["ReAct", "SFT rollout", "on-policy rollout"],
        "alternate_tape_stability_qualified": False,
    }
