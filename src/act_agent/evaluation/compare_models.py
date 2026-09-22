"""Paired development comparison between two sealed adapter episode logs."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from act_agent.data.pipeline import sha256
from act_agent.evaluation.stats import PairedOutcome, paired_cluster_bootstrap


def _read(path: Path) -> dict[str, dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    result = {row["task_id"]: row for row in rows}
    if len(result) != len(rows) or not result:
        raise ValueError("empty or duplicate task IDs in adapter episode log")
    if any(row.get("split") != "development" for row in rows):
        raise ValueError("comparison accepts development episodes only")
    return result


def compare(baseline_path: Path, candidate_path: Path) -> dict[str, Any]:
    baseline = _read(baseline_path)
    candidate = _read(candidate_path)
    if baseline.keys() != candidate.keys():
        raise ValueError("paired adapter task IDs differ")
    for task_id, first in baseline.items():
        second = candidate[task_id]
        for field in ("task_family", "world_seed", "variant"):
            if first.get(field) is None or first[field] != second.get(field):
                raise ValueError(f"paired adapter {field} differs: {task_id}")
    fields = {
        "completion": "success",
        "safe_completion": "safe_success",
        "process_compliance": "process_compliant",
        "critical_process_flag": "critical_violation",
    }
    metrics = {}
    for label, field in fields.items():
        outcomes = [
            PairedOutcome(
                task_id,
                baseline[task_id]["task_family"],
                bool(baseline[task_id][field]),
                bool(candidate[task_id][field]),
            )
            for task_id in sorted(baseline)
        ]
        metrics[label] = asdict(paired_cluster_bootstrap(outcomes))
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "EXPLORATORY_DEVELOPMENT",
        "paired_tasks": len(baseline),
        "baseline_model": sorted({row["model"] for row in baseline.values()}),
        "candidate_model": sorted({row["model"] for row in candidate.values()}),
        "baseline_sha256": sha256(baseline_path),
        "candidate_sha256": sha256(candidate_path),
        "metrics": metrics,
        "qualification": "E07 task mechanics/oracle REVIEW; no protected outcome access",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    result = compare(args.baseline, args.candidate)
    target = Path("artifacts") / f"{args.run_id}_paired_comparison.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(target, result["metrics"]["completion"]["difference"])


if __name__ == "__main__":
    main()
