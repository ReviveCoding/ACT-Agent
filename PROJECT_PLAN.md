# ACT-Agent v1.0 execution plan

Protocol: `act-v1-20260920`. The authoritative contract is `MASTER_PROMPT.md`.

1. Qualify hardware, software, public sources, and public data (E00-E04).
2. Build and test transactional twins, task/user simulator, contracts, and local tools (E05-E08).
3. Run baseline, training, preference, and development experiments on the qualified CUDA device (E09-E16).
4. Freeze the protocol before protected outcomes, then run internal, security, transfer, and external evaluation (E17-E28).
5. Verify canonical evidence, regenerate reports, audit claims, and issue a verdict (E29).

Every stage has a machine-readable receipt. A stage cannot claim PASS from an exit code alone. GPU-heavy stages require a real CUDA computation. Protected evaluation cannot be opened until a valid freeze exists. Unavailable prerequisites are recorded explicitly and do not turn into numerical zeroes.
