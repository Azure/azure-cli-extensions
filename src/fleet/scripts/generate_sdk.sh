#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# generate_sdk.sh – Regenerate the Fleet vendored Python SDK from a
# azure-rest-api-specs branch. Deletes the old vendored SDK directory
# entirely and adds the newly generated files.
#
# The --branch value is used to construct the autorest readme URL:
#   https://raw.githubusercontent.com/Azure/azure-rest-api-specs/<BRANCH>/
#     specification/containerservice/resource-manager/
#     Microsoft.ContainerService/fleet/readme.md
#
# The spec path is always the same across branches; only the branch name
# changes. For example, branch "dev-aks-fleet-2026-05-01-preview" points to:
#   .../tree/dev-aks-fleet-2026-05-01-preview/.../fleet/readme.md
#
# Usage:
#   ./scripts/generate_sdk.sh <api-version> [--branch <branch>] [--tag <autorest-tag>]
#
# Examples:
#   # From main (default branch, default tag = package-<api-version>):
#   ./scripts/generate_sdk.sh 2026-03-02-preview
#
#   # From a dev branch (typical for new API versions):
#   ./scripts/generate_sdk.sh 2026-05-01-preview \
#       --branch dev-aks-fleet-2026-05-01-preview
#
#   # With an explicit autorest tag (only needed when the tag in the spec
#   # readme.md doesn't follow the "package-<api-version>" convention):
#   ./scripts/generate_sdk.sh 2026-05-01-preview \
#       --branch dev-aks-fleet-2026-05-01-preview \
#       --tag package-preview-2026-05
# ---------------------------------------------------------------------------
set -euo pipefail

# ── Resolve paths ─────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLEET_EXT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENDORED_DIR="${FLEET_EXT_DIR}/azext_fleet/vendored_sdks"

# ── Parse arguments ───────────────────────────────────────────────────────
API_VERSION=""
BRANCH="main"
TAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --branch|-b) BRANCH="$2"; shift 2 ;;
        --tag|-t)    TAG="$2";    shift 2 ;;
        --help|-h)
            head -20 "$0" | grep '^#' | sed 's/^# \?//'
            exit 0
            ;;
        *)
            if [[ -z "$API_VERSION" ]]; then
                API_VERSION="$1"; shift
            else
                echo "ERROR: Unknown argument: $1" >&2; exit 1
            fi
            ;;
    esac
done

if [[ -z "$API_VERSION" ]]; then
    echo "ERROR: api-version is required." >&2
    echo "Usage: $0 <api-version> [--branch <branch>] [--tag <tag>]" >&2
    exit 1
fi

# Derive the autorest tag if not explicitly provided.
# Convention: package-<api-version>  (e.g. package-2026-03-02-preview)
TAG="${TAG:-package-${API_VERSION}}"

# Convert API version to the Python folder name: 2026-03-02-preview → v2026_03_02_preview
FOLDER_NAME="v$(echo "${API_VERSION}" | tr '-' '_')"

# If the branch looks like a full GitHub URL, extract just the branch name.
# e.g. https://github.com/Azure/azure-rest-api-specs/tree/<branch>/specification/...
if [[ "$BRANCH" == https://github.com/* ]]; then
    BRANCH="$(echo "$BRANCH" | sed -E 's|https://github.com/[^/]+/[^/]+/tree/([^/]+).*|\1|')"
fi

# ── Configuration ─────────────────────────────────────────────────────────
# The fleet spec readme path is fixed; only the branch changes.
SPEC_README="https://raw.githubusercontent.com/Azure/azure-rest-api-specs/${BRANCH}/specification/containerservice/resource-manager/Microsoft.ContainerService/fleet/readme.md"
TMP_DIR="$(mktemp -d)"
SDK_OUTPUT="${TMP_DIR}/containerservice/azure-mgmt-containerservicefleet/azure/mgmt/containerservicefleet"

echo "========================================"
echo "Fleet SDK Generation"
echo "========================================"
echo "  API version : ${API_VERSION}"
echo "  Autorest tag: ${TAG}"
echo "  Branch      : ${BRANCH}"
echo "  Folder name : ${FOLDER_NAME}"
echo "  Spec readme : ${SPEC_README}"
echo "  Temp dir    : ${TMP_DIR}"
echo "  Output      : ${VENDORED_DIR}/${FOLDER_NAME}"
echo "========================================"

# ── Generate ──────────────────────────────────────────────────────────────
echo ""
echo "Running autorest..."
autorest "${SPEC_README}" \
    --python \
    --multiapi \
    --tag="${TAG}" \
    --version-tolerant=false \
    --python-sdks-folder="${TMP_DIR}" \
    --use=@autorest/python

# Verify output exists
if [[ ! -d "$SDK_OUTPUT" ]]; then
    echo "ERROR: autorest did not produce expected output at ${SDK_OUTPUT}" >&2
    echo "Contents of tmp dir:" >&2
    find "$TMP_DIR" -maxdepth 4 -type d >&2
    exit 1
fi

# ── Delete old SDK and add generated files ────────────────────────────────
TARGET_DIR="${VENDORED_DIR}/${FOLDER_NAME}"

if [[ -d "$TARGET_DIR" ]]; then
    echo ""
    echo "Deleting existing SDK directory at ${TARGET_DIR}..."
    rm -rf "$TARGET_DIR"
fi

echo "Adding generated SDK to ${TARGET_DIR}..."
cp -r "$SDK_OUTPUT" "$TARGET_DIR"

# Remove __pycache__ directories if any were generated
find "$TARGET_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Remove old API version folders (any v20* directory that isn't the one we just generated)
for old_dir in "${VENDORED_DIR}"/v20*/; do
    old_dir="${old_dir%/}"  # strip trailing slash
    if [[ -d "$old_dir" && "$old_dir" != "$TARGET_DIR" ]]; then
        echo "Removing old SDK version: $(basename "$old_dir")"
        rm -rf "$old_dir"
    fi
done

# ── Update vendored_sdks/__init__.py ──────────────────────────────────────
INIT_FILE="${VENDORED_DIR}/__init__.py"
echo ""
echo "Updating ${INIT_FILE} to reference ${FOLDER_NAME}..."

cat > "$INIT_FILE" << EOF
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import sys

from .${FOLDER_NAME} import ContainerServiceFleetMgmtClient
from .${FOLDER_NAME} import models as _models
from .${FOLDER_NAME} import operations as _operations

# Register the versioned sub-packages under short aliases so that
# import paths like "azext_fleet.vendored_sdks.operations._fleets_operations"
# and model resolution via cmd.get_models() both work without embedding the
# API version string everywhere.
sys.modules[__name__ + ".models"] = _models
sys.modules[__name__ + ".operations"] = _operations

# Also register every submodule that was eagerly loaded under ${FOLDER_NAME}
# so that lazy imports via the aliased path (used by CLI operations_tmpl) find
# them in sys.modules and don't re-import with the wrong __package__.
_v = __name__ + ".${FOLDER_NAME}"
for _key in list(sys.modules):
    if _key.startswith(_v + "."):
        _alias = __name__ + _key[len(_v):]
        sys.modules.setdefault(_alias, sys.modules[_key])

__all__ = ["ContainerServiceFleetMgmtClient"]
EOF

# ── Cleanup ───────────────────────────────────────────────────────────────
rm -rf "$TMP_DIR"

echo ""
echo "========================================"
echo "Done! SDK generated at: ${TARGET_DIR}"
echo ""
echo "Next steps:"
echo "  1. Review the generated files in ${FOLDER_NAME}/"
echo "  2. Verify old API version folder(s) were removed from vendored_sdks/"
echo "  3. Update azext_metadata.json if the min CLI version changed"
echo "  4. Run: azdev style fleet && azdev linter fleet"
echo "  5. Run: azdev test fleet --discover --live"
echo "========================================"
