"""Pre-protected task and deterministic user simulator audit."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from act_agent.tasks.generator import TASK_FAMILIES, agent_observation, make_task
from act_agent.user.core import UserSimulator


def qualify() -> dict[str, Any]:
    tasks = [make_task("development", index) for index in range(400)]
    families = Counter(task.family for task in tasks)
    levels = Counter(task.difficulty for task in tasks)
    observations_hide_oracle = all(
        "hidden_fault" not in agent_observation(task)
        and "world_seed" not in agent_observation(task)
        for task in tasks
    )
    scenarios = [
        "fully_specified",
        "underspecified",
        "contradictory",
        "goal_revision",
        "confirmation_required",
        "refusal_required",
    ]
    responses = {}
    expected = {
        "fully_specified": "Proceed with the specified local task.",
        "underspecified": "Please ask which campaign and objective I mean.",
        "contradictory": "The two requested goals conflict; ask me which takes priority.",
        "goal_revision": "Please pause the campaign instead.",
        "confirmation_required": "I have not confirmed the proposed local change.",
        "refusal_required": "I cannot authorize that action.",
    }
    for scenario in scenarios:
        first = UserSimulator(scenario).respond("proceed")
        second = UserSimulator(scenario).respond("proceed")
        responses[scenario] = {
            "first": first,
            "deterministic": first == second,
            "expected": first == expected[scenario],
        }
    responses["clarification_response"] = {
        "first": UserSimulator("underspecified").respond("clarify"),
        "expected": UserSimulator("underspecified").respond("clarify")
        == "Use the current campaign only.",
    }
    responses["confirmation_response"] = {
        "first": UserSimulator("confirmation_required").respond("confirm"),
        "expected": "confirm" in UserSimulator("confirmation_required").respond("confirm").lower(),
    }
    checks = {
        "all_families_present": set(families) == set(TASK_FAMILIES),
        "all_levels_present": set(levels) == set(range(10)),
        "split_seed_separation": all(
            make_task("train", i).world_seed != make_task("development", i).world_seed
            for i in range(400)
        ),
        "oracle_hidden_from_observation": observations_hide_oracle,
        "user_scenarios_deterministic": all(
            item["deterministic"] for item in responses.values() if "deterministic" in item
        ),
        "user_scenarios_expected": all(item["expected"] for item in responses.values()),
    }
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "REVIEW" if all(checks.values()) else "FAIL",
        "checks": checks,
        "families": dict(families),
        "difficulty_labels": dict(levels),
        "user_responses": responses,
        "limitation": "Difficulty labels cycle independently of generated task mechanics; L3-L9 semantic coverage and independent completion oracle remain unqualified.",
        "claim_effect": "Development evaluation only; no high-difficulty primary claim until repaired.",
    }


if __name__ == "__main__":
    result = qualify()
    Path("artifacts/task_qualification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], result["checks"])
    if result["status"] == "FAIL":
        raise SystemExit(1)
