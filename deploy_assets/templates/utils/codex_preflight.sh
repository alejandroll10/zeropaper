# Codex CLI preflight checks. Sourced (not executed) by launch.sh's codex
# branch, by code/utils/agent_launcher/launch_agent.sh at every worker
# dispatch, and by code/utils/codex_math/codex_common.sh — one implementation
# for the codex-runtime orchestrator, its dispatched workers, and the
# Claude-runtime codex-math co-processor.

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
