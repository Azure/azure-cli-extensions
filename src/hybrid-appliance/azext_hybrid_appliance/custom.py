# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import psutil
import requests
import subprocess
from knack.log import get_logger
from azure.cli.core import get_default_cli
from azure.cli.core import telemetry
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from azext_hybrid_appliance import _constants as consts
from azext_hybrid_appliance import _utils as utils
from azure.cli.core.azclierror import ValidationError, CLIInternalError
logger = get_logger(__name__)


def validate_hybrid_appliance(resource_group_name, name):

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
    endpoints = ["{}/{}/{}".format(consts.Snap_Config_Storage_End_Point, consts.Snap_Config_Container_Name, consts.Snap_Config_File_Name), consts.Snap_Pull_Public_Api_Endpoint, consts.Snap_Pull_Public_Storage_Endpoint, consts.App_Insights_Endpoint, consts.MCR_Endpoint]

    for endpoint in endpoints:
        try:
            subprocess.check_output(['curl', '-L', '-o', '/dev/null', '-s', '-w', '"%{http_code}\n"', endpoint, '--max-time', '10'])
        except requests.exceptions.RequestException:
            all_validations_passed = False
            logger.warning("The endpoint {} is not reachable from your machine".format(endpoint))
    
    # Install specific version of connectedk8s
    get_default_cli().invoke(['extension', 'add', '-n', 'connectedk8s', '--version', '1.3.14'])
    
    try:
        cmd_show_arc= ['az', 'connectedk8s', 'show', '-n', name, '-g', resource_group_name, '-o', 'none']
        process = subprocess.Popen(cmd_show_arc, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.wait() == 0:
            print("The appliance name and resource group name passed already correspond to an existing connected cluster. Please try again with a different appliance name.")
            all_validations_passed = False
        stdout = process.stdout.read().decode()
        stderr = process.stderr.read().decode()
        if "ResourceGroupNotFound" in stdout or "ResourceGroupNotFound" in stderr:
            all_validations_passed = False
            print("The specified resource group could not be found. Please make sure the resource group exists in the specified subscription")
        if "AuthorizationFailed" in stdout or "AuthorizationFailed" in stderr:
            all_validations_passed = False
            print("The current user does not have the required Azure permissions to perform this action. Please assign the required roles.")

    except Exception as e:
        print(type(e))
        print(str(e))
    
    if all_validations_passed is False:
        telemetry.set_exception(exception="")
        raise ValidationError("One or more pre-requisite validations have failed. Please resolve them and try again")
    else:
        print("All pre-requisite validations have passed successfully")

def create_hybrid_appliance(resource_group_name, name, correlation_id=None, https_proxy="", http_proxy="", no_proxy="", proxy_cert="", location=None, tags=None):
    kubeconfig_path = utils.get_kubeconfig_path()
    kubectl_client_location = utils.install_kubectl_client()
    latestMajorVersion, latestMinorVersion = utils.get_latest_tested_microk8s_version()
    os.environ["MICROK8S_VERSION"] = "{}.{}".format(latestMajorVersion, latestMinorVersion)
    os.environ["KUBECTL_CLIENT_LOCATION"] = "{}".format(kubectl_client_location)
    os.environ["KUBECONFIG_PATH"]=kubeconfig_path

    current_path = os.path.abspath(os.path.dirname(__file__))
    script_file_path = os.path.join(current_path, "microk8sbootstrap.sh")
    cmd = ["sh", script_file_path]

    process = subprocess.Popen(cmd)
    if process.wait() != 0:
        raise CLIInternalError("Failed to setup microk8s cluster")
    
    if not utils.check_microk8s():
        raise CLIInternalError("Microk8s cluster is not running after setting up the cluster. Please check the logs tarball at /var/snap/microk8s/current")

    # Onboard the cluster to arc
    cmd_onboard_arc= ['connectedk8s', 'connect', '-n', name, '-g', resource_group_name, '--kube-config', kubeconfig_path]

    # The NO_PROXY env variable needs the api server address, which is not available with the user before the cluster is provisioned.
    # To get around that, we get the server address and services cidr and append the no_proxy variable with those values.
    if http_proxy or https_proxy or no_proxy:
        no_proxy = utils.get_proxy_parameters(no_proxy)
        os.environ["NO_PROXY"] = no_proxy
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
    if tags:
        cmd_onboard_arc.extend(["--tags", tags])

    onboarding_result = get_default_cli().invoke(cmd_onboard_arc)
    if onboarding_result != 0:
        raise CLIInternalError("Onboarding the k8s cluster to Arc failed")
    else:
        print("The k8s cluster has been onboarded to Arc successfully")

def upgrade_hybrid_appliance(resource_group_name, name):
    try:
        azure_clusterconfig_cm = subprocess.check_output(['microk8s', 'kubectl', 'get', 'cm', 'azure-clusterconfig', '-n', 'azure-arc', '-o', 'json']).decode()
    except Exception as e:
        if utils.check_microk8s():
            print("The required configmap was not found on the kubernetes cluster.") # Is there anything else which can be done in this case?
        else:
            print("The kubernetes cluster is not running as expected or is not reachable.")

        print("Please delete the appliance and create it again.")
        return
    
    azure_clusterconfig_cm = json.loads(azure_clusterconfig_cm)
    try:
        if azure_clusterconfig_cm["data"]["AZURE_RESOURCE_GROUP"] != resource_group_name or azure_clusterconfig_cm["data"]["AZURE_RESOURCE_NAME"] != name:
            raise ValidationError("The parameters passed do not correspond to this appliance. Please check the resource group name and appliance name.")
    except KeyError:
        raise CLIInternalError("The required entries were not found in the config map. Please delete the appliance and recreate it.")

    kubernetesVersionResponseString = subprocess.check_output(['microk8s', 'kubectl', 'version', '-o', 'json']).decode()
    kubernetesVersionResponse = json.loads(kubernetesVersionResponseString)
    currentMajorVersion = kubernetesVersionResponse["serverVersion"]["major"]
    currentMinorVersion =  kubernetesVersionResponse["serverVersion"]["minor"].strip('+') # For some versions, for example, 1.23, minor version is represented as 23+ 
    
    latestMajorVersion, latestMinorVersion = utils.get_latest_tested_microk8s_version()

    if currentMajorVersion == latestMajorVersion and currentMinorVersion == latestMinorVersion:
        print("The kubernetes cluster is already at the latest available version.")
    else:
        if currentMinorVersion > latestMinorVersion:
             # This should never happen unless someone manually runs "snap refresh" against the cluster instead of using our cli command.
             # Microk8s recommends never to downgrade a cluster, as this behaviour is not tested or supported 
            raise ValidationError("The current version of the kubernetes cluster is greater than the latest supported version. Please delete the appliance and create it again.")
        
        # This logic works as long as new versions are only minor version bumps
        # TODO: Figure out what to do in case major version is bumped (very unlikely)
        while currentMinorVersion != latestMinorVersion:
            currentMinorVersion = int(currentMinorVersion) + 1
            process = subprocess.Popen(['snap', 'refresh', 'microk8s', '--channel={}.{}'.format(currentMajorVersion, currentMinorVersion)])
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise CLIInternalError("Failed to upgrade microk8s cluster: {}".format(stderr.decode()))
            try:
                subprocess.check_call(['microk8s', 'start'])
            except subprocess.CalledProcessError as e:
                raise CLIInternalError("Failed to start microk8s cluster with exception {}".format(str(e)))

            if not utils.check_microk8s():
                raise CLIInternalError("Cluster is not healthy after upgrading to {}.{}. Please check the logs at /var/snap/microk8s/current.".format(currentMajorVersion, currentMinorVersion))

            print("Upgraded cluster to {}.{}".format(currentMajorVersion, currentMinorVersion))

def delete_hybrid_appliance(resource_group_name, name):
    delete_cc = True
    utils.set_no_proxy_from_helm_values()
    kubeconfig_path = utils.get_kubeconfig_path()
    try:
        output = subprocess.check_output(['microk8s', 'status'], stderr=STDOUT)
    except:
        raise ValidationError("There is no microk8s cluster running on this machine. Please ensure you are running the command on the machine where the cluster is running.")

    if "not running" in output.decode():
            raise ValidationError("There is no microk8s cluster running on this machine. Please ensure you are running the command on the machine where the cluster is running.")

    try:
        azure_clusterconfig_cm = subprocess.check_output(['microk8s', 'kubectl', 'get', 'cm', 'azure-clusterconfig', '-n', 'azure-arc', '-o', 'json']).decode()
    except Exception as e:
        logger.error("Unable to find the required config map on the kubernetes cluster. The kubernetes cluster will be deleted.")
        delete_cc = False
    
    azure_clusterconfig_cm = json.loads(azure_clusterconfig_cm)
    try:
        if azure_clusterconfig_cm["data"]["AZURE_RESOURCE_GROUP"] != resource_group_name or azure_clusterconfig_cm["data"]["AZURE_RESOURCE_NAME"] != name:
            raise ValidationError("The parameters passed do not correspond to this appliance. Please check the resource group name and appliance name.")
    except KeyError:
        logger.error("The required entries were not found in the config map. The kubernetes cluster will be deleted")
        delete_cc = False

    if delete_cc:
        cmd_delete_arc= ['connectedk8s', 'delete', '-n', name, '-g', resource_group_name, '-y', '--kube-config', kubeconfig_path]
        delete_result = get_default_cli().invoke(cmd_delete_arc)
        if delete_result != 0:
            logger.error("Failed to delete connected cluster resource. The kubernetes cluster will be deleted. To delete the connected cluster resource, please visit the resource group in the Azure portal and delete the corresponding Azure resource.")
    else:
        logger.warning("The connected cluster resource will not be deleted. The kubernetes cluster will be deleted. To delete the connected cluster resource, please visit the resource group in the Azure portal and delete the corresponding Azure resource.")

    process = subprocess.Popen(['snap', 'remove', 'microk8s'])
    process.wait()
    if process.returncode != 0:
        logger.error("Failed to remove microk8s cluster")
        return_code = subprocess.Popen(['microk8s', 'inspect']).wait()
        if return_code == 0:
            logger.warning("Please share the logs generated at the above path, under /var/snap/microk8s/current")