# Lessons harvest — `finance-empirical-first-1-864b5015`

**Date:** 2026-06-09
**Run:** `finance-empirical-first-1-864b5015` (org `automated-papers-produced`), shipped 2026-05-04
**State:** `status: complete`, `current_stage: stage_10`, `problem_attempt: 1`, `seeded: false`
**Mode:** empirical-first (the `mode` field is unpopulated in `pipeline_state.json`, but LESSONS confirm: "Math-auditor / Gate 2 / Stage 2b were correctly skipped under empirical-first mode"; repo name + section structure corroborate). **2nd-oldest finished run in the sweep.**
**Paper:** *"Share-Class Aggregation in Mutual-Fund Shift-Share Instruments: A Methodological Note with a Target-Date-Fund Application"* — 37pp, ~3,800 words, FRL-tier Practitioner's Note. Tier downgraded `top-3-fin` → `field` → `letters` over the run.

---

## TL;DR

**This is the worst-*presenting* paper in the sweep, and a pure-corroboration repo.** The empirical *content* is honest, well-scoped, and internally coherent (matches the self-grade); Tables 1–6 are all legible (no clipping, no overfull). But the *rendered presentation* is broken in four ways, every one of which the self-grade is totally blind to, and every one of which is in an **already-tracked, already-filed class**:

1. **Every citation renders `?`** (BHJ, AKM, Lou, Coval-Stafford — every `\cite` undefined; bibliography effectively never compiled) → **ALREADY ADDRESSED** by the build-verify citation/bbl gate (`stage_5.md:64-65`); run predates it. **Validates the gate** — this is the most extreme citation-failure instance in the sweep, and a current run would fail the build and rebuild. Closed-on-arrival, not filed.
2. **Every cross-ref renders `??`** — **55 occurrences** (every Section/Table/equation/IA ref) → **OPEN, #75.** By far the largest #75 instance (fe5 ~10, fef2 7, **this 55**) and the most diagnostic: here citations *and* refs failed together, and the gate as written catches only the citation half — direct proof the `Citation`-but-not-`Reference` asymmetry is load-bearing. → **corroborate #75 (3rd run, decisive instance).**
3. **`[Author]` placeholder on the title page** → **OPEN, #81.** 3rd run (fef2 `AUTHOR PLACEHOLDER`, fe2 `[AUTHOR]`, **this `[Author]`**) — a **3rd distinct literal**, and critically one that does **not** match the skeleton token (`main.tex.template:32` ships `AUTHOR PLACEHOLDER`). This is the decisive case for #81's "guard the placeholder *class* + grep the rendered PDF, not a fixed string" — even a literal-token guard for `AUTHOR PLACEHOLDER` would miss `[Author]`. → **corroborate #81 (3rd run, 3rd distinct literal, defeats fixed-string guard).**
4. **Zero rendered figures in 37pp; the "DAG" ships as ASCII art in a verbatim block** (pp. 9–10) → **#71 class.** 8th figureless-main-body run. New sub-mechanism: the abstract/intro promise "the directed acyclic graph," and it is delivered as monospace ASCII (no `\includegraphics`, no float, no `\caption`, `grep -c figure`=0, `pdfimages` empty). Distinct from "never produced" (fe5/fe3/fec2), "produced-but-orphaned" (fe4), and "IA-only" (fef4): here it is **produced-as-ASCII-not-a-figure**. A source-grep for `\includegraphics` cannot catch it (there is none); a **rendered-PDF figure-presence check** (the strongest #71 sub-proposal, from fe4) would. → **corroborate #71 (8th figureless; ASCII-DAG mechanism reinforces the rendered-PDF-figure-check proposal).**

**No new issue filed** — all OPEN candidates duplicate existing issues.

---

## Track A — self-graded lessons (LESSONS_PAPER / LESSONS_PIPELINE / LIMITATIONS)

The self-grade is honest and self-aware about the *content* trajectory (mechanism-referee PARTIAL→PARTIAL→VALID; never-abandon rule; honest letters-tier landing) but **mentions none of the four presentation defects above** — the canonical LESSONS-blindness this sweep exists to catch.

LESSONS_PIPELINE "Specific template-maintenance recommendations", checked against current state:

| # | Self-lesson | Current-state verdict | Disposition |
|---|-------------|----------------------|-------------|
| 1 | Polish-agent prompts should require explicit `Write` (4 of 8 polish-r1 agents returned report content as task-summary text instead of writing files) | **ALREADY ADDRESSED** — Stage-9 write-verification gate added `3fba5cf` (dedup list item 2); run predates it | Closed-on-arrival, not filed |
| 2 | Stage-5 paper-writer should not author Table 1 / IA §D descriptive stats on its own (paper-writer-fabricated stats, caught only because empiricist re-ran) | **PARTIAL** — claim-enumerator/grounder/verifier (Stage-5 step 5a, `--ext empirical`) now backstops authored numerical claims as PAPER-SIDE-ERROR; but apply/source-grounding of *every* paper-writer-authored number is the #77 theme | **corroborate #77** (Nth unverified-producer instance, after fe3-L2 / fe2) |
| 3 | Idea-generator regeneration should verify regulatory implementation status before proposing a design that hinges on it (round-3: 6/7 sketches had regulatory-fact errors — DOL fiduciary rule never reached operational bite, SEC IC-30255 never finalized) | **OPEN but DROPPED** — realized harm is **cost only** (one wasted idea-gen round); the idea-reviewer backstop **caught all of them** before theory, so quality was not harmed. Note-only. | Not filed |
| 4 | Stage-6 editor Downgrade-tier should fire earlier when freeform repeatedly says "fits a lower-tier outlet" (4 rounds at field tier when r2 already signaled letters) | **Note-only / subjective** — same theme as fe3-L4 / fe4-A2 (no encoded early-within-tier-convergence exit; cost-only, subjective) | Not filed (corroborates the standing note-only cluster) |
| — | Gate-1c data-feasibility scout (NR-3/NR-4 surfaced one round too late, after round-2 budget spent) | OPEN but cost-only; idea-gen-quality, no clean gate | Note-only |

`LIMITATIONS.md` = stock macro-id `#18` (documented-deferred). No run-authored limitation.

---

## Track B — holistic read (the high-value track)

Read as a reader, not a referee. **Content reads honestly**: prose abstract (no notation wall; uses inline `crsp_fundno`/`wficn` code, fine), plain-language title (no acronym head; "shift-share" / "Target-Date-Fund" in plain English), conclusion spells BHJ out ("Borusyak-Hull-Jaravel"), honest scope (falsified the monotone-scaling posit and *retired* it; two placebos; AR-CI as power statement not bound). Tables 1–6 legible, no clipping, no overfull. The mechanism is clear and the contribution is locatable (the F-differential is the load-bearing positive content). On *content* this is a clean, honest Practitioner's Note.

**But the rendered presentation is broken** — see the four TL;DR defects. The reader cannot tell which papers are cited *anywhere* (every `\cite` → `?`), cannot follow a single cross-reference (every `\ref` → `??`, 55×), sees `[Author]` on page 1, and never sees a single figure despite a DAG being promised and delivered as ASCII. The first three are desk-reject-grade. The gap between the honest content and the broken presentation is the entire point of this sweep: **the run's LESSONS grade the content and are blind to the rendering.**

### Mechanical evidence
- `pdfimages -list`: empty (zero embedded images)
- `pdftotext | grep -c -i figure`: **0**
- `pdftotext | grep -c '??'`: **55**
- `grep -c -i placeholder` (rendered): 0 — but the title page shows literal `[Author]` (bracketed, not the skeleton's `AUTHOR PLACEHOLDER` token; pdftotext doesn't match "placeholder" on `[Author]`)
- Citations: every `\citep`/`\citet` in the body renders `?` (visible from p.2 onward: "following ? (hereafter BHJ)", "formalized by ?")

---

## Disposition summary

**Pending operator go-ahead** (method step 8a — corroboration comments are outward-facing writes):

- **Corroborate #75** — 3rd run, **55 `??`**, decisive: citations + refs failed together, gate catches only the citation half.
- **Corroborate #81** — 3rd run, 3rd distinct literal `[Author]` that **does not match the skeleton token** `AUTHOR PLACEHOLDER` (defeats any fixed-string guard).
- **Corroborate #71** — 8th figureless run; new **ASCII-DAG-in-verbatim** mechanism reinforces the rendered-PDF figure-presence-check proposal.
- **Corroborate #77** — paper-writer fabricated Table 1 / IA §D descriptive stats (Nth unverified-producer instance).

**Closed-on-arrival (not filed):**
- All-citation-failure (`?`) → ALREADY ADDRESSED, build-verify citation/bbl gate `stage_5.md:64-65`; **validates** the gate (most extreme instance in sweep).
- Silent polish-write-failure → ADDRESSED `3fba5cf`.
- Abstract/title read clean (prose abstract, plain title) — run predates `75e5c9e` yet reads clean.
- `LIMITATIONS.md` = stock macro-id `#18`.

**No new issue.**

---

## Sweep-logistics note

Remaining unswept finished repos after this session (from the Scope list, oldest tail): `finance-llm-1-96cea289` (2026-05-03, `complete`, **seeded** — `--ext theory_llm`/`finance-llm`; check whether the holistic-paper-read framing fits a theory_llm run), `finance-paper-1` (2026-05-02, `complete`, `stage_9`), `finance-empirical-1` (2026-05-02, `complete`, `stage_9`). The two `stage_9`-terminal repos finished but may predate Stage-10; confirm a committed `paper/main.pdf` before harvesting. `referee-c31e5f30` still deferred to a report-mode-specific pass. Known not_started/seed_triage skips (this + prior sessions): `charlie-2-7841b572`, `charlie-2`.
