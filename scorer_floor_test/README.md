# Scorer floor test (#102)

An external, one-sided regression guard on the Gate-4 **scorer**. It anchors the
scorer's bar **from below** against real published top-3 finance papers, so a
harshness / false-negative bias in the rubric is caught the way the recent ad-hoc
scorer-bias A/Bs caught theirs — but standing, re-runnable after any scorer edit.

> **Build-time / maintenance tooling. Lives in zeropaper only; never copied into a
> deployed project** (registered in `setup.sh`'s deploy cleanup, cf.
> `scripts/resolve_model_fallbacks.py`).

## Why this exists

The scorer is the same model family that wrote the theory, scoring its own
pipeline's output with no external benchmark. Every named-bias fix to date was
A/B-validated *by the same family* — that proves behavior changed, not that the
bar sits in the right place relative to the real world. This test adds the missing
external anchor: feed the scorer a faithful reconstruction of a paper that *did*
clear the top-3 bar, and check it doesn't rate it below the bar.

It is deliberately **one-sided**. Leniency / discrimination (does the scorer also
*reject* bad papers?) is out of scope — the corpus has no negatives — and is left
to #98.

## The invariant

A faithful reconstruction of a published top-3 finance paper must score **≥ 75**
(the `top-3-fin` advance bar) on the judgment dimensions
(Importance, Novelty, Surprise, Parsimony, Fertility). A published paper landing
below the floor on a gated dimension = a harshness bias in the rubric.

The harness gates a **configurable subset** of the judgment dimensions (default:
`Surprise,Parsimony` — the two most recently retuned — see `--gate all` for the
full set). Rigor is stipulated-pass for published papers, so it is recorded but
not floored.

## No teaching to the test

This is the property that makes the guard meaningful:

1. **Labels are fixed by publication, not by any model judgment.** Every corpus
   paper cleared a top-3 referee process; that is the ground truth.
2. **The reconstruction is blind to the scorer and its rubric.** `reconstruct.md`
   hands the reconstructor the *pipeline's* artifact schemas (theory-draft sections,
   implication tags, self-attack format) but never the scorer rubric, its
   dimensions, weights, or thresholds. Reconstruction agents are instructed to read
   only their page + `reconstruct.md`.
3. **Nothing from the scorer ever flows back into fixture construction.** Fixtures
   are built once and frozen (committed). They are regenerated **only** if the
   scorer's *input schema* changes (a structural migration) — never because a
   scorer output was disappointing. Tuning a fixture to lift a low score is the one
   thing that destroys the guard.

One acknowledged thumb near the scale: `reconstruct.md` instructs the
self-attack to keep robustness-attack severity ≤ 6 and not to manufacture a fatal
attack — and the scorer *does* key on self-attack severity ≥ 7. This is defensible
as faithful (a top-3-accepted paper genuinely lacks a fatal flaw, by the ground
truth of its acceptance), and the reconstructor is never told *why* severity
matters, so the blindness property holds. It is noted here because it is the lone
point where reconstruction guidance touches a scoring-relevant input.

## Layout

```
fetch_corpus.py     Freeze the live IAR distilled-lit wiki → corpus/raw/ (no auth; stdlib HTTP)
reconstruct.md      Rubric-BLIND reconstruction prompt: distilled page → pipeline artifacts
run_floor_test.py   Assemble the real finance scorer, run it per fixture, assert the floor
corpus/
  raw/{jf,rfs}/*.md Frozen snapshot of the distilled pages (the reconstruction source)
  PROVENANCE.json   Source site, content hash, freeze date, file list
fixtures/<slug>/    Frozen reconstructed scorer-native inputs (committed; one dir per paper)
  theory/theory_v1.md, output/stage3/implications.md, output/stage4/self_attack.md,
  process_log/pipeline_state.json, audits/*.md, meta.json
report.md           Latest run: per-paper dimension scores + floor breaches
```

## Running it

```bash
# 1. (Re)freeze the corpus snapshot from the live wiki. Run rarely + deliberately.
python3 scorer_floor_test/fetch_corpus.py
python3 scorer_floor_test/fetch_corpus.py --check     # verify snapshot vs provenance

# 2. Reconstruct fixtures (rubric-blind). Built once, then frozen — see reconstruct.md.
#    Each page is handed to an agent that reads ONLY that page + reconstruct.md.

# 3. Run the floor test (uses the pinned scorer model, opus, by default).
python3 scorer_floor_test/run_floor_test.py                       # default gate: Surprise,Parsimony
python3 scorer_floor_test/run_floor_test.py --gate all --floor 75 # all judgment dims
python3 scorer_floor_test/run_floor_test.py --only <slug>         # one paper
python3 scorer_floor_test/run_floor_test.py --repeat 3            # N runs/fixture, aggregate by mean (separates a real move from scorer noise)
python3 scorer_floor_test/run_floor_test.py --model sonnet        # cheaper dry run (NOT the calibration model)
python3 scorer_floor_test/run_floor_test.py --report-only         # rebuild report.md from saved decisions, no model calls
```

**Per-fixture routing.** Each fixture's `meta.json` carries a `route`: `theory-first`
(formal-model papers), `empirical-first` (causal-identification papers — scored with
the finance+empirical_first vocab overlay, ef/xe markers, injected Fertility
addendum, and the Stage-3a audit chain for H3), or `descriptive` (reduced-form
measurement with no model and no causal estimand — fits neither route, so it is
scored theory-first for reference but **excluded from the breach verdict** as
out-of-distribution). The harness assembles the matching scorer per fixture; keep
`assemble_scorer()` / `resolve_markers()` in sync with `setup.sh`.

**The scorer is stochastic.** Use `--repeat N` (matched N for a before/after A/B) so
a calibration move is read against run-to-run noise, not a single draw — a lesson
the pilot learned when a one-shot A/B disagreed with the ×2 means.

`--report-only` re-parses each fixture's `scorer_decision.md` — which is a run
output, **gitignored**, not committed. So it only works on a machine that has
already done a full run this checkout; a fresh clone must run the scorer first.

A non-zero exit + a `## Breaches` section in `report.md` means a published paper
scored below the floor — investigate the rubric, not the fixture.

## Re-freezing the corpus

The live wiki has no version pin, so reproducibility is anchored by
`corpus/PROVENANCE.json:corpus_sha256` (a content hash over the frozen pages).
Re-freeze only on a deliberate, audited refresh (e.g. the wiki added papers you
want covered) — and re-freeze the **corpus**, never a single fixture, in response
to scorer output.
