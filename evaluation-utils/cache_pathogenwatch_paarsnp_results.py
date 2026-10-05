#!/usr/bin/env python3
"""Cache current Pathogenwatch analysis results for a validation set.

The Pathogenwatch collection API intentionally exposes flattened analysis data
but not the assembly checksum required by the analysis S3 key.  This utility
therefore resolves each genome UUID through the public details endpoint at a
conservative one request per second, then uses the documented AWS S3 path.
It is resumable: both the checksum mapping and downloaded results are retained.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_BASE = "https://pathogen.watch"
S3_BUCKET = "s3://analyses.pathogen.watch"


def api_checksum(api_base: str, uuid: str, api_key: str) -> str:
    url = f"{api_base}/api/genomes/details?{urllib.parse.urlencode({'id': uuid})}"
    request = urllib.request.Request(url, headers={"X-API-Key": api_key})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)
    checksum = data.get("checksum")
    if not isinstance(checksum, str) or not checksum:
        raise RuntimeError(f"Genome {uuid} has no assembly checksum")
    return checksum


def load_rows(path: Path, uuid_column: str, expected_count: int | None) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    unique_uuids = {row[uuid_column] for row in rows}
    if len(rows) != len(unique_uuids):
        raise RuntimeError("Expected one row per unique Pathogenwatch genome UUID")
    if expected_count is not None and len(rows) != expected_count:
        raise RuntimeError(f"Expected exactly {expected_count:,} genomes, found {len(rows):,}")
    return rows


def load_checksums(path: Path, uuid_column: str) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="") as handle:
        return {
            row[uuid_column]: row["checksum"]
            for row in csv.DictReader(handle)
        }


def write_checksums(
    path: Path, rows: list[dict[str, str]], checksums: dict[str, str], uuid_column: str
) -> None:
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[uuid_column, "checksum"])
        writer.writeheader()
        for row in rows:
            uuid = row[uuid_column]
            if uuid not in checksums:
                continue
            writer.writerow({uuid_column: uuid, "checksum": checksums[uuid]})
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--uuid-column", default="catalogue_uuid")
    parser.add_argument("--api-key", default=os.environ.get("PW_API_KEY"))
    parser.add_argument("--limit", type=int, help="Process at most this many unresolved genomes")
    parser.add_argument(
        "--expected-count",
        type=int,
        help="Fail unless source contains this many unique genomes",
    )
    parser.add_argument("--api-base", default=API_BASE)
    parser.add_argument(
        "--analysis-job",
        required=True,
        help="Pathogenwatch analysis job used in the S3 result path",
    )
    args = parser.parse_args()
    if not args.api_key:
        parser.error("Set PW_API_KEY or pass --api-key")

    rows = load_rows(args.source, args.uuid_column, args.expected_count)
    args.output.mkdir(parents=True, exist_ok=True)
    s3_prefix = f"{S3_BUCKET}/{args.analysis_job}"
    results_dir = args.output / "results"
    results_dir.mkdir(exist_ok=True)
    checksums_path = args.output / "checksums.csv"
    checksums = load_checksums(checksums_path, args.uuid_column)

    unresolved = [row for row in rows if row[args.uuid_column] not in checksums]
    if args.limit is not None:
        unresolved = unresolved[:args.limit]
    for index, row in enumerate(unresolved, start=1):
        started = time.monotonic()
        uuid = row[args.uuid_column]
        try:
            checksums[uuid] = api_checksum(args.api_base, uuid, args.api_key)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"Checksum lookup failed for {uuid}: HTTP {error.code}: {detail}") from error
        write_checksums(checksums_path, rows, checksums, args.uuid_column)
        if index % 25 == 0 or index == len(unresolved):
            print(f"resolved {len(checksums)}/{len(rows)} checksums", flush=True)
        time.sleep(max(0, 1 - (time.monotonic() - started)))

    downloaded = 0
    for row in rows:
        checksum = checksums.get(row[args.uuid_column])
        if checksum is None:
            continue
        destination = results_dir / f"{checksum}.json.gz"
        if destination.exists() and destination.stat().st_size:
            continue
        subprocess.run([
            "aws", "s3", "cp", f"{s3_prefix}/{checksum}", str(destination),
        ], check=True)
        downloaded += 1
        if downloaded % 25 == 0:
            print(f"downloaded {downloaded} results", flush=True)

    manifest = {
        "genome_count": len(rows),
        "resolved_checksum_count": len(checksums),
        "analysis_job": args.analysis_job,
        "source": s3_prefix + "/{checksum}",
        "result_suffix": ".json.gz",
        "cached_result_count": len(list(results_dir.glob("*.json.gz"))),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
