# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import sre_parse
from typing import Dict, List, Optional
import shutil
import subprocess
import requests
import os
import platform
from pathlib import Path
from knack.prompting import prompt_y_n


# `az aks app init` function
def aks_draft_app_init(destination: str,
                       app_name: str,
                       language: str,
                       create_config: str,
                       dockerfile_only: str,
                       deployment_only: str) -> None:
    file_path = _binary_pre_check()
    if not file_path:
        raise ValueError('Binary check was NOT executed successfully')

    arguments = _build_init_arguments(destination, app_name, language, create_config, dockerfile_only, deployment_only)
    run_successful = _run_init(file_path, arguments)
    if run_successful:
        _init_finish()
    else:
        raise ValueError('`az aks app init` was NOT executed successfully')


# Returns the path to Draft binary. None if missing the required binary
def _binary_pre_check() -> Optional[str]:
    print('The Draft setup is in progress...')
    draft_binary_path = _get_existing_path()

    if draft_binary_path:  # found binary
        if _is_latest_version(draft_binary_path):  # no need to update
            print('Your local version of Draft is up to date.')
        else:  # prompt the user to update
            msg = 'We have detected a newer version of Draft. Would you like to download it?'
            response = prompt_y_n(msg, default='n')
            if response:
                return _download_binary()
        return draft_binary_path
    else:  # prompt the user to download binary
        # If users says no, we error out and tell them that this requires the binary
        msg = 'The required binary was not found. Would you like us to download the required binary for you?'

        if not prompt_y_n(msg, default='n'):
            raise ValueError('`az aks app` requires the missing dependency')

        return _download_binary()


# Returns the latest version str of Draft on Github
def _get_latest_version() -> str:
    response = requests.get('https://api.github.com/repos/Azure/aks-app/releases/latest')
    response_json = json.loads(response.text)
    return response_json.get('tag_name')


# Returns True if the local binary is the latest version, False otherwise
def _is_latest_version(binary_path: str) -> bool:
    latest_version = _get_latest_version()
    process = subprocess.Popen([binary_path, 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr.decode():
        return False
    # return string of result is "version: v0.0.x"
    current_version = stdout.decode().strip().split()[-1]
    return latest_version == current_version


# Returns the filename for the current os and architecture
# Returns None if the current system is not supported in Draft
def _get_filename() -> Optional[str]:
    operating_system = platform.system().lower()
    architecture = platform.machine().lower()

    if architecture == 'x86_64':
        architecture = 'amd64'
    if architecture not in ['arm64', 'amd64']:
        print('Cannot find a suitable download for the current system architecture. Draft only supports AMD64 and ARM64.')
        return None

    return f'draftv2-{operating_system}-{architecture}'


# Returns path to existing draft binary, None otherwise
def _get_existing_path() -> Optional[str]:
    print('Checking if Draft binary exists locally...')

    filename = _get_filename()
    if not filename:
        return None

    paths = _get_potential_paths()
    if not paths:
        print('List of potential Draft paths is empty')
        return None

    for path in paths:
        binary_file_path = path + '/' + filename
        if os.path.exists(binary_file_path):
            print('Existing binary found at: ' + binary_file_path)
            return binary_file_path
    return None


# Returns a list of potential draftV2 binary paths
def _get_potential_paths() -> List[str]:
    paths = os.environ['PATH'].split(':')
    # the download location of _download_binary()
    default_dir = str(Path.home()) + '/' + '.aksapp'
    paths.append(default_dir)

    return paths


# Downloads the latest binary to ~/.aksapp
# Returns path to the binary if sucessful, None otherwise
def _download_binary() -> Optional[str]:
    print('Attempting to download dependency...')

    filename = _get_filename()
    if not filename:
        return None

    url = f'https://github.com/Azure/aks-app/releases/latest/download/{filename}'
    headers = {'Accept': 'application/octet-stream'}

    dir_name = '.aksapp'
    # Downloading the file by sending the request to the URL
    response = requests.get(url, headers=headers)
    binary_path = str(Path.home()) + '/' + dir_name

    # Directory
    if os.path.exists(binary_path) is False:
        os.chdir(str(Path.home()))
        os.mkdir(dir_name)
        print(f'Directory {dir_name} was created inside of your HOME directory')

    if response.ok:
        # Split URL to get the file name 'draftv2-darwin-amd64'
        os.chdir(binary_path)
        # Writing the file to the local file system
        with open(filename, 'wb') as output_file:
            output_file.write(response.content)
        print('Download of Draft binary was successful with a status code: ' + str(response.status_code))
        os.chmod(binary_path + '/' + filename, 0o755)
        return binary_path + '/' + filename

    print('Download of Draft binary was unsuccessful with a status code: ' + str(response.status_code))
    return None


# Returns a list of arguments following the format `--arg=value`
def _build_args(options: Dict[str: str]) -> List[str]:
    args_list = []
    for arg, val in options.items():
        if val:
            args_list.append(f'--{arg}={val}')
    return args_list


# Returns a list of arguments for `az aks app init`
def _build_init_arguments(destination: str,
                          app_name: str,
                          language: str,
                          create_config: str,
                          dockerfile_only: str,
                          deployment_only: str) -> List[str]:
    options = {
        'destination': destination,
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


# Executes the `draft create` command
# Returns True if the process executed sucessfully, False otherwise
def _run_init(binary_path: str, arguments: List[str]) -> bool:
    if binary_path is None:
        raise ValueError('The given Binary path was null or empty')

    print('Running Draft Binary ...')
    cmd = [binary_path, 'create'] + arguments
    process = subprocess.Popen(cmd)
    exit_code = process.wait()
    return exit_code == 0


# Function for clean up logic
def _init_finish():
    # Clean up logic can go here if needed
    print('Finishing running `az aks app init`')
