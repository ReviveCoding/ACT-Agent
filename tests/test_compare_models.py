import json

import pytest

from act_agent.evaluation.compare_models import compare


def test_adapter_comparison_requires_same_world_identity(tmp_path) -> None:
    baseline = tmp_path / "baseline.jsonl"
    candidate = tmp_path / "candidate.jsonl"
    first = {
        "task_id": "development-000001",
        "task_family": "READ",
        "world_seed": "123",
        "variant": "A",
        "split": "development",
        "model": "B3",
        "success": False,
        "safe_success": False,
        "process_compliant": True,
        "critical_violation": False,
    }
    second = {**first, "model": "M0", "success": True, "safe_success": True}
    baseline.write_text(json.dumps(first) + "\n")
    candidate.write_text(json.dumps(second) + "\n")
    result = compare(baseline, candidate)
    assert result["metrics"]["completion"]["difference"] == 1
    candidate.write_text(json.dumps({**second, "world_seed": "456"}) + "\n")
    with pytest.raises(ValueError, match="world_seed"):
        compare(baseline, candidate)
