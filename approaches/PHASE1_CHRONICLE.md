# Phase 1 — Data Engineering + EDA Tournament

*15 iterations, each built by a pipeline (generate → clean → integrate → eda), QA-deepened, red-teamed, leakage-audited, and inventoried. Winner TBD (see §4).*

## 1. What was built

Each iteration delivers the same contract: five scripts (`generate.py`, `clean.py`, `integrate.py`, `eda.py`, `approach.md`), two summary JSONs (`eda_findings.json`, `integration_summary.json`), and one account-grain `modeling_table.csv`. Same shape on the surface; each takes a different angle on the data. Scales run 1,500–2,000 accounts (single hero product in a 20-product portfolio, except where noted).

| Iter | Design | Distinctive dirty-data / cleaning angle | Scale |
|---|---|---|---|
| part1_01 | Kimball star schema; fact_subscriptions + dims | Byte-identical duplicate rows (drop_duplicates); null-FK drops; product-median imputation with `_imputed` indicators; HHI concentration engineered at integration | 2000 rows, 2.3 MB |
| part1_02 | Event-sourced: single append-only log (~220k rows, 10 event types), state by folding the stream in event-time order | Shuffled ingest order (only 49.5% of consecutive pairs agree); 2.9% duplicate redeliveries deduped on event_id; dangling lifecycle events kept as flag columns, never deleted | 2000 rows, 36 MB |
| part1_03 | Wide feature-store panel: account-month, 24 months, CRM + billing ARR views side by side | CRM-vs-billing conflicts (13% of months) kept as `arr_conflict` features, billing = system of record; usage winsorized p99.5; 7,429 missing cells split into structural post-churn vs 652 forward-fillable pipeline gaps | 1800 rows, 16 MB |
| part1_04 | Normalized 3NF, one table per source system (CRM/ERP/catalog/support/telemetry) | Inconsistent company naming across 3 sources — normalize → exact match → difflib fuzzy (cutoff 0.80): 15,860 rows resolved, zero unresolved; timezone-naive timestamps localized per-account-tz; contract-vs-line-item ARR rescaling | 2000 rows, 16 MB |
| part1_05 | Account-hierarchy graph: 1,800 accounts, 260 ultimate parents, up to 3 levels deep, family-level churn correlation by design | 30 orphan parent records severed and flagged; 4 planted 3-cycles broken via iterative 3-color DFS; post-validation that all 1,800 nodes reach a root | 1800 rows, 1.5 MB |
| part1_06 | SCD-Type-2 as-of reconstruction: 12 monthly snapshots, contract dim with valid_from/valid_to, usage carries usage_month + arrived_at | Late-arriving usage (7.1%) held in dual views — `aur_asof` (truth as known at month-end) vs `aur_final` (all arrivals applied); 215 retroactive ARR corrections applied only as-of their effective date | 1500 rows, 2.9 MB |
| part1_07 | Survey-augmented: B2B spine + synthetic NPS/CSAT table with nonresponse and courtesy bias | Four fraud signatures (straight-lining, speeders, duplicate submissions, copy-paste farm) flagged on four independent signals: 2,044 raw → 1,768 valid (86.5%), 276 quarantined; honest satisficing deliberately untouched; silence treated as a risk feature | 2000 rows, 2.6 MB |
| part1_08 | Multi-currency global: 2,000 accounts, 12 countries, 10 currencies, daily FX table; CRM opportunities vs billing as competing money sources | ~6% of invoice rows stamped "USD" while amounts are local currency — detected by double-conversion against CRM truth at the billed date (189 mismatches, 0 false positives): reconciled **−$770M** (56% ARR overstatement); PII masked to pseudonyms, verified zero PII in the table | 2000 rows, 2.7 MB |
| part1_09 | PLG telemetry: 180-day daily grain (360k rows) with DAU, sessions, API calls, feature funnel | Bot windows on 8% of accounts (API-only, constant population) detected via `api_calls/dau > 60` sustained ≥7 days — 160/160 detected, 0 FP, day-level precision 1.000 / recall 0.993 vs hidden ground truth; ~93% of phantom traffic removed | 2000 rows, 32 MB |
| part1_10 | Support-centric: ticket-level threading (parent/child reopens), agent-identity table, explicit SLA policy | Systematically misclassified ticket categories (raw accuracy 72%) reclassified by priority-ordered keyword rules → 93.3% vs hidden ground truth; agent duplicates merged on name+team; churn modeled as partly caused by support experience | 1800 rows, 11 MB |
| part1_11 | Contract/commercial: quotes, discount schedules, renewal terms, competitor mentions in free text; contradictory contract records resolved by precedence engine | Precedence per account (signed > draft, later effective date, CLM > ERP > manual); 711 competitor mentions regex-extracted from 2,897 notes; contradiction flag `has_contract_conflict` (8%); raw contracts archived | 1800 rows, 3.2 MB |
| part1_12 | Marketing attribution: campaigns, 29,672 touch events, MQL/SQL funnel | 12% touches missing campaign_id kept as flagged blind spot; 1,225 duplicate campaign memberships (MAP/CRM double-sync) deduped to earliest; 200 misfiled contacts reassigned by email-domain match; 110 accounts' inverted funnel timestamps repaired by carry-forward; two attribution models run and compared | 1800 rows, 8.8 MB |
| part1_13 | Partner/channel: partner master + partner deal registrations (free-text names, foreign currency, mixed dates) vs direct-rep closed deals; ~35% of deals in both systems | Partner master 62→44 canonical (tier conflicts by mode); exact name match (2,108) then difflib cutoff 0.90 (369), 176 rows quarantined; channel-conflict rule (same account+product, |close−reg| ≤30d, value ±15%) — every decision logged in `conflict_audit.csv`; naive double-counting would have overstated bookings ~$200M | 2000 rows, 2.4 MB |
| part1_14 | Security-incident flavored: raw alert stream (~287k rows, 90 days), SOC incident tickets, threat-block counts from two feeds | Alert collapsing (<30 min apart within account+type+sensor → one cluster; 287k → 269k, storms at ≥25); incident reopen-within-24h dedup (4,140 → 3,095 true incidents); identical per-account-day block counts counted once, differing counts summed | 2000 rows, 52 MB |
| part1_15 | Audit-first data quality: great-expectations-style scorecard grading each of 7 source tables (completeness/validity/uniqueness/consistency) → PASS/REVIEW/FAIL | No silent imputation or fixing: impossible values, bad FKs, chronology violations, stage regressions quarantined (2,127 rows, trust coverage 94–99% except product catalog 80%); modeling table built from trusted slices only; every headline computed raw-vs-trusted side by side | 2000 rows, 3.4 MB |

The Part 1 assignment questions — **top ordered items** and **highest-value customer/product relationships** — are answered with concrete numbers in all 15 (verified in each `eda_findings.json`). The hero product dominates ARR in every iteration (48–77% share), so answers converge on portfolio mix and diverge on angle-specific findings.

## 2. QA process: what the deepening passes caught

QA was not a polish step — it changed shipped artifacts. The inventory sweep (2026-10-10 ~10:04–10:07 PDT) confirmed all 15 iterations fully ready: every pipeline script, `approach.md`, both summary JSONs, and a non-empty modeling table at the correct grain (one row per unique `account_id`), 15/15, no blockers. Along the way the passes caught and fixed three recurring failure classes:

**Silent drops.** The original judge brief flagged `modeling_table.csv` missing for part1_07/08/09 while their summaries described the tables (2000×47, 2000×37, 2000×31) — the QA pass resolved the substance, with the tables now existing at the **iteration root** rather than `outputs/` (path now verified grain-correct: 2000 rows = 2000 unique account_ids). During the same sweep, part1_14/15 briefly showed missing `outputs/` while the QA agent was mid-polish; all artifacts landed within minutes. Lesson recorded: consumers check both paths.

**Stale numbers in prose.** part1_05's `approach.md` narrated an earlier run — top-10 families at 30.0% of ARR (current JSON: 0.2205), median family 2 accounts/$307K (current: 5/$757.9K), subsidiary churn 21.7% vs 14.2% (current: 22.0% vs 17.2%). QA rewrote the doc and a script then verified every numeric claim in the new prose against both JSONs (verified clean in the inventory). The same failure recurred in part1_11 post-QA — quotes "2,955" vs raw 4,100, "57" dupes removed vs DQ-report 80, "711" competitor mentions vs 704, "2,897" renewal notes vs 2,956. Manual transcription of a machine-verified pipeline cannot be trusted; the standing rule is to script-diff every number in prose against the artifact JSONs before judging.

**Determinism bugs.** part1_02's approach.md notes two caught before they could corrupt downstream: folding the event stream in raw ingest order instead of event-time order, and impossible timelines being silently dropped by the fold (both fixed; the time-aware orphan check confirms zero impossible timelines). part1_13 caught a cross-account misassignment from an early two-word normalized-name scheme via a join diagnostic before the fuzzy ER ran.

## 3. Review findings

**Red-team severity counts** (covered part1_01–12; severities: FATAL = disqualifying in a shipped artifact, MAJOR = substantially weakens the approach or its headline claims, MINOR = polish/framing):

| Iter | FATAL | MAJOR | MINOR |
|---|---|---|---|
| 01 | 0 | 1 | 3 |
| 02 | 0 | 1 | 2 |
| 03 | 0 | 1 | 3 |
| 04 | 0 | 3 | 3 |
| 05 | 1 | 1 | 2 |
| 06 | 0 | 2 | 2 |
| 07 | 0 | 3 | 1 |
| 08 | 0 | 3 | 1 |
| 09 | 0 | 3 | 3 |
| 10 | 1 | 1 | 2 |
| 11 | 1 | 2 | 3 |
| 12 | 1 | 1 | 3 |
| **Total** | **4** | **22** | **28** |

The four FATALs all share one root cause — **the generator's answer key shipped as a feature.** In part1_10/11/12 the modeling tables carry `p_churn_latent`, the literal per-account probability the label was drawn from (corr 0.48–0.62 with the label; 63–74% churn when >0.5). In part1_05, `family_churn_rate` aggregates the label including the account itself — the iteration's headline "corr 0.47, the single strongest signal" re-measures at **0.15 leave-one-out**, and even that uses contemporaneous labels unknowable at prediction time. The next-most-serious flaws: part1_06 preaches as-of discipline while its headline 3-month usage-trend feature is computed from `aur_final` (the future-backfilled view; the code comment claims "(as-of)"), and part1_01's `pct_arr_churned` is exactly the label in continuous form (`> 0 ⟺ label`, 2000/2000 verified). The most defensible iterations are the ones whose honesty mechanisms survived contact with their own results — part1_02's churn-anchored re-analysis that *refutes* its own naive early-warning story (median events 27.0 vs 27.0), and part1_03's disclosed nulls.

**Leakage audit verdict: 10 LEAKED, 1 SUSPECT, 4 CLEAN.** The cross-cutting pattern is **generative truth**: `p_churn_latent` in part1_07/10/11/12 (never producible in production; corr 0.48–0.62), and `clv_12m` = `arr·(1 − p_churn)` computed from that same unknowable probability in part1_07/08/09/10/11/12 (corr as low as −0.03 — the modest correlations make it easy to miss, and a tree model would still exploit the definitional link). Supporting mechanisms: post-outcome windows (part1_02's trailing-velocity features measure post-churn silence, AUC up to 0.992; part1_03's `months_observed` and `_latest` features encode the outcome's footprint), self-in-label aggregates (part1_05), label re-expression (part1_01), and as-of vs final views (part1_06, SUSPECT). CLEAN as-is: part1_04, part1_13, part1_14, part1_15 (14/15 carry only minor caveats, e.g. 36 post-scoring incident resolutions feeding MTTR).

**What this means for Phase 2:** the Phase 2 pre-training checklist is per-iteration drop lists — the forbidden columns to exclude before any training (e.g. part1_01: `pct_arr_churned`, `churned_arr`; part1_02: the velocity family; part1_05: family aggregates; part1_07/08/09/10/11/12: `clv_12m` plus `p_churn_latent` where present; part1_06: use `aur_asof`, not `aur_final`). After dropping, re-run the audit's correlation + determinism checks and confirm no feature has AUC > 0.85 vs the label. Note the traps this creates: part1_13 and part1_15 carry no `clv_12m` (CLV-based modeling heads must pivot), and part1_02/03 have label semantics outside the 10–18% band and must be re-baselined.

## 4. Judging

A judge is currently scoring the 15 iterations on **quality of approach** (not end-result metrics) across six dimensions. **Winner: TBD.** The result will be recorded in `part1_TOURNAMENT.md` (not yet written at the time of this chapter); once it exists, this section should be updated with the winning iteration and its dimension scores. The judge brief's provisional flags — the 07/08/09 missing-table path issue and the part1_05 prose staleness — were closed by QA and the inventory sweep; the judge was instructed to check both table paths and score the JSON numbers for part1_05.

## 5. Key lessons

- **Leakage is the norm, not the exception.** 10 of 15 modeling tables carry at least one feature a production model could never legally know — most often the generator's own ground truth (`p_churn_latent`, `clv_12m`). The pattern recurred across six iterations built by different hands, which means Phase 2's first step is not modeling — it is a leakage audit gate, and the checklist in §3 must run on the *winning* table before any training.
- **EDA honesty checks are what separate defensible work from plausible fiction.** The tournament's best moments are all self-refutations: part1_02's churn-anchored re-analysis showing velocity *detects* churn rather than *predicts* it; part1_03's CRM/billing conflict turning out to be a DQ flag, not a model feature (12.4% vs 13.0% churn); part1_15's raw-vs-trusted framing, where the raw mean active ratio (1.09, max 39.95) is physically impossible and the trusted value (0.69) is the only one worth reporting. The judge's job — and the VP's — is to weight the checks, not the headlines.
- **Machine-generate everything checkable.** Stale prose corrupted two iterations' narratives (part1_05's whole numbers section, part1_11's four mismatches), phantom numbers appeared with no artifact behind them (part1_07's "8.33", part1_08's non-closing recall arithmetic, part1_09's prose-only precision/recall), and tables went missing from their specced paths. None of these were caught by reading — all were caught by scripted diffs: prose numbers vs JSONs, JSON claims vs disk, code comments vs actual computation. For a VP audience: this is the pipeline lesson that generalizes — every published number should have a machine-verified lineage to the artifact that produced it.
