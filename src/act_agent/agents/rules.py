"""Deterministic B0 rule agent; useful as a qualified non-LLM comparator."""

from __future__ import annotations

from dataclasses import dataclass

from act_agent.contracts.core import ProcessContract, ProcessEvent, evaluate
from act_agent.tools.local import LocalTools
from act_agent.twin.core import CampaignState, Twin


@dataclass(frozen=True)
class EpisodeResult:
    success: bool
    compliant: bool
    critical: bool
    tool_calls: int
    final_state: CampaignState
    events: tuple[ProcessEvent, ...]


def run_b0(
    state: CampaignState, task: str, *, confirmed: bool = False, seed: int = 0, variant: str = "A"
) -> EpisodeResult:
    twin = Twin(state, seed=seed, variant=variant)
    tools = LocalTools(twin)
    contract = ProcessContract()
    events: list[ProcessEvent] = []
    for name in ("get_campaign", "get_policy", "get_metrics"):
        tools.call(name)
        events.append(ProcessEvent("read", name))
    if task == "read":
        success = True
    elif task == "raise_bid" and state.bid < 1.5:
        tools.call("change_bid", value=1.5, expected_version=state.state_version)
        events.append(ProcessEvent("write", "change_bid"))
        success = twin.state.bid == 1.5
    elif task == "increase_budget" and confirmed:
        tools.call("change_budget", value=10, expected_version=state.state_version)
        events.append(ProcessEvent("write", "change_budget", confirmed=True))
        success = twin.state.budget_total == state.budget_total + 10
    elif task == "increase_budget":
        success = False
    elif task == "pause":
        tools.call("pause_campaign", expected_version=state.state_version)
        events.append(ProcessEvent("write", "pause_campaign"))
        success = twin.state.paused
    else:
        success = False
    check = evaluate(contract, events)
    return EpisodeResult(
        success, check.compliant, check.critical, len(events), twin.state, tuple(events)
    )
