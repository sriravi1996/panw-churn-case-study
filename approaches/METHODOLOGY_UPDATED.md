# Methodology — PANW Churn Case Study (Exhaustive Tournament Rebuild)

**Date:** 2026-10-10 · **Author:** Tara (Ravi's agent) · **Status:** final tournament record

This document is the comprehensive methodology record for the Palo Alto
Networks Senior Data Scientist case study. The solution was built through
three tournaments — 15 iterations each — with a deep-analysis judging step
after each part that picked a winner, scored every iteration, and adopted
the best elements of strong iterations. Full per-iteration scorecards live
in `approaches/part1_TOURNAMENT.md`, `approaches/part2_TOURNAMENT.md`, and
`approaches/part3_TOURNAMENT.md`; this document summarizes the iterations,
the judging rationale, the winners, and how the three winners compose into
one system.

## The three winners

| Part | Winner | Angle | Score |
|---|---|---|---|
| 1 — Data engineering + EDA | `part1_07` | Survey-Augmented: Stated vs Revealed Health | 25/30 |
| 2 — Analysis + modeling | `part2_07` | Behavioral Change-Point / Velocity Triggers | 29/30 |
| 3 — Documentation | `part3_07` | Playbook: the CSM operator's manual | 35/35 |

The composed system: **a survey-augmented, trust-gated data foundation**
(Part 1) feeds **a calibrated churn scorer behind a behavioral trigger gate**
(Part 2), delivered as **an operator's manual a CSM can run Monday morning**
(Part 3). The deck (`presentation/CloudSecure_Churn_Deck.pptx`) tells that
story in 12 TLDR-headed slides; every number traces to a pipeline artifact.

## Phase 1 — Data engineering + EDA (15 iterations)

### The 15 iterations and their angles

| # | Angle | Score /30 | One-line verdict |
|---|---|---|---|
| 01 | Star-schema baseline | 17 | Auditable grain discipline, but theater-grade dirty data and a weak modeling base |
| 02 | Event-sourced log | 21 | Best dirty-data realism and honesty, but a structural leak (post-churn silence) |
| 03 | Wide feature-store panel | 20 | Superb reconciliation, but variable label maturity is a modeling trap |
| 04 | Normalized 3NF + fuzzy ER | 21 | Most enterprise-real multi-source design, but its headline finding is mechanically confounded |
| 05 | Account-hierarchy graph | 16 | Structural self-inclusion leakage — cannot win |
| 06 | SCD-2 as-of | 19 | Right as-of discipline, but the headline trend feature broke its own premise |
| **07** | **Survey-augmented** | **25** | **Winner** |
| 08 | Multi-currency FX | 21 | Load-bearing FX reconciliation, but numerical-integrity failures |
| 09 | PLG telemetry | 22 | Compelling funnel gradient, but tuned-on-truth validation |
| 10 | Support-centric | 24 | Richest input, runner-up — shipped the tournament's strongest answer-key leak |
| 11 | Contract/commercial | 19 | Right precedence idea, resolved with a different rule than the generator used |
| 12 | Marketing attribution | 22 | Two attribution models that agree, but fabricated funnel dates |
| 13 | Partner/channel | 23 | Most explicit conflict lineage, clean audit, but a narrow table |
| 14 | Security-incident | 26 | Clean, product-native, runner-up — loses only on breadth |
| 15 | Audit-first DQ | 24 | Most inspectable lineage, but a gentle DGP that never stress-tests |

### Why part1_07 won

1. **Richest sound modeling input post-drop.** 2,000 rows × 47 columns
   (45 feature/label columns after the audit-verified drops), with the
   fullest canonical-slot coverage: dynamics (`usage_decay_90d`,
   `behavioral_health`), contract (`days_to_renewal`,
   `expansion_revenue_pct`, `downgraded_12m`), a full support family,
   trust-gated survey (`valid_nps_mean` + `has_valid_survey` companion),
   engagement (webinars, content, sales calls, QBR), firmographics, hero
   aggregates. Label `churned` = hero-product (PRD-01 SentinelShield)
   cancellation/non-renewal within 90 days of scoring date 2026-10-01, at
   11.85% (237/2,000) — in band.
2. **Leakage incidental, not structural.** The shipped `p_churn_latent`
   (the DGP's answer key) and `clv_12m` (truth-derived, forward-looking)
   were dropped; the leakage audit verified column-by-column that
   everything else is pre-scoring clean, and the design and EDA story do
   not depend on them. The drop is mechanical and exact.
3. **Best dirty-data realism + cleaning rigor.** Four fraud signatures
   with a signature-keyed detector that deliberately spares honest
   satisficing; nonresponse bias treated as a *risk feature* (respondents
   9.9% vs non-respondents 15.3% churn); trust-gated aggregates with the
   distractor (`naive_nps`) kept visible for comparison.
4. **Headline EDA findings with numbers.** $1,975.1M total ARR;
   SentinelShield $1,161.6M (58.8%); PostureLens $166.1M cross-sell lead,
   then NetBarrier $128.1M, ThreatScope $126.8M; mean 2.72 products/account;
   top-10% accounts hold 29% of ARR; top account ACC-01909 at $8.14M.
5. **Honest where it counts.** Valid NPS correlates 0.09 with behavioral
   health and −0.06 with churn vs −0.22 for behavioral — the iteration
   reports its angle's weakness straight. Its own headline construct,
   `stated_vs_revealed_gap`, is a documented NULL (deciles don't separate
   churn: 10.2% vs 10.9% vs 11.85%) — carried forward as a fact, not a
   feature.

### Phase 1 → Phase 2 handoff

Substrate: `approaches/part1_07/modeling_table.csv` (iteration root).
Drops before any training: `p_churn_latent` (class 1 — label drawn as
Bernoulli(p)), `clv_12m` (truth-derived; auxiliary target only),
`account_id`/`product_id` (identifiers). Survey columns in two families —
use the **valid** family gated by `has_valid_survey`; `naive_*` is the
distractor; trust machinery (`n_all_responses`, `validity_rate`) is not a
feature. `days_to_renewal` is a knowable contract term. Missingness on
survey columns (~36%) is legitimate — keep `has_valid_survey`. Small
missingness on `champion_logins_30d` (2.7%), `webinars_watched` (3.5%),
`content_downloads` (3%): impute with train-only statistics.

## Phase 2 — Analysis + modeling (15 iterations)

### The 15 iterations and their angles

| # | Angle | Score /30 | One-line verdict |
|---|---|---|---|
| 01 | Calibrated GBM reference | 27 | The clean, honest bar — the innovation it isn't |
| 02 | Survival / time-to-churn | 24 | Honest falsification (Cox 0.5829 vs logistic 0.8267); sequencing survives as a layer |
| 03 | Uplift / persuadables | 14 — INCOMPLETE | Broken build (`np.trapezoid` crash), one-liner from judgable |
| 04 | Multi-task churn + CLV | 21 | Shared representation earned (R² 0.954 vs 0.445 ablation), but a dollars-squared bug |
| 05 | Hierarchical segments | 24 | Per-segment fits lost to global+interactions; keep the playbook map, drop the fitting |
| 06 | Probabilistic CLV / BTYD | 17 | Falsified — a tenure sort in BTYD clothes (AUC 0.5); exemplary falsification |
| **07** | **Change-point / velocity triggers** | **29** | **Winner** |
| 08 | Causal framing | 25 | The tournament's honesty mechanism (ATE CI spans zero); evidence-for-others by design |
| 09 | Portfolio optimization | 25 | Right optimizer, assumed fuel; loses to plain EV on churn capture |
| 10 | Cross-sell CF | 26 | Exemplary falsification (popularity beats CF at 9 SKUs); churn-side tilt marginal |
| 11 | Interpretable-only EBM | 14 — INCOMPLETE | Broken build (`fit_reference` returns no estimator), one fix from judgable |
| 12 | Bayesian hierarchical | 11 — INCOMPLETE | Shipped code crashes; stale metrics.json |
| 13 | Event-triggered ops scoring | 26 | Best production wrapper — adopted as the winner's ops layer, not the winner |
| 14 | Graph / hierarchy embeddings | 24 | Clean null (+0.0005 PR-AUC) — a verdict, not a tool |
| 15 | Prescriptive counterfactuals | 26 | Right prescription architecture with assumed effects; scenarios, not a system |

Protocol note (G6): only p2_02 reused the canonical reference numbers; every
other iteration reimplemented p2_01 with its own features, producing four
divergent "p2_01_reference" baselines. The judge re-verified the winner's
claims against the canonical reference (`part2_01/metrics.json` +
`artifacts/reference_test_predictions.csv`). The verdict mandates that all
downstream work import the canonical reference, never reimplement it.

### Why part2_07 won (29/30)

- **Business usefulness (5/5):** the only iteration whose output a CSM can
  operate Monday morning — 8 triggers, each with a stated rule, threshold,
  owner role, and SLA (`trigger_catalog.csv`), plus a shadow-pilot design
  for graduation. p2_01 finds who is risky; p2_07 says what changed, who
  owns the next step, and how fast.
- **Angle distinctness (5/5):** the trigger gate + EV-rank-inside-gate is
  materially different from p2_01, and the head-to-head demonstrates the
  thesis — trigger-routed 11 churners / $19.65M actual vs score-routed 10 /
  $18.56M (canonical) and 11 / $17.48M on the builder's own frame.
- **Honesty (5/5):** two triggers shipped as failures (T2's threshold
  overfit, T5's 48% fire rate), the screened-out $1.04M churner disclosed,
  the "gate is nearly the whole book without T5's retirement" caveat
  stated, lead time honestly proxied by renewal runway.
- **Rigor (5/5):** train-only thresholds with alert-volume bounds
  (3%–40%), snapshot limitation handled as a data contract, leakage audit
  clean.

Headline numbers (test frame: 400 rows, 47 churners, K=40):
trigger-routed **11 churners** (precision 0.275, recall 0.234),
**$19.20M expected / $19.65M actual** ARR captured; canonical p2_01
reference 10 / $19.46M / $18.56M; uncalibrated baseline 16 / $21.63M
expected fiction / **$9.85M** actual. Sensitivity: K=20 → 5 / $14.99M;
K=60 → 13 / $20.91M. Star trigger T8 (renewal ≤ 90d + low behavioral
health): **43.5% test precision (10/23)**, median 50-day renewal runway.
Brier 0.1095 → 0.0905 (isotonic, train-only). Source:
`approaches/part2_07/metrics.json`, `trigger_catalog.csv`.

### Combination verdict — NO merged build (earned, not defaulted)

1. p2_13 is infrastructure around a scorer, not a competitor — merging
   would produce a byte-identical metrics.json. Adopted as the winner's
   production wrapper (contamination logging, drift runbook, freshness
   SLAs, shadow-pilot gating at trigger precision ≥ 2× base rate).
2. p2_08 is evidence for other iterations — its ATE estimate already feeds
   p2_09's scenarios with caveats in code. Adopted as the standing
   gatekeeper policy: no treatment-effect number enters money math.
3. Falsifications stand alone (p2_02, p2_06, p2_14): folding them into a
   winner buries them.
4. p2_03/p2_11/p2_12 are incomplete — cannot merge.
5. No remaining pair clears the bar: p2_07+p2_15 would package assumed
   effects as a system; p2_05's playbooks + p2_07's triggers are both
   routing layers, not a better one.

Adopted elements (documented, not built): p2_13's ops machinery; p2_08's
gatekeeper caveats; p2_05's 9-segment → 9-playbook map as the playbook
library; p2_10's cross-sell white-space as a SEPARATE motion (its tilt is
K-dependent and marginal — not merged into the churn worklist).

Known defects carried forward: (1) the winner's memo baseline column is
the builder's p2_01 reimplementation, not the canonical one — re-verified,
the claim holds; (2) the trigger union fires on 66.5% of accounts — T5
must be retired/narrowed before the gate means anything; (3) lead time is
proxied, not measured — the shadow pilot is the remedy; (4) involuntary
churn unseparated (documented assumption).

### Phase 2 → Phase 3 handoff

Winner id: `approaches/part2_07`. Winning approach: p2_01-reference
scorer (HGBT, class_weight="balanced", isotonic CalibratedClassifierCV
cv=5, train-only, 33 features) reused for probabilities; innovation is the
trigger gate — 8 stated triggers, thresholds chosen on train only;
worklist = fired accounts ranked by calibrated p × ARR, K = 10% of the
eval set. Numbers that must never be cited: p2_04/p2_06
`expected_arr_at_risk` $49T/$13.57T (dollars-squared pipeline bugs);
p2_12's stale metrics.json. Falsifications not to re-litigate: survival
adds nothing; BTYD collapses to a tenure sort; embeddings add nothing at
9 SKUs; per-segment fits lose to global+interactions; CF ties
popularity; no measured motion moves churn (ATE CI spans zero).

## Phase 3 — Documentation (15 iterations)

### The 15 iterations and their angles

| # | Angle | Score /35 | One-line verdict |
|---|---|---|---|
| 01 | Executive story (BLUF-first) | 34 | Cleanest conventional read; loses on freshness |
| 02 | Methods-first technical deep-dive | 34 | Strongest technical record; a peer doc, not a walk-in aid |
| 03 | Question-driven | 35 | Best reference document; defect-free; adopted as the Q&A appendix |
| 04 | Decision memo | 33 | Best decision form — but 4 of 9 playbook pairings wrong, fatal to its thesis |
| 05 | Visual-first | 33 | Best figures; two attribution slips |
| 06 | Risk-and-limitations-led | 34 | Most honest document; risk-first is armor, not a presentation |
| **07** | **Playbook: the CSM operator's manual** | **35** | **Winner** |
| 08 | Before/after (incumbent vs new) | 34 | Best comparison machinery; adopted as the standing protocol |
| 09 | Diary / lab-notebook | 32 | Best discovery story; Brier misattribution in prose |
| 10 | FAQ / defense drill | 33 | Best defense drill; Brier misattribution in the spine |
| 11 | One-pager + appendices | 32 | Best 3-minute read; Brier + SLA attribution slips |
| 12 | Metric tree | 33 | Best one-picture figure; Slide 7 headline states precision as recall |
| 13 | Account stories | 34 | Most human proof of operability; adopted as deck proof points |
| 14 | Refresh-and-ops | 34 | Best ops doc; pre-launch checklist adopted (T4 label fixed) |
| 15 | Contrarian | 34 | Best adversarial armor; adopted as Q&A appendix + dollar-override condition |

Judged on 7 dimensions (1–5 each): narrative clarity, VP-defensibility,
completeness across all three parts, honesty about limitations, usability
as a presentation aid, traceability discipline, freshness of take. The
Phase 2 judge brief's honest-claims rules carried over: one confirmed
honest-claims violation caps honesty at 2/5; a traceability spot-check
(≥5 numbers resolved through traceability.md to the artifact) ran per
iteration. Common failure modes: attributing part2_01's Brier
(0.1065→0.0905) to the winner instead of part2_07's (0.1095→0.0905);
misattributing freshness SLAs; stating T8's 43.5% precision as "catches
43.5% of churners."

### Why part3_07 won (35/35)

The tournament's ground truth is that the system won on dollars and
rigor; the presentation's ground truth is that a system nobody operates
is slideware. part3_07 is the only iteration whose thesis is the last
mile: the trigger catalog as an operating contract, success defined as
adoption by operators. It is defect-free (5/5 red-team clean, all 9
playbook pairings verified correct against p2_05/metrics.json — the only
iteration besides the artifacts to get them right, where part3_04 got 4
of 9 wrong), it covers all three parts, its 12 slides carry full-sentence
TLDR headlines and end with the ask, and its traceability map is the most
careful in the tournament (it correctly distinguishes part2_07's Brier
from part2_01's, and correctly states that both T8 and T4 clear the 2×
bar — distinctions that tripped six other iterations).

Tiebreak: part3_03 also scored a clean 35/35. Between the two, the rule
was the iteration Ravi would most want in the room — part3_07's operator
thesis answers the question that kills case-study presentations ("nice
model — will anyone use it?"), while part3_03's armor was adopted into
the winner's appendix anyway.

### Combination verdict — documented adoption (not prose stitching)

These are documents, not builds; the winner needed elements grafted in,
not rewriting. Adopted:
1. From part3_08 — the comparison protocol (same frame, same K, three
   numbers, exclusions disclosed both ways) as the deck's "how we
   compare" standing rule.
2. From part3_03 — the 10 canonical questions as the appendix navigation
   (checklist Q3 corrected to lead with trigger-system dollars).
3. From part3_12 — `metric_tree.png` as the deck's "one picture," with
   the precision-vs-recall headline corrected.
4. From part3_14 — the pre-launch checklist as the ops slide (T4 label
   fixed to "escalation burst").
5. From part3_15 — the 8-attack red-team brief as Q&A armor, plus the
   dollar-override condition (any account above a Finance-set materiality
   threshold bypasses the trigger gate into human review — the $1.04M
   screened-out churner is the reason).
6. From part3_13 — the three verified account stories (ACC-00528 SAVE,
   ACC-00833 DECAY, ACC-00955 CONTRAST) as operator-legibility proof.

Not adopted, with reasons: part3_04's pairing table (factually wrong);
part3_09/10/11's Brier attributions; part3_05/11's SLA attributions.

## The deck

`presentation/CloudSecure_Churn_Deck.pptx` (14 slides: 12 + 2 appendix
reference slides) was rebuilt from the part3_07 spine with the six
adopted elements. Every slide carries a full-sentence TLDR headline; the
arc is data work → analysis → findings/recommendations; methodology is
grounded in industry practice (see Industry grounding below); every
number traces to a pipeline artifact. Verified by reopening the pptx.
Deck figures in `presentation/fig_v3/` were generated from the actual
artifacts (`gen_figures` inline in the deck build). The prior deck is
preserved at `CloudSecure_Churn_Deck_v2_backup.pptx` (and the original at
`CloudSecure_Churn_Deck_v1_backup.pptx`).

## Industry grounding (deep web research, 2026-10-10)

The methodology was cross-checked against how real B2B SaaS and
cybersecurity companies run churn modeling:
- Mature teams ship a **dynamic risk score** refreshed as new data
  arrives (weekly scoring, not batch), surfaced inside CRM/CSM workflows
  with threshold-triggered alerts and recommended next steps. Our
  trigger catalog is the explanation layer on top of that score.
- The ranking currency is **expected value (p × ARR), not raw churn
  probability** — probability and value are often inversely correlated;
  the full expression adds save probability and intervention cost. This
  is exactly the EV-ranked worklist.
- **Explanations are a requirement, not a refinement**: a CSM receiving
  a flag needs driver text, because mismatched interventions can
  accelerate departure. Every trigger ships with its rule, owner, and
  SLA — the explanation is the delivery vehicle.
- **Calibration is load-bearing**: raw scores must not be presented as
  probabilities; isotonic/Platt calibration is what makes ROI math
  defensible (one public case: ECE 0.160 → 0.024). Our expected-$19.20M
  vs actual-$19.65M tracking is the proof it worked here.
- **Feedback loops with intervention logging**: CSMs must record
  intervention outcomes and feed them back into retraining, with treated
  flags so the model doesn't learn "high risk + save play = retained."
  Adopted from p2_13 as the ops wrapper.
- **Shadow/pilot discipline**: measure uplift at the list boundary
  (treated vs holdout) and promote only on measured precision — our
  shadow-pilot graduation gate (trigger precision ≥ 2× base rate) is the
  production path to real numbers.
- Public benchmarks for narrative context only (never pipeline numbers):
  healthy B2B SaaS annual GRR 85–95% (median ~88–92%), NRR median
  ~104–108%, enterprise NRR 115–125%; monthly logo churn enterprise
  <0.5–1%. The standard churn scoring window is 90 days; renewal
  workflows trigger at 90/60/30 days pre-expiration. Sources:
  `approaches/CHURN_RESEARCH.md` (Round 2 notes, 2026-10-10).

## What the tournaments deliberately killed (negative results)

These are deliverables, not regrets — and they must not be re-litigated:
survival framing adds nothing over binary logistic on identical features;
BTYD-style probabilistic CLV collapses to a tenure/ARR sort on snapshot
data; graph embeddings add nothing over tabular at 9 SKUs (+0.0005
PR-AUC); per-segment fits do not beat global+interactions; collaborative
filtering ties the popularity baseline; no measured motion moves churn
(ATE confidence interval spans zero); the stated-vs-revealed survey gap
is a documented null. The final system is what survived falsification.

## Traceability anchor (load-bearing numbers)

| Claim | Artifact |
|---|---|
| Base rate 11.85% (237/2,000); $1,975.1M ARR; SentinelShield $1,161.6M (58.8%) | `approaches/part1_07/outputs/eda_findings.json` |
| Survey: respondents 9.9% vs non-respondents 15.3% churn; NPS −0.06 / behavioral −0.22 | `approaches/part1_07/approach.md` + `eda_findings.json` |
| Worklist K=40: 11 churners, precision 0.275, recall 0.234, $19.20M expected / $19.65M actual | `approaches/part2_07/metrics.json` → `worklist` |
| Canonical p2_01 reference: 10 / $19.46M / $18.56M; uncalibrated: 16 / $9.85M | `approaches/part2_01/metrics.json` |
| Brier 0.1095 → 0.0905 (isotonic) | `approaches/part2_07/metrics.json` |
| Trigger union 66.5% (266/400) | `metrics.json` → `trigger_union_test_alert_rate` |
| T8: 43.5% precision (10/23), median 50-day runway; T4: 30.0% | `approaches/part2_07/trigger_catalog.csv` |
| Sensitivity: K=20 → 5/$14.99M; K=60 → 13/$20.91M | `metrics.json` → `sensitivity` |
| 6 swaps ($4.33M/$3.04M out; $1.09M/$1.71M in; $1.04M screened out) | `approaches/part2_07/approach.md` Evaluation |
| 2× go-live bar 23.7% | `approaches/part2_TOURNAMENT.md` §4 |
| No treatment-effect dollars (ATE CI spans zero) | `approaches/part2_TOURNAMENT.md` §p2_08 |
| Account stories ACC-00528/00833/00955 | `approaches/part3_13/traceability.md` |
| NEVER cite: $49T/$13.57T (p2_04/p2_06 dollars-squared bugs); p2_12 stale metrics | `approaches/part2_TOURNAMENT.md` |
