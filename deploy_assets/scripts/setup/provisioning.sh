#!/usr/bin/env bash
# Host-local Python environment and dependency provisioning for setup.sh.
#
# Provisioned paths live under the gitignored .venv and are intentionally not
# deployment-manifest infrastructure. update.sh owns the corresponding refresh
# and missing-venv bootstrap behavior for existing projects.

setup_python_environment() {
    local _venv_sp
    # The deployed pipeline (and agent-generated code) call a bare `python3`.
    # Give every production project a pinned environment rather than depending
    # on the host's ambient interpreter. Local assembly is filesystem-only.
    if [ "$LOCAL" = "0" ]; then
        # `--clear` makes retries idempotent after a partial first attempt.
        uv venv --python 3.12 "$P/.venv" 2>/dev/null \
            || uv venv --python 3.12 --clear "$P/.venv" 2>/dev/null \
            || uv venv --clear "$P/.venv" 2>/dev/null \
            || { rm -rf "$P/.venv"; echo "  ⚠ could not create $P/.venv — create it manually (uv venv $P/.venv) before launching"; }
    fi

    # Dep list is single-sourced in templates/deps/core.txt (also read by
    # update.sh). A failed venv creation yields only its warning, not a second
    # doomed install attempt.
    if [ "$LOCAL" = "0" ] && [ -d "$P/.venv" ]; then
        uv pip install --python "$P/.venv" -r "$TEMPLATE_ROOT/templates/deps/core.txt" -q 2>/dev/null \
            || echo "Note: core deps failed; install manually: source $P/.venv/bin/activate && uv pip install sympy matplotlib certifi"
    fi

    # Bare load_dotenv() asserts in python-dotenv's find_dotenv() when Python
    # runs from stdin. Install the stdin-safe guard as a module + .pth. It is
    # host-local, gitignored state and therefore never manifest-managed.
    if [ "$LOCAL" = "0" ] && [ -d "$P/.venv" ]; then
        _venv_sp="$("$P/.venv/bin/python3" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])' 2>/dev/null)"
        if [ -n "$_venv_sp" ] && [ -d "$_venv_sp" ]; then
            cp "$TEMPLATE_ROOT/templates/utils/pipeline_dotenv_guard.py" "$_venv_sp/_pipeline_dotenv_guard.py"
            printf 'import _pipeline_dotenv_guard\n' > "$_venv_sp/_pipeline_dotenv_guard.pth"
        else
            echo "  ⚠ could not locate venv site-packages — dotenv stdin guard not installed"
        fi
    fi
}

provision_ssj_dependencies() {
    # sequence-jacobian is non-fatal: numba can be finicky to build, and the
    # package declares no dependencies, so deps.txt pins compatible numerics.
    if [ "$LOCAL" = "0" ] && [ -d "$P/.venv" ]; then
        uv pip install --python "$P/.venv" -r "$TEMPLATE_ROOT/templates/deps/ssj.txt" -q 2>/dev/null \
            || echo "  ⚠ sequence-jacobian install failed (likely a numba build issue). The ssj skill will not work until you run: source $P/.venv/bin/activate && uv pip install sequence-jacobian numpy scipy 'numba>=0.59'"
    fi
}

provision_extension_dependencies() {
    local ext="$1"
    [ "$LOCAL" = "0" ] && [ -d "$P/.venv" ] || return 0
    case "$ext" in
        theory_llm)
            uv pip install --python "$P/.venv" -r "$TEMPLATE_ROOT/extensions/theory_llm/deps.txt" -q 2>/dev/null \
                || echo "Note: theory_llm deps failed; install manually: source $P/.venv/bin/activate && uv pip install openai python-dotenv"
            ;;
        empirical)
            uv pip install --python "$P/.venv" -r "$TEMPLATE_ROOT/extensions/empirical/deps.txt" -q 2>/dev/null \
                || echo "Note: empirical deps failed; install manually: source $P/.venv/bin/activate && uv pip install $(grep -vE '^[[:space:]]*(#|$)' "$TEMPLATE_ROOT/extensions/empirical/deps.txt" | tr '\n' ' ')"
            ;;
        *)
            echo "Error: no dependency provisioning policy for extension '$ext'" >&2
            exit 1
            ;;
    esac
}
