# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import Namespace
from pydoc import cli
from kubernetes import client, config, watch, utils
from logging import exception
import os
import yaml
import json
import datetime
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
import shutil
from knack.log import get_logger
from azure.cli.core import telemetry
import azext_connectedk8s._constants as consts
import azext_connectedk8s._utils as azext_utils
logger = get_logger(__name__)
# pylint: disable=unused-argument, too-many-locals, too-many-branches, too-many-statements, line-too-long

diagnoser_output = []


def fetch_kubectl_cluster_info(filepath_with_timestamp, storage_space_available, kubectl_client_location, kube_config, kube_context):

    global diagnoser_output
    try:
        # If storage space available then only store the azure-arc events
        if storage_space_available:
            # CMD command to get events using kubectl and converting it to json format
            kubect_cluster_info_command = [kubectl_client_location, "cluster-info"]
            if kube_config:
                kubect_cluster_info_command.extend(["--kubeconfig", kube_config])
            if kube_context:
                kubect_cluster_info_command.extend(["--context", kube_context])
            # Using Popen to execute the command and fetching the output
            response_cluster_info = Popen(kubect_cluster_info_command, stdout=PIPE, stderr=PIPE)
            output_cluster_info, error_cluster_info = response_cluster_info.communicate()
            if response_cluster_info.returncode != 0:
                telemetry.set_exception(exception=error_cluster_info.decode("ascii"), fault_type=consts.Kubectl_Cluster_Info_Failed_Fault_Type, summary="Error while doing kubectl cluster-info")
                logger.warning("Error while doing 'kubectl cluster-info'. We were not able to capture cluster-info logs in arc_diganostic_logs folder. Exception: ", error_cluster_info.decode("ascii"))
                diagnoser_output.append("Error while doing 'kubectl cluster-info'. We were not able to capture cluster-info logs in arc_diganostic_logs folder. Exception: ", error_cluster_info.decode("ascii"))
                return consts.Diagnostic_Check_Failed, storage_space_available
            output_cluster_info_decoded = output_cluster_info.decode()
            # Converting the output to list and remove the extra message(To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.) that gets printed
            list_output_cluster_info = output_cluster_info_decoded.split("\n")
            list_output_cluster_info.pop(-1)
            list_output_cluster_info.pop(-1)
            # Merging the list into string
            formatted_cluster_info = "\n".join(map(str, list_output_cluster_info))
            # Path to add the K8s cluster-info
            cluster_info_path = os.path.join(filepath_with_timestamp, consts.K8s_Cluster_Info)
            with open(cluster_info_path, 'w+') as cluster_info:
                cluster_info.write(str(formatted_cluster_info) + "\n")
            return consts.Diagnostic_Check_Passed, storage_space_available
        else:
            return consts.Diagnostic_Check_Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to store the cluster info in the arc_diagnostic_logs folder. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_Kubectl_Cluster_Info_Fault_Type, summary="Error occured while fetching cluster-info")
            diagnoser_output.append("An exception has occured while trying to store the cluster info in the arc_diagnostic_logs folder. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to store the cluster info in the arc_diagnostic_logs folder. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_Kubectl_Cluster_Info_Fault_Type, summary="Error occured while fetching cluster-info")
        diagnoser_output.append("An exception has occured while trying to store the cluster info in the arc_diagnostic_logs folder. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Failed, storage_space_available


def fetch_connected_cluster_resource(filepath_with_timestamp, connected_cluster, storage_space_available):

    global diagnoser_output
    try:
        # Path to add the connected_cluster resource
        connected_cluster_resource_file_path = os.path.join(filepath_with_timestamp, consts.Connected_Cluster_Resource)
        # Formatting the last_connectivity_time and managed_identity_certificate_expiration_time into proper data-time format
        last_connectivity_time_str = str(connected_cluster.last_connectivity_time)
        connected_cluster.last_connectivity_time = last_connectivity_time_str
        managed_identity_certificate_expiration_time_str = str(connected_cluster.managed_identity_certificate_expiration_time)
        connected_cluster.managed_identity_certificate_expiration_time = managed_identity_certificate_expiration_time_str

        # Formatting system_data
        created_at = str(connected_cluster.system_data.created_at)
        connected_cluster.system_data.created_at = created_at
        last_modified_at = str(connected_cluster.system_data.last_modified_at)
        connected_cluster.system_data.last_modified_at = last_modified_at
        system_data = str(connected_cluster.system_data)
        connected_cluster.system_data = system_data
        # Formatting identity
        identity = str(connected_cluster.identity)
        connected_cluster.identity = identity

        if storage_space_available:
            # If storage space is available then only store the connected cluster resource
            with open(connected_cluster_resource_file_path, 'w+') as cc:
                cc.write(str(connected_cluster))
        return consts.Diagnostic_Check_Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to store the get output of connected cluster resource in diagnostic logs folder. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Connected_Cluster_Resource_Fetch_Fault_Type, summary="Error occured while fetching the Get output of connected cluster")
            diagnoser_output.append("An exception has occured while trying to store the get output of connected cluster resource in diagnostic logs folder. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to store the get output of connected cluster resource in diagnostic logs folder. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Connected_Cluster_Resource_Fetch_Fault_Type, summary="Error occured while fetching the Get output of connected cluster")
        diagnoser_output.append("An exception has occured while trying to store the get output of connected cluster resource in diagnostic logs folder. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Failed, storage_space_available


def retrieve_arc_agents_logs(corev1_api_instance, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    try:
        if storage_space_available:
            # To retrieve all of the arc agents pods that are present in the Cluster
            arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")
            # Traversing through all agents
            for each_agent_pod in arc_agents_pod_list.items:
                # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
                agent_name = each_agent_pod.metadata.name
                arc_agent_logs_path = os.path.join(filepath_with_timestamp, consts.Arc_Agents_Logs)
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
                if (each_agent_pod.status.phase != "Running"):
                    continue
                # Traversing through all of the containers present inside each pods
                for each_container in each_agent_pod.spec.containers:
                    # Fetching the Container name
                    container_name = each_container.name
                    # Creating a text file with the name of the container and adding that containers logs in it
                    container_log = corev1_api_instance.read_namespaced_pod_log(name=agent_name, container=container_name, namespace="azure-arc")
                    # Path to add the arc agents container logs.
                    arc_agent_container_logs_path = os.path.join(agent_name_logs_path, container_name + ".txt")
                    with open(arc_agent_container_logs_path, 'w+') as container_file:
                        container_file.write(str(container_log))

        return consts.Diagnostic_Check_Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_Arc_Agent_Logs_Failed_Fault_Type, summary="Error occured in arc agents logger")
            diagnoser_output.append("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_Arc_Agent_Logs_Failed_Fault_Type, summary="Error occured in arc agents logger")
        diagnoser_output.append("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Failed, storage_space_available


def retrieve_arc_agents_event_logs(filepath_with_timestamp, storage_space_available, kubectl_client_location, kube_config, kube_context):

    global diagnoser_output
    try:
        # If storage space available then only store the azure-arc events
        if storage_space_available:
            # CMD command to get events using kubectl and converting it to json format
            command = [kubectl_client_location, "get", "events", "-n", "azure-arc", "--output", "json"]
            if kube_config:
                command.extend(["--kubeconfig", kube_config])
            if kube_context:
                command.extend(["--context", kube_context])
            # Using Popen to execute the command and fetching the output
            response_kubectl_get_events = Popen(command, stdout=PIPE, stderr=PIPE)
            output_kubectl_get_events, error_kubectl_get_events = response_kubectl_get_events.communicate()
            if response_kubectl_get_events.returncode != 0:
                telemetry.set_exception(exception=error_kubectl_get_events.decode("ascii"), fault_type=consts.Kubectl_Get_Events_Failed_Fault_Type, summary='Error while doing kubectl get events')
                logger.warning("Error while doing kubectl get events. We were not able to capture events log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_events.decode("ascii"))
                diagnoser_output.append("Error while doing kubectl get events. We were not able to capture events log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_events.decode("ascii"))
                return consts.Diagnostic_Check_Failed, storage_space_available

            # Converting output obtained in json format and fetching the azure-arc events
            events_json = json.loads(output_kubectl_get_events)
            # Path to add the azure-arc events
            event_logs_path = os.path.join(filepath_with_timestamp, consts.Arc_Agents_Events)
            if len(events_json["items"]) != 0:
                with open(event_logs_path, 'w+') as event_log:
                    # Adding all the individual events
                    for events in events_json["items"]:
                        event_log.write(str(events) + "\n")
            return consts.Diagnostic_Check_Passed, storage_space_available
        else:
            return consts.Diagnostic_Check_Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_Arc_Agents_Events_Logs_Failed_Fault_Type, summary="Error occured in arc agents events logger")
            diagnoser_output.append("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_Arc_Agents_Events_Logs_Failed_Fault_Type, summary="Error occured in arc agents events logger")
        diagnoser_output.append("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Failed, storage_space_available


def retrieve_deployments_logs(appv1_api_instance, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    try:
        if storage_space_available:
            # Creating new Deployment Logs folder in the given timestamp folder
            deployments_path = os.path.join(filepath_with_timestamp, consts.Arc_Deployment_Logs)
            try:
                os.mkdir(deployments_path)
            except FileExistsError:
                pass
            # To retrieve all the deployment that are present in the Cluster
            deployments_list = appv1_api_instance.list_namespaced_deployment("azure-arc")
            # Traversing through all the deployments present
            for deployment in deployments_list.items:
                # Fetching the deployment name
                deployment_name = deployment.metadata.name
                arc_deployment_logs_path = os.path.join(deployments_path, deployment_name + ".txt")
                # Creating a text file with the name of the deployment and adding deployment status in it
                with open(arc_deployment_logs_path, 'w+') as deployment_file:
                    deployment_file.write(str(deployment.status))

        return consts.Diagnostic_Check_Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_Arc_Deployment_Logs_Failed_Fault_Type, summary="Error occured in deployments logger")
            diagnoser_output.append("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_Arc_Deployment_Logs_Failed_Fault_Type, summary="Error occured in deployments logger")
        diagnoser_output.append("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Failed, storage_space_available


def check_agent_state(corev1_api_instance, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    # If all agents are stuck we will skip the certificates check
    all_agents_stuck = True
    # To check if agents are stuck because of insufficient resource
    probable_sufficient_resource_for_agents = True

    try:
        # To check if all the containers are working for the Running agents
        all_agent_containers_ready = True
        agent_state_path = os.path.join(filepath_with_timestamp, consts.Agent_State)
        # If storage space available then only we will be writing into the file
        if storage_space_available:
            with open(agent_state_path, 'w+') as agent_state:
                # To retrieve all of the arc agent pods that are present in the Cluster
                arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")
                # Check if any arc agent is not in Running state
                for each_agent_pod in arc_agents_pod_list.items:
                    if storage_space_available:
                        # Storing the state of the arc agent in the user machine
                        agent_state.write(each_agent_pod.metadata.name + " : Phase = " + each_agent_pod.status.phase + "\n")
                    if each_agent_pod.status.phase == 'Running':
                        all_agents_stuck = False
                    if each_agent_pod.status.container_statuses is None:
                        probable_sufficient_resource_for_agents = False
                        if storage_space_available:
                            # Adding empty line after each agents for formatting
                            agent_state.write("\n")
                        storage_space_available = describe_non_ready_agent_log(filepath_with_timestamp, corev1_api_instance, each_agent_pod.metadata.name, storage_space_available)
                    else:
                        all_containers_ready_for_each_agent = True
                        # If the agent is in running state we will check if all containers are running or not
                        for each_container_status in each_agent_pod.status.container_statuses:
                            # Checking if all containers are running or not
                            if each_container_status.ready is False:
                                all_containers_ready_for_each_agent = False
                                all_agent_containers_ready = False
                                try:
                                    # Adding the reason for container to be not in ready state
                                    container_not_ready_reason = each_container_status.state.waiting.reason
                                except Exception:
                                    container_not_ready_reason = None
                                # Adding the reason if continer is not in ready state
                                if container_not_ready_reason is not None:
                                    if storage_space_available:
                                        agent_state.write("\t" + each_container_status.name + " :" + " Ready = False {Reason : " + str(container_not_ready_reason) + "} , Restart_Counts = " + str(each_container_status.restart_count) + "\n")
                                else:
                                    if storage_space_available:
                                        agent_state.write("\t" + each_container_status.name + " :" + " Ready = " + str(each_container_status.ready) + ", Restart_Counts = " + str(each_container_status.restart_count) + "\n")
                            else:
                                if storage_space_available:
                                    agent_state.write("\t" + each_container_status.name + " :" + " Ready = " + str(each_container_status.ready) + ", Restart_Counts = " + str(each_container_status.restart_count) + "\n")
                            if all_containers_ready_for_each_agent is False:
                                storage_space_available = describe_non_ready_agent_log(filepath_with_timestamp, corev1_api_instance, each_agent_pod.metadata.name, storage_space_available)

                        if storage_space_available:
                            # Adding empty line after each agents for formatting
                            agent_state.write("\n")
        # If storage space not available then we will be just checking if all agents are running properly or not
        else:
            # To retrieve all of the arc agent pods that are present in the Cluster
            arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")
            # Check if any arc agent is not in Running state
            for each_agent_pod in arc_agents_pod_list.items:
                if each_agent_pod.status.phase == 'Running':
                    all_agents_stuck = False
                # If container statuses is not present then thats very high chance of less resource availability
                if each_agent_pod.status.container_statuses is None:
                    probable_sufficient_resource_for_agents = False
                    storage_space_available = describe_non_ready_agent_log(filepath_with_timestamp, corev1_api_instance, each_agent_pod.metadata.name, storage_space_available)
                else:
                    all_containers_ready_for_each_agent = True
                    # If the agent is in running state we will check if all containers are running or not
                    for each_container_status in each_agent_pod.status.container_statuses:
                        # Checking if all containers are running or not
                        if each_container_status.ready is False:
                            all_containers_ready_for_each_agent = False
                            all_agent_containers_ready = False
                            try:
                                # Adding the reason for container to be not in ready state
                                container_not_ready_reason = each_container_status.state.waiting.reason
                            except Exception:
                                container_not_ready_reason = None
                            # Adding the reason if continer is not in ready state
                        if all_containers_ready_for_each_agent is False:
                            storage_space_available = describe_non_ready_agent_log(filepath_with_timestamp, corev1_api_instance, each_agent_pod.metadata.name, storage_space_available)

        # Displaying error if the arc agents are in pending state.
        if probable_sufficient_resource_for_agents is False:
            logger.warning("Error: One or more Azure Arc agents are not in running state. It may be caused due to insufficient resource availability on the cluster.\n")
            diagnoser_output.append("Error: One or more Azure Arc agents are not in running state. It may be caused due to insufficient resource availability on the cluster.\n")
            return consts.Diagnostic_Check_Failed, storage_space_available, all_agents_stuck, probable_sufficient_resource_for_agents

        elif all_agent_containers_ready is False:
            logger.warning("Error: One or more agents in the Azure Arc are not fully running.\n")
            diagnoser_output.append("Error: One or more agents in the Azure Arc are not fully runnning.\n")
            return consts.Diagnostic_Check_Failed, storage_space_available, all_agents_stuck, probable_sufficient_resource_for_agents

        return consts.Diagnostic_Check_Passed, storage_space_available, all_agents_stuck, probable_sufficient_resource_for_agents

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Agent_State_Check_Fault_Type, summary="Error ocuured while performing the agent state check")
            diagnoser_output.append("An exception has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Agent_State_Check_Fault_Type, summary="Error ocuured while performing the agent state check")
        diagnoser_output.append("An exception has occured while trying to check the azure arc agents state in the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Incomplete, storage_space_available, all_agents_stuck, probable_sufficient_resource_for_agents


def check_agent_version(connected_cluster, azure_arc_agent_version):

    global diagnoser_output
    try:

        # If the agent version in the connected cluster resource is none skip the check
        if (connected_cluster.agent_version is None):
            return consts.Diagnostic_Check_Incomplete

        # To get user agent version and the latest agent version
        user_agent_version = connected_cluster.agent_version
        current_user_version = user_agent_version.split('.')
        latest_agent_version = azure_arc_agent_version.split('.')
        # Comparing if the user version is compatible or not
        if ((int(current_user_version[0]) < int(latest_agent_version[0])) or (int(latest_agent_version[1]) - int(current_user_version[1]) > 2)):
            logger.warning("We found that you are on an older agent version that is not supported.\n Please visit this link to know the agent version support policy 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/agent-upgrade#version-support-policy'.\n")
            diagnoser_output.append("We found that you are on an older agent version that is not supported.\n Please visit this link to know the agent version support policy 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/agent-upgrade#version-support-policy'.\n")
            return consts.Diagnostic_Check_Failed

        return consts.Diagnostic_Check_Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to check the azure arc agents version in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Agent_Version_Check_Fault_Type, summary="Error occured while performing the agent version check")
        diagnoser_output.append("An exception has occured while trying to check the azure arc agents version in the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Incomplete


def check_diagnoser_container(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp, storage_space_available, absolute_path, probable_sufficient_resource_for_agents, helm_client_location, kubectl_client_location, release_namespace, probable_pod_security_policy_presence, kube_config, kube_context):

    global diagnoser_output
    try:

        if probable_sufficient_resource_for_agents is False:
            logger.warning("Unable to execute the diagnoser job in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            diagnoser_output.append("Unable to execute the diagnoser job in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        # Setting DNS and Outbound Check as working
        dns_check = "Starting"
        outbound_connectivity_check = "Starting"
        # Executing the Diagnoser job and fetching diagnoser logs obtained
        diagnoser_container_log = executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp, storage_space_available, absolute_path, helm_client_location, kubectl_client_location, release_namespace, probable_pod_security_policy_presence, kube_config, kube_context)
        # If diagnoser_container_log is not empty then only we will check for the results
        if (diagnoser_container_log is not None and diagnoser_container_log != ""):
            diagnoser_container_log_list = diagnoser_container_log.split("\n")
            diagnoser_container_log_list.pop(-1)
            dns_check_log = ""
            counter_container_logs = 1
            # For retrieving only diagnoser logs from the diagnoser output
            for outputs in diagnoser_container_log_list:
                if consts.Outbound_Connectivity_Check_Result_String in outputs:
                    counter_container_logs = 1
                elif consts.DNS_Check_Result_String in outputs:
                    dns_check_log += outputs
                    counter_container_logs = 0
                elif counter_container_logs == 0:
                    dns_check_log += "  " + outputs
            dns_check, storage_space_available = azext_utils.check_cluster_DNS(dns_check_log, filepath_with_timestamp, storage_space_available, diagnoser_output)
            outbound_connectivity_check, storage_space_available = azext_utils.check_cluster_outbound_connectivity(diagnoser_container_log_list[-1], filepath_with_timestamp, storage_space_available, diagnoser_output, "troubleshoot")
        else:
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        # If both the check passed then we will return Diagnoser checks Passed
        if (dns_check == consts.Diagnostic_Check_Passed and outbound_connectivity_check == consts.Diagnostic_Check_Passed):
            return consts.Diagnostic_Check_Passed, storage_space_available
        # If any of the check remain Incomplete than we will return Incomplete
        elif (dns_check == consts.Diagnostic_Check_Incomplete or outbound_connectivity_check == consts.Diagnostic_Check_Incomplete):
            return consts.Diagnostic_Check_Incomplete, storage_space_available
        else:
            return consts.Diagnostic_Check_Failed, storage_space_available

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to perform diagnoser container check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Container_Check_Failed_Fault_Type, summary="Error occured while performing the diagnoser container checks")
        diagnoser_output.append("An exception has occured while trying to perform diagnoser container check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Incomplete, storage_space_available


def executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp, storage_space_available, absolute_path, helm_client_location, kubectl_client_location, release_namespace, probable_pod_security_policy_presence, kube_config, kube_context):

    global diagnoser_output
    job_name = "azure-arc-diagnoser-job"
    # CMD command to get helm values in azure arc and converting it to json format
    command = [helm_client_location, "get", "values", "azure-arc", "--namespace", release_namespace, "-o", "json"]
    if kube_config:
        command.extend(["--kubeconfig", kube_config])
    if kube_context:
        command.extend(["--kube-context", kube_context])
    # Using Popen to execute the helm get values command and fetching the output
    response_helm_values_get = Popen(command, stdout=PIPE, stderr=PIPE)
    output_helm_values_get, error_helm_get_values = response_helm_values_get.communicate()
    if response_helm_values_get.returncode != 0:
        if ('forbidden' in error_helm_get_values.decode("ascii") or 'timed out waiting for the condition' in error_helm_get_values.decode("ascii")):
            telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Get_Helm_Values_Failed,
                                    summary='Error while doing helm get values azure-arc')
    helm_values_json = json.loads(output_helm_values_get)
    # Retrieving the proxy values if they are present
    try:
        is_proxy_enabled = helm_values_json["global"]["isProxyEnabled"]
    except Exception as e:
        # This exception will come when isProxyEnabled parameter is not present so we are setting it as false
        if 'isProxyEnabled' in str(e):
            is_proxy_enabled = False
        else:
            logger.warning("An exception has occured while trying to fetch Field:'isProxyEnabled' from get helm values. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Values_Fetch_isProxyEnabled_Failed_Fault_Type, summary="Error while parsing the 'isProxyEnabled' while using helm get values")
            diagnoser_output.append("An exception has occured while trying to fetch Field:'isProxyEnabled' from get helm values. Exception: {}".format(str(e)) + "\n")
            return
    try:
        is_custom_cert = helm_values_json["global"]["isCustomCert"]
    except Exception as e:
        # This exception will come when isCustomCert parameter is not present so we are setting it as false
        if 'isCustomCert' in str(e):
            is_custom_cert = False
        else:
            logger.warning("An exception has occured while trying to fetch Field:'isCustomCert' from get helm values. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Values_Fetch_isCustomCert_Failed_Fault_Type, summary="Error while parsing the 'isCustomCert' while using helm get values")
            diagnoser_output.append("An exception has occured while trying to fetch Field:'isCustomCert' from get helm values. Exception: {}".format(str(e)) + "\n")
            return
    try:
        proxy_cert = helm_values_json["global"]["proxyCert"]
    except Exception as e:
        # This exception will come when proxyCert parameter is not present so we are setting it as false
        if 'proxyCert' in str(e):
            proxy_cert = False
        else:
            logger.warning("An exception has occured while trying to fetch Field:'proxyCert' from get helm values. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Values_Fetch_proxyCert_Failed_Fault_Type, summary="Error while parsing the 'proxyCert' while using helm get values")
            diagnoser_output.append("An exception has occured while trying to fetch Field:'proxyCert' from get helm values. Exception: {}".format(str(e)) + "\n")
            return

    # Depending on the presence of proxy cert using the yaml
    if proxy_cert and (is_custom_cert or is_proxy_enabled):
        yaml_file_path = os.path.join(absolute_path, "troubleshoot_diagnoser_job_with_proxycert_mount.yaml")
    else:
        yaml_file_path = os.path.join(absolute_path, "troubleshoot_diagnoser_job_without_proxycert.yaml")
    # Setting the log output as Empty
    diagnoser_container_log = ""
    cmd_delete_job = [kubectl_client_location, "delete", "-f", ""]
    if kube_config:
        cmd_delete_job.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_delete_job.extend(["--context", kube_context])
    cmd_delete_job[3] = str(yaml_file_path)
    # Editing the yaml file based on the release namespace
    new_yaml = []
    with open(yaml_file_path) as f:
        list_doc = yaml.safe_load_all(f)
        # We are creating 4 resources from a single yaml and troubleshoot_yaml_part points to the part of yaml we are referring to in 0 based index.
        troubleshoot_yaml_part = 0
        # Using release_namespace wherever required
        for each_yaml in list_doc:
            # Changing the role, rolebinding and the job args namespace field to the release-namespace
            # Secret-reader role is used to fetch the secrets present in the release-namespace
            # Also we pass release-namespace in args to read secrets for helm command that we are using in the script.
            if (troubleshoot_yaml_part == 1 or troubleshoot_yaml_part == 2):
                each_yaml['metadata']['namespace'] = release_namespace
            elif (troubleshoot_yaml_part == 3):
                each_yaml['spec']['template']['spec']['containers'][0]['args'][0] = release_namespace
            troubleshoot_yaml_part += 1
            new_yaml.append(each_yaml)
    # Updating the yaml file
    with open(yaml_file_path, 'w+') as f:
        for add_updated_yaml_part in new_yaml:
            f.write("---\n")
            yaml.dump(add_updated_yaml_part, f)

    # To handle the user keyboard Interrupt
    try:
        # Executing the diagnoser_job.yaml
        config.load_kube_config(kube_config, kube_context)
        k8s_client = client.ApiClient()
        # Attempting deletion of diagnoser resources to handle the scenario if any stale resources are present
        response_kubectl_delete_job = Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
        output_kubectl_delete_job, error_kubectl_delete_job = response_kubectl_delete_job.communicate()
        # If any error occured while execution of delete command
        if (response_kubectl_delete_job != 0):
            # Converting the string of multiple errors to list
            error_msg_list = error_kubectl_delete_job.decode("ascii").split("\n")
            error_msg_list.pop(-1)
            valid_exception_list = []
            # Checking if any exception occured or not
            exception_occured_counter = 0
            for ind_errors in error_msg_list:
                if ('Error from server (NotFound)' in ind_errors or 'deleted' in ind_errors):
                    pass
                else:
                    valid_exception_list.append(ind_errors)
                    exception_occured_counter = 1
            # If any exception occured we will print the exception and return
            if exception_occured_counter == 1:
                logger.warning("An error occured while deploying the diagnoser job in the cluster. Exception:")
                telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Diagnoser_Job_Failed_Fault_Type, summary="Error while executing Diagnoser Job")
                diagnoser_output.append("An error occured while deploying the diagnoser job in the cluster. Exception:")
                for ind_error in valid_exception_list:
                    logger.warning(ind_error)
                    diagnoser_output.append(ind_error)
                return
        # Creating the job from yaml file
        try:
            utils.create_from_yaml(k8s_client, yaml_file_path)
        # To handle the Exception that occured
        except Exception as e:
            logger.warning("An error occured while deploying the diagnoser job in the cluster. Exception:")
            logger.warning(str(e))
            diagnoser_output.append("An error occured while deploying the diagnoser job in the cluster. Exception:")
            diagnoser_output.append(str(e))
            telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Diagnoser_Job_Failed_Fault_Type, summary="Error while executing Diagnoser Job")
            # Deleting all the stale resources that got created
            Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
            return
        # Watching for diagnoser container to reach in completed stage
        w = watch.Watch()
        is_job_complete = False
        is_job_scheduled = False
        # To watch for changes in the pods states till it reach completed state or exit if it takes more than 60 seconds
        for event in w.stream(batchv1_api_instance.list_namespaced_job, namespace='azure-arc', label_selector="", timeout_seconds=180):
            try:
                # Checking if job get scheduled or not
                if event["object"].metadata.name == "azure-arc-diagnoser-job":
                    is_job_scheduled = True
                # Checking if job reached completed stage or not
                if event["object"].metadata.name == "azure-arc-diagnoser-job" and event["object"].status.conditions[0].type == "Complete":
                    is_job_complete = True
                    w.stop()
            except Exception:
                continue
            else:
                continue

        # Selecting the error message depending on the job getting scheduled, completed and the presence of  security policy
        if (is_job_scheduled is False and probable_pod_security_policy_presence == consts.Diagnostic_Check_Failed):
            logger.warning("Unable to schedule the diagnoser job in the kubernetes cluster. There might be a pod security policy or security context constraint (SCC) present which is preventing the deployment of azure-arc-diagnoser-job as it uses serviceaccount:azure-arc-troubleshoot-sa which does not have admin permissions.\nYou can whitelist it and then run the troubleshoot command again.\n")
            Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
            diagnoser_output.append("Unable to schedule the diagnoser job in the kubernetes cluster. There might be a pod security policy or security context constraint (SCC) present which is preventing the deployment of azure-arc-diagnoser-job as it uses serviceaccount:azure-arc-troubleshoot-sa which does not have admin permissions.\nYou can whitelist it and then run the troubleshoot command again.\n")
            return
        elif (is_job_scheduled is False):
            logger.warning("Unable to schedule the diagnoser job in the kubernetes cluster. The possible reasons can be presence of a security policy or security context constraint (SCC) or it may happen becuase of lack of ResourceQuota.\n")
            Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
            diagnoser_output.append("Unable to schedule the diagnoser job in the kubernetes cluster. The possible reasons can be presence of a security policy or security context constraint (SCC) or it may happen because of lack of ResourceQuota.\n")
            return
        elif (is_job_scheduled is True and is_job_complete is False):
            logger.warning("The diagnoser job failed to reach the completed state in the kubernetes cluster.\n")
            if storage_space_available:
                # Creating folder with name 'describe_non_ready_agent' in the given path
                unfinished_diagnoser_job_path = os.path.join(filepath_with_timestamp, consts.Events_of_Incomplete_Diagnoser_Job)
                cmd_get_diagnoser_job_events = [kubectl_client_location, "get", "events", "--field-selector", "", "-n", "azure-arc", "--output", "json"]
                if kube_config:
                    cmd_get_diagnoser_job_events.extend(["--kubeconfig", kube_config])
                if kube_context:
                    cmd_get_diagnoser_job_events.extend(["--context", kube_context])
                # To describe the diagnoser pod which did not reach completed stage
                arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")
                for each_pod in arc_agents_pod_list.items:
                    pod_name = each_pod.metadata.name
                    if (pod_name.startswith(job_name)):
                        # To retrieve the pod logs which is stuck
                        cmd_get_diagnoser_job_events[4] = "involvedObject.name=" + pod_name
                        # Using Popen to execute the command and fetching the output
                        response_kubectl_get_events = Popen(cmd_get_diagnoser_job_events, stdout=PIPE, stderr=PIPE)
                        output_kubectl_get_events, error_kubectl_get_events = response_kubectl_get_events.communicate()
                        if response_kubectl_get_events.returncode != 0:
                            telemetry.set_exception(exception=error_kubectl_get_events.decode("ascii"), fault_type=consts.Kubectl_Get_Events_Failed_Fault_Type, summary='Error while doing kubectl get events')
                            logger.warning("Error while doing kubectl get events. We were not able to capture events log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_events.decode("ascii"))
                            diagnoser_output.append("Error while doing kubectl get events. We were not able to capture events log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_events.decode("ascii"))
                            return consts.Diagnostic_Check_Failed, storage_space_available
                        # Converting output obtained in json format and fetching the clusterconnect-agent feature
                        events_json = json.loads(output_kubectl_get_events)
                        if len(events_json["items"]) != 0:
                            with open(unfinished_diagnoser_job_path, 'w+') as unfinished_diagnoser_job:
                                # Adding all the individual events
                                for events in events_json["items"]:
                                    unfinished_diagnoser_job.write(str(events) + "\n")
            Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
            diagnoser_output.append("The diagnoser job failed to reach the completed state in the kubernetes cluster.\n")
            return
        else:
            # Fetching the Diagnoser Container logs
            all_pods = corev1_api_instance.list_namespaced_pod('azure-arc')
            # Traversing through all agents
            for each_pod in all_pods.items:
                # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
                pod_name = each_pod.metadata.name
                if (pod_name.startswith(job_name)):
                    # Creating a text file with the name of the container and adding that containers logs in it
                    diagnoser_container_log = corev1_api_instance.read_namespaced_pod_log(name=pod_name, container="azure-arc-diagnoser-container", namespace='azure-arc')
        # Clearing all the resources after fetching the diagnoser container logs
        Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to execute the diagnoser job in the cluster. Exception: {}".format(str(e)) + "\n")
        Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Job_Failed_Fault_Type, summary="Error while executing Diagnoser Job")
        diagnoser_output.append("An exception has occured while trying to execute the diagnoser job in the cluster. Exception: {}".format(str(e)) + "\n")
        return

    return diagnoser_container_log


def check_msi_certificate_presence(corev1_api_instance):

    global diagnoser_output
    try:
        # Initializing msi certificate as not present
        msi_cert_present = False
        # Going through all the secrets in azure-arc
        all_secrets_azurearc = corev1_api_instance.list_namespaced_secret(namespace="azure-arc")
        for secrets in all_secrets_azurearc.items:
            # If name of secret is azure-identity-certificate then we stop there
            if (secrets.metadata.name == consts.MSI_Certificate_Secret_Name):
                msi_cert_present = True

        # Checking if msi cerificate is present or not
        if not msi_cert_present:
            logger.warning("Error: Unable to pull MSI certificate. Please ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements'. \n")
            diagnoser_output.append("Error: Unable to pull MSI certificate. Please ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements'. \n")
            return consts.Diagnostic_Check_Failed

        return consts.Diagnostic_Check_Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing the msi certificate check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.MSI_Cert_Check_Fault_Type, summary="Error occurred while trying to perform MSI certificate presence check")
        diagnoser_output.append("An exception has occured while performing the msi certificate check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Incomplete


def check_probable_cluster_security_policy(corev1_api_instance, helm_client_location, release_namespace, kube_config, kube_context):

    global diagnoser_output
    try:
        # Intializing the kap_pod_present and cluster_connect_feature variable as False
        kap_pod_present = False
        cluster_connect_feature = False
        # CMD command to get helm values in azure arc and converting it to json format
        command = [helm_client_location, "get", "values", "azure-arc", "--namespace", release_namespace, "-o", "json"]
        if kube_config:
            command.extend(["--kubeconfig", kube_config])
        if kube_context:
            command.extend(["--kube-context", kube_context])
        # Using Popen to execute the helm get values command and fetching the output
        response_helm_values_get = Popen(command, stdout=PIPE, stderr=PIPE)
        output_helm_values_get, error_helm_get_values = response_helm_values_get.communicate()
        if response_helm_values_get.returncode != 0:
            if ('forbidden' in error_helm_get_values.decode("ascii") or 'timed out waiting for the condition' in error_helm_get_values.decode("ascii")):
                telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Get_Helm_Values_Failed,
                                        summary='Error while doing helm get values azure-arc')
        # Converting output obtained in json format and fetching the clusterconnect-agent feature
        helm_values_json = json.loads(output_helm_values_get)
        cluster_connect_feature = helm_values_json["systemDefaultValues"]["clusterconnect-agent"]["enabled"]
        # To retrieve all of the arc agent pods that are present in the Cluster
        arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")
        # Traversing through all agents and checking if the Kube aad proxy pod is present or not
        for each_agent_pod in arc_agents_pod_list.items:
            if (each_agent_pod.metadata.name.startswith("kube-aad-proxy")):
                kap_pod_present = True
                break
        # Checking if there is any chance of pod security policy presence
        if (cluster_connect_feature is True and kap_pod_present is False):
            logger.warning("Error: Unable to create Kube-aad-proxy deployment. There might be a pod security policy or security context constraint (SCC) present which is preventing the deployment of kube-aad-proxy as it doesn't have admin privileges.\nKube aad proxy pod uses the azure-arc-kube-aad-proxy-sa service account, which doesn't have admin permissions but requires the permission to mount host path.\n")
            diagnoser_output.append("Error: Unable to create Kube-aad-proxy deployment. There might be a pod security policy or security context constraint (SCC) present which is preventing the deployment of kube-aad-proxy as it doesn't have admin privileges.\nKube aad proxy pod uses the azure-arc-kube-aad-proxy-sa service account, which doesn't have admin permissions but requires the permission to mount host path.\n")
            return consts.Diagnostic_Check_Failed
        return consts.Diagnostic_Check_Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to performing kube aad proxy presence and pod security policy presence check in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_Security_Policy_Check_Fault_Type, summary="Error occurred while trying to perform KAP certificate presence check")
        diagnoser_output.append("An exception has occured while trying to performing kube aad proxy presence and pod security policy presence check in the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Incomplete


def check_kap_cert(corev1_api_instance):

    global diagnoser_output
    try:
        # Initialize the kap_cert_present as False
        kap_cert_present = False
        kap_pod_status = ""
        # To retrieve all of the arc agent pods that are present in the Cluster
        arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")
        # Traversing through all agents and checking if the Kube aad proxy pod is in containercreating state
        for each_agent_pod in arc_agents_pod_list.items:
            if each_agent_pod.metadata.name.startswith("kube-aad-proxy") and each_agent_pod.status.phase == "ContainerCreating":
                kap_pod_status = "ContainerCreating"
                break
        # Going through all the secrets in azure-arc
        all_secrets_azurearc = corev1_api_instance.list_namespaced_secret(namespace="azure-arc")
        for secrets in all_secrets_azurearc.items:
            # If name of secret is kube-aad-proxy-certificate then we stop there
            if (secrets.metadata.name == consts.KAP_Certificate_Secret_Name):
                kap_cert_present = True
        if not kap_cert_present and kap_pod_status == "ContainerCreating":
            logger.warning("Error: Unable to pull Kube aad proxy certificate. Please attempt to onboard the cluster again.\n")
            diagnoser_output.append("Error: Unable to pull Kube aad proxy certificate. Please attempt to onboard the cluster again.\n")
            return consts.Diagnostic_Check_Failed

        return consts.Diagnostic_Check_Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception occured while trying to check the presence of kube aad proxy certificater. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.KAP_Cert_Check_Fault_Type, summary="Error occurred while trying to perform KAP certificate presence check")
        diagnoser_output.append("An exception occured while trying to check the presence of kube aad proxy certificate. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Incomplete


def check_msi_expiry(connected_cluster):

    global diagnoser_output
    try:
        # Fetch the expiry time of the msi certificate
        Expiry_date = str(connected_cluster.managed_identity_certificate_expiration_time)
        # Fetch the current time and format it same as msi certificate
        Current_date_temp = datetime.datetime.now().utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat()
        Current_date = Current_date_temp.replace('T', ' ')
        # Check if expiry date is lesser than current time
        if (Expiry_date < Current_date):
            logger.warning("Error: Your MSI certificate has expired. To resolve this issue you can delete the connected cluster and reconnect it to azure arc.\n")
            diagnoser_output.append("Error: Your MSI certificate has expired. To resolve this issue you can delete the connected cluster and reconnect it to azure arc.\n")
            return consts.Diagnostic_Check_Failed

        return consts.Diagnostic_Check_Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing msi expiry check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.MSI_Cert_Expiry_Check_Fault_Type, summary="Error occured while trying to perform the MSI cert expiry check")
        diagnoser_output.append("An exception has occured while performing msi expiry check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Diagnostic_Check_Incomplete


def describe_non_ready_agent_log(filepath_with_timestamp, corev1_api_instance, agent_pod_name, storage_space_available):

    try:
        # To describe pod if its not in running state and storing it if storage is available
        if storage_space_available:
            # Creating folder with name 'describe_non_ready_agent' in the given path
            describe_stuck_agent_path = os.path.join(filepath_with_timestamp, consts.Describe_Non_Ready_Arc_Agents)
            try:
                os.mkdir(describe_stuck_agent_path)
            except FileExistsError:
                pass
            # To retrieve the pod logs which is stuck
            api_response = corev1_api_instance.read_namespaced_pod(name=agent_pod_name, namespace='azure-arc')
            stuck_agent_pod_path = os.path.join(describe_stuck_agent_path, agent_pod_name + '.txt')
            with open(stuck_agent_pod_path, 'w+') as stuck_agent_log:
                stuck_agent_log.write(str(api_response))

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while storing stuck agent logs in the user local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Describe_Stuck_Agents_Fault_Type, summary="Error occured while storing the stuck agents description")
            diagnoser_output.append("An exception has occured while storing stuck agent logs in the user local machine. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while storing stuck agent logs in the user local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Describe_Stuck_Agents_Fault_Type, summary="Error occured while storing the stuck agents description")
        diagnoser_output.append("An exception has occured while storing stuck agent logs in the user local machine. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def get_secrets_azure_arc(corev1_api_instance, kubectl_client_location, kube_config, kube_context, filepath_with_timestamp, storage_space_available):

    try:
        if storage_space_available:
            command = [kubectl_client_location, "get", "secrets", "-n", "azure-arc"]
            if kube_config:
                command.extend(["--kubeconfig", kube_config])
            if kube_context:
                command.extend(["--context", kube_context])
            # Using Popen to execute the command and fetching the output
            response_kubectl_get_secrets = Popen(command, stdout=PIPE, stderr=PIPE)
            output_kubectl_get_secrets, error_kubectl_get_secrets = response_kubectl_get_secrets.communicate()
            if response_kubectl_get_secrets.returncode != 0:
                telemetry.set_exception(exception=error_kubectl_get_secrets.decode("ascii"), fault_type=consts.Kubectl_Get_Secrets_Failed_Fault_Type, summary='Error while doing kubectl get secrets')
                logger.warning("Error while doing kubectl get secrets for azure-arc namespace. We were not able to capture this log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_secrets.decode("ascii"))
                diagnoser_output.append("Error while doing kubectl get secrets in azure-arc namespace. We were not able to capture this log in arc_diganostic_logs folder. Exception: " + error_kubectl_get_secrets.decode("ascii"))
                return storage_space_available

            # Converting output obtained in json format
            secrets_json = output_kubectl_get_secrets.decode()
            # Path to add the azure-arc secrets
            secrets_logs_path = os.path.join(filepath_with_timestamp, "azure-arc-secrets.txt")

            with open(secrets_logs_path, 'w+') as secrets_log:
                secrets_log.write(secrets_json)

            return storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while storing list of secrets in azure arc namespace in the user local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_Kubectl_Get_Secrets_Fault_Type, summary="Exception occured while storing azure arc secrets")
            diagnoser_output.append("An exception has occured while storing azure arc secrets in the user local machine. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while storing list of secrets in azure arc namespace in the user local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_Kubectl_Get_Secrets_Fault_Type, summary="Exception occured while storing azure arc secrets")
        diagnoser_output.append("An exception has occured while storing azure arc secrets in the user local machine. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def get_helm_values_azure_arc(corev1_api_instance, helm_client_location, release_namespace, kube_config, kube_context, filepath_with_timestamp, storage_space_available):

    try:
        if storage_space_available:
            command = [helm_client_location, "get", "values", "azure-arc", "-n", release_namespace, "--output", "json"]
            if kube_config:
                command.extend(["--kubeconfig", kube_config])
            if kube_context:
                command.extend(["--kube-context", kube_context])
            # Using Popen to execute the command and fetching the output
            response_kubectl_get_helmvalues = Popen(command, stdout=PIPE, stderr=PIPE)
            output_kubectl_get_helmvalues, error_kubectl_get_helmvalues = response_kubectl_get_helmvalues.communicate()
            if response_kubectl_get_helmvalues.returncode != 0:
                telemetry.set_exception(exception=error_kubectl_get_helmvalues.decode("ascii"), fault_type=consts.Helm_Values_Save_Failed_Fault_Type, summary='Error while doing helm get values for azure-arc release')
                logger.warning("Error while doing helm get values for azure-arc release. We were not able to capture this log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_helmvalues.decode("ascii"))
                diagnoser_output.append("Error while doing helm get values for azure-arc release. We were not able to capture this log in arc_diganostic_logs folder. Exception: " + error_kubectl_get_helmvalues.decode("ascii"))
                return storage_space_available

            # Converting output obtained in json format
            helmvalues_json = output_kubectl_get_helmvalues.decode("ascii")
            helmvalues_json = json.loads(helmvalues_json)

            # removing onboarding private key
            try:
                if (helmvalues_json['global']['onboardingPrivateKey']):
                    del helmvalues_json['global']['onboardingPrivateKey']
            except Exception:
                pass

            # removing azure-rbac client id and client secret, if present
            try:
                if (helmvalues_json['systemDefaultValues']['guard']['clientId']):
                    del helmvalues_json['systemDefaultValues']['guard']['clientId']
                if (helmvalues_json['systemDefaultValues']['guard']['clientSecret']):
                    del helmvalues_json['systemDefaultValues']['guard']['clientSecret']
            except Exception:
                pass

            helmvalues_json = yaml.dump(helmvalues_json)
            # Path to add the helm values of azure-arc release
            helmvalues_logs_path = os.path.join(filepath_with_timestamp, "helm_values_azure_arc.txt")

            with open(helmvalues_logs_path, 'w') as helmvalues_log:
                helmvalues_log.write(helmvalues_json)

            return storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while storing helm values of azure-arc release in the user local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_Helm_Values_Save_Failed_Fault_Type, summary="Exception occured while storing helm values of azure-arc release")
            diagnoser_output.append("An exception has occured while storing helm values of azure-arc release in the user local machine. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while storing helm values of azure-arc release in the user local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_Helm_Values_Save_Failed_Fault_Type, summary="Exception occured while storing helm values of azure-arc release")
        diagnoser_output.append("An exception has occured while storing helm values of azure-arc release in the user local machine. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def get_metadata_cr_snapshot(corev1_api_instance, kubectl_client_location, kube_config, kube_context, filepath_with_timestamp, storage_space_available):

    try:
        if storage_space_available:
            command = [kubectl_client_location, "describe", "connectedclusters.arc.azure.com/clustermetadata", "-n", "azure-arc"]
            if kube_config:
                command.extend(["--kubeconfig", kube_config])
            if kube_context:
                command.extend(["--context", kube_context])
            # Using Popen to execute the command and fetching the output
            response_kubectl_get_metadata_cr = Popen(command, stdout=PIPE, stderr=PIPE)
            output_kubectl_get_metadata_cr, error_kubectl_get_metadata_cr = response_kubectl_get_metadata_cr.communicate()
            if response_kubectl_get_metadata_cr.returncode != 0:
                telemetry.set_exception(exception=error_kubectl_get_metadata_cr.decode("ascii"), fault_type=consts.Metadata_CR_Save_Failed_Fault_Type, summary='Error occured while fetching metadata CR details')
                logger.warning("Error while doing kubectl describe for clustermetadata CR. We were not able to capture this log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_metadata_cr.decode("ascii"))
                diagnoser_output.append("Error occured while fetching metadata CR details. We were not able to capture this log in arc_diganostic_logs folder. Exception: " + error_kubectl_get_metadata_cr.decode("ascii"))
                return storage_space_available

            # Converting output obtained in json format
            metadata_cr_json = output_kubectl_get_metadata_cr.decode()
            # Path to add the metadata CR details
            metadata_cr_logs_path = os.path.join(filepath_with_timestamp, "metadata_cr_snapshot.txt")

            with open(metadata_cr_logs_path, 'w+') as metadata_cr_log:
                metadata_cr_log.write(metadata_cr_json)

            return storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while storing metadata CR details in the user local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_Metadata_CR_Save_Failed_Fault_Type, summary="Error occured while storing metadata CR details")
            diagnoser_output.append("An exception has occured while storing metadata CR details in the user local machine. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while storing metadata CR details in the user local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_Metadata_CR_Save_Failed_Fault_Type, summary="Error occured while storing metadata CR details")
        diagnoser_output.append("An exception has occured while storing metadata CR details in the user local machine. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def get_kubeaadproxy_cr_snapshot(corev1_api_instance, kubectl_client_location, kube_config, kube_context, filepath_with_timestamp, storage_space_available):

    try:
        if storage_space_available:
            command = [kubectl_client_location, "describe", "arccertificates.clusterconfig.azure.com/kube-aad-proxy", "-n", "azure-arc"]
            if kube_config:
                command.extend(["--kubeconfig", kube_config])
            if kube_context:
                command.extend(["--context", kube_context])
            # Using Popen to execute the command and fetching the output
            response_kubectl_get_kap_cr = Popen(command, stdout=PIPE, stderr=PIPE)
            output_kubectl_get_kap_cr, error_kubectl_get_kap_cr = response_kubectl_get_kap_cr.communicate()
            if response_kubectl_get_kap_cr.returncode != 0:
                telemetry.set_exception(exception=error_kubectl_get_kap_cr.decode("ascii"), fault_type=consts.KAP_CR_Save_Failed_Fault_Type, summary='Error occured while fetching KAP CR details')
                logger.warning("Error while doing kubectl describe for kube-aad-proxy CR. We were not able to capture this log in arc_diganostic_logs folder. Exception: ", error_kubectl_get_kap_cr.decode("ascii"))
                diagnoser_output.append("Error occured while fetching kube-aad-proxy CR details. We were not able to capture this log in arc_diganostic_logs folder. Exception: " + error_kubectl_get_kap_cr.decode("ascii"))
                return storage_space_available

            # Converting output obtained in json format
            kap_cr_json = output_kubectl_get_kap_cr.decode()
            # Path to add the kube-aad-proxy CR details
            kap_cr_logs_path = os.path.join(filepath_with_timestamp, "kube_aad_proxy_cr_snapshot.txt")

            with open(kap_cr_logs_path, 'w+') as kap_cr_log:
                kap_cr_log.write(kap_cr_json)

            return storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while storing kube-aad-proxy CR details in the user local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Fetch_KAP_CR_Save_Failed_Fault_Type, summary="Exception occured while storing kube-aad-proxy CR details")
            diagnoser_output.append("An exception has occured while storing kube-aad-proxy CR details in the user local machine. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while storing kube-aad-proxy CR details in the user local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Fetch_KAP_CR_Save_Failed_Fault_Type, summary="Exception occured while storing kube-aad-proxy CR details")
        diagnoser_output.append("An exception has occured while storing kube-aad-proxy CR details in the user local machine. Exception: {}".format(str(e)) + "\n")

    return storage_space_available


def fetching_cli_output_logs(filepath_with_timestamp, storage_space_available, flag):

    # This function is used to store the output that is obtained throughout the Diagnoser process

    global diagnoser_output
    try:
        # If storage space is available then only we store the output
        if storage_space_available:
            # Path to store the diagnoser results
            cli_output_logger_path = os.path.join(filepath_with_timestamp, consts.Diagnoser_Results)
            # If any results are obtained during the process than we will add it to the text file.
            if len(diagnoser_output) > 0:
                with open(cli_output_logger_path, 'w+') as cli_output_writer:
                    for output in diagnoser_output:
                        cli_output_writer.write(output + "\n")
                    # If flag is 0 that means that process was terminated using the Keyboard Interrupt so adding that also to the text file
                    if flag == 0:
                        cli_output_writer.write("Process terminated externally.\n")

            # If no issues was found during the whole troubleshoot execution
            elif flag:
                with open(cli_output_logger_path, 'w+') as cli_output_writer:
                    cli_output_writer.write("The diagnoser didn't find any issues on the cluster.\n")
            # If process was terminated by user
            else:
                with open(cli_output_logger_path, 'w+') as cli_output_writer:
                    cli_output_writer.write("Process terminated externally.\n")

        return consts.Diagnostic_Check_Passed

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to store the diagnoser results. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Result_Fault_Type, summary="Error while storing the diagnoser results")

    return consts.Diagnostic_Check_Failed
