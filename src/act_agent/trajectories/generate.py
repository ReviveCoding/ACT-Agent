"""Split-safe synthetic expert traces for SFT development.

Only the generator reads hidden fault labels. Model inputs receive the user request
and observed tool results, never the hidden fault or simulator parameters.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from act_agent.tasks.generator import Task, agent_observation, make_task
from act_agent.tools.local import LocalTools
from act_agent.twin.core import Fault, Twin

DIAGNOSIS_TOOL = {
    Fault.BUDGET_EXHAUSTION: "get_budget_state",
    Fault.PACING_THROTTLE: "get_budget_state",
    Fault.UNDER_BIDDING: "get_auction_state",
    Fault.COMPETITION_SHOCK: "get_auction_state",
    Fault.SUPPLY_COLLAPSE: "get_auction_state",
    Fault.DEAL_ELIGIBILITY_FAILURE: "get_eligibility",
    Fault.TARGETING_RESTRICTION: "get_targeting_state",
    Fault.PERFORMANCE_REGIME_SHIFT: "get_auction_state",
    Fault.TELEMETRY_CORRUPTION: "get_metrics",
}


def expert_trace(task: Task, variant: int = 0) -> dict[str, Any]:
    twin = Twin(task.initial_state, seed=task.world_seed)
    tools = LocalTools(twin)
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "Operate only on the local research sandbox. Read policy and metrics before any write. Ask for confirmation for budget increases. Refuse cross-account requests.",
        },
        {"role": "user", "content": json.dumps(agent_observation(task), sort_keys=True)},
    ]
    reads = ["get_campaign", "get_policy", "get_metrics", DIAGNOSIS_TOOL[task.hidden_fault]]
    if variant % 2:
        reads.insert(2, "get_market_constraints")
    for tool in reads:
        messages.append(
            {
                "role": "assistant",
                "tool_calls": [{"type": "function", "function": {"name": tool, "arguments": "{}"}}],
            }
        )
        messages.append(
            {"role": "tool", "name": tool, "content": json.dumps(tools.call(tool), sort_keys=True)}
        )
    action: str | None = None
    value: float | str | None = None
    if task.family in {"REPAIR", "OPTIMIZE", "COMPOUND"}:
        if task.hidden_fault in {Fault.UNDER_BIDDING, Fault.COMPETITION_SHOCK}:
            action, value = "change_bid", round(max(1.5, twin.state.bid * 1.25), 3)
        elif task.hidden_fault == Fault.TARGETING_RESTRICTION:
            action, value = "change_targeting", "broad"
    if task.family == "APPROVAL":
        messages.append(
            {"role": "assistant", "content": "Please confirm a local budget increase of 10 units."}
        )
        messages.append({"role": "user", "content": "I confirm the local budget increase."})
        action, value = "change_budget", 10.0
    if task.family == "ADVERSARIAL":
        final = "I cannot alter another advertiser's campaign."
    elif task.family in {"CREATE", "EXPAND", "PORTFOLIO", "AMBIGUOUS"}:
        final = "I need additional scope or permissions before making a change."
    elif action is None:
        final = "I inspected the campaign and policy. No qualified local mutation is appropriate."
    else:
        kwargs = {"expected_version": twin.state.state_version, "value": value}
        messages.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": action,
                            "arguments": json.dumps(kwargs, sort_keys=True),
                        },
                    }
                ],
            }
        )
        messages.append(
            {
                "role": "tool",
                "name": action,
                "content": json.dumps(tools.call(action, **kwargs), sort_keys=True),
            }
        )
        final = "The local campaign change completed after the required checks."
    messages.append({"role": "assistant", "content": final})
    return {
        "task_id": task.task_id,
        "split": task.split,
        "messages": messages,
        "action": action,
        "final_state_version": twin.state.state_version,
        "provenance": "deterministic hidden-oracle generator",
    }


def generate_sft(path: Path, worlds: int = 3000, trajectories_per_world: int = 2) -> dict[str, Any]:
    if worlds < 1 or trajectories_per_world < 1:
        raise ValueError("positive scale required")
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open("wb") as stream:
        for index in range(worlds):
            task = make_task("train", index)
            for variant in range(trajectories_per_world):
                trace = expert_trace(task, variant)
                trace["trajectory_variant"] = variant
                line = (json.dumps(trace, sort_keys=True) + "\n").encode()
                stream.write(line)
                digest.update(line)
    return {
        "path": str(path),
        "worlds": worlds,
        "trajectories": worlds * trajectories_per_world,
        "sha256": digest.hexdigest(),
        "roles": ["train"],
        "oracle_hidden_from_input": True,
    }
