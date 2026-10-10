# Phase 2 Tournament Verdict — Modeling Angles (15 iterations)

**Judge:** Phase 2 judging subagent · **Date:** 2026-10-10
**Read:** part2_JUDGE_BRIEF.md (authoritative), PHASE2_SPEC.md (§1.5, §2.1–2.5, §4),
PHASE2_READINESS.md, part1_TOURNAMENT.md (handoff), all 15 `approach.md` files
(7 reconstructed by the judge from artifacts — see the G5 column in §2),
all `metrics.json` files, `run.sh` outputs, leakage-audit artifacts, and the
named pipeline artifacts on disk. Every number below traces to a
`metrics.json` key or a named artifact; no placeholder survives.

## 1. Rubric recap

Six criteria, 1–5 each, total /30 — approach quality, NOT raw AUC:

1. **Methodological rigor** — split discipline (stratified 80/20, seed 42,
   train-only statistics, calibration fit on train only), leakage audit
   passed, falsification checks attempted for the angle's own claim, edge
   cases as operating rules. Negative results reported, not buried.
2. **Protocol fidelity** — metrics.json complete and arithmetically sound,
   head-to-head vs the p2_01 reference on the same split, business metric on
   the iteration's OWN ranking, sensitivity at 5%/15%, G6 reference
   consistency clean.
3. **Honesty of claims** — every number traces to an artifact; capacity
   parameterized with sensitivity, never org-chart-invented; close-rates and
   treatment effects labeled as assumptions; no synthetic effect as measured;
   no self-grading; trade-offs disclosed. **One confirmed honest-claims
   violation caps this criterion at 2/5.**
4. **Angle distinctness** — the iteration tests ITS angle's thesis, is
   materially different from p2_01 in its brief-defined way, and earns its
   complexity. An honest "the fancy method added nothing" outscores a
   decorative win.
5. **Business usefulness** — the decision served is named; ranking currency
   matches the decision; outputs wire to an owner, a trigger, and a play;
   capacity-aware; speaks the business's language.
6. **Reproducibility & clarity** — `bash run.sh` exit 0 (G1), environment
   note present, memo ≤2 pages with the required sections, VP-defensible in
   30 seconds per decision, numbers cited to metrics.json keys.

**Calibration rules:** AUC/PR-AUC deltas under ~0.02 are noise — judge the
approach, not the leaderboard. Ties break toward the clearer production
path (shadow pilot > slideware). Withdrawn iterations (§2.5) are scored on
the memo alone: ladder rigor (1–5) + honesty of withdrawal (1–5) = /10,
marked WITHDRAWN; a documented withdrawal outranks a built-but-dishonest
one but cannot win. Structural leakage = cannot win (Phase 1 policy);
incidental leakage = penalized but survivable.

## 2. Verification-gate outcomes

### p2_01-first note
p2_01 was verified FIRST, before any head-to-head was trusted. `bash run.sh`
exit 0 (true exit code, not a piped tail); seed 42; stratified 80/20
(1,600/400, 47 test churners); leakage audit ALL CHECKS PASSED (15 asserts
including the part-1 drops `p_churn_latent`/`clv_12m`/IDs); isotonic
calibration fit on train only; test touched once. Canonical reference
numbers (`part2_01/metrics.json`): AUC 0.8040, PR-AUC 0.3483, Brier
0.1065 → 0.0905; worklist K=40: **10** churners (precision 0.25, recall
0.2128), $19,456,099.49 expected / **$18,562,000** actual; uncalibrated
baseline: 16 churners / $9,847,000 actual. The flagship "fewer churners,
more dollars" trade-off DOES reproduce on this table's test frame (10 vs 16
churners; $18.56M vs $9.85M) — the dry-run non-reproduction was a
different-table artifact. `artifacts/worklist_topK.csv` reconciles exactly
(10 churners, $19,456,099.49, $18,562,000). The reference is sound.

**G6 finding (systematic):** only p2_02 reuses the canonical reference
numbers (via `reference_test_predictions.csv`). Every other iteration
reimplemented p2_01 with its own feature set, producing FOUR divergent
"p2_01_reference" baselines: Builder B (04/05/06): 13 / $15.19M / $7.36M;
Builder C (07/08/09): 9 / $20.64M / $17.48M; Builder D (10/12): 9 /
$19.94M / $17.48M; ref_model (13/14/15): 11 / $19.47M / $20.27M. None
matches the canonical 10 / $19.46M / $18.56M. Cross-iteration
business-metric comparisons are therefore NOT canonical-anchored; each
head-to-head is internally consistent only. Protocol-fidelity scores
reflect this.

### Per-iteration gate table

| # | G1 run.sh exit 0 | G2 schema | G3 arithmetic | G4 leakage | G5 traceability | G6 ref consistency | G7 test discipline | G8 frame |
|---|---|---|---|---|---|---|---|---|
| 01 | PASS (true exit 0) | PASS all keys | PASS (10≤47; prec/rec exact) | PASS (15 asserts) | PASS (worklist artifact reconciles) | canonical | PASS (thresholds n/a; isotonic train-only) | PASS (trade-off disclosed on test frame) |
| 02 | PASS (true exit 0) | PASS | PASS (9≤47) | PASS | PARTIAL (memo placeholders unfilled; metrics.json notes carry the numbers) | **CLEAN** (canonical numbers reused) | PASS (midpoint sensitivity; no test tuning) | PASS |
| 03 | **FAIL** (exit 1; `np.trapezoid` — numpy 1.26.4 has no such attr; crash after full T-learner fit) | FAIL (no metrics.json) | n/a | PASS (audit ran; treatment acceptable-family) | FAIL (memo all placeholders) | n/a (reads canonical ref CSV — design-clean) | PASS (treatment defined on train) | n/a |
| 04 | PASS (true exit 0) | PASS keys; **DEFECT**: `worklist.expected_arr_at_risk` = $49,086,832,812,601.56 — pipeline passed the ranking score (p×CLV) as `p`, computing dollars²; wrong in kind | PASS on actuals (6≤47); expected column unusable | PASS | PARTIAL (judge-written memo flags the $49T; CLV-currency cols correct) | DRIFT (Builder-B baseline 13/$15.19M/$7.36M) | PASS | PASS |
| 05 | PASS (true exit 0) | PASS | PASS (14≤47) | PASS | PARTIAL (judge-written memo) | DRIFT (Builder-B baseline) | PASS (a-priori cutoffs, no tuning) | PASS |
| 06 | PASS (true exit 0) | PASS keys; **DEFECT**: `expected_arr_at_risk` = $13,571,438,090,525.69 (dollars² bug, same class as p2_04) | PASS on actuals (2≤47) | PASS | PARTIAL (judge-written memo flags $13.57T) | DRIFT (Builder-B baseline) | **DEFECT**: `posterior()` conditions on test deaths (`d_te` = test label); numerically neutered by degenerate (a,b) (AUC 0.5) but structurally wrong | PASS (collapse reported, not disguised) |
| 07 | PASS (true exit 0) | PASS | PASS (11≤47) | PASS (33 features clean) | PASS (memo numbers match metrics.json) | DRIFT (Builder-C baseline 9/$20.64M/$17.48M) — claim re-checked vs canonical: still wins (11 vs 10; $19.65M vs $18.56M) | PASS (thresholds train-only, volume-bounded) | PASS |
| 08 | PASS (true exit 0) | PASS | PASS (9≤47) | PASS (33 features clean) | PARTIAL (judge-written memo) | DRIFT (Builder-C baseline) | PASS (all estimation on train) | PASS (null result reported) |
| 09 | PASS (true exit 0) | PASS | PASS (6≤47; n_flagged=40 vs 41 selected — disclosed) | PASS (33 features clean) | PARTIAL (judge-written memo) | DRIFT (Builder-C baseline) | PASS | PASS |
| 10 | PASS (true exit 0) | PASS | PASS (10≤47) | PASS (holdings grain verified) | PASS (memo numbers match artifacts) | DRIFT (Builder-D baseline 9/$19.94M/$17.48M) | PASS (account-level holdout) | PASS |
| 11 | **FAIL** (KeyError `'model'` at `build.py:284` — `fit_reference` returns no fitted estimator; crash after ~22 min, no metrics.json) | FAIL (no metrics.json) | n/a | PASS (asserts in code; audit exists) | FAIL (no numbers to trace) | n/a | n/a (unverifiable) | n/a |
| 12 | **FAIL** (`AttributeError: 'xstd_'` at `build.py:255` in prior-sensitivity; shipped code cannot complete; on-disk metrics.json is STALE vs shipped code) | FAIL (no regenerable metrics.json) | n/a on fresh; stale JSON arithmetically consistent | PASS (asserts in code) | **FAIL**: stale `metrics.json` claims "posterior means are calibrated by construction" while reporting Brier 0.0955 → 0.2335 (worse); median CI width 1.0 in `posterior_summaries.json` | DRIFT (Builder-D baseline, stale) | PASS (train-only fit) | n/a |
| 13 | PASS (true exit 0) | PASS | PASS (9≤47) | PASS | PASS (memo numbers match metrics.json) | DRIFT (ref_model baseline 11/$19.47M/$20.27M) | PASS (design params, not tuned) | PASS (boost-hurts disclosed) |
| 14 | PASS (true exit 0) | PASS | PASS (8≤47) | PASS (train-subgraph embeddings) | PARTIAL (memo has [TO FILL] placeholders; `ablation.json`/`nn_sanity.json` carry the numbers) | DRIFT (ref_model baseline) | PASS | PASS (null result reported) |
| 15 | PASS (true exit 0) | PASS | PASS (9≤47) | PASS | PASS (memo numbers match metrics.json) | DRIFT (ref_model baseline) | PASS (no self-grading; assumptions labeled) | PASS |

**G1 adjudications:** p2_03, p2_11, p2_12 are marked **INCOMPLETE** (broken
builds, not documented withdrawals — the withdrawal contract §2.5 was not
invoked by any builder). One-line fixes are noted in each reconstructed
memo as adjudicated defects, not applied — the judge does not build.
p2_12's on-disk metrics.json is scored as the builder's earlier-run claim,
labeled stale.

**G7 notes:** no SMOTE anywhere (no re-calibration issues); all thresholds
and operating points chosen on train; p2_06's posterior construction is the
sole test-discipline defect (G7/G8 table above).

## 3. Per-iteration scores

| # | Angle | Rigor | Protocol | Honesty | Distinct | Business | Repro | **Total /30** |
|---|---|---|---|---|---|---|---|
| 01 | Calibrated GBM reference | 5 | 5 | 4 | 5 | 4 | 4 | **27** |
| 02 | Survival | 4 | 4 | 5 | 4 | 4 | 3 | **24** |
| 03 | Uplift | 3 | 1 | 3 | 3 | 3 | 1 | **14** — INCOMPLETE |
| 04 | Multi-task churn+CLV | 4 | 3 | 3 | 4 | 3 | 4 | **21** |
| 05 | Hierarchical segments | 4 | 4 | 5 | 3 | 4 | 4 | **24** |
| 06 | Probabilistic CLV/BTYD | 2 | 2 | 4 | 3 | 2 | 4 | **17** |
| 07 | Change-point triggers | 5 | 4 | 5 | 5 | 5 | 5 | **29** |
| 08 | Causal framing | 4 | 4 | 5 | 5 | 3 | 4 | **25** |
| 09 | Portfolio optimization | 4 | 4 | 4 | 4 | 4 | 5 | **25** |
| 10 | Cross-sell CF | 4 | 4 | 5 | 4 | 4 | 5 | **26** |
| 11 | Interpretable EBM/GAM | 3 | 1 | 3 | 3 | 3 | 1 | **14** — INCOMPLETE |
| 12 | Bayesian hierarchical | 2 | 1 | 3 | 2 | 2 | 1 | **11** — INCOMPLETE |
| 13 | Event-triggered ops | 4 | 4 | 5 | 4 | 5 | 5 | **26** |
| 14 | Graph embeddings | 4 | 4 | 5 | 4 | 3 | 4 | **24** |
| 15 | Prescriptive counterfactuals | 4 | 4 | 5 | 4 | 4 | 5 | **26** |

### p2_01 — Calibrated GBM reference

The decision: with fixed outreach capacity, which accounts should CSMs
engage to maximize retained ARR. Currency: calibrated P(churn) × ARR.

**Thesis test:** clean, honest baseline — logistic challenger
(standardized) vs HGBT, isotonic calibration, EV-ranked worklist,
head-to-head vs the uncalibrated baseline with BOTH churner count and
dollars disclosed. **Passes.** CV PR-AUC: HGBT 0.4598 ± 0.0599 vs logistic
0.4198 ± 0.0496 (champion: HGBT). Brier 0.1065 → 0.0905. The measured
trade-off on the test frame: EV-ranked 10 churners / $18.56M vs uncalibrated
16 / $9.85M — disclosed, not buried.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 5 | Train-only everything; isotonic on train; leakage audit 15/15 PASS; the 8.33 survey fill recoded to NaN. |
| 2 | Protocol | 5 | Full schema; canonical reference; sensitivity 5%/15%; h2h discloses the trade-off. |
| 3 | Honesty | 4 | Memo Evaluation section ships with `{placeholders}` never filled — the numbers live in metrics.json/artifacts, but the memo does not state them. Incompleteness, not misrepresentation. |
| 4 | Distinctness | 5 | It IS the reference; minimal complexity, fully earned. |
| 5 | Business | 4 | Decision + currency + illustrative K named; no owner/trigger/play wiring (that is p2_13's job). |
| 6 | Repro | 4 | True exit 0; env note; memo placeholders cost a point. |

- Strongest: #2 — the protocol is the tournament's anchor and it is clean.
- Weakest: #3/#6 — the unfilled memo placeholders.
- Red-team: clean (no phantom numbers — placeholders are visibly empty, not fake).
- Verdict note: the bar everything is judged against; sound enough to trust.

### p2_02 — Survival: When, Not Just Who

The decision: CSM weekly sequencing — which at-risk accounts need contact
*now* vs next month. Currency: model-based P(churn in next 90d | survived
to tenure).

**Thesis test:** time-to-churn reframing adds deployment value over binary
classification. **Honestly falsified on discrimination; partially delivered
on sequencing.** Cox 90-day-risk AUC 0.5829 vs binary logistic 0.8267 on
IDENTICAL features (`metrics.json` notes); test C-index 0.8738. The time
axis is explicit (origin = contract start; churners' event = tenure − 45d
midpoint with ±35d sensitivity; non-churners censored at tenure) — not the
forbidden bare (T=tenure, E=churned). Renewal-calendar sequencing
(90/60/30-day buckets, `renewal_calendar_sequencing.csv`) is the surviving
deliverable.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | Explicit axis + sensitivity; PH assumed not per-covariate tested; midpoint is a stated assumption. |
| 2 | Protocol | 4 | Full schema; the ONLY iteration besides p2_01 with G6-clean canonical numbers. |
| 3 | Honesty | 5 | The falsification (0.5829 vs 0.8267) is in the metrics notes, not buried. |
| 4 | Distinctness | 4 | Thesis tested and honestly halved: sequencing survives, discrimination does not. |
| 5 | Business | 4 | Sequencing buckets are a real CSM deliverable; the risk ranking itself is weaker than binary. |
| 6 | Repro | 3 | True exit 0; memo ships with unfilled `{placeholders}`. |

- Strongest: #3 — the honest falsification.
- Weakest: #6 — placeholder memo.
- Red-team: clean (no fictional time axis; midpoint is stated, sensitivity-run).
- Verdict note: the sequencing layer is worth keeping; the survival *model* is not.

### p2_03 — Uplift: Persuadables, Not Just the Risky — INCOMPLETE

The decision: under the same capacity, who gets the high-touch save motion
— and who deliberately gets nothing. Currency: uplift τ(x).

**Thesis test:** UNRUNNABLE — G1 FAIL. The design is sound (T-learner,
treatment 1[qbr≥2] passes the availability gate, confounders named, balance
artifacts exist, Qini on test, no-intervention policy), but `np.trapezoid`
(numpy 2.x API on numpy 1.26.4) crashes the pipeline after the full
T-learner fit. No metrics.json; memo is all `{placeholders}`.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 3 | Design discipline visible in code + treatment/balance artifacts; unverified end-to-end. |
| 2 | Protocol | 1 | No metrics.json. |
| 3 | Honesty | 3 | Assumptions labeled in code; no claims made (nothing to misrepresent). |
| 4 | Distinctness | 3 | Angle distinct; thesis untested. |
| 5 | Business | 3 | No-intervention policy artifact exists; no verified worklist. |
| 6 | Repro | 1 | G1 FAIL (exit 1, deterministic). |

- Strongest: #1 — the design is the right design.
- Weakest: #6 — the build does not complete.
- Red-team: n/a (no numbers to red-team).
- Verdict note: a good angle killed by an untested run.sh; one-line fix
  (`np.trapz`) away from being judgable. Phase 3 may revive it.

### p2_04 — Multi-Task Churn + CLV

The decision: rank the save list by expected value lost (p_churn × CLV).
Currency: p × predicted CLV, reported in ARR and CLV currencies.

**Thesis test:** shared representation helps both heads. **Split verdict.**
Churn head: shared AUC 0.8270 vs single 0.8044 (+0.023), PR-AUC 0.3581 vs
0.3588 (−0.001, noise) — no clear win. CLV head: shared R² 0.954 vs single
0.881 vs **ARR-only ablation 0.445** — clears the mandatory ablation, but on
this table CLV is truth-derived (arr·(1−p_churn)), so part of the win is the
shared churn label recovering the DGP's truth (stated). The combined p×CLV
ranking: 6 churners / **$15.53M** actual vs the builder's p2_01 baseline 13 /
$7.36M — fewer churners, 2.1× the dollars.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | Full three-rung ladder; OOF-isotonic calibration; leakage audit PASS. |
| 2 | Protocol | 3 | Schema complete, but `expected_arr_at_risk` = $49.09T (dollars² bug — wrong in kind); G6 drift. |
| 3 | Honesty | 3 | The $49T column is a real pipeline output but semantically wrong; CLV-currency cols are correct and the defect is flagged — defect, not deception. |
| 4 | Distinctness | 4 | Ladder run honestly; churn-head null reported; CLV-head win qualified by the truth-derived caveat. |
| 5 | Business | 3 | Value-based ranking is the right currency; the $49T bug undermines the dollar story. |
| 6 | Repro | 4 | True exit 0; env note; judge-reconstructed memo (shipped without one). |

- Strongest: #4 — the ladder is the brief's prescribed test, fully run.
- Weakest: #2/#3 — the $49T expectation bug.
- Red-team: flagged — the $49T column must never be cited; `actuals` and CLV-currency cols are sound.
- Verdict note: the CLV head earns the sharing; the churn head does not; the dollar column needs recomputation before any VP sees it.

### p2_05 — Hierarchical Per-Segment Models

The decision: do lifecycle segments get their own models — and their own
plays? Currency: pooled per-segment p × ARR.

**Thesis test:** separate per-segment fits beat (a) global p2_01 and (b)
global+interactions. **Fails (b).** Per-segment: 14 churners / $8.01M actual;
global p2_01: 13 / $7.36M; global+interaction: **14 / $7.97M** with AUC
0.8099 / PR-AUC 0.3516 vs pooled 0.7438 / 0.3247. The interaction model gets
the segment signal without the fragmentation cost. What survives: 3
broad-portfolio segments shrink to global by the stated rule, and the
9-segment → 9-distinct-playbook operating map.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | A-priori cutoffs (no tuning); stated fallback; both comparison arms; per-segment metrics. |
| 2 | Protocol | 4 | Full schema; arithmetic sound; G6 drift only. |
| 3 | Honesty | 5 | The (b)-arm falsification is reported, not buried — the pipeline prints all three worklists. |
| 4 | Distinctness | 3 | Modeling thesis fails; the segmentation survives as an operating construct, not a modeling win. |
| 5 | Business | 4 | Nine distinct playbooks, each wired to a segment; capacity-aware. |
| 6 | Repro | 4 | True exit 0; env note; judge-reconstructed memo. |

- Strongest: #3 — ran the arm that kills its own headline.
- Weakest: #4 — the fits do not earn their complexity over global+interactions.
- Red-team: clean (fallback rule applied, not waived for thin segments).
- Verdict note: keep the playbook map; drop the per-segment fitting.

### p2_06 — Probabilistic CLV (Beta-Geometric) — falsified, reported

The decision: price expected lifetime value with BTYD-style machinery.
Currency: q × ELV ("expected lost lifetime value").

**Thesis test:** the probabilistic machinery earns its complexity vs naive
revenue sorts. **Comprehensively falsified.** Beta-Binomial MLE degenerated
(a = 9.07M, b = 271K, implied per-period churn 0.971); AUC 0.5000, PR-AUC
0.1175 (= base rate); Spearman(prob-alive, tenure) = 0.967, Spearman(ELV,
ARR) = 0.999998 — a tenure sort in BTYD clothes. Worklist 2 churners /
$11.50M actual, identical to the naive ARR sort. The falsification battery
is in `metrics.json`, reported as the result.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 2 | Degenerate MLE; `posterior()` conditions on test deaths (structurally wrong, numerically neutered); falsification checks run. |
| 2 | Protocol | 2 | Schema complete, but `expected_arr_at_risk` = $13.57T (dollars² bug); G6 drift. |
| 3 | Honesty | 4 | The collapse is fully instrumented and reported — exemplary falsification reporting; no inflated claim (AUC 0.5). |
| 4 | Distinctness | 3 | Honest nothing outscores decorative win; the machinery is disproven, cleanly. |
| 5 | Business | 2 | The ranking is an ARR-sort clone; value is the "don't buy this" verdict. |
| 6 | Repro | 4 | True exit 0; env note; judge-reconstructed memo. |

- Strongest: #3 — the falsification is the deliverable and it is thorough.
- Weakest: #1 — degenerate fit + test-label conditioning.
- Red-team: flagged — test-label conditioning in `posterior()` (no benefit taken; still wrong); $13.57T column must never be cited.
- Verdict note: the brief's warned collapse, measured. Do not re-litigate without longitudinal renewal histories.

### p2_07 — Change-Point / Velocity Triggers — WINNER (29/30)

The decision: which accounts get human attention *this week*, before the
renewal conversation. Currency: expected ARR at risk, but the worklist is
**trigger-routed** — only accounts firing ≥1 trigger are eligible.

**Thesis test:** deployable early-warning rules beat or usefully complement
score-routed outreach. **Passes.** Eight triggers, each a stated rule +
threshold + owner + SLA (`trigger_catalog.csv`); thresholds chosen on train
only by precision-maximizing grid with alert-volume bounds (3%–40%); rule
triggers stated not tuned. Snapshot limitation handled honestly (trajectory
proxies named; longitudinal data contract specified in `shadow_pilot.md`;
lead time proxied by days-to-renewal at firing — stated proxy). Trigger-routed
K=40: **11** churners (precision 0.275, recall 0.234), $19.20M expected /
**$19.65M** actual vs p2_01 reference 9 / $20.64M / **$17.48M** — wins on both
counts on this frame, and still wins against the canonical reference (11 vs
10; $19.65M vs $18.56M). **Falsifications reported:** T2 (active-user-ratio
cliff: train 28.4% → test 6.3% precision — threshold overfit, flagged for
retirement) and T5 (P1 pain: fires on 48% of the book at ~base-rate
precision — too broad, flagged for rebuild).

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 5 | Train-only thresholds with volume bounds; honest snapshot limits; T2/T5 retired in-catalog. |
| 2 | Protocol | 4 | Full schema; arithmetic sound; G6 drift, but the claim survives canonical re-check. |
| 3 | Honesty | 5 | Failed triggers shipped as failures; the screened-out $1.04M churner disclosed; union-fires-66.5% caveat stated. |
| 4 | Distinctness | 5 | The trigger catalog is a distinct deliverable; the gate+EV-rank design is the brief's thesis, demonstrated. |
| 5 | Business | 5 | Every trigger has an owner and SLA; speaks CSM (outreach windows, renewal runway); capacity-aware. |
| 6 | Repro | 5 | True exit 0 (sweep-confirmed); env note; memo complete with real numbers. |

- Strongest: #5 — the catalog is operable as-shipped.
- Weakest: #2 — the non-canonical baseline (claim re-verified against canonical).
- Red-team: clean.
- Verdict note: the only iteration that beats the reference on both counts AND ships the operating layer to act on it. See §5–6.

### p2_08 — Causal Framing: the gatekeeper

The decision: is there credible evidence any existing motion moves churn —
before anyone spends dollars on an assumed effect? Currency: the ATE itself,
with fragility analysis.

**Thesis test:** at least one motion has credible evidence — or none does,
stated. **None does, stated.** ATE (IPW) −0.0089, 95% CI [−0.0271, 0.0075]
(spans zero); AIPW −0.0311; PSM 0 matched pairs (failed arm, reported);
E-value 1.95 (fragile); robustness cuts flip sign (+0.0825 / −0.0505).
`gatekeeper_caveats.txt` is the machine-readable contract p2_09 attaches.
The "causal-augmented" churn model is identical to the reference on every
column — the treatment flag coarsens an existing feature (reported no-op).

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | IPW/AIPW/PSM + bootstrap SE + E-value + balance, all on train; propensity includes the treatment-defining covariate (degenerate scores — killed PSM). |
| 2 | Protocol | 4 | Full schema; arithmetic sound; G6 drift only. |
| 3 | Honesty | 5 | The null IS the headline; caveats are an artifact, not prose; PSM failure reported. |
| 4 | Distinctness | 5 | The gatekeeper role is unique and executed per spec — p2_09's anchor exists because of it. |
| 5 | Business | 3 | Evidence-for-others by design (brief §6); the decision it serves (believe no effect yet) is real but not a worklist. |
| 6 | Repro | 4 | True exit 0; env note; judge-reconstructed memo. |

- Strongest: #4 — the gatekeeper contract is the tournament's load-bearing honesty mechanism.
- Weakest: #5 — not a decision tool per se.
- Red-team: noted — propensity design flaw (treatment-defining covariate in the design matrix); the 2.594 SMD is the tautological treatment variable, not a balance failure.
- Verdict note: the "no credible motion" verdict stands; Phase 3 must not invent treatment effects.

### p2_09 — Portfolio Optimization

The decision: under a fixed outreach-hour budget, which accounts get which
play to maximize expected retained dollars. Currency: p × ARR × close_rate
× treatment_effect, optimized by exact 0/1 knapsack vs greedy.

**Thesis test:** constrained selection beats plain EV-ranking at fixed
capacity. **Partially demonstrated.** Exact knapsack ≈ greedy ($46,219.90 vs
$46,210.39 — greedy is near-optimal, a finding). Base plan: 41 accounts,
200h, $46.2K expected retained; playbook mix 13/4/24. Treatment effects
anchored on p2_08's |ATE| WITH caveats attached (`plan.json`); close rate
0.30 and cross-sell 0.04 labeled assumptions; regret table all zeros
(structural — uniform scaling, not robustness evidence, stated). **Which
half drives the plan: cross-sell** ($5.02M vs retention $24.9K; 0.46 overlap
with retention-only). Own worklist: 6 churners / $15.04M actual vs p2_01
reference 9 / $17.48M — the optimizer spends hours on cross-sell-shaped
value the churn metric does not reward (disclosed).

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | Exact-vs-greedy, regret, budget/close-rate sensitivity, eligibility rule, p2_08-anchored effects. |
| 2 | Protocol | 4 | Full schema; arithmetic sound; G6 drift only. |
| 3 | Honesty | 4 | Assumptions labeled; scenarios not forecasts; cross-sell dominance stated; zero-regret explained. |
| 4 | Distinctness | 4 | Constrained optimization is distinct from EV ranking; findings are genuine (greedy tie, cross-sell drive). |
| 5 | Business | 4 | Hour budget + playbooks + eligibility = an operable plan; loses to EV ranking on churn capture (disclosed). |
| 6 | Repro | 5 | True exit 0 (sweep-confirmed); env note; judge-reconstructed memo complete. |

- Strongest: #6 — clean build, complete artifacts (`plan.json`, `regret_table.csv`).
- Weakest: #3 — the 200-hour budget is illustrative (sensitivity-banded, acceptable, but still the softest input).
- Red-team: clean (gatekeeper rule honored in code).
- Verdict note: the right optimizer with the wrong (assumed) fuel — useful once p2_08's pilot produces a measured effect.

### p2_10 — Cross-Sell CF vs Association Rules

The decision: which next-best products should CSMs pitch — and is latent CF
worth it over auditable rules at a 9-SKU catalog? Currency: p_churn × (ARR +
white-space ARR at 20%-close).

**Thesis test:** latent machinery beats auditable association rules.
**Half-passes, honestly.** Account-level holdout, leave-one-item-out
(n=246): item-CF recall@3 **0.752** beats rules **0.455**, but **loses to the
naive popularity baseline (0.760)**; SVD-MF (0.407) loses to rules. "At 9
SKUs the collaborative signal is mostly popularity; the machinery's edge
over rules is real but its edge over a sorted bar chart is nil."
White-space $952.3M gross labeled 100%-close (scenario, not forecast);
10/20/30% scenarios are labeled assumptions. Holdings from the winner's
verified file (5,445 rows, account × product grain asserted in code) —
never `data/product_holdings.csv`. Cross-sell-aware worklist: 10 churners /
$17.90M actual vs p2_01 reference 9 / $17.48M — directionally favorable,
K-dependent, disclosed as such.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | Verified holdings; account-level holdout; rules-vs-CF-vs-popularity; leakage audit. |
| 2 | Protocol | 4 | Full schema; arithmetic sound; G6 drift only. |
| 3 | Honesty | 5 | The popularity-baseline falsification is exemplary; white-space labeled scenario. |
| 4 | Distinctness | 4 | Thesis tested with the right comparator set; the null-vs-popularity is the finding. |
| 5 | Business | 4 | `recommendations_top3.csv` is shippable; white-space sized with scenarios. |
| 6 | Repro | 5 | True exit 0 (sweep-confirmed); env note; memo complete with artifact-matching numbers. |

- Strongest: #3 — the popularity baseline is the check most builders skip.
- Weakest: #1 — 9-SKU catalog limits transfer (stated).
- Red-team: clean (holdings verified; no revenue forecast without a labeled close rate).
- Verdict note: the CF-vs-rules question is answered; the answer is "rules lose to CF, CF ties popularity."

### p2_11 — Interpretable-Only (EBM→GAM) — INCOMPLETE

The decision: does a glass-box model change a DECISION vs GBM+attributions?
Currency: GAM p × ARR with exact additive attributions.

**Thesis test:** UNRUNNABLE — G1 FAIL. The design is the brief's checklist
made executable (honest GAM substitution for uninstallable EBM; occlusion —
labeled, not SHAP — for GBM attributions; C by train-CV PR-AUC;
monotonicity-constraint audit with cost; decision-difference analysis:
top-K flips, train-chosen Youden thresholds, playbook flips; flagship
allocation-arbitrariness audit; CSM reason cards with a stated trust
metric). `KeyError: 'model'` at `build.py:284` — `fit_reference` returns no
fitted estimator — crashes after ~22 min with no metrics.json.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 3 | Design is rigorous; unverified end-to-end. |
| 2 | Protocol | 1 | No metrics.json. |
| 3 | Honesty | 3 | Substitutions stated; no claims made. |
| 4 | Distinctness | 3 | Angle distinct; thesis untested. |
| 5 | Business | 3 | Reason cards + trust metric are good designs, undelivered. |
| 6 | Repro | 1 | G1 FAIL (deterministic). |

- Strongest: #1 — the analysis plan is exactly right.
- Weakest: #6 — the build does not complete.
- Red-team: n/a.
- Verdict note: the best-designed iteration that never ran; one-line fix
  (return the fitted model from `fit_reference`) away from judgable. Phase 3
  may revive it for reason cards.

### p2_12 — Bayesian Hierarchical — INCOMPLETE (machinery degenerate)

The decision: does posterior uncertainty change the worklist? Currency:
posterior-mean p × ARR, with an uncertainty-aware routing rule.

**Thesis test:** UNJUDGABLE — G1 FAIL on the shipped code
(`AttributeError: 'xstd_'` in the prior-sensitivity block); the on-disk
metrics.json is STALE (builder's earlier run). The stale numbers show
degenerate machinery: AUC 0.6364, PR-AUC 0.1803, Brier 0.0955 → **0.2335**
(worse after "calibration by construction"), median 90% CI width **1.0**
(vacuous intervals), 0.0 share of CIs above base rate. The Laplace
approximation collapsed (rank-deficient GLM warnings in the log).

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 2 | Sound design; numerically broken execution; shipped code crashes. |
| 2 | Protocol | 1 | No regenerable metrics.json. |
| 3 | Honesty | 3 | The degeneracy is in the artifacts (width 1.0 reported), not hidden — but "calibrated by construction" is contradicted by its own Brier. |
| 4 | Distinctness | 2 | Uncertainty routing undelivered; intervals vacuous. |
| 5 | Business | 2 | No usable uncertainty worklist. |
| 6 | Repro | 1 | G1 FAIL (deterministic). |

- Strongest: #3 — the PPC caught the failure (the check worked).
- Weakest: #6 — the build does not complete.
- Red-team: flagged — stale metrics vs shipped code; "calibrated by construction" claim vs Brier 0.2335.
- Verdict note: the machinery needs a rebuild (regularized covariance, non-degenerate prior), not a rerun.

### p2_13 — Event-Triggered Operational Scoring

The decision: how does a churn *score* become churn *prevention* in
production? Currency: EV × (1 + 0.10 × n_triggers) — risk dollars first,
trigger urgency second (the 0.10 is a stated design parameter, not tuned).

**Thesis test:** production-ready scoring system around the p2_01 model —
**exempt from the PR-AUC bar per spec §1.4.2, judged on
production-readiness. Passes.** `ops_runbook.md`: weekly + event-triggered
+ ad-hoc cadence; six triggers with rule/owner/SLA; freshness SLAs
(telemetry ≤7d, support ≤1d, ARR ≤30d, survey ≤90d); label-maturity gate;
treated-flag logging (anti-contamination); drift runbook (input PSI, score
drift, decay gates); "what breaks first" answered (telemetry freshness).
Involuntary churn: no reason codes → labeled proxy (churned ∧
downgraded_12m: 33/237, 13.9%), routed to win-back — an assumption, never
measured. **The trigger boost HURTS on this frame** (9 vs 11 churners,
$18.68M vs $20.27M actual) — reported, not buried. Trigger diagnostics:
renewal_imminent sharpest (19.6% churn when flagged vs 11.75% base);
escalation_burst too broad (87.3% fire rate); 100% of test churners fired ≥1
trigger (zero blind spots).

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | Scorer reused verbatim (stated); design params not tuned; contamination handling specified. |
| 2 | Protocol | 4 | Full schema; PR-AUC-exempt per spec; G6 drift only. |
| 3 | Honesty | 5 | The boost-hurts finding is the headline honesty moment; proxy labeled. |
| 4 | Distinctness | 4 | Infrastructure-around-a-scorer, judged as such; the runbook is a distinct deliverable. |
| 5 | Business | 5 | The most production-complete: cadence, SLAs, owners, drift, shadow-pilot gating (precision ≥2× base). |
| 6 | Repro | 5 | True exit 0 (sweep-confirmed); env note; memo complete. |

- Strongest: #5 — nothing else ships an operating system.
- Weakest: #1 — the boost parameter and thresholds are design choices (stated, not tuned).
- Red-team: clean.
- Verdict note: the production wrapper the winner needs; stands alone as infrastructure per brief §6.

### p2_14 — Graph / Hierarchy Embeddings — falsified, reported

The decision: does account-product graph structure carry churn signal beyond
tabular features? Currency: (tabular+embeddings) p × ARR.

**Thesis test:** embeddings add signal over tabular alone — **falsified by
the mandatory ablation.** Tabular-only: AUC 0.8132 / PR-AUC 0.3695;
tabular+16 embedding dims: AUC 0.7884 / PR-AUC 0.3700 (delta −0.0248 /
+0.0005): "no material gain from embeddings." Machinery proportional
(numpy random-walk + PPMI-SVD, no GNN on 2,000 rows); embeddings fit on the
TRAIN subgraph only; test accounts get compositional neighbor-mean vectors
(no transductive leakage). Holdings verified (5,445 rows, grain asserted).
NN sanity: neighbors match on industry/product (embeddings encode the
obvious structure) — structure that the tabular features already carry.
Worklist: 8 churners / $17.04M actual vs reference 11 / $20.27M.

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | Train-only embeddings; compositional test vectors; ablation on the same split/protocol. |
| 2 | Protocol | 4 | Full schema; arithmetic sound; G6 drift only. |
| 3 | Honesty | 5 | The null is the headline; machinery kept proportional; no deep-learning showcase. |
| 4 | Distinctness | 4 | Thesis tested with the exact prescribed ablation; clean falsification. |
| 5 | Business | 3 | The deliverable is a verdict ("don't build this"), not a tool. |
| 6 | Repro | 4 | True exit 0 (sweep-confirmed); env note; memo has [TO FILL] placeholders (ablation.json carries the numbers). |

- Strongest: #3 — clean, proportional, honest null.
- Weakest: #5 — no deployable output beyond the verdict.
- Red-team: clean (holdings verified; no transductive leakage).
- Verdict note: the bipartite premise is untestable-to-useless at 9 SKUs; do not re-litigate.

### p2_15 — Prescriptive Counterfactual Simulator

The decision: given a risk-ranked account, *what should the CSM actually
do* — and is it worth the cost? Currency: expected net retained value =
p × effect × ARR − cost, over feasible actions.

**Thesis test:** feasible per-account plays with honest coverage and costs.
**Passes as a scenario system.** Four actions with assumed costs/effects and
feasibility gates (`action_catalog.json`); effects labeled assumptions
(p2_08 absent at build time — stated); sensitivity 0.5×/1×/2×; no
self-grading (no perturbation evaluation at all — the model's response to
perturbed features is never ground truth); gaming defenses stated.
Coverage (base case): 96.3% pass ≥1 gate; 64.8% get a recommended action;
**15 accounts (3.8%) get "no feasible playbook"** — honestly reported.
exec_qbr feasible for 72 accounts but never the argmax (dominated under the
assumed costs — a finding about the assumption set, stated). Net-ranked
worklist: 9 churners / $18.68M actual vs p2_01 EV 11 / $20.27M — prescription
trades 2 churners and ~$1.6M for cost-awareness (disclosed). Scenario
economics: weak $2.70M / base $6.34M / strong $13.95M — "the ranking of
actions is stable across scenarios; the dollar scale is not."

| # | Criterion | Score | Rationale |
|---|---|---|---|
| 1 | Rigor | 4 | Feasibility-first; argmax-net rule; sensitivity; gaming defenses; no self-grading by construction. |
| 2 | Protocol | 4 | Full schema; arithmetic sound; G6 drift only. |
| 3 | Honesty | 5 | Every dollar labeled scenario; "no feasible playbook" reported; dominated action disclosed. |
| 4 | Distinctness | 4 | Prescription is distinct from prediction; the cost-aware trade-off is demonstrated. |
| 5 | Business | 4 | Action catalog + coverage + gaming defenses = operable; effects are assumed (the binding constraint). |
| 6 | Repro | 5 | True exit 0 (sweep-confirmed); env note; memo complete. |

- Strongest: #3 — assumption pedigree on every dollar.
- Weakest: #1 — effects are assumed, not measured (p2_08's null sharpens this).
- Red-team: clean (no self-grading; close rates labeled).
- Verdict note: the right prescription architecture waiting on a measured effect — p2_08 says none exists yet.

## 4. Combination verdict — single winner + adopted elements (NO merged build)

Per §6, combinations were evaluated on merit. **No executable merged
iteration is built.** Reasons, per the brief's do-not-combine rules:

1. **p2_13 is infrastructure around a scorer, not a competitor** (brief §6,
   explicit). Merging p2_07's trigger catalog with p2_13's ops runbook would
   be prose stitching: the merged metrics.json would be byte-identical to
   p2_07's (same scorer, same ranking) — no new capability, no re-scorable
   difference. The correct relationship is adoption, not merging (below).
2. **p2_08 is evidence for other iterations, not a ranking** (brief §6,
   explicit). Its ATE already feeds p2_09's scenarios with caveats attached
   in code — the composition the brief envisions already exists as built
   artifacts, not as a new iteration.
3. **Falsifications stand alone** (brief §6). p2_02's (survival adds
   nothing), p2_06's (BTYD collapses to a tenure sort), p2_14's (embeddings
   add nothing) are negative results; folding them into a winner buries them.
4. **Withdrawn/incomplete iterations cannot be merged** (brief §6). p2_03,
   p2_11, p2_12 are incomplete — no merge involving them.
5. **No remaining pair clears the bar.** p2_07+p2_15 (triggers say
   who/when, actions say what) is the most tempting, but p2_15's effects are
   labeled assumptions and p2_08's null sharpens that binding constraint —
   the merge would package assumed effects as a system without adding a
   measurable capability. p2_05's playbooks + p2_07's triggers overlap
   without composing (both are routing layers; the union is a longer list,
   not a better one).

**Adopted elements (documented, not built):** the winner p2_07 adopts —
(a) p2_13's ops machinery as its production wrapper: intervention-
contamination logging (treated flags), drift runbook (input PSI, score
drift, decay gates), freshness SLAs, and the shadow-pilot gating rule
(go-live at trigger precision ≥ 2× base rate); (b) p2_08's gatekeeper
caveats as the standing policy: no treatment-effect number enters any
Phase 3 money math without the caveats attached; (c) p2_05's 9-segment →
9-playbook map as the playbook library behind p2_07's trigger→owner→SLA
routing; (d) p2_10's cross-sell white-space sizing as a SEPARATE motion
(its 20%-close tilt is not merged into the churn worklist — p2_10's own
head-to-head shows the tilt is K-dependent and marginal).

## 5. Winner declaration — p2_07, Behavioral Change-Point / Velocity Triggers (29/30)

**Why it wins, criterion by criterion where it matters:**

- **#5 Business usefulness (5/5):** the only iteration whose output a CSM can
  operate Monday morning — eight triggers, each with a stated rule, a
  threshold, an owner role, and an SLA, plus a shadow-pilot design for
  graduation. p2_01 finds who is risky; p2_07 says what changed, who owns
  the next step, and how fast.
- **#4 Angle distinctness (5/5):** the trigger gate + EV-rank-inside-gate is
  materially different from p2_01, and the head-to-head demonstrates the
  thesis: trigger-routed 11 churners / $19.65M actual vs score-routed 9 /
  $17.48M (Builder-C frame), and 11 vs 10 / $19.65M vs $18.56M against the
  canonical reference. The complexity is earned, not decorative.
- **#3 Honesty (5/5):** two triggers shipped as failures (T2's threshold
  overfit, T5's 48% fire rate), the screened-out $1.04M churner disclosed,
  the "gate is nearly the whole book without T5's retirement" caveat
  stated, lead time honestly proxied.
- **#1 Rigor (5/5):** train-only thresholds with alert-volume bounds,
  snapshot limitation handled as a data contract (not hand-waved), leakage
  audit clean.

**Known, accepted defects (what kept it from 30):**

- G6: its head-to-head uses Builder C's p2_01 reimplementation (9 / $20.64M
  / $17.48M), not the canonical reference — re-verified against canonical
  (11 vs 10; $19.65M vs $18.56M), the claim holds, but the memo's baseline
  column is not the canonical one.
- The trigger union fires on 66.5% of test accounts (T5 dominates) — without
  T5's retirement the "gate" barely gates; the catalog flags this, but a
  production cut must actually retire T5.
- Lead time is a renewal-runway proxy, not measured days-to-churn; trigger
  stability (week-to-week flapping) is unmeasurable on one snapshot —
  graduation gates 1–4 in `shadow_pilot.md` are the remedy, not this table.
- Involuntary churn unseparated (no reason codes; documented assumption).

**Why not the runners-up (one line each, grounded):**

- **p2_01 (27):** the reference is clean and sound, but it is the bar, not
  the innovation — p2_07 beats it on both head-to-head counts AND ships the
  operating layer it lacks.
- **p2_10 (26):** exemplary falsification (popularity beats CF), but the
  cross-sell motion is a separate decision from churn prevention, and the
  churn-side tilt is marginal and K-dependent.
- **p2_13 (26):** the best production wrapper, but its trigger boost LOSES
  on this frame (9 vs 11 churners) — it is infrastructure around a scorer,
  adopted as the winner's ops layer rather than winning itself.
- **p2_15 (26):** the right prescription architecture with assumed effects —
  p2_08's null verdict (no credible measured effect) is its binding
  constraint; scenarios, not a system to deploy.
- **p2_08 (25):** the tournament's load-bearing honesty mechanism, but
  evidence-for-others by design — its verdict (no credible motion) is
  adopted as policy, not as the winning model.
- **p2_09 (25):** the right optimizer with assumed fuel; loses to plain EV
  ranking on churn capture; useful once a measured effect exists.
- **p2_02 (24):** honest falsification (Cox 0.5829 vs logistic 0.8267) —
  the sequencing survives as a layer, the survival model does not.
- **p2_05 (24):** per-segment fits do not beat global+interactions (AUC
  0.7438 vs 0.8099) — keep the playbook map, drop the fitting.
- **p2_14 (24):** clean null (delta PR-AUC +0.0005) — a verdict, not a tool.
- **p2_04 (21):** CLV head earns the sharing (R² 0.954 vs ablation 0.445),
  but the $49T expectation bug and the churn head's null keep it out.
- **p2_06 (17):** comprehensively falsified (AUC 0.5; tenure sort in BTYD
  clothes) — the falsification is exemplary, the angle is dead.
- **p2_03 / p2_11 / p2_12 (14 / 14 / 11):** INCOMPLETE — broken builds, not
  judged withdrawals; each is a documented one-line fix away from being
  judgable (p2_03, p2_11) or needs a numerical rebuild (p2_12).

## 6. Phase 3 handoff note

- **Winner id:** `approaches/part2_07` — Behavioral Change-Point / Velocity
  Triggers.
- **Winning modeling approach:** p2_01-reference scorer (HistGradientBoosting
  classifier, class_weight="balanced", isotonic CalibratedClassifierCV cv=5,
  train-only; 33 features after the Builder-C forbidden drop) reused for
  probabilities; the innovation is the **trigger gate**: 8 stated triggers
  (rule + threshold + owner + SLA in `trigger_catalog.csv`), thresholds
  chosen on train only (precision-maximizing grid, alert-volume bounds
  3%–40%); worklist = fired accounts ranked by calibrated p × ARR, top K =
  10% of the eval set. Star trigger: T8 (renewal ≤ 90d + low behavioral
  health) — 43.5% test precision (10/23), median 50 days renewal runway.
  Retire/rebuild: T2 (threshold overfit), T5 (48% fire rate, base-rate
  precision).
- **Substrate table:** `approaches/part1_07/modeling_table.csv` (2,000 rows
  × 47 cols; iteration root, not `outputs/`). Label `churned` = hero-product
  (PRD-01 SentinelShield) cancellation/non-renewal within 90 days of scoring
  date **2026-10-01**; base rate **11.85%** (237/2,000); canonical 90-day
  full-account churn (spec §1.6 case 1). Dollar currency `total_arr_usd`.
  Drops before training: `p_churn_latent` (class 1), `clv_12m` (aux target
  only), `account_id`/`product_id` (class 8/6), survey distractors + trust
  machinery, ARR twins. Valid survey family only (`valid_nps_mean`,
  `has_valid_survey` companion; 64% coverage); `stated_vs_revealed_gap` is a
  documented null.
- **Canonical test frame:** stratified 80/20, seed 42 → test 400 rows, 47
  churners (11.75%); K = 40 (sensitivity 20/60). Canonical p2_01 reference:
  10 churners / $19.46M expected / **$18.56M** actual; uncalibrated baseline
  16 / $9.85M. Winner's numbers on this frame: **11** / $19.20M / **$19.65M**.
- **Defects carried forward:** (1) G6 — every iteration reimplemented p2_01
  with its own features; Phase 3 must import the CANONICAL reference
  (`part2_01/artifacts/reference_test_predictions.csv` + `metrics.json`),
  never reimplement it. (2) p2_07's trigger union fires on 66.5% of
  accounts — T5 must be retired/narrowed before the gate means anything.
  (3) Lead time is proxied, not measured — the shadow pilot
  (`shadow_pilot.md`) is the path to real numbers. (4) Involuntary churn
  unseparated; all churn treated as voluntary (documented assumption).
- **Adopted elements:** p2_13's ops runbook (contamination logging, drift
  monitors, freshness SLAs, shadow-pilot gating) as the production wrapper;
  p2_08's gatekeeper caveats as standing policy (no treatment-effect number
  without them); p2_05's 9-playbook map as the playbook library; p2_10's
  white-space as a separate motion.
- **Falsifications NOT to re-litigate:** survival adds nothing over binary
  logistic on identical features (p2_02: 0.5829 vs 0.8267); BTYD-style
  probabilistic CLV collapses to a tenure/ARR sort on snapshot data (p2_06);
  graph embeddings add nothing over tabular at 9 SKUs (p2_14: delta PR-AUC
  +0.0005); per-segment fits do not beat global+interactions (p2_05); CF
  ties the popularity baseline (p2_10); no measured motion moves churn —
  ATE CI spans zero (p2_08). Revivable with fixes: p2_03 (uplift;
  `np.trapz` one-liner), p2_11 (GAM reason cards; return the fitted model
  from `fit_reference`).
- **Numbers that must never be cited:** p2_04 `expected_arr_at_risk`
  $49,086,832,812,601.56 and p2_06 `expected_arr_at_risk`
  $13,571,438,090,525.69 (dollars² pipeline bugs); p2_12's stale
  metrics.json (shipped code crashes; "calibrated by construction" vs Brier
  0.2335).
