#!/usr/bin/env bash
set -euo pipefail

# Resolve absolute path to this script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLES_DIR="$SCRIPT_DIR/samples/aci"

if [[ ! -d "$SAMPLES_DIR" ]]; then
    echo "Samples directory not found: $SAMPLES_DIR" >&2
    exit 1
fi

shopt -s nullglob
for dir in "$SAMPLES_DIR"/*/; do
    # Ensure we only process directories
    [[ -d "$dir" ]] || continue

    template_path="$dir/arm_template.json"
    output_path="$dir/policy_exclude_default_fragment.rego"

    if [[ ! -f "$template_path" ]]; then
        echo "Skipping $dir: missing $template_path" >&2
        continue
    fi

    echo "Generating policy for ${dir%/}" >&2

    PARAMETERS=""
    if [[ -f "$dir/parameters.json" ]]; then
        PARAMETERS="-p $dir/parameters.json"
    fi

    az confcom acipolicygen -a "$template_path" \
        $PARAMETERS \
        --outraw > "$dir/policy.rego"

    az confcom acipolicygen -a "$template_path" \
        $PARAMETERS \
        --exclude-default-fragments \
        --outraw > "$dir/policy_exclude_default_fragment.rego"

    az confcom acipolicygen -a "$template_path" \
        $PARAMETERS \
        --debug-mode \
        --outraw > "$dir/policy_debug.rego"

    az confcom acipolicygen -a "$template_path" \
        $PARAMETERS \
        --disable-stdio \
        --outraw > "$dir/policy_disable_stdio.rego"

    az confcom acipolicygen -a "$template_path" \
        $PARAMETERS \
        --infrastructure-svn "99" \
        --outraw > "$dir/policy_infrastructure_svn.rego"
done
shopt -u nullglob
