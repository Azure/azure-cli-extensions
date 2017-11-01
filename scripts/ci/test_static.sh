#!/usr/bin/env bash
set -e

proc_number=`python -c 'import multiprocessing; print(multiprocessing.cpu_count())'`
pylint ./src/*/azext_*/ --rcfile=./pylintrc -j $proc_number
flake8 --statistics --append-config=./.flake8 ./src/*/azext_*/

pylint ./scripts/ci/*.py  --rcfile=./pylintrc
flake8 --append-config=./.flake8 ./scripts/ci/*.py

python ./scripts/ci/verify_codeowners.py
python ./scripts/ci/verify_license.py
