#!/usr/bin/env bash
set -e

export AZDEV_CLI_REPO_PATH='_NONE_'
export AZDEV_EXT_REPO_PATHS=$(pwd)

azdev setup -r $AZDEV_CLI_REPO_PATH
azdev style --pylint

# Run pylint/flake8 on CI files
pylint ./scripts/ci/*.py  --rcfile=./pylintrc
flake8 --append-config=./.flake8 ./scripts/ci/*.py

# Other static checks
azdev verify license
python ./scripts/ci/verify_codeowners.py

