#!/usr/bin/env bash
#
# Sync the meta-repo's canonical dev instructions and dev skills into the mirrors
# other runtimes discover. Canonical sources:
#
#   CLAUDE.md         -> AGENTS.md            (Codex reads AGENTS.md automatically)
#   .claude/skills/*  -> .agents/skills/*     (Codex discovers repo skills here)
#
# Both mirrors are DEV-ONLY — they exist so a Codex session started in this repo
# gets the same instructions and dev skills a Claude session does. Neither reaches
# a deployed research project: setup.sh assembles into an empty project directory,
# generates that project's AGENTS.md and .agents/skills from deploy_assets/, and
# never copies either dev mirror. Consequently neither gets a manifest entry.
#
# Idempotent: safe to re-run, rewrites only what has drifted.
#
# The shape is a REAL .agents/skills directory containing SYMLINKED skill folders.
# This lets the sync own, validate, and prune each mirror entry independently; it is
# not a deployment constraint, because the dev mirror never enters a deployment.
# Codex also follows a wholesale symlinked .agents/skills directory (maintainer, on
# openai/codex#11314: "Codex does support symlinking the /.agents/skills directory
# (both global and per-project) ... We even have unit tests in place").
#   - symlinking SKILL.md itself is genuinely unsupported (openai/codex#9365: "We
#     support symlinks to a skill directory, not the SKILL.md file itself"). Link the
#     folder, never the file.
#   - the relative target is ../../ and getting it wrong fails silently. openai/codex#11314
#     was closed not-planned because it was not a bug at all: the reporter's symlink had
#     an invalid relative target. A link at .agents/skills/{name} resolves its first ..
#     to .agents/, so ../.claude/... points at the non-existent .agents/.claude/.
#   - AGENTS.md is a COPY, never a symlink to CLAUDE.md: this script regenerates
#     AGENTS.md wholesale, so writing through a symlink would overwrite the canonical
#     CLAUDE.md rather than refresh the mirror.
#
# Live-reload caveat (same issue thread): Codex watches skill files for live updates,
# and the watcher does not fire through a symlink. Edits to .claude/skills/{name}/SKILL.md
# show up in Codex only after relaunching the CLI.

set -euo pipefail

# Normalize the inherited environment before anything depends on it. Bash applies an
# exported SHELLOPTS at startup — before this script's own `set` line — so options set
# by the caller are already in force above. Each of these can only break us:
#   noglob     the mirror loops below are globs; under -f they expand to literal
#              pattern strings, match nothing, and the sync silently does nothing
#              while still exiting 0 — and the drift check then reports PASS with a
#              mirror genuinely missing.
#   noclobber  the AGENTS.md staging write is a truncating redirect; under -C a
#              leftover .tmp from an interrupted run makes it fail outright.
#   CDPATH     `cd` with a bare relative operand resolves through a CDPATH entry and
#              ECHOES the resolved path, landing inside the command substitutions
#              below and embedding a newline in the derived paths.
#   GLOBIGNORE/IFS  alter which glob matches survive and how results are split.
set +f +C
unset CDPATH GLOBIGNORE
IFS=$' \t\n'

# Resolve the script's own path before deriving the repo root: invoked through a
# symlink (a .git/hooks entry, a ~/bin shortcut), an unresolved BASH_SOURCE makes
# dirname/.. land on the symlink's directory instead of this repo.
_src="${BASH_SOURCE[0]}"
while [ -L "$_src" ]; do
    _dir="$(cd -P "$(dirname "$_src")" && pwd)"
    _src="$(readlink "$_src")"
    case "$_src" in /*) ;; *) _src="$_dir/$_src" ;; esac
done
SCRIPT_DIR="$(cd -P "$(dirname "$_src")" && pwd)"
ROOT_DIR="$(cd -P "$SCRIPT_DIR/.." && pwd)"

CANONICAL_DOC="$ROOT_DIR/CLAUDE.md"
MIRROR_DOC="$ROOT_DIR/AGENTS.md"
CANONICAL_SKILLS_DIR="$ROOT_DIR/.claude/skills"
MIRROR_SKILLS_DIR="$ROOT_DIR/.agents/skills"

if [ ! -f "$CANONICAL_DOC" ]; then
    echo "ERROR: canonical instructions not found: $CANONICAL_DOC" >&2
    exit 1
fi

# ── AGENTS.md ──
# Prepend a provenance header rather than a bare copy. A plain `cp` would leave the
# mirror indistinguishable from a hand-authored file, and the next person to edit
# would edit the copy and lose the change on the following sync.
#
# Staged through a .tmp so a failure mid-write cannot leave a half-written AGENTS.md.
# The trap removes it on any exit — an interrupted run (Ctrl-C during a pre-commit
# hook) would otherwise strand one, which is both litter and, under an inherited
# noclobber, a hard failure for every subsequent run.
trap 'rm -f "$MIRROR_DOC.tmp"' EXIT
{
    echo "<!-- GENERATED FILE — DO NOT EDIT."
    echo "     Mirror of CLAUDE.md, written by scripts/sync_dev_instructions.sh."
    echo "     Edit CLAUDE.md instead, then re-run that script. -->"
    echo
    cat "$CANONICAL_DOC"
} > "$MIRROR_DOC.tmp"

if [ -f "$MIRROR_DOC" ] && cmp -s "$MIRROR_DOC.tmp" "$MIRROR_DOC"; then
    rm -f "$MIRROR_DOC.tmp"
    echo "AGENTS.md already current"
else
    mv "$MIRROR_DOC.tmp" "$MIRROR_DOC"
    echo "AGENTS.md <- CLAUDE.md"
fi

# ── .agents/skills ──
# A real directory (never a symlink) holding one relative symlink per dev skill.
# The target is ../../.claude/skills/<name>: the link lives in .agents/skills/, so
# the first .. is .agents/ and the second is the repo root. A single ../ resolves
# to .agents/.claude/... and dangles.
# `.agents` and `.agents/skills` must be real directories. `mkdir -p` silently
# no-ops on a symlink-to-directory, after which every link this script writes lands
# inside the symlink's target while its ../../ target string still assumes the
# intended location — producing broken links in a directory the operator never
# chose, and failing later with an error that blames the skill rather than the
# hijacked path.
for _d in "$ROOT_DIR/.agents" "$MIRROR_SKILLS_DIR"; do
    if [ -L "$_d" ]; then
        echo "ERROR: $_d is a symlink; it must be a real directory." >&2
        echo "       Every mirror link is written relative to its real location," >&2
        echo "       so a redirected parent would scatter them elsewhere." >&2
        exit 1
    fi
    # Catch a plain file here too, or `mkdir -p` below fails with a bare
    # "Not a directory" that says nothing about which path is wrong.
    if [ -e "$_d" ] && [ ! -d "$_d" ]; then
        echo "ERROR: $_d exists but is not a directory." >&2
        echo "       Move or delete it, then re-run this script." >&2
        exit 1
    fi
done

mkdir -p "$MIRROR_SKILLS_DIR"

if [ ! -d "$CANONICAL_SKILLS_DIR" ]; then
    echo "ERROR: canonical skills dir not found: $CANONICAL_SKILLS_DIR" >&2
    exit 1
fi

# What a mirror entry points at, in whichever form this checkout gave it — a real
# symlink, or the plain file holding the target path that git writes when symlinks
# are unavailable (core.symlinks=false; native Windows without the privilege,
# exFAT/FAT32, some network mounts). Prints nothing for anything else, which is what
# every caller uses to mean "not one of ours." One content-aware test, so no caller
# has to re-derive the platform question with `-L`.
# Always returns 0. "Not one of ours" is signalled by empty output, never by exit
# status: callers assign the result, and a bare assignment is not exempt from
# `set -e`, so a nonzero return here would kill the script before it could print
# the refusal it was about to print — silently, with no diagnostic at all.
mirror_target() {
    local p="$1" size content
    if [ -L "$p" ]; then
        readlink "$p"
        return 0
    fi
    [ -f "$p" ] && [ -r "$p" ] || return 0
    size="$(wc -c < "$p")"
    # A materialized symlink blob is a short single-line path with no trailing
    # newline. Shape alone is not enough to claim the file is ours — a stray note
    # ("WIP, do not commit") fits it too — so the content must also read as a
    # mirror target. Anything else returns empty, i.e. "not one of ours", and the
    # callers refuse rather than touch it.
    # 256 is generous for "../../.claude/skills/<name>" — a skill directory name
    # would have to exceed ~234 characters to be refused by this bound, which no
    # runtime would accept anyway (Codex caps the skill NAME at 64).
    [ "$size" -gt 0 ] && [ "$size" -le 256 ] && [ "$(wc -l < "$p")" -eq 0 ] || return 0
    content="$(cat "$p")"
    case "$content" in
        ../../.claude/skills/*/*) return 0 ;;        # deeper than a skill dir
        ../../.claude/skills/?*) printf '%s' "$content" ;;
    esac
    return 0
}

# Can this checkout create symlinks at all? Probe once rather than guessing from the
# git config, which is not the same question: git may be configured either way while
# the filesystem decides. Without support we leave the mirror as git left it.
# Clear any probe a killed run left behind first: `ln -s` fails with "File exists"
# on a stale one, which would misreport a perfectly capable filesystem as incapable.
SYMLINKS_OK=0
rm -f "$MIRROR_SKILLS_DIR/.symlink-probe"
if ln -s .probe-target "$MIRROR_SKILLS_DIR/.symlink-probe" 2>/dev/null; then
    SYMLINKS_OK=1
fi
rm -f "$MIRROR_SKILLS_DIR/.symlink-probe"
if [ "$SYMLINKS_OK" = "0" ]; then
    echo "WARNING: this checkout cannot create symlinks, so the dev skills cannot be" >&2
    echo "         exposed under .agents/skills and Codex will not discover them here." >&2
    echo "         AGENTS.md still syncs. Enable symlink support (on Windows: Developer" >&2
    echo "         Mode, or run elevated, plus 'git config core.symlinks true' and a" >&2
    echo "         fresh checkout) to fix it. Existing entries are left untouched." >&2
fi

# Discovered, not a hardcoded name list — adding a dev skill needs no edit here.
linked=0
for src in "$CANONICAL_SKILLS_DIR"/*/; do
    [ -d "$src" ] || continue
    skill="$(basename "$src")"
    dst="$MIRROR_SKILLS_DIR/$skill"
    target="../../.claude/skills/$skill"

    if [ ! -f "$src/SKILL.md" ]; then
        echo "ERROR: $skill has no SKILL.md — Codex will not discover it." >&2
        exit 1
    fi
    # Frontmatter is checked against Codex's bundled skill-creator validator. Both
    # caps are measured in CHARACTERS, not UTF-8 bytes: quick_validate.py uses
    # len(name) / len(description). Counting bytes would over-flag descriptions
    # containing non-ASCII punctuation, including every dev skill currently here.
    #
    #   name         <= 64    HARD authoring limit; also rejected by the loader.
    #   description  <= 1024  HARD authoring limit. The current runtime loader is
    #                          permissive above it, but generated skills must not rely
    #                          on that implementation detail.
    #
    # Separate mechanism, deliberately not checked: an aggregate skills-metadata budget
    # across ALL rendered descriptions, which also truncates (openai/codex#24299). It is
    # 2% of the context window in TOKENS, not characters — skill_metadata_budget() in
    # codex-rs/ext/skills/src/render.rs returns SkillMetadataBudget::Tokens, falling back
    # to Characters only when the context window is unknown. The budget_limit=5440 in that
    # issue is 272_000 * 2%, i.e. tokens. It depends on the model and on what else is
    # installed, so it is not knowable from this repo.
    python3 - "$src/SKILL.md" "$skill" <<'PY' || exit 1
import sys

try:
    import yaml
except ImportError:
    print(
        "ERROR: scripts/sync_dev_instructions.sh requires PyYAML to validate "
        "Codex skill frontmatter.",
        file=sys.stderr,
    )
    sys.exit(1)

path, skill = sys.argv[1], sys.argv[2]

def fail(msg):
    print(f"ERROR: {skill} SKILL.md {msg}", file=sys.stderr)
    sys.exit(1)

lines = open(path, encoding="utf-8").read().splitlines(keepends=True)
if not lines or lines[0].rstrip("\r\n") != "---":
    fail("does not open with a '---' frontmatter block.")

block_lines = []
for line in lines[1:]:
    if line.rstrip("\r\n") == "---":
        break
    block_lines.append(line)
else:
    fail("has an unterminated frontmatter block (no closing '---').")

try:
    fields = yaml.safe_load("".join(block_lines))
except yaml.YAMLError as exc:
    fail(f"has invalid YAML frontmatter: {exc}")
if not isinstance(fields, dict):
    fail("frontmatter must be a YAML mapping.")

for field in ("name", "description"):
    value = fields.get(field)
    if not isinstance(value, str):
        fail(f"frontmatter '{field}' must be a string.")
    fields[field] = value.strip()
    if not fields[field]:
        fail(f"frontmatter is missing a non-empty '{field}:'.")

# Hard: parser.rs validate_len() rejects the skill outright.
n = len(fields["name"])
if n > 64:
    fail(f"'name' is {n} characters; Codex rejects a name over 64. Shorten it.")

d = len(fields["description"])
if d > 1024:
    fail(
        f"'description' is {d} characters; Codex's skill-authoring validator "
        "rejects a description over 1024. Shorten it."
    )
print(f"  {skill}: name {n}/64, description {d}/1024 chars")
PY

    # Refuse rather than clobber. Everything under .agents/skills is generated, so
    # content that is not one of ours arrived by mistake, and replacing it would be
    # silent data loss with no backup. Make it a human decision.
    #
    # The discriminator is the entry's TARGET, via mirror_target(), not `-L`. A
    # core.symlinks=false checkout materializes a tracked symlink as a plain file
    # holding the target path, so an `-L` test would call a correct fresh clone
    # "foreign content" and refuse — a dead end, since deleting the file just restores
    # it on the next checkout.
    # One rule, identical to the sweep below: an existing entry must already point at
    # this skill's canonical directory, or it is not ours and we refuse. Being a
    # symlink does not make it ours — a foreign link at a colliding name is exactly
    # as much someone else's content as a foreign file is, and the two loops
    # disagreeing about that is what produced silent deletions twice before.
    if [ -e "$dst" ] || [ -L "$dst" ]; then
        if [ "$(mirror_target "$dst")" != "$target" ]; then
            echo "ERROR: $dst is not a generated mirror entry for '$skill'." >&2
            echo "       .agents/skills/ holds only links into .claude/skills/." >&2
            echo "       Move or delete that path, then re-run this script." >&2
            exit 1
        fi
        # Ours and correctly aimed. A real symlink needs nothing; the plain-file
        # materialization git writes when symlinks are unavailable gets upgraded
        # where that is possible, and is otherwise left exactly as git wrote it.
        if [ ! -L "$dst" ] && [ "$SYMLINKS_OK" = "1" ]; then
            rm -f "$dst"
            ln -s "$target" "$dst"
            echo "linked .agents/skills/$skill -> $target"
        fi
    elif [ "$SYMLINKS_OK" = "1" ]; then
        ln -s "$target" "$dst"
        echo "linked .agents/skills/$skill -> $target"
    fi

    if [ "$SYMLINKS_OK" = "0" ]; then
        # Codex needs a real directory to discover a skill, so a materialized file
        # will not be found until symlinks work here.
        echo "  (skipping $skill — no symlink support on this checkout)" >&2
    fi

    if [ "$SYMLINKS_OK" = "1" ]; then
        if [ ! -f "$dst/SKILL.md" ]; then
            echo "ERROR: .agents/skills/$skill does not resolve to a readable SKILL.md." >&2
            exit 1
        fi
        # Counted only when a link actually exists, so the closing summary cannot
        # claim skills are exposed while the warning above says none are.
        linked=$((linked + 1))
    fi
done

# Sweep the mirror. The loop above only visits names that match a canonical skill, so
# anything else here — foreign content, or a leftover link to a skill that is gone, or
# a link aimed somewhere it should not be — is touched by neither loop and would sit
# here indefinitely, invisible to the drift check too once committed. Every entry must
# be a mirror entry AND aimed at the canonical skill of its own name.
for dst in "$MIRROR_SKILLS_DIR"/*; do
    [ -e "$dst" ] || [ -L "$dst" ] || continue   # unmatched glob on an empty dir
    name="$(basename "$dst")"
    current="$(mirror_target "$dst")"

    if [ -z "$current" ]; then
        echo "ERROR: $dst is not a generated mirror entry." >&2
        echo "       .agents/skills/ holds only links into .claude/skills/." >&2
        echo "       Move or delete that path, then re-run this script." >&2
        exit 1
    fi
    if [ "$current" != "../../.claude/skills/$name" ]; then
        # Aimed somewhere other than its own canonical skill. Never ours, and deleting
        # it could discard something intentional — refuse and let a human decide.
        echo "ERROR: $dst points at '$current', not ../../.claude/skills/$name." >&2
        echo "       Move or delete that path, then re-run this script." >&2
        exit 1
    fi
    if [ ! -d "$CANONICAL_SKILLS_DIR/$name" ]; then
        rm -f "$dst"
        echo "removed stale link $name"
    fi
done

echo "Sync complete ($linked dev skill(s) exposed to Codex)."
