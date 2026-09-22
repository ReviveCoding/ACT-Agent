"""Release evidence verifier: hashes, protected access, claims, and warehouse."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import duckdb

from act_agent.data.pipeline import sha256
from act_agent.evaluation.gates import Decision
from act_agent.evidence.release import PROTOCOL, STAGES
from act_agent.twin.seal import MECHANISM

TERMINAL = {"PASS", "FAIL", "REVIEW", "BLOCKED_EXTERNAL", "CLOSED"}
CLAIM_STATES = {"SUPPORTED", "SUPPORTED_WITH_QUALIFIER", "CONDITIONAL", "UNSUPPORTED", "PROHIBITED"}
PROHIBITED_CLAIMS = {
    "Synthetic interventions cause real advertiser lift",
    "Amazon proprietary data, Ads API integration, or production account control",
    "Production advertiser outcomes or production agent-safety certification",
    "Real-user benefit or real campaign-action causal effects",
    "Formal reproduction of national advertising policy",
    "Physical multi-GPU scaling",
}
DECISIONS: set[Decision] = {
    "PROMOTE_ACT_PO",
    "PROMOTE_DPO",
    "PROMOTE_IPO_OR_ROBUST",
    "RETAIN_SFT",
    "RETAIN_REACT",
    "HOLD",
}
WAREHOUSE_TABLES = {
    "runs",
    "episodes",
    "steps",
    "tool_calls",
    "state_transitions",
    "process_events",
    "safety_events",
    "preference_pairs",
    "training_metrics",
    "external_eval",
    "systems_metrics",
    "failures",
}


def verify_release(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    ledger = json.loads((root / "artifacts/run_state.json").read_text())
    if ledger.get("protocol") != PROTOCOL or len(ledger.get("stages", {})) != len(STAGES):
        errors.append("stage ledger incomplete or protocol mismatch")
    for index in range(len(STAGES)):
        name = f"E{index:02d}"
        receipt_path = root / "artifacts/receipts" / f"{name}.json"
        if not receipt_path.exists():
            errors.append(f"missing {name} receipt")
            continue
        receipt = json.loads(receipt_path.read_text())
        if receipt != ledger["stages"].get(name):
            errors.append(f"{name} receipt differs from run_state")
        if receipt.get("protocol") != PROTOCOL:
            errors.append(f"{name} protocol mismatch")
        if receipt.get("state") not in TERMINAL:
            errors.append(f"invalid {name} state")
        for relative, expected in receipt.get("outputs", {}).items():
            path = root / relative
            if not path.is_file() or sha256(path) != expected:
                errors.append(f"{name} output hash mismatch: {relative}")
    profile_path = root / "data/processed/profile.json"
    if profile_path.exists():
        profile = json.loads(profile_path.read_text())
        for name, info in profile.get("marts", {}).items():
            path = root / "data/processed" / f"{name}.parquet"
            if not path.exists() or sha256(path) != info["sha256"]:
                errors.append(f"mart hash mismatch: {name}")
    seal_path = root / "artifacts/twin_b_seal.json"
    if seal_path.exists():
        seal = json.loads(seal_path.read_text())
        mechanism = hashlib.sha256(
            json.dumps(MECHANISM, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        for key, path in (
            ("source_sha256", root / "src/act_agent/twin/core.py"),
            ("calibration_sha256", root / "configs/twin_a_calibration.json"),
        ):
            if not path.is_file() or sha256(path) != seal.get(key):
                errors.append(f"Twin-B seal mismatch: {key}")
        if mechanism != seal.get("parameter_sha256"):
            errors.append("Twin-B mechanism parameter seal mismatch")
    else:
        errors.append("Twin-B seal missing")
    e09_path = root / "artifacts/e09_baseline_summary.json"
    if e09_path.exists():
        e09 = json.loads(e09_path.read_text())
        episode_log = root / "artifacts/e09_episodes.jsonl"
        canonical_episodes = root / "artifacts/warehouse/e09_episodes.parquet"
        if not episode_log.is_file() or sha256(episode_log) != e09.get("source_sha256"):
            errors.append("E09 canonical episode log hash mismatch")
        if not canonical_episodes.is_file() or sha256(canonical_episodes) != e09.get(
            "canonical_sha256"
        ):
            errors.append("E09 paired episode table hash mismatch")
    claims = json.loads((root / "artifacts/claim_ledger.json").read_text())
    claims_by_text = {claim.get("claim"): claim for claim in claims}
    for required in PROHIBITED_CLAIMS:
        if claims_by_text.get(required, {}).get("status") != "PROHIBITED":
            errors.append(f"prohibited claim audit missing or weakened: {required}")
    for claim in claims:
        if claim.get("status") not in CLAIM_STATES:
            errors.append(f"invalid claim state: {claim.get('claim')}")
        if claim.get("status") in {"SUPPORTED", "SUPPORTED_WITH_QUALIFIER"} and (
            not claim.get("evidence") or any(not (root / p).exists() for p in claim["evidence"])
        ):
            errors.append(f"unsupported supported claim: {claim.get('claim')}")
    access = json.loads((root / "artifacts/protected_access_ledger.json").read_text())
    if (
        access.get("internal_outcome_access", 0)
        or access.get("external_benchmark_outcome_access", 0)
    ) and not (root / "artifacts/freeze_manifest.json").exists():
        errors.append("protected outcomes accessed without freeze")
    warehouse = root / "artifacts/warehouse/evidence.duckdb"
    if warehouse.exists():
        db = duckdb.connect(str(warehouse), read_only=True)
        existing = {item[0] for item in db.execute("SHOW TABLES").fetchall()}
        for table in sorted(WAREHOUSE_TABLES - existing):
            errors.append(f"missing warehouse view: {table}")
        count = (
            db.execute("SELECT count(*) FROM episodes").fetchone()
            if "episodes" in existing
            else None
        )
        if "episodes" in existing and access.get("internal_outcome_access", 0) == 0:
            protected_rows = db.execute(
                "SELECT count(*) FROM episodes WHERE split IN "
                "('id','composition','policy','tool','twin_b','security')"
            ).fetchone()
            if protected_rows and protected_rows[0] > 0:
                errors.append("protected episode rows exist while access ledger is zero")
        db.close()
        if count is None or count[0] < 100:
            errors.append("B0 development evidence missing")
    else:
        errors.append("evidence warehouse missing")
    verdict_path = root / "artifacts/final_verdict.json"
    if not verdict_path.exists():
        errors.append("final verdict missing")
    else:
        verdict = json.loads(verdict_path.read_text())
        if verdict.get("decision") not in DECISIONS:
            errors.append("invalid scientific decision")
        if verdict.get("decision") != "HOLD" and access.get("internal_outcome_access", 0) == 0:
            errors.append("promotion without protected internal evidence")
        if verdict.get("decision") == "PROMOTE_ACT_PO" and any(
            ledger["stages"].get(name, {}).get("state") != "PASS"
            for name in ("E05", "E07", "E08", "E17", "E18", "E20", "E21", "E22")
        ):
            errors.append("ACT-PO promoted despite failed critical stage gate")
    model_path = root / "artifacts/model_source_manifest.json"
    if model_path.exists():
        model = json.loads(model_path.read_text())
        snapshot = Path(model["local_snapshot"])
        for name, expected in model.get("files_sha256", {}).items():
            path = snapshot / name
            if not path.is_file() or sha256(path) != expected:
                errors.append(f"model source hash mismatch: {name}")
    else:
        errors.append("model source manifest missing")
    for report in (
        "executive_summary.md",
        "data_card.md",
        "eda_report.md",
        "main_experiment.md",
        "systems_report.md",
        "final_technical_report.md",
    ):
        if not (root / "reports" / report).is_file():
            errors.append(f"missing report: {report}")
    manifest_path = root / "artifacts/release_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("protocol") != PROTOCOL:
            errors.append("release manifest protocol mismatch")
        for relative, expected in manifest.get("files_sha256", {}).items():
            path = root / relative
            if not path.is_file() or sha256(path) != expected:
                errors.append(f"release manifest hash mismatch: {relative}")
        included = set(manifest.get("files_sha256", {}))
        for claim in claims:
            if claim.get("status") in {"SUPPORTED", "SUPPORTED_WITH_QUALIFIER"}:
                for relative in claim.get("evidence", []):
                    if relative not in included:
                        errors.append(f"supported claim evidence missing from manifest: {relative}")
    else:
        errors.append("release manifest missing")
    return {
        "pass": not errors,
        "errors": errors,
        "verified_stages": len(STAGES),
        "protected_internal_access": access.get("internal_outcome_access", 0),
    }
