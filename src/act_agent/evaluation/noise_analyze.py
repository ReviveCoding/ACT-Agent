"""Seal and analyze the predeclared scripted preference-noise development study."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from act_agent.data.pipeline import sha256
from act_agent.evaluation.analyze_adapter import analyze
from act_agent.evaluation.compare_models import compare

METHODS = {
    "dpo": ("B4", 13, "e13_b4-dpo-seed11-scripted_episodes.jsonl"),
    "ipo": ("B5", 13, "e13_b5-ipo-seed11-scripted_episodes.jsonl"),
    "robust_dpo": ("B6", 13, "e13_b6-robust-dpo-seed11-scripted_episodes.jsonl"),
    "act_po": ("M0", 15, "e15_m0-act-po-seed11-scripted_episodes.jsonl"),
}


def seal_and_analyze(root: Path, scratch: Path) -> dict[str, Any]:
    plan = json.loads((root / "artifacts/preference_noise_evaluation_plan.json").read_text())
    if plan["task_count"] != 24 or plan["protected_outcome_access"] != 0:
        raise ValueError("noise evaluation plan identity invalid")
    for relative, digest in plan["source_sha256"].items():
        if sha256(root / relative) != digest:
            raise ValueError(f"noise evaluation source changed: {relative}")
    baseline = root / "artifacts/warehouse/e09_episodes.parquet"
    rows: list[dict[str, Any]] = []
    for rate in (5, 10, 20):
        for method, (label, stage, base_name) in METHODS.items():
            run_id = f"noise{rate:02d}-{method}"
            prefix = root / "artifacts" / f"e{stage:02d}_{run_id}"
            manifest = json.loads(
                prefix.with_name(prefix.name + "_rollout_manifest.json").read_text()
            )
            receipt = json.loads(
                (
                    root
                    / "artifacts/training"
                    / f"{method}-seed11-steps3-pairs64-noise{rate:02d}.json"
                ).read_text()
            )
            if (
                manifest["count"] != 24
                or manifest["models"] != [label]
                or manifest["run_id"] != run_id
                or manifest["adapter_files_sha256"] != receipt["adapter_files_sha256"]
            ):
                raise ValueError(f"noisy rollout identity mismatch: {run_id}")
            source_dir = scratch / "rollouts" / run_id
            canonical: dict[str, Path] = {}
            for kind in ("episodes", "traces"):
                source = source_dir / f"{kind}.jsonl"
                records = [json.loads(line) for line in source.read_text().splitlines() if line]
                if len(records) != 24 or {row["task_id"] for row in records} != set(
                    plan["task_ids"]
                ):
                    raise ValueError(f"incomplete noisy {kind} log: {run_id}")
                if len({(row["model"], row["task_id"]) for row in records}) != 24:
                    raise ValueError(f"duplicate noisy {kind} log: {run_id}")
                target = prefix.with_name(prefix.name + f"_{kind}.jsonl")
                if target.exists() and sha256(target) != sha256(source):
                    raise ValueError(f"canonical noisy log changed: {target}")
                shutil.copyfile(source, target)
                canonical[kind] = target
            summary = analyze(
                base_path=baseline,
                adapter_path=canonical["episodes"],
                model_label=label,
                output_path=root / "artifacts/warehouse" / f"e23_{run_id}_development.parquet",
            )
            baseline_episodes = root / "artifacts" / base_name
            paired = compare(baseline_episodes, canonical["episodes"])
            summary_path = root / "artifacts" / f"e23_{run_id}_summary.json"
            paired_path = root / "artifacts" / f"e23_{run_id}_vs0_comparison.json"
            summary_path.write_text(json.dumps(summary, indent=2) + "\n")
            paired_path.write_text(json.dumps(paired, indent=2) + "\n")
            rows.append(
                {
                    "rate_percent": rate,
                    "method": method,
                    "model": label,
                    "run_id": run_id,
                    "completion": summary["successes"],
                    "safe_completion": summary["safe_successes"],
                    "process_compliance": summary["process_compliant"],
                    "critical_flags": summary["critical_violations"],
                    "completion_vs_zero": paired["metrics"]["completion"],
                    "critical_vs_zero": paired["metrics"]["critical_process_flag"],
                    "episodes_sha256": sha256(canonical["episodes"]),
                    "traces_sha256": sha256(canonical["traces"]),
                    "summary_sha256": sha256(summary_path),
                    "paired_sha256": sha256(paired_path),
                }
            )
    result = {
        "timestamp": datetime.now(UTC).isoformat(),
        "protocol": plan["protocol"],
        "status": "EXPLORATORY_DEVELOPMENT_COMPLETE",
        "training_matrix_sha256": sha256(root / "artifacts/preference_noise_training_audit.json"),
        "evaluation_plan_sha256": sha256(root / "artifacts/preference_noise_evaluation_plan.json"),
        "rows": rows,
        "limitations": [
            "E07 task mechanics/oracle REVIEW",
            "scripted preference pairs only; on-policy ACT-PO absent",
            "24 tasks cannot establish rare-event safety robustness",
        ],
        "protected_outcome_access": 0,
    }
    output = root / "artifacts/preference_noise_development_summary.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    zero_reference = ", ".join(
        f"{('ACT weighted pilot' if method == 'act_po' else method)} "
        f"{round(next(row for row in rows if row['method'] == method)['completion_vs_zero']['baseline_rate'] * 24)}/24"
        for method in METHODS
    )
    lines = [
        "# Preference-noise development study",
        "",
        (
            "Sixteen CUDA training pilots used the same 64 scripted pairs with exact predeclared label flips. "
            "Twelve noisy adapters were evaluated on the same 24 synthetic development tasks as their 0% counterparts."
        ),
        "",
        f"Zero-flip completion reference: {zero_reference}.",
        "",
        "| Method | Flip rate | Complete | Safe complete | Process compliant | Critical flags | Difference vs 0% (95% clustered interval) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        comparison = row["completion_vs_zero"]
        display_method = "ACT weighted pilot" if row["method"] == "act_po" else row["method"]
        lines.append(
            f"| {display_method} | {row['rate_percent']}% | {row['completion']}/24 | "
            f"{row['safe_completion']}/24 | {row['process_compliance']}/24 | "
            f"{row['critical_flags']}/24 | {100 * comparison['difference']:+.1f} pp "
            f"[{100 * comparison['ci_low']:+.1f}, {100 * comparison['ci_high']:+.1f}] |"
        )
    lines += [
        "",
        (
            "These are exploratory synthetic diagnostics. The task oracle and ACT-PO hard-negative source are unqualified; "
            "small differences and zero observed critical flags in some runs do not establish method robustness or safety non-inferiority."
        ),
        "",
        (
            "Canonical inputs, exact flips, training receipts, adapter hashes, episode logs, and paired results are in `artifacts/`. "
            "No protected outcomes were accessed."
        ),
        "",
    ]
    (root / "reports/preference_noise_report.md").write_text("\n".join(lines))
    return result


if __name__ == "__main__":
    print(seal_and_analyze(Path.cwd(), Path("/home/bjw-0/.cache/act-agent-v1"))["status"])
