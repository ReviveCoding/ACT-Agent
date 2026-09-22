"""Execution-time process guard, evaluated separately from learned policy quality."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from act_agent.contracts.core import ProcessContract, ProcessEvent, evaluate
from act_agent.tools.local import READ_TOOLS, WRITE_TOOLS, LocalTools


@dataclass
class RTrace:
    tools: LocalTools
    contract: ProcessContract = field(default_factory=ProcessContract)
    events: list[ProcessEvent] = field(default_factory=list)

    def call(self, name: str, *, confirmed: bool = False, **kwargs: Any) -> dict[str, Any]:
        if name in WRITE_TOOLS:
            candidate = ProcessEvent("write", name, confirmed=confirmed)
            check = evaluate(self.contract, [*self.events, candidate])
            if not check.compliant:
                raise PermissionError(",".join(check.violations))
            result = self.tools.call(name, **kwargs)
            self.events.append(candidate)
            return result
        result = self.tools.call(name, **kwargs)
        if name in READ_TOOLS:
            self.events.append(ProcessEvent("read", name))
        return result
