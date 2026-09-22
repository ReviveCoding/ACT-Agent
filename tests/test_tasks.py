from act_agent.tasks.generator import agent_observation, make_task
from act_agent.user.core import UserSimulator


def test_task_generation_deterministic_and_split_separated() -> None:
    train = make_task("train", 17)
    assert train == make_task("train", 17)
    assert train.world_seed != make_task("id", 17).world_seed
    assert "hidden_fault" not in agent_observation(train)
    assert "world_seed" not in agent_observation(train)


def test_task_state_invariants_across_faults() -> None:
    for i in range(120):
        make_task("train", i).initial_state.validate()


def test_user_simulator_requires_clarification_and_confirmation() -> None:
    unclear = UserSimulator("underspecified")
    assert "ask which campaign" in unclear.respond("proceed")
    assert unclear.state == "clarification_required"
    assert unclear.respond("clarify") == "Use the current campaign only."
    approval = UserSimulator("confirmation_required")
    assert "not confirmed" in approval.respond("proceed")
    assert "confirm" in approval.respond("confirm").lower()
    assert approval.state == "confirmed"
    assert "cannot authorize" in UserSimulator("refusal_required").respond("proceed")
