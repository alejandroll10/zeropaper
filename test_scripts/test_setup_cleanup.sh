#!/usr/bin/env bash
# Regression test: setup.sh's EXIT trap must ignore inherited temp-path names.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scratch="$(mktemp -d "${TMPDIR:-/tmp}/setup-cleanup-test.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT

inherited_source="$scratch/inherited-source"
inherited_catalog="$scratch/inherited-catalog"
inherited_tier="$scratch/inherited-tier"
mkdir -p "$inherited_source" "$inherited_catalog"
touch "$inherited_tier"

# An absent TMPDIR forces the first setup-owned mktemp to fail immediately
# after the cleanup trap is installed. None of the inherited paths may be
# treated as resources owned by this invocation.
if TMPDIR="$scratch/absent" \
   SRC_TMP="$inherited_source" \
   CATALOG_TMPDIR="$inherited_catalog" \
   TIER_VOCAB_FILE="$inherited_tier" \
   "$repo_root/setup.sh" "$scratch/output" --local --no-model-probe \
   >"$scratch/stdout" 2>"$scratch/stderr"; then
    echo "FAIL: setup unexpectedly succeeded with an absent TMPDIR" >&2
    exit 1
fi

for inherited_path in "$inherited_source" "$inherited_catalog" "$inherited_tier"; do
    if [ ! -e "$inherited_path" ]; then
        echo "FAIL: cleanup deleted inherited path: $inherited_path" >&2
        exit 1
    fi
done

echo "PASS: setup cleanup ignores inherited temp paths"
