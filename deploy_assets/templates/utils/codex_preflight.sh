# Codex CLI preflight checks. Sourced (not executed) by launch.sh's codex
# branch, by code/utils/agent_launcher/launch_agent.sh at every worker
# dispatch, and by code/utils/codex_math/codex_common.sh — one implementation
# for the codex-runtime orchestrator, its dispatched workers, and the
# Claude-runtime codex-math co-processor.

# codex_permission_profile_args <project-root-or-empty> <network:true|false>
#
# Populate CODEX_PERMISSION_PROFILE_ARGS with the one sandbox contract shared
# by the Codex orchestrator and its leaf workers. The broad ~/.cache grant is
# intentional: scientific and browser dependencies use package-specific cache
# paths that cannot be enumerated reliably. The narrower WRDS cache directory
# is read-only so released-client compatibility state cannot be cleared or
# replaced by an autonomous process. Permission-profile specificity (narrower
# read over broader write) is the mechanism; legacy writable_roots cannot
# express this carve-out.
codex_permission_profile_args() {
    local project_root="${1:-}" network="${2:-true}" git_root_key
    case "$network" in true|false) ;; *)
        echo "ERROR: invalid Codex permission-profile network value: $network" >&2
        return 2 ;;
    esac
    CODEX_PERMISSION_PROFILE_ARGS=(
        --strict-config
        -c 'default_permissions="zeropaper-pipeline"'
        -c 'permissions.zeropaper-pipeline.extends=":workspace"'
        -c 'permissions.zeropaper-pipeline.filesystem={":root"="read","~/.codex"="write","~/.codex/auth.json"="read","~/.codex/config.toml"="read","~/.codex/plugins"="read","~/.codex/skills"="read","~/.codex/rules"="read","~/.codex/packages"="read","~/.cache"="write","~/.cache/zeropaper/wrds"="read","~/.matplotlib"="write","~/Library/Caches"="write","~/.ssh"="deny","~/.aws"="deny","~/.claude"="deny"}'
        -c "permissions.zeropaper-pipeline.network.enabled=$network"
    )
    if [ -n "$project_root" ]; then
        git_root_key=$(/usr/bin/python3 -I -c \
            'import json,sys; print(json.dumps(sys.argv[1]))' \
            "$project_root/.git") || return 1
        CODEX_PERMISSION_PROFILE_ARGS+=(
            -c "permissions.zeropaper-pipeline.workspace_roots={$git_root_key=true}"
        )
    fi
}

# codex_permission_profile_preflight
# Permission profiles plus --ignore-user-config are the security boundary for
# broad-cache Codex exec sessions. Fail with an actionable version diagnostic
# instead of letting an older CLI silently fall back to a broad legacy root.
codex_permission_profile_preflight() {
    local ver maj min patch _vf _cpid _wpid
    _vf=$(mktemp "${TMPDIR:-/tmp}/codex_ver.XXXXXX" 2>/dev/null) || return 1
    codex --version >"$_vf" 2>/dev/null &
    _cpid=$!
    { sleep 10; kill "$_cpid" 2>/dev/null; } >/dev/null 2>&1 &
    _wpid=$!
    wait "$_cpid" 2>/dev/null || true
    kill "$_wpid" 2>/dev/null || true
    wait "$_wpid" 2>/dev/null || true
    ver=$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' "$_vf" | head -1) || true
    rm -f "$_vf"
    if [ -z "$ver" ]; then
        echo "ERROR: could not determine codex-cli version; >=0.147.0 is required for the pipeline permission profile" >&2
        return 1
    fi
    maj="${ver%%.*}"
    min="${ver#*.}"; min="${min%%.*}"
    patch="${ver##*.}"
    case "$maj$min$patch" in *[!0-9]*) return 1 ;; esac
    if [ "$maj" -eq 0 ] && { [ "$min" -lt 147 ] || \
            { [ "$min" -eq 147 ] && [ "$patch" -lt 0 ]; }; }; then
        echo "ERROR: codex-cli $ver is too old for safe broad-cache sandboxing; upgrade to >=0.147.0" >&2
        return 1
    fi
}

# codex_proxy_auth_preflight
# Warn (never fail) when the installed codex CLI is old enough to carry the
# Proxy-Authorization defect behind an authenticated proxy. codex-cli ≤0.144.x
# sends no Proxy-Authorization header on its HTTPS CONNECT tunnels, so behind
# an authenticated proxy every request — including the OAuth token refresh —
# dies transport-level ("error sending request for url", no HTTP status),
# which masquerades as an auth/login problem. Fixed in codex 0.146.0. Full
# diagnosis and the relay workaround live in the template repo's
# LIMITATIONS.md ("Codex behind authenticated proxies") — that file does not
# ship, so the warning below is self-contained. Warn-only on purpose: without
# an authenticated proxy, older versions work fine, and a version parse
# failure must never block a launch.
codex_proxy_auth_preflight() {
    local ver maj min proxy _vf _cpid _wpid
    # Bounded lookup: `codex --version` should be local and instant, but this
    # preflight runs in exactly the broken-network environments where a hung
    # binary is conceivable, and a diagnostic must never block a launch.
    # Portable watchdog (macOS ships no `timeout`). Output goes to a temp file,
    # NOT a command-substitution pipe: a hung codex's own children inherit a
    # pipe and keep it open past the kill, re-creating the hang; a file can't
    # be held open against the reader.
    _vf=$(mktemp "${TMPDIR:-/tmp}/codex_ver.XXXXXX" 2>/dev/null) || return 0
    codex --version >"$_vf" 2>/dev/null &
    _cpid=$!
    { sleep 10; kill "$_cpid" 2>/dev/null; } >/dev/null 2>&1 &
    _wpid=$!
    wait "$_cpid" 2>/dev/null || true
    kill "$_wpid" 2>/dev/null || true
    # Reap the killed watchdog so non-interactive bash doesn't print an
    # asynchronous "Terminated" job notice into the caller's output.
    wait "$_wpid" 2>/dev/null || true
    ver=$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' "$_vf" | head -1) || true
    rm -f "$_vf"
    [ -n "$ver" ] || return 0
    # Only relevant when the network path is an authenticated proxy
    # (credentials embedded in the proxy URL).
    proxy="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-${http_proxy:-${ALL_PROXY:-${all_proxy:-}}}}}}"
    case "$proxy" in
        *://*@*) ;;
        *) return 0 ;;
    esac
    maj="${ver%%.*}"
    min="${ver#*.}"; min="${min%%.*}"
    case "$maj$min" in *[!0-9]*) return 0 ;; esac
    if [ "$maj" -eq 0 ] && [ "$min" -lt 146 ]; then
        echo "WARNING: codex-cli $ver behind an authenticated proxy — versions ≤0.144.x send no" >&2
        echo "  Proxy-Authorization on HTTPS CONNECT, so every codex request (including the OAuth" >&2
        echo "  token refresh) fails transport-level with 'error sending request for url'." >&2
        echo "  Fix: upgrade codex to >=0.146.0. Stopgap: run a local forward proxy that injects" >&2
        echo "  Proxy-Authorization (Basic base64(user:pass) from the proxy URL credentials) into" >&2
        echo "  CONNECT requests, and point HTTPS_PROXY at it." >&2
    fi
    return 0
}
