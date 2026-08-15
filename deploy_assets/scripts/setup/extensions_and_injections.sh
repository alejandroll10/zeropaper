#!/usr/bin/env bash
# Agent pruning/injections and optional extension assembly for setup.sh.
#
# Source after base_agents.sh. setup_core_agent_injections_and_pruning runs
# before project scaffolding; setup_extensions_injections_and_pruning runs
# after core skills. Private helper functions intentionally persist between
# those calls. Both public functions keep phase-owned state local and export no
# shell variables.

setup_core_agent_injections_and_pruning() {
local agent _line VARIANT_BLOCK
local -a _core_bypass_agents _core_developing_agents _core_bash_agents
local -a _core_heavy_agents _report_pipeline_native_audit_agents
# ── Prune agents not used in --mode report ──
# Report mode only invokes the audit fan-out + report-synthesizer. Generative,
# pipeline-management, scoring, broad-survey, and writing-style agents have no
# job here. Removing them at assembly time prevents accidental invocation and
# keeps the deployed .claude/agents/ catalog focused. Audit, polish-*, referee*,
# bib-verifier, novelty-checker, self-attacker, debugger, report-synthesizer
# stay; extension generative agents (empiricist, identification-designer,
# experiment-designer) are pruned per-extension below by the same function.
# Delete assembled agent output files across all five runtimes. The
# mode/flag-conditional prune passes below decide *when* to call this; this
# helper just does the removal, so a new runtime output dir is wired in one
# place, not once per prune pass.
_setup_extensions_prune_agents() {
    local _name
    for _name in "$@"; do
        rm -f "$AGENTS_OUT/${_name}.md" "$CODEX_AGENTS_OUT/${_name}.toml" "$GEMINI_AGENTS_OUT/${_name}.md" "$GROK_AGENTS_OUT/${_name}.md" "$OPENCODE_AGENTS_OUT/${_name}.md"
    done
}

_setup_extensions_prune_report_mode_agents() {
    [ "$MODE" = "report" ] || return 0
    _setup_extensions_prune_agents "$@"
}

# Mode-conditional ADDITION (inverse of _setup_extensions_prune_report_mode_agents): an agent that
# is assembled for all --ext empirical deploys (it lives in the empirical
# extension metadata) but is meaningful ONLY under --mode empirical-first — the
# prose+DAG mechanism it audits exists only in that mode. We assemble it
# unconditionally with the rest of the empirical agents, then delete its output
# files in every other mode. This keeps the agent off the theory-first /
# macro / report build surface without adding a mode-conditional metadata path.
_setup_extensions_prune_non_empirical_first_agents() {
    [ "$MODE" = "empirical-first" ] && return 0
    _setup_extensions_prune_agents "$@"
}

# Inverse of _setup_extensions_prune_report_mode_agents (#164): report-synthesizer is invoked ONLY
# under --mode report (it aggregates audits/*.md into report/referee_report.md).
# It lives in shared agent metadata, so it assembles into every build; delete it
# in every non-report build so it never sits in the orchestrator's
# available-agents list where it can never fire (and can't be improvised into,
# e.g., a Stage-6 aggregation the `editor` agent owns).
_setup_extensions_prune_non_report_mode_agents() {
    [ "$MODE" = "report" ] && return 0
    _setup_extensions_prune_agents "$@"
}

# faithful-drift-auditor is launched ONLY on --faithful runs. It too assembles
# from shared metadata into every build; delete it in every non-faithful build.
# (This subsumes the report-mode case — report ⊥ faithful — so it need not be
# listed in _setup_extensions_prune_report_mode_agents.) (#164)
_setup_extensions_prune_non_faithful_agents() {
    [ "$FAITHFUL" = "1" ] && return 0
    _setup_extensions_prune_agents "$@"
}

# Core agents not deployed in report mode (rationale documented in
# templates/runtime/{claude,codex,gemini}/session_report.md's "What this mode
# does not do" block). Extension generative agents are pruned in the extension
# block below after they have been assembled.
_setup_extensions_prune_report_mode_agents \
    theory-generator \
    paper-writer \
    question-poser \
    question-referee \
    idea-generator \
    idea-reviewer \
    idea-prototyper \
    theory-explorer \
    implications-deriver \
    last-resort \
    scribe \
    triager \
    puzzle-triager \
    branch-manager \
    editor \
    scorer \
    scorer-freeform \
    literature-scout \
    gap-scout \
    style \
    table-auditor

if [ "$MODE" = "report" ]; then
    echo "  ✓ Pruned generative / management agents for --mode report"
fi

# ── Prune agents meaningful only in a mode/flag this build didn't select (#164) ──
# Symmetric to _setup_extensions_prune_report_mode_agents: these ship from shared metadata but can
# only ever fire in one mode/flag. Removing them keeps the deployed
# .claude/agents/ catalog to agents this build can actually invoke.
_setup_extensions_prune_non_report_mode_agents report-synthesizer
_setup_extensions_prune_non_faithful_agents faithful-drift-auditor

# ── Inject variant context into agents ──
VARIANT_BLOCK="
## Variant context
- **Paper type:** ${PAPER_TYPE}
- **Target journals:** ${JOURNAL_LIST}
- **Domain:** ${DOMAIN_AREAS}
"

for agent in literature-scout gap-scout novelty-checker theory-explorer implications-deriver referee referee-freeform referee-mechanism scorer scorer-freeform editor branch-manager last-resort paper-writer style report-synthesizer; do
    if [ -f "$AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$AGENTS_OUT/$agent.md"
    fi
    if [ -f "$CODEX_AGENTS_OUT/$agent.toml" ]; then
        # Insert before the closing ''' in the TOML multiline string
        # Use awk to find the LAST ''' and insert the block before it.
        # Pass the (multi-line) block via the environment, not `-v`: BSD awk
        # (stock macOS) rejects literal newlines in a `-v` value; ENVIRON is
        # portable across BSD and GNU awk.
        VARIANT_BLOCK="$VARIANT_BLOCK" awk '
        { lines[NR] = $0 }
        /^'\'''\'''\''$/ { last = NR }
        END {
            for (i = 1; i <= NR; i++) {
                if (i == last) print ENVIRON["VARIANT_BLOCK"]
                print lines[i]
            }
        }' "$CODEX_AGENTS_OUT/$agent.toml" > "$CODEX_AGENTS_OUT/$agent.toml.tmp" \
        && mv "$CODEX_AGENTS_OUT/$agent.toml.tmp" "$CODEX_AGENTS_OUT/$agent.toml"
    fi
    if [ -f "$GEMINI_AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$GEMINI_AGENTS_OUT/$agent.md"
    fi
    if [ -f "$GROK_AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$GROK_AGENTS_OUT/$agent.md"
    fi
    if [ -f "$OPENCODE_AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$OPENCODE_AGENTS_OUT/$agent.md"
    fi
done
echo "  ✓ Variant context injected into agents"

# ── Agent body inject helpers ──
# `_setup_extensions_inject_block_into_agents <inject_file> <agent>...` appends the contents of
# <inject_file> to the assembled body of each named agent across all five runtimes.
# The codex append uses awk to splice
# the block in just before the closing `'''` of the TOML prompt body; the claude/
# gemini appends are plain. File-existence guards make a not-yet-assembled agent a
# harmless no-op. Single source of the per-runtime append logic for every inject
# loop below (faithful, bash-background, core-bypass, efficiency).
_setup_extensions_inject_block_into_agents() {
    local _inject_file="$1"; shift
    if [ ! -f "$_inject_file" ]; then
        echo "Error: inject template not found: $_inject_file" >&2
        exit 1
    fi
    local _block
    _block=$(cat "$_inject_file")
    local _agent
    for _agent in "$@"; do
        if [ -f "$AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$AGENTS_OUT/$_agent.md"
        fi
        if [ -f "$CODEX_AGENTS_OUT/$_agent.toml" ]; then
            # Multi-line block via environment, not `-v` (BSD-awk-safe; see note above).
            _block="$_block" awk '
            { lines[NR] = $0 }
            /^'\'''\'''\''$/ { last = NR }
            END {
                for (i = 1; i <= NR; i++) {
                    if (i == last) print ENVIRON["_block"]
                    print lines[i]
                }
            }' "$CODEX_AGENTS_OUT/$_agent.toml" > "$CODEX_AGENTS_OUT/$_agent.toml.tmp" \
            && mv "$CODEX_AGENTS_OUT/$_agent.toml.tmp" "$CODEX_AGENTS_OUT/$_agent.toml"
        fi
        if [ -f "$GEMINI_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$GEMINI_AGENTS_OUT/$_agent.md"
        fi
        if [ -f "$GROK_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$GROK_AGENTS_OUT/$_agent.md"
        fi
        if [ -f "$OPENCODE_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$OPENCODE_AGENTS_OUT/$_agent.md"
        fi
    done
}

# ── Faithful-mode contract pointer for developing agents (--faithful only) ──
# Faithful mode adds a short pointer to *developing* agents — those that
# produce paper content — directing them to read `output/seed/mechanism_contract.md`
# before producing output. *Evaluators* (scorer, referees, auditors, novelty-checker,
# self-attacker, idea-{prototyper,reviewer}, branch-manager) stay impartial: quoting
# the contract into them would corrupt the evaluation signal. The faithful constraint
# enters at the orchestrator's routing of evaluator verdicts (see faithful.md),
# not at the evaluators themselves.
#
# Called once after core agent assembly and once inside each extension block (after
# the extension finishes assembling its own agents) so extension developing agents
# (empiricist, identification-designer, experiment-designer, etc.) also get the
# pointer. A no-op when FAITHFUL=0.
_setup_extensions_inject_faithful_into_agents() {
    [ "$FAITHFUL" = "1" ] || return 0
    _setup_extensions_inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/faithful_inject.md" "$@"
}

# `_setup_extensions_inject_bash_background_into_agents` appends the no-nohup / use-a-harness-
# tracked-background-job note to every Bash-capable agent. Unconditional (unlike
# the faithful injector): subagents never see the runtime doc, so a heavy job
# launched by e.g. theory-explorer/empiricist/experiment-designer would otherwise
# go unmonitored. Called after core assembly and inside each extension block.
_setup_extensions_inject_bash_background_into_agents() {
    _setup_extensions_inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/bash_background.md" "$@"
    # OpenCode has no Bash run_in_background argument. Replace the generic
    # Claude-compatible paragraph in only its generated agent bodies with the
    # foreground/checkpointing contract. Exact replacement fails loudly if the
    # expected generic block is absent, preventing silent instruction drift.
    python3 -I - \
        "$TEMPLATE_ROOT/templates/shared/bash_background.md" \
        "$TEMPLATE_ROOT/templates/shared/bash_foreground_opencode.md" \
        "$OPENCODE_AGENTS_OUT" "$@" <<'PYEOF'
import os, sys
old = open(sys.argv[1]).read().rstrip()
new = open(sys.argv[2]).read().rstrip()
root = sys.argv[3]
for agent in sys.argv[4:]:
    path = os.path.join(root, agent + ".md")
    if not os.path.exists(path):
        continue
    text = open(path).read()
    if old not in text:
        raise SystemExit(f"OpenCode Bash injection missing from {path}")
    with open(path, "w") as f:
        f.write(text.replace(old, new, 1))
PYEOF
}

# `_setup_extensions_inject_efficiency_into_agents` appends the compute-efficiency mandate (issue
# #74) — be mindful of memory/runtime/cost, size the data and method before
# running, stream rather than eager-load, test on a subsample — to the explicit
# set of data/compute-heavy agents (theory-explorer; the empirical empiricist/
# auditors/replicator; the theory_llm experiment-designer). Unconditional like the
# bash-background injector: subagents never see the runtime doc, and an OOM /
# runaway-cost run is a recurring cross-repo cost (see issue #74's evidence). The
# heavy set is an explicit list, not metadata-derived — "compute-heavy" is not a
# metadata category, and an explicit auditable list is clearer than approximating
# it via --has-tool Bash, which over-injects into read-only agents (scribe,
# literature-scout, polish-prose, ...). Called after core assembly and inside each
# extension block; file-existence guards make a not-yet-assembled agent a no-op.
_setup_extensions_inject_efficiency_into_agents() {
    _setup_extensions_inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/efficiency_inject.md" "$@"
}

# `_setup_extensions_inject_core_bypass_into_agents` appends the core-bypass guard pointer (issue
# #51) to agents that, mid-run, depend on a binding external source or a binding
# verification tool and could silently downgrade to a non-binding fallback when it
# is unavailable — i.e. agents that can themselves *detect* a bypass (source/cert
# failure, or a tool failure being misread as "source down", bypass conditions 1
# and 4 in docs/core_bypass.md). Gate-skip / agent-substitution (conditions 2-3)
# are orchestrator-only events an agent can't see while running, so they are not
# recorded by this inject; the orchestrator records them itself in default mode via
# the per-gate "Bypass recording" pointer in docs/stage_{2,4,5,6}.md (issue #61,
# off the runtime-doc char budget since stage docs are read on demand). The
# --halt-on-core-bypass flag additionally injects an orchestrator-side halt pointer
# into the runtime doc. Unconditional like the
# bash-background injector (subagents never see the runtime doc, and recording is
# the default behavior regardless of the --halt-on-core-bypass flag; the flag only
# adds the orchestrator-side halt pointer in the runtime doc). The pointer text
# degrades gracefully when there is no process_log/ (manual mode). File-existence
# guards make passing a not-yet-assembled agent a harmless no-op.
_setup_extensions_inject_core_bypass_into_agents() {
    _setup_extensions_inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/core_bypass_inject.md" "$@"
}

# Core (shared + variant) agents with a binding runtime dependency they could
# silently downgrade. Explicit list (not metadata-derived): "depends on a binding
# source/tool at run time" is not an existing metadata category, and an explicit,
# auditable list is clearer than approximating it via --has-tool. Keep in sync
# when adding such an agent. Extension agents get the pointer in their own blocks.
#   bib-verifier / novelty-checker / polish-bibliography / polish-institutions
#     — external lit sources (OpenAlex / Crossref / WebSearch).
#   math-auditor{,-freeform} — the codex-math tool; covered by bypass condition 4
#     (a codex-math outage must not be misread as "unverifiable, pass anyway").
_core_bypass_agents=(
    bib-verifier
    novelty-checker
    polish-bibliography
    polish-institutions
    math-auditor
    math-auditor-freeform
)
_setup_extensions_inject_core_bypass_into_agents "${_core_bypass_agents[@]}"
echo "  ✓ Core-bypass guard pointer injected into binding-source agents"

# Core developing agents — list comes from metadata `category: "developing"`,
# the single source of truth (see scripts/list_agents_by_category.py).
_core_developing_agents=()
while IFS= read -r _line; do _core_developing_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
    --category developing \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json" \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json")
# Fail loud: empty here means the lister errored (the read loop masks it under set -e),
# never a real result — there are always developing agents. Harmless when
# FAITHFUL=0 (injector is a no-op) but prevents a silent skip under --faithful.
if [ "${#_core_developing_agents[@]}" -eq 0 ]; then
    echo "Error: core developing-agent list is empty (lister failed or metadata missing)" >&2
    exit 1
fi
_setup_extensions_inject_faithful_into_agents "${_core_developing_agents[@]}"
if [ "$FAITHFUL" = "1" ]; then
    echo "  ✓ Faithful pointer injected into core developing agents"
fi

# Bash-capable core agents — list comes from metadata `tools` containing Bash.
_core_bash_agents=()
while IFS= read -r _line; do _core_bash_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
    --has-tool Bash \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json" \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json")
# Fail loud: the read loop masks python failure under set -e, so an empty list here
# means the lister errored or metadata is missing — never a real empty result.
if [ "${#_core_bash_agents[@]}" -eq 0 ]; then
    echo "Error: Bash-capable core agent list is empty (lister failed or metadata missing)" >&2
    exit 1
fi
_setup_extensions_inject_bash_background_into_agents "${_core_bash_agents[@]}"
echo "  ✓ Background-job note injected into Bash-capable core agents"

# Efficiency mandate (issue #74): inject into the explicit set of data/compute-
# heavy core agents. theory-explorer is the only core agent that runs real
# computation/simulation; the empirical/theory_llm heavy agents get the mandate in
# their own extension blocks.
_core_heavy_agents=(theory-explorer)
_setup_extensions_inject_efficiency_into_agents "${_core_heavy_agents[@]}"
echo "  ✓ Efficiency mandate injected into compute-heavy core agents"

# ── Report-mode context for pipeline-native audit agents (--mode report only) ──
# The report-mode fan-out reuses audit agents whose bodies were written for this
# pipeline's own drafts: they hardcode reads of pipeline artifacts
# (output/stage*/ theory drafts, negative_results, prior audit rounds) and writes
# to pipeline paths (output/polish_*_r{N}.md). In report mode neither exists —
# inputs live in submission/ and outputs go to the prompt-passed audits/<name>.md
# path. This block re-anchors those bodies: prompt paths win, pipeline artifacts
# don't exist, PDF-only submissions degrade with an explicit note, and
# submission/ is read-only. Excluded on purpose: the referee trio and
# polish-identification (report-native body overlays in
# templates/agent_bodies/shared_modes/report/), report-synthesizer (report-native
# shared body), and debugger (reactive tool-failure diagnosis, not a
# submission-facing audit). Keep this list in sync with the Step 2 fan-out table
# in templates/shared/core_report.md.
_setup_extensions_inject_report_mode_into_agents() {
    [ "$MODE" = "report" ] || return 0
    _setup_extensions_inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/report_mode_inject.md" "$@"
}
_report_pipeline_native_audit_agents=(
    math-auditor
    math-auditor-freeform
    self-attacker
    novelty-checker
    bib-verifier
    polish-formula
    polish-numerics
    polish-consistency
    polish-equilibria
    polish-prose
    polish-bibliography
    polish-institutions
)
_setup_extensions_inject_report_mode_into_agents "${_report_pipeline_native_audit_agents[@]}"
if [ "$MODE" = "report" ]; then
    echo "  ✓ Report-mode context injected into pipeline-native audit agents"
fi

}

setup_extensions_injections_and_pruning() {
local SKILLS_OUT CODEX_SKILLS_OUT ext LIGHT_MODEL INJECT doc _docfile _name _line
local EMPIRICAL_ENABLED EMPIRICAL_FIRST_ON EXT_EMPIRICAL_ON
local -a _tllm_developing_agents _tllm_bash_agents _tllm_heavy_agents
local -a _empirical_developing_agents _empirical_bash_agents _empirical_heavy_agents
# ── Apply extensions ──
SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"

for ext in "${EXTENSIONS[@]}"; do
    case "$ext" in
        theory_llm)
            echo "Applying LLM experiment extension..."
            infrastructure_copy_file 290 \
                "$TEMPLATE_ROOT/extensions/theory_llm/deps.txt" \
                ".arpipeline/update_inputs/deps/extensions/theory_llm.txt"
            LIGHT_MODEL=""
            if [ "$LIGHT" = "1" ]; then LIGHT_MODEL="sonnet"; fi
            bash "$TEMPLATE_ROOT/scripts/apply_extension_theory_llm.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$GEMINI_AGENTS_OUT" \
                "$OPENCODE_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$ASSEMBLE_ONLY" \
                "$LIGHT_MODEL" \
                "$MODE_BODIES_OVERLAY" \
                "$MODE_VOCAB_OVERLAY" \
                "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json" \
                "${MODE//-/_}"
            provision_extension_dependencies theory_llm

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
                --output-dir "$CODEX_SKILLS_OUT"

            # Inject stage instructions into runtime docs at {{EXTENSION_STAGES}} placeholder
            INJECT="$TEMPLATE_ROOT/extensions/theory_llm/stages_inject.md"
            for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
                python3 -I -c "
import sys; p=sys.argv[1]; d=sys.argv[2]
content=open(d).read(); inject=open(p).read()
open(d,'w').write(content.replace('{{EXTENSION_STAGES}}', inject.rstrip()+'\n\n{{EXTENSION_STAGES}}'))
" "$INJECT" "$doc"
            done

            # Copy extension docs into project docs/ with placeholder substitution
            if [ -d "$TEMPLATE_ROOT/extensions/theory_llm/docs" ]; then
                cp "$TEMPLATE_ROOT/extensions/theory_llm/docs/"*.md "$P/docs/"
                for _docfile in "$TEMPLATE_ROOT/extensions/theory_llm/docs/"*.md; do
                    _name=$(basename "$_docfile")
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g; s|{{INITIAL_TIER}}|$INITIAL_TIER|g; s|{{TIER_LADDER_PROSE}}|$TIER_LADDER_PROSE|g; s|{{TIER_LIST_INLINE}}|$TIER_LIST_INLINE|g; s|{{TIER_DOWNGRADE_EXAMPLES}}|$TIER_DOWNGRADE_EXAMPLES|g; s|{{MECHANISM_QUALIFIER_AN}}|$MECHANISM_QUALIFIER_AN|g; s|{{MECHANISM_QUALIFIER}}|$MECHANISM_QUALIFIER|g; s|{{MECHANISM_DISCIPLINE}}|$MECHANISM_DISCIPLINE|g; s|{{PRINCIPLED_MECHANISM_PHRASE}}|$PRINCIPLED_MECHANISM_PHRASE|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
                done
            fi

            # Fill theory_llm-only placeholders in shared docs / runtime docs.
            # Theory-only runs leave these placeholders to be stripped by the post-extension cleanup.
            python3 -I - \
                "$TEMPLATE_ROOT/extensions/theory_llm/stage2_rerun_inject.md" \
                "$TEMPLATE_ROOT/extensions/theory_llm/stage3b_gate_inject.md" \
                "$TEMPLATE_ROOT/extensions/theory_llm/state_fields_inject.md" \
                "$TEMPLATE_ROOT/extensions/theory_llm/state3b_doc_inject.md" \
                "$P/docs/stage_2.md" \
                "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" <<'PYEOF'
import json, os, sys
stage2 = open(sys.argv[1]).read()
stage3b_gate = open(sys.argv[2]).read()
state = open(sys.argv[3]).read()
state3b_doc = open(sys.argv[4]).read()
stage2_md = sys.argv[5]
runtime_docs = sys.argv[6:9]

def patch(path, pairs):
    if not os.path.exists(path):
        return
    with open(path) as f: t = f.read()
    new = t
    for needle, repl in pairs:
        new = new.replace(needle, repl)
    if new != t:
        with open(path, "w") as f: f.write(new)

patch(stage2_md, [
    ("{{THEORY_LLM_STAGE2_RERUN_ADDENDUM}}", stage2),
    ("{{THEORY_LLM_STAGE3B_GATE_ADDENDUM}}", stage3b_gate),
])

for d in runtime_docs:
    patch(d, [
        ("{{THEORY_LLM_STATE_FIELDS}}", state),
        ("{{THEORY_LLM_STATE3B_DOC}}", state3b_doc),
    ])

# pipeline_state.json: add stage3b_theory_version field, mirroring stage2b_theory_version.
state_path = os.path.join(os.path.dirname(stage2_md), "..", "process_log", "pipeline_state.json")
state_path = os.path.normpath(state_path)
if os.path.exists(state_path):
    with open(state_path) as f: data = json.load(f)
    if "stage3b_theory_version" not in data:
        # Insert immediately after stage3a_theory_version (if --ext empirical) or stage2b_theory_version.
        new = {}
        anchor = "stage3a_theory_version" if "stage3a_theory_version" in data else "stage2b_theory_version"
        for k, v in data.items():
            new[k] = v
            if k == anchor:
                new["stage3b_theory_version"] = None
        data = new
        with open(state_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
PYEOF

            # Theory_LLM extension developing agents — from metadata.
            _tllm_developing_agents=()
            while IFS= read -r _line; do _tllm_developing_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --category developing \
                --metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json")
            if [ "${#_tllm_developing_agents[@]}" -eq 0 ]; then
                echo "Error: theory_llm developing-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            _setup_extensions_inject_faithful_into_agents "${_tllm_developing_agents[@]}"

            _tllm_bash_agents=()
            while IFS= read -r _line; do _tllm_bash_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --has-tool Bash \
                --metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json")
            if [ "${#_tllm_bash_agents[@]}" -eq 0 ]; then
                echo "Error: theory_llm Bash-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            _setup_extensions_inject_bash_background_into_agents "${_tllm_bash_agents[@]}"

            # Efficiency mandate (issue #74): experiment-designer runs the LLM
            # experiments, where the "cost" dimension of the mandate bites hardest.
            _tllm_heavy_agents=(experiment-designer)
            _setup_extensions_inject_efficiency_into_agents "${_tllm_heavy_agents[@]}"

            # Core-bypass guard: the LLM API is a binding source for both the
            # designer (runs experiments) and the reviewer (re-checks them).
            # polish-experiments included: its reproducibility spot-check re-runs
            # an experiment slice against the LLM backend — a backend outage must
            # not be misread as "nothing to verify, pass."
            _setup_extensions_inject_core_bypass_into_agents experiment-designer experiment-reviewer polish-experiments

            # Report mode: --ext theory_llm is install-only (skills + LLM client).
            # experiment-designer (generative), experiment-reviewer (audit of
            # pipeline-produced experiments), and polish-experiments (audit of
            # pipeline-produced stage3b artifacts) are all pruned — there are no
            # pipeline-produced experiments on an external submission.
            _setup_extensions_prune_report_mode_agents experiment-designer experiment-reviewer polish-experiments
            if [ "$MODE" = "report" ]; then
                rm -f "$P/docs/stage_3b_experiments.md"
                # Mirror the stage3a cleanup below: the applier creates
                # output/stage3b/figures/ unconditionally, and a report
                # deployment has no stages, so both must go (child first —
                # rmdir only removes empty dirs). core_report.md promises
                # "no output/stage*/"; without this the promise is false.
                rmdir "$P/output/stage3b/figures" 2>/dev/null || true
                rmdir "$P/output/stage3b" 2>/dev/null || true
            fi
            echo "  ✓ LLM experiment extension applied"
            ;;
        empirical)
            echo "Applying empirical extension..."
            infrastructure_copy_file 290 \
                "$TEMPLATE_ROOT/extensions/empirical/deps.txt" \
                ".arpipeline/update_inputs/deps/extensions/empirical.txt"
            LIGHT_MODEL=""
            if [ "$LIGHT" = "1" ]; then LIGHT_MODEL="sonnet"; fi
            bash "$TEMPLATE_ROOT/scripts/apply_extension_empirical.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$GEMINI_AGENTS_OUT" \
                "$OPENCODE_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$AGENT_DIR" \
                "$ASSEMBLE_ONLY" \
                "$LIGHT_MODEL" \
                "$MODE_BODIES_OVERLAY" \
                "$MODE_VOCAB_OVERLAY" \
                "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json" \
                "${MODE//-/_}"
            provision_extension_dependencies empirical

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
                --output-dir "$CODEX_SKILLS_OUT"

            # Inject stage instructions into runtime docs at {{EXTENSION_STAGES}} placeholder
            INJECT="$TEMPLATE_ROOT/extensions/empirical/stages_inject.md"
            for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
                python3 -I -c "
import sys; p=sys.argv[1]; d=sys.argv[2]
content=open(d).read(); inject=open(p).read()
open(d,'w').write(content.replace('{{EXTENSION_STAGES}}', inject.rstrip()+'\n\n{{EXTENSION_STAGES}}'))
" "$INJECT" "$doc"
            done

            # Copy extension docs into project docs/ with placeholder substitution
            if [ -d "$TEMPLATE_ROOT/extensions/empirical/docs" ]; then
                cp "$TEMPLATE_ROOT/extensions/empirical/docs/"*.md "$P/docs/"
                for _docfile in "$TEMPLATE_ROOT/extensions/empirical/docs/"*.md; do
                    _name=$(basename "$_docfile")
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g; s|{{INITIAL_TIER}}|$INITIAL_TIER|g; s|{{TIER_LADDER_PROSE}}|$TIER_LADDER_PROSE|g; s|{{TIER_LIST_INLINE}}|$TIER_LIST_INLINE|g; s|{{TIER_DOWNGRADE_EXAMPLES}}|$TIER_DOWNGRADE_EXAMPLES|g; s|{{MECHANISM_QUALIFIER_AN}}|$MECHANISM_QUALIFIER_AN|g; s|{{MECHANISM_QUALIFIER}}|$MECHANISM_QUALIFIER|g; s|{{MECHANISM_DISCIPLINE}}|$MECHANISM_DISCIPLINE|g; s|{{PRINCIPLED_MECHANISM_PHRASE}}|$PRINCIPLED_MECHANISM_PHRASE|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
                done
            fi

            # Fill empirical-only placeholders in shared docs / runtime docs / scorer agent body.
            # Theory-only runs leave these placeholders to be stripped by the post-extension cleanup.
            python3 -I - \
                "$TEMPLATE_ROOT/extensions/empirical/stage2_rerun_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/stage3a_gate_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/state_fields_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/state3a_doc_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/playbook_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/scorer_fertility_inject.md" \
                "$P/docs/stage_2.md" \
                "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" \
                "$AGENTS_OUT/scorer.md" "$CODEX_AGENTS_OUT/scorer.toml" "$GEMINI_AGENTS_OUT/scorer.md" "$GROK_AGENTS_OUT/scorer.md" "$OPENCODE_AGENTS_OUT/scorer.md" \
                "$TEMPLATE_ROOT/extensions/empirical/state_loop_fields_inject.md" <<'PYEOF'
import json, os, sys
# Inject files are read raw — each file is responsible for its own leading/trailing
# whitespace. The final newline left by the editor IS content (it determines whether
# a blank line follows the substitution).
stage2 = open(sys.argv[1]).read()
stage3a_gate = open(sys.argv[2]).read()
state = open(sys.argv[3]).read()
state3a_doc = open(sys.argv[4]).read()
playbook = open(sys.argv[5]).read()
fertility = open(sys.argv[6]).read()
stage2_md = sys.argv[7]
runtime_docs = sys.argv[8:11]
# Five scorer files — OpenCode is the fifth runtime (.opencode/agents/scorer.md).
# These slices are hand-indexed against the argv list above; when you add a call
# site, re-count BOTH the slice end and every index after it. Getting this wrong is
# silent: an off-by-one previously made `state_loop` read the grok scorer body and
# splice that whole agent prompt into the deployed runtime docs.
scorer_files = sys.argv[11:16]
state_loop = open(sys.argv[16]).read()

def patch(path, pairs):
    if not os.path.exists(path):
        return
    with open(path) as f: t = f.read()
    new = t
    for needle, repl in pairs:
        new = new.replace(needle, repl)
    if new != t:
        with open(path, "w") as f: f.write(new)

# Stage_2.md: two placeholders. Each placeholder lives on its own line; the
# placeholder line's trailing newline is preserved by replacing only the
# placeholder text (no extra "\n" appended).
patch(stage2_md, [
    ("{{EMPIRICAL_STAGE2_RERUN_ADDENDUM}}", stage2),
    ("{{EMPIRICAL_STAGE3A_GATE_ADDENDUM}}", stage3a_gate),
])

# Runtime docs (CLAUDE.md / AGENTS.md / GEMINI.md): state JSON field + state-doc paragraph + playbook addendum.
for d in runtime_docs:
    patch(d, [
        ("{{EMPIRICAL_STATE_FIELDS}}", state),
        ("{{EMPIRICAL_LOOP_FIELDS}}", state_loop),
        ("{{EMPIRICAL_STATE3A_DOC}}", state3a_doc),
        ("{{EMPIRICAL_PLAYBOOK_ADDENDUM}}", playbook),
    ])

# Scorer agent bodies: replace the comment marker with the empirical fertility addendum.
for s in scorer_files:
    patch(s, [
        ("<!-- EMPIRICAL_FERTILITY_ADDENDUM -->", fertility),
    ])

# pipeline_state.json: add stage3a_theory_version field, mirroring stage2b_theory_version.
# Manual mode skips state file creation (search `Create project directories and initial files`
# in setup.sh), so guard on existence.
state_path = os.path.join(os.path.dirname(stage2_md), "..", "process_log", "pipeline_state.json")
state_path = os.path.normpath(state_path)
if os.path.exists(state_path):
    with open(state_path) as f: data = json.load(f)
    # Two empirical version-pointer fields, inserted after stage2b_theory_version to
    # preserve key order. Null/no-op in theory-first --ext empirical runs.
    if "stage3a_theory_version" not in data:
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "stage2b_theory_version":
                new["stage3a_theory_version"] = None
        data = new
    if "stage2_mechanism_version" not in data:
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "stage3a_theory_version":
                new["stage2_mechanism_version"] = None
        data = new
    # Empirical audit loops: merge into the generic `loops` object (see CLAUDE.md
    # "Audit-loop scoping" rule + Loop Registry). setdefault is idempotent across
    # re-runs / update refreshes and needs no hand-anchored key order — the whole point
    # of the loops:{} restructure (issue #166): a new empirical gate is added here in one
    # line and is loop-capped everywhere for free.
    emp_loops = {
        "identification_plan_revision": {"round": 0, "cap": 3},
        "headline_replication":         {"round": 0, "cap": 3},
        "replicator_self_refire":       {"round": 0, "cap": 3},
        "data_integrity":               {"round": 0, "cap": 3},
        "method_check":                 {"round": 0, "cap": 3},
        "claim_grounding":              {"round": 0, "cap": 3},
        "paper_writer_pse":             {"round": 0, "cap": 3},
        "claim_format_reexport":        {"round": 0, "cap": 2},
    }
    data.setdefault("loops", {})
    for _lid, _cfg in emp_loops.items():
        data["loops"].setdefault(_lid, dict(_cfg))
    with open(state_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
PYEOF

            # Empirical extension developing agents — from metadata.
            # Variant-aware via $AGENT_DIR (finance metadata adds identification-designer;
            # macro currently has empiricist only). The metadata is the source of truth.
            _empirical_developing_agents=()
            while IFS= read -r _line; do _empirical_developing_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --category developing \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json" \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json")
            if [ "${#_empirical_developing_agents[@]}" -eq 0 ]; then
                echo "Error: empirical developing-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            _setup_extensions_inject_faithful_into_agents "${_empirical_developing_agents[@]}"

            _empirical_bash_agents=()
            while IFS= read -r _line; do _empirical_bash_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --has-tool Bash \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json" \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json")
            if [ "${#_empirical_bash_agents[@]}" -eq 0 ]; then
                echo "Error: empirical Bash-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            _setup_extensions_inject_bash_background_into_agents "${_empirical_bash_agents[@]}"

            # Efficiency mandate (issue #74): the empirical agents that load/run
            # large tables — the source of every documented OOM. method-checker is
            # excluded (it reads code, doesn't run analyses); claim-enumerator/
            # claim-verifier do lightweight regex/file checks, not data analysis.
            _empirical_heavy_agents=(empiricist empirics-auditor headline-replicator data-integrity-auditor data-selection-auditor)
            _setup_extensions_inject_efficiency_into_agents "${_empirical_heavy_agents[@]}"

            # Core-bypass guard: empirical agents that read a binding data source
            # (WRDS/EDGAR/FRED) or verify the pipeline's empirics against it. The
            # injector's file-existence guards make pruned/absent agents a no-op
            # (e.g. macro has no identification-auditor; report mode prunes these).
            _setup_extensions_inject_core_bypass_into_agents \
                empiricist empirics-auditor headline-replicator \
                data-integrity-auditor data-selection-auditor method-checker \
                claim-grounder claim-verifier identification-auditor

            # Report mode: --ext empirical is install-only (WRDS/FRED/Census/SEC
            # skills + utility scripts). All audit agents that ship with the
            # empirical extension are pruned — they were designed against the
            # pipeline's own empiricist output (output/stage3a/empirical_analysis.md,
            # code/empirical.py) and would need substantial rewrites to operate on
            # an external submission. The base referees handle empirical refereeing
            # at the editorial level. Full code-level empirical auditing of
            # external submissions is a v2 feature. The generative empiricist /
            # identification-designer are pruned for the usual reason.
            _setup_extensions_prune_report_mode_agents \
                empiricist identification-designer \
                empirics-auditor identification-auditor \
                data-integrity-auditor data-selection-auditor method-checker \
                mechanism-auditor \
                headline-replicator \
                claim-enumerator claim-grounder claim-verifier
            # mechanism-auditor is meaningful only under --mode empirical-first
            # (it audits the prose+DAG mechanism that only that mode produces).
            # Assembled with the empirical agents above; removed in every other
            # mode (theory-first, macro, report — report is already covered by
            # the report prune list above, but the non-empirical-first prune is
            # the canonical guard).
            _setup_extensions_prune_non_empirical_first_agents mechanism-auditor
            # Empirical extension also creates output/stage3a/ unconditionally
            # and copies stage_3a_empirical.md into docs/. Both are pipeline-
            # workflow artifacts irrelevant to report mode — remove them.
            if [ "$MODE" = "report" ]; then
                # Remove the figures/ child before the parent: the extension
                # applier creates output/stage3a/figures/, so a bare rmdir on
                # the parent fails (non-empty) and silently leaves the whole
                # tree behind, contradicting core_report.md's "no output/stage*/"
                # invariant. Both stay rmdir (not rm -rf) on purpose — they must
                # only vanish when empty, which at setup time they always are.
                rmdir "$P/output/stage3a/figures" 2>/dev/null || true
                rmdir "$P/output/stage3a" 2>/dev/null || true
                rm -f "$P/docs/stage_3a_empirical.md"
            fi
            echo "  ✓ Empirical extension applied (skills + agents)"
            ;;
        *)
            reject_unknown_extension "$ext"
            ;;
    esac
done

# Clean up leftover {{EXTENSION_STAGES}} placeholder from runtime docs
for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
    python3 -I -c "
import sys; d=sys.argv[1]
content=open(d).read()
open(d,'w').write(content.replace('{{EXTENSION_STAGES}}', '').rstrip()+'\n')
" "$doc"
done

# Extension-disabled cleanup: strip any unfilled {{EMPIRICAL_*}} / {{THEORY_LLM_*}}
# placeholders and the <!-- EMPIRICAL_FERTILITY_ADDENDUM --> marker. When the
# corresponding extension is on, the inject blocks above already substituted real
# content; this is a no-op for those placeholders. When an extension is off, this
# leaves the docs and scorer body identical to the pre-edit baseline (lines
# containing only the placeholder are removed whole).
python3 -I - \
    "$P/docs/stage_2.md" \
    "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" \
    "$AGENTS_OUT/scorer.md" "$CODEX_AGENTS_OUT/scorer.toml" "$GEMINI_AGENTS_OUT/scorer.md" "$GROK_AGENTS_OUT/scorer.md" "$OPENCODE_AGENTS_OUT/scorer.md" <<'PYEOF'
import os, re, sys
# Match a whole line that is just {{EMPIRICAL_*}} or {{THEORY_LLM_*}} (with optional
# surrounding whitespace), including its trailing newline. Inline (mid-line)
# occurrences are not used.
LINE_PAT = re.compile(r"^[ \t]*\{\{(EMPIRICAL|THEORY_LLM)_[A-Z0-9_]+\}\}[ \t]*\n", re.MULTILINE)
MARKER_PAT = re.compile(r"^[ \t]*<!-- EMPIRICAL_FERTILITY_ADDENDUM -->[ \t]*\n", re.MULTILINE)
for p in sys.argv[1:]:
    if not os.path.exists(p):
        continue
    with open(p) as f: t = f.read()
    new = LINE_PAT.sub("", t)
    new = MARKER_PAT.sub("", new)
    # {{EMPIRICAL_LOOP_FIELDS}} is inline (appended to the last base loops entry inside
    # the loops object), so LINE_PAT does not catch it. Strip it inline when empirical is
    # off; when empirical is on the injector already replaced it, so this is a no-op.
    new = new.replace("{{EMPIRICAL_LOOP_FIELDS}}", "")
    if new != t:
        with open(p, "w") as f: f.write(new)
PYEOF

# Resolve THEORY_ONLY_GUARD markers in branch-manager across all five runtimes.
# Empirical mode: strip the whole guarded block (body + markers).
# Theory-only mode: strip just the marker lines, keep the rule text.
EMPIRICAL_ENABLED=0
for ext in "${EXTENSIONS[@]}"; do
    [ "$ext" = "empirical" ] && EMPIRICAL_ENABLED=1
done
python3 -I - "$EMPIRICAL_ENABLED" "$AGENTS_OUT/branch-manager.md" "$CODEX_AGENTS_OUT/branch-manager.toml" "$GEMINI_AGENTS_OUT/branch-manager.md" "$GROK_AGENTS_OUT/branch-manager.md" "$OPENCODE_AGENTS_OUT/branch-manager.md" <<'PYEOF'
import re, sys
emp = sys.argv[1] == "1"
if emp:
    pat = re.compile(r"<!-- THEORY_ONLY_GUARD_START -->\n.*?<!-- THEORY_ONLY_GUARD_END -->\n\n?", re.DOTALL)
    repl = ""
else:
    pat = re.compile(r"<!-- THEORY_ONLY_GUARD_(?:START|END) -->\n")
    repl = ""
for p in sys.argv[2:]:
    try:
        with open(p) as f: t = f.read()
    except OSError:
        continue
    new = pat.sub(repl, t)
    if new != t:
        try:
            with open(p, "w") as f: f.write(new)
        except OSError as e:
            print(f"  warn: could not resolve guard in {p}: {e}", file=sys.stderr)
PYEOF

# Resolve EMPIRICAL_FIRST / THEORY_FIRST guard markers in stage docs.
# Pattern mirrors THEORY_ONLY_GUARD: pairs of HTML-comment markers wrap
# alternative content for theory-first vs. empirical-first orchestration.
# When --mode empirical-first is set:
#   - EMPIRICAL_FIRST blocks: keep content, strip just the marker lines
#   - THEORY_FIRST blocks: strip the whole block (markers + content)
# When --mode is unset:
#   - EMPIRICAL_FIRST blocks: strip the whole block
#   - THEORY_FIRST blocks: keep content, strip just the marker lines
# Applied to docs/ only (agent-side mode-conditional content goes via vocab
# overlays in phase 4, not markers).
EMPIRICAL_FIRST_ON=0
[ "$MODE" = "empirical-first" ] && EMPIRICAL_FIRST_ON=1
# EXT_EMPIRICAL_ON gates content that should activate whenever the empirical
# extension is present, regardless of mode. Note: --mode empirical-first
# auto-adds --ext empirical in `_setup_config_resolve_variant_and_modes`, so
# EMPIRICAL_FIRST_ON=1 implies
# EXT_EMPIRICAL_ON=1; the converse is not true (theory-first --ext empirical).
EXT_EMPIRICAL_ON=0
EXT_EMPIRICAL_ON="$EMPIRICAL_ENABLED"
# Resolver runs over stage docs, the three runtime docs (CLAUDE.md /
# AGENTS.md / GEMINI.md, assembled from templates/shared/core.md), AND the
# five runtimes' assembled agent files. The agent-file coverage lets shared
# agent bodies (e.g., paper-writer.md) carry inline EMPIRICAL_FIRST /
# THEORY_FIRST / EXT_EMPIRICAL markers — the alternative is a parallel body
# in templates/agent_bodies/shared_modes/{mode}/, which is more duplication
# when the body's mode-specific delta is small. Vocab substitution runs at
# assembly time (before this resolver fires), so {{KEY}} placeholders are
# already resolved when the resolver sees the agent files.
python3 -I - "$MODE" "$EXT_EMPIRICAL_ON" "$VARIANT" "$P/docs/"*.md "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" \
    "$AGENTS_OUT"/*.md "$CODEX_AGENTS_OUT"/*.toml "$GEMINI_AGENTS_OUT"/*.md "$GROK_AGENTS_OUT"/*.md "$OPENCODE_AGENTS_OUT"/*.md <<'PYEOF'
import os, re, sys
mode = sys.argv[1]  # "", "empirical-first", "measurement-first", "report"
xe = sys.argv[2] == "1"
variant = sys.argv[3].upper()

def keep(name):
    """Marker-family semantics per mode. THEORY_FIRST = any theory-shaped
    pipeline (the no-mode default AND measurement-first, whose output is still
    a theory paper produced evidence-first). NO_MODE = strictly the modeless
    default — use it for THEORY_FIRST sites whose content a mode-specific
    block replaces (a site carrying both a NO_MODE and a MEASUREMENT_FIRST
    block renders exactly one of them in every mode). Report mode copies no
    stage docs and prunes the marker-carrying generative agents, so it takes
    the default branch."""
    if mode == "empirical-first":
        return name == "EMPIRICAL_FIRST"
    if mode == "measurement-first":
        return name in ("THEORY_FIRST", "MEASUREMENT_FIRST")
    return name in ("THEORY_FIRST", "NO_MODE")

patterns = []  # list of (regex, replacement) applied in order
# Trailing \n after END markers is optional so a marker at EOF (no final
# newline) still matches; otherwise the literal HTML comment leaks into the
# deployed file.
# ORDER MATTERS: every block REMOVAL runs before any marker STRIP. The removal
# pattern eats up to 2 trailing newlines (to collapse the blank line a removed
# block would otherwise leave behind). If a neighbouring block's markers were
# already stripped, that removal sees the neighbour's exposed leading blank line
# and eats it too — silently deleting a blank line from the kept content. That
# is invisible in single-block files and only shows up once two mode blocks sit
# adjacent at the same site (e.g. NO_MODE + MEASUREMENT_FIRST before an
# EMPIRICAL_FIRST twin). Doing all removals first makes the result independent
# of family order, so adding a mode block at an existing site cannot perturb the
# other modes' output.
_families = ("THEORY_FIRST", "EMPIRICAL_FIRST", "MEASUREMENT_FIRST", "NO_MODE")
for fam in _families:
    if not keep(fam):
        patterns.append((re.compile(r"<!-- " + fam + r"_START -->\n.*?<!-- " + fam + r"_END -->\n{0,2}", re.DOTALL), ""))
for fam in _families:
    if keep(fam):
        patterns.append((re.compile(r"<!-- " + fam + r"_(?:START|END) -->\n?"), ""))
if xe:
    patterns.append((re.compile(r"<!-- EXT_EMPIRICAL_(?:START|END) -->\n?"), ""))
else:
    patterns.append((re.compile(r"<!-- EXT_EMPIRICAL_START -->\n.*?<!-- EXT_EMPIRICAL_END -->\n{0,2}", re.DOTALL), ""))
# Variant markers: <!-- VARIANT_{NAME}_START/END --> blocks are kept (markers
# stripped) when {NAME} matches the deploying variant (uppercased) and removed
# wholesale otherwise. Generic — a new variant needs no resolver edit. The
# matching-variant unwrap runs first so the wholesale pattern (backreference-
# paired, so mismatched START/END names never span) only sees foreign blocks.
# CAUTION: never INTERLEAVE two differently-named marker blocks
# (A_START … B_START … A_END … B_END) — the non-greedy wholesale removal
# would swallow the embedded B_START and leak an orphaned B_END into the
# deployed file. Nesting (B fully inside A) and siblings are both fine.
# The same fragility exists in the mode-marker patterns above.
patterns.append((re.compile(r"<!-- VARIANT_" + re.escape(variant) + r"_(?:START|END) -->\n?"), ""))
patterns.append((re.compile(r"<!-- VARIANT_([A-Z0-9_]+)_START -->\n.*?<!-- VARIANT_\1_END -->\n{0,2}", re.DOTALL), ""))
for p in sys.argv[4:]:
    if not os.path.exists(p):
        continue
    with open(p) as f: t = f.read()
    new = t
    for rx, repl in patterns:
        new = rx.sub(repl, new)
    if new != t:
        with open(p, "w") as f: f.write(new)
PYEOF

# Re-run seed-override substitution now that extension docs have been copied into $P/docs/.
# Extensions may ship stage docs (e.g., stage_3a_empirical.md) containing {{SEED_OVERRIDE_*}} placeholders.
apply_seed_overrides

echo "  ✓ Codex custom agents assembled"

# ── Apply model-availability remap to assembled Claude agents ──
# Single post-assembly pass (after base + variant + every extension agent exists):
# rewrite the `model:` frontmatter for any model the probe found unavailable,
# repointing it to the resolved fallback. Claude agents dir only — see the
# "Resolve unavailable Claude subagent models" block above for rationale.
if [ ${#MODEL_REMAP_ARGS[@]} -gt 0 ]; then
    python3 "$TEMPLATE_ROOT/scripts/apply_model_remap.py" --dir "$AGENTS_OUT" "${MODEL_REMAP_ARGS[@]}"
    echo "  ✓ Subagent model remap applied to $AGENTS_OUT"
fi

}
