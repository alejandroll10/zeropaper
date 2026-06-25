#!/usr/bin/env python3
"""Scorer floor test (#102) — the one-sided regression guard.

Runs the *real* assembled finance scorer against frozen reconstructions of
published top-3 finance papers and asserts each judgment dimension clears a
floor. A published top-3 paper landing below the floor = a harshness /
false-negative bias in the scorer rubric. This is the standing regression guard
the recent scorer bias-fix A/Bs never had: re-run after any scorer edit.

One-sided by construction: it anchors the bar from *below* only. Leniency /
discrimination (does the scorer also reject bad papers?) is out of scope (#98) —
the corpus has no negatives.

Build-time / maintenance tooling — zeropaper only, never deployed.

Pipeline:
  1. Assemble the finance scorer body (shared scorer-core.md + finance vocab) via
     the same loader setup.sh uses — so we test the actual shipped scorer prompt.
  2. For each fixture, run the scorer headless (claude -p) against the
     reconstructed artifacts; it writes scorer_decision.md.
  3. Parse the dimension score table; assert the gated dimensions clear the floor.
  4. Emit report.md.

Usage:
  python3 scorer_floor_test/run_floor_test.py                 # all fixtures, default gate
  python3 scorer_floor_test/run_floor_test.py --only betermier-investor-factors-2025
  python3 scorer_floor_test/run_floor_test.py --gate Surprise,Parsimony --floor 75
  python3 scorer_floor_test/run_floor_test.py --model sonnet  # cheaper dry run (NOT the calibration model)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
FIXTURES = ROOT / "fixtures"
REPORT = ROOT / "report.md"

SCORER_CORE = REPO / "templates" / "agent_bodies" / "shared"
FINANCE_BODIES = REPO / "templates" / "agents" / "finance"
FINANCE_VOCAB = REPO / "templates" / "agents" / "finance" / "vocab.json"
EMPIRICAL_FIRST_VOCAB = REPO / "templates" / "agents" / "finance_modes" / "empirical_first" / "vocab.json"

# Each fixture is scored by the scorer config its pipeline route would use, read
# from meta.json's "route". The pipeline has exactly two scoring routes:
#   theory-first     — base finance vocab; markers ef=False, xe=False (default).
#   empirical-first  — finance + empirical_first vocab overlay (H3 swaps to
#                      identification+empirics audits, MECHANISM_TERM=channel,
#                      recalibrated Surprise); markers ef=True, xe=True.
# A third class, "descriptive" (reduced-form measurement, no formal model and no
# causal estimand — e.g. an index-effect measurement paper), fits NEITHER route:
# empirical-first's causal-estimand-fidelity guard hard-fails a descriptive H1/H5,
# and theory-first under-serves it. The pipeline does not target descriptive papers,
# so such a fixture is OUT OF SCOPE — scored theory-first for reference but excluded
# from the breach verdict (its low score is out-of-distribution, not a rubric bias).
ROUTES = {"theory-first", "empirical-first", "descriptive"}

DIMENSIONS = ["Importance", "Novelty", "Surprise", "Rigor", "Parsimony", "Fertility"]
# #102 names the judgment dimensions (Rigor is stipulated-pass for published papers,
# so the floor is asserted on the five judgment dimensions, not Rigor).
JUDGMENT_DIMS = ["Importance", "Novelty", "Surprise", "Parsimony", "Fertility"]
DEFAULT_GATE = ["Surprise", "Parsimony"]  # the two recently-retuned dimensions
DEFAULT_FLOOR = 75  # #102 invariant; top-3-fin advance bar

# Scorer aggregate weights (must match scorer-core.md "## Aggregate").
WEIGHTS = {"Importance": 0.30, "Novelty": 0.15, "Surprise": 0.20,
           "Rigor": 0.15, "Parsimony": 0.10, "Fertility": 0.10}


def weighted_total(scores):
    return sum(WEIGHTS[d] * scores[d] for d in WEIGHTS)


def resolve_markers(body, empirical_first=False, ext_empirical=False):
    """Replicate setup.sh's post-assembly marker resolution so the floor test scores
    the SAME prompt a real deployment ships — load_body() alone leaves the
    <!-- THEORY_FIRST / EMPIRICAL_FIRST / EXT_EMPIRICAL --> markers unresolved, which
    would feed the scorer a hybrid prompt carrying extra FAIL conditions no
    deployment ships.

    Source of truth: setup.sh's marker resolver (the `ef`/`xe` python block, ~2142)
    plus the EMPIRICAL_FERTILITY_ADDENDUM strip (~2074). Keep in sync with it.
    Default (empirical_first=False, ext_empirical=False) = the theory-first finance
    deployment, which is what the current fixtures target.
    """
    if empirical_first:
        body = re.sub(r"<!-- THEORY_FIRST_START -->\n.*?<!-- THEORY_FIRST_END -->\n{0,2}", "", body, flags=re.DOTALL)
        body = re.sub(r"<!-- EMPIRICAL_FIRST_(?:START|END) -->\n?", "", body)
    else:
        body = re.sub(r"<!-- EMPIRICAL_FIRST_START -->\n.*?<!-- EMPIRICAL_FIRST_END -->\n{0,2}", "", body, flags=re.DOTALL)
        body = re.sub(r"<!-- THEORY_FIRST_(?:START|END) -->\n?", "", body)
    if ext_empirical:
        body = re.sub(r"<!-- EXT_EMPIRICAL_(?:START|END) -->\n?", "", body)
    else:
        body = re.sub(r"<!-- EXT_EMPIRICAL_START -->\n.*?<!-- EXT_EMPIRICAL_END -->\n{0,2}", "", body, flags=re.DOTALL)
    # FERTILITY_ADDENDUM: under --ext empirical setup.sh *substitutes* the marker
    # with extensions/empirical/scorer_fertility_inject.md (setup.sh:1862-1864);
    # otherwise the marker line is stripped (setup.sh:2074). Mirror both — injecting
    # the addendum matters because it is a gated Fertility-scoring rule for the one
    # empirical-first route.
    if ext_empirical:
        # Read raw (no transformation) to be byte-exact with setup.sh's patch().
        addendum = (REPO / "extensions" / "empirical" / "scorer_fertility_inject.md").read_text()
        body = body.replace("<!-- EMPIRICAL_FERTILITY_ADDENDUM -->", addendum)
    else:
        body = re.sub(r"^[ \t]*<!-- EMPIRICAL_FERTILITY_ADDENDUM -->[ \t]*\n", "", body, flags=re.MULTILINE)
    leftover = sorted(set(re.findall(r"<!-- [A-Z_]+ -->", body)))
    if leftover:
        raise RuntimeError(
            f"unresolved markers after resolution: {leftover}. setup.sh's marker set "
            "may have drifted from resolve_markers() — re-sync with setup.sh."
        )
    return body


def assemble_scorer(route="theory-first"):
    """Assemble the scorer body for a pipeline route, mirroring setup.sh.

    theory-first / descriptive → base finance vocab, ef=False xe=False.
    empirical-first            → finance + empirical_first vocab overlay (later
                                 layer wins on duplicate keys), ef=True xe=True.
    (A descriptive fixture is scored with the theory-first scorer for reference.)
    """
    sys.path.insert(0, str(REPO / "scripts"))
    from agent_body_loader import load_body, load_vocab
    ef = route == "empirical-first"
    vocab_paths = [str(FINANCE_VOCAB)] + ([str(EMPIRICAL_FIRST_VOCAB)] if ef else [])
    vocab = load_vocab(vocab_paths)
    body = load_body("scorer", [str(FINANCE_BODIES)], [str(SCORER_CORE)], vocab)
    return resolve_markers(body, empirical_first=ef, ext_empirical=ef)


_AUDIT_INPUTS = {
    "theory-first": (
        "- Math audit (structured): audits/math_audit.md\n"
        "- Math audit (free-form): audits/math_audit_freeform.md"
    ),
    # Empirical-first skips the math audit; H3 keys on the Stage-3a audit chain.
    "empirical-first": (
        "- Identification design (Stage 1): output/stage1/identification_design.md\n"
        "- Delivered empirical analysis (Stage 3a): output/stage3a/empirical_analysis.md\n"
        "- Identification audit (Stage 3a): output/stage3a/identification_audit.md\n"
        "- Empirics audit (Stage 3a): output/stage3a/empirics_audit.md\n"
        "- Data-integrity audit (Stage 3a): output/stage3a/data_integrity_audit.md\n"
        "- Data-selection audit (Stage 3a): output/stage3a/data_selection_audit.md\n"
        "- (No math audit — empirical-first has no derivations to audit.)"
    ),
}


def build_task(route):
    audits = _AUDIT_INPUTS["empirical-first" if route == "empirical-first" else "theory-first"]
    return f"""\
You are running as the pipeline's Gate-4 scorer on a finance paper (route: {route}).
Follow your instructions below exactly. Score this version independently.

The artifacts to read are in the current working directory:
- Theory / mechanism draft: theory/theory_v1.md
{audits}
- Novelty check on idea (Gate 1b): audits/novelty_idea.md
- Novelty check on full theory (Gate 3): audits/novelty_theory.md
- Implications (tagged): output/stage3/implications.md
- Self-attack report: output/stage4/self_attack.md
- Pipeline state: process_log/pipeline_state.json

The tier table doc (docs/stage_4.md) is not provided in this run. Use the
`top-3-fin` band stated in your own instructions (advance at 75+); read
`target_journal_tier` from pipeline_state.json (it is `top-3-fin`).

Do NOT look for, read, or glob any prior scorer decision file — there is none.
Write your decision to `scorer_decision.md` in the current working directory,
using the exact output format your instructions specify (including the
`| Dimension | Score | Justification |` table).

=== YOUR INSTRUCTIONS (the scorer agent body) ===
"""


def run_scorer(fixture_dir, scorer_body, model, route):
    prompt = build_task(route) + scorer_body
    decision = fixture_dir / "scorer_decision.md"
    if decision.exists():
        decision.unlink()
    proc = subprocess.run(
        ["claude", "-p", prompt, "--model", model, "--dangerously-skip-permissions"],
        cwd=str(fixture_dir),
        capture_output=True,
        text=True,
        timeout=900,
    )
    if not decision.exists():
        # Fall back to stdout if the agent printed instead of writing.
        if proc.stdout.strip():
            decision.write_text(proc.stdout)
        else:
            raise RuntimeError(
                f"scorer produced no decision for {fixture_dir.name}.\n"
                f"stderr: {proc.stderr[:1000]}"
            )
    return decision.read_text()


SCORE_ROW = re.compile(
    r"^\|\s*(Importance|Novelty|Surprise|Rigor|Parsimony|Fertility)\s*\|\s*(\d{1,3})\s*\|",
    re.MULTILINE,
)


def parse_scores(decision_text):
    scores = {dim: int(v) for dim, v in SCORE_ROW.findall(decision_text)}
    missing = [d for d in DIMENSIONS if d not in scores]
    if missing:
        raise ValueError(f"could not parse dimension(s) {missing} from scorer output")
    return scores


HARD_FAIL = re.compile(
    r"\|\s*H[1-5][^|]*\|\s*FAIL"                       # explicit FAIL row in the H table
    r"|Decision:\s*(?:ABANDON|MAJOR REWORK|REVISE)"    # any non-advance decision (no score table ⇒ H-fail)
    r"|score is 0",
    re.IGNORECASE,
)


def detect_hard_fail(decision_text):
    """The scorer emits the dimension table only 'if all H pass' (scorer-core.md).
    A hard-requirement FAIL on a published paper is the loudest harshness signal, so
    classify it as a decision-level breach (total 0), not a parse error.

    Only ever called after parse_scores() has already failed (no dimension table),
    so a passing decision's H-template rows / threshold-table prose cannot reach it
    — that context is what makes the Decision:REVISE and prose alternations safe (a
    real REVISE in [60,79] always carries a score table)."""
    return bool(HARD_FAIL.search(decision_text))


def fixture_route(fd):
    """Read the pipeline route for a fixture from meta.json (default theory-first)."""
    meta = fd / "meta.json"
    route = "theory-first"
    if meta.exists():
        route = json.loads(meta.read_text()).get("route", "theory-first")
    if route not in ROUTES:
        raise ValueError(f"{fd.name}: unknown route '{route}' (expected one of {sorted(ROUTES)})")
    return route


def score_once(fd, scorer_body, model, report_only, route):
    """Return a dimension->score dict for one scoring of fixture `fd`. An H-fail
    (no score table) counts as an all-zero dict — catastrophic, and it pulls the
    mean down correctly under --repeat."""
    if report_only:
        saved = fd / "scorer_decision.md"
        if not saved.exists():
            raise RuntimeError("no saved scorer_decision.md (run without --report-only first)")
        decision = saved.read_text()
    else:
        decision = run_scorer(fd, scorer_body, model, route)
    try:
        return parse_scores(decision)
    except ValueError:
        if detect_hard_fail(decision):
            return {d: 0 for d in DIMENSIONS}
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="run a single fixture by slug")
    ap.add_argument("--gate", default=",".join(DEFAULT_GATE),
                    help="comma-separated dimensions to assert the floor on "
                         f"(default: {','.join(DEFAULT_GATE)}). Use 'all' for all judgment dims.")
    ap.add_argument("--floor", type=int, default=DEFAULT_FLOOR)
    ap.add_argument("--model", default="opus",
                    help="scorer model (default opus, the pinned scorer model — the calibration model)")
    ap.add_argument("--report-only", action="store_true",
                    help="re-parse the saved scorer_decision.md in each fixture and rebuild "
                         "report.md without re-running the scorer (no model calls).")
    ap.add_argument("--repeat", type=int, default=1, metavar="N",
                    help="score each fixture N times and aggregate by mean (default 1). The "
                         "scorer is stochastic; N>1 separates a real calibration move from "
                         "run-to-run noise. Use matched N for a before/after A/B.")
    ap.add_argument("--jobs", type=int, default=1, metavar="N",
                    help="run N fixtures concurrently (default 1, sequential). Each scorer "
                         "call is an independent claude subprocess writing only its own "
                         "fixture, so this parallelizes cleanly. 4-6 is a good range.")
    args = ap.parse_args()
    if args.report_only and args.repeat != 1:
        sys.exit("--repeat is incompatible with --report-only (only one saved decision per fixture).")
    if args.repeat < 1:
        sys.exit("--repeat must be >= 1.")

    gate = JUDGMENT_DIMS if args.gate.strip().lower() == "all" else [
        g.strip() for g in args.gate.split(",") if g.strip()
    ]
    bad = [g for g in gate if g not in DIMENSIONS]
    if bad:
        sys.exit(f"unknown gate dimension(s): {bad}")

    if not FIXTURES.exists():
        sys.exit("No fixtures/ — run the reconstruction step first (see README).")
    fixture_dirs = sorted(d for d in FIXTURES.iterdir() if d.is_dir() and (d / "theory").exists())
    if args.only:
        fixture_dirs = [d for d in fixture_dirs if d.name == args.only]
        if not fixture_dirs:
            sys.exit(f"no fixture named {args.only}")

    jobs = 1 if args.report_only else max(1, args.jobs)
    mode = "Re-parsing saved decisions for" if args.report_only else f"Scoring (model={args.model})"
    rpt = f" ×{args.repeat} runs/fixture (mean)" if args.repeat > 1 else ""
    par = f", {jobs} parallel" if jobs > 1 else ""
    print(f"{mode} {len(fixture_dirs)} fixture(s){rpt}{par}; gate={gate} floor={args.floor}\n")

    # Pre-assemble each route's scorer once (avoids races + redundant assembly across threads).
    scorer_cache = {}
    if not args.report_only:
        for fd in fixture_dirs:
            route = fixture_route(fd)
            scorer_cache.setdefault(route, assemble_scorer(route))

    def score_fixture(fd):
        """Run a fixture's ×N scoring and return its result tuple, or an error.
        Independent per fixture (each writes only its own decision file), so safe
        to run concurrently."""
        route = fixture_route(fd)
        scorer_body = None if args.report_only else scorer_cache[route]
        runs = [score_once(fd, scorer_body, args.model, args.report_only, route)
                for _ in range(args.repeat)]
        in_scope = route != "descriptive"
        scores = {d: round(sum(r[d] for r in runs) / len(runs), 1) for d in DIMENSIONS}
        spread = {d: (min(r[d] for r in runs), max(r[d] for r in runs)) for d in DIMENSIONS}
        below = [d for d in gate if scores[d] < args.floor] if in_scope else []
        total = weighted_total(scores)
        advance = total >= args.floor
        return (fd.name, scores, below, total, advance, spread, len(runs), route)

    results = {}  # fd -> tuple | Exception, keyed to preserve input order in the report
    if jobs > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futs = {ex.submit(score_fixture, fd): fd for fd in fixture_dirs}
            for fut in futs:
                fd = futs[fut]
                try:
                    results[fd] = fut.result()
                except Exception as e:
                    results[fd] = e
    else:
        for fd in fixture_dirs:
            try:
                results[fd] = score_fixture(fd)
            except Exception as e:
                results[fd] = e

    rows, breaches, errors = [], [], []
    for fd in fixture_dirs:  # input order
        res = results[fd]
        if isinstance(res, Exception):
            errors.append((fd.name, str(res)))
            print(f"  ERROR  {fd.name}: {res}")
            continue
        name, scores, below, total, advance, spread, nruns, route = res
        in_scope = route != "descriptive"
        is_breach = in_scope and (below or not advance)
        flag = "n/a " if not in_scope else ("FAIL" if is_breach else "ok")
        rows.append(res)
        if is_breach:
            breaches.append((name, below, {d: scores[d] for d in below}, total, advance))
        def sp(d):
            lo, hi = spread[d]
            return f"({lo}-{hi})" if (args.repeat > 1 and lo != hi) else ""
        tag = f"[{route}]" + ("(out-of-scope)" if not in_scope else "")
        print(f"  {flag:4} {name} {tag}  total={total:5.1f} {'ADV' if advance else 'REV'}  " +
              "  ".join(f"{d[:4]}={_fmt(scores[d])}{sp(d)}" for d in DIMENSIONS))

    write_report(rows, breaches, errors, gate, args.floor, args.model, args.repeat)
    print(f"\nReport → {REPORT}")
    if breaches or errors:
        print(f"\n{len(breaches)} floor breach(es), {len(errors)} error(s).")
        sys.exit(1)
    print("\nAll fixtures cleared the floor on the gated dimensions.")


def _median(vals):
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def _fmt(v):
    """Render an integer-valued mean as an int (80, not 80.0); keep real decimals."""
    return int(v) if float(v).is_integer() else round(float(v), 1)


def write_report(rows, breaches, errors, gate, floor, model, repeat=1):
    n_dimbreach = sum(1 for r in breaches if r[1])
    n_decbreach = sum(1 for r in breaches if not r[4])
    runnote = (f"  ·  **{repeat} runs/fixture** (scores are means; spread = min–max)"
               if repeat > 1 else "")
    lines = [
        "# Scorer floor test — report",
        "",
        f"- Model: `{model}`  ·  Floor: **{floor}** (top-3-fin advance bar)  ·  "
        f"Gated dimensions: {', '.join('**'+g+'**' for g in gate)}{runnote}",
        f"- Fixtures: {len(rows)}  ·  Decision-level false-negatives (aggregate < {floor}): "
        f"**{n_decbreach}**  ·  Dimension floor breaches: {n_dimbreach}  ·  Errors: {len(errors)}",
        "",
        "Two failure modes, both = a harshness / false-negative bias in the rubric:",
        "1. **Decision-level** — the weighted aggregate of a published top-3 paper falls "
        "below the tier advance bar (the scorer would REVISE, not ADVANCE). This is the "
        "primary signal: it is the actual gate decision.",
        "2. **Dimension-level** — a gated judgment dimension falls below the floor. Note a "
        "published paper may legitimately be weak on one dimension while clearing the "
        "aggregate; a *systematically* low dimension across papers is the real flag.",
        "",
        "## Per-fixture scores",
        "",
        "| Paper | route | total | decision | " + " | ".join(DIMENSIONS) + " | dim breach |",
        "|" + "---|" * (len(DIMENSIONS) + 5),
    ]
    for name, scores, below, total, advance, spread, nruns, route in rows:
        def cell(d):
            v = scores[d]
            v = int(v) if float(v).is_integer() else v
            if repeat > 1 and spread[d][0] != spread[d][1]:
                return f"{v} ({spread[d][0]}-{spread[d][1]})"
            return str(v)
        cells = " | ".join(cell(d) for d in DIMENSIONS)
        oos = route == "descriptive"
        dec = "out-of-scope" if oos else ("ADVANCE" if advance else "**REVISE**")
        breach_cell = "n/a" if oos else (",".join(below) if below else "—")
        lines.append(f"| {name} | {route} | {total:.1f} | {dec} | {cells} | {breach_cell} |")
    scoped = [r for r in rows if r[7] != "descriptive"]  # exclude out-of-scope from distributions
    if scoped:
        oos_n = len(rows) - len(scoped)
        oos_note = f"  (excludes {oos_n} out-of-scope descriptive fixture(s))" if oos_n else ""
        totals = [r[3] for r in scoped]
        lines += ["", "## Aggregate (the gate decision)" + oos_note, "",
                  f"- Weighted total: min={min(totals):.1f} median={_median(totals):.1f} "
                  f"max={max(totals):.1f}  ·  below {floor}: "
                  f"{sum(t < floor for t in totals)}/{len(totals)}",
                  "", "## Per-dimension harshness", ""]
        for d in DIMENSIONS:
            vals = [r[1][d] for r in scoped]
            mark = "  ← gated" if d in gate else ""
            lines.append(f"- {d}: min={_fmt(min(vals))} median={_fmt(_median(vals))} "
                         f"max={_fmt(max(vals))}  ·  "
                         f"below {floor}: {sum(v < floor for v in vals)}/{len(vals)}{mark}")
    if breaches:
        lines += ["", "## Breaches", ""]
        for name, below, vals, total, advance in breaches:
            parts = []
            if not advance:
                parts.append(f"aggregate={total:.1f} (REVISE)")
            if below:
                parts.append("dims: " + ", ".join(f"{d}={_fmt(vals[d])}" for d in below))
            lines.append(f"- **{name}**: " + "; ".join(parts))
    if errors:
        lines += ["", "## Errors", ""]
        for name, err in errors:
            lines.append(f"- **{name}**: {err}")
    REPORT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
