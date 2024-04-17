# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import Namespace
import errno
import logging
from logging import exception
import os
import json
import tempfile
import time
from packaging import version
import subprocess
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from base64 import b64encode, b64decode
import stat
import platform
from xml.dom.pulldom import default_bufsize
from azure.core.exceptions import ClientAuthenticationError
import yaml
import urllib.request
import shutil
from _thread import interrupt_main
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from azure.cli.core import get_default_cli
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.prompting import NoTTYException
from azure.cli.command_modules.role import graph_client_factory
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core._profile import Profile
from azure.cli.core.util import sdk_no_wait
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ManualInterrupt, InvalidArgumentValueError, UnclassifiedUserFault, \
    CLIInternalError, FileOperationError, ClientRequestError, DeploymentError, ValidationError, \
    ArgumentUsageError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError
from azure.core.exceptions import HttpResponseError
from kubernetes import client as kube_client, config
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import resource_providers_client
from azext_connectedk8s._client_factory import \
    cf_connected_cluster_prev_2022_10_01, cf_connected_cluster_prev_2023_11_01
from azext_connectedk8s._client_factory import cf_connectedmachine
import azext_connectedk8s._constants as consts
import azext_connectedk8s._utils as utils
import azext_connectedk8s._clientproxyutils as clientproxyutils
import azext_connectedk8s._troubleshootutils as troubleshootutils
import azext_connectedk8s._precheckutils as precheckutils
from glob import glob
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterIdentity, ConnectedClusterPatch, \
    ListClusterUserCredentialProperties
from .vendored_sdks.preview_2022_10_01.models import ConnectedCluster as ConnectedClusterPreview
from .vendored_sdks.preview_2022_10_01.models import ConnectedClusterPatch as ConnectedClusterPatchPreview
from threading import Timer, Thread
import sys
import hashlib
import re
logger = get_logger(__name__)
# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def create_connectedk8s(cmd, client, resource_group_name, cluster_name, correlation_id=None, https_proxy="",
                        http_proxy="", no_proxy="", proxy_cert="", location=None, kube_config=None, kube_context=None,
                        no_wait=False, tags=None, distribution='generic', infrastructure='generic',
                        disable_auto_upgrade=False, cl_oid=None, onboarding_timeout="600", enable_private_link=None,
                        private_link_scope_resource_id=None, distribution_version=None, azure_hybrid_benefit=None,
                        yes=False, container_log_path=None):
    logger.warning("This operation might take a while...\n")

    # changing cli config to push telemetry in 1 hr interval
    try:
        if cmd.cli_ctx and hasattr(cmd.cli_ctx, 'config'):
            cmd.cli_ctx.config.set_value('telemetry', 'push_interval_in_hours', '1')
    except exception as e:
        telemetry.set_exception(exception=e,
                                fault_type=consts.Failed_To_Change_Telemetry_Push_Interval,
                                summary="Failed to change the telemetry push interval to 1 hr")

    # Validate custom token operation
    custom_token_passed, location = utils.validate_custom_token(cmd, resource_group_name, location)

    # Prompt for confirmation for few parameters
    if enable_private_link is True:
        confirmation_message = "The Cluster Connect and Custom Location features are not supported by Private Link at \
        this time. Enabling Private Link will disable these features. Are you sure you want to continue?"
        utils.user_confirmation(confirmation_message, yes)
        if cl_oid:
            logger.warning("Private Link is being enabled, and Custom Location is not supported by Private Link at \
            this time, so the '--custom-locations-oid' parameter will be ignored.")
    if azure_hybrid_benefit == "True":
        confirmation_message = "I confirm I have an eligible Windows Server license with Azure Hybrid Benefit to apply\
         this benefit to AKS on HCI or Windows Server. Visit https://aka.ms/ahb-aks for details"
        utils.user_confirmation(confirmation_message, yes)

    # Setting subscription id and tenant Id
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID') if custom_token_passed is True \
        else get_subscription_id(cmd.cli_ctx)
    if custom_token_passed is True:
        onboarding_tenant_id = os.getenv('AZURE_TENANT_ID')
    else:
        account = Profile().get_subscription(subscription_id)
        onboarding_tenant_id = account['homeTenantId']

    resource_id = f'/subscriptions/{subscription_id}/resourcegroups/{resource_group_name}/providers/Microsoft.\
        Kubernetes/connectedClusters/{cluster_name}/location/{location}'
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.resourceid': resource_id})

    # Send cloud information to telemetry
    azure_cloud = send_cloud_telemetry(cmd)

    # Checking provider registration status
    utils.check_provider_registrations(cmd.cli_ctx, subscription_id)

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
        telemetry.set_exception(exception='Proxy cert path does not exist',
                                fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
                                summary='Proxy cert path does not exist')
        raise InvalidArgumentValueError(str.format(consts.Proxy_Cert_Path_Does_Not_Exist_Error, proxy_cert))

    proxy_cert = proxy_cert.replace('\\', r'\\\\')

    # Set preview client if latest preview properties are provided.
    if enable_private_link is not None or distribution_version is not None or azure_hybrid_benefit is not None:
        client = cf_connected_cluster_prev_2023_11_01(cmd.cli_ctx, None)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        azure_cloud = consts.Azure_DogfoodCloudName

    arm_metadata = utils.get_metadata(cmd.cli_ctx.cloud.endpoints.resource_manager)
    config_dp_endpoint, release_train = get_config_dp_endpoint(cmd, location, values_file, arm_metadata)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    utils.try_list_node_fix()
    api_instance = kube_client.CoreV1Api()
    node_api_response = utils.validate_node_api_response(api_instance, None)
    is_arm64_cluster = check_arm64_node(node_api_response)

    required_node_exists = check_linux_node(node_api_response)

    # check if this is aks_hci low bandwith scenario
    lowbandwidth = False
    lowbandwith_distros = ["aks_workload", "aks_management", "aks_edge_k3s", "aks_edge_k8s"]

    if (infrastructure.lower() == 'azure_stack_hci') and (distribution.lower() in lowbandwith_distros):
        lowbandwidth = True

    # Install kubectl and helm
    try:
        kubectl_client_location = install_kubectl_client()
        helm_client_location = install_helm_client()
    except Exception as e:
        raise CLIInternalError("An exception has occured while trying to perform kubectl or helm install : {}"
                               .format(str(e)))
    # Handling the user manual interrupt
    except KeyboardInterrupt:
        raise ManualInterrupt('Process terminated externally.')

    # Pre onboarding checks
    diagnostic_checks = "Failed"
    try:
        # if aks_hci lowbandwidth scenario skip, otherwise continue to perform pre-onboarding check
        if not lowbandwidth:
            batchv1_api_instance = kube_client.BatchV1Api()
            storage_space_available = True

            current_time = time.ctime(time.time())
            time_stamp = ""
            for elements in current_time:
                if (elements == ' '):
                    time_stamp += '-'
                    continue
                elif (elements == ':'):
                    time_stamp += '.'
                    continue
                time_stamp += elements
            time_stamp = cluster_name + '-' + time_stamp

            # Generate the diagnostic folder in a given location
            filepath_with_timestamp, diagnostic_folder_status = \
                utils.create_folder_diagnosticlogs(time_stamp, consts.Pre_Onboarding_Check_Logs)

            if (diagnostic_folder_status is not True):
                storage_space_available = False

            # Performing cluster-diagnostic-checks
            diagnostic_checks, storage_space_available = \
                precheckutils.fetch_diagnostic_checks_results(api_instance, batchv1_api_instance, helm_client_location,
                                                              kubectl_client_location, kube_config, kube_context,
                                                              location, http_proxy, https_proxy, no_proxy, proxy_cert,
                                                              azure_cloud, filepath_with_timestamp,
                                                              storage_space_available)
            precheckutils.fetching_cli_output_logs(filepath_with_timestamp, storage_space_available, 1)

            if storage_space_available is False:
                logger.warning("There is no storage space available on your device and hence not saving cluster \
                    diagnostic check logs on your device")

    except Exception as e:
        telemetry.set_exception(exception="An exception has occured while trying to execute pre-onboarding diagnostic \
            checks : {}".format(str(e)),
                                fault_type=consts.Pre_Onboarding_Diagnostic_Checks_Execution_Failed,
                                summary="An exception has occured while trying to execute pre-onboarding diagnostic \
                                    checks : {}".format(str(e)))
        raise CLIInternalError("An exception has occured while trying to execute pre-onboarding diagnostic checks : \
            {}".format(str(e)))

    # Handling the user manual interrupt
    except KeyboardInterrupt:
        try:
            troubleshootutils.fetching_cli_output_logs(filepath_with_timestamp, storage_space_available, 0)
        except Exception:
            pass
        raise ManualInterrupt('Process terminated externally.')

    # If the checks didnt pass then stop the onboarding
    if diagnostic_checks != consts.Diagnostic_Check_Passed and lowbandwidth is False:
        if storage_space_available:
            logger.warning("The pre-check result logs logs have been saved at this path:" + filepath_with_timestamp +
                           " .\nThese logs can be attached while filing a support ticket for further assistance.\n")
        if (diagnostic_checks == consts.Diagnostic_Check_Incomplete):
            telemetry.set_exception(exception='Cluster Diagnostic Prechecks Incomplete',
                                    fault_type=consts.Cluster_Diagnostic_Prechecks_Incomplete,
                                    summary="Cluster Diagnostic Prechecks didnt complete in the cluster")
            raise ValidationError("Execution of pre-onboarding checks failed and hence not proceeding with cluster \
                onboarding. Please meet the prerequisites \
                    - " + consts.Onboarding_PreRequisites_Url + " and try onboarding again.")

        # if diagnostic_checks != consts.Diagnostic_Check_Incomplete
        telemetry.set_exception(exception='Cluster Diagnostic Prechecks Failed',
                                fault_type=consts.Cluster_Diagnostic_Prechecks_Failed,
                                summary="Cluster Diagnostic Prechecks Failed in the cluster")
        raise ValidationError("One or more pre-onboarding diagnostic checks failed and hence not proceeding with \
            cluster onboarding. Please resolve them and try onboarding again.")

    if lowbandwidth is False:
        print("The required pre-checks for onboarding have succeeded.")
    else:
        print("Skipped onboarding pre-checks for AKS-HCI low bandwidth scenario. Continuing...")

    if not required_node_exists:
        telemetry.set_user_fault()
        telemetry.set_exception(exception="Couldn't find any node on the kubernetes cluster with the OS 'linux'",
                                fault_type=consts.Linux_Node_Not_Exists,
                                summary="Couldn't find any node on the kubernetes cluster with the OS 'linux'")
        logger.warning("Please ensure that this Kubernetes cluster have any nodes with OS 'linux', for scheduling the \
            Arc-Agents onto and connecting to Azure. \
                Learn more at {}".format("https://aka.ms/ArcK8sSupportedOSArchitecture"))

    crb_permission = utils.can_create_clusterrolebindings()
    if not crb_permission:
        telemetry.set_exception(exception="Your credentials doesn't have permission to create clusterrolebindings on \
                                this kubernetes cluster.",
                                fault_type=consts.Cannot_Create_ClusterRoleBindings_Fault_Type,
                                summary="Your credentials doesn't have permission to create clusterrolebindings on \
                                    this kubernetes cluster.")
        raise ValidationError("Your credentials doesn't have permission to create clusterrolebindings on this \
            kubernetes cluster. Please check your permissions.")

    # Get kubernetes cluster info
    if distribution == 'generic':
        kubernetes_distro = get_kubernetes_distro(node_api_response)  # (cluster heuristics)
    else:
        kubernetes_distro = distribution

    if infrastructure == 'generic':
        kubernetes_infra = get_kubernetes_infra(node_api_response)  # (cluster heuristics)
    else:
        kubernetes_infra = infrastructure

    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro,
        'Context.Default.AzureCLI.KubernetesInfra': kubernetes_infra
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    # Checking if it is an AKS cluster
    is_aks_cluster = check_aks_cluster(kube_config, kube_context)
    if is_aks_cluster:
        logger.warning("Connecting an Azure Kubernetes Service (AKS) cluster to Azure Arc is only required for \
            running Arc enabled services like App Services and Data Services on the cluster. Other features like \
             Azure Monitor and Azure Defender are natively available on AKS. \
                 Learn more at {}.".format(" https://go.microsoft.com/fwlink/?linkid=2144200"))

    # Install helm client
    helm_client_location = install_helm_client()

    # Validate location
    utils.validate_location(cmd, location)
    resourceClient = cf_resource_groups(cmd.cli_ctx, subscription_id=subscription_id)

    # Validate location of private link scope resource. Throws error only if there is a location mismatch
    if enable_private_link is True:
        try:
            pls_arm_id_arr = private_link_scope_resource_id.split('/')
            hc_client = cf_connectedmachine(cmd.cli_ctx, pls_arm_id_arr[2])
            pls_get_result = hc_client.get(pls_arm_id_arr[4], pls_arm_id_arr[8])
            pls_location = pls_get_result.location.lower()
            if pls_location != location.lower():
                telemetry.set_exception(exception='Connected cluster resource and Private link scope resource are \
                    present in different locations',
                                        fault_type=consts.Pls_Location_Mismatch_Fault_Type,
                                        summary='Pls resource location mismatch')
                raise ArgumentUsageError("The location of the private link scope resource does not match the location \
                    of connected cluster resource. Please ensure that both the resources are in the same azure \
                    location.")
        except ArgumentUsageError as argex:
            raise (argex)
        except Exception as ex:
            if isinstance(ex, HttpResponseError):
                status_code = ex.response.status_code
                if status_code == 404:
                    telemetry.set_exception(exception='Private link scope resource does not exist',
                                            fault_type=consts.Pls_Resource_Not_Found,
                                            summary='Pls resource does not exist')
                    raise ArgumentUsageError("The private link scope resource '{}' does not exist. Please ensure that \
                        you pass a valid ARM Resource Id.".format(private_link_scope_resource_id))
            logger.warning("Error occured while checking the private link scope resource location: %s\n", ex)

    # Check Release Existance
    release_namespace = utils.get_release_namespace(kube_config, kube_context, helm_client_location)

    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api()
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                               error_message="Unable to read ConfigMap 'azure-clusterconfig' in \
                                                   'azure-arc' namespace: ",
                                               message_for_not_found="The helm release 'azure-arc' is present but the \
                                                    azure-arc namespace/configmap is missing. Please run 'helm delete \
                                                    azure-arc --namespace {} --no-hooks' to cleanup the release \
                                                    before onboarding the cluster again.".format(release_namespace))
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            preview_cluster_resource = None
            public_key = None

            try:
                preview_cluster_resource = get_connectedk8s_2023_11_01(cmd,
                                                                       configmap_rg_name,
                                                                       configmap_cluster_name)
                public_key = preview_cluster_resource.agent_public_key_certificate
            except Exception as e:  # pylint: disable=broad-except
                utils.arm_exception_handler(e,
                                            consts.Get_ConnectedCluster_Fault_Type,
                                            'Failed to check if connected cluster resource already exists.')

            if (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                # Re-put connected cluster
                # If cluster is of kind provisioned cluster, there are several properties that cannot be updated
                validate_existing_provisioned_cluster_for_reput(preview_cluster_resource, kubernetes_distro,
                                                                kubernetes_infra, enable_private_link,
                                                                private_link_scope_resource_id, distribution_version,
                                                                azure_hybrid_benefit, location)

                cc = generate_request_payload(location, public_key, tags, kubernetes_distro, kubernetes_infra,
                                              enable_private_link, private_link_scope_resource_id,
                                              distribution_version, azure_hybrid_benefit)
                cc_response = create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)
                cc_response = LongRunningOperation(cmd.cli_ctx)(cc_response)
                # Disabling cluster-connect if private link is getting enabled
                if enable_private_link is True:
                    disable_cluster_connect(cmd, client, resource_group_name, cluster_name, kube_config,
                                            kube_context, values_file, release_namespace, helm_client_location)
                return cc_response

            # else
            telemetry.set_exception(exception='The kubernetes cluster is already onboarded',
                                    fault_type=consts.Cluster_Already_Onboarded_Fault_Type,
                                    summary='Kubernetes cluster already onboarded')
            raise ArgumentUsageError("The kubernetes cluster you are trying to onboard is already onboarded to \
                the resource group '{}' with resource name \
                    '{}'.".format(configmap_rg_name, configmap_cluster_name))
        else:
            logger.warning("Cleaning up the stale arc agents present on the cluster before starting new onboarding.")
            # Explicit CRD Deletion
            crd_cleanup_force_delete(kubectl_client_location, kube_config, kube_context)
            # Cleaning up the cluster
            utils.delete_arc_agents(release_namespace, kube_config, kube_context, helm_client_location,
                                    is_arm64_cluster, True)

    else:
        if connected_cluster_exists(client, resource_group_name, cluster_name):
            telemetry.set_exception(exception='The connected cluster resource already exists',
                                    fault_type=consts.Resource_Already_Exists_Fault_Type,
                                    summary='Connected cluster resource already exists')
            raise ArgumentUsageError("The connected cluster resource {} already exists ".format(cluster_name) +
                                     "in the resource group {} ".format(resource_group_name) +
                                     "and corresponds to a different Kubernetes cluster.",
                                     recommendation="To onboard this Kubernetes cluster to Azure, specify different \
                                         resource name or resource group name.")
        else:
            # cleanup of stuck CRD if release namespace is not present/deleted
            crd_cleanup_force_delete(kubectl_client_location, kube_config, kube_context)

    # Resource group Creation
    if resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id) is False:
        from azure.cli.core.profiles import ResourceType
        ResourceGroup = cmd.get_models('ResourceGroup', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
        parameters = ResourceGroup(location=location)
        try:
            resourceClient.create_or_update(resource_group_name, parameters)
        except Exception as e:  # pylint: disable=broad-except
            utils.arm_exception_handler(e, consts.Create_ResourceGroup_Fault_Type,
                                        'Failed to create the resource group')

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else \
        utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

    # Get azure-arc agent version for telemetry
    azure_arc_agent_version = registry_path.split(':')[1]
    telemetry.add_extension_event('connectedk8s',
                                  {'Context.Default.AzureCLI.AgentVersion': azure_arc_agent_version})

    # Get helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    # Generate public-private key pair
    try:
        key_pair = RSA.generate(4096)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.KeyPair_Generate_Fault_Type,
                                summary='Failed to generate public-private key pair')
        raise CLIInternalError("Failed to generate public-private key pair. " + str(e))
    try:
        public_key = get_public_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PublicKey_Export_Fault_Type,
                                summary='Failed to export public key')
        raise CLIInternalError("Failed to export public key." + str(e))
    try:
        private_key_pem = get_private_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PrivateKey_Export_Fault_Type,
                                summary='Failed to export private key')
        raise CLIInternalError("Failed to export private key." + str(e))

    # Generate request payload
    cc = generate_request_payload(location, public_key, tags, kubernetes_distro, kubernetes_infra,
                                  enable_private_link, private_link_scope_resource_id, distribution_version,
                                  azure_hybrid_benefit)

    print("Azure resource provisioning has begun.")
    # Create connected cluster resource
    put_cc_response = create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)
    put_cc_response = LongRunningOperation(cmd.cli_ctx)(put_cc_response)
    print("Azure resource provisioning has finished.")
    # Checking if custom locations rp is registered and fetching oid if it is registered
    enable_custom_locations, custom_locations_oid = check_cl_registration_and_get_oid(cmd, cl_oid, subscription_id)

    print("Starting to install Azure arc agents on the Kubernetes cluster.")
    # Install azure-arc agents
    utils.helm_install_release(cmd.cli_ctx.cloud.endpoints.resource_manager, chart_path, subscription_id,
                               kubernetes_distro, kubernetes_infra, resource_group_name, cluster_name,
                               location, onboarding_tenant_id, http_proxy, https_proxy, no_proxy, proxy_cert,
                               private_key_pem, kube_config, kube_context, no_wait, values_file, azure_cloud,
                               disable_auto_upgrade, enable_custom_locations, custom_locations_oid,
                               helm_client_location, enable_private_link, arm_metadata,
                               onboarding_timeout, container_log_path)
    return put_cc_response


def validate_existing_provisioned_cluster_for_reput(cluster_resource, kubernetes_distro, kubernetes_infra,
                                                    enable_private_link, private_link_scope_resource_id,
                                                    distribution_version, azure_hybrid_benefit, location):
    if ((cluster_resource is not None) and (cluster_resource.kind is not None) and
            (cluster_resource.kind.lower() == consts.Provisioned_Cluster_Kind)):
        if azure_hybrid_benefit is not None:
            raise InvalidArgumentValueError("Updating the 'azure hybrid benefit' property of a Provisioned Cluster \
                is not supported from the Connected Cluster CLI. Please use the 'az aksarc update' CLI command.\
                \nhttps://learn.microsoft.com/en-us/cli/azure/aksarc?view=azure-cli-latest#az-aksarc-update")

        validation_values = [
            kubernetes_distro,
            kubernetes_infra,
            enable_private_link,
            private_link_scope_resource_id,
            distribution_version,
            azure_hybrid_benefit,
            location,
        ]

        for value in validation_values:
            if value is not None:
                raise InvalidArgumentValueError("Updating the following properties of a Provisioned Cluster are not supported from the Connected Cluster CLI: kubernetes_distro, kubernetes_infra, enable_private_link, private_link_scope_resource_id, distribution_version, azure_hybrid_benefit, location, public_key.\n\nPlease use the 'az aksarc update' CLI command. https://learn.microsoft.com/en-us/cli/azure/aksarc?view=azure-cli-latest#az-aksarc-update")


def send_cloud_telemetry(cmd):
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AzureCloud': cmd.cli_ctx.cloud.name})
    cloud_name = cmd.cli_ctx.cloud.name.upper()
    # Setting cloud name to format that is understood by golang SDK.
    if cloud_name == consts.PublicCloud_OriginalName:
        cloud_name = consts.Azure_PublicCloudName
    elif cloud_name == consts.USGovCloud_OriginalName:
        cloud_name = consts.Azure_USGovCloudName
    return cloud_name


def validate_env_file_dogfood(values_file):
    if not values_file:
        telemetry.set_exception(exception='Helm environment file not provided', fault_type=consts.Helm_Environment_File_Fault_Type,
                                summary='Helm environment file missing')
        raise ValidationError("Helm environment file is required when using Dogfood environment for onboarding the cluster.", recommendation="Please set the environment variable 'HELMVALUESPATH' to point to the file.")

    with open(values_file, 'r') as f:
        try:
            env_dict = yaml.safe_load(f)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Environment_File_Fault_Type,
                                    summary='Problem loading the helm environment file')
            raise FileOperationError("Problem loading the helm environment file: " + str(e))
        try:
            assert env_dict.get('global').get('azureEnvironment') == 'AZUREDOGFOOD'
            assert env_dict.get('systemDefaultValues').get('azureArcAgents').get('config_dp_endpoint_override')
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Environment_File_Fault_Type,
                                    summary='Problem loading the helm environment variables')
            raise FileOperationError("The required helm environment variables for dogfood onboarding are either not present in the file or incorrectly set.", recommendation="Please check the values 'global.azureEnvironment' and 'systemDefaultValues.azureArcAgents.config_dp_endpoint_override' in the file.")

    # Return the dp endpoint and release train
    dp_endpoint = env_dict.get('systemDefaultValues').get('azureArcAgents').get('config_dp_endpoint_override')
    release_train = env_dict.get('systemDefaultValues').get('azureArcAgents').get('releaseTrain')
    return dp_endpoint, release_train


def set_kube_config(kube_config):
    if kube_config:
        # Trim kubeconfig. This is required for windows os.
        if (kube_config.startswith("'") or kube_config.startswith('"')):
            kube_config = kube_config[1:]
        if (kube_config.endswith("'") or kube_config.endswith('"')):
            kube_config = kube_config[:-1]
        return kube_config
    return None


def escape_proxy_settings(proxy_setting):
    if proxy_setting is None:
        return ""
    proxy_setting = proxy_setting.replace(',', r'\,')
    proxy_setting = proxy_setting.replace('/', r'\/')
    return proxy_setting


def check_kube_connection():
    api_instance = kube_client.VersionApi()
    try:
        api_response = api_instance.get_code()
        return api_response.git_version
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Unable to verify connectivity to the Kubernetes cluster.")
        utils.kubernetes_exception_handler(e, consts.Kubernetes_Connectivity_FaultType, 'Unable to verify connectivity to the Kubernetes cluster')


def install_helm_client():
    # Return helm client path set by user
    if os.getenv('HELM_CLIENT_PATH'):
        return os.getenv('HELM_CLIENT_PATH')

    # Fetch system related info
    operating_system = platform.system().lower()
    machine_type = platform.machine()

    # Send machine telemetry
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.MachineType': machine_type})

    # Set helm binary download & install locations
    # TODO: [Kit] Move helm binaries to internal endpoints
    if (operating_system == 'windows'):
        download_location_string = f'.azure\\helm\\{consts.HELM_VERSION}\\helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip'
        install_location_string = f'.azure\\helm\\{consts.HELM_VERSION}\\{operating_system}-amd64\\helm.exe'
        # requestUri = f'{consts.HELM_STORAGE_URL}/helm/helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip'
        requestUri = f'https://get.helm.sh/helm-{consts.HELM_VERSION}-{operating_system}-amd64.zip'
    elif (operating_system == 'linux' or operating_system == 'darwin'):
        download_location_string = f'.azure/helm/{consts.HELM_VERSION}/helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz'
        install_location_string = f'.azure/helm/{consts.HELM_VERSION}/{operating_system}-amd64/helm'
        # requestUri = f'{consts.HELM_STORAGE_URL}/helm/helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz'
        requestUri = f'https://get.helm.sh/helm-{consts.HELM_VERSION}-{operating_system}-amd64.tar.gz'
    else:
        telemetry.set_exception(exception='Unsupported OS for installing helm client', fault_type=consts.Helm_Unsupported_OS_Fault_Type,
                                summary=f'{operating_system} is not supported for installing helm client')
        raise ClientRequestError(f'The {operating_system} platform is not currently supported for installing helm client.')

    download_location = os.path.expanduser(os.path.join('~', download_location_string))
    download_dir = os.path.dirname(download_location)
    install_location = os.path.expanduser(os.path.join('~', install_location_string))

    # Download compressed Helm binary if not already present
    if not os.path.isfile(download_location):
        # Creating the helm folder if it doesnt exist
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except Exception as e:
                telemetry.set_exception(exception=e, fault_type=consts.Create_Directory_Fault_Type,
                                        summary='Unable to create helm directory')
                raise ClientRequestError("Failed to create helm directory." + str(e))

        # Downloading compressed helm client executable
        logger.warning("Downloading helm client for first time. This can take few minutes...")
        retry_count = 3
        retry_delay = 5
        for i in range(retry_count):
            try:
                response = urllib.request.urlopen(requestUri)
                break
            except Exception as e:
                if i == retry_count - 1:
                    if "Connection reset by peer" in str(e):
                        telemetry.set_user_fault()
                    telemetry.set_exception(exception=e, fault_type=consts.Download_Helm_Fault_Type,
                                            summary='Unable to download helm client.')
                    raise CLIInternalError("Failed to download helm client.", recommendation="Please check your internet connection." + str(e))
                time.sleep(retry_delay)

        responseContent = response.read()
        response.close()

        # Creating the compressed helm binaries
        try:
            with open(download_location, 'wb') as f:
                f.write(responseContent)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Create_HelmExe_Fault_Type,
                                    summary='Unable to create helm executable')
            raise ClientRequestError("Failed to create helm executable." + str(e), recommendation="Please ensure that you delete the directory '{}' before trying again.".format(download_dir))

    # Extract compressed helm binary
    if not os.path.isfile(install_location):
        try:
            shutil.unpack_archive(download_location, download_dir)
            os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Extract_HelmExe_Fault_Type,
                                    summary='Unable to extract helm executable')
            raise ClientRequestError("Failed to extract helm executable." + str(e), recommendation="Please ensure that you delete the directory '{}' before trying again.".format(download_dir))

    return install_location


def resource_group_exists(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    try:
        groups.get(resource_group_name)
        return True
    except:  # pylint: disable=bare-except
        return False


def connected_cluster_exists(client, resource_group_name, cluster_name):
    try:
        client.get(resource_group_name, cluster_name)
    except Exception as e:  # pylint: disable=broad-except
        utils.arm_exception_handler(e, consts.Get_ConnectedCluster_Fault_Type, 'Failed to check if connected cluster resource already exists.', return_if_not_found=True)
        return False
    return True


def get_default_config_dp_endpoint(cmd, location):
    cloud_based_domain = cmd.cli_ctx.cloud.endpoints.active_directory.split('.')[2]
    config_dp_endpoint = "https://{}.dp.kubernetesconfiguration.azure.{}".format(location, cloud_based_domain)
    return config_dp_endpoint


def get_config_dp_endpoint(cmd, location, values_file, arm_metadata=None):
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
            logger.debug("'arcConfigEndpoint' doesn't exist under 'dataplaneEndpoints' in the ARM metadata.")
    # Get the default config dataplane endpoint.
    if config_dp_endpoint is None:
        config_dp_endpoint = get_default_config_dp_endpoint(cmd, location)
    return config_dp_endpoint, release_train


def get_public_key(key_pair):
    pubKey = key_pair.publickey()
    seq = asn1.DerSequence([pubKey.n, pubKey.e])
    enc = seq.encode()
    return b64encode(enc).decode('utf-8')


def load_kube_config(kube_config, kube_context):
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Problem loading the kubeconfig file')
        raise FileOperationError("Problem loading the kubeconfig file." + str(e))


def get_private_key(key_pair):
    privKey_DER = key_pair.exportKey(format='DER')
    return PEM.encode(privKey_DER, "RSA PRIVATE KEY")


def get_kubernetes_distro(api_response):  # Heuristic
    if api_response is None:
        return "generic"
    try:
        for node in api_response.items:
            labels = node.metadata.labels
            provider_id = str(node.spec.provider_id)
            annotations = node.metadata.annotations
            if labels.get("node.openshift.io/os_id"):
                return "openshift"
            if labels.get("kubernetes.azure.com/node-image-version"):
                return "aks"
            if labels.get("cloud.google.com/gke-nodepool") or labels.get("cloud.google.com/gke-os-distribution"):
                return "gke"
            if labels.get("eks.amazonaws.com/nodegroup"):
                return "eks"
            if labels.get("minikube.k8s.io/version"):
                return "minikube"
            if annotations.get("node.aksedge.io/distro") == 'aks_edge_k3s':
                return "aks_edge_k3s"
            if annotations.get("node.aksedge.io/distro") == 'aks_edge_k8s':
                return "aks_edge_k8s"
            if provider_id.startswith("kind://"):
                return "kind"
            if provider_id.startswith("k3s://"):
                return "k3s"
            if annotations.get("rke.cattle.io/external-ip") or annotations.get("rke.cattle.io/internal-ip"):
                return "rancher_rke"
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to fetch kubernetes distribution: " + str(e))
        utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Distro_Fault_Type, 'Unable to fetch kubernetes distribution',
                                           raise_error=False)
        return "generic"


def get_kubernetes_infra(api_response):  # Heuristic
    if api_response is None:
        return "generic"
    try:
        for node in api_response.items:
            provider_id = str(node.spec.provider_id)
            infra = provider_id.split(':')[0]
            if infra == "k3s" or infra == "kind":
                return "generic"
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
        logger.debug("Error occured while trying to fetch kubernetes infrastructure: " + str(e))
        utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Infra_Fault_Type, 'Unable to fetch kubernetes infrastructure',
                                           raise_error=False)
        return "generic"


def check_linux_node(api_response):
    try:
        for item in api_response.items:
            node_os = item.metadata.labels.get("kubernetes.io/os")
            if node_os == "linux":
                return True
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to find a linux node: " + str(e))
        utils.kubernetes_exception_handler(e, consts.Kubernetes_Node_Type_Fetch_Fault_OS, 'Unable to find a linux node',
                                           raise_error=False)
    return False


def check_arm64_node(api_response):
    try:
        for item in api_response.items:
            node_arch = item.metadata.labels.get("kubernetes.io/arch")
            if node_arch == "arm64":
                return True
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to find an arm64 node: " + str(e))
        utils.kubernetes_exception_handler(e, consts.Kubernetes_Node_Type_Fetch_Fault_Arch, 'Unable to find an arm64 node',
                                           raise_error=False)
    return False


def generate_request_payload(location, public_key, tags, kubernetes_distro, kubernetes_infra, enable_private_link, private_link_scope_resource_id, distribution_version, azure_hybrid_benefit):
    # Create connected cluster resource object
    identity = ConnectedClusterIdentity(
        type="SystemAssigned"
    )
    if tags is None:
        tags = {}
    cc = ConnectedCluster(
        location=location,
        identity=identity,
        agent_public_key_certificate=public_key,
        tags=tags,
        distribution=kubernetes_distro,
        infrastructure=kubernetes_infra
    )

    if enable_private_link is not None or distribution_version is not None or azure_hybrid_benefit is not None:
        private_link_state = None
        if enable_private_link is not None:
            private_link_state = "Enabled" if enable_private_link is True else "Disabled"
        cc = ConnectedClusterPreview(
            location=location,
            identity=identity,
            agent_public_key_certificate=public_key,
            tags=tags,
            distribution=kubernetes_distro,
            infrastructure=kubernetes_infra,
            private_link_scope_resource_id=private_link_scope_resource_id,
            private_link_state=private_link_state,
            azure_hybrid_benefit=azure_hybrid_benefit,
            distribution_version=distribution_version
        )
    return cc


def generate_patch_payload(tags, distribution, distribution_version, azure_hybrid_benefit):
    cc = ConnectedClusterPatchPreview(
        tags=tags,
        distribution=distribution,
        distribution_version=distribution_version,
        azure_hybrid_benefit=azure_hybrid_benefit
    )
    return cc


def get_kubeconfig_node_dict(kube_config=None):
    if kube_config is None:
        kube_config = os.getenv('KUBECONFIG') if os.getenv('KUBECONFIG') else os.path.join(os.path.expanduser('~'), '.kube', 'config')
    try:
        kubeconfig_data = config.kube_config._get_kube_config_loader_for_yaml_file(kube_config)._config
    except Exception as ex:
        telemetry.set_exception(exception=ex, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Error while fetching details from kubeconfig')
        raise FileOperationError("Error while fetching details from kubeconfig." + str(ex))
    return kubeconfig_data


def check_proxy_kubeconfig(kube_config, kube_context, arm_hash):
    server_address = get_server_address(kube_config, kube_context)
    regex_string = r'https://127.0.0.1:[0-9]{1,5}/' + arm_hash
    p = re.compile(regex_string)
    if p.fullmatch(server_address) is not None:
        return True
    else:
        return False


def check_aks_cluster(kube_config, kube_context):
    server_address = get_server_address(kube_config, kube_context)
    if server_address.find(".azmk8s.io:") == -1:
        return False
    else:
        return True


def get_server_address(kube_config, kube_context):
    config_data = get_kubeconfig_node_dict(kube_config=kube_config)
    try:
        all_contexts, current_context = config.list_kube_config_contexts(config_file=kube_config)
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Exception while trying to list kube contexts: %s\n", e)

    if kube_context is None:
        # Get name of the cluster from current context as kube_context is none.
        cluster_name = current_context.get('context').get('cluster')
        if cluster_name is None:
            logger.warning("Cluster not found in currentcontext: " + str(current_context))
    else:
        cluster_found = False
        for context in all_contexts:
            if context.get('name') == kube_context:
                cluster_found = True
                cluster_name = context.get('context').get('cluster')
                break
        if not cluster_found or cluster_name is None:
            logger.warning("Cluster not found in kubecontext: " + str(kube_context))

    clusters = config_data.safe_get('clusters')
    server_address = ""
    for cluster in clusters:
        if cluster.safe_get('name') == cluster_name:
            server_address = cluster.safe_get('cluster').get('server')
            break
    return server_address


def get_connectedk8s(cmd, client, resource_group_name, cluster_name):
    # Override preview client to show private link properties and cluster kind to customers
    client = cf_connected_cluster_prev_2023_11_01(cmd.cli_ctx, None)
    return client.get(resource_group_name, cluster_name)


def get_connectedk8s_2023_11_01(cmd, resource_group_name, cluster_name):
    # Override preview client to show private link properties and cluster kind to customers
    client = cf_connected_cluster_prev_2023_11_01(cmd.cli_ctx, None)
    return client.get(resource_group_name, cluster_name)


def list_connectedk8s(cmd, client, resource_group_name=None):
    # Override preview client to show private link properties and cluster kind to customers
    client = cf_connected_cluster_prev_2023_11_01(cmd.cli_ctx, None)
    if not resource_group_name:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def delete_connectedk8s(cmd, client, resource_group_name, cluster_name,
                        kube_config=None, kube_context=None, no_wait=False, force_delete=False, yes=False):

    # The force delete prompt is added because it can be used in the case where the config map is missing
    # so we cannot check if the user context is pointing to the cluster that he intends to delete
    if not force_delete:
        confirmation_message = "Are you sure you want to perform delete operation?"
        utils.user_confirmation(confirmation_message, yes)
    elif force_delete:
        confirmation_message = "Force delete will clean up all the azure-arc resources, including extensions. Please make sure your current kubeconfig is pointing to the right cluster.\n" + "Are you sure you want to perform force delete:"
        utils.user_confirmation(confirmation_message, yes)

    logger.warning("This operation might take a while ...\n")

    # Check if the cluster is of supported type for deletion
    preview_cluster_resource = get_connectedk8s_2023_11_01(cmd, resource_group_name, cluster_name)
    if (preview_cluster_resource is not None) and (preview_cluster_resource.kind is not None) and (preview_cluster_resource.kind.lower() == consts.Provisioned_Cluster_Kind):
        raise InvalidArgumentValueError("Deleting a Provisioned Cluster is not supported from the Connected Cluster CLI. Please use the 'az aksarc delete' CLI command.\nhttps://learn.microsoft.com/en-us/cli/azure/aksarc?view=azure-cli-latest#az-aksarc-delete")

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled
    # AKS clusters if the user had not logged in.
    check_kube_connection()

    # Install helm client
    helm_client_location = install_helm_client()

    # Check Release Existance
    release_namespace = utils.get_release_namespace(kube_config, kube_context, helm_client_location)

    utils.try_list_node_fix()
    api_instance = kube_client.CoreV1Api()
    node_api_response = utils.validate_node_api_response(api_instance, None)
    is_arm64_cluster = check_arm64_node(node_api_response)

    # Check forced delete flag
    if (force_delete):

        kubectl_client_location = install_kubectl_client()

        delete_cc_resource(client, resource_group_name, cluster_name, no_wait).result()

        # Explicit CRD Deletion
        crd_cleanup_force_delete(kubectl_client_location, kube_config, kube_context)

        if (release_namespace):
            utils.delete_arc_agents(release_namespace, kube_config, kube_context, helm_client_location, is_arm64_cluster, True)

        return

    if not release_namespace:
        delete_cc_resource(client, resource_group_name, cluster_name, no_wait).result()
        return

    # Loading config map
    try:
        configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
    except Exception as e:  # pylint: disable=broad-except
        utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                           error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                                           message_for_not_found="The helm release 'azure-arc' is present but the azure-arc namespace/configmap is missing. Please run 'helm delete azure-arc --namepace {} --no-hooks' to cleanup the release before onboarding the cluster again.".format(release_namespace))

    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID') if os.getenv('AZURE_ACCESS_TOKEN') else get_subscription_id(cmd.cli_ctx)

    if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and
            configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower() and configmap.data["AZURE_SUBSCRIPTION_ID"].lower() == subscription_id.lower()):

        armid = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Kubernetes/connectedClusters/{}".format(subscription_id, resource_group_name, cluster_name)
        arm_hash = hashlib.sha256(armid.lower().encode('utf-8')).hexdigest()

        if check_proxy_kubeconfig(kube_config, kube_context, arm_hash):
            telemetry.set_exception(exception='Encountered proxy kubeconfig during deletion.', fault_type=consts.Proxy_Kubeconfig_During_Deletion_Fault_Type,
                                    summary='The resource cannot be deleted as user is using proxy kubeconfig.')
            raise ClientRequestError("az connectedk8s delete is not supported when using the Cluster Connect kubeconfig.", recommendation="Run the az connectedk8s delete command with your kubeconfig file pointing to the actual Kubernetes cluster to ensure that the agents are cleaned up successfully as part of the delete command.")

        delete_cc_resource(client, resource_group_name, cluster_name, no_wait).result()
    else:
        telemetry.set_exception(exception='Unable to delete connected cluster', fault_type=consts.Bad_DeleteRequest_Fault_Type,
                                summary='The resource cannot be deleted as kubernetes cluster is onboarded with some other resource id')
        raise ArgumentUsageError("The current context in the kubeconfig file does not correspond " +
                                 "to the connected cluster resource specified. Agents installed on this cluster correspond " +
                                 "to the resource group name '{}' ".format(configmap.data["AZURE_RESOURCE_GROUP"]) +
                                 "and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_NAME"]))

    # Deleting the azure-arc agents
    utils.delete_arc_agents(release_namespace, kube_config, kube_context, helm_client_location, is_arm64_cluster)


def create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait):
    try:
        return sdk_no_wait(no_wait, client.begin_create, resource_group_name=resource_group_name,
                           cluster_name=cluster_name, connected_cluster=cc)
    except Exception as e:
        utils.arm_exception_handler(e, consts.Create_ConnectedCluster_Fault_Type, 'Unable to create connected cluster resource')


def patch_cc_resource(client, resource_group_name, cluster_name, cc):
    try:
        return client.update(resource_group_name=resource_group_name,
                             cluster_name=cluster_name, connected_cluster_patch=cc)
    except Exception as e:
        utils.arm_exception_handler(e, consts.Update_ConnectedCluster_Fault_Type, 'Unable to update connected cluster resource')


def delete_cc_resource(client, resource_group_name, cluster_name, no_wait):
    try:
        return sdk_no_wait(no_wait, client.begin_delete,
                           resource_group_name=resource_group_name,
                           cluster_name=cluster_name)
    except Exception as e:
        utils.arm_exception_handler(e, consts.Delete_ConnectedCluster_Fault_Type, 'Unable to delete connected cluster resource')


def update_connected_cluster_internal(client, resource_group_name, cluster_name, tags=None, distribution=None, distribution_version=None, azure_hybrid_benefit=None):
    cc = generate_patch_payload(tags, distribution, distribution_version, azure_hybrid_benefit)
    return patch_cc_resource(client, resource_group_name, cluster_name, cc)


# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def update_connected_cluster(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="", proxy_cert="",
                             disable_proxy=False, kube_config=None, kube_context=None, auto_upgrade=None, tags=None,
                             distribution=None, distribution_version=None, azure_hybrid_benefit=None, yes=False, container_log_path=None):

    # Prompt for confirmation for few parameters
    if azure_hybrid_benefit == "True":
        confirmation_message = "I confirm I have an eligible Windows Server license with Azure Hybrid Benefit to apply this benefit to AKS on HCI or Windows Server. Visit https://aka.ms/ahb-aks for details"
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
        telemetry.set_exception(exception='Proxy cert path does not exist', fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
                                summary='Proxy cert path does not exist')
        raise InvalidArgumentValueError(str.format(consts.Proxy_Cert_Path_Does_Not_Exist_Error, proxy_cert))

    proxy_cert = proxy_cert.replace('\\', r'\\\\')

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s_2023_11_01(cmd, resource_group_name, cluster_name)

    if (connected_cluster is not None) and (connected_cluster.kind is not None) and (connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind):
        raise InvalidArgumentValueError("Updating a Provisioned Cluster is not supported from the Connected Cluster CLI. Please use the 'az aksarc update' CLI command. https://learn.microsoft.com/en-us/cli/azure/aksarc?view=azure-cli-latest#az-aksarc-update")

    # Set preview client as most of the patchable fields are available in preview api-version
    client = cf_connected_cluster_prev_2022_10_01(cmd.cli_ctx, None)

    # Patching the connected cluster ARM resource
    arm_properties_unset = (tags is None and distribution is None and distribution_version is None and azure_hybrid_benefit is None)
    if not arm_properties_unset:
        patch_cc_response = update_connected_cluster_internal(client, resource_group_name, cluster_name, tags, distribution, distribution_version, azure_hybrid_benefit)

    proxy_params_unset = (https_proxy == "" and http_proxy == "" and no_proxy == "" and proxy_cert == "" and not disable_proxy)

    # Returning the ARM response if only AHB is being updated
    arm_properties_only_ahb_set = (tags is None and distribution is None and distribution_version is None and azure_hybrid_benefit is not None)
    if proxy_params_unset and auto_upgrade is None and container_log_path is None and arm_properties_only_ahb_set:
        return patch_cc_response

    if proxy_params_unset and not auto_upgrade and arm_properties_unset and not container_log_path:
        raise RequiredArgumentMissingError(consts.No_Param_Error)

    if (https_proxy or http_proxy or no_proxy) and disable_proxy:
        raise MutuallyExclusiveArgumentError(consts.EnableProxy_Conflict_Error)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    utils.try_list_node_fix()

    # Install helm client
    helm_client_location = install_helm_client()

    release_namespace = validate_release_namespace(client, cluster_name, resource_group_name, kube_config, kube_context, helm_client_location)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    kubernetes_properties = {'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version}

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties['Context.Default.AzureCLI.KubernetesDistro'] = kubernetes_distro

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties['Context.Default.AzureCLI.KubernetesInfra'] = kubernetes_infra

    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    config_dp_endpoint, release_train = get_config_dp_endpoint(cmd, connected_cluster.location, values_file)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    check_operation_support("update (properties)", agent_version)

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    cmd_helm_values = [helm_client_location, "get", "values", "azure-arc", "--namespace", release_namespace]
    if kube_config:
        cmd_helm_values.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_values.extend(["--kube-context", kube_context])

    user_values_location = os.path.join(os.path.expanduser('~'), '.azure', 'userValues.txt')
    existing_user_values = open(user_values_location, 'w+')
    response_helm_values_get = Popen(cmd_helm_values, stdout=existing_user_values, stderr=PIPE)
    _, error_helm_get_values = response_helm_values_get.communicate()
    if response_helm_values_get.returncode != 0:
        if ('forbidden' in error_helm_get_values.decode("ascii") or 'timed out waiting for the condition' in error_helm_get_values.decode("ascii")):
            telemetry.set_user_fault()
            telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Get_Helm_Values_Failed,
                                    summary='Error while doing helm get values azure-arc')
            raise CLIInternalError(str.format(consts.Update_Agent_Failure, error_helm_get_values.decode("ascii")))

    cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace", release_namespace,
                        "-f", user_values_location, "--wait", "--output", "json"]
    if values_file:
        cmd_helm_upgrade.extend(["-f", values_file])
    if auto_upgrade is not None:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.azureArcAgents.autoUpdate={}".format(auto_upgrade)])
    if https_proxy:
        cmd_helm_upgrade.extend(["--set", "global.httpsProxy={}".format(https_proxy)])
    if http_proxy:
        cmd_helm_upgrade.extend(["--set", "global.httpProxy={}".format(http_proxy)])
    if no_proxy:
        cmd_helm_upgrade.extend(["--set", "global.noProxy={}".format(no_proxy)])
    if https_proxy or http_proxy or no_proxy:
        cmd_helm_upgrade.extend(["--set", "global.isProxyEnabled={}".format(True)])
    if disable_proxy:
        cmd_helm_upgrade.extend(["--set", "global.isProxyEnabled={}".format(False)])
    if proxy_cert:
        cmd_helm_upgrade.extend(["--set-file", "global.proxyCert={}".format(proxy_cert)])
        cmd_helm_upgrade.extend(["--set", "global.isCustomCert={}".format(True)])
    if container_log_path is not None:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.fluent-bit.containerLogPath={}".format(container_log_path)])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    response_helm_upgrade = Popen(cmd_helm_upgrade, stdout=PIPE, stderr=PIPE)
    _, error_helm_upgrade = response_helm_upgrade.communicate()
    if response_helm_upgrade.returncode != 0:
        helm_upgrade_error_message = error_helm_upgrade.decode("ascii")
        if any(message in helm_upgrade_error_message for message in consts.Helm_Install_Release_Userfault_Messages):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_upgrade.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        try:
            os.remove(user_values_location)
        except OSError:
            pass
        raise CLIInternalError(str.format(consts.Update_Agent_Failure, error_helm_upgrade.decode("ascii")))

    logger.info(str.format(consts.Update_Agent_Success, connected_cluster.name))
    try:
        os.remove(user_values_location)
    except OSError:
        pass
    if not arm_properties_unset:
        return patch_cc_response


def upgrade_agents(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None, arc_agent_version=None, upgrade_timeout="600"):
    # Check if cluster supports upgrading
    connected_cluster = get_connectedk8s_2023_11_01(cmd, resource_group_name, cluster_name)

    if (connected_cluster is not None) and (connected_cluster.kind is not None) and (connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind):
        raise InvalidArgumentValueError("Upgrading a Provisioned Cluster is not supported from the Connected Cluster CLI. Please use the 'az aksarc upgrade' CLI command. https://learn.microsoft.com/en-us/cli/azure/aksarc?view=azure-cli-latest#az-aksarc-upgrade")

    logger.warning("This operation might take a while...\n")

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    utils.try_list_node_fix()
    api_instance = kube_client.CoreV1Api()

    # Install helm client
    helm_client_location = install_helm_client()

    # Check Release Existence
    release_namespace = utils.get_release_namespace(kube_config, kube_context, helm_client_location)
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api()
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                               error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                                               message_for_not_found="The helm release 'azure-arc' is present but the azure-arc namespace/configmap is missing. Please run 'helm delete azure-arc --namespace {} --no-hooks' to cleanup the release before onboarding the cluster again.".format(release_namespace))
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if not (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                telemetry.set_exception(exception='The provided cluster name and rg correspond to different cluster', fault_type=consts.Upgrade_RG_Cluster_Name_Conflict,
                                        summary='The provided cluster name and resource group name do not correspond to the kubernetes cluster being upgraded.')
                raise ArgumentUsageError("The provided cluster name and resource group name do not correspond to the kubernetes cluster you are trying to upgrade.",
                                         recommendation="Please upgrade the cluster, with correct resource group and cluster name, using 'az upgrade agents -g <rg_name> -n <cluster_name>'.")
        else:
            telemetry.set_exception(exception='The corresponding CC resource does not exist', fault_type=consts.Corresponding_CC_Resource_Deleted_Fault,
                                    summary='CC resource corresponding to this cluster has been deleted by the customer')
            raise ArgumentUsageError("There exist no ConnectedCluster resource corresponding to this kubernetes Cluster.",
                                     recommendation="Please cleanup the helm release first using 'az connectedk8s delete -n <connected-cluster-name> -g <resource-group-name>' and re-onboard the cluster using " +
                                     "'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>'")

        auto_update_enabled = configmap.data["AZURE_ARC_AUTOUPDATE"]
        if auto_update_enabled == "true":
            telemetry.set_exception(exception='connectedk8s upgrade called when auto-update is set to true', fault_type=consts.Manual_Upgrade_Called_In_Auto_Update_Enabled,
                                    summary='az connectedk8s upgrade to manually upgrade agents and extensions is only supported when auto-upgrade is set to false.')
            raise ClientRequestError("az connectedk8s upgrade to manually upgrade agents and extensions is only supported when auto-upgrade is set to false.",
                                     recommendation="Please run 'az connectedk8s update -n <connected-cluster-name> -g <resource-group-name> --auto-upgrade false' before performing manual upgrade")

    else:
        telemetry.set_exception(exception="The azure-arc release namespace couldn't be retrieved", fault_type=consts.Release_Namespace_Not_Found,
                                summary="The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc.")
        raise ClientRequestError("The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc.",
                                 recommendation="Please run 'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>' to onboard the cluster")

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    kubernetes_properties = {'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version}

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties['Context.Default.AzureCLI.KubernetesDistro'] = kubernetes_distro

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties['Context.Default.AzureCLI.KubernetesInfra'] = kubernetes_infra

    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    config_dp_endpoint, release_train = get_config_dp_endpoint(cmd, connected_cluster.location, values_file)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    if arc_agent_version is not None:
        agent_version = arc_agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    cmd_helm_values = [helm_client_location, "get", "values", "azure-arc", "--namespace", release_namespace]
    if kube_config:
        cmd_helm_values.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_values.extend(["--kube-context", kube_context])

    response_helm_values_get = Popen(cmd_helm_values, stdout=PIPE, stderr=PIPE)
    output_helm_values, error_helm_get_values = response_helm_values_get.communicate()
    if response_helm_values_get.returncode != 0:
        if ('forbidden' in error_helm_get_values.decode("ascii") or 'timed out waiting for the condition' in error_helm_get_values.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Get_Helm_Values_Failed,
                                summary='Error while doing helm get values azure-arc')
        raise CLIInternalError(str.format(consts.Upgrade_Agent_Failure, error_helm_get_values.decode("ascii")))

    output_helm_values = output_helm_values.decode("ascii")

    try:
        existing_user_values = yaml.safe_load(output_helm_values)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Helm_Existing_User_Supplied_Value_Get_Fault,
                                summary='Problem loading the helm existing user supplied values')
        raise CLIInternalError("Problem loading the helm existing user supplied values: " + str(e))

    # Change --timeout format for helm client to understand
    upgrade_timeout = upgrade_timeout + "s"
    cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace", release_namespace,
                        "--output", "json", "--atomic", "--wait", "--timeout", "{}".format(upgrade_timeout)]

    proxy_enabled_param_added = False
    infra_added = False
    for key, value in utils.flatten(existing_user_values).items():
        if value is not None:
            if key == "global.isProxyEnabled":
                proxy_enabled_param_added = True
            if (key == "global.httpProxy" or key == "global.httpsProxy" or key == "global.noProxy"):
                value = escape_proxy_settings(value)
                if value and not proxy_enabled_param_added:
                    cmd_helm_upgrade.extend(["--set", "global.isProxyEnabled={}".format(True)])
                    proxy_enabled_param_added = True
            if key == "global.kubernetesDistro" and value == "default":
                value = "generic"
            if key == "global.kubernetesInfra":
                infra_added = True
            cmd_helm_upgrade.extend(["--set", "{}={}".format(key, value)])

    if not proxy_enabled_param_added:
        cmd_helm_upgrade.extend(["--set", "global.isProxyEnabled={}".format(False)])

    if not infra_added:
        cmd_helm_upgrade.extend(["--set", "global.kubernetesInfra={}".format("generic")])

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
        if any(message in helm_upgrade_error_message for message in consts.Helm_Install_Release_Userfault_Messages):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_upgrade.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        raise CLIInternalError(str.format(consts.Upgrade_Agent_Failure, error_helm_upgrade.decode("ascii")))

    return str.format(consts.Upgrade_Agent_Success, connected_cluster.name)


def validate_release_namespace(client, cluster_name, resource_group_name, kube_config, kube_context, helm_client_location):
    # Check Release Existance
    release_namespace = utils.get_release_namespace(kube_config, kube_context, helm_client_location)
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api()
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                               error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                                               message_for_not_found="The helm release 'azure-arc' is present but the azure-arc namespace/configmap is missing. Please run 'helm delete azure-arc --namespace {} --no-hooks' to cleanup the release before onboarding the cluster again.".format(release_namespace))
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if not (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                telemetry.set_exception(exception='The provided cluster name and rg correspond to different cluster', fault_type=consts.Operate_RG_Cluster_Name_Conflict,
                                        summary='The provided cluster name and resource group name do not correspond to the kubernetes cluster being operated on.')
                raise ArgumentUsageError("The provided cluster name and resource group name do not correspond to the kubernetes cluster you are operating on.",
                                         recommendation="Please use the cluster, with correct resource group and cluster name.")
        else:
            telemetry.set_exception(exception='The corresponding CC resource does not exist', fault_type=consts.Corresponding_CC_Resource_Deleted_Fault,
                                    summary='CC resource corresponding to this cluster has been deleted by the customer')
            raise ClientRequestError("There exist no ConnectedCluster resource corresponding to this kubernetes Cluster.",
                                     recommendation="Please cleanup the helm release first using 'az connectedk8s delete -n <connected-cluster-name> -g <resource-group-name>' and re-onboard the cluster using " +
                                     "'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>'")

    else:
        telemetry.set_exception(exception="The azure-arc release namespace couldn't be retrieved", fault_type=consts.Release_Namespace_Not_Found,
                                summary="The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc.")
        raise ClientRequestError("The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc.",
                                 recommendation="Please run 'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>' to onboard the cluster")
    return release_namespace


def get_all_helm_values(release_namespace, kube_config, kube_context, helm_client_location):
    cmd_helm_values = [helm_client_location, "get", "values", "--all", "azure-arc", "--namespace", release_namespace]
    if kube_config:
        cmd_helm_values.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_values.extend(["--kube-context", kube_context])

    response_helm_values_get = Popen(cmd_helm_values, stdout=PIPE, stderr=PIPE)
    output_helm_values, error_helm_get_values = response_helm_values_get.communicate()
    if response_helm_values_get.returncode != 0:
        if 'forbidden' in error_helm_get_values.decode("ascii"):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_get_values.decode("ascii"), fault_type=consts.Get_Helm_Values_Failed,
                                summary='Error while doing helm get values azure-arc')
        raise CLIInternalError("Error while getting the helm values in the azure-arc namespace: " + error_helm_get_values.decode("ascii"))

    output_helm_values = output_helm_values.decode("ascii")

    try:
        existing_values = yaml.safe_load(output_helm_values)
        return existing_values
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Helm_Existing_User_Supplied_Value_Get_Fault,
                                summary='Problem loading the helm existing values')
        raise CLIInternalError("Problem loading the helm existing values: " + str(e))


def enable_features(cmd, client, resource_group_name, cluster_name, features, kube_config=None, kube_context=None,
                    azrbac_client_id=None, azrbac_client_secret=None, azrbac_skip_authz_check=None, cl_oid=None):
    logger.warning("This operation might take a while...\n")

    # Validate custom token operation
    custom_token_passed, _ = utils.validate_custom_token(cmd, resource_group_name, "dummyLocation")

    features = [x.lower() for x in features]
    enable_cluster_connect, enable_azure_rbac, enable_cl = utils.check_features_to_update(features)

    # Check if cluster is private link enabled
    connected_cluster = get_connectedk8s_2023_11_01(cmd, resource_group_name, cluster_name)

    if (connected_cluster is not None) and (connected_cluster.kind is not None) and (connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind):
        raise InvalidArgumentValueError("Enable feature of a Provisioned Cluster is not supported from the Connected Cluster CLI. For information on how to enable a feature on a Provisioned Cluster using a cluster extension, please refer to: https://learn.microsoft.com/en-us/azure/aks/deploy-extensions-az-cli")

    if connected_cluster.private_link_state.lower() == "enabled" and (enable_cluster_connect or enable_cl):
        telemetry.set_exception(exception='Invalid arguments provided', fault_type=consts.Invalid_Argument_Fault_Type,
                                summary='Invalid arguments provided')
        raise InvalidArgumentValueError("The features 'cluster-connect' and 'custom-locations' cannot be enabled for a private link enabled connected cluster.")

    if enable_azure_rbac:
        if azrbac_skip_authz_check is None:
            azrbac_skip_authz_check = ""
        azrbac_skip_authz_check = escape_proxy_settings(azrbac_skip_authz_check)

    if enable_cl:
        subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID') if custom_token_passed is True else get_subscription_id(cmd.cli_ctx)
        enable_cl, custom_locations_oid = check_cl_registration_and_get_oid(cmd, cl_oid, subscription_id)
        if not enable_cluster_connect and enable_cl:
            enable_cluster_connect = True
            logger.warning("Enabling 'custom-locations' feature will enable 'cluster-connect' feature too.")
        if not enable_cl:
            features.remove("custom-locations")
            if len(features) == 0:
                raise ClientRequestError("Failed to enable 'custom-locations' feature.")

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    utils.try_list_node_fix()

    # Install helm client
    helm_client_location = install_helm_client()

    release_namespace = validate_release_namespace(client, cluster_name, resource_group_name, kube_config, kube_context, helm_client_location)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    kubernetes_properties = {'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version}

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties['Context.Default.AzureCLI.KubernetesDistro'] = kubernetes_distro

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties['Context.Default.AzureCLI.KubernetesInfra'] = kubernetes_infra

    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    config_dp_endpoint, release_train = get_config_dp_endpoint(cmd, connected_cluster.location, values_file)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    check_operation_support("enable-features", agent_version)

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace", release_namespace,
                        "--reuse-values",
                        "--wait", "--output", "json"]
    if values_file:
        cmd_helm_upgrade.extend(["-f", values_file])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    if enable_azure_rbac:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled=true"])
        # Setting the default authnMode mode as "arc" for guard. This mode uses PoP token based auth. and Arc RBAC 1P apps for authN/authZ.
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.authnMode=arc"])
        logger.warning("Please use the kubelogin version v0.0.32 or higher which has support for generating PoP token(s). This is needed by guard running in 'arc' authN mode.")
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.skipAuthzCheck={}".format(azrbac_skip_authz_check)])
    if enable_cluster_connect:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.clusterconnect-agent.enabled=true"])
    if enable_cl:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.enabled=true"])
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.oid={}".format(custom_locations_oid)])

    response_helm_upgrade = Popen(cmd_helm_upgrade, stdout=PIPE, stderr=PIPE)
    _, error_helm_upgrade = response_helm_upgrade.communicate()
    if response_helm_upgrade.returncode != 0:
        helm_upgrade_error_message = error_helm_upgrade.decode("ascii")
        if any(message in helm_upgrade_error_message for message in consts.Helm_Install_Release_Userfault_Messages):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_upgrade.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        raise CLIInternalError(str.format(consts.Error_enabling_Features, error_helm_upgrade.decode("ascii")))

    return str.format(consts.Successfully_Enabled_Features, features, connected_cluster.name)


def disable_features(cmd, client, resource_group_name, cluster_name, features, kube_config=None, kube_context=None,
                     yes=False):

    features = [x.lower() for x in features]
    confirmation_message = "Disabling few of the features may adversely impact dependent resources. Learn more about this at https://aka.ms/ArcK8sDependentResources. \n" + "Are you sure you want to disable these features: {}".format(features)
    utils.user_confirmation(confirmation_message, yes)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s_2023_11_01(cmd, resource_group_name, cluster_name)

    if (connected_cluster is not None) and (connected_cluster.kind is not None) and (connected_cluster.kind.lower() == consts.Provisioned_Cluster_Kind):
        raise InvalidArgumentValueError("Disable feature of a Provisioned Cluster is not supported from the Connected Cluster CLI. For information on how to disable a feature on a Provisioned Cluster using a cluster extension, please refer to: https://learn.microsoft.com/en-us/azure/aks/deploy-extensions-az-cli")

    logger.warning("This operation might take a while...\n")

    disable_cluster_connect, disable_azure_rbac, disable_cl = utils.check_features_to_update(features)

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file = utils.get_values_file()

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kubernetes_version = check_kube_connection()

    utils.try_list_node_fix()

    # Install helm client
    helm_client_location = install_helm_client()

    release_namespace = validate_release_namespace(client, cluster_name, resource_group_name, kube_config, kube_context, helm_client_location)

    kubernetes_properties = {'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version}

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
        kubernetes_properties['Context.Default.AzureCLI.KubernetesDistro'] = kubernetes_distro

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
        kubernetes_properties['Context.Default.AzureCLI.KubernetesInfra'] = kubernetes_infra

    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    if disable_cluster_connect:
        try:
            helm_values = get_all_helm_values(release_namespace, kube_config, kube_context, helm_client_location)
            if not disable_cl and helm_values.get('systemDefaultValues').get('customLocations').get('enabled') is True and helm_values.get('systemDefaultValues').get('customLocations').get('oid') != "":
                raise Exception("Disabling 'cluster-connect' feature is not allowed when 'custom-locations' feature is enabled.")
        except AttributeError:
            pass
        except Exception as ex:
            raise ArgumentUsageError(str(ex))

    if disable_cl:
        logger.warning("Disabling 'custom-locations' feature might impact some dependent resources. Learn more about this at https://aka.ms/ArcK8sDependentResources.")

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context, helm_client_location)

    get_chart_and_disable_features(cmd, connected_cluster, kube_config, kube_context,
                                   helm_client_location, release_namespace, values_file, disable_azure_rbac,
                                   disable_cluster_connect, disable_cl)

    return str.format(consts.Successfully_Disabled_Features, features, connected_cluster.name)


def get_chart_and_disable_features(cmd, connected_cluster, kube_config, kube_context,
                                   helm_client_location, release_namespace, values_file, disable_azure_rbac=False,
                                   disable_cluster_connect=False, disable_cl=False):

    config_dp_endpoint, release_train = get_config_dp_endpoint(cmd, connected_cluster.location, values_file)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    check_operation_support("disable-features", agent_version)

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    cmd_helm_upgrade = [helm_client_location, "upgrade", "azure-arc", chart_path, "--namespace", release_namespace,
                        "--reuse-values",
                        "--wait", "--output", "json"]
    if values_file:
        cmd_helm_upgrade.extend(["-f", values_file])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    if disable_azure_rbac:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled=false"])
    if disable_cluster_connect:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.clusterconnect-agent.enabled=false"])
    if disable_cl:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.enabled=false"])
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.oid={}".format("")])

    response_helm_upgrade = Popen(cmd_helm_upgrade, stdout=PIPE, stderr=PIPE)
    _, error_helm_upgrade = response_helm_upgrade.communicate()
    if response_helm_upgrade.returncode != 0:
        helm_upgrade_error_message = error_helm_upgrade.decode("ascii")
        if any(message in helm_upgrade_error_message for message in consts.Helm_Install_Release_Userfault_Messages):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_upgrade.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        raise CLIInternalError(str.format(consts.Error_disabling_Features, error_helm_upgrade.decode("ascii")))


def disable_cluster_connect(cmd, client, resource_group_name, cluster_name, kube_config, kube_context, values_file, release_namespace, helm_client_location):
    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    get_chart_and_disable_features(cmd, connected_cluster, kube_config, kube_context,
                                   helm_client_location, release_namespace, values_file, False,
                                   True, True)


def load_kubernetes_configuration(filename):
    try:
        with open(filename) as stream:
            return yaml.safe_load(stream)
    except (IOError, OSError) as ex:
        if getattr(ex, 'errno', 0) == errno.ENOENT:
            telemetry.set_exception(exception=ex, fault_type=consts.Kubeconfig_Failed_To_Load_Fault_Type,
                                    summary='{} does not exist'.format(filename))
            raise FileOperationError('{} does not exist'.format(filename))
    except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
        telemetry.set_exception(exception=ex, fault_type=consts.Kubeconfig_Failed_To_Load_Fault_Type,
                                summary='Error parsing {} ({})'.format(filename, str(ex)))
        raise FileOperationError('Error parsing {} ({})'.format(filename, str(ex)))


def print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name):
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
                telemetry.set_exception(exception=ex, fault_type=consts.Failed_To_Merge_Credentials_Fault_Type,
                                        summary='Could not create a kubeconfig directory.')
                raise FileOperationError("Could not create a kubeconfig directory." + str(ex))
    if not os.path.exists(path):
        with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt'):
            pass

    # merge the new kubeconfig into the existing one
    fd, temp_path = tempfile.mkstemp()
    additional_file = os.fdopen(fd, 'w+t')
    try:
        additional_file.write(kubeconfig)
        additional_file.flush()
        merge_kubernetes_configurations(path, temp_path, overwrite_existing, context_name)
    except yaml.YAMLError as ex:
        logger.warning('Failed to merge credentials to kube config file: %s', ex)
    finally:
        additional_file.close()
        os.remove(temp_path)


def merge_kubernetes_configurations(existing_file, addition_file, replace, context_name=None):
    try:
        existing = load_kubernetes_configuration(existing_file)
        addition = load_kubernetes_configuration(addition_file)
    except Exception as ex:
        telemetry.set_exception(exception=ex, fault_type=consts.Failed_To_Load_K8s_Configuration_Fault_Type,
                                summary='Exception while loading kubernetes configuration')
        raise CLIInternalError('Exception while loading kubernetes configuration.' + str(ex))

    if context_name is not None:
        addition['contexts'][0]['name'] = context_name
        addition['contexts'][0]['context']['cluster'] = context_name
        addition['clusters'][0]['name'] = context_name
        addition['current-context'] = context_name

    # rename the admin context so it doesn't overwrite the user context
    for ctx in addition.get('contexts', []):
        try:
            if ctx['context']['user'].startswith('clusterAdmin'):
                admin_name = ctx['name'] + '-admin'
                addition['current-context'] = ctx['name'] = admin_name
                break
        except (KeyError, TypeError):
            continue

    if addition is None:
        telemetry.set_exception(exception='Failed to load additional configuration', fault_type=consts.Failed_To_Load_K8s_Configuration_Fault_Type,
                                summary='failed to load additional configuration from {}'.format(addition_file))
        raise CLIInternalError('failed to load additional configuration from {}'.format(addition_file))

    if existing is None:
        existing = addition
    else:
        handle_merge(existing, addition, 'clusters', replace)
        handle_merge(existing, addition, 'users', replace)
        handle_merge(existing, addition, 'contexts', replace)
        existing['current-context'] = addition['current-context']

    # check that ~/.kube/config is only read- and writable by its owner
    if platform.system() != 'Windows':
        existing_file_perms = "{:o}".format(stat.S_IMODE(os.lstat(existing_file).st_mode))
        if not existing_file_perms.endswith('600'):
            logger.warning('%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                           existing_file, existing_file_perms)

    with open(existing_file, 'w+') as stream:
        try:
            yaml.safe_dump(existing, stream, default_flow_style=False)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Failed_To_Merge_Kubeconfig_File,
                                    summary='Exception while merging the kubeconfig file')
            raise CLIInternalError('Exception while merging the kubeconfig file.' + str(e))

    current_context = addition.get('current-context', 'UNKNOWN')
    msg = 'Merged "{}" as current context in {}'.format(current_context, existing_file)
    print(msg)


def handle_merge(existing, addition, key, replace):
    if not addition[key]:
        return
    if existing[key] is None:
        existing[key] = addition[key]
        return

    i = addition[key][0]
    temp_list = []
    for j in existing[key]:
        remove_flag = False
        if not i.get('name', False) or not j.get('name', False):
            continue
        if i['name'] == j['name']:
            if replace or i == j:
                remove_flag = True
            else:
                msg = 'A different object named {} already exists in your kubeconfig file.\nOverwrite?'
                overwrite = False
                try:
                    overwrite = prompt_y_n(msg.format(i['name']))
                except NoTTYException:
                    pass
                if overwrite:
                    remove_flag = True
                else:
                    msg = 'A different object named {} already exists in {} in your kubeconfig file.'
                    telemetry.set_exception(exception='A different object with same name exists in the kubeconfig file', fault_type=consts.Different_Object_With_Same_Name_Fault_Type,
                                            summary=msg.format(i['name'], key))
                    raise FileOperationError(msg.format(i['name'], key))
        if not remove_flag:
            temp_list.append(j)

    existing[key][:] = temp_list
    existing[key].append(i)


def client_side_proxy_wrapper(cmd,
                              client,
                              resource_group_name,
                              cluster_name,
                              token=None,
                              path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                              context_name=None,
                              api_server_port=consts.API_SERVER_PORT):

    cloud = send_cloud_telemetry(cmd)
    profile = Profile()
    tenant_id = profile.get_subscription()['tenantId']

    client_proxy_port = consts.CLIENT_PROXY_PORT

    # Check if the internal port is already open. If so and the user has specified a port,
    # try using the port before the user specified port instead.
    if clientproxyutils.check_if_port_is_open(client_proxy_port) and api_server_port != consts.API_SERVER_PORT:
        client_proxy_port = int(api_server_port) - 1

    if int(client_proxy_port) == int(api_server_port):
        raise ClientRequestError(f'Proxy uses port {client_proxy_port} internally.', recommendation='Please pass some other unused port through --port option.')

    args = []
    operating_system = platform.system()
    proc_name = f'arcProxy{operating_system}'

    telemetry.set_debug_info('CSP Version is ', consts.CLIENT_PROXY_VERSION)
    telemetry.set_debug_info('OS is ', operating_system)

    if (clientproxyutils.check_process(proc_name)) and clientproxyutils.check_if_port_is_open(api_server_port):
        raise ClientRequestError('The proxy port is already in use, potentially by another proxy instance.', recommendation='Please stop the existing proxy instance or pass a different port through --port option.')

    port_error_string = ""
    if clientproxyutils.check_if_port_is_open(api_server_port):
        port_error_string += f'Port {api_server_port} is already in use. Please select a different port with --port option.\n'
    if clientproxyutils.check_if_port_is_open(client_proxy_port):
        telemetry.set_exception(exception='Client proxy port was in use.', fault_type=consts.Client_Proxy_Port_Fault_Type,
                                summary='Client proxy port was in use.')
        port_error_string += f"Port {client_proxy_port} is already in use. This is an internal port that proxy uses. Please ensure that this port is open before running 'az connectedk8s proxy'.\n"
    if port_error_string != "":
        raise ClientRequestError(port_error_string)

    # Set csp url based on cloud
    CSP_Url = consts.CSP_Storage_Url
    if cloud == consts.Azure_ChinaCloudName:
        CSP_Url = consts.CSP_Storage_Url_Mooncake
    elif cloud == consts.Azure_USGovCloudName:
        CSP_Url = consts.CSP_Storage_Url_Fairfax

    # Creating installation location, request uri and older version exe location depending on OS
    if (operating_system == 'Windows'):
        install_location_string = f'.clientproxy\\arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}.exe'
        requestUri = f'{CSP_Url}/{consts.RELEASE_DATE_WINDOWS}/arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}.exe'
        older_version_string = f'.clientproxy\\arcProxy{operating_system}*.exe'
        creds_string = r'.azure\accessTokens.json'

    elif (operating_system == 'Linux' or operating_system == 'Darwin'):
        install_location_string = f'.clientproxy/arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}'
        requestUri = f'{CSP_Url}/{consts.RELEASE_DATE_LINUX}/arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}'
        older_version_string = f'.clientproxy/arcProxy{operating_system}*'
        creds_string = r'.azure/accessTokens.json'

    else:
        telemetry.set_exception(exception='Unsupported OS', fault_type=consts.Unsupported_Fault_Type,
                                summary=f'{operating_system} is not supported yet')
        raise ClientRequestError(f'The {operating_system} platform is not currently supported.')

    install_location = os.path.expanduser(os.path.join('~', install_location_string))
    args.append(install_location)
    install_dir = os.path.dirname(install_location)

    # If version specified by install location doesnt exist, then download the executable
    if not os.path.isfile(install_location):

        print("Setting up environment for first time use. This can take few minutes...")
        # Downloading the executable
        try:
            response = urllib.request.urlopen(requestUri)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Download_Exe_Fault_Type,
                                    summary='Unable to download clientproxy executable.')
            raise CLIInternalError("Failed to download executable with client.", recommendation="Please check your internet connection." + str(e))

        responseContent = response.read()
        response.close()

        # Creating the .clientproxy folder if it doesnt exist
        if not os.path.exists(install_dir):
            try:
                os.makedirs(install_dir)
            except Exception as e:
                telemetry.set_exception(exception=e, fault_type=consts.Create_Directory_Fault_Type,
                                        summary='Unable to create installation directory')
                raise ClientRequestError("Failed to create installation directory." + str(e))
        else:
            older_version_string = os.path.expanduser(os.path.join('~', older_version_string))
            older_version_files = glob(older_version_string)

            # Removing older executables from the directory
            for f in older_version_files:
                try:
                    os.remove(f)
                except:
                    logger.warning("failed to delete older version files")

        try:
            with open(install_location, 'wb') as f:
                f.write(responseContent)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Create_CSPExe_Fault_Type,
                                    summary='Unable to create proxy executable')
            raise ClientRequestError("Failed to create proxy executable." + str(e))

        os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)

    # Creating config file to pass config to clientproxy
    config_file_location = os.path.join(install_dir, 'config.yml')

    if os.path.isfile(config_file_location):
        try:
            os.remove(config_file_location)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Remove_Config_Fault_Type,
                                    summary='Unable to remove old config file')
            raise FileOperationError("Failed to remove old config." + str(e))

    # initializations
    user_type = 'sat'
    creds = ''

    # if service account token is not passed
    if token is None:
        # Identifying type of logged in entity
        subscription_id = get_subscription_id(cmd.cli_ctx)
        account = Profile().get_subscription(subscription_id)
        user_type = account['user']['type']

        if user_type == 'user':
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)}, 'identity': {'tenantID': tenant_id, 'clientID': consts.CLIENTPROXY_CLIENT_ID}}
        else:
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)}, 'identity': {'tenantID': tenant_id, 'clientID': account['user']['name']}}

        if cloud == 'DOGFOOD':
            dict_file['cloud'] = 'AzureDogFood'

        if cloud == consts.Azure_ChinaCloudName:
            dict_file['cloud'] = 'AzureChinaCloud'
        elif cloud == consts.Azure_USGovCloudName:
            dict_file['cloud'] = 'AzureUSGovernmentCloud'

        if not utils.is_cli_using_msal_auth():
            # Fetching creds
            creds_location = os.path.expanduser(os.path.join('~', creds_string))
            try:
                with open(creds_location) as f:
                    creds_list = json.load(f)
            except Exception as e:
                telemetry.set_exception(exception=e, fault_type=consts.Load_Creds_Fault_Type,
                                        summary='Unable to load accessToken.json')
                raise FileOperationError("Failed to load credentials." + str(e))

            user_name = account['user']['name']

            if user_type == 'user':
                key = 'userId'
                key2 = 'refreshToken'
            else:
                key = 'servicePrincipalId'
                key2 = 'accessToken'

            for i in range(len(creds_list)):
                creds_obj = creds_list[i]

                if key in creds_obj and creds_obj[key] == user_name:
                    creds = creds_obj[key2]
                    break

            if creds == '':
                telemetry.set_exception(exception='Credentials of user not found.', fault_type=consts.Creds_NotFound_Fault_Type,
                                        summary='Unable to find creds of user')
                raise UnclassifiedUserFault("Credentials of user not found.")

            if user_type != 'user':
                dict_file['identity']['clientSecret'] = creds
    else:
        dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)}}
        if cloud == consts.Azure_ChinaCloudName:
            dict_file['cloud'] = 'AzureChinaCloud'
        elif cloud == consts.Azure_USGovCloudName:
            dict_file['cloud'] = 'AzureUSGovernmentCloud'

    telemetry.set_debug_info('User type is ', user_type)

    try:
        with open(config_file_location, 'w') as f:
            yaml.dump(dict_file, f, default_flow_style=False)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Create_Config_Fault_Type,
                                summary='Unable to create config file for proxy.')
        raise FileOperationError("Failed to create config for proxy." + str(e))

    args.append("-c")
    args.append(config_file_location)

    debug_mode = False
    if '--debug' in cmd.cli_ctx.data['safe_params']:
        args.append("-d")
        debug_mode = True

    client_side_proxy_main(cmd, tenant_id, client, resource_group_name, cluster_name, 0, args, client_proxy_port, api_server_port, operating_system, creds, user_type, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=None)


# Prepare data as needed by client proxy executable
def prepare_clientproxy_data(response):
    data = {}
    data['kubeconfigs'] = []
    kubeconfig = {}
    kubeconfig['name'] = 'Kubeconfig'
    kubeconfig['value'] = b64encode(response.kubeconfigs[0].value).decode("utf-8")
    data['kubeconfigs'].append(kubeconfig)
    data['hybridConnectionConfig'] = {}
    data['hybridConnectionConfig']['relay'] = response.hybrid_connection_config.relay
    data['hybridConnectionConfig']['hybridConnectionName'] = response.hybrid_connection_config.hybrid_connection_name
    data['hybridConnectionConfig']['token'] = response.hybrid_connection_config.token
    data['hybridConnectionConfig']['expirationTime'] = response.hybrid_connection_config.expiration_time
    return data


def client_side_proxy_main(cmd,
                           tenant_id,
                           client,
                           resource_group_name,
                           cluster_name,
                           flag,
                           args,
                           client_proxy_port,
                           api_server_port,
                           operating_system,
                           creds,
                           user_type,
                           debug_mode,
                           token=None,
                           path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                           context_name=None,
                           clientproxy_process=None):
    expiry, clientproxy_process = client_side_proxy(cmd, tenant_id, client, resource_group_name, cluster_name, 0, args, client_proxy_port, api_server_port, operating_system, creds, user_type, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=None)
    next_refresh_time = expiry - consts.CSP_REFRESH_TIME

    while (True):
        time.sleep(60)
        if (clientproxyutils.check_if_csp_is_running(clientproxy_process)):
            if time.time() >= next_refresh_time:
                expiry, clientproxy_process = client_side_proxy(cmd, tenant_id, client, resource_group_name, cluster_name, 1, args, client_proxy_port, api_server_port, operating_system, creds, user_type, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=clientproxy_process)
                next_refresh_time = expiry - consts.CSP_REFRESH_TIME
        else:
            telemetry.set_exception(exception='Process closed externally.', fault_type=consts.Proxy_Closed_Externally_Fault_Type,
                                    summary='Process closed externally.')
            raise ManualInterrupt('Proxy closed externally.')


def client_side_proxy(cmd,
                      tenant_id,
                      client,
                      resource_group_name,
                      cluster_name,
                      flag,
                      args,
                      client_proxy_port,
                      api_server_port,
                      operating_system,
                      creds,
                      user_type,
                      debug_mode,
                      token=None,
                      path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                      context_name=None,
                      clientproxy_process=None):

    subscription_id = get_subscription_id(cmd.cli_ctx)
    if token is not None:
        auth_method = 'Token'
    else:
        auth_method = 'AAD'

    # Fetching hybrid connection details from Userrp
    try:
        list_prop = ListClusterUserCredentialProperties(
            authentication_method=auth_method,
            client_proxy=True
        )
        response = client.list_cluster_user_credential(resource_group_name, cluster_name, list_prop)
    except Exception as e:
        if flag == 1:
            clientproxy_process.terminate()
        utils.arm_exception_handler(e, consts.Get_Credentials_Failed_Fault_Type, 'Unable to list cluster user credentials')
        raise CLIInternalError("Failed to get credentials." + str(e))

    # Starting the client proxy process, if this is the first time that this function is invoked
    if flag == 0:
        try:
            if debug_mode:
                clientproxy_process = Popen(args)
            else:
                clientproxy_process = Popen(args, stdout=DEVNULL, stderr=DEVNULL)
            print(f'Proxy is listening on port {api_server_port}')

        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Run_Clientproxy_Fault_Type,
                                    summary='Unable to run client proxy executable')
            raise CLIInternalError("Failed to start proxy process." + str(e))

        if not utils.is_cli_using_msal_auth():  # refresh token approach if cli is using ADAL auth. This is for cli < 2.30.0
            if user_type == 'user':
                identity_data = {}
                identity_data['refreshToken'] = creds
                identity_uri = f'https://localhost:{api_server_port}/identity/rt'

                # Needed to prevent skip tls warning from printing to the console
                original_stderr = sys.stderr
                f = open(os.devnull, 'w')
                sys.stderr = f

                clientproxyutils.make_api_call_with_retries(identity_uri, identity_data, "post", False, consts.Post_RefreshToken_Fault_Type,
                                                            'Unable to post refresh token details to clientproxy',
                                                            "Failed to pass refresh token details to proxy.", clientproxy_process)
                sys.stderr = original_stderr

    if token is None:
        if utils.is_cli_using_msal_auth():  # jwt token approach if cli is using MSAL. This is for cli >= 2.30.0
            kid = clientproxyutils.fetch_pop_publickey_kid(api_server_port, clientproxy_process)
            post_at_response = clientproxyutils.fetch_and_post_at_to_csp(cmd, api_server_port, tenant_id, kid, clientproxy_process)

            if post_at_response.status_code != 200:
                if post_at_response.status_code == 500 and "public key expired" in post_at_response.text:  # pop public key must have been rotated
                    telemetry.set_exception(exception=post_at_response.text, fault_type=consts.PoP_Public_Key_Expried_Fault_Type,
                                            summary='PoP public key has expired')
                    kid = clientproxyutils.fetch_pop_publickey_kid(api_server_port, clientproxy_process)  # fetch the rotated PoP public key
                    clientproxyutils.fetch_and_post_at_to_csp(cmd, api_server_port, tenant_id, kid, clientproxy_process)  # fetch and post the at corresponding to the new public key
                else:
                    telemetry.set_exception(exception=post_at_response.text, fault_type=consts.Post_AT_To_ClientProxy_Failed_Fault_Type,
                                            summary='Failed to post access token to client proxy')
                    clientproxyutils.close_subprocess_and_raise_cli_error(clientproxy_process, 'Failed to post access token to client proxy' + post_at_response.text)

    data = prepare_clientproxy_data(response)
    expiry = data['hybridConnectionConfig']['expirationTime']

    if token is not None:
        data['kubeconfigs'][0]['value'] = clientproxyutils.insert_token_in_kubeconfig(data, token)

    uri = f'http://localhost:{client_proxy_port}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Kubernetes/connectedClusters/{cluster_name}/register?api-version=2020-10-01'

    # Posting hybrid connection details to proxy in order to get kubeconfig
    response = clientproxyutils.make_api_call_with_retries(uri, data, "post", False, consts.Post_Hybridconn_Fault_Type,
                                                           'Unable to post hybrid connection details to clientproxy',
                                                           "Failed to pass hybrid connection details to proxy.", clientproxy_process)

    if flag == 0:
        # Decoding kubeconfig into a string
        try:
            kubeconfig = json.loads(response.text)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                    summary='Unable to load Kubeconfig')
            clientproxyutils.close_subprocess_and_raise_cli_error(clientproxy_process, "Failed to load kubeconfig." + str(e))

        kubeconfig = kubeconfig['kubeconfigs'][0]['value']
        kubeconfig = b64decode(kubeconfig).decode("utf-8")

        try:
            print_or_merge_credentials(path, kubeconfig, True, context_name)
            if path != "-":
                if context_name is None:
                    kubeconfig_obj = load_kubernetes_configuration(path)
                    temp_context_name = kubeconfig_obj['current-context']
                else:
                    temp_context_name = context_name
                print("Start sending kubectl requests on '{}' context using kubeconfig at {}".format(temp_context_name, path))

            print("Press Ctrl+C to close proxy.")

        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Merge_Kubeconfig_Fault_Type,
                                    summary='Unable to merge kubeconfig.')
            clientproxyutils.close_subprocess_and_raise_cli_error(clientproxy_process, "Failed to merge kubeconfig." + str(e))

    return expiry, clientproxy_process


def check_cl_registration_and_get_oid(cmd, cl_oid, subscription_id):
    enable_custom_locations = True
    custom_locations_oid = ""
    try:
        rp_client = resource_providers_client(cmd.cli_ctx, subscription_id)
        cl_registration_state = rp_client.get(consts.Custom_Locations_Provider_Namespace).registration_state
        if cl_registration_state != "Registered":
            enable_custom_locations = False
            logger.warning("'Custom-locations' feature couldn't be enabled on this cluster as the pre-requisite registration of 'Microsoft.ExtendedLocation' was not met. More details for enabling this feature later on this cluster can be found here - https://aka.ms/EnableCustomLocations")
        else:
            custom_locations_oid = get_custom_locations_oid(cmd, cl_oid)
            if custom_locations_oid == "":
                enable_custom_locations = False
    except Exception as e:
        enable_custom_locations = False
        logger.warning("Unable to fetch registration state of 'Microsoft.ExtendedLocation'. Failed to enable 'custom-locations' feature. This is fine if not required. Proceeding with helm install.")
        telemetry.set_exception(exception=e, fault_type=consts.Custom_Locations_Registration_Check_Fault_Type,
                                summary='Unable to fetch status of Custom Locations RP registration.')
    return enable_custom_locations, custom_locations_oid


def get_custom_locations_oid(cmd, cl_oid):
    try:
        graph_client = graph_client_factory(cmd.cli_ctx)
        app_id = "bc313c14-388c-4e7d-a58e-70017303ee3b"
        # Requires Application.Read.All for Microsoft Graph since AAD Graph is deprecated. See below for work-around.
        # https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/custom-locations#enable-custom-locations-on-your-cluster
        # Get Application Object for the CL App Id
        app_object = graph_client.service_principal_list(filter="appId eq '{}'".format(app_id))
        # If we successfully obtained it
        if len(app_object) != 0:
            # If a CL OID was input and it did not match the one we fetched, log a warning
            if cl_oid is not None and cl_oid != app_object[0]['id']:
                logger.debug("The 'Custom-locations' OID passed is different from the actual OID({}) of the Custom Locations RP app. Proceeding with the correct one...".format(app_object[0]['id']))
            # We return the fetched CL OID, if we successfully retrieved it - irrespective of CL OID was input or not
            return app_object[0]['id']  # Using the fetched OID

        # If a Cl OID was not input and we failed to fetch the CL App object, log a warning
        if cl_oid is None:
            logger.warning("Failed to enable Custom Locations feature on the cluster. Unable to fetch Object ID of Azure AD application used by Azure Arc service. Try enabling the feature by passing the --custom-locations-oid parameter directly. Learn more at https://aka.ms/CustomLocationsObjectID")
            telemetry.set_exception(exception='Unable to fetch oid of custom locations app.', fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type_CLOid_None,
                                    summary='Unable to fetch oid for custom locations app.')
            # Return empty for OID
            return ""
        else:
            # Return the input OID
            return cl_oid
    except Exception as e:
        # Encountered exeption while fetching OID, log error
        log_string = "Unable to fetch the Object ID of the Azure AD application used by Azure Arc service. "
        telemetry.set_exception(exception=e, fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type_Exception,
                                summary='Unable to fetch oid for custom locations app.')
        # If Cl OID was input, use that
        if cl_oid:
            log_string += "Proceeding with the Object ID provided to enable the 'custom-locations' feature."
            logger.warning(log_string)
            return cl_oid
        # If no Cl OID was input, log a Warning and return empty for OID
        log_string += "Unable to enable the 'custom-locations' feature. " + str(e)
        logger.warning(log_string)
        return ""


def troubleshoot(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None, no_wait=False, tags=None):

    try:

        logger.warning("Diagnoser running. This may take a while ...\n")
        absolute_path = os.path.abspath(os.path.dirname(__file__))

        # Setting the intial values as True
        storage_space_available = True
        probable_sufficient_resource_for_agents = True

        # Setting default values for all checks as True
        diagnostic_checks = {consts.Fetch_Kubectl_Cluster_Info: consts.Diagnostic_Check_Incomplete, consts.Retrieve_Arc_Agents_Event_Logs: consts.Diagnostic_Check_Incomplete, consts.Retrieve_Arc_Agents_Logs: consts.Diagnostic_Check_Incomplete, consts.Retrieve_Deployments_Logs: consts.Diagnostic_Check_Incomplete, consts.Fetch_Connected_Cluster_Resource: consts.Diagnostic_Check_Incomplete, consts.Storing_Diagnoser_Results_Logs: consts.Diagnostic_Check_Incomplete, consts.MSI_Cert_Expiry_Check: consts.Diagnostic_Check_Incomplete, consts.KAP_Security_Policy_Check: consts.Diagnostic_Check_Incomplete, consts.KAP_Cert_Check: consts.Diagnostic_Check_Incomplete, consts.Diagnoser_Check: consts.Diagnostic_Check_Incomplete, consts.MSI_Cert_Check: consts.Diagnostic_Check_Incomplete, consts.Agent_Version_Check: consts.Diagnostic_Check_Incomplete, consts.Arc_Agent_State_Check: consts.Diagnostic_Check_Incomplete}

        # Setting kube_config
        kube_config = set_kube_config(kube_config)
        kube_client.rest.logger.setLevel(logging.WARNING)

        # Loading the kubeconfig file in kubernetes client configuration
        load_kube_config(kube_config, kube_context)

        # Install helm client
        helm_client_location = install_helm_client()

        # Install kubectl client
        kubectl_client_location = install_kubectl_client()
        release_namespace = validate_release_namespace(client, cluster_name, resource_group_name, kube_config, kube_context, helm_client_location)

        # Checking the connection to kubernetes cluster.
        # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
        # if the user had not logged in.
        check_kube_connection()
        utils.try_list_node_fix()

        # Fetch Connected Cluster for agent version
        connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

        # Creating timestamp folder to store all the diagnoser logs
        current_time = time.ctime(time.time())
        time_stamp = ""
        for elements in current_time:
            if (elements == ' '):
                time_stamp += '-'
                continue
            elif (elements == ':'):
                time_stamp += '.'
                continue
            time_stamp += elements
        time_stamp = cluster_name + '-' + time_stamp
        # Generate the diagnostic folder in a given location
        filepath_with_timestamp, diagnostic_folder_status = utils.create_folder_diagnosticlogs(time_stamp, consts.Arc_Diagnostic_Logs)

        if (diagnostic_folder_status is not True):
            storage_space_available = False

        # To store the cluster-info of the cluster in current-context
        diagnostic_checks[consts.Fetch_Kubectl_Cluster_Info], storage_space_available = troubleshootutils.fetch_kubectl_cluster_info(filepath_with_timestamp, storage_space_available, kubectl_client_location, kube_config, kube_context)

        # To store the connected cluster resource logs in the diagnostic folder
        diagnostic_checks[consts.Fetch_Connected_Cluster_Resource], storage_space_available = troubleshootutils.fetch_connected_cluster_resource(filepath_with_timestamp, connected_cluster, storage_space_available)
        corev1_api_instance = kube_client.CoreV1Api()

        # Check if agents have been added to the cluster
        arc_agents_pod_list = corev1_api_instance.list_namespaced_pod(namespace="azure-arc")

        # To verify if arc agents have been added to the cluster
        if arc_agents_pod_list.items:

            # For storing all the agent logs using the CoreV1Api
            diagnostic_checks[consts.Retrieve_Arc_Agents_Logs], storage_space_available = troubleshootutils.retrieve_arc_agents_logs(corev1_api_instance, filepath_with_timestamp, storage_space_available)

            # For storing all arc agents events logs
            diagnostic_checks[consts.Retrieve_Arc_Agents_Event_Logs], storage_space_available = troubleshootutils.retrieve_arc_agents_event_logs(filepath_with_timestamp, storage_space_available, kubectl_client_location, kube_config, kube_context)

            # For storing all the deployments logs using the AppsV1Api
            appv1_api_instance = kube_client.AppsV1Api()
            diagnostic_checks[consts.Retrieve_Deployments_Logs], storage_space_available = troubleshootutils.retrieve_deployments_logs(appv1_api_instance, filepath_with_timestamp, storage_space_available)

            # Check for the azure arc agent states
            diagnostic_checks[consts.Arc_Agent_State_Check], storage_space_available, all_agents_stuck, probable_sufficient_resource_for_agents = troubleshootutils.check_agent_state(corev1_api_instance, filepath_with_timestamp, storage_space_available)

            # Check for msi certificate
            if all_agents_stuck is False:
                diagnostic_checks[consts.MSI_Cert_Check] = troubleshootutils.check_msi_certificate_presence(corev1_api_instance)

            # If msi certificate present then only we will perform msi certificate expiry check
            if diagnostic_checks[consts.MSI_Cert_Check] == consts.Diagnostic_Check_Passed:
                diagnostic_checks[consts.MSI_Cert_Expiry_Check] = troubleshootutils.check_msi_expiry(connected_cluster)

            # If msi certificate present then only we will do Kube aad proxy checks
            if diagnostic_checks[consts.MSI_Cert_Check] == consts.Diagnostic_Check_Passed:
                diagnostic_checks[consts.KAP_Security_Policy_Check] = troubleshootutils.check_probable_cluster_security_policy(corev1_api_instance, helm_client_location, release_namespace, kube_config, kube_context)

                # If no security policy is present in cluster then we can check for the Kube aad proxy certificate
                if diagnostic_checks[consts.KAP_Security_Policy_Check] == consts.Diagnostic_Check_Passed:
                    diagnostic_checks[consts.KAP_Cert_Check] = troubleshootutils.check_kap_cert(corev1_api_instance)

            # Checking whether optional extra values file has been provided.
            values_file = utils.get_values_file()

            # Adding helm repo
            if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
                utils.add_helm_repo(kube_config, kube_context, helm_client_location)

            config_dp_endpoint, release_train = get_config_dp_endpoint(cmd, connected_cluster.location, values_file)

            # Retrieving Helm chart OCI Artifact location
            registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, release_train)

            # Get azure-arc agent version for telemetry
            azure_arc_agent_version = registry_path.split(':')[1]

            # Check for agent version compatibility
            diagnostic_checks[consts.Agent_Version_Check] = troubleshootutils.check_agent_version(connected_cluster, azure_arc_agent_version)
        else:
            logger.warning("Error: Azure Arc agents are not present on the cluster. Please verify whether Arc onboarding of the Kubernetes cluster has been attempted.\n")

        batchv1_api_instance = kube_client.BatchV1Api()
        # Performing diagnoser container check
        diagnostic_checks[consts.Diagnoser_Check], storage_space_available = troubleshootutils.check_diagnoser_container(corev1_api_instance, batchv1_api_instance, filepath_with_timestamp, storage_space_available, absolute_path, probable_sufficient_resource_for_agents, helm_client_location, kubectl_client_location, release_namespace, diagnostic_checks[consts.KAP_Security_Policy_Check], kube_config, kube_context)

        # saving secrets in azure-arc namespace
        storage_space_available = troubleshootutils.get_secrets_azure_arc(corev1_api_instance, kubectl_client_location, kube_config, kube_context, filepath_with_timestamp, storage_space_available)

        # saving helm values of azure-arc release
        storage_space_available = troubleshootutils.get_helm_values_azure_arc(corev1_api_instance, helm_client_location, release_namespace, kube_config, kube_context, filepath_with_timestamp, storage_space_available)

        # saving metadata CR sanpshot
        storage_space_available = troubleshootutils.get_metadata_cr_snapshot(corev1_api_instance, kubectl_client_location, kube_config, kube_context, filepath_with_timestamp, storage_space_available)

        # saving kube-aad-proxy CR snapshot only in the case private link is disabled
        if connected_cluster.private_link_state == "Disabled":
            storage_space_available = troubleshootutils.get_kubeaadproxy_cr_snapshot(corev1_api_instance, kubectl_client_location, kube_config, kube_context, filepath_with_timestamp, storage_space_available)

        # checking cluster connectivity status
        cluster_connectivity_status = connected_cluster.connectivity_status

        if cluster_connectivity_status != "Connected":
            logger.warning("Cluster connectivity status is not connected. The current state of the cluster is : " + cluster_connectivity_status)

        # Adding cli output to the logs
        diagnostic_checks[consts.Storing_Diagnoser_Results_Logs] = troubleshootutils.fetching_cli_output_logs(filepath_with_timestamp, storage_space_available, 1)

        # If all the checks passed then display no error found
        all_checks_passed = True
        for checks in diagnostic_checks:
            if diagnostic_checks[checks] != consts.Diagnostic_Check_Passed:
                all_checks_passed = False
        if storage_space_available:
            # Depending on whether all tests passes we will give the output
            if (all_checks_passed):
                logger.warning("The diagnoser didn't find any issues on the cluster.\nThe diagnoser logs have been saved at this path:" + filepath_with_timestamp + " .\nThese logs can be attached while filing a support ticket for further assistance.\n")
            else:
                logger.warning("The diagnoser logs have been saved at this path:" + filepath_with_timestamp + " .\nThese logs can be attached while filing a support ticket for further assistance.\n")
        else:
            if (all_checks_passed):
                logger.warning("The diagnoser didn't find any issues on the cluster.\n")
            logger.warning("The diagnoser was unable to save logs to your machine. Please check whether sufficient storage is available and run the troubleshoot command again.")

    # Handling the user manual interrupt
    except KeyboardInterrupt:
        try:
            troubleshootutils.fetching_cli_output_logs(filepath_with_timestamp, storage_space_available, 0)
        except Exception:
            pass
        raise ManualInterrupt('Process terminated externally.')


def install_kubectl_client():
    # Return kubectl client path set by user
    try:

        # Fetching the current directory where the cli installs the kubectl executable
        home_dir = os.path.expanduser('~')
        kubectl_filepath = os.path.join(home_dir, '.azure', 'kubectl-client')

        try:
            os.makedirs(kubectl_filepath)
        except FileExistsError:
            pass

        operating_system = platform.system().lower()
        # Setting path depending on the OS being used
        if operating_system == 'windows':
            kubectl_path = os.path.join(kubectl_filepath, 'kubectl.exe')
        elif operating_system == 'linux' or operating_system == 'darwin':
            kubectl_path = os.path.join(kubectl_filepath, 'kubectl')

        if os.path.isfile(kubectl_path):
            return kubectl_path

        # Downloading kubectl executable if its not present in the machine
        logger.warning("Downloading kubectl client for first time. This can take few minutes...")
        logging.disable(logging.CRITICAL)
        get_default_cli().invoke(['aks', 'install-cli', '--install-location', kubectl_path])
        logging.disable(logging.NOTSET)
        logger.warning("\n")
        # Return the path of the kubectl executable
        return kubectl_path

    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Download_And_Install_Kubectl_Fault_Type, summary="Failed to download and install kubectl")
        raise CLIInternalError("Unable to install kubectl. Error: ", str(e))


def crd_cleanup_force_delete(kubectl_client_location, kube_config, kube_context):
    timeout_for_crd_deletion = "20s"
    for crds in consts.CRD_FOR_FORCE_DELETE:
        cmd_helm_delete = [kubectl_client_location, "delete", "crds", crds, "--ignore-not-found", "--wait", "--timeout", "{}".format(timeout_for_crd_deletion)]
        if kube_config:
            cmd_helm_delete.extend(["--kubeconfig", kube_config])
        if kube_context:
            cmd_helm_delete.extend(["--context", kube_context])
        response_helm_delete = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = response_helm_delete.communicate()

    # Timer added to have sufficient time after CRD deletion
    # to check the status of the CRD ( deleted or terminating )
    time.sleep(3)

    # patching yaml file path for removing CRD finalizer
    current_path = os.path.abspath(os.path.dirname(__file__))
    yaml_file_path = os.path.join(current_path, "remove_crd_finalizer.yaml")

    # Patch if CRD is in Terminating state
    for crds in consts.CRD_FOR_FORCE_DELETE:

        cmd = [kubectl_client_location, "get", "crd", crds, "-ojson"]
        if kube_config:
            cmd.extend(["--kubeconfig", kube_config])
        if kube_context:
            cmd.extend(["--context", kube_context])
        cmd_output = Popen(cmd, stdout=PIPE, stderr=PIPE)
        _, error_helm_delete = cmd_output.communicate()

        if (cmd_output.returncode == 0):
            changed_cmd = json.loads(cmd_output.communicate()[0].strip())
            status = changed_cmd['status']['conditions'][-1]['type']

            if (status == "Terminating"):
                patch_cmd = [kubectl_client_location, "patch", "crd", crds, "--type=merge", "--patch-file", yaml_file_path]
                if kube_config:
                    patch_cmd.extend(["--kubeconfig", kube_config])
                if kube_context:
                    patch_cmd.extend(["--context", kube_context])
                output_patch_cmd = Popen(patch_cmd, stdout=PIPE, stderr=PIPE)
                _, error_helm_delete = output_patch_cmd.communicate()


def check_operation_support(operation_name, agent_version):
    error_summary = 'This CLI version does not support {} for Agents older than v1.14'.format(operation_name)
    # Version check for stable release train (agent_version will be in X.Y.Z format as opposed to X.Y.Z-NONSTABLE)
    if '-' not in agent_version and (version.parse(agent_version) < version.parse("1.14.0")):
        telemetry.set_exception(exception='Operation not supported on older Agents', fault_type=consts.Operation_Not_Supported_Fault_Type, summary=error_summary)
        raise ClientRequestError(error_summary, recommendation="Please upgrade to the latest version of the Agents using 'az connectedk8s upgrade -g <rg_name> -n <cluster_name>'.")
