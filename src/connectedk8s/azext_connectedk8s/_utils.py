# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from subprocess import PIPE, Popen
from typing import TYPE_CHECKING, Any

from azure.cli.core import get_default_cli, telemetry
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    AzureInternalError,
    AzureResponseError,
    ClientRequestError,
    CLIInternalError,
    ManualInterrupt,
    ValidationError,
)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from kubernetes import client as kube_client
from kubernetes.client.rest import ApiException
from msrest.exceptions import AuthenticationError, HttpOperationError, TokenExpiredError
from msrest.exceptions import ValidationError as MSRestValidationError
from packaging import version

import azext_connectedk8s._constants as consts
from azext_connectedk8s._client_factory import (
    cf_resource_groups,
    resource_providers_client,
)

if TYPE_CHECKING:
    from azure.cli.core import AzCli
    from knack.commands import CLICommand
    from kubernetes.client import CoreV1Api, V1NodeList
    from requests import Response

    from azext_connectedk8s.vendored_sdks.preview_2024_07_01.models import (
        ConnectedCluster,
    )

logger = get_logger(__name__)

# pylint: disable=line-too-long
# pylint: disable=bare-except


def get_mcr_path(cmd: CLICommand) -> str:
    active_directory_array = cmd.cli_ctx.cloud.endpoints.active_directory.split(".")

    # default for public, mc, ff clouds
    mcr_postfix = active_directory_array[2]
    # special cases for USSec, exclude part of suffix
    if len(active_directory_array) == 4 and active_directory_array[2] == "microsoft":
        mcr_postfix = active_directory_array[3]
    # special case for USNat
    elif len(active_directory_array) == 5:
        mcr_postfix = (
            active_directory_array[2]
            + "."
            + active_directory_array[3]
            + "."
            + active_directory_array[4]
        )

    mcr_url = f"mcr.microsoft.{mcr_postfix}"
    return mcr_url


def validate_connect_rp_location(cmd: CLICommand, location: str) -> None:
    subscription_id = (
        os.getenv("AZURE_SUBSCRIPTION_ID")
        if os.getenv("AZURE_ACCESS_TOKEN")
        else get_subscription_id(cmd.cli_ctx)
    )
    rp_locations = []
    resourceClient = resource_providers_client(
        cmd.cli_ctx, subscription_id=subscription_id
    )

    try:
        providerDetails = resourceClient.get("Microsoft.Kubernetes")
    except Exception as e:  # pylint: disable=broad-except
        arm_exception_handler(
            e,
            consts.Get_ResourceProvider_Fault_Type,
            "Failed to fetch resource provider details",
        )

    for resourceTypes in providerDetails.resource_types:  # type: ignore[attr-defined]
        if resourceTypes.resource_type == "connectedClusters":
            rp_locations = [
                location.replace(" ", "").lower()
                for location in resourceTypes.locations
            ]
            if location.lower() not in rp_locations:
                telemetry.set_exception(
                    exception="Location not supported",
                    fault_type=consts.Invalid_Location_Fault_Type,
                    summary="Provided location is not supported for creating connected clusters",
                )
                raise ArgumentUsageError(
                    "Connected cluster resource creation is supported only in the following locations: "
                    + ", ".join(map(str, rp_locations)),
                    recommendation="Use the --location flag to specify one of these locations.",
                )
            break


def validate_custom_token(
    cmd: CLICommand, resource_group_name: str, location: str | None
) -> tuple[bool, str | None]:
    print(f"Step: {get_utctimestring()}: Validating custom access token")
    if os.getenv("AZURE_ACCESS_TOKEN"):
        if os.getenv("AZURE_SUBSCRIPTION_ID") is None:
            telemetry.set_exception(
                exception="Required environment variable SubscriptionId not set, for custom Azure access token",
                fault_type=consts.Custom_Access_Token_Env_Var_Sub_Id_Missing_Fault_Type,
                summary="Required environment variable SubscriptionId not set, for custom Azure access token",
            )
            raise ValidationError(
                "Environment variable 'AZURE_SUBSCRIPTION_ID' should be set when custom access token is enabled."
            )
        if os.getenv("AZURE_TENANT_ID") is None:
            telemetry.set_exception(
                exception="Required environment variable TenantId not set, for custom Azure access token",
                fault_type=consts.Custom_Access_Token_Env_Var_Tenant_Id_Missing_Fault_Type,
                summary="Required environment variable TenantId not set, for custom Azure access token",
            )
            raise ValidationError(
                "Environment variable 'AZURE_TENANT_ID' should be set when custom access token is enabled."
            )
        if location is None:
            try:
                resource_client = cf_resource_groups(
                    cmd.cli_ctx, os.getenv("AZURE_SUBSCRIPTION_ID")
                )
                rg = resource_client.get(resource_group_name)
                location = rg.location
            except Exception as ex:
                telemetry.set_exception(
                    exception=ex,
                    fault_type=consts.Location_Fetch_Fault_Type,
                    summary="Unable to fetch location from resource group",
                )
                raise ValidationError(
                    f"Unable to fetch location from resource group: '{ex}'"
                )
        return True, location
    return False, location


def get_chart_path(
    registry_path: str,
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
    chart_folder_name: str = "AzureArcCharts",
    chart_name: str = "azure-arc-k8sagents",
    new_path: bool = True,
) -> str:
    print(f"Step: {get_utctimestring()}: Determine Helmchart Export Path")
    # Exporting Helm chart
    chart_export_path = os.path.join(
        os.path.expanduser("~"), ".azure", chart_folder_name
    )
    try:
        if os.path.isdir(chart_export_path):
            shutil.rmtree(chart_export_path)
    except OSError:
        logger.warning(
            "Unable to cleanup the %s already present on the machine. In case of failure, please cleanup "
            "the directory '%s' and try again.",
            chart_folder_name,
            chart_export_path,
        )

    pull_helm_chart(
        registry_path,
        chart_export_path,
        kube_config,
        kube_context,
        helm_client_location,
        new_path,
        chart_name,
    )

    # Returning helm chart path
    helm_chart_path = os.path.join(chart_export_path, chart_name)
    if chart_folder_name == consts.Pre_Onboarding_Helm_Charts_Folder_Name:
        chart_path = helm_chart_path
    else:
        chart_path = os.getenv("HELMCHART", helm_chart_path)

    return chart_path


def pull_helm_chart(
    registry_path: str,
    chart_export_path: str,
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
    new_path: bool,
    chart_name: str = "azure-arc-k8sagents",
    retry_count: int = 5,
    retry_delay: int = 3,
) -> None:
    chart_url = registry_path.split(":")[0]
    chart_version = registry_path.split(":")[1]

    if new_path:
        # Version check for stable release train (chart_version will be in X.Y.Z format as opposed to X.Y.Z-NONSTABLE)
        if "-" not in chart_version and (
            version.parse(chart_version) < version.parse("1.14.0")
        ):
            error_summary = "This CLI version does not support upgrading to Agents versions older than v1.14"
            telemetry.set_exception(
                exception="Operation not supported on older Agents",
                fault_type=consts.Operation_Not_Supported_Fault_Type,
                summary=error_summary,
            )
            raise ClientRequestError(
                error_summary,
                recommendation="Please select an agent-version >= v1.14 to upgrade to using 'az connectedk8s upgrade "
                "-g <rg_name> -n <cluster_name> --agent-version <at-least-1.14>'.",
            )

        base_path = os.path.dirname(chart_url)
        image_name = os.path.basename(chart_url)
        chart_url = base_path + "/v2/" + image_name

    print(
        f"Step: {get_utctimestring()}: Pulling HelmChart: {chart_url}, Version: {chart_version}"
    )

    cmd_helm_chart_pull = [
        helm_client_location,
        "pull",
        "oci://" + chart_url,
        "--untar",
        "--untardir",
        chart_export_path,
        "--version",
        chart_version,
    ]
    if kube_config:
        cmd_helm_chart_pull.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_chart_pull.extend(["--kube-context", kube_context])
    for i in range(retry_count):
        response_helm_chart_pull = subprocess.Popen(
            cmd_helm_chart_pull, stdout=PIPE, stderr=PIPE
        )
        _, error_helm_chart_pull = response_helm_chart_pull.communicate()
        if response_helm_chart_pull.returncode != 0:
            error = error_helm_chart_pull.decode("ascii")
            if i == retry_count - 1:
                telemetry.set_exception(
                    exception=error,
                    fault_type=consts.Pull_HelmChart_Fault_Type,
                    summary=f"Unable to pull {chart_name} helm charts from the registry",
                )
                raise CLIInternalError(
                    f"Unable to pull {chart_name} helm chart from the registry"
                    f" '{registry_path}': {error}"
                )
            time.sleep(retry_delay)
        else:
            break


def save_cluster_diagnostic_checks_pod_description(
    corev1_api_instance: CoreV1Api,
    kubectl_client_location: str,
    kube_config: str | None,
    kube_context: str | None,
    filepath_with_timestamp: str,
    storage_space_available: bool,
) -> None:
    try:
        job_name = "cluster-diagnostic-checks-job"
        all_pods = corev1_api_instance.list_namespaced_pod("azure-arc-release")
        # Traversing through all agents
        for each_pod in all_pods.items:
            # Fetching the current Pod name and creating a folder with that name inside the timestamp folder
            pod_name = each_pod.metadata.name
            if pod_name.startswith(job_name):
                describe_job_pod = [
                    kubectl_client_location,
                    "describe",
                    "pod",
                    pod_name,
                    "-n",
                    "azure-arc-release",
                ]
                if kube_config:
                    describe_job_pod.extend(["--kubeconfig", kube_config])
                if kube_context:
                    describe_job_pod.extend(["--context", kube_context])
                response_describe_job_pod = Popen(
                    describe_job_pod, stdout=PIPE, stderr=PIPE
                )
                output_describe_job_pod, error_describe_job_pod = (
                    response_describe_job_pod.communicate()
                )
                if response_describe_job_pod.returncode == 0:
                    pod_description = output_describe_job_pod.decode()
                    if storage_space_available:
                        dns_check_path = os.path.join(
                            filepath_with_timestamp,
                            "cluster_diagnostic_checks_pod_description.txt",
                        )
                        with open(dns_check_path, "w+") as f:
                            f.write(pod_description)
                else:
                    telemetry.set_exception(
                        exception=error_describe_job_pod.decode("ascii"),
                        fault_type=consts.Cluster_Diagnostic_Checks_Pod_Description_Save_Failed,
                        summary="Failed to save cluster diagnostic checks pod description in the local machine",
                    )
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(
                exception=e,
                fault_type=consts.No_Storage_Space_Available_Fault_Type,
                summary="No space left on device",
            )
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False)
        else:
            logger.exception(
                "An exception has occured while saving the cluster diagnostic checks "
                "pod description in the local machine."
            )
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Cluster_Diagnostic_Checks_Pod_Description_Save_Failed,
                summary="Error occured while saving the cluster diagnostic checks pod description in the local machine",
            )

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.exception(
            "An exception has occured while saving the cluster diagnostic checks pod "
            "description in the local machine."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Cluster_Diagnostic_Checks_Pod_Description_Save_Failed,
            summary="Error occured while saving the cluster diagnostic checks pod description in the local machine",
        )


def check_cluster_DNS(
    dns_check_log: str,
    filepath_with_timestamp: str,
    storage_space_available: bool,
    diagnoser_output: list[str],
) -> tuple[str, bool]:
    try:
        if consts.DNS_Check_Result_String not in dns_check_log:
            return consts.Diagnostic_Check_Incomplete, storage_space_available
        formatted_dns_log = dns_check_log.replace("\t", "")
        # Validating if DNS is working or not and displaying proper result
        if (
            "NXDOMAIN" in formatted_dns_log
            or "connection timed out" in formatted_dns_log
        ):
            logger.warning(
                "Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS "
                "issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n"
            )
            diagnoser_output.append(
                "Error: We found an issue with the DNS resolution on your cluster. For details about debugging DNS "
                "issues visit 'https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/'.\n"
            )
            if storage_space_available:
                dns_check_path = os.path.join(filepath_with_timestamp, consts.DNS_Check)
                with open(dns_check_path, "w+") as dns:
                    dns.write(
                        formatted_dns_log
                        + "\nWe found an issue with the DNS resolution on your cluster."
                    )
            telemetry.set_exception(
                exception="DNS resolution check failed in the cluster",
                fault_type=consts.DNS_Check_Failed,
                summary="DNS check failed in the cluster",
            )
            return consts.Diagnostic_Check_Failed, storage_space_available

        if storage_space_available:
            dns_check_path = os.path.join(filepath_with_timestamp, consts.DNS_Check)
            with open(dns_check_path, "w+") as dns:
                dns.write(
                    formatted_dns_log + "\nCluster DNS check passed successfully."
                )

        return consts.Diagnostic_Check_Passed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(
                exception=e,
                fault_type=consts.No_Storage_Space_Available_Fault_Type,
                summary="No space left on device",
            )
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False)
        else:
            logger.exception(
                "An exception has occured while performing the DNS check on the "
                "cluster."
            )
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Cluster_DNS_Check_Fault_Type,
                summary="Error occured while performing cluster DNS check",
            )
            diagnoser_output.append(
                "An exception has occured while performing the DNS check on the cluster. "
                f"Exception: {e}\n"
            )

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.exception(
            "An exception has occured while performing the DNS check on the cluster."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Cluster_DNS_Check_Fault_Type,
            summary="Error occured while performing cluster DNS check",
        )
        diagnoser_output.append(
            "An exception has occured while performing the DNS check on the cluster. "
            f"Exception: {e}\n"
        )

    return consts.Diagnostic_Check_Incomplete, storage_space_available


def check_cluster_outbound_connectivity(
    outbound_connectivity_check_log: str,
    filepath_with_timestamp: str,
    storage_space_available: bool,
    diagnoser_output: list[str],
    outbound_connectivity_check_for: str = "pre-onboarding-inspector",
) -> tuple[str, bool]:
    try:
        if outbound_connectivity_check_for == "pre-onboarding-inspector":
            if (
                consts.Outbound_Connectivity_Check_Result_String
                not in outbound_connectivity_check_log
            ):
                return consts.Diagnostic_Check_Incomplete, storage_space_available

            Outbound_Connectivity_Log_For_Cluster_Connect = (
                outbound_connectivity_check_log.split("  ")[0]
            )
            # extracting the endpoints for cluster connect feature
            Cluster_Connect_Precheck_Endpoint_Url = (
                Outbound_Connectivity_Log_For_Cluster_Connect.split(" : ")[1]
            )
            # extracting the obo endpoint response code from outbound connectivity check
            Cluster_Connect_Precheck_Endpoint_response_code = (
                Outbound_Connectivity_Log_For_Cluster_Connect.split(" : ")[2]
            )

            if Cluster_Connect_Precheck_Endpoint_response_code != "000":
                if storage_space_available:
                    cluster_connect_outbound_connectivity_check_path = os.path.join(
                        filepath_with_timestamp,
                        consts.Outbound_Network_Connectivity_Check_for_cluster_connect,
                    )
                    with open(
                        cluster_connect_outbound_connectivity_check_path, "w+"
                    ) as outbound:
                        outbound.write(
                            "Response code "
                            + Cluster_Connect_Precheck_Endpoint_response_code
                            + "\nOutbound network connectivity check to cluster connect precheck endpoints "
                            "passed successfully."
                        )
            else:
                logger.warning(
                    "The outbound network connectivity check has failed for the "
                    "endpoint - %s\n"
                    'This will affect the "cluster-connect" feature. If you are planning to use '
                    '"cluster-connect" functionality, please ensure outbound connectivity to the '
                    "above endpoint.\n",
                    Cluster_Connect_Precheck_Endpoint_Url,
                )
                telemetry.set_user_fault()
                telemetry.set_exception(
                    exception="Outbound network connectivity check failed for the Cluster Connect endpoint",
                    fault_type=consts.Outbound_Connectivity_Check_Failed_For_Cluster_Connect,
                    summary="Outbound network connectivity check failed for the Cluster Connect precheck endpoint",
                )
                if storage_space_available:
                    cluster_connect_outbound_connectivity_check_path = os.path.join(
                        filepath_with_timestamp,
                        consts.Outbound_Network_Connectivity_Check_for_cluster_connect,
                    )
                    with open(
                        cluster_connect_outbound_connectivity_check_path, "w+"
                    ) as outbound:
                        outbound.write(
                            "Response code "
                            + Cluster_Connect_Precheck_Endpoint_response_code
                            + "\nOutbound connectivity failed for the endpoint:"
                            + Cluster_Connect_Precheck_Endpoint_Url
                            + " ,this is an optional endpoint needed for cluster-connect feature."
                        )

            Onboarding_Precheck_Endpoint_outbound_connectivity_response = (
                outbound_connectivity_check_log[-1:-4:-1]
            )
            Onboarding_Precheck_Endpoint_outbound_connectivity_response = (
                Onboarding_Precheck_Endpoint_outbound_connectivity_response[::-1]
            )

            # Validating if outbound connectiivty is working or not and displaying proper result
            if Onboarding_Precheck_Endpoint_outbound_connectivity_response != "000":
                if storage_space_available:
                    outbound_connectivity_check_path = os.path.join(
                        filepath_with_timestamp,
                        consts.Outbound_Network_Connectivity_Check_for_onboarding,
                    )
                    with open(outbound_connectivity_check_path, "w+") as outbound:
                        outbound.write(
                            "Response code "
                            + Onboarding_Precheck_Endpoint_outbound_connectivity_response
                            + "\nOutbound network connectivity check to the onboarding precheck endpoint "
                            "passed successfully."
                        )
                return consts.Diagnostic_Check_Passed, storage_space_available

            outbound_connectivity_failed_warning_message = (
                "Error: We found an issue with outbound network connectivity from the cluster to the endpoints "
                "required for onboarding.\nPlease ensure to meet the following network requirements "
                + consts.Doc_Network_Requirements_Url
                + "\nIf your cluster is behind an outbound proxy server, "
                " please ensure that you have passed proxy parameters during the onboarding of your cluster.\n"
                "For more details visit "
                + consts.Doc_Quick_Start_Outbound_Proxy_Url
                + " \n"
            )
            logger.warning(outbound_connectivity_failed_warning_message)
            telemetry.set_user_fault()
            diagnoser_output.append(outbound_connectivity_failed_warning_message)
            if storage_space_available:
                outbound_connectivity_check_path = os.path.join(
                    filepath_with_timestamp,
                    consts.Outbound_Network_Connectivity_Check_for_onboarding,
                )
                with open(outbound_connectivity_check_path, "w+") as outbound:
                    outbound.write(
                        "Response code "
                        + Onboarding_Precheck_Endpoint_outbound_connectivity_response
                        + "\nWe found an issue with Outbound network connectivity from the cluster "
                        "required for onboarding."
                    )
            telemetry.set_exception(
                exception="Outbound network connectivity check failed for onboarding",
                fault_type=consts.Outbound_Connectivity_Check_Failed_For_Onboarding,
                summary="Outbound network connectivity check for onboarding failed in the cluster",
            )
            return consts.Diagnostic_Check_Failed, storage_space_available

        if outbound_connectivity_check_for == "troubleshoot":
            outbound_connectivity_response = outbound_connectivity_check_log[-1:-4:-1]
            outbound_connectivity_response = outbound_connectivity_response[::-1]
            if (
                consts.Outbound_Connectivity_Check_Result_String
                not in outbound_connectivity_check_log
            ):
                return consts.Diagnostic_Check_Incomplete, storage_space_available

            if outbound_connectivity_response != "000":
                if storage_space_available:
                    outbound_connectivity_check_path = os.path.join(
                        filepath_with_timestamp,
                        consts.Outbound_Network_Connectivity_Check,
                    )
                    with open(outbound_connectivity_check_path, "w+") as outbound:
                        outbound.write(
                            "Response code "
                            + outbound_connectivity_response
                            + "\nOutbound network connectivity check passed successfully."
                        )
                return consts.Diagnostic_Check_Passed, storage_space_available

            outbound_connectivity_failed_warning_message = (
                "Error: We found an issue with outbound network connectivity from the cluster.\nPlease ensure to "
                "meet the following network requirements '"
                + consts.Doc_Network_Requirements_Url
                + " \nIf your cluster is behind an outbound proxy server, please ensure that you have passed proxy "
                "parameters during the onboarding of your cluster.\nFor more details visit "
                + consts.Doc_Quick_Start_Outbound_Proxy_Url
                + " \n"
            )
            logger.warning(outbound_connectivity_failed_warning_message)
            diagnoser_output.append(outbound_connectivity_failed_warning_message)
            if storage_space_available:
                outbound_connectivity_check_path = os.path.join(
                    filepath_with_timestamp, consts.Outbound_Network_Connectivity_Check
                )
                with open(outbound_connectivity_check_path, "w+") as outbound:
                    outbound.write(
                        "Response code "
                        + outbound_connectivity_response
                        + "\nWe found an issue with Outbound network connectivity from the cluster."
                    )
            telemetry.set_exception(
                exception="Outbound network connectivity check failed",
                fault_type=consts.Outbound_Connectivity_Check_Failed,
                summary="Outbound network connectivity check failed in the cluster",
            )
            return consts.Diagnostic_Check_Failed, storage_space_available

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            storage_space_available = False
            telemetry.set_exception(
                exception=e,
                fault_type=consts.No_Storage_Space_Available_Fault_Type,
                summary="No space left on device",
            )
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False)
        else:
            logger.exception(
                "An exception has occured while performing the outbound connectivity "
                "check on the cluster."
            )
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Outbound_Connectivity_Check_Fault_Type,
                summary="Error occured while performing outbound connectivity check in the cluster",
            )
            diagnoser_output.append(
                "An exception has occured while performing the outbound connectivity check on the cluster. "
                f"Exception: {e}\n"
            )

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.exception(
            "An exception has occured while performing the outbound connectivity check "
            "on the cluster."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Outbound_Connectivity_Check_Fault_Type,
            summary="Error occured while performing outbound connectivity check in the cluster",
        )
        diagnoser_output.append(
            "An exception has occured while performing the outbound connectivity check on the cluster. "
            f"Exception: {e}\n"
        )

    return consts.Diagnostic_Check_Incomplete, storage_space_available


def create_folder_diagnosticlogs(time_stamp: str, folder_name: str) -> tuple[str, bool]:
    print(
        f"Step: {get_utctimestring()}: Creating folder for Cluster Diagnostic Checks Logs"
    )
    try:
        # Fetching path to user directory to create the arc diagnostic folder
        home_dir = os.path.expanduser("~")
        filepath = os.path.join(home_dir, ".azure", folder_name)
        # Creating Diagnostic folder and its subfolder with the given timestamp and cluster name to store all the logs
        with contextlib.suppress(FileExistsError):
            os.mkdir(filepath)
        filepath_with_timestamp = os.path.join(filepath, time_stamp)
        try:
            os.mkdir(filepath_with_timestamp)
        except FileExistsError:
            # Deleting the folder if present with the same timestamp to prevent overriding in the same folder and then
            #  creating it again
            shutil.rmtree(filepath_with_timestamp, ignore_errors=True)
            os.mkdir(filepath_with_timestamp)

        return filepath_with_timestamp, True

    # For handling storage or OS exception that may occur during the execution
    except OSError as e:
        if "[Errno 28]" in str(e):
            shutil.rmtree(filepath_with_timestamp, ignore_errors=False)
            telemetry.set_exception(
                exception=e,
                fault_type=consts.No_Storage_Space_Available_Fault_Type,
                summary="No space left on device",
            )
            return "", False
        logger.exception(
            "An exception has occured while creating the diagnostic logs folder in "
            "your local machine."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type,
            summary="Error while trying to create diagnostic logs folder",
        )
        return "", False

    # To handle any exception that may occur during the execution
    except Exception as e:
        logger.exception(
            "An exception has occured while creating the diagnostic logs folder in "
            "your local machine."
        )
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Diagnostics_Folder_Creation_Failed_Fault_Type,
            summary="Error while trying to create diagnostic logs folder",
        )
        return "", False


def add_helm_repo(
    kube_config: str | None, kube_context: str | None, helm_client_location: str
) -> None:
    print(f"Step: {get_utctimestring()}: Adding Helm Repo")
    repo_name = os.environ["HELMREPONAME"]
    repo_url = os.environ["HELMREPOURL"]
    cmd_helm_repo = [helm_client_location, "repo", "add", repo_name, repo_url]
    if kube_config:
        cmd_helm_repo.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_repo.extend(["--kube-context", kube_context])
    response_helm_repo = Popen(cmd_helm_repo, stdout=PIPE, stderr=PIPE)
    _, error_helm_repo = response_helm_repo.communicate()
    if response_helm_repo.returncode != 0:
        error = error_helm_repo.decode("ascii")
        telemetry.set_exception(
            exception=error,
            fault_type=consts.Add_HelmRepo_Fault_Type,
            summary="Failed to add helm repository",
        )
        raise CLIInternalError(f"Unable to add repository {repo_url} to helm: {error}")


def get_helm_registry(
    cmd: CLICommand, config_dp_endpoint: str, release_train_custom: str | None = None
) -> str:
    print(f"Step: {get_utctimestring()}: Getting HelmPackagePath from Arc DataPlane")
    # Setting uri
    api_version = "2019-11-01-preview"
    chart_location_url_segment = (
        f"azure-arc-k8sagents/GetLatestHelmPackagePath?api-version={api_version}"
    )
    release_train = os.getenv("RELEASETRAIN") if os.getenv("RELEASETRAIN") else "stable"
    chart_location_url = f"{config_dp_endpoint}/{chart_location_url_segment}"
    if release_train_custom:
        release_train = release_train_custom
    uri_parameters = [f"releaseTrain={release_train}"]
    resource = cmd.cli_ctx.cloud.endpoints.active_directory_resource_id
    headers = None
    if os.getenv("AZURE_ACCESS_TOKEN"):
        headers = ["Authorization=Bearer {}".format(os.getenv("AZURE_ACCESS_TOKEN"))]
    # Sending request with retries
    r = send_request_with_retries(
        cmd.cli_ctx,
        "post",
        chart_location_url,
        headers=headers,
        fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
        summary="Error while fetching helm chart registry path",
        uri_parameters=uri_parameters,
        resource=resource,
    )
    if r.content:
        try:
            repository_path: str = r.json().get("repositoryPath")
            return repository_path
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                summary="Error while fetching helm chart registry path",
            )
            raise CLIInternalError(
                f"Error while fetching helm chart registry path from JSON response: {e}"
            )
    else:
        telemetry.set_exception(
            exception="No content in response",
            fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
            summary="No content in acr path response",
        )
        raise CLIInternalError("No content was found in helm registry path response.")


def get_helm_values(
    cmd: CLICommand,
    config_dp_endpoint: str,
    release_train_custom: str | None,
    connected_cluster: ConnectedCluster,
) -> dict[str, Any]:
    # Setting uri
    api_version = "2024-07-01-preview"
    chart_location_url_segment = (
        f"azure-arc-k8sagents/GetHelmSettings?api-version={api_version}"
    )
    release_train = os.getenv("RELEASETRAIN", "stable")
    chart_location_url = f"{config_dp_endpoint}/{chart_location_url_segment}"
    dp_request_identity = connected_cluster.identity
    identity = connected_cluster.id
    request_dict = connected_cluster.serialize()
    request_dict["identity"]["tenantId"] = dp_request_identity.tenant_id
    request_dict["identity"]["principalId"] = dp_request_identity.principal_id
    request_dict["id"] = identity
    request_body = json.dumps(request_dict)
    if release_train_custom:
        release_train = release_train_custom
    uri_parameters = [f"releaseTrain={release_train}"]
    resource = cmd.cli_ctx.cloud.endpoints.active_directory_resource_id
    headers = None
    if os.getenv("AZURE_ACCESS_TOKEN"):
        headers = ["Authorization=Bearer {}".format(os.getenv("AZURE_ACCESS_TOKEN"))]
    # Sending request with retries
    r = send_request_with_retries(
        cmd.cli_ctx,
        "post",
        chart_location_url,
        headers=headers,
        fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
        summary="Error while fetching helm chart registry path",
        uri_parameters=uri_parameters,
        resource=resource,
        request_body=request_body,
    )
    if r.content:
        try:
            content: dict[str, Any] = r.json()
            return content
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
                summary="Error while fetching helm values from DP",
            )
            raise CLIInternalError(
                f"Error while fetching helm values from DP from JSON response: {e}"
            )
    else:
        telemetry.set_exception(
            exception="No content in response",
            fault_type=consts.Get_HelmRegistery_Path_Fault_Type,
            summary="No content in acr path response",
        )
        raise CLIInternalError("No content was found in helm registry path response.")


def health_check_dp(cmd: CLICommand, config_dp_endpoint: str) -> bool:
    # Setting uri
    api_version = "2024-07-01-preview"
    chart_location_url_segment = (
        f"azure-arc-k8sagents/healthCheck?api-version={api_version}"
    )
    chart_location_url = f"{config_dp_endpoint}/{chart_location_url_segment}"
    uri_parameters: list[str] = []
    resource = cmd.cli_ctx.cloud.endpoints.active_directory_resource_id
    headers = None
    if os.getenv("AZURE_ACCESS_TOKEN"):
        headers = ["Authorization=Bearer {}".format(os.getenv("AZURE_ACCESS_TOKEN"))]
    # Sending request with retries
    r = send_request_with_retries(
        cmd.cli_ctx,
        "post",
        chart_location_url,
        headers=headers,
        fault_type=consts.DP_Health_Check_Fault_Type,
        summary="Error while performing DP health check",
        uri_parameters=uri_parameters,
        resource=resource,
    )
    if r.status_code == 200:
        return True

    telemetry.set_exception(
        exception="Error while performing DP health check",
        fault_type=consts.DP_Health_Check_Fault_Type,
        summary="Error while performing DP health check",
    )
    raise CLIInternalError("Error while performing DP health check")


def send_request_with_retries(
    cli_ctx: AzCli,
    method: str,
    url: str,
    headers: list[str] | None,
    fault_type: str,
    summary: str,
    uri_parameters: list[str] | None = None,
    resource: str | None = None,
    retry_count: int = 5,
    retry_delay: int = 3,
    request_body: str | None = None,
) -> Response:
    response: Response
    for i in range(retry_count):
        try:
            response = send_raw_request(
                cli_ctx,
                method,
                url,
                headers=headers,
                uri_parameters=uri_parameters,
                resource=resource,
                body=request_body,
            )
            return response
        except Exception as e:
            if i == retry_count - 1:
                telemetry.set_exception(
                    exception=e, fault_type=fault_type, summary=summary
                )
                raise CLIInternalError(
                    f"Error while fetching helm chart registry path: {e}"
                )
            time.sleep(retry_delay)

    assert False


def arm_exception_handler(
    ex: Exception, fault_type: str, summary: str, return_if_not_found: bool = False
) -> None:
    if isinstance(ex, AuthenticationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError(
            "Authentication error occured while making ARM request: "
            + str(ex)
            + f"\nSummary: {summary}"
        )

    if isinstance(ex, TokenExpiredError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError(
            "Token expiration error occured while making ARM request: "
            + str(ex)
            + f"\nSummary: {summary}"
        )

    if isinstance(ex, HttpOperationError):
        status_code = ex.response.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code // 100 == 5:
            raise AzureInternalError(
                "Http operation error occured while making ARM request: "
                + str(ex)
                + f"\nSummary: {summary}"
            )
        raise AzureResponseError(
            "Http operation error occured while making ARM request: "
            + str(ex)
            + f"\nSummary: {summary}"
        )

    if isinstance(ex, MSRestValidationError):
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        raise AzureResponseError(
            "Validation error occured while making ARM request: "
            + str(ex)
            + f"\nSummary: {summary}"
        )

    if isinstance(ex, HttpResponseError):
        status_code = ex.status_code
        if status_code == 404 and return_if_not_found:
            return
        if status_code is not None and status_code // 100 == 4:
            telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
        if status_code is not None and status_code // 100 == 5:
            raise AzureInternalError(
                "Http response error occured while making ARM request: "
                + str(ex)
                + f"\nSummary: {summary}"
            )
        raise AzureResponseError(
            "Http response error occured while making ARM request: "
            + str(ex)
            + f"\nSummary: {summary}"
        )

    if isinstance(ex, ResourceNotFoundError) and return_if_not_found:
        return

    telemetry.set_exception(exception=ex, fault_type=fault_type, summary=summary)
    raise ClientRequestError(
        "Error occured while making ARM request: " + str(ex) + f"\nSummary: {summary}"
    )


def kubernetes_exception_handler(
    ex: Exception,
    fault_type: str,
    summary: str,
    error_message: str = "Error occured while connecting to the kubernetes cluster: ",
    message_for_unauthorized_request: str = "The user does not have required privileges on the "
    "kubernetes cluster to deploy Azure Arc enabled Kubernetes agents. Please "
    "ensure you have cluster admin privileges on the cluster to onboard.",
    message_for_not_found: str = "The requested kubernetes resource was not found.",
    raise_error: bool = True,
) -> None:
    telemetry.set_user_fault()
    if isinstance(ex, ApiException):
        status_code = ex.status
        if status_code == 403:
            logger.warning(message_for_unauthorized_request)
        elif status_code == 404:
            logger.warning(message_for_not_found)
        else:
            logger.debug("Kubernetes Exception: ", exc_info=True)
        if raise_error:
            telemetry.set_exception(
                exception=ex, fault_type=fault_type, summary=summary
            )
            raise ValidationError(error_message + "\nError Response: " + str(ex.body))
    else:
        if raise_error:
            telemetry.set_exception(
                exception=ex, fault_type=fault_type, summary=summary
            )
            raise ValidationError(error_message + "\nError: " + str(ex))

        logger.debug("Kubernetes Exception", exc_info=True)


def validate_infrastructure_type(infra: str) -> str | None:
    for s in consts.Infrastructure_Enum_Values[1:]:  # First value is "auto"
        if s.lower() == infra.lower():
            return s
    return infra


def get_values_file() -> str | None:
    values_file = os.getenv("HELMVALUESPATH")
    if (values_file is not None) and (os.path.isfile(values_file)):
        logger.warning(
            "Values files detected. Reading additional helm parameters from same."
        )
        # trimming required for windows os
        if values_file.startswith(("'", '"')):
            values_file = values_file[1:]
        if values_file.endswith(("'", '"')):
            values_file = values_file[:-1]
        return values_file
    return None


def ensure_namespace_cleanup() -> None:
    print(
        f"Step: {get_utctimestring()}: Confirming '{consts.Arc_Namespace}' namespace got deleted."
    )
    api_instance = kube_client.CoreV1Api()
    timeout = time.time() + 180
    while True:
        if time.time() > timeout:
            telemetry.set_user_fault()
            logger.warning(
                "Namespace 'azure-arc' still in terminating state. Please ensure that you delete the "
                "'azure-arc' namespace before onboarding the cluster again."
            )
            return
        try:
            api_response = api_instance.list_namespace(
                field_selector="metadata.name=azure-arc"
            )
            if not api_response.items:
                return
            time.sleep(5)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Error while retrieving namespace information.")
            kubernetes_exception_handler(
                e,
                consts.Get_Kubernetes_Namespace_Fault_Type,
                "Unable to fetch kubernetes namespace",
                raise_error=False,
            )


def delete_arc_agents(
    release_namespace: str,
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
    is_arm64_cluster: bool = False,
    no_hooks: bool = False,
) -> None:
    print(f"Step: {get_utctimestring()}: Uninstalling Arc Agents' Helm release")
    if no_hooks:
        cmd_helm_delete = [
            helm_client_location,
            "delete",
            "azure-arc",
            "--namespace",
            release_namespace,
            "--no-hooks",
        ]
    else:
        cmd_helm_delete = [
            helm_client_location,
            "delete",
            "azure-arc",
            "--namespace",
            release_namespace,
        ]
    if is_arm64_cluster:
        cmd_helm_delete.extend(["--timeout", "15m"])
    if kube_config:
        cmd_helm_delete.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])
    response_helm_delete = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
    _, error_helm_delete = response_helm_delete.communicate()
    if response_helm_delete.returncode != 0:
        if (
            "forbidden" in error_helm_delete.decode("ascii")
            or "Error: warning: Hook pre-delete" in error_helm_delete.decode("ascii")
            or "Error: timed out waiting for the condition"
            in error_helm_delete.decode("ascii")
        ):
            telemetry.set_user_fault()
        telemetry.set_exception(
            exception=error_helm_delete.decode("ascii"),
            fault_type=consts.Delete_HelmRelease_Fault_Type,
            summary="Unable to delete helm release",
        )
        err_msg = (
            "Error occured while cleaning up arc agents. Helm release deletion failed: "
            + error_helm_delete.decode("ascii")
            + f" Please run 'helm delete azure-arc --namespace {release_namespace}' to ensure that "
            "the release is deleted."
        )
        raise CLIInternalError(err_msg)
    ensure_namespace_cleanup()
    # Cleanup azure-arc-release NS if present (created during helm installation)
    cleanup_release_install_namespace_if_exists()


def cleanup_release_install_namespace_if_exists() -> None:
    print(
        f"Step: {get_utctimestring()}: Clean up release namespace '{consts.Release_Install_Namespace}'."
    )
    api_instance = kube_client.CoreV1Api()
    try:
        api_instance.read_namespace(consts.Release_Install_Namespace)
    except ApiException as ex:
        if ex.status == 404:
            # Nothing to delete, exiting here
            return

        kubernetes_exception_handler(
            ex,
            consts.Get_Kubernetes_Helm_Release_Namespace_Fault_Type,
            error_message="Unable to fetch details about existense of kubernetes "
            f"namespace: {consts.Release_Install_Namespace}",
            summary="Unable to fetch kubernetes "
            f"namespace: {consts.Release_Install_Namespace}",
        )

    # If namespace exists, delete it
    try:
        api_instance.delete_namespace(consts.Release_Install_Namespace)
    except ApiException as ex:
        kubernetes_exception_handler(
            ex,
            consts.Delete_Kubernetes_Helm_Release_Namespace_Fault_Type,
            error_message="Unable to clean-up kubernetes "
            f"namespace: {consts.Release_Install_Namespace}",
            summary="Unable to delete kubernetes "
            f"namespace: {consts.Release_Install_Namespace}",
        )


# DO NOT use this method for re-put scenarios. This method involves new NS creation for helm release. For re-put scenarios, brownfield scenario needs to be handled where helm release still stays in default NS
def helm_install_release(
    resource_manager: str,
    chart_path: str,
    kubernetes_distro: str,
    kubernetes_infra: str,
    location: str,
    private_key_pem: str,
    kube_config: str | None,
    kube_context: str | None,
    no_wait: bool,
    values_file: str | None,
    cloud_name: str,
    enable_custom_locations: bool,
    custom_locations_oid: str,
    helm_client_location: str,
    enable_private_link: bool | None,
    arm_metadata: dict[str, Any],
    helm_content_values: dict[str, Any],
    registry_path: str,
    aad_identity_principal_id: str | None,
    onboarding_timeout: str = consts.DEFAULT_MAX_ONBOARDING_TIMEOUT_HELMVALUE_SECONDS,
) -> None:
    cmd_helm_install = [
        helm_client_location,
        "upgrade",
        "--install",
        "azure-arc",
        chart_path,
        "--set",
        f"global.kubernetesDistro={kubernetes_distro}",
        "--set",
        f"global.kubernetesInfra={kubernetes_infra}",
        "--set",
        f"global.onboardingPrivateKey={private_key_pem}",
        "--set",
        "systemDefaultValues.spnOnboarding=false",
        "--set",
        f"global.azureEnvironment={cloud_name}",
        "--set",
        "systemDefaultValues.clusterconnect-agent.enabled=true",
        "--namespace",
        f"{consts.Release_Install_Namespace}",
        "--create-namespace",
        "--output",
        "json",
    ]

    # Special configurations from 2022-09-01 ARM metadata.
    if "dataplaneEndpoints" in arm_metadata:
        if "arcConfigEndpoint" in arm_metadata["dataplaneEndpoints"]:
            notification_endpoint = arm_metadata["dataplaneEndpoints"][
                "arcGlobalNotificationServiceEndpoint"
            ]
            config_endpoint = arm_metadata["dataplaneEndpoints"]["arcConfigEndpoint"]
            his_endpoint = arm_metadata["dataplaneEndpoints"][
                "arcHybridIdentityServiceEndpoint"
            ]
            if his_endpoint[-1] != "/":
                his_endpoint = his_endpoint + "/"
            his_endpoint = (
                his_endpoint + f"discovery?location={location}&api-version=1.0-preview"
            )
            relay_endpoint = arm_metadata["suffixes"]["relayEndpointSuffix"]
            active_directory = arm_metadata["authentication"]["loginEndpoint"]
            if not aad_identity_principal_id:
                raise CLIInternalError(
                    "Failed to create the kubeAadEndpoint endpoint. The identity "
                    "principal ID of the created connected cluster is empty."
                )
            kube_aad_endpoint = f"{aad_identity_principal_id}.k8sproxysvc.connectrp.azs"
            cmd_helm_install.extend(
                [
                    "--set",
                    f"global.kubeAadEndpoint={kube_aad_endpoint}",
                    "--set",
                    f"systemDefaultValues.azureResourceManagerEndpoint={resource_manager}",
                    "--set",
                    f"systemDefaultValues.azureArcAgents.config_dp_endpoint_override={config_endpoint}",
                    "--set",
                    f"systemDefaultValues.clusterconnect-agent.notification_dp_endpoint_override={notification_endpoint}",
                    "--set",
                    f"systemDefaultValues.clusterconnect-agent.relay_endpoint_suffix_override={relay_endpoint}",
                    "--set",
                    f"systemDefaultValues.clusteridentityoperator.his_endpoint_override={his_endpoint}",
                    "--set",
                    f"systemDefaultValues.activeDirectoryEndpoint={active_directory}",
                    "--set",
                    "systemDefaultValues.image.repository={}".format(
                        registry_path.split("/")[0]
                    ),
                ]
            )
        else:
            logger.debug(
                "'arcConfigEndpoint' doesn't exist under 'dataplaneEndpoints' in the ARM metadata."
            )

    # Add helmValues content response from DP
    cmd_helm_install = parse_helm_values(helm_content_values, cmd_helm=cmd_helm_install)

    # Add custom-locations related params
    if enable_custom_locations and not enable_private_link:
        cmd_helm_install.extend(
            ["--set", "systemDefaultValues.customLocations.enabled=true"]
        )
        cmd_helm_install.extend(
            [
                "--set",
                f"systemDefaultValues.customLocations.oid={custom_locations_oid}",
            ]
        )
    # Disable cluster connect if private link is enabled
    if enable_private_link is True:
        cmd_helm_install.extend(
            ["--set", "systemDefaultValues.clusterconnect-agent.enabled=false"]
        )
    # To set some other helm parameters through file
    if values_file:
        cmd_helm_install.extend(["-f", values_file])
    if kube_config:
        cmd_helm_install.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])
    if not no_wait:
        # Change --timeout format for helm client to understand
        onboarding_timeout = onboarding_timeout + "s"
        cmd_helm_install.extend(["--wait", "--timeout", f"{onboarding_timeout}"])
    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        helm_install_error_message = error_helm_install.decode("ascii")
        helm_install_error_message = process_helm_error_detail(
            helm_install_error_message
        )
        helm_error_detail = {
            "Context.Default.AzureCLI.onboardingErrorType": consts.Install_HelmRelease_Fault_Type,
            "Context.Default.AzureCLI.onboardingErrorMessage": helm_install_error_message,
        }
        # Replace the existing calls with the new function

        telemetry.add_extension_event("connectedk8s", helm_error_detail)
        if any(
            message in helm_install_error_message
            for message in consts.Helm_Install_Release_Userfault_Messages
        ):
            telemetry.set_user_fault()
        telemetry.set_exception(
            exception=helm_install_error_message,
            fault_type=consts.Install_HelmRelease_Fault_Type,
            summary="Unable to install helm release",
        )
        warn_msg = (
            "Please check if the azure-arc namespace was deployed and run 'kubectl get pods -n azure-arc' "
            "to check if all the pods are in running state. A possible cause for pods stuck in pending "
            "state could be insufficient resources on the kubernetes cluster to onboard to arc."
            "Also pod logs can be checked using kubectl logs <pod-name> -n azure-arc.\n"
        )
        logger.warning(warn_msg)
        raise CLIInternalError(
            f"Unable to install helm release: {helm_install_error_message}"
        )


def process_helm_error_detail(helm_error_detail: str) -> str:
    helm_error_detail = remove_rsa_private_key(helm_error_detail)
    helm_error_detail = scrub_proxy_url(helm_error_detail)
    helm_error_detail = redact_base64_strings(helm_error_detail)
    helm_error_detail = redact_sensitive_fields_from_string(helm_error_detail)

    return helm_error_detail


def remove_rsa_private_key(input_text: str) -> str:
    # Regex to identify RSA private key
    rsa_key_pattern = re.compile(
        r"-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----", re.DOTALL
    )
    # Search for the key in the input text
    if rsa_key_pattern.search(input_text):
        # Remove the RSA private key
        return rsa_key_pattern.sub("[RSA PRIVATE KEY REMOVED]", input_text)
    return input_text


def scrub_proxy_url(proxy_url_str: str) -> str:
    regex = re.compile(r"://.*?:.*?@")
    # Replace matches with "://[REDACTED]:[REDACTED]@"
    proxy_url_str = regex.sub("://[REDACTED]:[REDACTED]@", proxy_url_str)
    return proxy_url_str


def redact_base64_strings(content: str) -> str:
    base64_pattern = r"\b[A-Za-z0-9+/=]{40,}\b"
    return re.sub(base64_pattern, "[REDACTED]", content)


def redact_sensitive_fields_from_string(input_text: str) -> str:
    # Define regex patterns for keys
    patterns = {
        r"(username:\s*).*": r"\1[REDACTED]",
        r"(password:\s*).*": r"\1[REDACTED]",
        r"(token:\s*).*": r"\1[REDACTED]",
    }

    # Apply regex to redact sensitive fields
    for pattern, replacement in patterns.items():
        input_text = re.sub(pattern, replacement, input_text)

    # Return the redacted text
    return input_text


def get_release_namespace(
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
    release_name: str = "azure-arc",
) -> str | None:
    print(f"Step: {get_utctimestring()}: Get namespace of release: {release_name}")
    cmd_helm_release = [
        helm_client_location,
        "list",
        "-a",
        "--all-namespaces",
        "--output",
        "json",
    ]
    if kube_config:
        cmd_helm_release.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_release.extend(["--kube-context", kube_context])
    response_helm_release = Popen(cmd_helm_release, stdout=PIPE, stderr=PIPE)
    output_helm_release, error_helm_release = response_helm_release.communicate()
    if response_helm_release.returncode != 0:
        error = error_helm_release.decode("ascii")
        if "forbidden" in error or "Kubernetes cluster unreachable" in error:
            telemetry.set_user_fault()

        telemetry.set_exception(
            exception=error,
            fault_type=consts.List_HelmRelease_Fault_Type,
            summary="Unable to list helm release",
        )
        raise CLIInternalError(f"Helm list release failed: {error}")

    output_helm_release_str = output_helm_release.decode("ascii")
    try:
        output_helm_release_dict = json.loads(output_helm_release_str)
    except json.decoder.JSONDecodeError:
        return None
    for release in output_helm_release_dict:
        if release["name"] == release_name:
            namespace: str = release["namespace"]
            return namespace
    return None


def flatten(dd: Any, separator: str = ".", prefix: str = "") -> dict[str, Any]:
    try:
        if isinstance(dd, dict):
            return {
                prefix + separator + k if prefix else k: v
                for kk, vv in dd.items()
                for k, v in flatten(vv, separator, kk).items()
            }

        return {prefix: dd}

    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Error_Flattening_User_Supplied_Value_Dict,
            summary="Error while flattening the user supplied helm values dict",
        )
        raise CLIInternalError(
            "Error while flattening the user supplied helm values dict"
        )


def check_features_to_update(features_to_update: list[str]) -> tuple[bool, bool, bool]:
    update_cluster_connect, update_azure_rbac, update_cl = False, False, False
    for feature in features_to_update:
        if feature == "cluster-connect":
            update_cluster_connect = True
        elif feature == "azure-rbac":
            update_azure_rbac = True
        elif feature == "custom-locations":
            update_cl = True
    return update_cluster_connect, update_azure_rbac, update_cl


def user_confirmation(message: str, yes: bool = False) -> None:
    if yes:
        return
    try:
        if not prompt_y_n(message):
            raise ManualInterrupt("Operation cancelled.")
    except NoTTYException:
        raise CLIInternalError(
            "Unable to prompt for confirmation as no tty available. Use --yes."
        )


def is_guid(guid: str) -> bool:
    import uuid

    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


def check_provider_registrations(
    cli_ctx: AzCli,
    subscription_id: str,
    is_gateway_enabled: bool,
    is_workload_identity_enabled: bool,
) -> None:
    print(f"Step: {get_utctimestring()}: Checking Provider Registrations")
    try:
        rp_client = resource_providers_client(cli_ctx, subscription_id)
        cc_registration_state = rp_client.get(
            consts.Connected_Cluster_Provider_Namespace
        ).registration_state
        if cc_registration_state not in consts.allowed_rp_registration_states:
            telemetry.set_exception(
                exception=f"{consts.Connected_Cluster_Provider_Namespace} provider is not registered",
                fault_type=consts.CC_Provider_Namespace_Not_Registered_Fault_Type,
                summary=f"{consts.Connected_Cluster_Provider_Namespace} provider is not registered",
            )
            err_msg = (
                f"{consts.Connected_Cluster_Provider_Namespace} provider is not registered. Please register it using 'az provider register -n 'Microsoft."
                "Kubernetes' before running the connect command."
            )
            raise ValidationError(err_msg)
        kc_registration_state = rp_client.get(
            consts.Kubernetes_Configuration_Provider_Namespace
        ).registration_state
        if kc_registration_state not in consts.allowed_rp_registration_states:
            if is_workload_identity_enabled:
                telemetry.set_exception(
                    exception=f"{consts.Kubernetes_Configuration_Provider_Namespace} provider is not registered",
                    fault_type=consts.Kubernetes_Configuration_Provider_Namespace_Not_Registered_Fault_Type,
                    summary=f"{consts.Kubernetes_Configuration_Provider_Namespace} provider is not registered",
                )
                err_msg = (
                    f"{consts.Kubernetes_Configuration_Provider_Namespace} provider is not registered. Please register it using 'az provider register -n 'Microsoft."
                    "KubernetesConfiguration' before running the connect command."
                )
                raise ValidationError(err_msg)

            telemetry.set_user_fault()
            logger.warning(
                "%s provider is not registered",
                consts.Kubernetes_Configuration_Provider_Namespace,
            )
        if is_gateway_enabled:
            hc_registration_state = rp_client.get(
                consts.Hybrid_Compute_Provider_Namespace
            ).registration_state
            if hc_registration_state not in consts.allowed_rp_registration_states:
                telemetry.set_exception(
                    exception=f"{consts.Hybrid_Compute_Provider_Namespace} provider is not registered",
                    fault_type=consts.HC_Provider_Namespace_Not_Registered_Fault_Type,
                    summary=f"{consts.Hybrid_Compute_Provider_Namespace} provider is not registered",
                )
                err_msg = (
                    f"{consts.Hybrid_Compute_Provider_Namespace} provider is not registered. Please register it using 'az provider register -n 'Microsoft."
                    "HybridCompute' before running the connect command."
                )
                raise ValidationError(err_msg)
    except ValidationError as e:
        raise e
    except Exception:
        logger.exception("Couldn't check the required provider's registration status")


def can_create_clusterrolebindings() -> bool | str:
    try:
        api_instance = kube_client.AuthorizationV1Api()
        access_review = kube_client.V1SelfSubjectAccessReview(
            spec={
                "resourceAttributes": {
                    "verb": "create",
                    "resource": "clusterrolebindings",
                    "group": "rbac.authorization.k8s.io",
                }
            }
        )
        response = api_instance.create_self_subject_access_review(access_review)
        allowed: bool = response.status.allowed
        return allowed
    except Exception as ex:
        warn_msg = (
            "Couldn't check for the permission to create clusterrolebindings on this k8s cluster. "
            f"Error: {ex}"
        )
        logger.warning(warn_msg)
        return "Unknown"


def validate_node_api_response(api_instance: CoreV1Api) -> V1NodeList | None:
    try:
        node_api_response = api_instance.list_node()
        return node_api_response
    except Exception:
        logger.debug(
            "Error occcured while listing nodes on this kubernetes cluster:",
            exc_info=True,
        )
        return None


def az_cli(args_str: str) -> Any:
    args = args_str.split()
    cli: AzCli = get_default_cli()
    with open(os.devnull, "w") as devnull:
        cli.invoke(args, out_file=devnull)
    if cli.result.result:
        return cli.result.result
    if cli.result.error:
        raise CLIInternalError(f"'az ${args_str}' failed: {cli.result.error}")
    return True


def is_cli_using_msal_auth() -> bool:
    response_cli_version = az_cli("version --output json")
    try:
        cli_version = response_cli_version["azure-cli"]
    except Exception as ex:
        raise CLIInternalError(f"Unable to decode the az cli version installed: {ex}")
    v1 = cli_version
    v2 = consts.AZ_CLI_ADAL_TO_MSAL_MIGRATE_VERSION
    for i, j in zip(map(int, v1.split(".")), map(int, v2.split("."))):
        if i == j:
            continue
        return i > j
    return len(v1.split(".")) == len(v2.split("."))


def get_metadata(arm_endpoint: str, api_version: str = "2022-09-01") -> dict[str, Any]:
    metadata_url_suffix = f"/metadata/endpoints?api-version={api_version}"
    metadata_endpoint = None
    try:
        import requests

        session = requests.Session()
        metadata_endpoint = arm_endpoint + metadata_url_suffix
        response = session.get(metadata_endpoint)
        if response.status_code == 200:
            metadata: dict[str, Any] = response.json()
            return metadata

        msg = f"ARM metadata endpoint '{metadata_endpoint}' returned status code {response.status_code}."
        raise HttpResponseError(msg)

    except Exception as err:
        msg = f"Failed to request ARM metadata {metadata_endpoint}."
        print(msg, file=sys.stderr)
        print(
            f"Please ensure you have network connection. Error: {err}",
            file=sys.stderr,
        )
        arm_exception_handler(err, msg, "Failed to get ARM metadata")

    assert False


def parse_helm_values(
    helm_content_values: dict[str, Any], cmd_helm: list[str]
) -> list[str]:
    for helm_param, helm_value in helm_content_values.items():
        if helm_param == "global.proxyCert":
            cmd_helm.extend(["--set-file", f"{helm_param}={helm_value}"])
            continue
        cmd_helm.extend(["--set", f"{helm_param}={helm_value}"])

    return cmd_helm


def get_utctimestring() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())


def helm_update_agent(
    helm_client_location: str,
    kube_config: str | None,
    kube_context: str | None,
    helm_content_values: dict[str, Any],
    values_file: str | None,
    cluster_name: str,
    release_namespace: str,
    chart_path: str,
) -> None:
    cmd_helm_values = [
        helm_client_location,
        "get",
        "values",
        "azure-arc",
        "--namespace",
        release_namespace,
    ]
    if kube_config:
        cmd_helm_values.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_values.extend(["--kube-context", kube_context])

    user_values_location = os.path.join(
        os.path.expanduser("~"), ".azure", "userValues.txt"
    )
    with open(user_values_location, "w+") as existing_user_values:
        response_helm_values_get = Popen(
            cmd_helm_values, stdout=existing_user_values, stderr=PIPE
        )
        _, error_helm_get_values = response_helm_values_get.communicate()

    if response_helm_values_get.returncode != 0:
        error = error_helm_get_values.decode("ascii")
        if "forbidden" in error or "timed out waiting for the condition" in error:
            telemetry.set_user_fault()
            telemetry.set_exception(
                exception=error,
                fault_type=consts.Get_Helm_Values_Failed,
                summary="Error while doing helm get values azure-arc",
            )
            raise CLIInternalError(str.format(consts.Update_Agent_Failure, error))

    cmd_helm_upgrade = [
        helm_client_location,
        "upgrade",
        "azure-arc",
        chart_path,
        "--namespace",
        release_namespace,
        "-f",
        user_values_location,
        "--wait",
        "--output",
        "json",
    ]
    # Add helmValues content response from DP
    cmd_helm_upgrade = parse_helm_values(helm_content_values, cmd_helm=cmd_helm_upgrade)
    if values_file:
        cmd_helm_upgrade.extend(["-f", values_file])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    response_helm_upgrade = Popen(cmd_helm_upgrade, stdout=PIPE, stderr=PIPE)
    _, error_helm_upgrade = response_helm_upgrade.communicate()
    if response_helm_upgrade.returncode != 0:
        helm_upgrade_error_message = error_helm_upgrade.decode("ascii")
        if any(
            message in helm_upgrade_error_message
            for message in consts.Helm_Install_Release_Userfault_Messages
        ):
            telemetry.set_user_fault()
        telemetry.set_exception(
            exception=helm_upgrade_error_message,
            fault_type=consts.Install_HelmRelease_Fault_Type,
            summary="Unable to install helm release",
        )
        with contextlib.suppress(OSError):
            os.remove(user_values_location)
        raise CLIInternalError(
            str.format(consts.Update_Agent_Failure, helm_upgrade_error_message)
        )

    logger.info(str.format(consts.Update_Agent_Success, cluster_name))
    with contextlib.suppress(OSError):
        os.remove(user_values_location)
