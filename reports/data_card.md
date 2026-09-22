# Data card: Criteo attribution anchor

Source: https://ailab.criteo.com/criteo-attribution-modeling-bidding-dataset/ and Criteo-owned mirror https://huggingface.co/datasets/criteo/criteo-attribution-dataset. File SHA-256: `94ac7a465564349bc7ba008602211d5990a3c53cc133abc0aadef61ea2391a98`. License: CC BY-NC-SA 4.0. Research use must preserve attribution and respect noncommercial and ShareAlike terms.

16,468,027 impression rows, 675 campaign IDs, 6,142,256 user IDs. The public file is anonymized and subsampled. `cost` is transformed; it is not spend in dollars. Conversion flags can repeat across impressions, so 806,196 flagged rows are not unique conversion events. No real advertiser control or action-effect identification is available.

Raw rows live only in WSL scratch. Repository marts are aggregates. `data/processed/profile.json` records checksums, schema hash, and aggregate counts. Source provenance is in `artifacts/source_registry.json`.

## Criteo Uplift v2.1

The Criteo-owned public mirror at `criteo/criteo-uplift`, revision
`2424920019e49d52d72c13ac1143ec5d53af276b`, supplied
`criteo-research-uplift-v2.1.csv.gz` (SHA-256
`2716e1bf0fd157a93b5bf86924d9088419dfbac2022c6cd90030220634f616dc`).
The gzip stream passed integrity validation. The file contains 13,979,592 user rows,
11 feature columns, a treatment indicator, and conversion, visit, and exposure
flags. Its treatment count is 11,882,655 and its conversion flag count is 40,774;
core labels have no nulls. The file is CC BY-NC-SA 4.0. The exact-file row
count differs from the broader dataset description; analysis uses the verified
file count. See `artifacts/uplift_profile.json` for the query result and source
hash. This data can anchor observed randomized-treatment distributions, but
does not identify the effects of the mutable campaign actions in the local twin.
