# Task and user simulator card

The development generator emits 400 deterministic synthetic tasks: all 12 named families and all ten numeric difficulty labels appear. Train and development tasks use disjoint seed namespaces. The agent observation omits the hidden fault and world seed. `artifacts/task_qualification.json` records these checks.

The six deterministic user scenarios return the expected first response. Clarification and confirmation have explicit follow-up responses. `tests/test_tasks.py` checks the response and state transitions for the cases used in evaluation.

**Qualification: REVIEW.** Difficulty labels currently cycle with task index. They do not establish distinct L3–L9 mechanics such as multi-source diagnosis, long workflows, or unseen composition. The current completion evaluator handles a narrow set of read, diagnosis, mutation, approval, and refusal cases; it is not an independent completion oracle for all 12 families. B0–B2 measurements on these tasks are development diagnostics only. They cannot support the contract's protected long-horizon capability claim or a promotion decision.

`artifacts/task_oracle_gap_matrix.json` records the family-level gap. CREATE, EXPAND, PORTFOLIO, and AMBIGUOUS have no completion criterion; RECOVERY currently falls through to a read criterion; COMPOUND contains one injected fault and a narrow repair criterion; OPTIMIZE uses the same bid/targeting rule as REPAIR. These family labels cannot be interpreted as validated operational outcomes.
