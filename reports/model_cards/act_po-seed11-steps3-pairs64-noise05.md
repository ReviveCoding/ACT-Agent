# act_po-seed11-steps3-pairs64-noise05 model card

- Method: act_po; seed: 11; optimizer steps: 3.
- Base model hash: `ac79c0b15abda13fcc6a54ab44bbafbde19681d45737f982a145ca9fc5708a2f`.
- Adapter file SHA-256: `{'adapter_model.safetensors': '64c127d36826e47a870a25106fcf7fb2a6a14e3b7b43e750411b4b6349bf0669'}`.
- Adapter config SHA-256: `0f482f051e7d647232a64a5f59a06805fef93bcb39c347dfda93272dadfab34e`.
- Training receipt: `artifacts/training/act_po-seed11-steps3-pairs64-noise05.json`.
- First and final recorded losses: 0.596749, 0.199643.
- Preference source hash: `9eda6b8f75c4db636c6d5d1fc349bcae9f1696574a3450a341a28c03b33b331e`.
- Pairs: 64; beta: 0.1; label-flip rate: 0.05.
- Frozen SFT reference cache hash: `8152661bcba7f520ef65d0e4dc1273006bd77145d3f2c11d85513f397f1d55e6`.
- Candidate source is scripted development perturbations; full on-policy ACT-PO is not qualified.
- Peak reserved VRAM: 8.35 GiB.

This adapter was trained on synthetic local tasks. Training loss alone is not task capability, safety, or production evidence. Protected outcomes were not used for training or selection.
