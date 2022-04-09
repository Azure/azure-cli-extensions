# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sre_parse
from typing import Dict, List
import shutil
import subprocess
import requests
import os
import platform
from pathlib import Path
from knack.prompting import prompt_y_n


def aks_draft_app_init(deployment_path: str,
                       app_name: str,
                       language: str,
                       create_config: str,
                       dockerfile_only: str,
                       deployment_only: str) -> None:
    file_path = _binary_pre_check()
    if not file_path:
        raise ValueError('Binary check was NOT executed successfully')

    arguments = _build_arguments(app_name, language, create_config, dockerfile_only, deployment_only)
    run_successful = _run(file_path, deployment_path, arguments)
    if run_successful:
        _cmd_finish()
    else:
        raise ValueError('\'az aks app init\' was NOT executed successfully')


# If setup is valid this method returns the correct binary path to execute
def _binary_pre_check() -> str:
    print('The DraftV2 setup is in progress...')
    draftv2_binary_path = _get_existing_path()

    if draftv2_binary_path:  # use found binary
        return draftv2_binary_path
    else:  # prompt user to download binary
        return _download_binary()


# Returns path to existing draftv2 binary and None otherwise
def _get_existing_path() -> str:
    print('Checking if DraftV2 binary exists locally...')

    operating_system = platform.system().lower()
    # Filename depends on the operating system
    filename = 'draftv2-' + operating_system + '-amd64'

    paths = _get_potential_paths()
    if not paths:
        print('List of potential DraftV2 paths is empty')
        return None

    for path in paths:
        binary_file_path = path + '/' + filename
        if os.path.exists(binary_file_path):
            print('Existing binary found at: ' + binary_file_path)
            return binary_file_path
    return None


# Returns a list of potential draftV2 binary paths
def _get_potential_paths() -> List[str]:
    result = [str(Path.home()) + '/' + '.aksapp']
    paths = os.environ['PATH'].split(':')

    for path in paths:
        if 'draftv2' in path:
            result.append(path)
    return result


def _build_arguments(app_name: str,
                     language: str,
                     create_config: str,
                     dockerfile_only: str,
                     deployment_only: str) -> List[str]:
    options = {
        'app-name': app_name,
        'language': language,
        'create-config': create_config,
        'dockerfile-only': dockerfile_only,
        'deployment-only': deployment_only
    }
    args_list = []
    for arg, val in options.items():
        if val:
            args_list.append(f'--{arg}={val}')
    return args_list


def _run(binary_path: str, deployment_path: str, arguments: List[str]) -> bool:
    if binary_path is None:
        raise ValueError('The given Binary path was null or empty')

    print('Running DraftV2 Binary ...')
    cmd = [binary_path, 'create', deployment_path] + arguments
    process = subprocess.Popen(cmd)
    exit_code = process.wait()
    return exit_code == 0


def _cmd_finish():
    # Clean up logic can go here if needed
    pass


def _download_binary() -> str:
    # prompt user to download binary. If users says no, we error out and tell them that this requires the binary
    from knack.prompting import prompt_y_n
    msg = 'The required binary was not found. Would you like us to download the required binary for you?'

    if not prompt_y_n(msg, default='n'):
        raise ValueError('`az aks app` requires the missing dependency')

    print('Attempting to download dependency...')

    operating_system = platform.system().lower()
    architecture = platform.machine().lower()

    if architecture == 'x86_64':
        architecture = 'amd64'
    if architecture not in ['arm64', 'amd64']:
        print('Cannot find a suitable download for the current system architecture. Draft only supports AMD64 and ARM64.')
        return None

    filename = f'draftv2-{operating_system}-{architecture}'
    url = f'https://github.com/Azure/aks-app/releases/latest/download/{filename}'
    headers = {'Accept': 'application/octet-stream'}

    dir_name = '.aksapp'
    # Downloading the file by sending the request to the URL
    req = requests.get(url, headers=headers)
    binary_path = str(Path.home()) + '/' + dir_name

    # Directory
    if os.path.exists(binary_path) is False:
        os.chdir(str(Path.home()))
        os.mkdir(dir_name)
        print(f'Directory {dir_name} was created inside of your HOME directory')

    if req.ok:
        # Split URL to get the file name 'draftv2-darwin-amd64'
        os.chdir(binary_path)
        # Writing the file to the local file system
        with open(filename, 'wb') as output_file:
            output_file.write(req.content)
        print('Download of DraftV2 binary was successful with a status code: ' + str(req.status_code))
        os.chmod(binary_path + '/' + filename, 0o755)
        return binary_path + '/' + filename

    print('Download of DraftV2 binary was unsuccessful with a status code: ' + str(req.status_code))
    return None
