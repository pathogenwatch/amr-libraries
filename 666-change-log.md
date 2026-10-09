# *V. cholerae* AMR library 666 change log

Updated: 2026-10-05

This log records the September/October 2026 update of `666.toml`. The library
is curated by Vibriowatch from published literature and expert knowledge.

## Corrections to existing library data

| Change                                                      | Reason                                                                                                                                                                                                                                                         |
|-------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `cmlA1` renamed `cmlA5`                                     | Renamed the stored 1,260-bp reference and its chloramphenicol rule, with no sequence or phenotype change. The sequence is the phenicol determinant described in the V. cholerae literature (PMID: 29123067); Vibriowatch curation assigns it the `cmlA5` name. |
| `blaOXA-10` profile corrected                               | Corrected the full-resistance profile to AMP, CAZ, CRO, and FEP, removing the duplicate AMP and unsupported CEP entry.                                                                                                                                         |
| `floR`: CHL resistant → intermediate                        | `floR` is retained as an intermediate marker: it is associated with decreased chloramphenicol susceptibility in V. cholerae (PMID: 22099122; PMID: 35608654).                                                                                                  |
| `nfsA R169C` + `nfsB Q5*`: FZL/NFT resistant → intermediate | The paired variants are retained as intermediate nitrofuran markers, reflecting the Yemen isolates and subsequent V. cholerae susceptibility analysis (PMID: 30602788; PMID: 35608654).                                                                        |
| `mph(A)` reference sequence corrected                       | Removed the trailing sequence that was not part of the curated coding sequence.                                                                                                                                                                                |
| `mrx` reference sequence corrected                          | Restored the initial `ATG` start codon.                                                                                                                                                                                                                        |
| `aac(6')-Ib-cr`: NAL resistance removed                     | Further checking of the literature suggests this was incorrect.                                                                                                                                                                                                |
| `qnrVC1`: NAL resistance removed                            | Futher checking of the literature suggest this was incorrect.                                                                                                                                                                                                  |
| `qnrVC5`: NAL resistance removed                            | Futher checking of the literature suggest this was incorrect.                                                                                                                                                                                                  |

## New or changed phenotype rules

| Rule                                                                                                        | Reason                                                                                                                                                                                                                                                     |
|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AMP: `blaCMY-2`, `blaCMY-4`, `blaPER-7`, `blaSHV-12`, `blaTEM-63`, `blaTEM-115`, or `blaOXA-10` → resistant | Extended the cephalosporin-associated beta-lactamase rules to ampicillin. These are curated broad/extended-spectrum beta-lactamase calls (PMID: 29123067; PMID: 34001879; PMID: 11585791; PMID: 21383087; PMID: 21653763; PMID: 36599823; PMID: 37770747). |
| CIP: `parC S85L` or `gyrA S83I` → intermediate; NAL: either → intermediate and both → resistant             | Replaced the former all-or-nothing pair rule: individual alleles are intermediate, while the pair is additive for nalidixic acid. This reflects the Haiti isolate phenotype and V. cholerae correlation data (PMID: 22099122; PMID: 35608654).             |
| TCY/DOX: `tet(C)`, `tet(D)`, `tet(G)`, `tet(M)`, `tet(59)`, or `tet(Y)` → resistant                         | Added doxycycline to the existing tetracycline rules. The Vibriowatch gene set is supported by V. cholerae resistance-gene surveys (PMID: 29123067; PMID: 36285907).                                                                                       |
| SXT: a `dfrA` determinant + `sul1` or `sul2` → resistant                                                    | Added all required trimethoprim/sulfonamide combinations for co-trimoxazole. A `dfrA` determinant remains TMP-only and `sul1`/`sul2` remain sulfonamide-only when present alone (PMID: 29123067).                                                          |
| AZM/ERY: `mph(A)`, `mph(E)`, `mrx`, `msr(E)`, or `lsa(A)` → resistant                                       | Added erythromycin alongside azithromycin for the curated macrolide determinants; `mrx` is supported by the pVC211 plasmid description (PMID: 28919196).                                                                                                   |
| CIP/NAL: `qnrVC1` → resistant                                                                               | Added nalidixic-acid resistance to the existing `qnrVC1` ciprofloxacin rule; `qnrVC1` is reported in V. cholerae and `qnrVC5` in a fluoroquinolone-resistant isolate (PMID: 29123067; PMID: 35664858).                                                     |

## Library coverage changes

| Change                                         | Reason                                                                                                                                             |
|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Added `ERY` and `SXT` antimicrobial keys       | These keys support the curated macrolide and co-trimoxazole rules.                                                                                 |
| Retained `catB9` and `varG` as `OTHER` markers | Their low or uncertain phenotypic effect is retained as contextual expert-analysis information rather than a direct antimicrobial-resistance call. |
