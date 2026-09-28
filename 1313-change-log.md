# S. pneumoniae AMR library 1313 change log

Date: 2026-09-25

This is the standalone summary of changes made to
`libraries/amr-libraries/1313.toml` during the `Spn-update-20260924` review.
Rifampicin and vancomycin were outside the scope of the update.

## Corrections to existing library data

The items in this section are corrections to entries or phenotype rules that
were already present in library 1313. They are not simply additions from the
new GPS dataset.

| Correction | Short explanation |
| --- | --- |
| Renamed `aph_3prime_III_1` to `aph_3'_III_1` | Corrected the existing aminoglycoside gene name to use the conventional apostrophe notation; its KAN mechanism member was renamed at the same time. |
| Removed `ermB_UPST` and its ERY/CLI rule | Corrected a misidentified existing entry: its stored sequence was tetO-like, not an ermB upstream region. The proposed replacement `ermBL_HG799494` was not added because the leader region adds no useful precision to the existing `ermB` call. |
| Corrected the `mef(A/E)` phenotype model | Removed the existing standalone resistant `mefA_3` and `mefA_10` rules. They were replaced by resistant combinations with the newly added `msrD`, plus a conservative standalone intermediate `msrD` rule; `mefB` was unchanged. |
| Corrected `gyrA`/`parC` FLQ tiering | Removed the existing standalone resistant rules and replaced them with 42 all-members-required resistant combinations. A qualifying mutation in only one target no longer assigns a generic FLQ phenotype; one configured mutation in each target assigns resistance. `gyrA S81F` + `parC S79F` and `gyrA S81F` + `parC S79Y` have direct phenotype support from the supplementary validation, while the other 40 exact pairs remain mechanistic inferences. |
| Changed `tetM_4` from TCY resistant to intermediate | **Curator judgement, not a literature-derived assertion.** In the Victoria validation cohort, 36 `tetM_4` carriers comprised 16 TCY-I, 7 TCY-R, and 13 TCY-S isolates. Intermediate is therefore a better empirical tier than unconditional resistance in this dataset. All I and S observations were concentrated in GPSC3, so this interpretation should be revisited with independent carriers. |
| Increased existing `folA` coverage from 60% to 90% | Tightened detection to reduce partial or paralogous matches; identity remains 80%. Existing locus-specific 60% settings for `folP`, `gyrA`, and `gyrB` were preserved. |

## New reference sequences and incoming-name normalization

| Change | Short explanation |
| --- | --- |
| Added `aac_6'_Ie_aph_2''_Ia` | Added the 1,440-nt bifunctional aminoglycoside-resistance determinant. |
| Added `aph_3'_IIa` | Added the 795-nt kanamycin phosphotransferase determinant. |
| Added `dfrA31`, `dfrF`, and `dfrS1` | Added three acquired trimethoprim-resistance determinants. The incoming `dfrC` allele was entered under its curated name, `dfrS1`. |
| Added `tetO` | Added the canonical 1,920-nt `tetO_Y07780` sequence; the other supplied `tetO` sequences are covered by its thresholds. |
| Added `folA_4` | Added the divergent `folA_4_14410_4_33` background to improve detection margin for `I100L`. |
| Added `msrD` | Added `msrD_2_AF274302`; the second supplied allele is 97.95% identical and is covered by the same reference. |

## New phenotype and mechanism rules

| Change | Short explanation |
| --- | --- |
| Added resistant KAN rules for `aac_6'_Ie_aph_2''_Ia` and `aph_3'_IIa` | Each determinant independently supports kanamycin resistance. |
| Added resistant TMP rules for `dfrA31`, `dfrF`, and `dfrS1` | Each acquired DHFR is treated as an independent trimethoprim-resistance mechanism. |
| Added a resistant TMP rule for `folA_4 I100L` | Mirrors the existing `folA I100L` mechanism on the divergent reference background. |
| Added a resistant TCY rule for `tetO` | `tetO` is treated as a standalone tetracycline-resistance determinant. |
| Added `folP` + `folA_4 I100L` as `INTERMEDIATE_ADDITIVE` for SXT | Either side alone is intermediate; finding both makes the combined co-trimoxazole phenotype resistant. This parallels the existing `folP` + canonical `folA I100L` rule. |
| Added resistant SXT combinations for `folP` with each acquired `dfr` | Added separate all-members-required rules for `folP aa_insert_57-70` with `dfrA31`, `dfrF`, or `dfrS1`; `folP` supplies the SMX-side determinant and `dfr` the TMP-side determinant. |
| Added `parC D83H` to the FLQ combinations | Retained as an independently supported pneumococcal ParC substitution; the incoming `gyrA D83H` row was rejected as erroneous. |

## Reviewed but deliberately not changed

| Candidate | Decision and short explanation |
| --- | --- |
| Broader `folP` disruption rules | Retained the existing `aa_insert_57-70` rule. Pneumococcal evidence supports in-frame one- or two-codon insertions in this loop, whereas no primary evidence was found for resistance from a `folP` frameshift or premature stop. Paarsnp also cannot currently constrain generic `frameshift` or `truncated` rules to this interval. |
| `aac3Ia` as KAN | Not added: its supported substrate spectrum does not include kanamycin A. |
| `gyrA D83H` | Not added: the supported pneumococcal D83H substitution is in `parC`, not `gyrA`. |
| `gyrA Q118A` | Deferred for a future update; it is distinct from the retained `Q118K`. |
| `tet58_KY887560` | Deferred; the supplied accession is reported as `tet(61)`, and its standalone clinical interpretation is unresolved. |
| `tetA(P)` and `tetB(P)` | A future implementation was modelled as resistant `tetA(P)` and intermediate `tetB(P)` without requiring a combination, but neither sequence nor rule was added in this update. |
| RIF and VAN candidates | Excluded by scope. |
