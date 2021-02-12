# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import shutil
import json
from subprocess import Popen, PIPE
from base64 import b64encode
import yaml

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from azure.cli.core import telemetry
from msrestazure.azure_exceptions import CloudError
from kubernetes import client as kube_client, config
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
import azext_connectedk8s._constants as consts
import azext_connectedk8s._utils as utils
import azext_connectedk8s._validators as validate
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterAADProfile, ConnectedClusterIdentity
from distutils.util import strtobool

logger = get_logger(__name__)

# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def create_connectedk8s(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="", proxy_cert="", location=None,
                        kube_config=None, kube_context=None, no_wait=False, tags=None, distribution='auto', infrastructure='auto', disable_auto_upgrade=False,
                        enable_azure_rbac=False, guard_client_id=None, guard_client_secret=None):
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
        telemetry.set_user_fault()
        telemetry.set_exception(fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
                                summary='Proxy cert path does not exist')
        raise CLIError(str.format(consts.Proxy_Cert_Path_Does_Not_Exist_Error, proxy_cert))

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

    # Get kubernetes cluster info
    kubernetes_version = get_server_version(configuration)
    # Validate enable-azure-rbac
    if enable_azure_rbac:
        validate.validate_enable_azure_rbac(kubernetes_version, guard_client_id, guard_client_secret)
    
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
        logger.warning("The cluster you are trying to connect to Azure Arc is an Azure Kubernetes Service (AKS) cluster. While Arc onboarding an AKS cluster is possible, it's not necessary. Learn more at {}.".format(" https://go.microsoft.com/fwlink/?linkid=2144200"))

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        telemetry.set_user_fault()
        raise CLIError("The current helm version is not supported for azure-arc onboarding. Please upgrade helm to a stable version and try again.")

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
                telemetry.set_user_fault()
                telemetry.set_exception(exception='The kubernetes cluster is already onboarded', fault_type=consts.Cluster_Already_Onboarded_Fault_Type,
                                        summary='Kubernetes cluster already onboarded')
                raise CLIError("The kubernetes cluster you are trying to onboard " +
                               "is already onboarded to the resource group" +
                               " '{}' with resource name '{}'.".format(configmap_rg_name, configmap_cluster_name))
        else:
            # Cleanup agents and continue with put
            utils.delete_arc_agents(release_namespace, kube_config, kube_context, configuration)
    else:
        if connected_cluster_exists(client, resource_group_name, cluster_name):
            telemetry.set_user_fault()
            telemetry.set_exception(exception='The connected cluster resource already exists', fault_type=consts.Resource_Already_Exists_Fault_Type,
                                    summary='Connected cluster resource already exists')
            raise CLIError("The connected cluster resource {} already exists ".format(cluster_name) +
                           "in the resource group {} ".format(resource_group_name) +
                           "and corresponds to a different Kubernetes cluster. To onboard this Kubernetes cluster " +
                           "to Azure, specify different resource name or resource group name.")

    # Resource group Creation
    if resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id) is False:
        resource_group_params = {'location': location}
        try:
            resourceClient.resource_groups.create_or_update(resource_group_name, resource_group_params)
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
        raise CLIError("Failed to generate public-private key pair. " + str(e))
    try:
        public_key = get_public_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PublicKey_Export_Fault_Type,
                                summary='Failed to export public key')
        raise CLIError("Failed to export public key." + str(e))
    try:
        private_key_pem = get_private_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PrivateKey_Export_Fault_Type,
                                summary='Failed to export private key')
        raise CLIError("Failed to export private key." + str(e))

    # Generate request payload
    cc = generate_request_payload(configuration, location, public_key, tags, kubernetes_distro, kubernetes_infra)

    # Create connected cluster resource
    put_cc_response = create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)

    # Install azure-arc agents
    utils.helm_install_release(chart_path, subscription_id, kubernetes_distro, kubernetes_infra, resource_group_name, cluster_name,
                               location, onboarding_tenant_id, http_proxy, https_proxy, no_proxy, proxy_cert, private_key_pem, kube_config,
                               kube_context, no_wait, values_file_provided, values_file, azure_cloud, disable_auto_upgrade,
                               enable_azure_rbac, guard_client_id, guard_client_secret)

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
        telemetry.set_user_fault()
        telemetry.set_exception(exception='Helm environment file not provided', fault_type=consts.Helm_Environment_File_Fault_Type,
                                summary='Helm environment file missing')
        raise CLIError("Helm environment file is required when using Dogfood environment for onboarding the cluster. Please set the environment variable 'HELMVALUESPATH' to point to the file.")

    with open(values_file, 'r') as f:
        try:
            env_dict = yaml.safe_load(f)
        except Exception as e:
            telemetry.set_user_fault()
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Environment_File_Fault_Type,
                                    summary='Problem loading the helm environment file')
            raise CLIError("Problem loading the helm environment file: " + str(e))
        try:
            assert env_dict.get('global').get('azureEnvironment') == 'AZUREDOGFOOD'
            assert env_dict.get('systemDefaultValues').get('azureArcAgents').get('config_dp_endpoint_override')
        except Exception as e:
            telemetry.set_user_fault()
            telemetry.set_exception(exception=e, fault_type=consts.Helm_Environment_File_Fault_Type,
                                    summary='Problem loading the helm environment variables')
            raise CLIError("The required helm environment variables for dogfood onboarding are either not present in the file or incorrectly set. Please check the values 'global.azureEnvironment' and 'systemDefaultValues.azureArcAgents.config_dp_endpoint_override' in the file.")

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
        utils.kubernetes_exception_handler(e, consts.Kubernetes_Connectivity_FaultType, 'Unable to verify connectivity to the Kubernetes cluster',
                                           error_message="If you are using AAD Enabled cluster, verify that you are able to access the cluster. Learn more at https://aka.ms/arc/k8s/onboarding-aad-enabled-clusters")


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
                telemetry.set_user_fault()
                telemetry.set_exception(exception='Helm 3 not found', fault_type=consts.Helm_Version_Fault_Type,
                                        summary='Helm3 not found on the machine')
                raise CLIError("Please install the latest version of Helm. " +
                               "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")
            telemetry.set_user_fault()
            telemetry.set_exception(exception=error_helm_installed.decode("ascii"), fault_type=consts.Helm_Installation_Fault_Type,
                                    summary='Helm3 not installed on the machine')
            raise CLIError(error_helm_installed.decode("ascii"))
    except FileNotFoundError as e:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=consts.Check_HelmInstallation_Fault_Type,
                                summary='Unable to verify helm installation')
        raise CLIError("Helm is not installed or the helm binary is not accessible to the connectedk8s cli. Could be a permission issue." +
                       "Ensure that you have the latest version of Helm installed on your machine and run using admin privilege. " +
                       "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")
    except Exception as e2:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e2, fault_type=consts.Check_HelmInstallation_Fault_Type,
                                summary='Error while verifying helm installation')
        raise CLIError("Error occured while verifying helm installation: " + str(e2))


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
        raise CLIError("Unable to determine helm version: " + error_helm_version.decode("ascii"))
    if "v2" in output_helm_version.decode("ascii"):
        telemetry.set_user_fault()
        telemetry.set_exception(exception='Helm 3 not found', fault_type=consts.Helm_Version_Fault_Type,
                                summary='Helm3 not found on the machine')
        raise CLIError("Helm version 3+ is required. " +
                       "Ensure that you have installed the latest version of Helm. " +
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
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Problem loading the kubeconfig file')
        raise CLIError("Problem loading the kubeconfig file." + str(e))


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
        logger.warning("Error occured while trying to fetch kubernetes distribution.")
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
        logger.warning("Error occured while trying to fetch kubernetes infrastructure.")
        utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Infra_Fault_Type, 'Unable to fetch kubernetes infrastructure',
                                           raise_error=False)
        return "generic"


def generate_request_payload(configuration, location, public_key, tags, kubernetes_distro, kubernetes_infra):
    # Create connected cluster resource object
    aad_profile = ConnectedClusterAADProfile(
        tenant_id="",
        client_app_id="",
        server_app_id=""
    )
    identity = ConnectedClusterIdentity(
        type="SystemAssigned"
    )
    if tags is None:
        tags = {}
    cc = ConnectedCluster(
        location=location,
        identity=identity,
        agent_public_key_certificate=public_key,
        aad_profile=aad_profile,
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
        telemetry.set_user_fault()
        telemetry.set_exception(exception=ex, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Error while fetching details from kubeconfig')
        raise CLIError("Error while fetching details from kubeconfig." + str(ex))
    return kubeconfig_data


def check_aks_cluster(kube_config, kube_context):
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

    if server_address.find(".azmk8s.io:") == -1:
        return False
    else:
        return True


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

    if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and
            configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower()):
        delete_cc_resource(client, resource_group_name, cluster_name, no_wait)
    else:
        telemetry.set_user_fault()
        telemetry.set_exception(exception='Unable to delete connected cluster', fault_type=consts.Bad_DeleteRequest_Fault_Type,
                                summary='The resource cannot be deleted as kubernetes cluster is onboarded with some other resource id')
        raise CLIError("The current context in the kubeconfig file does not correspond " +
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
        raise CLIError("Helm list release failed: " + error_helm_release.decode("ascii"))
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
        utils.arm_exception_handler(e, consts.Delete_ConnectedCluster_Fault_Type, 'Unable to create connected cluster resource')


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
                  disable_proxy=False, kube_config=None, kube_context=None, auto_upgrade=None, azure_rbac=None, guard_client_id=None, guard_client_secret=None):
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
        telemetry.set_user_fault()
        telemetry.set_exception(fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
                                summary='Proxy cert path does not exist')
        raise CLIError(str.format(consts.Proxy_Cert_Path_Does_Not_Exist_Error, proxy_cert))

    proxy_cert = proxy_cert.replace('\\', r'\\\\')

    if https_proxy == "" and http_proxy == "" and no_proxy == "" and proxy_cert == "" and not disable_proxy and not auto_upgrade and (azure_rbac is None):
        raise CLIError(consts.No_Param_Error)

    if (https_proxy or http_proxy or no_proxy or proxy_cert) and disable_proxy:
        raise CLIError(consts.EnableProxy_Conflict_Error)

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

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)

    # Validate enable-azure-rbac
    if (azure_rbac is not None) and (bool(strtobool(azure_rbac))):
        validate.validate_enable_azure_rbac(kubernetes_version, guard_client_id, guard_client_secret)
    
    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        telemetry.set_user_fault()
        raise CLIError("The current helm version is not supported for azure-arc onboarding. Please upgrade helm to a stable version and try again.")

    # Check whether Connected Cluster is present
    if not connected_cluster_exists(client, resource_group_name, cluster_name):
        telemetry.set_user_fault()
        telemetry.set_exception(exception='The connected cluster resource does not exist', fault_type=consts.Resource_Does_Not_Exist_Fault_Type,
                                summary='Connected cluster resource does not exist')
        raise CLIError("The connected cluster resource {} does not exist ".format(cluster_name) +
                       "in the resource group {} ".format(resource_group_name) +
                       "Please onboard the connected cluster using: az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>")

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
    if azure_rbac is not None:
        cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.enabled={}".format(azure_rbac)])
        if bool(strtobool(azure_rbac)):
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.clientId={}".format(guard_client_id)])
            cmd_helm_upgrade.extend(["--set", "systemDefaultValues.guard.clientSecret={}".format(guard_client_secret)])
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
        raise CLIError(str.format(consts.Update_Agent_Failure, error_helm_upgrade.decode("ascii")))

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

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    helm_version = check_helm_version(kube_config, kube_context)
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.HelmVersion': helm_version})

    # Check for faulty pre-release helm versions
    if "3.3.0-rc" in helm_version:
        telemetry.set_user_fault()
        raise CLIError("The current helm version is not supported for azure-arc onboarding. Please upgrade helm to a stable version and try again.")

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
                telemetry.set_user_fault()
                telemetry.set_exception(exception='The provided cluster name and rg correspond to different cluster', fault_type=consts.Upgrade_RG_Cluster_Name_Conflict,
                                        summary='The provided cluster name and resource group name do not correspond to the kubernetes cluster being upgraded.')
                raise CLIError("The provided cluster name and resource group name do not correspond to the kubernetes cluster you are trying to upgrade." +
                               "Please upgrade the cluster, with correct resource group and cluster name, using 'az upgrade agents -g <rg_name> -n <cluster_name>'.")
        else:
            telemetry.set_user_fault()
            telemetry.set_exception(exception='The corresponding CC resource does not exist', fault_type=consts.Corresponding_CC_Resource_Deleted_Fault,
                                    summary='CC resource corresponding to this cluster has been deleted by the customer')
            raise CLIError("There exist no ConnectedCluster resource corresponding to this kubernetes Cluster." +
                           "Please cleanup the helm release first using 'az connectedk8s delete -n <connected-cluster-name> -g <resource-group-name>' and re-onboard the cluster using " +
                           "'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>'")

        auto_update_enabled = configmap.data["AZURE_ARC_AUTOUPDATE"]
        if auto_update_enabled == "true":
            telemetry.set_user_fault()
            telemetry.set_exception(exception='connectedk8s upgrade called when auto-update is set to true', fault_type=consts.Manual_Upgrade_Called_In_Auto_Update_Enabled,
                                    summary='az connectedk8s upgrade to manually upgrade agents and extensions is only supported when auto-upgrade is set to false.')
            raise CLIError("az connectedk8s upgrade to manually upgrade agents and extensions is only supported when auto-upgrade is set to false. " +
                           "Please run az connectedk8s update -n <connected-cluster-name> -g <resource-group-name> --auto-upgrade 'false' before performing manual upgrade")

    else:
        telemetry.set_user_fault()
        telemetry.set_exception(exception="The azure-arc release namespace couldn't be retrieved", fault_type=consts.Release_Namespace_Not_Found,
                                summary="The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc.")
        raise CLIError("The azure-arc release namespace couldn't be retrieved, which implies that the kubernetes cluster has not been onboarded to azure-arc." +
                       "Please run 'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>' to onboard the cluster")

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
        raise CLIError(str.format(consts.Upgrade_Agent_Failure, error_helm_get_values.decode("ascii")))

    output_helm_values = output_helm_values.decode("ascii")

    try:
        existing_user_values = yaml.safe_load(output_helm_values)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Helm_Existing_User_Supplied_Value_Get_Fault,
                                summary='Problem loading the helm existing user supplied values')
        raise CLIError("Problem loading the helm existing user supplied values: " + str(e))

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
        raise CLIError(str.format(consts.Upgrade_Agent_Failure, error_helm_upgrade.decode("ascii")))

    return str.format(consts.Upgrade_Agent_Success, connected_cluster.name)
