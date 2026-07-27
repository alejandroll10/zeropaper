#!/usr/bin/env python3
"""Look up a single citation against OpenAlex.

Reads one or more citations from stdin (one JSON object per line, schema:
  {"key": "Smith2020", "title": "...", "authors": ["..."], "year": 2020}
or, in --plain mode, one free-text citation per line).

Writes one JSON result per input line to stdout:
  {"key": ..., "status": "VERIFIED|RESOLVED|MISS", "openalex_id": ...,
   "matched_title": ..., "doi": ..., "url": ..., "venue": ..., "year": ...,
   "similarity": float, "cited": {...}, "note": "..."}

Reads OPENALEX_API_KEY and EMAIL from .env at the project root (or the env).
The key buys a usable daily credit budget — see the budget note below.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

OPENALEX = "https://api.openalex.org/works"
CROSSREF = "https://api.crossref.org/works/"
TIMEOUT = 12

# ── OpenAlex credit budget (why this script prefers DOIs) ────────────────────
# Since 2026-02-24 OpenAlex bills a daily CREDIT budget instead of capping
# request rate: 10,000 credits/day with an OPENALEX_API_KEY, 1,000/day keyless
# (a demo tier shared per-IP, which is how concurrent pipelines used to exhaust
# it collectively — issue #179). Measured per-call costs:
#
#   /works/doi:{doi}  or  /works/W{id}   0 credits   ← canonical single entity
#   /works?filter=doi:{doi}              1 credit    (list endpoint)
#   /works?filter=title.search:{title}  10 credits   ← what a title lookup costs
#
# So resolving a cite by its DOI is FREE and a title search is not. `verify()`
# tries the DOI path first whenever the .bib carried a `doi` field, and falls
# back to (or cross-checks with) a search when there is no DOI, the DOI doesn't
# resolve, or the DOI's paper doesn't match the cited title. A DOI-bearing
# bibliography whose DOIs actually match their titles therefore verifies at zero
# credit cost; each stale or wrong DOI costs the usual 10 for its cross-check.
#
# Crossref is separate and still rate-based (10 req/s, no daily cap).
#
# Backoff therefore covers transient 5xx and short 429s, not a per-second cap
# (which no longer bites). Jitter keeps concurrent callers from retrying in
# lockstep. A short Retry-After is honored; a budget-exhaustion one (hours)
# raises OpenAlexBudgetExhausted rather than being slept off.
RETRIES = 10
BACKOFF = 1.5
BACKOFF_CAP = 30.0  # don't sleep longer than this per attempt


def _retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    """Parse a Retry-After header (delta-seconds form) off a 429/503, if present."""
    raw = exc.headers.get("Retry-After") if exc.headers else None
    if not raw:
        return None
    try:
        secs = float(raw.strip())
    except ValueError:
        return None  # HTTP-date form — fall back to our own backoff
    return secs if secs >= 0 else None  # never feed a negative to time.sleep()


class OpenAlexBudgetExhausted(RuntimeError):
    """A 429 whose Retry-After is far too long to wait out.

    OpenAlex's daily-budget limiter sends Retry-After = seconds-until-midnight-UTC
    (up to ~24h). Sleeping on that stalls the whole verify run — it is the
    mechanism behind the observed "55+ min, 0/18 entries processed, then killed"
    in issue #179. Raise instead, so verify() records an explicit api-error for
    the entry and the caller falls back to WebSearch.

    Carries retry_after for parity with openalex.py's OpenAlexRateLimited, which
    is the same fix mirrored in the literature-query client.
    """

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


def _raise_if_budget_exhausted(retry_after: float | None, code: int) -> None:
    """Bail immediately on a budget-exhaustion 429 rather than sleeping it off.

    Scoped to 429: a 5xx carrying a long Retry-After is a transient outage, not
    budget exhaustion, so it takes the normal capped-backoff path.
    """
    if code == 429 and retry_after is not None and retry_after > BACKOFF_CAP:
        tier = (
            "$1/day keyed budget"
            if load_env_api_key()
            else "$0.10/day KEYLESS demo budget (shared across this whole host IP) "
                 "— set OPENALEX_API_KEY in .env for 10x more"
        )
        raise OpenAlexBudgetExhausted(
            f"OpenAlex daily credit budget exhausted on the {tier}; "
            f"Retry-After={retry_after:.0f}s (~{retry_after / 3600:.1f}h), resets 00:00 UTC. "
            f"Not waiting — fall back to WebSearch for this entry.",
            retry_after=retry_after,
        )


def _backoff_sleep(attempt: int, retry_after: float | None) -> None:
    """Sleep before the next attempt: honor Retry-After, else exponential + jitter.

    Every sleep is capped at BACKOFF_CAP. A server-sent Retry-After can be hours
    (see OpenAlexBudgetExhausted); the callers bail on those before reaching
    here, and this cap is the second line of defense so no single attempt can
    stall a verify run.
    """
    window = min(BACKOFF * (2 ** attempt), BACKOFF_CAP)
    delay = retry_after if retry_after is not None else random.uniform(0, window)
    time.sleep(min(delay, BACKOFF_CAP))

# Surname-token noise to strip. Replaces the old `len >= 3` filter, which
# silently discarded short *real* surnames (Li, Wu, Bo, Ma, He, An, Xi) and so
# could not anchor an author check on them (issue #54). Tokens are matched
# post-normalize_title (lowercased, punctuation stripped), so all entries are
# lowercase. Two distinct classes, handled differently by `_filter_particles`:
#
# - Generational suffixes (jr, sr, iii) are NEVER a surname, so they are dropped
#   unconditionally — even when they are the only token. ("John Jr" must NOT
#   leave a spurious {jr} surname signal that can false-demote a 1-author cite.)
# - Name particles (de, van, da) CAN be a real standalone surname in some
#   traditions (Vietnamese "Do"/"Da", rare "De"/"Di"). They are dropped only
#   when a non-particle token co-occurs, so "da Silva" reduces to {silva} while
#   a standalone "Do" keeps {do}.
_GENERATIONAL_SUFFIXES = frozenset({
    "jr", "sr", "jnr", "snr", "ii", "iii", "iv",
})
_SURNAME_PARTICLE_STOPLIST = frozenset({
    "de", "di", "du", "da", "del", "della", "dos", "das", "do",
    "la", "le", "el", "lo", "von", "van", "der", "den", "ter", "ten",
    "af", "av", "al", "bin", "ibn", "abu", "mac", "mc",
})


def _filter_particles(tokens: set[str]) -> set[str]:
    """Strip generational suffixes (always) and name particles (if not all).

    Generational suffixes (jr/iii) are dropped unconditionally — they are never
    a surname. Name particles are dropped only when a non-particle token remains,
    so a standalone "Do"/"De" surname keeps its token (the particle IS the
    signal). Residual risk: two distinct authors that each reduce to the same
    bare particle would intersect in `author_overlap`; this needs a malformed
    Crossref `family` field that is only a particle (e.g. "van", "al") — well-
    formed records carry a non-particle token that wins — so exposure is
    negligible.
    """
    tokens = {t for t in tokens if t and t not in _GENERATIONAL_SUFFIXES}
    kept = {t for t in tokens if t not in _SURNAME_PARTICLE_STOPLIST}
    return kept or tokens


def _load_env(name: str) -> str:
    """Read `name` from the environment, else from the nearest .env walking up.

    Stops at the first .env found (a project root shadows anything above it).
    """
    val = os.environ.get(name, "").strip().strip('"').strip("'")
    if val:
        return val
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        env = parent / ".env"
        if env.is_file():
            for line in env.read_text().splitlines():
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    return ""


def load_env_email() -> str:
    return _load_env("EMAIL")


_api_key_cache: str | None = None


def load_env_api_key() -> str:
    """OPENALEX_API_KEY, cached (read once per process, used on every call)."""
    global _api_key_cache
    if _api_key_cache is None:
        _api_key_cache = _load_env("OPENALEX_API_KEY")
    return _api_key_cache


def _openalex_request(url: str) -> urllib.request.Request:
    """Build an OpenAlex request, authenticating via header when a key is set.

    The key goes in Authorization rather than the query string so it stays out
    of the error messages below (which embed the URL) and out of any logs.
    """
    headers = {}
    api_key = load_env_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return urllib.request.Request(url, headers=headers)


def _clean_doi(doi: str) -> str:
    """Strip URL/scheme wrappers off a DOI, leaving the bare 10.x/suffix form.

    Prefixes are stripped from the front only — a global replace would corrupt a
    DOI suffix that happened to contain one of these substrings.
    """
    out = (doi or "").strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/",
                   "http://dx.doi.org/", "doi:"):
        if out.lower().startswith(prefix):
            out = out[len(prefix):]
            break
    return out.strip().rstrip(".,;:")


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9 ]+", " ", title)
    return " ".join(title.split())


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def fetch_openalex_by_doi(doi: str, mailto: str) -> dict | None:
    """Resolve a work by DOI via the canonical single-entity path (0 credits).

    Returns the work dict, or None when the DOI is empty or OpenAlex doesn't
    have it (404 — a real "not indexed" answer, so the caller should fall back
    to the title search). Raises only on a genuine transport/limit failure, so
    a budget-exhaustion 429 is not silently mistaken for "DOI unknown".

    Note the URL form matters for cost: `/works/doi:{doi}` is free, while the
    `/works/https://doi.org/{doi}` alias and `?filter=doi:` both bill 1 credit.
    """
    doi_id = _clean_doi(doi)
    if not doi_id:
        return None
    params = {"mailto": mailto} if mailto else {}
    url = f"{OPENALEX}/doi:{urllib.parse.quote(doi_id, safe='/')}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    last_err: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(_openalex_request(url), timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_err = exc
            # 404 = OpenAlex genuinely lacks this DOI. That is an answer, not a
            # fault: report it as a miss so verify() pays for a title search.
            if exc.code == 404:
                return None
            if exc.code != 429 and exc.code < 500:
                break
            retry_after = _retry_after_seconds(exc)
            _raise_if_budget_exhausted(retry_after, exc.code)
            if attempt < RETRIES:
                _backoff_sleep(attempt, retry_after)
        except Exception as exc:
            last_err = exc
            if attempt < RETRIES:
                _backoff_sleep(attempt, None)
    raise RuntimeError(f"OpenAlex DOI lookup failed: {last_err}")


def query_openalex(title: str, mailto: str) -> list[dict]:
    """Title search — 10 credits per call. Prefer fetch_openalex_by_doi first."""
    params = {"search": title, "per-page": "3"}
    if mailto:
        params["mailto"] = mailto
    url = f"{OPENALEX}?{urllib.parse.urlencode(params)}"
    last_err: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(_openalex_request(url), timeout=TIMEOUT) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return payload.get("results", []) or []
        except urllib.error.HTTPError as exc:
            last_err = exc
            # Retry only rate-limit (429) and server (5xx) errors; other 4xx
            # (e.g. 400/404) are deterministic, so don't waste retries on them.
            if exc.code != 429 and exc.code < 500:
                break
            retry_after = _retry_after_seconds(exc)
            _raise_if_budget_exhausted(retry_after, exc.code)
            if attempt < RETRIES:
                _backoff_sleep(attempt, retry_after)
        except Exception as exc:
            last_err = exc
            if attempt < RETRIES:
                _backoff_sleep(attempt, None)
    raise RuntimeError(f"OpenAlex query failed: {last_err}")


def parse_plain(line: str) -> dict:
    """Best-effort parse of a freeform citation into {key, title, authors, year}.

    Expected (loose) shape:
      Author, Author2 (Year). "Title." Journal/Venue. <url-or-tag>
    Falls back to using the entire line as the title.
    """
    raw = line.strip()
    if not raw:
        return {}
    year_match = re.search(r"\((\d{4})\)", raw)
    year = int(year_match.group(1)) if year_match else None
    title = raw
    quote_match = re.search(r'["“]([^"”]+)["”]', raw)
    if quote_match:
        title = quote_match.group(1).strip().rstrip(".")
    else:
        if year_match:
            tail = raw[year_match.end():].lstrip(" .")
            tail = tail.split(".")[0]
            if len(tail) > 12:
                title = tail.strip()
    authors_part = raw.split("(", 1)[0].strip().rstrip(",")
    authors = [a.strip() for a in re.split(r",| and ", authors_part) if a.strip()] if authors_part else []
    return {"key": title[:60], "title": title, "authors": authors, "year": year}


def fetch_crossref(doi: str, mailto: str) -> dict | None:
    """Fetch a DOI from Crossref. Returns the `message` dict, or
    {"_error": "..."} on failure, or None if the DOI is empty/malformed."""
    if not doi:
        return None
    doi_id = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
    if not doi_id:
        return None
    url = CROSSREF + urllib.parse.quote(doi_id, safe="/")
    ua = f"bib-verify/1.0 (mailto:{mailto})" if mailto else "bib-verify/1.0"
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    last_err: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8")).get("message")
        except urllib.error.HTTPError as exc:
            last_err = exc
            # A 404 here is a real "DOI not in Crossref" answer, not a transient
            # fault — don't retry deterministic 4xx; only 429/5xx are worth it.
            if exc.code != 429 and exc.code < 500:
                break
            if attempt < RETRIES:
                _backoff_sleep(attempt, _retry_after_seconds(exc))
        except Exception as exc:
            last_err = exc
            if attempt < RETRIES:
                _backoff_sleep(attempt, None)
    return {"_error": f"crossref-fetch-failed: {last_err}"}


def _surname_tokens(author: str) -> set[str]:
    """Extract surname word-tokens from a freeform author string.

    Normalization folds hyphens, spaces, and punctuation to a single space (via
    `normalize_title`), so "Lopez-Lira" and "Lopez Lira" both yield {lopez, lira}.
    Name particles and generational suffixes (de/di/le, jr/iii) are dropped via
    `_SURNAME_PARTICLE_STOPLIST` rather than by length, so short real surnames
    (Li, Wu, He, Ma) are kept and can anchor the author check (issue #54).
    One-character initials are also caught by the pre-norm `[A-Z]\\.?` filter on
    the last raw segment.

    Name order: a comma signals "Lastname, Firstname" order (the BibTeX default),
    so the surname is the segment *before* the first comma. Without a comma the
    string is "Firstname ... Lastname" order and the surname is the last token.
    (Issue #105: the old code split on whitespace/comma/period together,
    discarding the comma, and always took the last token — which is the *given*
    name in "Lastname, Firstname" entries, yielding doi_author_overlap=0.0 and
    systematic false MISS verdicts.)
    """
    author = author.strip()
    if "," in author:
        # "Lastname, Firstname[, suffix]" — surname is the pre-comma segment
        # (keeps hyphenated/multiword surnames and standalone particles intact;
        # normalize_title + _filter_particles handle the rest).
        surname = author.split(",", 1)[0]
    else:
        raw_parts = [p for p in re.split(r"[\s.]+", author) if p]
        # Drop bare initials like "J." or "K"
        raw_parts = [p for p in raw_parts if not re.match(r"^[A-Z]\.?$", p)]
        if not raw_parts:
            return set()
        # Last raw segment carries the surname (incl. hyphenated/multiword).
        surname = raw_parts[-1]
    return _filter_particles(set(normalize_title(surname).split()))


def _crossref_surname_tokens(author: dict) -> set[str]:
    family = author.get("family") or ""
    return _filter_particles(set(normalize_title(family).split()))


def author_overlap(cited_authors: list[str], crossref_authors: list[dict]) -> float:
    """Fraction of cited authors whose surname tokens intersect any Crossref author's.

    Returns -1.0 when there is no signal on either side. A "match" requires
    whole-token set intersection (after dropping name particles), so unanchored
    substrings (e.g. "Li" ⊂ "Liang") cannot drive a false match.
    """
    cited_sets = [s for s in (_surname_tokens(a) for a in cited_authors or []) if s]
    if not cited_sets:
        return -1.0
    cr_sets = [s for s in (_crossref_surname_tokens(a) for a in crossref_authors or []) if s]
    if not cr_sets:
        return -1.0
    hits = sum(1 for c in cited_sets if any(c & f for f in cr_sets))
    return hits / len(cited_sets)


def best_match(cite: dict, results: list[dict]) -> tuple[dict | None, float]:
    cited_title = cite.get("title", "") or ""
    if not results or not cited_title:
        return None, 0.0
    scored = []
    for r in results:
        cand_title = r.get("title") or r.get("display_name") or ""
        sim = title_similarity(cited_title, cand_title)
        scored.append((sim, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1], scored[0][0]


def verify(cite: dict, mailto: str, threshold: float) -> dict:
    if not cite.get("title"):
        return {"key": cite.get("key", ""), "status": "MISS", "note": "no title to query",
                "lookup": "none", "credits": 0, "cited": cite}

    # Cheap path first: a cited DOI resolves for 0 credits where a title search
    # costs 10. The DOI only picks a *candidate* — it is still scored on title
    # similarity below, so a .bib pointing at the wrong paper gets no free pass.
    #
    # `lookup` records how much to trust the cited DOI, which is what a reviewer
    # needs for triage:
    #   "doi"      — DOI matched the cited title at >= threshold: trust it alone
    #   "doi-weak" — DOI matched below threshold, so the cite may name a
    #                different paper than its DOI points to. Needs human eyes
    #                whatever the final verdict (see the note for detail).
    #   "search"   — no usable DOI; resolved by title search alone
    # `credits` is what this entry actually cost, tracked at the call site so the
    # report can't overstate spend on a call that failed (and so was never billed).
    pre_notes: list[str] = []
    doi_work: dict | None = None
    match: dict | None = None
    sim = 0.0
    doi_sim = 0.0
    credits = 0
    lookup = "search"

    if cite.get("doi"):
        try:
            doi_work = fetch_openalex_by_doi(cite["doi"], mailto)
        except Exception as exc:
            # Transport/budget failure, not "DOI unknown" — fall through to the
            # search path, but keep the reason so an outage stays visible rather
            # than reading as a clean miss.
            pre_notes.append(f"doi-lookup-error: {exc}")
            doi_work = None
        if doi_work:
            match, sim = best_match(cite, [doi_work])
            doi_sim = sim
            lookup = "doi" if sim >= threshold else "doi-weak"

    # Accept the free DOI result unchallenged ONLY when it matches the cited
    # title at VERIFIED caliber. Below that bar the cited DOI may point at a
    # different paper (typo, companion paper, erratum, wrong copy-paste, or a
    # DOI scraped out of a link field), and taking it on faith would be *weaker*
    # than this function's pre-DOI behavior: the Crossref cross-check below
    # re-fetches the same DOI we started from, so it agrees with itself whenever
    # that DOI is real, and `doi_confirmed: true` would overclaim. So pay for
    # the title search and score the DOI candidate alongside the search hits.
    # The DOI candidate goes LAST so that on an exact title-similarity tie the
    # search hit wins, exactly as it did before the DOI path existed (best_match
    # sorts on title similarity only, and Python's sort is stable, so list order
    # decides ties — a stale-year DOI must not displace a correct-year hit).
    if match is None or sim < threshold:
        results: list[dict] = []
        try:
            results = query_openalex(cite["title"], mailto)
            credits += 10
        except Exception as exc:
            if match is None:
                note = "; ".join(pre_notes + [f"api-error: {exc}"])
                return {"key": cite.get("key", ""), "status": "MISS", "note": note,
                        "lookup": lookup, "credits": credits, "cited": cite}
            # Search unavailable but a weak DOI candidate is in hand: keep it and
            # flag it rather than discarding the only evidence we have. `lookup`
            # stays "doi-weak", so the entry is still routed for human review —
            # this failure clusters with budget exhaustion, the exact case where
            # a silently-trusted weak DOI would do the most damage.
            pre_notes.append(f"title-search-unavailable: {exc}")
        if results:
            if doi_work is not None:
                pre_notes.append(
                    f"cited doi matched the cited title only weakly "
                    f"(sim {doi_sim:.2f}); cross-checked against a title search"
                )
            match, sim = best_match(cite, results + ([doi_work] if doi_work else []))

    if match is None:
        return {
            "key": cite.get("key", ""),
            "status": "MISS",
            "note": "; ".join(pre_notes + ["no openalex results"]),
            "lookup": lookup,
            "credits": credits,
            "cited": cite,
        }
    matched_title = match.get("title") or match.get("display_name") or ""
    matched_year = match.get("publication_year")
    cited_year = cite.get("year")
    year_ok = (cited_year is None) or (matched_year is None) or abs(matched_year - cited_year) <= 1
    venue = ""
    primary = match.get("primary_location") or {}
    src = (primary.get("source") or {})
    if src.get("display_name"):
        venue = src["display_name"]
    status = "VERIFIED" if (sim >= threshold and year_ok) else ("RESOLVED" if sim >= 0.6 else "MISS")
    doi = match.get("doi")
    out = {
        "key": cite.get("key", ""),
        "status": status,
        "openalex_id": match.get("id"),
        "matched_title": matched_title,
        "doi": doi,
        "url": (primary.get("landing_page_url") or doi or match.get("id")),
        "venue": venue,
        "year": matched_year,
        "similarity": round(sim, 3),
        "doi_confirmed": None,
        "lookup": lookup,     # doi | doi-weak | search — see the note above
        "credits": credits,   # what this entry actually cost (0 or 10)
        "cited": cite,
    }
    notes: list[str] = list(pre_notes)
    if not year_ok:
        notes.append(f"year mismatch (cited {cited_year}, openalex {matched_year})")

    if doi and status != "MISS":
        cr = fetch_crossref(doi, mailto)
        if cr is None:
            notes.append("no-doi-on-match")
        elif cr.get("_error"):
            notes.append(cr["_error"])
        else:
            cr_title = (cr.get("title") or [""])[0]
            cr_authors = cr.get("author") or []
            t_sim = title_similarity(cite.get("title", ""), cr_title)
            a_overlap = author_overlap(cite.get("authors") or [], cr_authors)
            out["doi_title_similarity"] = round(t_sim, 3)
            out["doi_author_overlap"] = round(a_overlap, 3)
            out["doi_authors"] = [
                f"{a.get('given', '')} {a.get('family', '')}".strip()
                for a in cr_authors
            ]
            cited_author_count = sum(1 for a in (cite.get("authors") or []) if _surname_tokens(a))
            # Demote to MISS when DOI contradicts the cite:
            #   - title sim < 0.6, OR
            #   - author overlap is 0 with >=1 cited author carrying a usable surname.
            # The author branch fires on a single fabricated surname (issue #54
            # blind spot 1); a_overlap is 0.0 only when both sides carry surname
            # signal and none intersect (the no-signal case returns -1.0 and is
            # excluded by the == 0.0 test), so a real 1-author cite whose Crossref
            # romanization differs is the only false-demote risk — rare, and
            # caught by the bib-verifier WebSearch fallback on the resulting MISS.
            # Short real surnames (Li, Wu) are no longer dropped (blind spot 2),
            # so all-short-surname cites now carry signal too.
            if t_sim < 0.6 or (a_overlap == 0.0 and cited_author_count >= 1):
                out["status"] = "MISS"
                out["doi_confirmed"] = False
                notes.append(
                    f"doi-mismatch (crossref title sim {t_sim:.2f}, author overlap {a_overlap:.2f})"
                )
            else:
                out["doi_confirmed"] = True
    if notes:
        out["note"] = "; ".join(notes)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plain", action="store_true",
                    help="Each stdin line is freeform text; parse heuristically.")
    ap.add_argument("--threshold", type=float, default=0.85,
                    help="Title similarity threshold for VERIFIED (default 0.85).")
    ap.add_argument("--rate-delay", type=float, default=0.12,
                    help="Seconds to sleep between input entries (default 0.12). "
                         "OpenAlex no longer enforces a per-second cap — this is "
                         "politeness toward Crossref, which still does (10 req/s).")
    args = ap.parse_args()

    mailto = load_env_email()
    first = True
    for line in sys.stdin:
        if not first:
            time.sleep(args.rate_delay)
        first = False
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if args.plain:
            cite = parse_plain(line)
        else:
            try:
                cite = json.loads(line)
            except json.JSONDecodeError:
                cite = parse_plain(line)
        if not cite:
            continue
        result = verify(cite, mailto, args.threshold)
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
