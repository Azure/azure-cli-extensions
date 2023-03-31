import os
import json
import shutil
import time
import yaml
import requests
import subprocess
import logging
from knack.log import get_logger
from azure.cli.core import get_default_cli
from azure.cli.core import telemetry
from azext_hybrid_appliance import _constants as consts
from azure.cli.core.azclierror import CLIInternalError, ValidationError
from kubernetes.client.rest import ApiException
from kubernetes import client as kube_client, config
logger = get_logger(__name__)

def install_kubectl_client():
    # Return kubectl client path set by user
    try:

        # Fetching the current directory where the cli installs the kubectl executable
        home_dir = os.path.expanduser('~')
        kubectl_filepath = os.path.join(home_dir, '.azure', 'kubectl-client')

        try:
            os.mkdir(kubectl_filepath)
        except FileExistsError:
            pass

        kubectl_path = os.path.join(kubectl_filepath, 'kubectl')

        if os.path.isfile(kubectl_path):
            return kubectl_path

        # Downloading kubectl executable if its not present in the machine
        logger.warning("Downloading kubectl client for first time. This can take few minutes...")
        logging.disable(logging.CRITICAL)
        get_default_cli().invoke(['aks', 'install-cli', '--install-location', kubectl_path])
        logging.disable(logging.NOTSET)
        logger.warning("\n")
        # Return the path of the kubectl executable
        return kubectl_path

    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Download_And_Install_Kubectl_Fault_Type, summary="Failed to download and install kubectl")
        raise CLIInternalError("Unable to install kubectl. Error: ", str(e))

def get_latest_tested_microk8s_version():
    response = requests.get("{}/{}/{}".format(consts.Snap_Config_Storage_End_Point, consts.Snap_Config_Container_Name, consts.Snap_Config_File_Name))
    return json.loads(response.content.decode())["latestTested"].split('.')

def check_microk8s():
    statusYaml = subprocess.check_output(['microk8s', 'status', '--format', 'yaml']).decode()
    status = yaml.safe_load(statusYaml)
    if not status["microk8s"]["running"]:
        print(status)
        print("Microk8s is not running")
        subprocess.check_call(['microk8s', 'inspect'])
        return False
    return True

def get_api_server_address() -> str:
    kubeconfig_path = get_kubeconfig_path()
    config = yaml.safe_load(open(kubeconfig_path))
    return config["clusters"][0]["cluster"]["server"]

def get_services_cidr():
    try:
        services = subprocess.check_output(['microk8s', 'kubectl', 'get', 'svc', '-A', '-o', 'json']).decode()
    except:
        raise CLIInternalError("Failed to connect to kubernetes cluster to get services")

    services = json.loads(services)
    # return services
    try:
        service_IP = services["items"][0]["spec"]["clusterIP"]
    except KeyError:
        raise CLIInternalError("The required entries are not present in the service")
    
    service_IP_fragments = service_IP.split('.')
    return "{}.{}.0.0/16".format(service_IP_fragments[0], service_IP_fragments[1])

def get_kubeconfig_path():
    home_dir = os.path.expanduser('~')
    kubeconfig_path = os.path.join(home_dir, '.azure', 'hybrid_appliance', 'config')
    return kubeconfig_path

def get_no_proxy_parameters(no_proxy):
    api_server_address = get_api_server_address()
    api_server_address = api_server_address.strip('https://')
    service_cidr = get_services_cidr()
    if no_proxy is None:
        no_proxy = "{},{},{}".format(api_server_address, service_cidr, "kubernetes.default.svc")
    else:
        no_proxy = "{},{},{},{}".format(api_server_address, service_cidr, "kubernetes.default.svc", no_proxy)
    return no_proxy

def set_no_proxy_from_helm_values():
    try:
        helmValuesYaml = subprocess.check_output(['microk8s', 'helm', 'get', 'values', 'azure-arc', '-n', 'azure-arc-release'], stderr=subprocess.STDOUT)
    except:
        if "release: not found" in helmValuesYaml:
            return
        print("Failed to get helm values for the azure-arc release.")
        return
    
    helmValues = yaml.safe_load(helmValuesYaml)
    try:
        os.environ["NO_PROXY"] = helmValues["global"]["noProxy"]
    except KeyError:
        pass # The cluster is not behind proxy.
    except:
        print("Failed to check if cluster is behind proxy.")

def kubernetes_exception_handler(ex, fault_type, summary, error_message='Error occured while connecting to the kubernetes cluster: ',
                                 message_for_unauthorized_request='The user does not have required privileges on the kubernetes cluster to deploy Azure Arc enabled Kubernetes agents. Please ensure you have cluster admin privileges on the cluster to onboard.',
                                 message_for_not_found='The requested kubernetes resource was not found.', raise_error=True):
    telemetry.set_user_fault()
    if isinstance(ex, ApiException):
        status_code = ex.status
        if status_code == 403:
            logger.warning(message_for_unauthorized_request)
        elif status_code == 404:
            logger.warning(message_for_not_found)
        else:
            logger.debug("Kubernetes Exception: " + str(ex))
        if raise_error:
            telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
            raise ValidationError(error_message + "\nError Response: " + str(ex.body))
    else:
        if raise_error:
            telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
            raise ValidationError(error_message + "\nError: " + str(ex))
        else:
            logger.debug("Kubernetes Exception: " + str(ex))

def check_if_microk8s_is_running():
    try:
        output = subprocess.check_output(['microk8s', 'status'], stderr=subprocess.STDOUT)
    except:
        return False
    
    if output is None or "not running" in output.decode():
        return False

    return True

def get_azure_clusterconfig_cm():
    config.load_kube_config(get_kubeconfig_path())
    api_instance = kube_client.CoreV1Api()
    try:
        azure_clusterconfig_cm = api_instance.read_namespaced_config_map("azure-clusterconfig", "azure-arc")
        return azure_clusterconfig_cm
    except Exception as e:
        kubernetes_exception_handler(e, fault_type=consts.Read_ConfigMap_Fault_Type, summary="Unable to read ConfigMap", raise_error=False)

def validate_cluster_resource_group_and_name(azure_clusterconfig_cm, resource_group_name, name):
    try:
        if azure_clusterconfig_cm.data["AZURE_RESOURCE_GROUP"] != resource_group_name or azure_clusterconfig_cm.data["AZURE_RESOURCE_NAME"] != name:
            telemetry.set_exception()
            raise ValidationError("The parameters passed do not correspond to this appliance. Please check the resource group name and appliance name")
    except KeyError:
        raise ValidationError("The required entries were not found in the config map")
        

def troubleshoot_connectedk8s(resource_group_name, name, filepath):
    os.environ["TROUBLESHOOT_DIRECTORY"] = filepath
    os.environ["RESOURCE_GROUP"] = resource_group_name
    os.environ["APPLIANCE_NAME"] = name
    os.environ["KUBECONFIG_PATH"] = get_kubeconfig_path()
    
    current_path = os.path.abspath(os.path.dirname(__file__))
    script_file_path = os.path.join(current_path, "connectedk8s_troubleshoot.sh")
    cmd = ["bash", script_file_path]
    process = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
    if process.wait() != 0:
        telemetry.set_exception(exception="Failed to run connectedk8s troubleshoot", fault_type=consts.Connectedk8s_Troubleshoot_Failed, summary="Connectedk8s troubleshoot failed")
        raise CLIInternalError("Failed to run connectedk8s troubleshoot")

def create_folder_diagnosticlogs(folder_name, appliance_name):
    current_time = time.ctime(time.time())
    time_stamp = ""
    for elements in current_time:
        if(elements == ' '):
            time_stamp += '-'
            continue
        elif(elements == ':'):
            time_stamp += '.'
            continue
        time_stamp += elements
    time_stamp = appliance_name + '-' + time_stamp
    try:
        # Fetching path to user directory to create the arc diagnostic folder
        home_dir = os.path.expanduser('~')
        filepath = os.path.join(home_dir, '.azure', 'hybrid_appliance', folder_name)
        # Creating Diagnostic folder and its subfolder with the given timestamp and cluster name to store all the logs
        try:
            os.mkdir(filepath)
        except FileExistsError:
            pass
        filepath_with_timestamp = os.path.join(filepath, time_stamp)
        try:
            os.mkdir(filepath_with_timestamp)
        except FileExistsError:
            # Deleting the folder if present with the same timestamp to prevent overriding in the same folder and then creating it again
            shutil.rmtree(filepath_with_timestamp, ignore_errors=True)
            os.mkdir(filepath_with_timestamp)
            pass

        return filepath_with_timestamp, True

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            return "", False
        else:
            logger.warning("An exception has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type, summary="Error while trying to create diagnostic logs folder")
            return "", False

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type, summary="Error while trying to create diagnostic logs folder")
        return "", False