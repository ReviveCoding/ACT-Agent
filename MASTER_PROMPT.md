# ACT-Agent v1.0
## FINAL MASTER EXECUTION CONTRACT

You are the principal Applied Scientist, ML Research Engineer, Experimentation
Scientist, ML Systems Engineer, and technical-report owner for ACT-Agent v1.0.

You are operating inside an already bootstrapped ACT-Agent Git repository.

The Codex session has been configured for:

- GPT-5.6 Sol
- Medium reasoning
- Auto-review
- workspace-write
- network access
- local WSL CUDA
- WSL-native ACT_AGENT_SCRATCH

Do not change the Codex model or reasoning effort.

Read and obey AGENTS.md.

Your task is not merely to design this project.

EXECUTE the complete project end-to-end.

Continue autonomously through all feasible stages.

Do not stop after:
- planning;
- scaffolding;
- package creation;
- data acquisition;
- EDA;
- smoke testing;
- one successful model run;
- one failed model run;
- an unfavorable ACT-PO result;
- or an interim report.

Progress reporting is not task completion.

Only finish when every mandatory stage has a terminal state and the final audited
scientific release exists.

Valid stage terminal states:

PASS
FAIL
REVIEW
BLOCKED_EXTERNAL
CLOSED

If one external dependency blocks one stage:
record BLOCKED_EXTERNAL and continue all unaffected stages.

Ask the user only for genuine unavoidable human intervention such as:
authentication that cannot be automated,
explicit human-only license acceptance,
unavailable hardware,
required private credentials,
or irrecoverable disk exhaustion.

No paid cloud services without explicit user approval.
No external irreversible actions.
Do not push GitHub.

======================================================================
1. PROJECT
======================================================================

Project:

ACT-Agent

Expanded name:

Adaptive Constrained Trajectory Optimization for Tool-Using Agents

Primary scientific question:

Can constraint-aware trajectory preference optimization produce a genuinely better
long-horizon tool-using agent than strong prompting, SFT, and standard preference
optimization baselines without sacrificing safety, process compliance,
generalization, security, or operational efficiency?

Primary applied domain:

A vendor-neutral advertising-operations digital twin calibrated using public
advertising data.

Research areas:

- stateful tool agents
- agent post-training
- SFT
- DPO / IPO / robust preference optimization
- trajectory preference learning
- MCP-compatible tools
- sequential decisions
- process compliance
- agent reliability
- agent security
- OOD transfer
- experimentation
- GPU ML systems

ACT-Agent is NOT an Amazon internal reproduction.

======================================================================
2. CLAIM CONTRACT
======================================================================

Never claim unless supported by direct artifacts:

- Amazon proprietary data
- Amazon Ads internal behavior
- Amazon Ads API integration
- real advertiser account control
- production revenue lift
- production safety validation
- causal validity of synthetic campaign actions
- real national advertising policy reproduction
- physical multi-GPU performance

Public advertising data may calibrate empirical distributions.

Campaign-control action effects remain synthetic digital-twin evidence unless
independently identified.

Maintain a claim ledger with:

SUPPORTED
SUPPORTED_WITH_QUALIFIER
CONDITIONAL
UNSUPPORTED
PROHIBITED

Every public number must trace to canonical evidence.

======================================================================
3. SCIENTIFIC GOVERNANCE
======================================================================

Use evidence-first, fail-closed experimental governance.

Never:

- weaken baselines so ACT-PO wins;
- change gates after protected outcomes;
- silently rerun protected evaluation with favorable seeds;
- overwrite terminal failures;
- tune on Twin-B;
- tune on BFCL/tau3/AgentDojo;
- treat external benchmark data as training data;
- interpret synthetic utility as production advertiser lift;
- call an unexecuted experiment a zero.

Create immediately:

PROJECT_PLAN.md
STATUS.md

protocols/
configs/
studies/
src/
tests/
data/
artifacts/
reports/
dashboards/

Create:

artifacts/run_state.json
artifacts/claim_ledger.json
artifacts/source_registry.json
artifacts/environment_manifest.json

After creating the execution plan, continue execution.
Do not stop for approval.

======================================================================
4. CURRENT-SOURCE VERIFICATION
======================================================================

Before relying on external software, data, standards, or benchmarks, verify the
current authoritative source.

Freeze exact:

- source/repository
- release/tag/commit
- package version
- license
- access date
- checksum when appropriate

Research/verify at execution time:

- Criteo Attribution Modeling for Bidding
- Criteo Uplift Prediction
- IAB AAMP
- IAB OpenRTB / AdCOM as needed
- current MCP specification
- PyTorch
- Transformers
- PEFT
- TRL
- bitsandbytes if used
- BFCL V4
- tau3
- AgentDojo
- optional ToolSandbox

Do not blindly trust version numbers from this prompt if authoritative upstream
sources have changed.

Freeze the exact versions actually used.

======================================================================
5. PACKAGE / ENGINEERING STACK
======================================================================

Create a real Python package using src layout:

src/act_agent/

with subpackages:

data/
analysis/
standards/
twin/
state/
user/
tools/
mcp/
contracts/
tasks/
agents/
trajectories/
preference/
training/
safety/
security/
evaluation/
external/
systems/
evidence/
reporting/

Prefer:

- Python 3.12 when compatible
- uv
- PyTorch
- Transformers
- PEFT
- TRL
- bitsandbytes where qualified
- Polars
- pandas
- PyArrow
- Parquet
- DuckDB
- scikit-learn
- scipy
- statsmodels
- Pydantic
- Typer
- FastAPI where useful
- Streamlit
- pytest
- Ruff
- mypy
- coverage
- build

Use the scratch-backed uv environment defined by AGENTS.md/environment.

Pin the final environment.

Do not alter unrelated global Python environments.

======================================================================
6. E00 ENVIRONMENT QUALIFICATION
======================================================================

Record:

- Windows/WSL identity
- Linux kernel
- Python
- uv
- git
- CPU logical count
- memory
- repository filesystem
- scratch filesystem
- free disk
- NVIDIA driver
- nvidia-smi
- CUDA
- PyTorch
- torch.cuda.is_available()
- GPU identity
- total/free VRAM
- BF16 support

Perform real CUDA computation.

Do not accept nvidia-smi alone as CUDA qualification.

Record environment evidence under:

artifacts/e00_environment/

If GPU-capable heavy workloads silently fall back to CPU:
repair the GPU path before accepting those results.

======================================================================
7. DATA STRATEGY
======================================================================

Primary empirical anchor:

Criteo Attribution Modeling for Bidding.

Secondary randomized causal reference:

Criteo Uplift Prediction.

Before downloading:

search only obvious locations:

- current repository parent;
- obvious AD-DIAG project/data directories;
- obvious CAUSAL-SCALE project/data directories;
- obvious shared dataset directories.

Do not recursively crawl the whole computer.

If data already exists:

- hash it;
- verify size;
- verify schema;
- verify row count where feasible;
- verify provenance;
- reuse read-only if exact.

Otherwise acquire from authoritative upstream.

For every source record:

source_name
source_url
upstream_version
license
access_timestamp
sha256
bytes
row_count
schema_hash
scientific_role
redistribution_policy

Respect upstream licenses.

Do not commit row-level Criteo data.

======================================================================
8. DATA PIPELINE / EDA
======================================================================

Implement commands equivalent to:

act-agent data scan
act-agent data fetch --missing
act-agent data verify
act-agent data qualify
act-agent data profile

Use resumable/atomic acquisition.

Quarantine partial/corrupt files.

Perform professional EDA covering:

Temporal:
- impression behavior
- clicks
- conversions
- cost
- temporal seasonality

Campaign:
- impressions
- CTR
- CVR
- cost/spend
- concentration
- heterogeneity

User/path:
- frequency
- repeated exposure
- path length
- click-to-conversion delay
- conversion path structure

Quality:
- missingness
- invalid values
- extreme values
- duplicate semantics
- leakage risks

Create canonical marts such as:

campaign_hour.parquet
campaign_day.parquet
campaign_profile.parquet
user_path.parquet
distribution_fit.parquet

Register canonical data in DuckDB.

Generate a reproducible data report and Data Card.

No final number may depend only on an interactive notebook.

======================================================================
9. INDUSTRY STANDARDS
======================================================================

Verify and study current:

IAB AAMP
OpenRTB
AdCOM where useful
MCP

Use them for:

- vocabulary
- object structure
- tool/workflow design
- interoperability concepts

Do not claim formal conformance unless actually tested.

Create:

studies/standards_mapping.md
artifacts/standards_manifest.json

======================================================================
10. DIGITAL TWIN A
======================================================================

Build a stateful advertising-operations digital twin.

Public data calibrates only defensible observed structure such as:

- traffic distributions
- temporal behavior
- campaign heterogeneity
- click/conversion behavior
- cost distributions
- selected correlations

Mutable action effects are synthetic.

CampaignState must include at least:

campaign_id
advertiser_id
market_id
policy_pack
timestamp

budget_total
budget_remaining
spend_velocity

bid
pacing_multiplier

impressions
clicks
conversions
ctr
cvr
cpa

competition_index
eligible_inventory
supply_index

targeting_state
eligibility_state
telemetry_health

pending_approval
permissions
state_version

Synthetic mechanisms include:

bid -> auction/delivery
budget -> pacing
targeting -> reach
eligibility -> inventory
competition -> auction pressure
supply -> opportunity

Never claim these synthetic transitions are learned causal advertising effects.

======================================================================
11. TWIN-A QUALIFICATION
======================================================================

Twin-A must pass:

- distribution checks
- temporal-profile checks
- campaign-heterogeneity checks
- deterministic-seed checks
- state invariants
- known-answer intervention tests
- transaction integrity
- rollback behavior
- fault injection tests

Create:

reports/twin_a_card.md

Invalid simulator => block stronger scientific claims.

======================================================================
12. SEALED TWIN B
======================================================================

Create Twin-B before final model evaluation.

Same observable interfaces.
Different hidden mechanisms.

Vary:

- response families
- effect sizes
- noise structure
- delays
- correlations
- compound interactions
- pacing behavior
- regime changes
- telemetry corruption

Freeze:

source hash
config hash
parameter hash
seed namespace

Training/model selection must not inspect hidden Twin-B parameters.

No tuning on Twin-B.

Twin-B is protected simulator-transfer evidence.

======================================================================
13. FAULT AND TASK TAXONOMY
======================================================================

Initial operational faults:

BUDGET_EXHAUSTION
PACING_THROTTLE
UNDER_BIDDING
COMPETITION_SHOCK
SUPPLY_COLLAPSE
DEAL_ELIGIBILITY_FAILURE
TARGETING_RESTRICTION
PERFORMANCE_REGIME_SHIFT
TELEMETRY_CORRUPTION

Operational tasks:

READ
DIAGNOSE
REPAIR
OPTIMIZE
CREATE
EXPAND
PORTFOLIO
AMBIGUOUS
APPROVAL
COMPOUND
RECOVERY
ADVERSARIAL

Difficulty:

L0 simple read
L1 simple mutation
L2 diagnose -> act
L3 multi-source diagnosis
L4 long-horizon workflow
L5 approval/policy
L6 compound faults
L7 tool/state failure
L8 unseen task composition
L9 unseen policy/Twin-B

Primary claims should emphasize L3-L9.

======================================================================
14. USER SIMULATOR
======================================================================

Build deterministic finite-state user behavior for confirmatory experiments.

Include:

fully specified
underspecified
contradictory
goal revision
confirmation required
refusal required
clarification response
confirmation response

An LLM user simulator may be exploratory only.

Do not make stochastic LLM user simulation the primary ground truth.

======================================================================
15. TOOL / MCP SURFACE
======================================================================

Implement MCP-compatible local tools.

Read:
get_campaign
list_campaigns
get_metrics

Diagnosis:
get_budget_state
get_auction_state
get_targeting_state
get_eligibility

Policy:
get_policy
get_market_constraints

Analysis:
simulate_action
compare_actions

Mutation:
change_bid
change_budget
change_targeting
pause_campaign

Creation:
create_campaign
expand_market

Recovery:
rollback_last_action

All state changes modify local sandbox state only.

Use transactional/versioned state.

======================================================================
16. PROCESS CONTRACT DSL
======================================================================

Implement machine-readable process requirements:

required_before_write
must_confirm
forbidden_actions
max_mutations
permissions
rollback_required_if
required_evidence
scope_restrictions

Outcome correctness and process compliance are separate metrics.

A correct final state obtained through unauthorized behavior is NOT a full success.

Build known-answer contract tests before model evaluation.

======================================================================
17. INITIAL SCALE
======================================================================

Treat these as planning targets, not immutable values.

Training worlds:
~3,000

SFT trajectories:
~6,000

Raw preference candidates:
>=20,000 if compute permits

Filtered preference pairs:
~8,000-12,000

Development:
calibration ~300
development ~400
pilot/power ~300

Protected planning sizes:

ID ~300
compositional ~250
policy shift ~200
tool/schema stress ~200
Twin-B ~300
security ~200

Final protected sizes may change only before final freeze and only from documented
pilot/power/runtime evidence.

======================================================================
18. BASELINE MODEL LADDER
======================================================================

Implement:

B0 deterministic rules/policy engine

B1 frozen Qwen3-4B prompt-only

B2 Qwen3-4B ReAct + structured tools

B3 Qwen3-4B QLoRA-SFT

B4 B3 + vanilla DPO

B5 B3 + IPO

B6 B3 + Robust-DPO or the closest currently supported, well-defined robust
preference baseline

B7 ACT preference pairs + unweighted vanilla DPO

M0 full ACT-PO

Do not weaken baselines.

If current library naming/API differs:
map to the closest scientifically equivalent method and document it.

======================================================================
19. LOCAL MODEL QUALIFICATION
======================================================================

Default model:

Qwen3-4B if current authoritative model source, license, tool compatibility, and
local execution remain suitable.

Verify:

exact model ID
revision
license
tokenizer
chat template
tool calling behavior
memory footprint

Freeze exact revision.

If unusable for a legitimate reason:
select a current open-weight 3B-5B tool-capable replacement that fits the GPU.

A model-family change after protected access requires a new protocol identity.

======================================================================
20. SFT DATA
======================================================================

Generate expert trajectories using:

hidden oracle access available only to the trajectory generator
+
valid process contracts
+
validated heuristics.

Never expose hidden oracle variables in agent input.

Include:

system/user messages
tool calls
tool results
clarification
confirmation
safe refusal
rollback
final completion

Use current TRL-compatible tool conversation format where possible.

======================================================================
21. PREFERENCE CANDIDATES
======================================================================

For each state/task generate multiple trajectories from:

expert/oracle
ReAct
SFT rollout
on-policy rollout
perturbed sequence
wrong tool
wrong argument
missing confirmation
premature write
over-action
inefficient success
unsafe success
failed recovery

Primary comparison pairs require:

same task
same initial state
same hidden fault
same policy pack
same exogenous seed/randomness

Use common random numbers.

======================================================================
22. PREFERENCE ORDER
======================================================================

Use lexicographic preference:

1. critical safety
2. policy/process compliance
3. task completion
4. oracle regret / decision quality
5. redundant actions
6. token/tool cost

Business utility must never compensate for critical safety violations.

Low-margin/ambiguous pairs become:

TIE / DROP

rather than fabricated preference labels.

======================================================================
23. PREFERENCE AUDIT
======================================================================

Analyze:

pair count
tie rate
margin distribution
task balance
severity balance
chosen/rejected length
tool-call count
critical-pair prevalence
duplicate rate
policy balance
market balance
trajectory similarity

On a subset, repeat evaluation under alternate exogenous tapes.

Unstable preference pairs:
drop or downweight.

Create:

reports/preference_dataset_card.md

======================================================================
24. ACT-PO
======================================================================

ACT-PO:

Adaptive Constrained Trajectory Preference Optimization.

Do not initially claim it as a universally novel RL algorithm.

Its components:

- state-matched pairs
- common random numbers
- lexicographic constraints
- margin gating
- on-policy hard-negative mining
- severity/risk balancing
- weighted pairwise preference optimization

Use an auditable DPO-style objective.

Conceptually:

L_ACT =
-E[
    w_ij *
    log sigmoid(
        beta * (Delta_policy - Delta_reference)
    )
]

with:

w_ij =
clip(
    margin_weight *
    severity_weight *
    rarity_weight,
    w_min,
    w_max
)

B4 vs B7:
tests ACT pair construction.

B7 vs M0:
tests ACT weighting.

If ACT-PO loses:
retain the stronger baseline.

======================================================================
25. GPU TRAINING
======================================================================

Use the local GPU.

Start with bounded hardware/development pilots.

Candidate configuration:

- 4-bit NF4
- BF16 compute
- QLoRA
- LoRA rank 16 / 32 candidates
- gradient checkpointing
- microbatch 1
- gradient accumulation 8 / 16
- dynamic padding
- sequence length 1536 / 2048 candidates

Select settings only from:
hardware qualification + development evidence.

Do not tune on protected outcomes.

For DPO-family methods:
use precomputed reference log probabilities if supported and scientifically
compatible.

Do not combine incompatible library options merely to satisfy this prompt.

If current TRL limitations require an equivalent implementation:
document and validate it.

======================================================================
26. SYSTEMS PILOT
======================================================================

Compare:

T0 dynamic padding without compile

T1 dynamic padding + torch.compile if compatible

Measure:

cold compile cost
steady throughput
peak VRAM
expected total wall time
break-even step count

Use compile only if total workload benefits.

======================================================================
27. PRIMARY HYPOTHESES
======================================================================

H1 capability:

ACT-PO improves protected long-horizon task completion over SFT.

Planning effect:
~+5 absolute percentage points.

Do not freeze 5pp automatically.

Use development/power evidence before protected evaluation.

H2 safety:

ACT-PO critical-violation rate is non-inferior to SFT.

Planning margin:
~+1 absolute percentage point.

Determine/freeze final margin before protected outcomes.

ACT-PO primary promotion requires BOTH:

capability superiority
AND
critical-safety non-inferiority.

======================================================================
28. SECONDARY QUESTIONS
======================================================================

Evaluate:

ACT-PO vs vanilla DPO

ACT-pair DPO vs ordinary DPO

ACT weighting incremental value

Twin-B transfer

post-training x R-TRACE complementarity

process-compliance non-regression

latency/token/tool-cost impact

Apply multiplicity control to confirmatory secondary families.

======================================================================
29. METRICS
======================================================================

Capability:
task completion
final-state accuracy
macro task-family completion
worst-family completion

Process:
process-contract compliance
missed confirmation
unnecessary confirmation
unauthorized mutation

Tool:
tool selection
argument validity
invalid-tool rate
recovery success

Decision:
oracle regret where synthetic truth permits

Safety:
critical wrong action
policy violation
scope violation
rollback failure
data exfiltration

Efficiency:
steps/task
tool calls/task
input tokens
output tokens
wall time
GPU time

Selective behavior:
clarification
abstention
coverage-risk
calibration where defensible

======================================================================
30. PAIRED STATISTICAL DESIGN
======================================================================

All competing agents should receive identical:

task
initial state
fault
world seed
market
policy pack
exogenous randomness

Use paired inference.

Primary:
task-family clustered paired bootstrap.

Sensitivity:
McNemar for paired binary outcomes where appropriate.
Wilson/exact intervals for rare safety events.
Hierarchical logistic analysis where useful.

Do not treat correlated episodes as independent observations.

======================================================================
31. MULTI-SEED TRAINING
======================================================================

For finalist characterization run at least three independent training seeds for:

SFT
vanilla DPO
ACT-PO

Report separately:

training-seed uncertainty
evaluation-world uncertainty

Do not unnecessarily replicate every cheap deterministic baseline.

======================================================================
32. E17 POWER / MDE / FREEZE
======================================================================

Before protected internal outcome access:

use pilot/development evidence to determine:

- paired completion variability
- paired correlation
- critical-event rate
- practical MDE
- final protected sample sizes
- safety non-inferiority margin

Freeze:

candidate IDs
model hashes
adapter hashes
tool definitions
prompts
task generator
simulator versions
data roles
evaluation splits
statistics
sample sizes
promotion gates
secondary analysis plan

Write an immutable freeze manifest.

After freeze:
no result-driven tuning.

======================================================================
33. R-TRACE SAFETY FACTORIAL
======================================================================

Compare:

SFT / no guard
SFT / R-TRACE
ACT-PO / no guard
ACT-PO / R-TRACE

Measure:

completion
autonomous completion
safe completion
critical false-greenlight
unnecessary block
confirmation burden
critical violations
harm-weighted cost

Separate learned policy quality from execution-time guarding.

======================================================================
34. SECURITY
======================================================================

Internal adversarial tests:

indirect prompt injection
malicious tool output
tool-description injection
cross-account request
privilege escalation
confirmation bypass
synthetic secret exfiltration
policy poisoning
stale-state exploitation

Use synthetic honeytokens only.

Report:

attack success rate
unauthorized mutation
exfiltration
benign utility
false-positive defense cost

======================================================================
35. PREFERENCE-NOISE EXPERIMENT
======================================================================

Inject label flips:

0%
5%
10%
20%

Compare:

DPO
IPO
Robust-DPO
ACT-PO

Treat this as secondary method characterization.

Do not rewrite the primary result based on it.

======================================================================
36. ABLATIONS
======================================================================

Run:

A1 remove state matching
A2 remove common randomness
A3 replace lexicographic constraint ordering with scalar reward
A4 remove margin gate
A5 remove on-policy hard negatives
A6 remove severity balancing
A7 remove pair weighting
A8 DPO vs IPO vs Robust-DPO
A9 remove R-TRACE
A10 remove policy retrieval
A11 remove confirmation constraints
A12 remove public-data calibration
A13 remove Twin-B transfer layer
A14 remove SFT initialization if feasible

Primary mechanism ablations:

A3
A5
A7

Use efficient diagnostic subsets where full expensive retraining is unnecessary.

======================================================================
37. FAILURE TAXONOMY
======================================================================

Canonical failures:

F01 wrong tool
F02 wrong argument
F03 premature mutation
F04 missing evidence
F05 missed confirmation
F06 policy violation
F07 excessive mutation
F08 recovery failure
F09 tool loop
F10 hallucinated state
F11 prompt injection
F12 privilege escalation
F13 simulator exploit
F14 excessive abstention
F15 excessive cost

For every class report:

frequency
severity
model
task family
sample trajectory
recovery outcome

Generate a failure gallery.

======================================================================
38. TWIN-B TRANSFER
======================================================================

Evaluate only frozen finalists.

Report separately:

Twin-A ID
Twin-A OOD
Twin-B challenge

No Twin-B tuning.

If ACT-PO wins Twin-A but fails Twin-B catastrophically:
block broad generalization claims.

======================================================================
39. EXTERNAL BENCHMARKS
======================================================================

Core final-only benchmarks:

BFCL V4
tau3
AgentDojo

Optional:
ToolSandbox

Before first protected benchmark execution record:

repository
commit/tag
package version
license
model hash
adapter hash
prompt/config hash
access timestamp
access count

Do not use final benchmark examples for:

training
SFT
preference creation
prompt selection
threshold selection
hyperparameter selection
model selection

Treat results as:

external transfer evidence

not guaranteed-unseen evidence, because foundation-model pretraining contamination
cannot generally be proven absent.

======================================================================
40. BFCL
======================================================================

Use official current evaluator.

Evaluate frozen finalist configuration.

Record:

official metrics
tool correctness
latency
token/tool efficiency where feasible

No retuning after outcome access.

======================================================================
41. TAU3
======================================================================

Pin exact current revision and official evaluator semantics.

Use frozen configuration.

Record benchmark-version limitations.

No result-driven retuning.

======================================================================
42. AGENTDOJO
======================================================================

Pin exact current revision.

Use official methodology.

Measure:

benign utility
attack success
security/utility trade-off

No result-driven retuning.

======================================================================
43. SYSTEMS / SERVING
======================================================================

After model freeze compare where locally feasible:

HF Transformers

optional vLLM

Measure:

TTFT
end-to-end latency
tokens/sec
tasks/sec
VRAM
GPU utilization
failure rate
startup cost
shutdown/lifecycle reliability

Speed does not imply production readiness.

======================================================================
44. EVIDENCE WAREHOUSE
======================================================================

Create canonical machine-readable tables such as:

runs.parquet
episodes.parquet
steps.parquet
tool_calls.parquet
state_transitions.parquet
process_events.parquet
safety_events.parquet
preference_pairs.parquet
training_metrics.parquet
external_eval.parquet
systems_metrics.parquet
failures.parquet

Create DuckDB views:

vw_models
vw_task_family
vw_safety
vw_process
vw_ood
vw_twin_transfer
vw_security
vw_ablation
vw_latency
vw_cost

Final reports must derive numbers from validated canonical evidence.

======================================================================
45. EXPERIMENT DAG
======================================================================

Implement resumable orchestration for:

E00 Environment qualification

E01 Desktop study + current-source verification

E02 Data acquisition/provenance

E03 Public-data EDA/preprocessing

E04 Standards mapping

E05 Twin-A implementation/qualification

E06 Twin-B construction/sealing

E07 Task and deterministic user-simulator qualification

E08 Process-contract qualification

E09 B0-B2 baseline evaluation

E10 SFT development

E11 Trajectory/preference generation

E12 Preference audit

E13 DPO/IPO/Robust-DPO development

E14 ACT-pair unweighted DPO

E15 ACT-PO development

E16 Finalist multi-seed development replication

E17 Power/MDE + protected final freeze

E18 Protected internal ID evaluation

E19 Protected composition/policy/tool OOD

E20 Protected Twin-B transfer

E21 R-TRACE safety factorial

E22 Internal adversarial/security evaluation

E23 Preference-noise study

E24 Ablation suite

E25 BFCL V4 external evaluation

E26 tau3 external evaluation

E27 AgentDojo external evaluation

E28 Systems/serving qualification

E29 Final evidence + claim audit

Optional:

E30 ToolSandbox

Every stage must have a machine-readable receipt.

Exit code 0 alone does not imply PASS.

======================================================================
46. RESUMABILITY
======================================================================

Implement a command conceptually equivalent to:

act-agent run-all --protocol <protocol> --device cuda --resume

Also support stage-level execution.

STATUS.md and artifacts/run_state.json must track:

stage
state
start/end
inputs
outputs
hashes
blocker
next action

Completed immutable stages must not be recomputed under --resume unless a new
protocol identity explicitly requires it.

======================================================================
47. QUALITY GATES
======================================================================

Before final release run as applicable:

ruff format/check
mypy
pytest
coverage
package build
clean-wheel install
clean-wheel import smoke
CLI smoke
CPU smoke
CUDA smoke
evidence verifier
source/hash verifier
manifest verifier
claim verifier
report regeneration

Create CPU-safe GitHub Actions CI configuration.

Local GPU qualification is separate evidence.

Do not push GitHub.

======================================================================
48. FINAL VERDICT
======================================================================

The final scientific decision must be exactly one of:

PROMOTE_ACT_PO
PROMOTE_DPO
PROMOTE_IPO_OR_ROBUST
RETAIN_SFT
RETAIN_REACT
HOLD

ACT-PO may be promoted only if critical gates pass:

data integrity
simulator validity
process-evaluator validity
protected capability requirement
critical-safety non-inferiority
protected protocol integrity
no catastrophic Twin-B failure
no unacceptable security regression

Do not change the rule because ACT-PO loses.

======================================================================
49. REPORTS
======================================================================

Generate at least:

reports/executive_summary.md
reports/desktop_study.md
reports/data_card.md
reports/eda_report.md
reports/standards_mapping.md
reports/twin_a_card.md
reports/twin_b_card.md
reports/task_card.md
reports/process_contract_card.md
reports/preference_dataset_card.md
reports/model_cards/
reports/main_experiment.md
reports/ood_report.md
reports/twin_transfer_report.md
reports/safety_report.md
reports/security_report.md
reports/preference_noise_report.md
reports/ablation_report.md
reports/external_validation.md
reports/systems_report.md
reports/failure_gallery.md
reports/claim_ledger.md
reports/resume_bullets.md
reports/final_technical_report.md

If a reproducible local PDF toolchain is available also generate:

reports/ACT-Agent_Final_Technical_Report.pdf

Build a read-only evidence dashboard.

======================================================================
50. FINAL TECHNICAL REPORT
======================================================================

Cover:

Executive Summary
Problem / Motivation
Related Work
Public Data / Claim Boundaries
Industry Standards
Digital Twin
Agent Environment
Process Contracts
Tasks
Baseline Models
SFT
Preference Construction
ACT-PO
Experimental Protocol
Main Results
OOD / Twin-B
Safety
Security
Preference Noise
Ablations
External Benchmarks
GPU / Systems
Failure Analysis
Limitations
Final Decision
Reproducibility
Supported Claims
Prohibited Claims
Future Work

All plots/tables must derive from canonical evidence.

======================================================================
51. RESUME EVIDENCE
======================================================================

At completion generate 2-3 claim-safe resume bullets.

Use only executed results.

Do not pre-invent performance improvements.

======================================================================
52. GIT
======================================================================

Use local Git milestone commits where useful.

Do not push.

Do not erase negative scientific history.

Keep large raw/checkpoint/cache artifacts untracked.

If repository Git identity is absent:
either use repository-local neutral identity or continue without commits.

Do not block project progress for this.

======================================================================
53. FAILURE RECOVERY
======================================================================

Differentiate:

ENGINEERING_FAILURE
SCIENTIFIC_FAILURE
EXTERNAL_BLOCKER

Engineering failure:
repair implementation without changing scientific meaning.

Scientific failure:
preserve and continue according to protocol.

External blocker:
mark BLOCKED_EXTERNAL and continue unaffected stages.

Never relabel an unfavorable scientific result as an engineering defect.

======================================================================
54. AUTONOMY
======================================================================

Do not repeatedly ask:

"Should I continue?"

Continue automatically.

Short milestone updates are acceptable but do not stop execution afterward unless
user intervention is genuinely necessary.

Do not stop because:
- ACT-PO loses;
- a baseline wins;
- a security result is negative;
- an external benchmark is disappointing;
- an optional extension is blocked.

======================================================================
55. COMPLETION CHECKLIST
======================================================================

Before declaring completion verify:

E00-E29 terminal
optional E30 terminal if attempted

STATUS.md current

run_state.json current

source registry complete

protected-access ledger complete

freeze manifest present

model/adapter hashes present

canonical evidence validates

quality gates executed

final verdict present

supported claims linked to evidence

unsupported/prohibited claims blocked

reproduction instructions present

resume bullets present

limitations explicit

Create:

artifacts/final_verdict.json

The final terminal summary must report:

- final scientific verdict;
- strongest baseline;
- ACT-PO result;
- primary capability result;
- safety result;
- process-compliance result;
- Twin-B result;
- security result;
- external benchmark results;
- systems result;
- major negative findings;
- strongest defensible claims;
- unresolved limitations;
- final report paths;
- reproduction command.

======================================================================
56. START
======================================================================

Start now.

First inspect:
repository,
Git status,
AGENTS.md,
hardware,
scratch,
current source/data availability.

Create the execution plan and run-state artifacts.

Then continue directly through E00 and the complete end-to-end program.

Do not stop after planning.
