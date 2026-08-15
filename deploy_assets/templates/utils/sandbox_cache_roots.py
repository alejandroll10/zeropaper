#!/usr/bin/env python3
"""Materialize and no-follow validate external Codex/Claude/Grok write roots."""

import os
import stat


FLAGS = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
         getattr(os, "O_NOFOLLOW", 0))


def checked_open(path, label):
    try:
        fd = os.open(path, FLAGS)
    except OSError as exc:
        raise SystemExit(f"ERROR: unsafe sandbox {label} {path}: {exc}")
    info = os.fstat(fd)
    if (not stat.S_ISDIR(info.st_mode) or
            (hasattr(os, "getuid") and info.st_uid != os.getuid())):
        os.close(fd)
        raise SystemExit(
            f"ERROR: sandbox {label} must be a same-owner real directory: "
            f"{path}")
    return fd


def ensure(parent_fd, parent_path, name):
    try:
        os.mkdir(name, 0o700, dir_fd=parent_fd)
    except FileExistsError:
        pass
    path = os.path.join(parent_path, name)
    try:
        fd = os.open(name, FLAGS, dir_fd=parent_fd)
    except OSError as exc:
        raise SystemExit(f"ERROR: unsafe sandbox writable root {path}: {exc}")
    info = os.fstat(fd)
    if (not stat.S_ISDIR(info.st_mode) or
            (hasattr(os, "getuid") and info.st_uid != os.getuid())):
        os.close(fd)
        raise SystemExit(
            f"ERROR: sandbox writable root failed owner/type checks: {path}")
    return fd, path


def main():
    home = os.environ.get("HOME")
    if not home:
        raise SystemExit("ERROR: HOME must be set for sandbox-root validation")
    home_fd = checked_open(home, "home root")
    try:
        codex_fd, _ = ensure(home_fd, home, ".codex")
        os.close(codex_fd)
        mpl_fd, _ = ensure(home_fd, home, ".matplotlib")
        os.close(mpl_fd)
        library_fd, library_path = ensure(home_fd, home, "Library")
        try:
            caches_fd, _ = ensure(library_fd, library_path, "Caches")
            os.close(caches_fd)
        finally:
            os.close(library_fd)
        cache_fd, _ = ensure(home_fd, home, ".cache")
        os.close(cache_fd)
    finally:
        os.close(home_fd)


if __name__ == "__main__":
    main()
