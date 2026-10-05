#!/usr/bin/env python3
"""Compare AMRSearch prediction JSON files with a phenotype table.

Endpoint mappings are supplied at runtime, so the utility is not tied to one
organism, drug panel, or AMR library.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


SIR = {"S", "I", "R"}
ERROR_CATEGORIES = {
    "RESISTANCE_ASSIGNED_TO_S": "Resistance (I/R) assigned to phenotype S",
    "NO_RESISTANCE_ASSIGNED_TO_IR": "No resistance assigned to phenotype I/R",
    "INCORRECT_IR_TIER": "I/R assignment has the wrong tier",
}


def parse_endpoint(value: str) -> tuple[str, str, str]:
    """Parse LABEL:PHENOTYPE_COLUMN:AMRSEARCH_PROFILE."""
    fields = value.split(":", 2)
    if len(fields) != 3 or not all(fields):
        raise argparse.ArgumentTypeError(
            "Endpoint must be LABEL:PHENOTYPE_COLUMN:AMRSEARCH_PROFILE"
        )
    return tuple(fields)  # type: ignore[return-value]


def parse_state(value: str) -> tuple[str, str]:
    fields = value.split("=", 1)
    if len(fields) != 2 or fields[1] not in SIR:
        raise argparse.ArgumentTypeError("State mapping must be AMRSEARCH_STATE=S, I, or R")
    return tuple(fields)  # type: ignore[return-value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument(
        "--endpoint",
        action="append",
        type=parse_endpoint,
        required=True,
        metavar="LABEL:PHENOTYPE_COLUMN:AMRSEARCH_PROFILE",
        help="Repeat for every phenotype comparison to make",
    )
    parser.add_argument("--identifier-column", default="biosample_accession")
    parser.add_argument("--label-column", default="isolate")
    parser.add_argument(
        "--result-identifier-regex",
        required=True,
        help="Regex with named group 'id' that extracts the table identifier from a result filename",
    )
    parser.add_argument("--result-glob", default="*_amrsearch.jsn")
    parser.add_argument(
        "--state",
        action="append",
        type=parse_state,
        default=[
            ("NOT_FOUND", "S"),
            ("SUSCEPTIBLE", "S"),
            ("INTERMEDIATE", "I"),
            ("RESISTANT", "R"),
        ],
        metavar="AMRSEARCH_STATE=SIR",
        help="Map an AMRSearch state to S/I/R; repeatable",
    )
    return parser.parse_args()


def category(expected: str, predicted: str) -> str:
    if expected == "S" and predicted in {"I", "R"}:
        return "RESISTANCE_ASSIGNED_TO_S"
    if expected in {"I", "R"} and predicted == "S":
        return "NO_RESISTANCE_ASSIGNED_TO_IR"
    if expected in {"I", "R"} and predicted in {"I", "R"} and expected != predicted:
        return "INCORRECT_IR_TIER"
    return ""


def load_expected(path: Path, identifier_column: str) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    identifiers = [row.get(identifier_column, "") for row in rows]
    if not all(identifiers):
        raise ValueError(f"Missing {identifier_column!r} in expected phenotype table")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError(f"Duplicate {identifier_column!r} values in expected phenotype table")
    return dict(zip(identifiers, rows))


def load_results(
    directory: Path, result_glob: str, identifier_pattern: re.Pattern[str]
) -> tuple[dict[str, tuple[Path, dict]], list[str]]:
    results: dict[str, tuple[Path, dict]] = {}
    errors: list[str] = []
    for result_path in sorted(directory.glob(result_glob)):
        match = identifier_pattern.search(result_path.name)
        if match is None or "id" not in match.groupdict():
            errors.append(f"No named identifier match in {result_path.name}")
            continue
        identifier = match.group("id")
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid JSON {result_path.name}: {exc}")
            continue
        if identifier in results:
            errors.append(f"Duplicate result for {identifier}")
            continue
        results[identifier] = (result_path, result)
    return results, errors


def profiles(result: dict) -> dict[str, dict]:
    return {
        entry["agent"]["key"]: entry
        for entry in result.get("resistanceProfile", [])
        if entry.get("agent", {}).get("key")
    }


def main() -> None:
    options = parse_args()
    endpoints = options.endpoint
    endpoint_labels = [item[0] for item in endpoints]
    if len(set(endpoint_labels)) != len(endpoint_labels):
        raise ValueError("Endpoint labels must be unique")
    state_to_sir = dict(options.state)
    expected = load_expected(options.expected, options.identifier_column)
    results, result_errors = load_results(
        options.results, options.result_glob, re.compile(options.result_identifier_regex)
    )
    options.outdir.mkdir(parents=True, exist_ok=True)

    missing = sorted(set(expected) - set(results))
    unexpected = sorted(set(results) - set(expected))
    matrices = {label: Counter() for label in endpoint_labels}
    rows: list[dict[str, str]] = []
    wide_rows: list[dict[str, str]] = []

    for identifier in sorted(set(expected) & set(results)):
        phenotype = expected[identifier]
        result_path, result = results[identifier]
        result_profiles = profiles(result)
        acquired = ";".join(sorted(result.get("acquired", [])))
        variants = ";".join(sorted(result.get("variants", [])))
        wide = {
            "identifier": identifier,
            "label": phenotype.get(options.label_column, ""),
            "acquired": acquired,
            "variants": variants,
            "result_file": result_path.name,
        }
        for label, phenotype_column, profile_key in endpoints:
            expected_sir = phenotype.get(phenotype_column, "").strip().upper()
            profile = result_profiles.get(profile_key)
            raw_state = (profile or {}).get("state", "MISSING_PROFILE")
            predicted_sir = state_to_sir.get(raw_state, "?")
            wide[f"expected_{label}"] = expected_sir
            wide[f"predicted_{label}"] = predicted_sir
            if expected_sir not in SIR:
                continue
            determinant_rules = ";".join(sorted((profile or {}).get("determinantRules", {})))
            agreement = expected_sir == predicted_sir
            error_category = category(expected_sir, predicted_sir)
            matrices[label][(expected_sir, predicted_sir)] += 1
            rows.append(
                {
                    "identifier": identifier,
                    "label": phenotype.get(options.label_column, ""),
                    "endpoint": label,
                    "amrsearch_profile": profile_key,
                    "expected": expected_sir,
                    "predicted": predicted_sir,
                    "agreement": str(agreement).lower(),
                    "error_category": error_category,
                    "determinant_rules": determinant_rules,
                    "acquired": acquired,
                    "variants": variants,
                    "result_file": result_path.name,
                }
            )
        wide_rows.append(wide)

    long_fields = [
        "identifier", "label", "endpoint", "amrsearch_profile", "expected", "predicted",
        "agreement", "error_category", "determinant_rules", "acquired", "variants", "result_file",
    ]
    wide_fields = ["identifier", "label", "acquired", "variants", "result_file"]
    for label in endpoint_labels:
        wide_fields.extend((f"expected_{label}", f"predicted_{label}"))
    outputs = (
        ("comparison.csv", wide_rows, wide_fields),
        ("endpoint_comparison.csv", rows, long_fields),
        ("discordances.csv", [row for row in rows if row["agreement"] == "false"], long_fields),
    )
    for filename, selected_rows, fieldnames in outputs:
        with (options.outdir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(selected_rows)
    for error, filename in (
        ("RESISTANCE_ASSIGNED_TO_S", "resistance_assigned_to_s.csv"),
        ("NO_RESISTANCE_ASSIGNED_TO_IR", "no_resistance_assigned_to_ir.csv"),
        ("INCORRECT_IR_TIER", "incorrect_ir_tier.csv"),
    ):
        with (options.outdir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=long_fields)
            writer.writeheader()
            writer.writerows(row for row in rows if row["error_category"] == error)

    endpoint_summary = {}
    for label, matrix in matrices.items():
        evaluated = sum(matrix.values())
        endpoint_summary[label] = {
            "evaluated": evaluated,
            "agreements": sum(count for (expected_sir, predicted), count in matrix.items() if expected_sir == predicted),
            "matrix": {
                expected_sir: {predicted: matrix[(expected_sir, predicted)] for predicted in ("S", "I", "R", "?")}
                for expected_sir in ("S", "I", "R")
            },
        }
    summary = {
        "expected_genomes": len(expected),
        "result_files": len(results),
        "matched_genomes": len(set(expected) & set(results)),
        "missing_results": missing,
        "unexpected_results": unexpected,
        "result_errors": result_errors,
        "endpoint_mappings": [
            {"label": label, "phenotype_column": column, "amrsearch_profile": profile}
            for label, column, profile in endpoints
        ],
        "endpoints": endpoint_summary,
    }
    (options.outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# AMRSearch validation summary", "", f"- Expected genomes: {len(expected):,}",
        f"- Result files: {len(results):,}", f"- Matched genomes: {len(set(expected) & set(results)):,}",
        f"- Missing results: {len(missing):,}", f"- Unexpected results: {len(unexpected):,}",
        f"- Result-file errors: {len(result_errors):,}", "",
        "| Endpoint | Comparisons | Agreements | Discordances |",
        "| --- | ---: | ---: | ---: |",
    ]
    for label, item in endpoint_summary.items():
        lines.append(f"| {label} | {item['evaluated']:,} | {item['agreements']:,} | {item['evaluated'] - item['agreements']:,} |")
    lines.extend(["", "Rows are phenotypes and columns are AMRSearch predictions.", ""])
    for label, item in endpoint_summary.items():
        lines.extend([f"## {label}", "", "| Expected \\ Predicted | S | I | R | Unknown |", "| --- | ---: | ---: | ---: | ---: |"])
        for expected_sir, matrix in item["matrix"].items():
            lines.append(f"| {expected_sir} | {matrix['S']:,} | {matrix['I']:,} | {matrix['R']:,} | {matrix['?']:,} |")
        lines.append("")
    (options.outdir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    if missing or unexpected or result_errors:
        raise SystemExit("Result-set validation failed; see summary.json")


if __name__ == "__main__":
    main()
