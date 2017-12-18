#!/usr/bin/env bash
set -e

proc_number=`python -c 'import multiprocessing; print(multiprocessing.cpu_count())'`

# Run pylint/flake8 on extensions
# - We ignore 'models' and 'operations' as they typically come from vendored Azure SDKs
pylint ./src/*/azext_*/ --ignore=models,operations --rcfile=./pylintrc -j $proc_number
flake8 --statistics --exclude=models,operations --append-config=./.flake8 ./src/*/azext_*/

# Run pylint/flake8 on CI files
pylint ./scripts/ci/*.py  --rcfile=./pylintrc
flake8 --append-config=./.flake8 ./scripts/ci/*.py

# Other static checks
python ./scripts/ci/verify_codeowners.py
python ./scripts/ci/verify_license.py
