#!/usr/bin/env python3
"""Look up a single citation against OpenAlex.

Reads one or more citations from stdin (one JSON object per line, schema:
  {"key": "Smith2020", "title": "...", "authors": ["..."], "year": 2020}
or, in --plain mode, one free-text citation per line).

Writes one JSON result per input line to stdout:
  {"key": ..., "status": "VERIFIED|RESOLVED|MISS", "openalex_id": ...,
   "matched_title": ..., "doi": ..., "url": ..., "venue": ..., "year": ...,
   "similarity": float, "cited": {...}, "note": "..."}

OpenAlex is free and unauthenticated. Pass EMAIL via env var to enter the
polite pool (faster, more reliable). Reads .env at the project root if present.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

OPENALEX = "https://api.openalex.org/works"
CROSSREF = "https://api.crossref.org/works/"
TIMEOUT = 12
RETRIES = 2
BACKOFF = 1.5

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


def load_env_email() -> str:
    email = os.environ.get("EMAIL", "").strip().strip('"').strip("'")
    if email:
        return email
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        env = parent / ".env"
        if env.is_file():
            for line in env.read_text().splitlines():
                if line.startswith("EMAIL="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    return ""


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9 ]+", " ", title)
    return " ".join(title.split())


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def query_openalex(title: str, mailto: str) -> list[dict]:
    params = {"search": title, "per-page": "3"}
    if mailto:
        params["mailto"] = mailto
    url = f"{OPENALEX}?{urllib.parse.urlencode(params)}"
    last_err: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return payload.get("results", []) or []
        except Exception as exc:
            last_err = exc
            if attempt < RETRIES:
                time.sleep(BACKOFF * (attempt + 1))
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
        except Exception as exc:
            last_err = exc
            if attempt < RETRIES:
                time.sleep(BACKOFF * (attempt + 1))
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
        return {"key": cite.get("key", ""), "status": "MISS", "note": "no title to query", "cited": cite}
    try:
        results = query_openalex(cite["title"], mailto)
    except Exception as exc:
        return {"key": cite.get("key", ""), "status": "MISS", "note": f"api-error: {exc}", "cited": cite}
    match, sim = best_match(cite, results)
    if match is None:
        return {"key": cite.get("key", ""), "status": "MISS", "note": "no openalex results", "cited": cite}
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
        "cited": cite,
    }
    notes: list[str] = []
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
                    help="Seconds to sleep between API calls (default 0.12).")
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
