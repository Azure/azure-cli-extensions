# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import time
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
from kubernetes import client as kube_client, config
logger = get_logger(__name__)


def validate_hybrid_appliance(cmd, resource_group_name, name, validate_connectedk8s_exists=True):
    # changing cli config to push telemetry in 1 hr interval
    try:
        if cmd.cli_ctx and hasattr(cmd.cli_ctx, 'config'):
            cmd.cli_ctx.config.set_value('telemetry', 'push_interval_in_hours', '1')
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Failed_To_Change_Telemetry_Push_Interval, summary="Failed to change the telemetry push interval to 1 hr")

    all_validations_passed = True

    # Check if the operating system is Linux
    if not psutil.LINUX:
        all_validations_passed = False
        telemetry.set_exception(exception="User's machine is not linux machine", fault_type=consts.Non_Linux_Machine, summary="User's machine is not linux machine")
        logger.warning("This program can only run on a Linux machine")

    # Check if the disk space is at least 20GB
    disk_usage = psutil.disk_usage('/')
    if disk_usage.total < consts.Disk_Threshold * 1024 * 1024 * 1024:
        all_validations_passed = False
        telemetry.set_exception(exception="Machine doesn't meet min {}GB disk space requirement".format(consts.Disk_Threshold), fault_type=consts.DiskSpace_Validation_Failed, summary="Machine doesn't meen min disk space threshold")
        logger.warning("This program requires at least {}GB of disk space".format(consts.Disk_Threshold))

    # Check if the memory is at least 4GB
    memory = psutil.virtual_memory()
    if memory.total < consts.Memory_Threshold * 1024 * 1024 * 1024:
        all_validations_passed = False
        telemetry.set_exception(exception="Machine doesn't meet min {}GB memory requirement".format(consts.Memory_Threshold), fault_type=consts.Memory_Validation_Failed, summary="Machine doesn't meet min memory threshold")
        logger.warning("This program requires at least {}GB of memory".format(consts.Memory_Threshold))
    
    # Check if pre-req endpoints are reachable
    endpoints = ["{}/{}/{}".format(consts.Snap_Config_Storage_End_Point, consts.Snap_Config_Container_Name, consts.Snap_Config_File_Name), consts.Snap_Pull_Public_Api_Endpoint, consts.Snap_Pull_Public_Storage_Endpoint, consts.App_Insights_Endpoint, consts.MCR_Endpoint]

    for endpoint in endpoints:
        endpoints_reachability_check = True
        try:
            subprocess.check_output(['curl', '-L', '-o', '/dev/null', '-s', '-w', '"%{http_code}\n"', endpoint, '--max-time', '10'])
        except requests.exceptions.RequestException:
            all_validations_passed = False
            endpoints_reachability_check = False
            logger.warning("The endpoint {} is not reachable from your machine".format(endpoint))
    if endpoints_reachability_check is False:
        telemetry.set_exception(exception="Pre-requisite endpoints reachability validation failed", fault_type=consts.Endpoints_Reachability_Validation_Failed, summary="Pre-requisite endpoints reachability validation failed")
    # Install specific version of connectedk8s
    get_default_cli().invoke(['extension', 'add', '-n', 'connectedk8s', '--version', '1.3.14'])
    
    if validate_connectedk8s_exists:
        try:
            cmd_show_arc= ['az', 'connectedk8s', 'show', '-n', name, '-g', resource_group_name, '-o', 'none']
            process = subprocess.Popen(cmd_show_arc, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.wait() == 0:
                telemetry.set_exception(exception="An appliance with same name already exists in the resource group", fault_type=consts.Resource_Already_Exists_Fault_Type, summary="Appliance resource with same name already exists")
                logger.warning("The appliance name and resource group name passed already correspond to an existing connected cluster. Please try again with a different appliance name.")
                all_validations_passed = False
            stdout = process.stdout.read().decode()
            stderr = process.stderr.read().decode()
            if "ResourceGroupNotFound" in stdout or "ResourceGroupNotFound" in stderr:
                all_validations_passed = False
                logger.warning("The specified resource group could not be found. Please make sure the resource group exists in the specified subscription")
            if "AuthorizationFailed" in stdout or "AuthorizationFailed" in stderr:
                all_validations_passed = False
                logger.warning("The current user does not have the required Azure permissions to perform this action. Please assign the required roles.")

        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.CC_Resource_Get_Failed, summary="Failed to verify if CC resource already exists")
            logger.warning("An exception has occurred while trying verify if appliance resource already exists with the same name. Exception:" + str(e))
    
    if all_validations_passed is False:
        telemetry.set_exception(exception="One or more pre-requisite validations failed", fault_type=consts.Validations_Failed, summary="Pre-requisite validations failed")
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
        telemetry.set_exception(exception="Microk8s cluster setup failed", fault_type=consts.MicroK8s_Setup_Failed, summary="Microk8s cluster provisioning failed")
        raise CLIInternalError("Failed to setup microk8s cluster")
    
    if not utils.check_microk8s():
        telemetry.set_exception(exception="Microk8s cluster is not running", fault_type=consts.MicroK8s_Cluster_Not_Running, summary="Microk8s cluster is not running after the set up")
        raise CLIInternalError("Microk8s cluster is not running after setting up the cluster. Please check the logs tarball at /var/snap/microk8s/current")

    # Onboard the cluster to arc
    cmd_onboard_arc= ['connectedk8s', 'connect', '-n', name, '-g', resource_group_name, '--kube-config', kubeconfig_path]

    # The NO_PROXY env variable needs the api server address, which is not available with the user before the cluster is provisioned.
    # To get around that, we get the server address and services cidr and append the no_proxy variable with those values.
    if http_proxy or https_proxy or no_proxy:
        no_proxy = utils.get_no_proxy_parameters(no_proxy)
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
        cmd_onboard_arc.extend(["--tags"])
        for tag in tags:
            cmd_onboard_arc.extend(["{}={}".format(tag, tags[tag])])

    onboarding_result = get_default_cli().invoke(cmd_onboard_arc)
    if onboarding_result != 0:
        telemetry.set_exception(exception="Arc onboarding of the k8s cluster failed", fault_type=consts.Arc_Onboarding_Failed, summary="Arc onboarding of the k8s cluster failed")
        filepath_with_timestamp, diagnostic_folder_status = utils.create_folder_diagnosticlogs(consts.diagnostics_folder_name, name)

        if not diagnostic_folder_status:
            raise ValidationError("Unable to create the folder to store diagnostics logs.")
            
        utils.troubleshoot_connectedk8s(resource_group_name, name, filepath_with_timestamp)
        raise CLIInternalError("Onboarding the k8s cluster to Arc failed")
    else:
        print("The k8s cluster has been onboarded to Arc successfully")

def upgrade_hybrid_appliance(resource_group_name, name):
    config.load_kube_config(utils.get_kubeconfig_path())
    api_instance = kube_client.CoreV1Api()
    try:
        azure_clusterconfig_cm = api_instance.read_namespaced_config_map("azure-clusterconfig", "azure-arc")
    except Exception as e:
        utils.kubernetes_exception_handler(e, fault_type=consts.Read_ConfigMap_Fault_Type, summary="Unable to read ConfigMap")
            
    try:
        if azure_clusterconfig_cm.data["AZURE_RESOURCE_GROUP"] != resource_group_name or azure_clusterconfig_cm.data["AZURE_RESOURCE_NAME"] != name:
            telemetry.set_exception(exception='The provided name and rg correspond to different appliance', fault_type=consts.Upgrade_RG_Cluster_Name_Conflict,
                                    summary='The provided name and resource group name do not correspond to the current appliance')
            raise ValidationError("The parameters passed do not correspond to this appliance", "Please check the resource group name and appliance name.")
    except KeyError:
        telemetry.set_exception(exception="Name and RG entries not found in configmap", fault_type=consts.Entries_Not_Found_In_ConfigMap, summary="Name and RG entries not found in configmap")
        raise ValidationError("The required entries were not found in the config map.",  "Please delete the appliance and recreate it.")

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
            telemetry.set_exception(exception="K8s version greater than latest supported", fault_type=consts.Unsupported_K8s_Version, summary="K8s version greater than latest supported")
            raise ValidationError("The current version of the kubernetes cluster is greater than the latest supported version.",  "Please delete the appliance and create it again.")
        
        # This logic works as long as new versions are only minor version bumps
        # TODO: Figure out what to do in case major version is bumped (very unlikely)
        while int(currentMinorVersion) != int(latestMinorVersion):
            currentMinorVersion = int(currentMinorVersion) + 1
            process = subprocess.Popen(['snap', 'refresh', 'microk8s', '--channel={}.{}'.format(currentMajorVersion, currentMinorVersion)])
            _, stderr = process.communicate()
            if process.returncode != 0:
                error_message = ""
                if stderr is not None:
                    error_message = ": {}".format(stderr.decode())
                telemetry.set_exception(exception="Failed to upgrade microk8s cluster{}".format(error_message), fault_type=consts.MicroK8s_Upgrade_Failed, summary="Failed to upgrade microk8s cluster: {}".format(stderr.decode()))
                raise CLIInternalError("Failed to upgrade microk8s cluster{}}".format(error_message))
            
            time.sleep(60) # Sleep to give time for the cluster to get ready
            try:
                subprocess.check_call(['microk8s', 'start'])
            except subprocess.CalledProcessError as e:
                telemetry.set_exception(exception=e, fault_type=consts.Failed_To_Start_Microk8s, summary="Failed to start microk8s cluster with exception {}".format(str(e)))
                raise CLIInternalError("Failed to start microk8s cluster with exception {}".format(str(e)))

            if not utils.check_microk8s():
                telemetry.set_exception(exception="Microk8s not healthy after upgrade from {} to {}".format(currentMajorVersion, currentMinorVersion), fault_type=consts.MicroK8s_Unhealthy_Post_Upgrade, summary="MicroK8s cluster is unhealthy post upgradefrom {} to {}".format(currentMajorVersion, currentMinorVersion))
                raise CLIInternalError("Cluster is not healthy after upgrading to {}.{}. Please check the logs at /var/snap/microk8s/current.".format(currentMajorVersion, currentMinorVersion))

            print("Upgraded cluster to {}.{}".format(currentMajorVersion, currentMinorVersion))

def delete_hybrid_appliance(resource_group_name, name):
    delete_cc = True
    kubeconfig_path = utils.get_kubeconfig_path()
    if not utils.check_if_microk8s_is_running():
        telemetry.set_exception()
        raise ValidationError("There is no microk8s cluster running on this machine. Please ensure you are running the command on the machine where the cluster is running.")
    
    try:
        azure_clusterconfig_cm = utils.get_azure_clusterconfig_cm()
    except Exception as ex:
        telemetry.set_exception(exception=e, fault_type=consts.ConfigMap_Not_Found, summary="Config Map 'azure-clusterconfig' not found on the k8s cluster")
        raise CLIInternalError("Unable to find the required config map on the kubernetes cluster. Please delete the appliance and create it again.")
        delete_cc = False

    if delete_cc:
        try:
            utils.validate_cluster_resource_group_and_name(azure_clusterconfig_cm, resource_group_name, name)
        except Exception as ex:
            raise ValidationError("Failed to validate the configmap: {}.".format(str(ex)))

    if delete_cc:
        utils.set_no_proxy_from_helm_values()
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

def collect_logs(resource_group_name, name):
    try:
        validate_hybrid_appliance(resource_group_name, name, validate_connectedk8s_exists=False)
    except Exception as ex:
        logger.warning("One or more of the required prechecks have failed. Please ensure all the pre-requisites are met.")

    troubleshoot_connectedk8s = True
    if not utils.check_if_microk8s_is_running():
        telemetry.set_exception()
        raise ValidationError("There is no microk8s cluster running on this machine. Please ensure you are running the command on the machine where the cluster is running.")
    
    try:
        azure_clusterconfig_cm = utils.get_azure_clusterconfig_cm()
    except:
        logger.warning("Failed to get the configmap from the cluster. Not running connectedk8s troubleshoot")
        troubleshoot_connectedk8s = False

    if troubleshoot_connectedk8s:
        try:
            utils.validate_cluster_resource_group_and_name(azure_clusterconfig_cm, resource_group_name, name)    
        except Exception as ex:
            logger.warning("Failed to validate the configmap: {}. Not running connectedk8s troubleshoot".format(str(ex)))
            troubleshoot_connectedk8s = False

    filepath_with_timestamp, diagnostic_folder_status = utils.create_folder_diagnosticlogs(consts.diagnostics_folder_name, name)

    if not diagnostic_folder_status:
        logger.error("Unable to create the folder to store diagnostics logs.")
        return
    
    if troubleshoot_connectedk8s:
        try:
            utils.troubleshoot_connectedk8s(resource_group_name, name, filepath_with_timestamp)
        except Exception as ex:
            logger.warning(str(ex))

    os.environ["TROUBLESHOOT_DIRECTORY"] = filepath_with_timestamp
    current_path = os.path.abspath(os.path.dirname(__file__))
    script_file_path = os.path.join(current_path, "microk8s_inspect.sh")
    cmd = ["bash", script_file_path]
    process = subprocess.Popen(cmd)
    if process.wait() != 0:
        telemetry.set_exception(exception="Failed to run microk8s inspect", fault_type=consts.Microk8s_Inspect_Failed, summary="Microk8s inspect failed")
        raise CLIInternalError("Failed to run microk8s inspect")
    
    logger.warning("The logs have been stored at {}".format(filepath_with_timestamp))
    
