import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from act_agent.evaluation.analyze_adapter import analyze


def test_adapter_analysis_requires_matching_paired_task(tmp_path) -> None:
    base_path = tmp_path / "base.parquet"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "task_id": "development-000000",
                    "task_family": "READ",
                    "model": model,
                    "success": success,
                    "world_seed": "123",
                    "variant": "A",
                }
                for model, success in (("B0", True), ("B2", False))
            ]
        ),
        base_path,
    )
    adapter_path = tmp_path / "episodes.jsonl"
    episode = {
        "task_id": "development-000000",
        "task_family": "READ",
        "model": "B3",
        "split": "development",
        "success": True,
        "safe_success": True,
        "process_compliant": True,
        "critical_violation": False,
        "generated_tokens": 12,
        "generation_seconds": 1.5,
        "world_seed": "123",
        "variant": "A",
    }
    adapter_path.write_text(json.dumps(episode) + "\n")
    result = analyze(
        base_path=base_path,
        adapter_path=adapter_path,
        model_label="B3",
        output_path=tmp_path / "canonical.parquet",
    )
    assert result["paired_tasks"] == 1
    assert result["comparisons"]["B3_minus_B2"]["difference"] == 1.0
    adapter_path.write_text(json.dumps(episode) + "\n" + json.dumps(episode) + "\n")
    with pytest.raises(ValueError, match="duplicated"):
        analyze(
            base_path=base_path,
            adapter_path=adapter_path,
            model_label="B3",
            output_path=tmp_path / "canonical.parquet",
        )
    episode["world_seed"] = "wrong"
    adapter_path.write_text(json.dumps(episode) + "\n")
    with pytest.raises(ValueError, match="world seed"):
        analyze(
            base_path=base_path,
            adapter_path=adapter_path,
            model_label="B3",
            output_path=tmp_path / "canonical.parquet",
        )
