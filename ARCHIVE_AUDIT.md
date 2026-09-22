# ACT-Agent v1.0 local archival audit

The scientific release remains immutable: verdict **HOLD**, 30 terminal stages, and zero protected internal or external outcome accesses. This audit classifies each of the 561 non-Git files in the working tree; the exact path-level inventory is in `ARCHIVE_FILE_CLASSIFICATION.csv`.

| Classification | Files | Staged |
|---|---:|---:|
| INCLUDE_IN_RELEASE | 406 | yes |
| GENERATED_REPRODUCIBLE | 45 | only canonical files pinned by the release manifest |
| LOCAL_ONLY | 110 | no |
| SECRET_OR_FORBIDDEN | 0 | no |

Proposed staged files: **448**. Every one of the 437 files pinned by `artifacts/release_manifest.json` is included. Two pinned files require an explicit Git override: `artifacts/warehouse/evidence.duckdb` (274 KiB canonical warehouse) and `src/act_agent/__pycache__/__init__.py` (36-byte Python text stub, not bytecode). All other caches and generated build outputs remain local.

The repository contains no raw Criteo rows, model weights, checkpoints, or large scratch artifacts. The five `data/processed/*.parquet` files contain campaign/time aggregates or fitted statistics; their schemas contain no user identifier or impression-level row. The largest proposed file is `data/processed/campaign_hour.parquet` at 5.64 MB. Filename and content scans found no real credential, private key, password, or common API token pattern among proposed files. Synthetic security evidence is retained as part of the audited report.

`act-agent verify`, `act-agent run-all --resume`, and all 437 release-manifest hashes passed before staging. This archive audit and the `.gitignore` cleanup do not alter any experiment, terminal receipt, protected-access ledger, scientific result, or release-manifest entry. No commit, push, or public release is authorized by this audit.

Git initially normalized `AGENTS.md` and `MASTER_PROMPT.md` in the index. Exact `.gitattributes` exceptions now preserve their original bytes, so the staged blobs match the immutable manifest hashes. This changes only checkout behavior for those two files.

`MASTER_PROMPT.sha256` now has an LF terminator, so `sha256sum -c MASTER_PROMPT.sha256` passes locally. `git diff --check` still reports CRLF as trailing whitespace in the two immutable contract files and a final blank line in `artifacts/interim_sandbox_blocked/final_technical_report.md`; their historical bytes were left intact.
