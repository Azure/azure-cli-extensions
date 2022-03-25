#!/usr/bin/env python3

import shutil
import subprocess
import requests
import os
from pathlib import Path



def aks_web_app_init():
    validation = pre_setup_validations()
    if validation:
        run_binary()
        cmd_finish()

def pre_setup_validations() -> bool:
    print("The DraftV2 setup is in progress ...")

    paths = ["fakePath", "anotherFakePath"]
    draftV2BinaryExists = isExists(paths)

    isDownloadSuccessful = False

    if not draftV2BinaryExists:
        print("DraftV2 binary not found in the following paths:")
        print(*paths, sep = ", ")
        isDownloadSuccessful = downloadBinary()

    # Considered valid if binary already exists, or we were able to successfully download the binary
    return draftV2BinaryExists or isDownloadSuccessful

def isExists(paths) -> bool:
    print("Checking if DraftV2 binary exists ...")

    if not paths:
        print("List of given DraftV2 paths is empty")
        return False

    for path in paths:
        if os.path.exists(path):
            return True
    return False


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
    url = "https://github.com/Azure/aks-app/releases/download/v0.0.5/draftv2-darwin-amd64"
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
        # Split URL to get the file name "draft-v2darwin-arm64"
        os.chdir(binaryPath)
        filename = url.split('/')[-1]

        # Writing the file to the local file system
        with open(filename,'wb') as output_file:
            output_file.write(req.content)
        print("Download of DraftV2 binary was successful with a status code: " + str(req.status_code))
        return True

    print("Download of DraftV2 binary was unsuccessful with a status code: " + str(req.status_code))
    return False


