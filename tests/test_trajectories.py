import json

from act_agent.tasks.generator import make_task
from act_agent.trajectories.generate import expert_trace, generate_sft


def test_expert_trace_hides_fault_and_has_tool_results() -> None:
    trace = expert_trace(make_task("train", 2))
    user = next(m for m in trace["messages"] if m["role"] == "user")
    assert "hidden_fault" not in user["content"]
    assert any(m["role"] == "tool" for m in trace["messages"])


def test_sft_generation_count_and_hash(tmp_path) -> None:
    path = tmp_path / "sft.jsonl"
    manifest = generate_sft(path, worlds=3, trajectories_per_world=2)
    assert manifest["trajectories"] == 6
    assert len(path.read_text().splitlines()) == 6
    assert json.loads(path.read_text().splitlines()[0])["split"] == "train"
