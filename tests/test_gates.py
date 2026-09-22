from act_agent.evaluation.gates import PromotionEvidence, decide


def qualified(**overrides):
    values = {
        "data_integrity": True,
        "simulator_valid": True,
        "process_evaluator_valid": True,
        "protocol_intact": True,
        "security_acceptable": True,
        "twin_b_acceptable": True,
        "protected_capability_ci_low": 0.01,
        "critical_safety_difference_ci_high": 0.002,
        "safety_noninferiority_margin": 0.01,
    }
    values.update(overrides)
    return PromotionEvidence(**values)


def test_both_primary_gates_required() -> None:
    assert decide(qualified()) == "PROMOTE_ACT_PO"
    assert decide(qualified(protected_capability_ci_low=-0.01)) == "RETAIN_SFT"
    assert decide(qualified(critical_safety_difference_ci_high=0.02)) == "RETAIN_SFT"


def test_missing_or_invalid_evidence_holds() -> None:
    assert decide(qualified(protected_capability_ci_low=None)) == "HOLD"
    assert decide(qualified(twin_b_acceptable=False)) == "HOLD"
