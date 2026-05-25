#!/usr/bin/env bash
# Verify a paper's bibliography against OpenAlex.
#
# Usage:
#   code/utils/bib_verify/verify_bib.sh                       # auto-detect references file
#   code/utils/bib_verify/verify_bib.sh path/to/references.md
#   code/utils/bib_verify/verify_bib.sh path/to/refs.bib
#
# Output:
#   - Raw per-entry JSON: output/bib_verification.jsonl
#   - Human-readable report: output/bib_verification.md
#
# Reads EMAIL from .env (project root) for the OpenAlex polite pool.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(pwd)"
PY="$SCRIPT_DIR/openalex_check.py"

# ── Locate input ──
INPUT="${1:-}"
if [ -z "$INPUT" ]; then
    # Documented canonical path (paper-writer.md) is references/references.md;
    # check it first, then other reasonable locations.
    for cand in "$ROOT/references/references.md" "$ROOT/paper/references.md" \
                "$ROOT/references/references.bib" "$ROOT/paper/references.bib"; do
        if [ -f "$cand" ]; then INPUT="$cand"; break; fi
    done
fi
if [ -z "$INPUT" ] || [ ! -f "$INPUT" ]; then
    echo "ERROR: no references file found (tried paper/, references/). Pass a path explicitly." >&2
    exit 2
fi

OUT_DIR="$ROOT/output"
mkdir -p "$OUT_DIR"
JSONL="$OUT_DIR/bib_verification.jsonl"
REPORT="$OUT_DIR/bib_verification.md"

EXT="${INPUT##*.}"

# ── Build the input stream the python script consumes ──
TMP_IN="$(mktemp)"
trap 'rm -f "$TMP_IN"' EXIT

if [ "$EXT" = "bib" ]; then
    # BibTeX → one JSON cite per @entry. Use python for the parse.
    python3 - "$INPUT" > "$TMP_IN" <<'PYEOF'
import json, re, sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
entries = re.split(r"\n@", "\n" + text)
for raw in entries:
    raw = raw.strip()
    if not raw or raw.startswith("comment") or raw.startswith("preamble"):
        continue
    head_m = re.match(r"(\w+)\s*\{\s*([^,\s]+)\s*,", raw)
    if not head_m:
        continue
    key = head_m.group(2)
    fields = {}
    # Match field = {balanced braces or "quoted"}. The balanced-brace match
    # walks character-by-character so titles like {{Fed} Taper Tantrum} (common
    # protect-proper-nouns idiom in econ .bib files) survive intact.
    pos = 0
    field_pat = re.compile(r"(\w+)\s*=\s*", re.DOTALL)
    while True:
        m = field_pat.search(raw, pos)
        if not m:
            break
        name = m.group(1).lower()
        i = m.end()
        if i >= len(raw):
            break
        if raw[i] == "{":
            depth = 0
            j = i
            while j < len(raw):
                if raw[j] == "{":
                    depth += 1
                elif raw[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            value = raw[i + 1: j]
            pos = j + 1
        elif raw[i] == '"':
            j = raw.find('"', i + 1)
            if j == -1:
                break
            value = raw[i + 1: j]
            pos = j + 1
        else:
            j = raw.find(",", i)
            if j == -1:
                j = raw.find("}", i)
            value = raw[i: j if j != -1 else len(raw)]
            pos = j + 1 if j != -1 else len(raw)
        # Strip residual LaTeX braces used to protect capitalization
        value = re.sub(r"[{}]+", "", value)
        fields[name] = re.sub(r"\s+", " ", value).strip()
    title = fields.get("title", "")
    year_raw = fields.get("year", "")
    ym = re.search(r"\d{4}", year_raw)
    year = int(ym.group()) if ym else None
    authors_raw = fields.get("author", "")
    authors = [a.strip() for a in re.split(r"\s+and\s+", authors_raw) if a.strip()]
    print(json.dumps({"key": key, "title": title, "authors": authors, "year": year}))
PYEOF
    PLAIN_FLAG=""
else
    # Markdown / plain: one citation per non-empty, non-heading line.
    grep -vE '^\s*(#|$)' "$INPUT" | sed 's/^[-*•]\s*//' > "$TMP_IN"
    PLAIN_FLAG="--plain"
fi

ENTRY_COUNT="$(wc -l < "$TMP_IN" | tr -d ' ')"
if [ "$ENTRY_COUNT" = "0" ]; then
    echo "ERROR: no entries parsed from $INPUT" >&2
    exit 3
fi

echo "Verifying $ENTRY_COUNT entries from $INPUT against OpenAlex..."

# ── Run the verifier ──
python3 "$PY" $PLAIN_FLAG < "$TMP_IN" > "$JSONL"

# ── Render the markdown report ──
python3 - "$JSONL" "$INPUT" > "$REPORT" <<'PYEOF'
import json, sys
from collections import Counter
jsonl, src = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(jsonl) if l.strip()]
counts = Counter(r["status"] for r in rows)
total = len(rows)

print(f"# Bibliography Verification")
print()
print(f"**Source:** `{src}`")
print(f"**Total entries:** {total}")
print(f"**VERIFIED:** {counts.get('VERIFIED', 0)}  •  "
      f"**RESOLVED:** {counts.get('RESOLVED', 0)}  •  "
      f"**MISS:** {counts.get('MISS', 0)}")
print()
print("Status meanings:")
print("- **VERIFIED** — title match ≥ 0.85 in OpenAlex. If a DOI is present, Crossref also confirmed title and authors (`doi_confirmed: true`).")
print("- **RESOLVED** — partial match (0.60–0.85), or year off by >1. If a DOI is present, Crossref still confirmed (`doi_confirmed: true`). Review manually for typos / stale year.")
print("- **MISS** — either no good OpenAlex hit, OR OpenAlex matched but Crossref disagreed on title/authors (`doi_confirmed: false`, see `note` for `doi-mismatch`). A `doi-mismatch` MISS is strong evidence of a wrong-paper collision. Otherwise SSRN-only / very recent / fabricated — run a WebSearch fallback before deciding.")
print()
for status in ("MISS", "RESOLVED", "VERIFIED"):
    bucket = [r for r in rows if r["status"] == status]
    if not bucket:
        continue
    print(f"## {status} ({len(bucket)})")
    print()
    for r in bucket:
        cited = r.get("cited", {})
        cited_title = cited.get("title", "(no title)")
        cited_year = cited.get("year", "?")
        print(f"- **{r.get('key','')}** — {cited_title} ({cited_year})")
        if status != "MISS":
            print(f"    - matched: {r.get('matched_title','')} ({r.get('year','?')}) · sim={r.get('similarity','?')}")
            if r.get("venue"):
                print(f"    - venue: {r['venue']}")
            if r.get("doi"):
                print(f"    - doi: {r['doi']}")
            if r.get("url"):
                print(f"    - url: {r['url']}")
        if r.get("note"):
            print(f"    - note: {r['note']}")
    print()
PYEOF

echo "Report: $REPORT"
echo "Raw:    $JSONL"
