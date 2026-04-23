"""Shared body loader for the three runtime agent assemblers.

Resolves an agent body from either a shared-bodies dir (as `{id}-core.md`)
or the variant bodies dir (as `{id}.md`), and optionally applies variant
vocabulary substitution for `{{KEY}}` placeholders.
"""
import json
import re
from pathlib import Path

VOCAB_KEY_PATTERN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def load_vocab(vocab_path):
    if not vocab_path:
        return None
    path = Path(vocab_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Vocab file not found: {vocab_path}. "
            f"Either create it (variant vocab.json) or omit --vocab."
        )
    return json.loads(path.read_text())


def load_body(agent_id, bodies_dir, shared_bodies_dir=None, vocab=None):
    """Return the body text for `agent_id` with optional vocab substitution.

    Lookup order:
      1. `{shared_bodies_dir}/{agent_id}-core.md` (if `shared_bodies_dir` given)
      2. `{bodies_dir}/{agent_id}.md`

    If `vocab` is provided, every `{{KEY}}` in the loaded body is replaced by
    `vocab[KEY]`. An unresolved key raises KeyError with a pointer to the
    source file, so drift between the core body and a variant vocab is caught
    at setup time rather than silently shipping a literal `{{KEY}}` to an
    agent.
    """
    bodies_dir = Path(bodies_dir)
    source = None
    if shared_bodies_dir is not None:
        candidate = Path(shared_bodies_dir) / f"{agent_id}-core.md"
        if candidate.exists():
            source = candidate
    if source is None:
        source = bodies_dir / f"{agent_id}.md"
    body = source.read_text()
    if vocab is not None:
        body = _apply_vocab(body, vocab, source)
    return body


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
