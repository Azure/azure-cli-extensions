# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from argparse import Namespace
from pydoc import cli
from kubernetes import client, config, watch, utils
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
from kubernetes import client as kube_client
from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import CLIInternalError, ClientRequestError, ArgumentUsageError, ManualInterrupt, AzureResponseError, AzureInternalError, ValidationError

logger = get_logger(__name__)

# pylint: disable=unused-argument, too-many-locals, too-many-branches, too-many-statements, line-too-long
# pylint: disable
def check_diagnoser_container(corev1_api_instance, batchv1_api_instance, absolute_path, helm_client_location, kubectl_client_location, release_namespace, kube_config, kube_context, http_proxy, https_proxy, no_proxy, proxy_cert):
    try:
        # Setting DNS and Outbound Check as working
        dns_check = "Starting"
        
        outbound_connectivity_check = "Starting"
        # Executing the Diagnoser job and fetching diagnoser logs obtained
        diagnoser_container_log = executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, absolute_path, helm_client_location, kubectl_client_location, release_namespace, kube_config, kube_context, http_proxy, https_proxy, no_proxy, proxy_cert)
        # print(diagnoser_container_log)
        # If diagnoser_container_log is not empty then only we will check for the results
        if(diagnoser_container_log is not None and diagnoser_container_log != ""):
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
            # print(dns_check_log)
            dns_check = check_cluster_DNS(dns_check_log)
            # print("after dns")
            # print(diagnoser_container_log_list[-1])
            outbound_connectivity_check= check_cluster_outbound_connectivity(diagnoser_container_log_list[-1])
        else:
            # print("if test cannot start")
            return consts.Diagnostic_Check_Incomplete

        # If both the check passed then we will return Diagnoser checks Passed
        if(dns_check == consts.Diagnostic_Check_Passed and outbound_connectivity_check == consts.Diagnostic_Check_Passed):
            # print("if 1")
            return consts.Diagnostic_Check_Passed
        # If any of the check remain Incomplete than we will return Incomplete
        elif(dns_check == consts.Diagnostic_Check_Incomplete or outbound_connectivity_check == consts.Diagnostic_Check_Incomplete):
            # print("if 2")
            if dns_check == consts.Diagnostic_Check_Incomplete :
                print("DNS DIDNT WORK")
            if outbound_connectivity_check == consts.Diagnostic_Check_Incomplete :
                print("DNS DIDNT WORK")
            return consts.Diagnostic_Check_Incomplete
        else:
            # print("if 3")
            return consts.Diagnostic_Check_Failed

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to perform diagnoser container check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Container_Check_Failed_Fault_Type, summary="Error occured while performing the diagnoser container checks")

    return consts.Diagnostic_Check_Incomplete
		
def executing_diagnoser_job(corev1_api_instance, batchv1_api_instance, absolute_path, helm_client_location, kubectl_client_location, release_namespace, kube_config, kube_context, http_proxy, https_proxy, no_proxy, proxy_cert):
    job_name = "connect-precheck-diagnoser-job"
    # yaml_file_path = os.path.join(absolute_path, "connect-precheck-diagnoser-file.yaml")
    # Setting the log output as Empty
    diagnoser_container_log = ""
	
    # cmd_delete_job = [kubectl_client_location, "delete", "-f", ""]
    # if kube_config:
    #     cmd_delete_job.extend(["--kubeconfig", kube_config])
    # if kube_context:
    #     cmd_delete_job.extend(["--context", kube_context])

    cmd_helm_delete = [helm_client_location, "uninstall", "connect-precheck-diagnoser"]
    if kube_config:
        cmd_helm_delete.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_delete.extend(["--context", kube_context])
	
    # print("deleteing connect-precheck helm release if present")
    # To handle the user keyboard Interrupt
    try:
        # Executing the diagnoser_job.yaml
        config.load_kube_config(kube_config, kube_context)
        k8s_client = client.ApiClient()
        # Attempting deletion of diagnoser resources to handle the scenario if any stale resources are present
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
                # print(valid_exception_list)
                logger.warning("An error occured while installing the connect precheck helm release in the cluster. Exception:")
                # telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Diagnoser_Job_Failed_Fault_Type, summary="Error while executing Diagnoser Job")
                return
        # print("installing connect-precheck helm release")
        try:
            chart_path = get_chart_path(consts.Connect_Precheck_Job_Registry_Path, kube_config, kube_context, helm_client_location)

            helm_install_release(chart_path, http_proxy, https_proxy, no_proxy, proxy_cert, kube_config,
                               kube_context, helm_client_location)
        # To handle the Exception that occured
        except Exception as e:
            # print("helm not installed and job not applied")
            logger.warning("An error occured while deploying the connect precheck diagnoser job in the cluster. Exception:")
            logger.warning(str(e))
            # telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Diagnoser_Job_Failed_Fault_Type, summary="Error while executing Diagnoser Job")
            # Deleting all the stale resources that got created
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        # Watching for diagnoser container to reach in completed stage
        w = watch.Watch()
        is_job_complete = False
        is_job_scheduled = False
        # To watch for changes in the pods states till it reach completed state or exit if it takes more than 180 seconds
        for event in w.stream(batchv1_api_instance.list_namespaced_job, namespace='default', label_selector="", timeout_seconds=90):
            try:
                # Checking if job get scheduled or not
                if event["object"].metadata.name == "connect-precheck-diagnoser-job":
                    # print("job scheduled")
                    is_job_scheduled = True
                # Checking if job reached completed stage or not
                if event["object"].metadata.name == "connect-precheck-diagnoser-job" and event["object"].status.conditions[0].type == "Complete":
                    # print("job complete")
                    is_job_complete = True
                    w.stop()
            except Exception as e:
               
                # print("exception")
                # print(e)
                continue
            else:
                # print("passed")
                continue
				
        if (is_job_scheduled is False):
            logger.warning("Unable to schedule the connect precheck diagnoser job in the kubernetes cluster. The possible reasons can be presence of a security policy or security context constraint (SCC) or it may happen becuase of lack of ResourceQuota.\n")
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        elif (is_job_scheduled is True and is_job_complete is False):
            # print("scheduled not completed")
            Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
            return
        else:
            # print("Scheduled and finished job")
            # Fetching the Diagnoser Container logs
            all_pods = corev1_api_instance.list_namespaced_pod('default')
            # Traversing through all agents
            for each_pod in all_pods.items:
                # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
                pod_name = each_pod.metadata.name
                if(pod_name.startswith(job_name)):
                    # print("inside making diagnoser container log")
                    # Creating a text file with the name of the container and adding that containers logs in it
                    diagnoser_container_log = corev1_api_instance.read_namespaced_pod_log(name=pod_name, container="connect-precheck-diagnoser-container", namespace='default')
                    print(diagnoser_container_log)
        # Clearing all the resources after fetching the diagnoser container logs
        # Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
		
    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while trying to execute the diagnoser job in the cluster. Exception: {}".format(str(e)) + "\n")
        Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        telemetry.set_exception(exception=e, fault_type=consts.Diagnoser_Job_Failed_Fault_Type, summary="Error while executing Diagnoser Job")
        return
		
    return diagnoser_container_log
		
def check_cluster_DNS(dns_check_log):

    try:
        if consts.DNS_Check_Result_String not in dns_check_log:
            # print("dns prob")
            return consts.Diagnostic_Check_Incomplete
        formatted_dns_log = dns_check_log.replace('\t', '')
        # Validating if DNS is working or not and displaying proper result
        if("NXDOMAIN" in formatted_dns_log or "connection timed out" in formatted_dns_log):
            logger.warning("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
            return consts.Diagnostic_Check_Failed
        else:
            return consts.Diagnostic_Check_Passed

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
            logger.warning("An exception has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Cluster_DNS_Check_Fault_Type, summary="Error occured while performing cluster DNS check")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing the DNS check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_DNS_Check_Fault_Type, summary="Error occured while performing cluster DNS check")

    return consts.Diagnostic_Check_Incomplete


def check_cluster_outbound_connectivity(outbound_connectivity_check_log):

    global diagnoser_output
    try:
        outbound_connectivity_response = outbound_connectivity_check_log[-1:-4:-1]
        outbound_connectivity_response = outbound_connectivity_response[::-1]
        if consts.Outbound_Connectivity_Check_Result_String not in outbound_connectivity_check_log:
            # print("outbound prob")
            return consts.Diagnostic_Check_Incomplete
        # Validating if outbound connectiivty is working or not and displaying proper result
        if(outbound_connectivity_response != "000"):
            return consts.Diagnostic_Check_Passed
        else:
            logger.warning("Error: We found an issue with outbound network connectivity from the cluster.\nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy parameters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server'.\nPlease ensure to meet the following network requirements 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#meet-network-requirements' \n")
            return consts.Diagnostic_Check_Failed

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
            logger.warning("An exception has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Outbound_Connectivity_Check_Fault_Type, summary="Error occured while performing outbound connectivity check in the cluster")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while performing the outbound connectivity check on the cluster. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Outbound_Connectivity_Check_Fault_Type, summary="Error occured while performing outbound connectivity check in the cluster")

    return consts.Diagnostic_Check_Incomplete

def get_chart_path(registry_path, kube_config, kube_context, helm_client_location):
    # print("getting chart path")
    # Pulling helm chart from registry
    os.environ['HELM_EXPERIMENTAL_OCI'] = '1'
    pull_helm_chart(registry_path, kube_config, kube_context, helm_client_location)

    # Exporting helm chart after cleanup
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'ConnectPrecheckCharts')
    try:
        if os.path.isdir(chart_export_path):
            # print("found the chart")
            shutil.rmtree(chart_export_path)
    except:
        logger.warning("Unable to cleanup the connect-precheck helm charts already present on the machine. In case of failure, please cleanup the directory '%s' and try again.", chart_export_path)
    export_helm_chart(registry_path, chart_export_path, kube_config, kube_context, helm_client_location)

    # Returning helm chart path
    helm_chart_path = os.path.join(chart_export_path, 'connect-precheck-diagnoser')
    chart_path = os.getenv('HELMCHART') if os.getenv('HELMCHART') else helm_chart_path
    return chart_path

def pull_helm_chart(registry_path, kube_config, kube_context, helm_client_location):
    # print("pulling helm chart")
    cmd_helm_chart_pull = [helm_client_location, "chart", "pull", registry_path]
    # cmd_helm_chart_pull = [helm_client_location, "fetch", registry_path]
    # cmd_helm_chart_pull.extend(["--version", consts.Connect_Precheck_Job_Version])
    if kube_config:
        cmd_helm_chart_pull.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_chart_pull.extend(["--kube-context", kube_context])
    response_helm_chart_pull = subprocess.Popen(cmd_helm_chart_pull, stdout=PIPE, stderr=PIPE)
    _, error_helm_chart_pull = response_helm_chart_pull.communicate()
    if response_helm_chart_pull.returncode != 0:
        telemetry.set_exception(exception=error_helm_chart_pull.decode("ascii"), fault_type=consts.Pull_HelmChart_Fault_Type,
                                summary='Unable to pull helm chart from the registry')
        raise CLIInternalError("Unable to pull helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_pull.decode("ascii"))


def export_helm_chart(registry_path, chart_export_path, kube_config, kube_context, helm_client_location):
    # print("export chart ")
    cmd_helm_chart_export = [helm_client_location, "chart", "export", registry_path, "--destination", chart_export_path]
    if kube_config:
        cmd_helm_chart_export.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_chart_export.extend(["--kube-context", kube_context])
    response_helm_chart_export = subprocess.Popen(cmd_helm_chart_export, stdout=PIPE, stderr=PIPE)
    _, error_helm_chart_export = response_helm_chart_export.communicate()
    if response_helm_chart_export.returncode != 0:
        telemetry.set_exception(exception=error_helm_chart_export.decode("ascii"), fault_type=consts.Export_HelmChart_Fault_Type,
                                summary='Unable to export helm chart from the registry')
        raise CLIInternalError("Unable to export helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_export.decode("ascii"))


def helm_install_release(chart_path, http_proxy, https_proxy, no_proxy, proxy_cert,
                         kube_config, kube_context, helm_client_location, onboarding_timeout="200"):
    # print("installing release")
    # print(chart_path)
    cmd_helm_install = [helm_client_location, "upgrade", "--install", "connect-precheck-diagnoser", chart_path , "--debug"]
    # print("before cmd helm install")
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
    
    # if not no_wait:
    #     # Change --timeout format for helm client to understand
    #     onboarding_timeout = onboarding_timeout + "s"
    #     cmd_helm_install.extend(["--wait", "--timeout", "{}".format(onboarding_timeout)])    
    
    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        if ('forbidden' in error_helm_install.decode("ascii") or 'timed out waiting for the condition' in error_helm_install.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_install.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        logger.warning("Please check if the azure-arc namespace was deployed and run 'kubectl get pods -n azure-arc' to check if all the pods are in running state. A possible cause for pods stuck in pending state could be insufficient resources on the kubernetes cluster to onboard to arc.")
        raise CLIInternalError("Unable to install helm release: " + error_helm_install.decode("ascii"))
