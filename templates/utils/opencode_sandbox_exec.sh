#!/usr/bin/env bash
# Fail-closed adapter between OpenCode and Anthropic's standalone Sandbox
# Runtime. The SRT CLI insists on a domain allowlist, while this pipeline needs
# arbitrary research/data hosts. Its library API can apply only the filesystem
# boundary; opencode_sandbox_exec.mjs performs that explicit translation.
set -euo pipefail

[ "$#" -ge 2 ] || {
    echo "ERROR: OpenCode sandbox wrapper needs a policy and command" >&2
    exit 2
}

policy="$1"
shift
[ "$EUID" -ne 0 ] || {
    echo "ERROR: OpenCode sandbox does not support running as root" >&2
    exit 1
}
command -v node >/dev/null 2>&1 || {
    echo "ERROR: Node.js is unavailable (Anthropic Sandbox Runtime requires node >=20.11)" >&2
    exit 1
}

adapter_input="${BASH_SOURCE[0]}"
adapter_dir_logical="$(cd "$(dirname "$adapter_input")" && pwd -L)"
adapter_dir_physical="$(cd "$(dirname "$adapter_input")" && pwd -P)"
if [ -L "$adapter_input" ] || [ "$adapter_dir_logical" != "$adapter_dir_physical" ]; then
    echo "ERROR: OpenCode sandbox adapter path must not contain symlinks: $adapter_input" >&2
    exit 1
fi
if [ -L "$policy" ] || [ ! -f "$policy" ]; then
    echo "ERROR: OpenCode sandbox policy must be a regular non-symlink: $policy" >&2
    exit 1
fi
if [ -L "$HOME/.codex" ]; then
    echo "ERROR: OpenCode sandbox protected path must not be a symlink: $HOME/.codex" >&2
    exit 1
elif [ -e "$HOME/.codex" ] && [ ! -d "$HOME/.codex" ]; then
    echo "ERROR: OpenCode sandbox protected path is not a directory: $HOME/.codex" >&2
    exit 1
fi

# SRT's Linux bwrap backend resolves filesystem paths when the sandbox starts
# and cannot grant/deny a path that appears later. Materialize every expected
# OpenCode/cache write root and both protected credential directories first.
# Existing paths and permissions are left untouched.
for runtime_dir in \
    "$HOME/.cache" \
    "$HOME/Library/Caches" \
    "$HOME/.matplotlib" \
    "$HOME/.codex"
do
    mkdir -p "$runtime_dir" || {
        echo "ERROR: cannot prepare OpenCode sandbox write path: $runtime_dir" >&2
        exit 1
    }
done
project_root="$(pwd -P)"
project_log="$project_root/process_log"
if [ -L "$project_log" ] || { [ -e "$project_log" ] && [ ! -d "$project_log" ]; }; then
    echo "ERROR: OpenCode process_log must be a real directory: $project_log" >&2
    exit 1
fi
mkdir -p "$project_log"
if [ "$(cd "$project_log" && pwd -P)" != "$project_log" ]; then
    echo "ERROR: OpenCode process_log did not resolve inside the project: $project_log" >&2
    exit 1
fi
project_runtime="$project_log/.opencode-runtime"
if [ -L "$project_runtime" ]; then
    echo "ERROR: OpenCode project runtime path must not be a symlink: $project_runtime" >&2
    exit 1
fi
mkdir -p "$project_runtime/data" "$project_runtime/state" || {
    echo "ERROR: cannot prepare project-scoped OpenCode runtime state: $project_runtime" >&2
    exit 1
}
if [ "$(cd "$project_runtime" && pwd -P)" != "$project_runtime" ]; then
    echo "ERROR: OpenCode project runtime did not resolve in place: $project_runtime" >&2
    exit 1
fi

for protected_dir in \
    "$HOME/.ssh" "$HOME/.aws" "$HOME/.claude" \
    "$HOME/.codex/plugins" "$HOME/.codex/skills" "$HOME/.codex/rules" "$HOME/.codex/packages"
do
    if [ -L "$protected_dir" ]; then
        echo "ERROR: OpenCode sandbox protected path must not be a symlink: $protected_dir" >&2
        exit 1
    elif [ ! -e "$protected_dir" ]; then
        mkdir -m 700 "$protected_dir" || {
            echo "ERROR: cannot prepare OpenCode sandbox protected path: $protected_dir" >&2
            exit 1
        }
    elif [ ! -d "$protected_dir" ]; then
        echo "ERROR: OpenCode sandbox protected path is not a directory: $protected_dir" >&2
        exit 1
    fi
done
for protected_file in "$HOME/.codex/auth.json" "$HOME/.codex/config.toml"; do
    if [ -L "$protected_file" ]; then
        echo "ERROR: OpenCode sandbox protected path must not be a symlink: $protected_file" >&2
        exit 1
    elif [ ! -e "$protected_file" ]; then
        if [ "$protected_file" = "$HOME/.codex/auth.json" ]; then
            (umask 077 && printf '{}\n' > "$protected_file")
        else
            (umask 077 && : > "$protected_file")
        fi || {
            echo "ERROR: cannot prepare OpenCode sandbox protected path: $protected_file" >&2
            exit 1
        }
    elif [ ! -f "$protected_file" ]; then
        echo "ERROR: OpenCode sandbox protected path is not a regular file: $protected_file" >&2
        exit 1
    fi
    node -e '
const fs = require("fs");
const info = fs.lstatSync(process.argv[1]);
if (!info.isFile() || info.nlink !== 1) process.exit(1);
' "$protected_file" || {
        echo "ERROR: OpenCode sandbox protected file has alternate hard links: $protected_file" >&2
        exit 1
    }
done

srt_bin="$(command -v srt || true)"
[ -n "$srt_bin" ] || {
    echo "ERROR: Anthropic Sandbox Runtime is unavailable (install @anthropic-ai/sandbox-runtime)" >&2
    exit 1
}
srt_real="$(node -e 'process.stdout.write(require("fs").realpathSync(process.argv[1]))' "$srt_bin")"
srt_package="$(cd "$(dirname "$srt_real")/.." && pwd -P)"
runner="$(cd "$(dirname "$0")" && pwd -P)/opencode_sandbox_exec.mjs"
[ -f "$srt_package/package.json" ] && [ -f "$runner" ] && [ ! -L "$runner" ] || {
    echo "ERROR: cannot locate the Anthropic Sandbox Runtime library or OpenCode adapter" >&2
    exit 1
}

exec node "$runner" "$policy" "$srt_package" "$@"
