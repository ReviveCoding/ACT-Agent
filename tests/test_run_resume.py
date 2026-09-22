import json
from pathlib import Path

import pytest

from act_agent.data.pipeline import sha256
from act_agent.evidence.release import PROTOCOL, run_all


def test_run_all_resume_verifies_immutable_receipts_without_rewriting(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    immutable = artifacts / "qualified.txt"
    immutable.write_text("verified\n")
    ledger = {
        "protocol": PROTOCOL,
        "stages": {
            "E00": {"state": "PASS", "outputs": {"artifacts/qualified.txt": sha256(immutable)}},
            "E09": {"state": "PENDING", "outputs": {}},
        },
    }
    state = artifacts / "run_state.json"
    state.write_text(json.dumps(ledger))
    (artifacts / "protected_access_ledger.json").write_text(
        json.dumps({"internal_outcome_access": 0})
    )
    before = state.read_bytes()
    result = run_all(tmp_path)
    assert result["next_stage"] == "E09"
    assert state.read_bytes() == before
    immutable.write_text("changed\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        run_all(tmp_path)
