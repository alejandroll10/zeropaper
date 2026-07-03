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

## Deliberately NOT fragmented (documented so it isn't re-litigated)

The include mechanism inlines a *fixed* string; it cannot render one source
differently per call site. So text that merely *looks* duplicated but is
role- or mode-adapted must stay inline — fragmenting it would change behavior:

- **The substance-over-form leeway blocks and the multi-margin / union-thesis
  defenses** are intentionally verb- and verdict-specific per evaluator (scorer
  *scores*, referee *recommends*, self-attacker *attacks*, triager
  *downgrades*); only the byte-identical *atoms* inside them are fragmented
  (`archetype_list`, `policy_map_axes`).
- **The citation-discipline block** lives in the referee family only (the three
  referees + their `report` / `empirical_first` overlays), and its "Applies /
  Confidence-tail / Quoting-example / depth-gate-target" bullets are
  role-specific ([FIX]/[NOTE] vs recommendation vs MISATTRIBUTED/DECORATIVE
  verdict); only the byte-identical boilerplate is fragmented
  (`fetchable_sources`, `abstract_not_fulltext`, `citation_verify_bullets`).
- **The 2026 identification-diagnostics standards** (in
  `identification-designer`, `identification-auditor`, `polish-identification`)
  are the same reference corpus rendered in three *moods* — designer
  imperatives ("use X"), auditor `kebab-case` failure-flags (a controlled
  vocabulary other agents cite by name), and a polish paper-presence checklist.
  No two are byte-identical, so there is no fragment atom. Properly
  single-sourcing them needs a *data table rendered three ways* — a code-gen
  step this static-include mechanism does not provide. Until that exists, the
  three lists are hand-maintained and must be updated in lockstep when
  econometric standards move (issue #167 companion / follow-up).
- **The citation-discipline "Verified-or-deleted" bullet** is left inline
  because its tail varies by mode: the base ends "…treated as fabrications by
  the downstream synthesizer/triager and may cause your report to be
  discarded"; report mode has no triager (pruned), so `report/referee-core`
  keeps only "downstream synthesizer", while `report/referee-freeform` and
  `report/referee-mechanism` end at "…no escape hatch" and drop the
  fabrication-consequence tail entirely.
