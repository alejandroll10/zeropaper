#!/usr/bin/env bash
#
# Assert the Codex-facing dev mirrors are in sync with their canonical sources.
#
# CLAUDE.md and .claude/skills/ are canonical; AGENTS.md and .agents/skills/ are
# generated from them by scripts/sync_dev_instructions.sh. Nothing in git enforces
# that the generator was run, so the mirrors can drift silently: someone edits
# CLAUDE.md under a Claude session, commits, and a later Codex session reads stale
# instructions with no warning. This is the deterministic check that closes that gap
# — run it after touching either canonical source, and from the mandated post-change
# review. It is also safe to wire into a pre-commit hook or CI if either ever exists.
#
# Validates the INDEX — what a commit would record — and never the working tree; the
# body below carries the reasoning and the designs it replaced. Build-time only
# (scripts/ is stripped at deploy), so no manifest entry.

set -euo pipefail

# Normalize the inherited environment first — bash applies an exported SHELLOPTS
# before this script's own `set` line, so caller options are already in force. CDPATH
# in particular breaks this script precisely where it is meant to work: as a
# .git/hooks/pre-commit symlink, where `cd` with a bare relative operand would echo
# the resolved path into the command substitutions below and fail every commit.
# The generator this calls re-normalizes for itself, since it runs as a fresh bash.
set +f +C
unset CDPATH GLOBIGNORE
IFS=$' \t\n'

# git honours GIT_DIR/GIT_WORK_TREE over cwd-based discovery, so an ambient pair
# (set by a wrapper, a `git filter-branch`, a submodule foreach) would point this
# check at a DIFFERENT repository — which reports clean and PASSes while real drift
# sits unreported here. Unset them so discovery anchors on ROOT below. GIT_INDEX_FILE
# is deliberately left alone: a pre-commit hook sets it to the index being committed,
# which is exactly the state this check should be reading.
unset GIT_DIR GIT_WORK_TREE

# Resolve this script's own path first. Wiring it into .git/hooks/ — the hardening
# path this file's header names — is conventionally done with a symlink, and an
# unresolved $0 would then put ROOT outside any checkout, where the git gate below
# reports SKIP and exits 0. That is a silent false green in the one check whose
# entire purpose is to prevent silent false greens.
_src="${BASH_SOURCE[0]:-$0}"
while [ -L "$_src" ]; do
    _dir="$(cd -P "$(dirname "$_src")" && pwd)"
    _src="$(readlink "$_src")"
    case "$_src" in /*) ;; *) _src="$_dir/$_src" ;; esac
done
ROOT="$(cd -P "$(dirname "$_src")/.." && pwd)"
cd "$ROOT"

# Distinguish "no git repo here" (a legitimate skip) from "git is broken" (must not
# pass). Folding both into one silent skip would put a soft green one line above the
# code hardened against exactly that in mirrors_dirty().
# The discriminator is whether a .git exists, not git's message: an unreadable .git
# also reports "not a git repository", so matching on that text would skip a broken
# repo as though it were a tarball.
if ! rev_out="$(git rev-parse --git-dir 2>&1)"; then
    if [ -e .git ]; then
        echo "FAIL: .git exists here but git cannot use it, so the mirrors cannot" >&2
        echo "      be checked. Treating this as a failure rather than a skip:" >&2
        echo "      $rev_out" >&2
        exit 1
    fi
    echo "SKIP: not a git checkout, cannot compare the mirrors." >&2
    exit 0
fi

# ── Validate the INDEX, and nothing else ────────────────────────────────────
# A commit records the index. So the only question that matters is whether the
# index is internally consistent: do the mirrors it holds match the canonical
# sources it holds? Working tree, untracked scans and ignore rules are deliberately
# never consulted — each was an escape hatch that produced a false PASS:
#
#   working tree vs clean   deadlocked the pre-commit hook: staging the fix the hook
#                           demanded was then itself refused.
#   before/after porcelain  blind by construction — porcelain reports a two-letter
#                           status CODE, never content, so an already-dirty mirror
#                           kept the same code while the bytes changed underneath.
#   index vs working tree   defeated three ways: `assume-unchanged` makes `git diff`
#                           report no difference whatever the content; .gitignore or
#                           .git/info/exclude hides a generated-but-unstaged mirror
#                           from `ls-files --others --exclude-standard`; and it never
#                           inspected the CANONICAL side, so a staged mirror built
#                           from an UNSTAGED CLAUDE.md passed — committing a mirror
#                           whose source text exists in no commit.
#
# Reading only `git show :<path>` and `git ls-files -s` sidesteps all of it: index
# bits, ignore rules and the working tree cannot influence what those report. This
# check is a pure validator with no side effects — it never writes. On failure it
# tells you to run the generator and stage the result.
fail() {
    echo >&2
    echo "FAIL: the index is not self-consistent — what this commit would record" >&2
    echo "      does not match what the canonical sources in it generate." >&2
    echo "      $1" >&2
    echo >&2
    echo "      Fix: bash scripts/sync_dev_instructions.sh && git add -- AGENTS.md .agents/skills" >&2
    exit 1
}

for required in CLAUDE.md AGENTS.md; do
    git ls-files --error-unmatch -- "$required" >/dev/null 2>&1 \
        || fail "$required is not in the index (nothing to compare, or the mirror was never staged)."
done

# Compare BLOB HASHES, not captured text. `$(git show :path)` strips every trailing
# newline, so a mirror differing from its source only in trailing blank lines compared
# equal — real, generator-detectable drift reported as in sync. Hashing bytes cannot
# lose them.
#
# The expected blob is the mirror's own first four lines (the generator writes three
# header lines plus a blank) followed by the staged CLAUDE.md verbatim. Taking the
# header from the mirror rather than restating it here keeps this file from becoming a
# second copy of that text, which would be its own drift risk. `sed -n 1,4p` rather
# than `head -4` because head closes the pipe early and the SIGPIPE trips pipefail.
# Known scope limit: only line 1 of the header is asserted against a literal. Lines
# 2-4 are taken from the mirror itself, so hand-edits confined to them are invisible
# here — the check proves the mirror is "its own header + the staged CLAUDE.md", not
# that the header matches what the generator emits. Asserting the full header would
# mean a second copy of that text in this file, whose drift is the likelier failure.
if [ "$(git cat-file blob ":AGENTS.md" | sed -n '1p')" != "<!-- GENERATED FILE — DO NOT EDIT." ]; then
    fail "AGENTS.md in the index does not begin with the generated-file header."
fi
actual_doc_sha="$(git rev-parse ":AGENTS.md")"
expected_doc_sha="$(
    { git cat-file blob ":AGENTS.md" | sed -n '1,4p'; git cat-file blob ":CLAUDE.md"; } \
        | git hash-object --stdin
)"
if [ "$actual_doc_sha" != "$expected_doc_sha" ]; then
    fail "AGENTS.md in the index is not its header followed by CLAUDE.md in the index."
fi

# Canonical skills, from the index — by DIRECTORY name, not by globbing for SKILL.md.
# Globbing '.claude/skills/*/SKILL.md' silently omitted a staged skill directory that
# has no SKILL.md yet, so it was compared against nothing and passed, while the
# generator hard-errors on that same state. The check and the generator must decide
# "is this a skill" the same way, or one greenlights what the other rejects.
canonical_skills=""
while IFS= read -r path; do
    [ -n "$path" ] || continue
    name="${path#.claude/skills/}"
    name="${name%%/*}"
    # Anchored on BOTH sides. A bare *"$name"$'\n'* matches when the name is merely a
    # SUFFIX of one already seen — `foo` inside `afoo` — silently skipping its
    # SKILL.md check and dropping it from the comparison entirely. That reintroduces
    # the exact false PASS this derivation was rewritten to close.
    case $'\n'"$canonical_skills" in
        *$'\n'"$name"$'\n'*) continue ;;
    esac
    git ls-files --error-unmatch -- ".claude/skills/$name/SKILL.md" >/dev/null 2>&1 \
        || fail ".claude/skills/$name is staged without a SKILL.md; the generator rejects it."
    canonical_skills="$canonical_skills$name"$'\n'
done <<EOF
$(git ls-files -- '.claude/skills/*')
EOF
canonical_skills="$(printf '%s' "$canonical_skills" | LC_ALL=C sort)"

# Mirror entries, from the index. `ls-files -s` prints "<mode> <sha> <stage>\t<path>",
# so the tab split is safe for paths containing spaces.
mirror_skills=""
while IFS= read -r entry; do
    [ -n "$entry" ] || continue
    mode="${entry%% *}"
    path="${entry#*$'\t'}"
    name="${path#.agents/skills/}"
    case "$name" in
        */*) fail "$path is nested below a skill directory." ;;
    esac
    if [ "$mode" != "120000" ]; then
        fail "$path is recorded as mode $mode, not a symlink (120000)."
    fi
    # An unmerged path has no stage-0 entry, so `git show :path` fails. Reachable only
    # by running this by hand mid-conflict — `git commit` refuses before hooks run —
    # but it should say so rather than die on a raw git fatal.
    if ! target="$(git show ":$path" 2>/dev/null)"; then
        fail "$path has no stage-0 index entry (unmerged?); resolve the conflict first."
    fi
    if [ "$target" != "../../.claude/skills/$name" ]; then
        fail "$path points at '$target', not ../../.claude/skills/$name."
    fi
    mirror_skills="$mirror_skills$name"$'\n'
done <<EOF
$(git ls-files -s -- .agents/skills)
EOF
mirror_skills="$(printf '%s' "$mirror_skills" | LC_ALL=C sort)"

if [ "$canonical_skills" != "$mirror_skills" ]; then
    missing="$(comm -23 <(printf '%s\n' "$canonical_skills") <(printf '%s\n' "$mirror_skills") | tr '\n' ' ')"
    extra="$(comm -13 <(printf '%s\n' "$canonical_skills") <(printf '%s\n' "$mirror_skills") | tr '\n' ' ')"
    [ -n "${missing// /}" ] && echo "      Canonical skills with no staged mirror link: $missing" >&2
    [ -n "${extra// /}" ] && echo "      Staged mirror links with no canonical skill: $extra" >&2
    fail "the staged mirror links do not match the staged dev skills."
fi

echo "PASS: the index records AGENTS.md and .agents/skills in sync with their canonical sources."
exit 0
