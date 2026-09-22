import json

from act_agent.preference.materialize import perturb
from act_agent.tasks.generator import make_task
from act_agent.trajectories.generate import expert_trace


def test_missing_confirmation_only_on_approval_trace() -> None:
    approval = expert_trace(make_task("train", 8))["messages"]
    negative = perturb(approval, "missing_confirmation")
    assert negative is not None
    assert any(m.get("tool_calls") for m in negative)
    assert not any("confirm a local budget" in str(m.get("content", "")) for m in negative)
    assert perturb(expert_trace(make_task("train", 0))["messages"], "missing_confirmation") is None
    assert perturb(approval, "inefficient_success") is None


def test_wrong_argument_changes_executed_tool_call() -> None:
    trace = None
    for index in range(2, 120, 12):
        candidate = expert_trace(make_task("train", index))["messages"]
        if any(
            m.get("tool_calls") and m["tool_calls"][0]["function"]["name"].startswith("change_")
            for m in candidate
        ):
            trace = candidate
            break
    assert trace is not None
    negative = perturb(trace, "wrong_argument")
    assert negative is not None
    call = next(
        m["tool_calls"][0]["function"]
        for m in negative
        if m.get("tool_calls") and m["tool_calls"][0]["function"]["name"].startswith("change_")
    )
    assert json.loads(call["arguments"])["value"] in (-10.0, "invalid")
