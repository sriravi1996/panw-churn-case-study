# p2_07 — Behavioral Change-Point / Velocity Triggers

## Framing
The decision: which accounts get human attention *this week*, before the
renewal conversation. A ranked score tells a CSM who is risky; it does not
tell them *what changed* or *who owns the next step*. This iteration
delivers an operational early-warning trigger catalog: stated rules with
thresholds, lookbacks, owners, and SLAs, evaluated on holdout. The ranking
currency stays expected ARR at risk (`metrics.json`: `worklist`), but the
worklist is *trigger-routed* — only accounts firing at least one trigger
are eligible — versus the p2_01 score-routed list.

## Method
Table: `part1_07/modeling_table.csv` (2000 x 47); label `churned`,
hero cancellation/non-renewal within 90 days of 2026-10-01, base rate
11.85% (canonical 90-day full-account churn, spec 1.6 case 1). Dollar
currency `total_arr_usd`. Split: stratified 80/20, seed 42 (test n=400,
47 churners, test rate 11.75%). All preprocessing statistics fit on train;
the test set is touched once.

Eight triggers (catalog: `trigger_catalog.csv`). Continuous thresholds were
chosen on **train only** by a precision-maximizing grid search with alert
volume bounds (3%-40% of train); rule triggers (downgrade, P1) are stated,
not tuned. Because the table is a snapshot, "velocity" is honestly limited
to its trajectory proxies (`usage_decay_90d` as the velocity feature; no
invented longitudinal series). True change-point detection needs the
longitudinal data contract specified in `shadow_pilot.md`. Lead time is
proxied by `days_to_renewal` at firing — a stated proxy, not measured lead
time. Triggers emit no probabilities, so AUC/PR-AUC/Brier and the expected
ARR column reuse the p2_01 reference calibrator on the same split (stated
in `metrics.json` `probabilities_source`).

Leakage: dropped in code before modeling — `p_churn_latent` (class 1,
latent ground truth), `clv_12m` (auxiliary target only, task-forbidden),
exact duplicates `n_order_items`/`max_item_arr`/`z_valid_nps` (class 6),
constant `product_id` (class 6), untrusted survey distractors
`naive_nps_mean`/`naive_csat_mean` and trust machinery
`n_all_responses`/`n_valid_responses`/`validity_rate`. Audit:
`leakage_audit.py` (PASS, 33 features clean).

## Evaluation (`metrics.json` highlights)
- Reference model (reused): AUC 0.8092, PR-AUC 0.3515, Brier 0.1095 -> 0.0905
  (isotonic). Below the canonical-table anchor (0.847) — expected; this
  table's honest baseline, not a target to chase.
- Trigger-routed worklist (K=40, fired accounts ranked by calibrated
  p x ARR): **11 churners caught** (precision@K 0.275, recall 0.234),
  $19.20M expected ARR at risk, **$19.65M actual churned ARR captured**.
- Head-to-head vs p2_01 reference (same split): p2_01 catches **9** churners,
  $20.64M expected, **$17.48M** actual. Trigger routing wins on both counts
  on this frame — more churners *and* more dollars. The two top-40 lists
  differ by 6 swaps: the trigger gate excluded 5 high-ARR non-churners the
  pure EV rank promoted (including the $4.33M and $3.04M accounts) while
  pulling in 2 actual churners ($1.09M + $1.71M) that fired triggers.
  Disclosed, not buried: one actual churner ($1.04M) was in the reference
  list but screened out by the gate.
- Sensitivity: at K=20, 5 churners / $14.99M actual; at K=60, 13 churners /
  $20.91M actual.
- Per-trigger holdout: T8 (renewal <= 90d + low behavioral health) is the
  star — 43.5% precision (10/23), median 50 days of renewal runway. T4
  (escalation burst) 30.0%. T1 (usage-decay cliff) 12.5% at 22% alert volume.
  T7 (dark + decaying) 19.1%. **Falsifications:** T2's active-user-ratio
  cliff did not transfer (train precision 28.4% -> test 6.3%; threshold
  overfit on a 4% slice) and T5 (P1 pain) fires on 48% of the book at
  ~base-rate precision — too broad to be an operating trigger; both are
  flagged for retirement/rebuild in the catalog rather than shipped.

## Key decisions (30 seconds each)
1. **Thresholds on train, precision-maximizing with volume bounds.** Bounds
   stop degenerate 1%-alert "perfect precision" rules; train-only selection
   keeps the holdout honest.
2. **Trigger gate, then EV rank.** The gate is the product decision (a CSM
   acts on *events*); EV ranking inside the gate keeps dollar discipline.
3. **Snapshot honesty.** No synthetic longitudinal series; the memo states
   exactly which proxies stand in for velocity and what production must log.
4. **T5/T2 reported as failures.** A catalog that ships only its winners is
   slideware; the retirement recommendations are part of the deliverable.

## Limitations
- Lead time is a renewal-runway proxy, not measured days-to-churn; the
  shadow pilot (`shadow_pilot.md`) is the path to real lead-time numbers.
- Single snapshot: trigger stability (week-to-week flapping) is unmeasurable
  here — graduation gate #4 in the pilot design.
- The trigger gate helps on this frame but the union fires on 66.5% of test
  accounts (T5 dominates); without T5's retirement the "gate" is nearly the
  whole book.
- Involuntary churn is unseparated (no reason codes; all churn treated as
  voluntary, a documented assumption).
- Capacity K=40 is illustrative (10% of test rows), never an org-chart claim.
