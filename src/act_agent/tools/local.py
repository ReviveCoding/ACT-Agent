"""Local tool surface; no advertiser network access."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from act_agent.twin.core import Twin

READ_TOOLS = (
    "get_campaign",
    "list_campaigns",
    "get_metrics",
    "get_budget_state",
    "get_auction_state",
    "get_targeting_state",
    "get_eligibility",
    "get_policy",
    "get_market_constraints",
)
ANALYSIS_TOOLS = ("simulate_action", "compare_actions")
WRITE_TOOLS = (
    "change_bid",
    "change_budget",
    "change_targeting",
    "pause_campaign",
    "create_campaign",
    "expand_market",
    "rollback_last_action",
)


class LocalTools:
    def __init__(self, twin: Twin) -> None:
        self.twin = twin

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        state = self.twin.state
        if name not in (*READ_TOOLS, *ANALYSIS_TOOLS, *WRITE_TOOLS):
            raise KeyError(name)
        if kwargs.get("campaign_id", state.campaign_id) != state.campaign_id:
            raise PermissionError("campaign scope violation")
        if kwargs.get("advertiser_id", state.advertiser_id) != state.advertiser_id:
            raise PermissionError("advertiser scope violation")
        if name in READ_TOOLS:
            if name == "get_campaign":
                return asdict(state)
            if name == "list_campaigns":
                return {"campaigns": [state.campaign_id]}
            if name == "get_metrics":
                if state.telemetry_health != "ok":
                    return {"error": "telemetry_corruption", "state_version": state.state_version}
                return {
                    k: getattr(state, k)
                    for k in (
                        "impressions",
                        "clicks",
                        "conversions",
                        "ctr",
                        "cvr",
                        "cpa",
                        "spend_velocity",
                    )
                }
            if name == "get_budget_state":
                return {
                    k: getattr(state, k)
                    for k in (
                        "budget_total",
                        "budget_remaining",
                        "spend_velocity",
                        "pacing_multiplier",
                    )
                }
            if name == "get_auction_state":
                return {k: getattr(state, k) for k in ("bid", "competition_index", "supply_index")}
            if name == "get_targeting_state":
                return {"targeting_state": state.targeting_state}
            if name == "get_eligibility":
                return {
                    "eligibility_state": state.eligibility_state,
                    "eligible_inventory": state.eligible_inventory,
                }
            if name == "get_policy":
                return {
                    "policy_pack": state.policy_pack,
                    "pending_approval": state.pending_approval,
                }
            return {"market_id": state.market_id, "research_sandbox": True}
        if name in ANALYSIS_TOOLS:
            if name == "compare_actions":
                actions = kwargs.get("actions")
                if not isinstance(actions, list):
                    raise ValueError("actions must be a list")
                return {
                    "synthetic_only": True,
                    "comparisons": [
                        self.call("simulate_action", **candidate) for candidate in actions
                    ],
                }
            action = kwargs.get("action")
            action_map = {
                "change_bid": "bid",
                "change_budget": "budget",
                "change_targeting": "target",
                "pause_campaign": "pause",
            }
            if action not in action_map:
                raise ValueError("unsupported simulated action")
            scratch = Twin(
                state,
                seed=self.twin.seed,
                variant=self.twin.variant,
                calibration=self.twin.calibration,
            )
            scratch.mutate(action_map[action], kwargs.get("value"), state.state_version)
            pre_tick_budget = scratch.state.budget_remaining
            projected = scratch.tick()
            return {
                "synthetic_only": True,
                "action": action,
                "current_state_version": state.state_version,
                "projected_impressions": projected.impressions - state.impressions,
                "projected_clicks": projected.clicks - state.clicks,
                "projected_spend_units": pre_tick_budget - projected.budget_remaining,
            }
        expected = kwargs.get("expected_version")
        if expected is None:
            raise ValueError("expected_version required")
        if name == "rollback_last_action":
            return asdict(self.twin.rollback(int(expected)))
        action_map = {
            "change_bid": "bid",
            "change_budget": "budget",
            "change_targeting": "target",
            "pause_campaign": "pause",
        }
        if name in {"create_campaign", "expand_market"}:
            raise NotImplementedError("multi-campaign mutation is not qualified")
        return asdict(self.twin.mutate(action_map[name], kwargs.get("value"), int(expected)))
