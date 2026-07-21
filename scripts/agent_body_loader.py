"""Shared body loader for the three runtime agent assemblers.

Resolves an agent body from either a shared-bodies dir (as `{id}-core.md`)
or the variant bodies dir (as `{id}.md`), and optionally applies variant
vocabulary substitution for `{{KEY}}` placeholders.

Both `shared_bodies_dirs` and the vocab argument accept either a single path
(legacy) or a list. Lists are processed in order so a `--mode` overlay can
shadow a base shared-bodies entry per-agent (first match wins) and a vocab
overlay can override base vocab keys (later layers win on duplicates).
"""
import json
import re
from pathlib import Path

VOCAB_KEY_PATTERN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")

# Fragment-include directive: `{{> fragment_id }}` (lowercase id, optional
# surrounding whitespace). Disjoint from VOCAB_KEY_PATTERN, which requires an
# uppercase leading letter and forbids `>`, so the two never collide. Includes
# are resolved *before* vocab substitution, so a fragment may itself carry
# `{{VOCAB_KEY}}` placeholders that resolve against the calling agent's vocab.
INCLUDE_PATTERN = re.compile(r"\{\{>\s*([a-z0-9][a-z0-9_-]*)\s*\}\}")

# Single-source rule fragments live here, resolved relative to this loader so
# every assembler (base + extensions, all three runtimes) picks up the same
# directory with no per-call-site wiring. Build-time only — fragments are
# inlined at assembly, never copied into deployed projects.
DEFAULT_FRAGMENTS_DIR = Path(__file__).resolve().parent.parent / "templates" / "fragments"

# Depth backstop for nested/cyclic includes (a fragment including a fragment).
_MAX_INCLUDE_DEPTH = 16


def load_vocab(vocab_paths):
    """Load and merge one or more vocab files.

    `vocab_paths` may be None, a single path string (legacy), or a list of
    paths. For lists, files are loaded in order and shallowly merged with
    later layers overriding earlier ones — i.e. the last entry wins on
    duplicate keys. Comment keys (e.g. `_comment_*`) flow through unchanged
    because `_apply_vocab` only consumes keys that appear as `{{KEY}}` in a
    body, so unused keys are silently ignored at substitution time.

    Returns None when there are no paths to load.
    """
    if vocab_paths is None:
        return None
    if isinstance(vocab_paths, str):
        vocab_paths = [vocab_paths]
    if not vocab_paths:
        return None

    merged = {}
    for path in vocab_paths:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"Vocab file not found: {path}. "
                f"Either create it (variant vocab.json) or omit --vocab."
            )
        merged.update(json.loads(p.read_text()))
    return merged


def _resolve_includes(body, fragments_dir, source, _stack=None):
    """Inline every `{{> fragment_id }}` from `fragments_dir/{id}.md`.

    Resolves recursively so a fragment may include another fragment. A
    per-branch `_stack` catches include cycles; `_MAX_INCLUDE_DEPTH` is a hard
    backstop. A missing fragment file raises FileNotFoundError with a pointer to
    the body/fragment that referenced it, matching the fail-loud contract of the
    rest of this module. Leading/trailing blank lines are trimmed from each
    fragment so an include on its own line slots in without adding blank lines.
    """
    if _stack is None:
        _stack = ()
    if len(_stack) > _MAX_INCLUDE_DEPTH:
        raise RecursionError(
            f"Fragment include depth exceeded {_MAX_INCLUDE_DEPTH} at {source}. "
            f"Include chain: {' -> '.join(_stack)}. Likely a cycle."
        )

    frag_dir = Path(fragments_dir)

    def replace(match):
        frag_id = match.group(1)
        if frag_id in _stack:
            raise RecursionError(
                f"Fragment include cycle in {source}: "
                + " -> ".join((*_stack, frag_id))
            )
        frag_path = frag_dir / f"{frag_id}.md"
        if not frag_path.exists():
            raise FileNotFoundError(
                f"Fragment '{frag_id}' referenced by {source} not found at "
                f"{frag_path}. Create the fragment or fix the {{{{> {frag_id} }}}} directive."
            )
        text = frag_path.read_text().strip("\n")
        # Recurse so nested includes inside the fragment resolve too.
        return _resolve_includes(text, fragments_dir, frag_path, (*_stack, frag_id))

    return INCLUDE_PATTERN.sub(replace, body)


def load_body(agent_id, bodies_dirs, shared_bodies_dirs=None, vocab=None,
              fragments_dir=None):
    """Return the body text for `agent_id` with optional vocab substitution.

    Both `bodies_dirs` and `shared_bodies_dirs` may be a single path string
    (legacy) or a list. Lookup order:
      1. For each entry in `shared_bodies_dirs` (in order),
         `{entry}/{agent_id}-core.md`. First match wins.
      2. For each entry in `bodies_dirs` (in order),
         `{entry}/{agent_id}.md`. First match wins.

    The list form lets `setup.sh` pass a `--mode` overlay dir before the base
    dir on either tier:
      - Variant agent overrides (whose canonical body lives at
        `templates/agent_bodies/shared/{id}-core.md` and is composed with a
        variant vocab) live under `shared_bodies_dirs` as `{id}-core.md`.
      - Shared agent overrides (whose canonical body lives at
        `templates/agent_bodies/shared/{id}.md` with no vocab composition)
        live under `bodies_dirs` as `{id}.md`.
    Both kinds can coexist in the same mode-overlay dir without colliding —
    the suffix discriminates them.

    Before vocab substitution, every `{{> fragment_id }}` directive is inlined
    from `fragments_dir/{fragment_id}.md` (default: `templates/fragments/`,
    resolved relative to this loader so every assembler shares it with no
    per-call wiring). This single-sources rule blocks that would otherwise be
    hand-copied across many agent bodies. Includes resolve recursively and run
    *before* vocab, so a fragment may itself carry `{{VOCAB_KEY}}` placeholders.

    If `vocab` is provided, every `{{KEY}}` in the loaded body is replaced by
    `vocab[KEY]`. An unresolved key raises KeyError with a pointer to the
    source file, so drift between the core body and a variant vocab is caught
    at setup time rather than silently shipping a literal `{{KEY}}` to an
    agent.
    """
    if isinstance(bodies_dirs, (str, type(None))):
        bodies_dirs = [bodies_dirs] if bodies_dirs else []
    if shared_bodies_dirs is None:
        shared_bodies_dirs = []
    elif isinstance(shared_bodies_dirs, str):
        shared_bodies_dirs = [shared_bodies_dirs]

    source = None
    for sbd in shared_bodies_dirs:
        candidate = Path(sbd) / f"{agent_id}-core.md"
        if candidate.exists():
            source = candidate
            break
    if source is None:
        for bd in bodies_dirs:
            candidate = Path(bd) / f"{agent_id}.md"
            if candidate.exists():
                source = candidate
                break
    if source is None:
        searched = [f"{sbd}/{agent_id}-core.md" for sbd in shared_bodies_dirs]
        searched += [f"{bd}/{agent_id}.md" for bd in bodies_dirs]
        raise FileNotFoundError(
            f"Body not found for agent '{agent_id}'. Searched: "
            + ", ".join(searched)
        )
    body = source.read_text()
    # Inline shared fragments first so any `{{VOCAB_KEY}}` a fragment carries is
    # resolved by the single vocab pass below against the calling agent's vocab.
    if fragments_dir is None:
        fragments_dir = DEFAULT_FRAGMENTS_DIR
    body = _resolve_includes(body, fragments_dir, source)
    if vocab is not None:
        body = _apply_vocab(body, vocab, source)
    return body


def apply_mode_overrides(metadata, mode):
    """Merge an agent's per-mode metadata overrides over its base fields.

    Agent metadata may carry a `"modes"` key mapping a mode slug (underscored,
    e.g. "report", "empirical_first") to a dict of field overrides — the
    metadata twin of the `shared_modes/{mode}/` body overlays, used when a mode
    re-frames what an agent does (so its orchestrator-facing `description`
    matches the overlaid body, not the pipeline-native one). Returns a new dict
    with the matching mode's fields merged over the base and the `"modes"` key
    stripped, so it never renders into an assembled agent file. Call before
    apply_vocab_to_metadata so overridden strings get vocab substitution too.
    """
    if "modes" not in metadata:
        return metadata
    overrides = metadata.get("modes") or {}
    merged = {k: v for k, v in metadata.items() if k != "modes"}
    if mode:
        merged.update(overrides.get(mode, {}))
    return merged


def apply_vocab_to_metadata(metadata, vocab, source):
    """Substitute `{{KEY}}` in each string value of the metadata dict.

    Returns a new dict. Non-string values pass through unchanged. Unresolved
    keys raise KeyError (same fail-loud behavior as body substitution), so
    `{{DOMAIN}}` in a shared metadata file cannot silently ship unresolved.
    """
    if vocab is None:
        return metadata
    result = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            result[key] = _apply_vocab(value, vocab, f"{source}:{key}")
        else:
            result[key] = value
    return result


def _apply_vocab(body, vocab, source):
    missing = []

    def replace(match):
        key = match.group(1)
        if key not in vocab:
            missing.append(key)
            return match.group(0)
        return vocab[key]

    rendered = VOCAB_KEY_PATTERN.sub(replace, body)
    if missing:
        unique = sorted(set(missing))
        raise KeyError(
            f"Unresolved vocab key(s) in {source}: "
            + ", ".join(f"{{{{{k}}}}}" for k in unique)
            + ". Add them to the variant vocab.json."
        )
    return rendered
