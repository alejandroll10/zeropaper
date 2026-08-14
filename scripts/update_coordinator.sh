#!/bin/bash
# update.sh — Refresh pipeline infrastructure in a deployed project.
#
# Usage:
#   ./update.sh <deployed-project-path>
#   ./update.sh <deployed-project-path> --dry-run
#   ./update.sh <deployed-project-path> --variant finance --ext empirical
#   ./update.sh <deployed-project-path> --seeded --faithful --manual --light
#   ./update.sh <deployed-project-path> --no-model-probe
#
# Overrides (--variant, --ext, --seeded/--no-seeded,
# --faithful/--no-faithful, --manual/--no-manual,
# --light/--no-light) take precedence over the manifest's recorded values
# AND over sniffed values for pre-manifest deploys. Use them when the
# manifest is wrong on a pre-manifest deployment, or when applying a supported
# in-layout selector change. Manifested cross-variant migration fails closed.
# Each --ext repeats; passing --ext replaces the manifest's full extension
# list (does not append).
# --no-model-probe is a one-run assembly control forwarded to setup.sh; it is
# not a deployment selector and is not persisted in the manifest.
#
# What it does:
#   1. Reads .deploy_manifest.json from the target project (or sniffs/accepts
#      flags if the project predates manifests).
#   2. Assembles a fresh project into a tmp dir using setup.sh --assemble-only
#      from the checkout containing this update.sh, with the
#      same variant + extensions + flags.
#   3. Copies allow-listed infrastructure paths from the fresh deploy into the
#      target project (rm -rf + cp -r for dirs; overwrite for files; key-merge
#      for .env). Everything else is preserved: paper/, output/, process_log/,
#      data/, references.bib, .git/, paper/arpipeline.sty fingerprint.
#   4. Prints a diff summary (added / removed / changed agents).
#
# Safe to re-run. Does not touch git in the target project — review and
# commit the changes yourself.

set -e

# ── Parse arguments ──
PROJECT=""
DRY_RUN=0
OVERRIDE_VARIANT=""
OVERRIDE_MODE=""
OVERRIDE_MODE_SET=0   # distinguishes "no --mode flag" from "--no-mode (clear)"
OVERRIDE_EXTS=()
OVERRIDE_EXTS_SET=0   # distinguishes "no --ext flags" from "--ext '' (clear list)"
OVERRIDE_SEEDED=""    # "", "true", or "false"
OVERRIDE_FAITHFUL=""
OVERRIDE_MANUAL=""
OVERRIDE_LIGHT=""
NO_MODEL_PROBE=0
NEXT_IS_VARIANT=0
NEXT_IS_MODE=0
NEXT_IS_EXT=0

for arg in "$@"; do
    case "$arg" in
        --dry-run)        DRY_RUN=1 ;;
        --variant)        NEXT_IS_VARIANT=1 ;;
        --variant=*)      OVERRIDE_VARIANT="${arg#--variant=}" ;;
        --mode)           NEXT_IS_MODE=1 ;;
        --mode=*)         OVERRIDE_MODE="${arg#--mode=}";  OVERRIDE_MODE_SET=1 ;;
        --no-mode)        OVERRIDE_MODE="";                OVERRIDE_MODE_SET=1 ;;
        --ext)            NEXT_IS_EXT=1 ;;
        --ext=*)          OVERRIDE_EXTS+=("${arg#--ext=}"); OVERRIDE_EXTS_SET=1 ;;
        --clear-ext)      OVERRIDE_EXTS=();                  OVERRIDE_EXTS_SET=1 ;;
        --seeded)         OVERRIDE_SEEDED=true ;;
        --no-seeded)      OVERRIDE_SEEDED=false ;;
        --faithful)       OVERRIDE_FAITHFUL=true ;;
        --no-faithful)    OVERRIDE_FAITHFUL=false ;;
        --manual)         OVERRIDE_MANUAL=true ;;
        --no-manual)      OVERRIDE_MANUAL=false ;;
        --light)          OVERRIDE_LIGHT=true ;;
        --no-light)       OVERRIDE_LIGHT=false ;;
        --no-model-probe) NO_MODEL_PROBE=1 ;;
        -*)               echo "Unknown option: $arg"; exit 1 ;;
        *)
            if [ "$NEXT_IS_VARIANT" = "1" ]; then
                OVERRIDE_VARIANT="$arg"; NEXT_IS_VARIANT=0
            elif [ "$NEXT_IS_MODE" = "1" ]; then
                OVERRIDE_MODE="$arg"; OVERRIDE_MODE_SET=1; NEXT_IS_MODE=0
            elif [ "$NEXT_IS_EXT" = "1" ]; then
                OVERRIDE_EXTS+=("$arg"); OVERRIDE_EXTS_SET=1; NEXT_IS_EXT=0
            else
                PROJECT="$arg"
            fi
            ;;
    esac
done

# Catch dangling NEXT_IS_* sentinels — without these, `update.sh PROJECT
# --mode --variant finance` silently drops the --mode flag because --variant
# is an explicit case match (not a *) fallthrough), so NEXT_IS_MODE never
# gets consumed and OVERRIDE_MODE_SET stays 0.
if [ "$NEXT_IS_VARIANT" = "1" ]; then
    echo "Error: --variant requires a value (finance, macro, llm_cognition)"; exit 1
fi
if [ "$NEXT_IS_MODE" = "1" ]; then
    echo "Error: --mode requires a value (empirical-first), or use --no-mode to clear"; exit 1
fi
if [ "$NEXT_IS_EXT" = "1" ]; then
    echo "Error: --ext requires a value (empirical, theory_llm)"; exit 1
fi

if [ -z "$PROJECT" ]; then
    echo "usage: update.sh <deployed-project-path> [--dry-run] [--variant X] [--mode M] [--ext Y ...] [--faithful|--no-faithful] [--no-model-probe]"
    exit 1
fi

PROJECT="$(cd "$PROJECT" && pwd -P)"
TEMPLATE_ROOT="${ZEROPAPER_UPDATE_LAUNCH_ROOT:?missing isolated update launcher root}"
unset ZEROPAPER_UPDATE_LAUNCH_ROOT
# Updating the template checkout (or one of its build-input directories) would
# replace the updater's own source. A target above the checkout is equally
# destructive because the checkout sits inside its replacement boundary.
/usr/bin/python3 -I - "$PROJECT" "$TEMPLATE_ROOT" <<'PY'
import os
import sys

project, root = map(os.path.realpath, sys.argv[1:])

def ancestors(path):
    current = path
    while True:
        yield current
        parent = os.path.dirname(current)
        if parent == current:
            return
        current = parent

if any(os.path.samefile(project, current) for current in ancestors(root)):
    raise SystemExit(
        f"ERROR: update target overlaps template source checkout: {project}"
    )

deploy_assets = os.path.join(root, "deploy_assets")
if any(os.path.samefile(current, deploy_assets) for current in ancestors(project)):
    raise SystemExit(
        f"ERROR: update target overlaps template build inputs: {project}"
    )
PY

# Acquire launch.sh's project-directory lock before creating process_log or any
# other target path. Bash retains descriptor 9 throughout the refresh; a short
# isolated-Python helper applies flock to that inherited open file description.
if ! exec 9< "$PROJECT"; then
    echo "ERROR: could not open the project runtime/update lock" >&2
    exit 1
fi
if ! /usr/bin/python3 -I - 9 <<'PY'
import fcntl
import os
import stat
import sys

fd = int(sys.argv[1])
info = os.fstat(fd)
if not stat.S_ISDIR(info.st_mode):
    raise SystemExit("invalid project root lock")
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(75)
PY
then
    echo "ERROR: project runtime is active; stop every launch.sh session before update." >&2
    exit 1
fi

_update_main() {
# Deployable assets live under deploy_assets/. TEMPLATE_ROOT remains the repo
# checkout because setup.sh, VERSION, LICENSE, and .env.example are root inputs.
MANIFEST="$PROJECT/.deploy_manifest.json"

# The target venv/project is agent-writable. Never let an activated venv (or a
# temp/cache shim) provide host-authority tools used by the updater.
UPDATE_CONTROL_PATH=""
IFS=: read -r -a _update_path_entries <<< "${PATH:-}"
for _update_path_entry in /usr/bin /bin /usr/sbin /sbin "${_update_path_entries[@]}"; do
    [ -n "$_update_path_entry" ] && [ -d "$_update_path_entry" ] || continue
    _update_path_physical="$(cd "$_update_path_entry" 2>/dev/null && pwd -P)" || continue
    case "$_update_path_physical" in
        "$PROJECT"|"$PROJECT"/*|"$TEMPLATE_ROOT"|"$TEMPLATE_ROOT"/*|\
        /tmp|/tmp/*|/private/tmp|/private/tmp/*|/var/tmp|/var/tmp/*|/private/var/folders|/private/var/folders/*|\
        "$HOME/.local/share/opencode"|"$HOME/.local/share/opencode"/*|\
        "$HOME/.local/state/opencode"|"$HOME/.local/state/opencode"/*|\
        "$HOME/.cache"|"$HOME/.cache"/*|"$HOME/Library/Caches"|"$HOME/Library/Caches"/*|\
        "$HOME/.matplotlib"|"$HOME/.matplotlib"/*|"$HOME/.codex"|"$HOME/.codex"/*)
            continue ;;
    esac
    case ":$UPDATE_CONTROL_PATH:" in *":$_update_path_physical:"*) ;; *)
        UPDATE_CONTROL_PATH="${UPDATE_CONTROL_PATH:+$UPDATE_CONTROL_PATH:}$_update_path_physical" ;;
    esac
done
[ -n "$UPDATE_CONTROL_PATH" ] || { echo "update.sh could not establish a trusted host PATH"; exit 1; }
PATH="$UPDATE_CONTROL_PATH"
export PATH PYTHONNOUSERSITE=1
UPDATE_TOOL_UV="$(command -v uv 2>/dev/null || true)"
unset VIRTUAL_ENV CONDA_PREFIX CONDA_DEFAULT_ENV \
    CONDA_PROMPT_MODIFIER PIPENV_ACTIVE POETRY_ACTIVE \
    PYTHONHOME PYTHONPATH PYTHONSTARTUP PYTHONINSPECT
hash -r
[ -f /usr/bin/python3 ] && [ -x /usr/bin/python3 ] || {
    echo "update.sh requires the OS Python at /usr/bin/python3"; exit 1;
}
UPDATE_CONTROL_PYTHON=/usr/bin/python3
python3() { "$UPDATE_CONTROL_PYTHON" -I "$@"; }

command -v jq >/dev/null 2>&1 || { echo "update.sh requires jq (sudo apt-get install jq)"; exit 1; }

if [ -e "$MANIFEST" ] || [ -L "$MANIFEST" ]; then
    python3 -I - "$MANIFEST" <<'PY'
import os, stat, sys
info = os.lstat(sys.argv[1])
if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit("ERROR: deployment manifest must be one regular non-aliased file")
PY
fi

# The legacy folder migration below predates manifests and touches paper/
# before the fresh deployment exists. Refuse an aliased parent first.
if [ -L "$PROJECT/paper" ] || { [ -e "$PROJECT/paper" ] && [ ! -d "$PROJECT/paper" ]; }; then
    echo "ERROR: $PROJECT/paper must be a real project directory" >&2
    exit 1
fi
if [ -d "$PROJECT/paper" ] && [ "$(cd "$PROJECT/paper" && pwd -P)" != "$PROJECT/paper" ]; then
    echo "ERROR: $PROJECT/paper resolves outside the deployment" >&2
    exit 1
fi

# Host-authority update staging must be invisible to a concurrently running
# sandboxed OpenCode tree. /tmp and the project root are intentionally writable
# inside SRT, so use the policy-denied control directory on the project fs.
UPDATE_PROCESS_LOG="$PROJECT/process_log"
UPDATE_CONTROL_DIR="$UPDATE_PROCESS_LOG/.opencode-control"
UPDATE_CREATED_PROCESS_LOG=0
UPDATE_CREATED_CONTROL_DIR=0
if [ -L "$UPDATE_PROCESS_LOG" ] || { [ -e "$UPDATE_PROCESS_LOG" ] && [ ! -d "$UPDATE_PROCESS_LOG" ]; }; then
    echo "ERROR: $UPDATE_PROCESS_LOG must be a real project directory" >&2
    exit 1
fi
[ -e "$UPDATE_PROCESS_LOG" ] || UPDATE_CREATED_PROCESS_LOG=1
mkdir -p "$UPDATE_PROCESS_LOG"
if [ "$(cd "$UPDATE_PROCESS_LOG" && pwd -P)" != "$UPDATE_PROCESS_LOG" ]; then
    echo "ERROR: $UPDATE_PROCESS_LOG resolves outside the deployment" >&2
    exit 1
fi
TMP=""
SEED_MIGRATION_PENDING=0
SEED_MIGRATION_JOURNAL=""
CORE_STATE_CANDIDATE=""
_update_cleanup() {
    if [ "$SEED_MIGRATION_PENDING" = "1" ] && [ -f "$SEED_MIGRATION_JOURNAL" ]; then
        "$UPDATE_CONTROL_PYTHON" -I - "$SEED_MIGRATION_JOURNAL" <<'PY' || true
import json
import os
import secrets
import stat
import sys

journal = json.load(open(sys.argv[1], encoding="utf-8"))
state_path = journal["state_path"]
if journal.get("state_committed"):
    temp = os.path.join(
        os.path.dirname(state_path), f".pipeline-state.rollback.{secrets.token_hex(8)}"
    )
    fd = os.open(
        temp,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        journal["state_mode"],
    )
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(journal["original_state"])
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, state_path)
readme = journal["readme"]
if journal.get("created_readme") and os.path.lexists(readme):
    info = os.lstat(readme)
    if stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
        os.unlink(readme)
seed = journal["seed"]
if journal.get("created_seed") and os.path.isdir(seed) and not os.path.islink(seed):
    os.rmdir(seed)
for path in reversed(journal.get("created_dirs", [])):
    if os.path.isdir(path) and not os.path.islink(path):
        os.rmdir(path)
PY
    fi
    [ -z "$TMP" ] || rm -rf "$TMP"
    [ "$UPDATE_CREATED_CONTROL_DIR" = "1" ] && rmdir "$UPDATE_CONTROL_DIR" 2>/dev/null || true
    [ "$UPDATE_CREATED_PROCESS_LOG" = "1" ] && rmdir "$UPDATE_PROCESS_LOG" 2>/dev/null || true
}
trap _update_cleanup EXIT
if [ -L "$UPDATE_CONTROL_DIR" ] || { [ -e "$UPDATE_CONTROL_DIR" ] && [ ! -d "$UPDATE_CONTROL_DIR" ]; }; then
    echo "ERROR: $UPDATE_CONTROL_DIR must be a real control directory" >&2
    exit 1
fi
[ -e "$UPDATE_CONTROL_DIR" ] || UPDATE_CREATED_CONTROL_DIR=1
(umask 077 && mkdir -p "$UPDATE_CONTROL_DIR")
if [ "$(cd "$UPDATE_CONTROL_DIR" && pwd -P)" != "$UPDATE_CONTROL_DIR" ]; then
    echo "ERROR: $UPDATE_CONTROL_DIR resolves outside the deployment" >&2
    exit 1
fi

# Refuse an old deployment's live OpenCode server, which predates the shared
# launcher lock acquired above. New launchers (all runtimes) hold LOCK_SH for their
# lifetime; update holds LOCK_EX, making managed-path validation + replacement
# one quiescent interval rather than an uncloseable pathname-check race.
_server_pid_file="$UPDATE_CONTROL_DIR/server_pid"
if [ -f "$_server_pid_file" ] && [ ! -L "$_server_pid_file" ]; then
    _server_pid="$(cat "$_server_pid_file" 2>/dev/null || true)"
    if [[ "$_server_pid" =~ ^[0-9]+$ ]] && kill -0 "$_server_pid" 2>/dev/null; then
        echo "ERROR: project runtime is active (OpenCode server PID $_server_pid)." >&2
        echo "  Stop the runtime before running update.sh." >&2
        exit 1
    fi
fi
# poppler-utils is a *runtime* dependency of the refreshed pipeline, not of this
# script — so warn, never block. requirements.system is build-time-only and is
# never copied into a deployment, which means an operator refreshing an existing
# project has no other signal that the host now needs it. Without poppler the
# Stage 5 placeholder gate silently false-passes (empty pipe → grep -c prints 0),
# the autonomous rendered-table audit is GATE-BROKEN, report mode cannot read a
# PDF-only submission, and paper-writer cannot see a figure that shipped as
# .pdf-only from a run predating the dual-format contract.
if ! command -v pdftotext >/dev/null 2>&1 || ! command -v pdftoppm >/dev/null 2>&1; then
    echo "  ⚠ poppler-utils (pdftotext/pdftoppm) not found on this host."
    echo "    Install it: brew install poppler  |  sudo apt-get install poppler-utils"
    echo "    Without it Stage 5 PDF gates are broken and PDF reads fail."
fi

# ── Resolve original deployment parameters ──
# Every setup.sh flag that affects what gets deployed must be read here AND
# re-passed in the SETUP_FLAGS block below — drift between the two breaks the
# round-trip on update. Currently tracked: variant, mode, extensions, seeded, faithful,
# manual, light, halt_on_core_bypass. When adding a new setup.sh flag, update both blocks.
if [ -f "$MANIFEST" ]; then
    VARIANT=$(jq -r .variant "$MANIFEST")
    MODE=$(jq -r '.mode // ""' "$MANIFEST")
    EXTENSIONS=()
    while IFS= read -r _ext; do EXTENSIONS+=("$_ext"); done < <(jq -r '.extensions[]?' "$MANIFEST")
    SEEDED=$(jq -r .flags.seeded "$MANIFEST")
    FAITHFUL=$(jq -r '.flags.faithful // empty' "$MANIFEST")
    if [ -z "$FAITHFUL" ]; then
        FAITHFUL=$(jq -r '.faithful // false' "$PROJECT/process_log/pipeline_state.json" 2>/dev/null || echo false)
    fi
    MANUAL=$(jq -r .flags.manual "$MANIFEST")
    LIGHT=$(jq -r .flags.light "$MANIFEST")
    HALT_ON_CORE_BYPASS=$(jq -r '.flags.halt_on_core_bypass // false' "$MANIFEST")
    OLD_VERSION=$(jq -r .template_version "$MANIFEST")
    mode_str="${MODE:-(none)}"
    echo "Found manifest: variant=$VARIANT, mode=$mode_str, extensions=[${EXTENSIONS[*]}], template=$OLD_VERSION"
else
    echo "No .deploy_manifest.json — pre-manifest deploy. Sniffing..."
    # Sniff variant from CLAUDE.md
    if grep -q "macroeconomics theory paper" "$PROJECT/CLAUDE.md" 2>/dev/null; then
        VARIANT="macro"
    elif grep -q "language-model cognition paper" "$PROJECT/CLAUDE.md" 2>/dev/null; then
        VARIANT="llm_cognition"
    elif grep -q "finance theory paper" "$PROJECT/CLAUDE.md" 2>/dev/null; then
        VARIANT="finance"
    else
        VARIANT=""
    fi
    # Mode cannot be sniffed reliably — every empirical-first signature in a
    # deployed project (mechanism body content, identification at Stage 1)
    # could be retrofitted by hand or look the same across different
    # decisions. Default to empty; user can pass --mode if their pre-manifest
    # deploy was empirical-first.
    MODE=""
    EXTENSIONS=()
    [ -f "$PROJECT/code/utils/wrds_client.py" ] && EXTENSIONS+=("empirical")
    [ -f "$PROJECT/code/llm_client.py" ] && EXTENSIONS+=("theory_llm")
    [ -d "$PROJECT/output/seed" ] && SEEDED=true || SEEDED=false
    FAITHFUL=$(jq -r '.faithful // false' "$PROJECT/process_log/pipeline_state.json" 2>/dev/null || echo false)
    [ ! -d "$PROJECT/output/stage0" ] && [ ! -f "$PROJECT/dashboard.html" ] && MANUAL=true || MANUAL=false
    LIGHT=false
    # Pre-manifest deploys predate the core-bypass guard; default off. The
    # operator can re-assert it by re-running setup with --halt-on-core-bypass.
    HALT_ON_CORE_BYPASS=false
    OLD_VERSION="(pre-manifest)"

    if [ -z "$VARIANT" ] && [ -z "$OVERRIDE_VARIANT" ]; then
        echo "Could not infer variant. Pass --variant finance|macro|llm_cognition."
        exit 1
    fi
    echo "Inferred: variant=$VARIANT, extensions=[${EXTENSIONS[*]}], seeded=$SEEDED, manual=$MANUAL"
fi

ORIGINAL_SEEDED="$SEEDED"
ORIGINAL_FAITHFUL="$FAITHFUL"
ORIGINAL_MODE="$MODE"
ORIGINAL_EXT_STR="${EXTENSIONS[*]}"

# ── Apply explicit overrides (precedence: CLI flag > manifest > sniff) ──
APPLIED_OVERRIDES=()
if [ -n "$OVERRIDE_VARIANT" ] && [ "$OVERRIDE_VARIANT" != "$VARIANT" ]; then
    if [ -f "$MANIFEST" ]; then
        echo "Error: update cannot migrate project-owned paper/state across variants." >&2
        echo "  Create a fresh deployment with --variant $OVERRIDE_VARIANT." >&2
        exit 1
    fi
    APPLIED_OVERRIDES+=("variant identification: $VARIANT → $OVERRIDE_VARIANT")
    VARIANT="$OVERRIDE_VARIANT"
fi
if [ "$OVERRIDE_MODE_SET" = "1" ] && [ "$OVERRIDE_MODE" != "$MODE" ]; then
    old_mode_str="${MODE:-(none)}"
    new_mode_str="${OVERRIDE_MODE:-(none)}"
    APPLIED_OVERRIDES+=("mode: $old_mode_str → $new_mode_str")
    MODE="$OVERRIDE_MODE"
    # Mode change can leave a stale current_stage in pipeline_state.json that
    # references a stage marker only valid in the prior mode (e.g., the
    # empirical-first marker `stage_1_identification_design` has no handler
    # under theory-first). The session-start resume path would then stall.
    # Surface this so the operator can reset current_stage before relaunching.
    MODE_CHANGE_ADVISORY=1
fi
if [ "$OVERRIDE_EXTS_SET" = "1" ]; then
    OLD_EXT_STR="${EXTENSIONS[*]}"
    NEW_EXT_STR="${OVERRIDE_EXTS[*]}"
    if [ "$OLD_EXT_STR" != "$NEW_EXT_STR" ]; then
        APPLIED_OVERRIDES+=("extensions: [$OLD_EXT_STR] → [$NEW_EXT_STR]")
        EXTENSIONS=("${OVERRIDE_EXTS[@]}")
    fi
fi
if [ -n "$OVERRIDE_SEEDED" ] && [ "$OVERRIDE_SEEDED" != "$SEEDED" ]; then
    APPLIED_OVERRIDES+=("seeded: $SEEDED → $OVERRIDE_SEEDED")
    SEEDED="$OVERRIDE_SEEDED"
fi
if [ "$OVERRIDE_SEEDED" = "false" ]; then
    FAITHFUL=false
fi
if [ -n "$OVERRIDE_FAITHFUL" ] && [ "$OVERRIDE_FAITHFUL" != "$FAITHFUL" ]; then
    APPLIED_OVERRIDES+=("faithful: $FAITHFUL → $OVERRIDE_FAITHFUL")
    FAITHFUL="$OVERRIDE_FAITHFUL"
fi
if [ "$FAITHFUL" = "true" ]; then
    if [ "$OVERRIDE_SEEDED" = "false" ]; then
        echo "Error: --faithful and --no-seeded are mutually exclusive" >&2
        exit 1
    fi
    SEEDED=true
fi
if [ -n "$OVERRIDE_MANUAL" ] && [ "$OVERRIDE_MANUAL" != "$MANUAL" ]; then
    echo "Error: update cannot migrate between autonomous and manual project layouts." >&2
    echo "  Create a fresh deployment with the desired --manual setting." >&2
    exit 1
fi
if [ -n "$OVERRIDE_LIGHT" ] && [ "$OVERRIDE_LIGHT" != "$LIGHT" ]; then
    APPLIED_OVERRIDES+=("light: $LIGHT → $OVERRIDE_LIGHT")
    LIGHT="$OVERRIDE_LIGHT"
fi
if [ ${#APPLIED_OVERRIDES[@]} -gt 0 ]; then
    echo
    echo "Applying overrides:"
    for o in "${APPLIED_OVERRIDES[@]}"; do echo "  $o"; done
fi
if { [ "$ORIGINAL_MODE" = "report" ] && [ "$MODE" != "report" ]; } \
   || { [ "$ORIGINAL_MODE" != "report" ] && [ "$MODE" = "report" ]; }; then
    echo "Error: update cannot migrate between report and autonomous project layouts." >&2
    echo "  Create a fresh deployment with the desired --mode setting." >&2
    exit 1
fi
SEED_SELECTOR_CHANGE=0
if [ "$SEEDED" != "$ORIGINAL_SEEDED" ] || [ "$FAITHFUL" != "$ORIGINAL_FAITHFUL" ]; then
    SEED_SELECTOR_CHANGE=1
fi
SCHEMA_SELECTOR_CHANGE=0
if [ "$MODE" != "$ORIGINAL_MODE" ] || [ "${EXTENSIONS[*]}" != "$ORIGINAL_EXT_STR" ]; then
    SCHEMA_SELECTOR_CHANGE=1
fi
STATEFUL_SCHEMA_SELECTOR_CHANGE="$SCHEMA_SELECTOR_CHANGE"
if [ "$MANUAL" = "true" ] || [ "$MODE" = "report" ]; then
    # These same-layout extension refreshes have no pipeline_state.json or
    # autonomous output skeleton by design; managed infrastructure is enough.
    STATEFUL_SCHEMA_SELECTOR_CHANGE=0
fi
if [ "${MODE_CHANGE_ADVISORY:-0}" = "1" ]; then
    echo
    echo "  ⚠ Mode changed. Verify process_log/pipeline_state.json:current_stage is"
    echo "    valid in the new mode before relaunching the pipeline."
    echo "    - Empirical-first marker 'stage_1_identification_design' has no handler"
    echo "      under theory-first; reset to 'stage_1' or 'stage_2' if present."
    echo "    - Theory-first stage markers are all valid under empirical-first too,"
    echo "      so converting theory-first → empirical-first usually needs no reset"
    echo "      (unless the run is in Stage 2 mid-derivation — in which case reset"
    echo "      to 'stage_1' to re-enter and pick up Step 4 identification design)."
    echo "    See README.md (Modes section) and the runtime doc's halted-status"
    echo "    handler for the full procedure."
fi

# ── One-time folder rename: referee_reports → simulated_referee_reports (issue #35) ──
# Existing deployments have paper/referee_reports/; the template now emits
# paper/simulated_referee_reports/. Migrate in place when only the old name exists.
if [ -d "$PROJECT/paper/referee_reports" ] && [ ! -d "$PROJECT/paper/simulated_referee_reports" ]; then
    if [ "$DRY_RUN" = "1" ]; then
        echo "  (dry-run) would rename paper/referee_reports → paper/simulated_referee_reports"
    else
        mv "$PROJECT/paper/referee_reports" "$PROJECT/paper/simulated_referee_reports"
        echo "  ✓ renamed paper/referee_reports → paper/simulated_referee_reports"
    fi
elif [ -d "$PROJECT/paper/referee_reports" ] && [ -d "$PROJECT/paper/simulated_referee_reports" ]; then
    echo "  ⚠ Both paper/referee_reports/ and paper/simulated_referee_reports/ exist — skipping auto-rename. Inspect manually and merge if needed."
fi

# ── Build setup.sh flag list ──
# When adding a new setup.sh flag, update both this block AND the manifest-
# read block above so update→deploy round-trips preserve the deployment.
SETUP_FLAGS=( --variant "$VARIANT" --assemble-only )
[ "$NO_MODEL_PROBE" = "1" ] && SETUP_FLAGS+=( --no-model-probe )
[ -n "$MODE" ] && SETUP_FLAGS+=( --mode "$MODE" )
for ext in "${EXTENSIONS[@]}"; do SETUP_FLAGS+=( --ext "$ext" ); done
if [ "$FAITHFUL" = "true" ]; then
    SETUP_FLAGS+=( --faithful )
elif [ "$SEEDED" = "true" ]; then
    SETUP_FLAGS+=( --seed )
fi
[ "$MANUAL" = "true" ] && SETUP_FLAGS+=( --manual )
[ "$LIGHT" = "true" ] && SETUP_FLAGS+=( --light )
[ "$HALT_ON_CORE_BYPASS" = "true" ] && SETUP_FLAGS+=( --halt-on-core-bypass )

# ── Deploy fresh into tmp ──
TMP=$(mktemp -d "$UPDATE_CONTROL_DIR/update.XXXXXX")
FRESH="$TMP/refresh"
SETUP_TMPDIR="$TMP/setup-tmp"
(umask 077 && mkdir "$SETUP_TMPDIR")

echo
echo "Deploying fresh template into $FRESH ..."
( cd "$TEMPLATE_ROOT" && TMPDIR="$SETUP_TMPDIR" ./setup.sh "$FRESH" "${SETUP_FLAGS[@]}" ) >"$TMP/deploy.log" 2>&1 || {
    echo "Fresh deploy failed. Last 40 lines of log:"
    tail -40 "$TMP/deploy.log"
    exit 1
}
echo "  ✓ fresh deploy ok ($(wc -l < "$TMP/deploy.log") log lines)"

NEW_MANIFEST="$FRESH/.deploy_manifest.json"
if [ ! -f "$NEW_MANIFEST" ]; then
    echo "ERROR: fresh deploy did not produce a manifest. Is setup.sh up to date?"
    exit 1
fi
if ! NEW_VERSION="$(jq -er '.template_version | strings | select(length > 0)' "$NEW_MANIFEST")"; then
    echo "ERROR: fresh deploy manifest has no valid template_version" >&2
    exit 1
fi

# Pre-sandbox agents could have aliased any managed parent, not just
# `.opencode`. Validate every existing ancestor used by replacement, merging,
# or stale sweeping before the first target mutation.
python3 -I - "$PROJECT" "$NEW_MANIFEST" "$MANIFEST" <<'PY'
import json, os, stat, sys
from pathlib import PurePosixPath

project, new_path, old_path = sys.argv[1:]
manifests = [json.load(open(new_path, encoding="utf-8"))]
if os.path.isfile(old_path):
    manifests.append(json.load(open(old_path, encoding="utf-8")))
paths = set()
for manifest in manifests:
    infra = manifest.get("infrastructure", {})
    for key in ("dirs_replace", "files_replace", "files_env_merge"):
        values = infra.get(key, [])
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise SystemExit(f"ERROR: invalid manifest path list: {key}")
        paths.update(values)
for value in paths:
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise SystemExit(f"ERROR: unsafe manifest path: {value!r}")
    current = project
    for part in pure.parts[:-1]:
        current = os.path.join(current, part)
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise SystemExit(f"ERROR: managed path ancestor is not a real directory: {current}")
        if os.path.commonpath((project, os.path.realpath(current))) != project:
            raise SystemExit(f"ERROR: managed path ancestor escapes deployment: {current}")
for manifest in manifests:
    for value in manifest.get("infrastructure", {}).get("files_env_merge", []):
        target = os.path.join(project, value)
        if not os.path.lexists(target):
            continue
        info = os.lstat(target)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SystemExit(
                f"ERROR: environment target must be one regular non-aliased file: {target}"
            )
PY

# Seed/faithful selection has project-owned bootstrap effects as well as
# manifest-managed runtime effects. Run only after every managed ancestor has
# passed its fail-closed validation, and only before a pipeline starts. Never
# delete seed material when leaving seeded mode; it remains operator-owned.
if [ "$SEED_SELECTOR_CHANGE" = "1" ] || [ "$STATEFUL_SCHEMA_SELECTOR_CHANGE" = "1" ]; then
    SEED_MIGRATION_JOURNAL="$TMP/seed-migration.json"
    python3 -I - "$PROJECT" "$FRESH" "$SEEDED" "$FAITHFUL" "$DRY_RUN" \
        "$SEED_MIGRATION_JOURNAL" "$STATEFUL_SCHEMA_SELECTOR_CHANGE" <<'PY'
import json
import os
import stat
import sys

project, fresh, seeded_text, faithful_text, dry_text, journal_path, schema_text = sys.argv[1:]
seeded = seeded_text == "true"
faithful = faithful_text == "true"
dry_run = dry_text == "1"
schema_change = schema_text == "1"
state_path = os.path.join(project, "process_log", "pipeline_state.json")
flags = (os.O_RDONLY if dry_run else os.O_RDWR) | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(state_path, flags)
state_info = os.fstat(fd)
if not stat.S_ISREG(state_info.st_mode) or state_info.st_nlink != 1:
    os.close(fd)
    raise SystemExit("ERROR: seed migration requires one regular non-aliased pipeline_state.json")
with os.fdopen(fd, "r", encoding="utf-8") as handle:
    original_state = handle.read()
    state = json.loads(original_state)
    if state.get("status") != "not_started":
        raise SystemExit(
            "ERROR: mode/extension/seed migration is supported only before the pipeline starts; "
            "create a fresh deployment or preserve the existing selector"
        )
    output = os.path.join(project, "output")
    seed = os.path.join(output, "seed")
    paths = (output, seed) if seeded else ()
    for path in paths:
        if os.path.lexists(path):
            info = os.lstat(path)
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                raise SystemExit(f"ERROR: seed migration path must be a real directory: {path}")
    readme = os.path.join(seed, "README.md")
    if seeded and os.path.lexists(readme):
        info = os.lstat(readme)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SystemExit(f"ERROR: seed README must be one regular non-aliased file: {readme}")
    if dry_run:
        raise SystemExit(0)

    created_seed = False
    created_readme = False
    created_dirs = []
    try:
        if schema_change:
            fresh_output = os.path.join(fresh, "output")
            for root, dirs, _files in os.walk(fresh_output):
                dirs[:] = sorted(name for name in dirs if not (
                    os.path.relpath(os.path.join(root, name), fresh_output).split(os.sep)[0]
                    == "seed"
                ))
                rel = os.path.relpath(root, fresh)
                target = os.path.join(project, rel)
                if not os.path.lexists(target):
                    os.mkdir(target)
                    created_dirs.append(target)
                else:
                    info = os.lstat(target)
                    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                        raise SystemExit(
                            f"ERROR: selector migration path must be a real directory: {target}"
                        )
        if seeded and not os.path.exists(seed):
            os.mkdir(seed)
            created_seed = True
        if seeded and not os.path.lexists(readme):
            source = os.path.join(fresh, "output", "seed", "README.md")
            with open(source, "rb") as src:
                data = src.read()
            readme_fd = os.open(
                readme,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                0o644,
            )
            with os.fdopen(readme_fd, "wb") as target:
                target.write(data)
                target.flush()
                os.fsync(target.fileno())
            created_readme = True
        journal = {
            "state_path": state_path,
            "state_mode": stat.S_IMODE(state_info.st_mode),
            "original_state": original_state,
            "fresh_state_path": os.path.join(fresh, "process_log", "pipeline_state.json"),
            "schema_change": schema_change,
            "seed": seed,
            "readme": readme,
            "created_seed": created_seed,
            "created_readme": created_readme,
            "created_dirs": created_dirs,
            "state_committed": False,
        }
        fd = os.open(
            journal_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        with os.fdopen(fd, "w", encoding="utf-8") as target:
            json.dump(journal, target)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
    except BaseException:
        try:
            if created_readme and os.path.lexists(readme):
                os.unlink(readme)
            if created_seed and os.path.isdir(seed):
                os.rmdir(seed)
            for path in reversed(created_dirs):
                if os.path.isdir(path) and not os.path.islink(path):
                    os.rmdir(path)
        except OSError:
            pass
        raise
PY
    if [ "$DRY_RUN" = "1" ]; then
        echo "  project state: would migrate compatible pre-launch selectors"
    else
        SEED_MIGRATION_PENDING=1
        echo "  ✓ prepared project state migration"
    fi
fi

# ── Snapshot agent set BEFORE replacement (for diff) ──
OLD_AGENTS_TMP="$TMP/old_agents.txt"
NEW_AGENTS_TMP="$TMP/new_agents.txt"
ls "$PROJECT/.claude/agents/" 2>/dev/null | sort > "$OLD_AGENTS_TMP" || true
ls "$FRESH/.claude/agents/"   2>/dev/null | sort > "$NEW_AGENTS_TMP" || true

# ── Apply replacements ──
echo
if [ "$DRY_RUN" = "1" ]; then
    echo "=== DRY RUN — would replace ==="
else
    echo "=== Replacing infrastructure ==="
fi

while IFS= read -r d; do
    [ -d "$FRESH/$d" ] || continue
    if [ "$DRY_RUN" = "1" ]; then
        echo "  dir : $d"
    else
        rm -rf "$PROJECT/$d"
        mkdir -p "$(dirname "$PROJECT/$d")"
        cp -r "$FRESH/$d" "$PROJECT/$d"
        echo "  dir ✓ $d"
    fi
done < <(jq -r '.infrastructure.dirs_replace[]' "$NEW_MANIFEST")

while IFS= read -r f; do
    [ -f "$FRESH/$f" ] || continue
    # Guard against type mismatch: target exists as a directory where the
    # manifest expects a file. cp into a dir would silently put the file
    # *inside* the dir rather than replacing it.
    if [ -d "$PROJECT/$f" ]; then
        echo "  file ! $f — target is a directory; skipping (manual fix needed)"
        continue
    fi
    if [ "$DRY_RUN" = "1" ]; then
        echo "  file: $f"
    else
        mkdir -p "$(dirname "$PROJECT/$f")"
        # rm -f handles three cases that cp won't: regular symlinks (cp would
        # follow and overwrite the target, corrupting wherever it points),
        # dangling symlinks (cp errors with "not writing through dangling
        # symlink"), and read-only files. Plain files are removed cleanly.
        rm -f "$PROJECT/$f"
        cp "$FRESH/$f" "$PROJECT/$f"
        echo "  file ✓ $f"
    fi
done < <(jq -r '.infrastructure.files_replace[]' "$NEW_MANIFEST")

# ── Stale-infrastructure sweep (issue #205) ──
# A path recorded as infrastructure in the TARGET's existing manifest but
# absent from the fresh manifest is infrastructure this template version no
# longer deploys for this variant/mode/extension set (e.g. per-variant skill
# gating dropped the ssj + nber-agenda util dirs from llm_cognition). Leaving
# it would let old deployments diverge permanently from a fresh deploy, so
# remove it. Only paths the old deploy's own manifest called infrastructure
# are candidates — user content is never listed there. Pre-manifest deploys
# have no old manifest, so there is nothing to sweep. files_env_merge (.env)
# is deliberately not swept: it is user-merged, not replaced.
if [ -f "$MANIFEST" ]; then
    sweep() {
        local kind="$1" jqlist="$2" testflag="$3" p
        while IFS= read -r p; do
            # Manifest paths are repo-relative by construction; refuse
            # anything that could escape the project tree.
            case "$p" in /*|*..*|"") continue ;; esac
            case "$kind:$p" in
                dir:.claude/agents|dir:.claude/skills|dir:.codex/agents|dir:.agents/skills|\
                dir:.gemini/agents|dir:.grok/agents|dir:.opencode/agents|dir:docs|\
                dir:code/utils/codex_math|dir:code/utils/agent_launcher|dir:code/utils/bib_verify|\
                dir:code/utils/openalex|dir:code/utils/nber_agenda|dir:code/utils/model_heal|dir:code/utils/ssj)
                    ;;
                file:CLAUDE.md|file:AGENTS.md|file:GEMINI.md|file:launch.sh|\
                file:docs/start_session_claude.md|file:docs/start_session_codex.md|file:docs/start_session_gemini.md|\
                file:.claude/settings.json|file:.gemini/settings.json|file:.grok/sandbox.toml|\
                file:.opencode/sandbox.json|file:.opencode/opencode_driver.py|\
                file:.opencode/opencode_sandbox_exec.sh|file:.opencode/opencode_sandbox_exec.mjs|\
                file:opencode.json|file:.gitignore|file:dashboard.html|file:llm_client.py|\
                file:.arpipeline/update_inputs/pipeline_dotenv_guard.py|\
                file:.arpipeline/update_inputs/deps/core.txt|file:.arpipeline/update_inputs/deps/ssj.txt|\
                file:.arpipeline/update_inputs/deps/extensions/empirical.txt|\
                file:.arpipeline/update_inputs/deps/extensions/theory_llm.txt|\
                file:code/utils/setup_push_token.sh|file:code/utils/codex_preflight.sh|\
                file:code/utils/bls_census_utils.py|file:code/utils/call_reports_utils.py|\
                file:code/utils/chen_zimmerman_utils.py|file:code/utils/download_crsp_daily.py|\
                file:code/utils/download_crsp_monthly.py|file:code/utils/edgar_utils.py|\
                file:code/utils/form_5500_utils.py|file:code/utils/fred_utils.py|\
                file:code/utils/hrs_scf_utils.py|file:code/utils/ken_french_utils.py|\
                file:code/utils/mutual_fund_utils.py|file:code/utils/open_bond_pricing_utils.py|\
                file:code/utils/process_crsp_daily.py|file:code/utils/process_crsp_monthly.py|\
                file:code/utils/sec_funds_utils.py|file:code/utils/start_services.sh|\
                file:code/utils/trace_bonds_utils.py|file:code/utils/treasury_yields_utils.py|\
                file:code/utils/wrds_client.py|file:code/utils/wrds_server.py|file:code/utils/wrds_utils.py)
                    ;;
                *)
                    echo "  stale $kind: $p (untrusted legacy path — preserved)"
                    continue
                    ;;
            esac
            # Never let an untrusted old manifest remove a current managed path
            # or one of its ancestors/descendants.
            if jq -e --arg p "$p" '
                [.infrastructure.dirs_replace[]?, .infrastructure.files_replace[]?, .infrastructure.files_env_merge[]?]
                | any(. as $q | $q == $p or ($q | startswith($p + "/")) or ($p | startswith($q + "/")))
            ' "$NEW_MANIFEST" >/dev/null; then
                continue
            fi
            [ $testflag "$PROJECT/$p" ] || continue
            if [ "$DRY_RUN" = "1" ]; then
                echo "  stale $kind: $p (no longer deployed — would remove)"
            else
                rm -rf "$PROJECT/$p"
                echo "  stale $kind ✗ $p (no longer deployed — removed)"
            fi
        done < <(jq -r --slurpfile new "$NEW_MANIFEST" \
            ".infrastructure.${jqlist}[]? | select(. as \$p | (\$new[0].infrastructure.${jqlist} // [] | index(\$p)) | not)" \
            "$MANIFEST")
    }
    sweep dir dirs_replace -d
    sweep file files_replace -f
fi

# Extension dependency specs are individual manifest-owned files. When the
# last extension is removed, converge with a fresh extension-free deployment
# by removing their now-empty structural parent. rmdir is deliberately
# non-recursive: any project-owned content makes the directory survive.
if [ "$DRY_RUN" = "0" ]; then
    rmdir "$PROJECT/.arpipeline/update_inputs/deps/extensions" 2>/dev/null || true
fi

# ── Merge .env (append missing keys only; never overwrite values) ──
echo
echo "=== Merging .env ==="
while IFS= read -r env_file; do
    if [ -f "$FRESH/$env_file" ] && { [ -e "$PROJECT/$env_file" ] || [ -L "$PROJECT/$env_file" ]; }; then
        python3 -I - "$FRESH/$env_file" "$PROJECT/$env_file" "$DRY_RUN" <<'PY'
import os, stat, sys

source, target, dry_run = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
flags = os.O_RDONLY if dry_run else os.O_RDWR
flags |= getattr(os, "O_NOFOLLOW", 0)
fd = os.open(target, flags)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    os.close(fd)
    raise SystemExit(f"ERROR: environment target must be one regular non-aliased file: {target}")
with os.fdopen(fd, "r" if dry_run else "r+", encoding="utf-8", newline="") as handle:
    existing = handle.read()
    additions = []
    for line in open(source, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        key = line.split("=", 1)[0]
        if not any(row.startswith(key + "=") for row in existing.splitlines()):
            additions.append((key, line))
            existing += ("" if not existing or existing.endswith("\n") else "\n") + line + "\n"
    for key, _line in additions:
        print(f"  + {key}" + (" (would add)" if dry_run else ""))
    if not additions:
        print("  (no new keys)")
    if additions and not dry_run:
        handle.seek(0)
        handle.write(existing)
        handle.truncate()
        handle.flush()
        os.fsync(handle.fileno())
PY
    elif [ ! -e "$PROJECT/$env_file" ] && [ ! -L "$PROJECT/$env_file" ] && [ -f "$FRESH/$env_file" ]; then
        echo "  ! $env_file missing in target — copying fresh"
        if [ "$DRY_RUN" = "0" ]; then
            cp "$FRESH/$env_file" "$PROJECT/$env_file"
        fi
    fi
done < <(jq -r '.infrastructure.files_env_merge[]?' "$NEW_MANIFEST")

# ── Refresh the stdin-safe dotenv guard in the venv ──
# Counterpart of setup.sh's install step (see templates/utils/
# pipeline_dotenv_guard.py — installed as module + .pth, not sitecustomize.py,
# which Homebrew's stdlib copy shadows). The guard lives inside the gitignored
# .venv, so that installed copy is refreshed as a dedicated step; its verified
# source is a manifest-owned update input in the fresh assembly. Skipped when
# the target has no venv or that staged source is unavailable.
_guard_src="$FRESH/.arpipeline/update_inputs/pipeline_dotenv_guard.py"
if [ -f "$_guard_src" ] && [ -d "$PROJECT/.venv" ] && [ ! -L "$PROJECT/.venv" ]; then
    _venv_sp="$(python3 -I - "$PROJECT/.venv" <<'PY'
import glob, os, stat, sys
root = os.path.abspath(sys.argv[1])
if os.path.realpath(root) != root:
    raise SystemExit(1)
candidates = []
for path in glob.glob(os.path.join(root, "lib", "python*", "site-packages")):
    current = root
    safe = True
    for part in os.path.relpath(path, root).split(os.sep):
        current = os.path.join(current, part)
        info = os.lstat(current)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            safe = False
            break
    if safe and os.path.commonpath((root, os.path.realpath(path))) == root:
        candidates.append(path)
if candidates:
    print(sorted(candidates)[-1])
PY
)"
    if [ -n "$_venv_sp" ] && [ -d "$_venv_sp" ]; then
        if [ "$DRY_RUN" = "1" ]; then
            echo "  venv: would refresh _pipeline_dotenv_guard (dotenv stdin guard)"
        else
            rm -f "$_venv_sp/_pipeline_dotenv_guard.py" "$_venv_sp/_pipeline_dotenv_guard.pth"
            cp "$_guard_src" "$_venv_sp/_pipeline_dotenv_guard.py"
            printf 'import _pipeline_dotenv_guard\n' > "$_venv_sp/_pipeline_dotenv_guard.pth"
            # Remove the shadowed first-attempt install — but only if it is
            # OURS (the old file carries the _find_dotenv_stdin_safe wrapper).
            # A user-created sitecustomize.py (e.g. coverage.py's documented
            # subprocess-coverage hook) must survive the refresh.
            if [ -f "$_venv_sp/sitecustomize.py" ] && [ ! -L "$_venv_sp/sitecustomize.py" ] \
               && grep -q '_find_dotenv_stdin_safe' "$_venv_sp/sitecustomize.py" 2>/dev/null; then
                rm -f "$_venv_sp/sitecustomize.py"
            fi
            echo "  venv ✓ _pipeline_dotenv_guard (dotenv stdin guard)"
        fi
    else
        echo "  ⚠ venv present but site-packages could not be located — dotenv stdin guard not refreshed"
    fi
fi

# ── Migrate pipeline_state.json to the loops:{} shape (issue #166) ──
# The refreshed runtime docs reference loops.<id>.round; an in-flight deployment's
# pipeline_state.json (never in the manifest, so preserved verbatim) may still carry
# the legacy named counters. Fold them into a single `loops` object, preserving the
# in-progress round values, so a resumed run's state matches the new docs. New core
# loops are also added with setdefault semantics: ordinary same-selector updates do
# not run the extension/mode schema merge, but must still satisfy refreshed core docs.
STATE_FILE="$PROJECT/process_log/pipeline_state.json"
if [ -L "$PROJECT/process_log" ] || { [ -e "$PROJECT/process_log" ] && [ ! -d "$PROJECT/process_log" ]; }; then
    echo "ERROR: $PROJECT/process_log must be a real project directory" >&2
    exit 1
fi
if [ -d "$PROJECT/process_log" ] && [ "$(cd "$PROJECT/process_log" && pwd -P)" != "$PROJECT/process_log" ]; then
    echo "ERROR: $PROJECT/process_log resolves outside the deployment" >&2
    exit 1
fi
if [ "$DRY_RUN" = "0" ] && { [ -e "$STATE_FILE" ] || [ -L "$STATE_FILE" ]; }; then
    CORE_STATE_CANDIDATE="$TMP/core-pipeline-state.next"
    python3 -I - "$STATE_FILE" "$CORE_STATE_CANDIDATE" <<'PYEOF'
import json, os, re, stat, sys
from datetime import datetime, timezone
p, candidate_path = sys.argv[1:]
flags = os.O_RDWR | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(p, flags)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    os.close(fd)
    raise SystemExit(f"ERROR: pipeline state must be one regular non-aliased file: {p}")
with os.fdopen(fd, "r+", encoding="utf-8") as f:
 data = json.load(f)
 changed = False
 legacy_exhausted_attempts = set()
 legacy_domain_scan_count = 0
 legacy_stage0_artifact_evidence = False
 project_dir = os.path.dirname(os.path.dirname(p))
 dir_flags = (
    os.O_RDONLY
    | os.O_NONBLOCK
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
 )
 def open_project_dir(parent_fd, name, label):
    try:
        return os.open(name, dir_flags, dir_fd=parent_fd)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise SystemExit(f"ERROR: {label} must be a real directory inside the deployment: {exc}")
 try:
    project_fd = os.open(project_dir, dir_flags)
 except OSError as exc:
    raise SystemExit(f"ERROR: deployment root is not a real directory: {exc}")
 try:
    output_fd = open_project_dir(project_fd, "output", "output")
 finally:
    os.close(project_fd)
 stage0_fd = None
 if output_fd is not None:
    try:
        stage0_fd = open_project_dir(output_fd, "stage0", "output/stage0")
    finally:
        os.close(output_fd)
 if stage0_fd is not None:
    try:
        for entry in os.scandir(stage0_fd):
            # Fresh autonomous deployments create an empty stage0 directory.
            # Any retained entry therefore proves the project is non-pristine,
            # including pre-v2.18.1 maps that have no domain log or report.
            legacy_stage0_artifact_evidence = True
            match = re.fullmatch(r"branch_manager_discovery_p([0-9]+)\.md", entry.name)
            if match and entry.is_file(follow_symlinks=False):
                legacy_exhausted_attempts.add(int(match.group(1)))
        try:
            log_flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
            log_fd = os.open("domain_log.md", log_flags, dir_fd=stage0_fd)
        except FileNotFoundError:
            log_fd = None
        except OSError as exc:
            raise SystemExit(f"ERROR: output/stage0/domain_log.md must be a regular project file: {exc}")
        if log_fd is not None:
            log_info = os.fstat(log_fd)
            if not stat.S_ISREG(log_info.st_mode) or log_info.st_nlink != 1:
                os.close(log_fd)
                raise SystemExit("ERROR: output/stage0/domain_log.md must be one regular non-aliased file")
            with os.fdopen(log_fd, "r", encoding="utf-8") as domain_log:
                legacy_domain_scan_count = sum(1 for line in domain_log if line.strip())
    finally:
        os.close(stage0_fd)
 # The retired halt itself proves the current scan exhausted even if a legacy
 # report is absent (for example, a partially retained pre-update output tree).
 current_problem_attempt = int(data.get("problem_attempt", 1) or 1)
 retired_stage0_halt = data.get("status") == "halted_no_viable_question"
 if retired_stage0_halt:
    legacy_exhausted_attempts.add(current_problem_attempt)
 # No pre-#252 state can prove its lifetime physical-launch count: deployments
 # before v2.18.1 have no domain log, and later scored scans have no exhausted
 # report. Preserve the strict ceiling by failing closed for every non-pristine
 # legacy run. A never-started deployment is the only shape known to have spent
 # zero permits; active legacy runs retain their artifacts and enter autonomous
 # near-miss promotion at the cap.
 legacy_stage0_activity = (
    data.get("status") != "not_started"
    or current_problem_attempt > 1
    or legacy_domain_scan_count > 0
    or bool(legacy_exhausted_attempts)
    or legacy_stage0_artifact_evidence
 )
 legacy_scan_count = 100 if legacy_stage0_activity else 0
 if "loops" not in data:
    # legacy field -> (loop id, default cap)
    base = {
        "gate0_revise_cycles":               ("gate0_revise", 3),
        "gate0_questions_rejected":          ("gate0_reject", 5),
        "idea_round":                        ("idea", 5),
        "reject_cosmetic_round":             ("reject_cosmetic", 2),
        "downgrade_enrich_round":            ("downgrade_enrich", 2),
        "pivot_round":                       ("pivot", 2),
        "fix_empirics_round":                ("fix_empirics", 2),
        "referee_round":                     ("referee", 10),
        "bib_verify_round":                  ("bib_verify", 2),
        "polish_round":                      ("polish", 2),
    }
    emp = {
        "identification_plan_revision_round": ("identification_plan_revision", 3),
        "headline_replication_round":        ("headline_replication", 3),
        "data_integrity_round":              ("data_integrity", 3),
        "method_check_round":                ("method_check", 3),
        "claim_grounding_round":             ("claim_grounding", 3),
        "paper_writer_pse_round":            ("paper_writer_pse", 3),
        "claim_format_reexport_round":       ("claim_format_reexport", 2),
    }
    loops = {}
    # Always seed the full base set (round from legacy value if present, else 0).
    for legacy, (lid, cap) in base.items():
        loops[lid] = {"round": int(data.pop(legacy, 0) or 0), "cap": cap}
    # Unknown active legacy history fails closed at the run-global cap; only a
    # pristine not_started deployment can soundly receive all 100 permits.
    loops["stage0_discovery"] = {"round": legacy_scan_count, "cap": 100}
    # Seed empirical loops only if this deployment had them (any legacy empirical
    # counter present, or the empirical version pointer exists).
    had_emp = any(k in data for k in emp) or "stage3a_theory_version" in data
    for legacy, (lid, cap) in emp.items():
        v = data.pop(legacy, None)
        if had_emp:
            loops[lid] = {"round": int(v or 0), "cap": cap}
    if had_emp:
        loops["replicator_self_refire"] = {"round": 0, "cap": 3}
    # The Jaccard companion field is deleted outright.
    data.pop("paper_writer_pse_claim_ids", None)
    # Insert `loops` after gate0_best_question_score if present, else at a stable spot.
    new = {}
    inserted = False
    for k, v in data.items():
        new[k] = v
        if k == "gate0_best_question_score":
            new["loops"] = loops
            inserted = True
    if not inserted:
        new["loops"] = loops
    data = new
    changed = True
    print("  ✓ pipeline_state.json migrated to loops:{} (issue #166)")
 loops = data.get("loops")
 if not isinstance(loops, dict):
    raise SystemExit(f"ERROR: pipeline state loops must be an object: {p}")
 if "stage0_discovery_last_counted_attempt" not in data:
    data["stage0_discovery_last_counted_attempt"] = (
        current_problem_attempt
        if (
            retired_stage0_halt
            or (
                legacy_stage0_activity
                and data.get("current_stage") == "stage_0"
            )
            or (
                data.get("current_stage") == "stage_0"
                and current_problem_attempt in legacy_exhausted_attempts
            )
        )
        else None
    )
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 scan ownership marker (issue #252)")
 if "stage0_discovery_episode_start_attempt" not in data:
    data["stage0_discovery_episode_start_attempt"] = (
        current_problem_attempt
        if (
            retired_stage0_halt
            or (
                legacy_stage0_activity
                and data.get("current_stage") == "stage_0"
            )
        )
        else None
    )
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 episode boundary marker (issue #252)")
 if "stage0_discovery_phase" not in data:
    if (
        legacy_stage0_activity
        and (
            retired_stage0_halt
            or data.get("current_stage") == "stage_0"
        )
    ):
        data["stage0_discovery_phase"] = "legacy_reroute"
    elif (
        data.get("current_stage") == "stage_0"
        and current_problem_attempt in legacy_exhausted_attempts
    ):
        data["stage0_discovery_phase"] = "legacy_reroute"
    else:
        data["stage0_discovery_phase"] = "entry"
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 durable phase (issue #252)")
 if "stage0_discovery_step" not in data:
    data["stage0_discovery_step"] = (
        "select" if data.get("stage0_discovery_phase") == "gap_search" else None
    )
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 durable substep (issue #252)")
 if "stage0_discovery_cap_context" not in data:
    data["stage0_discovery_cap_context"] = None
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 cap-routing context (issue #252)")
 if "stage0_discovery_pending_scan" not in data:
    data["stage0_discovery_pending_scan"] = None
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 pending-scan payload (issue #252)")
 if "stage0_discovery_gap_serial" not in data:
    data["stage0_discovery_gap_serial"] = 0
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 stable gap serial (issue #252)")
 if "stage0_discovery_active_gap_id" not in data:
    data["stage0_discovery_active_gap_id"] = None
    changed = True
    print("  ✓ pipeline_state.json added Stage-0 active gap identity (issue #252)")
 if "stage0_discovery" not in loops:
    loops["stage0_discovery"] = {"round": legacy_scan_count, "cap": 100}
    changed = True
    print(f"  ✓ pipeline_state.json added core stage0_discovery loop at fail-closed round {legacy_scan_count} (issue #252)")
 # This exact halt was the retired terminal route for an exhausted Stage-0
 # domain scan. Resume it under the bounded discovery policy; every other
 # halted_* status remains operator-controlled.
 if retired_stage0_halt:
    data["status"] = "running"
    data["current_stage"] = "stage_0"
    history = data.setdefault("history", [])
    if not isinstance(history, list):
        raise SystemExit(f"ERROR: pipeline state history must be an array: {p}")
    history.append({
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": "update resumed retired halted_no_viable_question under bounded Stage-0 discovery",
    })
    changed = True
    print("  ✓ pipeline_state.json resumed retired Stage-0 terminal halt (issue #252)")
 if "table_legibility" not in loops:
    loops["table_legibility"] = {"round": 0, "cap": 3}
    changed = True
    print("  ✓ pipeline_state.json added core table_legibility loop (issue #253)")
 if changed:
    candidate_fd = os.open(
        candidate_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        stat.S_IMODE(info.st_mode),
    )
    with os.fdopen(candidate_fd, "w", encoding="utf-8") as candidate:
        json.dump(data, candidate, indent=2)
        candidate.write("\n")
        candidate.flush()
        os.fsync(candidate.fileno())
PYEOF
fi

# ── Bootstrap the project venv if missing ──
# Deploys made before the .venv change (or whose .venv was deleted) have no venv,
# but the refreshed runtime docs now tell the user/agents to
# `source .venv/bin/activate` and expect a bare `python3` to resolve there. Create
# it from the SAME manifest-owned dependency files setup.sh uses, so a refreshed
# legacy project matches both its new docs and the verified fresh assembly.
# A project that already has a .venv is left untouched — we never clobber an
# existing environment (its interpreter paths and user-installed packages).
VENV="$PROJECT/.venv"
if [ ! -d "$VENV" ]; then
    # ssj deps are variant-gated (issue #205; mirrors setup.sh's
    # variant_wants_skill — keep the two in sync when gating more skills).
    WANT_SSJ_DEPS=1
    [ "$VARIANT" = "llm_cognition" ] && WANT_SSJ_DEPS=0
    if [ "$DRY_RUN" = "1" ]; then
        echo
        echo "=== venv bootstrap ==="
        _ssj_label=""
        [ "$WANT_SSJ_DEPS" = "1" ] && _ssj_label=" + ssj"
        echo "  would create $VENV and install core${_ssj_label} + extension deps [${EXTENSIONS[*]}]"
    elif [ -z "$UPDATE_TOOL_UV" ] || [ ! -x "$UPDATE_TOOL_UV" ]; then
        echo
        echo "  ⚠ .venv missing and uv not found — install uv, then re-run update.sh (or create it manually)"
    else
        echo
        echo "=== Bootstrapping missing .venv ==="
        "$UPDATE_TOOL_UV" venv --python 3.12 "$VENV" 2>/dev/null \
            || "$UPDATE_TOOL_UV" venv --python 3.12 --clear "$VENV" 2>/dev/null \
            || "$UPDATE_TOOL_UV" venv --clear "$VENV" 2>/dev/null \
            || { rm -rf "$VENV"; echo "  ⚠ could not create $VENV (create manually: uv venv $VENV)"; }
        if [ -d "$VENV" ]; then
            "$UPDATE_TOOL_UV" pip install --python "$VENV" -r "$FRESH/.arpipeline/update_inputs/deps/core.txt" -q 2>/dev/null \
                && echo "  ✓ core deps installed" \
                || echo "  ⚠ core deps failed (source $VENV/bin/activate && uv pip install sympy matplotlib certifi)"
            if [ "$WANT_SSJ_DEPS" = "1" ]; then
                "$UPDATE_TOOL_UV" pip install --python "$VENV" -r "$FRESH/.arpipeline/update_inputs/deps/ssj.txt" -q 2>/dev/null \
                    && echo "  ✓ ssj deps installed" \
                    || echo "  ⚠ ssj deps skipped (numba build issue; non-fatal — ssj skill only)"
            fi
            for ext in "${EXTENSIONS[@]}"; do
                _extdeps="$FRESH/.arpipeline/update_inputs/deps/extensions/$ext.txt"
                [ -f "$_extdeps" ] || continue
                "$UPDATE_TOOL_UV" pip install --python "$VENV" -r "$_extdeps" -q 2>/dev/null \
                    && echo "  ✓ $ext deps installed" \
                    || echo "  ⚠ $ext deps failed (source $VENV/bin/activate && uv pip install -r extensions/$ext/deps.txt)"
            done
        fi
    fi
fi

# Commit the prepared project-owned selector state only after every other
# refresh step has succeeded. The journal is marked first, so any later shell,
# manifest, or process error restores the pre-commit state and removes only
# seed paths this update created.
if [ "$SEED_MIGRATION_PENDING" = "1" ]; then
    python3 -I - "$SEED_MIGRATION_JOURNAL" "$SEEDED" "$FAITHFUL" "$CORE_STATE_CANDIDATE" <<'PY'
import json
import os
import secrets
import stat
import sys

journal_path, seeded_text, faithful_text, core_candidate = sys.argv[1:]
seeded = seeded_text == "true"
faithful = faithful_text == "true"
journal = json.load(open(journal_path, encoding="utf-8"))
state_path = journal["state_path"]
fd = os.open(state_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    os.close(fd)
    raise SystemExit("ERROR: seed migration state changed before commit")
with os.fdopen(fd, "r", encoding="utf-8") as handle:
    original_state = handle.read()
if core_candidate and os.path.isfile(core_candidate):
    with open(core_candidate, encoding="utf-8") as handle:
        state = json.load(handle)
else:
    state = json.loads(original_state)
if state.get("status") != "not_started":
    raise SystemExit("ERROR: pipeline started while selector migration was being prepared")
if journal.get("schema_change"):
    with open(journal["fresh_state_path"], encoding="utf-8") as handle:
        fresh_state = json.load(handle)

    def merge_missing(current, expected):
        for key, value in expected.items():
            if key not in current:
                current[key] = value
            elif isinstance(current[key], dict) and isinstance(value, dict):
                merge_missing(current[key], value)

    merge_missing(state, fresh_state)
state["seeded"] = seeded
state["faithful"] = faithful
if seeded and state.get("current_stage") == "stage_0":
    state["current_stage"] = "seed_triage"
elif not seeded and state.get("current_stage") == "seed_triage":
    state["current_stage"] = "stage_0"

journal["original_state"] = original_state
journal["state_mode"] = stat.S_IMODE(info.st_mode)
journal["state_committed"] = True
journal_tmp = journal_path + ".next"
with open(journal_tmp, "x", encoding="utf-8") as handle:
    json.dump(journal, handle)
    handle.write("\n")
    handle.flush()
    os.fsync(handle.fileno())
os.replace(journal_tmp, journal_path)

state_tmp = os.path.join(
    os.path.dirname(state_path), f".pipeline-state.update.{secrets.token_hex(8)}"
)
try:
    state_fd = os.open(
        state_tmp,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        journal["state_mode"],
    )
    with os.fdopen(state_fd, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(state_tmp, state_path)
except BaseException:
    try:
        if os.path.lexists(state_tmp):
            os.unlink(state_tmp)
    except OSError:
        pass
    raise
PY
    [ -z "$CORE_STATE_CANDIDATE" ] || rm -f "$CORE_STATE_CANDIDATE"
    echo "  ✓ committed seed state (seeded=$SEEDED, faithful=$FAITHFUL)"
fi

# ── Refresh manifest in target (preserve original deploy_date + fingerprint) ──
if [ "$DRY_RUN" = "0" ]; then
    manifest_tmp="$TMP/manifest.next"
    if [ -f "$MANIFEST" ]; then
        # Update template_version + last_updated; sync deployment selectors
        # (variant, mode, extensions, flags) from the fresh deploy so that an override on
        # this run is reflected in the persisted manifest. Anything not
        # listed here passes through verbatim from the existing manifest
        # (e.g. deploy_fingerprint, deploy_date — original deploy metadata).
        # Bind NEW_MANIFEST once via `input as $new`; each bare `input` call
        # consumes one file from the argv list, so reusing `(input | .X)` four
        # times would try to read four files. The slurp pattern below reads
        # NEW_MANIFEST once and lets us pull multiple fields from it.
        jq --arg v "$NEW_VERSION" --arg d "$(date -u +%Y-%m-%d)" \
           'input as $new
            | .template_version = $v
            | .last_updated = $d
            | .variant = $new.variant
            | .mode = $new.mode
            | .extensions = $new.extensions
            | .flags = $new.flags
            | .source = $new.source
            | .infrastructure = $new.infrastructure' \
           "$MANIFEST" "$NEW_MANIFEST" > "$manifest_tmp" && mv "$manifest_tmp" "$MANIFEST" || {
               rm -f "$manifest_tmp"; exit 1;
           }
    else
        # No prior manifest — adopt the fresh manifest but blank deploy_fingerprint
        # (we don't know the original UUID; user can copy it from paper/arpipeline.sty if needed).
        jq --arg d "$(date -u +%Y-%m-%d)" \
           '.deploy_fingerprint = "(unknown — pre-manifest deploy)" | .last_updated = $d' \
           "$NEW_MANIFEST" > "$manifest_tmp" && mv "$manifest_tmp" "$MANIFEST" || {
               rm -f "$manifest_tmp"; exit 1;
           }
    fi
    if [ "$SEED_MIGRATION_PENDING" = "1" ]; then
        SEED_MIGRATION_PENDING=0
        rm -f "$SEED_MIGRATION_JOURNAL"
    fi
    echo
    echo "  ✓ manifest updated: template_version $OLD_VERSION → $NEW_VERSION"
fi

# Same-selector core schema/status migration is the final stateful update step:
# the refreshed manifest is already durable, and the candidate is published by
# one atomic replace. A kill before the replace leaves the original state (and
# any retired halt) intact; a kill after it leaves both manifest and state new.
if [ "$DRY_RUN" = "0" ] && [ "$SEED_MIGRATION_PENDING" = "0" ] \
    && [ -n "$CORE_STATE_CANDIDATE" ] && [ -f "$CORE_STATE_CANDIDATE" ]; then
    python3 -I - "$STATE_FILE" "$CORE_STATE_CANDIDATE" <<'PY'
import json
import os
import secrets
import stat
import sys

state_path, candidate_path = sys.argv[1:]
fd = os.open(state_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    os.close(fd)
    raise SystemExit("ERROR: core migration state changed before commit")
with os.fdopen(fd, "r", encoding="utf-8") as handle:
    json.load(handle)
with open(candidate_path, encoding="utf-8") as handle:
    candidate = json.load(handle)
state_tmp = os.path.join(
    os.path.dirname(state_path), f".pipeline-state.update.{secrets.token_hex(8)}"
)
try:
    state_fd = os.open(
        state_tmp,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        stat.S_IMODE(info.st_mode),
    )
    with os.fdopen(state_fd, "w", encoding="utf-8") as handle:
        json.dump(candidate, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(state_tmp, state_path)
except BaseException:
    try:
        if os.path.lexists(state_tmp):
            os.unlink(state_tmp)
    except OSError:
        pass
    raise
PY
    echo "  ✓ committed pipeline-state schema/status migration"
fi

# ── Report agent diff ──
echo
echo "=== Agent diff ($OLD_VERSION → $NEW_VERSION) ==="
ADDED=$(comm -13 "$OLD_AGENTS_TMP" "$NEW_AGENTS_TMP")
REMOVED=$(comm -23 "$OLD_AGENTS_TMP" "$NEW_AGENTS_TMP")
if [ -n "$ADDED" ]; then
    echo "Added:"
    echo "$ADDED" | sed 's/^/  + /'
fi
if [ -n "$REMOVED" ]; then
    echo "Removed:"
    echo "$REMOVED" | sed 's/^/  - /'
fi
[ -z "$ADDED" ] && [ -z "$REMOVED" ] && echo "  (no agent additions or removals)"

echo
if [ "$DRY_RUN" = "1" ]; then
    echo "Dry run complete. No files modified."
else
    echo "Update complete. Review with: cd $PROJECT && git status"
    echo "Then commit the infrastructure refresh when ready."
fi

}

# Keep LOCK_EX exclusively in this trusted parent. Setup, providers, venv tools,
# and every other refresh child run with fd 9 closed while the parent waits.
( _update_main ) 9<&-
