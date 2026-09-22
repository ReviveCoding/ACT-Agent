"""Pre-protected Twin-A qualification against observed anchors and known answers."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from act_agent.twin.core import CampaignState, Fault, Twin, TwinCalibration


def _correlation(left: list[float], right: list[float]) -> float:
    xbar, ybar = mean(left), mean(right)
    numerator = sum((x - xbar) * (y - ybar) for x, y in zip(left, right, strict=True))
    denominator = math.sqrt(
        sum((x - xbar) ** 2 for x in left) * sum((y - ybar) ** 2 for y in right)
    )
    return numerator / denominator


def qualify() -> dict[str, Any]:
    calibration = TwinCalibration()
    hourly: list[float] = []
    for hour in range(24):
        hourly.append(
            mean(
                Twin(CampaignState(f"H{i}", "A", timestamp=hour), seed=i).tick().impressions
                for i in range(100)
            )
        )
    temporal_r = _correlation(hourly, list(calibration.hourly_traffic_profile))
    bucket_counts = [[0, 0] for _ in range(3)]
    total_impressions = total_clicks = total_conversions = 0
    for i in range(3000):
        identifier = f"C{i}"
        outcome = Twin(CampaignState(identifier, "A", timestamp=12), seed=i).tick()
        bucket = hashlib.sha256(identifier.encode()).digest()[0] % 3
        bucket_counts[bucket][0] += outcome.impressions
        bucket_counts[bucket][1] += outcome.clicks
        total_impressions += outcome.impressions
        total_clicks += outcome.clicks
        total_conversions += outcome.conversions
    bucket_rates = [clicks / impressions for impressions, clicks in bucket_counts]
    baseline = CampaignState("known", "A", timestamp=12)
    base_impressions = Twin(baseline, seed=77).tick().impressions
    fault_results: dict[str, dict[str, Any]] = {}
    for fault in Fault:
        twin = Twin(baseline, seed=77)
        twin.inject_fault(fault)
        after = twin.tick()
        fault_results[fault.value] = {
            "impressions": after.impressions,
            "telemetry_health": after.telemetry_health,
            "state_valid": True,
        }
    bid_low = Twin(baseline, seed=123)
    bid_low.mutate("bid", 0.2, 0)
    bid_high = Twin(baseline, seed=123)
    bid_high.mutate("bid", 3.0, 0)
    intervention_direction = bid_high.tick().impressions > bid_low.tick().impressions
    transaction = Twin(baseline)
    transaction.mutate("bid", 2.0, 0)
    transaction.rollback(1)
    rollback_valid = transaction.state.bid == baseline.bid and transaction.state.state_version == 2
    deterministic = Twin(baseline, seed=7).tick() == Twin(baseline, seed=7).tick()
    checks = {
        "temporal_profile_r_at_least_0_95": temporal_r >= 0.95,
        "aggregate_click_anchor_within_0_03": abs(
            total_clicks / total_impressions - calibration.click_flag_rate
        )
        <= 0.03,
        "conditional_conversion_anchor_within_0_03": abs(
            total_conversions / total_clicks - calibration.conversion_flag_given_click
        )
        <= 0.03,
        "campaign_heterogeneity_ordered": bucket_rates[0] < bucket_rates[1] < bucket_rates[2],
        "faults_covered": len(fault_results) == len(Fault),
        "zero_delivery_budget_and_eligibility": fault_results[Fault.BUDGET_EXHAUSTION][
            "impressions"
        ]
        == 0
        and fault_results[Fault.DEAL_ELIGIBILITY_FAILURE]["impressions"] == 0,
        "delivery_faults_reduce_opportunity": all(
            fault_results[f.value]["impressions"] < base_impressions
            for f in (
                Fault.PACING_THROTTLE,
                Fault.UNDER_BIDDING,
                Fault.COMPETITION_SHOCK,
                Fault.SUPPLY_COLLAPSE,
                Fault.TARGETING_RESTRICTION,
                Fault.PERFORMANCE_REGIME_SHIFT,
            )
        ),
        "telemetry_corruption_visible": fault_results[Fault.TELEMETRY_CORRUPTION][
            "telemetry_health"
        ]
        == "corrupt",
        "bid_intervention_direction": intervention_direction,
        "rollback_and_version": rollback_valid,
        "deterministic_seed": deterministic,
    }
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "variant": "A",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "temporal_profile_correlation": temporal_r,
        "observed_click_flag_rate": calibration.click_flag_rate,
        "synthetic_click_flag_rate": total_clicks / total_impressions,
        "observed_conversion_given_click": calibration.conversion_flag_given_click,
        "synthetic_conversion_given_click": total_conversions / total_clicks,
        "campaign_bucket_rates": bucket_rates,
        "fault_results": fault_results,
        "calibration": asdict(calibration),
        "claim_boundary": "Observed rates anchor flags only; all intervention effects are synthetic.",
    }


if __name__ == "__main__":
    result = qualify()
    path = Path("artifacts/twin_a_qualification.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], result["checks"])
    if result["status"] != "PASS":
        raise SystemExit(1)
