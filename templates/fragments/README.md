# Shared rule fragments

Single-source blocks of agent-body rule text that would otherwise be
hand-copied across many agent bodies (issue #167).

**Usage.** In any agent body (base `templates/agent_bodies/shared/*.md`,
variant `*-core.md`, or extension `extensions/*/agent_bodies/**/*.md`), write:

```
{{> fragment_id }}
```

At assembly time `scripts/agent_body_loader.py` inlines
`templates/fragments/fragment_id.md` in place of the directive. Resolution
happens **before** vocab substitution, so a fragment may itself carry
`{{VOCAB_KEY}}` placeholders that resolve against the calling agent's vocab
(e.g. `{{MECHANISM_TERM}}`). Includes may nest (a fragment including another);
cycles and missing fragments fail loud at setup time.

**Build-time only.** Fragments are inlined into the assembled agent files; the
`templates/fragments/` directory is never copied into a deployed project, so it
is intentionally absent from the deployment manifest.

**This directory does not include `README.md` as a fragment** — the `.md`
basename is the fragment id, but `{{> README }}` would never be written (the
include id pattern is lowercase and no body references it).
