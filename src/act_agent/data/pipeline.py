"""Verified Criteo source and reproducible aggregate marts."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import duckdb

EXPECTED_SHA256 = "94ac7a465564349bc7ba008602211d5990a3c53cc133abc0aadef61ea2391a98"
SOURCE_URL = (
    "https://huggingface.co/datasets/criteo/criteo-attribution-dataset/resolve/main/"
    "criteo_attribution_dataset.tsv.gz"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else None,
    }


def verify(path: Path) -> dict[str, Any]:
    actual = sha256(path)
    if actual != EXPECTED_SHA256:
        raise ValueError(f"source checksum mismatch: {actual}")
    return {
        "sha256": actual,
        "bytes": path.stat().st_size,
        "source_url": SOURCE_URL,
        "license": "CC BY-NC-SA 4.0",
        "scientific_role": "observed distribution calibration",
        "redistribution_policy": "raw rows excluded from repository",
    }


def profile(path: Path, output: Path, scratch: Path) -> dict[str, Any]:
    verify(path)
    output.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    db_path = scratch / "profile.duckdb"
    db = duckdb.connect(str(db_path))
    db.execute("SET memory_limit='8GB'")
    db.execute(f"SET temp_directory='{scratch.as_posix()}/duckdb_tmp'")
    quoted = str(path).replace("'", "''")
    db.execute(
        f"CREATE OR REPLACE TABLE impressions AS SELECT * FROM read_csv('{quoted}', delim='\\t', header=true, compression='gzip', sample_size=200000)"
    )
    summary = db.execute("""SELECT count(*) AS rows, count(DISTINCT campaign) AS campaigns,
        count(DISTINCT uid) AS users, sum(click) AS clicks, sum(conversion) AS conversions,
        min(timestamp) AS min_timestamp, max(timestamp) AS max_timestamp,
        sum(cost) AS transformed_cost, count(*) FILTER (WHERE cost < 0) AS negative_cost,
        count(*) FILTER (WHERE click NOT IN (0,1) OR conversion NOT IN (0,1)) AS invalid_labels
        FROM impressions""").fetchone()
    assert summary is not None
    names = [x[0] for x in db.description]
    result = dict(zip(names, summary, strict=True))
    marts = {
        "campaign_hour": """SELECT campaign, CAST(floor(timestamp / 3600) AS BIGINT) AS hour,
            count(*) AS impressions, sum(click) AS clicks, sum(conversion) AS conversions,
            sum(cost) AS transformed_cost FROM impressions GROUP BY 1,2""",
        "campaign_day": """SELECT campaign, CAST(floor(timestamp / 86400) AS BIGINT) AS day,
            count(*) AS impressions, sum(click) AS clicks, sum(conversion) AS conversions,
            sum(cost) AS transformed_cost FROM impressions GROUP BY 1,2""",
        "campaign_profile": """SELECT campaign, count(*) AS impressions, sum(click) AS clicks,
            sum(conversion) AS conversions, avg(cost) AS mean_transformed_cost,
            avg(click) AS ctr, sum(conversion) / nullif(sum(click),0) AS cvr
            FROM impressions GROUP BY 1""",
        "user_path": """SELECT campaign, count(*) AS users, avg(path_length) AS mean_path_length,
            max(path_length) AS max_path_length, avg(clicks) AS mean_clicks,
            avg(conversions) AS mean_conversions FROM (
              SELECT campaign, uid, count(*) AS path_length, sum(click) AS clicks,
              sum(conversion) AS conversions FROM impressions GROUP BY 1,2
            ) GROUP BY 1""",
        "distribution_fit": """SELECT approx_quantile(cost, [0.01,0.1,0.5,0.9,0.99]) AS cost_quantiles,
            avg(click) AS ctr, avg(conversion) AS impression_conversion_rate,
            approx_quantile(timestamp % 86400, [0.1,0.5,0.9]) AS time_of_day_quantiles
            FROM impressions""",
    }
    for name, query in marts.items():
        destination = output / f"{name}.parquet"
        db.execute(f"COPY ({query}) TO '{destination.as_posix()}' (FORMAT PARQUET)")
        db.execute(
            f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet('{destination.as_posix()}')"
        )

    def mart_rows(name: str) -> int:
        row = db.execute(f"SELECT count(*) FROM {name}").fetchone()
        assert row is not None
        return int(row[0])

    result["marts"] = {
        name: {
            "rows": mart_rows(name),
            "sha256": sha256(output / f"{name}.parquet"),
        }
        for name in marts
    }
    result["schema_hash"] = hashlib.sha256(
        str(db.execute("DESCRIBE impressions").fetchall()).encode()
    ).hexdigest()
    db.close()
    receipt = output / "profile.json"
    temp = receipt.with_suffix(".json.tmp")
    temp.write_text(json.dumps(result, indent=2, default=str) + "\n")
    os.replace(temp, receipt)
    return result
