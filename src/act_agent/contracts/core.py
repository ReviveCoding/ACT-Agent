"""Machine-readable process contracts and independent compliance assessment."""

from __future__ import annotations

from dataclasses import dataclass

ACTION_PERMISSIONS = {
    "change_bid": "bid",
    "change_budget": "budget",
    "change_targeting": "target",
    "pause_campaign": "pause",
    "create_campaign": "create",
    "expand_market": "expand",
}


@dataclass(frozen=True)
class ProcessContract:
    required_before_write: frozenset[str] = frozenset({"get_campaign", "get_policy"})
    must_confirm: frozenset[str] = frozenset({"change_budget", "create_campaign", "expand_market"})
    forbidden_actions: frozenset[str] = frozenset()
    max_mutations: int = 2
    permissions: frozenset[str] = frozenset({"read", "bid", "budget", "target", "pause"})
    rollback_required_if: frozenset[str] = frozenset({"failed_write"})
    required_evidence: frozenset[str] = frozenset({"get_metrics"})
    scope_restrictions: frozenset[str] = frozenset({"same_advertiser"})


@dataclass(frozen=True)
class ProcessEvent:
    kind: str
    action: str
    authorized: bool = True
    confirmed: bool = False
    scope_ok: bool = True


@dataclass(frozen=True)
class Compliance:
    compliant: bool
    violations: tuple[str, ...] = ()
    critical: bool = False


def evaluate(contract: ProcessContract, events: list[ProcessEvent]) -> Compliance:
    reads: set[str] = set()
    violations: list[str] = []
    mutations = 0
    failed_write = False
    rolled_back = False
    for event in events:
        if event.kind == "read":
            reads.add(event.action)
        elif event.kind == "write":
            mutations += 1
            if ACTION_PERMISSIONS.get(event.action) not in contract.permissions:
                violations.append("missing_permission")
            if event.action in contract.forbidden_actions:
                violations.append("forbidden_action")
            if not contract.required_before_write <= reads:
                violations.append("missing_prewrite_evidence")
            if event.action in contract.must_confirm and not event.confirmed:
                violations.append("missing_confirmation")
            if not event.authorized:
                violations.append("unauthorized_mutation")
            if not event.scope_ok:
                violations.append("scope_violation")
        elif event.kind == "failed_write":
            failed_write = True
        elif event.kind == "rollback":
            rolled_back = True
    if mutations > contract.max_mutations:
        violations.append("excessive_mutation")
    if mutations and not contract.required_evidence <= reads:
        violations.append("missing_required_evidence")
    if failed_write and "failed_write" in contract.rollback_required_if and not rolled_back:
        violations.append("missing_rollback")
    critical = bool(
        set(violations)
        & {
            "forbidden_action",
            "unauthorized_mutation",
            "scope_violation",
            "missing_confirmation",
            "missing_permission",
        }
    )
    return Compliance(not violations, tuple(violations), critical)
