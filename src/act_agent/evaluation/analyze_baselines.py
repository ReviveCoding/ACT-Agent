"""Validate paired B0–B2 development evidence and publish canonical summaries."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from act_agent.data.pipeline import sha256
from act_agent.evaluation.stats import PairedOutcome, paired_cluster_bootstrap, wilson_interval


def analyze(source: Path, output: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in source.read_text().splitlines() if line]
    by_task: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        if row["model"] in by_task[row["task_id"]]:
            raise ValueError("duplicate model-task episode")
        if row["split"] != "development" or not row["synthetic"]:
            raise ValueError("non-development evidence in E09")
        by_task[row["task_id"]][row["model"]] = row
    complete = {
        task: models for task, models in by_task.items() if set(models) == {"B0", "B1", "B2"}
    }
    if not complete:
        raise ValueError("no complete paired B0-B2 tasks")
    canonical = [row for models in complete.values() for row in models.values()]
    output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(canonical), output)  # type: ignore[no-untyped-call]
    model_metrics = {}
    for model in ("B0", "B1", "B2"):
        m = [models[model] for models in complete.values()]
        critical = sum(row["critical_violation"] for row in m)
        model_metrics[model] = {
            "n": len(m),
            "success": sum(row["success"] for row in m),
            "safe_success": sum(row["safe_success"] for row in m),
            "process_compliant": sum(row["process_compliant"] for row in m),
            "critical_violations": critical,
            "critical_wilson_95": wilson_interval(critical, len(m)),
            "appropriate_abstention": sum(row["appropriate_abstention"] for row in m),
            "finalized": sum(row["finalized"] for row in m),
            "generated_tokens": sum(row["generated_tokens"] for row in m),
            "generation_seconds": sum(row["generation_seconds"] for row in m),
        }
    comparisons = {}
    for model in ("B1", "B2"):
        pairs = [
            PairedOutcome(
                task, models["B0"]["task_family"], models["B0"]["success"], models[model]["success"]
            )
            for task, models in complete.items()
        ]
        comparisons[model + "_minus_B0"] = vars(paired_cluster_bootstrap(pairs))
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "split": "development",
        "paired_tasks": len(complete),
        "source_sha256": sha256(source),
        "canonical_sha256": sha256(output),
        "models": model_metrics,
        "comparisons": comparisons,
        "task_family_balance": dict(
            Counter(models["B0"]["task_family"] for models in complete.values())
        ),
        "protected_outcome_access": 0,
        "caveat": "E07 task-difficulty qualification is REVIEW; no high-difficulty or protected claim.",
    }


if __name__ == "__main__":
    result = analyze(
        Path("/home/bjw-0/.cache/act-agent-v1/e09_baselines/episodes.jsonl"),
        Path("artifacts/warehouse/e09_episodes.parquet"),
    )
    Path("artifacts/e09_baseline_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["paired_tasks"], result["models"])
