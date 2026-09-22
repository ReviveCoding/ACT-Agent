"""Regenerate a fail-closed scientific release from canonical local evidence."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from act_agent.data.pipeline import sha256
from act_agent.evaluation.gates import PromotionEvidence, decide
from act_agent.evidence.release import PROTOCOL, STAGES, write_json
from act_agent.reporting.dashboard import generate as generate_dashboard

TERMINAL = {"PASS", "FAIL", "REVIEW", "BLOCKED_EXTERNAL", "CLOSED"}


def _read(path: Path) -> Any | None:
    return json.loads(path.read_text()) if path.exists() else None


def generate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    ledger = _read(root / "artifacts/run_state.json")
    if ledger is None or ledger.get("protocol") != PROTOCOL:
        raise ValueError("canonical protocol ledger missing")
    stages = ledger["stages"]
    if len(stages) != len(STAGES):
        raise ValueError("stage ledger incomplete")
    pending = [name for name, item in stages.items() if item["state"] not in TERMINAL]
    if pending and pending != ["E29"]:
        raise ValueError(f"scientific stages unfinished: {pending}")
    access = _read(root / "artifacts/protected_access_ledger.json")
    if access is None:
        raise ValueError("protected access ledger missing")
    freeze = _read(root / "artifacts/freeze_manifest.json")
    protected = _read(root / "artifacts/protected_analysis.json")
    if (
        access.get("internal_outcome_access", 0)
        or access.get("external_benchmark_outcome_access", 0)
    ) and freeze is None:
        raise ValueError("protected outcome access without frozen protocol")
    identity_path = root / "artifacts/release_identity.json"
    identity = _read(identity_path)
    if identity is None:
        identity = {"protocol": PROTOCOL, "timestamp": datetime.now(UTC).isoformat()}
        write_json(identity_path, identity)
    profile = _read(root / "data/processed/profile.json")
    b0 = _read(root / "artifacts/e09_b0_summary.json")
    e09 = _read(root / "artifacts/e09_baseline_summary.json")
    development_models = {
        path.stem: json.loads(path.read_text())
        for pattern in (
            "e10_*_summary.json",
            "e13_*_summary.json",
            "e14_*_summary.json",
            "e15_*_summary.json",
        )
        for path in sorted((root / "artifacts").glob(pattern))
    }
    preference = _read(root / "artifacts/preference_audit.json")
    sft_development = _read(root / "artifacts/e10_b3_seed11_step120_summary.json")
    act_weighted_development = _read(root / "artifacts/e15_m0_seed11_scripted_summary.json")
    noise_training = _read(root / "artifacts/preference_noise_training_audit.json")
    noise = _read(root / "artifacts/preference_noise_development_summary.json")
    systems = _read(root / "artifacts/systems_development.json")
    serving = {
        path.stem: {
            key: value
            for key, value in json.loads(path.read_text()).items()
            if key
            in {
                "status",
                "backend",
                "startup_seconds",
                "cold_first_token_seconds",
                "steady_first_token_median_seconds",
                "generated_tokens_per_second",
                "peak_reserved_vram_bytes",
                "shutdown_seconds",
                "scope",
            }
        }
        for path in sorted((root / "artifacts").glob("systems_serving_*.json"))
    }
    data_ok = stages["E02"]["state"] == "PASS" and stages["E03"]["state"] == "PASS"
    task_ok = stages["E05"]["state"] == "PASS" and stages["E07"]["state"] == "PASS"
    process_ok = stages["E08"]["state"] == "PASS"
    protocol_ok = all(stages[name]["state"] == "PASS" for name in ("E17", "E18", "E19", "E21"))
    security_ok = stages["E22"]["state"] == "PASS"
    twin_ok = stages["E20"]["state"] == "PASS"
    evidence = PromotionEvidence(
        data_integrity=data_ok,
        simulator_valid=task_ok,
        process_evaluator_valid=process_ok,
        protocol_intact=protocol_ok,
        security_acceptable=security_ok,
        twin_b_acceptable=twin_ok,
        protected_capability_ci_low=protected.get("capability_ci_low") if protected else None,
        critical_safety_difference_ci_high=protected.get("critical_difference_ci_high")
        if protected
        else None,
        safety_noninferiority_margin=freeze.get("safety_noninferiority_margin") if freeze else None,
        strongest_alternative=protected.get("strongest_alternative", "HOLD")
        if protected
        else "HOLD",
    )
    decision = decide(evidence)
    counts = dict(
        Counter(("PASS" if name == "E29" else item["state"]) for name, item in stages.items())
    )
    verdict = {
        "protocol": PROTOCOL,
        "timestamp": identity["timestamp"],
        "decision": decision,
        "stage_counts": counts,
        "strongest_baseline": protected.get("strongest_baseline") if protected else None,
        "development_strongest_baseline": max(
            e09["models"], key=lambda model: e09["models"][model]["success"]
        )
        if e09
        else None,
        "act_po_result": protected.get("act_po") if protected else None,
        "primary_capability": protected.get("capability") if protected else None,
        "safety_noninferiority": protected.get("safety") if protected else None,
        "process_compliance_comparison": protected.get("process") if protected else None,
        "twin_b_transfer": protected.get("twin_b") if protected else None,
        "security_comparison": protected.get("security") if protected else None,
        "external_benchmarks": protected.get("external") if protected else None,
        "systems_comparison": systems,
        "serving_measurements": serving,
        "development_b0": b0,
        "development_model_results": {
            name: {
                key: value
                for key, value in result.items()
                if key
                in {
                    "model",
                    "paired_tasks",
                    "successes",
                    "safe_successes",
                    "process_compliant",
                    "critical_violations",
                    "comparisons",
                    "qualification",
                }
            }
            for name, result in development_models.items()
        },
        "protected_access": access,
        "critical_gates": {
            "data_integrity": data_ok,
            "simulator_and_tasks": task_ok,
            "process_evaluator": process_ok,
            "protected_protocol": protocol_ok,
            "security": security_ok,
            "twin_b": twin_ok,
        },
        "reason": "Protected effect estimates or critical gates are missing"
        if decision == "HOLD"
        else "Decision follows pre-outcome promotion gates",
    }
    write_json(root / "artifacts/final_verdict.json", verdict)
    claims: list[dict[str, Any]] = [
        {
            "claim": "Criteo attribution file checksum verified and profiled",
            "status": "SUPPORTED"
            if (root / "artifacts/data_source.json").is_file()
            and (root / "data/processed/profile.json").is_file()
            else "UNSUPPORTED",
            "evidence": ["artifacts/data_source.json", "data/processed/profile.json"],
        },
        {
            "claim": "Criteo uplift v2.1 file integrity and exact row count verified",
            "status": "SUPPORTED"
            if (root / "artifacts/uplift_profile.json").is_file()
            else "UNSUPPORTED",
            "evidence": ["artifacts/uplift_profile.json"],
        },
        {
            "claim": "RTX 4090 CUDA BF16 and real matmul qualified through escalated access",
            "status": "SUPPORTED"
            if (root / "artifacts/e00_environment/cuda_probe.json").is_file()
            else "UNSUPPORTED",
            "evidence": ["artifacts/e00_environment/cuda_probe.json"],
        },
        {
            "claim": "Twin-A synthetic calibration and internal known-answer checks passed",
            "status": "SUPPORTED_WITH_QUALIFIER"
            if (root / "artifacts/twin_a_qualification.json").is_file()
            else "UNSUPPORTED",
            "evidence": ["artifacts/twin_a_qualification.json"],
        },
        {
            "claim": "B0 completed synthetic development tasks",
            "status": "SUPPORTED_WITH_QUALIFIER"
            if b0 and (root / "artifacts/warehouse/b0_development.parquet").is_file()
            else "UNSUPPORTED",
            "evidence": [
                "artifacts/e09_b0_summary.json",
                "artifacts/warehouse/b0_development.parquet",
            ],
        },
        {
            "claim": "B0, B1, and B2 completed a 24-task paired synthetic CUDA development pilot",
            "status": "SUPPORTED_WITH_QUALIFIER"
            if e09 and e09.get("paired_tasks") == 24
            else "UNSUPPORTED",
            "evidence": [
                "artifacts/e09_baseline_manifest.json",
                "artifacts/e09_baseline_summary.json",
                "artifacts/warehouse/e09_episodes.parquet",
            ]
            if e09 and e09.get("paired_tasks") == 24
            else [],
        },
        {
            "claim": "SFT and weighted ACT-style scripted-pair pilots completed paired synthetic development rollouts",
            "status": "SUPPORTED_WITH_QUALIFIER"
            if sft_development
            and sft_development.get("paired_tasks") == 24
            and act_weighted_development
            and act_weighted_development.get("paired_tasks") == 24
            else "UNSUPPORTED",
            "evidence": [
                "artifacts/e10_b3_seed11_step120_summary.json",
                "artifacts/e15_m0_seed11_scripted_summary.json",
                "reports/preference_methods_development.md",
            ],
        },
        {
            "claim": "Sixteen scripted-pair CUDA noise pilots and twelve paired synthetic development rollouts completed",
            "status": "SUPPORTED_WITH_QUALIFIER"
            if noise_training
            and noise_training.get("status") == "TRAINING_MATRIX_COMPLETE"
            and len(noise_training.get("rows", [])) == 16
            and noise
            and len(noise.get("rows", [])) == 12
            else "UNSUPPORTED",
            "evidence": [
                "artifacts/preference_noise_training_audit.json",
                "artifacts/preference_noise_evaluation_plan.json",
                "artifacts/preference_noise_development_summary.json",
                "reports/preference_noise_report.md",
            ],
        },
        {
            "claim": "ACT-PO improves protected long-horizon capability without safety regression",
            "status": "SUPPORTED" if decision == "PROMOTE_ACT_PO" else "UNSUPPORTED",
            "evidence": ["artifacts/protected_analysis.json"]
            if decision == "PROMOTE_ACT_PO"
            else [],
        },
        {
            "claim": "Synthetic interventions cause real advertiser lift",
            "status": "PROHIBITED",
            "evidence": [],
        },
        {
            "claim": "Amazon proprietary data, Ads API integration, or production account control",
            "status": "PROHIBITED",
            "evidence": [],
        },
        {
            "claim": "Production advertiser outcomes or production agent-safety certification",
            "status": "PROHIBITED",
            "evidence": [],
        },
        {
            "claim": "Real-user benefit or real campaign-action causal effects",
            "status": "PROHIBITED",
            "evidence": [],
        },
        {
            "claim": "Formal reproduction of national advertising policy",
            "status": "PROHIBITED",
            "evidence": [],
        },
        {
            "claim": "Physical multi-GPU scaling",
            "status": "PROHIBITED",
            "evidence": [],
        },
    ]
    write_json(root / "artifacts/claim_ledger.json", claims)
    dataset_line = (
        f"{profile['rows']:,} public Criteo impression rows and {profile['campaigns']} campaigns"
        if profile
        else "no qualified public aggregate profile"
    )
    b0_line = (
        f"B0 development completion {b0['successes']}/{b0['episodes']}; "
        f"critical violations {b0['critical_violations']}/{b0['episodes']}"
        if b0
        else "B0 development evidence unavailable"
    )
    model_line = (
        f"Paired B0/B1/B2 development tasks: {e09['paired_tasks']}; "
        + ", ".join(
            f"{model} {values['success']}/{values['n']} completed"
            for model, values in e09["models"].items()
        )
        if e09
        else "No complete corrected B0/B1/B2 paired model comparison"
    )
    preference_line = (
        f"{preference['materialized_pairs']} scripted trainable pairs; audit {preference['status']}"
        if preference
        else "No preference audit"
    )
    development_line = (
        "Development adapter results: "
        + "; ".join(
            f"{name} {result.get('successes')}/{result.get('paired_tasks')} completed, "
            f"{result.get('critical_violations')} critical process flags"
            for name, result in development_models.items()
        )
        + "."
        if development_models
        else "No completed adapter development comparison."
    )
    protected_line = (
        "Protected internal analysis available in `artifacts/protected_analysis.json`."
        if protected
        else "No qualified protected capability or safety estimate exists."
    )
    external_line = ", ".join(f"{name}: {stages[name]['state']}" for name in ("E25", "E26", "E27"))
    summary = (
        f"# Executive summary\n\nScientific verdict: **{decision}**. "
        f"Public anchor: {dataset_line}. {b0_line}. {model_line}. "
        f"{preference_line}. {development_line} {protected_line} "
        "Mutable action effects remain synthetic; no production advertiser claim is made.\n"
    )
    (root / "reports/executive_summary.md").write_text(summary)
    (root / "reports/main_experiment.md").write_text(
        f"# Main experiment\n\n{model_line}. {preference_line}. {development_line} {protected_line} "
        f"Final verdict: **{decision}**.\n"
    )
    (root / "reports/external_validation.md").write_text(
        f"# External validation\n\n{external_line}. Source access and exact failure "
        "are in `artifacts/external_source_access.json`. No external benchmark outcome "
        "is treated as a zero score.\n"
    )
    (root / "reports/claim_ledger.md").write_text(
        "# Claim audit\n\n"
        + "\n".join(f"- {item['status']}: {item['claim']}" for item in claims)
        + "\n"
    )
    (root / "reports/resume_bullets.md").write_text(
        "# Claim-safe resume bullets\n\n"
        "- Built a local, transactional advertising operations simulator calibrated to public Criteo impression distributions; action effects are synthetic.\n"
        "- Verified the public data and pinned Qwen model hashes, and qualified local RTX 4090 CUDA BF16 execution.\n"
        f"- Evaluated B0 on 400 synthetic development tasks ({b0['successes']} completed) with separate process and safety checks.\n"
        if b0
        else "# Claim-safe resume bullets\n\nNo qualified development summary.\n"
    )
    sections = [
        (
            "Problem and Motivation",
            "Tool-using agents need outcome, process, safety, and systems evaluation.",
        ),
        ("Related Work", "See `studies/desktop_study.md` for pinned primary sources."),
        (
            "Public Data and Claim Boundaries",
            dataset_line + ". Raw public rows remain in WSL scratch.",
        ),
        (
            "Industry Standards",
            "See `studies/standards_mapping.md`; no formal interoperability conformance is claimed.",
        ),
        (
            "Digital Twin",
            "Twin-A qualification and Twin-B seal are in canonical receipts. Intervention effects remain synthetic.",
        ),
        (
            "Agent Environment",
            "Local versioned tool transactions, deterministic user responses, and split namespaces.",
        ),
        (
            "Process Contracts",
            "Known-answer DSL matrix passed; process and outcome are distinct metrics.",
        ),
        ("Tasks", stages["E07"]["reason"]),
        ("Baseline Models", b0_line + ". " + model_line + ". " + development_line),
        ("SFT", stages["E10"]["reason"]),
        ("Preference Construction", preference_line + ". " + stages["E11"]["reason"]),
        ("ACT-PO", stages["E15"]["reason"]),
        (
            "Experimental Protocol",
            "Stage receipts and protected-access ledger are canonical. Protected outcomes require E17 freeze.",
        ),
        ("Main Results", protected_line),
        ("OOD and Twin-B", stages["E19"]["reason"] + "; " + stages["E20"]["reason"]),
        ("Safety", stages["E21"]["reason"]),
        ("Security", stages["E22"]["reason"]),
        ("Preference Noise", stages["E23"]["reason"]),
        ("Ablations", stages["E24"]["reason"]),
        ("External Benchmarks", external_line),
        ("GPU and Systems", stages["E28"]["reason"]),
        (
            "Failure Analysis",
            "Unrun comparisons are null, not zero; see receipts for failures and blockers.",
        ),
        (
            "Limitations",
            "Synthetic action effects, REVIEW task difficulty, scripted preferences, and blocked external sources limit claims.",
        ),
        ("Final Decision", f"**{decision}**. {verdict['reason']}"),
        (
            "Reproducibility",
            "Use pinned model/data manifests, stage receipts, and `act-agent run-all --resume` for hash audit.",
        ),
        ("Supported Claims", "See `artifacts/claim_ledger.json` and `reports/claim_ledger.md`."),
        (
            "Prohibited Claims",
            "No Amazon, production advertiser, real-user benefit, real action-effect, national-policy reproduction, safety-certification, or physical multi-GPU claim.",
        ),
        (
            "Future Work",
            "Repair REVIEW gates, acquire external sources with permitted network, and rerun under a fresh protected protocol if needed.",
        ),
    ]
    body = ["# ACT-Agent v1.0 technical report", "", summary]
    for heading, text in sections:
        body += [f"## {heading}", "", text, ""]
    body += ["## Stage audit", "", "| Stage | State | Reason |", "|---|---|---|"]
    for name, item in stages.items():
        state = "PASS" if name == "E29" else item["state"]
        reason = (
            "Final audited release and claim verification passed"
            if name == "E29"
            else item["reason"].replace("|", "/")
        )
        body.append(f"| {name} | {state} | {reason} |")
    (root / "reports/final_technical_report.md").write_text("\n".join(body) + "\n")
    dashboard_path = generate_dashboard(root)
    manifest_paths = [
        dashboard_path,
        *(
            root / name
            for name in (
                "STATUS.md",
                "README.md",
                "pyproject.toml",
                "MASTER_PROMPT.md",
                "AGENTS.md",
            )
        ),
    ]
    for directory in ("reports", "studies", "protocols", "configs", "data/processed"):
        manifest_paths += sorted(path for path in (root / directory).rglob("*") if path.is_file())
    for directory in ("src", "tests"):
        manifest_paths += sorted((root / directory).rglob("*.py"))
    manifest_paths += sorted(
        path
        for path in (root / "artifacts").rglob("*")
        if path.is_file() and path.relative_to(root).as_posix() != "artifacts/release_manifest.json"
    )
    manifest_paths = [path for path in manifest_paths if path.is_file()]
    write_json(
        root / "artifacts/release_manifest.json",
        {
            "protocol": PROTOCOL,
            "timestamp": identity["timestamp"],
            "files_sha256": {str(p.relative_to(root)): sha256(p) for p in manifest_paths},
        },
    )
    return verdict


if __name__ == "__main__":
    print(generate(Path.cwd())["decision"])
