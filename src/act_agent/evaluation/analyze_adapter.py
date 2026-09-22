"""Paired development analysis for a trained tool-use adapter."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from act_agent.data.pipeline import sha256
from act_agent.evaluation.stats import PairedOutcome, paired_cluster_bootstrap, wilson_interval


def analyze(
    *,
    base_path: Path,
    adapter_path: Path,
    model_label: str,
    output_path: Path,
) -> dict[str, Any]:
    base_rows = pq.read_table(base_path).to_pylist()  # type: ignore[no-untyped-call]
    base: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in base_rows:
        base[row["task_id"]][row["model"]] = row
    adapter_rows = [json.loads(line) for line in adapter_path.read_text().splitlines() if line]
    seen: set[str] = set()
    paired: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for row in adapter_rows:
        task_id = row["task_id"]
        if task_id in seen or row["model"] != model_label or row["split"] != "development":
            raise ValueError("adapter episode identity invalid or duplicated")
        seen.add(task_id)
        if task_id not in base or not {"B0", "B2"} <= set(base[task_id]):
            raise ValueError("adapter episode lacks paired B0/B2 development baseline")
        if row["task_family"] != base[task_id]["B2"]["task_family"]:
            raise ValueError("task-family mismatch")
        if (
            row.get("world_seed") is None
            or base[task_id]["B2"].get("world_seed") is None
            or row.get("world_seed") != base[task_id]["B2"].get("world_seed")
            or row.get("variant") is None
            or base[task_id]["B2"].get("variant") is None
            or row.get("variant") != base[task_id]["B2"].get("variant")
        ):
            raise ValueError("paired world seed or twin variant mismatch")
        paired.append((base[task_id]["B0"], base[task_id]["B2"], row))
    if not paired:
        raise ValueError("no paired adapter development episodes")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(adapter_rows), output_path)  # type: ignore[no-untyped-call]
    critical = sum(row[2]["critical_violation"] for row in paired)
    comparisons = {}
    for baseline_index, name in ((0, "B0"), (1, "B2")):
        outcomes = [
            PairedOutcome(
                candidate["task_id"],
                candidate["task_family"],
                baseline["success"],
                candidate["success"],
            )
            for triplet in paired
            for baseline, candidate in ((triplet[baseline_index], triplet[2]),)
        ]
        comparisons[f"{model_label}_minus_{name}"] = vars(paired_cluster_bootstrap(outcomes))
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model_label,
        "paired_tasks": len(paired),
        "successes": sum(row[2]["success"] for row in paired),
        "safe_successes": sum(row[2]["safe_success"] for row in paired),
        "process_compliant": sum(row[2]["process_compliant"] for row in paired),
        "critical_violations": critical,
        "critical_wilson_95": wilson_interval(critical, len(paired)),
        "generated_tokens": sum(row[2]["generated_tokens"] for row in paired),
        "generation_seconds": sum(row[2]["generation_seconds"] for row in paired),
        "comparisons": comparisons,
        "adapter_episode_sha256": sha256(adapter_path),
        "canonical_sha256": sha256(output_path),
        "protected_outcome_access": 0,
        "qualification": "development diagnostic only; E07 task mechanics/oracle REVIEW",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-label", choices=["B3", "B4", "B5", "B6", "B7", "M0"], required=True
    )
    parser.add_argument("--episodes", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    root = Path.cwd()
    result = analyze(
        base_path=root / "artifacts/warehouse/e09_episodes.parquet",
        adapter_path=args.episodes,
        model_label=args.model_label,
        output_path=root / "artifacts/warehouse" / f"{args.run_id}_development.parquet",
    )
    target = root / "artifacts" / f"{args.run_id}_summary.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(target, result["successes"], result["paired_tasks"])


if __name__ == "__main__":
    main()
