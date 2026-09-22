# robust_dpo-seed11-steps3-pairs64-noise10 model card

- Method: robust_dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '768f188b668683f95ad7c9f050e5e551a7283efeceaeac6bdef8a98a3e176284'}`.
- Adapter config SHA-256: `47c986c5826de56b2a2b520e0606336f752778afad204ccbcb0bc6a663e6a84f`.
- Training receipt: `artifacts/training/robust_dpo-seed11-steps3-pairs64-noise10.json`.
- First and final recorded losses: 0.689400, 0.048622.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.1.
- Frozen SFT reference cache hash: `01fb9a0d5142d1ac60669d1ece5196764f77b3af519e0222ba9a118bfb3fae29`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
