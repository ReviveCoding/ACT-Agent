# act_po-seed11-steps3-pairs64-noise00 model card

- Method: act_po; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': 'a1fc915a8c923f99c2f7a485aae59937da2a7abea6cae6d6e8726674565e35bd'}`.
- Adapter config SHA-256: `71cb295ca174aa3aab89696f91fa8f0165912c3d2b639714a3bfefaa9df1ee83`.
- Training receipt: `artifacts/training/act_po-seed11-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.596749, 0.195217.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `61f346683f3cd1054b1974e258d7cc3065814833f226da41f1f810bc099458f6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
