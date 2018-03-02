#!/usr/bin/env bash
set -e

proc_number=`python -c 'import multiprocessing; print(multiprocessing.cpu_count())'`

# Run pylint/flake8 on extensions
# - We ignore 'models', 'operations' and files with suffix '_client.py' as they typically come from vendored Azure SDKs
pylint ./src/*/azext_*/ --ignore=models,operations,service_bus_management_client,subscription_client,managementgroups,managementpartner --ignore-patterns=[a-zA-Z_]+_client.py --rcfile=./pylintrc -j $proc_number
flake8 --statistics --exclude=models,operations,*_client.py,managementgroups,managementpartner --append-config=./.flake8 ./src/*/azext_*/

# Run pylint/flake8 on CI files
pylint ./scripts/ci/*.py  --rcfile=./pylintrc
flake8 --append-config=./.flake8 ./scripts/ci/*.py

# Other static checks
python ./scripts/ci/verify_codeowners.py
python ./scripts/ci/verify_license.py
