# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
from logging import exception
import os
import json
import tempfile
import time
from subprocess import Popen, PIPE, run, STDOUT, call, DEVNULL
from base64 import b64encode, b64decode
import stat
import platform
from azure.core.exceptions import ClientAuthenticationError
import yaml
import requests
import urllib.request
import signal
from _thread import interrupt_main
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from knack.util import CLIError
from knack.log import get_logger
from knack.prompting import prompt_y_n
from knack.prompting import NoTTYException
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core._profile import Profile
from azure.cli.core.util import sdk_no_wait
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ManualInterrupt, InvalidArgumentValueError, UnclassifiedUserFault, CLIInternalError, FileOperationError, ClientRequestError, DeploymentError, ValidationError, ArgumentUsageError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError
from msrestazure.azure_exceptions import CloudError
from kubernetes import client as kube_client, config
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from azext_connectedk8s._client_factory import _resource_providers_client
from azext_connectedk8s._client_factory import get_graph_client_service_principals
import azext_connectedk8s._constants as consts
import azext_connectedk8s._utils as utils
from glob import glob
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterIdentity
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


def create_connectedk8s(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="", proxy_cert="", location=None,
                        kube_config=None, kube_context=None, no_wait=False, tags=None, distribution='auto', infrastructure='auto',
                        disable_auto_upgrade=False, cl_oid=None):
    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")

    # Setting subscription id
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Send cloud information to telemetry
    azure_cloud = send_cloud_telemetry(cmd)

    # Fetching Tenant Id
    graph_client = _graph_client_factory(cmd.cli_ctx)
    onboarding_tenant_id = graph_client.config.tenant_id

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

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        azure_cloud = consts.Azure_DogfoodCloudName
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    check_kube_connection(configuration)

    utils.try_list_node_fix()
    required_node_exists = check_linux_amd64_node(configuration)
    if not required_node_exists:
        telemetry.set_user_fault()
        telemetry.set_exception(exception="Couldn't find any node on the kubernetes cluster with the architecture type 'amd64' and OS 'linux'", fault_type=consts.Linux_Amd64_Node_Not_Exists,
                                summary="Couldn't find any node on the kubernetes cluster with the architecture type 'amd64' and OS 'linux'")
        logger.warning("Please ensure that this Kubernetes cluster have any nodes with OS 'linux' and architecture 'amd64', for scheduling the Arc-Agents onto and connecting to Azure. Learn more at {}".format("https://aka.ms/ArcK8sSupportedOSArchitecture"))

    # Get kubernetes cluster info
    kubernetes_version = get_server_version(configuration)

    if distribution == 'auto':
        kubernetes_distro = get_kubernetes_distro(configuration)  # (cluster heuristics)
    else:
        kubernetes_distro = distribution
    if infrastructure == 'auto':
        kubernetes_infra = get_kubernetes_infra(configuration)  # (cluster heuristics)
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
        logger.warning("Connecting an Azure Kubernetes Service (AKS) cluster to Azure Arc is only required for running Arc enabled services like App Services and Data Services on the cluster. Other features like Azure Monitor and Azure Defender are natively available on AKS. Learn more at {}.".format(" https://go.microsoft.com/fwlink/?linkid=2144200"))

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        raise ClientRequestError("The current helm version is not supported for azure-arc onboarding.", recommendation="Please upgrade helm to a stable version and try again.")

    # Validate location
    utils.validate_location(cmd, location)
    resourceClient = _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context)
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                               error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                                               message_for_not_found="The helm release 'azure-arc' is present but the azure-arc namespace/configmap is missing. Please run 'helm delete azure-arc --no-hooks' to cleanup the release before onboarding the cluster again.")
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                # Re-put connected cluster
                try:
                    public_key = client.get(configmap_rg_name,
                                            configmap_cluster_name).agent_public_key_certificate
                except Exception as e:  # pylint: disable=broad-except
                    utils.arm_exception_handler(e, consts.Get_ConnectedCluster_Fault_Type, 'Failed to check if connected cluster resource already exists.')
                cc = generate_request_payload(configuration, location, public_key, tags, kubernetes_distro, kubernetes_infra)
                create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)
            else:
                telemetry.set_exception(exception='The kubernetes cluster is already onboarded', fault_type=consts.Cluster_Already_Onboarded_Fault_Type,
                                        summary='Kubernetes cluster already onboarded')
                raise ArgumentUsageError("The kubernetes cluster you are trying to onboard " +
                                         "is already onboarded to the resource group" +
                                         " '{}' with resource name '{}'.".format(configmap_rg_name, configmap_cluster_name))
        else:
            # Cleanup agents and continue with put
            utils.delete_arc_agents(release_namespace, kube_config, kube_context, configuration)
    else:
        if connected_cluster_exists(client, resource_group_name, cluster_name):
            telemetry.set_exception(exception='The connected cluster resource already exists', fault_type=consts.Resource_Already_Exists_Fault_Type,
                                    summary='Connected cluster resource already exists')
            raise ArgumentUsageError("The connected cluster resource {} already exists ".format(cluster_name) +
                                     "in the resource group {} ".format(resource_group_name) +
                                     "and corresponds to a different Kubernetes cluster.", recommendation="To onboard this Kubernetes cluster " +
                                     "to Azure, specify different resource name or resource group name.")

    # Resource group Creation
    if resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id) is False:
        from azure.cli.core.profiles import ResourceType
        ResourceGroup = cmd.get_models('ResourceGroup', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
        parameters = ResourceGroup(location=location)
        try:
            resourceClient.resource_groups.create_or_update(resource_group_name, parameters)
        except Exception as e:  # pylint: disable=broad-except
            utils.arm_exception_handler(e, consts.Create_ResourceGroup_Fault_Type, 'Failed to create the resource group')

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context)

    # Setting the config dataplane endpoint
    config_dp_endpoint = get_config_dp_endpoint(cmd, location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood, release_train_dogfood)

    # Get azure-arc agent version for telemetry
    azure_arc_agent_version = registry_path.split(':')[1]
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': azure_arc_agent_version})

    # Get helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context)

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
    cc = generate_request_payload(configuration, location, public_key, tags, kubernetes_distro, kubernetes_infra)

    # Create connected cluster resource
    put_cc_response = create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)

    # Checking if custom locations rp is registered and fetching oid if it is registered
    enable_custom_locations, custom_locations_oid = check_cl_registration_and_get_oid(cmd, cl_oid)

    # Install azure-arc agents
    utils.helm_install_release(chart_path, subscription_id, kubernetes_distro, kubernetes_infra, resource_group_name, cluster_name,
                               location, onboarding_tenant_id, http_proxy, https_proxy, no_proxy, proxy_cert, private_key_pem, kube_config,
                               kube_context, no_wait, values_file_provided, values_file, azure_cloud, disable_auto_upgrade, enable_custom_locations, custom_locations_oid)

    return put_cc_response


def send_cloud_telemetry(cmd):
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AzureCloud': cmd.cli_ctx.cloud.name})
    cloud_name = cmd.cli_ctx.cloud.name.upper()
    # Setting cloud name to format that is understood by golang SDK.
    if cloud_name == consts.PublicCloud_OriginalName:
        cloud_name = consts.Azure_PublicCloudName
    elif cloud_name == consts.USGovCloud_OriginalName:
        cloud_name = consts.Azure_USGovCloudName
    return cloud_name


def validate_env_file_dogfood(values_file, values_file_provided):
    if not values_file_provided:
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


def check_kube_connection(configuration):
    api_instance = kube_client.NetworkingV1Api(kube_client.ApiClient(configuration))
    try:
        api_instance.get_api_resources()
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Unable to verify connectivity to the Kubernetes cluster.")
        utils.kubernetes_exception_handler(e, consts.Kubernetes_Connectivity_FaultType, 'Unable to verify connectivity to the Kubernetes cluster')


def check_helm_install(kube_config, kube_context):
    cmd_helm_installed = ["helm", "--debug"]
    if kube_config:
        cmd_helm_installed.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_installed.extend(["--kube-context", kube_context])
    try:
        response_helm_installed = Popen(cmd_helm_installed, stdout=PIPE, stderr=PIPE)
        _, error_helm_installed = response_helm_installed.communicate()
        if response_helm_installed.returncode != 0:
            if "unknown flag" in error_helm_installed.decode("ascii"):
                telemetry.set_exception(exception='Helm 3 not found', fault_type=consts.Helm_Version_Fault_Type,
                                        summary='Helm3 not found on the machine')
                raise ValidationError("Helm 3 not found", recommendation="Please install the latest version of Helm. " +
                                      "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")
            telemetry.set_exception(exception=error_helm_installed.decode("ascii"), fault_type=consts.Helm_Installation_Fault_Type,
                                    summary='Helm3 not installed on the machine')
            raise ValidationError(error_helm_installed.decode("ascii"))
    except FileNotFoundError as e:
        telemetry.set_exception(exception=e, fault_type=consts.Check_HelmInstallation_Fault_Type,
                                summary='Unable to verify helm installation')
        raise ValidationError("Helm is not installed or the helm binary is not accessible to the connectedk8s cli. Could be a permission issue.",
                              recommendation="Ensure that you have the latest version of Helm installed on your machine and run using admin privilege. " +
                              "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")
    except Exception as e2:
        telemetry.set_exception(exception=e2, fault_type=consts.Check_HelmInstallation_Fault_Type,
                                summary='Error while verifying helm installation')
        raise ValidationError("Error occured while verifying helm installation: " + str(e2))


def check_helm_version(kube_config, kube_context):
    cmd_helm_version = ["helm", "version", "--short", "--client"]
    if kube_config:
        cmd_helm_version.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_version.extend(["--kube-context", kube_context])
    response_helm_version = Popen(cmd_helm_version, stdout=PIPE, stderr=PIPE)
    output_helm_version, error_helm_version = response_helm_version.communicate()
    if response_helm_version.returncode != 0:
        telemetry.set_exception(exception=error_helm_version.decode('ascii'), fault_type=consts.Check_HelmVersion_Fault_Type,
                                summary='Unable to determine helm version')
        raise CLIInternalError("Unable to determine helm version: " + error_helm_version.decode("ascii"))
    if "v2" in output_helm_version.decode("ascii"):
        telemetry.set_exception(exception='Helm 3 not found', fault_type=consts.Helm_Version_Fault_Type,
                                summary='Helm3 not found on the machine')
        raise ValidationError("Helm version 3+ is required.",
                              recommendation="Ensure that you have installed the latest version of Helm. " +
                              "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")
    return output_helm_version.decode('ascii')


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


def get_config_dp_endpoint(cmd, location):
    cloud_based_domain = cmd.cli_ctx.cloud.endpoints.active_directory.split('.')[2]
    config_dp_endpoint = "https://{}.dp.kubernetesconfiguration.azure.{}".format(location, cloud_based_domain)
    return config_dp_endpoint


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


def get_server_version(configuration):
    api_instance = kube_client.VersionApi(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.get_code()
        return api_response.git_version
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Unable to fetch kubernetes version.")
        utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Version_Fault_Type, 'Unable to fetch kubernetes version',
                                           raise_error=False)


def get_kubernetes_distro(configuration):  # Heuristic
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        if api_response.items:
            labels = api_response.items[0].metadata.labels
            provider_id = str(api_response.items[0].spec.provider_id)
            annotations = list(api_response.items)[0].metadata.annotations
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
            if provider_id.startswith("kind://"):
                return "kind"
            if provider_id.startswith("k3s://"):
                return "k3s"
            if annotations.get("rke.cattle.io/external-ip") or annotations.get("rke.cattle.io/internal-ip"):
                return "rancher_rke"
            if provider_id.startswith("moc://"):   # Todo: ask from aks hci team for more reliable identifier in node labels,etc
                return "generic"                   # return "aks_hci"
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to fetch kubernetes distribution: " + str(e))
        utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Distro_Fault_Type, 'Unable to fetch kubernetes distribution',
                                           raise_error=False)
        return "generic"


def get_kubernetes_infra(configuration):  # Heuristic
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        if api_response.items:
            provider_id = str(api_response.items[0].spec.provider_id)
            infra = provider_id.split(':')[0]
            if infra == "k3s" or infra == "kind":
                return "generic"
            if infra == "azure":
                return "azure"
            if infra == "gce":
                return "gcp"
            if infra == "aws":
                return "aws"
            if infra == "moc":                  # Todo: ask from aks hci team for more reliable identifier in node labels,etc
                return "generic"                # return "azure_stack_hci"
            return utils.validate_infrastructure_type(infra)
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to fetch kubernetes infrastructure: " + str(e))
        utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Infra_Fault_Type, 'Unable to fetch kubernetes infrastructure',
                                           raise_error=False)
        return "generic"


def check_linux_amd64_node(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        for item in api_response.items:
            node_arch = item.metadata.labels.get("kubernetes.io/arch")
            node_os = item.metadata.labels.get("kubernetes.io/os")
            if node_arch == "amd64" and node_os == "linux":
                return True
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to find a linux/amd64 node: " + str(e))
        utils.kubernetes_exception_handler(e, consts.Kubernetes_Node_Type_Fetch_Fault, 'Unable to find a linux/amd64 node',
                                           raise_error=False)
    return False


def generate_request_payload(configuration, location, public_key, tags, kubernetes_distro, kubernetes_infra):
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
    return client.get(resource_group_name, cluster_name)


def list_connectedk8s(cmd, client, resource_group_name=None):
    if not resource_group_name:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def delete_connectedk8s(cmd, client, resource_group_name, cluster_name,
                        kube_config=None, kube_context=None, no_wait=False):
    logger.warning("Ensure that you have the latest helm version installed before proceeding to avoid unexpected errors.")
    logger.warning("This operation might take a while ...\n")

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled
    # AKS clusters if the user had not logged in.
    check_kube_connection(configuration)

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    check_helm_version(kube_config, kube_context)

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context)
    if not release_namespace:
        delete_cc_resource(client, resource_group_name, cluster_name, no_wait)
        return

    # Loading config map
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
    except Exception as e:  # pylint: disable=broad-except
        utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                           error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                                           message_for_not_found="The helm release 'azure-arc' is present but the azure-arc namespace/configmap is missing. Please run 'helm delete azure-arc --no-hooks' to cleanup the release before onboarding the cluster again.")

    subscription_id = get_subscription_id(cmd.cli_ctx)

    if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and
            configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower() and configmap.data["AZURE_SUBSCRIPTION_ID"].lower() == subscription_id.lower()):

        armid = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Kubernetes/connectedClusters/{}".format(subscription_id, resource_group_name, cluster_name)
        arm_hash = hashlib.sha256(armid.lower().encode('utf-8')).hexdigest()

        if check_proxy_kubeconfig(kube_config, kube_context, arm_hash):
            telemetry.set_exception(exception='Encountered proxy kubeconfig during deletion.', fault_type=consts.Proxy_Kubeconfig_During_Deletion_Fault_Type,
                                    summary='The resource cannot be deleted as user is using proxy kubeconfig.')
            raise ClientRequestError("az connectedk8s delete is not supported when using the Cluster Connect kubeconfig.", recommendation="Run the az connectedk8s delete command with your kubeconfig file pointing to the actual Kubernetes cluster to ensure that the agents are cleaned up successfully as part of the delete command.")

        delete_cc_resource(client, resource_group_name, cluster_name, no_wait)
    else:
        telemetry.set_exception(exception='Unable to delete connected cluster', fault_type=consts.Bad_DeleteRequest_Fault_Type,
                                summary='The resource cannot be deleted as kubernetes cluster is onboarded with some other resource id')
        raise ArgumentUsageError("The current context in the kubeconfig file does not correspond " +
                                 "to the connected cluster resource specified. Agents installed on this cluster correspond " +
                                 "to the resource group name '{}' ".format(configmap.data["AZURE_RESOURCE_GROUP"]) +
                                 "and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_NAME"]))

    # Deleting the azure-arc agents
    utils.delete_arc_agents(release_namespace, kube_config, kube_context, configuration)


def get_release_namespace(kube_config, kube_context):
    cmd_helm_release = ["helm", "list", "-a", "--all-namespaces", "--output", "json"]
    if kube_config:
        cmd_helm_release.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_release.extend(["--kube-context", kube_context])
    response_helm_release = Popen(cmd_helm_release, stdout=PIPE, stderr=PIPE)
    output_helm_release, error_helm_release = response_helm_release.communicate()
    if response_helm_release.returncode != 0:
        if 'forbidden' in error_helm_release.decode("ascii"):
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
        if release['name'] == 'azure-arc':
            return release['namespace']
    return None


def create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait):
    try:
        return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name,
                           cluster_name=cluster_name, connected_cluster=cc)
    except CloudError as e:
        utils.arm_exception_handler(e, consts.Create_ConnectedCluster_Fault_Type, 'Unable to create connected cluster resource')


def delete_cc_resource(client, resource_group_name, cluster_name, no_wait):
    try:
        sdk_no_wait(no_wait, client.delete,
                    resource_group_name=resource_group_name,
                    cluster_name=cluster_name)
    except CloudError as e:
        utils.arm_exception_handler(e, consts.Delete_ConnectedCluster_Fault_Type, 'Unable to delete connected cluster resource')


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def update_agents(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="", proxy_cert="",
                  disable_proxy=False, kube_config=None, kube_context=None, auto_upgrade=None):
    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")

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

    if https_proxy == "" and http_proxy == "" and no_proxy == "" and proxy_cert == "" and not disable_proxy and not auto_upgrade:
        raise RequiredArgumentMissingError(consts.No_Param_Error)

    if (https_proxy or http_proxy or no_proxy or proxy_cert) and disable_proxy:
        raise MutuallyExclusiveArgumentError(consts.EnableProxy_Conflict_Error)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    check_kube_connection(configuration)

    utils.try_list_node_fix()

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        raise ClientRequestError("The current helm version is not supported for azure-arc onboarding. Please upgrade helm to a stable version and try again.")

    validate_release_namespace(client, cluster_name, resource_group_name, configuration, kube_config, kube_context)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
    else:
        kubernetes_distro = get_kubernetes_distro(configuration)

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
    else:
        kubernetes_infra = get_kubernetes_infra(configuration)

    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro,
        'Context.Default.AzureCLI.KubernetesInfra': kubernetes_infra
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context)

    # Setting the config dataplane endpoint
    config_dp_endpoint = get_config_dp_endpoint(cmd, connected_cluster.location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood, release_train_dogfood)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context)

    cmd_helm_upgrade = ["helm", "upgrade", "azure-arc", chart_path,
                        "--reuse-values",
                        "--wait", "--output", "json"]
    if values_file_provided:
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
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    response_helm_upgrade = Popen(cmd_helm_upgrade, stdout=PIPE, stderr=PIPE)
    _, error_helm_upgrade = response_helm_upgrade.communicate()
    if response_helm_upgrade.returncode != 0:
        if ('forbidden' in error_helm_upgrade.decode("ascii") or 'timed out waiting for the condition' in error_helm_upgrade.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_upgrade.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        raise CLIInternalError(str.format(consts.Update_Agent_Failure, error_helm_upgrade.decode("ascii")))

    return str.format(consts.Update_Agent_Success, connected_cluster.name)


def upgrade_agents(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None, arc_agent_version=None):
    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    check_kube_connection(configuration)

    utils.try_list_node_fix()

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        raise ClientRequestError("The current helm version is not supported for azure-arc onboarding. Please upgrade helm to a stable version and try again.")

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context)
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                               error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                                               message_for_not_found="The helm release 'azure-arc' is present but the azure-arc namespace/configmap is missing. Please run 'helm delete azure-arc --no-hooks' to cleanup the release before onboarding the cluster again.")
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
                                     recommendation="Please run az connectedk8s update -n <connected-cluster-name> -g <resource-group-name> --auto-upgrade 'false' before performing manual upgrade")

    else:
        telemetry.set_exception(exception="The azure-arc release namespace couldn't be retrieved", fault_type=consts.Release_Namespace_Not_Found,
                                summary="The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc.")
        raise ClientRequestError("The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc.",
                                 recommendation="Please run 'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>' to onboard the cluster")

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
    else:
        kubernetes_distro = get_kubernetes_distro(configuration)

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
    else:
        kubernetes_infra = get_kubernetes_infra(configuration)

    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro,
        'Context.Default.AzureCLI.KubernetesInfra': kubernetes_infra
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context)

    # Setting the config dataplane endpoint
    config_dp_endpoint = get_config_dp_endpoint(cmd, connected_cluster.location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood, release_train_dogfood)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    if arc_agent_version is not None:
        agent_version = arc_agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context)

    cmd_helm_values = ["helm", "get", "values", "azure-arc", "--namespace", release_namespace]
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

    cmd_helm_upgrade = ["helm", "upgrade", "azure-arc", chart_path, "--namespace", release_namespace,
                        "--output", "json", "--atomic"]

    proxy_enabled_param_added = False
    infra_added = False
    for key, value in utils.flatten(existing_user_values).items():
        if value is not None:
            if key == "global.isProxyEnabled":
                proxy_enabled_param_added = True
            if (key == "global.httpProxy" or key == "global.httpsProxy" or key == "global.noProxy"):
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

    if values_file_provided:
        cmd_helm_upgrade.extend(["-f", values_file])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    response_helm_upgrade = Popen(cmd_helm_upgrade, stdout=PIPE, stderr=PIPE)
    _, error_helm_upgrade = response_helm_upgrade.communicate()

    if response_helm_upgrade.returncode != 0:
        if ('forbidden' in error_helm_upgrade.decode("ascii") or 'timed out waiting for the condition' in error_helm_upgrade.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_upgrade.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        raise CLIInternalError(str.format(consts.Upgrade_Agent_Failure, error_helm_upgrade.decode("ascii")))

    return str.format(consts.Upgrade_Agent_Success, connected_cluster.name)


def validate_release_namespace(client, cluster_name, resource_group_name, configuration, kube_config, kube_context):
    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context)
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                               error_message="Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: ",
                                               message_for_not_found="The helm release 'azure-arc' is present but the azure-arc namespace/configmap is missing. Please run 'helm delete azure-arc --no-hooks' to cleanup the release before onboarding the cluster again.")
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


def get_all_helm_values(release_namespace, kube_config, kube_context):
    cmd_helm_values = ["helm", "get", "values", "--all", "azure-arc", "--namespace", release_namespace]
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
    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")

    features = [x.lower() for x in features]
    enable_cluster_connect, enable_azure_rbac, enable_cl = utils.check_features_to_update(features)

    if enable_azure_rbac:
        if (azrbac_client_id is None) or (azrbac_client_secret is None):
            telemetry.set_exception(exception='Application ID or secret is not provided for Azure RBAC', fault_type=consts.Application_Details_Not_Provided_For_Azure_RBAC_Fault,
                                    summary='Application id, application secret is required to enable/update Azure RBAC feature')
            raise RequiredArgumentMissingError("Please provide Application id, application secret to enable/update Azure RBAC feature")
        if azrbac_skip_authz_check is None:
            azrbac_skip_authz_check = ""
        azrbac_skip_authz_check = escape_proxy_settings(azrbac_skip_authz_check)

    if enable_cl:
        enable_cl, custom_locations_oid = check_cl_registration_and_get_oid(cmd, cl_oid)
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
    values_file_provided, values_file = utils.get_values_file()

    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    check_kube_connection(configuration)

    utils.try_list_node_fix()

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        raise ClientRequestError("The current helm version is not supported for azure-arc onboarding. Please upgrade helm to a stable version and try again.")

    validate_release_namespace(client, cluster_name, resource_group_name, configuration, kube_config, kube_context)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
    else:
        kubernetes_distro = get_kubernetes_distro(configuration)

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
    else:
        kubernetes_infra = get_kubernetes_infra(configuration)

    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro,
        'Context.Default.AzureCLI.KubernetesInfra': kubernetes_infra
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context)

    # Setting the config dataplane endpoint
    config_dp_endpoint = get_config_dp_endpoint(cmd, connected_cluster.location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood, release_train_dogfood)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context)

    cmd_helm_upgrade = ["helm", "upgrade", "azure-arc", chart_path,
                        "--reuse-values",
                        "--wait", "--output", "json"]
    if values_file_provided:
        cmd_helm_upgrade.extend(["-f", values_file])
    if kube_config:
        cmd_helm_upgrade.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_upgrade.extend(["--kube-context", kube_context])
    if enable_azure_rbac:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled=true"])
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.clientId={}".format(azrbac_client_id)])
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.clientSecret={}".format(azrbac_client_secret)])
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.skipAuthzCheck={}".format(azrbac_skip_authz_check)])
    if enable_cluster_connect:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.clusterconnect-agent.enabled=true"])
    if enable_cl:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.enabled=true"])
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.customLocations.oid={}".format(custom_locations_oid)])

    response_helm_upgrade = Popen(cmd_helm_upgrade, stdout=PIPE, stderr=PIPE)
    _, error_helm_upgrade = response_helm_upgrade.communicate()
    if response_helm_upgrade.returncode != 0:
        if ('forbidden' in error_helm_upgrade.decode("ascii") or 'timed out waiting for the condition' in error_helm_upgrade.decode("ascii")):
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

    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")

    disable_cluster_connect, disable_azure_rbac, disable_cl = utils.check_features_to_update(features)

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Checking whether optional extra values file has been provided.
    values_file_provided, values_file = utils.get_values_file()

    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    load_kube_config(kube_config, kube_context)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    check_kube_connection(configuration)

    utils.try_list_node_fix()

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        raise ClientRequestError("The current helm version is not supported for azure-arc onboarding. Please upgrade helm to a stable version and try again.")

    release_namespace = validate_release_namespace(client, cluster_name, resource_group_name, configuration, kube_config, kube_context)

    # Fetch Connected Cluster for agent version
    connected_cluster = get_connectedk8s(cmd, client, resource_group_name, cluster_name)

    if hasattr(connected_cluster, 'distribution') and (connected_cluster.distribution is not None):
        kubernetes_distro = connected_cluster.distribution
    else:
        kubernetes_distro = get_kubernetes_distro(configuration)

    if hasattr(connected_cluster, 'infrastructure') and (connected_cluster.infrastructure is not None):
        kubernetes_infra = connected_cluster.infrastructure
    else:
        kubernetes_infra = get_kubernetes_infra(configuration)

    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro,
        'Context.Default.AzureCLI.KubernetesInfra': kubernetes_infra
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

    if disable_cluster_connect:
        try:
            helm_values = get_all_helm_values(release_namespace, kube_config, kube_context)
            if not disable_cl and helm_values.get('systemDefaultValues').get('customLocations').get('enabled') is True and helm_values.get('systemDefaultValues').get('customLocations').get('oid') != "":
                raise Exception("Disabling 'cluster-connect' feature is not allowed when 'custom-locations' feature is enabled.")
        except AttributeError as e:
            pass
        except Exception as ex:
            raise ArgumentUsageError(str(ex))

    if disable_cl:
        logger.warning("Disabling 'custom-locations' feature might impact some dependent resources. Learn more about this at https://aka.ms/ArcK8sDependentResources.")

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context)

    # Setting the config dataplane endpoint
    config_dp_endpoint = get_config_dp_endpoint(cmd, connected_cluster.location)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, config_dp_endpoint, dp_endpoint_dogfood, release_train_dogfood)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version
        registry_path = reg_path_array[0] + ":" + agent_version

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context)

    cmd_helm_upgrade = ["helm", "upgrade", "azure-arc", chart_path,
                        "--reuse-values",
                        "--wait", "--output", "json"]
    if values_file_provided:
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
        if ('forbidden' in error_helm_upgrade.decode("ascii") or 'timed out waiting for the condition' in error_helm_upgrade.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_upgrade.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        raise CLIInternalError(str.format(consts.Error_disabling_Features, error_helm_upgrade.decode("ascii")))

    return str.format(consts.Successfully_Disabled_Features, features, connected_cluster.name)


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

    client_proxy_port = consts.CLIENT_PROXY_PORT
    if int(client_proxy_port) == int(api_server_port):
        raise ClientRequestError('Proxy uses port 47010 internally.', recommendation='Please pass some other unused port through --port option.')

    cloud = send_cloud_telemetry(cmd)
    args = []
    operating_system = platform.system()
    proc_name = f'arcProxy{operating_system}'

    telemetry.set_debug_info('CSP Version is ', consts.CLIENT_PROXY_VERSION)
    telemetry.set_debug_info('OS is ', operating_system)

    if(check_process(proc_name)):
        raise ClientRequestError('Another instance of proxy already running')

    port_error_string = ""
    if check_if_port_is_open(api_server_port):
        port_error_string += f'Port {api_server_port} is already in use. Please select a different port with --port option.\n'
    if check_if_port_is_open(client_proxy_port):
        telemetry.set_exception(exception='Client proxy port was in use.', fault_type=consts.Client_Proxy_Port_Fault_Type,
                                summary=f'Client proxy port was in use.')
        port_error_string += f"Port {client_proxy_port} is already in use. This is an internal port that proxy uses. Please ensure that this port is open before running 'az connectedk8s proxy'.\n"
    if port_error_string != "":
        raise ClientRequestError(port_error_string)

    # Creating installation location, request uri and older version exe location depending on OS
    if(operating_system == 'Windows'):
        install_location_string = f'.clientproxy\\arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}.exe'
        requestUri = f'{consts.CSP_Storage_Url}/{consts.RELEASE_DATE_WINDOWS}/arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}.exe'
        older_version_string = f'.clientproxy\\arcProxy{operating_system}*.exe'
        creds_string = r'.azure\accessTokens.json'

    elif(operating_system == 'Linux' or operating_system == 'Darwin'):
        install_location_string = f'.clientproxy/arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}'
        requestUri = f'{consts.CSP_Storage_Url}/{consts.RELEASE_DATE_LINUX}/arcProxy{operating_system}{consts.CLIENT_PROXY_VERSION}'
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
        account = get_subscription_id(cmd.cli_ctx)
        account = Profile().get_subscription(account)
        user_type = account['user']['type']

        tenantId = _graph_client_factory(cmd.cli_ctx).config.tenant_id

        if user_type == 'user':
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)}, 'identity': {'tenantID': tenantId, 'clientID': consts.CLIENTPROXY_CLIENT_ID}}
        else:
            dict_file = {'server': {'httpPort': int(client_proxy_port), 'httpsPort': int(api_server_port)}, 'identity': {'tenantID': tenantId, 'clientID': account['user']['name']}}

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
            telemetry.set_exception(exception='Credentials of user not found.', fault_type=consts.Creds_NotFound_Fault_Type,
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

    client_side_proxy_main(cmd, client, resource_group_name, cluster_name, 0, args, client_proxy_port, api_server_port, operating_system, creds, user_type, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=None)


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
    expiry, clientproxy_process = client_side_proxy(cmd, client, resource_group_name, cluster_name, 0, args, client_proxy_port, api_server_port, operating_system, creds, user_type, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=None)
    next_refresh_time = expiry - consts.CSP_REFRESH_TIME

    while(True):
        time.sleep(60)
        if(check_if_csp_is_running(clientproxy_process)):
            if time.time() >= next_refresh_time:
                expiry, clientproxy_process = client_side_proxy(cmd, client, resource_group_name, cluster_name, 1, args, client_proxy_port, api_server_port, operating_system, creds, user_type, debug_mode, token=token, path=path, context_name=context_name, clientproxy_process=clientproxy_process)
                next_refresh_time = expiry - consts.CSP_REFRESH_TIME
        else:
            telemetry.set_exception(exception='Process closed externally.', fault_type=consts.Proxy_Closed_Externally_Fault_Type,
                                    summary='Process closed externally.')
            raise ManualInterrupt('Proxy closed externally.')


def client_side_proxy(cmd,
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
        response = client.list_cluster_user_credentials(resource_group_name, cluster_name, auth_method, True)
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

        if user_type == 'user':
            identity_data = {}
            identity_data['refreshToken'] = creds
            identity_uri = f'https://localhost:{api_server_port}/identity/rt'

            # Needed to prevent skip tls warning from printing to the console
            original_stderr = sys.stderr
            f = open(os.devnull, 'w')
            sys.stderr = f

            make_api_call_with_retries(identity_uri, identity_data, False, consts.Post_RefreshToken_Fault_Type,
                                       'Unable to post refresh token details to clientproxy',
                                       "Failed to pass refresh token details to proxy.", clientproxy_process)
            sys.stderr = original_stderr

    data = prepare_clientproxy_data(response)
    expiry = data['hybridConnectionConfig']['expirationTime']

    if token is not None:
        data['kubeconfigs'][0]['value'] = insert_token_in_kubeconfig(data, token)

    uri = f'http://localhost:{client_proxy_port}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Kubernetes/connectedClusters/{cluster_name}/register?api-version=2020-10-01'

    # Posting hybrid connection details to proxy in order to get kubeconfig
    response = make_api_call_with_retries(uri, data, False, consts.Post_Hybridconn_Fault_Type,
                                          'Unable to post hybrid connection details to clientproxy',
                                          "Failed to pass hybrid connection details to proxy.", clientproxy_process)

    if flag == 0:
        # Decoding kubeconfig into a string
        try:
            kubeconfig = json.loads(response.text)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                    summary='Unable to load Kubeconfig')
            close_subprocess_and_raise_cli_error(clientproxy_process, "Failed to load kubeconfig." + str(e))

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
            close_subprocess_and_raise_cli_error(clientproxy_process, "Failed to merge kubeconfig." + str(e))

    return expiry, clientproxy_process


def make_api_call_with_retries(uri, data, tls_verify, fault_type, summary, cli_error, clientproxy_process):
    for i in range(consts.API_CALL_RETRIES):
        try:
            response = requests.post(uri, json=data, verify=tls_verify)
            return response
        except Exception as e:
            if i != consts.API_CALL_RETRIES - 1:
                pass
            else:
                telemetry.set_exception(exception=e, fault_type=fault_type, summary=summary)
                close_subprocess_and_raise_cli_error(clientproxy_process, cli_error + str(e))


def insert_token_in_kubeconfig(data, token):
    b64kubeconfig = data['kubeconfigs'][0]['value']
    decoded_kubeconfig_str = b64decode(b64kubeconfig).decode("utf-8")
    dict_yaml = yaml.safe_load(decoded_kubeconfig_str)
    dict_yaml['users'][0]['user']['token'] = token
    kubeconfig = yaml.dump(dict_yaml).encode("utf-8")
    b64kubeconfig = b64encode(kubeconfig).decode("utf-8")
    return b64kubeconfig


def check_process(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    for proc in process_iter():
        try:
            if proc.name().startswith(processName):
                return True
        except (NoSuchProcess, AccessDenied, ZombieProcess):
            pass
    return False


def get_custom_locations_oid(cmd, cl_oid):
    try:
        sp_graph_client = get_graph_client_service_principals(cmd.cli_ctx)
        sub_filters = []
        sub_filters.append("displayName eq '{}'".format("Custom Locations RP"))
        result = list(sp_graph_client.list(filter=(' and '.join(sub_filters))))
        if len(result) != 0:
            if cl_oid is not None and cl_oid != result[0].object_id:
                logger.debug("The 'Custom-locations' OID passed is different from the actual OID({}) of the Custom Locations RP app. Proceeding with the correct one...".format(result[0].object_id))
            return result[0].object_id  # Using the fetched OID

        if cl_oid is None:
            logger.warning("Failed to enable Custom Locations feature on the cluster. Unable to fetch Object ID of Azure AD application used by Azure Arc service. Try enabling the feature by passing the --custom-locations-oid parameter directly. Learn more at https://aka.ms/CustomLocationsObjectID")
            telemetry.set_exception(exception='Unable to fetch oid of custom locations app.', fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type,
                                    summary='Unable to fetch oid for custom locations app.')
            return ""
        else:
            return cl_oid
    except Exception as e:
        log_string = "Unable to fetch the Object ID of the Azure AD application used by Azure Arc service. "
        telemetry.set_exception(exception=e, fault_type=consts.Custom_Locations_OID_Fetch_Fault_Type,
                                summary='Unable to fetch oid for custom locations app.')
        if cl_oid:
            log_string += "Proceeding with the Object ID provided to enable the 'custom-locations' feature."
            logger.warning(log_string)
            return cl_oid
        log_string += "Unable to enable the 'custom-locations' feature. " + str(e)
        logger.warning(log_string)
        return ""


def check_cl_registration_and_get_oid(cmd, cl_oid):
    enable_custom_locations = True
    custom_locations_oid = ""
    try:
        rp_client = _resource_providers_client(cmd.cli_ctx)
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
        logger.warning("Unable to fetch registration state of 'Microsoft.ExtendedLocation'. Failed to enable 'custom-locations' feature...")
        telemetry.set_exception(exception=e, fault_type=consts.Custom_Locations_Registration_Check_Fault_Type,
                                summary='Unable to fetch status of Custom Locations RP registration.')
    return enable_custom_locations, custom_locations_oid


def check_if_port_is_open(port):
    try:
        connections = net_connections(kind='inet')
        for tup in connections:
            if int(tup[3][1]) == int(port):
                return True
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Port_Check_Fault_Type,
                                summary='Failed to check if port is in use.')
        if platform.system() != 'Darwin':
            logger.info("Failed to check if port is in use. " + str(e))
        return False
    return False


def close_subprocess_and_raise_cli_error(proc_subprocess, msg):
    proc_subprocess.terminate()
    raise CLIInternalError(msg)


def check_if_csp_is_running(clientproxy_process):
    if clientproxy_process.poll() is None:
        return True
    else:
        return False
