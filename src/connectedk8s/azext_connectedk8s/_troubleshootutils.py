# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import Namespace
from pydoc import cli
from kubernetes import client, config, watch, utils
from binascii import a2b_hex
import subprocess
from logging import exception
import os
import json
import datetime
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from base64 import b64encode, b64decode
from unicodedata import name
from azure.core.exceptions import ClientAuthenticationError
import shutil
from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ManualInterrupt, InvalidArgumentValueError, UnclassifiedUserFault, CLIInternalError, FileOperationError, ClientRequestError, DeploymentError, ValidationError, ArgumentUsageError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from azext_connectedk8s._client_factory import _resource_providers_client
from azext_connectedk8s._client_factory import get_graph_client_service_principals
import azext_connectedk8s._constants as consts
import azext_connectedk8s.custom as custom
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterIdentity, ListClusterUserCredentialProperties
from threading import Timer, Thread
from azure.cli.core import get_default_cli
logger = get_logger(__name__)
# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


cli_outputs = []


def create_folder_diagnosticlogs(time_stamp, storage_space_available):

    home_dir = os.path.expanduser( '~' )
    filepath = os.path.join( home_dir, '.azure', 'arc_diagnostic_logs')
    global cli_outputs

    try:
        # Creating Diagnostic folder and its subfolder with the given timestamp and cluster name to store all the logs
        try:
            os.mkdir(filepath)
        except FileExistsError:
            pass

        filepath_with_timestamp = os.path.join(filepath, time_stamp )
        try:
            os.mkdir(filepath_with_timestamp)
        except FileExistsError:
            pass
        
        return filepath_with_timestamp, storage_space_available

    except OSError as e:
        print(type(e))
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An expection has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
            cli_outputs.append("An expection has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")

    except Exception as e:
        logger.warning("An expection has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
        cli_outputs.append("An expection has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")

    return filepath_with_timestamp, storage_space_available


def arc_agents_logger(corev1_api_instance, filepath_with_timestamp, storage_space_available):

    global cli_outputs

    try:
        if storage_space_available :
            # To retrieve all of the arc agents pods that are presesnt in the Cluster
            arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

            # Traversing thorugh all agents
            for each_agent_pod in arc_agents_pod_list.items:

                # Fethcing the current Pod name and creating a folder with that name inside the timestamp folder
                agent_name = each_agent_pod.metadata.name
                arc_agent_logs_path = os.path.join(filepath_with_timestamp, "Arc_Agents_logs")
                try:
                    os.mkdir(arc_agent_logs_path)
                except FileExistsError:
                    pass

                agent_name_logs_path = os.path.join(arc_agent_logs_path, agent_name)
                try:
                    os.mkdir(agent_name_logs_path)
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

                    arc_agent_container_logs = os.path.join(agent_name_logs_path, container_name + ".txt")
                    with open(arc_agent_container_logs, 'w+') as container_file:
                        container_file.write(str(container_log))

    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An expection has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Logger_Fault_Type, summary="Error occured in arc agents logger")
            cli_outputs.append("An expection has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")


    except Exception as e:
        logger.warning("An expection has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Logger_Fault_Type, summary="Error occured in arc agents logger")
        cli_outputs.append("An expection has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def arc_agents_event_logger(filepath_with_timestamp, storage_space_available):

    global cli_outputs

    try:

        if storage_space_available :

            # CMD command to get helm values in azure arc and converting it to json format
            command = ["kubectl", "get", "events", "-n", "azure-arc", "--output", "json"]

            # Using subprocess to execute the helm get values command and fetching the output
            response_kubectl_get_events = Popen(command, stdout=PIPE, stderr=PIPE)
            output_kubectl_get_events, error_kubectl_get_events = response_kubectl_get_events.communicate()

            if response_kubectl_get_events.returncode != 0:
                telemetry.set_exception(exception=error_kubectl_get_events.decode("ascii"), fault_type=consts.Kubectl_Get_Events_Failed,
                                summary='Error while doing kubectl get events')
                logger.warning("Error while doing kubectl get events")

            # Converting output obtained in json format and fetching the clusterconnect-agent feature
            events_json = json.loads(output_kubectl_get_events)

            event_logs_path=os.path.join(filepath_with_timestamp,"Arc_Agents_Events.txt")
            with open(event_logs_path, 'w+') as event_log:

                for events in events_json["items"] :
                        event_log.write(str(events) + "\n")

    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An expection has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")    
            telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Events_Logger_Fault_Type, summary="Error occured in arc agents events logger")
            cli_outputs.append("An expection has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")

    except Exception as e:
        logger.warning("An expection has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")    
        telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Events_Logger_Fault_Type, summary="Error occured in arc agents events logger")
        cli_outputs.append("An expection has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def deployments_logger(appv1_api_instance, filepath_with_timestamp, storage_space_available):

    global cli_outputs

    try:

        if storage_space_available :

            # Creating new Deployment Logs folder in the given timestamp folder
            deployments_path = os.path.join(filepath_with_timestamp, "Deployment_logs")
            try:
                os.mkdir(deployments_path)
            except FileExistsError:
                pass

            # To retrieve all the the deployements that are present in the Cluster
            deployments_list = appv1_api_instance.list_namespaced_deployment("azure-arc")

            # Traversing through all the deployments present
            for deployment in deployments_list.items:

                # Fetching the deployment name
                deployment_name = deployment.metadata.name

                deployment_logs_path = os.path.join(deployments_path, deployment_name + ".txt")
                # Creating a text file with the name of the deployment and adding deployment status in it
                with open(deployment_logs_path, 'w+') as deployment_file:
                    deployment_file.write(str(deployment.status))

    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An expection has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Arc_Deployments_Logger_Fault_Type, summary="Error occured in deployments logger")
            cli_outputs.append("An expection has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")

    except Exception as e:
        logger.warning("An expection has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Arc_Deployments_Logger_Fault_Type, summary="Error occured in deployments logger")
        cli_outputs.append("An expection has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def check_agent_state(corev1_api_instance, filepath_with_timestamp, storage_space_available):

    global cli_outputs

    try:
       
        counter = 0
        agent_state_path=os.path.join(filepath_with_timestamp, "Agent_State.txt")
        with open(agent_state_path, 'w+') as agent_state:
            # To retrieve all of the arc agent pods that are presesnt in the Cluster
            arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

            # Check if any arc agent other than kube aadp proxy is not in Running state
            for each_agent_pod in arc_agents_pod_list.items:

                if storage_space_available :

                    # Storing the state of the arc agent in the user machine
                    agent_state.write(each_agent_pod.metadata.name + " = " + each_agent_pod.status.phase +"\n")

                # If the agent is Kube add proxy we will continue with the next agent
                if(each_agent_pod.metadata.name.startswith("kube-aad-proxy")):
                    continue
                if each_agent_pod.status.phase != 'Running':
                    counter = 1

        # Displaying error if the arc agents are in pending state.
        if counter:
            print("Error: One or more Azure Arc agents are in pending state. It may be caused due to insufficient resource availability on the cluster.\n ")
            cli_outputs.append("Error: One or more Azure Arc agents are in pending state. It may be caused due to insufficient resource availability on the cluster.\n ")
            return "Failed", storage_space_available

        return "Passed", storage_space_available

    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An expection has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Agent_State_Check_Fault_Type, summary="Error ocuured while performing the agent state check")
            cli_outputs.append("An expection has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")

    except Exception as e:
        logger.warning("An expection has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Agent_State_Check_Fault_Type, summary="Error ocuured while performing the agent state check")
        cli_outputs.append("An expection has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete", storage_space_available


def check_agent_version(connected_cluster, azure_arc_agent_version):

    global cli_outputs

    try:

        # If the agent version in the connected cluster resource is none skip the check
        if(connected_cluster.agent_version is None):
            return "Incomplete"

        # To get user agent verison and the latest agent version
        user_agent_version = connected_cluster.agent_version
        current_user_version = user_agent_version.split('.')
        latest_agent_version = azure_arc_agent_version.split('.')

        # Comparing if the user version is comaptible or not
        if((int(current_user_version[0]) < int(latest_agent_version[0])) or (int(latest_agent_version[1]) - int(current_user_version[1]) > 2)):
            logger.warning("We found that you are on an older agent version thats not supported.\n Please visit this link to know the agent version support policy 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/agent-upgrade#version-support-policy'.\n")
            cli_outputs.append("We found that you are on an older agent version thats not supported.\n Please visit this link to know the agent version support policy 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/agent-upgrade#version-support-policy'.\n")
            return "Failed"

        return "Passed"

    except Exception as e:
        logger.warning("An expection has occured while trying to check the azure arc agents version in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Agent_Version_Check_Fault_Type, summary="Error occured while performing the agent version check")
        cli_outputs.append("An expection has occured while trying to check the azure arc agents version in the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete"


def check_diagnoser_container(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp , storage_space_available, namespace, absolute_path):

    global cli_outputs

    try:
        # Setting DNS and Outbound Check as working
        dns_check = "Starting"
        outbound_connectivity_check = "Starting"

        # Executing the Diagnoser job and fetching the logs obtained
        diagnoser_container_log = executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, namespace, absolute_path)

        if(diagnoser_container_log != ""):
            dns_check, storage_space_available = check_cluster_DNS(diagnoser_container_log, filepath_with_timestamp, storage_space_available)
            outbound_connectivity_check, storage_space_available = check_cluster_outbound_connectivity(diagnoser_container_log, filepath_with_timestamp, storage_space_available)
        else:
            return "Incomplete", storage_space_available

        if(dns_check == "Passed" and outbound_connectivity_check == "Passed"):
            return "Passed", storage_space_available
        elif(dns_check == "Incomplete" or outbound_connectivity_check == "Incomplete"):
            return "Incomplete", storage_space_available
        else:
            return "Failed", storage_space_available

    except Exception as e:
        logger.warning("An expection has occured while trying to perform diagnoser continer check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Container_Check_Fault_Type, summary="Error occured while performing the diagnoser container checks")
        cli_outputs.append("An expection has occured while trying to perform diagnoser continer check on the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete", storage_space_available


def executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, namespace, absolute_path):

    global cli_outputs

    # Setting the log output as Empty
    diagnoser_container_log = ""
    yaml_file_path = os.path.join(absolute_path,"troubleshoot_diagnoser_job.yaml")
    cmd_delete_job = ["kubectl", "delete", "-f", ""]
    cmd_delete_job[3]=str(yaml_file_path)

    # To handle the user keyboard Interrupt
    try:

        # Executing the diagnoser_job.yaml
        config.load_kube_config()
        k8s_client = client.ApiClient()

        try:
            utils.create_from_yaml(k8s_client, yaml_file_path)
        except Exception as e:
            print(e)
            pass

        # Watching for diagnoser contianer to reach in completed stage
        w = watch.Watch()
        counter = 0
        for event in w.stream(batchv1_api_instance.list_namespaced_job, namespace=namespace, label_selector="", timeout_seconds=90):
            try:
                if event["object"].metadata.name == "azure-arc-diagnoser-job" and event["object"].status.conditions[0].type == "Complete":
                    counter = 2
                    w.stop()

                elif event["object"].metadata.name == "azure-arc-diagnoser-job" and event["object"].status.conditions[0].type == "Pending":
                    counter = 1

            except Exception as e:
                continue
            else:
                continue

        # If container not created then clearing all the resource with proper error message
        if (counter == 0):
            logger.warning("Unable to create the diagnoser job in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            subprocess.run(cmd_delete_job, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cli_outputs.append("Unable to create the diagnoser job in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            return ""
        
        # If container stuck in pending state then clearing all the resources with proper error message
        elif (counter == 1):
            logger.warning("The diagnoser job is stuck in the 'Pending' state in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            subprocess.run(cmd_delete_job, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cli_outputs.append("The diagnoser job is stuck in the 'Pending' state in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            return ""

        else:

            # Fetching the Diagnoser Container logs
            try:

                job_name = "azure-arc-diagnoser-job"

                all_pods = corev1_api_instance.list_namespaced_pod(namespace)
                # Traversing thorugh all agents
                for each_pod in all_pods.items:

                    # Fethcing the current Pod name and creating a folder with that name inside the timestamp folder
                    pod_name = each_pod.metadata.name

                    if(pod_name.startswith(job_name)):

                        # Creating a text file with the name of the container and adding that containers logs in it
                        diagnoser_container_log = corev1_api_instance.read_namespaced_pod_log(name=pod_name, container="azure-arc-diagnoser-container", namespace=namespace)

                # Clearing all the resources after fetching the diagnoser container logs
                subprocess.run(cmd_delete_job, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            except Exception as e:
                subprocess.run(cmd_delete_job, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return ""

    except KeyboardInterrupt:
        # If process terminated by user then delete the resources if any added to the cluster.
        subprocess.run(cmd_delete_job, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except Exception as e:
        logger.warning("An expection has occured while trying to execute the diagnoser job in the cluster. Exception: {}".format(str(e)) + "\n")
        subprocess.run(cmd_delete_job, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        telemetry.set_exception(exception=e, fault_type=consts.Executing_Diagnoser_Job_Fault_Type, summary="Error while executing Diagnoser Job")
        cli_outputs.append("An expection has occured while trying to execute the diagnoser job in the cluster. Exception: {}".format(str(e)) + "\n")

    return diagnoser_container_log


def check_cluster_DNS(diagnoser_container_log, filepath_with_timestamp, storage_space_available):

    global cli_outputs

    try:
        # To retreive only the DNS lookup result from the diagnoser container logs
        dns_check = diagnoser_container_log[0:len(diagnoser_container_log) - 5:]

        # Validating if DNS is working or not and displaying proper result
        if("NXDOMAIN" in dns_check or "connection timed out" in dns_check):
            print("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
            cli_outputs.append("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
            if storage_space_available :
                dns_check_path = os.path.join(filepath_with_timestamp, "DNS_Check.txt")
                with open(dns_check_path, 'w+') as dns:
                    dns.write(dns_check + "\nWe found an issue with the DNS resolution on your cluster.")
            return "Failed", storage_space_available

        else:
            if storage_space_available :
                dns_check_path = os.path.join(filepath_with_timestamp, "DNS_Check.txt")
                with open(dns_check_path, 'w+') as dns:
                    dns.write(dns_check + "\nCluster DNS check passed successfully.")
            return "Passed", storage_space_available

    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An expection has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Cluster_DNS_Check_Fault_Type, summary="Error occured while performing cluster DNS check")
            cli_outputs.append("An expection has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")

    except Exception as e:
        logger.warning("An expection has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_DNS_Check_Fault_Type, summary="Error occured while performing cluster DNS check")
        cli_outputs.append("An expection has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete", storage_space_available


def check_cluster_outbound_connectivity(diagnoser_container_log, filepath_with_timestamp, storage_space_available):

    global cli_outputs

    try:

        # To retreive only the outbound connectivity result from the diagnoser container logs
        outbound_check = diagnoser_container_log[-4:-1:]

        # Validating if outbound connectiivty is working or not and displaying proper result
        if(outbound_check != "000"):
            if storage_space_available :
                outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, "Outbound_Network_Connectivity_Check.txt")
                with open(outbound_connectivity_check_path, 'w+') as outbound:
                    outbound.write("Response code " + outbound_check + "\nOutbound network connectivity check passed successfully.")
            return "Passed", storage_space_available
        else:
            print("Error: We found an issue with outbound network connectivity from the cluster.\nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy paramaters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server'.\nPlease ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements' \n")
            cli_outputs.append("Error: We found an issue with outbound network connectivity from the cluster.\nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy paramaters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server'.\nPlease ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements' \n")
            if storage_space_available :
                outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, "Outbound_Network_Connectivity_Check.txt")
                with open(outbound_connectivity_check_path, 'w+') as outbound:
                    outbound.write("Response code " + outbound_check + "\nWe found an issue with Outbound network connectivity from the cluster.")
            return "Failed", storage_space_available

    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An expection has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Outbound_Connectivity_Check_Fault_Type, summary="Error occured while performing outbound connectivity check in the cluster")
            cli_outputs.append("An expection has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")

    except Exception as e:
        logger.warning("An expection has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Outbound_Connectivity_Check_Fault_Type, summary="Error occured while performing outbound connectivity check in the cluster")
        cli_outputs.append("An expection has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")
    
    return "Incomplete", storage_space_available


def check_msi_certificate(corev1_api_instance):

    global cli_outputs

    try:
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
            print("Error: Unable to pull MSI certificate. Please ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements'. \n")
            cli_outputs.append("Error: Unable to pull MSI certificate. Please ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements'. \n")
            return "Failed"

        return "Passed"

    except Exception as e:
        logger.warning("An expection has occured while performing the msi certificate check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.MSI_Cert_Check_Fault_Type, summary="Error occured while trying to pull MSI certificate")
        cli_outputs.append("An expection has occured while performing the msi certificate check on the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete"


def check_cluster_security_policy(corev1_api_instance, helm_client_location):

    global cli_outputs

    try:
        # Intializing the kap_pod_present and cluster_connect_feature variable as False
        kap_pod_present = False
        cluster_connect_feature = False

        # CMD command to get helm values in azure arc and converting it to json format
        command = [helm_client_location, "get", "values", "azure-arc", "-o", "json"]

        # Using subprocess to execute the helm get values command and fetching the output
        response_helm_values_get = Popen(command,  stdout=PIPE, stderr=PIPE)
        output_helm_values_get , error_helm_get_values = response_helm_values_get.communicate()

        if response_helm_values_get.returncode != 0:
            if ('forbidden' in error_helm_get_values.decode("ascii") or 'timed out waiting for the condition' in error_helm_get_values.decode("ascii")):
                telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Get_Helm_Values_Failed,
                                        summary='Error while doing helm get values azure-arc')

        # Converting output obtained in json format and fetching the clusterconnect-agent feature
        helm_values_json = json.loads(output_helm_values_get)
        cluster_connect_feature = helm_values_json["systemDefaultValues"]["clusterconnect-agent"]["enabled"]

        # To retrieve all of the arc agent pods that are presesnt in the Cluster
        arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

        # Traversing thorugh all agents and checking if the Kube aad proxy pod is present or not
        for each_agent_pod in arc_agents_pod_list.items:

            if(each_agent_pod.metadata.name.startswith("kube-aad-proxy")):
                kap_pod_present = True
                break

        # Checking if any pod security policy is set
        if(cluster_connect_feature is True and kap_pod_present is False):
            print("Error: Unable to create Kube-aad-proxy deployment there might be a security policy present which is preventing the deployment of kube-aad-proxy as it doesn't have admin privileges.\n ")
            cli_outputs.append("Error: Unable to create Kube-aad-proxy deployment there might be a security policy present which is preventing the deployment of kube-aad-proxy as it doesn't have admin privileges.\n ")
            return "Failed"
        return "Passed"

    except Exception as e:
        logger.warning("An expection has occured while trying to performing KAP cluster security policy check in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_Security_Policy_Check_Fault_Type, summary="Error occured while performing cluster security policy check")
        cli_outputs.append("An expection has occured while trying to performing KAP cluster security policy check in the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete"


def check_kap_cert(corev1_api_instance):

    global cli_outputs

    try:
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
            print("Error: Unable to pull Kube aad proxy certificate.\n")
            cli_outputs.append("Error: Unable to pull Kube aad proxy certificate.\n")
            return "Failed"

        return "Passed"

    except Exception as e:
        logger.warning("An expection has occured while performing kube aad proxy certificate check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.KAP_Cert_Check_Fault_Type, summary="Error occured while trying to pull kap cert certificate")
        cli_outputs.append("An expection has occured while performing kube aad proxy certificate check on the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete"


def check_msi_expiry(connected_cluster):

    global cli_outputs

    try:
        # Fetch the expiry time of the msi certificate
        Expiry_date = str(connected_cluster.managed_identity_certificate_expiration_time)

        # Fetch the current time and format it same as msi certificate
        Current_date_temp = datetime.datetime.now().utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat()
        Current_date = Current_date_temp.replace('T', ' ')

        # Check if expiry date is lesser than current time
        if (Expiry_date < Current_date):
            print("Error: Your MSI certificate has expired. To resolve this issue you can delete the cluster and reconnect it to azure arc.\n")
            cli_outputs.append("Error: Your MSI certificate has expired. To resolve this issue you can delete the cluster and reconnect it to azure arc.\n")
            return "Failed"

        return "Passed"

    except Exception as e:
        logger.warning("An expection has occured while performing msi expiry check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.MSI_Cert_Expiry_Check_Fault_Type, summary="Error occured while trying to perform the MSI cert expiry check")
        cli_outputs.append("An expection has occured while performing msi expiry check on the cluster. Exception: {}".format(str(e)) + "\n")

    return "Incomplete"


def cli_output_logger(filepath_with_timestamp, storage_space_available):

    global cli_outputs

    try:

        if storage_space_available:

            cli_output_logger_path = os.path.join(filepath_with_timestamp, "Diagnoser_Results.txt")

            if len(cli_outputs)>0:
                with open(cli_output_logger_path, 'w+') as cli_output_writer:
                    for output in cli_outputs:
                        cli_output_writer.write(output+"\n")
            else:
                with open(cli_output_logger_path, 'w+') as cli_output_writer:
                        cli_output_writer.write("Diagnoser could not find any issues with the cluster.\n")

    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)

    except Exception as e:
        print(e)

