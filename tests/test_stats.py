import pytest

from act_agent.evaluation.stats import PairedOutcome, paired_cluster_bootstrap, wilson_interval


def test_paired_bootstrap_and_mcnemar() -> None:
    rows = [
        PairedOutcome(f"t{i}", "A" if i < 50 else "B", i % 3 == 0, i % 2 == 0) for i in range(100)
    ]
    summary = paired_cluster_bootstrap(rows, repetitions=200, seed=7)
    assert summary.n == 100
    assert summary.ci_low <= summary.difference <= summary.ci_high
    assert 0 <= summary.mcnemar_p <= 1


def test_rare_event_wilson_is_not_zero() -> None:
    low, high = wilson_interval(0, 100)
    assert low >= 0 and high > 0
    with pytest.raises(ValueError):
        wilson_interval(0, 0)
