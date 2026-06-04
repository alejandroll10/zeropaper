## What this is

A bibliography sanity check. Verifies every citation in the paper's references file against OpenAlex (a free bibliographic database covering ~250M scholarly works). Catches hallucinated, mistitled, or wrong-year citations before they ship.

Backing script: `code/utils/bib_verify/verify_bib.sh`. Reads `EMAIL` from `.env` for the OpenAlex polite pool.

## When to use

- After paper-writer finishes a draft and after every referee round that adds or changes citations.
- Before the pipeline marks `"status": "complete"`.
- Ad hoc whenever you want to sanity-check a bibliography (`/bib-verify` from the user, or `code/utils/bib_verify/verify_bib.sh` from any agent).

## How to run

```bash
# Auto-detects references/references.md, paper/references.md,
# references/references.bib, or paper/references.bib (in that order —
# .md first matches paper-writer's canonical path).
code/utils/bib_verify/verify_bib.sh

# Or pass an explicit file
code/utils/bib_verify/verify_bib.sh paper/references.bib
code/utils/bib_verify/verify_bib.sh references/references.md
```

Outputs:
- `output/bib_verification.md` — human-readable report grouped by status
- `output/bib_verification.jsonl` — one JSON object per entry (for machine triage)

## Status meanings

| Status | What it means | What to do |
|--------|---------------|------------|
| **VERIFIED** | OpenAlex returned a hit with title similarity ≥ 0.85 and matching year. If the match has a DOI, Crossref was also queried and the title/authors are consistent (`doi_confirmed: true`). High confidence the paper exists as cited. | Nothing. Move on. |
| **RESOLVED** | Title similarity 0.60–0.85, or year off by >1. Probably the same paper, but the cite is sloppy. Crossref still ran and the DOI is consistent (or the match had no DOI). | Read the matched title/venue. If it's clearly the right paper with a typo in the cite, fix the cite. If not, demote to MISS and triage. |
| **MISS** | One of: (a) no good OpenAlex match, (b) OpenAlex matched but Crossref disagreed on title or authors (`doi_confirmed: false`, see the `note` for the mismatch) — i.e. a title collision with a real paper that is **not** the cited one, (c) SSRN-only working paper not indexed, (d) very recent (last few months), (e) fabricated. | Read the `note`: a `doi-mismatch` MISS is strong evidence the cite is fabricated or misattributed. Otherwise run the SSRN/WebSearch fallback below; only mark as fabricated after the fallback also fails. |

The `doi_confirmed` field on each JSONL entry is `true` (Crossref agreed), `false` (Crossref disagreed — already demoted to MISS), or `null` (the OpenAlex match had no DOI, or Crossref was unreachable — see the `note`).

## SSRN / WebSearch fallback for MISS entries

OpenAlex has weak coverage of SSRN-only working papers and very recent preprints. So a MISS is not automatic evidence of fabrication — but the burden of proof shifts to confirming the paper exists.

For each MISS:

1. **WebSearch** the title in quotes. Try variants:
   - `"Exact Title Of Paper" author-last-name`
   - `"Exact Title" site:ssrn.com`
   - `"Exact Title" site:nber.org`
   - `"Exact Title" site:arxiv.org`
2. If a real result appears (matching title + plausible authors + year), the cite is real but unindexed by OpenAlex. Mark it RESOLVED-VIA-WEBSEARCH and capture the URL.
3. If WebSearch also returns nothing matching, mark it FABRICATED.

**Be honest at this step.** A vague hit ("paper with similar topic by different author") is not a confirmation. The whole point of verification is to catch hallucinations; don't soften the verdict to avoid the work of removing a cite.

## Final triage report

After both passes, write a triage section to `output/bib_verification.md` (append, don't overwrite the script-generated content):

```markdown
## Triage

### Confirmed (no action)
- N entries VERIFIED by OpenAlex
- M entries RESOLVED-VIA-WEBSEARCH — list one line per cite so downstream agents can find each key and its URL:
  - `keyA`: https://... (WebSearch match: title + authors + year)
  - ...

### Cite fixes needed
- `key1`: title typo — change "..." → "..."
- `key2`: wrong year — change 2019 → 2020
- ...

### Likely fabrications (remove or replace)
- `key3`: "..." — no OpenAlex hit, no WebSearch match. Likely hallucinated.
- ...
```

## Rules

- **Don't accept the verdict blindly.** OpenAlex can return a high-similarity match for the wrong paper (common-title collisions). The Crossref DOI check closes most of this gap — a `doi-mismatch` note on a MISS means the OpenAlex hit was on a different paper than the cite — but for RESOLVED entries with `doi_confirmed: null` (no DOI, e.g. SSRN/NBER), still glance at venue and authors.
- **Don't auto-edit the bibliography.** Report findings; let the caller (paper-writer or human) decide how to fix. Editing `.tex` or the references file is downstream of this skill's job.
- **EMAIL is required for the polite pool.** If `EMAIL` is missing from `.env`, the script still works but rate limits are tighter and lookups may fail. Warn if you notice many `api-error` notes in the report.
- **MISS ≠ fabricated.** Always run the WebSearch fallback before declaring fabrication. False accusations of fabrication are as bad as missing real ones.
