# dpo-seed11-steps3-pairs64-noise10 model card

- Method: dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'be9bbe05b3cc01dd9460360c1241c259e3de57e2f5c94ec0bd746ad255e00014'}`.
- Adapter config SHA-256: `cdc0e93f7bfa148fb4a5f496c6addbfa4ddcd8ee0b970907c586c5a168dea049`.
- Training receipt: `artifacts/training/dpo-seed11-steps3-pairs64-noise10.json`.
- First and final recorded losses: 0.690150, 0.238412.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.1.
- Frozen SFT reference cache hash: `01fb9a0d5142d1ac60669d1ece5196764f77b3af519e0222ba9a118bfb3fae29`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.16 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
