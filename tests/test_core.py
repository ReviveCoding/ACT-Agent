import pytest

from act_agent.agents.rules import run_b0
from act_agent.contracts.core import ProcessContract, ProcessEvent, evaluate
from act_agent.safety.rtrace import RTrace
from act_agent.tools.local import LocalTools
from act_agent.twin.core import CampaignState, Fault, Twin, TwinCalibration


def state() -> CampaignState:
    return CampaignState("C1", "A1")


def test_seed_reproducible_and_twin_distinct() -> None:
    a = Twin(state(), seed=42)
    b = Twin(state(), seed=42)
    c = Twin(state(), seed=42, variant="B")
    assert a.tick() == b.tick()
    assert a.state != c.tick()


def test_versioned_mutation_and_rollback() -> None:
    twin = Twin(state())
    twin.mutate("bid", 2.0, 0)
    with pytest.raises(ValueError, match="stale"):
        twin.mutate("bid", 3.0, 0)
    twin.rollback(1)
    assert twin.state.bid == 1.0
    assert twin.state.state_version == 2


def test_invalid_transaction_keeps_state() -> None:
    twin = Twin(state())
    with pytest.raises(ValueError):
        twin.mutate("bid", -1.0, 0)
    assert twin.state == state()
    assert not twin.events


def test_contract_detects_unsafe_success() -> None:
    events = [ProcessEvent("write", "change_budget", confirmed=False)]
    result = evaluate(ProcessContract(), events)
    assert not result.compliant and result.critical
    assert "missing_confirmation" in result.violations


def test_b0_read_and_confirmation() -> None:
    assert run_b0(state(), "read").success
    assert not run_b0(state(), "increase_budget").success
    result = run_b0(state(), "increase_budget", confirmed=True)
    assert result.success and result.compliant and not result.critical


def test_fault_taxonomy_and_scope_guard() -> None:
    for fault in Fault:
        twin = Twin(state())
        twin.inject_fault(fault)
        assert twin.state.state_version == 1
        twin.state.validate()
    tools = LocalTools(Twin(state()))
    with pytest.raises(PermissionError, match="scope"):
        tools.call("get_campaign", advertiser_id="OTHER")


def test_rtrace_blocks_premature_and_unconfirmed_write() -> None:
    guard = RTrace(LocalTools(Twin(state())))
    with pytest.raises(PermissionError, match="missing_prewrite_evidence"):
        guard.call("change_budget", value=10, expected_version=0)
    for name in ("get_campaign", "get_policy", "get_metrics"):
        guard.call(name)
    with pytest.raises(PermissionError, match="missing_confirmation"):
        guard.call("change_budget", value=10, expected_version=0)
    guard.call("change_budget", confirmed=True, value=10, expected_version=0)
    assert guard.tools.twin.state.budget_total == 110


def test_twin_a_aggregate_flag_rates_track_public_anchor() -> None:
    outcomes = [
        Twin(CampaignState(f"C{i}", "A1", timestamp=12), seed=i).tick() for i in range(1000)
    ]
    impressions = sum(s.impressions for s in outcomes)
    clicks = sum(s.clicks for s in outcomes)
    conversions = sum(s.conversions for s in outcomes)
    calibration = TwinCalibration()
    assert abs(clicks / impressions - calibration.click_flag_rate) < 0.02
    assert abs(conversions / clicks - calibration.conversion_flag_given_click) < 0.025


def test_observed_temporal_profile_shapes_synthetic_opportunity() -> None:
    night = [
        Twin(CampaignState(f"C{i}", "A1", timestamp=2), seed=i).tick().impressions
        for i in range(100)
    ]
    evening = [
        Twin(CampaignState(f"C{i}", "A1", timestamp=19), seed=i).tick().impressions
        for i in range(100)
    ]
    assert sum(evening) > 5 * sum(night)


def test_analysis_tools_share_randomness_without_mutating() -> None:
    twin = Twin(state(), seed=123)
    tools = LocalTools(twin)
    comparisons = tools.call(
        "compare_actions",
        actions=[
            {"action": "change_bid", "value": 0.5},
            {"action": "change_bid", "value": 3.0},
        ],
    )
    values = comparisons["comparisons"]
    assert values[1]["projected_impressions"] >= values[0]["projected_impressions"]
    assert twin.state == state()


def test_telemetry_corruption_is_visible_to_reader() -> None:
    twin = Twin(state())
    twin.inject_fault(Fault.TELEMETRY_CORRUPTION)
    assert LocalTools(twin).call("get_metrics")["error"] == "telemetry_corruption"
