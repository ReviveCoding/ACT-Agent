import json

import pyarrow as pa
import pyarrow.parquet as pq

from act_agent.evidence.warehouse_update import rebuild_development, rebuild_training_systems


def test_warehouse_keeps_only_complete_model_pairs(tmp_path) -> None:
    directory = tmp_path / "artifacts/warehouse"
    directory.mkdir(parents=True)
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "task_id": "development-000000",
                    "task_family": "READ",
                    "model": "B0",
                    "split": "development",
                    "success": True,
                    "critical_violation": False,
                    "violations": [],
                }
            ]
        ),
        directory / "b0_development.parquet",
    )
    scratch = tmp_path / "scratch/e09_baselines"
    scratch.mkdir(parents=True)
    episodes = [
        {
            "task_id": "development-000000",
            "model": model,
            "final_state_version": 0,
            "critical_violation": False,
            "violations": [],
        }
        for model in ("B0", "B1", "B2")
    ]
    episodes.append(
        {
            "task_id": "development-000001",
            "model": "B1",
            "final_state_version": 0,
            "critical_violation": False,
            "violations": [],
        }
    )
    (scratch / "episodes.jsonl").write_text("".join(json.dumps(row) + "\n" for row in episodes))
    (scratch / "traces.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "task_id": "development-000000",
                    "model": model,
                    "trace": [{"tool": "get_campaign"}],
                }
            )
            + "\n"
            for model in ("B0", "B1", "B2")
        )
    )
    result = rebuild_development(tmp_path, tmp_path / "scratch")
    assert result["paired_model_tasks"] == 1
    assert result["episodes"] == 3
    table = pq.read_table(directory / "episodes.parquet")
    assert "final_state_version" in table.schema.names
    assert set(table.column("model").to_pylist()) == {"B0", "B1", "B2"}
    adapter_prefix = tmp_path / "artifacts/e10_b3-test"
    adapter_prefix.with_name(adapter_prefix.name + "_rollout_manifest.json").write_text(
        json.dumps({"run_id": "b3-test", "models": ["B3"], "count": 1})
    )
    adapter_prefix.with_name(adapter_prefix.name + "_episodes.jsonl").write_text(
        json.dumps(
            {
                "task_id": "development-000000",
                "model": "B3",
                "final_state_version": 0,
                "critical_violation": False,
                "violations": [],
            }
        )
        + "\n"
    )
    adapter_prefix.with_name(adapter_prefix.name + "_traces.jsonl").write_text(
        json.dumps(
            {
                "task_id": "development-000000",
                "model": "B3",
                "trace": [{"tool": "get_campaign"}],
            }
        )
        + "\n"
    )
    adapter_result = rebuild_development(tmp_path, tmp_path / "scratch")
    assert adapter_result["episodes"] == 4
    assert set(pq.read_table(directory / "episodes.parquet").column("model").to_pylist()) == {
        "B0",
        "B1",
        "B2",
        "B3",
    }
    training = tmp_path / "artifacts/training"
    training.mkdir()
    (training / "sft-seed11.json").write_text(
        json.dumps({"status": "PASS", "seed": 11, "losses": [1.2, 0.8]})
    )
    (tmp_path / "artifacts/systems_serving_test.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "full_generation_seconds": [2.0],
                "full_generation_tokens": [10],
                "peak_reserved_vram_bytes": 1000,
            }
        )
    )
    extended = rebuild_training_systems(tmp_path)
    assert extended == {"training_runs": 1, "training_steps": 2, "serving_repeats": 1}
    assert pq.read_table(directory / "training_metrics.parquet").num_rows == 2
    assert "b3-test" in pq.read_table(directory / "runs.parquet").column("run_id").to_pylist()
