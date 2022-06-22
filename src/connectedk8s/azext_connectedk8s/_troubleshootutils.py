# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import Namespace
from kubernetes import client, config, watch, utils
from binascii import a2b_hex
import csv
import errno
import subprocess
from logging import exception
import os
import json
import tempfile
import time
import datetime
import base64
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from base64 import b64encode, b64decode
import stat
import platform
from unicodedata import name
from azure.core.exceptions import ClientAuthenticationError
import yaml
import requests
import urllib.request
import shutil
from _thread import interrupt_main
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.prompting import NoTTYException
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core._profile import Profile
from azure.cli.core.util import sdk_no_wait
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ManualInterrupt, InvalidArgumentValueError, UnclassifiedUserFault, CLIInternalError, FileOperationError, ClientRequestError, DeploymentError, ValidationError, ArgumentUsageError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from azext_connectedk8s._client_factory import _resource_providers_client
from azext_connectedk8s._client_factory import get_graph_client_service_principals
import azext_connectedk8s._constants as consts
import azext_connectedk8s.custom as custom
from glob import glob
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterIdentity, ListClusterUserCredentialProperties
from threading import Timer, Thread
import sys
import hashlib
import re
from azure.cli.core import get_default_cli
import urllib.request
logger = get_logger(__name__)
# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long

# def connect(host='http://portal.azure.com'):
#     try:
#         urllib.request.urlopen(host)
#         return True
#     except:
#         return False

# def check_internet_connectivity():
#     if connect():
#         return True
#     else:
#         return False

def create_folder_diagnosticlogs(time_stamp):

    home_dir = os.path.expanduser( '~' )
    filepath = os.path.join( home_dir, 'diagnostic_logs' )
    # Creating the Diagnoser Folder and adding it if its not already present
    try:
        os.mkdir(filepath)
    except FileExistsError:
        pass

    # Creating Subfolder with the given timestamp to store all the logs
    filepath_with_timestamp = os.path.join(filepath, time_stamp) 
    try:
        os.mkdir(filepath_with_timestamp)
    except FileExistsError:
        pass
    return filepath_with_timestamp


def arc_agents_logger(corev1_api_instance, filepath_with_timestamp ):

    # To retrieve all of the arc agents pods that are presesnt in the Cluster
    arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

    # Traversing thorugh all agents
    for each_agent_pod in arc_agents_pod_list.items:

        # Fethcing the current Pod name and creating a folder with that name inside the timestamp folder
        agent_name = each_agent_pod.metadata.name
        path = (filepath_with_timestamp + "\Arc_Agents_logs")
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        path = (filepath_with_timestamp + "\Arc_Agents_logs\ " + agent_name)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        # If the agent is not in Running state we wont be able to get logs of the containers
        if(each_agent_pod.status.phase != "Running"):
            continue

        # Traversing through all of the containers present inside each pods
        for each_container in each_agent_pod.spec.containers:

            # Fetching the Container name
            container_name = each_container.name

            # Creating a text file with the name of the container and adding that containers logs in it
            container_log = corev1_api_instance.read_namespaced_pod_log(name=agent_name, container=container_name, namespace="azure-arc")
            with open(filepath_with_timestamp + "\Arc_Agents_logs\ " + agent_name + "\ " + container_name + ".txt", 'w+') as container_file:
                container_file.write(str(container_log))


def deployments_logger(appv1_api_instance, filepath_with_timestamp ):

    # Creating new Deployment Logs folder in the given timestamp folder
    path = filepath_with_timestamp + "\Deployment_logs"
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    # To retrieve all the the deployements that are present in the Cluster
    deployments_list = appv1_api_instance.list_namespaced_deployment("azure-arc")

    # Traversing through all the deployments present
    for deployment in deployments_list.items:

        # Fetching the deployment name
        deployment_name = deployment.metadata.name

        # Creating a text file with the name of the deployment and adding deployment status in it
        with open(filepath_with_timestamp + "\Deployment_logs\ " + deployment_name + ".txt", 'w+') as deployment_file:
            deployment_file.write(str(deployment.status))


def check_agent_state(corev1_api_instance, filepath_with_timestamp ):

    with open(filepath_with_timestamp + "\Agent_State.txt", 'w+') as agent_state:

        # To retrieve all of the arc agent pods that are presesnt in the Cluster
        arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

        # Check if any arc agent other than kube aadp proxy is not in Running state
        counter = 0
        for each_agent_pod in arc_agents_pod_list.items:

            # Storing the state of the arc agent in the user machine
            agent_state.write(each_agent_pod.metadata.name + " = " + each_agent_pod.status.phase + "\n")

            # If the agent is Kube add proxy we will continue with the next agent
            if(each_agent_pod.metadata.name.startswith("kube-aad-proxy")):
                continue
            if each_agent_pod.status.phase != 'Running':
                counter = 1

        # Displaying error if the arc agents are in pending state.
        if counter:
            print("Error: One or more Azure Arc agents are in pending state. It may be caused due to insufficient resource availability on the cluster.\n For more details on resource requirement visit 'aka.ms\\arcenabledkubernetesresourcerequirement'. \n")
            return False

        return True


def check_agent_version(connected_cluster, azure_arc_agent_version):

    # If the agent version in the connected cluster resource is none skip the check
    if(connected_cluster.agent_version is None):
        return True

    # To get user agent verison and the latest agent version
    user_agent_version = connected_cluster.agent_version
    current_user_version = user_agent_version.split('.')
    latest_agent_version = azure_arc_agent_version.split('.')

    # Comparing if the user version is comaptible or not
    if((int(current_user_version[0]) < int(latest_agent_version[0])) or (int(latest_agent_version[1]) - int(current_user_version[1]) > 2)):
        print("Error: We found that you are on an older agent version thats not supported.\n Please visit this link to know the agent version support policy 'link'.\n")
        return False

    return True


def executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, namespace):

    # Setting the log output as Empty
    diagnoser_container_log = ""

    # To handle the user keyboard Interrupt
    try:

        # Executing the diagnoser_job.yaml
        config.load_kube_config()
        k8s_client = client.ApiClient()
        yaml_file = "TroubleshootTemplates\\diagnoser_job.yaml"
        try:
            utils.create_from_yaml(k8s_client, yaml_file)
        except Exception as e:
            pass

        # Watching for diagnosercontianer to reach in completed stage
        w = watch.Watch()
        counter = 0
        for event in w.stream(batchv1_api_instance.list_namespaced_job, namespace=namespace, label_selector="", timeout_seconds=90):
            try:
                if event["object"].metadata.name == "diagnosercontainer" and event["object"].status.conditions[0].type == "Complete":
                    counter = 1
                    w.stop()

            except Exception as e:
                continue
            else:
                continue

        # If container not created then clearing all the reosurce with proper error message
        if(counter == 0):

            subprocess.run(["kubectl", "delete", "-f", "TroubleshootTemplates\\diagnoser_job.yaml"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        else:

            # Fetching the Diagnoser Container logs
            try:

                job_name = "diagnosercontainer"

                all_pods = corev1_api_instance.list_namespaced_pod(namespace)
                # Traversing thorugh all agents
                for each_pod in all_pods.items:

                    # Fethcing the current Pod name and creating a folder with that name inside the timestamp folder
                    pod_name = each_pod.metadata.name

                    if(pod_name.startswith(job_name)):

                        # Creating a text file with the name of the container and adding that containers logs in it
                        diagnoser_container_log = corev1_api_instance.read_namespaced_pod_log(name=pod_name, container="networktest1", namespace=namespace)

                # Clearing all the resources after fetching the diagnoser container logs
                subprocess.run(["kubectl", "delete", "-f", "TroubleshootTemplates\\diagnoser_job.yaml"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            except Exception as e:
                subprocess.run(["kubectl", "delete", "-f", "TroubleshootTemplates\\diagnoser_job.yaml"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except KeyboardInterrupt:
        # If process terminated by user then delete the resources if any added to the cluster.
        subprocess.run(["kubectl", "delete", "-f", "TroubleshootTemplates\\diagnoser_job.yaml"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return diagnoser_container_log


def diagnoser_container_check(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp , namespace):

    # Setting DNS and Outbound Check as working
    dns_check = True
    outbound_connectivity_check = True

    # Executing the Diagnoser job and fetching the logs obtained
    diagnoser_container_log = executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, namespace)

    if(diagnoser_container_log != ""):
        dns_check = check_cluster_DNS(diagnoser_container_log, filepath_with_timestamp )
        outbound_connectivity_check = check_cluster_outbound_connectivity(diagnoser_container_log, filepath_with_timestamp )

    if(dns_check and outbound_connectivity_check):
        return True
    return False


def check_cluster_DNS(diagnoser_container_log, filepath_with_timestamp ):

    # To retreive only the DNS lookup result from the diagnoser container logs
    dns_check = diagnoser_container_log[0:len(diagnoser_container_log) - 5:]

    # Validating if DNS is working or not and displaying proper result
    if("NXDOMAIN" in dns_check or "connection timed out" in dns_check):
        print("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
        with open(filepath_with_timestamp + "\DNS_Check.txt", 'w+') as dns:
            dns.write(dns_check + "\nWe found an issue with the DNS resolution on your cluster.")
            return False

    else:
        with open(filepath_with_timestamp + "\DNS_Check.txt", 'w+') as dns:
            dns.write(dns_check + "\nCluster DNS check passed successfully.")
            return True


def check_cluster_outbound_connectivity(diagnoser_container_log, filepath_with_timestamp ):

    # To retreive only the outbound connectivity result from the diagnoser container logs
    outbound_check = diagnoser_container_log[-4:-1:]

    # Validating if outbound connectiivty is working or not and displaying proper result
    if(outbound_check != "000"):
        with open(filepath_with_timestamp + "\Outbound_Network_Connectivity_Check.txt", 'w+') as dns:
            dns.write("Response code " + outbound_check + "\nOutbound network connectivity check passed successfully.")
            return True
    else:
        print("Error: We found an issue with outbound network connectivity from the cluster.\nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy paramaters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server'.\nPlease ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements' \n")
        with open(filepath_with_timestamp + "\Outbound_Network_Connectivity_Check.txt", 'w+') as dns:
            dns.write("Response code " + outbound_check + "\nWe found an issue with Outbound network connectivity from the cluster.")
            return False


def check_msi_certificate(corev1_api_instance):

    # Initializing msi certificate as not present
    msi_cert_present = False

    # Going thorugh all the secrets in azure-arc
    all_secrets_azurearc = corev1_api_instance.list_namespaced_secret(namespace="azure-arc")

    for secrets in all_secrets_azurearc.items:

        # If name of secret is azure-identity-certificate then we stop there
        if(secrets.metadata.name == "azure-identity-certificate"):
            msi_cert_present = True

    # Checking if msi cerificate is present or not
    if not msi_cert_present:
        print("Error: Unable to pull MSI certificate. Refer this link to for more information 'msi_cert_link'\n")
        return False

    return True


def check_cluster_security_policy(corev1_api_instance):

    # Intializing the kap_pod_present and cluster_connect_feature variable as False
    kap_pod_present = False
    cluster_connect_feature = False

    # CMD command to get helm values in azure arc and converting it to json format
    command = ["helm", "get", "values", "azure-arc", "-o", "json"]

    # Using subprocess to execute the helm get values command and fetching the output
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    text = p.stdout.read()

    # Converting output obtained in json format and fetching the clusterconnect-agent feature
    my_json = json.loads(text)
    cluster_connect_feature = my_json["systemDefaultValues"]["clusterconnect-agent"]["enabled"]

    # To retrieve all of the arc agent pods that are presesnt in the Cluster
    arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

    # Traversing thorugh all agents and checking if the Kube aad proxy pod is present or not
    for each_agent_pod in arc_agents_pod_list.items:

        if(each_agent_pod.metadata.name.startswith("kube-aad-proxy")):
            kap_pod_present = True
            break

    # Checking if any pod security policy is set
    if(cluster_connect_feature is True and kap_pod_present is False):
        print("Error: Unable to create Kube-aad-proxy proxy deployment there is some network policy present in the cluster.\n Refer this link to for more information 'security_policy_link'.\n")
        return False
    return True


def check_kap_cert(corev1_api_instance):

    # Initialize the kap_cert_present as False
    kap_cert_present = False
    kap_pod_status = ""

    # To retrieve all of the arc agent pods that are presesnt in the Cluster
    arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

    # Traversing thorugh all agents and checking if the Kube aad proxy pod is in containercreating state
    for each_agent_pod in arc_agents_pod_list.items:

        if each_agent_pod.metadata.name.startswith("kube-aad-proxy") and each_agent_pod.status.phase == "ContainerCreating":
            kap_pod_status = "ContainerCreating"
            break

    # Going thorugh all the secrets in azure-arc
    all_secrets_azurearc = corev1_api_instance.list_namespaced_secret(namespace="azure-arc")

    for secrets in all_secrets_azurearc.items:

        # If name of secret is kube-aad-proxy-certificate then we stop there
        if(secrets.metadata.name == "kube-aad-proxy-certificate"):
            kap_cert_present = True

    if not kap_cert_present and kap_pod_status == "ContainerCreating":
        print("Error: Unable to pull Kube aad proxy certificate.\n Refer this link to for more information 'kap_cert_link'. \n")
        return False

    return True


def check_msi_expiry(connected_cluster):

    # Fetch the expiry time of the msi certificate
    Expiry_date = str(connected_cluster.managed_identity_certificate_expiration_time)

    # Fetch the current time and format it same as msi certificate
    Current_date_temp = datetime.datetime.now().utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat()
    Current_date = Current_date_temp.replace('T', ' ')

    # Check if expiry date is lesser than current time
    if (Expiry_date < Current_date):
        print("Error: Your MSI certificate has expired. To resolve this issue you can delete the cluster and reconnect it to azure arc.\n For further help visit this link:\n")
        return False

    return True
