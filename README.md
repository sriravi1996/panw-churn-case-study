# CloudSecure Churn Prediction

Account-level churn intelligence for **CloudSecure**, one product in an
8-product B2B cybersecurity portfolio. This case study answers the core
question: **how can we boost customer loyalty and accelerate sales?**

Three analyses feed one answer:
1. **Customer segmentation** (who are our accounts),
2. **Predictive modeling** (who will churn, and what they are worth),
3. **Product affinity** (what to sell them next).

This is the canonical solution: the winner of a 15-approach tournament,
rebuilt after adversarial review. Every number below is read from the
pipeline JSON outputs in `outputs/` (see "Run it"). The tournament report
(`approaches/TOURNAMENT_REPORT.md`) documents the selection.

## 1. Problem framing and approach

**Why account-level:** In B2B SaaS the buying unit is the account, not the
user. A 50,000-seat deployment renews or churns as one contract, so the
grain of prediction must be the account.

**Label, stated exactly:** churned = 1 if the account cancels or does not
renew the CloudSecure subscription within 90 days of the scoring date
(2026-10-01). We model logo churn (accounts) and revenue at risk (ARR)
separately, because one lost enterprise account outweighs many small ones.

**Why binary classification plus CLV regression:** the business decision is
binary (intervene or not), so we predict P(churn) and threshold it into a
CSM worklist; ranking quality (PR-AUC) matters more than raw accuracy at a
12.8% base rate. The CLV model answers the companion question, how much
each account is worth, so interventions are prioritized by expected
retained dollars, not just risk.

**Scope:** 3,000 enterprise accounts, 35 features across seven families
(firmographics, sales/cross-sell, marketing, support health, telemetry,
engagement, contract). Overall churn is 12.8% (383 of 3,000 accounts);
$1.78B total ARR in scope, $214.9M of it in churned accounts (GRR proxy
87.9%).

**The operating thesis:** the buying unit is the account, the decision is
binary (intervene or not), the scarce resource is CSM attention, and the
ranking currency is expected dollars at risk (calibrated p(churn) x ARR).

## 2. Data engineering and EDA

No CSVs were provided, so all data is synthetically generated for a B2B
SaaS cybersecurity company (`data/generate_data.py`, seed 42) as **seven
related source tables** mirroring real source systems:

| Table | Rows | Source system |
|---|---|---|
| accounts | 3,000 | CRM (firmographics, contract) |
| products | 8 | product catalog |
| subscriptions | 9,780 | billing/entitlements (account-product holdings) |
| telemetry | 2,940 | product analytics (target-product usage) |
| support_tickets | 3,000 | support desk |
| engagement | 3,000 | marketing automation / CRM |
| labels | 3,000 | churn outcome + CLV within 90-day window |

`scripts/integrate.py` ingests, cleans, and joins them into
`data/modeling_table.csv` (3,000 rows x 35 cols) plus
`data/product_holdings.csv` (account x product matrix). Cleaning is
deterministic (no statistics fit): 21 raw industry labels normalized to 5,
mixed date formats parsed (90 unparseable), 146 duplicate subscription rows
removed, product_id case normalized, 60 accounts with no telemetry kept via
left join. All statistic-based cleaning (median imputation, p99
winsorization) is fit on train only inside the modeling pipelines.

A code-enforced leakage audit runs before any modeling: the latent
ground-truth probability never reaches the modeling table, ID columns are
excluded from features, and as-of discipline is documented.

Key findings (`scripts/eda.py`, figures in `figures/`):
- **Breadth is stickiness:** single-product accounts churn at **27.5%**
  (931 accounts, $549.4M ARR) vs 7.1% for 2-5 products and 2.5% for 5+.
- **New logos are the risk cohort:** 19.9% churn under 2 years tenure vs
  8.9% above 5 years.
- **Industry is a weak signal:** churn spread only 16.5%-19.1% across
  industries.
- **Usage threshold:** 1,249 accounts below 0.35 active-user ratio churn at
  22.3%; churn collapses once the ratio clears 0.60 (3.3%).
- Strongest raw correlations with churn: `other_products_owned` (0.27),
  `active_user_ratio` (0.24), `portfolio_avg_usage` (0.22).

## 3. Analysis and modeling

### 3a. Customer segmentation

Rule-based lifecycle segments: tenure (new <2yr / mid 2-5yr / tenured
>5yr) x product breadth (single/multi). A-priori cutoffs, nothing tuned,
nothing that fails across seeds. (`scripts/02_segment.py`)

| Segment | Accounts | Churn | ARR | Playbook |
|---|---|---|---|---|
| new-single | 182 | 38.5% | $99.9M | New-logo adoption program |
| new-multi | 330 | 10.0% | $212.1M | Multi-product onboarding acceleration |
| mid-single | 459 | 27.2% | $261.8M | Save + cross-sell strike team |
| mid-multi | 1,012 | 6.3% | $596.9M | Grow play |
| tenured-single | 290 | 21.0% | $187.8M | Tenured attach motion |
| tenured-multi | 727 | 4.1% | $422.7M | Advocacy program |

Six segments, six DISTINCT playbooks (uniqueness asserted in code) - a
segmentation that changes decisions by construction. Churn separation
38.5% -> 4.1%.

### 3b. Predictive modeling

**Churn classifier** (`scripts/01_train_churn.py`). Stratified 80/20 split.
Class-weighted loss (no SMOTE: synthetic accounts would corrupt the
calibration every dollar figure depends on). Deterministic 8-config grid
search, 3-fold CV on train only, PR-AUC scoring (best 0.4751). Test set
touched once.

| Metric (test set) | Logistic regression | GBM calibrated (champion) |
|---|---|---|
| ROC-AUC | 0.830 | 0.858 |
| PR-AUC | 0.477 | 0.482 |
| Precision @ max-F1 | 0.226 | 0.471 |
| Recall @ max-F1 | 0.883 | 0.519 |
| F1 | 0.360 | 0.494 |
| Brier score | 0.1657 | 0.0858 |

**Calibration is the headline fix:** isotonic calibration cuts Brier from
0.1031 (uncalibrated GBM) to 0.0858 on the held-out test set. The business
consumes probabilities as dollars (p x ARR); uncalibrated dollars are
fiction.

**Why the GBM is champion:** better ranking (ROC-AUC 0.858 vs 0.830) and
substantially better calibration (Brier 0.0858 vs 0.1657); churn here is
threshold-driven (adoption either happens or it does not), which trees
represent natively. The linear model stays on as an interpretable
challenger. Top drivers (permutation importance, PR-AUC drop):
`active_user_ratio` (0.170), `other_products_owned` (0.084),
`ticket_resolution_rate` (0.078), `tenure_years` (0.047),
`arr_portfolio` (0.028).

**The capacity worklist and the honest trade-off.** The operating worklist
is the top-300 accounts by EXPECTED ARR AT RISK (calibrated p x ARR), with
capacity as an explicit operator-set parameter (default 300,
illustrative; sensitivity at 200/300/400). The pipeline computes the
incumbent head-to-head on the same out-of-fold data:

| Top-300 worklist | Churners caught | Churn rate | Actual churned ARR | Expected ARR at risk |
|---|---|---|---|---|
| Incumbent: uncalibrated, probability-ranked | 165 | 55.0% | $75.5M | $116.3M (uncalibrated) |
| Ours: calibrated, EV-ranked | 117 | 39.0% | $117.0M | $120.8M (calibrated) |

Probability ranking catches more churners (they skew low-ARR); EV ranking
captures 55% more actual churned dollars. The business maximizes retained
dollars, not correct classifications - so the worklist is EV-ranked, and
the churner-count trade-off is disclosed, not buried.

Risk tiers from out-of-fold calibrated probabilities:

| Tier | Accounts | Actual churn | Expected ARR at risk |
|---|---|---|---|
| High | 300 | 39.0% (117) | $120.8M |
| Medium | 600 | 23.3% (140) | $73.9M |
| Low | 2,100 | 6.0% (126) | $48.2M |

The worklist export (`outputs/worklist.csv`) carries `days_to_renewal` so
CSMs sequence save plays against the 90/60/30-day renewal calendar.

**CLV regression** (`scripts/04_clv.py`). HistGradientBoostingRegressor on
12-month expected revenue: test R2 0.9525, MAE $58,501, RMSE $133,852.
Honest ablation: ARR-features-only R2 is 0.9045 - most CLV signal is "worth
what they pay now"; the model adds retention/expansion refinement for
prioritization, not discovery. Role discipline: the worklist ranks by
p(churn) x ARR, cleaner to defend than regression-based CLV.

### 3c. Product affinity

Association rules on the account-product holdings matrix (support >= 2%,
confidence >= 15%, lift >= 1.2; Fisher's exact test per rule; universal
antecedent excluded). (`scripts/03_affinity.py`)

| Rule | Lift | Confidence |
|---|---|---|
| IdentityGuard -> SOCInsights | 1.82 | 37.3% |
| EndpointPro -> SOCInsights | 1.82 | 37.3% |
| SOCInsights -> IdentityGuard | 1.82 | 54.2% |

1,960 accounts have a quality-filtered cross-sell recommendation. Honest
sizing: gross white-space value $218.6M **assumes a 100% close rate** - it
is the size of the prize, not a revenue forecast. Pipeline scenarios at
labeled close-rate assumptions: 10% -> $21.9M; 20% -> $43.7M; 30% ->
$65.6M. Close rates are business assumptions, not model outputs.

## 4. Business recommendations

13 playbooks in `outputs/playbook_matrix.json`, each with owner, trigger,
action, SLA, decision, and success metric - all generated from the model
outputs, no invented numbers:

1. **Executive save play** (high tier: 300 accounts, $120.8M at risk).
   1:1 CSM + exec sponsor inside the 90-day window, sequenced by
   days_to_renewal. Success metric: high-tier churn vs the computed
   incumbent worklist rate (55.0%); retained ARR.
2. **CSM save play, human-reviewed** (medium tier: 600 accounts, $73.9M).
   Triggered on usage decay, P1, or downgrade.
3. **Automated adoption nudges** (low tier: 2,100 accounts). Zero human cost.
4. **Lifecycle overlay:** six segments, six distinct plays - new-logo
   adoption for new-single (38.5% churn), save + cross-sell strike team for
   mid-single (27.2%), grow play for the mid-multi core, attach motions
   for tenured-single, advocacy for tenured-multi.
5. **Cross-sell attach** on the single-product base (931 accounts, 27.5%
   churn, $549.4M ARR); the affinity engine picks the product per account.
6. **Adoption intervention** under the 0.35 usage threshold; **support fast
   lane** under 0.70 resolution; **renewal operations cadence** at
   90/60/30 days.

Expected impact framing (scenarios, not promises): moving the high tier's
churn halfway to the base rate protects ~$40M+ ARR (GRR lever); cross-sell
pipeline $21.9M-$65.6M at 10%-30% close rates (NRR lever, attach rate as
leading indicator).

## 5. Deployment architecture

See `docs/architecture.md` for the full diagram. In short:
- **Training:** monthly retrain on a 24-month rolling window (Airflow);
  champion/challenger gate on holdout PR-AUC.
- **Inference:** weekly batch scoring; scores, tiers, top drivers, and the
  cross-sell recommendation land on the CRM account record; the worklist
  carries days_to_renewal for calendar sequencing.
- **Monitoring:** executable PSI checks per feature (smoke-tested, 0 alerts
  on train vs test), score drift, PR-AUC decay as renewals resolve (monthly).
  Retrain on PSI > 0.2 or PR-AUC drop > 0.05. See
  `outputs/monitoring_runbook.json`.
- **Feedback loop:** CSM logs intervention + outcome per flagged account
  with a treated flag for retraining - or the model learns "high risk +
  save play = retained" as if risk alone did it.
- **Edge cases as operating rules:** temporal leakage (as-of cutoff, audit
  in code), censoring (label-maturity gate: never train on windows younger
  than 90 days), voluntary vs involuntary churn (billing reason codes ->
  dunning, excluded from training), label lag (90-day window, monthly
  backfill), model decay (drift monitors).

## 6. Limitations and next steps

- Synthetic data: relationships are realistic but the latent logic is
  known; on real data, expect lower separation - and the calibration
  discipline matters more, not less.
- No causal estimates: the worklist ranks by risk x dollars, not by the
  incremental effect of the save motion. The churner-count trade-off vs the
  incumbent (117 vs 165) is disclosed; if the org values logo-count over
  dollars, change the ranking - said explicitly.
- Single 90-day window: production scores on a renewal calendar cadence.
- Next, sequenced: (1) shadow-mode pilot - score weekly, log what the
  worklist would have flagged, compare against outcomes for two quarters
  before any behavioral signal drives automated plays; (2) uplift modeling
  to separate the persuadable from the merely risky; (3) champion-departure
  signals from contact data; (4) per-account SHAP attributions (exact
  TreeExplainer on the GBM) on the CRM record.

## Run it

```bash
pip install -r requirements.txt
python3 data/generate_data.py      # data/raw/ (7 source tables)
python3 scripts/integrate.py       # data/modeling_table.csv + integration report
python3 scripts/eda.py             # figures/ + figures/eda_findings.json
bash scripts/run_all.sh [capacity] # outputs/ (18 artifacts; default capacity 300)
python3 presentation/build_deck.py # presentation/CloudSecure_Churn_Deck.pptx
```

All steps are deterministic (seed 42). Every number in this README and the
deck is read from the pipeline JSON outputs at build time - nothing is
hardcoded.
