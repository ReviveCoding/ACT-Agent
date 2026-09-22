# act_pair-seed11-steps3-pairs64-noise00 model card

- Method: act_pair; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '97dc203ace25e6dd72cca7437135f2dfb38f09bf5e6a8deee06d5268d638f099'}`.
- Adapter config SHA-256: `e1cba4bf4963d270f74dfb9cff3951495d95986a7eafe1ee9a992fdcb19e0ae3`.
- Training receipt: `artifacts/training/act_pair-seed11-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.690150, 0.237463.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `61f346683f3cd1054b1974e258d7cc3065814833f226da41f1f810bc099458f6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
