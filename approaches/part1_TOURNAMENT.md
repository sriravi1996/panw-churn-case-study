# Phase 1 Tournament Verdict — Data-Engineering + EDA (15 iterations)

**Judge:** Phase 1 judging subagent · **Date:** 2026-10-10
**Read:** part1_JUDGE_BRIEF.md, part1_REDTEAM.md, part1_LEAKAGE_AUDIT.md,
part1_INVENTORY.md, part1_SCHEMA_MAP.md, all 15 approach.md files; verified
winner-finalist tables on disk by script (row/col counts, label rates,
drop-column presence).

## Scoring rubric (1–5 per dimension; approach quality, not just outputs)

- **Data design quality** — does the relational/event/panel design fit the B2B churn problem?
- **Dirty-data realism + cleaning rigor** — realistic failure modes? principled cleaning?
- **Integration correctness** — grain, no silent drops, honest reconciliation
- **EDA depth + honesty** — real insights? nulls reported? Saranya's questions answered with numbers?
- **Defensibility** — red-team + leakage findings weigh heavily
- **Modeling suitability** — after dropping leaked columns, a rich, sound Phase 2 input?

**Leakage policy applied:** leaked ≠ auto-disqualified. Incidental leaks (droppable
columns; design and EDA story independent of them) are penalized but survivable.
Structural leaks (headline findings or the modeling feature family depend on leaked
features) are disqualifying for the win.

---

## Per-iteration scores

| # | Angle | Design | Dirty | Integ | EDA | Defens | Model | **Total /30** |
|---|---|---|---|---|---|---|---|---|
| 01 | Star-schema baseline | 3 | 2 | 4 | 3 | 3 | 2 | **17** |
| 02 | Event-sourced log | 4 | 5 | 3 | 5 | 2 | 2 | **21** |
| 03 | Wide feature-store panel | 3 | 5 | 4 | 4 | 2 | 2 | **20** |
| 04 | Normalized 3NF + fuzzy ER | 4 | 3 | 4 | 3 | 3 | 4 | **21** |
| 05 | Account-hierarchy graph | 3 | 4 | 4 | 2 | 1 | 2 | **16** |
| 06 | SCD-2 as-of | 3 | 5 | 2 | 4 | 2 | 3 | **19** |
| **07** | **Survey-augmented** | **5** | **5** | **4** | **3** | **3** | **5** | **25** |
| 08 | Multi-currency FX | 4 | 5 | 4 | 2 | 2 | 4 | **21** |
| 09 | PLG telemetry | 4 | 4 | 4 | 3 | 3 | 4 | **22** |
| 10 | Support-centric | 5 | 4 | 4 | 4 | 2 | 5 | **24** |
| 11 | Contract/commercial | 4 | 4 | 2 | 3 | 2 | 4 | **19** |
| 12 | Marketing attribution | 4 | 4 | 3 | 4 | 3 | 4 | **22** |
| 13 | Partner/channel | 4 | 4 | 4 | 4 | 4 | 3 | **23** |
| 14 | Security-incident | 5 | 5 | 4 | 4 | 4 | 4 | **26** |
| 15 | Audit-first DQ | 4 | 3 | 4 | 4 | 5 | 4 | **24** |

### Two-line rationales

- **part1_01 (star schema) — 17.** Auditable Kimball grain discipline with HHI/cross-sell engineered, every number reconciling; but dirty data is theater (byte-identical dupes), "expansion engine" language is causal on selection, and the partial-line-churn label plus zero dynamics make it a weak modeling base.
- **part1_02 (event-sourced) — 21.** Best dirty realism (shuffled ingest, dangling lifecycle kept as flags) and the tournament's best honesty moment (churn-anchored re-analysis refuting its own velocity story); but the informative velocity family *is* post-churn silence — a structural leak — leaving a skeletal 16-col table with no firmographics and a 28.8% out-of-band label.
- **part1_03 (panel) — 20.** Superb CRM-vs-billing reconciliation and the only genuine *leading* indicator (6-month usage slope, onset ~4 months pre-churn); but `months_observed`/`_latest` missingness encode the outcome's footprint, the $5.19B "panel ARR" sums a stock over 24 months, and variable label maturity (1–24 months observed) is a structural modeling trap.
- **part1_04 (3NF + fuzzy ER) — 21.** The most enterprise-real multi-source design (CRM/ERP/desk/telemetry), CLEAN audit, label in band; but the named fuzzy-ER angle resolved 0.2% of rows (normalization did the rest), and the headline support-burden finding is mechanically confounded (burden quartiles = ARR quartiles in disguise) with a buried breadth null.
- **part1_05 (hierarchy) — 16.** Genuine B2B angle (family-grain risk) with exact cycle/orphan validation; but the headline 0.47 family-churn correlation is two-thirds self-inclusion leakage (0.15 leave-one-out) and the EDA story rides the leaked feature — structural per the leakage policy, cannot win.
- **part1_06 (SCD-2) — 19.** As-of vs final discipline is exactly right for point-in-time modeling and the revenue bridge/NRR decomposition is excellent; but the headline trend feature is computed from `aur_final` despite the "(as-of)" comment — the iteration's own premise broken in the shipped artifact — and the table is the thinnest (1,500 rows, 17 cols, no support family).
- **part1_07 (survey-augmented) — 25. WINNER.** See full rationale below.
- **part1_08 (multi-currency) — 21.** Load-bearing FX reconciliation (−$770M, 56% overstatement corrected) and verified PII masking; but the recall arithmetic doesn't close (189+3≠196, true recall 96.4% not 98.5%) and two misstatement totals disagree by ~$18M — numerical-integrity failures in the headline angle.
- **part1_09 (PLG telemetry) — 22.** Compelling funnel→churn gradient with a quantified bot counterfactual; but the headline cleaning metrics exist only in prose (unverifiable from artifacts), validation is tuned-on-truth circular, and residual error is 40% relative to median DAU — noisy, not surgical.
- **part1_10 (support-centric) — 24.** Fullest support family + contract dates of any table, rich 37-col post-drop input, label closest to canonical base rate; but it shipped the tournament's strongest answer-key leak (corr 0.62) and its DGP baked support→churn so heavily the findings partly rediscover the generator. Runner-up tier.
- **part1_11 (contract/commercial) — 19.** The precedence engine is the right idea for contradictory contracts; but it resolves them with a *different rule than the DGP used to generate the labels* (90/144 conflict accounts inconsistent) and it is never validated — the angle's centerpiece is internally inconsistent — plus four doc-vs-artifact number mismatches.
- **part1_12 (marketing attribution) — 22.** Runs two attribution models and reports they agree (a check most skip); richest engagement family; but 188 funnel dates are fabricated via carry-forward feeding the null finding, the "riskiest cohort" is n=28, and there are no ticket columns.
- **part1_13 (partner/channel) — 23.** The tournament's most explicit conflict lineage (per-decision audit log, $222M double-count prevented), CLEAN audit, honest EDA; but the table is narrower (23 cols: no days_to_renewal, no dynamics, partner tier 36% missing) and the fuzzy cutoff (0.90) invites a tuning probe.
- **part1_14 (security-incident) — 26.** CLEAN — zero surgery needed — with the most product-native finding (efficacy blocks-per-cluster predicts loyalty) and excellent collapsing hygiene; runner-up. Loses the win only on breadth: 24 cols, no contract dates, no dynamics, no support detail beyond incidents.
- **part1_15 (audit-first) — 24.** CLEAN with the most inspectable lineage (scorecard + quarantine + raw-vs-trusted side-by-side); but the gentlest DGP (7.45% churn, below band) never stress-tests the method, and the table is thin (18 cols) for modeling.

---

## Winner: part1_07 — Survey-Augmented: Stated vs Revealed Health

### Why 07 wins

1. **Richest sound modeling input post-drop.** 45 clean columns (verified on disk:
   2,000 rows × 47, drop 2) with the fullest canonical-slot coverage in the
   tournament — dynamics (`usage_decay_90d`, `behavioral_health`), contract
   (`days_to_renewal`, `expansion_revenue_pct`, `downgraded_12m`), full support
   family, trust-gated survey (`valid_nps_mean` + `has_valid_survey` companion),
   engagement (webinars, content, sales calls, QBR), firmographics, hero
   aggregates. Label `churned` is canonical 90-day hero cancellation at 11.85%,
   in band.
2. **Leakage is incidental, not structural.** The shipped `p_churn_latent` and
   `clv_12m` are the DGP's answer key — both must go — but the leakage audit
   verified column-by-column that everything else is pre-scoring clean, and the
   iteration's design and EDA story (survey quality, nonresponse bias) do not
   depend on them. The drop is mechanical and exact.
3. **Best dirty-data realism + cleaning rigor.** Four fraud signatures with a
   signature-keyed detector that deliberately spares honest satisficing,
   nonresponse bias treated as a *risk feature* rather than missing data
   (respondents 9.9% vs non-respondents 15.3% churn), and trust-gated aggregates
   with the distractor (`naive_nps`) kept visible for comparison.
4. **Saranya's questions answered with numbers.** Top ordered items (SentinelShield
   $1,161.6M, 58.8% of ARR; PostureLens cross-sell $166.1M) and highest-value
   relationships (top account, top-10 pairs) are concrete, not hand-wavy.
5. **Honest where it counts.** Valid NPS correlates 0.09 with behavioral health
   and −0.06 with churn vs −0.22 for behavioral — the iteration reports its
   angle's weakness straight.

### What kept it from a perfect score (known, accepted defects)

- Buried null on its core construct: `stated_vs_revealed_gap` deciles don't
  separate churn (10.2% vs 10.9% vs 11.85% base) — undisclosed in prose. For
  Phase 2 this is *information*: treat the gap feature as weak, not as signal.
- Phantom "mean 8.33" for quarantined responses appears in prose but no artifact
  — a doc-level number, not a table defect.
- Modeling table lives at the iteration root, not `outputs/` (path wrinkle only;
  grain verified: 2,000 rows = 2,000 unique `account_id`s).

### Why not the runners-up

- **part1_14 (26):** the cleanest table (zero surgery) and the most product-native
  angle — but 24 columns with no contract dates, no dynamics, and no support
  detail beyond incidents is a thinner Phase 2 foundation than 07's 45 clean
  columns. Cleanliness lost to richness at this margin; 14 is the recommended
  *second* table for any multi-table Phase 2 design.
- **part1_10 (24):** equally rich post-drop, but it shipped the strongest answer-key
  leak in the tournament (corr 0.62) and its DGP baked support→churn so the
  "findings" partly rediscover the generator.
- **part1_02/03:** the red-team's "most defensible" on EDA honesty — but their
  modeling tables are structurally compromised (post-churn silence as the feature
  family; variable label maturity). Honest EDA, unusable foundations. This is why
  the tournament is judged on modeling suitability, not just EDA.
- **part1_05:** excluded by the structural-leakage policy — its headline rode the
  leaked feature.

---

## Combination verdict: NO COMBINATION — single winner

No combination iteration is warranted. The 15 iterations are **separate synthetic
populations** (different account sets, DGPs, seeds, and churn definitions) — their
modeling tables cannot be merged row-wise, and a design-level hybrid (e.g. "07's
survey trust-gating + 10's support threading + 14's efficacy collapsing") would
require generating a new synthetic world, i.e. a Phase 1.5 rebuild, not an
executable merge of existing artifacts. The correct handoff is one table.

Guidance for Phase 2 builders (not a merge): 14's efficacy features
(`blocks_per_cluster`, storm/MTTR) and 10's support family
(`sla_breach_rate`, `reopen_rate`) are the two feature families most worth
re-collecting in a future data design; 15's quarantine/scorecard pattern is the
recommended DQ framing for the modeling pipeline's data contract.

---

## Phase 2 handoff note

- **Winner modeling table:** `~/workspace/goals/senior-staff-data-scientist-job-search/files/panw-case-study/approaches/part1_07/modeling_table.csv`
  (NOTE: iteration root, not `outputs/`). 2,000 rows × 47 cols on disk.
- **Columns to DROP before any training (leakage, audit-verified):**
  - `p_churn_latent` — the DGP's ground-truth churn probability (label drawn as
    Bernoulli(p_churn_latent)); can never exist in production.
  - `clv_12m` — computed from `arr·(1 − p_churn)`; truth-derived, forward-looking.
  - Also exclude ID/PII-adjacent columns from features: `account_id`,
    `top_product_name`, `product_id` (constant PRD-01).
  - Post-drop: 45 feature/label columns. Sanity check after drop: re-run the
    leakage audit's correlation/AUC sweep and confirm no feature has AUC > 0.85
    vs the label.
- **Label semantics:** `churned` = hero-product (PRD-01 SentinelShield)
  cancellation / non-renewal within 90 days of scoring date 2026-10-01.
  Base rate 11.85% (237/2,000). Canonical full-account churn semantics.
- **Feature notes for modelers:**
  - Survey columns come in two families — use the **valid** family
    (`valid_nps_mean`, `valid_csat_mean`, `z_valid_nps`) gated by
    `has_valid_survey` (64% coverage); `naive_nps_mean`/`naive_csat_mean`
    are the untrusted self-reports (distractor). `stated_vs_revealed_gap` is a
    documented null — weak feature, don't lean on it. `n_all_responses`,
    `n_valid_responses`, `validity_rate` are trust machinery, not model features.
  - `days_to_renewal` is a knowable contract term and a legitimate DGP driver.
  - 36% missingness on survey-gated columns is legitimate trust-gated
    missingness — keep `has_valid_survey` as the companion indicator.
  - Small missingness elsewhere: `champion_logins_30d` 2.7%, `webinars_watched`
    3.5%, `content_downloads` 3%.
- **Backup table (if a second clean table is wanted):**
  `approaches/part1_14/outputs/modeling_table.csv` — 2,000 × 24, CLEAN,
  no drops needed, label `churned` 11.0%; thinner (no contract dates/dynamics).
