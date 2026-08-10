#!/usr/bin/python3 -I
"""Start the updater without allowing Bash startup hooks to run first."""

import os
import stat
import sys


checkout_root = os.path.dirname(os.path.realpath(__file__))
coordinator = os.path.join(checkout_root, "scripts", "update_coordinator.sh")
try:
    coordinator_info = os.lstat(coordinator)
except OSError as error:
    raise SystemExit(f"Error: cannot inspect update coordinator: {error}") from error
if (
    not stat.S_ISREG(coordinator_info.st_mode)
    or coordinator_info.st_nlink != 1
    or (
        coordinator_info.st_uid != os.geteuid()
        and coordinator_info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)
    )
):
    raise SystemExit(
        f"Error: update coordinator must be one regular non-aliased file: {coordinator}"
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
        "CDPATH",
        "GLOBIGNORE",
        "VIRTUAL_ENV",
        "CONDA_PREFIX",
        "CONDA_DEFAULT_ENV",
        "CONDA_PROMPT_MODIFIER",
        "PIPENV_ACTIVE",
        "POETRY_ACTIVE",
    }
    and not key.startswith("BASH_FUNC_")
}
activation_roots = []
for key in ("VIRTUAL_ENV", "CONDA_PREFIX"):
    value = os.environ.get(key)
    if value:
        activation_roots.append((os.path.abspath(value), os.path.realpath(value)))


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


def path_is_activated_or_checkout(path):
    logical = os.path.abspath(path)
    physical = os.path.realpath(path)
    parts = {part.lower() for part in (*logical.split(os.sep), *physical.split(os.sep))}
    if {".venv", "venv"} & parts:
        return True
    for candidate in (logical, physical):
        if is_at_or_within_identity(candidate, checkout_root):
            return True
        for active_logical, active_physical in activation_roots:
            if is_at_or_within_identity(candidate, active_logical) \
                    or is_at_or_within_identity(candidate, active_physical):
                return True
    return False


safe_path = []
for raw in os.environ.get("PATH", "").split(os.pathsep):
    if not raw:
        continue
    physical = os.path.realpath(os.path.abspath(raw))
    if path_is_activated_or_checkout(raw) or not os.path.isdir(physical):
        continue
    if physical not in safe_path:
        safe_path.append(physical)
clean["PATH"] = os.pathsep.join(safe_path)
clean["ZEROPAPER_UPDATE_LAUNCH_ROOT"] = checkout_root
os.execve("/bin/bash", ["bash", coordinator, *sys.argv[1:]], clean)
