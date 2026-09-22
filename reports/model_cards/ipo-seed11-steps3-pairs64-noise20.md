# ipo-seed11-steps3-pairs64-noise20 model card

- Method: ipo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '87d4bf629f96ec699b474ab3ab98fc136a96f05bdb0f0b6e979ae21b54e50a1f'}`.
- Adapter config SHA-256: `f2158a181ee4bd0d52187f2c898a8415e5eadbff00faf6550e603262806cc2ac`.
- Training receipt: `artifacts/training/ipo-seed11-steps3-pairs64-noise20.json`.
- First and final recorded losses: 24.994955, 23.875603.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.2.
- Frozen SFT reference cache hash: `a362aeda7f48dc303834e2274f8e1a3b29319d0fb58f38d3af9a9ba30346d444`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
