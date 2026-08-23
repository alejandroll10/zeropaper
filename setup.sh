#!/usr/bin/python3 -I
"""Start setup through a clean environment before Bash can load startup code."""

import os
import stat
import sys


checkout_root = os.path.dirname(os.path.realpath(__file__))
coordinator = os.path.join(
    checkout_root, "deploy_assets", "scripts", "setup", "coordinator.sh"
)
try:
    coordinator_info = os.lstat(coordinator)
except OSError as error:
    raise SystemExit(f"Error: cannot inspect setup coordinator: {error}") from error
if (
    not stat.S_ISREG(coordinator_info.st_mode)
    or coordinator_info.st_nlink != 1
    or (
        coordinator_info.st_uid != os.geteuid()
        and coordinator_info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)
    )
):
    raise SystemExit(
        f"Error: setup coordinator must be one regular non-aliased file: {coordinator}"
    )

clean = {
    key: value
    for key, value in os.environ.items()
    if key
    not in {
        "BASH_ENV",
        "ENV",
        "BASHOPTS",
        "SHELLOPTS",
        "BASH_COMPAT",
        "POSIXLY_CORRECT",
        "VIRTUAL_ENV",
        "CONDA_PREFIX",
        "CONDA_DEFAULT_ENV",
        "CONDA_PROMPT_MODIFIER",
        "PIPENV_ACTIVE",
        "POETRY_ACTIVE",
        "CDPATH",
        "GLOBIGNORE",
        "ZEROPAPER_SETUP_CLEAN_SHELL",
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_NAMESPACE",
        "GIT_SHALLOW_FILE",
        "GIT_GRAFT_FILE",
        "GIT_REPLACE_REF_BASE",
        "GIT_CEILING_DIRECTORIES",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_TEMPLATE_DIR",
    }
    and not key.startswith("BASH_FUNC_")
    and not key.startswith("GIT_CONFIG_")
}
clean["GIT_NO_REPLACE_OBJECTS"] = "1"
clean["ZEROPAPER_SETUP_LAUNCH_ROOT"] = checkout_root
activation_roots = []
for key in ("VIRTUAL_ENV", "CONDA_PREFIX"):
    value = os.environ.get(key)
    if value:
        activation_roots.append((os.path.abspath(value), os.path.realpath(value)))


def path_is_unsafe(path):
    logical = os.path.abspath(path)
    physical = os.path.realpath(path)
    logical_parts = {part.lower() for part in logical.split(os.sep)}
    physical_parts = {part.lower() for part in physical.split(os.sep)}
    if {".venv", "venv"} & (logical_parts | physical_parts):
        return True
    def is_at_or_within_identity(candidate, ancestor):
        current = candidate
        while True:
            try:
                if os.path.samefile(current, ancestor):
                    return True
            except OSError:
                pass
            parent = os.path.dirname(current)
            if parent == current:
                return False
            current = parent

    for candidate in (logical, physical):
        try:
            if os.path.commonpath((candidate, checkout_root)) == checkout_root:
                return True
        except ValueError:
            pass
        if is_at_or_within_identity(candidate, checkout_root):
            return True
        for active_logical, active_physical in activation_roots:
            for active in (active_logical, active_physical):
                try:
                    if os.path.commonpath((candidate, active)) == active:
                        return True
                except ValueError:
                    pass
                if is_at_or_within_identity(candidate, active):
                    return True
    return False


provider_keys = {
    "uv": "ZEROPAPER_SETUP_TOOL_UV",
    "claude": "ZEROPAPER_SETUP_TOOL_CLAUDE",
    "gh": "ZEROPAPER_SETUP_TOOL_GH",
}
internal_handoff_keys = (
    "ZEROPAPER_SETUP_HANDOFF",
    "ZEROPAPER_SETUP_LIVE_ROOT",
    "ZEROPAPER_SETUP_SOURCE_DIGEST",
    "ZEROPAPER_SETUP_SNAPSHOT_ROOT",
)
if not all(os.environ.get(key) for key in internal_handoff_keys):
    for key in provider_keys.values():
        clean.pop(key, None)
    for tool, key in provider_keys.items():
        for raw in os.environ.get("PATH", "").split(os.pathsep):
            if not raw:
                continue
            directory = os.path.abspath(raw)
            candidate = os.path.join(directory, tool)
            if path_is_unsafe(directory) or path_is_unsafe(candidate):
                continue
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                clean[key] = os.path.realpath(candidate)
                break
# Core setup commands always resolve from OS directories first. Preserve later
# operator tool locations (uv/claude/gh), but never inherit an activated venv or
# a path inside the mutable template checkout.
path_entries = []
for raw in ["/usr/bin", "/bin", "/usr/sbin", "/sbin", *clean.get("PATH", "").split(os.pathsep)]:
    if not raw:
        continue
    logical = os.path.abspath(raw)
    physical = os.path.realpath(raw)
    if path_is_unsafe(logical):
        continue
    if physical not in path_entries and os.path.isdir(physical):
        path_entries.append(physical)
clean["PATH"] = os.pathsep.join(path_entries)
os.umask(0o022)
os.execve("/bin/bash", ["bash", coordinator, *sys.argv[1:]], clean)
