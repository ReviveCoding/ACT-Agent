"""Auditable lexicographic preference labels and bounded ACT pair weights."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class TrajectoryScore:
    critical_violations: int
    process_violations: int
    completed: bool
    oracle_regret: float
    redundant_actions: int
    token_tool_cost: float

    def __post_init__(self) -> None:
        if min(self.critical_violations, self.process_violations, self.redundant_actions) < 0:
            raise ValueError("negative count")
        if self.oracle_regret < 0 or self.token_tool_cost < 0:
            raise ValueError("negative regret or cost")


@dataclass(frozen=True)
class Preference:
    winner: str | None
    decisive_dimension: str | None
    margin: float
    weight: float


def compare(
    left: TrajectoryScore,
    right: TrajectoryScore,
    *,
    regret_margin: float = 0.01,
    cost_margin: float = 1.0,
    severity: float = 1.0,
    task_balance: float = 1.0,
    rarity: float = 1.0,
) -> Preference:
    """Lower critical/process violations dominate all utility and cost terms."""
    dimensions = (
        ("critical_safety", -left.critical_violations, -right.critical_violations, 0),
        ("process", -left.process_violations, -right.process_violations, 0),
        ("completion", int(left.completed), int(right.completed), 0),
        ("oracle_regret", -left.oracle_regret, -right.oracle_regret, regret_margin),
        ("redundant_actions", -left.redundant_actions, -right.redundant_actions, 0),
        ("token_tool_cost", -left.token_tool_cost, -right.token_tool_cost, cost_margin),
    )
    for name, a, b, gate in dimensions:
        delta = float(a - b)
        if abs(delta) <= gate:
            continue
        weight = min(4.0, max(0.25, severity * task_balance * rarity * (1 - exp(-abs(delta)))))
        return Preference("left" if delta > 0 else "right", name, abs(delta), weight)
    return Preference(None, None, 0.0, 0.0)


def dpo_pair_loss(
    policy_chosen: float,
    policy_rejected: float,
    reference_chosen: float,
    reference_rejected: float,
    beta: float,
    weight: float,
) -> float:
    """Stable scalar equivalent of weighted negative log-sigmoid DPO."""
    from math import log1p

    z = beta * ((policy_chosen - policy_rejected) - (reference_chosen - reference_rejected))
    return weight * (max(0.0, -z) + log1p(exp(-abs(z))))
