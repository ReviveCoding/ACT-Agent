# dpo-seed23-sft30-steps3-pairs64-noise00 model card

- Method: dpo; seed: 23; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '3b935d712e9c2b829cefa089a7cd018f767ba3911f00361f9061bc9ffeacc512'}`.
- Adapter config SHA-256: `500a7be4ab9ee5365d16da5d617699a535d47a835ac09063fda30e03223372b9`.
- Training receipt: `artifacts/training/dpo-seed23-sft30-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.700040, 0.001503.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `802ddfcc390943d38ba55404f32370f34bcd2ec800dd2cb3428edfffd179b5c1`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.26 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
