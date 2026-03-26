# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from azext_aks_preview._consts import CONST_DRAFT_CLI_VERSION
from knack.prompting import prompt_y_n


# `az aks draft create` function
def aks_draft_cmd_create(destination: str,
                         app_name: str,
                         language: str,
                         create_config: str,
                         dockerfile_only: str,
                         deployment_only: str,
                         download_path: str) -> None:
    file_path, arguments = _pre_run(download_path,
                                    destination=destination,
                                    app_name=app_name,
                                    language=language,
                                    create_config=create_config,
                                    dockerfile_only=dockerfile_only,
                                    deployment_only=deployment_only)
    run_successful = _run(file_path, 'create', arguments)
    if run_successful:
        _run_finish()
    else:
        raise ValueError('`az aks draft create` was NOT executed successfully')


# `az aks draft setup-gh` function
def aks_draft_cmd_setup_gh(app: str,
                           subscription_id: str,
                           resource_group: str,
                           provider: str,
                           gh_repo: str,
                           download_path: str) -> None:
    file_path, arguments = _pre_run(download_path,
                                    app=app,
                                    subscription_id=subscription_id,
                                    resource_group=resource_group,
                                    provider=provider,
                                    gh_repo=gh_repo)
    run_successful = _run(file_path, 'setup-gh', arguments)
    if run_successful:
        _run_finish()
    else:
        raise ValueError('`az aks draft setup-gh` was NOT executed successfully')


# `az aks draft generate-workflow` function
def aks_draft_cmd_generate_workflow(cluster_name: str,
                                    registry_name: str,
                                    container_name: str,
                                    resource_group: str,
                                    destination: str,
                                    branch: str,
                                    download_path: str) -> None:
    file_path, arguments = _pre_run(download_path,
                                    cluster_name=cluster_name,
                                    registry_name=registry_name,
                                    container_name=container_name,
                                    resource_group=resource_group,
                                    destination=destination,
                                    branch=branch)
    run_successful = _run(file_path, 'generate-workflow', arguments)
    if run_successful:
        _run_finish()
    else:
        raise ValueError('`az aks draft generate-workflow` was NOT executed successfully')


# `az aks draft up` function
def aks_draft_cmd_up(app: str,
                     subscription_id: str,
                     resource_group: str,
                     provider: str,
                     gh_repo: str,
                     cluster_name: str,
                     registry_name: str,
                     container_name: str,
                     destination: str,
                     branch: str,
                     download_path: str) -> None:
    file_path = _binary_pre_check(download_path)
    if not file_path:
        raise ValueError('Binary check was NOT executed successfully')

    setup_gh_args = _build_args(app=app,
                                subscription_id=subscription_id,
                                resource_group=resource_group,
                                provider=provider,
                                gh_repo=gh_repo)

    run_successful = _run(file_path, 'setup-gh', setup_gh_args)
    if not run_successful:
        raise ValueError('`az aks draft setup-gh` was NOT executed successfully')

    generate_workflow_args = _build_args(cluster_name=cluster_name,
                                         registry_name=registry_name,
                                         container_name=container_name,
                                         resource_group=resource_group,
                                         destination=destination,
                                         branch=branch)
    run_successful = _run(file_path, 'generate-workflow', generate_workflow_args)
    if run_successful:
        _run_finish()
    else:
        raise ValueError('`az aks draft generate-workflow` was NOT executed successfully')


# `az aks draft update` function
def aks_draft_cmd_update(host: str, certificate: str, destination: str, download_path: str) -> None:
    file_path, arguments = _pre_run(download_path, host=host, certificate=certificate, destination=destination)
    run_successful = _run(file_path, 'update', arguments)
    if run_successful:
        _run_finish()
    else:
        raise ValueError('`az aks draft update` was NOT executed successfully')


# Returns binary file path and arguments
def _pre_run(download_path: str, **kwargs) -> Tuple[str, List[str]]:
    file_path = _binary_pre_check(download_path)
    if not file_path:
        raise ValueError('Binary check was NOT executed successfully')
    arguments = _build_args(kwargs)
    return file_path, arguments


# Executes the Draft command
# Returns True if the process executed sucessfully, False otherwise
def _run(binary_path: str, command: str, arguments: List[str]) -> bool:
    if binary_path is None:
        raise ValueError('The given Binary path was null or empty')

    logging.info("Running `az aks draft %s`", command)
    cmd = [binary_path, command] + arguments
    with subprocess.Popen(cmd) as process:
        exit_code = process.wait()
    return exit_code == 0


# Function for clean up logic
def _run_finish():
    # Clean up logic can go here if needed
    logging.info('Finished running Draft command')


def _build_args(args_dict: Dict[str, str] = None, **kwargs) -> List[str]:
    if not args_dict:
        args_dict = kwargs
    args_list = []
    for key, val in args_dict.items():
        arg = key.replace('_', '-')
        if val:
            args_list.append(f'--{arg}={val}')
    return args_list


# Returns the path to Draft binary. None if missing the required binary
def _binary_pre_check(download_path: str) -> Optional[str]:
    # if user specifies a download path, download the draft binary to this location and use it as a path
    if download_path:
        return _download_binary(download_path)

    logging.info('The Draft binary check is in progress...')
    draft_binary_path = _get_existing_path()

    if draft_binary_path:  # found binary
        if _is_latest_version(draft_binary_path):  # no need to update
            logging.info('Your local version of Draft is up to date.')
        else:  # prompt the user to update
            msg = 'We have detected a newer version of Draft. Would you like to download it?'
            response = prompt_y_n(msg, default='n')
            if response:
                return _download_binary()
        return draft_binary_path
    # prompt the user to download binary
    # If users says no, we error out and tell them that this requires the binary
    msg = 'The required binary was not found. Would you like us to download the required binary for you?'
    if not prompt_y_n(msg, default='n'):
        raise ValueError('`az aks draft` requires the missing dependency')
    return _download_binary()


# Returns True if the local binary is the latest version, False otherwise
def _is_latest_version(binary_path: str) -> bool:
    latest_version = CONST_DRAFT_CLI_VERSION
    with subprocess.Popen([binary_path, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        stdout, stderr = process.communicate()
    if stderr.decode():
        return False
    # return string of result is "version: v0.0.x"
    current_version = stdout.decode().split('\n', maxsplit=1)[0].strip().split()[-1]
    return latest_version == current_version


# Returns the filename for the current os and architecture
# Returns None if the current system is not supported in Draft
def _get_filename() -> Optional[str]:
    operating_system = platform.system().lower()
    architecture = platform.machine().lower()

    if architecture == 'x86_64':
        architecture = 'amd64'
    if architecture not in ['arm64', 'amd64']:
        logging.error(
            "Cannot find a suitable download for the current system architecture. Draft only supports AMD64 and ARM64."
        )
        return None

    file_suffix = ".exe" if operating_system == "windows" else ""
    return f'draft-{operating_system}-{architecture}{file_suffix}'


# Returns path to existing draft binary, None otherwise
def _get_existing_path() -> Optional[str]:
    logging.info('Checking if Draft binary exists locally...')

    filename = _get_filename()
    if not filename:
        return None

    paths = _get_potential_paths()
    if not paths:
        logging.error('List of potential Draft paths is empty')
        return None

    for path in paths:
        binary_file_path = path + '/' + filename
        if os.path.exists(binary_file_path):
            logging.info("Existing binary found at: %s", binary_file_path)
            return binary_file_path
    return None


# Returns a list of potential draftV2 binary paths
def _get_potential_paths() -> List[str]:
    paths = os.environ['PATH'].split(':')
    # the download location of _download_binary()
    default_dir = str(Path.home()) + '/' + '.aksdraft'
    paths.append(default_dir)

    return paths


# Downloads the latest binary to ~/.aksdraft
# Returns path to the binary if sucessful, None otherwise
def _download_binary(download_path: str = '~/.aksdraft') -> Optional[str]:
    logging.info('Attempting to download dependency...')
    download_path = os.path.expanduser(download_path)
    filename = _get_filename()
    if not filename:
        return None

    url = f'https://github.com/Azure/draft/releases/download/{CONST_DRAFT_CLI_VERSION}/{filename}'
    headers = {'Accept': 'application/octet-stream'}

    # Downloading the file by sending the request to the URL
    response = requests.get(url, headers=headers)

    if response.ok:
        # Directory
        if os.path.exists(download_path) is False:
            Path(download_path).mkdir(parents=True, exist_ok=True)
            logging.info("Directory %s was created inside of your HOME directory", download_path)
        full_path = f'{download_path}/{filename}'

        # Writing the file to the local file system
        with open(full_path, 'wb') as output_file:
            output_file.write(response.content)
        logging.info("Download of Draft binary was successful with a status code: %s", response.status_code)
        os.chmod(full_path, 0o755)
        return full_path

    logging.error("Download of Draft binary was unsuccessful with a status code: %s", response.status_code)
    return None
