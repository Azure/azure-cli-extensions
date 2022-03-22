#!/usr/bin/env python3

import shutil
import subprocess
import requests


def aks_web_app_init():
    validation = pre_setup_validations()
    if validation:
        run_binary()
        cmd_finish()

def pre_setup_validations() -> bool:
    print("The DraftV2 setup is in progress ...")
    print("Checking if Binary exist ...")
    cmd_exist = False #cmd_exists("ifconfig")
    #print(cmd_exist)

    isDownloadSuccessful = False
    if not cmd_exist:
        print("DraftV2 binary not found")
        isDownloadSuccessful = downloadBinary()

    return cmd_exist or isDownloadSuccessful

def cmd_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None

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
    print("Attempting to download DraftV2 binary")
    url = "https://github.com/Azure/draftv2/releases/latest/"

    # Downloading the file by sending the request to the URL
    req = requests.get(url)
    result = False

    if req.ok:
        # Split URL to get the file name
        filename = url.split('/')[-1]

        # Writing the file to the local file system
        with open(filename,'wb') as output_file:
            output_file.write(req.content)
        print("download of DraftV2 binary was successful with a status code: " + str(req.status_code))
        return True

    print("Download of DraftV2 binary was unsuccessful with a status code: " + str(req.status_code))
    return False


