# *S. pneumoniae* AMR library 1313 change log

Updated: 2026-09-29

This log records the `Spn-update-20260924` review of `1313.toml`. **Source**
uses the GPS pipeline's explanation in
[PR #178](https://github.com/GlobalPneumoSeq/gps-pipeline/pull/178). Where PR
#178 does not describe a pre-existing GPS reference, this is stated rather than
inferring an origin from its accession. “Not GPS” means that the change arose
from a library or evidence audit rather than a GPS marker. RIF and VAN were
outside this update's scope.

## Corrections to existing library data

| Change | Decision and reason |
| --- | --- |
| `aph_3prime_III_1` renamed `aph_3'_III_1` | Normalised the existing gene and mechanism spelling to conventional apostrophe notation; sequence and KAN interpretation are unchanged. |
| Removed `ermB_UPST` and its ERY/CLI rule | The old stored sequence was incorrect and was tetO-like, not an ermB upstream region. The ErmBL leader regulates `ermB` but is not itself the determinant, so it adds no calling precision and was not added. |
| `tetM_4`: TCY resistant → intermediate | Curator judgement from Victoria validation: 16 I, 7 R, and 13 S among 36 carriers, with non-independent GPSC3 clustering. Intermediate is less overconfident; revisit with independent carriers. |
| `folA` and `folP` coverage: 60% → 90% | Tightened detection against partial/paralogous matches. Identity remains 80%; the existing 60% settings for `gyrA` and `gyrB` are retained. |

## New reference sequences

| Library entry | Source | Decision and concise rationale |
| --- | --- | --- |
| `aac_6'_Ie_aph_2''_Ia` (KAN) | GPS - Added KAN determinants from AMRFinderPlus. | Added as a standalone KAN determinant: the bifunctional enzyme has direct functional evidence for kanamycin resistance. PMID: 2833561. |
| `aph_3'_IIa` (KAN) | GPS - Added KAN determinants from AMRFinderPlus. | Added as a standalone KAN determinant; APH(3')-IIa is a kanamycin phosphotransferase. PMID: 6295884. |
| `dfrA31` (TMP) | GPS - Added TMP determinants from AMRFinderPlus. | Added as standalone TMP resistance: it is an acquired trimethoprim-insensitive DHFR. The exact allele is supported chiefly by curated catalogue evidence. |
| `dfrF` (TMP) | GPS - Added TMP determinants from AMRFinderPlus. | Added as standalone TMP resistance: acquired DHFR with clinical/isolate support. PMID: 24492367. |
| `dfrS1` (TMP) | GPS - Added TMP determinants from AMRFinderPlus. | GPS calls the sequence `dfrC_NG077973_WP000175735`; it was added under the curated `dfrS1` name as an acquired TMP-resistant DHFR. |
| `tetO` (TCY) | GPS - Added TET determinants from AMRFinderPlus (the `NC012216` and `NG048255` references); `Y07780` predates PR #178. | Added as standalone TCY resistance after correcting the tetO-like legacy `ermB_UPST` entry. The canonical reference is 1,920 nt; the remaining GPS allele is covered by configured thresholds. |
| `tetA(P)` / `tetAp_L20800` (TCY) | GPS - pre-existing reference; PR #178 gives no upstream source note. | Added as standalone TCY resistance. It is a functional efflux determinant and does not require `tetB(P)`; see PMID: 8170402. |
| `folA_4` (TMP/SXT detection background) | GPS - pre-existing reference; PR #178 gives no upstream source note. | Added as a divergent detection background, not a new mechanism. It improves margin around the 80% identity threshold for the established `I100L` TMP mechanism. PMID: 9371341. |
| `msrD` (ERY) | GPS - pre-existing reference; PR #178 gives no upstream source note. | Added because the cognate `mef(A/E)` + `msrD` system was missing from the library. One reference covers the second 97.95%-identical GPS allele at the configured thresholds. PMID: 29959337. |

## New or changed phenotype rules

| Rule | Source | Decision and concise rationale |
| --- | --- | --- |
| KAN: `aac_6'_Ie_aph_2''_Ia` or `aph_3'_IIa` → resistant | GPS - Added KAN determinants from AMRFinderPlus. | Each complete enzyme is independently sufficient; no combination is required. |
| TMP: `dfrA31`, `dfrF`, or `dfrS1` → resistant | GPS - Added TMP determinants from AMRFinderPlus. | Each acquired DHFR is independently represented for TMP. They are deliberately not standalone SXT calls. |
| TCY: `tetO` or `tetA(P)` → resistant | GPS - Added TET determinants from AMRFinderPlus for `tetO`; `tetA(P)` is pre-existing in GPS. | Each is a complete standalone tetracycline determinant. |
| TMP: `folA_4 I100L` → resistant | GPS - pre-existing reference; PR #178 gives no upstream source note. | Same established mechanism as canonical `folA I100L`, on the added detection background. |
| SXT: qualifying `folP` + `folA_4 I100L` → resistant | GPS - pre-existing `folP`/`folA_4` references; PR #178 gives no upstream source note. | Added as the existing two-component folate model on the divergent `folA_4` background: one side alone is intermediate, both give resistance. |
| SXT: qualifying `folP` + acquired `dfr` → resistant | GPS - TMP determinants added from AMRFinderPlus; `folP` predates PR #178. | Added as all-members-required rules: `folP` supplies the SMX-side determinant and acquired `dfr` the TMP-side determinant. An acquired `dfr` alone remains TMP-only. |
| ERY: cognate `mefA` + `msrD` → resistant; `msrD` alone → intermediate | GPS - pre-existing `msrD` references; PR #178 gives no upstream source note. | Added/revised for higher specificity: the intact pair is reliably resistant, whereas singleton effects vary by element, background, and MIC method. PMID: 29959337. |
| FLQ: evidence-supported target rules; added `parC D83H` | GPS - pre-existing QRDR variants; codex was used to extract all individual and combination mutations for which support could be found. DOI: 10.1128/AAC.49.6.2479-2486.2005; 10.1128/AAC.50.2.572-579.2006; 10.1128/AAC.45.12.3517-3523.2001. |

## Reviewed but not added

| Candidate | Source | Decision and concise rationale |
| --- | --- | --- |
| Broad `folP` frameshift, stop, truncation, or disruption calls | GPS - pre-existing `folP` reference; PR #178 gives no upstream source note. | Not added. Evidence supports in-frame one- or two-codon insertions in the resistance-associated loop, already represented by `aa_insert_57-70`; Paarsnp cannot limit generic disruptions to that interval. |
| `aac3Ia` as KAN | GPS - Added KAN determinants from AMRFinderPlus. | Not added: AAC(3)-Ia’s supported spectrum does not include kanamycin A. DOI: 10.1128/AAC.01450-05. |
| `gyrA D83H` | GPS - “Add gyrA mutation from AMRFinderPlus.” | Not added: this is an incorrect target assignment, not an unsupported substitution. The pneumococcal evidence is for `parC D83H`: clinical isolates carrying `gyrA S81Y` + `parC D83H` or `gyrA S81F` + `parC D83H` had high ciprofloxacin/levofloxacin MICs. DOI: 10.1128/AAC.00082-08. |
| `gyrA Q118A` | GPS - pre-existing variant; PR #178 gives no upstream source note. | Deferred: it is distinct from retained `Q118K`, and this review found insufficient primary pneumococcal evidence for Q118A. |
| `tet58_KY887560` | GPS - pre-existing reference; PR #178 gives no upstream source note. | Not added: `KY887560` is the single-gene determinant `tet(61)`, despite its GPS label. It must not be entered as `tet(58)`, which is a distinct two-component ABC transporter (`tetA(58)` + `tetB(58)`). This review did not establish an appropriate pneumococcal TCY phenotype tier for `tet(61)`, so neither a reference nor a rule was added. PMID: 32090022. |
| `tetB(P)` | GPS - pre-existing reference; PR #178 gives no upstream source note. | Deferred: a future standalone intermediate TCY model is plausible, but no pneumococcal expression/MIC study was found. It is not required for a `tetA(P)` call. PMID: 8170402. |
| RIF and VAN candidates | GPS - rpoB variants imported from DOI: 10.1093/jac/dkh073, 10.1128/AAC.49.6.2237-2245.2005, 10.1128/AAC.00856-10, and 10.1128/aac.47.3.863-868.2003; VAN sources are not described in PR #178. | Antibiotics not yet included in this library. |
