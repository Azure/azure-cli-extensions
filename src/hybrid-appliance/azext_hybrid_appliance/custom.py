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
from azure.cli.core import telemetry
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from azext_hybrid_appliance import _constants as consts
from azure.cli.core.azclierror import ValidationError, CLIInternalError
logger = get_logger(__name__)


def validate_hybrid_appliance(resource_group_name, appliance_name):

    all_validations_passed = True

    # Check if the operating system is Linux
    if not psutil.LINUX:
        all_validations_passed = False
        telemetry.set_exception(exception="User's machine is not linux machine", fault_type="", summary="")
        logger.warning("This program can only run on a Linux machine")

    # Check if the disk space is at least 20GB
    disk_usage = psutil.disk_usage('/')
    if disk_usage.total < consts.Disk_Threshold * 1024 * 1024 * 1024:
        all_validations_passed = False
        telemetry.set_exception(exception="Machine doesn't meet min 20GB disk space requirement", fault_type="", summary="")
        logger.warning("This program requires at least {} of disk space".format(consts.Disk_Threshold))

    # Check if the memory is at least 4GB
    memory = psutil.virtual_memory()
    if memory.total < consts.Memory_Threshold * 1024 * 1024 * 1024:
        all_validations_passed = False
        telemetry.set_exception(exception="Machine doesn't meet min 4GB memory requirement", fault_type="", summary="")
        logger.warning("This program requires at least {} of memory".format(consts.Memory_Threshold))
    
    # Check if pre-req endpoints are reachable
    endpoints = [consts.Snap_Config_Storage_Endpoint, consts.Apt_Pull_Public_Endpoint, consts.Snap_Pull_Public_Endpoint, consts.App_Insights_Endpoint, consts.MCR_Endpoint]

    for endpoint in endpoints:
        try:
            response = requests.head(endpoint, timeout=5)
            response.raise_for_status()
        except (requests.exceptions.RequestException):
            all_validations_passed = False
            logger.warning("The endpoint {} is not reachable from your machine".format(endpoint))

    if connected_cluster_exists(appliance_name, resource_group_name):
        all_validations_passed = False
        logger.warning("Connected cluster with name {} in resource group {} already exists".format(appliance_name, resource_group_name))
    
    if all_validations_passed is False:
        telemetry.set_exception(exception="")
        raise ValidationError("One or more pre-requisite validations have failed. Please resolve them and try again")
    else:
        logger.info("All pre-requisite validations have passed successfully")

def create_hybrid_appliance(resource_group_name, appliance_name, correlation_id=None, https_proxy="", http_proxy="", no_proxy="", proxy_cert="", location=None):
    current_path = os.path.abspath(os.path.dirname(__file__))
    script_file_path = os.path.join(current_path, "microk8sbootstrap.sh")
    cmd = ["sh", script_file_path]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Iterate over stdout and stderr in real-time
    for stdout_line, stderr_line in zip(process.stdout, process.stderr):
        # Print stdout output
        if stdout_line:
            print(stdout_line.strip())
        # Print stderr output
        if stderr_line:
            print(stderr_line.strip())

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
    if proxy_cert:
        cmd_onboard_arc.extend(["--proxy-cert", proxy_cert])

    onboarding_result = get_default_cli().invoke(cmd_onboard_arc)
    if onboarding_result != 0:
        error_code = onboarding_result.error.code
        error_message = onboarding_result.error.message
        raise CLIInternalError("Onboarding the k8s cluster to Arc failed with error: {}".format(error_code, error_message))
    else:
        logger.info("The k8s cluster has been onboarded to Arc successfully")
                               

