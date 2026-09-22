"""Deterministic finite-state user responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserSimulator:
    scenario: str
    state: str = "initial"

    def __post_init__(self) -> None:
        if self.scenario not in {
            "fully_specified",
            "underspecified",
            "contradictory",
            "goal_revision",
            "confirmation_required",
            "refusal_required",
        }:
            raise ValueError("unknown deterministic user scenario")

    def respond(self, agent_act: str) -> str:
        if self.scenario == "refusal_required":
            self.state = "refused"
            return "I cannot authorize that action."
        if self.scenario == "contradictory" and self.state == "initial":
            self.state = "clarification_required"
            return "The two requested goals conflict; ask me which takes priority."
        if self.scenario == "goal_revision" and self.state == "initial":
            self.state = "revised"
            return "Please pause the campaign instead."
        if self.scenario == "underspecified" and agent_act != "clarify":
            self.state = "clarification_required"
            return "Please ask which campaign and objective I mean."
        if self.scenario == "confirmation_required" and agent_act != "confirm":
            self.state = "confirmation_required"
            return "I have not confirmed the proposed local change."
        if agent_act == "clarify":
            self.state = "clarified"
            return "Use the current campaign only."
        if agent_act == "confirm":
            self.state = "confirmed"
            return "Yes, I confirm the proposed local change."
        return "Proceed with the specified local task."
