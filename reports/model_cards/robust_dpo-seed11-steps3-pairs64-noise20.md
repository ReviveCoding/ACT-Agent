# robust_dpo-seed11-steps3-pairs64-noise20 model card

- Method: robust_dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'ae6b25ee2a43a960348c3de9433a11121be412f66c9923e7a3fa7fa04722fd3c'}`.
- Adapter config SHA-256: `5277e3a90277fc0b4f2d2b1eb355000e7763a54b140ec2c4dee6d72c49245615`.
- Training receipt: `artifacts/training/robust_dpo-seed11-steps3-pairs64-noise20.json`.
- First and final recorded losses: 0.689400, 0.073069.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.2.
- Frozen SFT reference cache hash: `a362aeda7f48dc303834e2274f8e1a3b29319d0fb58f38d3af9a9ba30346d444`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
