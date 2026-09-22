"""Rebuild development warehouse facts from immutable receipts and episode logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from act_agent.evidence.release import PROTOCOL, warehouse

FAILURE_CODES = {
    "missing_prewrite_evidence": "F04_missing_evidence",
    "missing_required_evidence": "F04_missing_evidence",
    "missing_confirmation": "F05_missed_confirmation",
    "missing_permission": "F06_policy_violation_attempt",
    "unauthorized_mutation": "F06_policy_violation_attempt",
    "scope_violation": "F06_policy_violation_attempt",
    "max_mutations": "F07_excessive_mutation",
    "rollback_required": "F08_recovery_failure",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def _write(path: Path, rows: list[dict[str, Any]], schema: pa.Schema | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if schema is None and rows:
        keys = sorted({key for row in rows for key in row})
        rows = [{key: row.get(key) for key in keys} for row in rows]
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, path)  # type: ignore[no-untyped-call]


def rebuild_development(root: Path, scratch: Path) -> dict[str, int]:
    """Merge B0, paired B1/B2, and canonical completed adapter rollouts.

    Partial model tasks are excluded until all three baselines are present.
    Empty tables retain their declared schemas rather than implying zero outcomes.
    """
    directory = root / "artifacts/warehouse"
    b0 = pq.read_table(directory / "b0_development.parquet").to_pylist()  # type: ignore[no-untyped-call]
    canonical_episodes = root / "artifacts/e09_episodes.jsonl"
    logs = _read_jsonl(
        canonical_episodes
        if canonical_episodes.exists()
        else scratch / "e09_baselines/episodes.jsonl"
    )
    paired: dict[str, dict[str, dict[str, Any]]] = {}
    for item in logs:
        task_models = paired.setdefault(item["task_id"], {})
        if item["model"] in task_models:
            raise ValueError("duplicate model-task episode in scratch log")
        task_models[item["model"]] = item
    complete = {task for task, models in paired.items() if set(models) == {"B0", "B1", "B2"}}
    canonical_traces = root / "artifacts/e09_traces.jsonl"
    trace_rows = _read_jsonl(
        canonical_traces if canonical_traces.exists() else scratch / "e09_baselines/traces.jsonl"
    )
    trace_keys = [(record["model"], record["task_id"]) for record in trace_rows]
    if len(trace_keys) != len(set(trace_keys)):
        raise ValueError("duplicate model-task trace in scratch log")
    expected_traces = {(model, task) for task in complete for model in ("B0", "B1", "B2")}
    if not expected_traces <= set(trace_keys):
        raise ValueError("completed episode is missing its paired trace")
    episodes: list[dict[str, Any]] = []
    for item in b0:
        row = dict(item)
        row["protocol"] = PROTOCOL
        row["episode_id"] = f"B0:{item['task_id']}"
        row["generated_tokens"] = 0
        row["generation_seconds"] = 0.0
        episodes.append(row)
    for task in sorted(complete):
        for model in ("B1", "B2"):
            row = dict(paired[task][model])
            row["protocol"] = PROTOCOL
            row["episode_id"] = f"{model}:{task}"
            episodes.append(row)
    adapter_traces: list[dict[str, Any]] = []
    adapter_runs: list[dict[str, str]] = []
    for manifest_path in sorted((root / "artifacts").glob("e*_rollout_manifest.json")):
        manifest = json.loads(manifest_path.read_text())
        models = manifest.get("models", [])
        if len(models) != 1 or models[0] not in {"B3", "B4", "B5", "B6", "B7", "M0"}:
            continue
        run_id = manifest.get("run_id")
        if not isinstance(run_id, str):
            raise TypeError("adapter rollout manifest lacks a run ID")
        prefix = manifest_path.with_name(manifest_path.name.removesuffix("_rollout_manifest.json"))
        episode_path = prefix.with_name(prefix.name + "_episodes.jsonl")
        trace_path = prefix.with_name(prefix.name + "_traces.jsonl")
        if not episode_path.is_file() or not trace_path.is_file():
            continue
        adapter_rows = _read_jsonl(episode_path)
        traces_for_run = _read_jsonl(trace_path)
        episode_keys = {(row["model"], row["task_id"]) for row in adapter_rows}
        adapter_trace_keys = {(row["model"], row["task_id"]) for row in traces_for_run}
        if len(episode_keys) != len(adapter_rows) or episode_keys != adapter_trace_keys:
            raise ValueError(f"adapter episode/trace identity mismatch: {run_id}")
        if len(adapter_rows) != manifest["count"]:
            raise ValueError(f"adapter rollout count mismatch: {run_id}")
        for row in adapter_rows:
            record = dict(row)
            record["protocol"] = PROTOCOL
            record["episode_id"] = f"{run_id}:{row['task_id']}"
            episodes.append(record)
        for row in traces_for_run:
            adapter_traces.append({**row, "episode_id": f"{run_id}:{row['task_id']}"})
        adapter_runs.append(
            {
                "run_id": run_id,
                "model": models[0],
                "status": "COMPLETE",
                "role": "development_evaluation",
            }
        )
    _write(directory / "episodes.parquet", episodes)
    runs = [
        {
            "run_id": f"B0-development-{len(b0)}",
            "model": "B0",
            "status": "COMPLETE",
            "role": "development_evaluation",
        }
    ]
    runs.extend(
        {
            "run_id": f"{model}-development-{len(complete)}",
            "model": model,
            "status": "COMPLETE",
            "role": "development_evaluation",
        }
        for model in ("B1", "B2")
    )
    runs.extend(adapter_runs)
    _write(
        directory / "runs.parquet",
        runs,
        pa.schema(
            [
                ("run_id", pa.string()),
                ("model", pa.string()),
                ("status", pa.string()),
                ("role", pa.string()),
            ]
        ),
    )
    process_events: list[dict[str, str]] = []
    safety_events: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
    for row in episodes:
        for violation in row.get("violations") or []:
            process_events.append({"episode_id": row["episode_id"], "event": violation})
            failures.append(
                {
                    "episode_id": row["episode_id"],
                    "failure_class": FAILURE_CODES.get(violation, "UNCLASSIFIED_PROCESS"),
                }
            )
        if row["critical_violation"]:
            safety_events.append(
                {"episode_id": row["episode_id"], "event": "critical_process_violation"}
            )
    _write(
        directory / "process_events.parquet",
        process_events,
        pa.schema([("episode_id", pa.string()), ("event", pa.string())]),
    )
    _write(
        directory / "safety_events.parquet",
        safety_events,
        pa.schema([("episode_id", pa.string()), ("event", pa.string())]),
    )
    _write(
        directory / "failures.parquet",
        failures,
        pa.schema([("episode_id", pa.string()), ("failure_class", pa.string())]),
    )
    steps: list[dict[str, Any]] = []
    tools: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    for record in [*trace_rows, *adapter_traces]:
        key = (record["model"], record["task_id"])
        if record["task_id"] not in complete:
            continue
        episode_id = record.get("episode_id", f"{key[0]}:{key[1]}")
        for index, event in enumerate(record["trace"]):
            action = event.get("tool", "assistant" if "assistant" in event else "event")
            steps.append({"episode_id": episode_id, "step": index, "action": action})
            if "tool" in event:
                tools.append({"episode_id": episode_id, "tool": event["tool"]})
        model_row = (
            next(row for row in episodes if row["episode_id"] == episode_id)
            if "episode_id" in record
            else paired[record["task_id"]][record["model"]]
        )
        transitions.append({"episode_id": episode_id, "version": model_row["final_state_version"]})
    _write(
        directory / "steps.parquet",
        steps,
        pa.schema([("episode_id", pa.string()), ("step", pa.int64()), ("action", pa.string())]),
    )
    _write(
        directory / "tool_calls.parquet",
        tools,
        pa.schema([("episode_id", pa.string()), ("tool", pa.string())]),
    )
    _write(
        directory / "state_transitions.parquet",
        transitions,
        pa.schema([("episode_id", pa.string()), ("version", pa.int64())]),
    )
    warehouse(root)
    return {
        "b0_episodes": len(b0),
        "paired_model_tasks": len(complete),
        "episodes": len(episodes),
        "steps": len(steps),
        "tool_calls": len(tools),
        "state_transitions": len(transitions),
        "process_events": len(process_events),
        "safety_events": len(safety_events),
        "classified_failures": len(failures),
    }


def rebuild_training_systems(root: Path) -> dict[str, int]:
    """Load only completed local training and measured serving receipts."""
    directory = root / "artifacts/warehouse"
    runs_path = directory / "runs.parquet"
    runs = pq.read_table(runs_path).to_pylist() if runs_path.exists() else []  # type: ignore[no-untyped-call]
    runs = [row for row in runs if row.get("role") == "development_evaluation"]
    metrics: list[dict[str, Any]] = []
    completed_training_runs = 0
    for path in sorted((root / "artifacts/training").glob("*.json")):
        receipt = json.loads(path.read_text())
        if receipt.get("status") != "PASS" or not isinstance(receipt.get("losses"), list):
            continue
        completed_training_runs += 1
        run_id = path.stem
        model = "B3" if "mode" not in receipt else str(receipt["mode"])
        role = (
            "engineering_validation"
            if "pilot" in run_id or "validation" in run_id
            else "development_training"
        )
        runs.append({"run_id": run_id, "model": model, "status": "COMPLETE", "role": role})
        for step, loss in enumerate(receipt["losses"], start=1):
            metrics.append(
                {
                    "run_id": run_id,
                    "model": model,
                    "seed": receipt.get("seed"),
                    "step": step,
                    "loss": float(loss),
                    "source_receipt": str(path.relative_to(root)),
                    "role": role,
                }
            )
    _write(
        runs_path,
        runs,
        pa.schema(
            [
                ("run_id", pa.string()),
                ("model", pa.string()),
                ("status", pa.string()),
                ("role", pa.string()),
            ]
        ),
    )
    _write(
        directory / "training_metrics.parquet",
        metrics,
        pa.schema(
            [
                ("run_id", pa.string()),
                ("model", pa.string()),
                ("seed", pa.int64()),
                ("step", pa.int64()),
                ("loss", pa.float64()),
                ("source_receipt", pa.string()),
                ("role", pa.string()),
            ]
        ),
    )
    serving: list[dict[str, Any]] = []
    for path in sorted((root / "artifacts").glob("systems_serving_*.json")):
        receipt = json.loads(path.read_text())
        if receipt.get("status") != "PASS":
            continue
        for index, (seconds, tokens) in enumerate(
            zip(
                receipt["full_generation_seconds"],
                receipt["full_generation_tokens"],
                strict=True,
            )
        ):
            serving.append(
                {
                    "system": path.stem,
                    "repeat": index,
                    "latency_ms": 1000 * float(seconds),
                    "tokens": int(tokens),
                    "peak_reserved_vram_bytes": int(receipt["peak_reserved_vram_bytes"]),
                    "source_receipt": str(path.relative_to(root)),
                }
            )
    _write(
        directory / "systems_metrics.parquet",
        serving,
        pa.schema(
            [
                ("system", pa.string()),
                ("repeat", pa.int64()),
                ("latency_ms", pa.float64()),
                ("tokens", pa.int64()),
                ("peak_reserved_vram_bytes", pa.int64()),
                ("source_receipt", pa.string()),
            ]
        ),
    )
    warehouse(root)
    return {
        "training_runs": completed_training_runs,
        "training_steps": len(metrics),
        "serving_repeats": len(serving),
    }


if __name__ == "__main__":
    root = Path.cwd()
    print(rebuild_development(root, Path("/home/bjw-0/.cache/act-agent-v1")))
    print(rebuild_training_systems(root))
