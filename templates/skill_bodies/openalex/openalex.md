## What this is

A CLI wrapper over the OpenAlex API (~250M scholarly works, free, no key) for **deterministic, hallucination-free literature queries**. Backing script: `code/utils/openalex/openalex.py`. Reads `EMAIL` from `.env` for the polite pool.

Use this whenever you want a structured slice of the literature: top-cited papers in a topic, recent published work in a specific venue, citation traversal, or an author's bibliography. Every result has a real DOI, real venue, real year — straight from the database.

## When to use OpenAlex (not WebSearch)

- Finding the most-cited papers on a topic in top journals
- Surveying recent (last 5–10y) published work in JF/JFE/RFS/AER/QJE/JPE/etc.
- Forward citations of a seminal paper ("what built on this?")
- Backward references of a paper ("what did this build on?")
- Pulling all of an author's top papers in top venues

## When to keep using WebSearch

- Very recent uploads (last few days, before DOI registration)
- Working papers without DOIs
- Grey literature: blog posts, conference talks, news coverage
- General context not in academic papers

The two are complementary. A good workflow seeds the literature with citation-sorted OpenAlex queries (verified canonical work) and uses WebSearch for recency / commentary / grey literature.

## Commands

```
openalex.py search <query> [--venue ...] [--years YYYY-YYYY] [--top N] [--sort cited|relevance] [--abstracts]
openalex.py cites <work-id>  [--venue ...] [--years ...] [--top N] [--abstracts]
openalex.py refs  <work-id>  [--top N] [--abstracts]
openalex.py author <name>    [--venue ...] [--years ...] [--top N] [--abstracts]
openalex.py work  <work-id>  [--abstracts]
openalex.py venues
```

`<work-id>` accepts `W123...`, `https://openalex.org/W...`, or `doi:10.xxx/yyy`.

Add `--json` to any command to emit one JSON object per result (for piping to scripts).

`--json` also carries enriched bibliographic fields useful for metadata extraction: `author_details` (per author `name`, `orcid` when OpenAlex has one, which it frequently does even where Crossref returns none, and `institutions`), plus `topics` for subject classification. OpenAlex `topics` are accurate subfield labels (a usable substitute where a venue prints no JEL codes, for example The Journal of Finance). The legacy `concepts` field is deliberately not emitted: OpenAlex has deprecated it, and it keyword-matches on the title so noisily (`Forestry` for a paper titled "Forest through the Trees") that even a score filter leaves junk — use `topics`.

Add `--abstracts` to pull and reconstruct each work's abstract from OpenAlex's inverted index. The abstract is appended below each entry in the human view, and shows up as an `"abstract"` field in `--json`. Default is off because abstracts add real bandwidth — turn it on when reading what a paper actually says matters (novelty triage, deciding what to cite, comparing a closely-related paper to your contribution); leave it off for citation-graph traversal. Not every record has one: paywalled venues and some pre-2010 papers are missing from OpenAlex; the CLI prints `(no abstract available)` in those cases and emits `"abstract": null` in JSON.

## Venue aliases

```
Finance:    jf, jfe, rfs, jfqa, raps, rcfs, ms
Economics:  aer, qje, jpe, ecma, restud
Macro:      jme
```

Run `openalex.py venues` to see resolved source IDs and works counts. You can also pass an explicit OpenAlex source ID (`S123...`) or a literal journal name.

## Common patterns

```bash
# Top-cited papers in JF/JFE/RFS on a topic, last 10 years
code/utils/openalex/openalex.py search "intermediary asset pricing" \
    --venue jf,jfe,rfs --years 2015-2026 --top 25 --sort cited

# Recent activity in top finance venues (relevance, not citations)
code/utils/openalex/openalex.py search "machine learning return prediction" \
    --venue jf,jfe,rfs --years 2022-2026 --top 15 --sort relevance

# What cited a seminal paper, restricted to top venues
code/utils/openalex/openalex.py cites doi:10.1111/jofi.12189 \
    --venue jf,jfe,rfs,aer,qje,jpe --top 20

# What a key paper builds on
code/utils/openalex/openalex.py refs doi:10.1086/424739 --top 30

# All works by an author in top venues
code/utils/openalex/openalex.py author "Stefano Giglio" \
    --venue jf,jfe,rfs,aer,qje,jpe --top 10

# Pull abstracts to actually read what a small shortlist of candidates argues
code/utils/openalex/openalex.py search "intermediary asset pricing" \
    --venue jf,jfe,rfs --years 2018-2026 --top 5 --sort cited --abstracts

# Read one paper's abstract (e.g., before citing it in a related-work paragraph)
code/utils/openalex/openalex.py work doi:10.1093/rfs/hhaa009 --abstracts

# Find a paper's replication package or a named dataset (use --type dataset)
code/utils/openalex/openalex.py search "Gopinath Stein trade invoicing" --type dataset --top 5
```

**Datasets.** `--type dataset` filters to dataset records (ICPSR replication packages, Fed/government deposits, Harvard Dataverse, Zenodo, etc.). Use it for *targeted* lookups: finding the replication data of a specific paper, or verifying a named-dataset cite resolves. It is noisy for generic topical searches ("find me a dataset on X") — Figshare/PsycEXTRA-uploaded papers are often tagged as datasets and crowd out the canonical ones; use WebSearch for that.

## Caveats

- **Relevance sort is noisy without a venue filter.** OpenAlex's relevance score across the whole 250M-doc corpus surfaces tangential papers. For canonical work, use `--sort cited` and filter to top venues; for recency, filter to the years/venues of interest first, then sort by relevance.
- **Duplicate hits.** OpenAlex sometimes returns both the SSRN preprint and the published version of the same paper. Treat them as the same entry when building the literature map.
- **Online-first vs print year.** Recent JPE/QJE/RFS papers may show OpenAlex year = print year − 1 (Crossref online-first date). The verifier's ±1 year tolerance handles this; for literature listings just be aware.
- **Coverage gap.** OpenAlex misses very fresh uploads (< 24–48h before DOI registration), some pre-2018 NBER papers, and most grey literature. Fall back to WebSearch when you're hunting in those zones.
