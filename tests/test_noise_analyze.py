import json

import pytest

from act_agent.evaluation.noise_analyze import seal_and_analyze


def test_noise_seal_rejects_changed_evaluator_source(tmp_path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    evaluator = tmp_path / "evaluator.py"
    evaluator.write_text("changed")
    (artifacts / "preference_noise_evaluation_plan.json").write_text(
        json.dumps(
            {
                "task_count": 24,
                "protected_outcome_access": 0,
                "source_sha256": {"evaluator.py": "incorrect"},
            }
        )
    )
    with pytest.raises(ValueError, match="source changed"):
        seal_and_analyze(tmp_path, tmp_path / "scratch")
