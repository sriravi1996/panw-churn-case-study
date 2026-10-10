# part3_07 — Playbook Format: The CSM Operator's Manual

## Narrative thesis

Every other angle in this tournament answers the analyst's question. This one
answers the operator's question: *it is Monday morning, a worklist of at-risk
accounts just landed in my queue — what exactly do I do, who owns it, by when,
and what do I say on the phone?*

The thesis is that the case study's Phase 2 winner (the trigger catalog) is
not a modeling deliverable at all — it is an operating contract. Eight stated
rules, each with a threshold, an owner role, an SLA, and a plain-language
reading of what the firing means. This documentation iteration is written to
be printed, handed to the people who work the worklist, and used. It covers
all three assignment parts as one arc, but Part 3 — the operating layer — is
the star, because Parts 1 and 2 exist only to make the list trustworthy enough
to act on.

The target reader is a CSM, an account executive, or a support lead. Not a
data scientist. Not the VP (there is a separate 12-slide outline for that
meeting). When this manual mentions a model, it does so only to answer the
operator's two legitimate questions: "how is my list built?" and "why should I
trust the ordering?" Everything else about the model is deliberately
compressed to "just enough."

## Differentiation contract

This is the only Phase 3 angle whose success metric is **adoption by
operators** — judged on clarity of instruction, not analytical depth. The
contract this iteration must honor:

1. **Every trigger is a complete instruction.** Rule, threshold, owner, SLA,
   plain-language meaning, what to say on the call, and a success metric —
   all in the trigger's own section. An operator never has to hunt across
   sections to act.
2. **Six triggers ship; two are marked RETIRED.** T2 and T5 are named as
   retired inside their own sections, with the reason and what happens to
   their signal. A playbook that ships its failures silently is slideware.
3. **The model appears only where the operator needs it.** How the list is
   built (calibrated score, trigger gate, EV rank), why the ordering is
   trustworthy (calibration numbers), and what "calibrated p × ARR" means on
   a call. No architecture diagrams, no hyperparameter tables.
4. **Honesty rules are operating rules, not footnotes.** No assumed save
   rates in the money math, treated-flag logging on every action, and the
   capacity bands (K=20/40/60) stated as measured coverage — never as org
   charts or headcount claims.
5. **It covers all three assignment parts.** The data foundation (Part 1) and
   the modeling (Part 2) are retold in business language as the reasons the
   list can be trusted; Part 3 is the manual itself. The limitations section
   is explicit and named.

Material difference from the sibling angles: none of them optimize for the
person who works the list. This one does, and only this one is judged on
whether a CSM could act on Monday morning.

## Deliverable map

| File | Audience | Job it does |
|---|---|---|
| `README.md` | CSMs, AEs, support leads (the people who work the worklist) | The manual itself: how the list is built, the trigger playbook, the 9-playbook library, the capacity bands, the honesty rules, the limitations |
| `slides.md` | Ravi, presenting to the VP | 12-slide outline with full-sentence TLDR headlines, every slide grounded in traced numbers, ending with the pilot ask |
| `traceability.md` | Any skeptical reader | `claim | artifact(s) | key(s)/section | derivation or "direct"` — every number in README and slides resolves to a named artifact |
| `checklist.md` | Ravi, the night before | 10 VP questions, each answered in one sentence with a citation |

All numbers trace to the verified artifacts: `approaches/part1_07/`
(survey-augmented winner), `approaches/part2_07/` (trigger winner:
`approach.md`, `metrics.json`, `trigger_catalog.csv`, `shadow_pilot.md`),
`approaches/part2_01/metrics.json` (canonical reference), and
`approaches/part2_05/` (the 9-segment → 9-playbook map). No other numbers
are used; the banned numbers (p2_04/p2_06 dollars-squared expectations,
p2_12's stale metrics) never appear.
