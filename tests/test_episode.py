from act_agent.contracts.core import ProcessEvent
from act_agent.evaluation.episode import judge, run_b0_task
from act_agent.tasks.generator import make_task
from act_agent.twin.core import Twin


def test_clarification_is_not_counted_as_task_completion() -> None:
    result, _ = run_b0_task(make_task("development", 4))
    assert result.task_family == "CREATE"
    assert result.appropriate_abstention
    assert not result.success
    assert result.process_compliant


def test_paired_b0_task_is_reproducible() -> None:
    first, first_trace = run_b0_task(make_task("development", 2))
    second, second_trace = run_b0_task(make_task("development", 2))
    assert first == second
    assert first_trace == second_trace


def test_tool_reads_without_final_answer_are_incomplete() -> None:
    task = make_task("development", 0)
    result = judge(
        task,
        Twin(task.initial_state),
        [ProcessEvent("read", "get_campaign")],
        "B2",
        finalized=False,
    )
    assert not result.success
    assert not result.finalized
