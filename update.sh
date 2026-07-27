#!/bin/bash
# update.sh — Refresh pipeline infrastructure in a deployed project.
#
# Usage:
#   ./update.sh <deployed-project-path>
#   ./update.sh <deployed-project-path> --dry-run
#   ./update.sh <deployed-project-path> --variant finance --ext empirical
#   ./update.sh <deployed-project-path> --seeded --manual --light
#
# Overrides (--variant, --ext, --seeded/--no-seeded, --manual/--no-manual,
# --light/--no-light) take precedence over the manifest's recorded values
# AND over sniffed values for pre-manifest deploys. Use them when the
# manifest is wrong, or when you want to migrate a project across variants.
# Each --ext repeats; passing --ext replaces the manifest's full extension
# list (does not append).
#
# What it does:
#   1. Reads .deploy_manifest.json from the target project (or sniffs/accepts
#      flags if the project predates manifests).
#   2. Deploys a fresh project into a tmp dir using setup.sh --local with the
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
OVERRIDE_MANUAL=""
OVERRIDE_LIGHT=""
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
        --manual)         OVERRIDE_MANUAL=true ;;
        --no-manual)      OVERRIDE_MANUAL=false ;;
        --light)          OVERRIDE_LIGHT=true ;;
        --no-light)       OVERRIDE_LIGHT=false ;;
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
    echo "usage: update.sh <deployed-project-path> [--dry-run] [--variant X] [--mode M] [--ext Y ...]"
    exit 1
fi

PROJECT="$(cd "$PROJECT" && pwd)"
TEMPLATE_ROOT="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$PROJECT/.deploy_manifest.json"

command -v jq >/dev/null 2>&1 || { echo "update.sh requires jq (sudo apt-get install jq)"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "update.sh requires python3"; exit 1; }

# poppler-utils is a *runtime* dependency of the refreshed pipeline, not of this
# script — so warn, never block. requirements.system is build-time-only and is
# never copied into a deployment, which means an operator refreshing an existing
# project has no other signal that the host now needs it. Without poppler the
# Stage 5 placeholder gate silently false-passes (empty pipe → grep -c prints 0),
# report mode cannot read a PDF-only submission, and paper-writer cannot see a
# figure that shipped as .pdf-only from a run predating the dual-format contract.
if ! command -v pdftotext >/dev/null 2>&1 || ! command -v pdftoppm >/dev/null 2>&1; then
    echo "  ⚠ poppler-utils (pdftotext/pdftoppm) not found on this host."
    echo "    Install it: brew install poppler  |  sudo apt-get install poppler-utils"
    echo "    Without it the Stage 5 placeholder gate silently passes and PDF reads fail."
fi

# ── Resolve original deployment parameters ──
# Every setup.sh flag that affects what gets deployed must be read here AND
# re-passed in the SETUP_FLAGS block below — drift between the two breaks the
# round-trip on update. Currently tracked: variant, mode, extensions, seeded,
# manual, light, halt_on_core_bypass. When adding a new setup.sh flag, update both blocks.
if [ -f "$MANIFEST" ]; then
    VARIANT=$(jq -r .variant "$MANIFEST")
    MODE=$(jq -r '.mode // ""' "$MANIFEST")
    EXTENSIONS=()
    while IFS= read -r _ext; do EXTENSIONS+=("$_ext"); done < <(jq -r '.extensions[]?' "$MANIFEST")
    SEEDED=$(jq -r .flags.seeded "$MANIFEST")
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

# ── Apply explicit overrides (precedence: CLI flag > manifest > sniff) ──
APPLIED_OVERRIDES=()
if [ -n "$OVERRIDE_VARIANT" ] && [ "$OVERRIDE_VARIANT" != "$VARIANT" ]; then
    APPLIED_OVERRIDES+=("variant: $VARIANT → $OVERRIDE_VARIANT")
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
if [ -n "$OVERRIDE_MANUAL" ] && [ "$OVERRIDE_MANUAL" != "$MANUAL" ]; then
    APPLIED_OVERRIDES+=("manual: $MANUAL → $OVERRIDE_MANUAL")
    MANUAL="$OVERRIDE_MANUAL"
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

# Compose the version stamp identically to setup.sh (VERSION semver + git hash,
# e.g. "2.6.0+4be4d75"), so an update→deploy round-trip preserves the semver
# component instead of overwriting the manifest with a bare hash.
NEW_HASH=$(cd "$TEMPLATE_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
NEW_SEMVER=$(tr -d '[:space:]' < "$TEMPLATE_ROOT/VERSION" 2>/dev/null || true)
NEW_VERSION="${NEW_SEMVER:+${NEW_SEMVER}+}${NEW_HASH}"

# ── Build setup.sh flag list ──
# When adding a new setup.sh flag, update both this block AND the manifest-
# read block above so update→deploy round-trips preserve the deployment.
SETUP_FLAGS=( --variant "$VARIANT" --local )
[ -n "$MODE" ] && SETUP_FLAGS+=( --mode "$MODE" )
for ext in "${EXTENSIONS[@]}"; do SETUP_FLAGS+=( --ext "$ext" ); done
[ "$SEEDED" = "true" ] && SETUP_FLAGS+=( --seed )
[ "$MANUAL" = "true" ] && SETUP_FLAGS+=( --manual )
[ "$LIGHT" = "true" ] && SETUP_FLAGS+=( --light )
[ "$HALT_ON_CORE_BYPASS" = "true" ] && SETUP_FLAGS+=( --halt-on-core-bypass )

# ── Deploy fresh into tmp ──
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
FRESH="$TMP/refresh"

echo
echo "Deploying fresh template into $FRESH ..."
( cd "$TEMPLATE_ROOT" && bash setup.sh "$FRESH" "${SETUP_FLAGS[@]}" ) >"$TMP/deploy.log" 2>&1 || {
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

# ── Merge .env (append missing keys only; never overwrite values) ──
echo
echo "=== Merging .env ==="
while IFS= read -r env_file; do
    if [ -f "$FRESH/$env_file" ] && [ -f "$PROJECT/$env_file" ]; then
        added=0
        # `|| [ -n "$line" ]` catches a final line with no trailing newline:
        # plain `read` sets the variable but returns non-zero at EOF, so the
        # loop body would skip it and that key would be silently dropped from
        # the merge. Editors that don't terminate the last line are common.
        while IFS= read -r line || [ -n "$line" ]; do
            [[ -z "$line" || "$line" =~ ^# ]] && continue
            key="${line%%=*}"
            if ! grep -q "^${key}=" "$PROJECT/$env_file" 2>/dev/null; then
                if [ "$DRY_RUN" = "1" ]; then
                    echo "  + $key (would add)"
                else
                    # Guard against the same problem on the receiving side: if
                    # the target's last line is unterminated, a bare append
                    # would concatenate onto it and corrupt both keys.
                    [ -s "$PROJECT/$env_file" ] && [ -n "$(tail -c1 "$PROJECT/$env_file")" ] \
                        && printf '\n' >> "$PROJECT/$env_file"
                    echo "$line" >> "$PROJECT/$env_file"
                    echo "  + $key"
                fi
                added=$((added+1))
            fi
        done < "$FRESH/$env_file"
        [ "$added" = "0" ] && echo "  (no new keys)"
    elif [ ! -f "$PROJECT/$env_file" ] && [ -f "$FRESH/$env_file" ]; then
        echo "  ! $env_file missing in target — copying fresh"
        # rm -f for the same dangling-symlink reason as files_replace: -f
        # tests regular files, so a dangling symlink at this path would
        # satisfy "! -f" and then trip cp.
        if [ "$DRY_RUN" = "0" ]; then
            rm -f "$PROJECT/$env_file"
            cp "$FRESH/$env_file" "$PROJECT/$env_file"
        fi
    fi
done < <(jq -r '.infrastructure.files_env_merge[]?' "$NEW_MANIFEST")

# ── Refresh the stdin-safe dotenv guard in the venv ──
# Counterpart of setup.sh's install step (see templates/utils/
# pipeline_dotenv_guard.py — installed as module + .pth, not sitecustomize.py,
# which Homebrew's stdlib copy shadows). The guard lives inside the gitignored
# .venv, so it can't ride the manifest's dirs/files lists — refreshed here as a
# dedicated step, like the .env merge. Skipped silently when the target has no
# venv (pre-venv deploys) or the template copy is missing (updating from an old
# template checkout).
_guard_src="$TEMPLATE_ROOT/templates/utils/pipeline_dotenv_guard.py"
if [ -f "$_guard_src" ] && [ -x "$PROJECT/.venv/bin/python3" ]; then
    _venv_sp="$("$PROJECT/.venv/bin/python3" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])' 2>/dev/null)"
    if [ -n "$_venv_sp" ] && [ -d "$_venv_sp" ]; then
        if [ "$DRY_RUN" = "1" ]; then
            echo "  venv: would refresh _pipeline_dotenv_guard (dotenv stdin guard)"
        else
            cp "$_guard_src" "$_venv_sp/_pipeline_dotenv_guard.py"
            printf 'import _pipeline_dotenv_guard\n' > "$_venv_sp/_pipeline_dotenv_guard.pth"
            # Remove the shadowed first-attempt install — but only if it is
            # OURS (the old file carries the _find_dotenv_stdin_safe wrapper).
            # A user-created sitecustomize.py (e.g. coverage.py's documented
            # subprocess-coverage hook) must survive the refresh.
            if [ -f "$_venv_sp/sitecustomize.py" ] \
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
# in-progress round values, so a resumed run's state matches the new docs. Idempotent:
# if `loops` already exists this is a no-op.
STATE_FILE="$PROJECT/process_log/pipeline_state.json"
if [ "$DRY_RUN" = "0" ] && [ -f "$STATE_FILE" ]; then
    python3 - "$STATE_FILE" <<'PYEOF'
import json, sys
p = sys.argv[1]
with open(p) as f: data = json.load(f)
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
    with open(p, "w") as f:
        json.dump(new, f, indent=2); f.write("\n")
    print("  ✓ pipeline_state.json migrated to loops:{} (issue #166)")
PYEOF
fi

# ── Bootstrap the project venv if missing ──
# Deploys made before the .venv change (or whose .venv was deleted) have no venv,
# but the refreshed runtime docs now tell the user/agents to
# `source .venv/bin/activate` and expect a bare `python3` to resolve there. Create
# it from the SAME single-sourced deps files setup.sh uses (templates/deps/*.txt +
# each extension's deps.txt), so a refreshed legacy project matches its new docs.
# A project that already has a .venv is left untouched — we never clobber an
# existing environment (its interpreter paths and user-installed packages).
VENV="$PROJECT/.venv"
if [ ! -d "$VENV" ]; then
    if [ "$DRY_RUN" = "1" ]; then
        echo
        echo "=== venv bootstrap ==="
        echo "  would create $VENV and install core + ssj + extension deps [${EXTENSIONS[*]}]"
    elif ! command -v uv >/dev/null 2>&1; then
        echo
        echo "  ⚠ .venv missing and uv not found — install uv, then re-run update.sh (or create it manually)"
    else
        echo
        echo "=== Bootstrapping missing .venv ==="
        uv venv --python 3.12 "$VENV" 2>/dev/null \
            || uv venv --python 3.12 --clear "$VENV" 2>/dev/null \
            || uv venv --clear "$VENV" 2>/dev/null \
            || { rm -rf "$VENV"; echo "  ⚠ could not create $VENV (create manually: uv venv $VENV)"; }
        if [ -d "$VENV" ]; then
            uv pip install --python "$VENV" -r "$TEMPLATE_ROOT/templates/deps/core.txt" -q 2>/dev/null \
                && echo "  ✓ core deps installed" \
                || echo "  ⚠ core deps failed (source $VENV/bin/activate && uv pip install sympy matplotlib certifi)"
            uv pip install --python "$VENV" -r "$TEMPLATE_ROOT/templates/deps/ssj.txt" -q 2>/dev/null \
                && echo "  ✓ ssj deps installed" \
                || echo "  ⚠ ssj deps skipped (numba build issue; non-fatal — ssj skill only)"
            for ext in "${EXTENSIONS[@]}"; do
                _extdeps="$TEMPLATE_ROOT/extensions/$ext/deps.txt"
                [ -f "$_extdeps" ] || continue
                uv pip install --python "$VENV" -r "$_extdeps" -q 2>/dev/null \
                    && echo "  ✓ $ext deps installed" \
                    || echo "  ⚠ $ext deps failed (source $VENV/bin/activate && uv pip install -r extensions/$ext/deps.txt)"
            done
        fi
    fi
fi

# ── Refresh manifest in target (preserve original deploy_date + fingerprint) ──
if [ "$DRY_RUN" = "0" ]; then
    if [ -f "$MANIFEST" ]; then
        # Update template_version + last_updated; sync deployment selectors
        # (mode, extensions) from the fresh deploy so that an --override on
        # this run is reflected in the persisted manifest. Anything not
        # listed here passes through verbatim from the existing manifest
        # (e.g. deploy_fingerprint, deploy_date — original deploy metadata).
        # variant cannot be overridden mid-life on a deployed project, so
        # it's not synced; if it ever can, add `.variant = (input | .variant)`.
        # Bind NEW_MANIFEST once via `input as $new`; each bare `input` call
        # consumes one file from the argv list, so reusing `(input | .X)` four
        # times would try to read four files. The slurp pattern below reads
        # NEW_MANIFEST once and lets us pull multiple fields from it.
        jq --arg v "$NEW_VERSION" --arg d "$(date -u +%Y-%m-%d)" \
           'input as $new
            | .template_version = $v
            | .last_updated = $d
            | .mode = $new.mode
            | .extensions = $new.extensions
            | .flags = $new.flags
            | .infrastructure = $new.infrastructure' \
           "$MANIFEST" "$NEW_MANIFEST" > "$MANIFEST.tmp" && mv "$MANIFEST.tmp" "$MANIFEST"
    else
        # No prior manifest — adopt the fresh manifest but blank deploy_fingerprint
        # (we don't know the original UUID; user can copy it from paper/arpipeline.sty if needed).
        jq --arg d "$(date -u +%Y-%m-%d)" \
           '.deploy_fingerprint = "(unknown — pre-manifest deploy)" | .last_updated = $d' \
           "$NEW_MANIFEST" > "$MANIFEST"
    fi
    echo
    echo "  ✓ manifest updated: template_version $OLD_VERSION → $NEW_VERSION"
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
