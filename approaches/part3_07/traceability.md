# Traceability — part3_07

Every number appearing in `README.md` or `slides.md` resolves to a named
artifact below. Format: `claim | artifact(s) | key(s)/section | derivation or "direct"`.

| Claim | Artifact(s) | Key(s) / section | Derivation or "direct" |
|---|---|---|---|
| Modeling table 2,000 rows × 47 cols; 45 features + label post-drop | `approaches/part1_TOURNAMENT.md` | Winner rationale 1; Phase 2 handoff | direct (verified on disk: 2,000 × 47, drop 2) |
| Label `churned` = SentinelShield hero-product 90-day cancellation/non-renewal, scoring date 2026-10-01 | `approaches/part2_07/approach.md` | Method | direct |
| Base churn rate 11.85% (237/2,000) | `approaches/part2_07/metrics.json` | `churn_rate: 0.1185` | direct; 237 = 0.1185 × 2000 (stated in part1_TOURNAMENT.md) |
| Test frame 400 rows, 47 churners (11.75%), stratified 80/20 seed 42 | `approaches/part2_07/metrics.json` | `n_test: 400`, `test_churn_rate: 0.1175` | direct; 47 = 0.1175 × 400 |
| Dropped before training: `p_churn_latent`, `clv_12m`, IDs, survey distractors/trust machinery | `approaches/part2_07/approach.md` | Leakage | direct; audit PASS, 33 features clean |
| Scorer: HistGradientBoosting, class_weight="balanced", isotonic CalibratedClassifierCV cv=5, train-only | `approaches/part2_07/approach.md`; task verified numbers | Method ("p2_01 reference calibrator") | direct |
| Brier 0.1095 → 0.0905 after isotonic calibration (p2_07 frame) | `approaches/part2_07/metrics.json` | `brier_before: 0.109484...`, `brier_after: 0.090523...` | direct (rounded) |
| AUC 0.8092, PR-AUC 0.3515 (p2_07 frame) | `approaches/part2_07/approach.md` | Evaluation | direct (metrics.json: 0.8092339 / 0.3515099) |
| Canonical reference Brier 0.1065 → 0.0905; AUC 0.8040, PR-AUC 0.3483 | `approaches/part2_01/metrics.json` | `brier_before`, `brier_after`, `auc`, `pr_auc` | direct |
| Worklist K=40: 11 churners, precision 0.275, recall 0.234, $19.20M expected / $19.65M actual | `approaches/part2_07/metrics.json` | `worklist` | direct (19201607.96 → $19.20M; 19652000 → $19.65M; 11/40 = 0.275; 11/47 = 0.234) |
| Canonical reference worklist: 10 churners, precision 0.25, recall 0.2128, $19.46M expected / $18.56M actual | `approaches/part2_01/metrics.json` | `worklist` | direct (19456099.49 → $19.46M; 18562000 → $18.56M) |
| Uncalibrated baseline: 16 churners, $9.85M actual | `approaches/part2_01/metrics.json` | `incumbent_head_to_head.baseline_actual_churners_caught: 16`, `baseline_actual_churned_arr_captured: 9847000` | direct |
| K=20: 5 churners, precision 0.25, $13.54M expected / $14.99M actual | `approaches/part2_07/metrics.json` | `sensitivity["5pct"]` | direct (13540492.12 → $13.54M; 14991000 → $14.99M) |
| K=60: 13 churners, precision 0.2167, $22.80M expected / $20.91M actual | `approaches/part2_07/metrics.json` | `sensitivity["15pct"]` | direct (22799098.80 → $22.80M; 20907000 → $20.91M) |
| K=40 ≈ 10% of the 400-row evaluation frame | `approaches/part2_07/metrics.json` | `n_test: 400`, `worklist.capacity: 40` | 40/400 = 10% |
| 6 swaps; 5 high-ARR non-churners screened out ($4.33M, $3.04M named); 2 real churners pulled in ($1.09M, $1.71M); one $1.04M churner screened out | `approaches/part2_07/approach.md` | Evaluation | direct (prose numbers in the memo) |
| Thresholds chosen on train only; precision-maximizing grid; alert bounds 3%–40% | `approaches/part2_07/approach.md`; `metrics.json` notes | Method | direct |
| Trigger union fires on 66.5% of test accounts (266/400) | `approaches/part2_07/metrics.json` | `trigger_union_test_alert_rate: 0.665`, `trigger_union_test_alerts: 266` | direct |
| T8: 10/23 flagged churned = 43.5% test precision; median 50-day renewal runway; owner Account Executive; renewal plan within 5 business days | `approaches/part2_07/trigger_catalog.csv` | T8 row: `test_precision 0.4348`, `leadtime_proxy_median_days_to_renewal 50.0`, `owner`, `sla`; `test_alerts_n 23` | 10/23 = 0.4348 direct from CSV |
| T4: 30.0% test precision; owner Support Lead; exec review within 24 hours; lead-time proxy 148.5 days | `approaches/part2_07/trigger_catalog.csv` | T4 row | direct |
| T1: rule `usage_decay_90d <= 0.803`; 22% alert volume; test precision 12.5%; lead-time proxy 171.5 days; owner CSM; outreach within 2 business days | `approaches/part2_07/trigger_catalog.csv` | T1 row | direct (0.803 threshold, 0.22 train alert rate, 0.125 test precision) |
| T3: rule `champion_logins_30d <= 0`; test precision 13.0%; lead-time proxy 209 days; owner CSM; champion check-in within 5 business days | `approaches/part2_07/trigger_catalog.csv` | T3 row | direct |
| T6: rule `downgraded_12m == 1`; test precision 14.7%; owner Account Executive; save conversation within 3 business days | `approaches/part2_07/trigger_catalog.csv` | T6 row | direct |
| T7: rule `has_valid_survey == 0 AND usage_decay_90d <= 0.715`; test precision 19.1%; lead-time proxy 128 days; owner CSM; discovery call within 5 business days | `approaches/part2_07/trigger_catalog.csv` | T7 row | direct |
| T2 RETIRED: train precision 28.4% → test 6.25%; 4% slice threshold overfit | `approaches/part2_07/trigger_catalog.csv`; `part2_07/approach.md` | T2 row (`train_precision 0.2836`, `test_precision 0.0625`, `train_alert_rate 0.0419`) | direct |
| T5 RETIRED: fires on 48% of the book at ~base-rate precision (14.3% train / 12.5% test) | `approaches/part2_07/trigger_catalog.csv`; `part2_07/approach.md` | T5 row (`train_alert_rate 0.4981`, `test_alert_rate 0.48`, `train_precision 0.143`, `test_precision 0.125`) | direct |
| Go-live bar: trigger precision ≥ 2× base churn rate = 23.7% on an 11.85% base | `approaches/part2_TOURNAMENT.md` §4 (adopted p2_13 ops runbook); `part2_07/metrics.json` `churn_rate` | Adopted elements | 2 × 0.1185 = 0.237 (derivation). Note: `shadow_pilot.md` states 1.5× sustained as a pilot gate; the adopted production go-live bar is 2×. |
| T8 (43.5%) and T4 (30.0%) clear the 2× bar; T1/T3/T6/T7 ship gated | `approaches/part2_07/trigger_catalog.csv` | test_precision column vs 0.237 bar | comparison (derivation) |
| Total ARR $1,975.1M; SentinelShield $1,161.6M (58.8%); PostureLens $166.1M (704 orders); NetBarrier $128.1M (525); ThreatScope $126.8M (532) | `approaches/part1_07/outputs/eda_findings.json` | `/top_ordered_items_by_arr`; `/value_concentration/hero_product_share_of_total_arr: 0.588` | direct ($1,975.1M stated in part1_07/approach.md EDA) |
| Mean 2.72 products/account; top-10% accounts hold 29% of ARR | `approaches/part1_07/outputs/eda_findings.json` | `/value_concentration/mean_products_per_account: 2.72`, `/top_10pct_accounts_share_of_arr: 0.29` | direct |
| Top account ACC-01909 $8.14M (churned) | `approaches/part1_07/outputs/eda_findings.json` | `/top_accounts_by_arr[0]`: total_arr_usd 8135000, churned 1 | direct |
| Valid survey coverage 64%; fraud filter 2,044 raw → 1,768 valid (86.5%), 276 quarantined (13.5%) | `approaches/part1_07/approach.md` | Cleaning / dedup; `/fraud_filter_impact` in eda_findings.json | direct |
| Respondents churn 9.9% vs non-respondents 15.3% | `approaches/part1_07/approach.md` | EDA stated-vs-revealed | direct |
| Valid NPS corr 0.091 with behavioral health, −0.056 with churn; behavioral health corr −0.223 with churn | `approaches/part1_07/outputs/eda_findings.json` | `/stated_vs_revealed/*` | direct (rounded to 0.09 / −0.06 / −0.22) |
| Stated-vs-revealed gap is a documented null (top decile 10.2% vs bottom 10.9% vs 11.85% base) | `approaches/part1_07/outputs/eda_findings.json`; `approaches/part1_TOURNAMENT.md` | `/stated_vs_revealed_gap/top_gap_decile_churn: 0.102`, `bottom_gap_decile_churn: 0.109`; known defect | direct |
| 9 segments (tenure × breadth, a-priori cutoffs) → 9 distinct playbooks | `approaches/part2_05/approach.md`; `part2_05/segment_metrics.csv` | Method; `segment,playbook` columns | direct |
| Per-segment fits lost to global+interactions: AUC 0.7438 vs 0.8099; PR-AUC 0.3247 vs 0.3516 | `approaches/part2_05/approach.md` | Evaluation | direct |
| Segment churn concentration (train/test): mid_2to5y__single 64/14; new_lt2y__single 35/8; mid_2to5y__few_2to4 26/7 | `approaches/part2_05/segment_metrics.csv` | `churners_train`, `churners_test` columns | direct |
| 3 broad-portfolio segments fell back to the global model (shrink-to-global rule) | `approaches/part2_05/approach.md`; `segment_metrics.csv` | `fell_back_to_global` = True for the three `broad_5plus` segments | direct |
| No measured motion moves churn: ATE (IPW) −0.0089, 95% CI [−0.0271, 0.0075] spans zero | `approaches/part2_TOURNAMENT.md` §p2_08 | Thesis test | direct |
| Freshness SLAs: telemetry ≤7d, support ≤1d, ARR ≤30d, survey ≤90d | `approaches/part2_TOURNAMENT.md` §p2_13 | Thesis test | direct |
| Treated-flag (intervention-contamination) logging; drift monitors (input PSI, score drift, decay gates) | `approaches/part2_TOURNAMENT.md` §4 (adopted p2_13) | Adopted elements | direct |
| Shadow pilot: 2 quarters, weekly Monday scoring, blinded flags, 90-day outcome join | `approaches/part2_07/shadow_pilot.md` | Pilot mechanics | direct |
| Graduation gates: lead time ≥ 30 days, stability ≥ 60%, volume ≤ 15% of book/week/trigger family | `approaches/part2_07/shadow_pilot.md` | Graduation gates | direct |
| Cross-sell white-space is a separate motion, not merged into the churn worklist | `approaches/part2_TOURNAMENT.md` §4 | Adopted elements (d) | direct |
| Falsifications: survival Cox 0.5829 vs binary logistic 0.8267; BTYD AUC 0.5000 (tenure sort); embeddings delta PR-AUC +0.0005; CF recall@3 0.752 vs popularity 0.760 | `approaches/part2_TOURNAMENT.md` §p2_02, §p2_06, §p2_14, §p2_10 | Thesis tests | direct |
| Synthetic-data caveat: generator known, separation lower on real data, absolute numbers not production forecasts | `approaches/part2_TOURNAMENT.md` §6 | Phase 3 handoff note | direct |
| Involuntary churn unseparated (no reason codes; all churn treated as voluntary) | `approaches/part2_TOURNAMENT.md` §5 (p2_07 known defects) | Known, accepted defects | direct |
| Lead time is a days-to-renewal proxy, not measured days-to-churn; trigger stability unmeasurable on one snapshot | `approaches/part2_07/approach.md` | Limitations | direct |
| Banned numbers (never cited): p2_04/p2_06 dollars-squared expectations; p2_12 stale metrics.json; pre-tournament 3,000-account outputs | `approaches/part2_TOURNAMENT.md` §6 | "Numbers that must never be cited" | excluded by policy |
