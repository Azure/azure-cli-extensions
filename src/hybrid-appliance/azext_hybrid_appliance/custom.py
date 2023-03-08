# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import psutil
import requests
import subprocess
import yaml
from knack.log import get_logger
from azure.cli.core import get_default_cli

from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from azext_hybrid_appliance import _constants as consts
from azure.cli.core.azclierror import ValidationError, CLIInternalError
logger = get_logger(__name__)


def validate_hybrid_appliance(resource_group_name, name):

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
    
    # Check if pre-req endpoints are reachable
    endpoints = [consts.Snap_Config_Storage_Endpoint, consts.Apt_Pull_Public_Endpoint, consts.Snap_Pull_Public_Endpoint, consts.App_Insights_Endpoint]

    for endpoint in endpoints:
        try:
            response = requests.head(endpoint, timeout=5)
            response.raise_for_status()
        except (requests.exceptions.RequestException):
            all_validations_passed = False
            logger.warning("The endpoint {} is not reachable from your machine".format(endpoint))
    
    try:
        cmd_show_arc= ['az', 'connectedk8s', 'show', '-n', name, '-g', resource_group_name, '-o', 'none']
        process = subprocess.Popen(cmd_show_arc)
        if process.wait() == 0:
            print("The appliance name and resource group name passed already correspond to an existing connected cluster. Please try again with a different appliance name.")
            all_validations_passed = False
    except Exception as e:
        print(type(e))
        print(str(e))
    
    if all_validations_passed is False:
        raise ValidationError("One or more pre-requisite validations have failed. Please resolve them and try again")
    else:
        logger.info("All pre-requisite validations have passed successfully")

def create_hybrid_appliance(resource_group_name, name, correlation_id=None, https_proxy="", http_proxy="", no_proxy="", proxy_cert="", location=None):
    latestMajorVersion, latestMinorVersion = get_latest_tested_microsk8_version()
    os.environ["MICROK8S_VERSION"]="{}.{}".format(latestMajorVersion, latestMinorVersion)

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
    cmd_onboard_arc= ['connectedk8s', 'connect', '-n', name, '-g', resource_group_name]
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
    # if onboarding_result.is_success():
    #     logger.info("The k8s cluster has been onboarded to Arc successfully")
    # else:
    #     error_code = onboarding_result.error.code
    #     error_message = onboarding_result.error.message
    #     raise CLIInternalError("Onboarding the k8s cluster Arc failed with error: {}".format(error_code, error_message))
    check_microk8s()

def upgrade_hybrid_appliance(resource_group_name, name):
    try:
        azure_clusterconfig_cm = subprocess.check_output(['kubectl', 'get', 'cm', 'azure-clusterconfig', '-n', 'azure-arc', '-o', 'json']).decode()
    except Exception as e:
        if check_microk8s():
            print("The required configmap was not found on the kubernetes cluster.") # Is there anything else which can be done in this case?
        else:
            print("The kubernetes cluster is not running as expected.")

        print("Please delete the appliance and create it again.")
    
    azure_clusterconfig_cm = json.loads(azure_clusterconfig_cm)
    if azure_clusterconfig_cm["data"]["AZURE_RESOURCE_GROUP"] != resource_group_name or azure_clusterconfig_cm["data"]["AZURE_RESOURCE_NAME"] != name:
        print("The parameters passed do not correspond to this appliance. Please check the resource group name and appliance name.")
        return # How to return non 0 error code?

    kubernetesVersionResponseString = subprocess.check_output(['kubectl', 'version', '-o', 'json']).decode()
    kubernetesVersionResponse = json.loads(kubernetesVersionResponseString)
    currentMajorVersion = kubernetesVersionResponse["serverVersion"]["major"]
    currentMinorVersion =  kubernetesVersionResponse["serverVersion"]["minor"].strip('+') # For some versions, for example, 1.23, minor version is represented as 23+ 
    
    latestMajorVersion, latestMinorVersion = get_latest_tested_microsk8_version()

    if currentMajorVersion == latestMajorVersion and currentMinorVersion == latestMinorVersion:
        print("Already at latest version")
    else:
        if currentMinorVersion > latestMinorVersion:
             # This should never happen unless someone manually runs "snap refresh" against the cluster instead of using our cli command.
             # Microk8s recommends never to downgrade a cluster, as this behaviour is not tested or supported 
            print("The current version of the kubernetes cluster is greater than the latest supported version. Please delete the appliance and create it again")
            return # Non zero return code?
        
        # This logic works as long as new versions are only minor version bumps
        # TODO: Figure out what to do in case major version is bumped (very unlikely)
        while currentMinorVersion != latestMinorVersion:
            currentMinorVersion = int(currentMinorVersion) + 1
            process = subprocess.Popen(['snap', 'refresh', 'microk8s', '--channel={}.{}'.format(currentMajorVersion, currentMinorVersion)])
            _, stderr = process.communicate()
            if process.returncode != 0:
                print("Failed to upgrade microk8s cluster: {}".format(stderr.decode()))
            try:
                subprocess.check_call(['microk8s', 'start'])
            except Exception as e:
                print("Failed to start microk8s cluster with exception {}".format(str(e)))

            if not check_microk8s():
                print("Cluster is not healthy after upgrading to {}.{}. Please check the logs at /var/snap/microk8s/current.".format(currentMajorVersion, currentMinorVersion))
                return # Non zero return code?
            print("Upgraded cluster to {}.{}".format(currentMajorVersion, currentMinorVersion))

def get_latest_tested_microsk8_version():
    response = requests.get("{}/{}/{}".format(consts.Snap_Config_Storage_End_Point, consts.Snap_Config_Container_Name, consts.Snap_Config_File_Name))
    return json.loads(response.content.decode())["latestTested"].split('.')

def check_microk8s():
    statusYaml = subprocess.check_output(['microk8s', 'status', '--format', 'yaml']).decode()
    print(statusYaml)
    status = yaml.safe_load(statusYaml)
    print(status)
    if not status["microk8s"]["running"]:
        print("Microk8s is not running")
        subprocess.check_call(['microk8s', 'inspect'])