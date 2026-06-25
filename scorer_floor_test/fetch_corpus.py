#!/usr/bin/env python3
"""Freeze a snapshot of the IAR distilled-lit corpus for the scorer floor test (#102).

Build-time / maintenance tooling — lives in zeropaper only, never copied into a
deployed project (cf. scripts/resolve_model_fallbacks.py). It pulls the distilled
top-3 finance paper pages from the **live IAR wiki** and caches them under
corpus/raw/ as a *frozen* snapshot. The frozen snapshot — not the live site — is
what the reconstruction step reads, so the floor-test fixtures never drift when the
wiki changes (the #102 "built once, no feedback" rule).

Source: the public wiki at https://instituteforautomatedresearch.org/wiki, pages
under papers/{jf,rfs}/2025/. Each rendered page also serves its raw markdown (with
full YAML frontmatter — relatesTo / findings[] / resultType / outcome) at the same
URL with a `.md` suffix; that raw markdown is what we freeze. No auth required.

The page list is enumerated from the Starlight sidebar present in any rendered
page (the wiki has no machine index for the year dir, and the sitemap only lists
top-level pages).

Usage:
    python3 scorer_floor_test/fetch_corpus.py          # refresh the frozen snapshot
    python3 scorer_floor_test/fetch_corpus.py --check   # verify snapshot vs provenance, no write

No external CLI dependency — pure stdlib HTTP.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://instituteforautomatedresearch.org"
WIKI = f"{SITE}/wiki"
# Any real page works as the enumeration seed — its sidebar lists every sibling.
SEED_PAGE = f"{WIKI}/papers/jf/2025/betermier-investor-factors-2025/"
LINK_RE = re.compile(r"/wiki/papers/(jf|rfs)/2025/([a-z0-9][a-z0-9-]*)/")

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "corpus" / "raw"
PROVENANCE = ROOT / "corpus" / "PROVENANCE.json"


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "iar-floor-test-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def enumerate_pages():
    """Return sorted [(journal, slug)] for every jf/rfs 2025 paper in the sidebar."""
    html = http_get(SEED_PAGE)
    found = set(LINK_RE.findall(html))
    if not found:
        sys.exit("Could not enumerate papers from the sidebar — site layout may have changed.")
    return sorted(found)


def md_url(journal, slug):
    return f"{WIKI}/papers/{journal}/2025/{slug}.md"


def corpus_hash(files):
    """Deterministic content hash over the frozen pages (stand-in for a git SHA)."""
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(rel.encode())
        h.update(b"\0")
        h.update((RAW_DIR / rel).read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="Verify the frozen snapshot's files + content hash match the recorded "
        "provenance without re-downloading. Exit 1 on drift.",
    )
    args = ap.parse_args()

    if args.check:
        if not PROVENANCE.exists():
            sys.exit("No PROVENANCE.json — run fetch_corpus.py first to freeze a snapshot.")
        prov = json.loads(PROVENANCE.read_text())
        on_disk = sorted(p.relative_to(RAW_DIR).as_posix() for p in RAW_DIR.rglob("*.md"))
        if on_disk != sorted(prov["files"]):
            sys.exit("Snapshot file list drifted from PROVENANCE.json — re-freeze.")
        if corpus_hash(on_disk) != prov["corpus_sha256"]:
            sys.exit("Snapshot content drifted from PROVENANCE.json (hash mismatch) — re-freeze.")
        print(f"OK: {len(on_disk)} pages match provenance "
              f"(corpus {prov['corpus_sha256'][:12]}, frozen {prov['frozen_at']}).")
        return

    pages = enumerate_pages()
    by_journal = {}
    for journal, slug in pages:
        by_journal.setdefault(journal, 0)
        by_journal[journal] += 1
    print(f"Enumerated {len(pages)} pages: " + ", ".join(f"{j}={n}" for j, n in sorted(by_journal.items())))

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    def fetch_one(item):
        journal, slug = item
        content = http_get(md_url(journal, slug))
        out_dir = RAW_DIR / journal
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{slug}.md").write_text(content)
        return f"{journal}/{slug}.md"

    with ThreadPoolExecutor(max_workers=8) as ex:
        files = sorted(ex.map(fetch_one, pages))

    chash = corpus_hash(files)
    PROVENANCE.write_text(json.dumps({
        "source_site": SITE,
        "source_path": "/wiki/papers/{jf,rfs}/2025/<slug>.md  (live wiki, raw markdown)",
        "enumerated_from": "Starlight sidebar of a rendered page (no machine index for the year dir)",
        "corpus_sha256": chash,
        "frozen_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "page_count": len(files),
        "files": sorted(files),
        "note": (
            "Frozen snapshot of the live IAR distilled-lit wiki for the scorer floor "
            "test (#102). The reconstruction step reads THIS snapshot, never the live "
            "site — fixtures must not drift when the wiki changes. The live site has no "
            "version pin, so reproducibility is anchored by corpus_sha256 (content hash "
            "over the frozen pages). Re-freeze only on a deliberate, audited refresh, "
            "never as feedback from scorer output."
        ),
    }, indent=2) + "\n")
    print(f"Froze {len(files)} pages (corpus {chash[:12]}) → {RAW_DIR}")


if __name__ == "__main__":
    main()
