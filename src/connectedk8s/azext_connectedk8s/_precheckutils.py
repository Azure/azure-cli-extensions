# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil
import subprocess
from subprocess import Popen, PIPE
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from kubernetes import client, config, watch, utils
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from azure.cli.core import telemetry
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError
from msrest.exceptions import ValidationError as MSRestValidationError
from kubernetes.client.rest import ApiException
import azext_connectedk8s._constants as consts
import azext_connectedk8s._utils as azext_utils
from kubernetes import client as kube_client
from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import CLIInternalError, ClientRequestError, ArgumentUsageError, ManualInterrupt, \
    AzureResponseError, AzureInternalError, ValidationError
from argparse import Namespace
from pydoc import cli
from logging import exception
import yaml
import json
import datetime
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
import shutil
from knack.log import get_logger
from azure.cli.core import telemetry
import azext_connectedk8s._constants as consts
logger = get_logger(__name__)
# pylint: disable=unused-argument, too-many-locals, too-many-branches, too-many-statements, line-too-long
# pylint: disable

diagnoser_output = []


def fetch_diagnostic_checks_results(corev1_api_instance, batchv1_api_instance, helm_client_location,
                                    kubectl_client_location, kube_config, kube_context, location, http_proxy,
                                    https_proxy, no_proxy, proxy_cert, azure_cloud, filepath_with_timestamp,
                                    storage_space_available):
    global diagnoser_output
    try:
        # Setting DNS and Outbound Check as working
        dns_check = "Starting"
        outbound_connectivity_check = "Starting"
        # Executing the cluster_diagnostic_checks job and fetching the logs obtained
        cluster_diagnostic_checks_container_log = \
            executing_cluster_diagnostic_checks_job(corev1_api_instance, batchv1_api_instance, helm_client_location,
                                                    kubectl_client_location, kube_config, kube_context, location,
                                                    http_proxy, https_proxy, no_proxy, proxy_cert, azure_cloud,
                                                    filepath_with_timestamp, storage_space_available)
        # If cluster_diagnostic_checks_container_log is not empty then only we will check for the results
        if (cluster_diagnostic_checks_container_log is not None and cluster_diagnostic_checks_container_log != ""):
            cluster_diagnostic_checks_container_log_list = cluster_diagnostic_checks_container_log.split("\n")
            cluster_diagnostic_checks_container_log_list.pop(-1)
            dns_check_log = ""
            outbound_connectivity_check_log = ""
            counter_container_logs = 1
            # For retrieving only cluster_diagnostic_checks logs from the output
            for outputs in cluster_diagnostic_checks_container_log_list:
                if consts.Outbound_Connectivity_Check_Result_String in outputs:
                    counter_container_logs = 1
                    if outbound_connectivity_check_log == "":
                        outbound_connectivity_check_log += outputs
                    else:
                        outbound_connectivity_check_log += "  " + outputs
                elif consts.DNS_Check_Result_String in outputs:
                    dns_check_log += outputs
                    counter_container_logs = 0
                elif counter_container_logs == 0:
                    dns_check_log += "  " + outputs
            dns_check, storage_space_available = \
                azext_utils.check_cluster_DNS(dns_check_log, filepath_with_timestamp,
                                              storage_space_available, diagnoser_output)
            outbound_connectivity_check, storage_space_available = \
                azext_utils.check_cluster_outbound_connectivity(outbound_connectivity_check_log,
                                                                filepath_with_timestamp, storage_space_available,
                                                                diagnoser_output)
        else:
            return consts.Diagnostic_Check_Incomplete, storage_space_available

        # If both the check passed then we will return cluster diagnostic checks Passed
        if (dns_check == consts.Diagnostic_Check_Passed and
                outbound_connectivity_check == consts.Diagnostic_Check_Passed):
            return consts.Diagnostic_Check_Passed, storage_space_available
        # If any of the check remain Incomplete than we will return Incomplete
        elif (dns_check == consts.Diagnostic_Check_Incomplete or
                outbound_connectivity_check == consts.Diagnostic_Check_Incomplete):
            return consts.Diagnostic_Check_Incomplete, storage_space_available
        else:
            return consts.Diagnostic_Check_Failed, storage_space_available

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to execute cluster diagnostic checks container on the \
            cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_Diagnostic_Checks_Execution_Failed_Fault_Type,
                                summary="Error occured while executing the cluster diagnostic checks container")

    return consts.Diagnostic_Check_Incomplete, storage_space_available


def executing_cluster_diagnostic_checks_job(corev1_api_instance, batchv1_api_instance, helm_client_location,
                                            kubectl_client_location, kube_config, kube_context, location,
                                            http_proxy, https_proxy, no_proxy, proxy_cert, azure_cloud,
                                            filepath_with_timestamp, storage_space_available):
    job_name = "cluster-diagnostic-checks-job"
    # Setting the log output as Empty
    cluster_diagnostic_checks_container_log = ""
    release_namespace = azext_utils.get_release_namespace(kube_config, kube_context, helm_client_location,
                                                          "cluster-diagnostic-checks")
    cmd_helm_delete = [helm_client_location, "delete", "cluster-diagnostic-checks", "-n", "azure-arc-release"]
    if kube_config:
        cmd_helm_delete.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])

    # To handle the user keyboard Interrupt
    try:
        # Executing the cluster diagnostic checks job yaml
        config.load_kube_config(kube_config, kube_context)
        # checking existence of the release and if present we delete the stale release
        if release_namespace is not None:
            # Attempting deletion of cluster diagnostic checks resources to handle the scenario if any stale
            # resources are present
            response_kubectl_delete_helm = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            output_kubectl_delete_helm, error_kubectl_delete_helm = response_kubectl_delete_helm.communicate()
            # If any error occured while execution of delete command
            if (response_kubectl_delete_helm.returncode != 0):
                # Converting the string of multiple errors to list
                error_msg_list = error_kubectl_delete_helm.decode("ascii").split("\n")
                error_msg_list.pop(-1)
                valid_exception_list = []
                # Checking if any exception occured or not
                exception_occured_counter = 0
                for ind_errors in error_msg_list:
                    if ('not found' in ind_errors or 'deleted' in ind_errors):
                        pass
                    else:
                        valid_exception_list.append(ind_errors)
                        exception_occured_counter = 1
                # If any exception occured we will print the exception and return
                if exception_occured_counter == 1:
                    logger.warning("Cleanup of previous diagnostic checks helm release failed and hence couldn't \
                        install the new helm release. Please cleanup older release using \"helm delete \
                            cluster-diagnostic-checks -n azure-arc-release\" and try onboarding again")
                    telemetry.set_exception(exception=error_kubectl_delete_helm.decode("ascii"),
                                            fault_type=consts.Cluster_Diagnostic_Checks_Release_Cleanup_Failed,
                                            summary="Error while executing cluster diagnostic checks Job")
                    return

        chart_path = azext_utils.get_chart_path(consts.Cluster_Diagnostic_Checks_Job_Registry_Path, kube_config,
                                                kube_context, helm_client_location,
                                                consts.Pre_Onboarding_Helm_Charts_Folder_Name,
                                                consts.Pre_Onboarding_Helm_Charts_Release_Name, False)

        helm_install_release_cluster_diagnostic_checks(chart_path, location, http_proxy, https_proxy, no_proxy,
                                                       proxy_cert, azure_cloud, kube_config, kube_context,
                                                       helm_client_location)

        # Watching for cluster diagnostic checks container to reach in completed stage
        w = watch.Watch()
        is_job_complete = False
        is_job_scheduled = False
        # To watch for changes in the pods states till it reach completed state or exit if it takes more than 180 seconds
        for event in w.stream(batchv1_api_instance.list_namespaced_job, namespace='azure-arc-release',
                              label_selector="", timeout_seconds=60):
            try:
                # Checking if job get scheduled or not
                if event["object"].metadata.name == "cluster-diagnostic-checks-job":
                    is_job_scheduled = True
                # Checking if job reached completed stage or not
                if event["object"].metadata.name == "cluster-diagnostic-checks-job" and \
                        event["object"].status.conditions[0].type == "Complete":
                    is_job_complete = True
                    w.stop()
            except Exception:
                continue
            else:
                continue

        azext_utils.save_cluster_diagnostic_checks_pod_description(corev1_api_instance, batchv1_api_instance,
                                                                   helm_client_location, kubectl_client_location,
                                                                   kube_config, kube_context, filepath_with_timestamp,
                                                                   storage_space_available)

        if (is_job_scheduled is False):
            telemetry.set_exception(exception="Couldn't schedule cluster diagnostic checks job in the cluster",
                                    fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Scheduled,
                                    summary="Couldn't schedule cluster diagnostic checks job in the cluster")
            logger.warning("Unable to schedule the cluster diagnostic checks job in the kubernetes cluster. The \
                possible reasons can be presence of a security policy or security context constraint (SCC) or it may \
                    happen becuase of lack of ResourceQuota.\n")
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        elif (is_job_scheduled is True and is_job_complete is False):
            telemetry.set_exception(exception="Couldn't complete cluster diagnostic checks job after scheduling in \
                the cluster", fault_type=consts.Cluster_Diagnostic_Checks_Job_Not_Complete,
                                    summary="Couldn't complete cluster diagnostic checks job after scheduling in the \
                                        cluster")
            logger.warning("Cluster diagnostics job didn't reach completed state in the kubernetes cluster. The \
                possible reasons can be resource constraints on the cluster.\n")
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        else:
            # Fetching the cluster diagnostic checks Container logs
            all_pods = corev1_api_instance.list_namespaced_pod('azure-arc-release')
            # Traversing through all agents
            for each_pod in all_pods.items:
                # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
                pod_name = each_pod.metadata.name
                if (pod_name.startswith(job_name)):
                    # Creating a text file with the name of the container and adding that containers logs in it
                    cluster_diagnostic_checks_container_log = \
                        corev1_api_instance.read_namespaced_pod_log(name=pod_name,
                                                                    container="cluster-diagnostic-checks-container",
                                                                    namespace='azure-arc-release')
                    try:
                        if storage_space_available:
                            dns_check_path = os.path.join(filepath_with_timestamp,
                                                          "cluster_diagnostic_checks_job_log.txt")
                            with open(dns_check_path, 'w+') as f:
                                f.write(cluster_diagnostic_checks_container_log)
                    except OSError as e:
                        if "[Errno 28]" in str(e):
                            storage_space_available = False
                            telemetry.set_exception(exception=e,
                                                    fault_type=consts.No_Storage_Space_Available_Fault_Type,
                                                    summary="No space left on device")
                            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
                        else:
                            logger.warning("An exception has occured while saving the cluster diagnostic checks job \
                                logs in the local machine. Exception: {}".format(str(e)) + "\n")
                            telemetry.set_exception(exception=e,
                                                    fault_type=consts.Cluster_Diagnostic_Checks_Job_Log_Save_Failed,
                                                    summary="Error occured while saving the cluster diagnostic \
                                                        checks job logs in the local machine")

                    # To handle any exception that may occur during the execution
                    except Exception as e:
                        logger.warning("An exception has occured while saving the cluster diagnostic checks job logs \
                            in the local machine. Exception: {}".format(str(e)) + "\n")
                        telemetry.set_exception(exception=e,
                                                fault_type=consts.Cluster_Diagnostic_Checks_Job_Log_Save_Failed,
                                                summary="Error occured while saving the cluster diagnostic checks \
                                                    job logs in the local machine")
        # Clearing all the resources after fetching the cluster diagnostic checks container logs
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to execute the cluster diagnostic checks in the \
            cluster. Exception: {}".format(str(e)) + "\n")
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_Diagnostic_Checks_Execution_Failed_Fault_Type,
                                summary="Error while executing cluster diagnostic checks Job")
        return

    return cluster_diagnostic_checks_container_log


def helm_install_release_cluster_diagnostic_checks(chart_path, location, http_proxy, https_proxy, no_proxy, proxy_cert,
                                                   azure_cloud, kube_config, kube_context, helm_client_location,
                                                   onboarding_timeout="60"):
    cmd_helm_install = [helm_client_location, "upgrade", "--install", "cluster-diagnostic-checks", chart_path,
                        "--namespace", "{}".format(consts.Release_Install_Namespace), "--create-namespace",
                        "--output", "json"]
    # To set some other helm parameters through file
    cmd_helm_install.extend(["--set", "global.location={}".format(location)])
    cmd_helm_install.extend(["--set", "global.azureCloud={}".format(azure_cloud)])
    if https_proxy:
        cmd_helm_install.extend(["--set", "global.httpsProxy={}".format(https_proxy)])
    if http_proxy:
        cmd_helm_install.extend(["--set", "global.httpProxy={}".format(http_proxy)])
    if no_proxy:
        cmd_helm_install.extend(["--set", "global.noProxy={}".format(no_proxy)])
    if proxy_cert:
        cmd_helm_install.extend(["--set-file", "global.proxyCert={}".format(proxy_cert)])

    if kube_config:
        cmd_helm_install.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])

    # Change --timeout format for helm client to understand
    onboarding_timeout = onboarding_timeout + "s"
    cmd_helm_install.extend(["--wait", "--timeout", "{}".format(onboarding_timeout)])

    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        if ('forbidden' in error_helm_install.decode("ascii") or
                'timed out waiting for the condition' in error_helm_install.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_install.decode("ascii"),
                                fault_type=consts.Cluster_Diagnostic_Checks_Helm_Install_Failed_Fault_Type,
                                summary='Unable to install cluster diagnostic checks helm release')
        raise CLIInternalError("Unable to install cluster diagnostic checks helm release: "
                               + error_helm_install.decode("ascii"))


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
                    # If flag is 0 that means that process was terminated using the Keyboard Interrupt so adding that
                    # also to the text file
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
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type,
                                    summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to store the diagnoser results. Exception: \
            {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Result_Fault_Type,
                                summary="Error while storing the diagnoser results")

    return consts.Diagnostic_Check_Failed
