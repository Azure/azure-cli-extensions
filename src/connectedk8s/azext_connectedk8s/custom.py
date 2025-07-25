# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

import contextlib
import errno
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import stat
import tempfile
import time
from base64 import b64decode, b64encode
from concurrent.futures import ThreadPoolExecutor
from subprocess import DEVNULL, PIPE, Popen
from typing import TYPE_CHECKING, Any, Iterable

import oras.client  # type: ignore[import-untyped]
import yaml
from azure.cli.command_modules.role import graph_client_factory
from azure.cli.core import get_default_cli, telemetry
from azure.cli.core._profile import Profile
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    ClientRequestError,
    CLIInternalError,
    FileOperationError,
    InvalidArgumentValueError,
    ManualInterrupt,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
    ValidationError,
)
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from azure.core.exceptions import HttpResponseError
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from kubernetes import client as kube_client
from kubernetes import config
from kubernetes.config.kube_config import KubeConfigMerger
from packaging import version

import azext_connectedk8s._constants as consts
import azext_connectedk8s._precheckutils as precheckutils
import azext_connectedk8s._troubleshootutils as troubleshootutils
import azext_connectedk8s._utils as utils
import azext_connectedk8s.clientproxyhelper._binaryutils as proxybinaryutils
import azext_connectedk8s.clientproxyhelper._proxylogic as proxylogic
import azext_connectedk8s.clientproxyhelper._utils as clientproxyutils
from azext_connectedk8s._client_factory import (
    cf_connectedmachine,
    cf_resource_groups,
    resource_providers_client,
)
from azext_connectedk8s.clientproxyhelper._enums import ProxyStatus

from .vendored_sdks.preview_2024_07_01.models import (
    ArcAgentProfile,
    ArcAgentryConfigurations,
    ConnectedCluster,
    ConnectedClusterIdentity,
    ConnectedClusterPatch,
    Gateway,
    OidcIssuerProfile,
    SecurityProfile,
    SecurityProfileWorkloadIdentity,
)

if TYPE_CHECKING:
    from azure.cli.core.commands import AzCliCommand
    from azure.core.polling import LROPoller
    from Crypto.PublicKey.RSA import RsaKey
    from knack.commands import CLICommand
    from kubernetes.client import V1NodeList
    from kubernetes.config.kube_config import ConfigNode
    from requests.models import Response

    from azext_connectedk8s.vendored_sdks.preview_2024_07_01.operations import (
        ConnectedClusterOperations,
    )

logger = get_logger(__name__)
# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def create_connectedk8s(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    correlation_id: str | None = None,
    https_proxy: str = "",
    http_proxy: str = "",
    no_proxy: str = "",
    proxy_cert: str = "",
    location: str | None = None,
    kube_config: str | None = None,
    kube_context: str | None = None,
    no_wait: bool = False,
    tags: dict[str, str] | None = None,
    distribution: str = "generic",
    infrastructure: str = "generic",
    disable_auto_upgrade: bool = False,
    cl_oid: str | None = None,
    onboarding_timeout: str = consts.DEFAULT_MAX_ONBOARDING_TIMEOUT_HELMVALUE_SECONDS,
    enable_private_link: bool | None = None,
    private_link_scope_resource_id: str = "",
    distribution_version: str | None = None,
    azure_hybrid_benefit: str | None = None,
    skip_ssl_verification: bool = False,
    yes: bool = False,
    container_log_path: str | None = None,
    enable_oidc_issuer: bool = False,
    enable_workload_identity: bool = False,
    self_hosted_issuer: str = "",
    gateway_resource_id: str = "",
    configuration_settings: dict[str, Any] | None = None,
    configuration_protected_settings: dict[str, Any] | None = None,
) -> ConnectedCluster:
    logger.warning("This operation might take a while...\n")
    # changing cli config to push telemetry in 1 hr interval
    try:
        if cmd.cli_ctx and hasattr(cmd.cli_ctx, "config"):
            cmd.cli_ctx.config.set_value("telemetry", "push_interval_in_hours", "1")
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Failed_To_Change_Telemetry_Push_Interval,
            summary="Failed to change the telemetry push interval to 1 hr",
        )

    # Validate custom token operation
    custom_token_passed, location = utils.validate_custom_token(
        cmd, resource_group_name, location
    )
    assert location is not None

    # Prompt for confirmation for few parameters
    if enable_private_link is True:
        confirmation_message = (
            "The Cluster Connect and Custom Location features are not supported by Private Link at "
            "this time. Enabling Private Link will disable these features. Are you sure you want to continue?"
        )
        utils.user_confirmation(confirmation_message, yes)
        if cl_oid:
            logger.warning(
                "Private Link is being enabled, and Custom Location is not supported by Private Link at "
                "this time, so the '--custom-locations-oid' parameter will be ignored."
            )
    if azure_hybrid_benefit == "True":
        confirmation_message = (
            "I confirm I have an eligible Windows Server license with Azure Hybrid Benefit to "
            "apply this benefit to AKS on HCI or Windows Server. Visit https://aka.ms/ahb-aks for details"
        )
        utils.user_confirmation(confirmation_message, yes)

    # Setting subscription id and tenant Id
    subscription_id = (
        os.environ["AZURE_SUBSCRIPTION_ID"]
        if custom_token_passed is True
        else get_subscription_id(cmd.cli_ctx)
    )

    resource_id = (
        f"/subscriptions/{subscription_id}/resourcegroups/{resource_group_name}/providers/Microsoft.\
        Kubernetes/connectedClusters/{cluster_name}/location/{location}"
    )
    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.resourceid": resource_id}
    )

    # Send cloud information to telemetry
    azure_cloud = send_cloud_telemetry(cmd)

    # Checking provider registration status
    utils.check_provider_registrations(
        cmd.cli_ctx,
        subscription_id,
        is_gateway_enabled=bool(gateway_resource_id),
        is_workload_identity_enabled=(enable_workload_identity or enable_oidc_issuer),
    )

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    print(f"Step: {utils.get_utctimestring()}: Escape Proxy Settings, if passed in")

    # Escaping comma, forward slash present in https proxy urls, needed for helm params.
    https_proxy = escape_proxy_settings(https_proxy)

    # Escaping comma, forward slash present in http proxy urls, needed for helm params.
    http_proxy = escape_proxy_settings(http_proxy)

    # Escaping comma, forward slash present in no proxy urls, needed for helm params.
    no_proxy = escape_proxy_settings(no_proxy)

    # check whether proxy cert path exists
    if proxy_cert != "" and (not os.path.exists(proxy_cert)):
        telemetry.set_exception(
            exception="Proxy cert path does not exist",
            fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
            summary="Proxy cert path does not exist",
        )
        raise InvalidArgumentValueError(
            str.format(consts.Proxy_Cert_Path_Does_Not_Exist_Error, proxy_cert)
        )

    proxy_cert = proxy_cert.replace("\\", r"\\\\")

    (
        configuration_settings,
        configuration_protected_settings,
        redacted_protected_values,
    ) = add_config_protected_settings(
        http_proxy,
        https_proxy,
        no_proxy,
        proxy_cert,
        container_log_path,
        configuration_settings,
        configuration_protected_settings,
    )
    arc_agentry_configurations = generate_arc_agent_configuration(
        configuration_settings, configuration_protected_settings
    )

    gateway = None
    if gateway_resource_id != "":
        gateway = Gateway(enabled=True, resource_id=gateway_resource_id)

    arc_agent_profile = None
    if disable_auto_upgrade:
        arc_agent_profile = ArcAgentProfile(agent_auto_upgrade="Disabled")

    oidc_profile = None
    if enable_oidc_issuer:
        oidc_profile = set_oidc_issuer_profile(enable_oidc_issuer)

    security_profile = None
    if enable_workload_identity:
        security_profile = set_security_profile(enable_workload_identity)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        azure_cloud = consts.Azure_DogfoodCloudName

    arm_metadata = utils.get_metadata(cmd.cli_ctx.cloud.endpoints.resource_manager)
    config_dp_endpoint, release_train = get_config_dp_endpoint(
        cmd, location, values_file, arm_metadata
    )

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context, skip_ssl_verification)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    print(f"Step: {utils.get_utctimestring()}: Do node validations")
    api_instance = kube_client.CoreV1Api()
    node_api_response = utils.validate_node_api_response(api_instance)
    is_arm64_cluster = check_arm64_node(node_api_response)

    required_node_exists = check_linux_node(node_api_response)

    # check if this is aks_hci low bandwith scenario
    lowbandwidth = False
    lowbandwith_distros = [
        "aks_workload",
        "aks_management",
        "aks_edge_k3s",
        "aks_edge_k8s",
    ]

    if (infrastructure.lower() == "azure_stack_hci") and (
        distribution.lower() in lowbandwith_distros
    ):
        lowbandwidth = True

    azure_local_disconnected = False
    if os.getenv("AZURE_LOCAL_DISCONNECTED", "").lower() == "true":
        azure_local_disconnected = True

    # Install kubectl and helm
    try:
        kubectl_client_location = install_kubectl_client()
        helm_client_location = install_helm_client(cmd)
    except Exception as e:
        raise CLIInternalError(
            f"An exception has occured while trying to perform kubectl or helm install: {e}"
        )
    # Handling the user manual interrupt
    except KeyboardInterrupt:
        raise ManualInterrupt("Process terminated externally.")

    # Pre onboarding checks
    diagnostic_checks = "Failed"
    try:
        # if aks_hci lowbandwidth scenario or Azure local disconnected, skip, otherwise continue pre-onboarding check.
        if not azure_local_disconnected and not lowbandwidth:
            print(f"Step: {utils.get_utctimestring()}: Starting Pre-onboarding-check")
            batchv1_api_instance = kube_client.BatchV1Api()
            storage_space_available = True

            current_time = time.ctime(time.time())
            time_stamp = ""
            for elements in current_time:
                if elements == " ":
                    time_stamp += "-"
                    continue
                if elements == ":":
                    time_stamp += "."
                    continue
                time_stamp += elements
            time_stamp = cluster_name + "-" + time_stamp

            # Generate the diagnostic folder in a given location
            filepath_with_timestamp, diagnostic_folder_status = (
                utils.create_folder_diagnosticlogs(
                    time_stamp, consts.Pre_Onboarding_Check_Logs
                )
            )

            if diagnostic_folder_status is not True:
                storage_space_available = False

            # Performing cluster-diagnostic-checks
            diagnostic_checks, storage_space_available = (
                precheckutils.fetch_diagnostic_checks_results(
                    cmd,
                    api_instance,
                    batchv1_api_instance,
                    helm_client_location,
                    kubectl_client_location,
                    kube_config,
                    kube_context,
                    location,
                    http_proxy,
                    https_proxy,
                    no_proxy,
                    proxy_cert,
                    azure_cloud,
                    filepath_with_timestamp,
                    storage_space_available,
                )
            )
            precheckutils.fetching_cli_output_logs(
                filepath_with_timestamp, storage_space_available, 1
            )

            if storage_space_available is False:
                logger.warning(
                    "There is no storage space available on your device and hence not saving cluster "
                    "diagnostic check logs on your device"
                )

    except Exception as e:
        ex_msg = f"An exception occured while trying to execute pre-onboarding diagnostic checks : {e}"
        summ_msg = f"An exception occured while trying to execute pre-onboarding diagnostic checks : {e}"
        telemetry.set_exception(
            exception=ex_msg,
            fault_type=consts.Pre_Onboarding_Diagnostic_Checks_Execution_Failed,
            summary=summ_msg,
        )
        err_msg = (
            "An exception has occured while trying to execute pre-onboarding diagnostic checks : "
            f"{e}"
        )
        raise CLIInternalError(err_msg)

    # Handling the user manual interrupt
    except KeyboardInterrupt:
        with contextlib.suppress(Exception):
            troubleshootutils.fetching_cli_output_logs(
                filepath_with_timestamp, storage_space_available, 0
            )
        raise ManualInterrupt("Process terminated externally.")

    # If the checks didnt pass then stop the onboarding
    if (
        diagnostic_checks != consts.Diagnostic_Check_Passed
        and not azure_local_disconnected
        and not lowbandwidth
    ):
        if storage_space_available:
            logger.warning(
                "The pre-check result logs logs have been saved at this path: "
                "%s.\nThese logs can be attached while filing a support ticket for further assistance.\n",
                filepath_with_timestamp,
            )
        if diagnostic_checks == consts.Diagnostic_Check_Incomplete:
            telemetry.set_exception(
                exception="Cluster Diagnostic Prechecks Incomplete",
                fault_type=consts.Cluster_Diagnostic_Prechecks_Incomplete,
                summary="Cluster Diagnostic Prechecks didnt complete in the cluster",
            )
            err_msg = (
                "Execution of pre-onboarding checks failed. So not proceeding with cluster onboarding. Please "
                "meet the prerequisites - "
                + consts.Doc_Onboarding_PreRequisites_Url
                + " and try onboarding again."
            )
            raise ValidationError(err_msg)

        # if diagnostic_checks != consts.Diagnostic_Check_Incomplete
        telemetry.set_exception(
            exception="Cluster Diagnostic Prechecks Failed",
            fault_type=consts.Cluster_Diagnostic_Prechecks_Failed,
            summary="Cluster Diagnostic Prechecks Failed in the cluster",
        )
        err_msg = (
            "One or more pre-onboarding diagnostic checks failed and hence not proceeding with "
            "cluster onboarding. Please resolve them and try onboarding again."
        )
        raise ValidationError(err_msg)

    if not azure_local_disconnected and not lowbandwidth:
        print(
            f"Step: {utils.get_utctimestring()}: The required pre-checks for onboarding have succeeded."
        )
    else:
        print(
            f"Step: {utils.get_utctimestring()}: Skipped onboarding pre-checks for AKS-HCI low bandwidth scenario. "
            "Continuing..."
        )

    if not required_node_exists:
        telemetry.set_user_fault()
        telemetry.set_exception(
            exception="Couldn't find any node on the kubernetes cluster with the OS 'linux'",
            fault_type=consts.Linux_Node_Not_Exists,
            summary="Couldn't find any node on the kubernetes cluster with the OS 'linux'",
        )
        logger.warning(
            "Please ensure that this Kubernetes cluster has any nodes with OS 'linux', for scheduling the "
            "Arc-Agents onto and connecting to Azure. Learn more at %s",
            "https://aka.ms/ArcK8sSupportedOSArchitecture",
        )

    print(
        f"Step: {utils.get_utctimestring()}: Checking if user can create ClusterRoleBindings"
    )
    crb_permission = utils.can_create_clusterrolebindings()
    if not crb_permission or crb_permission == "Unknown":
        ex_msg = "Your credentials doesn't have permission to create clusterrolebindings on this kubernetes cluster."
        summ_msg = "Your credentials doesn't have permission to create clusterrolebindings on this kubernetes cluster."
        telemetry.set_exception(
            exception=ex_msg,
            fault_type=consts.Cannot_Create_ClusterRoleBindings_Fault_Type,
            summary=summ_msg,
        )
        err_msg = (
            "Your credentials doesn't have permission to create clusterrolebindings on this "
            "kubernetes cluster. Please check your permissions."
        )
        raise ValidationError(err_msg)

    print(
        f"Step: {utils.get_utctimestring()}: Determining Cluster Distribution and Infrastructure"
    )
    # Get kubernetes cluster info
    if distribution == "generic":
        kubernetes_distro = get_kubernetes_distro(
            node_api_response
        )  # (cluster heuristics)
    else:
        kubernetes_distro = distribution

    if infrastructure == "generic":
        kubernetes_infra = get_kubernetes_infra(
            node_api_response
        )  # (cluster heuristics)
    else:
        kubernetes_infra = infrastructure

    kubernetes_properties = {
        "Context.Default.AzureCLI.KubernetesVersion": kubernetes_version,
        "Context.Default.AzureCLI.KubernetesDistro": kubernetes_distro,
        "Context.Default.AzureCLI.KubernetesInfra": kubernetes_infra,
    }
    telemetry.add_extension_event("connectedk8s", kubernetes_properties)

    # Checking if it is an AKS cluster
    is_aks_cluster = check_aks_cluster(kube_config, kube_context)
    if is_aks_cluster:
        logger.warning(
            "Connecting an Azure Kubernetes Service (AKS) cluster to Azure Arc is only required for "
            "running Arc enabled services like App Services and Data Services on the cluster. Other "
            "features like Azure Monitor and Azure Defender are natively available on AKS. "
            "Learn more at %s.",
            "https://go.microsoft.com/fwlink/?linkid=2144200",
        )

    # Validate location
    print(
        f"Step: {utils.get_utctimestring()}: Checking Connect RP is available in the Location passed in."
    )
    utils.validate_connect_rp_location(cmd, location)
    resourceClient = cf_resource_groups(cmd.cli_ctx, subscription_id=subscription_id)

    # Validate location of private link scope resource. Throws error only if there is a location mismatch
    if enable_private_link is True:
        print(
            f"Step: {utils.get_utctimestring()}: Validate location of PrviateLinkScope passed in."
        )
        try:
            pls_arm_id_arr = private_link_scope_resource_id.split("/")
            hc_client = cf_connectedmachine(cmd.cli_ctx, pls_arm_id_arr[2])
            pls_get_result = hc_client.get(pls_arm_id_arr[4], pls_arm_id_arr[8])
            pls_location = pls_get_result.location.lower()
            if pls_location != location.lower():
                ex_msg = "Connected cluster resource and Private link scope resource are present in different locations"
                telemetry.set_exception(
                    exception=ex_msg,
                    fault_type=consts.Pls_Location_Mismatch_Fault_Type,
                    summary="Pls resource location mismatch",
                )
                err_msg = (
                    "The location of the private link scope resource does not match the location "
                    "of connected cluster resource. Please ensure that both the resources are in the same azure "
                    "location."
                )
                raise ArgumentUsageError(err_msg)
        except ArgumentUsageError as argex:
            raise (argex)
        except Exception as ex:
            if (
                isinstance(ex, HttpResponseError)
                and ex.response is not None
                and ex.response.status_code == 404
            ):
                telemetry.set_exception(
                    exception="Private link scope resource does not exist",
                    fault_type=consts.Pls_Resource_Not_Found,
                    summary="Pls resource does not exist",
                )
                err_msg = (
                    f"The private link scope resource '{private_link_scope_resource_id}' does not exist. Please ensure that "
                    "you pass a valid ARM Resource Id."
                )
                raise ArgumentUsageError(err_msg)
            logger.warning(
                "Error occured while checking the private link scope resource location: %s\n",
                ex,
            )

    # Check Previous Azure-Arc release's Existance
    print(
        f"Step: {utils.get_utctimestring()}: Check if an earlier azure-arc release exists"
    )
    release_namespace = utils.get_release_namespace(
        kube_config, kube_context, helm_client_location
    )

    if release_namespace:
        print(
            f"Step: {utils.get_utctimestring()}: Found an earlier instance of azure-arc release"
        )
        # Loading config map
        api_instance = kube_client.CoreV1Api()
        try:
            configmap = api_instance.read_namespaced_config_map(
                "azure-clusterconfig", "azure-arc"
            )
        except Exception as e:  # pylint: disable=broad-except
            not_found_msg = (
                "The helm release 'azure-arc' is present but azure-arc namespace/configmap is missing "
                f"is missing. Please run 'helm delete azure-arc --namespace {release_namespace} --no-hooks' to cleanup the release "
                "before onboarding the cluster again."
            )
            utils.kubernetes_exception_handler(
                e,
                consts.Read_ConfigMap_Fault_Type,
                "Unable to read ConfigMap",
                error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                message_for_not_found=not_found_msg,
            )
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            cluster_resource: ConnectedCluster
            public_key: str

            try:
                cluster_resource = client.get(configmap_rg_name, configmap_cluster_name)
                public_key = cluster_resource.agent_public_key_certificate
            except Exception as e:  # pylint: disable=broad-except
                utils.arm_exception_handler(
                    e,
                    consts.Get_ConnectedCluster_Fault_Type,
                    "Failed to check if connected cluster resource already exists.",
                )

            if (
                configmap_rg_name.lower() != resource_group_name.lower()
                or configmap_cluster_name.lower() != cluster_name.lower()
            ):
                telemetry.set_exception(
                    exception="The kubernetes cluster is already onboarded",
                    fault_type=consts.Cluster_Already_Onboarded_Fault_Type,
                    summary="Kubernetes cluster already onboarded",
                )
                err_msg = (
                    "The kubernetes cluster you are trying to onboard is already onboarded to "
                    f"the resource group '{configmap_rg_name}' with resource name '{configmap_cluster_name}'."
                )
                logger.warning(consts.Cluster_Already_Onboarded_Error)
                raise ArgumentUsageError(err_msg)

            # Re-put connected cluster
            # If cluster is of kind provisioned cluster, there are several properties that cannot be updated
            validate_existing_provisioned_cluster_for_reput(
                cluster_resource,
                kubernetes_distro,
                kubernetes_infra,
                enable_private_link,
                private_link_scope_resource_id,
                distribution_version,
                azure_hybrid_benefit,
                location,
            )

            cc = generate_request_payload(
                location,
                public_key,
                tags,
                kubernetes_distro,
                kubernetes_infra,
                enable_private_link,
                private_link_scope_resource_id,
                distribution_version,
                azure_hybrid_benefit,
                oidc_profile,
                security_profile,
                gateway,
                arc_agentry_configurations,
                arc_agent_profile,
            )
            cc_poller = create_cc_resource(
                client, resource_group_name, cluster_name, cc, no_wait
            )
            dp_request_payload = cc_poller.result()
            cc_response: ConnectedCluster = LongRunningOperation(cmd.cli_ctx)(cc_poller)
            # Disabling cluster-connect if private link is getting enabled
            if enable_private_link is True:
                disable_cluster_connect(
                    cmd,
                    client,
                    resource_group_name,
                    cluster_name,
                    kube_config,
                    kube_context,
                    values_file,
                    release_namespace,
                    helm_client_location,
                )

            # Perform helm upgrade if gateway
            if gateway is not None:
                # Update arc agent configuration to include protected parameters in dp call
                arc_agentry_configurations = generate_arc_agent_configuration(
                    configuration_settings,
                    redacted_protected_values,
                    is_dp_call=True,
                )
                dp_request_payload.arc_agentry_configurations = (
                    arc_agentry_configurations
                )

                # Perform DP health check
                _ = utils.health_check_dp(cmd, config_dp_endpoint)

                # Retrieving Helm chart OCI Artifact location
                helm_values_dp = utils.get_helm_values(
                    cmd,
                    config_dp_endpoint,
                    release_train,
                    connected_cluster=dp_request_payload,
                )

                registry_path = (
                    os.getenv("HELMREGISTRY") or helm_values_dp["repositoryPath"]
                )

                if registry_path == "":
                    registry_path = utils.get_helm_registry(
                        cmd, config_dp_endpoint, release_train
                    )

                # Get azure-arc agent version for telemetry
                azure_arc_agent_version = registry_path.split(":")[1]
                telemetry.add_extension_event(
                    "connectedk8s",
                    {"Context.Default.AzureCLI.AgentVersion": azure_arc_agent_version},
                )

                # Get helm chart path
                chart_path = utils.get_chart_path(
                    registry_path, kube_config, kube_context, helm_client_location
                )

                helm_content_values = helm_values_dp["helmValuesContent"]

                # Substitute any protected helm values as the value for that will be 'redacted-<feature>-<protectedSetting>'
                for helm_parameter, helm_value in helm_content_values.items():
                    if "redacted" in helm_value:
                        _, feature, protectedSetting = helm_value.split(":")
                        helm_content_values[helm_parameter] = (
                            configuration_protected_settings[feature][protectedSetting]
                        )

                # Perform helm upgrade
                utils.helm_update_agent(
                    helm_client_location,
                    kube_config,
                    kube_context,
                    helm_content_values,
                    values_file,
                    cluster_name,
                    release_namespace,
                    chart_path,
                )
            return cc_response

        # else case
        logger.warning(
            "Cleaning up the stale arc agents present on the cluster before starting new onboarding."
        )
        # Explicit CRD Deletion
        crd_cleanup_force_delete(
            cmd, kubectl_client_location, kube_config, kube_context
        )
        # Cleaning up the cluster
        utils.delete_arc_agents(
            release_namespace,
            kube_config,
            kube_context,
            helm_client_location,
            is_arm64_cluster,
            True,
        )

    else:
        if connected_cluster_exists(client, resource_group_name, cluster_name):
            telemetry.set_exception(
                exception="The connected cluster resource already exists",
                fault_type=consts.Resource_Already_Exists_Fault_Type,
                summary="Connected cluster resource already exists",
            )
            err_msg = (
                f"The connected cluster resource {cluster_name} already exists "
                + " in the "
                f"resource group {resource_group_name} "
                + "and corresponds to a different Kubernetes cluster."
            )
            reco_msg = (
                "To onboard this Kubernetes cluster to Azure, specify different "
                "resource name or resource group name."
            )
            raise ArgumentUsageError(err_msg, recommendation=reco_msg)

        # cleanup of stuck CRD if release namespace is not present/deleted
        crd_cleanup_force_delete(
            cmd, kubectl_client_location, kube_config, kube_context
        )

    print(
        f"Step: {utils.get_utctimestring()}: Check if ResourceGroup exists.  Try to create if it doesn't"
    )
    # Resource group Creation
    if (
        resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id)
        is False
    ):
        from azure.cli.core.profiles import ResourceType

        ResourceGroup = cmd.get_models(
            "ResourceGroup", resource_type=ResourceType.MGMT_RESOURCE_RESOURCES
        )
        parameters = ResourceGroup(location=location)
        try:
            resourceClient.create_or_update(resource_group_name, parameters)
        except Exception as e:  # pylint: disable=broad-except
            utils.arm_exception_handler(
                e,
                consts.Create_ResourceGroup_Fault_Type,
                "Failed to create the resource group",
            )

    print(f"Step: {utils.get_utctimestring()}: Generating Public-Private Key pair")

    # Generate public-private key pair
    try:
        key_pair = RSA.generate(4096)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.KeyPair_Generate_Fault_Type,
            summary="Failed to generate public-private key pair",
        )
        raise CLIInternalError(f"Failed to generate public-private key pair: {e}")
    try:
        public_key = get_public_key(key_pair)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.PublicKey_Export_Fault_Type,
            summary="Failed to export public key",
        )
        raise CLIInternalError(f"Failed to export public key: {e}")
    try:
        private_key_pem = get_private_key(key_pair)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.PrivateKey_Export_Fault_Type,
            summary="Failed to export private key",
        )
        raise CLIInternalError(f"Failed to export private key: {e}")

    # Perform validation for self hosted issuer and set oidc issuer profile
    if enable_oidc_issuer:
        if (
            self_hosted_issuer == ""
            and kubernetes_distro in consts.Public_Cloud_Distribution_List
        ):
            raise ValidationError(
                f"Self hosted issuer is required for {kubernetes_distro} cluster when OIDC issuer is being enabled."
            )
        oidc_profile = set_oidc_issuer_profile(enable_oidc_issuer, self_hosted_issuer)

    print(f"Step: {utils.get_utctimestring()}: Generating ARM Request Payload")
    # Generate request payload
    cc = generate_request_payload(
        location,
        public_key,
        tags,
        kubernetes_distro,
        kubernetes_infra,
        enable_private_link,
        private_link_scope_resource_id,
        distribution_version,
        azure_hybrid_benefit,
        oidc_profile,
        security_profile,
        gateway,
        arc_agentry_configurations,
        arc_agent_profile,
    )

    print(f"Step: {utils.get_utctimestring()}: Azure resource provisioning has begun.")
    # Create connected cluster resource
    put_cc_poller = create_cc_resource(
        client, resource_group_name, cluster_name, cc, no_wait
    )
    dp_request_payload = put_cc_poller.result()
    put_cc_response: ConnectedCluster = LongRunningOperation(cmd.cli_ctx)(put_cc_poller)
    print(
        f"Step: {utils.get_utctimestring()}: Azure resource provisioning has finished."
    )

    # Checking if custom locations rp is registered and fetching oid if it is registered
    enable_custom_locations, custom_locations_oid = check_cl_registration_and_get_oid(
        cmd, cl_oid, subscription_id
    )

    # Update arc agent configuration to include protected parameters in dp call
    arc_agentry_configurations = generate_arc_agent_configuration(
        configuration_settings, redacted_protected_values, is_dp_call=True
    )
    dp_request_payload.arc_agentry_configurations = arc_agentry_configurations

    # Perform DP health check
    _ = utils.health_check_dp(cmd, config_dp_endpoint)

    # Retrieving Helm chart OCI Artifact location
    helm_values_dp = utils.get_helm_values(
        cmd, config_dp_endpoint, release_train, connected_cluster=dp_request_payload
    )

    registry_path = os.getenv("HELMREGISTRY") or helm_values_dp["repositoryPath"]

    if registry_path == "":
        registry_path = utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

    # Get azure-arc agent version for telemetry
    azure_arc_agent_version = registry_path.split(":")[1]
    telemetry.add_extension_event(
        "connectedk8s",
        {"Context.Default.AzureCLI.AgentVersion": azure_arc_agent_version},
    )

    # Get helm chart path
    chart_path = utils.get_chart_path(
        registry_path, kube_config, kube_context, helm_client_location
    )

    helm_content_values = helm_values_dp["helmValuesContent"]
    aad_identity_principal_id = put_cc_response.identity.principal_id

    # Substitute any protected helm values as the value for that will be 'redacted-<feature>-<protectedSetting>'
    for helm_parameter, helm_value in helm_content_values.items():
        if "redacted" in helm_value:
            _, feature, protectedSetting = helm_value.split(":")
            helm_content_values[helm_parameter] = configuration_protected_settings[
                feature
            ][protectedSetting]

    print(
        f"Step: {utils.get_utctimestring()}: Starting to install Azure arc agents on the Kubernetes cluster."
    )
    # Install azure-arc agents
    utils.helm_install_release(
        cmd.cli_ctx.cloud.endpoints.resource_manager,
        chart_path,
        kubernetes_distro,
        kubernetes_infra,
        location,
        private_key_pem,
        kube_config,
        kube_context,
        no_wait,
        values_file,
        azure_cloud,
        enable_custom_locations,
        custom_locations_oid,
        helm_client_location,
        enable_private_link,
        arm_metadata,
        helm_content_values,
        registry_path,
        aad_identity_principal_id,
        onboarding_timeout,
    )

    # Long Running Operation for Agent State
    # Agent state is used for feedback of workload identity extension installation
    # Cases for when to poll for agent state:
    #     - If OIDC is enabled and self hosted issuer is passed in, extension is not installed.
    #       Feedback loop is not enabled, do not poll for agent state.
    #     - If OIDC is enabled and self hosted issuer is empty, extension is installed.
    #       Need to poll for agent state.
    #     - If workload identity is enabled, extension is installed, poll for agent state.
    if (enable_oidc_issuer and self_hosted_issuer == "") or enable_workload_identity:
        print(
            f"Step: {utils.get_utctimestring()}: Wait for Agent State to reach terminal state, with timeout of {consts.Agent_State_Timeout}"
        )
        terminal, connected_cluster = poll_for_agent_state(
            client, resource_group_name, cluster_name
        )
        if terminal:
            print(
                f"Step: {utils.get_utctimestring()}: Agent state has reached terminal state."
            )
            return connected_cluster

        raise CLIInternalError(
            "Timed out waiting for Agent State to reach terminal state."
        )
    if cl_oid and enable_custom_locations and cl_oid == custom_locations_oid:
        logger.warning(consts.Manual_Custom_Location_Oid_Warning)
    return put_cc_response


def poll_for_agent_state(
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    timeout_minutes: int = consts.Agent_State_Timeout,
    interval: int = 5,
) -> tuple[bool, ConnectedCluster]:
    start_time = time.time()
    while True:
        connected_cluster = client.get(resource_group_name, cluster_name)
        state: str | None = (
            None
            if connected_cluster.arc_agent_profile is None
            else connected_cluster.arc_agent_profile.agent_state
        )
        if state is None or state in (
            consts.Agent_State_Succeeded,
            consts.Agent_State_Failed,
        ):
            return True, connected_cluster

        elapsed_time = time.time() - start_time
        if elapsed_time >= timeout_minutes * 60:
            return False, connected_cluster

        time.sleep(interval)


def validate_existing_provisioned_cluster_for_reput(
    cluster_resource: ConnectedCluster,
    kubernetes_distro: str,
    kubernetes_infra: str,
    enable_private_link: bool | None,
    private_link_scope_resource_id: str,
    distribution_version: str | None,
    azure_hybrid_benefit: str | None,
    location: str,
) -> None:
    if (cluster_resource.kind is not None) and (
        cluster_resource.kind.lower() == consts.Provisioned_Cluster_Kind
    ):
        err_msg = (
            "Updating the 'azure hybrid benefit' property of a Provisioned Cluster is not supported from the "
            "Connected Cluster CLI. Please use the 'az aksarc update' CLI command.\n"
            + consts.Doc_Provisioned_Cluster_Update_Url
        )
        if azure_hybrid_benefit is not None:
            raise InvalidArgumentValueError(err_msg)

        validation_values = [
            kubernetes_distro,
            kubernetes_infra,
            private_link_scope_resource_id,
            distribution_version,
            azure_hybrid_benefit,
            location,
        ]

        for value in validation_values:
            if value is not None:
                err_msg = (
                    "Updating the following properties of a Provisioned Cluster are not supported from the "
                    "Connected Cluster CLI: kubernetes_distro, kubernetes_infra, enable_private_link, "
                    "private_link_scope_resource_id, distribution_version, azure_hybrid_benefit, location, "
                    "public_key.\n\nPlease use the 'az aksarc update' CLI command. "
                    + consts.Doc_Provisioned_Cluster_Update_Url
                )
                raise InvalidArgumentValueError(err_msg)


def send_cloud_telemetry(cmd: CLICommand) -> str:
    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.AzureCloud": cmd.cli_ctx.cloud.name}
    )
    cloud_name: str = cmd.cli_ctx.cloud.name.upper()
    # Setting cloud name to format that is understood by golang SDK.
    if cloud_name == consts.PublicCloud_OriginalName:
        cloud_name = consts.Azure_PublicCloudName
    elif cloud_name == consts.USGovCloud_OriginalName:
        cloud_name = consts.Azure_USGovCloudName
    return cloud_name


def validate_env_file_dogfood(values_file: str | None) -> tuple[str | None, str | None]:
    if not values_file:
        telemetry.set_exception(
            exception="Helm environment file not provided",
            fault_type=consts.Helm_Environment_File_Fault_Type,
            summary="Helm environment file missing",
        )
        raise ValidationError(
            "Helm environment file is required when using Dogfood environment for onboarding the cluster.",
            recommendation="Please set the environment variable 'HELMVALUESPATH' to point to the file.",
        )

    with open(values_file) as f:
        try:
            env_dict = yaml.safe_load(f)
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Helm_Environment_File_Fault_Type,
                summary="Problem loading the helm environment file",
            )
            raise FileOperationError(
                "Problem loading the helm environment file: " + str(e)
            )
        try:
            assert env_dict.get("global").get("azureEnvironment") == "AZUREDOGFOOD"
            assert (
                env_dict.get("systemDefaultValues")
                .get("azureArcAgents")
                .get("config_dp_endpoint_override")
            )
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Helm_Environment_File_Fault_Type,
                summary="Problem loading the helm environment variables",
            )
            reco_str = (
                "Please check the values 'global.azureEnvironment' and "
                "'systemDefaultValues.azureArcAgents.config_dp_endpoint_override' in the file."
            )
            err_msg = (
                "The required helm environment variables for dogfood onboarding are either not present in the "
                "file or incorrectly set."
            )
            raise FileOperationError(err_msg, recommendation=reco_str)

    # Return the dp endpoint and release train
    dp_endpoint = (
        env_dict.get("systemDefaultValues")
        .get("azureArcAgents")
        .get("config_dp_endpoint_override")
    )
    release_train = (
        env_dict.get("systemDefaultValues").get("azureArcAgents").get("releaseTrain")
    )
    return dp_endpoint, release_train


def set_kube_config(kube_config: str | None) -> str | None:
    print(f"Step: {utils.get_utctimestring()}: Setting KubeConfig")
    if kube_config:
        # Trim kubeconfig. This is required for windows os.
        if kube_config.startswith(("'", '"')):
            kube_config = kube_config[1:]
        if kube_config.endswith(("'", '"')):
            kube_config = kube_config[:-1]
        return kube_config
    return None


def escape_proxy_settings(proxy_setting: str | None) -> str:
    if proxy_setting is None:
        return ""
    proxy_setting = proxy_setting.replace(",", r"\,")
    proxy_setting = proxy_setting.replace("/", r"\/")
    return proxy_setting


def check_kube_connection() -> str:
    print(f"Step: {utils.get_utctimestring()}: Checking Connectivity to Cluster")
    api_instance = kube_client.VersionApi()
    try:
        api_response = api_instance.get_code()
        git_version: str = api_response.git_version
        return git_version
    except Exception as e:  # pylint: disable=broad-except
        logger.warning(consts.KubeApi_Connectivity_Failed_Warning)
        utils.kubernetes_exception_handler(
            e,
            consts.Kubernetes_Connectivity_FaultType,
            "Unable to verify connectivity to the Kubernetes cluster",
        )

    assert False


def install_helm_client(cmd: CLICommand) -> str:
    print(
        f"Step: {utils.get_utctimestring()}: Install Helm client if it does not exist"
    )
    # Return helm client path set by user
    helm_client_path = os.getenv("HELM_CLIENT_PATH")
    if helm_client_path:
        return helm_client_path

    # Fetch system related info
    operating_system = platform.system().lower()
    machine_type = platform.machine()

    # Send machine telemetry
    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.MachineType": machine_type}
    )
    # Set helm binary download & install locations
    if operating_system == "windows":
        download_location_string = f".azure\\helm\\{consts.HELM_VERSION}"
        download_file_name = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip"
        install_location_string = (
            f".azure\\helm\\{consts.HELM_VERSION}\\{operating_system}-amd64\\helm.exe"
        )
        artifactTag = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64"
    elif operating_system == "linux" or operating_system == "darwin":
        download_location_string = f".azure/helm/{consts.HELM_VERSION}"
        download_file_name = (
            f"helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz"
        )
        install_location_string = (
            f".azure/helm/{consts.HELM_VERSION}/{operating_system}-amd64/helm"
        )
        artifactTag = f"helm-{consts.HELM_VERSION}-{operating_system}-amd64"
    else:
        telemetry.set_exception(
            exception="Unsupported OS for installing helm client",
            fault_type=consts.Helm_Unsupported_OS_Fault_Type,
            summary=f"{operating_system} is not supported for installing helm client",
        )
        raise ClientRequestError(
            f"The {operating_system} platform is not currently supported for installing helm client."
        )

    download_location = os.path.expanduser(os.path.join("~", download_location_string))
    download_dir = os.path.dirname(download_location)
    install_location = os.path.expanduser(os.path.join("~", install_location_string))

    # Download compressed Helm binary if not already present
    if not os.path.isfile(install_location):
        # Creating the helm folder if it doesnt exist
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                telemetry.set_exception(
                    exception=e,
                    fault_type=consts.Create_Directory_Fault_Type,
                    summary="Unable to create helm directory",
                )
                raise ClientRequestError("Failed to create helm directory." + str(e))

        # Downloading compressed helm client executable
        logger.warning(
            "Downloading helm client for first time. This can take few minutes..."
        )

        mcr_url = utils.get_mcr_path(cmd)

        client = oras.client.OrasClient(hostname=mcr_url)
        retry_count = 3
        retry_delay = 5
        for i in range(retry_count):
            try:
                client.pull(
                    target=f"{mcr_url}/{consts.HELM_MCR_URL}:{artifactTag}",
                    outdir=download_location,
                )
                break
            except Exception as e:
                if i == retry_count - 1:
                    if "Connection reset by peer" in str(e):
                        telemetry.set_user_fault()
                    telemetry.set_exception(
                        exception=e,
                        fault_type=consts.Download_Helm_Fault_Type,
                        summary="Unable to download helm client.",
                    )
                    raise CLIInternalError(
                        f"Failed to download helm client: {e}",
                        recommendation="Please check your internet connection.",
                    )
                time.sleep(retry_delay)

        # Extract the archive.
        try:
            extract_dir = download_location
            download_location = os.path.expanduser(
                os.path.join(download_location, download_file_name)
            )
            shutil.unpack_archive(download_location, extract_dir)
            os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Extract_HelmExe_Fault_Type,
                summary="Unable to extract helm executable",
            )
            reco_str = f"Please ensure that you delete the directory '{extract_dir}' before trying again."
            raise ClientRequestError(
                "Failed to extract helm executable." + str(e), recommendation=reco_str
            )

    return install_location


def resource_group_exists(
    ctx: AzCliCommand, resource_group_name: str, subscription_id: str | None = None
) -> bool:
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    return groups.check_existence(resource_group_name)


def connected_cluster_exists(
    client: ConnectedClusterOperations, resource_group_name: str, cluster_name: str
) -> bool:
    try:
        client.get(resource_group_name, cluster_name)
    except Exception as e:  # pylint: disable=broad-except
        utils.arm_exception_handler(
            e,
            consts.Get_ConnectedCluster_Fault_Type,
            "Failed to check if connected cluster resource already exists.",
            return_if_not_found=True,
        )
        return False
    return True


def get_default_config_dp_endpoint(cmd: CLICommand, location: str) -> str:
    active_directory_array = cmd.cli_ctx.cloud.endpoints.active_directory.split(".")
    # default for public, mc, ff clouds
    cloud_based_domain = active_directory_array[2]
    # special cases for USSec/USNat clouds
    if len(active_directory_array) == 4:
        cloud_based_domain = active_directory_array[2] + "." + active_directory_array[3]
    elif len(active_directory_array) == 5:
        cloud_based_domain = (
            active_directory_array[2]
            + "."
            + active_directory_array[3]
            + "."
            + active_directory_array[4]
        )

    config_dp_endpoint = (
        f"https://{location}.dp.kubernetesconfiguration.azure.{cloud_based_domain}"
    )
    return config_dp_endpoint


def get_config_dp_endpoint(
    cmd: CLICommand,
    location: str,
    values_file: str | None,
    arm_metadata: dict[str, Any] | None = None,
) -> tuple[str, str | None]:
    release_train = None
    config_dp_endpoint = None
    if arm_metadata is None:
        arm_metadata = utils.get_metadata(cmd.cli_ctx.cloud.endpoints.resource_manager)
    # Read and validate the helm values file for Dogfood.
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        config_dp_endpoint, release_train = validate_env_file_dogfood(values_file)
    # Get the values or endpoints required for retreiving the Helm registry URL.
    if "dataplaneEndpoints" in arm_metadata:
        if "arcConfigEndpoint" in arm_metadata["dataplaneEndpoints"]:
            config_dp_endpoint = arm_metadata["dataplaneEndpoints"]["arcConfigEndpoint"]
        else:
            logger.debug(
                "'arcConfigEndpoint' doesn't exist under 'dataplaneEndpoints' in the ARM metadata."
            )
    # Get the default config dataplane endpoint.
    if config_dp_endpoint is None:
        config_dp_endpoint = get_default_config_dp_endpoint(cmd, location)
    return config_dp_endpoint, release_train


def get_public_key(key_pair: RsaKey) -> str:
    pubKey = key_pair.publickey()
    seq = asn1.DerSequence([pubKey.n, pubKey.e])
    enc = seq.encode()
    return b64encode(enc).decode("utf-8")


def load_kube_config(
    kube_config: str | None, kube_context: str | None, skip_ssl_verification: bool
) -> None:
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
        if skip_ssl_verification:
            from kubernetes.client import Configuration

            default_config = Configuration.get_default_copy()
            default_config.verify_ssl = False
            Configuration.set_default(default_config)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Load_Kubeconfig_Fault_Type,
            summary="Problem loading the kubeconfig file",
        )
        logger.warning(consts.Kubeconfig_Load_Failed_Warning)
        raise FileOperationError("Problem loading the kubeconfig file. " + str(e))


def get_private_key(key_pair: RsaKey) -> str:
    privKey_DER = key_pair.exportKey(format="DER")
    return PEM.encode(privKey_DER, "RSA PRIVATE KEY")


# Updated function to include more Kubernetes distributions based on provided criteria
def get_kubernetes_distro(api_response: V1NodeList) -> str:  # Heuristic
    if api_response is None:
        return "generic"
    try:
        for node in api_response.items:
            labels = node.metadata.labels or {}
            provider_id = str(node.spec.provider_id)
            annotations = node.metadata.annotations or {}

            if labels.get("node.openshift.io/os_id"):
                return "openshift"
            if labels.get("kubernetes.azure.com/node-image-version"):
                return "aks"
            if labels.get("cloud.google.com/gke-nodepool") or labels.get(
                "cloud.google.com/gke-os-distribution"
            ):
                return "gke"
            if labels.get("eks.amazonaws.com/nodegroup"):
                return "eks"
            if labels.get("minikube.k8s.io/version"):
                return "minikube"
            if annotations.get("node.aksedge.io/distro") == "aks_edge_k3s":
                return "aks_edge_k3s"
            if annotations.get("node.aksedge.io/distro") == "aks_edge_k8s":
                return "aks_edge_k8s"
            if provider_id.startswith("kind://"):
                return "kind"
            if provider_id.startswith("k3s://"):
                return "k3s"
            if annotations.get("rke.cattle.io/external-ip") or annotations.get(
                "rke.cattle.io/internal-ip"
            ):
                return "rancher_rke"
            if any(label.startswith("snap.microk8s") for label in labels):
                return "microk8s"
            if any(label.startswith("k3os.io") for label in labels):
                return "k3os"
            if any(label.startswith("talos.dev") for label in labels):
                return "talos"
            if any(key.startswith("rke2.io") for key in annotations):
                return "rke2"
            if any(
                label.startswith("node-role.kubernetes.io") for label in labels
            ) or any(
                key.startswith("kubeadm.alpha.kubernetes.io") for key in annotations
            ):
                return "kubeadm"
            if any(label.startswith("run.tanzu.vmware.com") for label in labels):
                return "tkg"
            if any(label.startswith("openebs.io") for label in labels):
                return "openebs"
            if any(label.startswith("flatcar-linux") for label in labels):
                return "flatcar"
            if any(label.startswith("k0s.k0sproject.io") for label in labels):
                return "k0s"
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        logger.debug(
            "Error occurred while trying to fetch Kubernetes distribution: %s", e
        )
        utils.kubernetes_exception_handler(
            e,
            consts.Get_Kubernetes_Distro_Fault_Type,
            "Unable to fetch kubernetes distribution",
            raise_error=False,
        )
        return "generic"


def get_kubernetes_infra(api_response: V1NodeList) -> str:  # Heuristic
    if api_response is None:
        return "generic"
    try:
        for node in api_response.items:
            provider_id = str(node.spec.provider_id)
            infra = provider_id.split(":")[0]
            if infra == "k3s":
                return "k3s"
            if infra == "kind":
                return "kind"
            if infra == "azure":
                return "azure"
            if infra == "gce":
                return "gcp"
            if infra == "aws":
                return "aws"
            k8s_infra = utils.validate_infrastructure_type(infra)
            if k8s_infra is not None:
                return k8s_infra
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        logger.debug(
            "Error occured while trying to fetch kubernetes infrastructure: %s", e
        )
        utils.kubernetes_exception_handler(
            e,
            consts.Get_Kubernetes_Infra_Fault_Type,
            "Unable to fetch kubernetes infrastructure",
            raise_error=False,
        )
        return "generic"


def check_linux_node(api_response: V1NodeList) -> bool:
    try:
        for item in api_response.items:
            node_os = item.metadata.labels.get("kubernetes.io/os")
            if node_os == "linux":
                return True
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to find a linux node: %s", e)
        utils.kubernetes_exception_handler(
            e,
            consts.Kubernetes_Node_Type_Fetch_Fault_OS,
            "Unable to find a linux node",
            raise_error=False,
        )
    return False


def check_arm64_node(api_response: V1NodeList) -> bool:
    try:
        for item in api_response.items:
            node_arch = item.metadata.labels.get("kubernetes.io/arch")
            if node_arch == "arm64":
                return True
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to find an arm64 node: %s", e)
        utils.kubernetes_exception_handler(
            e,
            consts.Kubernetes_Node_Type_Fetch_Fault_Arch,
            "Unable to find an arm64 node",
            raise_error=False,
        )
    return False


def set_oidc_issuer_profile(
    enable_oidc_issuer: bool, self_hosted_issuer: str = ""
) -> OidcIssuerProfile:
    oidc_profile = OidcIssuerProfile(enabled=enable_oidc_issuer)
    if self_hosted_issuer != "":
        oidc_profile.self_hosted_issuer_url = self_hosted_issuer
    return oidc_profile


def set_security_profile(enable_workload_identity: bool) -> SecurityProfile:
    security_profile = SecurityProfile(
        workload_identity=SecurityProfileWorkloadIdentity(
            enabled=enable_workload_identity
        )
    )
    return security_profile


def generate_arc_agent_configuration(
    configuration_settings: dict[str, Any],
    redacted_protected_settings: dict[str, Any],
    is_dp_call: bool = False,
) -> list[ArcAgentryConfigurations] | None:
    if not configuration_settings and not redacted_protected_settings:
        return None

    arc_agentry_configurations = []

    for feature in configuration_settings.keys() | redacted_protected_settings.keys():
        settings = configuration_settings.get(feature)
        protected_settings = redacted_protected_settings.get(feature)
        configuration = ArcAgentryConfigurations(
            feature=feature,
            settings=settings,
            protected_settings=protected_settings if is_dp_call else None,
        )
        arc_agentry_configurations.append(configuration)
    return arc_agentry_configurations


def generate_request_payload(
    location: str,
    public_key: str,
    tags: dict[str, str] | None,
    kubernetes_distro: str,
    kubernetes_infra: str,
    enable_private_link: bool | None,
    private_link_scope_resource_id: str,
    distribution_version: str | None,
    azure_hybrid_benefit: str | None,
    oidc_profile: OidcIssuerProfile | None,
    security_profile: SecurityProfile | None,
    gateway: Gateway | None,
    arc_agentry_configurations: list[ArcAgentryConfigurations] | None,
    arc_agent_profile: ArcAgentProfile | None,
) -> ConnectedCluster:
    # Create connected cluster resource object
    identity = ConnectedClusterIdentity(type="SystemAssigned")
    if tags is None:
        tags = {}

    cc = ConnectedCluster(
        location=location,
        identity=identity,
        agent_public_key_certificate=public_key,
        tags=tags,
        distribution=kubernetes_distro,
        infrastructure=kubernetes_infra,
    )

    if (
        enable_private_link is not None
        or distribution_version is not None
        or azure_hybrid_benefit is not None
        or oidc_profile is not None
        or security_profile is not None
        or gateway is not None
        or arc_agentry_configurations is not None
        or arc_agent_profile is not None
    ):
        # Set additional parameters
        kwargs: dict[str, Any] = {}
        if enable_private_link is not None:
            kwargs["private_link_state"] = (
                "Enabled" if enable_private_link else "Disabled"
            )
        if private_link_scope_resource_id:
            kwargs["private_link_scope_resource_id"] = private_link_scope_resource_id

        cc = ConnectedCluster(
            location=location,
            identity=identity,
            agent_public_key_certificate=public_key,
            tags=tags,
            distribution=kubernetes_distro,
            infrastructure=kubernetes_infra,
            azure_hybrid_benefit=azure_hybrid_benefit,
            distribution_version=distribution_version,
            arc_agent_profile=arc_agent_profile,
            gateway=gateway,
            arc_agentry_configurations=arc_agentry_configurations,
            oidc_issuer_profile=oidc_profile,
            security_profile=security_profile,
            **kwargs,
        )

    return cc


def generate_reput_request_payload(
    cc: ConnectedCluster,
    oidc_profile: OidcIssuerProfile | None,
    security_profile: SecurityProfile | None,
    gateway: Gateway | None,
    arc_agentry_configurations: list[ArcAgentryConfigurations] | None,
    arc_agent_profile: ArcAgentProfile | None,
) -> ConnectedCluster:
    # Update connected cluster resource object
    if oidc_profile is not None:
        cc.oidc_issuer_profile = oidc_profile

    if security_profile is not None:
        cc.security_profile = security_profile

    if gateway is not None:
        cc.gateway = gateway

    if arc_agentry_configurations is not None:
        cc.arc_agentry_configurations = arc_agentry_configurations

    if arc_agent_profile is not None:
        cc.arc_agent_profile = arc_agent_profile

    return cc


def generate_patch_payload(
    tags: dict[str, str] | None,
    distribution: str | None,
    distribution_version: str | None,
    azure_hybrid_benefit: str | None,
) -> ConnectedClusterPatch:
    cc = ConnectedClusterPatch(
        tags=tags,
        distribution=distribution,
        distribution_version=distribution_version,
        azure_hybrid_benefit=azure_hybrid_benefit,
    )
    return cc


def get_kubeconfig_node_dict(kube_config: str | None = None) -> ConfigNode:
    if kube_config is None:
        kube_config = os.getenv("KUBECONFIG") or os.path.join(
            os.path.expanduser("~"), ".kube", "config"
        )
    try:
        kubeconfig_data = KubeConfigMerger(kube_config).config
    except Exception as ex:
        telemetry.set_exception(
            exception=ex,
            fault_type=consts.Load_Kubeconfig_Fault_Type,
            summary="Error while fetching details from kubeconfig",
        )
        raise FileOperationError(
            "Error while fetching details from kubeconfig." + str(ex)
        )
    return kubeconfig_data


def check_proxy_kubeconfig(
    kube_config: str | None, kube_context: str | None, arm_hash: str
) -> bool:
    server_address = get_server_address(kube_config, kube_context)
    regex_string = r"https://127.0.0.1:[0-9]{1,5}/" + arm_hash
    p = re.compile(regex_string)
    return bool(p.fullmatch(server_address))


def check_aks_cluster(kube_config: str | None, kube_context: str | None) -> bool:
    server_address = get_server_address(kube_config, kube_context)
    return server_address.find(".azmk8s.io:") != -1


def get_server_address(kube_config: str | None, kube_context: str | None) -> str:
    config_data = get_kubeconfig_node_dict(kube_config=kube_config)
    try:
        all_contexts, current_context = config.list_kube_config_contexts(
            config_file=kube_config
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Exception while trying to list kube contexts: %s\n", e)

    if kube_context is None:
        # Get name of the cluster from current context as kube_context is none.
        cluster_name = current_context.get("context").get("cluster")
        if cluster_name is None:
            logger.warning(
                "Cluster not found in currentcontext: %s", str(current_context)
            )
    else:
        cluster_found = False
        for context in all_contexts:
            if context.get("name") == kube_context:
                cluster_found = True
                cluster_name = context.get("context").get("cluster")
                break
        if not cluster_found or cluster_name is None:
            logger.warning("Cluster not found in kubecontext: %s", str(kube_context))

    clusters = config_data.safe_get("clusters")
    server_address = ""
    for cluster in clusters:
        if cluster.safe_get("name") == cluster_name:
            server_address = cluster.safe_get("cluster").get("server")
            break
    return server_address


def get_connectedk8s(
    cmd: AzCliCommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
) -> ConnectedCluster:
    return client.get(resource_group_name, cluster_name)


def list_connectedk8s(
    cmd: AzCliCommand,
    client: ConnectedClusterOperations,
    resource_group_name: str | None = None,
) -> Iterable[ConnectedCluster]:
    if not resource_group_name:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def delete_connectedk8s(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    kube_config: str | None = None,
    kube_context: str | None = None,
    no_wait: bool = False,
    force_delete: bool = False,
    skip_ssl_verification: bool = False,
    yes: bool = False,
) -> None:
    # The force delete prompt is added because it can be used in the case where the config map is missing
    # so we cannot check if the user context is pointing to the cluster that he intends to delete
    if not force_delete:
        confirmation_message = "Are you sure you want to perform delete operation?"
        utils.user_confirmation(confirmation_message, yes)
    elif force_delete:
        confirmation_message = (
            "Force delete will clean up all the azure-arc resources, including extensions. Please make sure your "
            " current kubeconfig is pointing to the right cluster.\nAre you sure you want to perform force delete:"
        )
        utils.user_confirmation(confirmation_message, yes)

    logger.warning("This operation might take a while ...\n")

    # Check if the cluster is of supported type for deletion
    cluster_resource = client.get(resource_group_name, cluster_name)
    if (cluster_resource.kind is not None) and (
        cluster_resource.kind.lower() == consts.Provisioned_Cluster_Kind
    ):
        err_msg = (
            "Deleting a Provisioned Cluster is not supported from the Connected Cluster CLI. Please use the "
            "'az aksarc delete' CLI command.\n"
            + consts.Doc_Provisioned_Cluster_Delete_Url
        )
        raise InvalidArgumentValueError(err_msg)

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context, skip_ssl_verification)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled
    # AKS clusters if the user had not logged in.
    check_kube_connection()

    # Install helm client
    helm_client_location = install_helm_client(cmd)

    # Check Release Existance
    release_namespace = utils.get_release_namespace(
        kube_config, kube_context, helm_client_location
    )

    print(f"Step: {utils.get_utctimestring()}: Do node validations")
    api_instance = kube_client.CoreV1Api()
    node_api_response = utils.validate_node_api_response(api_instance)
    is_arm64_cluster = check_arm64_node(node_api_response)

    # Check forced delete flag
    if force_delete:
        print(f"Step: {utils.get_utctimestring()}: Performing Force Delete")
        kubectl_client_location = install_kubectl_client()

        delete_cc_resource(
            client, resource_group_name, cluster_name, no_wait, force=force_delete
        ).result()

        # Explicit CRD Deletion
        crd_cleanup_force_delete(
            cmd, kubectl_client_location, kube_config, kube_context
        )

        if release_namespace:
            utils.delete_arc_agents(
                release_namespace,
                kube_config,
                kube_context,
                helm_client_location,
                is_arm64_cluster,
                True,
            )

        return

    if not release_namespace:
        delete_cc_resource(
            client, resource_group_name, cluster_name, no_wait, force=force_delete
        ).result()
        return

    # Loading config map
    try:
        configmap = api_instance.read_namespaced_config_map(
            "azure-clusterconfig", "azure-arc"
        )
    except Exception as e:  # pylint: disable=broad-except
        err_msg = (
            "The helm release 'azure-arc' is present but the azure-arc namespace/configmap "
            f"is missing. Please run 'helm delete azure-arc --namepace {release_namespace} --no-hooks' to cleanup the release "
            "before onboarding the cluster again."
        )
        utils.kubernetes_exception_handler(
            e,
            consts.Read_ConfigMap_Fault_Type,
            "Unable to read ConfigMap",
            error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
            message_for_not_found=err_msg,
        )

    subscription_id = (
        os.environ["AZURE_SUBSCRIPTION_ID"]
        if os.getenv("AZURE_ACCESS_TOKEN")
        else get_subscription_id(cmd.cli_ctx)
    )

    if (
        configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower()
        and configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower()
        and configmap.data["AZURE_SUBSCRIPTION_ID"].lower() == subscription_id.lower()
    ):
        armid = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Kubernetes/connectedClusters/{cluster_name}"
        arm_hash = hashlib.sha256(armid.lower().encode("utf-8")).hexdigest()

        if check_proxy_kubeconfig(kube_config, kube_context, arm_hash):
            telemetry.set_exception(
                exception="Encountered proxy kubeconfig during deletion.",
                fault_type=consts.Proxy_Kubeconfig_During_Deletion_Fault_Type,
                summary="The resource cannot be deleted as user is using proxy kubeconfig.",
            )
            reco_str = (
                "Run the az connectedk8s delete command with your kubeconfig file pointing to the actual "
                "Kubernetes cluster to ensure that agents are cleaned up successfully as part of the delete command."
            )
            raise ClientRequestError(
                "az connectedk8s delete is not supported when using the Cluster Connect kubeconfig.",
                recommendation=reco_str,
            )

        delete_cc_resource(
            client, resource_group_name, cluster_name, no_wait, force=force_delete
        ).result()
    else:
        telemetry.set_exception(
            exception="Unable to delete connected cluster",
            fault_type=consts.Bad_DeleteRequest_Fault_Type,
            summary="The resource cannot be deleted as kubernetes cluster is onboarded with some other resource id",
        )
        raise ArgumentUsageError(
            "The current context in the kubeconfig file does not correspond "
            + "to the connected cluster resource specified. Agents installed on this cluster correspond "
            + "to the resource group name '{}' ".format(
                configmap.data["AZURE_RESOURCE_GROUP"]
            )
            + "and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_NAME"])
        )

    # Deleting the azure-arc agents
    utils.delete_arc_agents(
        release_namespace,
        kube_config,
        kube_context,
        helm_client_location,
        is_arm64_cluster,
    )

    print(f"Step: {utils.get_utctimestring()}: Delete of Connected Cluster ended.")


def create_cc_resource(
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    cc: ConnectedCluster,
    no_wait: bool,
) -> LROPoller[ConnectedCluster]:
    try:
        poller: LROPoller[ConnectedCluster] = sdk_no_wait(
            no_wait,
            client.begin_create,
            resource_group_name=resource_group_name,
            cluster_name=cluster_name,
            connected_cluster=cc,
        )
        return poller
    except Exception as e:
        utils.arm_exception_handler(
            e,
            consts.Create_ConnectedCluster_Fault_Type,
            "Unable to create connected cluster resource",
        )

    assert False


def patch_cc_resource(
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    cc: ConnectedClusterPatch,
) -> ConnectedCluster:
    try:
        return client.update(
            resource_group_name=resource_group_name,
            cluster_name=cluster_name,
            connected_cluster_patch=cc,
        )
    except Exception as e:
        utils.arm_exception_handler(
            e,
            consts.Update_ConnectedCluster_Fault_Type,
            "Unable to update connected cluster resource",
        )

    assert False


def delete_cc_resource(
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    no_wait: bool,
    force: bool = False,
) -> LROPoller[None]:
    print(f"Step: {utils.get_utctimestring()}: Deleting ARM resource")
    try:
        poller: LROPoller[None]
        if force:
            poller = sdk_no_wait(
                no_wait,
                client.begin_delete,
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
                params={"force": True},
            )
        else:
            poller = sdk_no_wait(
                no_wait,
                client.begin_delete,
                resource_group_name=resource_group_name,
                cluster_name=cluster_name,
            )
        return poller
    except Exception as e:
        utils.arm_exception_handler(
            e,
            consts.Delete_ConnectedCluster_Fault_Type,
            "Unable to delete connected cluster resource",
        )

    assert False


def update_connected_cluster_internal(
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    tags: dict[str, str] | None = None,
    distribution: str | None = None,
    distribution_version: str | None = None,
    azure_hybrid_benefit: str | None = None,
) -> ConnectedCluster:
    cc = generate_patch_payload(
        tags, distribution, distribution_version, azure_hybrid_benefit
    )
    return patch_cc_resource(client, resource_group_name, cluster_name, cc)


# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def update_connected_cluster(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    https_proxy: str = "",
    http_proxy: str = "",
    no_proxy: str = "",
    proxy_cert: str = "",
    disable_proxy: bool = False,
    kube_config: str | None = None,
    kube_context: str | None = None,
    auto_upgrade: str | None = None,
    tags: dict[str, str] | None = None,
    distribution: str | None = None,
    distribution_version: str | None = None,
    azure_hybrid_benefit: str | None = None,
    skip_ssl_verification: bool = False,
    yes: bool = False,
    container_log_path: str | None = None,
    enable_oidc_issuer: bool | None = None,
    enable_workload_identity: bool | None = None,
    self_hosted_issuer: str = "",
    disable_workload_identity: bool | None = None,
    gateway_resource_id: str = "",
    disable_gateway: bool = False,
    configuration_settings: dict[str, Any] | None = None,
    configuration_protected_settings: dict[str, Any] | None = None,
) -> ConnectedCluster:
    # Prompt for confirmation for few parameters
    if azure_hybrid_benefit == "True":
        confirmation_message = (
            "I confirm I have an eligible Windows Server license with Azure Hybrid Benefit to "
            "apply this benefit to AKS on HCI or Windows Server. Visit https://aka.ms/ahb-aks for details"
        )
        utils.user_confirmation(confirmation_message, yes)

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Escaping comma, forward slash present in https proxy urls, needed for helm params.
    https_proxy = escape_proxy_settings(https_proxy)

    # Escaping comma, forward slash present in http proxy urls, needed for helm params.
    http_proxy = escape_proxy_settings(http_proxy)

    # Escaping comma, forward slash present in no proxy urls, needed for helm params.
    no_proxy = escape_proxy_settings(no_proxy)

    # check whether proxy cert path exists
    if proxy_cert != "" and (not os.path.exists(proxy_cert)):
        telemetry.set_exception(
            exception="Proxy cert path does not exist",
            fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
            summary="Proxy cert path does not exist",
        )
        raise InvalidArgumentValueError(
            str.format(consts.Proxy_Cert_Path_Does_Not_Exist_Error, proxy_cert)
        )

    proxy_cert = proxy_cert.replace("\\", r"\\\\")

    (
        configuration_settings,
        configuration_protected_settings,
        redacted_protected_values,
    ) = add_config_protected_settings(
        http_proxy,
        https_proxy,
        no_proxy,
        proxy_cert,
        container_log_path,
        configuration_settings,
        configuration_protected_settings,
    )
    arc_agentry_configurations = generate_arc_agent_configuration(
        configuration_settings, redacted_protected_values
    )

    # Fetch Connected Cluster for agent version
    connected_cluster = client.get(resource_group_name, cluster_name)

    if (connected_cluster.kind is not None) and (
        connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind
    ):
        err_msg = (
            "Updating a Provisioned Cluster is not supported from the Connected Cluster CLI. "
            "Please use the 'az aksarc update' CLI command.\n"
            + consts.Doc_Provisioned_Cluster_Update_Url
        )
        raise InvalidArgumentValueError(err_msg)

    # Patching the connected cluster ARM resource
    arm_properties_unset = (
        tags is None
        and distribution is None
        and distribution_version is None
        and azure_hybrid_benefit is None
    )
    proxy_params_unset = (
        https_proxy == ""
        and http_proxy == ""
        and no_proxy == ""
        and proxy_cert == ""
        and not disable_proxy
    )

    if not arm_properties_unset:
        patch_cc_response = update_connected_cluster_internal(
            client,
            resource_group_name,
            cluster_name,
            tags,
            distribution,
            distribution_version,
            azure_hybrid_benefit,
        )

        # Returning the ARM response if only AHB is being updated
        arm_properties_only_ahb_set = (
            tags is None
            and distribution is None
            and distribution_version is None
            and azure_hybrid_benefit is not None
        )
        if (
            proxy_params_unset
            and auto_upgrade is None
            and container_log_path is None
            and arm_properties_only_ahb_set
        ):
            return patch_cc_response

    if (
        proxy_params_unset
        and not auto_upgrade
        and arm_properties_unset
        and not container_log_path
        and enable_oidc_issuer is None
        and disable_workload_identity is None
        and enable_workload_identity is None
        and gateway_resource_id == ""
        and not disable_gateway
    ):
        raise RequiredArgumentMissingError(consts.No_Param_Error)

    if (https_proxy or http_proxy or no_proxy) and disable_proxy:
        raise MutuallyExclusiveArgumentError(consts.EnableProxy_Conflict_Error)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context, skip_ssl_verification)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    # Install helm client
    helm_client_location = install_helm_client(cmd)

    release_namespace = validate_release_namespace(
        client,
        cluster_name,
        resource_group_name,
        kube_config,
        kube_context,
        helm_client_location,
    )

    # Fetch Connected Cluster for agent version
    connected_cluster = client.get(resource_group_name, cluster_name)

    kubernetes_properties = {
        "Context.Default.AzureCLI.KubernetesVersion": kubernetes_version
    }

    if hasattr(connected_cluster, "distribution") and (
        connected_cluster.distribution is not None
    ):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties["Context.Default.AzureCLI.KubernetesDistro"] = (
            kubernetes_distro
        )

    if hasattr(connected_cluster, "infrastructure") and (
        connected_cluster.infrastructure is not None
    ):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties["Context.Default.AzureCLI.KubernetesInfra"] = (
            kubernetes_infra
        )

    telemetry.add_extension_event("connectedk8s", kubernetes_properties)

    # Get the connected cluster resource using latest api version and generate reput request payload
    connected_cluster = client.get(resource_group_name, cluster_name)

    # If gateway is enabled
    gateway = None
    if gateway_resource_id != "":
        gateway = Gateway(enabled=True, resource_id=gateway_resource_id)
    if disable_gateway:
        gateway = Gateway(enabled=False)

    # Set arc agent profile when auto-upgrade is set
    arc_agent_profile = None
    if auto_upgrade is not None:
        arc_agent_profile = (
            ArcAgentProfile(agent_auto_upgrade="Enabled")
            if auto_upgrade.lower() == "true"
            else ArcAgentProfile(agent_auto_upgrade="Disabled")
        )

    # Set enable workload identity
    if disable_workload_identity is True:
        enable_workload_identity = False
    security_profile = None
    if enable_workload_identity is not None:
        security_profile = set_security_profile(enable_workload_identity)

    # Perform validation for self hosted issuer and set oidc issuer profile
    oidc_profile = None
    if enable_oidc_issuer:
        if (
            self_hosted_issuer == ""
            and kubernetes_distro in consts.Public_Cloud_Distribution_List
        ):
            raise ValidationError(
                f"Self hosted issuer is required for {kubernetes_distro} cluster when OIDC issuer is being enabled."
            )
        oidc_profile = set_oidc_issuer_profile(enable_oidc_issuer, self_hosted_issuer)

    cc = generate_reput_request_payload(
        connected_cluster,
        oidc_profile,
        security_profile,
        gateway,
        arc_agentry_configurations,
        arc_agent_profile,
    )

    # Update connected cluster resource
    reput_cc_poller = create_cc_resource(
        client, resource_group_name, cluster_name, cc, False
    )
    dp_request_payload = reput_cc_poller.result()
    _ = LongRunningOperation(cmd.cli_ctx)(reput_cc_poller)

    # Before proceeding, we prefer to see agent state settle - updating the helm chart
    # while things are happening risks race conditions.  Eg
    # <https://msazure.visualstudio.com/AzureArcPlatform/_workitems/edit/29816874>.
    #
    # If we don't see a terminal state, we'll go ahead and update the helm chart anyway,
    # and throw an error later.
    print(
        f"Step: {utils.get_utctimestring()}: Wait for Agent State to reach terminal state, with timeout of {consts.Agent_State_Timeout}"
    )
    terminal_agent_state, connected_cluster = poll_for_agent_state(
        client, resource_group_name, cluster_name
    )
    maybe_has = "has" if terminal_agent_state else "has not"
    print(
        f"Step: {utils.get_utctimestring()}: Agent state {maybe_has} reached terminal state."
    )

    # Adding helm repo
    if os.getenv("HELMREPONAME") and os.getenv("HELMREPOURL"):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    config_dp_endpoint, release_train = get_config_dp_endpoint(
        cmd, connected_cluster.location, values_file
    )

    # Update arc agent configuration to include protected parameters in dp call
    arc_agentry_configurations = generate_arc_agent_configuration(
        configuration_settings, redacted_protected_values, is_dp_call=True
    )
    dp_request_payload.arc_agentry_configurations = arc_agentry_configurations

    # Perform DP health check
    _ = utils.health_check_dp(cmd, config_dp_endpoint)

    # Retrieving Helm chart OCI Artifact location
    helm_values_dp = utils.get_helm_values(
        cmd, config_dp_endpoint, release_train, connected_cluster=dp_request_payload
    )

    registry_path = os.getenv("HELMREGISTRY") or helm_values_dp["repositoryPath"]

    if registry_path == "":
        registry_path = utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

    # Get azure-arc agent version for telemetry
    reg_path_array = registry_path.split(":")
    agent_version = reg_path_array[1]

    helm_content_values = helm_values_dp["helmValuesContent"]

    # Substitute any protected helm values as the value for that will be 'redacted-<feature>-<protectedSetting>'
    for helm_parameter, helm_value in helm_content_values.items():
        if "redacted" in helm_value:
            _, feature, protectedSetting = helm_value.split(":")
            helm_content_values[helm_parameter] = configuration_protected_settings[
                feature
            ][protectedSetting]

    # Disable proxy if disable_proxy flag is set
    if disable_proxy:
        helm_content_values["global.isProxyEnabled"] = "False"

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version  # type: ignore[unreachable]
        registry_path = reg_path_array[0] + ":" + agent_version

    check_operation_support("update (properties)", agent_version)

    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.AgentVersion": agent_version}
    )

    # Get Helm chart path
    chart_path = utils.get_chart_path(
        registry_path, kube_config, kube_context, helm_client_location
    )

    print(
        f"Step: {utils.get_utctimestring()}: Starting to update Azure arc agents on the Kubernetes cluster."
    )
    # Perform helm upgrade
    utils.helm_update_agent(
        helm_client_location,
        kube_config,
        kube_context,
        helm_content_values,
        values_file,
        cluster_name,
        release_namespace,
        chart_path,
    )

    # If we didn't see a terminal agent state, now's the time to throw an error.
    if not terminal_agent_state:
        raise CLIInternalError(
            "Timed out waiting for Agent State to reach terminal state."
        )

    return connected_cluster


def upgrade_agents(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    kube_config: str | None = None,
    kube_context: str | None = None,
    skip_ssl_verification: bool = False,
    arc_agent_version: str | None = None,
    upgrade_timeout: str = "600",
) -> str:
    # Check if cluster supports upgrading
    connected_cluster = client.get(resource_group_name, cluster_name)

    if (connected_cluster.kind is not None) and (
        connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind
    ):
        err_msg = (
            "Upgrading a Provisioned Cluster is not supported from the Connected Cluster CLI. Please use the "
            "'az aksarc upgrade' CLI command. \n"
            + consts.Doc_Provisioned_Cluster_Upgrade_Url
        )
        raise InvalidArgumentValueError(err_msg)

    logger.warning("This operation might take a while...\n")

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context, skip_ssl_verification)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    api_instance = kube_client.CoreV1Api()

    # Install helm client
    helm_client_location = install_helm_client(cmd)

    # Check Release Existence
    release_namespace = utils.get_release_namespace(
        kube_config, kube_context, helm_client_location
    )
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api()
        try:
            configmap = api_instance.read_namespaced_config_map(
                "azure-clusterconfig", "azure-arc"
            )
        except Exception as e:  # pylint: disable=broad-except
            not_found_msg = (
                "The helm release 'azure-arc' is present but the azure-arc namespace/configmap is "
                f"missing. Please run 'helm delete azure-arc --namespace {release_namespace} --no-hooks' to cleanup the release "
                "before onboarding the cluster again."
            )
            utils.kubernetes_exception_handler(
                e,
                consts.Read_ConfigMap_Fault_Type,
                "Unable to read ConfigMap",
                error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                message_for_not_found=not_found_msg,
            )
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if not (
                configmap_rg_name.lower() == resource_group_name.lower()
                and configmap_cluster_name.lower() == cluster_name.lower()
            ):
                err_msg = (
                    "The provided cluster name and resource group name do not correspond to the kubernetes "
                    "cluster being upgraded."
                )
                telemetry.set_exception(
                    exception="The provided cluster name and rg correspond to different cluster",
                    fault_type=consts.Upgrade_RG_Cluster_Name_Conflict,
                    summary=err_msg,
                )
                reco_msg = (
                    "Please upgrade the cluster, with correct resource group and cluster name, using "
                    "'az upgrade agents -g <rg_name> -n <cluster_name>'."
                )
                raise ArgumentUsageError(err_msg, recommendation=reco_msg)
        else:
            telemetry.set_exception(
                exception="The corresponding CC resource does not exist",
                fault_type=consts.Corresponding_CC_Resource_Deleted_Fault,
                summary="CC resource corresponding to this cluster has been deleted by the customer",
            )
            err_msg = "There exist no ConnectedCluster resource corresponding to this kubernetes Cluster."
            reco_msg = (
                "Please cleanup the helm release first using 'az connectedk8s delete -n "
                "<connected-cluster-name> -g <resource-group-name>' and re-onboard the cluster using "
                "'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>'"
            )
            raise ArgumentUsageError(err_msg, recommendation=reco_msg)

        auto_update_enabled = configmap.data["AZURE_ARC_AUTOUPDATE"]
        if auto_update_enabled == "true":
            summary_msg = (
                "az connectedk8s upgrade to manually upgrade agents and extensions is only supported when "
                "auto-upgrade is set to false."
            )
            telemetry.set_exception(
                exception="connectedk8s upgrade called when auto-update is set to true",
                fault_type=consts.Manual_Upgrade_Called_In_Auto_Update_Enabled,
                summary=summary_msg,
            )
            err_msg = (
                "az connectedk8s upgrade to manually upgrade agents and extensions is only supported when "
                "auto-upgrade is set to false."
            )
            reco_msg = (
                "Please run 'az connectedk8s update -n <connected-cluster-name> -g "
                "<resource-group-name> --auto-upgrade false' before performing manual upgrade"
            )
            raise ClientRequestError(err_msg, recommendation=reco_msg)

    else:
        summary_msg = (
            "The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes "
            "cluster has not been onboarded to azure-arc."
        )
        telemetry.set_exception(
            exception="The azure-arc release namespace couldn't be retrieved",
            fault_type=consts.Release_Namespace_Not_Found,
            summary=summary_msg,
        )
        err_msg = (
            "The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster "
            "has not been onboarded to azure-arc."
        )
        reco_msg = (
            "Please run 'az connectedk8s connect -n <connected-cluster-name> -g "
            "<resource-group-name>' to onboard the cluster"
        )
        raise ClientRequestError(err_msg, recommendation=reco_msg)

    # Fetch Connected Cluster for agent version
    connected_cluster = client.get(resource_group_name, cluster_name)

    kubernetes_properties = {
        "Context.Default.AzureCLI.KubernetesVersion": kubernetes_version
    }

    if hasattr(connected_cluster, "distribution") and (
        connected_cluster.distribution is not None
    ):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties["Context.Default.AzureCLI.KubernetesDistro"] = (
            kubernetes_distro
        )

    if hasattr(connected_cluster, "infrastructure") and (
        connected_cluster.infrastructure is not None
    ):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties["Context.Default.AzureCLI.KubernetesInfra"] = (
            kubernetes_infra
        )

    telemetry.add_extension_event("connectedk8s", kubernetes_properties)

    # Adding helm repo
    if os.getenv("HELMREPONAME") and os.getenv("HELMREPOURL"):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    config_dp_endpoint, release_train = get_config_dp_endpoint(
        cmd, connected_cluster.location, values_file
    )

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv("HELMREGISTRY") or utils.get_helm_registry(
        cmd, config_dp_endpoint, release_train
    )

    reg_path_array = registry_path.split(":")
    agent_version = reg_path_array[1]

    if arc_agent_version is not None:
        agent_version = arc_agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.AgentVersion": agent_version}
    )

    # Get Helm chart path
    chart_path = utils.get_chart_path(
        registry_path, kube_config, kube_context, helm_client_location
    )

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

    response_helm_values_get = Popen(cmd_helm_values, stdout=PIPE, stderr=PIPE)
    output_helm_values, error_helm_get_values = response_helm_values_get.communicate()
    if response_helm_values_get.returncode != 0:
        error = error_helm_get_values.decode("ascii")
        if "forbidden" in error or "timed out waiting for the condition" in error:
            telemetry.set_user_fault()
        telemetry.set_exception(
            exception=error,
            fault_type=consts.Get_Helm_Values_Failed,
            summary="Error while doing helm get values azure-arc",
        )
        raise CLIInternalError(str.format(consts.Upgrade_Agent_Failure, error))

    output_helm_values_str = output_helm_values.decode("ascii")

    try:
        existing_user_values = yaml.safe_load(output_helm_values_str)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Helm_Existing_User_Supplied_Value_Get_Fault,
            summary="Problem loading the helm existing user supplied values",
        )
        raise CLIInternalError(
            f"Problem loading the helm existing user supplied values: {e}"
        )

    # Change --timeout format for helm client to understand
    upgrade_timeout = upgrade_timeout + "s"
    cmd_helm_upgrade = [
        helm_client_location,
        "upgrade",
        "azure-arc",
        chart_path,
        "--namespace",
        release_namespace,
        "--output",
        "json",
        "--atomic",
        "--wait",
        "--timeout",
        f"{upgrade_timeout}",
    ]

    proxy_enabled_param_added = False
    infra_added = False
    for key, value in utils.flatten(existing_user_values).items():
        if value is not None:
            if key == "global.isProxyEnabled":
                proxy_enabled_param_added = True
            if (
                key == "global.httpProxy"
                or key == "global.httpsProxy"
                or key == "global.noProxy"
            ):
                value = escape_proxy_settings(value)
                if value and not proxy_enabled_param_added:
                    cmd_helm_upgrade.extend(["--set", f"global.isProxyEnabled={True}"])
                    proxy_enabled_param_added = True
            if key == "global.kubernetesDistro" and value == "default":
                value = "generic"
            if key == "global.kubernetesInfra":
                infra_added = True
            cmd_helm_upgrade.extend(["--set", f"{key}={value}"])

    if not proxy_enabled_param_added:
        cmd_helm_upgrade.extend(["--set", f"global.isProxyEnabled={False}"])

    if not infra_added:
        cmd_helm_upgrade.extend(
            ["--set", "global.kubernetesInfra={}".format("generic")]
        )

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
            exception=error_helm_upgrade.decode("ascii"),
            fault_type=consts.Install_HelmRelease_Fault_Type,
            summary="Unable to install helm release",
        )
        raise CLIInternalError(
            str.format(consts.Upgrade_Agent_Failure, helm_upgrade_error_message)
        )

    return str.format(consts.Upgrade_Agent_Success, connected_cluster.name)


def validate_release_namespace(
    client: ConnectedClusterOperations,
    cluster_name: str,
    resource_group_name: str,
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
) -> str:
    # Check Release Existance
    release_namespace = utils.get_release_namespace(
        kube_config, kube_context, helm_client_location
    )
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api()
        try:
            configmap = api_instance.read_namespaced_config_map(
                "azure-clusterconfig", "azure-arc"
            )
        except Exception as e:  # pylint: disable=broad-except
            not_found_msg = (
                "The helm release 'azure-arc' is present but the azure-arc namespace/configmap is "
                f"missing. Please run 'helm delete azure-arc --namespace {release_namespace} --no-hooks' to cleanup the release "
                "before onboarding the cluster again."
            )
            utils.kubernetes_exception_handler(
                e,
                consts.Read_ConfigMap_Fault_Type,
                "Unable to read ConfigMap",
                error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                message_for_not_found=not_found_msg,
            )
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if not (
                configmap_rg_name.lower() == resource_group_name.lower()
                and configmap_cluster_name.lower() == cluster_name.lower()
            ):
                err_msg = (
                    "The provided cluster name and resource group name do not correspond to the kubernetes "
                    "cluster being operated on."
                )
                reco_msg = "Please use the cluster, with correct resource group and cluster name."
                telemetry.set_exception(
                    exception="The provided cluster name and rg correspond to different cluster",
                    fault_type=consts.Operate_RG_Cluster_Name_Conflict,
                    summary=err_msg,
                )
                raise ArgumentUsageError(err_msg, recommendation=reco_msg)
        else:
            telemetry.set_exception(
                exception="The corresponding CC resource does not exist",
                fault_type=consts.Corresponding_CC_Resource_Deleted_Fault,
                summary="CC resource corresponding to this cluster has been deleted by the customer",
            )
            err_msg = "There exist no ConnectedCluster resource corresponding to this kubernetes Cluster."
            reco_msg = (
                "Please cleanup the helm release first using 'az connectedk8s delete -n "
                "<connected-cluster-name> -g <resource-group-name>' and re-onboard the cluster using "
                "'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>'"
            )
            raise ClientRequestError(err_msg, recommendation=reco_msg)
    else:
        err_msg = (
            "The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes "
            "cluster has not been onboarded to azure-arc."
        )
        telemetry.set_exception(
            exception="The azure-arc release namespace couldn't be retrieved",
            fault_type=consts.Release_Namespace_Not_Found,
            summary=err_msg,
        )
        reco_msg = (
            "Please run 'az connectedk8s connect -n <connected-cluster-name> -g "
            "<resource-group-name>' to onboard the cluster"
        )
        raise ClientRequestError(err_msg, recommendation=reco_msg)
    return release_namespace


def get_all_helm_values(
    release_namespace: str,
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
) -> dict[str, Any]:
    cmd_helm_values = [
        helm_client_location,
        "get",
        "values",
        "--all",
        "azure-arc",
        "--namespace",
        release_namespace,
    ]
    if kube_config:
        cmd_helm_values.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_values.extend(["--kube-context", kube_context])

    response_helm_values_get = Popen(cmd_helm_values, stdout=PIPE, stderr=PIPE)
    output_helm_values, error_helm_get_values = response_helm_values_get.communicate()
    if response_helm_values_get.returncode != 0:
        error = error_helm_get_values.decode("ascii")
        if "forbidden" in error:
            telemetry.set_user_fault()
        telemetry.set_exception(
            exception=error,
            fault_type=consts.Get_Helm_Values_Failed,
            summary="Error while doing helm get values azure-arc",
        )
        raise CLIInternalError(
            f"Error while getting the helm values in the azure-arc namespace: {error}"
        )

    output_helm_values_str = output_helm_values.decode("ascii")

    try:
        existing_values: dict[str, Any] = yaml.safe_load(output_helm_values_str)
        return existing_values
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Helm_Existing_User_Supplied_Value_Get_Fault,
            summary="Problem loading the helm existing values",
        )
        raise CLIInternalError(f"Problem loading the helm existing values: {e}")


def enable_features(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    features: list[str],
    kube_config: str | None = None,
    kube_context: str | None = None,
    azrbac_client_id: str | None = None,
    azrbac_client_secret: str | None = None,
    azrbac_skip_authz_check: str | None = None,
    skip_ssl_verification: bool = False,
    cl_oid: str | None = None,
) -> str:
    logger.warning("This operation might take a while...\n")

    # Validate custom token operation
    custom_token_passed, _ = utils.validate_custom_token(
        cmd, resource_group_name, "dummyLocation"
    )

    features = [x.lower() for x in features]
    enable_cluster_connect, enable_azure_rbac, enable_cl = (
        utils.check_features_to_update(features)
    )

    # Check if cluster is private link enabled
    connected_cluster = client.get(resource_group_name, cluster_name)

    if (connected_cluster.kind is not None) and (
        connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind
    ):
        err_msg = (
            "Enable feature of a Provisioned Cluster is not supported from the Connected Cluster CLI. For "
            "information on how to enable a feature on a Provisioned Cluster using a cluster extension, "
            "please refer to: https://learn.microsoft.com/en-us/azure/aks/deploy-extensions-az-cli"
        )
        raise InvalidArgumentValueError(err_msg)

    if connected_cluster.private_link_state.lower() == "enabled" and (
        enable_cluster_connect or enable_cl
    ):
        telemetry.set_exception(
            exception="Invalid arguments provided",
            fault_type=consts.Invalid_Argument_Fault_Type,
            summary="Invalid arguments provided",
        )
        err_msg = (
            "The features 'cluster-connect' and 'custom-locations' cannot be enabled for a private link "
            "enabled connected cluster."
        )
        raise InvalidArgumentValueError(err_msg)

    if enable_azure_rbac:
        if azrbac_skip_authz_check is None:
            azrbac_skip_authz_check = ""
        azrbac_skip_authz_check = escape_proxy_settings(azrbac_skip_authz_check)

    if enable_cl:
        subscription_id = (
            os.getenv("AZURE_SUBSCRIPTION_ID")
            if custom_token_passed is True
            else get_subscription_id(cmd.cli_ctx)
        )
        final_enable_cl, custom_locations_oid = check_cl_registration_and_get_oid(
            cmd, cl_oid, subscription_id
        )
        if not enable_cluster_connect and final_enable_cl:
            enable_cluster_connect = True
            logger.warning(
                "Enabling 'custom-locations' feature will enable 'cluster-connect' feature too."
            )
        if not final_enable_cl:
            features.remove("custom-locations")
            logger.warning(consts.Custom_Location_Enable_Failed_warning)
            if len(features) == 0:
                raise ClientRequestError("Failed to enable 'custom-locations' feature.")

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context, skip_ssl_verification)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    # Install helm client
    helm_client_location = install_helm_client(cmd)

    release_namespace = validate_release_namespace(
        client,
        cluster_name,
        resource_group_name,
        kube_config,
        kube_context,
        helm_client_location,
    )

    kubernetes_properties = {
        "Context.Default.AzureCLI.KubernetesVersion": kubernetes_version
    }

    if hasattr(connected_cluster, "distribution") and (
        connected_cluster.distribution is not None
    ):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties["Context.Default.AzureCLI.KubernetesDistro"] = (
            kubernetes_distro
        )

    if hasattr(connected_cluster, "infrastructure") and (
        connected_cluster.infrastructure is not None
    ):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties["Context.Default.AzureCLI.KubernetesInfra"] = (
            kubernetes_infra
        )

    telemetry.add_extension_event("connectedk8s", kubernetes_properties)

    # Adding helm repo
    if os.getenv("HELMREPONAME") and os.getenv("HELMREPOURL"):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    config_dp_endpoint, release_train = get_config_dp_endpoint(
        cmd, connected_cluster.location, values_file
    )

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv("HELMREGISTRY") or utils.get_helm_registry(
        cmd, config_dp_endpoint, release_train
    )

    reg_path_array = registry_path.split(":")
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version  # type: ignore[unreachable]
        registry_path = reg_path_array[0] + ":" + agent_version

    check_operation_support("enable-features", agent_version)

    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.AgentVersion": agent_version}
    )

    # Get Helm chart path
    chart_path = utils.get_chart_path(
        registry_path, kube_config, kube_context, helm_client_location
    )

    cmd_helm_upgrade = [
        helm_client_location,
        "upgrade",
        "azure-arc",
        chart_path,
        "--namespace",
        release_namespace,
        "--reuse-values",
        "--wait",
        "--output",
        "json",
    ]
    if values_file:
        cmd_helm_upgrade.extend(["-f", values_file])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    if enable_azure_rbac:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled=true"])
        # Setting the default authnMode mode as "arc" for guard. This mode uses PoP token based auth. and Arc RBAC 1P
        #  apps for authN/authZ.
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.authnMode=arc"])
        logger.warning(
            "Please use the kubelogin version v0.0.32 or higher which has support for generating PoP token(s). "
            "This is needed by guard running in 'arc' authN mode."
        )
        cmd_helm_upgrade.extend(
            [
                "--set",
                f"systemDefaultValues.guard.skipAuthzCheck={azrbac_skip_authz_check}",
            ]
        )
    if enable_cluster_connect:
        cmd_helm_upgrade.extend(
            ["--set", "systemDefaultValues.clusterconnect-agent.enabled=true"]
        )
    if final_enable_cl:
        cmd_helm_upgrade.extend(
            ["--set", "systemDefaultValues.customLocations.enabled=true"]
        )
        cmd_helm_upgrade.extend(
            [
                "--set",
                f"systemDefaultValues.customLocations.oid={custom_locations_oid}",
            ]
        )

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
            exception=error_helm_upgrade.decode("ascii"),
            fault_type=consts.Install_HelmRelease_Fault_Type,
            summary="Unable to install helm release",
        )
        raise CLIInternalError(
            str.format(consts.Error_enabling_Features, helm_upgrade_error_message)
        )
    if cl_oid and final_enable_cl and cl_oid == custom_locations_oid:
        logger.warning(consts.Manual_Custom_Location_Oid_Warning)
    return str.format(
        consts.Successfully_Enabled_Features, features, connected_cluster.name
    )


def disable_features(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    features: list[str],
    kube_config: str | None = None,
    kube_context: str | None = None,
    yes: bool = False,
    skip_ssl_verification: bool = False,
) -> str:
    features = [x.lower() for x in features]
    confirmation_message = (
        "Disabling few of the features may adversely impact dependent resources. Learn more "
        "about this at https://aka.ms/ArcK8sDependentResources. \n"
        + f"Are you sure you want to disable these features: {features}"
    )
    utils.user_confirmation(confirmation_message, yes)

    # Fetch Connected Cluster for agent version
    connected_cluster = client.get(resource_group_name, cluster_name)

    if (connected_cluster.kind is not None) and (
        connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind
    ):
        err_msg = (
            "Disable feature of a Provisioned Cluster is not supported from the Connected Cluster CLI. For "
            "information on how to disable a feature on a Provisioned Cluster using a cluster extension, please "
            "refer to: https://learn.microsoft.com/en-us/azure/aks/deploy-extensions-az-cli"
        )
        raise InvalidArgumentValueError(err_msg)

    logger.warning("This operation might take a while...\n")

    disable_clstr_connect, disable_azure_rbac, disable_cl = (
        utils.check_features_to_update(features)
    )

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context, skip_ssl_verification)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    # Install helm client
    helm_client_location = install_helm_client(cmd)

    release_namespace = validate_release_namespace(
        client,
        cluster_name,
        resource_group_name,
        kube_config,
        kube_context,
        helm_client_location,
    )

    kubernetes_properties = {
        "Context.Default.AzureCLI.KubernetesVersion": kubernetes_version
    }

    if hasattr(connected_cluster, "distribution") and (
        connected_cluster.distribution is not None
    ):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties["Context.Default.AzureCLI.KubernetesDistro"] = (
            kubernetes_distro
        )

    if hasattr(connected_cluster, "infrastructure") and (
        connected_cluster.infrastructure is not None
    ):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties["Context.Default.AzureCLI.KubernetesInfra"] = (
            kubernetes_infra
        )

    telemetry.add_extension_event("connectedk8s", kubernetes_properties)

    if disable_clstr_connect:
        try:
            helm_values = get_all_helm_values(
                release_namespace, kube_config, kube_context, helm_client_location
            )
            cl_enabled = (
                helm_values.get("systemDefaultValues")  # type: ignore[union-attr]
                .get("customLocations")
                .get("enabled")
            )
            cl_oid = (
                helm_values.get("systemDefaultValues").get("customLocations").get("oid")  # type: ignore[union-attr]
            )
            if not disable_cl and cl_enabled is True and cl_oid != "":
                raise ClientRequestError(
                    "Disabling 'cluster-connect' feature is not allowed when 'custom-locations' feature is enabled"
                )
        except AttributeError:
            pass
        except Exception as ex:
            raise ArgumentUsageError(str(ex))

    if disable_cl:
        logger.warning(
            "Disabling 'custom-locations' feature might impact some dependent resources. Learn more about this at "
            "https://aka.ms/ArcK8sDependentResources."
        )

    # Adding helm repo
    if os.getenv("HELMREPONAME") and os.getenv("HELMREPOURL"):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    get_chart_and_disable_features(
        cmd,
        connected_cluster,
        kube_config,
        kube_context,
        helm_client_location,
        release_namespace,
        values_file,
        disable_azure_rbac,
        disable_clstr_connect,
        disable_cl,
    )

    return str.format(
        consts.Successfully_Disabled_Features, features, connected_cluster.name
    )


def get_chart_and_disable_features(
    cmd: CLICommand,
    connected_cluster: ConnectedCluster,
    kube_config: str | None,
    kube_context: str | None,
    helm_client_location: str,
    release_namespace: str,
    values_file: str | None,
    disable_azure_rbac: bool = False,
    disable_clstr_connect: bool = False,
    disable_cl: bool = False,
) -> None:
    config_dp_endpoint, release_train = get_config_dp_endpoint(
        cmd, connected_cluster.location, values_file
    )

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv("HELMREGISTRY") or utils.get_helm_registry(
        cmd, config_dp_endpoint, release_train
    )

    reg_path_array = registry_path.split(":")
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version  # type: ignore[unreachable]
        registry_path = reg_path_array[0] + ":" + agent_version

    check_operation_support("disable-features", agent_version)

    telemetry.add_extension_event(
        "connectedk8s", {"Context.Default.AzureCLI.AgentVersion": agent_version}
    )

    # Get Helm chart path
    chart_path = utils.get_chart_path(
        registry_path, kube_config, kube_context, helm_client_location
    )

    cmd_helm_upgrade = [
        helm_client_location,
        "upgrade",
        "azure-arc",
        chart_path,
        "--namespace",
        release_namespace,
        "--reuse-values",
        "--wait",
        "--output",
        "json",
    ]
    if values_file:
        cmd_helm_upgrade.extend(["-f", values_file])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    if disable_azure_rbac:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled=false"])
    if disable_clstr_connect:
        cmd_helm_upgrade.extend(
            ["--set", "systemDefaultValues.clusterconnect-agent.enabled=false"]
        )
    if disable_cl:
        cmd_helm_upgrade.extend(
            ["--set", "systemDefaultValues.customLocations.enabled=false"]
        )
        cmd_helm_upgrade.extend(
            ["--set", "systemDefaultValues.customLocations.oid={}".format("")]
        )

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
            exception=error_helm_upgrade.decode("ascii"),
            fault_type=consts.Install_HelmRelease_Fault_Type,
            summary="Unable to install helm release",
        )
        raise CLIInternalError(
            str.format(consts.Error_disabling_Features, helm_upgrade_error_message)
        )


def disable_cluster_connect(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    kube_config: str | None,
    kube_context: str | None,
    values_file: str | None,
    release_namespace: str,
    helm_client_location: str,
) -> None:
    # Fetch Connected Cluster for agent version
    connected_cluster = client.get(resource_group_name, cluster_name)

    get_chart_and_disable_features(
        cmd,
        connected_cluster,
        kube_config,
        kube_context,
        helm_client_location,
        release_namespace,
        values_file,
        False,
        True,
        True,
    )


def load_kubernetes_configuration(filename: str) -> dict[str, Any]:
    try:
        with open(filename) as stream:
            k8s_config: dict[str, Any] = yaml.safe_load(stream) or {}
            return k8s_config
    except OSError as ex:
        if getattr(ex, "errno", 0) == errno.ENOENT:
            telemetry.set_exception(
                exception=ex,
                fault_type=consts.Kubeconfig_Failed_To_Load_Fault_Type,
                summary=f"{filename} does not exist",
            )
            raise FileOperationError(f"{filename} does not exist")
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        telemetry.set_exception(
            exception=ex,
            fault_type=consts.Kubeconfig_Failed_To_Load_Fault_Type,
            summary=f"Error parsing {filename} ({ex})",
        )
        raise FileOperationError(f"Error parsing {filename} ({ex})")

    assert False


def print_or_merge_credentials(
    path: str, kubeconfig: str, overwrite_existing: bool, context_name: str | None
) -> None:
    """Merge an unencrypted kubeconfig into the file at the specified path, or print it to
    stdout if the path is "-".
    """
    # Special case for printing to stdout
    if path == "-":
        print(kubeconfig)
        return

    # ensure that at least an empty ~/.kube/config exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                telemetry.set_exception(
                    exception=ex,
                    fault_type=consts.Failed_To_Merge_Credentials_Fault_Type,
                    summary="Could not create a kubeconfig directory.",
                )
                raise FileOperationError(
                    "Could not create a kubeconfig directory." + str(ex)
                )
    if not os.path.exists(path):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), "wt"):
            pass

    # merge the new kubeconfig into the existing one
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, "w+t")
    try:
        additional_file.write(kubeconfig)
        additional_file.flush()
        merge_kubernetes_configurations(
            path, temp_path, overwrite_existing, context_name
        )
    except yaml.YAMLError as ex:
        logger.warning("Failed to merge credentials to kube config file: %s", ex)
    finally:
        additional_file.close()
        os.remove(temp_path)


def merge_kubernetes_configurations(
    existing_file: str,
    addition_file: str,
    replace: bool,
    context_name: str | None = None,
) -> None:
    try:
        existing = load_kubernetes_configuration(existing_file)
        addition = load_kubernetes_configuration(addition_file)
    except Exception as ex:
        telemetry.set_exception(
            exception=ex,
            fault_type=consts.Failed_To_Load_K8s_Configuration_Fault_Type,
            summary="Exception while loading kubernetes configuration",
        )
        raise CLIInternalError(
            f"Exception while loading kubernetes configuration: {ex}"
        )

    if context_name is not None:
        addition["contexts"][0]["name"] = context_name
        addition["contexts"][0]["context"]["cluster"] = context_name
        addition["clusters"][0]["name"] = context_name
        addition["current-context"] = context_name

    # rename the admin context so it doesn't overwrite the user context
    for ctx in addition.get("contexts", []):
        try:
            if ctx["context"]["user"].startswith("clusterAdmin"):
                admin_name = ctx["name"] + "-admin"
                addition["current-context"] = ctx["name"] = admin_name
                break
        except (KeyError, TypeError):
            continue

    if not existing:
        existing = addition
    else:
        handle_merge(existing, addition, "clusters", replace)
        handle_merge(existing, addition, "users", replace)
        handle_merge(existing, addition, "contexts", replace)
        existing["current-context"] = addition["current-context"]

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != "Windows":
        existing_file_perms = f"{stat.S_IMODE(os.lstat(existing_file).st_mode):o}"
        if not existing_file_perms.endswith("600"):
            logger.warning(
                '%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                existing_file,
                existing_file_perms,
            )

    with open(existing_file, "w+") as stream:
        try:
            yaml.safe_dump(existing, stream, default_flow_style=False)
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Failed_To_Merge_Kubeconfig_File,
                summary="Exception while merging the kubeconfig file",
            )
            raise CLIInternalError(f"Exception while merging the kubeconfig file: {e}")

    current_context = addition.get("current-context", "UNKNOWN")
    msg = f'Merged "{current_context}" as current context in {existing_file}'
    print(msg)


def handle_merge(
    existing: dict[str, Any], addition: dict[str, Any], key: str, replace: bool
) -> None:
    if not addition[key]:
        return
    if existing[key] is None:
        existing[key] = addition[key]
        return

    i = addition[key][0]
    temp_list = []
    for j in existing[key]:
        remove_flag = False
        if not i.get("name", False) or not j.get("name", False):
            continue
        if i["name"] == j["name"]:
            if replace or i == j:
                remove_flag = True
            else:
                msg = "A different object named {} already exists in your kubeconfig file.\nOverwrite?"
                overwrite = False
                with contextlib.suppress(NoTTYException):
                    overwrite = prompt_y_n(msg.format(i["name"]))
                if overwrite:
                    remove_flag = True
                else:
                    msg = "A different object named {} already exists in {} in your kubeconfig file."
                    telemetry.set_exception(
                        exception="A different object with same name exists in the kubeconfig file",
                        fault_type=consts.Different_Object_With_Same_Name_Fault_Type,
                        summary=msg.format(i["name"], key),
                    )
                    raise FileOperationError(msg.format(i["name"], key))
        if not remove_flag:
            temp_list.append(j)

    existing[key][:] = temp_list
    existing[key].append(i)


def client_side_proxy_wrapper(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    token: str | None = None,
    path: str = os.path.join(os.path.expanduser("~"), ".kube", "config"),
    context_name: str | None = None,
    api_server_port: int = consts.API_SERVER_PORT,
) -> None:
    cloud = send_cloud_telemetry(cmd)
    profile = Profile()
    tenant_id = profile.get_subscription()["tenantId"]

    client_proxy_port = consts.CLIENT_PROXY_PORT

    # Check if the internal port is already open. If so and the user has specified a port,
    # try using the port before the user specified port instead.
    if (
        clientproxyutils.check_if_port_is_open(client_proxy_port)
        and api_server_port != consts.API_SERVER_PORT
    ):
        client_proxy_port = int(api_server_port) - 1

    if int(client_proxy_port) == int(api_server_port):
        raise ClientRequestError(
            f"Proxy uses port {client_proxy_port} internally.",
            recommendation="Please pass some other unused port through --port option.",
        )

    args = []
    operating_system = proxybinaryutils._get_client_operating_system()
    proc_name = f"arcProxy_{operating_system.lower()}"

    telemetry.set_debug_info("CSP Version is ", consts.CLIENT_PROXY_VERSION)
    telemetry.set_debug_info("OS is ", operating_system)

    if (
        clientproxyutils.check_process(proc_name)
    ) and clientproxyutils.check_if_port_is_open(api_server_port):
        err_msg = (
            "The proxy port is already in use, potentially by another proxy instance."
        )
        reco_msg = "Please stop the existing proxy instance or pass a different port through --port option."
        raise ClientRequestError(err_msg, recommendation=reco_msg)

    port_error_string = ""
    if clientproxyutils.check_if_port_is_open(api_server_port):
        port_error_string += (
            f"Port {api_server_port} is already in use. Please select a different port with "
            "--port option.\n"
        )
    if clientproxyutils.check_if_port_is_open(client_proxy_port):
        telemetry.set_exception(
            exception="Client proxy port was in use.",
            fault_type=consts.Client_Proxy_Port_Fault_Type,
            summary="Client proxy port was in use.",
        )
        port_error_string += (
            f"Port {client_proxy_port} is already in use. This is an internal port that proxy "
            "uses. Please ensure that this port is open before running 'az connectedk8s proxy'.\n"
        )
    if port_error_string != "":
        raise ClientRequestError(port_error_string)

    debug_mode = False
    if "--debug" in cmd.cli_ctx.data["safe_params"]:
        debug_mode = True

    install_location = proxybinaryutils.install_client_side_proxy(cmd, None, debug_mode)
    args.append(install_location)
    install_dir = os.path.dirname(install_location)

    # Creating config file to pass config to clientproxy
    config_file_location = os.path.join(install_dir, "config.yml")

    if os.path.isfile(config_file_location):
        try:
            os.remove(config_file_location)
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Remove_Config_Fault_Type,
                summary="Unable to remove old config file",
            )
            raise FileOperationError("Failed to remove old config." + str(e))

    # initializations
    user_type = "sat"
    dict_file: dict[str, Any] = {
        "server": {
            "httpPort": int(client_proxy_port),
            "httpsPort": int(api_server_port),
        },
        "identity": {"tenantID": tenant_id},
    }

    # if service account token is not passed
    if token is None:
        # Identifying type of logged in entity
        subscription_id = get_subscription_id(cmd.cli_ctx)
        account = Profile().get_subscription(subscription_id)
        user_type = account["user"]["type"]

        if user_type == "user":
            dict_file["identity"]["clientID"] = consts.CLIENTPROXY_CLIENT_ID
        else:
            dict_file["identity"]["clientID"] = account["user"]["name"]

    if cloud == "DOGFOOD":
        dict_file["cloud"] = "AzureDogFood"
    elif cloud == consts.Azure_ChinaCloudName:
        dict_file["cloud"] = "AzureChinaCloud"
    elif cloud == consts.Azure_USGovCloudName:
        dict_file["cloud"] = "AzureUSGovernmentCloud"
    else:
        dict_file["cloud"] = cloud

    # Azure local configurations.
    arm_metadata = utils.get_metadata(cmd.cli_ctx.cloud.endpoints.resource_manager)
    if "dataplaneEndpoints" in arm_metadata:
        dict_file["cloudConfig"] = {}
        dict_file["cloudConfig"]["resourceManagerEndpoint"] = arm_metadata[
            "resourceManager"
        ]
        relay_endpoint_suffix = arm_metadata["suffixes"]["relayEndpointSuffix"]
        if relay_endpoint_suffix[0] == ".":
            dict_file["cloudConfig"]["serviceBusEndpointSuffix"] = (
                relay_endpoint_suffix
            )[1:]
        else:
            dict_file["cloudConfig"]["serviceBusEndpointSuffix"] = relay_endpoint_suffix
        dict_file["cloudConfig"]["activeDirectoryEndpoint"] = arm_metadata[
            "authentication"
        ]["loginEndpoint"]

    telemetry.set_debug_info("User type is ", user_type)

    try:
        with open(config_file_location, "w") as f:
            yaml.dump(dict_file, f, default_flow_style=False)
    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Create_Config_Fault_Type,
            summary="Unable to create config file for proxy.",
        )
        raise FileOperationError("Failed to create config for proxy." + str(e))

    args.append("-c")
    args.append(config_file_location)

    if debug_mode:
        args.append("-d")

    client_side_proxy_main(
        cmd,
        tenant_id,
        client,
        resource_group_name,
        cluster_name,
        args,
        client_proxy_port,
        api_server_port,
        debug_mode,
        token=token,
        path=path,
        context_name=context_name,
    )


def client_side_proxy_main(
    cmd: CLICommand,
    tenant_id: str,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    args: list[str],
    client_proxy_port: int,
    api_server_port: int,
    debug_mode: bool,
    token: str | None = None,
    path: str = os.path.join(os.path.expanduser("~"), ".kube", "config"),
    context_name: str | None = None,
) -> None:
    hc_expiry, at_expiry, clientproxy_process = client_side_proxy(
        cmd,
        tenant_id,
        client,
        resource_group_name,
        cluster_name,
        ProxyStatus.FirstRun,
        args,
        client_proxy_port,
        api_server_port,
        debug_mode,
        token=token,
        path=path,
        context_name=context_name,
        clientproxy_process=None,
    )

    while True:
        time.sleep(60)
        if clientproxyutils.check_if_csp_is_running(clientproxy_process):
            flag = None
            if time.time() >= (hc_expiry - consts.CSP_REFRESH_TIME):
                flag = ProxyStatus.HCTokenRefresh
            elif time.time() >= (at_expiry - consts.CSP_REFRESH_TIME):
                flag = ProxyStatus.AccessTokenRefresh

            if flag is not None:
                new_hc_expiry, new_at_expiry, clientproxy_process = client_side_proxy(
                    cmd,
                    tenant_id,
                    client,
                    resource_group_name,
                    cluster_name,
                    flag,
                    args,
                    client_proxy_port,
                    api_server_port,
                    debug_mode,
                    token=token,
                    path=path,
                    context_name=context_name,
                    clientproxy_process=clientproxy_process,
                )
                if flag == ProxyStatus.HCTokenRefresh:
                    hc_expiry = new_hc_expiry
                elif flag == ProxyStatus.AccessTokenRefresh:
                    at_expiry = new_at_expiry

        else:
            telemetry.set_exception(
                exception="Process closed externally.",
                fault_type=consts.Proxy_Closed_Externally_Fault_Type,
                summary="Process closed externally.",
            )
            raise ManualInterrupt("Proxy closed externally.")


def client_side_proxy(
    cmd: CLICommand,
    tenant_id: str,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    flag: ProxyStatus,
    args: list[str],
    client_proxy_port: int,
    api_server_port: int,
    debug_mode: bool,
    token: str | None = None,
    path: str = os.path.join(os.path.expanduser("~"), ".kube", "config"),
    context_name: str | None = None,
    clientproxy_process: Popen[bytes] | None = None,
) -> tuple[int, int, Popen[bytes]]:
    subscription_id = get_subscription_id(cmd.cli_ctx)
    auth_method = "Token" if token is not None else "AAD"

    hc_expiry, at_expiry = 0, 0

    # Fetching hybrid connection details from Userrp
    # We do this in a separate process to avoid blocking the main thread
    # Since we still need to bring up the proxy and make API calls to it.
    if ProxyStatus.should_hc_token_refresh(flag):
        with ThreadPoolExecutor() as executor:
            future_get_cluster_user_credentials = executor.submit(
                proxylogic.get_cluster_user_credentials,
                client,
                resource_group_name,
                cluster_name,
                auth_method,
            )

    # Starting the client proxy process, if this is the first time that this function is invoked
    if flag == ProxyStatus.FirstRun:
        try:
            if debug_mode:
                clientproxy_process = Popen(args)
            else:
                clientproxy_process = Popen(args, stdout=DEVNULL, stderr=DEVNULL)
            print(f"Proxy is listening on port {api_server_port}")

        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Run_Clientproxy_Fault_Type,
                summary="Unable to run client proxy executable",
            )
            raise CLIInternalError(f"Failed to start proxy process: {e}")

    assert clientproxy_process is not None

    if token is None and ProxyStatus.should_access_token_refresh(flag):
        # jwt token approach if cli is using MSAL. This is for cli >= 2.30.0
        at_expiry = proxylogic.handle_post_at_to_csp(
            cmd, api_server_port, tenant_id, clientproxy_process
        )

    # Check hybrid connection details from Userrp
    response: Response

    if ProxyStatus.should_hc_token_refresh(flag):
        try:
            response_data = future_get_cluster_user_credentials.result()
        except Exception as e:
            clientproxy_process.terminate()
            utils.arm_exception_handler(
                e,
                consts.Get_Credentials_Failed_Fault_Type,
                "Unable to list cluster user credentials",
            )
            raise CLIInternalError(f"Failed to get credentials: {e}")

        data = clientproxyutils.prepare_clientproxy_data(response_data)
        hc_expiry = data["hybridConnectionConfig"]["expirationTime"]

        response = proxylogic.post_register_to_proxy(
            data,
            token,
            client_proxy_port,
            subscription_id,
            resource_group_name,
            cluster_name,
            clientproxy_process,
        )

    if flag == ProxyStatus.FirstRun:
        # Decoding kubeconfig into a string
        try:
            kubeconfig = json.loads(response.text)
        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Load_Kubeconfig_Fault_Type,
                summary="Unable to load Kubeconfig",
            )
            clientproxyutils.close_subprocess_and_raise_cli_error(
                clientproxy_process, "Failed to load kubeconfig." + str(e)
            )

        kubeconfig = kubeconfig["kubeconfigs"][0]["value"]
        kubeconfig = b64decode(kubeconfig).decode("utf-8")

        try:
            print_or_merge_credentials(path, kubeconfig, True, context_name)
            if path != "-":
                if context_name is None:
                    kubeconfig_obj = load_kubernetes_configuration(path)
                    temp_context_name = kubeconfig_obj["current-context"]
                else:
                    temp_context_name = context_name
                msg = (
                    f"Start sending kubectl requests on '{temp_context_name}' context using kubeconfig "
                    f"at {path}"
                )
                print(msg)

            print("Press Ctrl+C to close proxy.")

        except Exception as e:
            telemetry.set_exception(
                exception=e,
                fault_type=consts.Merge_Kubeconfig_Fault_Type,
                summary="Unable to merge kubeconfig.",
            )
            clientproxyutils.close_subprocess_and_raise_cli_error(
                clientproxy_process, "Failed to merge kubeconfig." + str(e)
            )

    return hc_expiry, at_expiry, clientproxy_process


def check_cl_registration_and_get_oid(
    cmd: CLICommand, cl_oid: str | None, subscription_id: str | None
) -> tuple[bool, str]:
    print(
        f"Step: {utils.get_utctimestring()}: Checking Custom Location(Microsoft.ExtendedLocation) RP Registration state for this Subscription, and attempt to get the Custom Location Object ID (OID),if registered"
    )
    enable_custom_locations = True
    custom_locations_oid = ""
    try:
        rp_client = resource_providers_client(cmd.cli_ctx, subscription_id)
        cl_registration_state = rp_client.get(
            consts.Custom_Locations_Provider_Namespace
        ).registration_state
        if cl_registration_state != "Registered":
            enable_custom_locations = False
            warn_msg = (
                "'Custom-locations' feature couldn't be enabled on this cluster as the pre-requisite "
                "registration of 'Microsoft.ExtendedLocation' was not met. More details for enabling this"
                " feature later on this cluster can be found here - https://aka.ms/EnableCustomLocations"
            )
            logger.warning(warn_msg)
        else:
            custom_locations_oid = get_custom_locations_oid(cmd, cl_oid)
            if custom_locations_oid == "":
                enable_custom_locations = False
    except Exception as e:
        enable_custom_locations = False
        warn_msg = (
            "The custom location feature was not enabled because the custom location OID could not be retrieved. Please refer to: https://aka.ms/enable-customlocation "
            "Proceeding with helm install..."
        )
        logger.warning(warn_msg)
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Custom_Locations_Registration_Check_Fault_Type,
            summary="Unable to fetch status of Custom Locations RP registration.",
        )
    return enable_custom_locations, custom_locations_oid


def get_custom_locations_oid(cmd: CLICommand, cl_oid: str | None) -> str:
    try:
        graph_client = graph_client_factory(cmd.cli_ctx)
        app_id = "bc313c14-388c-4e7d-a58e-70017303ee3b"
        # Requires Application.Read.All for Microsoft Graph since AAD Graph is deprecated. See below for work-around.
        # https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/
        # custom-locations#enable-custom-locations-on-your-cluster
        # Get Application Object for the CL App Id
        app_object = graph_client.service_principal_list(filter=f"appId eq '{app_id}'")
        # If we successfully obtained it
        if len(app_object) != 0:
            # If a CL OID was input and it did not match the one we fetched, log a warning
            if cl_oid is not None and cl_oid != app_object[0]["id"]:
                debug_msg = (
                    "The 'Custom-locations' OID passed is different from the actual OID(%s) of the Custom "
                    "Locations RP app. Proceeding with the correct one...",
                    app_object[0]["id"],
                )
                logger.debug(debug_msg)
            # We return the fetched CL OID, if we successfully retrieved it - irrespective of CL OID was input or not
            oid: str = app_object[0]["id"]  # Using the fetched OID
            return oid

        # If a Cl OID was not input and we failed to fetch the CL App object, log a warning
        if cl_oid is None:
            logger.warning(
                "Failed to enable Custom Locations feature on the cluster. Unable to fetch Object ID of Azure AD "
                "application used by Azure Arc service. Try enabling the feature by passing the "
                "--custom-locations-oid parameter directly. Learn more at https://aka.ms/CustomLocationsObjectID"
            )
            telemetry.set_exception(
                exception="Unable to fetch oid of custom locations app.",
                fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type_CLOid_None,
                summary="Unable to fetch oid for custom locations app.",
            )
            # Return empty for OID
            return ""
        # Else return the input OID
        return cl_oid
    except Exception as e:
        # Encountered exeption while fetching OID, log error
        log_string = "Unable to fetch the Custom Location OID  with permissions set on this account. The account does not have sufficient permissions to fetch or validate the OID."

        telemetry.set_exception(
            exception=e,
            fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type_Exception,
            summary="Unable to fetch oid for custom locations app.",
        )
        # If Cl OID was input, use that
        if cl_oid:
            log_string += "\nProceeding with using the OID manually provided to enable the 'custom-locations' feature without validation."
            log_string += "\nIf the manual OID is invalid, custom location may not be properly enabled."
            logger.warning(log_string)
            return cl_oid
        # If no Cl OID was input, log a Warning and return empty for OID
        log_string += "\nException encountered: " + str(e)
        logger.warning(log_string)
        return ""


def troubleshoot(
    cmd: CLICommand,
    client: ConnectedClusterOperations,
    resource_group_name: str,
    cluster_name: str,
    kube_config: str | None = None,
    kube_context: str | None = None,
    skip_ssl_verification: bool = False,
    no_wait: bool = False,
    tags: dict[str, str] | None = None,
) -> None:
    try:
        logger.warning("Diagnoser running. This may take a while ...\n")
        absolute_path = os.path.abspath(os.path.dirname(__file__))

        # Setting the intial values as True
        storage_space_available = True
        probable_sufficient_resource_for_agents = True

        # Setting default values for all checks as True
        diagnostic_checks = {
            consts.Fetch_Kubectl_Cluster_Info: consts.Diagnostic_Check_Incomplete,
            consts.Retrieve_Arc_Agents_Event_Logs: consts.Diagnostic_Check_Incomplete,
            consts.Retrieve_Arc_Agents_Logs: consts.Diagnostic_Check_Incomplete,
            consts.Retrieve_Deployments_Logs: consts.Diagnostic_Check_Incomplete,
            consts.Fetch_Connected_Cluster_Resource: consts.Diagnostic_Check_Incomplete,
            consts.Storing_Diagnoser_Results_Logs: consts.Diagnostic_Check_Incomplete,
            consts.MSI_Cert_Expiry_Check: consts.Diagnostic_Check_Incomplete,
            consts.KAP_Security_Policy_Check: consts.Diagnostic_Check_Incomplete,
            consts.KAP_Cert_Check: consts.Diagnostic_Check_Incomplete,
            consts.Diagnoser_Check: consts.Diagnostic_Check_Incomplete,
            consts.MSI_Cert_Check: consts.Diagnostic_Check_Incomplete,
            consts.Agent_Version_Check: consts.Diagnostic_Check_Incomplete,
            consts.Arc_Agent_State_Check: consts.Diagnostic_Check_Incomplete,
        }

        # Setting kube_config
        kube_config = set_kube_config(kube_config)
        kube_client.rest.logger.setLevel(logging.WARNING)

        # Loading the kubeconfig file in kubernetes client configuration
        load_kube_config(kube_config, kube_context, skip_ssl_verification)

        # Install helm client
        helm_client_location = install_helm_client(cmd)

        # Install kubectl client
        kubectl_client_location = install_kubectl_client()
        release_namespace = validate_release_namespace(
            client,
            cluster_name,
            resource_group_name,
            kube_config,
            kube_context,
            helm_client_location,
        )

        # Checking the connection to kubernetes cluster.
        # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
        # if the user had not logged in.
        check_kube_connection()

        # Fetch Connected Cluster for agent version
        connected_cluster = client.get(resource_group_name, cluster_name)

        # Creating timestamp folder to store all the diagnoser logs
        current_time = time.ctime(time.time())
        time_stamp = ""
        for elements in current_time:
            if elements == " ":
                time_stamp += "-"
                continue
            if elements == ":":
                time_stamp += "."
                continue
            time_stamp += elements
        time_stamp = cluster_name + "-" + time_stamp
        # Generate the diagnostic folder in a given location
        filepath_with_timestamp, diagnostic_folder_status = (
            utils.create_folder_diagnosticlogs(time_stamp, consts.Arc_Diagnostic_Logs)
        )

        if diagnostic_folder_status is not True:
            storage_space_available = False

        # To store the cluster-info of the cluster in current-context
        (
            diagnostic_checks[consts.Fetch_Kubectl_Cluster_Info],
            storage_space_available,
        ) = troubleshootutils.fetch_kubectl_cluster_info(
            filepath_with_timestamp,
            storage_space_available,
            kubectl_client_location,
            kube_config,
            kube_context,
        )

        # To store the connected cluster resource logs in the diagnostic folder
        (
            diagnostic_checks[consts.Fetch_Connected_Cluster_Resource],
            storage_space_available,
        ) = troubleshootutils.fetch_connected_cluster_resource(
            filepath_with_timestamp, connected_cluster, storage_space_available
        )
        corev1_api_instance = kube_client.CoreV1Api()

        # Check if agents have been added to the cluster
        arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(
            namespace="azure-arc"
        )

        # To verify if arc agents have been added to the cluster
        if arc_agents_pod_list.items:
            # For storing all arc agent logs using the CoreV1Api
            (
                diagnostic_checks[consts.Retrieve_Arc_Agents_Logs],
                storage_space_available,
            ) = troubleshootutils.retrieve_arc_agents_logs(
                corev1_api_instance, filepath_with_timestamp, storage_space_available
            )

            # For storing all arc agents events logs
            (
                diagnostic_checks[consts.Retrieve_Arc_Agents_Event_Logs],
                storage_space_available,
            ) = troubleshootutils.retrieve_arc_agents_event_logs(
                filepath_with_timestamp,
                storage_space_available,
                kubectl_client_location,
                kube_config,
                kube_context,
            )

            # For storing all the deployments logs using the AppsV1Api
            appv1_api_instance = kube_client.AppsV1Api()
            (
                diagnostic_checks[consts.Retrieve_Deployments_Logs],
                storage_space_available,
            ) = troubleshootutils.retrieve_deployments_logs(
                appv1_api_instance, filepath_with_timestamp, storage_space_available
            )

            # Check for the azure arc agent states
            (
                diagnostic_checks[consts.Arc_Agent_State_Check],
                storage_space_available,
                all_agents_stuck,
                probable_sufficient_resource_for_agents,
            ) = troubleshootutils.check_agent_state(
                corev1_api_instance, filepath_with_timestamp, storage_space_available
            )

            # Check for msi certificate
            if all_agents_stuck is False:
                diagnostic_checks[consts.MSI_Cert_Check] = (
                    troubleshootutils.check_msi_certificate_presence(
                        corev1_api_instance
                    )
                )

            # If msi certificate present then only we will perform msi certificate expiry check
            if (
                diagnostic_checks[consts.MSI_Cert_Check]
                == consts.Diagnostic_Check_Passed
            ):
                diagnostic_checks[consts.MSI_Cert_Expiry_Check] = (
                    troubleshootutils.check_msi_expiry(connected_cluster)
                )

            # If msi certificate present then only we will do Kube aad proxy checks
            if (
                diagnostic_checks[consts.MSI_Cert_Check]
                == consts.Diagnostic_Check_Passed
            ):
                diagnostic_checks[consts.KAP_Security_Policy_Check] = (
                    troubleshootutils.check_probable_cluster_security_policy(
                        corev1_api_instance,
                        helm_client_location,
                        release_namespace,
                        kube_config,
                        kube_context,
                    )
                )

                # If no security policy is present in cluster then we can check for the Kube aad proxy certificate
                if (
                    diagnostic_checks[consts.KAP_Security_Policy_Check]
                    == consts.Diagnostic_Check_Passed
                ):
                    diagnostic_checks[consts.KAP_Cert_Check] = (
                        troubleshootutils.check_kap_cert(corev1_api_instance)
                    )

            # Checking whether optional extra values file has been provided.
            values_file = utils.get_values_file()

            # Adding helm repo
            if os.getenv("HELMREPONAME") and os.getenv("HELMREPOURL"):
                utils.add_helm_repo(kube_config, kube_context, helm_client_location)

            config_dp_endpoint, release_train = get_config_dp_endpoint(
                cmd, connected_cluster.location, values_file
            )

            # Retrieving Helm chart OCI Artifact location
            registry_path = os.getenv("HELMREGISTRY") or utils.get_helm_registry(
                cmd, config_dp_endpoint, release_train
            )

            # Get azure-arc agent version for telemetry
            azure_arc_agent_version = registry_path.split(":")[1]

            # Check for agent version compatibility
            diagnostic_checks[consts.Agent_Version_Check] = (
                troubleshootutils.check_agent_version(
                    connected_cluster, azure_arc_agent_version
                )
            )
        else:
            logger.warning(
                "Error: Azure Arc agents are not present on the cluster. Please verify whether Arc onboarding of "
                "the Kubernetes cluster has been attempted.\n"
            )

        batchv1_api_instance = kube_client.BatchV1Api()
        # Performing diagnoser container check
        diagnostic_checks[consts.Diagnoser_Check], storage_space_available = (
            troubleshootutils.check_diagnoser_container(
                corev1_api_instance,
                batchv1_api_instance,
                filepath_with_timestamp,
                storage_space_available,
                absolute_path,
                probable_sufficient_resource_for_agents,
                helm_client_location,
                kubectl_client_location,
                release_namespace,
                diagnostic_checks[consts.KAP_Security_Policy_Check],
                kube_config,
                kube_context,
            )
        )

        # saving secrets in azure-arc namespace
        storage_space_available = troubleshootutils.get_secrets_azure_arc(
            corev1_api_instance,
            kubectl_client_location,
            kube_config,
            kube_context,
            filepath_with_timestamp,
            storage_space_available,
        )

        # saving helm values of azure-arc release
        storage_space_available = troubleshootutils.get_helm_values_azure_arc(
            corev1_api_instance,
            helm_client_location,
            release_namespace,
            kube_config,
            kube_context,
            filepath_with_timestamp,
            storage_space_available,
        )

        # saving metadata CR sanpshot
        storage_space_available = troubleshootutils.get_metadata_cr_snapshot(
            corev1_api_instance,
            kubectl_client_location,
            kube_config,
            kube_context,
            filepath_with_timestamp,
            storage_space_available,
        )

        # saving kube-aad-proxy CR snapshot only in the case private link is disabled
        if connected_cluster.private_link_state == "Disabled":
            storage_space_available = troubleshootutils.get_kubeaadproxy_cr_snapshot(
                corev1_api_instance,
                kubectl_client_location,
                kube_config,
                kube_context,
                filepath_with_timestamp,
                storage_space_available,
            )

        # saving signing key CR snapshot only if oidc issuer prfile is enabled
        oidc_issuer_profile_enabled = (
            connected_cluster.oidc_issuer_profile is not None
            and connected_cluster.oidc_issuer_profile.enabled
        )
        if oidc_issuer_profile_enabled:
            storage_space_available = troubleshootutils.get_signingkey_cr_snapshot(
                corev1_api_instance,
                kubectl_client_location,
                kube_config,
                kube_context,
                filepath_with_timestamp,
                storage_space_available,
            )

        # saving all other workload identity related information if enabled
        workload_identity_enabled = (
            connected_cluster.security_profile is not None
            and connected_cluster.security_profile.workload_identity is not None
            and connected_cluster.security_profile.workload_identity.enabled
        )
        if oidc_issuer_profile_enabled or workload_identity_enabled:
            # saving helm values of wiextension release
            storage_space_available = (
                troubleshootutils.get_helm_values_arc_workload_identity(
                    corev1_api_instance,
                    helm_client_location,
                    release_namespace,
                    kube_config,
                    kube_context,
                    filepath_with_timestamp,
                    storage_space_available,
                )
            )

            # saving arc-workload-identity logs
            (
                diagnostic_checks[consts.Retrieve_Arc_Workload_Identity_Pod_Logs],
                storage_space_available,
            ) = troubleshootutils.retrieve_arc_workload_identity_pod_logs(
                corev1_api_instance, filepath_with_timestamp, storage_space_available
            )

            # saving arc-workload-identity event logs
            (
                diagnostic_checks[consts.Retrieve_Arc_Workload_Identity_Events_Logs],
                storage_space_available,
            ) = troubleshootutils.retrieve_arc_workload_identity_event_logs(
                filepath_with_timestamp,
                storage_space_available,
                kubectl_client_location,
                kube_config,
                kube_context,
            )

            # saving arc-workload-identity deployment logs
            appv1_api_instance = kube_client.AppsV1Api()
            (
                diagnostic_checks[
                    consts.Retrieve_Arc_Workload_Identity_Deployments_Logs
                ],
                storage_space_available,
            ) = troubleshootutils.retrieve_arc_workload_identity_deployments_logs(
                appv1_api_instance, filepath_with_timestamp, storage_space_available
            )

        # checking cluster connectivity status
        cluster_connectivity_status = connected_cluster.connectivity_status

        if cluster_connectivity_status != "Connected":
            logger.warning(
                "Cluster connectivity status is not connected. The current state of the cluster is : %s",
                cluster_connectivity_status,
            )

        # Adding cli output to the logs
        diagnostic_checks[consts.Storing_Diagnoser_Results_Logs] = (
            troubleshootutils.fetching_cli_output_logs(
                filepath_with_timestamp, storage_space_available, 1
            )
        )

        # If all the checks passed then display no error found
        all_checks_passed = True
        for checks in diagnostic_checks:
            if diagnostic_checks[checks] != consts.Diagnostic_Check_Passed:
                all_checks_passed = False
        if storage_space_available:
            # Depending on whether all tests passes we will give the output
            if all_checks_passed:
                logger.warning(
                    "The diagnoser didn't find any issues on the cluster.\nThe diagnoser logs have been saved at this"
                    " path: %s.\nThese logs can be attached while filing a support ticket for further assistance.\n",
                    filepath_with_timestamp,
                )
            else:
                logger.warning(
                    "The diagnoser logs have been saved at this path: %s.\nThese logs can be attached while filing a "
                    "support ticket for further assistance.\n",
                    filepath_with_timestamp,
                )
        else:
            if all_checks_passed:
                logger.warning("The diagnoser didn't find any issues on the cluster.\n")
            logger.warning(
                "The diagnoser was unable to save logs to your machine. Please check whether sufficient storage is "
                "available and run the troubleshoot command again."
            )

    # Handling the user manual interrupt
    except KeyboardInterrupt:
        with contextlib.suppress(Exception):
            troubleshootutils.fetching_cli_output_logs(
                filepath_with_timestamp, storage_space_available, 0
            )
        raise ManualInterrupt("Process terminated externally.")


def install_kubectl_client() -> str:
    print(
        f"Step: {utils.get_utctimestring()}: Install Kubectl client if it does not exist"
    )
    # Return kubectl client path set by user
    kubectl_client_path = os.getenv("KUBECTL_CLIENT_PATH")
    if kubectl_client_path:
        return kubectl_client_path

    try:
        # Fetching the current directory where the cli installs the kubectl executable
        home_dir = os.path.expanduser("~")
        kubectl_filepath = os.path.join(home_dir, ".azure", "kubectl-client")

        with contextlib.suppress(FileExistsError):
            os.makedirs(kubectl_filepath)

        # Setting path depending on the OS being used
        operating_system = platform.system().lower()
        kubectl = "kubectl.exe" if operating_system == "windows" else "kubectl"
        kubectl_path = os.path.join(kubectl_filepath, kubectl)

        if os.path.isfile(kubectl_path):
            return kubectl_path

        # Downloading kubectl executable if its not present in the machine
        logger.warning(
            "Downloading kubectl client for first time. This can take few minutes..."
        )
        logging.disable(logging.CRITICAL)
        get_default_cli().invoke(
            ["aks", "install-cli", "--install-location", kubectl_path]
        )
        logging.disable(logging.NOTSET)
        logger.warning("\n")
        # Return the path of the kubectl executable
        return kubectl_path

    except Exception as e:
        telemetry.set_exception(
            exception=e,
            fault_type=consts.Download_And_Install_Kubectl_Fault_Type,
            summary="Failed to download and install kubectl",
        )
        raise CLIInternalError(f"Unable to install kubectl. Error: {e}")


def crd_cleanup_force_delete(
    cmd: CLICommand,
    kubectl_client_location: str,
    kube_config: str | None,
    kube_context: str | None,
) -> None:
    print(f"Step: {utils.get_utctimestring()}: Deleting Arc CRDs")

    active_directory_array = cmd.cli_ctx.cloud.endpoints.active_directory.split(".")
    # default for public, mc, ff clouds
    cloud_based_domain = active_directory_array[2]
    # special cases for USSec/USNat clouds
    if len(active_directory_array) == 4:
        cloud_based_domain = active_directory_array[2] + "." + active_directory_array[3]
    elif len(active_directory_array) == 5:
        cloud_based_domain = (
            active_directory_array[2]
            + "."
            + active_directory_array[3]
            + "."
            + active_directory_array[4]
        )

    timeout_for_crd_deletion = "20s"
    for crds in consts.CRD_FOR_FORCE_DELETE:
        full_crds = f"{crds}.{cloud_based_domain}"
        cmd_helm_delete = [
            kubectl_client_location,
            "delete",
            "crds",
            full_crds,
            "--ignore-not-found",
            "--wait",
            "--timeout",
            f"{timeout_for_crd_deletion}",
        ]
        if kube_config:
            cmd_helm_delete.extend(["--kubeconfig", kube_config])
        if kube_context:
            cmd_helm_delete.extend(["--context", kube_context])
        response_helm_delete = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        _, _ = response_helm_delete.communicate()

    # Timer added to have sufficient time after CRD deletion
    # to check the status of the CRD ( deleted or terminating )
    time.sleep(3)

    # patching yaml file path for removing CRD finalizer
    current_path = os.path.abspath(os.path.dirname(__file__))
    yaml_file_path = os.path.join(current_path, "remove_crd_finalizer.yaml")

    # Patch if CRD is in Terminating state
    for crds in consts.CRD_FOR_FORCE_DELETE:
        full_crds = f"{crds}.{cloud_based_domain}"
        cmd = [kubectl_client_location, "get", "crd", full_crds, "-ojson"]
        if kube_config:
            cmd.extend(["--kubeconfig", kube_config])
        if kube_context:
            cmd.extend(["--context", kube_context])
        cmd_output = Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, _ = cmd_output.communicate()

        if cmd_output.returncode == 0:
            changed_cmd = json.loads(cmd_output.communicate()[0].strip())
            status = changed_cmd["status"]["conditions"][-1]["type"]

            if status == "Terminating":
                patch_cmd = [
                    kubectl_client_location,
                    "patch",
                    "crd",
                    full_crds,
                    "--type=merge",
                    "--patch-file",
                    yaml_file_path,
                ]
                if kube_config:
                    patch_cmd.extend(["--kubeconfig", kube_config])
                if kube_context:
                    patch_cmd.extend(["--context", kube_context])
                output_patch_cmd = Popen(patch_cmd, stdout=PIPE, stderr=PIPE)
                _, _ = output_patch_cmd.communicate()


def check_operation_support(operation_name: str, agent_version: str) -> None:
    error_summary = f"This CLI version does not support {operation_name} for Agents older than v1.14"
    # Version check for stable release train (agent_version will be in X.Y.Z format as opposed to X.Y.Z-NONSTABLE)
    if "-" not in agent_version and (
        version.parse(agent_version) < version.parse("1.14.0")
    ):
        telemetry.set_exception(
            exception="Operation not supported on older Agents",
            fault_type=consts.Operation_Not_Supported_Fault_Type,
            summary=error_summary,
        )
        raise ClientRequestError(
            error_summary,
            recommendation="Please upgrade to the latest version of the Agents using 'az connectedk8s upgrade -g "
            + "<rg_name> -n <cluster_name>'.",
        )


def add_config_protected_settings(
    http_proxy: str,
    https_proxy: str,
    no_proxy: str,
    proxy_cert: str,
    container_log_path: str | None,
    configuration_settings: dict[str, Any] | None,
    configuration_protected_settings: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    redacted_protected_values: dict[str, Any] = {}

    # Initialize configuration_protected_settings if it is None
    if configuration_protected_settings is None:
        configuration_protected_settings = {}

    if configuration_settings is None:
        configuration_settings = {}

    if container_log_path:
        configuration_settings.setdefault(
            "logging", {"container_log_path": container_log_path}
        )
    if any([https_proxy, http_proxy, no_proxy, proxy_cert]):
        configuration_protected_settings.setdefault("proxy", {})
        configuration_settings.setdefault("proxy", {})
        if https_proxy:
            configuration_protected_settings["proxy"]["https_proxy"] = https_proxy
        if http_proxy:
            configuration_protected_settings["proxy"]["http_proxy"] = http_proxy
        if no_proxy:
            configuration_protected_settings["proxy"]["no_proxy"] = no_proxy
        if proxy_cert:
            configuration_protected_settings["proxy"]["proxy_cert"] = proxy_cert

    for feature, protected_settings in configuration_protected_settings.items():
        for setting, _ in protected_settings.items():
            if feature not in redacted_protected_values:
                redacted_protected_values[feature] = {}
            redacted_protected_values[feature][setting] = (
                f"redacted:{feature}:{setting}"
            )

    return (
        configuration_settings,
        configuration_protected_settings,
        redacted_protected_values,
    )
