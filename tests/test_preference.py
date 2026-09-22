from act_agent.preference.core import TrajectoryScore, compare, dpo_pair_loss


def test_safety_dominates_completion() -> None:
    safe = TrajectoryScore(0, 0, False, 100, 10, 1000)
    unsafe = TrajectoryScore(1, 0, True, 0, 0, 0)
    pref = compare(safe, unsafe)
    assert pref.winner == "left" and pref.decisive_dimension == "critical_safety"


def test_tie_gate_and_weight_bounds() -> None:
    a = TrajectoryScore(0, 0, True, 0.1, 0, 10)
    b = TrajectoryScore(0, 0, True, 0.105, 0, 10.5)
    assert compare(a, b).winner is None
    c = TrajectoryScore(0, 0, False, 1, 0, 10)
    pref = compare(a, c, severity=100)
    assert pref.winner == "left" and pref.weight == 4.0


def test_weighted_dpo_loss_monotone() -> None:
    assert dpo_pair_loss(2, 0, 0, 0, 0.1, 1) < dpo_pair_loss(0, 2, 0, 0, 0.1, 1)
