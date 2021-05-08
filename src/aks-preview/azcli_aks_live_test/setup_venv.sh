#!/bin/bash

set -eux
pwd
ls -alh

# delete existing venv
rm -rf azEnv || true

# install python packages
python$PYTHON_VERSION -m venv azEnv
source azEnv/bin/activate
python -m pip install -U pip
# fixed azdev version to avoid call failure in az_aks_tool
pip install azdev==0.1.32
# install pytest plugins
pip install pytest-json-report pytest-rerunfailures --upgrade
# pip install pytest-html --upgrade
# module for measuring code coverage
pip install coverage

# pre-install: check existing az 
which az || az version || az extension list || true

# install az from cloned repos with azdev
azdev setup -c azure-cli/ -r azure-cli-extensions/
deactivate
source azEnv/bin/activate

# post-install: check installation result
which az
az version

# mkdir to store reports
mkdir -p reports/
