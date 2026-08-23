#!/bin/bash
# update.sh — Refresh pipeline infrastructure in a deployed project.
#
# Usage: every invocation explicitly authorizes the complete target selector:
#   ./update.sh <project> --source-digest sha256:<trusted-setup-digest> \
#     --variant finance --no-mode --clear-ext \
#     --no-seeded --no-faithful --no-manual --no-light \
#     --no-halt-on-core-bypass [--dry-run] [--no-model-probe]
#
# Selectors (--variant, --mode/--no-mode, --ext/--clear-ext, --seeded/--no-seeded,
# --faithful/--no-faithful, --manual/--no-manual,
# --light/--no-light, --halt-on-core-bypass/--no-halt-on-core-bypass) are
# mandatory and must exactly describe the deployment's current shape. No
# selector change is supported in place; create a fresh deployment instead.
# Each --ext repeats and the ordered list must match the current manifest.
# --source-digest is mandatory operator attestation from the trusted setup
# record; never derive it from the project-writable manifest.
# --no-model-probe is a one-run assembly control forwarded to setup.sh; it is
# not a deployment selector and is not persisted in the manifest.
#
# What it does:
#   1. Reads a v2.28-generation .deploy_manifest.json from the target project.
#      Older and pre-manifest deployments are intentionally unsupported.
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
OVERRIDE_HALT_ON_CORE_BYPASS=""
NO_MODEL_PROBE=0
ATTESTED_SOURCE_DIGEST=""
NEXT_IS_VARIANT=0
NEXT_IS_MODE=0
NEXT_IS_EXT=0
NEXT_IS_SOURCE_DIGEST=0
COUNT_SOURCE_DIGEST=0
COUNT_VARIANT=0
COUNT_MODE=0
COUNT_CLEAR_EXT=0
COUNT_SEEDED=0
COUNT_FAITHFUL=0
COUNT_MANUAL=0
COUNT_LIGHT=0
COUNT_HALT=0

for arg in "$@"; do
    case "$arg" in
        --dry-run)        DRY_RUN=1 ;;
        --source-digest)  NEXT_IS_SOURCE_DIGEST=1; COUNT_SOURCE_DIGEST=$((COUNT_SOURCE_DIGEST + 1)) ;;
        --source-digest=*) ATTESTED_SOURCE_DIGEST="${arg#--source-digest=}"; COUNT_SOURCE_DIGEST=$((COUNT_SOURCE_DIGEST + 1)) ;;
        --variant)        NEXT_IS_VARIANT=1; COUNT_VARIANT=$((COUNT_VARIANT + 1)) ;;
        --variant=*)      OVERRIDE_VARIANT="${arg#--variant=}"; COUNT_VARIANT=$((COUNT_VARIANT + 1)) ;;
        --mode)           NEXT_IS_MODE=1; COUNT_MODE=$((COUNT_MODE + 1)) ;;
        --mode=*)
            OVERRIDE_MODE="${arg#--mode=}"
            [ -n "$OVERRIDE_MODE" ] || {
                echo "ERROR: empty --mode is unsupported; use explicit --no-mode" >&2
                exit 1
            }
            OVERRIDE_MODE_SET=1; COUNT_MODE=$((COUNT_MODE + 1))
            ;;
        --no-mode)        OVERRIDE_MODE="";                OVERRIDE_MODE_SET=1; COUNT_MODE=$((COUNT_MODE + 1)) ;;
        --ext)            NEXT_IS_EXT=1 ;;
        --ext=*)          OVERRIDE_EXTS+=("${arg#--ext=}"); OVERRIDE_EXTS_SET=1 ;;
        --clear-ext)
            if [ "${#OVERRIDE_EXTS[@]}" -gt 0 ]; then
                echo "ERROR: --clear-ext must precede every --ext selector" >&2
                exit 1
            fi
            OVERRIDE_EXTS=(); OVERRIDE_EXTS_SET=1; COUNT_CLEAR_EXT=$((COUNT_CLEAR_EXT + 1))
            ;;
        --seeded)         OVERRIDE_SEEDED=true; COUNT_SEEDED=$((COUNT_SEEDED + 1)) ;;
        --no-seeded)      OVERRIDE_SEEDED=false; COUNT_SEEDED=$((COUNT_SEEDED + 1)) ;;
        --faithful)       OVERRIDE_FAITHFUL=true; COUNT_FAITHFUL=$((COUNT_FAITHFUL + 1)) ;;
        --no-faithful)    OVERRIDE_FAITHFUL=false; COUNT_FAITHFUL=$((COUNT_FAITHFUL + 1)) ;;
        --manual)         OVERRIDE_MANUAL=true; COUNT_MANUAL=$((COUNT_MANUAL + 1)) ;;
        --no-manual)      OVERRIDE_MANUAL=false; COUNT_MANUAL=$((COUNT_MANUAL + 1)) ;;
        --light)          OVERRIDE_LIGHT=true; COUNT_LIGHT=$((COUNT_LIGHT + 1)) ;;
        --no-light)       OVERRIDE_LIGHT=false; COUNT_LIGHT=$((COUNT_LIGHT + 1)) ;;
        --halt-on-core-bypass)    OVERRIDE_HALT_ON_CORE_BYPASS=true; COUNT_HALT=$((COUNT_HALT + 1)) ;;
        --no-halt-on-core-bypass) OVERRIDE_HALT_ON_CORE_BYPASS=false; COUNT_HALT=$((COUNT_HALT + 1)) ;;
        --no-model-probe) NO_MODEL_PROBE=1 ;;
        -*)               echo "Unknown option: $arg"; exit 1 ;;
        *)
            if [ "$NEXT_IS_VARIANT" = "1" ]; then
                OVERRIDE_VARIANT="$arg"; NEXT_IS_VARIANT=0
            elif [ "$NEXT_IS_SOURCE_DIGEST" = "1" ]; then
                ATTESTED_SOURCE_DIGEST="$arg"; NEXT_IS_SOURCE_DIGEST=0
            elif [ "$NEXT_IS_MODE" = "1" ]; then
                [ -n "$arg" ] || {
                    echo "ERROR: empty --mode is unsupported; use explicit --no-mode" >&2
                    exit 1
                }
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
    echo "Error: --mode requires a value (empirical-first, measurement-first, report), or use --no-mode"; exit 1
fi
if [ "$NEXT_IS_EXT" = "1" ]; then
    echo "Error: --ext requires a value (empirical, theory_llm)"; exit 1
fi
if [ "$NEXT_IS_SOURCE_DIGEST" = "1" ]; then
    echo "Error: --source-digest requires a sha256:<64 lowercase hex> value"; exit 1
fi

if [ "$COUNT_SOURCE_DIGEST" != "1" ] || [ "$COUNT_VARIANT" != "1" ] \
   || [ "$COUNT_MODE" != "1" ] || [ "$COUNT_SEEDED" != "1" ] \
   || [ "$COUNT_FAITHFUL" != "1" ] || [ "$COUNT_MANUAL" != "1" ] \
   || [ "$COUNT_LIGHT" != "1" ] || [ "$COUNT_HALT" != "1" ] \
   || [ "$COUNT_CLEAR_EXT" -gt 1 ]; then
    echo "ERROR: update requires each deployment selector exactly once" >&2
    exit 1
fi
if [ "${#OVERRIDE_EXTS[@]}" -eq 0 ] && [ "$COUNT_CLEAR_EXT" != "1" ]; then
    echo "ERROR: an empty extension selector requires exactly one --clear-ext" >&2
    exit 1
fi
declare -A _seen_update_extensions=()
for _extension in "${OVERRIDE_EXTS[@]}"; do
    if [[ ! "$_extension" =~ ^(empirical|theory_llm)$ ]] \
       || [ -n "${_seen_update_extensions[$_extension]:-}" ]; then
        echo "ERROR: extension selector contains empty, unknown, or duplicate values" >&2
        exit 1
    fi
    _seen_update_extensions[$_extension]=1
done

if [ -z "$PROJECT" ]; then
    echo "usage: update.sh <project> --source-digest sha256:... --variant X (--mode M|--no-mode) (--ext Y...|--clear-ext) (--seeded|--no-seeded) (--faithful|--no-faithful) (--manual|--no-manual) (--light|--no-light) (--halt-on-core-bypass|--no-halt-on-core-bypass) [--dry-run] [--no-model-probe]"
    exit 1
fi
if [ -z "$OVERRIDE_VARIANT" ] || [ "$OVERRIDE_MODE_SET" != "1" ] \
   || [ "$OVERRIDE_EXTS_SET" != "1" ] || [ -z "$OVERRIDE_SEEDED" ] \
   || [ -z "$OVERRIDE_FAITHFUL" ] || [ -z "$OVERRIDE_MANUAL" ] \
   || [ -z "$OVERRIDE_LIGHT" ] || [ -z "$OVERRIDE_HALT_ON_CORE_BYPASS" ]; then
    echo "ERROR: update requires the complete deployment selector explicitly; see the usage line above" >&2
    exit 1
fi
if [[ ! "$ATTESTED_SOURCE_DIGEST" =~ ^sha256:[0-9a-f]{64}$ ]]; then
    echo "ERROR: update requires --source-digest from the trusted setup record; do not derive it from project files" >&2
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

# The authenticated Python launcher acquires launch.sh's project-directory lock
# before snapshotting any build input and passes that same open file description
# here. Retain it as fd 9 for the whole refresh; direct coordinator invocation is
# deliberately unsupported.
_inherited_project_lock_fd="${ZEROPAPER_UPDATE_PROJECT_LOCK_FD:-}"
unset ZEROPAPER_UPDATE_PROJECT_LOCK_FD
if [[ ! "$_inherited_project_lock_fd" =~ ^[0-9]+$ ]]; then
    echo "ERROR: missing authenticated project runtime/update lock" >&2
    exit 1
fi
if [ "$_inherited_project_lock_fd" != "9" ]; then
    if ! eval "exec 9<&$_inherited_project_lock_fd"; then
        echo "ERROR: missing authenticated project runtime/update lock" >&2
        exit 1
    fi
    eval "exec ${_inherited_project_lock_fd}<&-"
fi
UPDATE_DOTENV_FD=""
_inherited_dotenv_fd="${ZEROPAPER_UPDATE_DOTENV_FD:-}"
unset ZEROPAPER_UPDATE_DOTENV_FD
if [ -n "$_inherited_dotenv_fd" ]; then
    if [[ ! "$_inherited_dotenv_fd" =~ ^[0-9]+$ ]] \
       || [ "$_inherited_dotenv_fd" = "9" ]; then
        echo "ERROR: invalid authenticated operator environment descriptor" >&2
        exit 1
    fi
    if [ "$_inherited_dotenv_fd" != "10" ]; then
        if ! eval "exec 10<&$_inherited_dotenv_fd"; then
            echo "ERROR: missing authenticated operator environment descriptor" >&2
            exit 1
        fi
        eval "exec ${_inherited_dotenv_fd}<&-"
    fi
    if ! /usr/bin/python3 -I - 10 <<'PY'
import os, stat, sys
fd = int(sys.argv[1])
info = os.fstat(fd)
if not stat.S_ISFIFO(info.st_mode):
    raise SystemExit("invalid authenticated operator environment descriptor")
PY
    then
        echo "ERROR: invalid authenticated operator environment descriptor" >&2
        exit 1
    fi
    UPDATE_DOTENV_FD=10
fi
_inherited_launcher_liveness_fd="${ZEROPAPER_UPDATE_LAUNCHER_LIVENESS_FD:-}"
unset ZEROPAPER_UPDATE_LAUNCHER_LIVENESS_FD
if [[ ! "$_inherited_launcher_liveness_fd" =~ ^[0-9]+$ ]] \
   || [ "$_inherited_launcher_liveness_fd" = "9" ] \
   || { [ -n "$UPDATE_DOTENV_FD" ] \
        && [ "$_inherited_launcher_liveness_fd" = "$UPDATE_DOTENV_FD" ]; }; then
    echo "ERROR: missing authenticated updater-launcher liveness descriptor" >&2
    exit 1
fi
if ! eval "exec {UPDATE_LAUNCHER_LIVENESS_FD}<&$_inherited_launcher_liveness_fd"; then
    echo "ERROR: missing authenticated updater-launcher liveness descriptor" >&2
    exit 1
fi
eval "exec ${_inherited_launcher_liveness_fd}<&-"
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
# checkout because setup.sh, update.sh, scripts/update_coordinator.sh, VERSION,
# LICENSE, and .env.example are root inputs.
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
unset VIRTUAL_ENV CONDA_PREFIX CONDA_DEFAULT_ENV \
    CONDA_PROMPT_MODIFIER PIPENV_ACTIVE POETRY_ACTIVE \
    PYTHONHOME PYTHONPATH PYTHONSTARTUP PYTHONINSPECT
hash -r
[ -f /usr/bin/python3 ] && [ -x /usr/bin/python3 ] || {
    echo "update.sh requires the OS Python at /usr/bin/python3"; exit 1;
}
UPDATE_CONTROL_PYTHON=/usr/bin/python3
python3() { "$UPDATE_CONTROL_PYTHON" -I "$@"; }

UPDATE_CONTROL_JQ="${ZEROPAPER_UPDATE_JQ:?missing isolated update jq path}"
unset ZEROPAPER_UPDATE_JQ
"$UPDATE_CONTROL_PYTHON" -I - "$UPDATE_CONTROL_JQ" "$PROJECT" "$TEMPLATE_ROOT" <<'PY'
import os, stat, sys
path, project, template = sys.argv[1:]
if not os.path.isabs(path) or os.path.realpath(path) != path:
    raise SystemExit("update.sh received an untrusted jq path")
info = os.stat(path)
if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
        or not os.access(path, os.X_OK)):
    raise SystemExit("update.sh requires one regular executable jq")
for forbidden in (project, template, "/tmp", "/var/tmp", "/private/tmp"):
    forbidden = os.path.realpath(forbidden)
    if os.path.commonpath((path, forbidden)) == forbidden:
        raise SystemExit("update.sh jq path crosses a mutable project/source/temp boundary")
allowed_roots = ("/usr", "/bin", "/opt/homebrew", "/usr/local", "/opt/local", "/nix/store")
if not any(os.path.commonpath((path, root)) == root for root in allowed_roots):
    raise SystemExit("update.sh jq path is outside fixed host installation roots")
PY
jq() { "$UPDATE_CONTROL_JQ" "$@"; }

if [ ! -e "$MANIFEST" ] && [ ! -L "$MANIFEST" ]; then
    echo "ERROR: update supports only same-version manifest-backed deployments; create a fresh deployment" >&2
    exit 1
fi
UPDATE_VERSION="$(tr -d '[:space:]' < "$TEMPLATE_ROOT/VERSION")"
python3 -I - "$MANIFEST" "$UPDATE_VERSION" "$ATTESTED_SOURCE_DIGEST" <<'PY'
import json, os, stat, sys
path, expected_version, attested_source_digest = sys.argv[1:]

def reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result

info = os.lstat(path)
if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit("ERROR: deployment manifest must be one regular non-aliased file")
try:
    with open(path, encoding="utf-8") as handle:
        manifest = json.load(
            handle, parse_constant=reject_constant, object_pairs_hook=unique_object
        )
except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
    raise SystemExit(f"ERROR: deployment manifest is not strict UTF-8 JSON: {exc}")
required_keys = {
    "manifest_version", "template_version", "deploy_date", "deploy_fingerprint",
    "source", "variant", "mode", "extensions", "flags", "infrastructure",
}
if not isinstance(manifest, dict) or not required_keys <= set(manifest) \
        or set(manifest) - required_keys - {"last_updated"}:
    raise SystemExit("ERROR: deployment manifest is not the exact current-generation shape")
if manifest.get("manifest_version") != 1:
    raise SystemExit("ERROR: unsupported deployment manifest generation; create a fresh deployment")
for key in ("template_version", "deploy_date", "deploy_fingerprint"):
    if not isinstance(manifest.get(key), str) or not manifest[key]:
        raise SystemExit(f"ERROR: deployment manifest {key} is malformed")
if "last_updated" in manifest and (
        not isinstance(manifest["last_updated"], str) or not manifest["last_updated"]):
    raise SystemExit("ERROR: deployment manifest last_updated is malformed")
version = manifest.get("template_version") if isinstance(manifest, dict) else None
semver = version.split("+", 1)[0] if isinstance(version, str) else None
if semver != expected_version:
    raise SystemExit(
        f"ERROR: update requires a {expected_version} deployment; "
        "create a fresh deployment for every other version"
    )
source = manifest.get("source")
source_keys = {"kind", "repository", "commit", "dirty", "content_digest", "update_channel"}
if not isinstance(source, dict) or set(source) != source_keys:
    raise SystemExit("ERROR: deployment manifest source is malformed")
for key in ("kind", "commit", "content_digest", "update_channel"):
    if not isinstance(source[key], str) or not source[key]:
        raise SystemExit(f"ERROR: deployment manifest source.{key} is malformed")
if source["repository"] is not None and not isinstance(source["repository"], str):
    raise SystemExit("ERROR: deployment manifest source.repository is malformed")
if not isinstance(source["dirty"], bool):
    raise SystemExit("ERROR: deployment manifest source.dirty is malformed")
recorded_digest = source.get("content_digest") if isinstance(source, dict) else None
if recorded_digest != attested_source_digest:
    raise SystemExit(
        "ERROR: project manifest source digest does not match the operator-attested "
        "trusted setup record"
    )
variant = manifest.get("variant")
if not isinstance(variant, str) or variant not in {"finance", "macro", "llm_cognition"}:
    raise SystemExit("ERROR: deployment manifest has an invalid variant")
if manifest.get("mode") not in {"", "empirical-first", "measurement-first", "report"}:
    raise SystemExit("ERROR: deployment manifest mode must be a string")
extensions = manifest.get("extensions")
if (not isinstance(extensions, list)
        or any(not isinstance(value, str)
               or value not in {"empirical", "theory_llm"}
               for value in extensions)
        or len(extensions) != len(set(extensions))):
    raise SystemExit("ERROR: deployment manifest extensions are malformed")
flags = manifest.get("flags")
expected_flags = {"seeded", "faithful", "manual", "light", "halt_on_core_bypass"}
if (not isinstance(flags, dict) or set(flags) != expected_flags
        or any(not isinstance(flags[key], bool) for key in expected_flags)):
    raise SystemExit("ERROR: deployment manifest flags are malformed")
infrastructure = manifest.get("infrastructure")
infrastructure_keys = {"dirs_replace", "files_replace", "files_env_merge"}
if not isinstance(infrastructure, dict) or set(infrastructure) != infrastructure_keys:
    raise SystemExit("ERROR: deployment manifest infrastructure is malformed")
for key in infrastructure_keys:
    values = infrastructure[key]
    if (not isinstance(values, list)
            or any(not isinstance(value, str) or not value for value in values)
            or len(values) != len(set(values))):
        raise SystemExit(f"ERROR: deployment manifest infrastructure.{key} is malformed")
PY

_recorded_variant="$(jq -r '.variant' "$MANIFEST")"
_recorded_mode="$(jq -r '.mode' "$MANIFEST")"
mapfile -t _recorded_exts < <(jq -r '.extensions[]' "$MANIFEST")
_extensions_match=1
if [ "${#OVERRIDE_EXTS[@]}" -ne "${#_recorded_exts[@]}" ]; then
    _extensions_match=0
else
    for _extension_index in "${!OVERRIDE_EXTS[@]}"; do
        if [ "${OVERRIDE_EXTS[$_extension_index]}" != "${_recorded_exts[$_extension_index]}" ]; then
            _extensions_match=0
            break
        fi
    done
fi
_recorded_seeded="$(jq -r '.flags.seeded' "$MANIFEST")"
_recorded_faithful="$(jq -r '.flags.faithful' "$MANIFEST")"
_recorded_manual="$(jq -r '.flags.manual' "$MANIFEST")"
_recorded_light="$(jq -r '.flags.light' "$MANIFEST")"
_recorded_halt="$(jq -r '.flags.halt_on_core_bypass' "$MANIFEST")"
if [ "$OVERRIDE_VARIANT" != "$_recorded_variant" ] \
   || [ "$OVERRIDE_MODE" != "$_recorded_mode" ] \
   || [ "$_extensions_match" != "1" ] \
   || [ "$OVERRIDE_SEEDED" != "$_recorded_seeded" ] \
   || [ "$OVERRIDE_FAITHFUL" != "$_recorded_faithful" ] \
   || [ "$OVERRIDE_MANUAL" != "$_recorded_manual" ] \
   || [ "$OVERRIDE_LIGHT" != "$_recorded_light" ] \
   || [ "$OVERRIDE_HALT_ON_CORE_BYPASS" != "$_recorded_halt" ]; then
    echo "ERROR: update selectors must exactly describe the current deployment" >&2
    echo "  In-place selector changes are unsupported; create a fresh deployment." >&2
    exit 1
fi

# Reject extension additions before creating any target-side update control
# path when an agent-writable virtualenv already exists. The updater cannot
# safely execute that environment's interpreter with host authority.
VENV="$PROJECT/.venv"
if [ -L "$VENV" ] || { [ -e "$VENV" ] && [ ! -d "$VENV" ]; }; then
    echo "ERROR: .venv must be a real directory when present" >&2
    exit 1
fi
if [ -d "$VENV" ]; then
    _manifest_extensions="$(jq -r '.extensions[]?' "$MANIFEST")"
    for _requested_extension in "${OVERRIDE_EXTS[@]}"; do
        if ! grep -Fxq -- "$_requested_extension" <<< "$_manifest_extensions"; then
            echo "ERROR: adding extensions to an existing .venv requires a fresh deployment" >&2
            exit 1
        fi
    done
fi

# Paper is mutable project content. Validate its parent before any later
# same-layout selector operation inspects it.
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
UPDATE_CREATED_CONTROL_DIR=0
if [ -L "$UPDATE_PROCESS_LOG" ] || { [ -e "$UPDATE_PROCESS_LOG" ] && [ ! -d "$UPDATE_PROCESS_LOG" ]; }; then
    echo "ERROR: $UPDATE_PROCESS_LOG must be a real project directory" >&2
    exit 1
fi
[ -d "$UPDATE_PROCESS_LOG" ] || {
    echo "ERROR: same-version update requires an existing process_log directory" >&2
    exit 1
}
if [ "$(cd "$UPDATE_PROCESS_LOG" && pwd -P)" != "$UPDATE_PROCESS_LOG" ]; then
    echo "ERROR: $UPDATE_PROCESS_LOG resolves outside the deployment" >&2
    exit 1
fi
TMP=""
SEED_MIGRATION_JOURNAL="$UPDATE_CONTROL_DIR/selector-migration.json"
SEED_MIGRATION_NEXT="$SEED_MIGRATION_JOURNAL.next"
UPDATE_TRANSACTION_MARKER="$UPDATE_CONTROL_DIR/update-in-progress"
_remove_private_update_tree() {
    local _private_root="$1"
    "$UPDATE_CONTROL_PYTHON" -I - "$_private_root" <<'PY'
import os
import stat
import sys

root = sys.argv[1]
if not os.path.lexists(root):
    raise SystemExit(0)
root_info = os.lstat(root)
if not stat.S_ISDIR(root_info.st_mode) or stat.S_ISLNK(root_info.st_mode):
    raise SystemExit(f"ERROR: unsafe updater workspace root: {root}")
directories = []
pending = [root]
while pending:
    current = pending.pop()
    info = os.lstat(current)
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise SystemExit(f"ERROR: unsafe updater workspace directory: {current}")
    os.chmod(current, 0o700)
    directories.append(current)
    with os.scandir(current) as entries:
        for entry in entries:
            child_info = entry.stat(follow_symlinks=False)
            if stat.S_ISDIR(child_info.st_mode) and not stat.S_ISLNK(child_info.st_mode):
                pending.append(entry.path)
            else:
                os.unlink(entry.path)
for directory in reversed(directories):
    os.rmdir(directory)
if os.path.lexists(root):
    raise SystemExit(f"ERROR: updater workspace cleanup incomplete: {root}")
PY
}
_update_cleanup() {
    [ -z "$TMP" ] || _remove_private_update_tree "$TMP"
    if [ "$UPDATE_CREATED_CONTROL_DIR" = "1" ] \
       && rmdir "$UPDATE_CONTROL_DIR" 2>/dev/null; then
        "$UPDATE_CONTROL_PYTHON" -I - "$UPDATE_PROCESS_LOG" <<'PY' || true
import os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
try:
    os.fsync(fd)
finally:
    os.close(fd)
PY
    fi
}
trap _update_cleanup EXIT
if [ -L "$UPDATE_CONTROL_DIR" ] || { [ -e "$UPDATE_CONTROL_DIR" ] && [ ! -d "$UPDATE_CONTROL_DIR" ]; }; then
    echo "ERROR: $UPDATE_CONTROL_DIR must be a real control directory" >&2
    exit 1
fi
if [ -e "$UPDATE_CONTROL_DIR" ]; then
    if [ "$(cd "$UPDATE_CONTROL_DIR" && pwd -P)" != "$UPDATE_CONTROL_DIR" ]; then
        echo "ERROR: $UPDATE_CONTROL_DIR resolves outside the deployment" >&2
        exit 1
    fi
elif [ "$DRY_RUN" = "0" ]; then
    UPDATE_CREATED_CONTROL_DIR=1
    (umask 077 && mkdir "$UPDATE_CONTROL_DIR")
fi
# Infrastructure replacement cannot be published as one atomic filesystem
# operation. Validate any crash-left marker now, but publish a new marker only
# after every read-only preflight succeeds and immediately before the first
# managed mutation. Remove it only after state and manifest publication succeeds.
UPDATE_MARKER_PRESENT=0
if [ -e "$UPDATE_TRANSACTION_MARKER" ] || [ -L "$UPDATE_TRANSACTION_MARKER" ]; then
    "$UPDATE_CONTROL_PYTHON" -I - "$UPDATE_TRANSACTION_MARKER" <<'PY'
import os, stat, sys
path = sys.argv[1]
try:
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
except OSError as exc:
    raise SystemExit(f"ERROR: cannot safely read update transaction marker: {exc}")
info = os.fstat(fd)
os.close(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit("ERROR: update transaction marker must be one regular file")
PY
    if [ "$DRY_RUN" = "1" ]; then
        echo "ERROR: dry-run cannot inspect an interrupted update; rerun update without --dry-run" >&2
        exit 1
    fi
    UPDATE_MARKER_PRESENT=1
    echo "  ✓ resuming interrupted update"
fi
# Selector migration was removed: current-generation updates refresh one exact
# deployment shape only. Any old journal is unsupported mutable state, not an
# instruction the host-authority updater may execute.
if [ -e "$SEED_MIGRATION_JOURNAL" ] || [ -L "$SEED_MIGRATION_JOURNAL" ] \
   || [ -e "$SEED_MIGRATION_NEXT" ] || [ -L "$SEED_MIGRATION_NEXT" ]; then
    echo "ERROR: obsolete selector-migration state is unsupported; create a fresh deployment" >&2
    exit 1
fi

# A SIGKILLed refresh body cannot run its EXIT trap. On the next mutating
# invocation, remove only updater-created `update.XXXXXX` workspaces from the
# policy-denied control directory before assembling a replacement. This also
# removes any copied `.env`; dry-run remains byte-for-byte read-only.
if [ "$DRY_RUN" = "0" ]; then
    "$UPDATE_CONTROL_PYTHON" -I - "$UPDATE_CONTROL_DIR" <<'PY'
import os
import re
import stat
import sys

control = sys.argv[1]
for name in os.listdir(control):
    if re.fullmatch(r"update\.[A-Za-z0-9]{6}", name) is None:
        continue
    root = os.path.join(control, name)
    info = os.lstat(root)
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise SystemExit(f"ERROR: abandoned updater workspace has unsafe type: {root}")
    os.chmod(root, 0o700)
    directories = []
    for current, child_dirs, files in os.walk(root, topdown=True, followlinks=False):
        os.chmod(current, 0o700)
        for child in list(child_dirs):
            path = os.path.join(current, child)
            child_info = os.lstat(path)
            if stat.S_ISLNK(child_info.st_mode):
                os.unlink(path)
                child_dirs.remove(child)
            elif stat.S_ISDIR(child_info.st_mode):
                os.chmod(path, 0o700)
            else:
                raise SystemExit(
                    f"ERROR: abandoned updater workspace descendant has unsafe type: {path}"
                )
        for filename in files:
            path = os.path.join(current, filename)
            file_info = os.lstat(path)
            if stat.S_ISDIR(file_info.st_mode) and not stat.S_ISLNK(file_info.st_mode):
                raise SystemExit(
                    f"ERROR: abandoned updater workspace changed during cleanup: {path}"
                )
            os.unlink(path)
        directories.append(current)
    for directory in reversed(directories):
        os.rmdir(directory)
PY
fi

# Defense in depth for an OpenCode server not attached to the ordinary launcher
# lock. Current launchers hold LOCK_SH for their lifetime; update holds LOCK_EX.
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
VARIANT=$(jq -r .variant "$MANIFEST")
MODE=$(jq -r '.mode // ""' "$MANIFEST")
EXTENSIONS=()
while IFS= read -r _ext; do EXTENSIONS+=("$_ext"); done < <(jq -r '.extensions[]?' "$MANIFEST")
SEEDED=$(jq -r .flags.seeded "$MANIFEST")
FAITHFUL=$(jq -r '.flags.faithful // false' "$MANIFEST")
MANUAL=$(jq -r .flags.manual "$MANIFEST")
LIGHT=$(jq -r .flags.light "$MANIFEST")
HALT_ON_CORE_BYPASS=$(jq -r '.flags.halt_on_core_bypass // false' "$MANIFEST")
OLD_VERSION=$(jq -r .template_version "$MANIFEST")
mode_str="${MODE:-(none)}"
echo "Found manifest: variant=$VARIANT, mode=$mode_str, extensions=[${EXTENSIONS[*]}], template=$OLD_VERSION"

ORIGINAL_EXT_STR="${EXTENSIONS[*]}"

# The mandatory CLI selector was matched against the manifest before any
# target-side control path was created. From here the deployment shape is
# immutable: update only refreshes managed bytes for this exact selector.
# Require the complete v2.28 state contract before any project mutation.
EVIDENCE_STATE="$PROJECT/process_log/pipeline_state.json"
STRICT_CONTROL_JSON=()
for _strict_control in \
    "$EVIDENCE_STATE" \
    "$PROJECT/process_log/manual_evidence_state.json" \
    "$PROJECT/process_log/results_registry.json" \
    "$PROJECT/process_log/paper_evidence.receipt.json"
do
    if [ -e "$_strict_control" ] || [ -L "$_strict_control" ]; then
        STRICT_CONTROL_JSON+=("$_strict_control")
    fi
done
if [ "${#STRICT_CONTROL_JSON[@]}" -gt 0 ]; then
    "$UPDATE_CONTROL_PYTHON" -I - "${STRICT_CONTROL_JSON[@]}" <<'PY'
import json
import os
import stat
import sys

no_follow = getattr(os, "O_NOFOLLOW", 0)

def reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result

for path in sys.argv[1:]:
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | no_follow)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            os.close(descriptor)
            raise ValueError("must be one regular non-aliased file")
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            json.load(
                handle,
                parse_constant=reject_constant,
                object_pairs_hook=unique_object,
            )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"ERROR: {path} is not strict UTF-8 JSON: {exc}")
PY
fi
if [ -e "$EVIDENCE_STATE" ] || [ -L "$EVIDENCE_STATE" ]; then
    "$UPDATE_CONTROL_PYTHON" -I - "$EVIDENCE_STATE" "$ORIGINAL_EXT_STR" <<'PY'
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import PurePosixPath

path, original_extensions_text = sys.argv[1:]
original_extensions = set(original_extensions_text.split())
try:
    fd = os.open(
        path,
        os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0),
    )
except OSError as exc:
    raise SystemExit(f"ERROR: cannot safely read pipeline state: {exc}")
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    os.close(fd)
    raise SystemExit("ERROR: pipeline state must be one regular non-aliased file")
try:
    with os.fdopen(fd, "r", encoding="utf-8") as handle:
        state = json.load(handle)
except (OSError, UnicodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"ERROR: pipeline state is not valid UTF-8 JSON: {exc}")
if not isinstance(state, dict):
    raise SystemExit("ERROR: pipeline state must be a JSON object")
loops = state.get("loops")
evidence = loops.get("evidence") if isinstance(loops, dict) else None
if (not isinstance(loops, dict)
        or not isinstance(evidence, dict)
        or set(evidence) != {"round", "cap"}
        or not all(isinstance(evidence[key], int) and not isinstance(evidence[key], bool)
                   for key in ("round", "cap"))
        or evidence["round"] < 0 or evidence["cap"] < 1):
    raise SystemExit(
        "ERROR: pipeline state does not match the supported v2.28 evidence contract; "
        "create a fresh deployment"
    )
problem_attempt = state.get("problem_attempt", 1)
if (not isinstance(problem_attempt, int) or isinstance(problem_attempt, bool)
        or problem_attempt < 1):
    raise SystemExit("ERROR: pipeline state problem_attempt must be a positive integer")
if not isinstance(state.get("history"), list):
    raise SystemExit("ERROR: pipeline state history must be an array")
legacy_keys = {
    "stage2b_legacy_recovery_inputs", "stage3a_legacy_recovery_inputs",
    "stage3a_feasibility_legacy_recovery_inputs", "stage3b_legacy_recovery_inputs",
}
present = sorted(legacy_keys & state.keys())
if present:
    raise SystemExit(
        "ERROR: legacy computed-evidence recovery fields are unsupported; "
        "create a fresh deployment: " + ", ".join(present)
    )
required_triplets = [
    ("stage2b_theory_version", "stage2b_exploration_path", "stage2b_result_receipt"),
]
if "empirical" in original_extensions:
    required_triplets.append(
        ("stage3a_theory_version", "stage3a_analysis_path", "stage3a_result_receipt")
    )
if "theory_llm" in original_extensions:
    required_triplets.append(
        ("stage3b_theory_version", "stage3b_results_path", "stage3b_result_receipt")
    )
for version_key, report_key, receipt_key in required_triplets:
    missing = [key for key in (version_key, report_key, receipt_key) if key not in state]
    if missing:
        raise SystemExit(
            "ERROR: pipeline state is missing required receipt-backed evidence fields; "
            "create a fresh deployment: "
            + ", ".join(missing)
        )
    version = state.get(version_key)
    report = state.get(report_key)
    receipt = state.get(receipt_key)
    if version is None and report is None and receipt is None:
        continue
    if (report is None) != (receipt is None):
        raise SystemExit(
            f"ERROR: {report_key}/{receipt_key} must both be null or populated"
        )
    if (version is not None and
            (not isinstance(version, int) or isinstance(version, bool) or version < 1)):
        raise SystemExit(f"ERROR: {version_key} must be a positive integer or null")
    if report is None:
        if version is not None:
            raise SystemExit(
                f"ERROR: {version_key} cannot be populated without report/receipt pointers"
            )
        continue
    for raw, key, suffix in (
        (report, report_key, ".md"),
        (receipt, receipt_key, "results.receipt.json"),
    ):
        if not isinstance(raw, str) or not raw:
            raise SystemExit(f"ERROR: {key} must be a normalized output path or null")
        path_value = PurePosixPath(raw.replace("\\", "/"))
        normalized = path_value.as_posix()
        if (path_value.is_absolute()
                or any(part in {"", ".", ".."} for part in path_value.parts)
                or any(part == ".git" or part.startswith(".env") for part in path_value.parts)
                or normalized != raw or not normalized.startswith("output/")
                or not normalized.endswith(suffix)):
            raise SystemExit(f"ERROR: {key} must be a normalized output path or null")
PY
elif [ "$MANUAL" != "true" ] && [ "$MODE" != "report" ]; then
    echo "ERROR: autonomous update requires process_log/pipeline_state.json" >&2
    exit 1
fi

# Validate every existing mutable evidence control before replacing managed
# infrastructure. Same-version updates never create missing mutable state.
"$UPDATE_CONTROL_PYTHON" -I - "$PROJECT" "$MANUAL" "$MODE" <<'PY'
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import PurePosixPath

project, manual_text, mode = sys.argv[1:]
no_follow = getattr(os, "O_NOFOLLOW", 0)

def load_regular(path, label):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | no_follow)
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot safely read {label}: {exc}")
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(fd)
        raise SystemExit(f"ERROR: {label} must be one regular non-aliased file")
    try:
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: {label} is not valid UTF-8 JSON: {exc}")

def normalized_receipt(raw):
    if not isinstance(raw, str) or not raw:
        raise SystemExit("ERROR: result receipt paths must be non-empty strings")
    posix = PurePosixPath(raw.replace("\\", "/"))
    normalized = posix.as_posix()
    if (posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts)
            or any(part == ".git" or part.startswith(".env") for part in posix.parts)
            or normalized != raw or not normalized.startswith("output/")
            or not normalized.endswith("results.receipt.json")):
        raise SystemExit("ERROR: result receipt paths must be normalized output receipts")
    return normalized

def normalized_report(raw):
    if not isinstance(raw, str) or not raw:
        raise SystemExit("ERROR: result report paths must be non-empty strings")
    posix = PurePosixPath(raw.replace("\\", "/"))
    normalized = posix.as_posix()
    if (posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts)
            or any(part == ".git" or part.startswith(".env") for part in posix.parts)
            or normalized != raw or not normalized.startswith("output/")
            or not normalized.endswith(".md")):
        raise SystemExit("ERROR: result report paths must be normalized output Markdown files")
    return normalized

def open_project_regular(relative, label):
    parts = PurePosixPath(relative).parts
    try:
        directory_fd = os.open(
            project, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | no_follow
        )
        for part in parts[:-1]:
            next_fd = os.open(
                part, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | no_follow,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
        fd = os.open(
            parts[-1], os.O_RDONLY | os.O_NONBLOCK | no_follow,
            dir_fd=directory_fd,
        )
        os.close(directory_fd)
    except OSError as exc:
        try:
            os.close(directory_fd)
        except (NameError, OSError):
            pass
        raise SystemExit(f"ERROR: cannot safely read {label}: {exc}")
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(fd)
        raise SystemExit(f"ERROR: {label} must be one regular non-aliased file")
    return fd

def read_project_json(relative, label):
    fd = open_project_regular(relative, label)
    try:
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: {label} is not valid UTF-8 JSON: {exc}")

def project_file_digest(relative, label):
    fd = open_project_regular(relative, label)
    digest = hashlib.sha256()
    with os.fdopen(fd, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()

manual_path = os.path.join(project, "process_log", "manual_evidence_state.json")
if os.path.lexists(manual_path):
    value = load_regular(manual_path, "process_log/manual_evidence_state.json")
    evidence = value.get("loops", {}).get("evidence") if isinstance(value, dict) else None
    if (not isinstance(value, dict)
            or value.get("kind") != "manual_evidence_state"
            or isinstance(value.get("state_version"), bool)
            or value.get("state_version") != 1
            or set(value) != {"kind", "state_version", "loops"}
            or not isinstance(value.get("loops"), dict)
            or set(value["loops"]) != {"evidence"}
            or not isinstance(evidence, dict)
            or set(evidence) != {"round", "cap"}
            or not all(isinstance(evidence[key], int) and not isinstance(evidence[key], bool)
                       for key in ("round", "cap"))
            or evidence["round"] < 0 or evidence["cap"] < 1):
        raise SystemExit("ERROR: process_log/manual_evidence_state.json is malformed")
elif manual_text == "true":
    raise SystemExit(
        "ERROR: manual update requires process_log/manual_evidence_state.json; "
        "create a fresh deployment"
    )

if mode == "report":
    raise SystemExit(0)

output = os.path.join(project, "output")
process_log = os.path.join(project, "process_log")
for path, label in ((output, "output"), (process_log, "process_log")):
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: {label}/ must exist before update")
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise SystemExit(f"ERROR: {label}/ must be a real directory")

evidence_dir = os.path.join(output, "evidence")
try:
    info = os.lstat(evidence_dir)
except FileNotFoundError:
    raise SystemExit(
        "ERROR: update requires output/evidence from the same template version; "
        "create a fresh deployment"
    )
if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
    raise SystemExit("ERROR: output/evidence must be a real directory")

stage0_dir = os.path.join(output, "stage0")
if os.path.lexists(stage0_dir):
    info = os.lstat(stage0_dir)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise SystemExit("ERROR: output/stage0 must be a real directory")

registry_temp = os.path.join(process_log, ".results_registry.update.tmp")
if os.path.lexists(registry_temp):
    info = os.lstat(registry_temp)
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise SystemExit("ERROR: unsafe stale results-registry update file")

registry_path = os.path.join(process_log, "results_registry.json")
if not os.path.lexists(registry_path):
    raise SystemExit(
        "ERROR: update requires process_log/results_registry.json from the same "
        "template version; create a fresh deployment"
    )

value = load_regular(registry_path, "process_log/results_registry.json")
required = {"kind", "registry_version", "active", "pending", "retired",
            "receipt_fingerprints"}
if (not isinstance(value, dict) or set(value) != required
        or value.get("kind") != "result_registry"
        or isinstance(value.get("registry_version"), bool)
        or value.get("registry_version") != 1):
    raise SystemExit("ERROR: process_log/results_registry.json is malformed")
active = value["active"]
if (not isinstance(active, list)
        or any(not isinstance(item, str) or not item for item in active)
        or len(active) != len(set(active))):
    raise SystemExit("ERROR: results registry has malformed active entries")
active = [normalized_receipt(item) for item in active]
pending_paths = []
if not isinstance(value["pending"], list):
    raise SystemExit("ERROR: results registry has malformed pending entries")
for entry in value["pending"]:
    if (not isinstance(entry, dict) or set(entry) != {"receipt", "supersedes"}
            or not isinstance(entry["supersedes"], list)
            or any(not isinstance(item, str) or not item
                   for item in entry["supersedes"])
            or len(entry["supersedes"]) != len(set(entry["supersedes"]))):
        raise SystemExit("ERROR: results registry has malformed pending entries")
    receipt = normalized_receipt(entry.get("receipt"))
    supersedes = [normalized_receipt(item) for item in entry["supersedes"]]
    if receipt in supersedes or not set(supersedes).issubset(active):
        raise SystemExit("ERROR: results registry has malformed pending entries")
    pending_paths.append(receipt)
retired_paths = []
if not isinstance(value["retired"], list):
    raise SystemExit("ERROR: results registry has malformed retired entries")
for entry in value["retired"]:
    allowed = {"receipt", "reason", "last_fingerprint", "superseded_by"}
    if (not isinstance(entry, dict) or not {"receipt", "reason", "last_fingerprint"}.issubset(entry)
            or not set(entry).issubset(allowed) or not isinstance(entry["reason"], str)
            or not entry["reason"] or not isinstance(entry["last_fingerprint"], dict)):
        raise SystemExit("ERROR: results registry has malformed retired entries")
    receipt = normalized_receipt(entry["receipt"])
    last = entry["last_fingerprint"]
    if (set(last) != {"path", "kind", "sha256"}
            or last.get("path") != receipt or last.get("kind") != "file"
            or not isinstance(last.get("sha256"), str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", last["sha256"])):
        raise SystemExit("ERROR: results registry has malformed retired entries")
    if "superseded_by" in entry:
        normalized_receipt(entry["superseded_by"])
    retired_paths.append(receipt)
if (len(pending_paths) != len(set(pending_paths))
        or len(retired_paths) != len(set(retired_paths))
        or set(active) & set(pending_paths) or set(active) & set(retired_paths)
        or set(pending_paths) & set(retired_paths)):
    raise SystemExit("ERROR: results registry has conflicting lifecycle entries")
fingerprints = value["receipt_fingerprints"]
if not isinstance(fingerprints, dict) or set(fingerprints) != set(active) | set(pending_paths):
    raise SystemExit("ERROR: results registry has malformed receipt fingerprints")
for receipt, record in fingerprints.items():
    normalized_receipt(receipt)
    if (not isinstance(record, dict) or set(record) != {"path", "kind", "sha256"}
            or record.get("path") != receipt or record.get("kind") != "file"
            or not isinstance(record.get("sha256"), str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", record["sha256"])):
        raise SystemExit("ERROR: results registry has malformed receipt fingerprints")

receipt_values = {}
for receipt in active + pending_paths:
    expected = fingerprints[receipt]["sha256"]
    if project_file_digest(receipt, f"registered receipt {receipt}") != expected:
        raise SystemExit(f"ERROR: registered receipt fingerprint is stale: {receipt}")
    receipt_values[receipt] = read_project_json(receipt, f"registered receipt {receipt}")
    if not isinstance(receipt_values[receipt], dict):
        raise SystemExit(f"ERROR: registered receipt must be a JSON object: {receipt}")
for entry in value["retired"]:
    receipt = entry["receipt"]
    if project_file_digest(receipt, f"retired receipt {receipt}") != entry["last_fingerprint"]["sha256"]:
        raise SystemExit(f"ERROR: retired receipt fingerprint is stale: {receipt}")
    receipt_values[receipt] = read_project_json(receipt, f"retired receipt {receipt}")
    if not isinstance(receipt_values[receipt], dict):
        raise SystemExit(f"ERROR: retired receipt must be a JSON object: {receipt}")

state_path = os.path.join(process_log, "pipeline_state.json")
if os.path.lexists(state_path):
    state = load_regular(state_path, "process_log/pipeline_state.json")
    pointer_pairs = [
        ("stage2b_exploration_path", "stage2b_result_receipt"),
        ("stage3a_analysis_path", "stage3a_result_receipt"),
        ("stage3b_results_path", "stage3b_result_receipt"),
    ]
    for report_key, receipt_key in pointer_pairs:
        receipt = state.get(receipt_key)
        report = state.get(report_key)
        if receipt is None and report is None:
            continue
        if receipt is None or report is None:
            raise SystemExit(
                f"ERROR: {report_key}/{receipt_key} must both be null or populated"
            )
        receipt = normalized_receipt(receipt)
        report = normalized_report(report)
        if receipt not in active:
            raise SystemExit(f"ERROR: {receipt_key} must name an active result receipt")
        report_fd = open_project_regular(report, f"active report {report}")
        os.close(report_fd)
        producer = receipt_values[receipt].get("producer_run")
        artifacts = producer.get("artifacts") if isinstance(producer, dict) else None
        artifact_paths = {
            item.get("path") for item in artifacts if isinstance(item, dict)
        } if isinstance(artifacts, list) else set()
        if report not in artifact_paths:
            raise SystemExit(
                f"ERROR: {report_key} is not a generated artifact of {receipt_key}"
            )
PY

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
if [ "$DRY_RUN" = "1" ]; then
    TMP=$(mktemp -d /tmp/zeropaper-update.XXXXXX)
else
    TMP=$(mktemp -d "$UPDATE_CONTROL_DIR/update.XXXXXX")
fi
FRESH="$TMP/refresh"
SETUP_TMPDIR="$TMP/setup-tmp"
(umask 077 && mkdir "$SETUP_TMPDIR")
OLD_MANIFEST_SNAPSHOT="$TMP/target-manifest.before.json"
cp "$MANIFEST" "$OLD_MANIFEST_SNAPSHOT"

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
if [ "$NEW_VERSION" != "$OLD_VERSION" ]; then
    echo "ERROR: template source changed during update assembly; rerun from one stable checkout" >&2
    exit 1
fi
PINNED_SOURCE_DIGEST="$(jq -er '.source.content_digest | strings | select(test("^sha256:[0-9a-f]{64}$"))' "$NEW_MANIFEST")" \
    || { echo "ERROR: fresh deploy manifest has no valid source content digest" >&2; exit 1; }
RECORDED_SOURCE_DIGEST="$(jq -er '.source.content_digest | strings | select(test("^sha256:[0-9a-f]{64}$"))' "$MANIFEST")" \
    || { echo "ERROR: target manifest has no valid source content digest" >&2; exit 1; }
if [ "$RECORDED_SOURCE_DIGEST" != "$PINNED_SOURCE_DIGEST" ]; then
    echo "ERROR: target deployment was not assembled from this exact source snapshot" >&2
    echo "  Create a fresh deployment; cross-snapshot update compatibility is unsupported." >&2
    exit 1
fi
if [ "$PINNED_SOURCE_DIGEST" != "$ATTESTED_SOURCE_DIGEST" ]; then
    echo "ERROR: this checkout does not match the operator-attested trusted setup digest" >&2
    echo "  Create a fresh deployment; cross-snapshot update compatibility is unsupported." >&2
    exit 1
fi
# The exact-selector preflight means setup's resolved extension list must be
# identical as well; the trusted manifest comparison below enforces it.

EXPECTED_OLD_MANIFEST="$NEW_MANIFEST"
ORIGINAL_STATE_REFERENCE="$FRESH/process_log/pipeline_state.json"

# Same-generation means the mutable autonomous state has the exact field
# inventory emitted by this checkout. Validate that complete shape before any
# target replacement; do not maintain a second partial schema in the updater.
if [ "$MANUAL" != "true" ] && [ "$MODE" != "report" ]; then
    python3 -I - "$EVIDENCE_STATE" "$ORIGINAL_STATE_REFERENCE" "$VARIANT" <<'PY'
import json
import re
import sys

target_path, fresh_path, variant = sys.argv[1:]
with open(target_path, encoding="utf-8") as handle:
    target = json.load(handle)
with open(fresh_path, encoding="utf-8") as handle:
    fresh = json.load(handle)
if not isinstance(target, dict) or set(target) != set(fresh):
    raise SystemExit(
        "ERROR: pipeline state field inventory does not match this template version; "
        "create a fresh deployment"
    )

def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)

for key, expected in fresh.items():
    value = target[key]
    if key == "loops":
        if not isinstance(value, dict) or set(value) != set(expected):
            raise SystemExit("ERROR: pipeline state loops do not match this template version")
        for loop, loop_value in value.items():
            if (not isinstance(loop_value, dict) or set(loop_value) != {"round", "cap"}
                    or not integer(loop_value["round"]) or loop_value["round"] < 0
                    or not integer(loop_value["cap"]) or loop_value["cap"] < 1
                    or loop_value["cap"] != expected[loop]["cap"]):
                raise SystemExit(f"ERROR: pipeline state loop {loop} is malformed")
        continue
    if key == "archived_best_scores":
        if (not isinstance(value, dict)
                or any(re.fullmatch(r"r[1-9][0-9]*", round_key) is None
                       or not isinstance(score, (int, float))
                       or isinstance(score, bool)
                       for round_key, score in value.items())):
            raise SystemExit("ERROR: pipeline state archived_best_scores is malformed")
        continue
    if key == "stage0_discovery_phase":
        if value not in {
                "entry", "entry_initializing", "scan_charged", "gap_search",
                "cap_routing", "promotion"}:
            raise SystemExit("ERROR: pipeline state stage0_discovery_phase is malformed")
        continue
    if key == "stage0_discovery_step":
        if value not in {None, "characterize", "pose", "review", "route", "select"}:
            raise SystemExit("ERROR: pipeline state stage0_discovery_step is malformed")
        continue
    if key in {"problem_attempt", "theory_attempt", "theory_version"}:
        if not integer(value) or value < 1:
            raise SystemExit(f"ERROR: pipeline state field {key} must be positive")
        continue
    if key in {"regeneration_round", "stage0_discovery_gap_serial"}:
        if not integer(value) or value < 0:
            raise SystemExit(f"ERROR: pipeline state field {key} must be nonnegative")
        continue
    if expected is None:
        if value is None:
            continue
        if key == "pivot_resolved":
            valid = isinstance(value, bool)
        elif key == "stage0_discovery_pending_scan":
            valid = (isinstance(value, dict)
                     and set(value) == {"instruction", "permit"}
                     and isinstance(value["instruction"], str)
                     and integer(value["permit"]) and value["permit"] >= 1)
        elif key.endswith("_version") or key.endswith("_attempt"):
            valid = integer(value) and value >= 1
        elif key.endswith("_serial"):
            valid = integer(value) and value >= 0
        else:
            valid = isinstance(value, str) and bool(value)
        if not valid:
            raise SystemExit(f"ERROR: pipeline state field {key} has an invalid type")
        continue
    if key in {"seeded", "faithful", "halt_on_core_bypass",
               "initial_journal_tier"}:
        if value != expected or type(value) is not type(expected):
            raise SystemExit(
                f"ERROR: pipeline state field {key} does not match its immutable setup value"
            )
        continue
    if isinstance(expected, bool):
        valid = isinstance(value, bool)
    elif isinstance(expected, int):
        valid = integer(value)
    elif isinstance(expected, str):
        valid = isinstance(value, str) and bool(value)
    elif isinstance(expected, list):
        valid = isinstance(value, list)
    elif isinstance(expected, dict):
        valid = isinstance(value, dict)
    else:
        valid = type(value) is type(expected)
    if not valid:
        raise SystemExit(f"ERROR: pipeline state field {key} has an invalid type")

tier_ladders = {
    "finance": ("top-5", "top-3-fin", "field", "letters"),
    "macro": ("top-5", "field", "letters"),
    "llm_cognition": ("nature", "top-ml", "field", "workshop"),
}
ladder = tier_ladders[variant]
target_tier = target.get("target_journal_tier")
initial_tier = target["initial_journal_tier"]
if target_tier not in ladder:
    raise SystemExit(
        "ERROR: pipeline state target_journal_tier is outside the variant ladder"
    )
if ladder.index(target_tier) < ladder.index(initial_tier):
    raise SystemExit(
        "ERROR: pipeline state target_journal_tier is above its immutable initial tier"
    )

allowed_statuses = {
    "not_started", "running", "complete", "complete_pending_verification",
    "halted_core_bypass", "halted_no_identification_design",
    "halted_seed_abandon", "halted_wrds_unreachable",
    "halted_data_audit_unreachable", "halted_replicator_self_failure",
    "halted_replicator_unrecognized_failure", "halted_replication_artifact_collision",
}
status = target["status"]
if status not in allowed_statuses:
    raise SystemExit("ERROR: pipeline state status is malformed")
allowed_stages = {"seed_triage", "stage_1_identification_design"}
allowed_stages.update(f"stage_{index}" for index in range(11))
if target["current_stage"] not in allowed_stages:
    raise SystemExit("ERROR: pipeline state current_stage is malformed")
for index, entry in enumerate(target["history"]):
    if (not isinstance(entry, dict) or set(entry) != {"timestamp", "event"}
            or not all(isinstance(entry[name], str) and entry[name]
                       for name in ("timestamp", "event"))):
        raise SystemExit(f"ERROR: pipeline state history[{index}] is malformed")
PY
fi

if [ "$MANUAL" = "true" ]; then
    python3 -I - "$PROJECT/process_log/manual_evidence_state.json" \
        "$FRESH/process_log/manual_evidence_state.json" <<'PY'
import json
import sys

target_path, fresh_path = sys.argv[1:]
with open(target_path, encoding="utf-8") as handle:
    target = json.load(handle)
with open(fresh_path, encoding="utf-8") as handle:
    fresh = json.load(handle)
if (target.get("kind") != fresh.get("kind")
        or target.get("state_version") != fresh.get("state_version")
        or target.get("loops", {}).get("evidence", {}).get("cap")
           != fresh.get("loops", {}).get("evidence", {}).get("cap")):
    raise SystemExit(
        "ERROR: manual evidence state invariants do not match this template version"
    )
PY
fi

# Use only the freshly assembled utility—not target-project executable code—to
# validate every lifecycle receipt against the current immutable contract.
# --read-only performs no lock creation or transaction recovery, preserving the
# update dry-run guarantee.
if [ "$MODE" != "report" ]; then
    while IFS= read -r receipt; do
        [ -n "$receipt" ] || continue
        if ! python3 -I "$FRESH/code/utils/results_pipeline/results_pipeline.py" \
            validate-receipt --read-only --project-root "$PROJECT" \
            --receipt "$receipt" >/dev/null; then
            echo "ERROR: results registry contains an invalid receipt: $receipt" >&2
            exit 1
        fi
    done < <(jq -r '.active[]?, .pending[]?.receipt, .retired[]?.receipt' \
        "$PROJECT/process_log/results_registry.json")
fi

# A completed run is terminal to every launcher, so a stale or malformed bound
# paper receipt must be converted into durable Stage-9 work by the updater
# itself. The freshly assembled verifier is trusted; --read-only neither locks
# nor recovers/mutates the target.
PAPER_REAUDIT_REQUIRED=0
if [ "$MANUAL" != "true" ] && [ "$MODE" != "report" ]; then
    _paper_status="$(jq -r '.status' "$EVIDENCE_STATE")"
    if [ "$_paper_status" = "complete" ] || \
       [ "$_paper_status" = "complete_pending_verification" ]; then
        if ! python3 -I "$FRESH/code/utils/results_pipeline/results_pipeline.py" \
            verify-paper --read-only --project-root "$PROJECT" \
            --receipt process_log/paper_evidence.receipt.json >/dev/null 2>&1; then
            PAPER_REAUDIT_REQUIRED=1
        fi
    fi
fi

# Authenticate the target's complete ownership inventory against a trusted
# same-version assembly of its recorded selector. A project-writable manifest
# may not omit retired infrastructure and thereby suppress the stale sweep.
python3 -I - "$MANIFEST" "$EXPECTED_OLD_MANIFEST" <<'PY'
import json, sys
target_path, expected_path = sys.argv[1:]
with open(target_path, encoding="utf-8") as handle:
    target = json.load(handle)
with open(expected_path, encoding="utf-8") as handle:
    expected = json.load(handle)
for key in ("variant", "mode", "extensions", "flags", "infrastructure"):
    if target.get(key) != expected.get(key):
        raise SystemExit(
            f"ERROR: deployment manifest {key} does not match the trusted "
            "same-version assembly; create a fresh deployment"
        )
PY

# Pre-sandbox agents could have aliased any managed parent, not just
# `.opencode`. Validate every existing ancestor used by replacement, merging,
# or stale sweeping before the first target mutation.
python3 -I - "$PROJECT" "$NEW_MANIFEST" "$MANIFEST" <<'PY'
import json, os, stat, sys
from pathlib import PurePosixPath

project, new_path, old_path = sys.argv[1:]
new_manifest = json.load(open(new_path, encoding="utf-8"))
manifests = [new_manifest]
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
for value in new_manifest.get("infrastructure", {}).get("files_replace", []):
    target = os.path.join(project, value)
    if not os.path.lexists(target):
        continue
    info = os.lstat(target)
    if not stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode):
        raise SystemExit(
            f"ERROR: managed file target has an incompatible type: {target}"
        )
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

# ── Snapshot agent set BEFORE replacement (for diff) ──
OLD_AGENTS_TMP="$TMP/old_agents.txt"
NEW_AGENTS_TMP="$TMP/new_agents.txt"
ls "$PROJECT/.claude/agents/" 2>/dev/null | sort > "$OLD_AGENTS_TMP" || true
ls "$FRESH/.claude/agents/"   2>/dev/null | sort > "$NEW_AGENTS_TMP" || true

# All read-only target/source/state/ownership checks have succeeded. Publish
# the launch barrier at the last possible point before target infrastructure
# can change. A crash-left marker validated above is reused rather than
# replaced, preserving its durable recovery signal.
if [ "$DRY_RUN" = "0" ] && [ "$UPDATE_MARKER_PRESENT" = "0" ]; then
    "$UPDATE_CONTROL_PYTHON" -I - "$UPDATE_TRANSACTION_MARKER" "$UPDATE_CONTROL_DIR" \
        "$UPDATE_PROCESS_LOG" "$UPDATE_CREATED_CONTROL_DIR" <<'PY'
import os, sys
path, directory, parent, created_text = sys.argv[1:]
fd = os.open(
    path,
    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
    0o600,
)
with os.fdopen(fd, "wb") as handle:
    handle.write(b"zeropaper update transaction\n")
    handle.flush()
    os.fsync(handle.fileno())
dir_fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
try:
    os.fsync(dir_fd)
finally:
    os.close(dir_fd)
if created_text == "1":
    parent_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
PY
    UPDATE_MARKER_PRESENT=1
fi

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
    if [ -d "$PROJECT/$f" ] && [ ! -L "$PROJECT/$f" ]; then
        echo "ERROR: managed file target became a directory after preflight: $f" >&2
        exit 1
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
# remove it. The complete old ownership inventory has already been matched
# byte-for-byte against a trusted same-version assembly, so it is the sole
# deletion source; there is intentionally no second hand-maintained catalog.
# files_env_merge (.env) is deliberately not swept: it is user-merged, not
# replaced.
if [ -f "$MANIFEST" ]; then
    sweep() {
        local kind="$1" jqlist="$2" p
        while IFS= read -r p; do
            # Never remove a current managed path or one of its
            # ancestors/descendants.
            if jq -e --arg p "$p" '
                [.infrastructure.dirs_replace[]?, .infrastructure.files_replace[]?, .infrastructure.files_env_merge[]?]
                | any(. as $q | $q == $p or ($q | startswith($p + "/")) or ($p | startswith($q + "/")))
            ' "$NEW_MANIFEST" >/dev/null; then
                continue
            fi
            [ -e "$PROJECT/$p" ] || [ -L "$PROJECT/$p" ] || continue
            if [ "$kind" = "dir" ]; then
                if [ ! -d "$PROJECT/$p" ] || [ -L "$PROJECT/$p" ]; then
                    echo "ERROR: stale managed directory changed type: $p" >&2
                    exit 1
                fi
            elif [ -d "$PROJECT/$p" ] && [ ! -L "$PROJECT/$p" ]; then
                echo "ERROR: stale managed file changed into a directory: $p" >&2
                exit 1
            fi
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
    sweep dir dirs_replace
    sweep file files_replace
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
    env_source="$FRESH/$env_file"
    env_source_fd=""
    if [ "$env_file" = ".env" ] && [ -n "$UPDATE_DOTENV_FD" ]; then
        env_source_fd="$UPDATE_DOTENV_FD"
    fi
    if [ -n "$env_source_fd" ] || [ -f "$env_source" ]; then
        python3 -I - "$env_source" "$PROJECT/$env_file" "$DRY_RUN" "$env_source_fd" <<'PY'
import hashlib, os, re, stat, sys

source, target, dry_text, source_fd_text = sys.argv[1:]
dry_run = dry_text == "1"
no_follow = getattr(os, "O_NOFOLLOW", 0)
staged = os.path.join(
    os.path.dirname(target), f".{os.path.basename(target)}.zeropaper-update.next"
)
target_exists = os.path.lexists(target)
if target_exists:
    fd = os.open(target, os.O_RDONLY | no_follow)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(fd)
        raise SystemExit(
            f"ERROR: environment target must be one regular non-aliased file: {target}"
        )
    mode = stat.S_IMODE(info.st_mode)
    with os.fdopen(fd, "r", encoding="utf-8", newline="") as handle:
        existing = handle.read()
else:
    mode = 0o600
    existing = ""
    print(f"  ! {os.path.basename(target)} missing in target — " +
          ("would copy fresh" if dry_run else "copying fresh"))

additions = []
if source_fd_text:
    source_fd = int(source_fd_text)
    with os.fdopen(os.dup(source_fd), "rb") as pipe:
        framed = pipe.read()
    header, separator, payload = framed.partition(b"\n")
    match = re.fullmatch(
        rb"ZEROPAPER_DOTENV_V1 ([0-9]+) ([0-9a-f]{64})", header
    )
    if (not separator or match is None or int(match.group(1)) != len(payload)
            or hashlib.sha256(payload).hexdigest().encode("ascii") != match.group(2)):
        raise SystemExit("ERROR: authenticated operator environment transfer was truncated")
    try:
        source_text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit("ERROR: source environment is not valid UTF-8") from exc
    if source_text and not source_text.endswith("\n"):
        source_text += "\n"
    source_lines = source_text.splitlines(keepends=True)
    seen_keys = {
        line.rstrip("\n").split("=", 1)[0]
        for line in source_lines
        if line.rstrip("\n") and not line.startswith("#")
    }
    # Fresh setup normally copies the operator .env and then appends every
    # missing .env.example key. The operator bytes stay anonymous here, but
    # update must preserve that same composite source semantics.
    with open(source, encoding="utf-8") as source_handle:
        for line in source_handle:
            stripped = line.rstrip("\n")
            if not stripped or stripped.startswith("#"):
                continue
            key = stripped.split("=", 1)[0]
            if key not in seen_keys:
                source_lines.append(line if line.endswith("\n") else line + "\n")
                seen_keys.add(key)
else:
    with open(source, encoding="utf-8") as source_handle:
        source_lines = source_handle.readlines()
if not target_exists:
    existing = "".join(source_lines)
for line in source_lines:
    line = line.rstrip("\n")
    if not line or line.startswith("#"):
        continue
    key = line.split("=", 1)[0]
    if not target_exists:
        additions.append((key, line))
    elif not any(row.startswith(key + "=") for row in existing.splitlines()):
        additions.append((key, line))
        existing += ("" if not existing or existing.endswith("\n") else "\n") + line + "\n"
for key, _line in additions:
    print(f"  + {key}" + (" (would add)" if dry_run else ""))
if not additions and target_exists:
    print("  (no new keys)")
if dry_run or (target_exists and not additions):
    raise SystemExit(0)

if os.path.lexists(staged):
    staged_fd = os.open(staged, os.O_RDONLY | os.O_NONBLOCK | no_follow)
    staged_info = os.fstat(staged_fd)
    os.close(staged_fd)
    if not stat.S_ISREG(staged_info.st_mode) or staged_info.st_nlink != 1:
        raise SystemExit("ERROR: unsafe interrupted environment merge file")
    os.unlink(staged)
fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | no_follow, mode)
try:
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        handle.write(existing)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(staged, target)
    directory_fd = os.open(
        os.path.dirname(target), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    )
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
except BaseException:
    try:
        if os.path.lexists(staged):
            os.unlink(staged)
    except OSError:
        pass
    raise
PY
    fi
done < <(jq -r '.infrastructure.files_env_merge[]?' "$NEW_MANIFEST")

# Completed launchers are terminal, so stale paper evidence must become
# durable Stage-9 work before the refreshed manifest can commit. This is the
# only project-owned state transition performed by update; selector fields are
# immutable.
if [ "$PAPER_REAUDIT_REQUIRED" = "1" ]; then
    if [ "$DRY_RUN" = "1" ]; then
        echo "  project state: would reopen Stage 9 for paper evidence re-audit"
    else
        python3 -I - "$EVIDENCE_STATE" <<'PY'
from datetime import datetime, timezone
import json
import os
import stat
import sys

path = sys.argv[1]
no_follow = getattr(os, "O_NOFOLLOW", 0)
fd = os.open(path, os.O_RDONLY | no_follow)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    os.close(fd)
    raise SystemExit("ERROR: pipeline state changed type before Stage-9 reopen")
with os.fdopen(fd, "r", encoding="utf-8") as handle:
    state = json.load(handle)
if state.get("status") not in {"complete", "complete_pending_verification"}:
    raise SystemExit("ERROR: pipeline state changed before Stage-9 reopen")
state["status"] = "running"
state["current_stage"] = "stage_9"
state["history"].append({
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "event": "Updater reopened Stage 9 because the bound paper evidence is stale or malformed",
})
temporary = os.path.join(os.path.dirname(path), ".pipeline-state.reaudit.next")
if os.path.lexists(temporary):
    stale = os.open(
        temporary, os.O_RDONLY | os.O_NONBLOCK | no_follow
    )
    stale_info = os.fstat(stale)
    os.close(stale)
    if not stat.S_ISREG(stale_info.st_mode) or stale_info.st_nlink != 1:
        raise SystemExit("ERROR: unsafe interrupted Stage-9 state publication")
    os.unlink(temporary)
out = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | no_follow,
              stat.S_IMODE(info.st_mode))
try:
    with os.fdopen(out, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    directory = os.open(
        os.path.dirname(path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
except BaseException:
    if os.path.lexists(temporary):
        os.unlink(temporary)
    raise
PY
    fi
fi

# ── Refresh manifest in target (preserve original deploy_date + fingerprint) ──
if [ "$DRY_RUN" = "0" ]; then
    manifest_tmp="$TMP/manifest.next"
    # Update template_version + last_updated and sync deployment selectors from
    # the verified fresh assembly while preserving project identity metadata.
    if ! jq --arg v "$NEW_VERSION" --arg d "$(date -u +%Y-%m-%d)" \
       'input as $new
        | .template_version = $v
        | .last_updated = $d
        | .variant = $new.variant
        | .mode = $new.mode
        | .extensions = $new.extensions
        | .flags = $new.flags
        | .source = $new.source
        | .infrastructure = $new.infrastructure' \
       "$MANIFEST" "$NEW_MANIFEST" > "$manifest_tmp"; then
        rm -f "$manifest_tmp"
        exit 1
    fi
    python3 -I - "$manifest_tmp" "$MANIFEST" "$PROJECT" <<'PY'
import os
import stat
import sys

source, destination, project = sys.argv[1:]
no_follow = getattr(os, "O_NOFOLLOW", 0)
source_fd = os.open(source, os.O_RDONLY | no_follow)
source_info = os.fstat(source_fd)
if not stat.S_ISREG(source_info.st_mode) or source_info.st_nlink != 1:
    os.close(source_fd)
    raise SystemExit("ERROR: staged deployment manifest is not one regular file")
staged = os.path.join(project, ".deploy_manifest.zeropaper-update.next")
if os.path.lexists(staged):
    stale_fd = os.open(staged, os.O_RDONLY | os.O_NONBLOCK | no_follow)
    stale_info = os.fstat(stale_fd)
    os.close(stale_fd)
    if not stat.S_ISREG(stale_info.st_mode) or stale_info.st_nlink != 1:
        os.close(source_fd)
        raise SystemExit("ERROR: unsafe interrupted deployment-manifest staging file")
    os.unlink(staged)
staged_fd = os.open(
    staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL | no_follow,
    stat.S_IMODE(source_info.st_mode),
)
try:
    while True:
        chunk = os.read(source_fd, 1024 * 1024)
        if not chunk:
            break
        view = memoryview(chunk)
        while view:
            written = os.write(staged_fd, view)
            if written <= 0:
                raise SystemExit("ERROR: short write while staging deployment manifest")
            view = view[written:]
    os.fsync(staged_fd)
finally:
    os.close(staged_fd)
    os.close(source_fd)
os.replace(staged, destination)
root_fd = os.open(project, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
try:
    os.fsync(root_fd)
finally:
    os.close(root_fd)
PY
    echo
    echo "  ✓ manifest updated: template_version $OLD_VERSION → $NEW_VERSION"
fi

# The transaction marker is the launch barrier. Before it can disappear,
# force every published managed byte and every affected directory entry to
# stable storage, including parents that recorded stale-path deletions.
if [ "$DRY_RUN" = "0" ]; then
    python3 -I - "$PROJECT" "$NEW_MANIFEST" "$OLD_MANIFEST_SNAPSHOT" <<'PY'
import json
import os
import stat
import sys

project, new_manifest_path, old_manifest_path = sys.argv[1:]
with open(new_manifest_path, encoding="utf-8") as handle:
    new = json.load(handle)["infrastructure"]
with open(old_manifest_path, encoding="utf-8") as handle:
    old = json.load(handle)["infrastructure"]
no_follow = getattr(os, "O_NOFOLLOW", 0)
directory_flag = getattr(os, "O_DIRECTORY", 0)

def fsync_file(path):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | no_follow)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise SystemExit(f"ERROR: managed file changed type before durability barrier: {path}")
        os.fsync(fd)
    finally:
        os.close(fd)

def fsync_tree(path):
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode):
        raise SystemExit(f"ERROR: managed tree contains a symlink at durability barrier: {path}")
    if stat.S_ISREG(info.st_mode):
        fsync_file(path)
        return
    if not stat.S_ISDIR(info.st_mode):
        raise SystemExit(f"ERROR: managed tree contains a special file: {path}")
    with os.scandir(path) as entries:
        children = [entry.path for entry in entries]
    for child in children:
        fsync_tree(child)
    fd = os.open(path, os.O_RDONLY | directory_flag | no_follow)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

for relative in new.get("dirs_replace", []):
    fsync_tree(os.path.join(project, relative))
for key in ("files_replace", "files_env_merge"):
    for relative in new.get(key, []):
        path = os.path.join(project, relative)
        if os.path.lexists(path):
            fsync_file(path)

directories = {project}
for manifest in (old, new):
    for key in ("dirs_replace", "files_replace", "files_env_merge"):
        for relative in manifest.get(key, []):
            current = os.path.dirname(os.path.join(project, relative))
            while current.startswith(project) and current not in directories:
                directories.add(current)
                if current == project:
                    break
                current = os.path.dirname(current)
for directory in sorted(directories, key=lambda value: value.count(os.sep), reverse=True):
    if not os.path.isdir(directory) or os.path.islink(directory):
        continue
    fd = os.open(directory, os.O_RDONLY | directory_flag | no_follow)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
PY
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
    "$UPDATE_CONTROL_PYTHON" -I - "$UPDATE_TRANSACTION_MARKER" "$UPDATE_CONTROL_DIR" <<'PY'
import os, sys
path, directory = sys.argv[1:]
os.unlink(path)
dir_fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
try:
    os.fsync(dir_fd)
finally:
    os.close(dir_fd)
PY
    echo "Update complete. Review with: cd $PROJECT && git status"
    echo "Then commit the infrastructure refresh when ready."
fi

}

# Keep LOCK_EX in the visible parent plus a detached guardian, never in the
# refresh body. If the visible updater is SIGKILLed, the guardian retains the
# lock, terminates the body's private process group, and waits for it to drain
# before releasing LOCK_EX. No updater writer can therefore outlive the lock.
coproc UPDATE_GUARD {
    /usr/bin/python3 -I /dev/fd/6 9 "$UPDATE_LAUNCHER_LIVENESS_FD" 6<<'PY'
import os
import select
import signal
import subprocess
import sys
import time

try:
    os.setsid()
except OSError:
    pass
liveness_fd = int(sys.argv[2])


def launcher_died():
    readable, _, _ = select.select([liveness_fd], [], [], 0)
    return bool(readable) and os.read(liveness_fd, 1) == b""


def read_control():
    while True:
        readable, _, _ = select.select([sys.stdin, liveness_fd], [], [], 0.1)
        # Prefer a simultaneously available PID/control message so launcher
        # death can still terminate the exact armed body identity.
        if sys.stdin in readable:
            return sys.stdin.readline().strip(), False
        if liveness_fd in readable and os.read(liveness_fd, 1) == b"":
            return "", True


raw, launcher_is_dead = read_control()
if not raw.isdigit():
    raise SystemExit(0)
child = int(raw)
deadline = time.monotonic() + 5.0
while True:
    try:
        if os.getpgid(child) == child:
            break
    except ProcessLookupError:
        print("armed", flush=True)
        raise SystemExit(0)
    launcher_is_dead = launcher_is_dead or launcher_died()
    if time.monotonic() >= deadline:
        raise SystemExit("update body did not enter its private process group")
    time.sleep(0.01)
if launcher_is_dead:
    message = ""
else:
    try:
        os.kill(child, signal.SIGUSR1)
    except ProcessLookupError:
        print("armed", flush=True)
        raise SystemExit(0)
    print("armed", flush=True)
    message, launcher_is_dead = read_control()
    if launcher_is_dead:
        message = ""
if message.startswith("complete "):
    def members():
        try:
            output = subprocess.check_output(
                ["/bin/ps", "-axo", "pid=,pgid="], text=True,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError):
            raise SystemExit("cannot enumerate update body process group")
        result = []
        for line in output.splitlines():
            fields = line.split()
            if len(fields) != 2 or not all(field.isdigit() for field in fields):
                continue
            pid, pgid = map(int, fields)
            if pgid == child and pid != child:
                result.append(pid)
        return result

    for sent_signal, duration in ((signal.SIGTERM, 2.0), (signal.SIGKILL, 5.0)):
        deadline = time.monotonic() + duration
        while True:
            remaining = members()
            if not remaining:
                print("drained", flush=True)
                raise SystemExit(0)
            for pid in remaining:
                try:
                    os.kill(pid, sent_signal)
                except ProcessLookupError:
                    pass
            if time.monotonic() >= deadline:
                break
            time.sleep(0.02)
    raise SystemExit("update body descendants did not terminate")
if message:
    raise SystemExit("invalid update body completion message")
if not message:
    # The body died before its explicit completion handshake. Its group leader
    # is still the identity armed above; terminate and drain the whole group.
    pass
else:
    raise SystemExit(0)
for sent_signal, duration in ((signal.SIGTERM, 2.0), (signal.SIGKILL, 5.0)):
    try:
        os.killpg(child, sent_signal)
    except ProcessLookupError:
        raise SystemExit(0)
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        try:
            os.killpg(child, 0)
        except ProcessLookupError:
            raise SystemExit(0)
        time.sleep(0.02)
raise SystemExit("update body process group did not terminate")
PY
}
_update_guard_read="${UPDATE_GUARD[0]}"
_update_guard_write="${UPDATE_GUARD[1]}"
_update_guard_pid="$UPDATE_GUARD_PID"
# Coprocess descriptors are marked close-on-subshell by Bash. Duplicate the
# ends onto ordinary descriptors so the body can publish its PID, report
# completion, and wait until the detached guardian drains its descendants.
exec 7>&"$_update_guard_write"
exec 8<&"$_update_guard_read"
exec {_update_guard_write}>&-
set -m
(
    _update_body_start=0
    trap '_update_body_start=1' USR1
    printf '%s\n' "$BASHPID" >&7
    while [ "$_update_body_start" = "0" ]; do
        sleep 0.01
    done
    trap - USR1
    set +e
    ( set -e; _update_main ) 7>&- 8<&-
    _update_body_status=$?
    set -e
    printf 'complete %s\n' "$_update_body_status" >&7
    if ! read -r _update_guard_drained <&8 \
       || [ "$_update_guard_drained" != "drained" ]; then
        exit 1
    fi
    exec 7>&- 8<&-
    exit "$_update_body_status"
) 9<&- &
_update_body_pid=$!
set +m
if ! read -r _update_guard_ready <&"$_update_guard_read" \
   || [ "$_update_guard_ready" != "armed" ]; then
    kill -KILL -- "-$_update_body_pid" 2>/dev/null || true
    echo "ERROR: update supervisor failed to arm" >&2
    exit 1
fi
exec 7>&-
if wait "$_update_body_pid"; then
    _update_body_status=0
else
    _update_body_status=$?
fi
exec 8<&-
wait "$_update_guard_pid"
exit "$_update_body_status"
