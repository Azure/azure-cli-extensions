#!/usr/bin/env bash

# check var
[[ -z "${PYTHON_VERSION}" ]] && (echo "PYTHON_VERSION is empty"; exit 1)

setupVenv(){
    # delete existing venv
    deactivate || true
    rm -rf azEnv || true

    # create new venv
    python${PYTHON_VERSION} -m venv azEnv
    source azEnv/bin/activate
    python -m pip install -U pip
}

installBuildTools(){
    pip install tox
    pip install -U build
}

setupAZ(){
    cli_repo=${1:-"."}
    ext_repo=${2:-""}

    # install azdev, used later to install azcli and extension
    pip install azdev==0.1.32

    # pre-install-az: check existing az
    which az || az version || az extension list || true

    # install-az: from cloned repos with azdev
    if [[ -z ${ext_repo} ]]; then
        azdev setup -c ${cli_repo}
    else
        azdev setup -c ${cli_repo} -r ${ext_repo}
    fi

    # post-install-az: check installation result
    which az && az version
}

installTestPackages(){
    # install pytest plugins
    pip install pytest-json-report pytest-rerunfailures --upgrade

    # install coverage for measuring code coverage
    pip install coverage
}

installAZAKSTOOLFromLocal(){
    wheel_file=${1}
    pip install ${wheel_file}
}

installAZAKSTOOL(){
    wheel_file="az_aks_tool-latest-py3-none-any.whl"
    wheel_url="https://akspreview.blob.core.windows.net/azakstool/${wheel_file}"
    curl -sLO ${wheel_url}
    installAZAKSTOOLFromLocal ${wheel_file}
}

removeKustoPTHFile(){
    pushd azEnv/lib/python${PYTHON_VERSION}/site-packages
    rm azure_kusto_data*nspkg.pth
    rm azure_kusto_ingest*nspkg.pth
    popd
}

if [[ -n ${1} ]]; then
    # bash options
    set -o errexit
    set -o nounset
    set -o pipefail
    set -o xtrace

    # create new venv if second arg is not "n"
    new_venv=${2:-"y"}
    if [[ ! ${new_venv} == "n" ]]; then
        echo "Create new venv!"
        setupVenv
    fi

    if [[ ${1} == "build" ]]; then
        echo "Start to build az-aks-tool!"
        installBuildTools
    elif [[ ${1} == "setuptool" ]]; then
        echo "Start to setup az-aks-tool!"
        local_setup=${3:-"n"}
        if [[ ${local_setup} == "y" ]]; then
            wheel_file=${4}
            installAZAKSTOOLFromLocal ${wheel_file}
        else
            installAZAKSTOOL
        fi
        removeKustoPTHFile
    elif [[ ${1} == "setupaz" ]]; then
        echo "Start to setup azure-cli!"
        cli_repo=${3:-"azure-cli/"}
        ext_repo=${4:-""}
        setupAZ ${cli_repo} ${ext_repo}
        installTestPackages
    else
        echo "Unknown arg '${1}'!"
    fi
    echo "All Done!"
fi
