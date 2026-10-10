# p2_07 Shadow-Mode Pilot Design

## Purpose
Run the trigger catalog in **shadow mode for two quarters** (6 months): log
what the triggers *would* have flagged, take no automated action on the
flags, then measure empirical precision, lead time, and alert volume against
realized churn before any trigger routes outreach on its own.

## Why shadow mode first
The catalog's thresholds were tuned on a single as-of snapshot. A snapshot
cannot tell us (a) true lead time (days from first firing to the churn
event), (b) trigger stability (does T1 flap on/off week to week?),
(c) alert fatigue at the CSM-book level, or (d) whether firing correlates
with churn *because* someone already intervened (intervention
contamination). Shadow mode measures all four without acting on the flags.

## Longitudinal data contract (what production must build)
The snapshot table must become a point-in-time feature store. Weekly
snapshots (Sunday 00:00 UTC as-of) of, per account:
- usage telemetry: the inputs behind `usage_decay_90d` (raw 90-day usage
  series), `active_user_ratio`, `api_calls_weekly`, `feature_depth`
- champion activity: `champion_logins_30d` (daily login events collapsed)
- support: `tickets_opened_12m` increments, `escalations_12m` increments,
  `p1_tickets_12m` increments with event timestamps
- contract events: `downgraded_12m` with event date, `days_to_renewal`
- survey: `has_valid_survey`, `valid_nps_mean` refresh cadence
- outcome: churn event date (hero cancellation/non-renewal), for 90-day
  forward labeling from each snapshot

Freshness SLA: telemetry ≤ 24h lag, support events ≤ 4h, contract events
same-day. Owner: data engineering. Backfill: 6 months of weekly snapshots
before pilot start (needed to evaluate T7's decay lookback honestly).

## Pilot mechanics
1. **Scoring cadence:** every Monday 06:00, score all accounts against the
   8 catalog rules using the latest snapshot. Log: account_id, trigger_id,
   snapshot date, feature values at firing, days_to_renewal at firing.
2. **Blinding:** CSMs are NOT shown shadow flags (prevents behavior change
   that would contaminate the precision read). CSMs work their normal
   process; RevOps audits that no shadow-flagged account received
   out-of-process attention.
3. **Outcome join:** 90 days after each snapshot, join firings to realized
   churn. Compute per trigger: empirical precision, alert volume, median
   lead time (first-firing date to churn date), and firing stability
   (share of flagged accounts still flagged 4 weeks later).
4. **Intervention-contamination handling:** every CSM save action is logged
   with a treated flag and timestamp (per p2_13's discipline). Sensitivity
   read: precision among flagged-but-untreated accounts.

## Graduation gates (all must hold at the 6-month review)
- Per-trigger empirical precision ≥ 1.5x the base churn rate, sustained
  across both quarters (no single-quarter flukes).
- Median lead time ≥ 30 days (a trigger that fires the week of renewal is
  an obituary, not an early warning).
- Alert volume ≤ 15% of the CSM book per week per trigger family
  (fatigue cap; owner: RevOps).
- Firing stability ≥ 60% (a trigger that flaps weekly cannot drive a play).

## What graduates, what doesn't
Triggers passing all gates graduate to **trigger-routed outreach**: firing
creates a task for the catalog owner with the catalog SLA. Triggers failing
precision graduate to **model-feature duty only** (their signal stays in
the score, the rule does not page a human). Triggers failing stability are
rebuilt on the longitudinal contract (true change-point logic) or retired.

## Risks and mitigations
- **Alert fatigue:** weekly per-book volume caps; triggers are additive to,
  not a replacement for, the score-ranked worklist during the pilot.
- **Seasonality:** two quarters covers one renewal cycle for most books;
  annual-renewal cohorts need a full year for a second read (stated limit).
- **Silent accounts (T7):** the pilot's most valuable read - if "dark +
  decaying" does not beat the base rate on realized churn, the nonresponse
  story stays a modeling feature, not an operating trigger.
