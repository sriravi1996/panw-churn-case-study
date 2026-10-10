# part1_07 — Survey-Augmented: Stated vs Revealed Account Health

## Design choices
Core B2B spine (2,000 accounts, 20-product portfolio, hero product **PRD-01
"SentinelShield"**) plus a synthetic **NPS/CSAT survey table** — the angle.
Each account receives 1–3 survey invitations; a latent satisfaction score
drives both survey answers and churn, creating two realistic distortions:

- **Nonresponse bias**: response probability rises steeply with satisfaction
  (at-risk accounts go silent), so the respondent pool skews healthy.
- **Courtesy bias**: 12% of respondents inflate NPS by +2 out of politeness.
  This is *bias, not fraud* — the quality filter must not catch it.

Survey fraud (the cleaning challenge) is injected as four patterns:
straight-lining (3%, zero-variance 5-item grids), speeders (4%, <60s),
duplicate submissions (1.5%, same respondent email), and a copy-paste farm
(2%, identical open text submitted in 3-day bursts across accounts).

## Dirty-data patterns
Industry label variants (24 → 6 canonical), mixed contract-date formats plus
"N/A"/"TBD" tokens (pandas `read_csv` silently coerces "N/A" to NaN — read
with `keep_default_na=False`), ~1.5% duplicate order rows, product_id case
variants, MCAR missingness on engagement/telemetry fields. In the survey
table, the four fraud patterns above plus honest satisficing (zero-variance
grids completed at normal speed — deliberately *not* flagged as fraud).

## Cleaning / dedup / entity resolution
Standard tables: industry mapping, `format="mixed"` date parsing, dedup on
the `(account_id, product_id)` business key (81 rows), product_id upper-case
ER (288 rows). Survey response-quality pipeline flags each response on four
independent signals; a response is valid only if none fire. Duplicates and
copy-paste are treated as entity-resolution problems (same respondent / same
farm text → single canonical record, earliest kept). Copy-paste detection
keys on the fraud *signature* — identical long text across >3 accounts inside
a ≤7-day burst — so honest template reuse spread over 90 days is untouched.
**Result**: 2,044 raw responses → 1,768 valid (86.5%), 276 quarantined
(13.5%: 129 straight-liners, 133 speeders, 30 duplicates, 40 copy-paste).
Account coverage: 1,391/2,000 accounts have ≥1 response; 1,279 have
≥1 *valid* response.

## Integration
Left-join account spine → subscription aggregates (total ARR, hero ARR,
hero share, top product), telemetry, support, engagement, valid-only survey
aggregates (mean NPS/CSAT, validity rate), and labels. Derived
`stated_vs_revealed_gap = z(valid NPS) − z(behavioral health)`, where
behavioral health blends active-user ratio, 90-day usage decay, and ticket
resolution rate. Output: `modeling_table.csv` (2,000 × 47), join keys
verified unique, plus `outputs/integration_summary.json`.

## EDA questions + key findings
**Top ordered items**: SentinelShield leads (2,000 orders, $1,161.6M ARR);
best cross-sell is PostureLens (704 orders, $166.1M), then NetBarrier
($128.1M) and ThreatScope ($126.8M). Hero product = 58.8% of total ARR
($1,975.1M); mean 2.72 products/account; top-10% accounts hold 29% of ARR.

**Highest-value relationships**: top account ACC-01909 at $8.14M ARR
(92% hero); the 10 largest account×product pairs are all SentinelShield
($4.2M–$7.5M) — expansion lives or dies on the hero product.

**Stated vs revealed health**:
- Valid NPS correlates only **0.09** with behavioral health, and **−0.06**
  with churn — the survey barely tracks what accounts *do*. Behavioral
  health correlates **−0.22** with churn (4× stronger).
- **Nonresponse bias is the dominant distortion**: 63.9% response rate;
  respondents churn at 9.9% vs **15.3% for non-respondents** (+55%).
  "Dark accounts" (no valid survey + usage decay <0.80): 158 accounts
  (7.9%), churn **15.8%** vs 11.5% elsewhere — the blind spot is where the
  risk concentrates.
- Fraud filter: naive NPS 8.17 vs valid 8.15 — the mean barely moves, but
  quarantined responses skew hard-promoter (36.6% score 10; mean 8.33 vs
  8.15 valid), so unfiltered NPS overstates advocacy at the top end. The
  inflation is not spread evenly: **straight-liners** drive it (129
  responses, mean NPS 8.60, **46.5% score 10** vs 32.3% for valid), followed
  by the **copy-paste farm** (40 responses, 40.0% tens); **speeders** look
  like valid respondents (mean 8.14, 27.8% tens) and merely add noise. 48 of
  the 129 straight-liners are also speeders — rushed grid-filling — and 53
  responses carry multiple flags.
- Top stated-vs-revealed gap decile: mean NPS 9.8 with active-user ratio
  only 0.24 ("polite but disengaged") vs bottom decile NPS 4.8 / ratio 0.52.
  Takeaway for the churn model: never trust NPS without a behavioral
  cross-check, and treat *silence* (nonresponse) as a risk feature, not
  missing data.
