# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import psutil
import requests
import subprocess
from azure.cli.core import get_default_cli
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from azext_hybrid_appliance import _constants as consts
from azure.cli.core.azclierror import ValidationError


def validate_hybrid_appliance():

    # Check if the operating system is Linux
    if not psutil.LINUX:
        raise ValidationError("This program can only run on a Linux machine")

    # Check if the disk space is at least 20GB
    disk_usage = psutil.disk_usage('/')
    if disk_usage.total < consts.Disk_Threshold * 1024 * 1024 * 1024:
        raise ValidationError("This program requires at least 20GB of disk space")

    # Check if the memory is at least 4GB
    memory = psutil.virtual_memory()
    if memory.total < consts.Memory_Threshold * 1024 * 1024 * 1024:
        raise ValidationError("This program requires at least 4GB of memory")
    
    # Check if snap storage endpoint is reachable
    try:
        response = requests.head(consts.Snap_Config_Storage_End_Point, timeout=5)
        response.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        raise ValidationError("The endpoint {} is not reachable", consts.Snap_Storage_End_Point)

def create_hybrid_appliance(resource_group_name, appliance_name, correlation_id=None, https_proxy="", http_proxy="", no_proxy="", proxy_cert="", location=None):
    current_path = os.path.abspath(os.path.dirname(__file__))
    script_file_path = os.path.join(current_path, "microk8sbootstrap.sh")
    cmd = ["sh", script_file_path]

    proccess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = proccess.communicate()

    print("Output:", output.decode("utf-8"))
    print("Error:", error.decode("utf-8"))

    # Install specific version of connectedk8s
    get_default_cli().invoke(['extension', 'add', '-n', 'connectedk8s', '--version', '1.13'])
    # Onboard the cluster to arc
    cmd_onboard_arc= ['connectedk8s', 'connect', '-n', appliance_name, '-g', resource_group_name]
    if http_proxy:
        cmd_onboard_arc.extend(["--proxy-http", http_proxy])
    if https_proxy:
        cmd_onboard_arc.extend(["--proxy-https", https_proxy])
    if no_proxy:
        cmd_onboard_arc.extend(["--proxy-skip-range", no_proxy])

    get_default_cli().invoke(cmd_onboard_arc)


