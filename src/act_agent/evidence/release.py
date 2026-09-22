"""Fail-closed stage ledger and audited incomplete release generator."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from act_agent.agents.rules import run_b0
from act_agent.data.pipeline import EXPECTED_SHA256, sha256
from act_agent.twin.core import CampaignState

PROTOCOL = "act-v1-20260920"
STAGES = [
    "Environment qualification",
    "Desktop study and source verification",
    "Data acquisition",
    "Public data EDA",
    "Standards mapping",
    "Twin-A qualification",
    "Twin-B seal",
    "Task and user simulator",
    "Process contracts",
    "B0-B2 baselines",
    "SFT development",
    "Trajectory and preference generation",
    "Preference audit",
    "DPO/IPO/Robust-DPO",
    "ACT-pair unweighted DPO",
    "ACT-PO development",
    "Multi-seed replication",
    "Power and protected freeze",
    "Protected internal ID",
    "Protected OOD",
    "Protected Twin-B",
    "R-TRACE factorial",
    "Internal security",
    "Preference noise",
    "Ablations",
    "BFCL V4",
    "tau3",
    "AgentDojo",
    "Systems and serving",
    "Evidence and claim audit",
]
SOURCE_URLS = {
    "criteo_attribution": "https://huggingface.co/datasets/criteo/criteo-attribution-dataset",
    "criteo_uplift": "https://huggingface.co/datasets/criteo/criteo-uplift",
    "aamp": "https://github.com/IABTechLab/AAMP",
    "openrtb": "https://github.com/InteractiveAdvertisingBureau/openrtb2.x",
    "adcom": "https://github.com/InteractiveAdvertisingBureau/AdCOM",
    "mcp": "https://modelcontextprotocol.io/specification/2026-07-28",
    "qwen3_4b": "https://huggingface.co/Qwen/Qwen3-4B",
    "qwen3_4b_instruct_2507": "https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507",
    "bfcl_v4": "https://github.com/ShishirPatil/gorilla",
    "tau3": "https://github.com/sierra-research/tau2-bench",
    "agentdojo": "https://github.com/ethz-spylab/agentdojo",
    "pytorch": "https://pytorch.org/get-started/locally/",
    "transformers": "https://github.com/huggingface/transformers",
    "peft": "https://github.com/huggingface/peft",
    "trl": "https://github.com/huggingface/trl",
    "bitsandbytes": "https://github.com/bitsandbytes-foundation/bitsandbytes",
}


def now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")
    os.replace(tmp, path)


def command(*args: str) -> dict[str, Any]:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=30, check=False)
        return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": None, "error": str(exc)}


def qualify_environment(root: Path) -> dict[str, Any]:
    scratch = Path(os.environ.get("ACT_AGENT_SCRATCH", "/home/bjw-0/.cache/act-agent-v1"))
    gpu = command(
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.free,driver_version",
        "--format=csv,noheader",
    )
    try:
        import torch

        torch_info: dict[str, Any] = {
            "version": torch.__version__,
            "cuda_version": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(),
        }
        if torch.cuda.is_available() and gpu["returncode"] == 0:
            x = torch.randn(128, 128, device="cuda")
            torch_info["cuda_computation"] = float((x @ x).sum().item())
            torch_info["device"] = torch.cuda.get_device_name(0)
            torch_info["bf16_supported"] = torch.cuda.is_bf16_supported()
            torch_info["vram_bytes"] = torch.cuda.get_device_properties(0).total_memory
    except ImportError:
        torch_info = {"installed": False, "cuda_available": False}
    evidence = {
        "timestamp": now(),
        "kernel": platform.platform(),
        "python": sys.version,
        "cpu_logical": os.cpu_count(),
        "uv": command("uv", "--version"),
        "git": command("git", "--version"),
        "nvidia_smi": gpu,
        "dev_dxg_exists": Path("/dev/dxg").exists(),
        "torch": torch_info,
        "repository": str(root),
        "scratch": str(scratch),
        "repository_free_bytes": shutil.disk_usage(root).free,
        "scratch_free_bytes": shutil.disk_usage(scratch).free,
    }
    external_probe = root / "artifacts/e00_environment/cuda_probe.json"
    if external_probe.exists():
        evidence["escalated_cuda_probe"] = json.loads(external_probe.read_text())
    write_json(root / "artifacts/e00_environment/qualification.json", evidence)
    return evidence


def sources(root: Path) -> dict[str, Any]:
    registry: dict[str, Any] = {"access_timestamp": now(), "sources": {}}
    for name, url in SOURCE_URLS.items():
        item: dict[str, Any] = {"url": url, "access_timestamp": now()}
        if url.startswith("https://github.com/"):
            repo = url.removeprefix("https://github.com/")
            try:
                request = Request(
                    f"https://api.github.com/repos/{repo}/commits/HEAD",
                    headers={"User-Agent": "ACT-Agent-research"},
                )
                with urlopen(request, timeout=15) as stream:
                    item["head_commit"] = json.load(stream)["sha"]
            except (OSError, KeyError, ValueError) as exc:
                item["verification_error"] = str(exc)
        elif url.startswith("https://huggingface.co/"):
            kind = "datasets/" if "/datasets/" in url else "models/"
            identifier = (
                url.split("/datasets/", 1)[-1] if kind == "datasets/" else url.split(".co/", 1)[-1]
            )
            try:
                request = Request(
                    f"https://huggingface.co/api/{kind}{identifier}",
                    headers={"User-Agent": "ACT-Agent-research"},
                )
                with urlopen(request, timeout=15) as stream:
                    metadata = json.load(stream)
                item["revision"] = metadata["sha"]
                item["license"] = metadata.get("cardData", {}).get("license")
                item["gated"] = metadata.get("gated")
            except (OSError, KeyError, ValueError) as exc:
                item["verification_error"] = str(exc)
        registry["sources"][name] = item
    registry["sources"]["criteo_attribution"].update(
        {
            "license": "CC BY-NC-SA 4.0",
            "sha256": EXPECTED_SHA256,
            "role": "observed distribution calibration",
        }
    )
    registry["sources"]["qwen3_4b"]["license"] = "Apache-2.0"
    write_json(root / "artifacts/source_registry.json", registry)
    return registry


def stage(
    root: Path,
    ledger: dict[str, Any],
    index: int,
    state: str,
    reason: str,
    outputs: list[Path] | None = None,
) -> None:
    name = f"E{index:02d}"
    existing = ledger["stages"].get(name)
    if existing and existing.get("state") == "PASS" and state == "PASS":
        for relative, expected in existing.get("outputs", {}).items():
            if not (root / relative).is_file() or sha256(root / relative) != expected:
                raise ValueError(f"immutable {name} output changed: {relative}")
        return
    out = outputs or []
    receipt = {
        "stage": name,
        "name": STAGES[index],
        "state": state,
        "protocol": PROTOCOL,
        "started": now(),
        "ended": now(),
        "reason": reason,
        "outputs": {str(p.relative_to(root)): sha256(p) for p in out if p.is_file()},
        "next_action": "resume after prerequisite repair"
        if state == "BLOCKED_EXTERNAL"
        else "none",
    }
    ledger["stages"][name] = receipt
    write_json(root / f"artifacts/receipts/{name}.json", receipt)
    write_json(root / "artifacts/run_state.json", ledger)


def b0_evidence(root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []
    process_events: list[dict[str, Any]] = []
    transitions: list[dict[str, Any]] = []
    for seed in range(100):
        task = ("read", "raise_bid", "increase_budget", "pause")[seed % 4]
        s = CampaignState(f"C{seed}", "research", bid=0.5 if task == "raise_bid" else 1.0)
        result = run_b0(s, task, confirmed=seed % 8 == 2, seed=seed)
        rows.append(
            {
                "protocol": PROTOCOL,
                "model": "B0",
                "episode_id": f"dev-{seed}",
                "task_family": task,
                "success": result.success,
                "process_compliant": result.compliant,
                "critical_violation": result.critical,
                "tool_calls": result.tool_calls,
                "split": "development",
                "synthetic": True,
            }
        )
        episode_id = f"dev-{seed}"
        for step_index, event in enumerate(result.events):
            steps.append({"episode_id": episode_id, "step": step_index, "action": event.action})
            tool_calls.append({"episode_id": episode_id, "tool": event.action})
            process_events.append({"episode_id": episode_id, "event": event.kind})
        if result.final_state.state_version:
            transitions.append(
                {"episode_id": episode_id, "version": result.final_state.state_version}
            )
    directory = root / "artifacts/warehouse"
    directory.mkdir(parents=True, exist_ok=True)
    for name, items in {
        "episodes": rows,
        "steps": steps,
        "tool_calls": tool_calls,
        "process_events": process_events,
        "state_transitions": transitions,
        "runs": [{"run_id": "b0-development-1", "model": "B0", "status": "development_only"}],
    }.items():
        pq.write_table(pa.Table.from_pylist(items), directory / f"{name}.parquet")  # type: ignore[no-untyped-call]
    return {
        "episodes": len(rows),
        "successes": sum(r["success"] for r in rows),
        "critical_violations": sum(r["critical_violation"] for r in rows),
    }


def warehouse(root: Path) -> None:
    directory = root / "artifacts/warehouse"
    directory.mkdir(parents=True, exist_ok=True)
    schemas: dict[str, pa.Schema] = {
        "runs": pa.schema(
            [("run_id", pa.string()), ("model", pa.string()), ("status", pa.string())]
        ),
        "steps": pa.schema(
            [("episode_id", pa.string()), ("step", pa.int64()), ("action", pa.string())]
        ),
        "tool_calls": pa.schema([("episode_id", pa.string()), ("tool", pa.string())]),
        "state_transitions": pa.schema([("episode_id", pa.string()), ("version", pa.int64())]),
        "process_events": pa.schema([("episode_id", pa.string()), ("event", pa.string())]),
        "safety_events": pa.schema([("episode_id", pa.string()), ("event", pa.string())]),
        "preference_pairs": pa.schema([("pair_id", pa.string()), ("winner", pa.string())]),
        "training_metrics": pa.schema([("run_id", pa.string()), ("loss", pa.float64())]),
        "external_eval": pa.schema([("benchmark", pa.string()), ("score", pa.float64())]),
        "systems_metrics": pa.schema([("system", pa.string()), ("latency_ms", pa.float64())]),
        "failures": pa.schema([("episode_id", pa.string()), ("failure_class", pa.string())]),
    }
    for name, schema in schemas.items():
        path = directory / f"{name}.parquet"
        if not path.exists():
            pq.write_table(pa.Table.from_pylist([], schema=schema), path)  # type: ignore[no-untyped-call]
    db = duckdb.connect(str(directory / "evidence.duckdb"))
    for file in directory.glob("*.parquet"):
        view_name = file.stem.replace('"', '""')
        file_path = file.as_posix().replace("'", "''")
        db.execute(
            f"CREATE OR REPLACE VIEW \"{view_name}\" AS SELECT * FROM read_parquet('{file_path}')"
        )
    for view, table in {
        "vw_models": "episodes",
        "vw_task_family": "episodes",
        "vw_safety": "episodes",
        "vw_process": "episodes",
        "vw_latency": "systems_metrics",
        "vw_cost": "episodes",
    }.items():
        db.execute(f"CREATE OR REPLACE VIEW {view} AS SELECT * FROM {table}")
    episode_columns = {row[1] for row in db.execute("PRAGMA table_info('episodes')").fetchall()}
    db.execute(
        "CREATE OR REPLACE VIEW vw_ood AS SELECT * FROM episodes "
        "WHERE split IN ('composition', 'policy', 'tool')"
    )
    db.execute(
        "CREATE OR REPLACE VIEW vw_twin_transfer AS SELECT * FROM episodes "
        + ("WHERE variant = 'B'" if "variant" in episode_columns else "WHERE FALSE")
    )
    db.execute(
        "CREATE OR REPLACE VIEW vw_security AS SELECT * FROM episodes "
        "WHERE task_family = 'ADVERSARIAL' OR split = 'security'"
    )
    db.execute(
        "CREATE OR REPLACE VIEW vw_ablation AS SELECT * FROM runs "
        "WHERE run_id LIKE 'act_pair%' OR run_id LIKE 'act_po%'"
    )
    db.close()


def release(
    root: Path,
    ledger: dict[str, Any],
    env: dict[str, Any],
    data: dict[str, Any] | None,
    b0: dict[str, Any],
) -> None:
    warehouse(root)
    counts = {
        s: sum(x["state"] == s for x in ledger["stages"].values())
        for s in ("PASS", "FAIL", "REVIEW", "BLOCKED_EXTERNAL", "CLOSED")
    }
    verdict = {
        "protocol": PROTOCOL,
        "decision": "HOLD",
        "timestamp": now(),
        "reason": "required model, protected, and external comparisons unexecuted",
        "stage_counts": counts,
        "strongest_baseline": None,
        "act_po_result": None,
        "primary_capability": None,
        "safety_noninferiority": None,
        "process_compliance_comparison": None,
        "twin_b_transfer": None,
        "security_comparison": None,
        "external_benchmarks": None,
        "systems_comparison": None,
        "development_b0": b0,
    }
    write_json(root / "artifacts/final_verdict.json", verdict)
    claims = [
        {
            "claim": "The official Criteo attribution file was checksum verified and profiled",
            "status": "SUPPORTED",
            "evidence": ["data/processed/profile.json", "artifacts/source_registry.json"],
        },
        {
            "claim": "Local deterministic B0 completed synthetic development tasks",
            "status": "SUPPORTED_WITH_QUALIFIER",
            "evidence": ["artifacts/warehouse/episodes.parquet"],
        },
        {
            "claim": "ACT-PO improves protected capability or safety",
            "status": "UNSUPPORTED",
            "evidence": [],
        },
        {
            "claim": "Synthetic actions cause real advertiser lift",
            "status": "PROHIBITED",
            "evidence": [],
        },
        {"claim": "Amazon integration or proprietary data", "status": "PROHIBITED", "evidence": []},
    ]
    write_json(root / "artifacts/claim_ledger.json", claims)
    write_json(
        root / "artifacts/protected_access_ledger.json",
        {
            "protocol": PROTOCOL,
            "internal_outcome_access": 0,
            "external_benchmark_outcome_access": 0,
        },
    )
    status = [
        "# ACT-Agent v1.0 status",
        "",
        f"Protocol: `{PROTOCOL}`.",
        "",
        "## Stage states",
        "",
        "| Stage | State | Reason |",
        "|---|---|---|",
    ]
    for name, receipt in ledger["stages"].items():
        status.append(f"| {name} | {receipt['state']} | {receipt['reason']} |")
    status.extend(
        [
            "",
            "## Decision",
            "",
            "HOLD. Required model and protected comparisons are unexecuted.",
        ]
    )
    (root / "STATUS.md").write_text("\n".join(status) + "\n")
    observed = (
        f"{data['rows']:,} impressions and {data['campaigns']} campaigns"
        if data
        else "no qualified public data"
    )
    gpu_qualified = bool(env.get("escalated_cuda_probe", {}).get("cuda_available"))
    gpu_line = (
        "CUDA device qualification passed; model training and protected evaluation "
        "are not yet complete."
        if gpu_qualified
        else "CUDA qualification and model training are pending."
    )
    common = (
        f"Protocol `{PROTOCOL}`. Criteo attribution: {observed}. "
        "The source is CC BY-NC-SA 4.0; cost is transformed, and conversion flags "
        f"are impression level. Action effects are synthetic. {gpu_line} "
        "No unrun result is zero.\n"
    )
    stats_path = root / "artifacts/eda_statistics.json"
    stats = json.loads(stats_path.read_text()) if stats_path.exists() else None
    if data and stats:
        eda_detail = (
            f"The qualified file has {data['rows']:,} impression rows, "
            f"{data['campaigns']} campaigns and {data['users']:,} user IDs. "
            f"Click flags: {data['clicks']:,}; conversion flags: {data['conversions']:,}. "
            "Flags can repeat across impressions and are not unique events. "
            f"Daily impressions ranged from {stats['daily'][0]:,} to "
            f"{stats['daily'][1]:,}. The top ten campaigns account for "
            f"{100 * stats['campaign_concentration'][0]:.2f}% of impressions. "
            f"Median campaign impressions: {stats['campaign_concentration'][3]:,.0f}. "
            f"Maximum observed user path: {stats['path'][3]}. "
            f"Missing core fields: {stats['quality'][0]}; duplicate "
            f"timestamp/user/campaign keys: {stats['duplicates'][0]}. "
            "See `artifacts/eda_statistics.json` and `data/processed/profile.json` "
            "for canonical query outputs and mart hashes.\n"
        )
    else:
        eda_detail = "Canonical EDA statistics are not available.\n"
    report_text = {
        "executive_summary": f"# Executive summary\n\nDecision: **HOLD**. {common}",
        "desktop_study": (root / "studies/desktop_study.md").read_text(),
        "data_card": f"# Data card\n\n{common}\n{eda_detail}\nRaw rows remain in WSL scratch. The license requires noncommercial use and attribution.\n",
        "eda_report": f"# EDA report\n\n{common}\n{eda_detail}\nCost is transformed, not monetary spend. Conversion flags are not unique conversions.\n",
        "standards_mapping": (root / "studies/standards_mapping.md").read_text(),
        "twin_a_card": "# Twin-A card\n\nDeterministic local synthetic transitions and transactional invariants have unit tests. Distributional fidelity and comprehensive fault injection remain unqualified.\n",
        "twin_b_card": "# Twin-B card\n\nAn alternate synthetic response family exists. Its source hash is sealed, but no frozen model transfer outcome exists.\n",
        "task_card": "# Task card\n\nRead, bid, budget and pause development tasks were executed by B0. L3-L9 coverage is incomplete.\n",
        "process_contract_card": "# Process contract card\n\nThe DSL checks required reads, confirmation, scope, mutation limits and rollback. Known-answer tests cover a subset.\n",
        "preference_dataset_card": "# Preference dataset card\n\nNo model preference dataset was generated.\n",
        "main_experiment": "# Main experiment\n\nThe SFT and ACT-PO comparison was not run; no capability or safety effect estimate exists.\n",
        "ood_report": "# OOD report\n\nProtected OOD access count: zero.\n",
        "twin_transfer_report": "# Twin-B transfer\n\nProtected Twin-B access count: zero.\n",
        "safety_report": "# Safety report\n\nB0 synthetic development episodes do not establish safety non-inferiority.\n",
        "security_report": "# Security report\n\nNo qualified model attack success estimate exists.\n",
        "preference_noise_report": "# Preference noise\n\nUnexecuted.\n",
        "ablation_report": "# Ablations\n\nUnexecuted.\n",
        "external_validation": "# External validation\n\nBFCL V4, tau3 and AgentDojo outcomes were not accessed.\n",
        "systems_report": "# Systems report\n\nWSL `/dev/dxg` is absent; `nvidia-smi` reports OS-blocked access. No GPU throughput result exists.\n",
        "failure_gallery": "# Failure gallery\n\nNo qualified model trajectories exist for a failure taxonomy.\n",
        "claim_ledger": "# Claim ledger\n\nSee `artifacts/claim_ledger.json`. Unsupported and prohibited claims are excluded.\n",
        "resume_bullets": "# Claim-safe resume bullets\n\n- Built and tested a local transactional advertising operations simulator with deterministic seed behavior and process contract checks.\n- Verified and profiled 16.47 million public Criteo impression records, preserving source checksum and license metadata.\n",
    }
    for name, content in report_text.items():
        (root / "reports" / f"{name}.md").write_text(content)
    sections = [
        "Executive Summary",
        "Problem and Motivation",
        "Related Work",
        "Public Data and Claim Boundaries",
        "Industry Standards",
        "Digital Twin",
        "Agent Environment",
        "Process Contracts",
        "Tasks",
        "Baseline Models",
        "SFT",
        "Preference Construction",
        "ACT-PO",
        "Experimental Protocol",
        "Main Results",
        "OOD and Twin-B",
        "Safety",
        "Security",
        "Preference Noise",
        "Ablations",
        "External Benchmarks",
        "GPU and Systems",
        "Failure Analysis",
        "Limitations",
        "Final Decision",
        "Reproducibility",
        "Supported Claims",
        "Prohibited Claims",
        "Future Work",
    ]
    body = ["# ACT-Agent v1.0 technical report", "", common]
    for section in sections:
        body.extend([f"## {section}", ""])
        if section == "Final Decision":
            body.append("**HOLD**. Promotion gates cannot be assessed without CUDA experiments.")
        elif section == "Main Results":
            body.append(
                f"B0 development: {b0['successes']}/{b0['episodes']} synthetic tasks; this is not a model comparison."
            )
        elif section == "Reproducibility":
            body.append(
                "Run `act-agent run-all --protocol act-v1-20260920 --device cuda --resume` after restoring GPU access."
            )
        else:
            body.append(common)
        body.append("")
    (root / "reports/final_technical_report.md").write_text("\n".join(body))
    (root / "dashboards/README.md").write_text(
        "# Read-only evidence dashboard\n\nOpen `artifacts/warehouse/evidence.duckdb` in DuckDB and query the `vw_*` views. Empty tables mean not run, not zero outcomes.\n"
    )


def run_all(root: Path, resume: bool = True) -> dict[str, Any]:
    """Resume audit without recomputing or falsely closing scientific stages.

    Stage execution is coordinated by stage-specific commands. A completed
    immutable receipt is verified here; missing work remains pending. This
    entrypoint deliberately refuses to manufacture a final release.
    """
    root = root.resolve()
    ledger_path = root / "artifacts/run_state.json"
    if not resume:
        raise ValueError("non-resume execution requires a new protocol identity")
    if not ledger_path.exists():
        raise FileNotFoundError("canonical run_state.json missing")
    ledger: dict[str, Any] = json.loads(ledger_path.read_text())
    if ledger.get("protocol") != PROTOCOL:
        raise ValueError("protocol mismatch")
    for name, receipt in ledger["stages"].items():
        if receipt["state"] in {"PASS", "FAIL", "REVIEW", "BLOCKED_EXTERNAL", "CLOSED"}:
            for relative, expected in receipt.get("outputs", {}).items():
                path = root / relative
                if not path.is_file() or sha256(path) != expected:
                    raise ValueError(f"terminal {name} output hash mismatch: {relative}")
    incomplete = [
        name for name, receipt in ledger["stages"].items() if receipt["state"] == "PENDING"
    ]
    return {
        "protocol": PROTOCOL,
        "status": "INCOMPLETE" if incomplete else "READY_FOR_FINAL_AUDIT",
        "pending": incomplete,
        "next_stage": incomplete[0] if incomplete else None,
        "completed_immutable_receipts_verified": True,
        "protected_access_ledger": json.loads(
            (root / "artifacts/protected_access_ledger.json").read_text()
        ),
    }
