# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import psutil
import requests
import subprocess
from knack.log import get_logger
from azure.cli.core import get_default_cli
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from azext_hybrid_appliance import _constants as consts
from azure.cli.core.azclierror import ValidationError
logger = get_logger(__name__)


def validate_hybrid_appliance():

    all_validations_passed = True

    # Check if the operating system is Linux
    if not psutil.LINUX:
        all_validations_passed = False
        logger.warning("This program can only run on a Linux machine")

    # Check if the disk space is at least 20GB
    disk_usage = psutil.disk_usage('/')
    if disk_usage.total < consts.Disk_Threshold * 1024 * 1024 * 1024:
        all_validations_passed = False
        logger.warning("This program requires at least {} of disk space".format(consts.Disk_Threshold))

    # Check if the memory is at least 4GB
    memory = psutil.virtual_memory()
    if memory.total < consts.Memory_Threshold * 1024 * 1024 * 1024:
        all_validations_passed = False
        logger.warning("This program requires at least {} of memory".format(consts.Memory_Threshold))
    
    # Check if snap storage endpoint is reachable
    try:
        response = requests.head(consts.Snap_Config_Storage_End_Point, timeout=5)
        response.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        all_validations_passed = False
        logger.warning("The endpoint {} is not reachable".format(consts.Snap_Config_Storage_End_Point))
    
    if all_validations_passed is False:
        raise ValidationError("One or more pre-requisite validations have failed. Please resolve them and try again")
    else:
        logger.info("All pre-requisite validations have passed successfully")

def create_hybrid_appliance(resource_group_name, appliance_name, correlation_id=None, https_proxy="", http_proxy="", no_proxy="", proxy_cert="", location=None):
    current_path = os.path.abspath(os.path.dirname(__file__))
    script_file_path = os.path.join(current_path, "microk8sbootstrap.sh")
    cmd = ["sh", script_file_path]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Print the output and error messages in real-time
    for line in iter(process.stdout.readline, ""):
        print(line, end="") # Use 'end' parameter to prevent printing extra newline characters

    for line in iter(process.stderr.readline, ""):
        print(line, end="")

    # Install specific version of connectedk8s
    get_default_cli().invoke(['extension', 'add', '-n', 'connectedk8s', '--version', '1.3.14'])
    # Onboard the cluster to arc
    cmd_onboard_arc= ['connectedk8s', 'connect', '-n', appliance_name, '-g', resource_group_name]
    if location:
        cmd_onboard_arc.extend(["--location", location])
    if http_proxy:
        cmd_onboard_arc.extend(["--proxy-http", http_proxy])
    if https_proxy:
        cmd_onboard_arc.extend(["--proxy-https", https_proxy])
    if no_proxy:
        cmd_onboard_arc.extend(["--proxy-skip-range", no_proxy])

    onboarding_result = get_default_cli().invoke(cmd_onboard_arc)


