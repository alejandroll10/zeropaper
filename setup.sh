#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro] [--ext empirical|theory_llm] [--seed] [--light] [--local]
#
# --local  Skip git clone, use templates from this repo directly.
#          Outputs to test_output/{variant}/ for inspection.
# --ext    Add an extension (can be repeated). Available: empirical, theory_llm
# --seed   Create a seeded-idea project. Creates output/seed/ with instructions.
#          Drop your idea files there before launching. Pipeline starts at seed_triage.
# --light  Use sonnet for all subagents (cheaper/faster). Orchestrator model unchanged.
#
# Legacy: --variant finance_llm is shorthand for --variant finance --ext theory_llm

set -e

# ── Parse arguments ──
PROJECT_NAME=""
VARIANT="finance"
LOCAL=0
NEXT_IS_VARIANT=0
NEXT_IS_EXT=0
SEEDED=0
LIGHT=0
EXTENSIONS=()

for arg in "$@"; do
    case "$arg" in
        --variant)     NEXT_IS_VARIANT=1 ;;
        --ext)         NEXT_IS_EXT=1 ;;
        --seed)        SEEDED=1 ;;
        --light)       LIGHT=1 ;;
        --local)       LOCAL=1 ;;
        --theory-llm)  VARIANT="finance_llm" ;;  # legacy flag
        -*)            echo "Unknown option: $arg"; exit 1 ;;
        *)
            if [ "$NEXT_IS_VARIANT" = "1" ]; then
                VARIANT="$arg"
                NEXT_IS_VARIANT=0
            elif [ "$NEXT_IS_EXT" = "1" ]; then
                EXTENSIONS+=("$arg")
                NEXT_IS_EXT=0
            else
                PROJECT_NAME="$arg"
            fi
            ;;
    esac
done

if [ "$NEXT_IS_VARIANT" = "1" ]; then
    echo "Error: --variant requires a value (finance, macro)"
    exit 1
fi
if [ "$NEXT_IS_EXT" = "1" ]; then
    echo "Error: --ext requires a value (empirical, theory_llm)"
    exit 1
fi

# ── Expand legacy finance_llm variant ──
if [ "$VARIANT" = "finance_llm" ]; then
    VARIANT="finance"
    EXTENSIONS+=("theory_llm")
fi

# ── Variant configuration ──
case "$VARIANT" in
    finance)
        PAPER_TYPE="finance theory paper"
        TARGET_JOURNALS="top-3 finance journal (JF, JFE, RFS)"
        DOMAIN_AREAS="finance theory — asset pricing, corporate finance, information economics, market design, financial intermediation, or behavioral finance"
        JOURNAL_LIST="Top-3 finance: JF, JFE, RFS. Also: Review of Finance, Management Science, JFQA. Top accounting: JAR, JAE, TAR, RAS. Top-5 econ: AER, Econometrica, QJE, JPE, ReStud."
        AGENT_DIR="finance"
        ;;
    macro)
        PAPER_TYPE="macroeconomics theory paper"
        TARGET_JOURNALS="top-5 economics journal (AER, Econometrica, QJE, JPE, ReStud) or leading macro field journal (JME, JEDC, AEJ:Macro)"
        DOMAIN_AREAS="macroeconomics"
        JOURNAL_LIST="Top-5 econ: AER, Econometrica, QJE, JPE, ReStud. Top-3 finance: JF, JFE, RFS. Macro field: JME, JEDC, AEJ:Macro, AEJ:Micro, JIE, JET, RED."
        AGENT_DIR="macro"
        ;;
    *)
        echo "Unknown variant: $VARIANT"
        echo "Available variants: finance, macro"
        exit 1
        ;;
esac

# ── Resolve paths ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR_REL=".claude"
CLAUDE_AGENTS_REL="$CLAUDE_DIR_REL/agents"
CLAUDE_SKILLS_REL="$CLAUDE_DIR_REL/skills"
CLAUDE_SETTINGS_REL="$CLAUDE_DIR_REL/settings.json"
CODEX_DIR_REL=".agents"
CODEX_SUBAGENT_DIR_REL=".codex"
CODEX_AGENTS_REL="$CODEX_SUBAGENT_DIR_REL/agents"
CODEX_SKILLS_REL="$CODEX_DIR_REL/skills"
GEMINI_DIR_REL=".gemini"
GEMINI_AGENTS_REL="$GEMINI_DIR_REL/agents"
GEMINI_SETTINGS_REL="$GEMINI_DIR_REL/settings.json"


MODEL_OVERRIDE_ARGS=()
if [ "$LIGHT" = "1" ]; then
    MODEL_OVERRIDE_ARGS=(--model-override sonnet)
fi

assemble_claude_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        --bodies-dir "$template_root/templates/agent_bodies/shared" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_claude_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    [ -f "$vocab_file" ] && vocab_args=(--vocab "$vocab_file")

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        --shared-bodies-dir "$template_root/templates/agent_bodies/shared" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_codex_subagents_from_parts() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_codex_subagents.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir"
}

assemble_claude_agents_from_parts() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_codex_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"

    assemble_codex_subagents_from_parts \
        "$template_root" \
        "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "$template_root/templates/agent_bodies/shared" \
        "$dest_dir"
}

assemble_codex_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    [ -f "$vocab_file" ] && vocab_args=(--vocab "$vocab_file")

    python3 "$template_root/scripts/assemble_codex_subagents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        --shared-bodies-dir "$template_root/templates/agent_bodies/shared" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir"
}

assemble_gemini_agents_from_parts() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_gemini_agents.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_gemini_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"

    assemble_gemini_agents_from_parts \
        "$template_root" \
        "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "$template_root/templates/agent_bodies/shared" \
        "$dest_dir"
}

assemble_gemini_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    [ -f "$vocab_file" ] && vocab_args=(--vocab "$vocab_file")

    python3 "$template_root/scripts/assemble_gemini_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        --shared-bodies-dir "$template_root/templates/agent_bodies/shared" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_claude_skills() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_claude_skills.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir"
}

if [ "$LOCAL" = "1" ]; then
    # Local test mode — no clone, no git, no prereq checks
    PROJECT_NAME="${PROJECT_NAME:-test_output/$VARIANT}"
    TEMPLATE_ROOT="$SCRIPT_DIR"
    OUT_DIR="$SCRIPT_DIR/$PROJECT_NAME"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR/$CLAUDE_AGENTS_REL"
    mkdir -p "$OUT_DIR/$CODEX_AGENTS_REL"
    mkdir -p "$OUT_DIR/$GEMINI_AGENTS_REL"
    # Copy shared project files
    mkdir -p "$OUT_DIR/$CLAUDE_DIR_REL"
    cp "$SCRIPT_DIR/$CLAUDE_SETTINGS_REL" "$OUT_DIR/$CLAUDE_DIR_REL/"
    mkdir -p "$OUT_DIR/$GEMINI_DIR_REL"
    cp "$SCRIPT_DIR/$GEMINI_SETTINGS_REL" "$OUT_DIR/$GEMINI_DIR_REL/"
    cp "$SCRIPT_DIR/.gitignore" "$OUT_DIR/"
    cp "$SCRIPT_DIR/dashboard.html" "$OUT_DIR/"

    echo "Local test mode: $VARIANT → $OUT_DIR"
else
    # Production mode — clone, check prereqs, full setup
    PROJECT_NAME="${PROJECT_NAME:-my-research-paper}"

    echo "Checking prerequisites..."
    missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git >/dev/null 2>&1 || missing+=("git")
    command -v claude >/dev/null 2>&1 || missing+=("claude (npm install -g @anthropic-ai/claude-code)")
    command -v uv >/dev/null 2>&1 || missing+=("uv (curl -LsSf https://astral.sh/uv/install.sh | sh)")
    if [[ "$(uname)" == "Linux" ]]; then
        command -v bwrap >/dev/null 2>&1 || missing+=("bubblewrap (sudo apt-get install bubblewrap)")
    fi
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Missing dependencies:"
        for dep in "${missing[@]}"; do echo "  - $dep"; done
        exit 1
    fi
    echo "All prerequisites found."

    if [ -e "$PROJECT_NAME" ]; then
        echo "Error: $PROJECT_NAME already exists"
        exit 1
    fi

    echo "Cloning template into $PROJECT_NAME..."
    git clone https://github.com/alejandroll10/auto-ai-research-template.git "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    git remote remove origin

    TEMPLATE_ROOT="."
    OUT_DIR="."
fi

# ── Assemble runtime docs ──
echo "Assembling runtime docs for variant: $VARIANT..."

CORE="$TEMPLATE_ROOT/templates/shared/core.md"
RUNTIME_SESSION="$TEMPLATE_ROOT/templates/runtime/claude/session.md"
SCORING_FILE="$TEMPLATE_ROOT/templates/scoring/${AGENT_DIR}.md"

for f in "$CORE" "$RUNTIME_SESSION" "$SCORING_FILE"; do
    if [ ! -f "$f" ]; then
        echo "Error: $f not found"
        exit 1
    fi
done

if [ "$LOCAL" = "1" ]; then
    CLAUDE_MD_OUT="$OUT_DIR/CLAUDE.md"
    AGENTS_MD_OUT="$OUT_DIR/AGENTS.md"
    GEMINI_MD_OUT="$OUT_DIR/GEMINI.md"
else
    CLAUDE_MD_OUT="CLAUDE.md"
    AGENTS_MD_OUT="AGENTS.md"
    GEMINI_MD_OUT="GEMINI.md"
fi

SEED_ARGS=()
if [ "$SEEDED" = "1" ]; then
    SEED_TEMPLATE="$TEMPLATE_ROOT/templates/shared/seed.md"
    if [ ! -f "$SEED_TEMPLATE" ]; then
        echo "Error: seed template not found: $SEED_TEMPLATE"
        exit 1
    fi
    SEED_ARGS=(--seed-block "$SEED_TEMPLATE")
fi

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$RUNTIME_SESSION" \
    --scoring "$SCORING_FILE" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --doc-name "CLAUDE.md" \
    --agent-dir "$CLAUDE_AGENTS_REL" \
    --skill-dir "$CLAUDE_SKILLS_REL" \
    "${SEED_ARGS[@]}" \
    --output "$CLAUDE_MD_OUT"

CODEX_DISCIPLINE="$TEMPLATE_ROOT/templates/runtime/codex/session.md"

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$RUNTIME_SESSION" \
    --scoring "$SCORING_FILE" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --doc-name "AGENTS.md" \
    --agent-dir "$CODEX_AGENTS_REL" \
    --skill-dir "$CODEX_SKILLS_REL" \
    --discipline "$CODEX_DISCIPLINE" \
    "${SEED_ARGS[@]}" \
    --output "$AGENTS_MD_OUT"

GEMINI_DISCIPLINE="$TEMPLATE_ROOT/templates/runtime/gemini/session.md"

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$RUNTIME_SESSION" \
    --scoring "$SCORING_FILE" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --doc-name "GEMINI.md" \
    --agent-dir "$GEMINI_AGENTS_REL" \
    --skill-dir "$GEMINI_DIR_REL/skills" \
    --discipline "$GEMINI_DISCIPLINE" \
    "${SEED_ARGS[@]}" \
    --output "$GEMINI_MD_OUT"

echo "  ✓ Runtime docs assembled (CLAUDE.md + AGENTS.md + GEMINI.md)"

# ── Assemble agents ──
echo "Copying agents..."

if [ "$LOCAL" = "1" ]; then
    AGENTS_OUT="$OUT_DIR/$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$OUT_DIR/$CODEX_AGENTS_REL"
    GEMINI_AGENTS_OUT="$OUT_DIR/$GEMINI_AGENTS_REL"
else
    AGENTS_OUT="$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$CODEX_AGENTS_REL"
    GEMINI_AGENTS_OUT="$GEMINI_AGENTS_REL"
    mkdir -p "$AGENTS_OUT"
    mkdir -p "$CODEX_AGENTS_OUT"
    mkdir -p "$GEMINI_AGENTS_OUT"
fi

assemble_claude_shared_agents "$TEMPLATE_ROOT" "$AGENTS_OUT"
assemble_codex_shared_agents "$TEMPLATE_ROOT" "$CODEX_AGENTS_OUT"
assemble_gemini_shared_agents "$TEMPLATE_ROOT" "$GEMINI_AGENTS_OUT"

if [ -f "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json" ]; then
    assemble_claude_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$AGENTS_OUT"
    assemble_codex_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$CODEX_AGENTS_OUT"
    assemble_gemini_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$GEMINI_AGENTS_OUT"
fi

echo "  ✓ Agents assembled (shared + ${AGENT_DIR})"

# ── Inject variant context into agents ──
VARIANT_BLOCK="
## Variant context
- **Paper type:** ${PAPER_TYPE}
- **Target journals:** ${JOURNAL_LIST}
- **Domain:** ${DOMAIN_AREAS}
"

for agent in literature-scout gap-scout novelty-checker theory-explorer referee referee-freeform scorer scorer-freeform branch-manager paper-writer style; do
    if [ -f "$AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$AGENTS_OUT/$agent.md"
    fi
    if [ -f "$CODEX_AGENTS_OUT/$agent.toml" ]; then
        # Insert before the closing ''' in the TOML multiline string
        # Use awk to find the LAST ''' and insert the block before it
        awk -v block="$VARIANT_BLOCK" '
        { lines[NR] = $0 }
        /^'\'''\'''\''$/ { last = NR }
        END {
            for (i = 1; i <= NR; i++) {
                if (i == last) print block
                print lines[i]
            }
        }' "$CODEX_AGENTS_OUT/$agent.toml" > "$CODEX_AGENTS_OUT/$agent.toml.tmp" \
        && mv "$CODEX_AGENTS_OUT/$agent.toml.tmp" "$CODEX_AGENTS_OUT/$agent.toml"
    fi
    if [ -f "$GEMINI_AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$GEMINI_AGENTS_OUT/$agent.md"
    fi
done
echo "  ✓ Variant context injected into agents"

# ── Create project directories and initial files ──
echo "Creating project structure..."

if [ "$LOCAL" = "1" ]; then
    P="$OUT_DIR"
else
    P="."
fi

mkdir -p "$P/code/analysis" "$P/code/download" "$P/code/tmp" "$P/code/explore"
mkdir -p "$P/data"
mkdir -p "$P/output/stage0" "$P/output/stage1" "$P/output/stage2" "$P/output/stage3" "$P/output/stage3a/figures" "$P/output/stage4" "$P/output/puzzle_triage" "$P/output/post_pipeline"
mkdir -p "$P/paper/sections" "$P/paper/referee_reports"
mkdir -p "$P/process_log/sessions" "$P/process_log/decisions" "$P/process_log/discussions" "$P/process_log/patterns"
mkdir -p "$P/references"

# Copy per-stage documentation (referenced from CLAUDE.md/AGENTS.md/GEMINI.md pointer blocks)
mkdir -p "$P/docs"
cp "$TEMPLATE_ROOT/templates/shared/docs/"*.md "$P/docs/"
# Substitute variant placeholders (same ones assemble_runtime_doc.py handles for core.md)
for _docfile in "$P/docs/"*.md; do
    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g" "$_docfile" && rm "${_docfile}.bak"
done

# Function to substitute {{SEED_OVERRIDE_*}} placeholders in all docs in $P/docs/.
# Called after shared docs copy AND after each extension copies its own docs, so
# extension-specific stage docs (e.g., stage_3b_empirical.md) also get substituted.
apply_seed_overrides() {
    local override_dir="$TEMPLATE_ROOT/templates/shared/seed_overrides"
    [ -d "$override_dir" ] || return 0
    for _override in "$override_dir"/*.md; do
        [ -f "$_override" ] || continue
        local _key
        _key=$(basename "$_override" .md)
        for _docfile in "$P/docs/"*.md; do
            if grep -q "{{$_key}}" "$_docfile"; then
                if [ "$SEEDED" = "1" ]; then
                    python3 -c "
import sys, pathlib
doc = pathlib.Path(sys.argv[1])
override = pathlib.Path(sys.argv[2]).read_text().rstrip()
doc.write_text(doc.read_text().replace('{{' + sys.argv[3] + '}}', override))
" "$_docfile" "$_override" "$_key"
                else
                    # Strip placeholder and any immediately surrounding blank lines
                    python3 -c "
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
key = sys.argv[2]
p.write_text(re.sub(r'\n*\{\{' + re.escape(key) + r'\}\}\n*', '\n\n', p.read_text()))
" "$_docfile" "$_key"
                fi
            fi
        done
    done
}

apply_seed_overrides

# Create seed folder with instructions if --seed
if [ "$SEEDED" = "1" ]; then
    mkdir -p "$P/output/seed"
    cat > "$P/output/seed/README.md" <<'SEEDREADME'
# Seed folder

Drop your idea files here before launching the pipeline. The pipeline will read
everything in this folder as the seeded idea.

You can put anything here: markdown notes, PDFs, paper drafts, evaluation
reports, emails, code snippets — whatever describes the idea you want the
pipeline to develop.

The pipeline reads your files, builds a literature map, assesses maturity, and
enters at the appropriate stage. It will never silently abandon your seeded idea.
If a gate fails, it reports the issue rather than pivoting.
SEEDREADME
    echo "  ✓ Seed folder created at output/seed/ — drop your idea files there before launching"
fi

# Initial pipeline state
if [ "$SEEDED" = "1" ]; then
cat > "$P/process_log/pipeline_state.json" <<'JSONEOF'
{
  "current_stage": "seed_triage",
  "problem_attempt": 1,
  "idea_round": 0,
  "theory_attempt": 1,
  "theory_version": 1,
  "referee_round": 0,
  "pivot_round": 0,
  "fix_empirics_rounds": 0,
  "bib_verify_round": 0,
  "pivot_resolved": null,
  "pivot_history": [],
  "status": "not_started",
  "seeded": true,
  "scores": {},
  "history": []
}
JSONEOF
else
cat > "$P/process_log/pipeline_state.json" <<'JSONEOF'
{
  "current_stage": "stage_0",
  "problem_attempt": 1,
  "idea_round": 0,
  "theory_attempt": 1,
  "theory_version": 1,
  "referee_round": 0,
  "pivot_round": 0,
  "fix_empirics_rounds": 0,
  "bib_verify_round": 0,
  "pivot_resolved": null,
  "pivot_history": [],
  "status": "not_started",
  "scores": {},
  "history": []
}
JSONEOF
fi

touch "$P/process_log/history.md"

echo "  ✓ Project structure created"

# ── Copy .env if available ──
if [ -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env" "$P/.env"
    echo "  ✓ .env copied from template repo"
fi

# ── Install core Python deps ──
if [ "$LOCAL" = "0" ]; then
    uv pip install sympy matplotlib -q 2>/dev/null \
        || echo "Note: install core deps manually: uv pip install sympy matplotlib"
fi

# ── Assemble core skills ──
echo "Assembling core skills..."

if [ "$LOCAL" = "1" ]; then
    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"
else
    SKILLS_OUT="$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$CODEX_SKILLS_REL"
fi

# Codex math skill (available for all variants)
assemble_claude_skills \
    "$TEMPLATE_ROOT" \
    "$TEMPLATE_ROOT/templates/skill_metadata/codex_math_skills.json" \
    "$TEMPLATE_ROOT/templates/skill_bodies/codex_math" \
    "$SKILLS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/codex_math_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/codex_math" \
    --output-dir "$CODEX_SKILLS_OUT"

# Copy codex-math utility scripts
mkdir -p "$P/code/utils/codex_math"
cp "$TEMPLATE_ROOT/templates/utils/codex_math/"*.sh "$P/code/utils/codex_math/"
chmod +x "$P/code/utils/codex_math/"*.sh

# Create codex output directories
mkdir -p "$P/output/codex_audits" "$P/output/codex_proofs" "$P/output/codex_explorations"

# Check for codex CLI (optional dependency — warn, don't fail)
if ! command -v codex >/dev/null 2>&1; then
    echo "  ⚠ codex CLI not found. Install with: npm install -g @openai/codex"
    echo "  ⚠ The codex-math skill will not work until codex is installed."
fi

# Bibliography verification skill (available for all variants)
assemble_claude_skills \
    "$TEMPLATE_ROOT" \
    "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json" \
    "$TEMPLATE_ROOT/templates/skill_bodies/bib_verify" \
    "$SKILLS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/bib_verify" \
    --output-dir "$CODEX_SKILLS_OUT"

# Copy bib-verify utility scripts
mkdir -p "$P/code/utils/bib_verify"
cp "$TEMPLATE_ROOT/templates/utils/bib_verify/"openalex_check.py "$P/code/utils/bib_verify/"
cp "$TEMPLATE_ROOT/templates/utils/bib_verify/"verify_bib.sh "$P/code/utils/bib_verify/"
chmod +x "$P/code/utils/bib_verify/"openalex_check.py "$P/code/utils/bib_verify/"verify_bib.sh

# OpenAlex literature search skill (loaded by literature-scout, gap-scout, novelty-checker)
assemble_claude_skills \
    "$TEMPLATE_ROOT" \
    "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json" \
    "$TEMPLATE_ROOT/templates/skill_bodies/openalex" \
    "$SKILLS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/openalex" \
    --output-dir "$CODEX_SKILLS_OUT"

# Copy OpenAlex utility script
mkdir -p "$P/code/utils/openalex"
cp "$TEMPLATE_ROOT/templates/utils/openalex/"openalex.py "$P/code/utils/openalex/"
chmod +x "$P/code/utils/openalex/"openalex.py

echo "  ✓ Core skills assembled"

# ── Apply extensions ──
if [ "$LOCAL" = "1" ]; then
    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"
else
    SKILLS_OUT="$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$CODEX_SKILLS_REL"
fi

for ext in "${EXTENSIONS[@]}"; do
    case "$ext" in
        theory_llm)
            echo "Applying LLM experiment extension..."
            LIGHT_MODEL=""
            if [ "$LIGHT" = "1" ]; then LIGHT_MODEL="sonnet"; fi
            bash "$TEMPLATE_ROOT/scripts/apply_extension_theory_llm.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$GEMINI_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$LOCAL" \
                "$LIGHT_MODEL"

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
                --output-dir "$CODEX_SKILLS_OUT"

            # Inject stage instructions into runtime docs at {{EXTENSION_STAGES}} placeholder
            INJECT="$TEMPLATE_ROOT/extensions/theory_llm/stages_inject.md"
            for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
                python3 -c "
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
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
                done
            fi

            echo "  ✓ LLM experiment extension applied"
            ;;
        empirical)
            echo "Applying empirical extension..."
            LIGHT_MODEL=""
            if [ "$LIGHT" = "1" ]; then LIGHT_MODEL="sonnet"; fi
            bash "$TEMPLATE_ROOT/scripts/apply_extension_empirical.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$GEMINI_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$AGENT_DIR" \
                "$LOCAL" \
                "$LIGHT_MODEL"

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
                --output-dir "$CODEX_SKILLS_OUT"

            # Inject stage instructions into runtime docs at {{EXTENSION_STAGES}} placeholder
            INJECT="$TEMPLATE_ROOT/extensions/empirical/stages_inject.md"
            for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
                python3 -c "
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
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
                done
            fi

            echo "  ✓ Empirical extension applied (skills + agents)"
            ;;
        *)
            echo "Unknown extension: $ext"
            echo "Available extensions: empirical, theory_llm"
            exit 1
            ;;
    esac
done

# Clean up leftover {{EXTENSION_STAGES}} placeholder from runtime docs
for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
    python3 -c "
import sys; d=sys.argv[1]
content=open(d).read()
open(d,'w').write(content.replace('{{EXTENSION_STAGES}}', '').rstrip()+'\n')
" "$doc"
done

# Re-run seed-override substitution now that extension docs have been copied into $P/docs/.
# Extensions may ship stage docs (e.g., stage_3b_empirical.md) containing {{SEED_OVERRIDE_*}} placeholders.
apply_seed_overrides

echo "  ✓ Codex custom agents assembled"

# ── Local mode: summary and exit ──
if [ "$LOCAL" = "1" ]; then
    echo ""
    echo "=== Assembled CLAUDE.md ==="
    echo "Lines: $(wc -l < "$CLAUDE_MD_OUT")"
    REMAINING=$(grep -c '{{' "$CLAUDE_MD_OUT" 2>/dev/null || true)
    REMAINING="${REMAINING:-0}"
    echo "Placeholders remaining: $REMAINING"
    echo ""
    echo "=== Assembled AGENTS.md ==="
    echo "Lines: $(wc -l < "$AGENTS_MD_OUT")"
    AGENTS_REMAINING=$(grep -c '{{' "$AGENTS_MD_OUT" 2>/dev/null || true)
    AGENTS_REMAINING="${AGENTS_REMAINING:-0}"
    echo "Placeholders remaining: $AGENTS_REMAINING"
    echo ""
    echo "=== Assembled GEMINI.md ==="
    echo "Lines: $(wc -l < "$GEMINI_MD_OUT")"
    GEMINI_REMAINING=$(grep -c '{{' "$GEMINI_MD_OUT" 2>/dev/null || true)
    GEMINI_REMAINING="${GEMINI_REMAINING:-0}"
    echo "Placeholders remaining: $GEMINI_REMAINING"
    echo ""
    echo "=== Agents ($CLAUDE_AGENTS_REL/) ==="
    ls -1 "$AGENTS_OUT/"
    echo ""
    echo "=== Codex Agents ($CODEX_AGENTS_REL/) ==="
    ls -1 "$CODEX_AGENTS_OUT/"
    echo ""
    echo "=== Gemini Agents ($GEMINI_AGENTS_REL/) ==="
    ls -1 "$GEMINI_AGENTS_OUT/"
    if [ -d "$OUT_DIR/$CLAUDE_SKILLS_REL" ]; then
        echo ""
        echo "=== Skills ($CLAUDE_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CLAUDE_SKILLS_REL/"
    fi
    if [ -d "$OUT_DIR/$CODEX_SKILLS_REL" ]; then
        echo ""
        echo "=== Codex Skills ($CODEX_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CODEX_SKILLS_REL/"
    fi
    echo ""
    echo "=== First 10 lines ==="
    head -10 "$CLAUDE_MD_OUT"
    echo ""
    echo "=== Domain section ==="
    grep -A 5 "^## Domain:" "$CLAUDE_MD_OUT" | head -8
    echo ""

    if [ "$REMAINING" -gt 0 ]; then
        echo "WARNING: $REMAINING unresolved placeholders:"
        grep '{{' "$CLAUDE_MD_OUT"
        exit 1
    elif [ "$AGENTS_REMAINING" -gt 0 ]; then
        echo "WARNING: $AGENTS_REMAINING unresolved placeholders:"
        grep '{{' "$AGENTS_MD_OUT"
        exit 1
    elif [ "$GEMINI_REMAINING" -gt 0 ]; then
        echo "WARNING: $GEMINI_REMAINING unresolved placeholders:"
        grep '{{' "$GEMINI_MD_OUT"
        exit 1
    else
        echo "✓ All placeholders resolved"
    fi
    echo ""
    echo "Output at: $OUT_DIR/"
    exit 0
fi

# ── Production mode: clean up and commit ──
echo "Cleaning up template files..."

# Replace template .gitignore with project-specific one (before deleting templates/)
cp templates/gitignore_project .gitignore

rm -rf templates/
rm -rf extensions/
rm -rf meta_paper/
rm -rf test_scripts/
rm -rf scripts/
rm -rf codex_inspect/
rm -rf test_output/
rm -f setup.sh
rm -f README.md
rm -f CLAUDE_REFACTOR_PLAN.md
rm -f requirements.system
rm -f texput.log
echo "  ✓ Template files removed"

git add -A
git commit -m "setup: initialized ${VARIANT} variant pipeline" -q

echo ""
echo "============================================"
echo "  Setup complete: $PROJECT_NAME ($VARIANT)"
echo "============================================"
echo ""
echo "To run the autonomous pipeline:"
echo ""
echo "  cd $PROJECT_NAME"
echo ""
echo "Claude:"
echo "  claude --dangerously-skip-permissions"
echo ""
echo "Codex:"
echo "  codex --sandbox danger-full-access --ask-for-approval never"
echo ""
echo "Gemini:"
echo "  gemini --yolo"
echo ""
echo "Then say: \"Run the pipeline.\""
echo ""
echo "Variant: $VARIANT"
echo "Extensions: ${EXTENSIONS[*]:-none}"
if [ "$LIGHT" = "1" ]; then
    echo "Mode: light (all subagents use sonnet)"
fi
if [ "$SEEDED" = "1" ]; then
    echo "Seeded: drop your idea files in output/seed/ before launching"
    echo "Pipeline will triage seed maturity and enter at the appropriate stage"
fi
echo "Sandbox is pre-configured in $CLAUDE_SETTINGS_REL"
echo "(Bash restricted to project folder, web access works freely)"
