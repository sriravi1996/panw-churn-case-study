# Phase 3 Tournament — Judging Report (part3_01 … part3_15)

**Judge:** Phase 3 judging subagent (deep-analysis role). **Date:** 2026-10-10.
**Deliverable:** this file, `approaches/part3_TOURNAMENT.md`.

## 1. Header — what was read

For each of the 15 Phase 3 documentation iterations, all five files were read
in full: `approach.md` (thesis), `README.md` (the document), `slides.md`
(the 12-slide outline), `traceability.md` (the claim→artifact map), and
`checklist.md` (the 10-question VP drill). Background was read first, in
order: `approaches/PHASE3_SPEC.md` (§4 judging procedure), then
`approaches/part1_TOURNAMENT.md` and `approaches/part2_TOURNAMENT.md`
(the ground truth). Every iteration was spot-checked on ≥5 numbers, resolved
through its `traceability.md` to the actual artifacts
(`part1_07/` substrate, `part2_07/metrics.json` + `trigger_catalog.csv` +
`shadow_pilot.md`, `part2_01/metrics.json`, `part2_13/ops_runbook.md`, or the
tournament verdicts for red-team/falsification claims — the citation path
the spec sanctions). Several numbers were additionally re-verified by
script against the raw artifacts (account rows in `modeling_table.csv`,
trigger firings recomputed, the p2_13 trigger-boost head-to-head, the
trigger_stats.json diagnostics, the survey fraud counts). Slide outlines
were checked for 12 slides, full-sentence TLDR headlines, all-three-parts
coverage, a closing ask, and figure existence on disk
(`part3_05/figures/` — 6 PNGs verified; `part3_12/metric_tree.png` —
verified as a real 2400×1740 generated figure, all quantitative nodes
matching artifacts).

Ground truth used throughout (verified by script 2026-10-10; the old
3,000-account / 12.8% / $117M canonical figures were treated as banned):
Phase 1 winner **part1_07** (2,000 rows × 47 cols; `churned` = SentinelShield
90-day cancellation, 11.85% / 237; $1,975.1M total ARR; SentinelShield
$1,161.6M / 58.8%; respondents 9.9% vs non-respondents 15.3% churn).
Phase 2 winner **part2_07** (trigger-gated worklist, K=40: 11 churners,
precision 0.275, recall 0.234, $19.20M expected / $19.65M actual, on the
400-row / 47-churner test frame; Brier 0.1095 → 0.0905; AUC 0.8092;
PR-AUC 0.3515; union alert rate 66.5% / 266; T8 test precision 43.5% /
10 of 23, median 50-day runway; T2 test precision 6.3% and T5 48% fire
rate shipped as failures). Canonical reference **part2_01** (K=40:
10 churners, $19.46M expected / $18.56M actual; uncalibrated baseline
16 churners / $9.85M; Brier **0.1065** → 0.0905 — note the 0.1065, which
recurs below). Adopted elements: p2_13 ops wrapper (freshness SLAs
telemetry ≤7d / support ≤1d / contract 30d / survey 90d; go-live gate
trigger precision ≥ 2× base = 23.7%), p2_07 shadow-pilot gates
(1.5× precision sustained, ≥30d lead time, ≤15% weekly volume, ≥60%
stability), p2_08 gatekeeper policy (ATE −0.0089, 95% CI [−0.0271,
0.0075] spans zero — no treatment-effect dollar enters money math),
p2_05 9-segment → 9-playbook map, p2_10 cross-sell white-space
($952.3M gross) as a separate motion.

## 2. Rubric recap

Seven dimensions, 1–5 each, /35 total: narrative clarity, VP-defensibility,
completeness across all three parts, honesty about limitations, usability
as a presentation aid, traceability discipline, freshness of take.
Calibration anchor: the canonical README form anchors 4/5 on dimensions
1–6 and 1/5 on freshness — an iteration that merely rewords the tournament
facts without a fresh take loses on freshness regardless of polish.
Red-team rule: ≥5 numbers per iteration resolved through traceability to
artifacts; 1 unresolved number caps defensibility at 2/5; 2 unresolved
fails the iteration. Honest-claims rule: one confirmed violation (phantom
number, invented capacity, unlabeled forecast, treatment-effect money math
without caveats, old-canonical numbers presented as current) caps honesty
at 2/5. **No iteration triggered either cap.** The defects found are wrong
derivations and misattributions of real, resolving numbers — scored as
traceability/honesty 4s, not violations. Tiebreak: the iteration Ravi would
most want in the room — the one that makes him hardest to surprise.

## 3. Score table (/35)

| Iter | Angle | n | d | c | h | u | t | f | Total |
|---|---|---|---|---|---|---|---|---|---|
| part3_01 | Executive story (BLUF) | 5 | 5 | 5 | 5 | 5 | 5 | 4 | **34** |
| part3_02 | Methods deep-dive | 5 | 5 | 5 | 5 | 4 | 5 | 5 | **34** |
| part3_03 | Question-driven | 5 | 5 | 5 | 5 | 5 | 5 | 5 | **35** |
| part3_04 | Decision memo | 5 | 5 | 5 | 4 | 5 | 4 | 5 | **33** |
| part3_05 | Visual-first | 5 | 5 | 4 | 4 | 5 | 5 | 5 | **33** |
| part3_06 | Risk-led | 5 | 5 | 5 | 5 | 4 | 5 | 5 | **34** |
| part3_07 | Playbook (CSM manual) | 5 | 5 | 5 | 5 | 5 | 5 | 5 | **35** |
| part3_08 | Before/after | 5 | 4 | 5 | 4 | 5 | 5 | 5 | **34** |
| part3_09 | Diary | 5 | 4 | 5 | 5 | 4 | 4 | 5 | **32** |
| part3_10 | FAQ / defense drill | 5 | 4 | 5 | 5 | 5 | 4 | 5 | **33** |
| part3_11 | One-pager + appendices | 5 | 4 | 5 | 4 | 5 | 4 | 5 | **32** |
| part3_12 | Metric tree | 5 | 4 | 5 | 4 | 5 | 5 | 5 | **33** |
| part3_13 | Account stories | 5 | 4 | 4 | 5 | 5 | 5 | 5 | **34** |
| part3_14 | Refresh-and-ops | 5 | 4 | 5 | 4 | 5 | 5 | 5 | **34** |
| part3_15 | Contrarian | 5 | 5 | 5 | 4 | 5 | 5 | 5 | **34** |

Dims: n = narrative clarity, d = VP-defensibility, c = completeness,
h = honesty, u = usability, t = traceability, f = freshness.

## 4. Scorecards

### part3_01 — Executive story (BLUF-first) — 34/35
- **Thesis:** retention is where-and-when, not who; money at risk → owner → caveats; the document ends in a decision (shadow pilot + parameterized worklist + staffing).
- **Strongest:** narrative clarity (BLUF in the first 200 words; failure-front-loading).
- **Weakest:** freshness (BLUF-first is distinct but closest to a canonical exec summary).
- **Red-team:** 5/5 resolved ($19.65M/11, T8 43.5%, $1,975.1M, 15.3%/9.9%, 16/$9.85M). Minor: "4× the strength" for 0.22/0.06 = 3.7×, unlabeled derivation — defensible rounding.
- **Verdict note:** the cleanest conventional executive read; loses the top tier only on freshness.

### part3_02 — Methods-first technical deep-dive — 34/35
- **Thesis:** every modeling choice = decision + alternative + justifying number + disclosed trade-off; EDA as feature-validation evidence; falsifications first-class.
- **Strongest:** VP-defensibility (decision tables; the $49T bug as process lesson).
- **Weakest:** usability as a VP walk-in aid (a DS-peer's record; the VP would need the slides).
- **Red-team:** 5/5 resolved (both Briers, CV PR-AUCs from cv_results.json, the banned $49T cited as banned, p2_01 K=60 sensitivity 14/$21.95M).
- **Verdict note:** the strongest technical record; not the presentation.

### part3_03 — Question-driven — 35/35
- **Thesis:** the TOC is the analysis — 8 sub-questions; every claim adjacent to its citation; limitations asked as questions inline.
- **Strongest:** usability (best-in-class findability; questions as navigation).
- **Weakest:** none material (checklist Q3 answers with p2_01 dollars where the trigger-system dollars were the tighter answer — phrasing, not falsehood).
- **Red-team:** 5/5 resolved (T8 43.5%/10/23, h2h 11/$19.65M vs 9/$17.48M, PostureLens 704/$166.1M, ATE CI, cross-sell worklist 10/$17.90M). Brier correctly attributed to part2_07 in the explicit statement.
- **Verdict note:** defect-free; the best reference document. Runner-up.

### part3_04 — Decision memo — 33/35
- **Thesis:** a decision instrument, not a report — page 1 is THE DECISION REQUESTED with a GO / GO-WITH-CONDITIONS / DEFER block and signature line.
- **Strongest:** narrative/usability (the decision-instrument form).
- **Weakest:** traceability — **4 of 9 segment→playbook pairings are wrong vs p2_05/metrics.json** (new/mid-breadth ↔ mid/single swapped; mid/broad ↔ long/single swapped). Hedged as a "working draft" but asserted as the map's pairing; a wrong derivation from the artifact.
- **Red-team:** 5/5 numbers resolve; the pairing defect is the finding.
- **Verdict note:** the best decision form, damaged by the one factual defect that matters most to its own thesis (the map it asks the VP to bless).

### part3_05 — Visual-first — 33/35
- **Thesis:** one flagship figure per major claim; the deck is the README's summary and the README is the deck's speaker notes; `gen_figures.py` generates from artifact inputs only.
- **Strongest:** usability/freshness (6 verified figures on disk; captions carry the argument).
- **Weakest:** completeness (cross-sell/affinity thin) and honesty — two slips: "+55% lift over the 11.85% base" (the +55% is vs respondents, not vs base); freshness SLAs 24h/4h attributed to "p2_13" when they come from `shadow_pilot.md` (the runbook says 7d/1d).
- **Red-team:** 5/5 numbers resolve (attribution slips, not phantoms).
- **Verdict note:** the best figures; the prose needs an attribution pass.

### part3_06 — Risk-and-limitations-led — 34/35
- **Thesis:** the limitations are the spine — an 11-item honest inventory (incl. part1_07's undisclosed null and the G6 baseline drift), then labeled "we expect… because…" judgment pairs; recommendations = what can responsibly be claimed.
- **Strongest:** honesty (exemplary: G6 drift disclosed with canonical-only comparisons; both SLA standards attributed to the correct documents).
- **Weakest:** usability (risk-first is armor, not a walk-in case).
- **Red-team:** 5/5 resolved (sensitivity deltas, T5 24/192, the 2× gate, robustness cuts +0.0825/−0.0505).
- **Verdict note:** the most honest document; the presentation would need a narrative spine grafted on.

### part3_07 — Playbook: the CSM operator's manual — 35/35 ⭐ WINNER
- **Thesis:** the trigger catalog is an operating contract; success = adoption by operators. Monday-morning actionable: per-trigger rule/threshold/owner/SLA/plain-language/what-to-say/success-metric; the 9-playbook library; capacity bands; guardrails as operating rules.
- **Strongest:** usability (the manual a CSM could actually work Monday) — and traceability (all 9 segment→playbook pairings verified correct vs p2_05/metrics.json; the 2× bar correctly stated as cleared by **both** T8 43.5% and T4 30.0%).
- **Weakest:** none material (Slide 1's title doubles as the TLDR sentence without an explicit "TLDR:" prefix — a formatting nit for the deck build).
- **Red-team:** 5/5 resolved (segment churn counts 64/14, 35/8, 26/7; all 9 pairings; 76% = $14.99M/$19.65M; 23.7% gate; the 6 swaps).
- **Verdict note:** defect-free, and the only iteration that answers the question that kills case-study presentations: "will anyone actually use this?"

### part3_08 — Before/after (incumbent vs new system) — 34/35
- **Thesis:** one sustained head-to-head on the same 400-account frame; every modeling choice staged as before/after; the "after" not triumphalist; plus a reusable comparison protocol (same frame, same K, three numbers, disclose exclusions both ways, expected-vs-actual calibration check) — genuinely useful machinery.
- **Strongest:** narrative (the protocol as reusable machinery) and usability.
- **Weakest:** honesty/defensibility — the calibration paragraph blends p2_07's Brier (0.1095→0.0905, 17%) with p2_01's dollar pair ($19.46M/$18.56M) in one sentence; the traceability map documents both Briers correctly, but the prose implies they belong together.
- **Red-team:** 4/5 clean + the Brier-blend looseness.
- **Verdict note:** the best argumentative machinery; its comparison protocol is adopted into the winner (see §5).

### part3_09 — Diary / lab notebook — 32/35
- **Thesis:** told in the order it happened; dead ends as main text; each pivot names what was learned; "import the canonical reference" as a block-letter operating rule.
- **Strongest:** narrative (the what-was-learned entries).
- **Weakest:** traceability — Entry 4 and Slide 4 attribute p2_07's scorer numbers (Brier 0.1095→0.0905, AUC 0.8092, PR-AUC 0.3515) to "the reference (p2_01)"; p2_01's are 0.1065→0.0905 / 0.8040 / 0.3483. The map cites part2_07 correctly; the prose mislabels.
- **Red-team:** 4/5 clean + the misattribution.
- **Verdict note:** the most readable discovery story; the mislabeled Brier/AUC/PR-AUC trio is exactly the kind of thing a sharp reviewer catches.

### part3_10 — FAQ / defense drill — 33/35
- **Thesis:** 20 questions by part, each answered "number, source, caveat" plus a generalizing principle; adversarial completeness (10 least-wanted questions, incl. the vacationing AE and hire-more-CSMs).
- **Strongest:** usability (the night-before drill; quotable answers).
- **Weakest:** traceability — the narrative spine writes "(part2_01: … Brier 0.1095 → 0.0905)"; p2_01's Brier is 0.1065→0.0905. Same misattribution class as part3_09.
- **Red-team:** 4/5 clean + the misattribution. (Its falsification inline citations to raw metrics.json files are loose but the numbers are verifiable via the sanctioned tournament-doc path.)
- **Verdict note:** the best adversarial coverage; one label fix away from the top tier.

### part3_11 — One-pager + appendices — 32/35
- **Thesis:** extreme concision with zero loss of verifiability — page 1 carries the whole case (~700 words, six numbers, the ask); every claim carries an appendix anchor (A/B/C/D); the chain is one-pager → appendix → artifact → exact key.
- **Strongest:** usability (the best 3-minute read in the tournament).
- **Weakest:** traceability — (1) Brier 0.1095→0.0905 attributed to "the canonical reference scorer" in approach.md, the one-pager, and B.1 (p2_01's is 0.1065→0.0905); the traceability map's row 42 explicitly documents the choice ("uses the p2_07 calibrator read"), so it is documented-but-mislabeled, not phantom; (2) freshness SLAs 24h/4h attributed to p2_13's runbook instead of `shadow_pilot.md`.
- **Red-team:** 5 numbers resolve (the Brier choice is owned in the map).
- **Verdict note:** the best information density; needs the same attribution pass as part3_05.

### part3_12 — Metric-tree framing — 33/35
- **Thesis:** every model number answers "which business metric does it move?" — GRR/NRR/loyalty decomposed to model metrics, built as a real figure (`metric_tree.png`, 2400×1740, spec'd in README §2, every quantitative node matching an artifact).
- **Strongest:** freshness/usability (the only metric tree; the figure is a genuine one-picture summary).
- **Weakest:** honesty — Slide 7's TLDR says T8 "catches 43.5% of churners": 43.5% is **precision** (10/23), not recall (10/47 = 21.3%). A factual error in the most visible line of the slide.
- **Red-team:** 4/5 clean + the headline error (plus loose Brier attribution in §4b; the spec table itself is correct).
- **Verdict note:** the figure is adopted into the winner's deck with the headline corrected (see §6).

### part3_13 — Account stories — 34/35
- **Thesis:** the system at the only grain the business works — three REAL rows of the modeling table walked through the full pipeline (SAVE: ACC-00528, T8/T4, $2.60M, 55d; DECAY: ACC-00833, T1/T6, $1.24M, 275d; CONTRAST: ACC-00955, T5-only, $2.845M healthy).
- **Strongest:** usability/traceability — `select_accounts.py` reproduces the derivation; all three accounts verified by script as real rows with exactly the stated trigger firings (T4/T5/T8; T1/T5/T6; T5-only), train-Q25 = −0.3756 reproduced, all in the test frame.
- **Weakest:** completeness — the task's required cross-sell derivation (association rules on holdings) was not attempted; ACC-00955's cross-sell routing is asserted narratively. (The old-canonical paths don't exist, so full compliance was impossible; still a gap.) Minor: "test median ARR $789k" vs $778.5k actual.
- **Red-team:** 4/5 fully verified + the minor median discrepancy.
- **Verdict note:** the most human-readable proof of operability; its three accounts are adopted as the winner's deck proof points.

### part3_14 — Refresh-and-ops — 34/35
- **Thesis:** a churn model that cannot be deployed, monitored, and shut off safely is a liability — deployment architecture leads; the ONLY iteration that names and resolves the conflicts between `shadow_pilot.md` and the p2_13 runbook (freshness strictness, 2× vs 1.5× graduation, timezone, the trigger boost, the two trigger sets).
- **Strongest:** freshness (the reconciliation is genuinely novel) and traceability — the only iteration to attribute the freshness SLAs correctly to the runbook (7d/1d/30d/90d).
- **Weakest:** honesty — §1.1/§1.2 prose labels T4 as "(downgrade)" twice; T4 is the escalation-burst trigger, T6 is the downgrade trigger. The §1.4 table is correct; the prose slips.
- **Red-team:** 5/5 resolve (trigger boost 9 vs 11 / $18.68M vs $20.27M; renewal_imminent 19.6% / escalation_burst 87.3%; fraud 129/133/30/40; involuntary proxy 33/237).
- **Verdict note:** the best ops document; its pre-launch checklist is adopted into the winner's deck with the T4 label fixed.

### part3_15 — Contrarian — 34/35
- **Thesis:** the red-team's document — the 8 strongest honest attacks on the winner at full strength, 10 killed alternatives steelmanned fairly (appeal + kill disclosed in the same paragraph), landing in a verdict with teeth: the winner survives **in a reduced, conditional form** (six triggers, dollar-override, no treatment-effect dollars, 2× graduation, never reimplement the reference).
- **Strongest:** freshness/defensibility (the dollar-override for the screened-out $1.04M churner is a genuine design improvement; the G6 lesson as an operating rule).
- **Weakest:** honesty — "T8 is the only trigger whose precision clears 2× the base rate on holdout" is wrong: T4's 30.0% ≥ 23.7% also clears. (Also in the slides.)
- **Red-team:** 4/5 clean + the exclusivity error. New claims verified: ACC-01909 is indeed a churner; the G6 baseline numbers; Attack 3's "225 gross alerts ex-T5" arithmetic (88+16+23+20+34+21+23).
- **Verdict note:** the best adversarial armor; its 8-attack brief and the dollar-override condition are adopted into the winner.

## 5. Combination verdict — documented adoption (not prose stitching)

These are documents, not builds; the winner does not need rewriting, it needs
specific elements grafted in. The combination is **documented adoption** of
six elements from five runners-up, each with its placement and its defect
carried or fixed:

1. **From part3_08 — the comparison protocol.** Adopt as the deck's "how we
   compare" slide and as the standing rule for any alternative the VP
   proposes: same frame, same K, three numbers (churners, expected $,
   actual $), disclose exclusions both ways, expected-vs-actual calibration
   check. This is the machinery that makes Ravi hardest to surprise on
   "why not X?" — any counter-proposal gets run through the protocol.
2. **From part3_03 — the question-driven Q&A appendix.** Adopt the 10
   canonical questions as the appendix navigation for night-before prep.
   (Its checklist Q3 should use the trigger-system dollars, $19.65M vs
   $9.85M, as the primary answer.)
3. **From part3_12 — the metric-tree figure.** Adopt `metric_tree.png` as
   the deck's "one picture" slide, with the Slide 7 headline **corrected**
   to "T8 hits 43.5% precision (10 of 23 flagged accounts churned) with a
   median 50-day renewal runway" — never "catches 43.5% of churners."
4. **From part3_14 — the pre-launch checklist.** Adopt the 8-gate checklist
   as the deck's ops slide, with the T4 "(downgrade)" prose slip corrected
   to "(escalation burst)."
5. **From part3_15 — the red-team brief + the dollar-override.** Adopt the
   8 attacks as the Q&A armor appendix, and the dollar-override condition
   (any account above a Finance-set materiality threshold bypasses the
   trigger gate into human review — the $1.04M screened-out churner is the
   reason) as a stated condition in the ask. Correct the "only trigger
   clearing 2×" claim to "T8 (43.5%) and T4 (30.0%)."
6. **From part3_13 — the three account stories.** Adopt ACC-00528
   (SAVE), ACC-00833 (DECAY), ACC-00955 (CONTRAST) — all verified real
   rows with reproduced trigger firings — as the deck's operator-legibility
   proof (one slide per account, or an appendix; the deck builder decides
   placement).

What is NOT adopted and why: part3_04's decision-memo form (its signature
block is nice, but its playbook pairings are wrong — do not import the
pairing table); part3_05's figures (good, but the deck already has the
metric-tree figure and the account stories — more figures dilute);
part3_09's diary and part3_10's FAQ (their Brier misattributions must not
propagate); part3_11's one-pager (excellent density, but the winner's
manual format is the chosen spine — the one-pager's anchor discipline is
commended, not imported).

## 6. Winner declaration — part3_07 (Playbook: the CSM operator's manual)

**Why it wins.** The tournament's ground truth is that the system won on
dollars and rigor; the presentation's ground truth is that a system nobody
operates is slideware. part3_07 is the only iteration whose thesis is the
last mile: the trigger catalog as an operating contract, success defined
as adoption by operators. It is defect-free (5/5 red-team clean, all 9
playbook pairings verified correct against p2_05/metrics.json — the one
iteration besides the artifacts themselves to get them right, where
part3_04 got 4 of 9 wrong), it covers all three parts, its 12 slides carry
full-sentence TLDR headlines and end with the ask, and its traceability
map is the most careful in the tournament (it correctly distinguishes
p2_07's Brier 0.1095→0.0905 from p2_01's 0.1065→0.0905, and correctly states
that both T8 and T4 clear the 2× bar — distinctions that tripped six other
iterations).

**Criterion-by-criterion where it matters.**
- *Narrative (5):* "the manual, not the model, is the deliverable" is the
  strongest substantive thesis in the tournament — a claim about what
  success means, not a structural gimmick.
- *VP-defensibility (5):* every number resolves; the honesty ledger is
  explicit; the 6-swap disclosure and the $1.04M screened-out churner are
  stated, not buried.
- *Completeness (5):* all three parts, the 9-playbook library, capacity
  bands, guardrails as operating rules, explicit limitations.
- *Honesty (5):* no invented per-account anything; T2/T5 as retired
  failures; the gatekeeper policy as a standing rule.
- *Usability (5):* the manual a CSM could work Monday morning — per-trigger
  rule/threshold/owner/SLA/plain-language/what-to-say/success-metric.
- *Traceability (5):* the best map in the tournament (see above).
- *Freshness (5):* the only operator's manual; a genuinely different
  document, not a rewording.

**Tiebreak.** Two iterations scored a clean 35/35: part3_03 (question-driven)
and part3_07 (playbook). (part3_08 reached 34 after its Brier-blend
looseness.) Between the two clean 35s, the tiebreak — the iteration
Ravi would most want in the room — goes to part3_07. part3_03 is the best
reference document (findability as armor), but in the room Ravi needs a
story first and armor second; part3_07's thesis answers the question that
kills case-study presentations ("nice model — will anyone use it?") with a
document the operators could actually run, while part3_03's armor is
adopted into the winner's appendix anyway (§5.2).

**Known accepted defects of the winner.** (1) Slide 1's title doubles as
its TLDR headline without an explicit "TLDR:" prefix (other slides use the
prefix) — normalize in the deck build; the title is a complete sentence,
so nothing substantive is missing. (2) The angle is operator-focused by
design; the slide outline already pivots to a VP audience, and the deck
build must preserve that pivot rather than drifting into pure manual.

**One-line why-not per runner-up.**
- part3_03 (35): the best Q&A reference; adopted as the winner's appendix — the winner's operator thesis is the better main narrative.
- part3_08 (34): the best comparison machinery; adopted as the deck's standing protocol — its Brier-blend sentence needs the fix the winner doesn't.
- part3_15 (34): the best adversarial armor; adopted as Q&A appendix + the dollar-override condition — armor supports the narrative, it isn't the narrative.
- part3_14 (34): the best ops doc; its pre-launch checklist is adopted — the winner answers operability at the CSM grain the VP feels directly.
- part3_13 (34): the most human proof of operability; its three accounts are adopted as deck proof points — the winner's manual is the better spine.
- part3_01 (34): the cleanest conventional read; the winner's angle is fresher and more distinctive.
- part3_02 (34): the strongest technical record; a peer doc, not a walk-in presentation aid.
- part3_06 (34): the most honest document; risk-first is armor, not a presentation.
- part3_04 (33): the best decision form — but 4 of 9 playbook pairings are wrong, which is fatal to a memo that asks the VP to bless the map.
- part3_05 (33): the best figures; two attribution slips (the +55% base wording; 24h/4h SLAs misattributed to p2_13).
- part3_10 (33): the best defense drill; the Brier misattribution in the spine.
- part3_12 (33): the best one-picture figure; the Slide 7 headline states precision as recall.
- part3_09 (32): the best discovery story; mislabels p2_07's Brier/AUC/PR-AUC trio as p2_01's in prose and slides.
- part3_11 (32): the best 3-minute read; the Brier misattribution plus the SLA attribution slip.

## 7. Deck-build handoff note

- **Winner id:** `part3_07` — Playbook: the CSM operator's manual
  (`approaches/part3_07/`).
- **Its 12 TLDR headlines (summarized):**
  1. The manual, not the model, is the deliverable.
  2. Part 1 built a foundation the list can stand on: 2,000 accounts, a clean 90-day hero-churn label at 11.85%.
  3. Part 1's survey lesson: never trust what accounts say without checking what they do.
  4. Part 2 built the list in three steps: calibrated score, trigger gate, expected-dollar rank.
  5. The trigger-routed list beats the score-only list on both counts: 11 churners and $19.65M vs 10 and $18.56M.
  6. The calibration story in one comparison: the uncalibrated shortcut catches more churners (16) but half the dollars ($9.85M).
  7. T8 is the star trigger (43.5% precision, 50-day runway) and T2/T5 are retired as documented failures.
  8. The six live triggers route into a 9-playbook library by lifecycle segment, and segments deliberately do not touch the score.
  9. Capacity is a measured band, not a headcount claim: K=20 → $14.99M, K=40 → $19.65M, K=60 → $20.91M.
  10. The honesty ledger: what the data does not support, stated as facts.
  11. Nothing pages a human until the shadow pilot promotes it: two quarters, blinded, with graduation gates.
  12. The ask: fund the two-quarter shadow pilot and the snapshot store behind it.
- **Slide-outline elements to use for the deck rebuild:** part3_07's
  12-slide outline as the spine (normalize Slide 1 with an explicit
  "TLDR:" prefix); insert the adopted elements at these beats —
  `metric_tree.png` (part3_12, headline corrected) as the "one picture"
  after Slide 4; the three account stories (part3_13: ACC-00528, ACC-00833,
  ACC-00955) as operator-legibility proof after Slide 8; the comparison
  protocol (part3_08) as the "how we compare" slide after Slide 6; the
  pre-launch checklist (part3_14, T4 label fixed) as the ops slide after
  Slide 11; the question-driven Q&A (part3_03) and the 8-attack red-team
  brief (part3_15) as appendices; the dollar-override condition
  (part3_15) as a stated condition in the ask (Slide 12).
- **Load-bearing traceability rows for the deck** (all in
  `approaches/part3_07/traceability.md`): base rate 11.85% (237/2,000) →
  `part2_07/metrics.json` `churn_rate`; worklist K=40 (11, 0.275, 0.234,
  $19.20M/$19.65M) → `worklist`; union 66.5% (266/400) →
  `trigger_union_test_alert_rate`; T8 43.5% (10/23), 50-day runway →
  `trigger_catalog.csv` T8 row; 2× go-live bar 23.7% → part2_TOURNAMENT.md
  §4 (adopted p2_13); T8+T4 clear the bar → trigger_catalog.csv
  test_precision column; $1,975.1M / $1,161.6M (58.8%) / PostureLens
  $166.1M → `part1_07/outputs/eda_findings.json`; stated-vs-revealed gap
  null (10.2% vs 10.9% vs 11.85%) → eda_findings.json + part1_TOURNAMENT.md;
  Brier 0.1095→0.0905 → `part2_07/metrics.json` (NOT part2_01's
  0.1065→0.0905 — the deck must keep these distinct); the 6 swaps
  ($4.33M/$3.04M out, $1.09M/$1.71M in, $1.04M screened out) →
  `part2_07/approach.md` Evaluation; ATE CI spans zero → part2_TOURNAMENT.md
  §p2_08 (no treatment-effect dollars anywhere).
- **Known defects the deck must carry (fixed, not propagated):** none
  from the winner itself beyond the Slide 1 "TLDR:" normalization; from
  adopted elements — part3_12's "catches 43.5% of churners" → "hits 43.5%
  precision (10 of 23 flagged)"; part3_14's "T4 (downgrade)" → "T4
  (escalation burst)"; part3_15's "only trigger clearing 2×" → "T8
  (43.5%) and T4 (30.0%)"; part3_03's checklist Q3 → lead with the
  trigger-system dollars. Do NOT import part3_04's pairing table,
  part3_09/10/11's Brier attributions, or part3_05/11's SLA attributions.
