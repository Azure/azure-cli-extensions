#!/usr/bin/env bash
set -ex

az --version
python ./scripts/ci/test_min_version.py -v

echo "Finish azure cli min version test."
