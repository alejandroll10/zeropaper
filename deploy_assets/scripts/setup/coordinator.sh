#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro|llm_cognition] [--mode empirical-first|measurement-first|report]
#                  [--ext empirical|theory_llm] [--seed|--faithful|--manual] [--light]
#                  [--no-model-probe] [--publish|--no-publish] [--assemble-only]
#
# Every invocation assembles from the checkout containing this setup.sh. To
# deploy a release, check out the desired tag or commit before running setup.
# --assemble-only  Assemble and validate into an explicit destination, then
#           stop before dependency provisioning, project Git initialization,
#           the initial commit, or publishing. Intended for tests and updates.
# --ext     Add an extension (can be repeated). Available: empirical, theory_llm
# --mode    Pipeline-architecture mode (orthogonal to --variant). Available:
#             empirical-first  — flips the pipeline so identification design and
#                                empirical results lead and theory-generator runs
#                                in mechanism mode (prose+DAG, no theorem/proof).
#                                Auto-implies --ext empirical. Finance variant only
#                                in v1; macro has theory-first identification tooling
#                                but not this mode's mechanism/vocabulary calibration.
#             report           — referee an external paper submission instead of
#                                generating one. Reads submission/, fans out audit
#                                agents in parallel, synthesizes report/referee_report.md.
#                                One-shot, no stages/gates/state. Mutually exclusive
#                                with --seed, --faithful, --manual. Composes with
#                                --ext empirical / --ext theory_llm / --light.
# --seed    Create a seeded-idea project. Creates output/seed/ with instructions.
#           Drop your idea files there before launching. Pipeline starts at seed_triage.
#           Soft semantics: the pipeline preserves the seed's mechanism but may
#           pivot under puzzle-triage / refine framing under scorer recommendations.
# --faithful  Stricter variant of --seed. The seed is treated as a contract; the
#           pipeline implements the seed's named mechanism faithfully and
#           documents impossibilities rather than substituting alternatives. Use
#           when you want the seed executed as written, with additions on top
#           allowed but no replacement of the seed's mechanism / headline /
#           identification strategy. Mutually exclusive with --seed and --manual.
# --manual  Manual mode: assemble agents/skills as a research toolkit, no autonomous
#           pipeline. The runtime doc lists what's available and lets you drive.
#           Mutually exclusive with --seed and --faithful.
# --light   Use the cheapest capability tier for the whole run (cheaper/faster).
#           Applies to every runtime through its own tier table: claude `sonnet`,
#           codex `gpt-5.6-luna`, gemini `gemini-3-flash-preview`. Grok and
#           OpenCode are no-ops because each has one configured model. Subagents are pinned at assembly time
#           and their per-agent reasoning effort is dropped; the ORCHESTRATOR is
#           pinned to the same tier by launch.sh, which reads it back from the
#           assembled agents rather than carrying its own copy of the table.
# --no-model-probe  Skip the live claude-CLI availability probe. Agent models are
#           still remapped off the built-in known-unavailable list (fable/mythos
#           → opus), but newly-suspended models won't be auto-detected. Use in CI
#           or offline setups where launching `claude` at setup time isn't wanted.
# --publish Create and push a GitHub repository after setup. Publishing is opt-in;
#           new deployments stay local unless this flag is present. The target
#           defaults to automated-papers-produced and can be changed with
#           PUBLISH_ORG=<org>; PUBLISH_VISIBILITY defaults to private.
# --no-publish  Explicitly keep the deployment local (the default). Useful in
#           scripts that want the safety choice visible at the call site.
#
# Legacy: --variant finance_llm is shorthand for --variant finance --ext theory_llm

set -e

# ── Capture and enter one checkout-local source snapshot ──
SCRIPT_DIR="${ZEROPAPER_SETUP_LAUNCH_ROOT:?missing sanitized setup launcher root}"
unset ZEROPAPER_SETUP_LAUNCH_ROOT
# Keep this list in dependency order: it drives snapshotting, the clean gate,
# and destination protection. .env.example is a template input; .env is
# operator state.
SOURCE_INPUT_PATHS=(
    setup.sh update.sh scripts/update_coordinator.sh
    VERSION LICENSE .env.example deploy_assets
)
_setup_source_digest() {
    local digest_root="$1"
    python3 -I - "$digest_root" "${SOURCE_INPUT_PATHS[@]}" <<'PYEOF'
import hashlib
import os
import stat
import sys

root = os.path.realpath(sys.argv[1])
source_inputs = sys.argv[2:]
hasher = hashlib.sha256()

def emit(kind, logical, mode, payload=b""):
    hasher.update(kind.encode() + b"\0")
    hasher.update(logical.encode() + b"\0")
    hasher.update(f"{stat.S_IMODE(mode):o}".encode() + b"\0")
    hasher.update(payload)
    hasher.update(b"\0")

def visit(logical, actual):
    info = os.lstat(actual)
    if stat.S_ISLNK(info.st_mode):
        raise SystemExit(
            f"symlink build input is not allowed: {logical} -> {os.readlink(actual)}"
        )
    elif stat.S_ISDIR(info.st_mode):
        emit("dir", logical, info.st_mode)
        for name in sorted(os.listdir(actual)):
            # Later local-module imports use a private PYTHONPYCACHEPREFIX, so
            # checkout caches are deliberately non-input artifacts.
            if name in {"__pycache__", ".ipynb_checkpoints", ".venv", "venv"} \
                    or name.endswith(".egg-info"):
                continue
            visit(f"{logical}/{name}", os.path.join(actual, name))
    elif stat.S_ISREG(info.st_mode):
        if logical.endswith(".pyc"):
            raise SystemExit(f"standalone bytecode build input is not allowed: {logical}")
        if logical.endswith(("/.DS_Store", "/Thumbs.db")):
            return
        with open(actual, "rb") as handle:
            emit("file", logical, info.st_mode, handle.read())
    else:
        raise SystemExit(f"unsupported build-input file type: {logical}")

for name in source_inputs:
    path = os.path.join(root, name)
    if not os.path.lexists(path):
        raise SystemExit(f"missing build input: {path}")
    visit(name, path)

print("sha256:" + hasher.hexdigest())
PYEOF
}

# One cleanup trap owns every private resource created by the active phase.
# The outer capture phase hands snapshot cleanup to a fixed wrapper; the inner
# snapshot phase owns all later cache/catalog/ownership state.
CATALOG_TMPDIR=""
TIER_VOCAB_FILE=""
OWNERSHIP_TMPDIR=""
PYTHON_CACHE_TMPDIR=""
SETUP_GIT_TEMPLATE_DIR=""
SOURCE_SNAPSHOT_TMPDIR=""
_setup_cleanup() {
    [ -n "${SOURCE_SNAPSHOT_TMPDIR:-}" ] && rm -rf "$SOURCE_SNAPSHOT_TMPDIR" 2>/dev/null || true
    [ -n "${OWNERSHIP_TMPDIR:-}" ] && rm -rf "$OWNERSHIP_TMPDIR" 2>/dev/null || true
    [ -n "${CATALOG_TMPDIR:-}" ] && rm -rf "$CATALOG_TMPDIR" 2>/dev/null || true
    [ -n "${PYTHON_CACHE_TMPDIR:-}" ] && rm -rf "$PYTHON_CACHE_TMPDIR" 2>/dev/null || true
    [ -n "${SETUP_GIT_TEMPLATE_DIR:-}" ] && rm -rf "$SETUP_GIT_TEMPLATE_DIR" 2>/dev/null || true
    [ -n "${TIER_VOCAB_FILE:-}" ] && rm -f "$TIER_VOCAB_FILE" 2>/dev/null || true
    return 0
}
trap _setup_cleanup EXIT

_setup_validate_handoff() {
    python3 -I - "$SCRIPT_DIR" "$ZEROPAPER_SETUP_HANDOFF" \
        "$ZEROPAPER_SETUP_LIVE_ROOT" "$ZEROPAPER_SETUP_SOURCE_DIGEST" \
        "${TMPDIR:-/tmp}" <<'PYEOF'
import json
import os
import stat
import sys

snapshot, handoff, live_root, digest, temporary = sys.argv[1:]
snapshot = os.path.realpath(snapshot)
handoff = os.path.abspath(handoff)
parent = os.path.dirname(snapshot)
info = os.lstat(handoff)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 \
        or stat.S_IMODE(info.st_mode) != 0o600 or info.st_uid != os.geteuid():
    raise SystemExit("invalid internal setup snapshot handoff")
if handoff != os.path.join(parent, ".setup-handoff.json"):
    raise SystemExit("invalid internal setup snapshot handoff location")
if os.path.basename(snapshot) != "source" or os.path.basename(parent).split(".", 1)[0] != "zeropaper-source":
    raise SystemExit("invalid internal setup snapshot layout")
temporary = os.path.realpath(temporary)
if os.path.dirname(parent) != temporary:
    raise SystemExit("internal setup snapshot is outside the validated temporary root")
with open(handoff, encoding="utf-8") as handle:
    payload = json.load(handle)
expected = {
    "snapshot": snapshot,
    "live_root": os.path.realpath(live_root),
    "digest": digest,
}
if payload != expected:
    raise SystemExit("internal setup snapshot handoff does not match its environment")
if not digest.startswith("sha256:") or len(digest) != 71:
    raise SystemExit("invalid internal setup source digest")
PYEOF
}

_setup_capture_and_exec_snapshot() {
    local snapshot_root snapshot_digest post_snapshot_digest handoff
    SOURCE_CHECKOUT_ROOT="$SCRIPT_DIR"
    _live_config_module="$SOURCE_CHECKOUT_ROOT/deploy_assets/scripts/setup/resolve_config.sh"
    [ -f "$_live_config_module" ] || {
        echo "Error: setup configuration module not found: $_live_config_module" >&2
        echo "  Run setup.sh from a complete zeropaper checkout." >&2
        exit 1
    }

    # Capture the baseline before executing any build-input module. The outer
    # coordinator does no assembly itself; after verification it transfers
    # control to the snapshotted setup.sh so Bash cannot continue reading a
    # concurrently replaced live coordinator inode.
    SOURCE_CONTENT_DIGEST="$(_setup_source_digest "$SOURCE_CHECKOUT_ROOT")"
    SOURCE_SNAPSHOT_TMPDIR="$(mktemp -d "$SETUP_TMP_ROOT/zeropaper-source.XXXXXX")"
    snapshot_root="$SOURCE_SNAPSHOT_TMPDIR/source"
    python3 -I - "$SOURCE_CHECKOUT_ROOT" "$snapshot_root" "${SOURCE_INPUT_PATHS[@]}" <<'PYEOF'
import os
import shutil
import sys

source, destination = sys.argv[1:3]
os.mkdir(destination)

def ignore_non_inputs(_directory, names):
    return {
        name for name in names
        if name in {
            "__pycache__", ".ipynb_checkpoints", ".venv", "venv",
            ".DS_Store", "Thumbs.db",
        }
        or name.endswith((".egg-info", ".pyc"))
    }

for logical in sys.argv[3:]:
    src = os.path.join(source, logical)
    dst = os.path.join(destination, logical)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src) and not os.path.islink(src):
        shutil.copytree(src, dst, symlinks=True, ignore=ignore_non_inputs)
    else:
        shutil.copy2(src, dst, follow_symlinks=False)
PYEOF
    snapshot_digest="$(_setup_source_digest "$snapshot_root")"
    post_snapshot_digest="$(_setup_source_digest "$SOURCE_CHECKOUT_ROOT")"
    if [ "$snapshot_digest" != "$SOURCE_CONTENT_DIGEST" ] \
       || [ "$post_snapshot_digest" != "$SOURCE_CONTENT_DIGEST" ]; then
        echo "Error: template build inputs changed while capturing the local snapshot." >&2
        echo "  Rerun setup from a stable checkout." >&2
        exit 1
    fi

    handoff="$SOURCE_SNAPSHOT_TMPDIR/.setup-handoff.json"
    python3 -I - "$handoff" "$snapshot_root" "$SOURCE_CHECKOUT_ROOT" \
        "$SOURCE_CONTENT_DIGEST" <<'PYEOF'
import json
import os
import sys

path, snapshot, live_root, digest = sys.argv[1:]
payload = {
    "snapshot": os.path.realpath(snapshot),
    "live_root": os.path.realpath(live_root),
    "digest": digest,
}
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, sort_keys=True)
    handle.write("\n")
PYEOF
    export ZEROPAPER_SETUP_HANDOFF="$handoff"
    export ZEROPAPER_SETUP_LIVE_ROOT="$SOURCE_CHECKOUT_ROOT"
    export ZEROPAPER_SETUP_SOURCE_DIGEST="$SOURCE_CONTENT_DIGEST"
    export ZEROPAPER_SETUP_SNAPSHOT_ROOT="$snapshot_root"

    # The wrapper text is already parsed before the handoff and never performs
    # assembly. It exists only to remove the private snapshot after the pinned
    # coordinator exits, including failure paths.
    exec bash -c '
        snapshot_tmp=$1
        shift
        trap '\''rm -rf -- "$snapshot_tmp" 2>/dev/null || true'\'' EXIT
        "$ZEROPAPER_SETUP_SNAPSHOT_ROOT/setup.sh" "$@"
    ' zeropaper-setup-snapshot "$SOURCE_SNAPSHOT_TMPDIR" "$@"
}

# The live phase validates against its checkout; the internal phase validates
# against the original checkout recorded by the handoff before trusting it.
if [ -n "${ZEROPAPER_SETUP_LIVE_ROOT:-}" ]; then
    SOURCE_CHECKOUT_ROOT="$ZEROPAPER_SETUP_LIVE_ROOT"
else
    SOURCE_CHECKOUT_ROOT="$SCRIPT_DIR"
fi

# Temporary resources must remain physically outside every directory build
# input. Normalize TMPDIR once so relative paths cannot change meaning after
# setup enters the new project directory, and reject symlink aliases into the
# source before the first setup-owned file is created.
if ! SETUP_TMP_ROOT="$(python3 -I - "${TMPDIR:-/tmp}" "$SOURCE_CHECKOUT_ROOT" "${SOURCE_INPUT_PATHS[@]}" <<'PYEOF'
import os
import sys

temporary = os.path.realpath(sys.argv[1])
root = os.path.realpath(sys.argv[2])
if not os.path.isdir(temporary):
    raise SystemExit(f"temporary directory does not exist or is not a directory: {temporary}")

def is_at_or_within(path, ancestor):
    current = path
    while True:
        try:
            if os.path.samefile(current, ancestor):
                return True
        except OSError:
            pass
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent

for logical in sys.argv[3:]:
    source_input = os.path.join(root, logical)
    if os.path.isdir(source_input) and not os.path.islink(source_input):
        source_input = os.path.realpath(source_input)
        if is_at_or_within(temporary, source_input):
            raise SystemExit(
                "temporary directory must be outside template build inputs: "
                f"{temporary} is inside {source_input}"
            )
print(temporary)
PYEOF
)"; then
    exit 1
fi
TMPDIR="$SETUP_TMP_ROOT"
export TMPDIR

if [ -n "${ZEROPAPER_SETUP_HANDOFF:-}" ] \
   || [ -n "${ZEROPAPER_SETUP_LIVE_ROOT:-}" ] \
   || [ -n "${ZEROPAPER_SETUP_SOURCE_DIGEST:-}" ] \
   || [ -n "${ZEROPAPER_SETUP_SNAPSHOT_ROOT:-}" ]; then
    [ -n "${ZEROPAPER_SETUP_HANDOFF:-}" ] \
        && [ -n "${ZEROPAPER_SETUP_LIVE_ROOT:-}" ] \
        && [ -n "${ZEROPAPER_SETUP_SOURCE_DIGEST:-}" ] \
        && [ -n "${ZEROPAPER_SETUP_SNAPSHOT_ROOT:-}" ] \
        || { echo "Error: incomplete internal setup snapshot handoff" >&2; exit 1; }
    [ "$SCRIPT_DIR" = "$(cd "$ZEROPAPER_SETUP_SNAPSHOT_ROOT" 2>/dev/null && pwd -P)" ] \
        || { echo "Error: internal setup snapshot root mismatch" >&2; exit 1; }
    _setup_validate_handoff
    SOURCE_CHECKOUT_ROOT="$(cd "$ZEROPAPER_SETUP_LIVE_ROOT" && pwd -P)"
    SOURCE_CONTENT_DIGEST="$ZEROPAPER_SETUP_SOURCE_DIGEST"
    SRC_ROOT="$SCRIPT_DIR"
    TEMPLATE_ROOT="$SRC_ROOT/deploy_assets"
    SOURCE_SNAPSHOT_TMPDIR=""
    unset ZEROPAPER_SETUP_HANDOFF ZEROPAPER_SETUP_LIVE_ROOT \
        ZEROPAPER_SETUP_SOURCE_DIGEST ZEROPAPER_SETUP_SNAPSHOT_ROOT
    [ "$(_setup_source_digest "$SRC_ROOT")" = "$SOURCE_CONTENT_DIGEST" ] \
        && [ "$(_setup_source_digest "$SOURCE_CHECKOUT_ROOT")" = "$SOURCE_CONTENT_DIGEST" ] \
        || { echo "Error: template source changed during snapshot handoff." >&2; exit 1; }
else
    _setup_capture_and_exec_snapshot "$@"
fi

SETUP_TOOL_UV="${ZEROPAPER_SETUP_TOOL_UV:-}"
SETUP_TOOL_CLAUDE="${ZEROPAPER_SETUP_TOOL_CLAUDE:-}"
SETUP_TOOL_GH="${ZEROPAPER_SETUP_TOOL_GH:-}"
unset ZEROPAPER_SETUP_TOOL_UV ZEROPAPER_SETUP_TOOL_CLAUDE ZEROPAPER_SETUP_TOOL_GH

# Embedded snippets are isolated, while local assembler scripts import sibling
# modules from the snapshot. Redirect bytecode lookup to a new private prefix,
# disable writes/user-site startup, and discard ambient import-path controls.
PYTHON_CACHE_TMPDIR="$(mktemp -d "$SETUP_TMP_ROOT/zeropaper-python-cache.XXXXXX")"
export PYTHONPYCACHEPREFIX="$PYTHON_CACHE_TMPDIR"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
unset PYTHONPATH PYTHONHOME PYTHONINSPECT PYTHONSTARTUP
SETUP_CONFIG_MODULE="$TEMPLATE_ROOT/scripts/setup/resolve_config.sh"

# shellcheck source=deploy_assets/scripts/setup/resolve_config.sh
source "$SETUP_CONFIG_MODULE"
resolve_setup_config "$@"

# Argument parsing, validation, legacy expansion, implied/deduplicated
# extensions, and variant/mode descriptors are resolved by the configuration
# module above.  setup.sh now consumes that interface and coordinates assembly.

# ── Tier vocab for agent bodies ──
# The tier ladder is a setup configuration variable (resolved by
# resolve_config.sh) that the runtime-doc assembler consumes directly, but agent BODIES go
# through the vocab-substitution path. Bodies that must name the variant's tier
# slugs (editor.md's ladder/allowed-values lines) reference {{TIER_LIST_INLINE}}
# / {{TIER_LADDER_PROSE}}, resolved from this generated overlay so the ladder
# has exactly one source of truth per deploy. Passed to every base assembler
# (shared + variant, all five runtimes). Build-time only (mktemp, never
# deployed): no manifest entry. Best-effort cleanup — a leaked file holds only
# the public tier strings.
#
# No `.json` suffix on the template: BSD/macOS mktemp randomizes only a
# *trailing* run of X's, so `tier_vocab.XXXXXX.json` yields that name
# **literally** — a fixed path, which defeats mktemp entirely. Sequential
# deploys still worked (the cleanup below removes it), but any run that died
# between here and cleanup left the file behind and then bricked every
# subsequent deploy on the host: `set -e` aborts on this line with a bare
# "mkstemp failed ... File exists" that names neither setup.sh nor the tier
# vocab. Concurrent deploys collided for the same reason. The extension was
# decorative — the path is passed to the assemblers explicitly via --vocab.
# The shared EXIT trap was installed before snapshot capture, so this tier-vocab
# file and later catalog/ownership temp state join the same cleanup lifecycle.
TIER_VOCAB_FILE="$(mktemp "$SETUP_TMP_ROOT/tier_vocab.XXXXXX")"
TIER_LIST_INLINE="$TIER_LIST_INLINE" TIER_LADDER_PROSE="$TIER_LADDER_PROSE" python3 -I - "$TIER_VOCAB_FILE" <<'PYEOF'
import json, os, sys
with open(sys.argv[1], "w") as f:
    json.dump({
        "TIER_LIST_INLINE": os.environ["TIER_LIST_INLINE"],
        "TIER_LADDER_PROSE": os.environ["TIER_LADDER_PROSE"],
    }, f)
PYEOF

# ── Resolve paths ──
CLAUDE_DIR_REL=".claude"
CLAUDE_AGENTS_REL="$CLAUDE_DIR_REL/agents"
CLAUDE_SKILLS_REL="$CLAUDE_DIR_REL/skills"
CLAUDE_SETTINGS_REL="$CLAUDE_DIR_REL/settings.json"
# Source of the DEPLOYED Claude settings (the sandbox profile a research project
# runs under). Deliberately NOT this repo's own .claude/settings.json: that file
# configures the template-development session, and a single file cannot be both
# — the template repo wants a permissive dev posture while a deployed project
# wants the sandbox on. Build-time only (lives under templates/, removed in the
# cleanup block), so no deployment-manifest entry; the *destination*
# .claude/settings.json is manifested, so update.sh refreshes it.
CLAUDE_SETTINGS_SRC_REL="templates/runtime/claude/settings.json"
CODEX_DIR_REL=".agents"
CODEX_SUBAGENT_DIR_REL=".codex"
CODEX_AGENTS_REL="$CODEX_SUBAGENT_DIR_REL/agents"
CODEX_SKILLS_REL="$CODEX_DIR_REL/skills"
GEMINI_DIR_REL=".gemini"
GEMINI_AGENTS_REL="$GEMINI_DIR_REL/agents"
GEMINI_SETTINGS_REL="$GEMINI_DIR_REL/settings.json"
# Same split as CLAUDE_SETTINGS_SRC_REL above: deployed Gemini settings ship from
# templates/, not from a dual-role file at this repo's root.
GEMINI_SETTINGS_SRC_REL="templates/runtime/gemini/settings.json"
# Grok Build (xAI `grok` CLI). Reads project instructions from the shared root
# AGENTS.md (same file as Codex — see the labeled-dispatch block in
# templates/runtime/codex/session.md), and its subagents from .grok/agents/*.md.
GROK_DIR_REL=".grok"
GROK_AGENTS_REL="$GROK_DIR_REL/agents"
# Grok's OS-kernel sandbox profile (Seatbelt on macOS / Landlock on Linux),
# generated by scripts/setup/base_agents.sh with the deploying user's $HOME baked in (grok's
# sandbox.toml does not expand ~/$HOME). Launched via
# `grok --sandbox pipeline --always-approve --leader-socket "$(pwd)/.grok/leader.sock"`
# (the per-project leader socket keeps concurrent grok projects from cancelling
# each other's turns — see the launch-line comment below).
GROK_SANDBOX_REL="$GROK_DIR_REL/sandbox.toml"
OPENCODE_DIR_REL=".opencode"
OPENCODE_AGENTS_REL="$OPENCODE_DIR_REL/agents"
OPENCODE_CONFIG_REL="opencode.json"
OPENCODE_CONFIG_SRC_REL="templates/runtime/opencode/opencode.json"
OPENCODE_SANDBOX_REL="$OPENCODE_DIR_REL/sandbox.json"
OPENCODE_SANDBOX_SRC_REL="templates/runtime/opencode/sandbox.json"


MODEL_OVERRIDE_ARGS=()
if [ "$LIGHT" = "1" ]; then
    MODEL_OVERRIDE_ARGS=(--model-override sonnet)
fi

_setup_sanitize_repository() {
    python3 -I - "$1" <<'PYEOF'
import os
import re
import sys
from urllib.parse import urlsplit, urlunsplit

value = sys.argv[1]
if re.match(r"^[a-z][a-z0-9+.-]*://", value, re.I):
    parts = urlsplit(value)
    if parts.scheme.lower() == "file":
        print("local:" + os.path.basename(os.path.realpath(parts.path)))
        raise SystemExit
    host = parts.hostname or ""
    if parts.port:
        host += f":{parts.port}"
    print(urlunsplit((parts.scheme, host, parts.path, "", "")))
elif re.match(r"^[A-Za-z]:[\\/]", value):
    normalized = value.replace("\\", "/").rstrip("/")
    print("local:" + normalized.rsplit("/", 1)[-1])
elif re.match(r"^(?:[^/@:]+@)?[^/:]+:.+", value):
    print(value.split("@", 1)[-1])
else:
    # Git accepts bare relative filesystem remotes (private/path/repo.git),
    # which must not be mistaken for a public repository identifier.
    normalized = value.replace("\\", "/").rstrip("/")
    print("local:" + normalized.rsplit("/", 1)[-1])
PYEOF
}

_setup_source_git() {
    # Source provenance must never execute ambient fsmonitor/filter/hook code.
    # Global/system config is excluded; the remaining explicit settings make
    # even repository-local fsmonitor/attributes inert for inspection calls.
    GIT_CONFIG_GLOBAL=/dev/null \
    GIT_CONFIG_SYSTEM=/dev/null \
    GIT_CONFIG_NOSYSTEM=1 \
    GIT_PAGER=cat \
        git -c core.fsmonitor=false -c core.hooksPath=/dev/null \
            -c core.attributesFile=/dev/null "$@"
}

_setup_source_index_healthy() {
    local index_path
    index_path="$(_setup_source_git -C "$SOURCE_CHECKOUT_ROOT" rev-parse --git-path index 2>/dev/null)" \
        || return 1
    python3 -I - "$SOURCE_CHECKOUT_ROOT" "$index_path" <<'PYEOF' || return 1
import os
import stat
import sys

root, path = sys.argv[1:]
if not os.path.isabs(path):
    path = os.path.join(root, path)
try:
    info = os.lstat(path)
except FileNotFoundError:
    raise SystemExit(1)
raise SystemExit(
    0 if stat.S_ISREG(info.st_mode) and info.st_nlink == 1 else 1
)
PYEOF
    _setup_source_git -C "$SOURCE_CHECKOUT_ROOT" ls-files --stage -- \
        "${SOURCE_INPUT_PATHS[@]}" >/dev/null 2>&1
}

_setup_source_matches_commit() {
    local expected_commit="$1"
    python3 -I - "$SOURCE_CHECKOUT_ROOT" "$expected_commit" \
        "${SOURCE_INPUT_PATHS[@]}" <<'PYEOF'
import os
import stat
import subprocess
import sys

root = os.path.realpath(sys.argv[1])
expected_commit = sys.argv[2]
source_inputs = sys.argv[3:]
git_env = os.environ.copy()
for key in (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR",
):
    git_env.pop(key, None)
git_env["GIT_NO_REPLACE_OBJECTS"] = "1"
git_env["GIT_CONFIG_GLOBAL"] = "/dev/null"
git_env["GIT_CONFIG_SYSTEM"] = "/dev/null"
git_env["GIT_CONFIG_NOSYSTEM"] = "1"
git_env["GIT_PAGER"] = "cat"
git_prefix = [
    "git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
    "-c", "core.attributesFile=/dev/null",
]

def excluded(logical, is_dir=False):
    parts = logical.split("/")
    for part in parts:
        if part in {"__pycache__", ".ipynb_checkpoints", ".venv", "venv"} \
                or part.endswith(".egg-info"):
            return True
    if not is_dir and (logical.endswith(".pyc") \
            or parts[-1] in {".DS_Store", "Thumbs.db"}):
        return True
    return False

tree = subprocess.run(
    [*git_prefix, "-C", root, "ls-tree", "-rz", "--full-tree", expected_commit, "--", *source_inputs],
    env=git_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
).stdout
expected_meta = {}
for record in tree.split(b"\0"):
    if not record:
        continue
    metadata, raw_path = record.split(b"\t", 1)
    mode, kind, oid = metadata.decode("ascii").split()
    logical = raw_path.decode("utf-8", "surrogateescape")
    if excluded(logical):
        continue
    if kind != "blob" or mode == "120000":
        raise SystemExit(f"effective build input is not a committed regular file: {logical}")
    expected_meta[logical] = (mode, oid)

request = "".join(oid + "\n" for _mode, oid in expected_meta.values()).encode("ascii")
batch = subprocess.run(
    [*git_prefix, "-C", root, "cat-file", "--batch"], env=git_env,
    input=request, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
).stdout
cursor = 0
expected = {}
for logical, (mode, oid) in expected_meta.items():
    end = batch.index(b"\n", cursor)
    header = batch[cursor:end].decode("ascii").split()
    if len(header) != 3 or header[0] != oid or header[1] != "blob":
        raise SystemExit(f"could not read committed build input: {logical}")
    size = int(header[2])
    start = end + 1
    payload = batch[start:start + size]
    if batch[start + size:start + size + 1] != b"\n":
        raise SystemExit(f"malformed Git object response for: {logical}")
    expected[logical] = (mode == "100755", payload)
    cursor = start + size + 1

expected_dirs = set()
for logical in expected:
    parent = os.path.dirname(logical)
    while parent:
        expected_dirs.add(parent)
        parent = os.path.dirname(parent)

actual = {}
actual_dirs = set()

def visit(logical, path):
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode):
        raise SystemExit(f"effective build input is a symlink: {logical}")
    if stat.S_ISDIR(info.st_mode):
        actual_dirs.add(logical)
        for name in sorted(os.listdir(path)):
            child = f"{logical}/{name}"
            child_path = os.path.join(path, name)
            child_info = os.lstat(child_path)
            if excluded(child, stat.S_ISDIR(child_info.st_mode)):
                continue
            visit(child, child_path)
    elif stat.S_ISREG(info.st_mode):
        if excluded(logical):
            return
        with open(path, "rb") as handle:
            actual[logical] = (bool(stat.S_IMODE(info.st_mode) & 0o111), handle.read())
    else:
        raise SystemExit(f"unsupported effective build input: {logical}")

for logical in source_inputs:
    parent = os.path.dirname(logical)
    while parent:
        actual_dirs.add(parent)
        parent = os.path.dirname(parent)
    visit(logical, os.path.join(root, logical))

if actual != expected or actual_dirs != expected_dirs:
    changed = sorted(
        {path for path in set(actual) | set(expected) if actual.get(path) != expected.get(path)}
        | (actual_dirs ^ expected_dirs)
    )
    preview = ", ".join(changed[:8])
    if len(changed) > 8:
        preview += f", ... ({len(changed)} paths)"
    raise SystemExit(f"effective build inputs differ from HEAD: {preview}")
PYEOF
}

SOURCE_KIND="checkout"
SOURCE_REPOSITORY=""
SOURCE_COMMIT="unknown"
SOURCE_DIRTY=true
SOURCE_UPDATE_CHANNEL="checkout"
SOURCE_GIT_ROOT=""
SOURCE_CLEAN_STATE="unavailable"
if SOURCE_GIT_ROOT="$(_setup_source_git -C "$SOURCE_CHECKOUT_ROOT" rev-parse --show-toplevel 2>/dev/null)" \
   && [ "$(cd "$SOURCE_GIT_ROOT" && pwd -P)" = "$SOURCE_CHECKOUT_ROOT" ]; then
    SOURCE_COMMIT="$(_setup_source_git -C "$SOURCE_CHECKOUT_ROOT" rev-parse HEAD)"
    _source_remote="$(_setup_source_git -C "$SOURCE_CHECKOUT_ROOT" remote get-url origin 2>/dev/null || true)"
    [ -z "$_source_remote" ] || SOURCE_REPOSITORY="$(_setup_sanitize_repository "$_source_remote")"
    # ls-files reads and validates the index without consulting fsmonitor or
    # worktree filters. Effective cleanliness comes from the byte/mode/tree
    # comparison above, not Git's configurable status machinery.
    if _setup_source_index_healthy; then
        if _setup_source_matches_commit "$SOURCE_COMMIT"; then
            SOURCE_DIRTY=false
            SOURCE_CLEAN_STATE="clean"
        else
            SOURCE_CLEAN_STATE="dirty"
        fi
    fi
fi

_setup_reject_build_input_destination() {
    local candidate="$1" resolved protected_input
    resolved="$(python3 -I - "$candidate" <<'PYEOF'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PYEOF
)"
    # Never let the destination replace the checkout, contain the checkout, or
    # replace an individual root build input. Descendants elsewhere in the
    # checkout remain valid (normal setup commonly creates ./my-paper there).
    protected_input="$(python3 -I - "$resolved" "$SOURCE_CHECKOUT_ROOT" "${SOURCE_INPUT_PATHS[@]}" <<'PYEOF'
import os
import sys

candidate = os.path.realpath(sys.argv[1])
root = os.path.realpath(sys.argv[2])

def nearest_existing(path):
    current = path
    while not os.path.lexists(current):
        parent = os.path.dirname(current)
        if parent == current:
            return current
        current = parent
    return current

def is_at_or_within(path, ancestor):
    current = nearest_existing(path)
    while True:
        try:
            if os.path.samefile(current, ancestor):
                return True
        except OSError:
            pass
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent

# A destination at or above the checkout would consume the source itself.
if os.path.lexists(candidate):
    current = root
    while True:
        try:
            if os.path.samefile(candidate, current):
                print(root)
                raise SystemExit
        except OSError:
            pass
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

for logical in sys.argv[3:]:
    source_input = os.path.realpath(os.path.join(root, logical))
    if is_at_or_within(candidate, source_input):
        print(source_input)
        raise SystemExit
PYEOF
)"
    if [ -n "$protected_input" ]; then
        echo "Error: deployment destination overlaps template build inputs: $resolved" >&2
        echo "  Protected source input: $protected_input" >&2
        exit 1
    fi
}

_setup_normalize_destination() {
    python3 -I - "$1" <<'PYEOF'
import os
import sys

if any(ord(character) < 32 or ord(character) == 127 for character in sys.argv[1]):
    raise SystemExit("Error: deployment destination cannot contain control characters")
destination = os.path.abspath(os.path.normpath(sys.argv[1]))
# macOS exposes these root-owned compatibility aliases. Canonicalize only the
# exact platform mappings before walking ancestors; arbitrary/user-created
# symlinks remain visible to lstat and are rejected.
for alias, physical in (("/tmp", "/private/tmp"), ("/var", "/private/var")):
    if destination == alias or destination.startswith(alias + os.sep):
        try:
            if os.path.islink(alias) and os.path.realpath(alias) == physical:
                destination = physical + destination[len(alias):]
        except OSError:
            pass
        break
print(destination)
PYEOF
}

_setup_validate_destination_ancestors() {
    python3 -I - "$1" <<'PYEOF'
import os
import stat
import sys

destination = os.path.abspath(sys.argv[1])
parts = destination.split(os.sep)
current = os.sep
# The final component has its own exact type/link checks. Every existing
# ancestor must be a real directory so an absent or empty destination cannot
# be reached through a foreign symlink target.
for part in parts[1:-1]:
    current = os.path.join(current, part)
    try:
        info = os.lstat(current)
    except FileNotFoundError:
        break
    if stat.S_ISLNK(info.st_mode):
        raise SystemExit(
            f"Error: deployment destination ancestor is a symbolic link: {current}"
        )
    if not stat.S_ISDIR(info.st_mode):
        raise SystemExit(
            f"Error: deployment destination ancestor is not a directory: {current}"
        )
PYEOF
}

_setup_validate_destination_directory() {
    python3 -I - "$1" <<'PYEOF'
import os
import stat
import sys

destination = os.path.abspath(sys.argv[1])
try:
    info = os.lstat(destination)
except FileNotFoundError:
    raise SystemExit(f"Error: deployment destination disappeared: {destination}")
if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
    raise SystemExit(
        f"Error: deployment destination must be a real directory: {destination}"
    )
PYEOF
}

_setup_verify_source_stable() {
    local final_digest snapshot_digest final_commit final_status
    final_digest="$(_setup_source_digest "$SOURCE_CHECKOUT_ROOT")"
    if [ "$final_digest" != "$SOURCE_CONTENT_DIGEST" ]; then
        echo "Error: template build inputs changed during assembly." >&2
        echo "  Discard this output and rerun from a stable checkout." >&2
        exit 1
    fi
    snapshot_digest="$(_setup_source_digest "$SRC_ROOT")"
    if [ "$snapshot_digest" != "$SOURCE_CONTENT_DIGEST" ]; then
        echo "Error: private template snapshot changed during assembly." >&2
        echo "  Discard this output and rerun setup." >&2
        exit 1
    fi
    if [ "$SOURCE_COMMIT" != "unknown" ]; then
        final_commit="$(_setup_source_git -C "$SOURCE_CHECKOUT_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
        if [ "$final_commit" != "$SOURCE_COMMIT" ]; then
            echo "Error: template checkout HEAD changed during assembly." >&2
            echo "  Discard this output and rerun from a stable checkout." >&2
            exit 1
        fi
        if [ "$SOURCE_DIRTY" = "false" ]; then
            if ! _setup_source_index_healthy \
               || ! _setup_source_matches_commit "$SOURCE_COMMIT"; then
                echo "Error: clean template source no longer matches its recorded commit." >&2
                echo "  Discard this output and rerun from a stable checkout." >&2
                exit 1
            fi
        fi
    fi
}

# Mode-overlay paths resolve against the same checkout-local TEMPLATE_ROOT in
# both full deployments and assembly-only builds.

if [ "$ASSEMBLE_ONLY" = "1" ]; then
    # Assembly-only mode — explicit destination, no provisioning or project Git.

    # Resolve OUT_DIR: absolute path stays absolute, relative anchors to the
    # invoking checkout rather than the private snapshot that will be deleted.
    case "$PROJECT_NAME" in
        /*) OUT_DIR="$PROJECT_NAME" ;;
        *)  OUT_DIR="$SOURCE_CHECKOUT_ROOT/$PROJECT_NAME" ;;
    esac
    # Normalize lexical trailing slash/`.` components before testing the final
    # path itself. Bash's `-L link/` follows the slash and otherwise misses a
    # direct destination symlink.
    OUT_DIR="$(_setup_normalize_destination "$OUT_DIR")"
    _setup_validate_destination_ancestors "$OUT_DIR"
    _setup_reject_build_input_destination "$OUT_DIR"

    # Safety: never replace a file or symlink. A non-empty directory is
    # automatically disposable only beneath this checkout's own test_output/.
    # A same-named directory elsewhere is not evidence that setup owns it.
    if [ -L "$OUT_DIR" ]; then
        echo "Error: $OUT_DIR is a symbolic link; refusing to overwrite it." >&2
        exit 1
    fi
    if [ -e "$OUT_DIR" ] && [ ! -d "$OUT_DIR" ]; then
        echo "Error: $OUT_DIR exists and is not a directory; refusing to overwrite it." >&2
        exit 1
    fi
    _out_dir_state="empty"
    if [ -d "$OUT_DIR" ]; then
        if ! _out_dir_state="$(python3 -I - "$OUT_DIR" <<'PYEOF'
import os
import sys

try:
    with os.scandir(sys.argv[1]) as entries:
        print("nonempty" if next(entries, None) is not None else "empty")
except OSError as error:
    print(f"cannot inspect destination: {error}", file=sys.stderr)
    raise SystemExit(1)
PYEOF
)"; then
            echo "Error: cannot inspect existing destination $OUT_DIR; refusing to overwrite it." >&2
            exit 1
        fi
    fi
    _reset_existing_destination=0
    if [ "$_out_dir_state" = "nonempty" ]; then
        _out_dir_physical="$(python3 -I - "$OUT_DIR" <<'PYEOF'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PYEOF
)"
        _test_output_physical=""
        _owned_scratch=0
        if [ ! -L "$SOURCE_CHECKOUT_ROOT/test_output" ]; then
            _test_output_physical="$(python3 -I - "$SOURCE_CHECKOUT_ROOT/test_output" <<'PYEOF'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PYEOF
)"
            case "$_out_dir_physical" in
                "$_test_output_physical"/*) _owned_scratch=1 ;;
            esac
        fi
        if [ "$_owned_scratch" = "1" ]; then
            _reset_existing_destination=1
        else
            if [ -L "$SOURCE_CHECKOUT_ROOT/test_output" ]; then
                echo "Error: $OUT_DIR already exists and is not empty." >&2
                echo "Refusing to overwrite because this checkout's test_output is a symbolic link." >&2
            else
                echo "Error: $OUT_DIR already exists and is not empty."
                echo "Refusing to overwrite. Move or delete the directory first, or pick a different project name."
            fi
            exit 1
        fi
    fi

    if [ "$_reset_existing_destination" = "1" ]; then
        _setup_validate_destination_ancestors "$OUT_DIR"
        rm -rf -- "$OUT_DIR"
    fi
    _setup_validate_destination_ancestors "$OUT_DIR"
    mkdir -p "$OUT_DIR"
    _setup_validate_destination_ancestors "$OUT_DIR"
    _setup_validate_destination_directory "$OUT_DIR"
    # Agent output dirs, runtime settings dirs, and the OpenCode config files
    # are created by shared assembly below.
    echo "Assembly-only mode: $VARIANT → $OUT_DIR"
else
    # Full deployment — clean checkout, prerequisites, provisioning, and commit.
    PROJECT_NAME="${PROJECT_NAME:-my-research-paper}"
    case "$PROJECT_NAME" in
        /*) _project_destination="$PROJECT_NAME" ;;
        *)  _project_destination="$(pwd -P)/$PROJECT_NAME" ;;
    esac
    _project_destination="$(_setup_normalize_destination "$_project_destination")"
    _setup_validate_destination_ancestors "$_project_destination"
    _setup_reject_build_input_destination "$_project_destination"

    if [ -z "$SOURCE_GIT_ROOT" ] || [ "$(cd "$SOURCE_GIT_ROOT" && pwd -P)" != "$SOURCE_CHECKOUT_ROOT" ]; then
        echo "Error: full setup requires setup.sh to live at the root of a Git checkout." >&2
        echo "  Clone the template, check out the desired tag or commit, then run that checkout's setup.sh." >&2
        exit 1
    fi
    if [ "$SOURCE_CLEAN_STATE" = "unavailable" ]; then
        echo "Error: could not verify template source cleanliness; full setup fails closed." >&2
        echo "  Repair the checkout/index, then rerun setup." >&2
        exit 1
    fi
    if [ "$SOURCE_CLEAN_STATE" = "dirty" ]; then
        echo "Error: template build inputs are dirty; full setup requires committed source." >&2
        echo "  Commit or remove changes under setup.sh, update.sh, scripts/update_coordinator.sh, VERSION, LICENSE, .env.example, and deploy_assets/." >&2
        echo "  Use --assemble-only <destination> to validate development changes without provisioning." >&2
        exit 1
    fi
    echo "Template source: checkout $SOURCE_COMMIT${SOURCE_REPOSITORY:+ ($SOURCE_REPOSITORY)}"

    echo "Checking prerequisites..."
    missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git >/dev/null 2>&1 || missing+=("git")
    [ -n "$SETUP_TOOL_CLAUDE" ] && [ -x "$SETUP_TOOL_CLAUDE" ] \
        || missing+=("claude (npm install -g @anthropic-ai/claude-code)")
    [ -n "$SETUP_TOOL_UV" ] && [ -x "$SETUP_TOOL_UV" ] \
        || missing+=("uv (curl -LsSf https://astral.sh/uv/install.sh | sh)")
    if [[ "$(uname)" == "Linux" ]]; then
        [ -x /usr/bin/bwrap ] || missing+=("bubblewrap at /usr/bin/bwrap (sudo apt-get install bubblewrap)")
    elif [[ "$(uname)" == "Darwin" ]]; then
        _setup_modern_bash=""
        for _candidate in /opt/homebrew/bin/bash /usr/local/bin/bash /opt/local/bin/bash; do
            if [ -x "$_candidate" ] && "$_candidate" -c '(( BASH_VERSINFO[0] >= 4 ))' \
                    >/dev/null 2>&1; then
                _setup_modern_bash="$_candidate"
                break
            fi
        done
        [ -n "$_setup_modern_bash" ] \
            || missing+=("Bash 4+ at a Homebrew/MacPorts path (brew install bash)")
    fi
    # Git identity is required: setup.sh runs `git commit` on the new project, and
    # `set -e` aborts the whole script (skipping any requested publish step) if commit
    # fails with "Author identity unknown". Check both global and local config.
    SETUP_GIT_USER_EMAIL="$(git config --get user.email 2>/dev/null || true)"
    SETUP_GIT_USER_NAME="$(git config --get user.name 2>/dev/null || true)"
    if [ -z "$SETUP_GIT_USER_EMAIL" ] || [ -z "$SETUP_GIT_USER_NAME" ]; then
        missing+=("git identity (run: git config --global user.email \"you@example.com\" && git config --global user.name \"Your Name\")")
    fi
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Missing dependencies:"
        for dep in "${missing[@]}"; do echo "  - $dep"; done
        exit 1
    fi
    echo "All prerequisites found."

    if [ -e "$_project_destination" ] || [ -L "$_project_destination" ]; then
        echo "Error: $PROJECT_NAME already exists"
        exit 1
    fi

    echo "Creating project $PROJECT_NAME..."
    _setup_validate_destination_ancestors "$_project_destination"
    mkdir -p "$_project_destination"
    _setup_validate_destination_ancestors "$_project_destination"
    _setup_validate_destination_directory "$_project_destination"
    cd "$_project_destination"

    # cwd is the fresh, empty project; build inputs remain in the invoking
    # checkout through SRC_ROOT/TEMPLATE_ROOT.
    OUT_DIR="."

fi

# ── Initialize infrastructure / bootstrap ownership boundary ──
P="$OUT_DIR"
FINALIZATION_MODULE="$TEMPLATE_ROOT/scripts/setup/finalization.sh"
if [ ! -f "$FINALIZATION_MODULE" ]; then
    echo "Error: setup finalization module not found: $FINALIZATION_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$FINALIZATION_MODULE"
setup_initialize_project_git

OWNERSHIP_MODULE="$TEMPLATE_ROOT/scripts/setup/ownership.sh"
if [ ! -f "$OWNERSHIP_MODULE" ]; then
    echo "Error: setup ownership module not found: $OWNERSHIP_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$OWNERSHIP_MODULE"
setup_ownership_init

# Verbatim template-owned root infrastructure. Registration is part of the
# install call, so manifest membership cannot drift from creation.
infrastructure_copy_file 220 "$TEMPLATE_ROOT/templates/gitignore_project" ".gitignore"
infrastructure_copy_file 130 "$TEMPLATE_ROOT/launch.sh" "launch.sh"
infrastructure_copy_file 285 "$TEMPLATE_ROOT/templates/utils/pipeline_dotenv_guard.py" ".arpipeline/update_inputs/pipeline_dotenv_guard.py"
infrastructure_copy_file 290 "$TEMPLATE_ROOT/templates/deps/core.txt" ".arpipeline/update_inputs/deps/core.txt"
infrastructure_copy_file 290 "$TEMPLATE_ROOT/templates/deps/ssj.txt" ".arpipeline/update_inputs/deps/ssj.txt"
if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
    infrastructure_copy_file 230 "$TEMPLATE_ROOT/dashboard.html" "dashboard.html"
    if [ "$ASSEMBLE_ONLY" = "1" ]; then
        DASHBOARD_SUBTITLE="Autonomous $(python3 -I -c "import sys; print(sys.argv[1].title())" "$PAPER_TYPE") Generator"
        sed -i.bak "s|Autonomous Finance Theory Paper Generator|$DASHBOARD_SUBTITLE|" "$P/dashboard.html" && rm "$P/dashboard.html.bak"
    fi
fi

# LICENSE is bootstrap content: setup creates it for publishability, but
# update.sh has never owned or refreshed it.
if [ "$ASSEMBLE_ONLY" = "0" ]; then
    bootstrap_copy_file "$SRC_ROOT/LICENSE" "LICENSE"
fi

# ── Runtime-document assembly ──
# Source from the checkout-local TEMPLATE_ROOT. The module also resolves the
# mode overlays consumed by the agent assemblers below.
CLAUDE_MD_OUT="$OUT_DIR/CLAUDE.md"
AGENTS_MD_OUT="$OUT_DIR/AGENTS.md"
GEMINI_MD_OUT="$OUT_DIR/GEMINI.md"
SESSION_OUT_DIR="$OUT_DIR/docs"
RUNTIME_DOCUMENTS_MODULE="$TEMPLATE_ROOT/scripts/setup/runtime_documents.sh"
if [ ! -f "$RUNTIME_DOCUMENTS_MODULE" ]; then
    echo "Error: setup runtime-doc module not found: $RUNTIME_DOCUMENTS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$RUNTIME_DOCUMENTS_MODULE"
setup_runtime_documents
# ── Base and variant agent assembly ──
BASE_AGENTS_MODULE="$TEMPLATE_ROOT/scripts/setup/base_agents.sh"
if [ ! -f "$BASE_AGENTS_MODULE" ]; then
    echo "Error: setup base-agent module not found: $BASE_AGENTS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$BASE_AGENTS_MODULE"
setup_base_agents

# ── Core agent pruning and injections ──
EXTENSIONS_INJECTIONS_MODULE="$TEMPLATE_ROOT/scripts/setup/extensions_and_injections.sh"
if [ ! -f "$EXTENSIONS_INJECTIONS_MODULE" ]; then
    echo "Error: setup extensions/injections module not found: $EXTENSIONS_INJECTIONS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$EXTENSIONS_INJECTIONS_MODULE"
setup_core_agent_injections_and_pruning
# ── Mutable project bootstrap (phase 1) ──
PROJECT_BOOTSTRAP_MODULE="$TEMPLATE_ROOT/scripts/setup/project_bootstrap.sh"
if [ ! -f "$PROJECT_BOOTSTRAP_MODULE" ]; then
    echo "Error: setup project-bootstrap module not found: $PROJECT_BOOTSTRAP_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$PROJECT_BOOTSTRAP_MODULE"
setup_project_bootstrap_before_docs
# ── Template-owned stage documentation ──
INFRASTRUCTURE_DOCS_MODULE="$TEMPLATE_ROOT/scripts/setup/infrastructure_docs.sh"
if [ ! -f "$INFRASTRUCTURE_DOCS_MODULE" ]; then
    echo "Error: setup infrastructure-docs module not found: $INFRASTRUCTURE_DOCS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$INFRASTRUCTURE_DOCS_MODULE"
setup_infrastructure_docs

# Create seed folder with instructions if --seed
# ── Mutable project bootstrap (phase 2) ──
setup_project_bootstrap_after_docs
# ── Mutable environment bootstrap ──
setup_project_environment_bootstrap
# ── Host-local Python environment and dependency provisioning ──
PROVISIONING_MODULE="$TEMPLATE_ROOT/scripts/setup/provisioning.sh"
if [ ! -f "$PROVISIONING_MODULE" ]; then
    echo "Error: setup provisioning module not found: $PROVISIONING_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$PROVISIONING_MODULE"
setup_python_environment
# ── Skills and utilities ──
SKILLS_UTILITIES_MODULE="$TEMPLATE_ROOT/scripts/setup/skills_and_utilities.sh"
if [ ! -f "$SKILLS_UTILITIES_MODULE" ]; then
    echo "Error: setup skills/utilities module not found: $SKILLS_UTILITIES_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$SKILLS_UTILITIES_MODULE"
setup_skills_and_utilities
# ── Extensions, extension injections/pruning, and final model remap ──
setup_extensions_injections_and_pruning
# The checkout is a live external source rather than a private clone. Refuse a
# mixed-revision deployment if its build inputs or HEAD changed while assembly
# was in progress.
_setup_verify_source_stable
# ── Emit deployment manifest from structural ownership registries ──
emit_deployment_manifest
# ── Finalization ──
if [ "$ASSEMBLE_ONLY" = "1" ]; then
    finalize_assemble_only_setup
    exit 0
fi
finalize_production_setup
# temp resources are removed by the shared _setup_cleanup EXIT trap
