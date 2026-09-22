# act_po-seed37-sft30-steps3-pairs64-noise00 model card

- Method: act_po; seed: 37; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '817dbb4d8f03360be832f47d3b5b80d9eaca870157e583bc930e254728c42e3a'}`.
- Adapter config SHA-256: `f4a28c6d2adf655ea2a02491d8a95022a6ec3f31167e93fe1c1bfc136157aff9`.
- Training receipt: `artifacts/training/act_po-seed37-sft30-steps3-pairs64-noise00.json`.
- First and final recorded losses: 0.870856, 0.254275.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.0.
- Frozen SFT reference cache hash: `30084859d0022e60a9f9ce56135e66575586866d76c1f5dc6c1fad2c06bfce36`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.47 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
