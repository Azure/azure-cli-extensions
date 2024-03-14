# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import os
import shutil
from packaging import version
import subprocess
from subprocess import Popen, PIPE
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
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
from azext_connectedk8s._client_factory import resource_providers_client, cf_resource_groups
import azext_connectedk8s._constants as consts
from kubernetes import client as kube_client
from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import CLIInternalError, ClientRequestError, ArgumentUsageError, ManualInterrupt, AzureResponseError, AzureInternalError, ValidationError

logger = get_logger(__name__)

# pylint: disable=line-too-long
# pylint: disable=bare-except


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = consts.DEFAULT_REQUEST_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def validate_location(cmd, location):
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID') if os.getenv('AZURE_ACCESS_TOKEN') else get_subscription_id(cmd.cli_ctx)
    rp_locations = []
    resourceClient = resource_providers_client(cmd.cli_ctx, subscription_id=subscription_id)
    try:
        providerDetails = resourceClient.get('Microsoft.Kubernetes')
    except Exception as e:  # pylint: disable=broad-except
        arm_exception_handler(e, consts.Get_ResourceProvider_Fault_Type, 'Failed to fetch resource provider details')
    for resourceTypes in providerDetails.resource_types:
        if resourceTypes.resource_type == 'connectedClusters':
            rp_locations = [location.replace(" ", "").lower() for location in resourceTypes.locations]
            if location.lower() not in rp_locations:
                telemetry.set_exception(exception='Location not supported', fault_type=consts.Invalid_Location_Fault_Type,
                                        summary='Provided location is not supported for creating connected clusters')
                raise ArgumentUsageError("Connected cluster resource creation is supported only in the following locations: " +
                                         ', '.join(map(str, rp_locations)), recommendation="Use the --location flag to specify one of these locations.")
            break


def validate_custom_token(cmd, resource_group_name, location):
    if os.getenv('AZURE_ACCESS_TOKEN'):
        if os.getenv('AZURE_SUBSCRIPTION_ID') is None:
            telemetry.set_exception(exception='Required environment variable SubscriptionId not set', fault_type=consts.Custom_Token_Environments_Fault_Type_Sub_Id,
                                    summary='Required environment variable for SubscriptionId not set')
            raise ValidationError("Environment variable 'AZURE_SUBSCRIPTION_ID' should be set when custom access token is enabled.")
        if os.getenv('AZURE_TENANT_ID') is None:
            telemetry.set_exception(exception='Required environment variable for TenantId not set', fault_type=consts.Custom_Token_Environments_Fault_Type_Tenant_Id,
                                    summary='Required environment variable for TenantId not set')
            raise ValidationError("Environment variable 'AZURE_TENANT_ID' should be set when custom access token is enabled.")
        if location is None:
            try:
                resource_client = cf_resource_groups(cmd.cli_ctx, os.getenv('AZURE_SUBSCRIPTION_ID'))
                rg = resource_client.get(resource_group_name)
                location = rg.location
            except Exception as ex:
                telemetry.set_exception(exception=ex, fault_type=consts.Location_Fetch_Fault_Type,
                                        summary='Unable to fetch location from resource group')
                raise ValidationError("Unable to fetch location from resource group: '{}'".format(str(ex)))
        return True, location
    return False, location


def get_chart_path(registry_path, kube_config, kube_context, helm_client_location, chart_folder_name='AzureArcCharts', chart_name='azure-arc-k8sagents', new_path=True):
    # Exporting Helm chart
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', chart_folder_name)
    try:
        if os.path.isdir(chart_export_path):
            shutil.rmtree(chart_export_path)
    except:
        logger.warning("Unable to cleanup the {} already present on the machine. In case of failure, please cleanup the directory '{}' and try again.".format(chart_folder_name, chart_export_path))

    pull_helm_chart(registry_path, chart_export_path, kube_config, kube_context, helm_client_location, new_path, chart_name)

    # Returning helm chart path
    helm_chart_path = os.path.join(chart_export_path, chart_name)
    if chart_folder_name == consts.Pre_Onboarding_Helm_Charts_Folder_Name:
        chart_path = helm_chart_path
    else:
        chart_path = os.getenv('HELMCHART') if os.getenv('HELMCHART') else helm_chart_path

    return chart_path


def pull_helm_chart(registry_path, chart_export_path, kube_config, kube_context, helm_client_location, new_path, chart_name='azure-arc-k8sagents', retry_count=5, retry_delay=3):
    chart_url = registry_path.split(':')[0]
    chart_version = registry_path.split(':')[1]

    if new_path:
        # Version check for stable release train (chart_version will be in X.Y.Z format as opposed to X.Y.Z-NONSTABLE)
        if '-' not in chart_version and (version.parse(chart_version) < version.parse("1.14.0")):
            error_summary = "This CLI version does not support upgrading to Agents versions older than v1.14"
            telemetry.set_exception(exception='Operation not supported on older Agents', fault_type=consts.Operation_Not_Supported_Fault_Type, summary=error_summary)
            raise ClientRequestError(error_summary, recommendation="Please select an agent-version >= v1.14 to upgrade to using 'az connectedk8s upgrade -g <rg_name> -n <cluster_name> --agent-version <at-least-1.14>'.")

        base_path = os.path.dirname(chart_url)
        image_name = os.path.basename(chart_url)
        chart_url = base_path + '/v2/' + image_name

    cmd_helm_chart_pull = [helm_client_location, "pull", "oci://" + chart_url, "--untar", "--untardir", chart_export_path, "--version", chart_version]
    if kube_config:
        cmd_helm_chart_pull.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_chart_pull.extend(["--kube-context", kube_context])
    for i in range(retry_count):
        response_helm_chart_pull = subprocess.Popen(cmd_helm_chart_pull, stdout=PIPE, stderr=PIPE)
        _, error_helm_chart_pull = response_helm_chart_pull.communicate()
        if response_helm_chart_pull.returncode != 0:
            if i == retry_count - 1:
                telemetry.set_exception(exception=error_helm_chart_pull.decode("ascii"), fault_type=consts.Pull_HelmChart_Fault_Type,
                                        summary="Unable to pull {} helm charts from the registry".format(chart_name))
                raise CLIInternalError("Unable to pull {} helm chart from the registry '{}': ".format(chart_name, registry_path) + error_helm_chart_pull.decode("ascii"))
            time.sleep(retry_delay)
        else:
            break


def save_cluster_diagnostic_checks_pod_description(corev1_api_instance, batchv1_api_instance, helm_client_location, kubectl_client_location, kube_config, kube_context, filepath_with_timestamp, storage_space_available):
    try:
        job_name = "cluster-diagnostic-checks-job"
        all_pods = corev1_api_instance.list_namespaced_pod('azure-arc-release')
        # Traversing through all agents
        for each_pod in all_pods.items:
            # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
            pod_name = each_pod.metadata.name
            if (pod_name.startswith(job_name)):
                describe_job_pod = [kubectl_client_location, "describe", "pod", pod_name, "-n", "azure-arc-release"]
                if kube_config:
                    describe_job_pod.extend(["--kubeconfig", kube_config])
                if kube_context:
                    describe_job_pod.extend(["--context", kube_context])
                response_describe_job_pod = Popen(describe_job_pod, stdout=PIPE, stderr=PIPE)
                output_describe_job_pod, error_describe_job_pod = response_describe_job_pod.communicate()
                if (response_describe_job_pod.returncode == 0):
                    pod_description = output_describe_job_pod.decode()
                    if storage_space_available:
                        dns_check_path = os.path.join(filepath_with_timestamp, "cluster_diagnostic_checks_pod_description.txt")
                        with open(dns_check_path, 'w+') as f:
                            f.write(pod_description)
                else:
                    telemetry.set_exception(exception=error_describe_job_pod.decode("ascii"), fault_type=consts.Cluster_Diagnostic_Checks_Pod_Description_Save_Failed, summary="Failed to save cluster diagnostic checks pod description in the local machine")
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(exception=e, fault_type=consts.No_Storage_Space_Available_Fault_Type, summary="No space left on device")
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False, onerror=None)
        else:
            logger.warning("An exception has occured while saving the cluster diagnostic checks pod description in the local machine. Exception: {}".format(str(e)) + "\n")
            telemetry.set_exception(exception=e, fault_type=consts.Cluster_Diagnostic_Checks_Pod_Description_Save_Failed, summary="Error occured while saving the cluster diagnostic checks pod description in the local machine")

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.warning("An exception has occured while saving the cluster diagnostic checks pod description in the local machine. Exception: {}".format(str(e)) + "\n")
        telemetry.set_exception(exception=e, fault_type=consts.Cluster_Diagnostic_Checks_Pod_Description_Save_Failed, summary="Error occured while saving the cluster diagnostic checks pod description in the local machine")


def check_cluster_DNS(dns_check_log, filepath_with_timestamp, storage_space_available, diagnoser_output):

    try:
        if consts.DNS_Check_Result_String not in dns_check_log:
            return consts.Diagnostic_Check_Incomplete, storage_space_available
        formatted_dns_log = dns_check_log.replace('\t', '')
        # Validating if DNS is working or not and displaying proper result
        if ("NXDOMAIN" in formatted_dns_log or "connection timed out" in formatted_dns_log):
            logger.warning("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
            diagnoser_output.append("Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n")
            if storage_space_available:
                dns_check_path = os.path.join(filepath_with_timestamp, consts.DNS_Check)
                with open(dns_check_path, 'w+') as dns:
                    dns.write(formatted_dns_log + "\nWe found an issue with the DNS resolution on your cluster.")
            telemetry.set_exception(exception='DNS resolution check failed in the cluster', fault_type=consts.DNS_Check_Failed, summary="DNS check failed in the cluster")
            return consts.Diagnostic_Check_Failed, storage_space_available
        else:
            if storage_space_available:
                dns_check_path = os.path.join(filepath_with_timestamp, consts.DNS_Check)
                with open(dns_check_path, 'w+') as dns:
                    dns.write(formatted_dns_log + "\nCluster DNS check passed successfully.")
            return consts.Diagnostic_Check_Passed, storage_space_available

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

    return consts.Diagnostic_Check_Incomplete, storage_space_available


def check_cluster_outbound_connectivity(outbound_connectivity_check_log, filepath_with_timestamp, storage_space_available, diagnoser_output, outbound_connectivity_check_for='pre-onboarding-inspector'):

    try:
        if outbound_connectivity_check_for == 'pre-onboarding-inspector':
            if consts.Outbound_Connectivity_Check_Result_String not in outbound_connectivity_check_log:
                return consts.Diagnostic_Check_Incomplete, storage_space_available

            Outbound_Connectivity_Log_For_Cluster_Connect = outbound_connectivity_check_log.split('  ')[0]
            # extracting the endpoints for cluster connect feature
            Cluster_Connect_Precheck_Endpoint_Url = Outbound_Connectivity_Log_For_Cluster_Connect.split(" : ")[1]
            # extracting the obo endpoint response code from outbound connectivity check
            Cluster_Connect_Precheck_Endpoint_response_code = Outbound_Connectivity_Log_For_Cluster_Connect.split(" : ")[2]

            if (Cluster_Connect_Precheck_Endpoint_response_code != "000"):
                if storage_space_available:
                    cluster_connect_outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, consts.Outbound_Network_Connectivity_Check_for_cluster_connect)
                    with open(cluster_connect_outbound_connectivity_check_path, 'w+') as outbound:
                        outbound.write("Response code " + Cluster_Connect_Precheck_Endpoint_response_code + "\nOutbound network connectivity check to cluster connect precheck endpoints passed successfully.")
            else:
                logger.warning("The outbound network connectivity check has failed for the endpoint - " + Cluster_Connect_Precheck_Endpoint_Url + "\nThis will affect the \"cluster-connect\" feature. If you are planning to use \"cluster-connect\" functionality , please ensure outbound connectivity to the above endpoint.\n")
                telemetry.set_user_fault()
                telemetry.set_exception(exception='Outbound network connectivity check failed for the Cluster Connect endpoint', fault_type=consts.Outbound_Connectivity_Check_Failed_For_Cluster_Connect, summary="Outbound network connectivity check failed for the Cluster Connect precheck endpoint")
                if storage_space_available:
                    cluster_connect_outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, consts.Outbound_Network_Connectivity_Check_for_cluster_connect)
                    with open(cluster_connect_outbound_connectivity_check_path, 'w+') as outbound:
                        outbound.write("Response code " + Cluster_Connect_Precheck_Endpoint_response_code + "\nOutbound connectivity failed for the endpoint:" + Cluster_Connect_Precheck_Endpoint_Url + " ,this is an optional endpoint needed for cluster-connect feature.")

            Onboarding_Precheck_Endpoint_outbound_connectivity_response = outbound_connectivity_check_log[-1:-4:-1]
            Onboarding_Precheck_Endpoint_outbound_connectivity_response = Onboarding_Precheck_Endpoint_outbound_connectivity_response[::-1]

            # Validating if outbound connectiivty is working or not and displaying proper result
            if (Onboarding_Precheck_Endpoint_outbound_connectivity_response != "000"):
                if storage_space_available:
                    outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, consts.Outbound_Network_Connectivity_Check_for_onboarding)
                    with open(outbound_connectivity_check_path, 'w+') as outbound:
                        outbound.write("Response code " + Onboarding_Precheck_Endpoint_outbound_connectivity_response + "\nOutbound network connectivity check to the onboarding precheck endpoint passed successfully.")
                return consts.Diagnostic_Check_Passed, storage_space_available
            else:
                outbound_connectivity_failed_warning_message = "Error: We found an issue with outbound network connectivity from the cluster to the endpoints required for onboarding.\nPlease ensure to meet the following network requirements 'https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/network-requirements?tabs=azure-cloud' \nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy parameters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server' \n"
                logger.warning(outbound_connectivity_failed_warning_message)
                telemetry.set_user_fault()
                diagnoser_output.append(outbound_connectivity_failed_warning_message)
                if storage_space_available:
                    outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, consts.Outbound_Network_Connectivity_Check_for_onboarding)
                    with open(outbound_connectivity_check_path, 'w+') as outbound:
                        outbound.write("Response code " + Onboarding_Precheck_Endpoint_outbound_connectivity_response + "\nWe found an issue with Outbound network connectivity from the cluster required for onboarding.")
                telemetry.set_exception(exception='Outbound network connectivity check failed for onboarding', fault_type=consts.Outbound_Connectivity_Check_Failed_For_Onboarding, summary="Outbound network connectivity check for onboarding failed in the cluster")
                return consts.Diagnostic_Check_Failed, storage_space_available

        elif outbound_connectivity_check_for == 'troubleshoot':
            outbound_connectivity_response = outbound_connectivity_check_log[-1:-4:-1]
            outbound_connectivity_response = outbound_connectivity_response[::-1]
            if consts.Outbound_Connectivity_Check_Result_String not in outbound_connectivity_check_log:
                return consts.Diagnostic_Check_Incomplete, storage_space_available

            if (outbound_connectivity_response != "000"):
                if storage_space_available:
                    outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, consts.Outbound_Network_Connectivity_Check)
                    with open(outbound_connectivity_check_path, 'w+') as outbound:
                        outbound.write("Response code " + outbound_connectivity_response + "\nOutbound network connectivity check passed successfully.")
                return consts.Diagnostic_Check_Passed, storage_space_available
            else:
                outbound_connectivity_failed_warning_message = "Error: We found an issue with outbound network connectivity from the cluster.\nPlease ensure to meet the following network requirements 'https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/network-requirements?tabs=azure-cloud' \nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy parameters during the onboarding of your cluster.\nFor more details visit 'https://docs.microsoft.com/en-us/azure/azure-arc/kubernetes/quickstart-connect-cluster?tabs=azure-cli#connect-using-an-outbound-proxy-server' \n"
                logger.warning(outbound_connectivity_failed_warning_message)
                diagnoser_output.append(outbound_connectivity_failed_warning_message)
                if storage_space_available:
                    outbound_connectivity_check_path = os.path.join(filepath_with_timestamp, consts.Outbound_Network_Connectivity_Check)
                    with open(outbound_connectivity_check_path, 'w+') as outbound:
                        outbound.write("Response code " + outbound_connectivity_response + "\nWe found an issue with Outbound network connectivity from the cluster.")
                telemetry.set_exception(exception='Outbound network connectivity check failed', fault_type=consts.Outbound_Connectivity_Check_Failed, summary="Outbound network connectivity check failed in the cluster")
                return consts.Diagnostic_Check_Failed, storage_space_available

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

    return consts.Diagnostic_Check_Incomplete, storage_space_available


def create_folder_diagnosticlogs(time_stamp, folder_name):

    try:
        # Fetching path to user directory to create the arc diagnostic folder
        home_dir = os.path.expanduser('~')
        filepath = os.path.join(home_dir, '.azure', folder_name)
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


def add_helm_repo(kube_config, kube_context, helm_client_location):
    repo_name = os.getenv('HELMREPONAME')
    repo_url = os.getenv('HELMREPOURL')
    cmd_helm_repo = [helm_client_location, "repo", "add", repo_name, repo_url]
    if kube_config:
        cmd_helm_repo.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_repo.extend(["--kube-context", kube_context])
    response_helm_repo = Popen(cmd_helm_repo, stdout=PIPE, stderr=PIPE)
    _, error_helm_repo = response_helm_repo.communicate()
    if response_helm_repo.returncode != 0:
        telemetry.set_exception(exception=error_helm_repo.decode("ascii"), fault_type=consts.Add_HelmRepo_Fault_Type,
                                summary='Failed to add helm repository')
        raise CLIInternalError("Unable to add repository {} to helm: ".format(repo_url) + error_helm_repo.decode("ascii"))


def get_helm_registry(cmd, config_dp_endpoint, release_train_custom=None):
    # Setting uri
    api_version = "2019-11-01-preview"
    chart_location_url_segment = "azure-arc-k8sagents/GetLatestHelmPackagePath?api-version={}".format(api_version)
    release_train = os.getenv('RELEASETRAIN') if os.getenv('RELEASETRAIN') else 'stable'
    chart_location_url = "{}/{}".format(config_dp_endpoint, chart_location_url_segment)
    if release_train_custom:
        release_train = release_train_custom
    uri_parameters = ["releaseTrain={}".format(release_train)]
    resource = cmd.cli_ctx.cloud.endpoints.active_directory_resource_id
    headers = None
    if os.getenv('AZURE_ACCESS_TOKEN'):
        headers = ["Authorization=Bearer {}".format(os.getenv('AZURE_ACCESS_TOKEN'))]
    # Sending request with retries
    r = send_request_with_retries(cmd.cli_ctx, 'post', chart_location_url, headers=headers, fault_type=consts.Get_HelmRegistery_Path_Fault_Type, summary='Error while fetching helm chart registry path', uri_parameters=uri_parameters, resource=resource)
    if r.content:
        try:
            return r.json().get('repositoryPath')
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                    summary='Error while fetching helm chart registry path')
            raise CLIInternalError("Error while fetching helm chart registry path from JSON response: " + str(e))
    else:
        telemetry.set_exception(exception='No content in response', fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                                summary='No content in acr path response')
        raise CLIInternalError("No content was found in helm registry path response.")


def send_request_with_retries(cli_ctx, method, url, headers, fault_type, summary, uri_parameters=None, resource=None, retry_count=5, retry_delay=3):
    for i in range(retry_count):
        try:
            response = send_raw_request(cli_ctx, method, url, headers=headers, uri_parameters=uri_parameters, resource=resource)
            return response
        except Exception as e:
            if i == retry_count - 1:
                telemetry.set_exception(exception=e, fault_type=fault_type, summary=summary)
                raise CLIInternalError("Error while fetching helm chart registry path: " + str(e))
            time.sleep(retry_delay)


def arm_exception_handler(ex, fault_type, summary, return_if_not_found=False):
    if isinstance(ex, AuthenticationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Authentication error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, TokenExpiredError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Token expiration error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpOperationError):
        status_code = ex.response.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError("Http operation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError("Http operation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, MSRestValidationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError("Validation error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, HttpResponseError):
        status_code = ex.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError("Http response error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))
        raise AzureResponseError("Http response error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))

    if isinstance(ex, ResourceNotFoundError) and return_if_not_found:
        return

    telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
    raise ClientRequestError("Error occured while making ARM request: " + str(ex) + "\nSummary: {}".format(summary))


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


def validate_infrastructure_type(infra):
    for s in consts.Infrastructure_Enum_Values[1:]:  # First value is "auto"
        if s.lower() == infra.lower():
            return s
    return None


def get_values_file():
    values_file = os.getenv('HELMVALUESPATH')
    if (values_file is not None) and (os.path.isfile(values_file)):
        logger.warning("Values files detected. Reading additional helm parameters from same.")
        # trimming required for windows os
        if (values_file.startswith("'") or values_file.startswith('"')):
            values_file = values_file[1:]
        if (values_file.endswith("'") or values_file.endswith('"')):
            values_file = values_file[:-1]
        return values_file
    return None


def ensure_namespace_cleanup():
    api_instance = kube_client.CoreV1Api()
    timeout = time.time() + 180
    while True:
        if time.time() > timeout:
            telemetry.set_user_fault()
            logger.warning("Namespace 'azure-arc' still in terminating state. Please ensure that you delete the 'azure-arc' namespace before onboarding the cluster again.")
            return
        try:
            api_response = api_instance.list_namespace(field_selector='metadata.name=azure-arc')
            if not api_response.items:
                return
            time.sleep(5)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error while retrieving namespace information: " + str(e))
            kubernetes_exception_handler(e, consts.Get_Kubernetes_Namespace_Fault_Type, 'Unable to fetch kubernetes namespace',
                                         raise_error=False)


def delete_arc_agents(release_namespace, kube_config, kube_context, helm_client_location, is_arm64_cluster=False, no_hooks=False):
    if (no_hooks):
        cmd_helm_delete = [helm_client_location, "delete", "azure-arc", "--namespace", release_namespace, "--no-hooks"]
    else:
        cmd_helm_delete = [helm_client_location, "delete", "azure-arc", "--namespace", release_namespace]
    if is_arm64_cluster:
        cmd_helm_delete.extend(["--timeout", "15m"])
    if kube_config:
        cmd_helm_delete.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])
    response_helm_delete = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
    _, error_helm_delete = response_helm_delete.communicate()
    if response_helm_delete.returncode != 0:
        if 'forbidden' in error_helm_delete.decode("ascii") or 'Error: warning: Hook pre-delete' in error_helm_delete.decode("ascii") or 'Error: timed out waiting for the condition' in error_helm_delete.decode("ascii"):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_delete.decode("ascii"), fault_type=consts.Delete_HelmRelease_Fault_Type,
                                summary='Unable to delete helm release')
        raise CLIInternalError("Error occured while cleaning up arc agents. " +
                               "Helm release deletion failed: " + error_helm_delete.decode("ascii") +
                               " Please run 'helm delete azure-arc --namespace {}' to ensure that the release is deleted.".format(release_namespace))
    ensure_namespace_cleanup()
    # Cleanup azure-arc-release NS if present (created during helm installation)
    cleanup_release_install_namespace_if_exists()


def cleanup_release_install_namespace_if_exists():
    api_instance = kube_client.CoreV1Api()
    try:
        api_instance.read_namespace(consts.Release_Install_Namespace)
    except Exception as ex:
        if ex.status == 404:
            # Nothing to delete, exiting here
            return
        else:
            kubernetes_exception_handler(ex, consts.Get_Kubernetes_Helm_Release_Namespace_Fault_Type, error_message='Unable to fetch details about existense of kubernetes namespace: {}'.format(consts.Release_Install_Namespace), summary='Unable to fetch kubernetes namespace: {}'.format(consts.Release_Install_Namespace))

    # If namespace exists, delete it
    try:
        api_instance.delete_namespace(consts.Release_Install_Namespace)
    except Exception as ex:
        kubernetes_exception_handler(ex, consts.Delete_Kubernetes_Helm_Release_Namespace_Fault_Type, error_message='Unable to clean-up kubernetes namespace: {}'.format(consts.Release_Install_Namespace), summary='Unable to delete kubernetes namespace: {}'.format(consts.Release_Install_Namespace))


# DO NOT use this method for re-put scenarios. This method involves new NS creation for helm release. For re-put scenarios, brownfield scenario needs to be handled where helm release still stays in default NS
def helm_install_release(resource_manager, chart_path, subscription_id, kubernetes_distro, kubernetes_infra, resource_group_name,
                         cluster_name, location, onboarding_tenant_id, http_proxy, https_proxy, no_proxy, proxy_cert, private_key_pem,
                         kube_config, kube_context, no_wait, values_file, cloud_name, disable_auto_upgrade, enable_custom_locations,
                         custom_locations_oid, helm_client_location, enable_private_link, arm_metadata, onboarding_timeout="600",
                         container_log_path=None):

    cmd_helm_install = [helm_client_location, "upgrade", "--install", "azure-arc", chart_path,
                        "--set", "global.subscriptionId={}".format(subscription_id),
                        "--set", "global.kubernetesDistro={}".format(kubernetes_distro),
                        "--set", "global.kubernetesInfra={}".format(kubernetes_infra),
                        "--set", "global.resourceGroupName={}".format(resource_group_name),
                        "--set", "global.resourceName={}".format(cluster_name),
                        "--set", "global.location={}".format(location),
                        "--set", "global.tenantId={}".format(onboarding_tenant_id),
                        "--set", "global.onboardingPrivateKey={}".format(private_key_pem),
                        "--set", "systemDefaultValues.spnOnboarding=false",
                        "--set", "global.azureEnvironment={}".format(cloud_name),
                        "--set", "systemDefaultValues.clusterconnect-agent.enabled=true",
                        "--namespace", "{}".format(consts.Release_Install_Namespace),
                        "--create-namespace",
                        "--output", "json"]

    # Special configurations from 2022-09-01 ARM metadata.
    if "dataplaneEndpoints" in arm_metadata:
        if "arcConfigEndpoint" in arm_metadata["dataplaneEndpoints"]:
            notification_endpoint = arm_metadata["dataplaneEndpoints"]["arcGlobalNotificationServiceEndpoint"]
            config_endpoint = arm_metadata["dataplaneEndpoints"]["arcConfigEndpoint"]
            his_endpoint = arm_metadata["dataplaneEndpoints"]["arcHybridIdentityServiceEndpoint"]
            if his_endpoint[-1] != "/":
                his_endpoint = his_endpoint + "/"
            his_endpoint = his_endpoint + f"discovery?location={location}&api-version=1.0-preview"
            relay_endpoint = arm_metadata["suffixes"]["relayEndpointSuffix"]
            active_directory = arm_metadata["authentication"]["loginEndpoint"]
            cmd_helm_install.extend(
                [
                    "--set", "systemDefaultValues.azureResourceManagerEndpoint={}".format(resource_manager),
                    "--set", "systemDefaultValues.azureArcAgents.config_dp_endpoint_override={}".format(config_endpoint),
                    "--set", "systemDefaultValues.clusterconnect-agent.notification_dp_endpoint_override={}".format(notification_endpoint),
                    "--set", "systemDefaultValues.clusterconnect-agent.relay_endpoint_suffix_override={}".format(relay_endpoint),
                    "--set", "systemDefaultValues.clusteridentityoperator.his_endpoint_override={}".format(his_endpoint),
                    "--set", "systemDefaultValues.activeDirectoryEndpoint={}".format(active_directory)
                ]
            )
        else:
            logger.debug("'arcConfigEndpoint' doesn't exist under 'dataplaneEndpoints' in the ARM metadata.")

    # Add custom-locations related params
    if enable_custom_locations and not enable_private_link:
        cmd_helm_install.extend(["--set", "systemDefaultValues.customLocations.enabled=true"])
        cmd_helm_install.extend(["--set", "systemDefaultValues.customLocations.oid={}".format(custom_locations_oid)])
    # Disable cluster connect if private link is enabled
    if enable_private_link is True:
        cmd_helm_install.extend(["--set", "systemDefaultValues.clusterconnect-agent.enabled=false"])
    # To set some other helm parameters through file
    if values_file:
        cmd_helm_install.extend(["-f", values_file])
    if disable_auto_upgrade:
        cmd_helm_install.extend(["--set", "systemDefaultValues.azureArcAgents.autoUpdate={}".format("false")])
    if https_proxy:
        cmd_helm_install.extend(["--set", "global.httpsProxy={}".format(https_proxy)])
    if http_proxy:
        cmd_helm_install.extend(["--set", "global.httpProxy={}".format(http_proxy)])
    if no_proxy:
        cmd_helm_install.extend(["--set", "global.noProxy={}".format(no_proxy)])
    if proxy_cert:
        cmd_helm_install.extend(["--set-file", "global.proxyCert={}".format(proxy_cert)])
        cmd_helm_install.extend(["--set", "global.isCustomCert={}".format(True)])
    if https_proxy or http_proxy or no_proxy:
        cmd_helm_install.extend(["--set", "global.isProxyEnabled={}".format(True)])
    if container_log_path is not None:
        cmd_helm_install.extend(["--set", "systemDefaultValues.fluent-bit.containerLogPath={}".format(container_log_path)])
    if kube_config:
        cmd_helm_install.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])
    if not no_wait:
        # Change --timeout format for helm client to understand
        onboarding_timeout = onboarding_timeout + "s"
        cmd_helm_install.extend(["--wait", "--timeout", "{}".format(onboarding_timeout)])
    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        helm_install_error_message = error_helm_install.decode("ascii")
        if any(message in helm_install_error_message for message in consts.Helm_Install_Release_Userfault_Messages):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=helm_install_error_message, fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        logger.warning("Please check if the azure-arc namespace was deployed and run 'kubectl get pods -n azure-arc' to check if all the pods are in running state. A possible cause for pods stuck in pending state could be insufficient resources on the kubernetes cluster to onboard to arc.")
        raise CLIInternalError("Unable to install helm release: " + error_helm_install.decode("ascii"))


def get_release_namespace(kube_config, kube_context, helm_client_location, release_name='azure-arc'):
    cmd_helm_release = [helm_client_location, "list", "-a", "--all-namespaces", "--output", "json"]
    if kube_config:
        cmd_helm_release.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_release.extend(["--kube-context", kube_context])
    response_helm_release = Popen(cmd_helm_release, stdout=PIPE, stderr=PIPE)
    output_helm_release, error_helm_release = response_helm_release.communicate()
    if response_helm_release.returncode != 0:
        if 'forbidden' in error_helm_release.decode("ascii") or "Kubernetes cluster unreachable" in error_helm_release.decode("ascii"):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_release.decode("ascii"), fault_type=consts.List_HelmRelease_Fault_Type,
                                summary='Unable to list helm release')
        raise CLIInternalError("Helm list release failed: " + error_helm_release.decode("ascii"))
    output_helm_release = output_helm_release.decode("ascii")
    try:
        output_helm_release = json.loads(output_helm_release)
    except json.decoder.JSONDecodeError:
        return None
    for release in output_helm_release:
        if release['name'] == release_name:
            return release['namespace']
    return None


def flatten(dd, separator='.', prefix=''):
    try:
        if isinstance(dd, dict):
            return {prefix + separator + k if prefix else k: v for kk, vv in dd.items() for k, v in flatten(vv, separator, kk).items()}
        else:
            return {prefix: dd}
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Error_Flattening_User_Supplied_Value_Dict,
                                summary='Error while flattening the user supplied helm values dict')
        raise CLIInternalError("Error while flattening the user supplied helm values dict")


def check_features_to_update(features_to_update):
    update_cluster_connect, update_azure_rbac, update_cl = False, False, False
    for feature in features_to_update:
        if feature == "cluster-connect":
            update_cluster_connect = True
        elif feature == "azure-rbac":
            update_azure_rbac = True
        elif feature == "custom-locations":
            update_cl = True
    return update_cluster_connect, update_azure_rbac, update_cl


def user_confirmation(message, yes=False):
    if yes:
        return
    try:
        if not prompt_y_n(message):
            raise ManualInterrupt('Operation cancelled.')
    except NoTTYException:
        raise CLIInternalError('Unable to prompt for confirmation as no tty available. Use --yes.')


def is_guid(guid):
    import uuid
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


def try_list_node_fix():
    try:
        from kubernetes.client.models.v1_container_image import V1ContainerImage

        def names(self, names):
            self._names = names

        V1ContainerImage.names = V1ContainerImage.names.setter(names)
    except Exception as ex:
        logger.debug("Error while trying to monkey patch the fix for list_node(): {}".format(str(ex)))


def check_provider_registrations(cli_ctx, subscription_id):
    try:
        rp_client = resource_providers_client(cli_ctx, subscription_id)
        cc_registration_state = rp_client.get(consts.Connected_Cluster_Provider_Namespace).registration_state
        if cc_registration_state != "Registered":
            telemetry.set_exception(exception="{} provider is not registered".format(consts.Connected_Cluster_Provider_Namespace), fault_type=consts.CC_Provider_Namespace_Not_Registered_Fault_Type,
                                    summary="{} provider is not registered".format(consts.Connected_Cluster_Provider_Namespace))
            raise ValidationError("{} provider is not registered. Please register it using 'az provider register -n 'Microsoft.Kubernetes' before running the connect command.".format(consts.Connected_Cluster_Provider_Namespace))
        kc_registration_state = rp_client.get(consts.Kubernetes_Configuration_Provider_Namespace).registration_state
        if kc_registration_state != "Registered":
            telemetry.set_user_fault()
            logger.warning("{} provider is not registered".format(consts.Kubernetes_Configuration_Provider_Namespace))
    except ValidationError as e:
        raise e
    except Exception as ex:
        logger.warning("Couldn't check the required provider's registration status. Error: {}".format(str(ex)))


def can_create_clusterrolebindings():
    try:
        api_instance = kube_client.AuthorizationV1Api()
        access_review = kube_client.V1SelfSubjectAccessReview(spec={
            "resourceAttributes": {
                "verb": "create",
                "resource": "clusterrolebindings",
                "group": "rbac.authorization.k8s.io"
            }
        })
        response = api_instance.create_self_subject_access_review(access_review)
        return response.status.allowed
    except Exception as ex:
        logger.warning("Couldn't check for the permission to create clusterrolebindings on this k8s cluster. Error: {}".format(str(ex)))
        return "Unknown"


def validate_node_api_response(api_instance, node_api_response):
    if node_api_response is None:
        try:
            node_api_response = api_instance.list_node()
            return node_api_response
        except Exception as ex:
            logger.debug("Error occcured while listing nodes on this kubernetes cluster: {}".format(str(ex)))
            return None
    else:
        return node_api_response


def az_cli(args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args, out_file=open(os.devnull, 'w'))
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise Exception(cli.result.error)
    return True


# def is_cli_using_msal_auth():
#     response_cli_version = az_cli("version --output json")
#     try:
#         cli_version = response_cli_version['azure-cli']
#     except Exception as ex:
#         raise CLIInternalError("Unable to decode the az cli version installed: {}".format(str(ex)))
#     if version.parse(cli_version) >= version.parse(consts.AZ_CLI_ADAL_TO_MSAL_MIGRATE_VERSION):
#         return True
#     else:
#         return False

def is_cli_using_msal_auth():
    response_cli_version = az_cli("version --output json")
    try:
        cli_version = response_cli_version['azure-cli']
    except Exception as ex:
        raise CLIInternalError("Unable to decode the az cli version installed: {}".format(str(ex)))
    v1 = cli_version
    v2 = consts.AZ_CLI_ADAL_TO_MSAL_MIGRATE_VERSION
    for i, j in zip(map(int, v1.split(".")), map(int, v2.split("."))):
        if i == j:
            continue
        return i > j
    return len(v1.split(".")) == len(v2.split("."))


def get_metadata(arm_endpoint, api_version="2022-09-01"):
    metadata_url_suffix = f"/metadata/endpoints?api-version={api_version}"
    metadata_endpoint = None
    try:
        import requests
        session = requests.Session()
        metadata_endpoint = arm_endpoint + metadata_url_suffix
        response = session.get(metadata_endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            msg = f"ARM metadata endpoint '{metadata_endpoint}' returned status code {response.status_code}."
            raise HttpResponseError(msg)
    except Exception as err:
        msg = f"Failed to request ARM metadata {metadata_endpoint}."
        print(msg, file=sys.stderr)
        print(f"Please ensure you have network connection. Error: {str(err)}", file=sys.stderr)
        arm_exception_handler(err, msg)
