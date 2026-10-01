# *S. pneumoniae* AMR library 1313 evaluation log

Updated: 2026-10-01  
Release version `0.0.20`  
Baseline: version `0.0.16`

This is the first evaluation log for this library. Version `0.0.16` is the
baseline and therefore has no comparison with an earlier release. `NOT_FOUND`
is counted as susceptible (S). Rows in every phenotype–genotype concordance
matrix are the reference phenotype and columns are the Paarsnp prediction.

## Test sets

| Test set                                                                                                                                      | Genome source / URL                                                                                                                                                                                                                                                                        | Phenotype data and purpose                                                                                                                                                                                                                           | Citation                                                                                                                                                                                                      |
|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Victoria, Australia, 2018–2022](https://pathogen.watch/collections/d8N653w2ZHFxMkyqYs8CeB-higgs-et-al-2023)                                  | 1,472 public *S. pneumoniae* genomes; source sequence collection: [NCBI BioProject PRJNA857543](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA857543).                                                                                                                                      | Published Sensititre STP6F broth-microdilution MICs, interpreted by CLSI. CHL, CLI, ERY, LVX, MFX, LNZ, TCY and SXT were evaluated. Two of the 1,474 published isolates were not in Pathogenwatch; both were susceptible at all evaluated endpoints. | [Higgs *et al.* 2023](https://doi.org/10.1128/aac.00785-23)                                                                                                                                                   |
| [Supplementary FLQ/KAN controls](https://pathogen.watch/collections/nEaETRcy3bL6hHQRf2S8bz-s-pneumoniae-flqkan-validation-genomes-2026-09-29) | Public assemblies: [SP224896](https://www.ncbi.nlm.nih.gov/assembly/GCA_001553495.1), [SP225994](https://www.ncbi.nlm.nih.gov/assembly/GCA_001545505.1), [BM4200](https://www.ncbi.nlm.nih.gov/assembly/GCA_035465375.1), and [R6](https://www.ncbi.nlm.nih.gov/assembly/GCF_000007045.1). | Three literature-linked FLQ controls and two KAN controls. This small set is a targeted rule check, not an accuracy estimate.                                                                                                                        | [Hawkins *et al.* 2017](https://doi.org/10.1016/j.ijmm.2017.07.008); [Keness & Bisharat 2016](https://doi.org/10.1128/genomeA.00181-16); [Collatz *et al.* 1984](https://doi.org/10.1099/00221287-130-7-1665) |

## Data availability

- CSV files containing phenotypes are in [1313-evaluation-phenotypes](./1313-evaluation-phenotypes).
- FASTA files can be downloaded from the corresponding Pathongewatch collections by clicking on the name of the test set.
- Code for running validations and generating tables are in [evaluation-utils](./evaluation-utils).

## Release comparison summary

Exact agreement means identical S/I/R categories. “False I/R” counts an I or R
prediction for a phenotype-S isolate; “missed I/R” counts an S prediction for a
phenotype-I/R isolate; “wrong I/R tier” counts an I/R prediction that has the
wrong non-susceptible category. LVX and MFX are both compared with Paarsnp's
single generic `FLQ` output, so their figures are not independent.

| Endpoint |        Baseline exact |       Candidate exact | Change | Baseline false I/R → candidate | Baseline missed I/R → candidate | Baseline wrong I/R tier → candidate |
|----------|----------------------:|----------------------:|-------:|-------------------------------:|--------------------------------:|------------------------------------:|
| CHL      |  1,457/1,469 (99.18%) |  1,457/1,469 (99.18%) |      0 |                          0 → 0 |                         12 → 12 |                               0 → 0 |
| CLI      |  1,446/1,469 (98.43%) |  1,446/1,469 (98.43%) |      0 |                          9 → 9 |                           8 → 8 |                               6 → 6 |
| ERY      |  1,445/1,469 (98.37%) |  1,445/1,469 (98.37%) |      0 |                          3 → 3 |                         19 → 19 |                               2 → 2 |
| LVX      |  1,452/1,468 (98.91%) |  1,464/1,468 (99.73%) |    +12 |                         12 → 0 |                           3 → 4 |                               1 → 0 |
| MFX      |  1,450/1,468 (98.77%) |  1,463/1,468 (99.66%) |    +13 |                         13 → 0 |                           5 → 5 |                               0 → 0 |
| LNZ      | 1,469/1,469 (100.00%) | 1,469/1,469 (100.00%) |      0 |                          0 → 0 |                           0 → 0 |                               0 → 0 |
| TCY      |  1,411/1,469 (96.05%) |  1,420/1,469 (96.66%) |     +9 |                        22 → 22 |                         17 → 17 |                             19 → 10 |
| SXT      |  1,393/1,469 (94.83%) |  1,393/1,469 (94.83%) |      0 |                        24 → 24 |                         24 → 24 |                             28 → 28 |

Across 11,750 Victoria phenotype comparisons, exact agreement rose from
11,523 to 11,557 (+34). False I/R calls fell from 83 to 58; missed I/R calls
rose from 88 to 89; and wrong I/R tiers fell from 56 to 46. The main benefit
is FLQ specificity: removing generic singleton-QRDR intermediate calls removes
all 12 LVX and 13 MFX false non-susceptible predictions, with one additional
LVX I/R phenotype predicted S.

## Victoria phenotype–genotype concordance matrices

Each cell is **baseline → release candidate**. Columns are predicted S, I and
R; rows are phenotype S, I and R. No unknown predictions occurred.

| Endpoint | Phenotype |   Predicted S | Predicted I | Predicted R |
|----------|-----------|--------------:|------------:|------------:|
| CHL      | S         | 1,444 → 1,444 |       0 → 0 |       0 → 0 |
|          | I         |         0 → 0 |       0 → 0 |       0 → 0 |
|          | R         |       12 → 12 |       0 → 0 |     13 → 13 |
| CLI      | S         | 1,327 → 1,327 |       0 → 0 |       9 → 9 |
|          | I         |         2 → 2 |       0 → 0 |       6 → 6 |
|          | R         |         6 → 6 |       0 → 0 |   119 → 119 |
| ERY      | S         | 1,285 → 1,285 |       0 → 0 |       3 → 3 |
|          | I         |         7 → 7 |       0 → 0 |       2 → 2 |
|          | R         |       12 → 12 |       0 → 0 |   160 → 160 |
| LVX      | S         | 1,452 → 1,464 |      12 → 0 |       0 → 0 |
|          | I         |         2 → 2 |       0 → 0 |       0 → 0 |
|          | R         |         1 → 2 |       1 → 0 |       0 → 0 |
| MFX      | S         | 1,450 → 1,463 |      13 → 0 |       0 → 0 |
|          | I         |         4 → 4 |       0 → 0 |       0 → 0 |
|          | R         |         1 → 1 |       0 → 0 |       0 → 0 |
| LNZ      | S         | 1,469 → 1,469 |       0 → 0 |       0 → 0 |
|          | I         |         0 → 0 |       0 → 0 |       0 → 0 |
|          | R         |         0 → 0 |       0 → 0 |       0 → 0 |
| TCY      | S         | 1,265 → 1,265 |      0 → 13 |      22 → 9 |
|          | I         |         4 → 4 |      0 → 16 |      19 → 3 |
|          | R         |       13 → 13 |       0 → 7 |   146 → 139 |
| SXT      | S         | 1,111 → 1,111 |     22 → 22 |       2 → 2 |
|          | I         |       17 → 17 |   108 → 108 |     10 → 10 |
|          | R         |         7 → 7 |     18 → 18 |   174 → 174 |

## FLQ/KAN supplementary concordance matrices

This test set has only S and R reference calls. Baseline and candidate each
made five predictions, so the concordance matrices are shown separately rather than as
population-level performance estimates.

| Version | Endpoint | Phenotype | Predicted S | Predicted I | Predicted R |
|---------|----------|-----------|------------:|------------:|------------:|
| 0.0.16  | FLQ      | S         |           0 |           1 |           0 |
|         |          | I         |           0 |           0 |           0 |
|         |          | R         |           0 |           0 |           2 |
| 0.0.16  | KAN      | S         |           1 |           0 |           0 |
|         |          | I         |           0 |           0 |           0 |
|         |          | R         |           0 |           0 |           1 |
| 0.0.20  | FLQ      | S         |           1 |           0 |           0 |
|         |          | I         |           0 |           0 |           0 |
|         |          | R         |           0 |           0 |           2 |
| 0.0.20  | KAN      | S         |           1 |           0 |           0 |
|         |          | I         |           0 |           0 |           0 |
|         |          | R         |           0 |           0 |           1 |

The baseline agreed with 4/5 controls; the candidate agreed with 5/5. The
changed control is `SP224896`: `parC S79F` alone changes from FLQ-I to S, while
the resistant `SP225994` with `parC S79F` plus `gyrA S81F` remains R.

## Interpretation for the next release

The candidate is supported for release on this evidence. CHL has only 25
non-susceptible observations and LNZ has none, so those endpoints cannot
support strong sensitivity claims. FLQ must remain labelled as a generic
prediction: the same target genotype can have different LVX and MFX outcomes.
Future releases should append a comparison using this `0.0.20` evaluation as
the baseline, preserving both the raw-result location and the full concordance
matrices.

Updated: 2020-01-29  
Release version `0.0.16`  
Baseline: version -

This one-off baseline evaluation uses the test sets described above. It has no
comparison with an earlier release. Rows are reference phenotypes and columns
are Paarsnp predictions; `NOT_FOUND` is counted as susceptible (S). No unknown
predictions occurred.

## Victoria phenotype–genotype concordance matrices

| Endpoint | Phenotype | Predicted S | Predicted I | Predicted R |
|----------|-----------|------------:|------------:|------------:|
| CHL      | S         |       1,444 |           0 |           0 |
|          | I         |           0 |           0 |           0 |
|          | R         |          12 |           0 |          13 |
| CLI      | S         |       1,327 |           0 |           9 |
|          | I         |           2 |           0 |           6 |
|          | R         |           6 |           0 |         119 |
| ERY      | S         |       1,285 |           0 |           3 |
|          | I         |           7 |           0 |           2 |
|          | R         |          12 |           0 |         160 |
| LVX      | S         |       1,452 |          12 |           0 |
|          | I         |           2 |           0 |           0 |
|          | R         |           1 |           1 |           0 |
| MFX      | S         |       1,450 |          13 |           0 |
|          | I         |           4 |           0 |           0 |
|          | R         |           1 |           0 |           0 |
| LNZ      | S         |       1,469 |           0 |           0 |
|          | I         |           0 |           0 |           0 |
|          | R         |           0 |           0 |           0 |
| TCY      | S         |       1,265 |           0 |          22 |
|          | I         |           4 |           0 |          19 |
|          | R         |          13 |           0 |         146 |
| SXT      | S         |       1,111 |          22 |           2 |
|          | I         |          17 |         108 |          10 |
|          | R         |           7 |          18 |         174 |

## FLQ/KAN supplementary concordance matrices

The supplementary controls contain S and R reference calls only and are a
targeted rule check, not a population-level accuracy estimate.

| Endpoint | Phenotype | Predicted S | Predicted I | Predicted R |
|----------|-----------|------------:|------------:|------------:|
| FLQ      | S         |           0 |           1 |           0 |
|          | I         |           0 |           0 |           0 |
|          | R         |           0 |           0 |           2 |
| KAN      | S         |           1 |           0 |           0 |
|          | I         |           0 |           0 |           0 |
|          | R         |           0 |           0 |           1 |
