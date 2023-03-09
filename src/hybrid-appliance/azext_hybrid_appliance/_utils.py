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

def get_latest_tested_microsk8_version():
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