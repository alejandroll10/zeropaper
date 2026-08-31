# INV-2: Citation Fabrication/Misattribution Passes the Bib Check (T3)

**Verdict: REPRODUCED**

The reported failure mode is real and fully explainable against current HEAD. The authoritative-source mechanism is exclusively OpenAlex + WebSearch; no DOI/publisher-registry check exists anywhere in the verification chain. The firing schedule creates a large propagation window. Neither operator-proposed fix is currently implemented, though both are feasible to build. One of the two (DOI/publisher binding check) requires new infra; the other (fire at citation introduction) requires an orchestrator rule change.

---

## 1. Exact Authoritative-Source Mechanism

### 1a. The Python verifier: OpenAlex only

The entire mechanical verification layer is `templates/utils/bib_verify/openalex_check.py`. Its `verify()` function (lines 118–151) queries:

```
OPENALEX = "https://api.openalex.org/works"
```

It submits `{"search": title, "per-page": "3"}` — a free-text title search returning at most 3 candidates — and picks the best match by `SequenceMatcher` title similarity (line 113–115). A VERIFIED result requires `sim >= 0.85` AND `abs(matched_year - cited_year) <= 1` (lines 139, 131). The DOI field OpenAlex returns is echoed into the JSONL output (line 142) and printed in the markdown report (lines 166–167 of `verify_bib.sh`), but **it is never fetched or validated**. The script does not call `doi.org`, `crossref.org`, any publisher endpoint, or any DOI resolution service. The DOI is decorative in the output.

### 1b. The WebSearch fallback: web search only

When a cite produces a MISS from OpenAlex, the `bib-verifier` agent body (`templates/agent_bodies/shared/bib-verifier.md`, lines 17–22 / skill body `templates/skill_bodies/bib_verify/bib-verify.md`, lines 43–49) instructs the agent to run WebSearch in this order:

1. `"Exact Title Of Paper" author-last-name`
2. `"Exact Title" site:ssrn.com`
3. `"Exact Title" site:nber.org`
4. `"Exact Title" site:arxiv.org`

If any of these returns "a real result (matching title + plausible authors + year)" the cite is marked `RESOLVED-VIA-WEBSEARCH` and the URL is captured. There is no instruction to fetch that URL and confirm the paper exists; the instruction is to look for "a real result" in the web search snippet.

**Critical gap:** For a misattributed or fabricated paper, both channels fail in the same way:
- A fabricated title that sounds like a real paper may collide in OpenAlex with a high-similarity real paper, yielding VERIFIED with a wrong DOI (which is never fetched).
- A fabricated paper whose title is plausible but distinct from any real paper will get a MISS, then the WebSearch fallback looks for snippets — a hallucinated paper with a plausible title in a real venue can produce a web result that "looks" matching enough that a model marks it RESOLVED-VIA-WEBSEARCH.

The `polish-bibliography` agent (`templates/agent_bodies/shared/polish-bibliography.md`) also leans entirely on OpenAlex (`openalex skill`, line 13; `openalex.py work <doi-or-id>`, line 14) and WebFetch as fallback (line 36). It does not consult publisher pages or DOI registries.

### 1c. No DOI/publisher-registry check anywhere

A search across the full template tree confirms: no file in `templates/utils/`, `templates/agent_bodies/`, `templates/skill_bodies/`, or `templates/shared/docs/` contains a call to `doi.org`, `api.crossref.org`, `api.datacite.org`, or any publisher API. The `doi` field that OpenAlex returns is stored in JSONL output but never resolved. The operator's diagnosis is exactly correct: **the binding check is a secondary bibliographic database, not the authoritative publisher/DOI registry**.

---

## 2. Behavior on Fabricated or Misattributed Papers

### Fabrication scenario

A cite key for a plausible-sounding but non-existent paper is submitted.

1. OpenAlex title search (`per-page=3`) returns 0 results or results with low similarity → **MISS**.
2. WebSearch fallback: the agent searches for `"Fabricated Title" author-name`. If the title is common-sounding and an actual paper with a similar title/author exists anywhere on the web, the agent can mark it **RESOLVED-VIA-WEBSEARCH** with a URL that points to a different (real) paper — a misattribution, not a fabrication catch.
3. If WebSearch also finds nothing, the agent marks it **FABRICATED** — this path works correctly.

The dangerous scenario is #2: a hallucinated paper can be "confirmed" by a real paper that happens to have a similar title, producing a RESOLVED-VIA-WEBSEARCH verdict that is actually a misattribution. The agent instruction says "If a real result appears (matching title + plausible authors + year)" — but matching title and plausible authors can be satisfied by a different paper with a similar title by an author who has written in the same area.

### Misattribution scenario

A real paper exists in OpenAlex but the citation attributes it to the wrong authors or a wrong claim. The OpenAlex lookup succeeds on title similarity → **VERIFIED**. The verification ends there. No content check is performed at the bib-verifier stage (that is `polish-bibliography`'s job, which fires much later in Stage 9). A VERIFIED verdict propagates the misattribution through the pipeline cleanly.

### Common-title collision scenario

Two real papers share most of a title. OpenAlex returns the wrong one at similarity >= 0.85 → **VERIFIED** for the wrong paper. The DOI in the JSONL points to the wrong paper but is never fetched to confirm. This is specifically noted as a known risk in the skill body (`templates/skill_bodies/bib_verify/bib-verify.md`, line 76: "OpenAlex sometimes returns a high-similarity match that is the wrong paper (common-title collisions)") but the only mitigation instruction is "glance at the venue and authors" — an LLM instruction, not a programmatic guard.

---

## 3. Firing Schedule

Bib-verifier fires at three points in the pipeline. None of these is at citation introduction.

| Stage | Firing point | Document source | What it checks |
|---|---|---|---|
| Stage 5, step 6 | After initial paper draft completes | `docs/stage_5.md:57` | Full references file of the newly written paper |
| Stage 8 | Dedicated bibliography verification stage, after every referee round that changes citations | `docs/stage_8.md:1–10` | Full references file; up to 2 rounds (cap at `bib_verify_round >= 2`) |
| Stage 9, step 4 | One-shot post-polish pass when paper-writer adds/removes citations during polish | `docs/stage_9.md:38` | Post-polish references; does not increment `bib_verify_round` |

**Citations first appear in documents at Stage 0 (literature-scout, `docs/stage_0.md`) and Stage 5 (paper-writer).** The literature-scout body (`templates/agent_bodies/shared/literature-scout.md:47`) instructs "No hallucinated references. Every paper you cite must come from a WebSearch result" — but this is an instruction to the scout, not a verification step. Gap-scout, idea-generator, novelty-checker, and paper-writer all introduce citations into `output/stage0/literature_map.md`, `output/stage1/`, and eventually `paper/sections/` before any bib check fires.

**The propagation window is real**: a fabricated or misattributed cite introduced by the literature-scout at Stage 0 step 1 populates `literature_map.md`, flows through idea-generator → `selected_idea.md`, theory-generator → `theory_draft.md`, implications writer → `implications.md`, paper-writer → all `.tex` sections. By the time bib-verifier first fires (Stage 5 step 6), the cite has already shaped gap framing, contribution language, lit positioning, and mechanism wording across multiple `output/stage*/` artifacts. The ~17-file propagation reported by the operator is plausible because many stage artifacts quote or paraphrase the literature map.

---

## 4. Assessment of Each Operator-Proposed Fix

### (a) Make the BINDING check the publisher/DOI-registry page, not secondary DBs

**Feasibility: YES, but requires new infra.**

The current script (`openalex_check.py`) already receives the DOI from OpenAlex and stores it in the JSONL output. Adding a DOI resolution step is a contained change to `openalex_check.py`:

1. After finding a VERIFIED or RESOLVED match, call `https://doi.org/{doi}` (or `https://api.crossref.org/works/{doi}`) and confirm the response HTTP status is 2xx and the returned title matches within some tolerance.
2. If the DOI doesn't resolve (404, NXDOMAIN, timeout) → downgrade the OpenAlex VERIFIED verdict to MISS and run the WebSearch fallback from there.
3. For the WebSearch-RESOLVED path, instruct the agent to `WebFetch` the captured URL and confirm the page title/authors match.

This is the correct fix because it binds the verdict to a source that the hallucination cannot fake: `doi.org` and CrossRef are the true registries; OpenAlex merely mirrors them. A fabricated paper will not have a registered DOI.

**Caveat:** working papers (SSRN, NBER, arXiv) often lack DOIs before publication. The fix must treat missing-DOI papers differently — apply the WebFetch step to the SSRN/NBER/arXiv URL captured during the WebSearch fallback, not the DOI path.

The bib-verify skill body and agent body also need updates to reflect the new binding-check step so agents understand why a paper with a high OpenAlex similarity can still be downgraded.

**Files to change:** `templates/utils/bib_verify/openalex_check.py` (add DOI resolution), `templates/utils/bib_verify/verify_bib.sh` (pass DOI through or call the resolver), `templates/skill_bodies/bib_verify/bib-verify.md` (document new VERIFIED-DOI-CONFIRMED vs VERIFIED-OPENALEX-ONLY status), `templates/agent_bodies/shared/bib-verifier.md` (explain the new statuses to the agent).

### (b) Fire the check the moment a citation is INTRODUCED, not near the end

**Feasibility: YES for Stage 5 (already partially done), HARDER for Stages 0–4.**

Stage 5 step 6 already fires bib-verifier immediately after the initial paper draft — this is a correct partial implementation of the operator's intent. The gap is upstream: citations are introduced into `literature_map.md` (Stage 0), `selected_idea.md` (Stage 1), `theory_draft.md` (Stage 2), and `implications.md` (Stage 3) without any verification step. These pre-draft artifacts are the source of the ~17-file propagation.

The structural difficulty is that upstream artifacts are not in BibTeX or Markdown-citation format — they are prose summaries with inline author-year citations. The current bib_verify script handles `.bib` and `.md` citation-list formats, not inline prose with mixed-format citations. Extending it to verify every inline citation in upstream stage artifacts requires either:
  - Extending the plain-text parser in `openalex_check.py` (the `parse_plain` function at lines 78–102 is already designed for this; it handles freeform citation lines)
  - Or instructing the literature-scout and gap-scout to output a separate verifiable citation list alongside their prose, which bib-verifier can check before the prose is committed

The minimum viable version of fix (b) is: after literature-scout writes `output/stage0/literature_map.md`, have the orchestrator immediately call bib-verifier on a citation list extracted from that file (the scout already lists papers in a structured way; the plain-mode parser can handle it). This fires before the cite propagates into downstream stage artifacts.

**Files to change:** `templates/shared/docs/stage_0.md` (add a "verify citations in literature_map.md" step after literature-scout completes), and analogously in `stage_1.md` if novelty-checker or idea-generator add new cites. The skill and verifier scripts are already capable; only the orchestrator doc needs the trigger.

---

## 5. Concrete Fix Direction

### Priority 1 (binding-check): add DOI resolution to `openalex_check.py`

In `verify()` (line 118), after the current VERIFIED/RESOLVED determination and before emitting the output dict, add:

```python
doi = match.get("doi", "")
if doi:
    status, note = resolve_doi(doi, cited_title)   # new helper
    if status == "NOT_FOUND":
        # Downgrade: OpenAlex matched something but DOI doesn't resolve
        out["status"] = "MISS"
        out["note"] = f"DOI {doi} does not resolve at doi.org (OpenAlex false positive?)"
    elif status == "TITLE_MISMATCH":
        out["status"] = "RESOLVED"
        out["note"] = f"DOI resolved but publisher title differs from OpenAlex title"
```

The `resolve_doi` helper calls `https://doi.org/{doi}` with `Accept: application/json` (Crossref content negotiation) and compares the returned `title` against `cited_title` using the same `title_similarity` function already in the script. This adds one HTTPS round-trip per VERIFIED citation; with the existing `rate_delay=0.12s`, total runtime for a 40-cite bibliography grows by roughly 5–10 seconds, which is negligible.

For the bib-verifier agent body, add a VERIFIED-DOI-CONFIRMED status to the JSONL rubric and instruct the agent that any VERIFIED entry that lacks a DOI (working papers) must have its WebSearch RESOLVED-VIA-WEBSEARCH URL fetched to confirm the page title matches.

### Priority 2 (early-fire): add a post-scout citation check step to stage_0.md

After Stage 0 Step 1 (literature-scout writes `output/stage0/literature_map.md`), add:

```
1b. **Scout citation spot-check.** Extract the citation list from literature_map.md 
(any line of the form "Author (Year). Title. Venue." or equivalent) and pass it to 
bib-verifier in --plain mode: `code/utils/bib_verify/verify_bib.sh output/stage0/literature_map.md`. 
If LIKELY FABRICATIONS > 0, re-launch literature-scout with the fabricated-cite list before 
proceeding. A fabrication caught here cannot propagate into downstream stage artifacts.
```

The plain-mode parser in `openalex_check.py` (the `parse_plain` function, lines 78–102) already handles freeform citation lines; this requires no script changes. The same pattern applies to Stage 1 after novelty-checker writes its output (which references competitor papers by title/author).

### Priority 3 (agent instruction): distinguish RESOLVED from VERIFIED in the agent body

The current bib-verifier instruction treats RESOLVED entries as "glance at the matched venue/authors" — a soft prompt instruction with no required action. The fix: require that for any RESOLVED entry, the agent fetches the `url` field from the JSONL and confirms the landing page title matches the cited title. This is a one-line WebFetch call per RESOLVED entry and turns a "glance" into a binding check.

---

## 6. File Targets Summary

| File | Change needed |
|---|---|
| `templates/utils/bib_verify/openalex_check.py` | Add `resolve_doi()` helper; downgrade VERIFIED to MISS when DOI doesn't resolve at `doi.org` |
| `templates/utils/bib_verify/verify_bib.sh` | Pass through DOI-resolution status in JSONL; add VERIFIED-DOI-CONFIRMED / VERIFIED-NO-DOI status codes |
| `templates/skill_bodies/bib_verify/bib-verify.md` | Document new status codes; require WebFetch confirmation for RESOLVED entries |
| `templates/agent_bodies/shared/bib-verifier.md` | Explain new DOI-confirmed vs. OpenAlex-only statuses; require URL fetch for RESOLVED entries |
| `templates/shared/docs/stage_0.md` | Add step 1b: post-scout bib-verify pass on literature_map.md |
| `templates/shared/docs/stage_1.md` | (Lower priority) Add a citation spot-check after novelty-checker if it introduces new cites |

The `polish-bibliography` agent does not need structural changes — it already does content verification via OpenAlex. But it should be updated to note that for any cite bib-verifier marked VERIFIED-NO-DOI, the polish-bibliography agent should attempt a WebFetch of the abstract URL as a content-existence check, not just a prose-claim check.

---

## 7. Summary (8 lines)

The symptom is REPRODUCED against current HEAD. The entire verification chain is OpenAlex title-search + LLM-driven WebSearch; no DOI/publisher-registry call is made anywhere — the DOI OpenAlex returns is printed in the report but never resolved. A fabricated paper can pass as VERIFIED if it collides with a real paper on title similarity, and a misattributed paper is VERIFIED by definition (it has the right title, the wrong claim). The first bib-verifier call fires at Stage 5 step 6, after the initial paper draft; citations enter the pipeline at Stage 0 (literature-scout) and propagate through all upstream stage artifacts with no verification, making the ~17-file propagation fully consistent with the current firing schedule. Fix (a) — DOI/publisher binding — requires adding a `doi.org` resolution step to `openalex_check.py` and updating the skill/agent bodies; the DOI is already available in the JSONL, so this is a contained change. Fix (b) — fire at introduction — requires adding a post-scout bib-verify step to `stage_0.md`; the plain-mode parser in `openalex_check.py` already supports freeform citation input and no script changes are needed. Both fixes are feasible, non-overlapping, and should be implemented together: (b) catches fabrications before propagation, (a) closes the OpenAlex-false-positive gap that lets misattributed papers through at any check point.
