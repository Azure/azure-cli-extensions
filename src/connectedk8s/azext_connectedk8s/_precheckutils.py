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
from azext_connectedk8s._client_factory import _resource_client_factory, _resource_providers_client
import azext_connectedk8s._constants as consts
import azext_connectedk8s._utils as azext_utils
from kubernetes import client as kube_client
from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import CLIInternalError, ClientRequestError, ArgumentUsageError, ManualInterrupt, AzureResponseError, AzureInternalError, ValidationError
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


def check_preonboarding_inspector_container(corev1_api_instance, batchv1_api_instance, absolute_path, helm_client_location, kubectl_client_location, release_namespace, kube_config, kube_context, http_proxy, https_proxy, no_proxy, proxy_cert):
    try:
        # Setting DNS and Outbound Check as working
        dns_check = "Starting"
        outbound_connectivity_check = "Starting"
        # Executing the pre onboarding inspector job and fetching the logs obtained
        preonboarding_inspector_container_log = executing_preonboarding_inspector_job(corev1_api_instance, batchv1_api_instance, absolute_path, helm_client_location, kubectl_client_location, release_namespace, kube_config, kube_context, http_proxy, https_proxy, no_proxy, proxy_cert)
        # If preonboarding_inspector_container_log is not empty then only we will check for the results
        if(preonboarding_inspector_container_log is not None and preonboarding_inspector_container_log != ""):
            preonboarding_inspector_container_log_list = preonboarding_inspector_container_log.split("\n")
            preonboarding_inspector_container_log_list.pop(-1)
            dns_check_log = ""
            counter_container_logs = 1
            # For retrieving only preonboarding inspector logs from the inspector output
            for outputs in preonboarding_inspector_container_log_list:
                if consts.Outbound_Connectivity_Check_Result_String in outputs:
                    counter_container_logs = 1
                elif consts.DNS_Check_Result_String in outputs:
                    dns_check_log += outputs
                    counter_container_logs = 0
                elif counter_container_logs == 0:
                    dns_check_log += "  " + outputs
            dns_check = azext_utils.check_cluster_DNS(dns_check_log, True)
            outbound_connectivity_check = azext_utils.check_cluster_outbound_connectivity(preonboarding_inspector_container_log_list[-1], True)
        else:
            return consts.Diagnostic_Check_Incomplete

        # If both the check passed then we will return pre onboarding inspector checks Passed
        if(dns_check == consts.Diagnostic_Check_Passed and outbound_connectivity_check == consts.Diagnostic_Check_Passed):
            return consts.Diagnostic_Check_Passed
        # If any of the check remain Incomplete than we will return Incomplete
        elif(dns_check == consts.Diagnostic_Check_Incomplete or outbound_connectivity_check == consts.Diagnostic_Check_Incomplete):
            return consts.Diagnostic_Check_Incomplete
        else:
            return consts.Diagnostic_Check_Failed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to perform pre onboarding inspector container on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Pre_Onboarding_Inspector_Check_Failed_Fault_Type, summary="Error occured while performing the pre onboarding inspector container")

    return consts.Diagnostic_Check_Incomplete


def executing_preonboarding_inspector_job(corev1_api_instance, batchv1_api_instance, absolute_path, helm_client_location, kubectl_client_location, release_namespace, kube_config, kube_context, http_proxy, https_proxy, no_proxy, proxy_cert):
    job_name = "pre-onboarding-inspector-job"
    # Setting the log output as Empty
    preonboarding_inspector_container_log = ""

    cmd_helm_delete = [helm_client_location, "uninstall", "pre-onboarding-inspector"]
    if kube_config:
        cmd_helm_delete.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_delete.extend(["--context", kube_context])

    # To handle the user keyboard Interrupt
    try:
        # Executing the pre onboarding inspector job yaml
        config.load_kube_config(kube_config, kube_context)
        # Attempting deletion of pre onboarding inspector resources to handle the scenario if any stale resources are present
        response_kubectl_delete_helm = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        output_kubectl_delete_helm, error_kubectl_delete_helm = response_kubectl_delete_helm.communicate()
        # If any error occured while execution of delete command
        if (response_kubectl_delete_helm != 0):
            # Converting the string of multiple errors to list
            error_msg_list = error_kubectl_delete_helm.decode("ascii").split("\n")
            error_msg_list.pop(-1)
            valid_exception_list = []
            # Checking if any exception occured or not
            exception_occured_counter = 0
            for ind_errors in error_msg_list:
                if('not found' in ind_errors or 'deleted' in ind_errors):
                    pass
                else:
                    valid_exception_list.append(ind_errors)
                    exception_occured_counter = 1
            # If any exception occured we will print the exception and return
            if exception_occured_counter == 1:
                logger.warning("An error occured while installing the pre onboarding inspector helm release in the cluster. Exception:")
                telemetry.set_exception(exception=error_kubectl_delete_helm.decode("ascii"), fault_type=consts.Pre_Onboarding_Inspector_Failed_Fault_Type, summary="Error while executing pre onboarding inspector Job")
                return
        try:
            chart_path = azext_utils.get_chart_path(consts.Pre_Onboarding_Inspector_Job_Registry_Path, kube_config, kube_context, helm_client_location, True)

            helm_install_release(chart_path, http_proxy, https_proxy, no_proxy, proxy_cert, kube_config, kube_context, helm_client_location)
        # To handle the Exception that occured
        except Exception as e:
            logger.warning("An error occured while installing helm release of pre onboarding inspector in the cluster. Exception:")
            logger.warning(str(e))
            telemetry.set_exception(exception=e, fault_type=consts.Pre_Onboarding_Inspector_Helm_Release_Failed_Fault_Type, summary="Error while installing pre onboarding inspector helm release")
            # Deleting all the stale resources that got created
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        # Watching for pre onboarding inspector container to reach in completed stage
        w = watch.Watch()
        is_job_complete = False
        is_job_scheduled = False
        # To watch for changes in the pods states till it reach completed state or exit if it takes more than 180 seconds
        for event in w.stream(batchv1_api_instance.list_namespaced_job, namespace='default', label_selector="", timeout_seconds=60):
            try:
                # Checking if job get scheduled or not
                if event["object"].metadata.name == "pre-onboarding-inspector-job":
                    is_job_scheduled = True
                # Checking if job reached completed stage or not
                if event["object"].metadata.name == "pre-onboarding-inspector-job" and event["object"].status.conditions[0].type == "Complete":
                    is_job_complete = True
                    w.stop()
            except Exception as e:
                continue
            else:
                continue

        if (is_job_scheduled is False):
            logger.warning("Unable to schedule the pre onboarding inspector job in the kubernetes cluster. The possible reasons can be presence of a security policy or security context constraint (SCC) or it may happen becuase of lack of ResourceQuota.\n")
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        elif (is_job_scheduled is True and is_job_complete is False):
            logger.warning("Unable to finish the pre onboarding inspector job in the kubernetes cluster. The possible reasons can be presence of lack of Resources on the cluster.\n")
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        else:
            # Fetching the pre onboarding inspector Container logs
            all_pods = corev1_api_instance.list_namespaced_pod('default')
            # Traversing through all agents
            for each_pod in all_pods.items:
                # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
                pod_name = each_pod.metadata.name
                if(pod_name.startswith(job_name)):
                    # Creating a text file with the name of the container and adding that containers logs in it
                    preonboarding_inspector_container_log = corev1_api_instance.read_namespaced_pod_log(name=pod_name, container="pre-onboarding-inspector-container", namespace='default')
        # Clearing all the resources after fetching the pre onboarding inspector container logs
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to execute the pre onboarding inspector in the cluster. Exception: {}".format(str(e)) + "\n")
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        telemetry.set_exception(exception=e, fault_type=consts.Pre_Onboarding_Inspector_Failed_Fault_Type, summary="Error while executing Pre onboarding inspector Job")
        return

    return preonboarding_inspector_container_log


def helm_install_release(chart_path, http_proxy, https_proxy, no_proxy, proxy_cert, kube_config, kube_context, helm_client_location, onboarding_timeout="60"):
    cmd_helm_install = [helm_client_location, "upgrade", "--install", "pre-onboarding-inspector", chart_path]
    # To set some other helm parameters through file
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
        if ('forbidden' in error_helm_install.decode("ascii") or 'timed out waiting for the condition' in error_helm_install.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_install.decode("ascii"), fault_type=consts.Pre_Onboarding_Inspector_Install_HelmRelease_Fault_Type,
                                summary='Unable to install pre onboarding inspector helm release')
        raise CLIInternalError("Unable to install pre onboarding inspector helm release: " + error_helm_install.decode("ascii"))
