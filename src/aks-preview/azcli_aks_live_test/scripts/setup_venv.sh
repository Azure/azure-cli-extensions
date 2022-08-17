#!/usr/bin/env bash

# check var
# specify the version of python3, e.g. 3.6
[[ -z "${PYTHON_VERSION}" ]] && (echo "PYTHON_VERSION is empty"; exit 1)
[[ -z "${ACS_BASE_DIR}" ]] && (echo "ACS_BASE_DIR is empty"; exit 1)

setupVenv(){
    # delete existing venv
    deactivate || true
    rm -rf azEnv || true

    # create new venv
    python"${PYTHON_VERSION}" -m venv azEnv
    source azEnv/bin/activate
    python -m pip install -U pip
}

# need to be executed in a venv
installBuildTools(){
    pip install tox coverage
    pip install -U build
}

# need to be executed in a venv
setupAZ(){
    cli_repo=${1:-"."}
    ext_repo=${2:-""}

    # install azdev, used later to install azcli and extension
    # TODO: update to a new version with dependency version fixed
    pip install azdev==0.1.36

    # pre-install-az: check existing az
    which az || az version || az extension list || true

    # install-az: from cloned repos with azdev
    if [[ -z ${ext_repo} ]]; then
        azdev setup -c "${cli_repo}"
    else
        azdev setup -c "${cli_repo}" -r "${ext_repo}"
    fi

    # post-install-az: check installation result
    which az && az version
}

# need to be executed in a venv
installTestPackages(){
    # install pytest plugins
    pip install pytest-json-report pytest-rerunfailures pytest-cov --upgrade

    # install coverage for measuring code coverage
    pip install coverage
}

# need to be executed in a venv
installAZAKSTOOLFromLocal(){
    wheel_file=${1}
    pip install "${wheel_file}"
    pip show az-aks-tool
}

# need to be executed in a venv
installAZAKSTOOL(){
    wheel_file="az_aks_tool-latest-py3-none-any.whl"
    wheel_url="https://akspreview.blob.core.windows.net/azakstool/${wheel_file}"
    curl -sLO "${wheel_url}"
    installAZAKSTOOLFromLocal "${wheel_file}"
}

# need to be executed in a venv with kusto related modules installed
removeKustoPTHFile(){
    pushd azEnv/lib/python"${PYTHON_VERSION}"/site-packages
    rm azure_kusto_data*nspkg.pth
    rm azure_kusto_ingest*nspkg.pth
    popd
}

# need to be executed in a venv after 'setupAZ'
igniteAKSPreview(){
    # use a fake command to force trigger the command index update of azure-cli, in order to load aks-preview commands
    # otherwise, cold boot execution of azdev test / pytest would only use commands in the acs module
    az aks fake-command --debug || true
}

# need to be executed in a venv
removeAKSPreview(){
    # remove extension
    echo "Remove existing aks-preview extension (if any)"
    if az extension remove --name aks-preview || azdev extension remove aks-preview; then
        deactivate
        source azEnv/bin/activate
    fi
}

# need to be executed in a venv after 'setupAZ'
setupAKSPreview(){
    # remove extension
    removeAKSPreview

    # install latest extension
    echo "Install the latest aks-preview extension and re-activate the virtualenv"
    azdev extension add aks-preview
    az extension list
    azdev extension list | grep "aks-preview" -C 5
    deactivate
    source azEnv/bin/activate
}

createSSHKey(){
    # create ssh-key in advance to avoid the race condition that is prone to occur when key creation is handled by
    # azure-cli when performing test cases concurrently, this command will not overwrite the existing ssh-key
    custom_ssh_dir=${1:-"${ACS_BASE_DIR}/tests/latest/data/.ssh"}
    # remove dir if exists (clean up), otherwise create it
    if [[ -d ${custom_ssh_dir} ]]; then
        rm -rf ${custom_ssh_dir}
    else
        mkdir -p ${custom_ssh_dir}
    fi
    ssh-keygen -t rsa -b 2048 -C "azcli_aks_live_test@example.com" -f ${custom_ssh_dir}/id_rsa -N "" -q <<< n
}

setup_option=${1:-""}
if [[ -n ${setup_option} ]]; then
    # bash options
    set -o errexit
    set -o nounset
    set -o pipefail
    set -o xtrace

    # create new venv if second arg is not "n"
    new_venv=${2:-"n"}
    if [[ ${new_venv} == "y" ]]; then
        echo "Create new venv!"
        setupVenv
    else
        source azEnv/bin/activate
    fi

    if [[ ${setup_option} == "build" ]]; then
        echo "Start to build az-aks-tool!"
        installBuildTools
    elif [[ ${setup_option} == "setup-tool" ]]; then
        echo "Start to setup az-aks-tool!"
        local_setup=${3:-"n"}
        if [[ ${local_setup} == "y" ]]; then
            wheel_file=${4}
            installAZAKSTOOLFromLocal "${wheel_file}"
        else
            installAZAKSTOOL
        fi
        removeKustoPTHFile
    elif [[ ${setup_option} == "setup-az" ]]; then
        echo "Start to setup azure-cli!"
        cli_repo=${3:-"azure-cli/"}
        ext_repo=${4:-""}
        setupAZ "${cli_repo}" "${ext_repo}"
        installTestPackages
        createSSHKey
    elif [[ ${setup_option} == "setup-akspreview" ]]; then
        echo "Start to setup aks-preview!"
        setupAKSPreview
        igniteAKSPreview
    else
        echo "Unsupported setup option '${setup_option}'!"
    fi
    echo "All Done!"
fi
