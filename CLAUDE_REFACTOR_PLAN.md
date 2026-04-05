# Claude Refactor Plan

## Goal

Finish modularizing the currently implemented Claude runtime path before adding support for additional runtimes.

Current principle:
- preserve generated Claude output exactly
- move shared logic out of `setup.sh`
- separate runtime-specific packaging from shared content
- treat agents, skills, utilities, and workflow logic as shared capabilities, even if Claude is the only implemented runtime today

## Current status

Interpretation:
- the research workflow content is not Claude-specific in principle
- it is only packaged for Claude right now because Claude is the only implemented runtime
- future runtimes should reuse the same shared capabilities and content, with runtime-specific adapters handling packaging

Completed:
- `CLAUDE.md` assembly split into:
  - `templates/shared/core.md`
  - `templates/runtime/claude/session.md`
  - `templates/scoring/*.md`
- Claude path conventions centralized in `setup.sh`
- helper functions added for copying agents
- shared Claude agents modularized into:
  - `templates/agent_metadata/claude_shared_agents.json`
  - `templates/agent_bodies/shared/*.md`
  - `scripts/assemble_claude_agents.py`
- `setup.sh` now assembles shared Claude agents from metadata + bodies
- Claude variant agents modularized into:
  - `templates/agent_metadata/claude_finance_agents.json`
  - `templates/agent_metadata/claude_macro_agents.json`
  - `templates/agent_bodies/finance/*.md`
  - `templates/agent_bodies/macro/*.md`
- `setup.sh` now assembles variant agents from metadata + bodies
- Claude extension agents modularized into:
  - `extensions/empirical/agent_metadata/*.json`
  - `extensions/empirical/agent_bodies/{shared,finance,macro}/*.md`
  - `extensions/theory_llm/agent_metadata/agents.json`
  - `extensions/theory_llm/agent_bodies/*.md`
- `setup.sh` now assembles extension agents from metadata + bodies
- Claude extension skills modularized into:
  - `templates/skill_metadata/empirical_skills.json`
  - `templates/skill_metadata/theory_llm_skills.json`
  - `templates/skill_bodies/empirical/*.md`
  - `templates/skill_bodies/theory_llm/*.md`
  - `scripts/assemble_claude_skills.py`
- `setup.sh` now assembles extension skills from metadata + bodies

Verified:
- generated `CLAUDE.md` matches `codex_inspect/CLAUDE.md`
- generated shared `.claude/agents/*.md` match `codex_inspect/.claude/agents/*.md`
- generated finance variant agents match baseline output after refactor
- generated macro variant agents match baseline output after refactor
- generated finance extension agents match baseline output after refactor
- generated macro extension agents match baseline output after refactor
- generated `.claude/skills/*/SKILL.md` match `codex_inspect/.claude/skills/*/SKILL.md`
- full local regeneration passed:
  - `./setup.sh test_output/refactor_compare --variant finance --ext empirical --ext theory_llm --local`
- variant parity checks passed:
  - `diff -ru test_output/variant_baseline_finance/.claude/agents test_output/variant_compare_finance/.claude/agents`
  - `diff -ru test_output/variant_baseline_macro/.claude/agents test_output/variant_compare_macro/.claude/agents`
- extension parity checks passed:
  - `diff -ru test_output/ext_agent_baseline_finance/.claude/agents test_output/ext_agent_compare_finance/.claude/agents`
  - `diff -ru test_output/ext_agent_baseline_macro/.claude/agents test_output/ext_agent_compare_macro/.claude/agents`
- committed and pushed:
  - `72ac58c` (`Modularize Claude skill assembly`)
  - `62ddb52` (`Modularize Claude variant agents`)
  - `643621d` (`Modularize Claude extension agents`)

Not done yet:
- none for the current Claude runtime packaging path

Not started yet:
- runtime packaging support beyond the first Codex pass

## Recommended next steps

### 1. Add support for additional runtimes

Current status:
- the currently implemented Claude runtime path is modularized end to end
- a first Codex pass now shares the same runtime content and skill source layers
- shared capabilities and content are now separated from most runtime packaging concerns
- Codex skill generation is implemented from the shared skill metadata + body layer
- runtime document generation is shared across `CLAUDE.md` and `AGENTS.md`

Recommended structure:
- keep shared capabilities in reusable metadata/body/utils layers
- add runtime-specific adapters for each new runtime
- avoid duplicating shared content across runtimes

Goal:
- implement a second runtime without disturbing Claude parity
- prove the architecture supports multiple runtimes cleanly

## Short-term Codex plan

Principle:
- do the minimum needed to prove a second runtime can consume the existing shared skill content
- avoid renaming or restructuring existing skill metadata/body files in the first pass
- reuse current skill metadata JSON and body markdown as the source of truth

Scope for first Codex pass:
- add a Codex skill assembler script
- generate Codex-native skill directories from existing metadata + bodies
- add `AGENTS.md` generation as the Codex analogue of `CLAUDE.md`
- keep shared content identical where possible and limit Codex-specific wording to the runtime layer
- emit both `CLAUDE.md` and `AGENTS.md` by default from the same setup flow

Recommended first target:
- start with `AGENTS.md` + skills, not Codex-specific agent packaging
- use existing files such as:
  - `templates/skill_metadata/empirical_skills.json`
  - `templates/skill_metadata/theory_llm_skills.json`
  - `templates/skill_metadata/codex_math_skills.json`
  - `templates/skill_bodies/...`
  - shared `CLAUDE.md` source components where reusable

Likely Codex runtime shape:
- `AGENTS.md`
- `.agents/agents/*.md`
- `.agents/skills/<skill-name>/SKILL.md`

Expected Codex output shape:
- `.agents/skills/<skill-name>/SKILL.md`
- frontmatter contains only:
  - `name`
  - `description`
- body comes from the existing shared skill body markdown

Likely implementation:
- add `scripts/assemble_codex_skills.py`
- add a general runtime document assembler for both `CLAUDE.md` and `AGENTS.md`
- reuse current metadata files, with top-level shared fields plus nested `claude` fields
- ignore Claude-only fields when generating Codex skills

If the first Codex pass works:
- then decide whether to:
  - add `agents/openai.yaml` for selected skills
  - support additional runtimes using the same shared layers

## Verification for first Codex pass

Codex-specific verification:
1. Generate `AGENTS.md` and Codex skills into a test output directory.
2. Confirm one directory is created per skill under `.agents/skills/`.
3. Confirm `.agents/agents/` is generated from the same agent content used for Claude output.
4. Confirm each generated `SKILL.md` has:
   - only `name` and `description` in frontmatter
   - the expected body content from the existing skill body source
5. Confirm no Claude-only metadata fields appear in generated Codex skills.
6. Confirm `AGENTS.md` uses the expected shared content and Codex-specific runtime wording.
7. Confirm existing Claude outputs are unchanged.

Minimum checks:
1. Run the Codex runtime generation into a scratch directory.
2. Inspect a few representative generated skills:
   - one empirical skill
   - `llm-experiments`
   - `codex-math`
3. Inspect generated `AGENTS.md`.
4. Inspect generated `.agents/agents/`.
5. Re-run the Claude generation path and diff against the pre-change output.

Claude-regression checks:
1. Run:
```bash
./setup.sh test_output/refactor_compare --variant finance --ext empirical --ext theory_llm --local
```
2. Diff:
```bash
diff -u codex_inspect/CLAUDE.md test_output/refactor_compare/CLAUDE.md
diff -ru codex_inspect/.claude test_output/refactor_compare/.claude
```
3. Only commit after Codex generation looks correct and Claude output parity is preserved.

## Constraints

- Do not modify or overwrite `codex_inspect/`
- Use `test_output/` for regeneration and diff checks
- Preserve generated Claude output exactly at each step
- Keep unrelated worktree changes untouched

## Verification checklist

After each refactor:

1. Run:
```bash
./setup.sh test_output/refactor_compare --variant finance --ext empirical --ext theory_llm --local
```

2. Diff orchestrator:
```bash
diff -u codex_inspect/CLAUDE.md test_output/refactor_compare/CLAUDE.md
```

3. Diff generated agent/skill outputs affected by the refactor.

4. Only commit after output parity is confirmed.

## Suggested order for the next session

1. decide whether the first Codex pass should keep `.agents/agents/` as a mirrored adapter layer or become more Codex-native
2. add optional Codex-native metadata like `agents/openai.yaml` where useful
3. then expand the same shared-layer approach to additional runtimes
