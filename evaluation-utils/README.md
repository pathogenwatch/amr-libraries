# AMR-library release evaluation utilities

These standard-library-only Python 3 utilities prepare validation inputs and
produce auditable release-evaluation data for any AMRSearch AMR library. Organism,
phenotype columns, AMRSearch profiles, filename identifiers, and Pathogenwatch
analysis jobs are runtime options rather than code-level assumptions.

The utilities do not build a database or run AMRSearch. Build the candidate
library and run its validation FASTAs with the usual project/Docker workflow,
then use these scripts to analyse those results.

All relative paths and commands in this document are written for execution
from the `amr-libraries` repository root (the directory containing
`evaluation-utils/` and the AMR-library JSON files).

## Prerequisites

- Python 3.10 or later; no third-party Python packages.
- A phenotype table with a unique sample identifier, an optional display-label
  column, and S/I/R values in the phenotype columns being compared.
- Candidate AMRSearch JSON results.
- `PW_API_KEY` for catalogue matching or cached-analysis retrieval; AWS CLI
  credentials only for cached-analysis retrieval.

Use a distinct release-artifact directory for every run. Preserve the source
phenotypes, match report, candidate-library checksum, FASTA/archive checksums,
raw AMRSearch JSON, commands, and generated reports.

## General workflow

### 1. Match and prepare a cohort

Match one or more phenotype/accession tables to the Pathogenwatch catalogue.
The default response fields are `name` and `uuid`; add `--record-field` for
another catalogue field.

```sh
export PW_API_KEY='...'
python3 evaluation-utils/match_pathogenwatch_accessions.py \
  --organism-id ORGANISM_ID \
  --cohort cohort-a /data/cohort-a-phenotypes.csv \
  --output release-artifacts/catalogue-matches.json
```

Create a matched phenotype table and a FASTA-request payload. Specify the
source identifier column, match cohort, dataset label, and optionally the
phenotype columns used to count non-susceptible samples.

```sh
python3 evaluation-utils/prepare_validation_dataset.py \
  --phenotypes /data/cohort-a-phenotypes.csv \
  --matches release-artifacts/catalogue-matches.json \
  --cohort cohort-a --dataset-label 'Cohort A' \
  --identifier-column sample_accession \
  --nonsusceptible-column drug_a --nonsusceptible-column drug_b \
  --output-dir release-artifacts/cohort-a-input
```

After downloading and extracting the requested FASTAs, verify their identifiers
and checksum manifest. The regular expression must have a named `id` group.

```sh
python3 evaluation-utils/verify_validation_dataset.py \
  release-artifacts/cohort-a-input \
  --identifier-column sample_accession \
  --fasta-identifier-regex '(?P<id>SAMPLE[0-9]+)'
```

### 2. Run the candidate library

Run the candidate database over each validation FASTA. Result filenames must
retain the identifier in the phenotype table. Record the exact candidate
library/database checksum and invocation beside the raw JSON.

### 3. Produce full-cohort comparison data

Map phenotype columns to AMRSearch profile keys using repeated `--endpoint`
arguments in the form `LABEL:PHENOTYPE_COLUMN:AMRSEARCH_PROFILE`.

```sh
python3 evaluation-utils/compare_prediction_results.py \
  --expected release-artifacts/cohort-a-input/expected_phenotypes.csv \
  --results release-artifacts/cohort-a-results \
  --outdir release-artifacts/cohort-a-comparison \
  --identifier-column sample_accession --label-column isolate_name \
  --result-identifier-regex '(?P<id>SAMPLE[0-9]+)' \
  --endpoint DRUG_A:drug_a:DRUG_A \
  --endpoint DRUG_B:drug_b:DRUG_B
```

This writes wide and long comparison tables, discordances, the three error
classes, S/I/R matrices, and Markdown/JSON summaries. `NOT_FOUND` is S by
default; add `--state AMRSEARCH_STATE=SIR` to override or extend state mappings.

List library rules lacking a complete observed genotype with a mapped phenotype.
Map library profile keys to the generated `expected_*` comparison columns:

```sh
python3 evaluation-utils/list_untested_rules.py \
  --library /path/to/candidate-library.jsn \
  --comparison release-artifacts/cohort-a-comparison/comparison.csv \
  --endpoint DRUG_A=expected_DRUG_A \
  --endpoint DRUG_B=expected_DRUG_B \
  --csv release-artifacts/cohort-a-comparison/untested-rules.csv \
  --markdown release-artifacts/cohort-a-comparison/untested-rules.md
```

### 4. Compare a targeted control panel

For a small, literature-derived or reference panel, use the same endpoint
syntax with `compare_targeted_validation.py`. Its default result names are
`{id}_amrsearch.jsn`.

```sh
python3 evaluation-utils/compare_targeted_validation.py \
  --expected /data/controls.csv --results release-artifacts/control-results \
  --identifier-column sample_id --endpoint DRUG_A:drug_a:DRUG_A \
  --output release-artifacts/controls/comparison.csv \
  --summary release-artifacts/controls/summary.md
```

### 5. Optionally cache a deployed baseline

`cache_pathogenwatch_amrsearch_results.py` resolves checksums from a supplied
UUID column, then retrieves objects from the specified Pathogenwatch analysis
job. It is resumable and is useful for candidate-versus-deployed comparison,
not candidate result generation.

```sh
export PW_API_KEY='...'
python3 evaluation-utils/cache_pathogenwatch_amrsearch_results.py \
  --source release-artifacts/cohort-a-input/expected_phenotypes.csv \
  --uuid-column catalogue_uuid \
  --analysis-job amrsearch-ORGANISM_ID-VERSION \
  --output release-artifacts/deployed-baseline
```

Use `--limit` for a connectivity check and `--expected-count` when cohort size
should itself be verified.

## Runnable *Streptococcus pneumoniae* 1313 example

`evaluation-utils/examples/s_pneumoniae` contains a five-isolate mini cohort,
its matching AMRSearch results, a built 1313 library, and a targeted control
panel. It demonstrates the commands only; it is not a release validation.
The mini cohort maps AMRSearch's generic `FLQ` profile to both levofloxacin and
moxifloxacin:

```sh
python3 evaluation-utils/compare_prediction_results.py \
  --expected evaluation-utils/examples/s_pneumoniae/mini-phenotypes.csv \
  --results evaluation-utils/examples/s_pneumoniae/mini-results \
  --outdir /tmp/amrsearch-evaluation-example/mini-comparison \
  --result-identifier-regex '(?P<id>SAMN[0-9]+)' \
  --endpoint CHL:CHL:CHL --endpoint CLI:CLI:CLI --endpoint ERY:ERY:ERY \
  --endpoint LVX:LVX:FLQ --endpoint MFX:MFX:FLQ --endpoint LNZ:LNZ:LNZ \
  --endpoint TCY:TCY:TCY --endpoint SXT:SXT:SXT
```

For the rule inventory, map `FLQ` to both `expected_LVX` and `expected_MFX`:

```sh
python3 evaluation-utils/list_untested_rules.py \
  --library evaluation-utils/examples/s_pneumoniae/1313.jsn \
  --comparison /tmp/amrsearch-evaluation-example/mini-comparison/comparison.csv \
  --endpoint CHL=expected_CHL --endpoint CLI=expected_CLI \
  --endpoint ERY=expected_ERY --endpoint FLQ=expected_LVX,expected_MFX \
  --endpoint LNZ=expected_LNZ --endpoint TCY=expected_TCY \
  --endpoint SXT=expected_SXT \
  --csv /tmp/amrsearch-evaluation-example/mini-comparison/untested-rules.csv \
  --markdown /tmp/amrsearch-evaluation-example/mini-comparison/untested-rules.md
```

The targeted panel runs without any network access:

```sh
python3 evaluation-utils/compare_targeted_validation.py \
  --expected evaluation-utils/examples/s_pneumoniae/targeted-controls.csv \
  --results evaluation-utils/examples/s_pneumoniae/targeted-results \
  --endpoint FLQ:FLQ:FLQ --endpoint KAN:KAN:KAN \
  --output /tmp/amrsearch-evaluation-example/targeted/comparison.csv \
  --summary /tmp/amrsearch-evaluation-example/targeted/summary.md
```
