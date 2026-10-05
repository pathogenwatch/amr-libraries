#!/usr/bin/env python3
"""Match accession lists to public/shared organism records in Pathogenwatch.

Only catalogue metadata are requested. The API key is read from PW_API_KEY and
is never written to output.
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def read_accessions(path: Path) -> set[str]:
    accessions: set[str] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        delimiter = csv.Sniffer().sniff(sample, delimiters=",\t").delimiter
        for row in csv.DictReader(handle, delimiter=delimiter):
            for field in (
                "accession",
                "biosample_accession",
                "sample_accession",
                "secondary_sample_accession",
            ):
                value = (row.get(field) or "").strip()
                if value:
                    accessions.add(value)
    return accessions


def request_page(
    api_url: str, api_key: str, organism_id: str, page_size: int, after: str | None
) -> dict:
    query = {"limit": str(page_size)}
    if after:
        query["after"] = after
    url = api_url + "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(
        url,
        data=json.dumps({"organismId": organism_id}).encode(),
        headers={"Content-Type": "application/json", "X-API-Key": api_key},
        method="POST",
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", action="append", nargs=2, metavar=("NAME", "TSV"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--organism-id", required=True, help="Pathogenwatch organism identifier")
    parser.add_argument(
        "--api-url",
        default="https://pathogen.watch/api/search/genomes",
        help="Pathogenwatch catalogue-search endpoint",
    )
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument(
        "--record-field",
        action="append",
        default=["name", "uuid"],
        help="Genome response field to compare with cohort identifiers; repeatable",
    )
    args = parser.parse_args()

    api_key = os.environ.get("PW_API_KEY")
    if not api_key:
        print("PW_API_KEY is required", file=sys.stderr)
        return 2

    cohorts = {name: read_accessions(Path(path)) for name, path in args.cohort}
    matches = {name: [] for name in cohorts}
    after = None
    catalogue_count = None
    pages = 0

    while True:
        payload = request_page(args.api_url, api_key, args.organism_id, args.page_size, after)
        pages += 1
        meta = payload["meta"]
        catalogue_count = meta["count"]
        for genome in payload["genomes"]:
            identifiers = {str(genome.get(field, "")) for field in args.record_field}
            for cohort, accessions in cohorts.items():
                if identifiers & accessions:
                    matches[cohort].append(genome)
        next_after = meta.get("endCursor")
        if meta.get("empty") or not payload["genomes"] or not next_after or next_after == after:
            break
        after = next_after

    result = {
        "catalogue_count": catalogue_count,
        "organism_id": args.organism_id,
        "pages_examined": pages,
        "cohorts": {
            name: {
                "input_accession_count": len(cohorts[name]),
                "matched_genome_count": len(genomes),
                "genomes": genomes,
            }
            for name, genomes in matches.items()
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
