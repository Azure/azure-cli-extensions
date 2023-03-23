import os
import json
import yaml
import requests
import subprocess
import logging
from knack.log import get_logger
from azure.cli.core import get_default_cli
from azure.cli.core import telemetry
from azext_hybrid_appliance import _constants as consts
from azure.cli.core.azclierror import CLIInternalError
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
        helmValuesYaml = subprocess.check_output(['microk8s', 'helm', 'get', 'values', 'azure-arc', '-n', 'azure-arc-release'])
    except:
        print("Failed to get helm values for the azure-arc release.")
        return
    
    helmValues = yaml.safe_load(helmValuesYaml)
    try:
        os.environ["NO_PROXY"] = helmValues["global"]["noProxy"]
    except KeyError:
        pass # The cluster is not behind proxy.
    except:
        print("Failed to check if cluster is behind proxy.")