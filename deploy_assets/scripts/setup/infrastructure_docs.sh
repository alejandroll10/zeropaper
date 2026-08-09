#!/usr/bin/env bash
# Template-owned stage-document installation and seed-override rendering.
# docs/ is registered as one infrastructure replacement unit by the runtime
# document module; extension docs join the same owned tree later.

setup_infrastructure_docs() {
local _docfile TIER_TABLE_FILE
# Copy per-stage documentation (referenced from CLAUDE.md/AGENTS.md/GEMINI.md pointer blocks).
# Skipped in report mode — there are no stages to document, and the audit
# conventions live in core_report.md itself. The session pointer files
# (start_session_*.md) are written into docs/ separately by --session-out.
mkdir -p "$P/docs"
if [ "$MODE" != "report" ]; then
    cp "$TEMPLATE_ROOT/templates/shared/docs/"*.md "$P/docs/"
    # Substitute variant placeholders (same ones assemble_runtime_doc.py handles for core.md)
    for _docfile in "$P/docs/"*.md; do
        sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g; s|{{INITIAL_TIER}}|$INITIAL_TIER|g; s|{{TIER_LADDER_PROSE}}|$TIER_LADDER_PROSE|g; s|{{TIER_LIST_INLINE}}|$TIER_LIST_INLINE|g; s|{{TIER_DOWNGRADE_EXAMPLES}}|$TIER_DOWNGRADE_EXAMPLES|g; s|{{MECHANISM_QUALIFIER_AN}}|$MECHANISM_QUALIFIER_AN|g; s|{{MECHANISM_QUALIFIER}}|$MECHANISM_QUALIFIER|g; s|{{MECHANISM_DISCIPLINE}}|$MECHANISM_DISCIPLINE|g; s|{{PRINCIPLED_MECHANISM_PHRASE}}|$PRINCIPLED_MECHANISM_PHRASE|g" "$_docfile" && rm "${_docfile}.bak"
    done

    # Inject the variant-specific tier table into stage_4.md (multi-line content via sed -r)
    TIER_TABLE_FILE="$TEMPLATE_ROOT/templates/shared/tier_tables/${VARIANT}.md"
    if [ -f "$TIER_TABLE_FILE" ] && [ -f "$P/docs/stage_4.md" ]; then
        sed -i.bak -e "/{{TIER_TABLE}}/r $TIER_TABLE_FILE" -e "/{{TIER_TABLE}}/d" "$P/docs/stage_4.md" && rm "$P/docs/stage_4.md.bak"
    fi
else
    # Report mode skips the bulk stage-doc copy, but the core-bypass guard still
    # applies (the audit agents verify an external submission against binding
    # sources like OpenAlex). Copy just the doctrine doc the injected agent
    # pointer references. It has no variant placeholders, so no substitution.
    cp "$TEMPLATE_ROOT/templates/shared/docs/core_bypass.md" "$P/docs/"
fi

# Function to substitute {{SEED_OVERRIDE_*}} placeholders in all docs in $P/docs/.
# Called after shared docs copy AND after each extension copies its own docs, so
# extension-specific stage docs (e.g., stage_3a_empirical.md) also get substituted.
#
# Resolution order for each placeholder:
#   1. Collect placeholder keys: union of seed_overrides/*.md and (if FAITHFUL=1)
#      faithful_overrides/*.md basenames.
#   2. For each key, pick the override body:
#      - FAITHFUL=1: prefer faithful_overrides/<key>.md, fall back to
#        seed_overrides/<key>.md if no faithful version exists. This lets us
#        write only the *strict-delta* faithful overrides — for placeholders
#        where seeded behavior is already strict enough, faithful mode reuses
#        the seeded text.
#      - SEEDED=1 (and not FAITHFUL): use seed_overrides/<key>.md only.
#      - Neither: strip the placeholder.
apply_seed_overrides() {
    local seed_override_dir="$TEMPLATE_ROOT/templates/shared/seed_overrides"
    local faithful_override_dir="$TEMPLATE_ROOT/templates/shared/faithful_overrides"

    # Build the union of placeholder keys across both dirs.
    local _keys=()
    if [ -d "$seed_override_dir" ]; then
        for _f in "$seed_override_dir"/*.md; do
            [ -f "$_f" ] && _keys+=("$(basename "$_f" .md)")
        done
    fi
    # Always include faithful_overrides keys in the union — even when FAITHFUL=0.
    # This ensures placeholders that exist only in the faithful set (e.g., the
    # Stage 1 INCREMENTAL-forwarding override) get stripped cleanly in regular
    # and soft-seed modes rather than leaking into the deployed docs as raw
    # `{{SEED_OVERRIDE_*}}` text. The body-resolution step below still picks
    # the faithful body only when FAITHFUL=1.
    if [ -d "$faithful_override_dir" ]; then
        for _f in "$faithful_override_dir"/*.md; do
            [ -f "$_f" ] || continue
            local _k="$(basename "$_f" .md)"
            # Only add if not already in _keys (dedupe).
            local _found=0
            for _existing in "${_keys[@]:-}"; do
                [ "$_existing" = "$_k" ] && { _found=1; break; }
            done
            [ "$_found" = "0" ] && _keys+=("$_k")
        done
    fi

    [ "${#_keys[@]}" -eq 0 ] && return 0

    for _key in "${_keys[@]}"; do
        # Pick the override body for this key per the resolution order above.
        local _override=""
        if [ "$FAITHFUL" = "1" ] && [ -f "$faithful_override_dir/$_key.md" ]; then
            _override="$faithful_override_dir/$_key.md"
        elif [ "$SEEDED" = "1" ] && [ -f "$seed_override_dir/$_key.md" ]; then
            _override="$seed_override_dir/$_key.md"
        fi

        for _docfile in "$P/docs/"*.md; do
            grep -q "{{$_key}}" "$_docfile" || continue
            if [ -n "$_override" ]; then
                python3 -c "
import sys, pathlib
doc = pathlib.Path(sys.argv[1])
override = pathlib.Path(sys.argv[2]).read_text().rstrip()
doc.write_text(doc.read_text().replace('{{' + sys.argv[3] + '}}', override))
" "$_docfile" "$_override" "$_key"
            else
                # Strip placeholder and any immediately surrounding blank lines.
                python3 -c "
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
key = sys.argv[2]
p.write_text(re.sub(r'\n*\{\{' + re.escape(key) + r'\}\}\n*', '\n\n', p.read_text()))
" "$_docfile" "$_key"
            fi
        done
    done
}

apply_seed_overrides
}
