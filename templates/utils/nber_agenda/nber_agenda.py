#!/usr/bin/env python3
"""Fetch an NBER conference agenda as clean text or structured JSON.

NBER conference pages (nber.org/conferences/<slug>) render their agenda
client-side, so a plain fetch of the page returns only a "Loading..."
placeholder. The actual agenda is served, fully rendered, by a separate
host: conference.nber.org/agenda/simple_printable?conf_id=<ID>. The conf_id
is embedded in the conference page's "Print agenda" link.

This script does slug -> conf_id -> parsed agenda in one shot, so the
agenda is available without a browser.

Usage:
    nber_agenda.py <slug | url | conf_id> [--json] [--papers-only]

    <slug>     e.g. si-2026-asset-pricing  (from nber.org/conferences/<slug>)
    <url>      a full nber.org/conferences/... URL
    <conf_id>  e.g. SI26AP or APs26, if you already know it

    --json         emit structured records (title, authors, discussant, links)
    --papers-only  drop breaks/meals/session headings; keep only paper rows

Finding a slug: browse https://www.nber.org/conferences or a program page
such as https://www.nber.org/programs-projects/programs-working-groups/asset-pricing
(each lists its meetings, and each meeting URL ends in the slug).

Dependency-free (stdlib only).
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request

CONF_PAGE = "https://www.nber.org/conferences/{slug}"
AGENDA = "https://conference.nber.org/agenda/simple_printable?conf_id={cid}"
UA = {"User-Agent": "Mozilla/5.0 (nber_agenda.py; research pipeline)"}


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} fetching {url}")
    except urllib.error.URLError as e:
        sys.exit(f"network error fetching {url}: {e.reason}")


def resolve_conf_id(arg):
    """Map a slug / conference URL / conf_id to a conf_id."""
    # A bare conf_id has no slug separators or path; treat it as already resolved.
    if "-" not in arg and "/" not in arg:
        return arg
    slug = arg.split("/conferences/")[-1].split("?")[0].strip("/")
    page = _get(CONF_PAGE.format(slug=slug))
    # The conf_id can contain lowercase (e.g. APs26), so do NOT restrict to [A-Z].
    m = re.search(r"conf_id=([A-Za-z0-9]+)", page)
    if not m:
        sys.exit(f"could not resolve conf_id from slug: {slug}")
    return m.group(1)


def _strip(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_agenda(htmltext):
    """Parse simple_printable HTML into a header string + list of item dicts."""
    header = _strip(htmltext.split('<tr class="agenda-entry"', 1)[0])
    rows = re.split(r'<tr class="agenda-entry"', htmltext)[1:]
    items = []
    for row in rows:
        tm = re.search(r'agenda-entry__time"[^>]*>(.*?)</td>', row, re.S)
        time = _strip(tm.group(1)) if tm else ""
        title_m = re.search(r"<em>(.*?)</em>", row, re.S)
        if title_m:
            authors = [
                {"name": _strip(n), "affiliation": _strip(a)}
                for n, a in re.findall(
                    r'author-name[^"]*">(.*?)</span>\s*,?\s*'
                    r'(?:<span class="affiliation">(.*?)</span>)?',
                    row,
                    re.S,
                )
            ]
            discussants = [
                _strip(d) for d in re.findall(r'discussant-name">(.*?)</span>', row, re.S)
            ]
            # Only absolute links — uploaded paper/slide PDFs. Relative hrefs
            # in the row (author profiles, conference back-links) are noise.
            links = re.findall(r'href="(https?://[^"]+)"', row)
            items.append(
                {
                    "type": "paper",
                    "time": time,
                    "title": _strip(title_m.group(1)),
                    "authors": authors,
                    "discussants": discussants,
                    "links": links,
                }
            )
        else:
            info = re.search(r'agenda-entry__info"[^>]*>(.*?)</td>', row, re.S)
            text = _strip(info.group(1)) if info else ""
            if text:
                items.append({"type": "note", "time": time, "text": text})
    return header, items


def as_text(header, items):
    out = [header, ""]
    for it in items:
        if it["type"] == "note":
            out.append(f'  {it["time"]+"  " if it["time"] else ""}{it["text"]}')
        else:
            out.append(f'{it["time"]}  {it["title"]}')
            for a in it["authors"]:
                aff = f' — {a["affiliation"]}' if a["affiliation"] else ""
                out.append(f'    {a["name"]}{aff}')
            if it["discussants"]:
                out.append(f'    Discussant: {", ".join(it["discussants"])}')
            for ln in it["links"]:
                out.append(f'    link: {ln}')
            out.append("")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description="Fetch an NBER conference agenda.")
    p.add_argument("conf", help="conference slug, URL, or conf_id")
    p.add_argument("--json", action="store_true", help="emit structured JSON")
    p.add_argument("--papers-only", action="store_true",
                   help="keep only paper rows (drop breaks/meals/headings)")
    args = p.parse_args()

    cid = resolve_conf_id(args.conf)
    header, items = parse_agenda(_get(AGENDA.format(cid=cid)))
    if args.papers_only:
        items = [it for it in items if it["type"] == "paper"]

    if args.json:
        json.dump({"conf_id": cid, "header": header, "items": items},
                  sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        print(as_text(header, items))


if __name__ == "__main__":
    main()
