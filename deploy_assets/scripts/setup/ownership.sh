#!/usr/bin/env bash
# Structural ownership boundary for setup.sh.
#
# Template-owned outputs use infrastructure_* helpers, which create/install and
# register the replacement unit in the same call. Mutable project bootstrap
# content uses bootstrap_* helpers and is never inferred to be update-managed.
# Numeric order preserves manifest v1's historical array order; ties sort by
# path (used for extension-installed flat utility files).

setup_ownership_init() {
    OWNERSHIP_TMPDIR="$(mktemp -d "${TMPDIR:-/tmp}/setup-ownership.XXXXXX")"
    INFRA_DIRS_REGISTRY="$OWNERSHIP_TMPDIR/dirs.tsv"
    INFRA_FILES_REGISTRY="$OWNERSHIP_TMPDIR/files.tsv"
    BOOTSTRAP_MERGE_REGISTRY="$OWNERSHIP_TMPDIR/env_merge.tsv"
    : > "$INFRA_DIRS_REGISTRY"
    : > "$INFRA_FILES_REGISTRY"
    : > "$BOOTSTRAP_MERGE_REGISTRY"
    export INFRA_DIRS_REGISTRY INFRA_FILES_REGISTRY BOOTSTRAP_MERGE_REGISTRY
}

_setup_ownership_record() {
    local registry="$1" order="$2" rel="$3"
    _setup_ownership_validate_rel "$rel"
    printf '%s\t%s\n' "$order" "$rel" >> "$registry"
}

_setup_ownership_validate_rel() {
    local rel="$1"
    case "$rel" in
        ""|/*|*[[:cntrl:]]*)
            echo "Error: ownership path must be a non-empty project-relative path: $rel" >&2
            exit 1
            ;;
    esac
    case "/$rel/" in
        *//*|*/./*|*/../*)
            echo "Error: ownership path must not contain empty, '.' or '..' components: $rel" >&2
            exit 1
            ;;
    esac
}

_setup_ownership_validate_destination() {
    local rel="$1" rest component current
    _setup_ownership_validate_rel "$rel"
    if [ -L "$P" ]; then
        echo "Error: ownership project root must not be a symlink: $P" >&2
        exit 1
    fi
    rest="$rel"
    current="$P"
    while :; do
        case "$rest" in
            */*) component="${rest%%/*}"; rest="${rest#*/}" ;;
            *) component="$rest"; rest="" ;;
        esac
        current="$current/$component"
        if [ -L "$current" ]; then
            echo "Error: ownership destination must not traverse a symlink: $rel" >&2
            exit 1
        fi
        [ -n "$rest" ] || break
    done
}

_setup_ownership_require_regular_file() {
    local rel="$1"
    if [ ! -f "$P/$rel" ] || [ -L "$P/$rel" ]; then
        echo "Error: infrastructure producer did not create a regular file: $rel" >&2
        exit 1
    fi
}

_setup_ownership_reject_nonregular_target() {
    local rel="$1"
    if [ -e "$P/$rel" ] && [ ! -f "$P/$rel" ]; then
        echo "Error: file destination exists but is not a regular file: $rel" >&2
        exit 1
    fi
}

infrastructure_dir() {
    local order="$1" rel="$2"
    _setup_ownership_validate_destination "$rel"
    mkdir -p "$P/$rel"
    if [ ! -d "$P/$rel" ]; then
        echo "Error: infrastructure producer did not create directory $rel" >&2
        exit 1
    fi
    _setup_ownership_record "$INFRA_DIRS_REGISTRY" "$order" "$rel"
}

infrastructure_file() {
    local order="$1" rel="$2"
    _setup_ownership_validate_destination "$rel"
    _setup_ownership_require_regular_file "$rel"
    _setup_ownership_record "$INFRA_FILES_REGISTRY" "$order" "$rel"
}

infrastructure_optional_file() {
    local order="$1" rel="$2"
    _setup_ownership_validate_destination "$rel"
    _setup_ownership_reject_nonregular_target "$rel"
    if [ -e "$P/$rel" ]; then
        _setup_ownership_require_regular_file "$rel"
        _setup_ownership_record "$INFRA_FILES_REGISTRY" "$order" "$rel"
    fi
}

infrastructure_copy_file() {
    local order="$1" src="$2" rel="$3" dest
    _setup_ownership_validate_destination "$rel"
    _setup_ownership_reject_nonregular_target "$rel"
    dest="$P/$rel"
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    _setup_ownership_require_regular_file "$rel"
    _setup_ownership_record "$INFRA_FILES_REGISTRY" "$order" "$rel"
}

bootstrap_dir() {
    local rel="$1"
    _setup_ownership_validate_destination "$rel"
    mkdir -p "$P/$rel"
    if [ ! -d "$P/$rel" ]; then
        echo "Error: bootstrap producer did not create directory $rel" >&2
        exit 1
    fi
}

bootstrap_copy_file() {
    local src="$1" rel="$2" dest
    _setup_ownership_validate_destination "$rel"
    _setup_ownership_reject_nonregular_target "$rel"
    dest="$P/$rel"
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    if [ ! -f "$dest" ] || [ -L "$dest" ]; then
        echo "Error: bootstrap copy did not create file $rel" >&2
        exit 1
    fi
}

bootstrap_env_merge() {
    local order="$1" rel="$2"
    _setup_ownership_validate_destination "$rel"
    _setup_ownership_require_regular_file "$rel"
    _setup_ownership_record "$BOOTSTRAP_MERGE_REGISTRY" "$order" "$rel"
}

emit_deployment_manifest() {
    local EXT_JSON SEEDED_BOOL FAITHFUL_BOOL MANUAL_BOOL LIGHT_BOOL HALT_ON_CORE_BYPASS_BOOL
# ── Emit deployment manifest ──
# Records what setup.sh produced as "infrastructure" — paths that update.sh
# may overwrite when refreshing a deployed project against a newer template.
# Anything not in this manifest is preserved on update (paper content,
# output/, process_log/, .env values, references.bib, git history, paper/
# arpipeline.sty fingerprint, paper/main.tex, paper/internet_appendix.tex).
EXT_JSON=$(python3 -I -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "${EXTENSIONS[@]}")
# Keep the shell values explicit; the quoted Python boundary parses them below.
SEEDED_BOOL=$([ "$SEEDED" = "1" ] && echo True || echo False)
FAITHFUL_BOOL=$([ "$FAITHFUL" = "1" ] && echo True || echo False)
MANUAL_BOOL=$([ "$MANUAL" = "1" ] && echo True || echo False)
LIGHT_BOOL=$([ "$LIGHT" = "1" ] && echo True || echo False)
HALT_ON_CORE_BYPASS_BOOL=$([ "$HALT_ON_CORE_BYPASS" = "1" ] && echo True || echo False)

SOURCE_KIND="$SOURCE_KIND" \
SOURCE_REPOSITORY="$SOURCE_REPOSITORY" \
SOURCE_COMMIT="$SOURCE_COMMIT" \
SOURCE_DIRTY="$SOURCE_DIRTY" \
SOURCE_CONTENT_DIGEST="$SOURCE_CONTENT_DIGEST" \
SOURCE_UPDATE_CHANNEL="$SOURCE_UPDATE_CHANNEL" \
python3 -I - "$P" "$INFRA_DIRS_REGISTRY" "$INFRA_FILES_REGISTRY" \
    "$BOOTSTRAP_MERGE_REGISTRY" "$EXT_JSON" "$ARP_VERSION" "$ARP_DATE" \
    "$ARP_UUID" "$VARIANT" "$MODE" "$SEEDED_BOOL" "$FAITHFUL_BOOL" "$MANUAL_BOOL" \
    "$LIGHT_BOOL" "$HALT_ON_CORE_BYPASS_BOOL" <<'PYEMIT'
import json
import os
import sys
from pathlib import Path

(
    project_value,
    infrastructure_dirs_registry,
    infrastructure_files_registry,
    bootstrap_merge_registry,
    extensions_json,
    template_version,
    deploy_date,
    deploy_fingerprint,
    variant,
    mode,
    seeded,
    faithful,
    manual,
    light,
    halt_on_core_bypass,
) = sys.argv[1:]
project = Path(project_value)
manifest_path = project / ".deploy_manifest.json"

# Producers register template-owned paths as they create them. update.sh
# nukes-and-replaces each present entry; project bootstrap paths never enter
# these registries and are therefore preserved.
def owned_paths(registry_name, kind):
    entries = []
    for raw in Path(registry_name).read_text().splitlines():
        if not raw:
            continue
        order, rel = raw.split("\t", 1)
        entries.append((int(order), rel))
    result = []
    seen = set()
    for _, rel in sorted(entries, key=lambda item: (item[0], item[1])):
        if rel in seen:
            continue
        seen.add(rel)
        target = project / rel
        if (kind == "dir" and target.is_dir()) or (kind == "file" and target.is_file()):
            result.append(rel)
    return result

infrastructure_dirs = owned_paths(infrastructure_dirs_registry, "dir")
infrastructure_files = owned_paths(infrastructure_files_registry, "file")
env_merge_files = owned_paths(bootstrap_merge_registry, "file")
extensions = json.loads(extensions_json)
manifest = {
    "manifest_version": 1,
    "template_version": template_version,
    "deploy_date": deploy_date,
    "deploy_fingerprint": deploy_fingerprint,
    "source": {
        "kind": os.environ["SOURCE_KIND"],
        "repository": os.environ["SOURCE_REPOSITORY"] or None,
        "commit": os.environ["SOURCE_COMMIT"],
        "dirty": os.environ["SOURCE_DIRTY"] == "true",
        "content_digest": os.environ["SOURCE_CONTENT_DIGEST"],
        "update_channel": os.environ["SOURCE_UPDATE_CHANNEL"],
    },
    "variant": variant,
    "mode": mode,
    "extensions": extensions,
    "flags": {
        "seeded": seeded == "True",
        "faithful": faithful == "True",
        "manual": manual == "True",
        "light": light == "True",
        "halt_on_core_bypass": halt_on_core_bypass == "True",
    },
    "infrastructure": {
        "dirs_replace": infrastructure_dirs,
        "files_replace": infrastructure_files,
        "files_env_merge": env_merge_files,
    },
}

manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
PYEMIT
echo "  ✓ deployment manifest written: .deploy_manifest.json"

}
