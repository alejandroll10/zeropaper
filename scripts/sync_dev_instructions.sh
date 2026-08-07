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
#   noclobber  mktemp creates the AGENTS.md staging file before the truncating
#              redirect opens it; under -C even that new unique file is refused.
#   CDPATH     `cd` with a bare relative operand resolves through a CDPATH entry and
#              ECHOES the resolved path, landing inside the command substitutions
#              below and embedding a newline in the derived paths.
#   GLOBIGNORE/IFS and inherited shopt glob modes alter which entries the mirror
#              loops see. In particular, failglob can abort an empty sweep and
#              dotglob/nocaseglob can silently change membership, while
#              nocasematch weakens the lowercase-only skill-name case check.
set +f +C
unset CDPATH GLOBIGNORE
IFS=$' \t\n'
shopt -u failglob nullglob dotglob nocaseglob nocasematch

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
CODEX_SKILL_VALIDATOR="$ROOT_DIR/deploy_assets/scripts/codex_skill_validation.py"

if [ ! -f "$CANONICAL_DOC" ]; then
    echo "ERROR: canonical instructions not found: $CANONICAL_DOC" >&2
    exit 1
fi

# ── AGENTS.md ──
# Prepend a provenance header rather than a bare copy. A plain `cp` would leave the
# mirror indistinguishable from a hand-authored file, and the next person to edit
# would edit the copy and lose the change on the following sync.
#
# Staged through a unique same-directory tempfile so a failure mid-write cannot leave
# a half-written AGENTS.md and an existing predictable path cannot redirect the write
# through a symlink. Same-directory placement keeps the final mv atomic. The trap
# removes the tempfile on any ordinary exit or handled interruption.
MIRROR_DOC_TMP="$(mktemp "$ROOT_DIR/.AGENTS.md.tmp.XXXXXX")"
cleanup_mirror_doc_tmp() {
    if [ -n "${SYMLINK_PROBE_DIR:-}" ]; then
        rm -f "$SYMLINK_PROBE_DIR/link"
        rmdir "$SYMLINK_PROBE_DIR" 2>/dev/null || true
    fi
    if [ -n "${MIRROR_DOC_TMP:-}" ]; then
        rm -f "$MIRROR_DOC_TMP"
    fi
}
trap cleanup_mirror_doc_tmp EXIT
{
    echo "<!-- GENERATED FILE — DO NOT EDIT."
    echo "     Mirror of CLAUDE.md, written by scripts/sync_dev_instructions.sh."
    echo "     Edit CLAUDE.md instead, then re-run that script. -->"
    echo
    cat "$CANONICAL_DOC"
} > "$MIRROR_DOC_TMP"

if [ ! -L "$MIRROR_DOC" ] && [ -f "$MIRROR_DOC" ] \
    && cmp -s "$MIRROR_DOC_TMP" "$MIRROR_DOC"; then
    rm -f "$MIRROR_DOC_TMP"
    MIRROR_DOC_TMP=""
    # Normalize unconditionally: Git records the executable bit, but local read/write
    # policy belongs to the checkout's umask and ACL rather than this generator.
    chmod a-x "$MIRROR_DOC"
    echo "AGENTS.md already current"
else
    # A content refresh should not replace the checkout's read/write policy merely
    # because mktemp starts at 0600. Preserve an existing regular file's permission
    # bits while removing execute bits; a missing/symlinked mirror gets the normal
    # file-creation mode filtered through the caller's umask. Atomic replacement does
    # replace inode-local ACLs: a checkout that adds a custom ACL to AGENTS.md must
    # reapply it after content-changing syncs. Closing that portably would require
    # platform-specific ACL snapshot/restore or giving up the atomic replacement.
    if [ ! -L "$MIRROR_DOC" ] && [ -f "$MIRROR_DOC" ]; then
        python3 - "$MIRROR_DOC" "$MIRROR_DOC_TMP" <<'PY'
import os
import stat
import sys

mode = stat.S_IMODE(os.stat(sys.argv[1], follow_symlinks=False).st_mode)
os.chmod(sys.argv[2], mode & ~0o111)
PY
    else
        chmod =rw "$MIRROR_DOC_TMP"
    fi

    # The mirror is a regular copy, never a symlink. Remove a link explicitly
    # before mv: when it points at a directory, a bare mv treats that target as the
    # destination directory and puts AGENTS.md.tmp inside it instead of replacing
    # the link. Other non-regular paths are foreign content and fail closed.
    if [ -L "$MIRROR_DOC" ]; then
        rm -f "$MIRROR_DOC"
    elif [ -e "$MIRROR_DOC" ] && [ ! -f "$MIRROR_DOC" ]; then
        echo "ERROR: $MIRROR_DOC exists but is not a regular file." >&2
        echo "       Move or delete it, then re-run this script." >&2
        exit 1
    fi
    mv "$MIRROR_DOC_TMP" "$MIRROR_DOC"
    MIRROR_DOC_TMP=""
    chmod a-x "$MIRROR_DOC"
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
if [ ! -f "$CODEX_SKILL_VALIDATOR" ]; then
    echo "ERROR: Codex skill validator not found: $CODEX_SKILL_VALIDATOR" >&2
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
        # Write the target bytes with no record delimiter. `readlink` adds a newline,
        # and command substitution would then strip both that delimiter and any real
        # trailing newlines in the target. A byte-oriented Python call avoids both.
        python3 - "$p" <<'PY'
import os
import sys

sys.stdout.buffer.write(os.readlink(os.fsencode(sys.argv[1])))
PY
        return $?
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

# Capture mirror_target without command substitution stripping trailing newlines.
# The appended sentinel is removed after capture; if the real target itself ends in
# the same byte, removing one occurrence still removes only the appended sentinel.
mirror_target_tagged() {
    mirror_target "$1" || return 1
    printf '\034'
}

# Can this checkout create symlinks at all? Probe once rather than guessing from the
# git config, which is not the same question: git may be configured either way while
# the filesystem decides. Without support we leave the mirror as git left it.
# Probe inside the actual destination filesystem and directory — probing elsewhere
# can disagree on both symlink support and write permission. A unique private
# directory avoids deleting or overwriting a developer's content at a fixed name.
SYMLINKS_OK=0
SYMLINK_PROBE_DIR=""
if SYMLINK_PROBE_DIR="$(
    mktemp -d "$MIRROR_SKILLS_DIR/.symlink-probe.XXXXXX" 2>/dev/null
)"; then
    if ln -s .probe-target "$SYMLINK_PROBE_DIR/link" 2>/dev/null; then
        SYMLINKS_OK=1
    fi
    rm -f "$SYMLINK_PROBE_DIR/link"
    rmdir "$SYMLINK_PROBE_DIR"
    SYMLINK_PROBE_DIR=""
fi
if [ "$SYMLINKS_OK" = "0" ]; then
    echo "WARNING: this checkout cannot create symlinks, so the dev skills cannot be" >&2
    echo "         exposed under .agents/skills and Codex will not discover them here." >&2
    echo "         AGENTS.md still syncs. Enable symlink support (on Windows: Developer" >&2
    echo "         Mode, or run elevated, plus 'git config core.symlinks true' and a" >&2
    echo "         fresh checkout) to fix it. Existing entries are left untouched." >&2
fi

# Discovered, not a hardcoded name list — adding a dev skill needs no edit here.
linked=0
for src in "$CANONICAL_SKILLS_DIR"/*/ \
    "$CANONICAL_SKILLS_DIR"/.[!.]*/ "$CANONICAL_SKILLS_DIR"/..?*/; do
    [ -d "$src" ] || continue
    skill_path="${src%/}"
    skill="${skill_path##*/}"
    case "$skill" in
        ""|*[!abcdefghijklmnopqrstuvwxyz0123456789-]*|-*|*-|*--*)
            echo "ERROR: canonical skill directory '$skill' is not a valid Codex skill name." >&2
            echo "       Use lowercase letters, digits, and single interior hyphens." >&2
            exit 1
            ;;
    esac
    if [ "${#skill}" -gt 64 ]; then
        echo "ERROR: canonical skill directory '$skill' exceeds Codex's 64-character name limit." >&2
        exit 1
    fi
    dst="$MIRROR_SKILLS_DIR/$skill"
    target="../../.claude/skills/$skill"

    if [ ! -f "$src/SKILL.md" ]; then
        echo "ERROR: $skill has no SKILL.md — Codex will not discover it." >&2
        exit 1
    fi
    # The shared validator mirrors Codex's complete bundled skill-creator contract:
    # allowed/required fields and types, hyphen-case name syntax, the 64/1024
    # character caps, and the description angle-bracket ban. Both caps count Unicode
    # CHARACTERS, not UTF-8 bytes. It is shared with assemble_codex_skills.py so dev
    # mirrors and deployed skills cannot drift onto different authoring rules.
    #
    # Separate mechanism, deliberately not checked: an aggregate skills-metadata budget
    # across ALL rendered descriptions, which also truncates (openai/codex#24299). It is
    # 2% of the context window in TOKENS, not characters — skill_metadata_budget() in
    # codex-rs/ext/skills/src/render.rs returns SkillMetadataBudget::Tokens, falling back
    # to Characters only when the context window is unknown. The budget_limit=5440 in that
    # issue is 272_000 * 2%, i.e. tokens. It depends on the model and on what else is
    # installed, so it is not knowable from this repo.
    python3 "$CODEX_SKILL_VALIDATOR" "$src/SKILL.md" --label "$skill" || exit 1

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
        if ! observed_tagged="$(mirror_target_tagged "$dst")"; then
            echo "ERROR: cannot inspect mirror target: $dst" >&2
            exit 1
        fi
        observed="${observed_tagged%$'\034'}"
        if [ "$observed" != "$target" ]; then
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
for dst in "$MIRROR_SKILLS_DIR"/* \
    "$MIRROR_SKILLS_DIR"/.[!.]* "$MIRROR_SKILLS_DIR"/..?*; do
    [ -e "$dst" ] || [ -L "$dst" ] || continue   # unmatched glob on an empty dir
    name="${dst##*/}"
    if ! current_tagged="$(mirror_target_tagged "$dst")"; then
        echo "ERROR: cannot inspect mirror target: $dst" >&2
        exit 1
    fi
    current="${current_tagged%$'\034'}"

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
