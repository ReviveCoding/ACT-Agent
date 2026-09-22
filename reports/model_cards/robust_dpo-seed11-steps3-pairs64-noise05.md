# robust_dpo-seed11-steps3-pairs64-noise05 model card

- Method: robust_dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '31dc41ba670be28552fa28b014ec16ad41e5bccc271c26fceadd246370ae246b'}`.
- Adapter config SHA-256: `81d7c63396e46cc177d5792a024a0f91eeba7fadced92b7af97477f67d8d9f41`.
- Training receipt: `artifacts/training/robust_dpo-seed11-steps3-pairs64-noise05.json`.
- First and final recorded losses: 0.689400, 0.066576.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.05.
- Frozen SFT reference cache hash: `8152661bcba7f520ef65d0e4dc1273006bd77145d3f2c11d85513f397f1d55e6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
