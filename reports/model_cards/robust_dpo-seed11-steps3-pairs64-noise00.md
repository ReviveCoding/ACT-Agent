# robust_dpo-seed11-steps3-pairs64-noise00 model card

- Method: robust_dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'b8222908209718c8fd53178faad99282d59e66e91828377a76388f1bbd6bb413'}`.
- Adapter config SHA-256: `deeefd14ce3f84f5d56e3174ed82bb7a83a0d98383ecc90c2ea3789abed5c31c`.
- Training receipt: `artifacts/training/robust_dpo-seed11-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.689400, 0.062934.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `61f346683f3cd1054b1974e258d7cc3065814833f226da41f1f810bc099458f6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
