# Tournament Artifact Index

Master map of everything built for the churn case-study tournament, in `approaches/`.
All file sizes/sizes below verified 2026-10-10 ~10:10 PDT. Status meanings: **final** (exists, complete),
**pending** (not written yet).

---

## 1. Phase 1 iterations — part1_01 to part1_15

Each iteration: generate → clean → integrate → eda pipeline producing a modeling table plus
`approach.md` (design doc) and summary JSONs in `outputs/`. Scale = accounts in the modeling table.
Base rate = churned label share from `outputs/integration_summary.json`.

| Iter | Design angle | Scale | Label base rate |
|---|---|---|---|
| part1_01 | Kimball star schema (fact_subscriptions + dims); grain discipline focus | 2,000 accounts | 16.3% |
| part1_02 | Event-sourced: single append-only log (~220k events), state folded in event-time order | 2,000 accounts | 28.8% |
| part1_03 | Wide feature-store panel (account-month × 24 mo); CRM vs billing reconciliation | 1,800 accounts | 33.2% |
| part1_04 | Normalized 3NF (one table per source system) + fuzzy entity resolution | 2,000 accounts | 16.8% |
| part1_05 | Account-hierarchy graph (1,800 accounts → 260 ultimate parents) + roll-up ARR | 1,800 accounts | 18.7% |
| part1_06 | SCD-Type-2 monthly snapshots + as-of reconstruction (asof vs final views) | 1,500 accounts | 17.8% |
| part1_07 | Survey-augmented: stated (NPS/CSAT) vs revealed account health, fraud signatures | 2,000 accounts | 11.9% |
| part1_08 | Multi-currency global (12 countries / 11 currencies); FX reconciliation + PII masking | 2,000 accounts | 17.8% |
| part1_09 | PLG telemetry-heavy (180-day daily grain, 360k rows); bot decontamination + activation funnels | 2,000 accounts | 15.4% |
| part1_10 | Support-centric: ticket threading, agent-identity table, SLA policy table | 1,800 accounts | 12.7% |
| part1_11 | Contract/commercial: quotes, discounts, renewal terms, competitor mentions in notes | 1,800 accounts | 12.7% |
| part1_12 | Marketing attribution: campaigns, ~30k touches, MQL/SQL funnel, unattributed-touch blind spots | 1,800 accounts | 12.2% |
| part1_13 | Partner/channel: deal-registration vs direct-sales conflict resolution | 2,000 accounts | 10.3% |
| part1_14 | Security-incident flavored: alert-stream collapsing, efficacy-vs-loyalty split | 2,000 accounts | 11.0% |
| part1_15 | Audit-first data quality: scorecard grades each source table; build only from trusted slices | 2,000 accounts | 7.5% |

Per-iteration contents: `approach.md`, `generate.py`, `clean.py`, `integrate.py`, `eda.py`,
`outputs/` (contains `integration_summary.json`, `eda_findings.json`, `modeling_table.csv` for most).

---

## 2. Review / audit artifacts

| File | Description | Size | Status |
|---|---|---|---|
| `PHASE1_CHRONICLE.md` | Narrative of the Phase 1 tournament: what was built, QA catches, leakage verdict, lessons | 16K | **final** (judge section notes winner TBD) |
| `part1_JUDGE_BRIEF.md` | Scoring brief/rubric given to the Phase 1 judge | 32K | **final** |
| `part1_REDTEAM.md` | Adversarial review of the iterations | 24K | **final** |
| `part1_LEAKAGE_AUDIT.md` | Leakage audit report — verdict: 10 LEAKED, 1 SUSPECT, 4 CLEAN | 16K | **final** |
| `part1_LEAKAGE_ADDENDUM.md` | Addendum to the leakage audit (iterations 13–15 results) | 4K | **final** |
| `part1_LEAKAGE_AUDIT_raw_13_15.json` | Raw audit output for iterations 13–15 | 12K | **final** |
| `leakage_audit.py` / `leakage_audit_13_15.py` | Audit scripts (correlation + determinism checks) | 8K / 8K | **final** |
| `part1_INVENTORY.md` | File-inventory sweep across all 15 iterations | 8K | **final** |
| `part1_SCHEMA_MAP.md` | Schema map across the iterations | 32K | **final** |
| `part1_TOURNAMENT.md` | Judge's final verdict + winning iteration | — | **pending** (not yet written; judge still scoring) |

## 3. Phase 2 / 3 prep artifacts

| File | Description | Size | Status |
|---|---|---|---|
| `PHASE2_SPEC.md` | Phase 2 (modeling tournament) spec | 44K | **final** |
| `PHASE2_SPEC_REVIEW.md` | Review of the Phase 2 spec | 28K | **final** |
| `PHASE2_READINESS.md` | Readiness checklist before Phase 2 modeling starts (incl. per-iteration leakage drop lists) | 12K | **final** |
| `PHASE3_SPEC.md` | Phase 3 spec | 32K | **final** |
| `PHASE3_SPEC_REVIEW.md` | Review of the Phase 3 spec | 20K | **final** |
| `CHURN_RESEARCH.md` | Churn research / landscape notes feeding later phases | 24K | **final** |

Note: `TOURNAMENT_REPORT.md` (12K, final) also lives here, but it covers the *modeling*
tournament (`approach_01`–`approach_15`: 15 modeling approaches, 7-point rubric, 8 red-teamed
to KILLs) — a separate track from the Phase 1 data-engineering tournament above.

---

## How to review tomorrow (suggested reading order)

1. **Read `PHASE1_CHRONICLE.md` first** — the whole Phase 1 arc in ~70 lines: what the 15
   iterations did, what QA caught, and the leakage verdict.
2. **Internalize the leakage verdict** (`part1_LEAKAGE_AUDIT.md` + `part1_LEAKAGE_ADDENDUM.md`) —
   10 of 15 tables leaked (`p_churn_latent`, `clv_12m`, label re-expressions); 4 are CLEAN
   (part1_04, 13, 14, 15). This is the single most decision-relevant fact for the VP round.
3. **Check the judge's state** — `part1_JUDGE_BRIEF.md` for how the winner is being picked;
   `part1_TOURNAMENT.md` will hold the verdict once the judge finishes (pending).
4. **Spot-check 2–3 iterations** from the table above (pick one CLEAN + one LEAKED):
   read each `approach.md` and skim `outputs/eda_findings.json` + `modeling_table.csv` schema.
5. **Forward plan** — `PHASE2_SPEC.md` + `PHASE2_READINESS.md` (drop lists before any
   training), then `PHASE3_SPEC.md` + `CHURN_RESEARCH.md`.
6. **Deep dives on demand** — `part1_REDTEAM.md`, `part1_SCHEMA_MAP.md`, `part1_INVENTORY.md`
   for adversarial critique, schema comparisons, and file-level coverage.
