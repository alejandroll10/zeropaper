# Shared .env key-merge routine. Build-time only (sourced by setup.sh and
# update.sh from the template checkout; removed with the rest of scripts/ on
# deploy, so no deployment-manifest entry).
#
# Single implementation on purpose: setup.sh (union of the repo's personal
# .env with .env.example at deploy time) and update.sh (merging new template
# keys into existing deployments) must stay byte-identical in their edge-case
# handling — a divergent second copy is how the v2.11.1 silent-key-drop bug
# class reappears.

# merge_env_missing_keys <source_env> <target_env> [dry_run 0|1]
# Appends every KEY=... line present in source but absent from target. Never
# overwrites an existing key's value. Prints "  + KEY" per addition and sets
# MERGE_ENV_ADDED to the number of keys added.
merge_env_missing_keys() {
    local src="$1" target="$2" dry_run="${3:-0}" line key
    MERGE_ENV_ADDED=0
    # `|| [ -n "$line" ]` catches a final line with no trailing newline: plain
    # `read` sets the variable but returns non-zero at EOF, so the loop body
    # would skip it and that key would be silently dropped from the merge.
    # Editors that don't terminate the last line are common.
    while IFS= read -r line || [ -n "$line" ]; do
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        key="${line%%=*}"
        if ! grep -q "^${key}=" "$target" 2>/dev/null; then
            if [ "$dry_run" = "1" ]; then
                echo "  + $key (would add)"
            else
                # Guard the receiving side too: if the target's last line is
                # unterminated, a bare append would concatenate onto it and
                # corrupt both keys.
                [ -s "$target" ] && [ -n "$(tail -c1 "$target")" ] \
                    && printf '\n' >> "$target"
                echo "$line" >> "$target"
                echo "  + $key"
            fi
            MERGE_ENV_ADDED=$((MERGE_ENV_ADDED+1))
        fi
    done < "$src"
}
