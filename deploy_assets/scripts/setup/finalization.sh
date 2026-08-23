#!/usr/bin/env bash
# Git initialization, optional publication, and completion reporting.

setup_initialize_project_git() {
    [ "$ASSEMBLE_ONLY" = "0" ] || return 0
    SETUP_GIT_TEMPLATE_DIR="$(mktemp -d "$SETUP_TMP_ROOT/zeropaper-git-template.XXXXXX")"
    _setup_git_control init -q -b main --template="$SETUP_GIT_TEMPLATE_DIR"
    # Persist hook/attribute/fsmonitor neutrality for the later gh-driven push,
    # which cannot inherit `_setup_git_control`'s one-command config boundary.
    _setup_git_control config --local core.hooksPath /dev/null
    _setup_git_control config --local core.attributesFile /dev/null
    _setup_git_control config --local core.fsmonitor false
    _setup_git_control config --local commit.gpgSign false
}

_setup_git_control() {
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
        git -c "user.name=$SETUP_GIT_USER_NAME" \
            -c "user.email=$SETUP_GIT_USER_EMAIL" \
            -c core.hooksPath=/dev/null \
            -c core.attributesFile=/dev/null \
            -c core.fsmonitor=false \
            -c commit.gpgSign=false "$@"
}

_setup_print_update_attestation() {
    local -a update_command
    local extension update_launcher
    local update_launcher_source update_launcher_digest update_bootstrap
    update_launcher="$SOURCE_CHECKOUT_ROOT/update.sh"
    update_launcher_source="$SCRIPT_DIR/update.sh"
    update_launcher_digest="$(python3 -I - "$update_launcher_source" <<'PY'
import hashlib
import os
import stat
import sys

path = sys.argv[1]
fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit("update launcher is not one regular file")
digest = hashlib.sha256()
with os.fdopen(fd, "rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
print("sha256:" + digest.hexdigest())
PY
)"
    update_bootstrap='import hashlib, os, stat, sys
launcher, launcher_digest, *arguments = sys.argv[1:]
def verified_open(path, expected):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0))
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise SystemExit(f"attested updater input is not one regular file: {path}")
    digest = hashlib.sha256()
    chunks = []
    while True:
        chunk = os.read(fd, 1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        chunks.append(chunk)
    if "sha256:" + digest.hexdigest() != expected:
        raise SystemExit(f"attested updater bytes changed; rerun setup from a trusted snapshot: {path}")
    os.close(fd)
    return b"".join(chunks)
launcher_source = verified_open(launcher, launcher_digest)
sys.argv = [launcher, *arguments]
namespace = {"__name__": "__main__", "__file__": launcher}
exec(compile(launcher_source.decode("utf-8"), launcher, "exec"), namespace)'
    update_command=(
        /usr/bin/python3 -I -c "$update_bootstrap"
        "$update_launcher" "$update_launcher_digest" "$P"
        --source-digest "$SOURCE_CONTENT_DIGEST"
        --variant "$VARIANT"
    )
    if [ -n "$MODE" ]; then
        update_command+=(--mode "$MODE")
    else
        update_command+=(--no-mode)
    fi
    update_command+=(--clear-ext)
    for extension in "${EXTENSIONS[@]}"; do
        update_command+=(--ext "$extension")
    done
    [ "$SEEDED" = "1" ] && update_command+=(--seeded) || update_command+=(--no-seeded)
    [ "$FAITHFUL" = "1" ] && update_command+=(--faithful) || update_command+=(--no-faithful)
    [ "$MANUAL" = "1" ] && update_command+=(--manual) || update_command+=(--no-manual)
    [ "$LIGHT" = "1" ] && update_command+=(--light) || update_command+=(--no-light)
    [ "$HALT_ON_CORE_BYPASS" = "1" ] \
        && update_command+=(--halt-on-core-bypass) \
        || update_command+=(--no-halt-on-core-bypass)

    echo "Trusted update attestation (record this complete command outside the project):"
    printf '  '
    printf '%q ' "${update_command[@]}"
    printf '\n'
}

finalize_assemble_only_setup() {
    echo ""
    echo "=== Assembled CLAUDE.md ==="
    echo "Lines: $(wc -l < "$CLAUDE_MD_OUT")"
    REMAINING=$(grep -c '{{' "$CLAUDE_MD_OUT" 2>/dev/null || true)
    REMAINING="${REMAINING:-0}"
    echo "Placeholders remaining: $REMAINING"
    echo ""
    echo "=== Assembled AGENTS.md ==="
    echo "Lines: $(wc -l < "$AGENTS_MD_OUT")"
    AGENTS_REMAINING=$(grep -c '{{' "$AGENTS_MD_OUT" 2>/dev/null || true)
    AGENTS_REMAINING="${AGENTS_REMAINING:-0}"
    echo "Placeholders remaining: $AGENTS_REMAINING"
    echo ""
    echo "=== Assembled GEMINI.md ==="
    echo "Lines: $(wc -l < "$GEMINI_MD_OUT")"
    GEMINI_REMAINING=$(grep -c '{{' "$GEMINI_MD_OUT" 2>/dev/null || true)
    GEMINI_REMAINING="${GEMINI_REMAINING:-0}"
    echo "Placeholders remaining: $GEMINI_REMAINING"
    echo ""
    # The rendered fingerprint .sty is a sed-substitution target too; absent
    # in report mode, where no paper skeleton is installed.
    STY_OUT="$P/paper/arpipeline.sty"
    STY_REMAINING=0
    if [ -f "$STY_OUT" ]; then
        STY_REMAINING=$(grep -c '{{' "$STY_OUT" 2>/dev/null || true)
        STY_REMAINING="${STY_REMAINING:-0}"
        echo "=== Rendered paper/arpipeline.sty ==="
        echo "Placeholders remaining: $STY_REMAINING"
        echo ""
    fi
    echo "=== Agents ($CLAUDE_AGENTS_REL/) ==="
    ls -1 "$AGENTS_OUT/"
    echo ""
    echo "=== Codex Agents ($CODEX_AGENTS_REL/) ==="
    ls -1 "$CODEX_AGENTS_OUT/"
    echo ""
    echo "=== Gemini Agents ($GEMINI_AGENTS_REL/) ==="
    ls -1 "$GEMINI_AGENTS_OUT/"
    echo ""
    echo "=== Grok Agents ($GROK_AGENTS_REL/) ==="
    ls -1 "$GROK_AGENTS_OUT/"
    echo ""
    echo "=== OpenCode Agents ($OPENCODE_AGENTS_REL/) ==="
    ls -1 "$OPENCODE_AGENTS_OUT/"
    if [ -d "$OUT_DIR/$CLAUDE_SKILLS_REL" ]; then
        echo ""
        echo "=== Skills ($CLAUDE_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CLAUDE_SKILLS_REL/"
    fi
    if [ -d "$OUT_DIR/$CODEX_SKILLS_REL" ]; then
        echo ""
        echo "=== Codex Skills ($CODEX_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CODEX_SKILLS_REL/"
    fi
    echo ""
    echo "=== First 10 lines ==="
    head -10 "$CLAUDE_MD_OUT"
    echo ""
    echo "=== Domain section ==="
    grep -A 5 "^## Domain:" "$CLAUDE_MD_OUT" | head -8
    echo ""

    if [ "$REMAINING" -gt 0 ]; then
        echo "WARNING: $REMAINING unresolved placeholders:"
        grep '{{' "$CLAUDE_MD_OUT"
        exit 1
    elif [ "$AGENTS_REMAINING" -gt 0 ]; then
        echo "WARNING: $AGENTS_REMAINING unresolved placeholders:"
        grep '{{' "$AGENTS_MD_OUT"
        exit 1
    elif [ "$GEMINI_REMAINING" -gt 0 ]; then
        echo "WARNING: $GEMINI_REMAINING unresolved placeholders:"
        grep '{{' "$GEMINI_MD_OUT"
        exit 1
    elif [ "$STY_REMAINING" -gt 0 ]; then
        echo "WARNING: $STY_REMAINING unresolved placeholders in paper/arpipeline.sty:"
        grep '{{' "$STY_OUT"
        exit 1
    else
        echo "✓ All placeholders resolved"
    fi
    echo ""
    _setup_print_update_attestation
    echo ""
    echo "Assembly output at: $OUT_DIR/"
}

_setup_publish_project() {
    if [ "$PUBLISH" = "1" ]; then
        # Always suffix with the deployment fingerprint so the repository URL
        # identifies one deployment even when project basenames collide.
        PUBLISH_SUFFIX="${ARP_UUID:0:8}"
        PUBLISH_NAME="$(basename "$PROJECT_NAME")-${PUBLISH_SUFFIX}"
        echo "Publish requested: $PUBLISH_ORG/$PUBLISH_NAME ($PUBLISH_VISIBILITY)"

        if [ -z "$SETUP_TOOL_GH" ] || [ ! -x "$SETUP_TOOL_GH" ]; then
            echo "  ⚠ GitHub CLI (gh) not found. Repo remains local."
        elif ! "$SETUP_TOOL_GH" auth status >/dev/null 2>&1; then
            echo "  ⚠ GitHub CLI is not authenticated. Repo remains local."
        else
            gh_user=""
            membership_state=""
            if ! gh_user=$("$SETUP_TOOL_GH" api user --jq .login); then
                echo "  ⚠ Could not identify the authenticated GitHub user. Repo remains local."
            elif [ -z "$gh_user" ]; then
                echo "  ⚠ GitHub returned an empty authenticated-user login. Repo remains local."
            elif ! membership_state=$("$SETUP_TOOL_GH" api "orgs/$PUBLISH_ORG/memberships/$gh_user" --jq .state); then
                echo "  ⚠ Could not verify active membership in $PUBLISH_ORG. Repo remains local."
            elif [ "$membership_state" != "active" ]; then
                membership_state="${membership_state:-unknown}"
                echo "  ⚠ GitHub membership in $PUBLISH_ORG is $membership_state, not active. Repo remains local."
            else
                echo "Publishing to $PUBLISH_ORG/$PUBLISH_NAME ($PUBLISH_VISIBILITY)..."
                if "$SETUP_TOOL_GH" repo create "$PUBLISH_ORG/$PUBLISH_NAME" \
                       "--$PUBLISH_VISIBILITY" \
                       --source=. --remote=origin --push >/dev/null; then
                    echo "  ✓ Pushed to $PUBLISH_ORG/$PUBLISH_NAME"
                    echo "    (deployment fingerprint: $ARP_UUID)"
                else
                    echo "  ⚠ GitHub publication failed. The local commit is intact, but remote state may be partial."
                    echo "    Inspect https://github.com/$PUBLISH_ORG/$PUBLISH_NAME before retrying."
                fi
            fi
        fi
    else
        echo "Publishing skipped: local repository only (pass --publish to create and push a GitHub repository)."
    fi
}

_setup_print_completion() {
    echo ""
    echo "============================================"
    if [ "$MANUAL" = "1" ]; then
        echo "  Setup complete: $PROJECT_NAME ($VARIANT, manual mode)"
    elif [ "$MODE" = "report" ]; then
        echo "  Setup complete: $PROJECT_NAME ($VARIANT, --mode report)"
    else
        echo "  Setup complete: $PROJECT_NAME ($VARIANT)"
    fi
    echo "============================================"
    echo ""
    echo "  cd $PROJECT_NAME"
    echo ""
    echo "  # Activate the project venv first so the pipeline's python3 finds its deps:"
    echo "  source .venv/bin/activate"
    echo ""
    echo "Preferred: ./launch.sh <claude|codex|gemini|grok|opencode>   (activates the venv and applies each runtime's flags)"
    echo ""
    echo "Claude:"
    echo "  source .venv/bin/activate && claude --dangerously-skip-permissions"
    echo ""
    if [ "$MANUAL" = "1" ] || [ "$MODE" = "report" ]; then
        echo "Codex (manual/report deployments have no autonomous pipeline-state driver):"
        echo "  ./launch.sh codex --once   # interactive TUI; native subagents complete inside their spawning turn"
    else
        echo "Codex (headless driver loop; native subagents complete inside their spawning turn):"
        echo "  ./launch.sh codex          # add --tmux for a detached window; --once for a plain TUI"
    fi
    echo ""
    echo "Gemini:"
    echo "  source .venv/bin/activate && gemini --yolo"
    echo ""
    echo "Grok (reads the shared AGENTS.md; agents in .grok/agents/):"
    echo "  ./launch.sh grok           # per-project leader socket + venv python shims applied automatically"
    echo "  # Manual equivalent (run from the project root — the per-project --leader-socket is required"
    echo "  # when you run more than one grok project on this host: all grok clients share"
    echo "  # ~/.grok/leader.sock by default, and a second client on that socket TEARS DOWN the"
    echo "  # first session's in-flight turn):"
    echo "  source .venv/bin/activate && grok --sandbox pipeline --always-approve --leader-socket \"\$(pwd)/.grok/leader.sock\""
    echo "  # grok demotes the venv in its bash PATH (bare python3 = system python) — ./launch.sh grok"
    echo "  # installs transparent VIRTUAL_ENV shims in ~/.local/bin to fix this; manual launches need them too."
    echo "  # git push under grok's sandbox cannot use the macOS keychain; to enable pushes:"
    echo "  #   bash code/utils/setup_push_token.sh   (repo-scoped fine-grained PAT; otherwise commits stay local)"
    echo ""
    if [ "$MANUAL" = "1" ]; then
        echo "Manual mode — read the runtime doc for the agent and skill catalog, then drive."
    elif [ "$MODE" = "report" ]; then
        echo "Drop the submission to be refereed in submission/ (PDF or LaTeX source bundle), then say: \"run\""
        echo "  - core_report.md fans out the audit agents in parallel"
        echo "  - report-synthesizer aggregates them into report/referee_report.md"
        echo "  - report-reviewer must return a versioned CLEAN gate before completion"
        echo "  - one-shot; for a revised submission re-run setup.sh on a fresh folder"
    else
        echo "Then say: \"Run the pipeline.\""
    fi
    echo ""
    echo "Variant: $VARIANT"
    echo "Extensions: ${EXTENSIONS[*]:-none}"
    _setup_print_update_attestation
    if [ "$LIGHT" = "1" ]; then
        echo "Mode: light (cheapest tier throughout — subagents AND orchestrator: claude sonnet, codex gpt-5.6-luna, gemini flash; per-agent effort dropped)"
    fi
    if [ "$FAITHFUL" = "1" ]; then
        echo "Mode: faithful (the seed is a contract; the pipeline implements it as written)"
        echo "Drop your idea files in output/seed/ before launching"
        echo "Pipeline will extract a mechanism contract first, then triage entry-stage"
    elif [ "$SEEDED" = "1" ]; then
        echo "Seeded: drop your idea files in output/seed/ before launching"
        echo "Pipeline will triage seed maturity and enter at the appropriate stage"
    fi
    echo "Runtime permissions are pre-configured for Claude, Grok, and OpenCode ($OPENCODE_CONFIG_REL)"
    echo "(OpenCode's launcher wraps its server and Bash descendants in Anthropic Sandbox Runtime)"
}

finalize_production_setup() {
    # No cleanup/strip step: the project received build outputs only.
    if [ -f dashboard.html ]; then
        DASHBOARD_SUBTITLE="Autonomous $(python3 -I -c "import sys; print(sys.argv[1].title())" "$PAPER_TYPE") Generator"
        sed -i.bak "s|Autonomous Finance Theory Paper Generator|$DASHBOARD_SUBTITLE|" dashboard.html && rm -f dashboard.html.bak
    fi

    _setup_git_control add -A
    if [ "$MANUAL" = "1" ]; then
        _setup_git_control commit -m "setup: initialized ${VARIANT} variant toolkit (manual mode)" -q
    elif [ "$MODE" = "report" ]; then
        _setup_git_control commit -m "setup: initialized ${VARIANT} variant referee-report deployment" -q
    else
        _setup_git_control commit -m "setup: initialized ${VARIANT} variant pipeline" -q
    fi

    _setup_publish_project
    _setup_print_completion
}
