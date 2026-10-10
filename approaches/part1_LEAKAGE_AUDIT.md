# Phase 1 Modeling-Table Leakage Audit

**Date:** 2026-10-10 · **Scope:** `part1_01`–`part1_15` modeling tables (QA-final, READ-ONLY — nothing modified).
`part1_13/14/15` were QA-finalized after the first pass and audited in the same session via an adapted script (`leakage_audit_13_15.py`) — **all three now audited.**
**Purpose:** Phase 2 will train churn models on the winning iteration's `modeling_table.csv`. This audit finds features that would not be knowable at scoring time or are circular with the label.

## Method
For each table: identified the label column (from `approach.md` / `integrate.py` / `generate.py`), computed per-feature point-biserial correlation with the label and conditional churn-rate spreads, verified determinism of suspect columns by cross-tabulation (not just correlation), checked date columns against each iteration's scoring date (2026-10-01 standard; part1_06 = September 2026 as-of), and traced every flagged column back to its construction in `generate.py`/`clean.py`/`integrate.py` to confirm the mechanism. No column was flagged on name alone — every LEAKED column below was verified against the data and the code. The `part1_13`–`part1_15` pass used `leakage_audit_13_15.py` (adapted from `leakage_audit.py`: LABELS extended to the three new tables, all labeled `churned` with scoring 2026-10-01, raw output to `part1_LEAKAGE_AUDIT_raw_13_15.json`; all thresholds and checks unchanged), plus hand verification of window bounds in `clean/` source tables and binary-feature cross-tabs.

## Verdicts

### part1_01 — Star-Schema Baseline — **LEAKED**
Label: `ever_churned_line` (16.3%).
| Column | Rationale |
|---|---|
| `pct_arr_churned` | **Deterministic label proxy**: `pct_arr_churned > 0 ⟺ ever_churned_line` exactly (2000/2000 verified). It is `churned_arr / total_arr` where `churned_arr = total − active` — the label in continuous form. Must be dropped. |
| `churned_arr` | Near-deterministic with the label (corr 0.79); the monetary twin of the same circularity. Must be dropped. |
Remaining features (health, NPS, usage, hero share, HHI, `active_arr`, dates) are knowable at scoring; `signup_date` max 2026-06-14 — temporally clean.

### part1_02 — Event-Sourced Log — **LEAKED**
Label: `churned` (28.8%).
| Column | Rationale |
|---|---|
| `days_since_last_usage` | AUC 0.992 vs label; `> 90` days perfectly separates (328/328 churned, 0 retained). Measures **post-churn silence**, not pre-churn behavior — the iteration's own approach.md admits the median churn happened 102 days before scoring and 54.2% of churned accounts churned >90 days ago, so the trailing window is entirely silence. |
| `events_90d` / `usage_events_90d` / `health_velocity_score` / `velocity_trend_180d` | Same post-churn-silence mechanism (inverse AUCs 0.92/0.92/0.92/0.85); the honest pre-churn-anchored test in the approach shows **no** separation on any channel. |
| `tickets_opened_90d` (SUSPECT) | Partially the same mechanism (inv AUC 0.74). |
These features would let a Phase 2 model "predict" churn by detecting that the account already went quiet after churning. All five should be dropped or recomputed on windows anchored before each account's last pre-churn event.

### part1_03 — Wide Feature-Store Panel — **LEAKED**
Label: `ever_churned` (33.2%).
| Column | Rationale |
|---|---|
| `months_observed` | AUC 0.96 (mean 23.5 retained vs 12.5 churned); counts only *present* panel months, and post-churn months are structurally absent — the feature encodes the outcome's footprint. |
| `api_calls_latest_w` / `nps_latest` / `n_products_latest` (SUSPECT) | "Latest snapshot" is taken from the last grid row, which for churned accounts is a post-churn NaN row: 86–95% null for churned vs ~1–2% for retained. The missingness itself encodes the label; a missingness indicator would be a laundered leak. |
The trajectory block (`usage_slope_6m`, `arr_trend_6m`) is legitimately built from the last 6 *observed* (pre-churn) months and stays.

### part1_04 — Contracts + Tickets + Telemetry — **CLEAN**
Label: `churned` (16.75%). No feature exceeds |corr| 0.3 with the label; all ticket opens ≤ 2026-09-28, telemetry 2026-07-04…2026-10-01, `contract_start_date` all ≤ scoring. Caveats (not leakage): `arr_usd`/`line_revenue_usd` are exact dupes (r=1.0) and `avg_dau`/`avg_api_calls` near-dupes (r=0.999) — redundancy for Phase 2 to dedupe; `avg_resolution_hours` mixes resolution outcomes that may land just after scoring for late-September tickets (negligible).

### part1_05 — Corporate Family Graph — **LEAKED**
Label: `churned` (18.7%).
| Column | Rationale |
|---|---|
| `family_churn_rate` | Built as `groupby(ultimate_parent)["churned"].transform("mean")` — the label aggregated **including the account itself**. Verified: for all 39 orphan accounts (family_size=1) it equals the account's own label exactly; at every rate level the conditional churn rate equals the feature value to the decimal. Must be recomputed leave-one-out or dropped. |
| `family_churned_any` (SUSPECT) | Same self-inclusion (`transform("max")`); =1 for 100% of churned accounts by construction. |
| `parent_is_churned` (SUSPECT) | The parent's own contemporaneous label mapped onto the row — label-derived; family-correlated by design so it carries real signal, but it is another account's outcome, not a knowable pre-scoring attribute. |
Graph features (`depth`, `family_size`, `family_arr`, `ultimate_parent`) are clean.

### part1_06 — SCD-2 / Late-Arriving Panel — **SUSPECT**
Label: `churned` (17.8%), scoring = September 2026 as-of.
| Column | Rationale |
|---|---|
| `aur_final` | Built from the "final truth" usage view that ignores `arrived_at` — it bakes in September usage events that arrived 1–2 months **after** the scoring as-of (the planted late-arrival pattern). `aur_asof` is what was actually knowable; use it instead. |
| `usage_trend_3m` | Computed from `aur_final` over Jul–Sep despite the "as-of" comment in code — same post-scoring backfill contamination. |
Magnitude is small (0.962 corr with `aur_asof`) but the mechanism is real temporal leakage; `expanded_mar_sep`/`contracted_mar_sep`/`api_calls` (as-of) are clean.

### part1_07 — Surveys + Stated-vs-Revealed — **LEAKED**
Label: `churned` (11.85%), scoring 2026-10-01.
| Column | Rationale |
|---|---|
| `p_churn_latent` | **The DGP's ground-truth churn probability** — the label is drawn as `Bernoulli(p_churn_latent)` in `generate.py`. It can never exist in production; corr 0.55 only because of the Bernoulli draw noise. Must be dropped. |
| `clv_12m` | Formula is `arr·(1 − p_churn) + …` — built directly from the unknowable true `p_churn`, plus a forward-looking 12-month value. Truth-derived leak; must be dropped. |
All survey/behavioral/support features are pre-scoring and clean; `days_to_renewal` is a knowable contract term (and a legit DGP driver).

### part1_08 — Multi-Currency Billing — **LEAKED**
Label: `churned` (17.75%).
| Column | Rationale |
|---|---|
| `clv_12m` | Same `arr·(1 − p_churn)` generative-truth formula as part1_07 (corr −0.25; low only because CLV is ARR-scaled). Must be dropped. |
(No `p_churn_latent` column in this table.) Billing/FX features, `days_to_renewal`, invoice-aging are pre-scoring and clean.

### part1_09 — Telemetry De-botted — **LEAKED**
Label: `churned` (15.4%).
| Column | Rationale |
|---|---|
| `clv_12m` | Same truth-derived formula (corr −0.13). Must be dropped. |
Telemetry, funnel, support, engagement features are pre-scoring and clean.

### part1_10 — Support Threading — **LEAKED**
Label: `churned` (12.67%), scoring 2026-10-01, churn = hero cancellation/non-renewal within 90 days.
| Column | Rationale |
|---|---|
| `p_churn_latent` | DGP ground truth (corr 0.62 — strongest of the four). Must be dropped. |
| `clv_12m` | Truth-derived (`1 − p_churn`). Must be dropped. |
`renewal_date` values after scoring are fine (knowable future contract dates, not outcomes); `days_to_renewal` is a legit knowable driver; ticket threading/SLA features are built from tickets created before scoring.

### part1_11 — Commercial / CPQ — **LEAKED**
Label: `churned` (12.72%).
| Column | Rationale |
|---|---|
| `p_churn_latent` | DGP ground truth (corr 0.52). Must be dropped. |
| `clv_12m` | Truth-derived. Must be dropped. |
`renewal_terms` (auto/manual/evergreen), `term_months`, `auto_renew`, discount/quote/note features are knowable pre-scoring attributes; `n_notes_12m=7`'s 100% churn cell is a single account (noise, not leakage).

### part1_12 — Marketing Attribution — **LEAKED**
Label: `churned` (12.22%).
| Column | Rationale |
|---|---|
| `p_churn_latent` | DGP ground truth (corr 0.48). Must be dropped. |
| `clv_12m` | Truth-derived. Must be dropped. |
All funnel/touch/campaign windows are explicitly shifted to stay before scoring; `demo_request_ever`, `funnel_velocity_days` clean.

### part1_13 — Partner/Channel Angle — **CLEAN**
Label: `churned` (10.25%), scoring 2026-10-01. No feature exceeds |corr| 0.08 with the label (strongest: `health_score` −0.068; top AUC 0.56); no name-hits; binary churn-rate spreads all ≤ 0.25 with the widest coming from single-digit cells. No date columns in the table. Temporal check: `integrate.py` filters deals only on the lower bound (`close_date >= scoring − 1y`), but the data respects the upper bound — `clean/direct_deals.csv` max close_date 2026-10-01 and `clean/deal_registrations.csv` max reg_date 2026-10-01 — so the 12-month booking aggregates (`booked_arr_12m`, `channel_booked_arr`, `channel_arr_pct`, `channel_deals_12m`) contain no post-scoring deals, and `primary_partner_id/tier` use only pre-scoring registrations. No `p_churn_latent`/`clv_12m`; the label logit uses features as DGP drivers (intended signal, not leakage).

### part1_14 — Security-Incident Flavored — **CLEAN** (minor caveat)
Label: `churned` (11.0%), scoring 2026-10-01. No feature exceeds |corr| 0.08 (strongest: `champion_logins_30d` +0.08; top AUC 0.59). Alert clusters and threat-block days are bounded 2026-07-03…2026-09-30; incidents opened ≤ 2026-09-30. Caveat (not leakage): `is_open` in `clean.py` means "still open at snapshot," and 36 of 2,938 closed incidents (34 accounts) resolved 2026-10-01…2026-10-25, so `mean_mttr_h`/`open_incidents` mix a small amount of post-scoring resolution state — same negligible class as part1_04's `avg_resolution_hours`. The wide spreads on `p2_incidents_12m`/`open_incidents` cross-tabs trace to 2-account cells (noise).

### part1_15 — Audit-First Data Quality — **CLEAN**
Label: `churned` (7.45%), scoring 2026-10-01. No feature exceeds |corr| 0.07 (strongest: `n_products` −0.066; top AUC 0.58). Every feature comes from the trusted slices; trusted tickets created ≤ 2026-10-01, sales activities close ≤ 2026-10-01, telemetry weeks ≤ 2026-09-27. Caveat (not leakage): `mean_resolution_days` mixes resolution outcomes that land just after scoring for late-September tickets (same negligible class as part1_04; corr 0.02).

## Summary table

| Iteration | Label | Label rate | Verdict | Drop before Phase 2 | Notes |
|---|---|---|---|---|---|
| part1_01 | `ever_churned_line` | 16.3% | **LEAKED** | `pct_arr_churned`, `churned_arr` | `pct_arr_churned>0 ⟺ label` exactly |
| part1_02 | `churned` | 28.8% | **LEAKED** | `days_since_last_usage`, `events_90d`, `usage_events_90d`, `health_velocity_score`, `velocity_trend_180d` (+`tickets_opened_90d` suspect) | Post-churn silence; AUC up to 0.99 |
| part1_03 | `ever_churned` | 33.2% | **LEAKED** | `months_observed` (+`*_latest` missingness suspect) | Outcome-footprint via absent post-churn months |
| part1_04 | `churned` | 16.75% | **CLEAN** | — | Dedupe exact-duplicate feature pairs |
| part1_05 | `churned` | 18.7% | **LEAKED** | `family_churn_rate` (+`family_churned_any`, `parent_is_churned` suspect) | Label aggregated including self; exact for orphans |
| part1_06 | `churned` | 17.8% | **SUSPECT** | `aur_final`, `usage_trend_3m` (prefer `aur_asof`) | Late-arriving September events baked into "final" view |
| part1_07 | `churned` | 11.85% | **LEAKED** | `p_churn_latent`, `clv_12m` | DGP ground truth + truth-derived CLV |
| part1_08 | `churned` | 17.75% | **LEAKED** | `clv_12m` | Truth-derived CLV |
| part1_09 | `churned` | 15.4% | **LEAKED** | `clv_12m` | Truth-derived CLV |
| part1_10 | `churned` | 12.67% | **LEAKED** | `p_churn_latent`, `clv_12m` | DGP ground truth |
| part1_11 | `churned` | 12.72% | **LEAKED** | `p_churn_latent`, `clv_12m` | DGP ground truth |
| part1_12 | `churned` | 12.22% | **LEAKED** | `p_churn_latent`, `clv_12m` | DGP ground truth |
| part1_13 | `churned` | 10.25% | **CLEAN** | — | Strongest \|corr\| 0.07; deal/reg windows data-bounded ≤ scoring |
| part1_14 | `churned` | 11.0% | **CLEAN** | — | Telemetry 07-03…09-30; mttr mixes 36 post-scoring resolutions (minor caveat) |
| part1_15 | `churned` | 7.45% | **CLEAN** | — | Trusted slices only; all source dates ≤ scoring |

**Counts:** 15 tables audited → **10 LEAKED, 1 SUSPECT, 4 CLEAN.**

## Cross-cutting patterns for Phase 2
1. **Generative-truth features (most dangerous, 6 tables):** `p_churn_latent` (07/10/11/12) is the literal probability the label was drawn from, and `clv_12m` (07/08/09/10/11/12) is computed from `1 − p_churn`. These can never exist in production, and their modest correlations (−0.03 to 0.62) make them easy to miss — a tree model would still exploit the definitional link. **Drop both columns from every table before any Phase 2 training.**
2. **Post-outcome windows (02/03):** trailing-window features computed at scoring time over periods that include post-churn silence/absence. Fix by anchoring windows to the last pre-outcome event, not the scoring date.
3. **Self-in-label aggregates (05):** family features must be recomputed leave-one-out; the current `family_churn_rate` is partially the label itself.
4. **Label re-expression (01):** `pct_arr_churned` is the label in continuous form — check every table for features that are algebraic transforms of the label.
5. **As-of vs final views (06):** any "final/restated" column must be re-derived strictly from data that had arrived by the scoring as-of.
6. **One-sided window filters (13/14/15 — turned out clean):** all three `integrate.py` files filter trailing windows only on the lower bound (`>= scoring − 1y`) with no upper bound; the data happens to respect scoring (deals/regs/tickets/sales max 2026-10-01, telemetry ≤ 2026-09-30), so no post-scoring data entered. Future iterations must re-verify the upper bound in the source tables, not just the filter code — a single late row would silently leak.

## Phase 2 pre-training checklist (winning iteration)
- [ ] Drop all LEAKED columns listed above for the winning iteration
- [ ] Recompute or drop SUSPECT columns (`months_observed`-style absence features, `aur_final`, family aggregates)
- [ ] Re-run this audit's correlation + determinism checks on the cleaned table and confirm no feature has AUC > 0.85 vs the label
- [ ] Confirm no date column exceeds the scoring date
- [ ] part1_04, part1_13, part1_14, part1_15 are clean as-is and need only the noted caveats (04: feature-dedup; 14: negligible mttr snapshot effect; 15: negligible resolution-day tail)
