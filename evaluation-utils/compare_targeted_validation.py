#!/usr/bin/env python3
"""Compare a small, targeted phenotype panel with AMRSearch results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def endpoint(value: str) -> tuple[str, str, str]:
    fields = value.split(":", 2)
    if len(fields) != 3 or not all(fields):
        raise argparse.ArgumentTypeError(
            "Endpoint must be LABEL:PHENOTYPE_COLUMN:AMRSEARCH_PROFILE"
        )
    return tuple(fields)  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--identifier-column", default="isolate")
    parser.add_argument("--result-pattern", default="{id}_amrsearch.jsn")
    parser.add_argument(
        "--endpoint",
        action="append",
        type=endpoint,
        required=True,
        metavar="LABEL:PHENOTYPE_COLUMN:AMRSEARCH_PROFILE",
    )
    args = parser.parse_args()

    with args.expected.open(newline="", encoding="utf-8-sig") as handle:
        expected_rows = list(csv.DictReader(handle))
    comparisons = []
    for expected in expected_rows:
        identifier = expected.get(args.identifier_column, "")
        if not identifier:
            raise ValueError(f"Missing {args.identifier_column!r} in expected table")
        result_path = args.results / args.result_pattern.format(id=identifier)
        result = json.loads(result_path.read_text(encoding="utf-8"))
        profiles = {item["agent"]["key"]: item for item in result["resistanceProfile"]}
        for label, phenotype_column, profile_key in args.endpoint:
            expected_state = (expected.get(phenotype_column) or "").strip().upper()
            if not expected_state:
                continue
            profile = profiles[profile_key]
            raw_state = profile["state"]
            predicted_state = "S" if raw_state == "NOT_FOUND" else raw_state[0]
            determinants = profile.get("determinants", {})
            acquired = [item["gene"] for item in determinants.get("acquired", [])]
            variants = [
                f'{item["gene"]} {item["variant"]}'
                for item in determinants.get("variants", [])
            ]
            comparisons.append(
                {
                    "identifier": identifier,
                    "endpoint": label,
                    "expected": expected_state,
                    "predicted": predicted_state,
                    "agreement": "yes" if predicted_state == expected_state else "no",
                    "acquired": "; ".join(acquired),
                    "variants": "; ".join(variants),
                    "result_file": result_path.name,
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(comparisons[0]) if comparisons else ["identifier", "endpoint", "expected", "predicted", "agreement", "acquired", "variants", "result_file"]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(comparisons)

    agreements = sum(row["agreement"] == "yes" for row in comparisons)
    lines = [
        "# Targeted AMRSearch validation results",
        "",
        f"Evaluated phenotype comparisons: {len(comparisons)}; agreements: {agreements}; discrepancies: {len(comparisons) - agreements}.",
        "",
        "| Identifier | Endpoint | Expected | Predicted | Determinants | Agreement |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in comparisons:
        determinants = "; ".join(filter(None, (row["acquired"], row["variants"]))) or "none"
        lines.append(
            f'| `{row["identifier"]}` | {row["endpoint"]} | {row["expected"]} | '
            f'{row["predicted"]} | {determinants} | {row["agreement"]} |'
        )
    lines.extend(["", "`NOT_FOUND` is interpreted as susceptible.", ""])
    args.summary.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
