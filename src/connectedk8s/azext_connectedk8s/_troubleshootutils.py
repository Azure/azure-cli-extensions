# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import Namespace
from pydoc import cli
from kubernetes import client, config, watch, utils
from binascii import a2b_hex
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
logger = get_logger(__name__)
# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long

diagnoser_output = []


def create_folder_diagnosticlogs(time_stamp):

    global diagnoser_output
    try:

        # Fetching path to user directory to create the arc diagnostic folder
        home_dir = os.path.expanduser('~')
        filepath = os.path.join(home_dir, '.azure', 'arc_diagnostic_logs')

        # Creating Diagnostic folder and its subfolder with the given timestamp and cluster name to store all the logs
        try:
            os.mkdir(filepath)
        except FileExistsError:
            pass

        filepath_with_timestamp = os.path.join(filepath, time_stamp)
        try:
            os.mkdir(filepath_with_timestamp)
        except FileExistsError:
            pass

        return filepath_with_timestamp, consts.Folder_Created

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            return "", consts.No_Storage_Space
        else:
            logger.warning("An exception has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type, summary="Error while trying to create diagnostic logs folder")
            diagnoser_output.append("An exception has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
            return "", consts.Folder_Not_Created

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type, summary="Error while trying to create diagnostic logs folder")
        diagnoser_output.append("An exception has occured while creating the diagnostic logs folder in your local machine. Exception: {}".format(str(e)) + "\n")
        return "", consts.Folder_Not_Created


def fetch_connected_cluster_resource(filepath_with_timestamp, connected_cluster, storage_space_available):

    global diagnoser_output
    try:

        # Path to add the connected_cluster resource
        connected_cluster_resource_path = os.path.join(filepath_with_timestamp, "Connected_cluster_resource.txt")
        if storage_space_available:

            # If storage space is available then obly store the connected cluster resource
            with open(connected_cluster_resource_path, 'w+') as cc:
                cc.write(str(connected_cluster))
        return consts.Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to store the connected cluster resource from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Connected_Cluster_Resource_Fault_Type, summary="Error occured while fetching the Get output of connected cluster")
            diagnoser_output.append("An exception has occured while trying to store the connected cluster resource from the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to store the connected cluster resource logs from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Connected_Cluster_Resource_Fault_Type, summary="Eror occure while storing the connected cluster resource logs")
        diagnoser_output.append("An exception has occured while trying to store the connected cluster resource logs from the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Failed, storage_space_available


def retrieve_arc_agents_logs(corev1_api_instance, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    try:

        if storage_space_available:
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

                    # Path to add the arc agents container logs.
                    arc_agent_container_logs_path = os.path.join(agent_name_logs_path, container_name + ".txt")
                    with open(arc_agent_container_logs_path, 'w+') as container_file:
                        container_file.write(str(container_log))

        return consts.Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Logger_Fault_Type, summary="Error occured in arc agents logger")
            diagnoser_output.append("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Logger_Fault_Type, summary="Error occured in arc agents logger")
        diagnoser_output.append("An exception has occured while trying to fetch the azure arc agents logs from the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Failed, storage_space_available


def retrieve_arc_agents_event_logs(filepath_with_timestamp, storage_space_available, kubectl_client_location):

    global diagnoser_output
    try:

        # If storage space available then only store the azure-arc events
        if storage_space_available:

            # CMD command to get events using kubectl and converting it to json format
            command = [kubectl_client_location, "get", "events", "-n", "azure-arc", "--output", "json"]

            # Using Popen to execute the command and fetching the output
            response_kubectl_get_events = Popen(command, stdout=PIPE, stderr=PIPE)
            output_kubectl_get_events, error_kubectl_get_events = response_kubectl_get_events.communicate()

            if response_kubectl_get_events.returncode != 0:
                telemetry.set_exception(exception=error_kubectl_get_events.decode("ascii"), fault_type=consts.Kubectl_Get_Events_Failed, summary='Error while doing kubectl get events')
                logger.warning("Error while doing kubectl get events")

            # Converting output obtained in json format and fetching the clusterconnect-agent feature
            events_json = json.loads(output_kubectl_get_events)

            # Path to add the azure-arc events
            event_logs_path = os.path.join(filepath_with_timestamp, "Arc_Agents_Events.txt")
            with open(event_logs_path, 'w+') as event_log:

                # Adding all the individual events
                for events in events_json["items"]:
                        event_log.write(str(events) + "\n")

            return consts.Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Events_Logger_Fault_Type, summary="Error occured in arc agents events logger")
            diagnoser_output.append("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Arc_Agents_Events_Logger_Fault_Type, summary="Error occured in arc agents events logger")
        diagnoser_output.append("An exception has occured while trying to fetch the events occured in azure-arc namespace from the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Failed, storage_space_available


def retrieve_deployments_logs(appv1_api_instance, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    try:

        if storage_space_available:

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

        return consts.Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Arc_Deployments_Logger_Fault_Type, summary="Error occured in deployments logger")
            diagnoser_output.append("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Arc_Deployments_Logger_Fault_Type, summary="Error occured in deployments logger")
        diagnoser_output.append("An exception has occured while trying to fetch the azure arc deployment logs from the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Failed, storage_space_available


def check_agent_state(corev1_api_instance, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    all_agents_stuck = True
    sufficient_resource_for_agents = True

    try:

        # To check if agents are stuck because of insufficient resource
        sufficient_resource_for_agents = True

        # To check if all the containers are working for the Running agents
        all_agent_containers_ready = True

        # If all agents are stuck we will skip the certificates check
        all_agents_stuck = True

        agent_state_path = os.path.join(filepath_with_timestamp, "Agent_State.txt")
        with open(agent_state_path, 'w+') as agent_state:
            # To retrieve all of the arc agent pods that are presesnt in the Cluster
            arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

            # Check if any arc agent is not in Running state
            for each_agent_pod in arc_agents_pod_list.items:

                if storage_space_available:

                    # Storing the state of the arc agent in the user machine
                    agent_state.write(each_agent_pod.metadata.name + " : Phase = " + each_agent_pod.status.phase + "\n")

                    if each_agent_pod.status.phase == 'Running':
                        all_agents_stuck = False

                    if each_agent_pod.status.container_statuses is None:
                        sufficient_resource_for_agents = False
                        storage_space_available = describe_stuck_agent_log(filepath_with_timestamp, corev1_api_instance, each_agent_pod.metadata.name, storage_space_available)
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
                                except Exception as e:
                                    container_not_ready_reason = None

                                # Adding the reason if continer is not in ready state
                                if container_not_ready_reason is not None:
                                    agent_state.write("\t" + each_container_status.name + " :" + " Ready = False {Reason : " + str(container_not_ready_reason) + "} , Restart_Counts = " + str(each_container_status.restart_count) + "\n")
                                else:
                                    agent_state.write("\t" + each_container_status.name + " :" + " Ready = " + str(each_container_status.ready) + ", Restart_Counts = " + str(each_container_status.restart_count) + "\n")

                            else:
                                agent_state.write("\t" + each_container_status.name + " :" + " Ready = " + str(each_container_status.ready) + ", Restart_Counts = " + str(each_container_status.restart_count) + "\n")

                        if all_containers_ready_for_each_agent is False:
                            storage_space_available = describe_stuck_agent_log(filepath_with_timestamp, corev1_api_instance, each_agent_pod.metadata.name, storage_space_available)
                    # Adding empty line after each agents for formatting
                    agent_state.write("\n")

        # Displaying error if the arc agents are in pending state.
        if sufficient_resource_for_agents is False:
            print("Error: One or more Azure Arc agents are not in running state. It may be caused due to insufficient resource availability on the cluster.\n")
            diagnoser_output.append("Error: One or more Azure Arc agents are not in running state. It may be caused due to insufficient resource availability on the cluster.\n")
            return consts.Failed, storage_space_available, all_agents_stuck, sufficient_resource_for_agents

        elif all_agent_containers_ready is False:
            print("Error: One or more agents in the Azure Arc are not fully running.\n")
            diagnoser_output.append("Error: One or more agents in the Azure Arc are not fully runnning.\n")
            return consts.Failed, storage_space_available, all_agents_stuck, sufficient_resource_for_agents

        return consts.Passed, storage_space_available, all_agents_stuck, sufficient_resource_for_agents

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

    return consts.Incomplete, storage_space_available, all_agents_stuck, sufficient_resource_for_agents


def check_agent_version(connected_cluster, azure_arc_agent_version):

    global diagnoser_output
    try:

        # If the agent version in the connected cluster resource is none skip the check
        if(connected_cluster.agent_version is None):
            return consts.Incomplete

        # To get user agent verison and the latest agent version
        user_agent_version = connected_cluster.agent_version
        current_user_version = user_agent_version.split('.')
        latest_agent_version = azure_arc_agent_version.split('.')

        # Comparing if the user version is comaptible or not
        if((int(current_user_version[0]) < int(latest_agent_version[0])) or (int(latest_agent_version[1]) - int(current_user_version[1]) > 2)):
            logger.warning("We found that you are on an older agent version that is not supported.\n Please visit this link to know the agent version support policy 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/agent-upgrade#version-support-policy'.\n")
            diagnoser_output.append("We found that you are on an older agent version that is not supported.\n Please visit this link to know the agent version support policy 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/agent-upgrade#version-support-policy'.\n")
            return consts.Failed

        return consts.Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to check the azure arc agents version in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Agent_Version_Check_Fault_Type, summary="Error occured while performing the agent version check")
        diagnoser_output.append("An exception has occured while trying to check the azure arc agents version in the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete


def check_diagnoser_container(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp, storage_space_available, absolute_path, sufficient_resource_for_agents, helm_client_location, kubectl_client_location, release_namespace, security_policy_present):

    global diagnoser_output
    try:

        if sufficient_resource_for_agents is False:
            logger.warning("Unable to execute the diagnoser job in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            diagnoser_output.append("Unable to execute the diagnoser job in the cluster. It may be caused due to insufficient resource availability on the cluster.\n")
            return consts.Incomplete, storage_space_available

        # Setting DNS and Outbound Check as working
        dns_check = "Starting"
        outbound_connectivity_check = "Starting"

        # Executing the Diagnoser job and fetching the logs obtained
        diagnoser_container_log = executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp, storage_space_available, absolute_path, helm_client_location, kubectl_client_location, release_namespace, security_policy_present)

        # If diagnoser_container_log is not empty then only we will check for the results
        if(diagnoser_container_log != ""):
            diagnoser_container_log_list = diagnoser_container_log.split("\n")
            diagnoser_container_log_list.pop(-1)
            dns_check, storage_space_available = check_cluster_DNS(diagnoser_container_log_list[-2], filepath_with_timestamp, storage_space_available)
            outbound_connectivity_check, storage_space_available = check_cluster_outbound_connectivity(diagnoser_container_log_list[-1], filepath_with_timestamp, storage_space_available)
        else:
            return consts.Incomplete, storage_space_available

        # If both the check passed then we will return Diagnoser checks Passed
        if(dns_check == consts.Passed and outbound_connectivity_check == consts.Passed):
            return consts.Passed, storage_space_available

        # If any of the check remain Incomplete than we will return Incomplete
        elif(dns_check == consts.Incomplete or outbound_connectivity_check == consts.Incomplete):
            return consts.Incomplete, storage_space_available
        else:
            return consts.Failed, storage_space_available

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to perform diagnoser container check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Container_Check_Fault_Type, summary="Error occured while performing the diagnoser container checks")
        diagnoser_output.append("An exception has occured while trying to perform diagnoser container check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete, storage_space_available


def executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp, storage_space_available, absolute_path, helm_client_location, kubectl_client_location, release_namespace, security_policy_present):

    global diagnoser_output
    job_name = "azure-arc-diagnoser-job"
    # CMD command to get helm values in azure arc and converting it to json format
    command = [helm_client_location, "get", "values", "azure-arc", "--namespace", release_namespace, "-o", "json"]

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
        is_proxy_enabled = False
    try:
        is_custom_cert = helm_values_json["global"]["isCustomCert"]
    except Exception as e:
        is_custom_cert = False
    try:
        proxy_cert = helm_values_json["global"]["proxyCert"]
    except Exception as e:
        proxy_cert = False

    # Depending on the presence of proxy cert using the yaml
    if proxy_cert and (is_custom_cert or is_proxy_enabled):
        yaml_file_path = os.path.join(absolute_path, "troubleshoot_diagnoser_job_with_proxycert.yaml")

    else:
        yaml_file_path = os.path.join(absolute_path, "troubleshoot_diagnoser_job_without_proxycert.yaml")

    # Setting the log output as Empty
    diagnoser_container_log = ""
    cmd_delete_job = [kubectl_client_location, "delete", "-f", ""]
    cmd_delete_job[3] = str(yaml_file_path)

    # Editing the yaml file based on the release nameespace
    new_yaml = []
    with open(yaml_file_path) as f:
        list_doc = yaml.safe_load_all(f)
        counter = 0

        # USing release_namespace wherever required
        for each_yaml in list_doc:
            if(counter == 1 or counter == 2):
                each_yaml['metadata']['namespace'] = release_namespace
            elif(counter == 3):
                each_yaml['spec']['template']['spec']['containers'][0]['args'][0] = release_namespace

            counter += 1
            new_yaml.append(each_yaml)

    # Updating the yaml file
    with open(yaml_file_path, 'w+') as f:
        for i in new_yaml:
            f.write("---\n")
            yaml.dump(i, f)

    # To handle the user keyboard Interrupt
    try:

        # Executing the diagnoser_job.yaml
        config.load_kube_config()
        k8s_client = client.ApiClient()

        # To check if there are any issues while trying to deploy the Jobs yaml file
        try:
            utils.create_from_yaml(k8s_client, yaml_file_path)

        # To handle the Exception that occured
        except Exception as e:

            # As there we are adding multiple objects from yaml we will split the error
            all_exceptions_list = str(e).split('\n')

            # Last element would be an empty element so removing it
            all_exceptions_list.pop(-1)

            # Setting the counter to print the that error occured while executing the yaml only once.
            counter = 0

            # Traversing all the exceptions in the list
            for ind_exception in all_exceptions_list:

                # If the error occured due to resource already present than we skip it
                if("Error from server (Conflict)" in ind_exception):
                    continue
                else:

                    # If counter is 0 we will print the Error statement once and then set the counter as 1
                    if(counter == 0):
                        diagnoser_output.append("An Error occured while trying to execute diagnoser_job.yaml.")
                        logger.warning("An Error occured while trying to execute diagnoser_job.yaml.")
                        counter = 1
                        logger.warning(ind_exception)
                    else:
                        logger.warning(ind_exception)
            logger.warning("\n")

            # If the counter is 1 that means error occured during execution of yaml so we skip the further process
            if(counter == 1):
                Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
                return ""

        # Watching for diagnoser contianer to reach in completed stage
        w = watch.Watch()
        did_job_complete = False
        did_job_got_scheduled = False
        # To watch for changes in the pods states till it reach completed state or exit if it takes more than 60 seconds
        for event in w.stream(batchv1_api_instance.list_namespaced_job, namespace='azure-arc', label_selector="", timeout_seconds=60):

            try:

                # Checking if job get scheduled or not
                if event["object"].metadata.name == "azure-arc-diagnoser-job":
                    did_job_got_scheduled = True
                # Checking if job reached completed stage or not
                if event["object"].metadata.name == "azure-arc-diagnoser-job" and event["object"].status.conditions[0].type == "Complete":
                    did_job_complete = True
                    w.stop()

            except Exception as e:
                continue
            else:
                continue

        # Selecting the error message depending on the job getting scheduled, completed and the presence of  security policy
        if (did_job_got_scheduled is False and security_policy_present == consts.Failed):
            logger.warning("Unable to schedule the diagnoser job in the kubernetes cluster. There might be a security policy or security context constraint (SCC) present which is preventing the deployment of azure-arc-diagnoser-job as it uses serviceaccount:azure-arc-troubleshoot-sa which doesnt have admin permissions.\nYou can whitelist it and then run the troubleshoot command again.\n")
            Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
            diagnoser_output.append("Unable to schedule the diagnoser job in the kubernetes cluster. There might be a security policy or security context constraint (SCC) present which is preventing the deployment of azure-arc-diagnoser-job as it uses serviceaccount:azure-arc-troubleshoot-sa which doesnt have admin permissions.\nYou can whitelist it and then run the troubleshoot command again.\n")
            return ""
        elif (did_job_got_scheduled is False):
            logger.warning("Unable to schedule the diagnoser job in the kubernetes cluster. The possible reasons can be presence of a security policy or security context constraint (SCC) or it may happen becuase of lack of ResourceQuota.\n")
            Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
            diagnoser_output.append("Unable to schedule the diagnoser job in the kubernetes cluster. The possible reasons can be presence of a security policy or security context constraint (SCC) or it may happen because of lack of ResourceQuota.\n")
            return ""
        elif (did_job_got_scheduled is True and did_job_complete is False):
            logger.warning("The diagnoser job failed to reach the completed state in the kubernetes cluster.\n")
            if storage_space_available:

                # Creating folder with name 'Describe_Stuck_Agents' in the given path
                unfinished_diagnoser_job_path = os.path.join(filepath_with_timestamp, 'Events_of_I_Diagnoser_Job.txt')

                cmd_get_diagnoser_job_events = [kubectl_client_location, "get", "events", "--field-selector", "", "-n", "azure-arc", "--output", "json"]
                # To describe the diagnoser pod which did not reach completed stage
                arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

                for each_pod in arc_agents_pod_list.items:
                    pod_name = each_pod.metadata.name

                    if(pod_name.startswith(job_name)):
                        # To retrieve the pod logs which is stuck

                        cmd_get_diagnoser_job_events[4] = "involvedObject.name=" + pod_name
                        # Using Popen to execute the command and fetching the output
                        response_kubectl_get_events = Popen(cmd_get_diagnoser_job_events, stdout=PIPE, stderr=PIPE)
                        output_kubectl_get_events, error_kubectl_get_events = response_kubectl_get_events.communicate()

                        if response_kubectl_get_events.returncode != 0:
                            telemetry.set_exception(exception=error_kubectl_get_events.decode("ascii"), fault_type=consts.Kubectl_Get_Events_Failed, summary='Error while doing kubectl get events')
                            logger.warning("Error while doing kubectl get events")

                        # Converting output obtained in json format and fetching the clusterconnect-agent feature
                        events_json = json.loads(output_kubectl_get_events)

                with open(unfinished_diagnoser_job_path, 'w+') as unfinished_diagnoser_job:
                    # Adding all the individual events
                    for events in events_json["items"]:
                            unfinished_diagnoser_job.write(str(events) + "\n")

            Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
            diagnoser_output.append("The diagnoser job failed to reach the completed state in the kubernetes cluster.\n")
            return ""

        else:

            # Fetching the Diagnoser Container logs
            try:

                all_pods = corev1_api_instance.list_namespaced_pod('azure-arc')
                # Traversing thorugh all agents
                for each_pod in all_pods.items:

                    # Fethcing the current Pod name and creating a folder with that name inside the timestamp folder
                    pod_name = each_pod.metadata.name

                    if(pod_name.startswith(job_name)):

                        # Creating a text file with the name of the container and adding that containers logs in it
                        diagnoser_container_log = corev1_api_instance.read_namespaced_pod_log(name=pod_name, container="azure-arc-diagnoser-container", namespace='azure-arc')

                # Clearing all the resources after fetching the diagnoser container logs
                Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)

            except Exception as e:
                Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
                return ""

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to execute the diagnoser job in the cluster. Exception: {}".format(str(e)) + "\n")
        Popen(cmd_delete_job, stdout=PIPE, stderr=PIPE)
        telemetry.set_exception(exception=e, fault_type=consts.Executing_Diagnoser_Job_Fault_Type, summary="Error while executing Diagnoser Job")
        diagnoser_output.append("An exception has occured while trying to execute the diagnoser job in the cluster. Exception: {}".format(str(e)) + "\n")

    return diagnoser_container_log


def check_cluster_DNS(dns_check_log, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    try:

        # Validating if DNS is working or not and displaying proper result
        if("NXDOMAIN" in dns_check_log or "connection timed out" in dns_check_log):
            print("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
            diagnoser_output.append("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
            if storage_space_available:
                dns_check_path = os.path.join(filepath_with_timestamp, "DNS_Check.txt")
                with open(dns_check_path, 'w+') as dns:
                    dns.write(dns_check_log + "\nWe found an issue with the DNS resolution on your cluster.")
            return consts.Failed, storage_space_available

        else:
            if storage_space_available:
                dns_check_path = os.path.join(filepath_with_timestamp, "DNS_Check.txt")
                with open(dns_check_path, 'w+') as dns:
                    dns.write(dns_check_log + "\nCluster DNS check passed successfully.")
            return consts.Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Cluster_DNS_Check_Fault_Type, summary="Error occured while performing cluster DNS check")
            diagnoser_output.append("An exception has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_DNS_Check_Fault_Type, summary="Error occured while performing cluster DNS check")
        diagnoser_output.append("An exception has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete, storage_space_available


def check_cluster_outbound_connectivity(outbound_connectivity_check_log, filepath_with_timestamp, storage_space_available):

    global diagnoser_output
    try:

        # Validating if outbound connectiivty is working or not and displaying proper result
        if(outbound_connectivity_check_log != "000"):
            if storage_space_available:
                outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, "Outbound_Network_Connectivity_Check.txt")
                with open(outbound_connectivity_check_path, 'w+') as outbound:
                    outbound.write("Response code " + outbound_connectivity_check_log + "\nOutbound network connectivity check passed successfully.")
            return consts.Passed, storage_space_available
        else:
            print("Error: We found an issue with outbound network connectivity from the cluster.\nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy paramaters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server'.\nPlease ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements' \n")
            diagnoser_output.append("Error: We found an issue with outbound network connectivity from the cluster.\nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy paramaters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server'.\nPlease ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements' \n")
            if storage_space_available:
                outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, "Outbound_Network_Connectivity_Check.txt")
                with open(outbound_connectivity_check_path, 'w+') as outbound:
                    outbound.write("Response code " + outbound_connectivity_check_log + "\nWe found an issue with Outbound network connectivity from the cluster.")
            return consts.Failed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Outbound_Connectivity_Check_Fault_Type, summary="Error occured while performing outbound connectivity check in the cluster")
            diagnoser_output.append("An exception has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Outbound_Connectivity_Check_Fault_Type, summary="Error occured while performing outbound connectivity check in the cluster")
        diagnoser_output.append("An exception has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete, storage_space_available


def check_msi_certificate_presence(corev1_api_instance):

    global diagnoser_output
    try:

        # Initializing msi certificate as not present
        msi_cert_present = False

        # Going thorugh all the secrets in azure-arc
        all_secrets_azurearc = corev1_api_instance.list_namespaced_secret(namespace="azure-arc")

        for secrets in all_secrets_azurearc.items:

            # If name of secret is azure-identity-certificate then we stop there
            if(secrets.metadata.name == consts.MSI_Certificate_Secret_Name):
                msi_cert_present = True

        # Checking if msi cerificate is present or not
        if not msi_cert_present:
            print("Error: Unable to pull MSI certificate. Please ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements'. \n")
            diagnoser_output.append("Error: Unable to pull MSI certificate. Please ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements'. \n")
            return consts.Failed

        return consts.Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing the msi certificate check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.MSI_Cert_Check_Fault_Type, summary="Error occurred while trying to perform MSI ceritificate presence check right")
        diagnoser_output.append("An exception has occured while performing the msi certificate check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete


def check_cluster_security_policy(corev1_api_instance, helm_client_location, release_namespace):

    global diagnoser_output
    try:
        # Intializing the kap_pod_present and cluster_connect_feature variable as False
        kap_pod_present = False
        cluster_connect_feature = False

        # CMD command to get helm values in azure arc and converting it to json format
        command = [helm_client_location, "get", "values", "azure-arc", "--namespace", release_namespace, "-o", "json"]

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

        # To retrieve all of the arc agent pods that are presesnt in the Cluster
        arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

        # Traversing thorugh all agents and checking if the Kube aad proxy pod is present or not
        for each_agent_pod in arc_agents_pod_list.items:

            if(each_agent_pod.metadata.name.startswith("kube-aad-proxy")):
                kap_pod_present = True
                break

        # Checking if any pod security policy is set
        if(cluster_connect_feature is True and kap_pod_present is False):
            print("Error: Unable to create Kube-aad-proxy deployment there might be a security policy or security context constraint (SCC) present which is preventing the deployment of kube-aad-proxy as it doesn't have admin privileges.\nKube aad proxy pod uses the azure-arc-kube-aad-proxy-sa service account, which doesn't have admin permissions but requires the permission to mount host path.\n ")
            diagnoser_output.append("Error: Unable to create Kube-aad-proxy deployment there might be a security policy or security context constraint (SCC) present which is preventing the deployment of kube-aad-proxy as it doesn't have admin privileges.\nKube aad proxy pod uses the azure-arc-kube-aad-proxy-sa service account, which doesn't have admin permissions but requires the permission to mount host path.\n")
            return consts.Failed
        return consts.Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to performing KAP cluster security policy check in the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_Security_Policy_Check_Fault_Type, summary="Error occurred while trying to perform KAP ceritificate presence check right")
        diagnoser_output.append("An exception has occured while trying to performing KAP cluster security policy check in the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete


def check_kap_cert(corev1_api_instance):

    global diagnoser_output
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
            if(secrets.metadata.name == consts.KAP_Certificate_Secret_Name):
                kap_cert_present = True

        if not kap_cert_present and kap_pod_status == "ContainerCreating":
            print("Error: Unable to pull Kube aad proxy certificate.\n")
            diagnoser_output.append("Error: Unable to pull Kube aad proxy certificate.\n")
            return consts.Failed

        return consts.Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing kube aad proxy certificate check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.KAP_Cert_Check_Fault_Type, summary="Error occured while trying to pull kap cert certificate")
        diagnoser_output.append("An exception has occured while performing kube aad proxy certificate check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete


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
            print("Error: Your MSI certificate has expired. To resolve this issue you can delete the cluster and reconnect it to azure arc.\n")
            diagnoser_output.append("Error: Your MSI certificate has expired. To resolve this issue you can delete the cluster and reconnect it to azure arc.\n")
            return consts.Failed

        return consts.Passed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing msi expiry check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.MSI_Cert_Expiry_Check_Fault_Type, summary="Error occured while trying to perform the MSI cert expiry check")
        diagnoser_output.append("An exception has occured while performing msi expiry check on the cluster. Exception: {}".format(str(e)) + "\n")

    return consts.Incomplete


def describe_stuck_agent_log(filepath_with_timestamp, corev1_api_instance, agent_pod_name, storage_space_available):

    try:

        # To describe pod if its not in running state and storing it if storage is available
        if storage_space_available:

            # Creating folder with name 'Describe_Stuck_Agents' in the given path
            describe_stuck_agent_path = os.path.join(filepath_with_timestamp, 'Describe_Non-Ready_Agents')
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


def cli_output_logger(filepath_with_timestamp, storage_space_available, flag):

    # This function is used to store the output that is obtained throughout the Diagnoser process
    global diagnoser_output
    try:

        # If storage space is available then only we store the output
        if storage_space_available:

            # Path to store the diagnoser results
            cli_output_logger_path = os.path.join(filepath_with_timestamp, "Diagnoser_Results.txt")

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
                    cli_output_writer.write("Diagnoser did not find any issues with the cluster.\n")

            # If process was terminated by user
            else:
                with open(cli_output_logger_path, 'w+') as cli_output_writer:
                    cli_output_writer.write("Process terminated externally.\n")

        return consts.Passed

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

    return consts.Failed
