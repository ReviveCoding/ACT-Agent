# act_po-seed23-sft30-steps3-pairs64-noise00 model card

- Method: act_po; seed: 23; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '8fd9e9ac347e6b5dbbf464aeba23eedd1e284030bed43b20f5d1ddc3b39d7471'}`.
- Adapter config SHA-256: `6e67c28812d30d3d83d23f121dca2447c0fe3acddeec3d7c71d9c1826c9edfdf`.
- Training receipt: `artifacts/training/act_po-seed23-sft30-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.442510, 0.000967.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `802ddfcc390943d38ba55404f32370f34bcd2ec800dd2cb3428edfffd179b5c1`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.33 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
