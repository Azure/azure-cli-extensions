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
pip install azdev
pip install pytest-json-report pytest-rerunfailures --upgrade
# pip install pytest-html --upgrade

# check existing az 
which az || az version || az extension list || true

# install latest az
azdev setup -c azure-cli -r azure-cli-extensions
deactivate
source azEnv/bin/activate

# check installation result
which az
az version
