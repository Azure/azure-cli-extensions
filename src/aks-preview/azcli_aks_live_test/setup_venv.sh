#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
PYTHON_VERSION=${PYTHON_VERSION:-"3.8"}

# dir
pwd
ls -alh

# delete existing venv
rm -rf azEnv || true

# install python packages
python${PYTHON_VERSION} -m venv azEnv
source azEnv/bin/activate
python -m pip install -U pip
# install azdev, used later to install azcli and extension
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

# post-install: reactivate venv to check installation result
source azEnv/bin/activate
which az && az version

# mkdir to store reports
mkdir -p reports/

# export PYTHONPATH
export PYTHONPATH=$(pwd)
