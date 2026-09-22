# dpo-seed11-steps3-pairs64-noise00 model card

- Method: dpo; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'e54e9162b2012d8efed554b1e62211aa65ee98afb02ca9e5da6e52647b709aa6'}`.
- Adapter config SHA-256: `9ad317d27bae07de4627b2f9ad7217bc0e9e6634be0e6aab6acb0d1f2746978d`.
- Training receipt: `artifacts/training/dpo-seed11-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.690150, 0.232190.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `61f346683f3cd1054b1974e258d7cc3065814833f226da41f1f810bc099458f6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.16 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
