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

# SRT resolves policy paths at sandbox creation. Validate every component and
# reject symlinks before granting an external writable root; broad-cache
# deployments predating v5 could otherwise redirect one to WRDS protected state.
node - "$HOME" <<'JS'
const fs = require("fs");
const path = require("path");
const home = process.argv[2];
const expectedUid = typeof process.getuid === "function" ? process.getuid() : null;
function ensure(parts) {
  let current = home;
  for (const component of parts) {
    current = path.join(current, component);
    if (!fs.existsSync(current)) fs.mkdirSync(current, {mode: 0o700});
    const info = fs.lstatSync(current);
    if (!info.isDirectory() || info.isSymbolicLink() ||
        (expectedUid !== null && info.uid !== expectedUid) || (info.mode & 0o022)) {
      throw new Error(`unsafe OpenCode sandbox writable root: ${current}`);
    }
    const fd = fs.openSync(current,
      fs.constants.O_RDONLY | fs.constants.O_DIRECTORY | (fs.constants.O_NOFOLLOW || 0));
    const opened = fs.fstatSync(fd);
    fs.closeSync(fd);
    if (opened.dev !== info.dev || opened.ino !== info.ino) {
      throw new Error(`OpenCode sandbox root changed during validation: ${current}`);
    }
  }
}
for (const parts of [
  [".codex"], [".matplotlib"], ["Library", "Caches"],
  ...["uv", "pip", "matplotlib", "fontconfig", "gdown", "huggingface",
      "torch", "ms-playwright", "opencode"].map(name => [".cache", name]),
]) ensure(parts);
JS
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

zeropaper_cache_parent="$HOME/.cache/zeropaper"
if [ -L "$zeropaper_cache_parent" ]; then
    echo "ERROR: OpenCode sandbox protected path must not have a symlinked parent: $zeropaper_cache_parent" >&2
    exit 1
elif [ ! -e "$zeropaper_cache_parent" ]; then
    mkdir -m 700 "$zeropaper_cache_parent" || {
        echo "ERROR: cannot prepare OpenCode sandbox protected parent: $zeropaper_cache_parent" >&2
        exit 1
    }
elif [ ! -d "$zeropaper_cache_parent" ]; then
    echo "ERROR: OpenCode sandbox protected parent is not a directory: $zeropaper_cache_parent" >&2
    exit 1
fi

for protected_dir in \
    "$HOME/.cache/zeropaper/wrds" \
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
