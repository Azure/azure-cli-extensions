#!/usr/bin/env bash

set -ev
pip install requests

echo $(pwd)

python scripts/ci/sync_extensions.py
