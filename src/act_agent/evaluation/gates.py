"""Frozen-style promotion logic; thresholds supplied by a pre-outcome freeze."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Decision = Literal[
    "PROMOTE_ACT_PO", "PROMOTE_DPO", "PROMOTE_IPO_OR_ROBUST", "RETAIN_SFT", "RETAIN_REACT", "HOLD"
]


@dataclass(frozen=True)
class PromotionEvidence:
    data_integrity: bool
    simulator_valid: bool
    process_evaluator_valid: bool
    protocol_intact: bool
    security_acceptable: bool
    twin_b_acceptable: bool
    protected_capability_ci_low: float | None
    critical_safety_difference_ci_high: float | None
    safety_noninferiority_margin: float | None
    strongest_alternative: Decision = "RETAIN_SFT"


def decide(evidence: PromotionEvidence) -> Decision:
    gates = (
        evidence.data_integrity,
        evidence.simulator_valid,
        evidence.process_evaluator_valid,
        evidence.protocol_intact,
        evidence.security_acceptable,
        evidence.twin_b_acceptable,
    )
    if not all(gates):
        return "HOLD"
    if (
        evidence.protected_capability_ci_low is None
        or evidence.critical_safety_difference_ci_high is None
        or evidence.safety_noninferiority_margin is None
    ):
        return "HOLD"
    if (
        evidence.protected_capability_ci_low > 0
        and evidence.critical_safety_difference_ci_high < evidence.safety_noninferiority_margin
    ):
        return "PROMOTE_ACT_PO"
    return evidence.strongest_alternative
