## What this is

A CLI wrapper that fetches an **NBER conference agenda** as clean text or structured JSON. Backing script: `code/utils/nber_agenda/nber_agenda.py` (stdlib only, no key).

NBER conference pages (`nber.org/conferences/<slug>`) render their agenda client-side, so a plain fetch of the page returns only a `Loading...` placeholder — the papers are invisible to a scraper. The real agenda is served, fully rendered, by a separate host (`conference.nber.org`). This script does slug → hidden `conf_id` → parsed agenda in one shot, so the agenda is available without a browser.

Each paper row yields: title, authors + affiliations, discussant(s), and any uploaded paper/slide links.

## When to use this (not OpenAlex / WebSearch)

NBER meetings are a **leading indicator** of the research frontier: the agenda lists what top groups are presenting *now*, typically months before the work is published, indexed, or even has a DOI. Reach for this when you want:

- A read on what a field is actively working on this season (e.g. Summer Institute Asset Pricing, Forecasting & Empirical Methods, Monetary Economics).
- Frontier *techniques* — a methods conference agenda surfaces new estimators/identification strategies by title.
- The set of authors + institutions converging on a topic, to seed an author search.

Complementary to the other literature skills:

- **OpenAlex** — published, DOI-bearing work and citation structure. Use for the established literature.
- **WebSearch** — grey literature, news, working papers once they are public.
- **nber-agenda** — the pre-publication frontier: who is presenting what, right now.

A good scout workflow: skim a recent meeting agenda for the live frontier, then pull the specific papers/authors via OpenAlex (for published precursors) and WebSearch (for the working-paper PDF).

## Commands

```
nber_agenda.py <slug | url | conf_id> [--json] [--papers-only]
```

- `<slug>` — e.g. `si-2026-asset-pricing` (the tail of `nber.org/conferences/<slug>`)
- `<url>` — a full `https://www.nber.org/conferences/...` URL
- `<conf_id>` — e.g. `SI26AP` or `APs26`, if you already know it
- `--json` — structured records (`title`, `authors`, `discussants`, `links`) instead of text
- `--papers-only` — drop breaks/meals/session headings; keep only paper rows

## Finding a conference slug

Browse the conference index at `https://www.nber.org/conferences`, or a program page such as
`https://www.nber.org/programs-projects/programs-working-groups/asset-pricing` — each lists its
meetings, and every meeting URL ends in the slug. Summer Institute slugs follow the pattern
`si-<year>-<program>` (e.g. `si-2026-monetary-economics`); program meetings look like
`asset-pricing-program-meeting-spring-2026`.

## How it works (in case it breaks)

The conference page embeds a `conf_id=<ID>` in its "Print agenda" link. The script greps that
id (it can contain lowercase, e.g. `APs26`) and fetches
`https://conference.nber.org/agenda/simple_printable?conf_id=<ID>`, then parses the HTML table.
If NBER changes the markup, the `simple_printable` endpoint is still the thing to fetch; only the
parser would need updating. Agendas for future meetings populate a few weeks before the event —
before that, the endpoint returns the header with no paper rows.
