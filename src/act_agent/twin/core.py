"""Versioned, local-only advertising operations simulator.

Intervention response is deliberately synthetic; public observations cannot identify it.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Any


@dataclass(frozen=True)
class CampaignState:
    campaign_id: str
    advertiser_id: str
    market_id: str = "M1"
    policy_pack: str = "research-v1"
    timestamp: int = 0
    budget_total: float = 100.0
    budget_remaining: float = 100.0
    spend_velocity: float = 0.0
    bid: float = 1.0
    pacing_multiplier: float = 1.0
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    ctr: float = 0.0
    cvr: float = 0.0
    cpa: float = 0.0
    competition_index: float = 1.0
    eligible_inventory: float = 1.0
    supply_index: float = 1.0
    targeting_state: str = "broad"
    eligibility_state: str = "eligible"
    telemetry_health: str = "ok"
    pending_approval: bool = False
    permissions: tuple[str, ...] = ("read", "bid", "budget", "target", "pause")
    state_version: int = 0
    paused: bool = False

    def validate(self) -> None:
        if self.budget_total < 0 or not 0 <= self.budget_remaining <= self.budget_total:
            raise ValueError("invalid budget")
        if self.bid < 0 or self.pacing_multiplier < 0:
            raise ValueError("negative bid or pacing")
        if min(self.impressions, self.clicks, self.conversions) < 0:
            raise ValueError("negative counts")
        if self.clicks > self.impressions or self.conversions > self.clicks:
            raise ValueError("invalid funnel counts")
        if not all(math.isfinite(x) for x in (self.bid, self.budget_total, self.budget_remaining)):
            raise ValueError("non-finite financial value")


class Fault(StrEnum):
    BUDGET_EXHAUSTION = "BUDGET_EXHAUSTION"
    PACING_THROTTLE = "PACING_THROTTLE"
    UNDER_BIDDING = "UNDER_BIDDING"
    COMPETITION_SHOCK = "COMPETITION_SHOCK"
    SUPPLY_COLLAPSE = "SUPPLY_COLLAPSE"
    DEAL_ELIGIBILITY_FAILURE = "DEAL_ELIGIBILITY_FAILURE"
    TARGETING_RESTRICTION = "TARGETING_RESTRICTION"
    PERFORMANCE_REGIME_SHIFT = "PERFORMANCE_REGIME_SHIFT"
    TELEMETRY_CORRUPTION = "TELEMETRY_CORRUPTION"


@dataclass(frozen=True)
class TwinCalibration:
    """Observed impression-level rates; action effects remain synthetic."""

    click_flag_rate: float = 0.3611582006757701
    conversion_flag_given_click: float = 0.13555064486076063
    source_sha256: str = "94ac7a465564349bc7ba008602211d5990a3c53cc133abc0aadef61ea2391a98"
    hourly_traffic_profile: tuple[float, ...] = (
        0.1945,
        0.1343,
        0.1286,
        0.1783,
        0.3021,
        0.5589,
        0.8703,
        1.1224,
        1.2721,
        1.3034,
        1.3188,
        1.3321,
        1.3396,
        1.3380,
        1.3217,
        1.3460,
        1.4507,
        1.5297,
        1.5897,
        1.6123,
        1.4903,
        1.1703,
        0.7339,
        0.3619,
    )
    campaign_ctr_quantiles: tuple[float, float, float] = (
        0.24798207450961218,
        0.3429812824390682,
        0.45707048362782654,
    )

    def validate(self) -> None:
        if not 0 <= self.click_flag_rate <= 1 or not 0 <= self.conversion_flag_given_click <= 1:
            raise ValueError("invalid calibration rate")
        if len(self.hourly_traffic_profile) != 24 or min(self.hourly_traffic_profile) <= 0:
            raise ValueError("invalid hourly profile")


@dataclass
class Twin:
    state: CampaignState
    seed: int = 0
    variant: str = "A"
    calibration: TwinCalibration = field(default_factory=TwinCalibration)
    history: list[CampaignState] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.state.validate()
        self.calibration.validate()
        if self.variant not in {"A", "B"}:
            raise ValueError("unknown twin")

    def inject_fault(self, fault: Fault) -> CampaignState:
        s = self.state
        fault_changes: dict[Fault, dict[str, Any]] = {
            Fault.BUDGET_EXHAUSTION: {"budget_remaining": 0.0},
            Fault.PACING_THROTTLE: {"pacing_multiplier": 0.15},
            Fault.UNDER_BIDDING: {"bid": 0.1},
            Fault.COMPETITION_SHOCK: {"competition_index": 4.0},
            Fault.SUPPLY_COLLAPSE: {"supply_index": 0.1},
            Fault.DEAL_ELIGIBILITY_FAILURE: {"eligibility_state": "ineligible"},
            Fault.TARGETING_RESTRICTION: {"targeting_state": "narrow"},
            Fault.PERFORMANCE_REGIME_SHIFT: {"competition_index": 2.0, "supply_index": 0.7},
            Fault.TELEMETRY_CORRUPTION: {"telemetry_health": "corrupt"},
        }
        changes = fault_changes[fault]
        new = replace(s, **changes, state_version=s.state_version + 1)
        new.validate()
        self.state = new
        self.events.append(
            {"action": "inject_fault", "fault": fault.value, "after": new.state_version}
        )
        return new

    def mutate(
        self, action: str, value: float | str | None, expected_version: int
    ) -> CampaignState:
        old = self.state
        if expected_version != old.state_version:
            raise ValueError("stale state version")
        if action not in old.permissions:
            raise PermissionError(action)
        if old.pending_approval:
            raise PermissionError("pending approval")
        if action in {"bid", "budget"} and value is None:
            raise ValueError("numeric value required")
        if action == "bid":
            assert value is not None
            new = replace(old, bid=float(value))
        elif action == "budget":
            assert value is not None
            delta = float(value)
            if delta < 0:
                raise ValueError("budget increase must be nonnegative")
            new = replace(
                old,
                budget_total=old.budget_total + delta,
                budget_remaining=old.budget_remaining + delta,
            )
        elif action == "target":
            if value not in {"broad", "narrow"}:
                raise ValueError("unknown targeting")
            new = replace(old, targeting_state=str(value))
        elif action == "pause":
            new = replace(old, paused=True)
        else:
            raise ValueError(action)
        new = replace(new, state_version=old.state_version + 1)
        new.validate()
        self.history.append(old)
        self.state = new
        self.events.append(
            {
                "action": action,
                "before": old.state_version,
                "after": new.state_version,
                "value": value,
            }
        )
        return new

    def rollback(self, expected_version: int) -> CampaignState:
        if expected_version != self.state.state_version or not self.history:
            raise ValueError("no matching rollback point")
        previous = self.history.pop()
        self.state = replace(previous, state_version=self.state.state_version + 1)
        self.events.append({"action": "rollback", "after": self.state.state_version})
        return self.state

    def tick(self, hours: int = 1) -> CampaignState:
        if hours <= 0:
            raise ValueError("hours must be positive")
        s = self.state
        rng = random.Random(f"{self.seed}:{s.timestamp}:{s.campaign_id}:{self.variant}")
        temporal = (
            sum(
                self.calibration.hourly_traffic_profile[(s.timestamp + i) % 24]
                for i in range(hours)
            )
            / hours
        )
        opportunity = s.supply_index * s.eligible_inventory * s.pacing_multiplier * temporal
        if s.paused or s.eligibility_state != "eligible" or s.budget_remaining <= 0:
            opportunity = 0
        if self.variant == "A":
            win = s.bid / (s.bid + max(s.competition_index, 0.01))
        else:
            win = 1 / (1 + math.exp(-2.0 * (s.bid - 1.3 * s.competition_index)))
            opportunity *= 0.75 + 0.25 * math.sin(s.timestamp / 6)
        reach = 0.6 if s.targeting_state == "narrow" else 1.0
        impressions = max(0, int(100 * hours * opportunity * win * reach + rng.gauss(0, 2)))
        price = min(s.budget_remaining, impressions * (0.01 + 0.005 * s.bid))
        actual = min(impressions, int(price / (0.01 + 0.005 * s.bid)))
        click_p = self.calibration.click_flag_rate
        conversion_p = self.calibration.conversion_flag_given_click
        bucket = hashlib.sha256(s.campaign_id.encode()).digest()[0] % 3
        click_p *= (
            self.calibration.campaign_ctr_quantiles[bucket]
            / self.calibration.campaign_ctr_quantiles[1]
        )
        click_p = min(click_p, 1.0)
        if self.variant == "B":
            click_p *= 0.85 + 0.1 * math.sin(s.timestamp / 8)
            conversion_p *= 0.75
        clicks = sum(rng.random() < click_p for _ in range(actual))
        conversions = sum(rng.random() < conversion_p for _ in range(clicks))
        new = replace(
            s,
            timestamp=s.timestamp + hours,
            budget_remaining=max(0.0, s.budget_remaining - price),
            spend_velocity=price / hours,
            impressions=s.impressions + actual,
            clicks=s.clicks + clicks,
            conversions=s.conversions + conversions,
            state_version=s.state_version + 1,
        )
        new = replace(
            new,
            ctr=new.clicks / new.impressions if new.impressions else 0,
            cvr=new.conversions / new.clicks if new.clicks else 0,
            cpa=(new.budget_total - new.budget_remaining) / new.conversions
            if new.conversions
            else 0,
        )
        new.validate()
        self.state = new
        self.events.append({"action": "tick", "hours": hours, "after": new.state_version})
        return new
