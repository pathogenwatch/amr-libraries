#!/usr/bin/env python3
"""Prepare matched phenotype metadata and a Pathogenwatch FASTA request."""

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phenotypes", type=Path, required=True)
    parser.add_argument("--matches", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cohort", required=True, help="Cohort name used in --matches")
    parser.add_argument("--dataset-label", required=True)
    parser.add_argument("--identifier-column", default="biosample_accession")
    parser.add_argument("--match-result-field", default="name")
    parser.add_argument(
        "--nonsusceptible-column",
        action="append",
        default=[],
        help="Phenotype column to include in I/R cohort count; repeatable",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    match_payload = json.loads(args.matches.read_text(encoding="utf-8"))
    genomes = match_payload["cohorts"][args.cohort]["genomes"]
    by_name = {str(genome[args.match_result_field]): genome for genome in genomes}

    with args.phenotypes.open(newline="", encoding="utf-8-sig") as source:
        rows = list(csv.DictReader(source))
        source_fields = list(rows[0])

    matched_rows = []
    for row in rows:
        genome = by_name.get(row[args.identifier_column])
        if genome is None:
            continue
        matched_rows.append(
            {
                "catalogue_id": genome.get("id", ""),
                "catalogue_uuid": genome.get("uuid", ""),
                "catalogue_name": genome.get("name", ""),
                **row,
            }
        )

    if len(matched_rows) != len(genomes):
        raise ValueError(
            f"Metadata/match mismatch: {len(matched_rows)} rows for {len(genomes)} genomes"
        )

    phenotype_output = args.output_dir / "expected_phenotypes.csv"
    with phenotype_output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
                fieldnames=["catalogue_id", "catalogue_uuid", "catalogue_name", *source_fields],
        )
        writer.writeheader()
        writer.writerows(matched_rows)

    request_output = args.output_dir / "fasta_request.json"
    request_output.write_text(
        json.dumps({"ids": ",".join(str(row["catalogue_id"]) for row in matched_rows)})
        + "\n",
        encoding="utf-8",
    )

    nonsusceptible = None
    if args.nonsusceptible_column:
        nonsusceptible = sum(
            any(row.get(field, "").strip().upper() in {"I", "R"}
                for field in args.nonsusceptible_column)
            for row in matched_rows
        )

    manifest_output = args.output_dir / "dataset_manifest.json"
    manifest_output.write_text(
        json.dumps(
            {
                "dataset": args.dataset_label,
                "cohort": args.cohort,
                "identifier_column": args.identifier_column,
                "expected_fasta_count": len(matched_rows),
                "relevant_nonsusceptible_count": nonsusceptible,
                "excluded_missing_pathogenwatch_count": len(rows) - len(matched_rows),
                "expected_phenotypes_sha256": sha256(phenotype_output),
                "selection": "All source rows with an exact Pathogenwatch catalogue match",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
