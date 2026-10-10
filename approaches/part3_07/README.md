# Churn Early-Warning: The Operator's Manual

*A CSM's guide to the SentinelShield churn early-warning system — what the
list is, what to do when an account fires, and what the numbers mean. Built
from `approaches/part1_07/` (data foundation), `approaches/part2_07/`
(trigger catalog + pilot), `approaches/part2_01/metrics.json` (the
reference model), and `approaches/part2_05/` (the playbook library).*

## How to use this manual

This is not an analytics report. It is the instruction set for the people who
work the churn worklist. If you own accounts, read the trigger sections for
the triggers you own, learn the routing rule, and keep the capacity bands in
mind when your queue is full. If you are new, read it cover to cover once;
after that, each trigger's section stands alone — rule, threshold, owner,
SLA, what the firing means, what to say on the call, and how we measure it.

The whole system, in one paragraph: every account gets a calibrated churn
probability from a model trained on 2,000 accounts. But probabilities alone
never told anyone what to do, so eight behavioral triggers turn the score
into events — a usage cliff, a silent champion, a renewal under pressure.
Only accounts that fire at least one trigger can make your list, and the
fired accounts are ordered by expected dollars at risk. Work from the top
down, act within your SLA, and log everything you do. Two of the eight
triggers are retired before go-live; their sections say so in the headline.

---

## Part 1: the data underneath your list (why it is trustworthy)

Before you trust a list, you should know what was built under it. Three facts
matter for operators.

**First, the label is clean and honest.** An account "churns" if it cancels
or does not renew SentinelShield, the hero product, within 90 days of the
scoring date. Across 2,000 accounts that happened 237 times — an 11.85%
base rate. Hero-product churn is the right grain for this job: SentinelShield
is $1,161.6M of the $1,975.1M total book (58.8%), expansion lives or dies on
it, and the 10 largest account-product pairs are all SentinelShield. When the
manual talks about dollars at risk, it talks about this product's ARR.

**Second, the survey data was treated the way surveys deserve.** About 64% of
accounts have a valid survey response; the rest are gated by a fraud filter
that quarantined 13.5% of raw responses (straight-liners, speeders,
duplicates, a copy-paste farm). Two findings matter to you. One: accounts
that answered the survey churn at 9.9%, accounts that did not answer churn at
15.3% — silence is itself a risk signal, which is why "dark account" is one
of your triggers. Two: the stated-vs-revealed check came back weak — valid
NPS correlates only 0.09 with behavioral health and −0.06 with churn, while
behavioral health correlates −0.22 with churn, roughly four times stronger.
So this system never trusts what an account *says* without checking what it
*does*. Survey scores are context on your calls; they never gate the list.

**Third, the book is concentrated.** Mean 2.72 products per account; the top
10% of accounts hold 29% of ARR; the largest account is $8.14M. One sobering
data point: even the top account, ACC-01909 at $8.14M, churned. Size does not
immunize. That is exactly why the list is ranked by dollars times
probability, not by size alone — a big account with no churn signal should
not crowd out a smaller account that is actively dying.

---

## Part 2: how your list is built (just enough model)

Three steps turn the data into your Monday list. You need to understand the
logic, not the math.

**Step 1: a calibrated risk score.** Every account gets a churn probability
from a gradient-boosted model trained only on data known before the scoring
date (no peeking at the future; the leakage audit passed with 33 clean
features). Then the probabilities are calibrated — a process that cut the
Brier score from 0.1095 to 0.0905. In plain language: when the model says
30%, about 30 in 100 such accounts actually churn. That is the entire reason
the dollars on your list are trustworthy. A 30% chance on a $2M account is
$600K of expected exposure, and the 30% means what it says.

**Step 2: the trigger gate.** Only accounts that fire at least one trigger
are eligible for your list. This is the decision that makes the system
operable: instead of "here are the 40 riskiest accounts, good luck," you get
"this account fired because its champion went silent 30 days ago — here is
who owns the next step and how fast." The triggers are the subject of the
whole next section. Their thresholds were chosen on training data only, with
alert-volume bounds of 3% to 40%, so the list cannot be gamed into a tiny
"perfect" alert set.

**Step 3: rank by expected dollars at risk.** The fired accounts are ordered
by calibrated probability × ARR — expected ARR at risk — and the top K form
the worklist. K=40 is the illustrative default: 40 accounts, roughly 10% of
the book. On the evaluation data, those 40 accounts contained 11 actual
churners (27.5% precision, 23.4% recall) and $19.65M of actual churned ARR,
against $19.20M expected — the expectation and the reality line up, which is
what calibration buys you.

**Why not just the score?** The head-to-head was run. The pure score-ranked
reference list caught 10 churners and $18.56M. The trigger-routed list caught
11 churners and $19.65M — more churners *and* more dollars. The two lists
differed by 6 swaps: the gate screened out 5 high-ARR accounts that were not
churning (including a $4.33M and a $3.04M account — expensive false alarms
the score alone would have sent you chasing) and pulled in 2 real churners
($1.09M and $1.71M) the pure score missed. Disclosed cost of the gate: one
$1.04M churner was in the score list but did not fire a trigger and was
screened out. No gate is free; this one's cost is known and small.

**Why not the uncalibrated shortcut?** The raw, uncalibrated ranking caught
*more* churners — 16 — but only $9.85M of actual ARR. It finds many small
accounts and misses the big ones. Calibration plus expected-value ranking
catches fewer accounts and roughly twice the dollars. If your job is to
protect revenue, you want the second list.

**What the model output means on a call.** You will never see a raw
probability and you must never quote one to an account. On the worklist you
see the trigger that fired and the expected ARR at risk — "calibrated p ×
ARR — the dollars are real because the Brier score went 0.1095 to 0.0905."
What you say on the phone is the trigger's plain-language reading, not the
number. "Your usage has dropped sharply over the last 90 days, and I want to
understand what changed on your team before your renewal comes up" — that is
T1. The dollars are for your prioritization; the trigger is for the
conversation.

---

## The trigger playbook: trigger → owner → SLA

The catalog holds eight triggers. Six are live. Two — T2 and T5 — are
**RETIRED before go-live** and say so in their own sections. They are
organized here by owner, and within each owner by readiness.

A standing rule for every live trigger: when you act, log the action with a
treated flag and a timestamp. We have no measured evidence that any save
motion moves churn — the causal analysis came back null — so nothing in this
manual assumes a save rate. The treated-flag log is how the pilot will
eventually measure what works. Act, then log, in that order.

### Account-executive triggers

#### T8 — Renewal pressure + low health: LIVE, highest priority

- **Exact rule:** `days_to_renewal <= 90 AND behavioral_health <= train-Q25`
  (behavioral health in the bottom quartile of the training book).
- **Plain language:** this account fired T8 because it renews within 90 days
  AND its behavioral health is in the bottom quartile. The renewal
  conversation starts now, not at renewal. This is the only trigger whose
  lead-time proxy is measured in weeks rather than months — a median 50-day
  renewal runway — so it is the closest thing this system has to an alarm.
- **Owner:** Account Executive.
- **SLA:** renewal plan within 5 business days.
- **Test read:** 10 of 23 flagged accounts churned — 43.5% precision, the
  sharpest trigger in the catalog, and the only one far above the 2×
  base-rate go-live bar (23.7%).
- **On the call:** do not lead with the renewal. Lead with the health. "I am
  looking at your team's usage ahead of the renewal, and a few signals are
  off — I want to get ahead of it with you. Walk me through how the team is
  using us day to day." You have roughly 50 days; spend them on diagnosis,
  not on discounting.
- **Route into:** the account's segment playbook (Section "The playbook
  library"). For a new single-product account, that is the fast-start
  adoption play; for a tenured single-product account, loyalty +
  modernization.
- **Success metric (process):** renewal plan created and logged within the
  5-day SLA; treated flag set on every save action; account either exits the
  trigger state or has a dated renewal plan.

#### T6 — Downgrade event: LIVE

- **Exact rule:** `downgraded_12m == 1` — the account downgraded at least once
  in the last 12 months.
- **Plain language:** this account already told you something is wrong, once,
  in the language of money. A downgrade is a partial churn that got
  negotiated instead of completed.
- **Owner:** Account Executive.
- **SLA:** save conversation within 3 business days — the tightest AE clock
  in the catalog, because the account has already demonstrated willingness
  to shrink the contract.
- **Test read:** 14.7% precision — below the 2× go-live bar, so it ships
  gated: it pages a human only after the shadow pilot promotes it; until
  then its signal lives in the score and the worklist ordering.
- **On the call:** "I saw the downgrade last quarter. I want to understand
  what drove it and whether the remaining footprint is actually delivering
  what your team needs." The downgrade is the opening; the real question is
  what else is at risk.
- **Success metric (process):** save conversation completed and logged
  within 3 business days; treated flag set.

### Support-lead triggers

#### T4 — Escalation burst: LIVE, clearest support signal

- **Exact rule:** `escalations_12m >= 4` — four or more escalations in 12
  months.
- **Plain language:** the relationship is running on incident response. Four
  escalations in a year means the account experiences you as a problem, not
  a platform.
- **Owner:** Support Lead.
- **SLA:** executive review within 24 hours — the fastest clock in the
  catalog. An escalation-burst account cannot wait for the weekly cycle.
- **Test read:** 30.0% precision, the second-sharpest trigger, and it clears
  the 2× base-rate go-live bar. Median lead-time proxy 148.5 days to
  renewal — this one fires early, which is why the 24-hour clock matters:
  you have time if you start now.
- **On the call:** this is a support-led motion, not a sales motion. The
  message is ownership of the incident history: "Your team has escalated
  four times this year. That is not acceptable to me. I have reviewed the
  history and here is what changes." Bring the incident review, not a pitch.
- **Success metric (process):** executive review completed within 24 hours;
  post-incident review delivered; treated flag set on the account.

#### T5 — P1 pain: RETIRED before go-live

- **Exact rule as built:** `p1_tickets_12m >= 1` — at least one P1 ticket in
  12 months.
- **Status: RETIRED.** This trigger fires on 48% of the book at roughly
  base-rate precision (12.5% test vs 14.3% train). In plain language: half
  the book has had a P1 ticket at some point in a year. That is a fact about
  support load, not a churn signal. Shipping it would page a human for
  nearly every other account — the catalog's 66.5% union fire rate is almost
  entirely this trigger's doing.
- **What happens to its signal:** it stays in the model as a feature, where
  it contributes honestly to the score. It does not create tasks, pages, or
  SLA clocks.
- **Path back (if ever):** narrow it until it means something — multiple P1s
  without a completed post-incident review, for example — then re-prove
  precision on fresh data. Not this quarter.

### CSM triggers

#### T1 — Usage-decay cliff: LIVE

- **Exact rule:** `usage_decay_90d <= 0.803` — 90-day usage at or below
  about 80% of the account's own baseline.
- **Plain language:** usage fell off a cliff. The account's teams stopped
  using the product — or stopped using it the way they used to. This is the
  highest-volume trigger (22% of the book), which is a feature, not a bug:
  usage decay is the most common early shape of churn.
- **Owner:** CSM.
- **SLA:** outreach within 2 business days.
- **Test read:** 12.5% precision — below the 2× go-live bar, so it ships
  gated (score feature + worklist ordering; pages a human after the pilot
  promotes it). Median lead-time proxy 171.5 days to renewal: the runway is
  long, which is exactly why the outreach clock is short — you are catching
  it early.
- **On the call:** "I am seeing a sharp drop in usage over the last 90
  days. Something changed on your side — a reorg, a champion leaving, a
  competing tool? I want to understand it before it becomes a renewal
  conversation." Diagnose the cause; the cause picks the playbook.
- **Success metric (process):** outreach completed within 2 business days;
  cause of decay identified and logged; treated flag set.

#### T3 — Champion login gap: LIVE

- **Exact rule:** `champion_logins_30d <= 0` — the recorded champion has not
  logged in for 30 days.
- **Plain language:** your person went dark. In B2B, churn usually walks out
  through the champion's door first — they stop logging in months before the
  contract conversation.
- **Owner:** CSM.
- **SLA:** champion check-in within 5 business days.
- **Test read:** 13.0% precision — gated until the pilot promotes it.
  Median lead-time proxy 209 days: the longest runway in the catalog, and
  the reason this trigger is worth working even at modest precision.
- **On the call:** this one is detective work, not a pitch. "I have not seen
  [champion] in the product for a month — everything okay on their end? Is
  there someone else I should be working with?" If the champion left, you
  are re-onboarding. If they are still there but disengaged, you are
  re-selling. Either way, multi-thread now.
- **Success metric (process):** champion status confirmed (still in role /
  left / disengaged) and logged within 5 business days; multi-threading
  started if the champion is gone; treated flag set.

#### T7 — Dark account + decay: LIVE

- **Exact rule:** `has_valid_survey == 0 AND usage_decay_90d <= 0.715` — no
  valid survey response AND 90-day usage at or below ~71% of baseline.
- **Plain language:** the account is silent and shrinking. It never answered
  a survey — remember, non-respondents churn at 15.3% versus 9.9% for
  respondents — and the usage we can see is decaying. The blind spot is
  where the risk concentrates.
- **Owner:** CSM.
- **SLA:** discovery call within 5 business days.
- **Test read:** 19.1% precision — the strongest of the gated triggers, and
  the pilot's most valuable read: if "dark + decaying" beats the base rate
  on realized churn over two quarters, the nonresponse story graduates from
  modeling feature to operating trigger.
- **On the call:** you are starting from zero relationship data, so this is
  pure discovery. "I want to make sure we are set up right for your team —
  can we spend 30 minutes on how you are using us today?" Do not mention
  the survey; do not mention the model.
- **Success metric (process):** discovery call completed within 5 business
  days; account contact map established and logged; treated flag set.

#### T2 — Active-user-ratio cliff: RETIRED before go-live

- **Exact rule as built:** `active_user_ratio <= 0.084`.
- **Status: RETIRED.** This is the catalog's honest failure: 28.4%
  precision on training data, 6.3% on the test set. The threshold was tuned
  on a 4%-of-book slice and did not transfer — a textbook overfit, caught
  by the holdout and shipped as a failure rather than buried.
- **What happens to its signal:** active-user ratio stays in the model as a
  feature. The rule does not create tasks.
- **Path back (if ever):** a threshold re-derived on longitudinal data with
  stability checks, or a rule that combines the ratio with a second
  signal. Not this quarter.

---

## The playbook library: 9 segments, 9 plays

A trigger tells you *that* an account needs attention and *who* acts. The
playbook library tells you *what to do*. Every account sits in exactly one
of nine lifecycle segments — tenure (<2y / 2–5y / >5y) by portfolio breadth
(1 product / 2–4 / 5+) — and each segment has one distinct playbook. The
routing rule is simple: **when a trigger fires, find the account's segment
and open the matching playbook.**

One important note on what segments are and are not. The modeling experiment
tested per-segment models and they *lost* to one global model with segment
interactions (pooled per-segment AUC 0.7438 vs 0.8099). So segments do not
change the score and do not change your list. They change the conversation.
The segment is the operating map; the score is the ranking. Keep the map,
drop the fitting.

| # | Segment (tenure × breadth) | The playbook | When to reach for it |
|---|---|---|---|
| 1 | New (<2y), single product | **Fast-start adoption:** champion enablement + first-90-day usage milestones; CSM owns onboarding health. | T1 or T3 fires on a new logo. The risk is failed onboarding — re-run the first 90 days, do not "check in." |
| 2 | New (<2y), 2–4 products | **Portfolio anchoring:** cross-product value review to make the second product sticky; exec sponsor intro. | T1/T7 on a new multi-product account. The second product is the one that dies first; anchor it. |
| 3 | New (<2y), 5+ products | **Complexity taming:** value-realization audit across products; consolidate or rationalize shelfware. | Any trigger on a broad new account. They bought too much, too fast. Help them shrink to what works. |
| 4 | Mid (2–5y), single product | **Land-and-expand:** add-a-product motion with ROI proof from the hero product; champion multi-threading. | T6 fires here — a downgrade on a single-product account is an existential signal. Expand or lose. |
| 5 | Mid (2–5y), 2–4 products | **Exec QBR:** business-outcome review + expansion roadmap; pricing/term optimization ahead of renewal. | T8's natural home. Renewal under pressure with mid-tenure breadth: run the business review early. |
| 6 | Mid (2–5y), 5+ products | **Strategic renewal:** multi-year term lock with committed expansion; renewal 180 days out. | T8 on a broad mid-tenure account. Lock the term before the renewal becomes a renegotiation. |
| 7 | Long (>5y), single product | **Loyalty + modernization:** exec sponsorship + roadmap briefing; defend against rip-and-replace. | T3 on a tenured single-product account — a silent champion after five years smells like an evaluation of your replacement. |
| 8 | Long (>5y), 2–4 products | **Enterprise success plan:** joint innovation backlog; usage-depth expansion in owned products. | T4 on a tenured account — four escalations after five good years is a relationship to save, not a ticket queue to clear. |
| 9 | Long (>5y), 5+ products | **Strategic partnership:** co-innovation / advisory board seat; portfolio-wide ELA discussion. | Any trigger on the broadest tenured accounts. These are partnership conversations, not save motions. |

Where churn concentrates in the operating map (measured, train frame):
mid-tenure single-product accounts carry the most churners (64 train / 14
test), followed by new single-product (35 / 8) and mid-tenure 2–4 product
(26 / 7). If you have to choose which segment playbooks to learn first,
learn 4, 1, and 5 — in that order.

---

## Capacity bands: what K=20, K=40, K=60 means for your week

The list size is a capacity decision, not a model decision. K=40 is the
illustrative default — 40 accounts, about 10% of the evaluation book. All
three bands below are measured on the same evaluation frame; none of them
assumes a save rate or invents headcount.

| Band | Accounts | Churners caught | Precision | Actual ARR captured | What it means operationally |
|---|---|---|---|---|---|
| K=20 (lean) | 20 | 5 | 0.25 | $14.99M | Half the effort of the default, 76% of its dollars. Use when the team is at capacity or the book is small. Expected $13.54M vs actual $14.99M — the expectation holds. |
| K=40 (default) | 40 | 11 | 0.275 | $19.65M | The recommended starting point: 11 churners, $19.65M actual vs $19.20M expected. Covers the sharp triggers (T8, T4) fully and the gated ones partially. |
| K=60 (full-court) | 60 | 13 | 0.217 | $20.91M | The extra 20 accounts buy 2 more churners and $1.26M of captured ARR. Use ahead of renewal season or with a dedicated retention motion. Diminishing returns are visible and honest. |

Three rules for working the bands. **One:** start at 40; flex down to 20
when capacity is tight rather than working 40 badly. **Two:** never invent
the band from headcount math — the bands are measured coverage on one
evaluation frame, and real-book coverage will differ; the shadow pilot
re-measures them. **Three:** the ordering inside every band is the same —
expected dollars at risk, top down. A lean band does not re-rank; it just
stops earlier.

---

## Guardrails: the honesty rules you operate under

These are not footnotes. They are the rules that keep the system honest, and
breaking them is how good analytics becomes bad operations.

1. **No assumed save rates in the money math.** The causal analysis found no
   measured evidence that any existing motion moves churn — the estimated
   effect's confidence interval spans zero. So the dollars on your list are
   *exposure*, never *forecast savings*. Never multiply expected ARR at risk
   by an assumed save rate. If someone asks "how much will we save," the
   answer is "we do not know yet; that is what the pilot measures."
2. **The list is expected exposure, ranked.** "Calibrated p × ARR — the
   dollars are real because the Brier score went 0.1095 to 0.0905." Expected
   $19.20M vs actual $19.65M on the evaluation frame is the receipt. But an
   expectation is not a promise on any single account.
3. **Log every action with a treated flag and a timestamp.** This is the
   anti-contamination discipline: if you save an account, the pilot must be
   able to tell it was saved *by you*, so the trigger's measured precision
   is not polluted by your own work. Act first, log immediately after.
4. **Cross-sell is a separate motion.** The white-space analysis found real
   cross-sell opportunity, but it is a different decision (what to sell
   next) from this system's decision (who is about to leave). Do not bolt a
   cross-sell pitch onto a save call; the two motions have different owners
   and different success metrics.
5. **Freshness is the system's oxygen.** The triggers assume telemetry no
   older than 7 days, support data no older than 1 day, ARR no older than 30
   days, and survey data no older than 90 days. If the data feeding your
   list is stale, the list is stale — escalate to RevOps, do not work a
   stale list harder.
6. **Retired means retired.** T2 and T5 do not create tasks, do not page,
   and do not appear in your queue. Their signals live in the score. If you
   see an account that "would have fired T5," that is the model already
   knowing — trust the ranking.

---

## Limitations: what this system does not do

Read this section before you defend the system to anyone. Every limitation
below is stated in the underlying artifacts; none is new.

1. **The data is synthetic.** The generator is known, which means the
   separation you see here will be lower on real data. Absolute numbers —
   precision, dollars captured, trigger hit rates — are not production
   forecasts. They are the shape of the system, not its scale.
2. **There are no causal estimates.** No measured motion has been shown to
   move churn. Every playbook in this manual is a structured best practice
   with a treated-flag log, not a proven intervention. The pilot exists to
   change that sentence.
3. **The 11-vs-16 trade-off is real.** The calibrated, trigger-routed list
   catches fewer churners (11) than the uncalibrated baseline (16) but
   roughly twice the dollars ($19.65M vs $9.85M). If the business ever
   decides it wants churner count over dollars, the ranking changes — say so
   out loud before switching.
4. **One 90-day window, one snapshot.** Lead time is proxied by
   days-to-renewal at firing, not measured as days from firing to the churn
   event. T8's 50-day median runway is a renewal-calendar fact, not a
   measured warning window. Trigger stability — whether a trigger flaps on
   and off week to week — is unmeasurable on a single snapshot.
5. **T2 and T5 are retired.** They shipped as documented failures. The
   catalog's honesty depends on the retirement being real, not cosmetic.
6. **The trigger union fires on 66.5% of accounts — before retirement.**
   Almost all of that is T5's 48% fire rate. Retiring T5 is what turns the
   "gate" from a slogan into a gate. After retirement, the union is the six
   live triggers, and the pilot re-measures the real coverage.
7. **Involuntary churn is unseparated.** There are no churn reason codes, so
   all churn is treated as voluntary. Some of what the triggers flag will be
   bankruptcies, acquisitions, and non-payment — accounts no playbook can
   save. The win-back path for those is a different motion.
8. **What breaks first is telemetry freshness.** The system's first failure
   mode is stale usage data, then alert fatigue if retired triggers are
   ever re-enabled without re-proof, then threshold drift as the book
   changes. The drift monitors (input PSI, score drift, decay gates) exist
   for exactly this.
9. **The gate has a known cost.** One $1.04M churner was screened out
   because it fired no trigger. Gating trades a small, known miss for a
   much more actionable list. That trade is disclosed, not hidden.
10. **Thresholds are train-chosen; the evaluation frame is one split.**
    Every threshold was chosen on training data only, which is the right
    discipline — but it also means the test-frame numbers are one draw. The
    two-quarter shadow pilot is the second draw, on real data, and it is
    the one that decides what graduates.

---

## The ask: what the pilot needs

The system is ready for shadow mode, not for autonomous action. The pilot
runs two quarters: every Monday the triggers score the book, the firings are
logged and blinded (CSMs work their normal process), and 90 days later each
firing is joined to realized churn. What graduates is decided by gates, not
by opinion.

**Graduation gates (all must hold at the 6-month review):** per-trigger
empirical precision at or above 2× the base churn rate (23.7% on an 11.85%
base), sustained across both quarters; median measured lead time of at least
30 days; firing stability of at least 60% (still flagged four weeks later);
alert volume at or below 15% of the CSM book per week per trigger family.
Triggers that pass graduate to trigger-routed outreach — firing creates a
task for the catalog owner on the catalog SLA. Triggers that fail on
precision go to model-feature duty only. Triggers that fail on stability get
rebuilt or retired.

**What the pilot needs from the business:**

- **Data engineering:** the weekly snapshot store — per-account usage,
  champion activity, support events, contract events, and survey refreshes
  snapshotted every Sunday, with the freshness SLAs above. Six months of
  backfill before the pilot starts.
- **RevOps:** ownership of the blinded shadow log, the 90-day outcome join,
  the per-trigger precision/lead-time/stability read, and the weekly
  per-book volume caps.
- **CSM leadership:** one pod working the gated triggers normally with
  treated-flag discipline, so the pilot measures the system against a real
  operating motion — and agreement that no trigger pages a human until it
  passes the gates.

That is the whole manual. The list tells you who is at risk and in what
order. The triggers tell you what changed. The owners and SLAs tell you who
acts and how fast. The playbooks tell you what to do. The guardrails tell
you what not to claim. Work the list top-down, act within your SLA, and log
everything.
