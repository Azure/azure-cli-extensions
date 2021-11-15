# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import stat
import platform
import urllib.request
import shutil

import yaml
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core._profile import Profile
from azure.cli.core import telemetry
from azure.cli.core.azclierror import UnclassifiedUserFault, CLIInternalError, FileOperationError, ClientRequestError
from azure.cli.core.azclierror import ValidationError, ArgumentUsageError, MutuallyExclusiveArgumentError
from azure.cli.core.azclierror import RequiredArgumentMissingError
from kubernetes import client as kube_client, config
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._arc_agent_utils import ArcAgentUtils
from azext_connectedk8s._helm_core_utils import HelmCoreUtils
import azext_connectedk8s._constants as consts
import azext_connectedk8s._custom_location_utils as cl_utils
import azext_connectedk8s._connected_cluster_utils as cc_utils
import azext_connectedk8s._helm_utils as helm_utils
import azext_connectedk8s._kube_core_utils as kube_core_utils
import azext_connectedk8s._kube_utils as kube_utils
import azext_connectedk8s._proxy_utils as proxy_utils
import azext_connectedk8s._utils as utils
from glob import glob
import hashlib
logger = get_logger(__name__)


def create_connectedk8s(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="",
                        proxy_cert="", location=None, kube_config=None, kube_context=None, no_wait=False, tags=None,
                        distribution='auto', infrastructure='auto', disable_auto_upgrade=False, cl_oid=None,
                        onboarding_timeout="300"):
    utils.initial_log_warning()

    # Setting subscription id
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Send cloud information to telemetry
    azure_cloud = utils.send_cloud_telemetry(cmd)

    # Fetching Tenant Id
    graph_client = _graph_client_factory(cmd.cli_ctx)
    onboarding_tenant_id = graph_client.config.tenant_id

    # Get resource provider client
    resource_client = cc_utils.get_resource_client(cmd)
    # Checking provider registration status
    cc_utils.check_provider_registrations(resource_client)

    # Setting kubeconfig
    kube_config = kube_utils.set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    cloud_name, dp_endpoint_dogfood, release_train_dogfood = \
        helm_utils.validate_helm_environment_file(cmd, values_file, values_file_provided)

    if cloud_name:
        azure_cloud = cloud_name

    # Loading the kubeconfig file in kubernetes client configuration
    kube_utils.load_kube_config(config, kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kube_core_utils.check_kube_connection(configuration)

    kube_core_utils.try_list_node_fix()
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    node_api_response = kube_utils.validate_node_api_response(api_instance, None)
    required_node_exists = kube_core_utils.check_linux_amd64_node(node_api_response)

    if not required_node_exists:
        telemetry.set_user_fault()
        telemetry.set_exception(exception="Couldn't find any node on the kubernetes cluster with the architecture"
                                " type 'amd64' and OS 'linux'", fault_type=consts.Linux_Amd64_Node_Not_Exists,
                                summary="Couldn't find any node on the kubernetes cluster with the architecture"
                                " type 'amd64' and OS 'linux'")
        logger.warning("Please ensure that this Kubernetes cluster have any nodes with OS 'linux' and architecture"
                       " 'amd64', for scheduling the Arc-Agents onto and connecting to Azure. Learn more at {}"
                       .format("https://aka.ms/ArcK8sSupportedOSArchitecture"))

    crb_permission = kube_core_utils.can_create_clusterrolebindings(configuration)
    if not crb_permission:
        telemetry.set_exception(exception="Your credentials doesn't have permission to create clusterrolebindings"
                                " on this kubernetes cluster.",
                                fault_type=consts.Cannot_Create_ClusterRoleBindings_Fault_Type,
                                summary="Your credentials doesn't have permission to create clusterrolebindings"
                                " on this kubernetes cluster.")
        raise ValidationError("Your credentials doesn't have permission to create clusterrolebindings on this"
                              " kubernetes cluster. Please check your permissions.")

    # Get kubernetes cluster info
    kubernetes_version = kube_core_utils.get_server_version(configuration)
    if distribution == 'auto':
        kubernetes_distro = kube_core_utils.get_kubernetes_distro(node_api_response)  # (cluster heuristics)
    else:
        kubernetes_distro = distribution
    if infrastructure == 'auto':
        kubernetes_infra = kube_core_utils.get_kubernetes_infra(node_api_response)  # (cluster heuristics)
    else:
        kubernetes_infra = infrastructure
    kube_utils.add_kubernetes_telemetry_extension_event_raw(kubernetes_version, kubernetes_distro, kubernetes_infra)

    # Checking if it is an AKS cluster
    is_aks_cluster = kube_utils.check_aks_cluster(config, kube_config, kube_context)
    if is_aks_cluster:
        logger.warning("Connecting an Azure Kubernetes Service (AKS) cluster to Azure Arc is only required for"
                       " running Arc enabled services like App Services and Data Services on the cluster. Other"
                       " features like Azure Monitor and Azure Defender are natively available on AKS. Learn"
                       " more at {}.".format(" https://go.microsoft.com/fwlink/?linkid=2144200"))

    # Install helm client
    helm_client_location = helm_utils.install_helm_client()

    # Validate location
    cc_utils.validate_location(location, resource_client)

    # Creating ArcAgentUtilObject with kube configuration
    arc_agent_utils = ArcAgentUtils(kube_config, kube_context)

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    # Check Release Existance
    release_namespace = helm_core_utils.get_release_namespace(helm_client_location)

    if release_namespace:
        # Loading config map
        configmap = kube_core_utils.load_config_map(configuration)
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if cc_utils.connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                # Re-put connected cluster
                try:
                    public_key = client.get(configmap_rg_name,
                                            configmap_cluster_name).agent_public_key_certificate
                except Exception as e:  # pylint: disable=broad-except
                    cc_utils.arm_exception_handler(e, consts.Get_ConnectedCluster_Fault_Type,
                                                   'Failed to check if connected cluster resource already exists.')
                cc = utils.generate_request_payload(location, public_key, tags, kubernetes_distro, kubernetes_infra)
                cc_utils.create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)
            else:
                telemetry.set_exception(exception='The kubernetes cluster is already onboarded',
                                        fault_type=consts.Cluster_Already_Onboarded_Fault_Type,
                                        summary='Kubernetes cluster already onboarded')
                raise ArgumentUsageError("The kubernetes cluster you are trying to onboard is already onboarded to"
                                         " the resource group '{}' with resource name '{}'."
                                         .format(configmap_rg_name, configmap_cluster_name))
        else:
            # Cleanup agents and continue with put
            arc_agent_utils.execute_delete_arc_agents(release_namespace, configuration, helm_client_location)

    else:
        if cc_utils.connected_cluster_exists(client, resource_group_name, cluster_name):
            telemetry.set_exception(exception='The connected cluster resource already exists',
                                    fault_type=consts.Resource_Already_Exists_Fault_Type,
                                    summary='Connected cluster resource already exists')
            raise ArgumentUsageError("The connected cluster resource {} already exists ".format(cluster_name) +
                                     "in the resource group {} ".format(resource_group_name) +
                                     "and corresponds to a different Kubernetes cluster.",
                                     recommendation="To onboard this Kubernetes cluster " +
                                     "to Azure, specify different resource name or resource group name.")

    try:
        k8s_contexts = config.list_kube_config_contexts()  # returns tuple of (all_contexts, current_context)
        if kube_context:  # if custom kube-context is specified
            if k8s_contexts[1].get('name') == kube_context:
                current_k8s_context = k8s_contexts[1]
            else:
                for context in k8s_contexts[0]:
                    if context.get('name') == kube_context:
                        current_k8s_context = context
                        break
        else:
            current_k8s_context = k8s_contexts[1]

        # Take "default" namespace, if not specified in the kube-config
        current_k8s_namespace = current_k8s_context.get('context').get('namespace', "default")
        namespace_exists = False
        k8s_v1 = kube_client.CoreV1Api()
        k8s_ns = k8s_v1.list_namespace()
        for ns in k8s_ns.items:
            if ns.metadata.name == current_k8s_namespace:
                namespace_exists = True
                break
        if namespace_exists is False:
            telemetry.set_exception(exception="Namespace doesn't exist",
                                    fault_type=consts.Default_Namespace_Does_Not_Exist_Fault_Type,
                                    summary="The default namespace defined in the kubeconfig doesn't exist "
                                    " on the kubernetes cluster.")
            raise ValidationError("The default namespace '{}' defined in the kubeconfig doesn't exist"
                                  " on the kubernetes cluster.".format(current_k8s_namespace))
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.warning("Failed to validate if the active namespace exists on the kubernetes cluster. Exception: {}"
                       .format(str(e)))

    # Resource group Creation
    if cc_utils.resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id) is False:
        from azure.cli.core.profiles import ResourceType
        ResourceGroup = cmd.get_models('ResourceGroup', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
        parameters = ResourceGroup(location=location)
        try:
            resource_client.resource_groups.create_or_update(resource_group_name, parameters)
        except Exception as e:  # pylint: disable=broad-except
            cc_utils.arm_exception_handler(e, consts.Create_ResourceGroup_Fault_Type,
                                           'Failed to create the resource group')

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        helm_core_utils.add_helm_repo(os.getenv('HELMREPONAME'), os.getenv('HELMREPOURL'), helm_client_location)

    # Setting the config dataplane endpoint
    config_dp_endpoint = helm_utils.get_config_dp_endpoint(cmd, location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') \
        else helm_utils.get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood, release_train_dogfood)

    # Get azure-arc agent version for telemetry
    azure_arc_agent_version = registry_path.split(':')[1]
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': azure_arc_agent_version})

    # Get helm chart path
    chart_path = helm_utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    public_key, private_key_pem = utils.generate_public_private_key()

    # Generate request payload
    cc = utils.generate_request_payload(location, public_key, tags, kubernetes_distro, kubernetes_infra)

    # Create connected cluster resource
    put_cc_response = cc_utils.create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)

    # Checking if custom locations rp is registered and fetching oid if it is registered
    enable_custom_locations, custom_locations_oid = cl_utils.check_cl_registration_and_get_oid(cmd, cl_oid)

    # Set proxy details
    proxy_details = proxy_utils.create_proxy_details(https_proxy, http_proxy, no_proxy, proxy_cert)
    arc_agent_utils.set_proxy_configuration(proxy_details)

    # Set values file
    arc_agent_utils.set_values_file(values_file)

    # Set autoupgrade
    auto_upgrade = not disable_auto_upgrade  # If disable_auto_upgrade is False auto_upgrade is True
    arc_agent_utils.set_auto_upgrade(auto_upgrade)

    # Install azure-arc agents
    arc_agent_utils.execute_arc_agent_install(chart_path, subscription_id, kubernetes_distro, kubernetes_infra,
                                              resource_group_name, cluster_name, location, onboarding_tenant_id,
                                              private_key_pem, no_wait, azure_cloud, enable_custom_locations,
                                              custom_locations_oid, helm_client_location, onboarding_timeout)
    return put_cc_response


def delete_connectedk8s(cmd, client, resource_group_name, cluster_name,
                        kube_config=None, kube_context=None, no_wait=False):
    utils.initial_log_warning()

    # Send cloud information to telemetry
    utils.send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = kube_utils.set_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    kube_utils.load_kube_config(config, kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled
    # AKS clusters if the user had not logged in.
    kube_core_utils.check_kube_connection(configuration)

    # Install helm client
    helm_client_location = helm_utils.install_helm_client()

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    # Check Release Existance
    release_namespace = helm_core_utils.get_release_namespace(helm_client_location)

    if not release_namespace:
        cc_utils.delete_cc_resource(client, resource_group_name, cluster_name, no_wait)
        return

    # Loading config map
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
    except Exception as e:  # pylint: disable=broad-except
        kube_core_utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                                error_message="Unable to read ConfigMap 'azure-clusterconfig' in"
                                                " 'azure-arc' namespace: ", message_for_not_found="The helm release"
                                                " 'azure-arc' is present but the azure-arc namespace/configmap is"
                                                " missing. Please run 'helm delete azure-arc --no-hooks' to cleanup"
                                                " the release before onboarding the cluster again.")

    subscription_id = get_subscription_id(cmd.cli_ctx)

    if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and
            configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower() and
            configmap.data["AZURE_SUBSCRIPTION_ID"].lower() == subscription_id.lower()):

        armid = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Kubernetes/connectedClusters/{}" \
            .format(subscription_id, resource_group_name, cluster_name)
        arm_hash = hashlib.sha256(armid.lower().encode('utf-8')).hexdigest()

        if kube_utils.check_proxy_kubeconfig(config, kube_config, kube_context, arm_hash):
            telemetry.set_exception(exception='Encountered proxy kubeconfig during deletion.',
                                    fault_type=consts.Proxy_Kubeconfig_During_Deletion_Fault_Type,
                                    summary='The resource cannot be deleted as user is using proxy kubeconfig.')
            raise ClientRequestError("az connectedk8s delete is not supported when using the Cluster Connect"
                                     " kubeconfig.", recommendation="Run the az connectedk8s delete command with"
                                     " your kubeconfig file pointing to the actual Kubernetes cluster to ensure "
                                     "that the agents are cleaned up successfully as part of the delete command.")

        cc_utils.delete_cc_resource(client, resource_group_name, cluster_name, no_wait)
    else:
        telemetry.set_exception(exception='Unable to delete connected cluster',
                                fault_type=consts.Bad_DeleteRequest_Fault_Type,
                                summary='The resource cannot be deleted as kubernetes cluster is onboarded with" \
                                " some other resource id')
        raise ArgumentUsageError("The current context in the kubeconfig file does not correspond " +
                                 "to the connected cluster resource specified. Agents installed on this cluster"
                                 " correspond to the resource group name '{}' "
                                 .format(configmap.data["AZURE_RESOURCE_GROUP"]) +
                                 "and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_NAME"]))

    arc_agent_utils = ArcAgentUtils(kube_config, kube_context)
    # Deleting the azure-arc agents
    arc_agent_utils.execute_delete_arc_agents(release_namespace, configuration, helm_client_location)


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


def update_agents(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="",
                  proxy_cert="", disable_proxy=False, kube_config=None, kube_context=None, auto_upgrade=None):
    utils.initial_log_warning()

    # Send cloud information to telemetry
    utils.send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = kube_utils.set_kube_config(kube_config)

    proxy_details = proxy_utils.create_proxy_details(https_proxy, http_proxy, no_proxy, proxy_cert, disable_proxy)

    if (proxy_details and proxy_details.get('https_proxy') == "" and proxy_details.get('http_proxy') == "" and
            proxy_details.get('no_proxy') == "" and proxy_details.get('proxy_cert') == "" and not
            proxy_details.get('disable_proxy') and not auto_upgrade):
        raise RequiredArgumentMissingError(consts.No_Param_Error)

    if ((proxy_details.get('https_proxy') or proxy_details.get('http_proxy') or proxy_details.get('no_proxy') or
         proxy_details.get('proxy_cert')) and proxy_details.get('disable_proxy')):
        raise MutuallyExclusiveArgumentError(consts.EnableProxy_Conflict_Error)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    _, dp_endpoint_dogfood, release_train_dogfood = \
        helm_utils.validate_helm_environment_file(cmd, values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    kube_utils.load_kube_config(config, kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kube_core_utils.check_kube_connection(configuration)

    kube_core_utils.try_list_node_fix()

    # Install helm client
    helm_client_location = helm_utils.install_helm_client()

    release_namespace = kube_core_utils.validate_release_namespace(client, cluster_name, resource_group_name,
                                                                   configuration, kube_config, kube_context, 
                                                                   helm_client_location)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))

    kube_utils.add_kubernetes_telemetry_extension_event(connected_cluster, configuration, api_instance)
    
    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    registry_path = helm_utils.get_helm_registry_path(cmd, connected_cluster.location, helm_core_utils,
                                                      connected_cluster.agent_version, dp_endpoint_dogfood,
                                                      release_train_dogfood, helm_client_location)

    # Get Helm chart path
    chart_path = helm_utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    arc_agent_utils = ArcAgentUtils(kube_config, kube_context, values_file, proxy_details, auto_upgrade)

    arc_agent_utils.execute_arc_agent_update(chart_path, release_namespace, helm_client_location)

    return str.format(consts.Update_Agent_Success, cluster_name)


def upgrade_agents(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None,
                   arc_agent_version=None, upgrade_timeout="300"):
    utils.initial_log_warning()

    # Send cloud information to telemetry
    utils.send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = kube_utils.set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    _, dp_endpoint_dogfood, release_train_dogfood = \
        helm_utils.validate_helm_environment_file(cmd, values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    kube_utils.load_kube_config(config, kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kube_core_utils.check_kube_connection(configuration)

    kube_core_utils.try_list_node_fix()
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)

    # Install helm client
    helm_client_location = helm_utils.install_helm_client()
    # Check Release Existance
    release_namespace = helm_core_utils.get_release_namespace(helm_client_location)

    if release_namespace:
        # Loading config map
        configmap = kube_core_utils.load_config_map(configuration)
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if cc_utils.connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if not (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                telemetry.set_exception(exception='The provided cluster name and rg correspond to different cluster',
                                        fault_type=consts.Upgrade_RG_Cluster_Name_Conflict,
                                        summary='The provided cluster name and resource group name do not correspond'
                                        ' to the kubernetes cluster being upgraded.')
                raise ArgumentUsageError("The provided cluster name and resource group name do not correspond to the"
                                         " kubernetes cluster you are trying to upgrade.",
                                         recommendation="Please upgrade the cluster, with correct resource group and"
                                         " cluster name, using 'az upgrade agents -g <rg_name> -n <cluster_name>'.")
        else:
            telemetry.set_exception(exception='The corresponding CC resource does not exist',
                                    fault_type=consts.Corresponding_CC_Resource_Deleted_Fault,
                                    summary='CC resource corresponding to this cluster has been deleted by'
                                    ' the customer')
            raise ArgumentUsageError("There exist no ConnectedCluster resource corresponding to this "
                                     "kubernetes Cluster.", recommendation="Please cleanup the helm release"
                                     " first using 'az connectedk8s delete -n <connected-cluster-name> -g"
                                     " <resource-group-name>' and re-onboard the cluster using "
                                     "'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>'")

        auto_update_enabled = configmap.data["AZURE_ARC_AUTOUPDATE"]
        if auto_update_enabled == "true":
            telemetry.set_exception(exception='connectedk8s upgrade called when auto-update is set to true',
                                    fault_type=consts.Manual_Upgrade_Called_In_Auto_Update_Enabled,
                                    summary='az connectedk8s upgrade to manually upgrade agents and extensions is'
                                    ' only supported when auto-upgrade is set to false.')
            raise ClientRequestError("az connectedk8s upgrade to manually upgrade agents and extensions is only"
                                     " supported when auto-upgrade is set to false.",
                                     recommendation="Please run 'az connectedk8s update -n <connected-cluster-name>"
                                     " -g <resource-group-name> --auto-upgrade false' before performing manual upgrade")

    else:
        telemetry.set_exception(exception="The azure-arc release namespace couldn't be retrieved",
                                fault_type=consts.Release_Namespace_Not_Found,
                                summary="The azure-arc release namespace couldn't be retrieved, which implies that"
                                " the kubernetes cluster has not been onboarded to azure-arc.")
        raise ClientRequestError("The azure-arc release namespace couldn't be retrieved, which implies that the"
                                 " kubernetes cluster has not been onboarded to azure-arc.",
                                 recommendation="Please run 'az connectedk8s connect -n <connected-cluster-name> "
                                 "-g <resource-group-name>' to onboard the cluster")

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    kube_utils.add_kubernetes_telemetry_extension_event(connected_cluster, configuration, api_instance)
    registry_path = helm_utils.get_helm_registry_path(cmd, connected_cluster.location, helm_core_utils,
                                                      arc_agent_version, dp_endpoint_dogfood, release_train_dogfood,
                                                      helm_client_location)

    # Get Helm chart path
    chart_path = helm_utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    existing_user_values = helm_core_utils.get_all_helm_values(release_namespace, helm_client_location)

    # Change --timeout format for helm client to understand
    upgrade_timeout = upgrade_timeout + "s"

    arc_agent_utils = ArcAgentUtils(kube_config, kube_context, values_file)

    arc_agent_utils.execute_arc_agent_upgrade(chart_path, release_namespace, upgrade_timeout, existing_user_values, helm_client_location)
    return str.format(consts.Upgrade_Agent_Success, connected_cluster.name)


def enable_features(cmd, client, resource_group_name, cluster_name, features, kube_config=None, kube_context=None,
                    azrbac_client_id=None, azrbac_client_secret=None, azrbac_skip_authz_check=None, cl_oid=None):
    utils.initial_log_warning()

    features = [x.lower() for x in features]
    enable_cluster_connect, enable_azure_rbac, enable_cl = utils.check_features_to_update(features)

    if enable_azure_rbac:
        if (azrbac_client_id is None) or (azrbac_client_secret is None):
            telemetry.set_exception(exception='Application ID or secret is not provided for Azure RBAC',
                                    fault_type=consts.Application_Details_Not_Provided_For_Azure_RBAC_Fault,
                                    summary='Application id, application secret is required to enable/update'
                                    ' Azure RBAC feature')
            raise RequiredArgumentMissingError("Please provide Application id, application secret to enable/update"
                                               " Azure RBAC feature")
        if azrbac_skip_authz_check is None:
            azrbac_skip_authz_check = ""
        azrbac_skip_authz_check = proxy_utils.escape_proxy_settings(azrbac_skip_authz_check)

    enable_cl = None
    custom_locations_oid = None
    if enable_cl:
        enable_cl, custom_locations_oid = cl_utils.check_cl_registration_and_get_oid(cmd, cl_oid)
        if not enable_cluster_connect and enable_cl:
            enable_cluster_connect = True
            logger.warning("Enabling 'custom-locations' feature will enable 'cluster-connect' feature too.")
        if not enable_cl:
            features.remove("custom-locations")
            if len(features) == 0:
                raise ClientRequestError("Failed to enable 'custom-locations' feature.")

    # Send cloud information to telemetry
    utils.send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = kube_utils.set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    _, dp_endpoint_dogfood, release_train_dogfood = \
        helm_utils.validate_helm_environment_file(cmd, values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    kube_utils.load_kube_config(config, kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kube_core_utils.check_kube_connection(configuration)

    kube_core_utils.try_list_node_fix()
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    # Install helm client
    helm_client_location = helm_utils.install_helm_client()
    release_namespace = kube_core_utils.validate_release_namespace(client, cluster_name, resource_group_name,
                                                                   configuration, kube_config, kube_context,
                                                                   helm_client_location)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    kube_utils.add_kubernetes_telemetry_extension_event(connected_cluster, configuration, api_instance)

    registry_path = helm_utils.get_helm_registry_path(cmd, connected_cluster.location, helm_core_utils,
                                                      connected_cluster.agent_version, dp_endpoint_dogfood,
                                                      release_train_dogfood, helm_client_location)

    # Get Helm chart path
    chart_path = helm_utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)

    arc_agent_utils = ArcAgentUtils(kube_config, kube_context, values_file)

    arc_agent_utils.execute_arc_agent_enable_features(chart_path, release_namespace, enable_azure_rbac,
                                                      enable_cluster_connect, enable_cl, custom_locations_oid,
                                                      helm_client_location, azrbac_client_id, azrbac_client_secret,
                                                      azrbac_skip_authz_check)
                                                      
    return str.format(consts.Successfully_Enabled_Features, features, connected_cluster.name)


def disable_features(cmd, client, resource_group_name, cluster_name, features, kube_config=None, kube_context=None,
                     yes=False):
    features = [x.lower() for x in features]
    confirmation_message = "Disabling few of the features may adversely impact dependent resources. Learn more about" \
        " this at https://aka.ms/ArcK8sDependentResources. \n Are you sure you want to disable these features: {}" \
        .format(features)
    utils.user_confirmation(confirmation_message, yes)

    utils.initial_log_warning()

    disable_cluster_connect, disable_azure_rbac, disable_cl = utils.check_features_to_update(features)

    # Send cloud information to telemetry
    utils.send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = kube_utils.set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    _, dp_endpoint_dogfood, release_train_dogfood = \
        helm_utils.validate_helm_environment_file(cmd, values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    kube_utils.load_kube_config(config, kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    kube_core_utils.check_kube_connection(configuration)
    kube_core_utils.try_list_node_fix()
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    # Install helm client
    helm_client_location = helm_utils.install_helm_client()
    release_namespace = kube_core_utils.validate_release_namespace(client, cluster_name, resource_group_name,
                                                                   configuration, kube_config, kube_context, 
                                                                   helm_client_location)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    kube_utils.add_kubernetes_telemetry_extension_event(connected_cluster, configuration, api_instance)

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    if disable_cluster_connect:
        try:
            helm_values = helm_core_utils.get_all_helm_values(release_namespace, helm_client_location)
            if not disable_cl and \
            helm_values.get('systemDefaultValues').get('customLocations').get('enabled') is True and \
            helm_values.get('systemDefaultValues').get('customLocations').get('oid') != "":
                raise Exception("Disabling 'cluster-connect' feature is not allowed when 'custom-locations' feature "
                                "is enabled.")

        except AttributeError as e:
            pass
        except Exception as ex:
            raise ArgumentUsageError(str(ex))

    if disable_cl:
        logger.warning("Disabling 'custom-locations' feature might impact some dependent resources. Learn more about"
                       " this at https://aka.ms/ArcK8sDependentResources.")

    registry_path = helm_utils.get_helm_registry_path(cmd, connected_cluster.location, helm_core_utils,
                                                      connected_cluster.agent_version, dp_endpoint_dogfood,
                                                      release_train_dogfood, helm_client_location)

    # Get Helm chart path
    chart_path = helm_utils.get_chart_path(registry_path, kube_config, kube_context, helm_client_location)
    arc_agent_utils = ArcAgentUtils(kube_config, kube_context, values_file)

    arc_agent_utils.execute_arc_agent_disable_features(chart_path, release_namespace, disable_azure_rbac,
                                                       disable_cluster_connect, disable_cl, helm_client_location)

    return str.format(consts.Successfully_Disabled_Features, features, connected_cluster.name)


def get_connectedk8s(cmd, client, resource_group_name, cluster_name):
    return client.get(resource_group_name, cluster_name)


def list_connectedk8s(cmd, client, resource_group_name=None):
    if not resource_group_name:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def client_side_proxy_wrapper(cmd,
                              client,
                              resource_group_name,
                              cluster_name,
                              token=None,
                              path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                              context_name=None,
                              api_server_port=consts.API_SERVER_PORT):

    client_proxy_port = consts.CLIENT_PROXY_PORT
    if int(client_proxy_port) == int(api_server_port):
        raise ClientRequestError('Proxy uses port 47010 internally.', recommendation='Please pass some other unused'
                                 ' port through --port option.')

    cloud = utils.send_cloud_telemetry(cmd)
    args = []
    operating_system = platform.system()
    proc_name = f'arcProxy{operating_system}'

    telemetry.set_debug_info('CSP Version is ', consts.CLIENT_PROXY_VERSION)
    telemetry.set_debug_info('OS is ', operating_system)

    if utils.check_process(proc_name):
        raise ClientRequestError('Another instance of proxy already running')

    port_error_string = ""
    if utils.check_if_port_is_open(api_server_port):
        port_error_string += {f'Port {api_server_port} is already in use. Please select a different port with --port'
                              ' option.\n'}
    if utils.check_if_port_is_open(client_proxy_port):
        telemetry.set_exception(exception='Client proxy port was in use.',
                                fault_type=consts.Client_Proxy_Port_Fault_Type,
                                summary=f'Client proxy port was in use.')
        port_error_string += {f"Port {client_proxy_port} is already in use. This is an internal port that proxy uses."
                              " Please ensure that this port is open before running 'az connectedk8s proxy'.\n"}
    if port_error_string != "":
        raise ClientRequestError(port_error_string)

    # Creating installation location, request uri and older version exe location depending on OS
    if operating_system == 'Windows':
        install_location_string = f'.clientproxy\\arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}.exe'
        requestUri = {f'{consts.CSP_Storage_Url}/{consts.RELEASE_DATE_WINDOWS}/arcProxy{operating_system}'
                      f'{consts.CLIENT_PROXY_VERSION}.exe'}
        older_version_string = f'.clientproxy\\arcProxy{operating_system}*.exe'
        creds_string = r'.azure\accessTokens.json'

    elif(operating_system == 'Linux' or operating_system == 'Darwin'):
        install_location_string = f'.clientproxy/arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}'
        requestUri = {f'{consts.CSP_Storage_Url}/{consts.RELEASE_DATE_LINUX}/arcProxy{operating_system}'
                      f'{consts.CLIENT_PROXY_VERSION}'}
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
            raise CLIInternalError("Failed to download executable with client.",
                                   recommendation="Please check your internet connection." + str(e))

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
        account = get_subscription_id(cmd.cli_ctx)
        account = Profile().get_subscription(account)
        user_type = account['user']['type']

        tenantId = _graph_client_factory(cmd.cli_ctx).config.tenant_id

        if user_type == 'user':
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)},
                         'identity': {'tenantID': tenantId, 'clientID': consts.CLIENTPROXY_CLIENT_ID}}
        else:
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)},
                         'identity': {'tenantID': tenantId, 'clientID': account['user']['name']}}

        if cloud == 'DOGFOOD':
            dict_file['cloud'] = 'AzureDogFood'

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
            telemetry.set_exception(exception='Credentials of user not found.',
                                    fault_type=consts.Creds_NotFound_Fault_Type,
                                    summary='Unable to find creds of user')
            raise UnclassifiedUserFault("Credentials of user not found.")

        if user_type != 'user':
            dict_file['identity']['clientSecret'] = creds
    else:
        dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)}}

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

    proxy_utils.client_side_proxy_main(cmd, client, resource_group_name, cluster_name, args, client_proxy_port,
                                       api_server_port, creds, user_type, debug_mode, token=token, path=path,
                                       context_name=context_name, clientproxy_process=None)
