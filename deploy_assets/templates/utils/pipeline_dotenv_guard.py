"""Installed into the project venv's site-packages as _pipeline_dotenv_guard.py,
activated by a companion _pipeline_dotenv_guard.pth (a one-line
`import _pipeline_dotenv_guard`, executed by the site module at every
interpreter startup).

A .pth file — NOT sitecustomize.py — because only one module can own the
`sitecustomize` name and Homebrew's Python ships its own in the stdlib
directory, which is earlier on sys.path than the venv's site-packages and
silently shadows anything we put there (observed: a venv copy was never
imported). .pth import lines run for every site-packages dir unconditionally.

Installed by setup.sh at venv creation. It lives inside the gitignored .venv,
which update.sh deliberately never executes or mutates; a changed guard
therefore requires a fresh deployment.

WHY THIS EXISTS: python-dotenv's find_dotenv() locates .env by walking the
call stack for the first frame whose filename exists on disk. When the
interpreter runs from stdin — `python - <<'PY'` heredocs, the natural shape of
agent-written ad-hoc checks — every frame's filename is '<stdin>', the walk
runs off the top of the stack, and `assert frame.f_back is not None` raises
AssertionError (python-dotenv 1.2.2, dotenv/main.py). Python >= 3.11 sets
__main__.__file__ = '<stdin>', so dotenv's interactive-session detection
(which would fall back to cwd) misses too. Observed in production at Stage 0
data inventory (2026-07-12): the assert fired *before any credential was read*
and initially presented as a data-source failure, costing a debugger cycle.

The wrapper retries with usecwd=True, i.e. "search upward from the current
directory" — correct here because pipeline shells always run from the project
root, where .env lives. Imported modules (code/utils/*.py) are unaffected:
their frames are real files, so the original resolution path succeeds and the
except branch never runs. `python -c` was never affected (no __main__.__file__
-> dotenv already falls back to cwd).

No dotenv in the venv -> clean no-op (the ImportError branch). A *failure to
patch* an installed dotenv, by contrast, warns on stderr: silence there would
mean the AssertionError this file exists to fix quietly returns when a future
python-dotenv reshapes its internals, with no signal the guard went inert.
"""

try:
    import dotenv as _dotenv
    import dotenv.main as _dotenv_main
except ImportError:
    pass
else:
    try:
        # Re-import in the same process (importlib.reload, a second .pth
        # line) must not re-wrap the wrapper: `_find_dotenv` is a late-bound
        # global, so wrapping twice would make the wrapper call itself.
        if not getattr(_dotenv_main.find_dotenv, "_pipeline_stdin_safe", False):
            _find_dotenv = _dotenv_main.find_dotenv

            # Signature mirrors python-dotenv 1.x find_dotenv(). Keyword-
            # explicit so a positional usecwd from a caller can't collide
            # with the retry override.
            def _find_dotenv_stdin_safe(
                filename=".env", raise_error_if_not_found=False, usecwd=False
            ):
                try:
                    return _find_dotenv(filename, raise_error_if_not_found, usecwd)
                except AssertionError:
                    # Stack walk found no on-disk caller (stdin/heredoc):
                    # search from the current directory instead.
                    return _find_dotenv(filename, raise_error_if_not_found, True)

            _find_dotenv_stdin_safe._pipeline_stdin_safe = True

            # load_dotenv() resolves `find_dotenv` from dotenv.main's globals
            # at call time, so patching the module attribute covers the
            # bare-load_dotenv path; the top-level alias covers direct
            # `from dotenv import find_dotenv` users.
            _dotenv_main.find_dotenv = _find_dotenv_stdin_safe
            _dotenv.find_dotenv = _find_dotenv_stdin_safe
    except Exception as _exc:  # noqa: BLE001 — must never break interpreter start
        import sys as _sys

        print(
            f"[pipeline_dotenv_guard] could not patch python-dotenv ({_exc!r}); "
            "bare load_dotenv() may fail from stdin heredocs",
            file=_sys.stderr,
        )
