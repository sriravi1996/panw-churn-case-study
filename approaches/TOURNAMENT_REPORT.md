# Tournament Report: 15-Approach Churn Case Study

**Date:** 2026-10-10. **Selection criterion:** approach quality (7-point rubric), NOT end-result metrics.
**Adversarial review:** 8 approaches red-teamed by hostile reviewers. **Result: 8 KILLs, 0 survivals.**

## The 15 approaches

| # | Name | Self | Mine |
|---|---|---|---|
| 01 | Refined Baseline (calibrated GBM + capacity worklist) | 34 | 33 |
| 02 | Survival Analysis (Cox/RSF, renewal calendar) | 32 | 31 |
| 03 | Uplift Modeling (persuadables) | 32 | 31 |
| 04 | Multi-Task Learning (joint churn + CLV) | 31 | 28 |
| 05 | Hierarchical (rule-based segments, per-segment models) | 29 | 29 |
| 06 | Probabilistic CLV (Beta-Geometric renewal survival) | 33 | 31 |
| 07 | Change-Detection (trajectory alerts) | 33 | 31 |
| 08 | Causal Inference (PSM/IPW/AIPW on save motion) | 30 | 28 |
| 09 | Revenue-at-Risk Portfolio Optimization (MILP knapsack) | 31 | 30 |
| 10 | Collaborative Filtering (matrix factorization) | 31 | 28 |
| 11 | Interpretable-Only (GAM/EBM because-cards) | 33 | 31 |
| 12 | Bayesian Hierarchical (partial pooling) | 32 | 29 |
| 13 | Operational Framing (event-triggered scoring) | 30 | 29 |
| 14 | Graph Embeddings (account-product bipartite) | 30 | 27 |
| 15 | Prescriptive Counterfactuals (what-if simulator) | 32 | 33 |

Rubric (1-5 each): (1) problem framing, (2) methodological rigor, (3) business actionability,
(4) VP-defensibility, (5) edge-case coverage, (6) industry alignment, (7) completeness vs Parts 1-3.

Approaches 04, 05, 08, 10, 12, 13, 14 were scored but not red-teamed (below the top tier;
all 8 red-teamed approaches above them died, so red-teaming lower-scored ones was not pursued).

## Red-team outcomes (all KILL)

### Approach 01 — Refined Baseline — KILL
- The founding 44% calibration-overstatement figure was never computed in this approach;
  it lives only in a code docstring and traces to a stale table. The undisclosed head-to-head:
  incumbent top-300 caught 166 churners (55.3%); the "refined" worklist catches 117 (39.0%).
- Capacity model (300 = 12 CSMs x 25) is invented; no basis exists in the repo. The chosen
  operating point has worse precision (0.25) than the max-F1 it replaced (0.386).
- K-means segments (silhouette 0.0705) are a usage tertile in costume; two of three map to
  the identical playbook; one playbook assigns a "new-logo onboarding" motion to a segment
  with median tenure 4.1 years. Segmentation changes zero decisions.
- The $218.6M cross-sell figure uses co-ownership as conversion rate (no close-rate assumption).
- Justification #7 defends k=4; the actual k is 3. The repo's own run log shows a failed run.
- What survives: the calibration technique replicates across seeds; no temporal leakage found;
  all JSON numbers are genuine outputs. The flaws are in claims and scoping, not the core.

### Approach 02 — Survival Analysis — KILL
- The (T=tenure, E=churned) event-time construction is fictional: the generator never simulated
  event times (Bernoulli DGP, no time component). The memo contradicts itself on time direction.
- A plain binary logistic regression beats the Cox model on identical features (AUC 0.8510 vs
  C-index 0.8372), empirically falsifying the thesis that survival analysis was needed.
- The shipped worklist assigns intensive save plays to 17 already-churned accounts.
- Excluding days_to_renewal as "leakage" is unjustified and self-defeating (it's in the true DGP).

### Approach 03 — Uplift Modeling — KILL
- Treatment is synthetic; 12-24 months before production-usable. Unconfoundedness assumed;
  the synthesis deletes the main confounder (CSM gut feel) by construction.
- The X-learner gamed Qini past the true-tau oracle, indicting the evaluation metric itself.
- Qini-estimated vs TRUE ARR are 25x apart ($1.0M vs $26.0M); the money slide is unquotable.
- Its own ground-truth table refutes its deployment policy: "sure things" (no intervention)
  respond at +8.6pp; the policy starves the most persuadable segments.
- Do not present the $26M ARR or "8.1x" figures anywhere; they are synthetic-only.

### Approach 11 — Interpretable-Only — KILL
- Central claim is false on both halves: exact TreeExplainer SHAP on GBM already yields
  per-account additive attributions, so the because-cards aren't exclusive; and CSM trust is
  driven by precision (43%), which the glass box doesn't fix.
- Its own correlation audit proves the flagship because-card number (+1.51) is
  allocation-arbitrary. The GBM baseline was overfit (train AUC 1.0) and uncalibrated.
- Monotonicity constraints encode author priors and can erase real signal; the interaction
  experiment is rigged by the additive synthetic DGP.

### Approach 15 — Prescriptive Counterfactuals — KILL
- The entire evaluation is the model grading its own homework: coverage, costs, and the
  $15.3M "expected retained value" are the GBM's response to synthetic perturbations, with
  no measured treatment effect anywhere. No sensitivity analysis on the 0.5x-IQR effect sizes.
- Gaming defenses channel gaming into the exact features the catalog perturbs.
- The hours-knapsack uses a false resource model, a weak optimizer (sorts by total EV, not
  value-per-hour), and documents behavior ("light-touch for unfunded") that doesn't exist in code.
- Full-book coverage is 71.6%, concentrated in the highest-risk accounts.

### Approach 06 — Probabilistic CLV — KILL
- The Beta-Geometric "model" is mathematically equivalent to sorting by tenure:
  Spearman(p_death, -tenure) = 1.0 with 13 unique values. Every downstream product is a
  tenure sort in probabilistic costume.
- The revenue-coverage comparison ($167.5M vs $141.9M) rests on a GBM number that exists
  nowhere in the repo's code or data, in a rigged comparison that loses to sorting by ARR
  ($173.0M vs $167.5M).
- The "122 reassigned by the engagement guard" claim is false; actual reassignments = 0.
- The Watch segment (light touch) holds more RAR ($191.4M) and higher churn (21.2%) than
  Protect (exec save motions, 6.9%) — the "principled prioritization" prioritizes backwards.

### Approach 07 — Change-Detection — KILL
- Every headline number was measured on trajectories whose shapes were assigned from the
  labels (89% of churners get explicit decay archetypes). The 0.947 AUC cannot distinguish
  "change detection works" from "the author simulated churners that decay."
- The "5-week lead time" is a deterministic readout of integers typed into the simulator's RNG.
- Alert rule tuned and evaluated in-sample (no holdout); the detector was handed the seasonal
  cycle answer key (CYCLE=4 hardcoded in both synthesis and detection).
- Keep as unvalidated prototype; strip all comparative numbers until real telemetry exists.

### Approach 09 — Portfolio Optimization — KILL
- The "optimal" plan is a pure function of invented treatment effects; its own sensitivity
  analysis proves fragility (T2 27->0 under T2-weak; $1.34M regret on the base plan).
- The "exact" MILP was beaten by its own greedy heuristic; the pessimistic plan outscores
  the base "optimum" under base economics.
- Cross-sell is 1.2% of the objective despite half the thesis; the eligibility gate excludes
  72% of portfolio risk; T1 automation (55% of headline) was never stress-tested.

## Winner selection

No approach survived adversarial review. The winner is selected as the **least dead**:
the approach whose core methodology is sound and whose flaws are fixable in presentation
and scoping rather than structural.

**Winner: Approach 01 (Refined Baseline).**

Why 01 and not the others:
- 02's clock is fictional; 03 can't run in production for 12-24 months; 06's model is a
  tenure sort; 07's numbers are baked into its simulation; 09 optimizes invented inputs;
  11's thesis is false; 15's evaluation is circular. These are structural/methodological deaths.
- 01's deaths are in claims and scoping: the phantom 44% figure, invented capacity numbers,
  weak K-means segments, decorative sales half, reproducibility gaps. Its core — stratified
  split, train-only statistics, calibrated GBM, honest validation, no temporal leakage —
  is methodologically sound. The red-teamer confirmed: "The calibration technique replicates"
  and "No temporal leakage found. This is the one attack the approach walks away from."

## Salvageable insights folded into the winner

- From 03: rank by incremental effect, not just risk (as a limitations footnote, not a method).
- From 11: global SHAP explanations for the GBM (the real edge 11 buried); group correlated
  drivers on any per-account explanation.
- From 15: feasibility-constraint thinking for playbooks; explicit "no feasible playbook"
  routing (honestly reported).
- From 07: the shadow-mode pilot proposal as the validation roadmap for any behavioral signal.
- From 09: capacity-as-parameter with honest sensitivity (not invented constants).
- From 02: renewal-calendar anchoring of plays (binary model + calendar, not fictional survival).
- From 05: rule-based segments (tenure x breadth) replacing K-means.

## Rebuild requirements (canonical solution)

The canonical rebuild MUST fix every fatal 01 finding:
1. Remove the phantom 44% claim; report honest Brier before/after with the measured numbers.
2. Capacity as an explicit parameter with sensitivity analysis; no invented "12 CSMs."
3. Replace K-means (silhouette 0.0705, zero decision-changing segments) with rule-based
   segments (tenure x product breadth, per approach 05); verify each segment maps to a
   DISTINCT playbook or drop segmentation as a decision input.
4. Honest sales scoping: drop the $218.6M co-ownership-as-conversion fiction; report
   white-space identification with explicit close-rate assumptions or not at all.
5. Reproducibility: one command reproduces everything; the shipped model regenerates the
   shipped worklist; fix the 12-vs-8 config discrepancy; fix justification #7 (k=3, not 4).
6. Disclose the incumbent comparison honestly (166 vs 117) or don't claim improvement.
7. Every number from actual pipeline outputs; no hardcoded deck figures.

## Rebuild completed (2026-10-10)

All 7 requirements verified fixed:
1. 44% claim removed everywhere (code, memos, deck); calibration rests on measured
   Brier 0.1031 -> 0.0858.
2. `--capacity` CLI parameter (default 300, illustrative); sensitivity 200/300/400
   in outputs; no org-chart fiction.
3. Rule-based tenure-x-breadth segments; 6 segments -> 6 distinct playbooks
   (asserted in code); churn separation 38.5% -> 4.1%.
4. $218.6M relabeled gross white-space (100% close, labeled NOT a forecast);
   pipeline scenarios at 10/20/30% close: $21.9M / $43.7M / $65.6M.
5. `bash scripts/run_all.sh` runs clean end-to-end (exit 0), twice verified;
   8-config grid documented as 8; k=4 justification rewritten for rule-based.
6. Head-to-head computed in-pipeline and disclosed on a deck slide:
   incumbent 165 churners (55.0%), $75.5M actual churned ARR;
   EV-ranked 117 (39.0%), $117.0M actual churned ARR.
7. Deck rebuilt via presentation/build_deck.py reading only pipeline JSONs;
   12 slides verified - every figure traces to outputs/, no phantom numbers.

Canonical solution at the project root: scripts/01-06 + common.py,
outputs/ (18 artifacts), README.md, presentation/CloudSecure_Churn_Deck.pptx.
The pre-tournament scripts (train_model.py, segmentation.py, affinity.py,
clv_model.py) and their stale artifacts were moved to recoverable trash.
