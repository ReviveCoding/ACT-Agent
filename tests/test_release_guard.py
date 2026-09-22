import json
from pathlib import Path

import pytest

from act_agent.evidence.release import PROTOCOL, STAGES
from act_agent.reporting.release import generate


def test_release_refuses_pending_scientific_stage(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    stages = {f"E{i:02d}": {"state": "CLOSED", "reason": "fixture"} for i in range(len(STAGES))}
    stages["E09"]["state"] = "PENDING"
    (artifacts / "run_state.json").write_text(json.dumps({"protocol": PROTOCOL, "stages": stages}))
    with pytest.raises(ValueError, match="scientific stages unfinished"):
        generate(tmp_path)
    assert not (artifacts / "final_verdict.json").exists()


def test_release_fail_closed_without_protected_outcomes(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (tmp_path / "reports").mkdir()
    (artifacts / "receipts").mkdir()
    stages = {f"E{i:02d}": {"state": "CLOSED", "reason": "fixture"} for i in range(len(STAGES))}
    stages["E29"]["state"] = "PENDING"
    (artifacts / "run_state.json").write_text(json.dumps({"protocol": PROTOCOL, "stages": stages}))
    (artifacts / "protected_access_ledger.json").write_text(
        json.dumps({"internal_outcome_access": 0, "external_benchmark_outcome_access": 0})
    )
    verdict = generate(tmp_path)
    assert verdict["decision"] == "HOLD"
    assert verdict["primary_capability"] is None
    claims = json.loads((artifacts / "claim_ledger.json").read_text())
    assert claims[0]["status"] == "UNSUPPORTED"
    report_before = (tmp_path / "reports/final_technical_report.md").read_bytes()
    manifest_before = (artifacts / "release_manifest.json").read_bytes()
    generate(tmp_path)
    assert (tmp_path / "reports/final_technical_report.md").read_bytes() == report_before
    assert (artifacts / "release_manifest.json").read_bytes() == manifest_before
