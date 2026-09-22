from act_agent.contracts.core import ProcessContract, ProcessEvent, evaluate


def safe_reads() -> list[ProcessEvent]:
    return [ProcessEvent("read", name) for name in ("get_campaign", "get_policy", "get_metrics")]


def test_contract_known_answer_matrix() -> None:
    reads = safe_reads()
    assert evaluate(ProcessContract(), [*reads, ProcessEvent("write", "change_bid")]).compliant
    cases = [
        ([ProcessEvent("write", "change_bid")], "missing_prewrite_evidence"),
        ([*reads, ProcessEvent("write", "change_budget")], "missing_confirmation"),
        ([*reads, ProcessEvent("write", "change_bid", authorized=False)], "unauthorized_mutation"),
        ([*reads, ProcessEvent("write", "change_bid", scope_ok=False)], "scope_violation"),
        ([*reads, ProcessEvent("write", "create_campaign", confirmed=True)], "missing_permission"),
        ([*reads, ProcessEvent("failed_write", "change_bid")], "missing_rollback"),
        ([*reads, *(ProcessEvent("write", "change_bid") for _ in range(3))], "excessive_mutation"),
    ]
    for events, violation in cases:
        result = evaluate(ProcessContract(), events)
        assert not result.compliant, violation
        assert violation in result.violations
    recovered = evaluate(
        ProcessContract(),
        [
            *reads,
            ProcessEvent("failed_write", "change_bid"),
            ProcessEvent("rollback", "rollback_last_action"),
        ],
    )
    assert recovered.compliant


def test_forbidden_action_and_required_evidence() -> None:
    contract = ProcessContract(forbidden_actions=frozenset({"change_bid"}))
    blocked = evaluate(contract, [*safe_reads(), ProcessEvent("write", "change_bid")])
    assert blocked.critical and "forbidden_action" in blocked.violations
    missing_metrics = evaluate(
        ProcessContract(),
        [
            ProcessEvent("read", "get_campaign"),
            ProcessEvent("read", "get_policy"),
            ProcessEvent("write", "change_bid"),
        ],
    )
    assert "missing_required_evidence" in missing_metrics.violations
