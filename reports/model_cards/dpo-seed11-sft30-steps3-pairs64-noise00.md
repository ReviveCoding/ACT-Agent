# dpo-seed11-sft30-steps3-pairs64-noise00 model card

- Method: dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '94dfe88b8b7bc0992dbaa2a61975efc6e88b46a7e92767a92c50e313227d5ff8'}`.
- Adapter config SHA-256: `87f4e3c2811c12f061661c1df27058e00710eb1d1d0a9846d7c777bbbcecea3e`.
- Training receipt: `artifacts/training/dpo-seed11-sft30-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.701467, 0.064685.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `430da0c08383b51af3befd0731d677c5750c277e520c8f997397ea7221ed10d6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.16 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
