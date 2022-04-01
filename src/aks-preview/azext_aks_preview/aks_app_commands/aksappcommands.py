# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List
import shutil
import subprocess
import requests
import os
import platform
from pathlib import Path
from knack.prompting import prompt_y_n


def aks_web_app_init():
    filePath = _binary_pre_check()
    if filePath:
        isRunSuccessful = run_binary(filePath)
        if isRunSuccessful == 0:
            cmd_finish()
            return

    raise ValueError("Binary was NOT executed successfully")


# If setup is valid this method returns the correct binary path to execute
def _binary_pre_check() -> str:
    print("The DraftV2 setup is in progress ...")
    draftV2BinaryPath = _find_existing_path(get_potential_paths())
    if draftV2BinaryPath:
        return draftV2BinaryPath

    print("DraftV2 binary not found")
    return download_binary()


def _find_existing_path(paths: List[str]) -> str:
    print("Checking if DraftV2 binary exists ...")
    operatingSystem = platform.system()
    # Filename depends on the operating system
    filename = "draftv2-" + operatingSystem.lower() + "-amd64"

    if not paths:
        print("List of given DraftV2 paths is empty")
        return None

    for path in paths:
        binaryFilePath = path + "/" + filename
        if os.path.exists(binaryFilePath):
            print("Existing binary found at: " + binaryFilePath)
            return binaryFilePath
    return ""


# Returns a list of potential draftV2 binary paths
def get_potential_paths() -> List[str]:
    result = [str(Path.home()) + "/" + ".aksapp"]
    paths = os.environ['PATH'].split(':')

    for path in paths:
        if "draftv2" in path:
            result.append(path)
    return result


def run_binary(path: str):
    if path is None:
        raise ValueError("The given Binary path was null or empty")

    print("Running DraftV2 Binary ...")
    process = subprocess.Popen([path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    exit_code = process.wait()
    print(stdout, stderr, exit_code)
    return exit_code


def cmd_finish():
    # Clean up logic can go here if needed
    print("We are done Stop.")


def download_binary() -> str:
    # prompt user to download binary. If users says no, we error out and tell them that this requires the binary
    from knack.prompting import prompt_y_n
    msg = 'he required binary was not found. Would you like us to download the required binary for you?'

    if not prompt_y_n(msg, default="n"):
        raise ValueError("`az aks app` requires the missing dependency")

    print("Attempting to download dependency...")

    operatingSystem = platform.system()
    draftV2ReleaseVersion = "v0.0.5"
    filename = "draftv2-" + operatingSystem.lower() + "-amd64"
    url = "https://github.com/Azure/aks-app/releases/download/" + draftV2ReleaseVersion + "/" + filename
    headers = {'Accept': 'application/octet-stream'}

    # Downloading the file by sending the request to the URL
    req = requests.get(url, headers=headers)
    binaryPath = str(Path.home()) + "/" + ".aksapp"

    # Directory
    if os.path.exists(binaryPath) is False:
        os.chdir(str(Path.home()))
        os.mkdir(".aksapp")
        print("Directory '% s' was created inside of your HOME directory" % ".aksapp")

    if req.ok:
        # Split URL to get the file name "draftv2-darwin-amd64"
        os.chdir(binaryPath)
        # Writing the file to the local file system
        with open(filename, 'wb') as output_file:
            output_file.write(req.content)
        print("Download of DraftV2 binary was successful with a status code: " + str(req.status_code))
        os.chmod(binaryPath + "/" + filename, 0o777)
        return binaryPath + "/" + filename

    print("Download of DraftV2 binary was unsuccessful with a status code: " + str(req.status_code))
    return None
