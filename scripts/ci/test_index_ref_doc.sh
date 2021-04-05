#!/usr/bin/env bash
set -ex

# Install CLI
echo "Installing azure-cli..."

pip install "azure-cli" -q
pip install "sphinx==1.7.0" -q
echo "Installed."

python ./scripts/ci/index_ref_doc.py -v

echo "OK."
