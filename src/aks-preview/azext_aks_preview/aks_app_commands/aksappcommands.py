#!/usr/bin/env python3

import shutil
import subprocess
import requests
import os
import platform
from pathlib import Path


def aks_web_app_init():
    validation = pre_setup_validations()
    if validation:
        run_binary()
        cmd_finish()

def pre_setup_validations() -> bool:
    print("The DraftV2 setup is in progress ...")

    paths = getPaths()
    draftV2BinaryExists = isExists(paths)

    isDownloadSuccessful = False

    if not draftV2BinaryExists:
        print("DraftV2 binary not found in the following paths:")
        isDownloadSuccessful = downloadBinary()

    # Considered valid if binary already exists, or we were able to successfully download the binary
    return draftV2BinaryExists or isDownloadSuccessful


def isExists(paths) -> bool:
    print("Checking if DraftV2 binary exists ...")

    operatingSystem = platform.system()
    # Filename depends on the operating system
    filename = "draftv2-" + operatingSystem.lower() + "-amd64"

    if not paths:
        print("List of given DraftV2 paths is empty")
        return False

    for path in paths:
        if os.path.exists(path + "/" + filename):
            print("Existing binary found at: " + path)
            return True
    return False


# Returns a list of potential draftV2 binary paths
def getPaths():
    result = [str(Path.home()) + "/" +".aksapp"]
    paths = os.environ['PATH'].split(':')

    for path in paths:
        if "draftv2" in path:
            result.append(path)

    return result



def run_binary():
    print("Running DraftV2 Binary ...")
    # for keen mind here is the difference of .popen vs .run
    # subprocess.run(["ls", "-l"], shell=True, check=True, stdout=subprocess.PIPE) # This will run the command and return any output
    process = subprocess.Popen(
        ['ifconfig'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    exit_code = process.wait()
    print("If non zero then binary ran fine and job is done.")
    print(stdout, stderr, exit_code)
    print("prepare exiting mechanism.")


def cmd_finish():
    print("Depending ont the exit_code display message")
    print("We are done Stop.")


def downloadBinary() -> bool:
    # prompt user to download binary. If users says no, we error out and tell them that this requires the binary
    permissionToDownload = input("The required binary was not found. Would you like us to download the required binary for you? Y/n: ")

    if permissionToDownload.lower() != "y" :
        raise ValueError("`az aks app` requires the missing dependency")

    print("Attempting to download dependency...")

    operatingSystem = platform.system()
    draftV2ReleaseVersion = "v0.0.5"
    filename = "draftv2-" + operatingSystem.lower() + "-amd64"
    url = "https://github.com/Azure/aks-app/releases/download/"+ releaseVersion + "/" +  filename
    headers = {'Accept': 'application/octet-stream'}

    # Downloading the file by sending the request to the URL
    req = requests.get(url, headers=headers)

    binaryPath = str(Path.home()) + "/" +".aksapp"

    # Directory
    if os.path.exists(binaryPath) == False:
        os.chdir(str(Path.home()))
        os.mkdir(".aksapp")
        print("Directory '% s' was created inside of your HOME directory" % ".aksapp")

    if req.ok:
        # Split URL to get the file name "draftv2-darwin-amd64"
        os.chdir(binaryPath)
        # Writing the file to the local file system
        with open(filename,'wb') as output_file:
            output_file.write(req.content)
        print("Download of DraftV2 binary was successful with a status code: " + str(req.status_code))
        return True

    print("Download of DraftV2 binary was unsuccessful with a status code: " + str(req.status_code))
    return False


