#!/usr/bin/env python3
"""List AMR-library rules not directly tested by a validation dataset."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


SIR = {"S", "I", "R"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument(
        "--endpoint",
        action="append",
        required=True,
        metavar="PROFILE=COLUMN[,COLUMN...]",
        help="Map a library phenotype profile to comparison.csv expected columns; repeatable",
    )
    return parser.parse_args()


def endpoint_columns(values: list[str]) -> dict[str, tuple[str, ...]]:
    result = {}
    for value in values:
        profile, separator, columns = value.partition("=")
        parsed_columns = tuple(column for column in columns.split(",") if column)
        if not separator or not profile or not parsed_columns:
            raise ValueError("Endpoint must be PROFILE=COLUMN[,COLUMN...]")
        result[profile] = parsed_columns
    return result


def marker_sets(row: dict[str, str]) -> tuple[set[str], set[str]]:
    return (
        {value for value in row["acquired"].split(";") if value},
        {value for value in row["variants"].split(";") if value},
    )


def member_present(member: dict, acquired: set[str], variants: set[str]) -> bool:
    gene = member["gene"]
    required_variants = member.get("variants", [])
    if required_variants:
        return any(f"{gene}_{variant}" in variants for variant in required_variants)
    return gene in acquired


def member_label(member: dict) -> str:
    variants = member.get("variants", [])
    if variants:
        return f"{member['gene']} " + "/".join(variants)
    return member["gene"]


def has_target_phenotype(
    row: dict[str, str], targets: set[str], columns_by_profile: dict[str, tuple[str, ...]]
) -> bool:
    return any(
        row.get(column, "") in SIR
        for target in targets
        for column in columns_by_profile.get(target, ())
    )


def main() -> None:
    options = parse_args()
    columns_by_profile = endpoint_columns(options.endpoint)
    library = json.loads(options.library.read_text())
    with options.comparison.open(newline="") as handle:
        genomes = list(csv.DictReader(handle))

    records: list[dict[str, object]] = []
    for name, rule in sorted(library["sets"].items()):
        phenotypes = rule["phenotypes"]
        targets = {target for phenotype in phenotypes for target in phenotype["profile"]}
        effects = {phenotype["effect"] for phenotype in phenotypes}
        members = rule["members"]
        complete = 0
        complete_with_ast = 0
        partial = 0
        partial_with_ast = 0
        for genome in genomes:
            acquired, variants = marker_sets(genome)
            present = sum(member_present(member, acquired, variants) for member in members)
            ast = has_target_phenotype(genome, targets, columns_by_profile)
            if present == len(members):
                complete += 1
                complete_with_ast += ast
            elif present:
                partial += 1
                partial_with_ast += ast

        has_endpoint = any(target in columns_by_profile for target in targets)
        if not has_endpoint:
            status = "NO_MATCHING_PHENOTYPE"
        elif complete == 0 and partial and "INTERMEDIATE_ADDITIVE" in effects:
            status = "ADDITIVE_PARTIAL_ONLY"
        elif complete == 0:
            status = "NO_COMPLETE_GENOTYPE"
        elif complete_with_ast == 0:
            status = "COMPLETE_WITHOUT_PHENOTYPE"
        else:
            status = "TESTED"

        records.append(
            {
                "rule": name,
                "rule_type": "phenotype",
                "members": " + ".join(member_label(member) for member in members),
                "effects": ";".join(sorted(effects)),
                "profiles": ";".join(sorted(targets)),
                "status": status,
                "complete_genomes": complete,
                "complete_with_phenotype": complete_with_ast,
                "partial_genomes": partial,
                "partial_with_phenotype": partial_with_ast,
            }
        )

        for phenotype in phenotypes:
            for modifier in phenotype.get("modifiers", []):
                modifier_targets = set(phenotype["profile"])
                relevant = 0
                relevant_with_ast = 0
                for genome in genomes:
                    acquired, variants = marker_sets(genome)
                    parent_present = all(member_present(member, acquired, variants) for member in members)
                    modifier_present = member_present(modifier, acquired, variants)
                    if parent_present and modifier_present:
                        relevant += 1
                        relevant_with_ast += has_target_phenotype(genome, modifier_targets, columns_by_profile)
                has_modifier_endpoint = any(target in columns_by_profile for target in modifier_targets)
                if not has_modifier_endpoint:
                    modifier_status = "NO_MATCHING_PHENOTYPE"
                elif relevant == 0:
                    modifier_status = "NO_COMPLETE_GENOTYPE"
                elif relevant_with_ast == 0:
                    modifier_status = "COMPLETE_WITHOUT_PHENOTYPE"
                else:
                    modifier_status = "TESTED"
                records.append(
                    {
                        "rule": f"{name} modifier: {member_label(modifier)} {modifier['effect']}",
                        "rule_type": "modifier",
                        "members": f"{member_label(modifier)} (with parent {name})",
                        "effects": modifier["effect"],
                        "profiles": ";".join(sorted(modifier_targets)),
                        "status": modifier_status,
                        "complete_genomes": relevant,
                        "complete_with_phenotype": relevant_with_ast,
                        "partial_genomes": 0,
                        "partial_with_phenotype": 0,
                    }
                )

    untested = [record for record in records if record["status"] != "TESTED"]
    fieldnames = [
        "rule", "rule_type", "members", "effects", "profiles", "status",
        "complete_genomes", "complete_with_phenotype", "partial_genomes",
        "partial_with_phenotype",
    ]
    options.csv.parent.mkdir(parents=True, exist_ok=True)
    with options.csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(untested)

    counts = Counter(record["status"] for record in records)
    markdown = [
        "# Rules untested by the validation cohort",
        "",
        f"Library: `{library['version']['label']}` version `{library['version']['version']}`.",
        f"Genomes evaluated: {len(genomes):,}.",
        "",
        "A rule is counted as tested only when its complete genotype was found",
        "in an isolate having a corresponding phenotype. For additive rules,",
        "`ADDITIVE_PARTIAL_ONLY` means at least one member was observed but the",
        "complete combination was not. `NO_MATCHING_PHENOTYPE` means the library",
        "profile was not mapped to a phenotype column. Suppressor conditions are",
        "listed separately from their parent",
        "rules.",
        "",
        "## Summary",
        "",
        "| Status | Rules/conditions |",
        "| --- | ---: |",
    ]
    for status in (
        "TESTED", "NO_COMPLETE_GENOTYPE", "ADDITIVE_PARTIAL_ONLY",
        "NO_MATCHING_PHENOTYPE", "COMPLETE_WITHOUT_PHENOTYPE",
    ):
        markdown.append(f"| {status} | {counts[status]:,} |")

    for status in (
        "NO_COMPLETE_GENOTYPE", "ADDITIVE_PARTIAL_ONLY",
        "NO_MATCHING_PHENOTYPE", "COMPLETE_WITHOUT_PHENOTYPE",
    ):
        selected = [record for record in untested if record["status"] == status]
        if not selected:
            continue
        markdown.extend(
            [
                "",
                f"## {status}",
                "",
                "| Profiles | Rule/condition | Members | Complete | Partial |",
                "| --- | --- | --- | ---: | ---: |",
            ]
        )
        for record in selected:
            markdown.append(
                f"| {record['profiles']} | `{record['rule']}` | "
                f"`{record['members']}` | {record['complete_genomes']} | "
                f"{record['partial_genomes']} |"
            )

    options.markdown.write_text("\n".join(markdown) + "\n")


if __name__ == "__main__":
    main()
