#!/usr/bin/env bash
# Host-local Python environment and dependency provisioning for setup.sh.
#
# Provisioned paths live under the gitignored .venv and are intentionally not
# deployment-manifest infrastructure. update.sh deliberately never executes or
# mutates this agent-writable environment; dependency changes require a fresh setup.

setup_python_environment() {
    local _venv_sp
    # The deployed pipeline (and agent-generated code) call a bare `python3`.
    # Give every production project a pinned environment rather than depending
    # on the host's ambient interpreter. Local assembly is filesystem-only.
    if [ "$ASSEMBLE_ONLY" = "0" ]; then
        # `--clear` makes retries idempotent after a partial first attempt.
        "$SETUP_TOOL_UV" venv --python 3.12 "$P/.venv" 2>/dev/null \
            || "$SETUP_TOOL_UV" venv --python 3.12 --clear "$P/.venv" 2>/dev/null \
            || "$SETUP_TOOL_UV" venv --clear "$P/.venv" 2>/dev/null \
            || { rm -rf "$P/.venv"; echo "  ⚠ could not create $P/.venv — create it manually (uv venv $P/.venv) before launching"; }
    fi

    # Dependency inputs are copied into manifest-owned deployment paths before
    # provisioning. setup.sh installs from the exact verified bytes represented
    # by the deployment manifest.
    if [ "$ASSEMBLE_ONLY" = "0" ] && [ -d "$P/.venv" ]; then
        "$SETUP_TOOL_UV" pip install --python "$P/.venv" -r "$P/.arpipeline/update_inputs/deps/core.txt" -q 2>/dev/null \
            || echo "Note: core deps failed; install manually: source $P/.venv/bin/activate && uv pip install sympy matplotlib certifi"
    fi

    # Bare load_dotenv() asserts in python-dotenv's find_dotenv() when Python
    # runs from stdin. Install the stdin-safe guard as a module + .pth. It is
    # host-local, gitignored state; its verified source is manifest-managed.
    if [ "$ASSEMBLE_ONLY" = "0" ] && [ -d "$P/.venv" ]; then
        _venv_sp="$("$P/.venv/bin/python3" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])' 2>/dev/null)"
        if [ -n "$_venv_sp" ] && [ -d "$_venv_sp" ]; then
            cp "$P/.arpipeline/update_inputs/pipeline_dotenv_guard.py" "$_venv_sp/_pipeline_dotenv_guard.py"
            printf 'import _pipeline_dotenv_guard\n' > "$_venv_sp/_pipeline_dotenv_guard.pth"
        else
            echo "  ⚠ could not locate venv site-packages — dotenv stdin guard not installed"
        fi
    fi
}

provision_ssj_dependencies() {
    # sequence-jacobian is non-fatal: numba can be finicky to build, and the
    # package declares no dependencies, so deps.txt pins compatible numerics.
    if [ "$ASSEMBLE_ONLY" = "0" ] && [ -d "$P/.venv" ]; then
        "$SETUP_TOOL_UV" pip install --python "$P/.venv" -r "$P/.arpipeline/update_inputs/deps/ssj.txt" -q 2>/dev/null \
            || echo "  ⚠ sequence-jacobian install failed (likely a numba build issue). The ssj skill will not work until you run: source $P/.venv/bin/activate && uv pip install sequence-jacobian numpy scipy 'numba>=0.59'"
    fi
}

provision_extension_dependencies() {
    local ext="$1"
    [ "$ASSEMBLE_ONLY" = "0" ] && [ -d "$P/.venv" ] || return 0
    case "$ext" in
        theory_llm)
            "$SETUP_TOOL_UV" pip install --python "$P/.venv" -r "$P/.arpipeline/update_inputs/deps/extensions/theory_llm.txt" -q 2>/dev/null \
                || echo "Note: theory_llm deps failed; install manually: source $P/.venv/bin/activate && uv pip install openai anthropic python-dotenv"
            ;;
        empirical)
            "$SETUP_TOOL_UV" pip install --python "$P/.venv" -r "$P/.arpipeline/update_inputs/deps/extensions/empirical.txt" -q 2>/dev/null \
                || echo "Note: empirical deps failed; install manually: source $P/.venv/bin/activate && uv pip install -r $P/.arpipeline/update_inputs/deps/extensions/empirical.txt"
            ;;
        *)
            echo "Error: no dependency provisioning policy for extension '$ext'" >&2
            exit 1
            ;;
    esac
}
