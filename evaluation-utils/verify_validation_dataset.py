#!/usr/bin/env python3
"""Verify an extracted Pathogenwatch validation dataset and update its manifest."""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_dir", type=Path)
    parser.add_argument(
        "--archive-name",
        default="validation-fasta.zip",
        help="Name of the downloaded FASTA archive within dataset_dir",
    )
    parser.add_argument(
        "--fasta-dir-name",
        default="fasta",
        help="Name of the extracted FASTA directory within dataset_dir",
    )
    parser.add_argument("--identifier-column", default="biosample_accession")
    parser.add_argument(
        "--fasta-identifier-regex",
        required=True,
        help="Regex with named group 'id' that extracts the expected identifier from FASTA filenames",
    )
    args = parser.parse_args()

    phenotype_path = args.dataset_dir / "expected_phenotypes.csv"
    manifest_path = args.dataset_dir / "dataset_manifest.json"
    archive_path = args.dataset_dir / args.archive_name
    fasta_dir = args.dataset_dir / args.fasta_dir_name

    with phenotype_path.open(newline="", encoding="utf-8") as handle:
        expected_rows = list(csv.DictReader(handle))
    expected_identifiers = {row[args.identifier_column] for row in expected_rows}

    fasta_paths = sorted(fasta_dir.glob("*.fasta"))
    identifier_pattern = re.compile(args.fasta_identifier_regex)
    observed_identifiers = set()
    invalid_identifier_names = []
    for path in fasta_paths:
        match = identifier_pattern.search(path.name)
        if match is None or "id" not in match.groupdict():
            invalid_identifier_names.append(path.name)
        else:
            observed_identifiers.add(match.group("id"))
    empty = [path.name for path in fasta_paths if path.stat().st_size == 0]
    invalid_headers = []
    for path in fasta_paths:
        with path.open("rb") as handle:
            if handle.read(1) != b">":
                invalid_headers.append(path.name)

    failures = {
        "missing_identifiers": sorted(expected_identifiers - observed_identifiers),
        "unexpected_identifiers": sorted(observed_identifiers - expected_identifiers),
        "unparseable_fasta_names": invalid_identifier_names,
        "empty_fasta": empty,
        "invalid_fasta_header": invalid_headers,
    }
    failures = {key: value for key, value in failures.items() if value}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "observed_fasta_count": len(fasta_paths),
            "fasta_total_bytes": sum(path.stat().st_size for path in fasta_paths),
            "archive_bytes": archive_path.stat().st_size,
            "archive_sha256": sha256(archive_path),
            "verification": "passed" if not failures else "failed",
            "verification_failures": failures,
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({key: manifest[key] for key in (
        "expected_fasta_count",
        "observed_fasta_count",
        "fasta_total_bytes",
        "archive_bytes",
        "archive_sha256",
        "verification",
        "verification_failures",
    )}, indent=2))
    return 0 if not failures and len(fasta_paths) == manifest["expected_fasta_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
