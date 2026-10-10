# Slides: Churn Early-Warning — The Operator's Manual (part3_07)

*12-slide outline. Each slide carries one full-sentence TLDR headline plus
talking points with a key number and an artifact citation. All three
assignment parts are covered; the final slide is the ask.*

---

## Slide 1 — The manual, not the model, is the deliverable.

- This case study ships an operating contract for the people who work the
  churn worklist: 6 live triggers, each with a rule, a threshold, an owner
  role, an SLA, and a script for the call (`approaches/part2_07/trigger_catalog.csv`).
- The target reader is the CSM, not the VP: every trigger section answers
  "what fired, who acts, by when, what do I say" (`README.md`, trigger playbook).
- Success for this angle is adoption by operators — clarity of instruction,
  not analytical depth (`approach.md`, differentiation contract).

## Slide 2 — Part 1 built a foundation the list can stand on: 2,000 accounts, a clean 90-day hero-churn label at 11.85%.

- Label: `churned` = SentinelShield cancellation/non-renewal within 90 days
  of 2026-10-01; base rate 11.85% (237/2,000) — the Phase 1 winner's
  canonical label (`approaches/part1_TOURNAMENT.md`; `part2_07/approach.md`).
- Leakage was incidental and dropped before training: the DGP's answer key
  (`p_churn_latent`) and the forward-looking `clv_12m` were removed, with
  IDs excluded from features (`approaches/part1_TOURNAMENT.md`, Phase 1 handoff).
- The book is concentrated: $1,975.1M total ARR, SentinelShield $1,161.6M
  (58.8%), top 10% of accounts hold 29% of ARR, largest account $8.14M —
  and even that account churned (`approaches/part1_07/approach.md`;
  `part1_07/outputs/eda_findings.json`).

## Slide 3 — Part 1's survey lesson: never trust what accounts say without checking what they do.

- Valid survey coverage is 64%, gated by a fraud filter that quarantined
  13.5% of raw responses (2,044 → 1,768 valid) (`approaches/part1_07/approach.md`).
- Non-respondents churn at 15.3% vs 9.9% for respondents — silence is a risk
  feature, not missing data, and it is why "dark account" is a trigger
  (`approaches/part1_07/approach.md`).
- Valid NPS correlates only −0.06 with churn vs −0.22 for behavioral health
  — roughly 4× weaker — so survey scores are call context, never list gates
  (`approaches/part1_07/outputs/eda_findings.json`).

## Slide 4 — Part 2 built the list in three steps: calibrated score, trigger gate, expected-dollar rank.

- Step 1: HistGradientBoosting with isotonic calibration (train-only);
  Brier 0.1095 → 0.0905, so a stated 30% means ~30 in 100
  (`approaches/part2_07/metrics.json`: `brier_before`, `brier_after`).
- Step 2: the trigger gate — only accounts firing ≥1 trigger are eligible;
  thresholds chosen on train only with alert-volume bounds 3%–40%
  (`approaches/part2_07/approach.md`; `trigger_catalog.csv`).
- Step 3: fired accounts ranked by calibrated p × ARR; K=40 ≈ 10% of the
  400-row evaluation frame (47 churners) (`approaches/part2_07/metrics.json`: `worklist`).

## Slide 5 — The trigger-routed list beats the score-only list on both counts: 11 churners and $19.65M vs 10 and $18.56M.

- Trigger-routed K=40: 11 churners (precision 0.275, recall 0.234),
  $19.20M expected vs $19.65M actual churned ARR captured
  (`approaches/part2_07/metrics.json`: `worklist`).
- Canonical score-only reference: 10 churners, $19.46M expected, $18.56M
  actual — the gate wins on churners *and* dollars
  (`approaches/part2_01/metrics.json`: `worklist`).
- The 6 swaps: the gate screened out 5 high-ARR non-churners (incl. $4.33M
  and $3.04M) and pulled in 2 real churners ($1.09M, $1.71M); disclosed
  cost — one $1.04M churner screened out (`approaches/part2_07/approach.md`).

## Slide 6 — The calibration story in one comparison: the uncalibrated shortcut catches more churners (16) but half the dollars ($9.85M).

- Uncalibrated probability-ranked baseline: 16 churners, $9.85M actual —
  it finds many small accounts and misses the big ones
  (`approaches/part2_01/metrics.json`: `incumbent_head_to_head`).
- Calibrated EV ranking: 11 churners, $19.65M actual — fewer accounts,
  roughly 2× the dollars (`approaches/part2_07/metrics.json`: `worklist`).
- The dollars are real because the probabilities are honest: Brier
  0.1095 → 0.0905 after isotonic calibration
  (`approaches/part2_07/metrics.json`).

## Slide 7 — T8 is the star trigger (43.5% precision, 50-day runway) and T2/T5 are retired as documented failures.

- T8 (renewal ≤90d + behavioral health in bottom quartile): 10/23 flagged
  churned = 43.5% test precision, median 50-day renewal runway, owner
  Account Executive, renewal plan within 5 business days
  (`approaches/part2_07/trigger_catalog.csv`).
- T4 (≥4 escalations/12m): 30.0% precision, owner Support Lead, exec review
  within 24 hours — the only other trigger clearing the 2× base-rate
  go-live bar of 23.7% (`trigger_catalog.csv`; go-live bar from
  `approaches/part2_TOURNAMENT.md` §4).
- T2 RETIRED: train 28.4% → test 6.3% precision (threshold overfit on a 4%
  slice). T5 RETIRED: fires on 48% of the book at ~base-rate precision —
  support load, not a churn signal (`trigger_catalog.csv`;
  `approaches/part2_07/approach.md`).

## Slide 8 — The six live triggers route into a 9-playbook library by lifecycle segment, and segments deliberately do not touch the score.

- Segments: tenure (<2y / 2–5y / >5y) × breadth (1 / 2–4 / 5+), a-priori
  cutoffs; each maps to one distinct playbook (e.g., mid-tenure single →
  land-and-expand; new single → fast-start adoption)
  (`approaches/part2_05/approach.md`; `part2_05/segment_metrics.csv`).
- Per-segment model fits *lost* to one global model with segment
  interactions (AUC 0.7438 vs 0.8099) — so segments are the operating map
  for *what to do*, never a modeling scheme for *who is risky*
  (`approaches/part2_TOURNAMENT.md` §p2_05).
- Routing rule: when a trigger fires, look up the account's segment and open
  the matching playbook; the score still decides the order
  (`README.md`, playbook library).

## Slide 9 — Capacity is a measured band, not a headcount claim: K=20 catches $14.99M, K=40 $19.65M, K=60 $20.91M.

- K=20 (lean): 5 churners, $13.54M expected / $14.99M actual — half the
  effort, 76% of the default band's dollars
  (`approaches/part2_07/metrics.json`: `sensitivity["5pct"]`).
- K=40 (default): 11 churners, $19.20M expected / $19.65M actual — the
  recommended starting point (`metrics.json`: `worklist`).
- K=60 (full-court): 13 churners, $22.80M expected / $20.91M actual — the
  extra 20 accounts buy 2 churners and $1.26M; diminishing returns are
  visible (`metrics.json`: `sensitivity["15pct"]`).
- No band assumes a save rate — coverage is measured churners and captured
  ARR, because no motion has a measured effect
  (`approaches/part2_TOURNAMENT.md` §p2_08).

## Slide 10 — The honesty ledger: what the data does not support, stated as facts.

- No measured save motion exists: the causal estimate's confidence interval
  spans zero, so no treatment-effect number enters any money math
  (`approaches/part2_TOURNAMENT.md` §p2_08: ATE −0.0089, CI [−0.0271, 0.0075]).
- Falsifications stand: survival adds nothing (0.5829 vs 0.8267), BTYD
  collapses to a tenure sort (AUC 0.5), embeddings add nothing at 9 SKUs,
  CF ties popularity, the stated-vs-revealed gap is a documented null
  (`approaches/part2_TOURNAMENT.md` §6).
- Data is synthetic: separation will be lower on real data; absolute numbers
  are not production forecasts (`approaches/part2_TOURNAMENT.md` §6).
- The trigger union fires on 66.5% of accounts before T5's retirement — the
  retirement is what makes the gate a gate
  (`approaches/part2_07/metrics.json`: `trigger_union_test_alert_rate`).

## Slide 11 — Nothing pages a human until the shadow pilot promotes it: two quarters, blinded, with graduation gates.

- Mechanics: weekly Monday scoring of the 8 catalog rules against fresh
  snapshots, firings logged and blinded from CSMs, 90-day outcome join to
  realized churn (`approaches/part2_07/shadow_pilot.md`).
- Graduation gates: per-trigger precision ≥ 2× base rate (23.7%) sustained
  across both quarters, median lead time ≥ 30 days, firing stability ≥ 60%,
  volume ≤ 15% of the book per week per trigger family
  (`approaches/part2_07/shadow_pilot.md`; 2× bar adopted per
  `approaches/part2_TOURNAMENT.md` §4).
- Production wrapper adopted: treated-flag logging on every save action,
  drift monitors (input PSI, score drift, decay gates), freshness SLAs
  (telemetry ≤7d, support ≤1d, ARR ≤30d, survey ≤90d)
  (`approaches/part2_TOURNAMENT.md` §4, §p2_13).

## Slide 12 — The ask: fund the two-quarter shadow pilot and the snapshot store behind it.

- Data engineering: a weekly per-account snapshot store (usage, champion
  activity, support events, contract events, survey refreshes) with six
  months of backfill before the pilot starts
  (`approaches/part2_07/shadow_pilot.md`, longitudinal data contract).
- RevOps: ownership of the blinded shadow log, the 90-day outcome join, and
  the per-trigger precision / lead-time / stability read
  (`approaches/part2_07/shadow_pilot.md`, pilot mechanics).
- CSM leadership: one pod working the gated triggers with treated-flag
  discipline, and agreement that no trigger pages a human until it passes
  the gates (`README.md`, guardrails; `approaches/part2_07/shadow_pilot.md`).
