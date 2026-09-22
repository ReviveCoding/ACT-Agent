# Process contract card

The machine-readable DSL checks required reads before writes, evidence, confirmation, forbidden actions, per-action permissions, advertiser scope, mutation limits, and rollback after failed writes. The known-answer matrix in `tests/test_contract_matrix.py` passed for each rule; `RTrace` applies the same checker at execution time. Outcome success and process compliance are scored separately. The current task difficulty and end-to-end model behavior remain separate qualifications.
