"""Canonical audit of scripted preference pairs and materialized continuations."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean, median
from typing import Any

import pyarrow.parquet as pq

from act_agent.data.pipeline import sha256
from act_agent.tasks.generator import make_task


def audit(source: Path, materialized: Path) -> dict[str, Any]:
    pairs = pq.read_table(source).to_pylist()  # type: ignore[no-untyped-call]
    texts = pq.read_table(materialized).to_pylist()  # type: ignore[no-untyped-call]
    ids = [row["pair_id"] for row in pairs]
    text_ids = {row["pair_id"] for row in texts}
    weights = [float(row["weight"]) for row in texts]
    chosen = [row["chosen_assistant_tokens"] for row in texts]
    rejected = [row["rejected_assistant_tokens"] for row in texts]
    markets = Counter(
        make_task("train", int(row["task_id"].split("-")[-1])).initial_state.market_id
        for row in texts
    )
    checks = {
        "pair_ids_unique": len(ids) == len(set(ids)),
        "materialized_subset": text_ids <= set(ids),
        "positive_assistant_targets": min(chosen + rejected) > 0,
        "finite_bounded_weights": all(0.1 <= weight <= 5.0 for weight in weights),
        "matched_tape_metadata": all(row["world_seed"] == row["exogenous_seed"] for row in pairs),
    }
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "REVIEW" if all(checks.values()) else "FAIL",
        "checks": checks,
        "source_pairs": len(pairs),
        "materialized_pairs": len(texts),
        "source_sha256": sha256(source),
        "materialized_sha256": sha256(materialized),
        "duplicate_pair_id_count": len(ids) - len(set(ids)),
        "task_family_balance": dict(Counter(row["task_family"] for row in texts)),
        "negative_type_balance": dict(Counter(row["negative_type"] for row in texts)),
        "market_balance": dict(markets),
        "policy_pack_balance": dict(Counter(row["policy_pack"] for row in pairs)),
        "decisive_dimension_balance": dict(Counter(row["decisive_dimension"] for row in pairs)),
        "mean_weight": mean(weights),
        "median_weight": median(weights),
        "mean_chosen_assistant_tokens": mean(chosen),
        "mean_rejected_assistant_tokens": mean(rejected),
        "alternate_exogenous_tape_replay": "NOT_RUN",
        "model_rollout_sources": "NOT_PRESENT",
        "conclusion": "Scripted development pairs may be used for bounded method pilots; they do not qualify full ACT-PO hard-negative claims.",
    }


if __name__ == "__main__":
    source = Path("artifacts/warehouse/preference_pairs.parquet")
    materialized = Path("/home/bjw-0/.cache/act-agent-v1/data/preference_tokens.parquet")
    result = audit(source, materialized)
    Path("artifacts/preference_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], result["checks"], result["materialized_pairs"])
    if result["status"] == "FAIL":
        raise SystemExit(1)
