# VP Checklist — 10 Questions Pre-Answered (part3_07)

One sentence each, with the citation that backs it.

1. **Why account-level?** Because the decision (which account gets a human
   this week), the label (hero-product cancellation within 90 days), and the
   dollars (account ARR) all live at the account grain — the CSM's unit of
   ownership. *(part2_07/approach.md, Framing; part1_TOURNAMENT.md, label semantics)*
2. **Why believe the dollars?** Because the probabilities are calibrated —
   Brier 0.1095 → 0.0905 — so expected ARR at risk priced the evaluation
   book at $19.20M and reality came in at $19.65M. *(part2_07/metrics.json:
   `brier_before`, `brier_after`, `worklist`)*
3. **Fewer churners (11 vs 16) — why switch?** Because the 16-churner
   uncalibrated list captured only $9.85M of actual churned ARR while the
   11-churner calibrated list captured $19.65M — it finds small accounts and
   misses the big ones. *(part2_01/metrics.json: `incumbent_head_to_head`;
   part2_07/metrics.json: `worklist`)*
4. **Where did K=40 come from?** It is illustrative — 10% of the 400-row
   evaluation frame — and it is bracketed by measured sensitivity at K=20
   (5 churners, $14.99M) and K=60 (13 churners, $20.91M), never derived from
   headcount. *(part2_07/metrics.json: `worklist`, `sensitivity`, `n_test`)*
5. **Why triggers, not just the score?** Because the score says who is
   risky while the trigger says what changed, who owns the next step, and
   by when — and the gate won on both counts anyway (11/$19.65M vs
   10/$18.56M). *(part2_07/approach.md, Evaluation; part2_07/trigger_catalog.csv)*
6. **What does the data NOT support?** Any measured save motion (the causal
   estimate's CI spans zero), per-segment model fits (they lost to
   global+interactions), survival/BTYD/embeddings/CF over the baseline, and
   the stated-vs-revealed gap as a signal — all falsified or null on the
   record. *(part2_TOURNAMENT.md §§p2_08, p2_05, p2_02, p2_06, p2_14, p2_10;
   part1_07/outputs/eda_findings.json: `/stated_vs_revealed_gap`)*
7. **What breaks first?** Stale telemetry (freshness SLAs: 7d/1d/30d/90d),
   then alert fatigue if a retired trigger is ever re-enabled without
   re-proof, then threshold drift — which is why the drift monitors exist.
   *(part2_TOURNAMENT.md §4, §p2_13; README.md, Limitations)*
8. **Why not sort by ARR?** Because an ARR sort ignores churn likelihood —
   the trigger gate screened out a $4.33M and a $3.04M non-churning account
   the score alone would have sent CSMs chasing. *(part2_07/approach.md,
   Evaluation)*
9. **Do segments change any decision?** Not the ranking — per-segment fits
   lost (AUC 0.7438 vs 0.8099) — but they change the conversation: the
   9-segment → 9-playbook map is the operating library the triggers route
   into. *(part2_TOURNAMENT.md §p2_05; part2_05/segment_metrics.csv)*
10. **Two more quarters of real data?** That is the shadow pilot: weekly
    blinded scoring, 90-day outcome joins, and graduation gates (precision ≥
    2× base rate, lead time ≥ 30 days, stability ≥ 60%) before any trigger
    pages a human. *(part2_07/shadow_pilot.md; part2_TOURNAMENT.md §4)*
