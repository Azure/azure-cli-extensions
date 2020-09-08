# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import time
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

from .vendored_sdks.models import ConnectedCluster, ConnectedClusterAADProfile, ConnectedClusterIdentity


logger = get_logger(__name__)

# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def create_connectedk8s(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="", location=None,
                        kube_config=None, kube_context=None, no_wait=False, tags=None):
    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")

    # Setting subscription id
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Send cloud information to telemetry
    send_cloud_telemetry(cmd)

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

    # Checking whether optional extra values file has been provided.
    values_file_provided = False
    values_file = os.getenv('HELMVALUESPATH')
    if (values_file is not None) and (os.path.isfile(values_file)):
        values_file_provided = True
        logger.warning("Values files detected. Reading additional helm parameters from same.")
        # trimming required for windows os
        if (values_file.startswith("'") or values_file.startswith('"')):
            values_file = values_file[1:]
        if (values_file.endswith("'") or values_file.endswith('"')):
            values_file = values_file[:-1]

    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Problem loading the kubeconfig file')
        raise CLIError("Problem loading the kubeconfig file." + str(e))
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    check_kube_connection(configuration)

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)
    kubernetes_distro = get_kubernetes_distro(configuration)

    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

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
                cc = generate_request_payload(configuration, location, public_key, tags)
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
            delete_arc_agents(release_namespace, kube_config, kube_context, configuration)
    else:
        if connected_cluster_exists(client, resource_group_name, cluster_name):
            telemetry.set_user_fault()
            telemetry.set_exception(exception='The connected cluster resource already exists', fault_type=consts.Resource_Already_Exists_Fault_Type,
                                    summary='Connected cluster resource already exists')
            raise CLIError("The connected cluster resource {} already exists ".format(cluster_name) +
                           "in the resource group {} ".format(resource_group_name) +
                           "and corresponds to a different Kubernetes cluster. To onboard this Kubernetes cluster" +
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

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, location, dp_endpoint_dogfood, release_train_dogfood)

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
    cc = generate_request_payload(configuration, location, public_key, tags)

    # Create connected cluster resource
    put_cc_response = create_cc_resource(client, resource_group_name, cluster_name, cc, no_wait)

    # Install azure-arc agents
    helm_install_release(chart_path, subscription_id, kubernetes_distro, resource_group_name, cluster_name,
                         location, onboarding_tenant_id, http_proxy, https_proxy, no_proxy, private_key_pem, kube_config,
                         kube_context, no_wait, values_file_provided, values_file)

    return put_cc_response


def send_cloud_telemetry(cmd):
    cloud_name = cmd.cli_ctx.cloud.name
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AzureCloud': cloud_name})


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


def get_public_key(key_pair):
    pubKey = key_pair.publickey()
    seq = asn1.DerSequence([pubKey.n, pubKey.e])
    enc = seq.encode()
    return b64encode(enc).decode('utf-8')


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


def get_kubernetes_distro(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        if api_response.items:
            labels = api_response.items[0].metadata.labels
            if labels.get("node.openshift.io/os_id") == "rhcos" or labels.get("node.openshift.io/os_id") == "rhel":
                return "openshift"
        return "default"
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Error occured while trying to fetch kubernetes distribution.")
        utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Distro_Fault_Type, 'Unable to fetch kubernetes distribution',
                                           raise_error=False)


def generate_request_payload(configuration, location, public_key, tags):
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
        tags=tags
    )
    return cc


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
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Problem loading the kubeconfig file')
        raise CLIError("Problem loading the kubeconfig file." + str(e))
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
    delete_arc_agents(release_namespace, kube_config, kube_context, configuration)


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


def helm_install_release(chart_path, subscription_id, kubernetes_distro, resource_group_name, cluster_name,
                         location, onboarding_tenant_id, http_proxy, https_proxy, no_proxy, private_key_pem,
                         kube_config, kube_context, no_wait, values_file_provided, values_file):
    cmd_helm_install = ["helm", "upgrade", "--install", "azure-arc", chart_path,
                        "--set", "global.subscriptionId={}".format(subscription_id),
                        "--set", "global.kubernetesDistro={}".format(kubernetes_distro),
                        "--set", "global.resourceGroupName={}".format(resource_group_name),
                        "--set", "global.resourceName={}".format(cluster_name),
                        "--set", "global.location={}".format(location),
                        "--set", "global.tenantId={}".format(onboarding_tenant_id),
                        "--set", "global.httpsProxy={}".format(https_proxy),
                        "--set", "global.httpProxy={}".format(http_proxy),
                        "--set", "global.noProxy={}".format(no_proxy),
                        "--set", "global.onboardingPrivateKey={}".format(private_key_pem),
                        "--set", "systemDefaultValues.spnOnboarding=false",
                        "--output", "json"]
    # To set some other helm parameters through file
    if values_file_provided:
        cmd_helm_install.extend(["-f", values_file])
    if kube_config:
        cmd_helm_install.extend(["--kubeconfig", kube_config])
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])
    if not no_wait:
        cmd_helm_install.extend(["--wait"])
    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        if ('forbidden' in error_helm_install.decode("ascii") or 'timed out waiting for the condition' in error_helm_install.decode("ascii")):
            telemetry.set_user_fault()
        telemetry.set_exception(exception=error_helm_install.decode("ascii"), fault_type=consts.Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        logger.warning("Please check if the azure-arc namespace was deployed and run 'kubectl get pods -n azure-arc' to check if all the pods are in running state. A possible cause for pods stuck in pending state could be insufficient resources on the kubernetes cluster to onboard to arc.")
        raise CLIError("Unable to install helm release: " + error_helm_install.decode("ascii"))


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


def delete_arc_agents(release_namespace, kube_config, kube_context, configuration):
    cmd_helm_delete = ["helm", "delete", "azure-arc", "--namespace", release_namespace]
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
        raise CLIError("Error occured while cleaning up arc agents. " +
                       "Helm release deletion failed: " + error_helm_delete.decode("ascii") +
                       " Please run 'helm delete azure-arc' to ensure that the release is deleted.")
    ensure_namespace_cleanup(configuration)


def ensure_namespace_cleanup(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
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
            logger.warning("Error while retrieving namespace information.")
            utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Namespace_Fault_Type, 'Unable to fetch kubernetes namespace',
                                               raise_error=False)


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long


def update_agents(cmd, client, resource_group_name, cluster_name, https_proxy="", http_proxy="", no_proxy="",
                  kube_config=None, kube_context=None, no_wait=False):
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

    # Checking whether optional extra values file has been provided.
    values_file_provided = False
    values_file = os.getenv('HELMVALUESPATH')
    if (values_file is not None) and (os.path.isfile(values_file)):
        values_file_provided = True
        logger.warning("Values files detected. Reading additional helm parameters from same.")
        # trimming required for windows os
        if (values_file.startswith("'") or values_file.startswith('"')):
            values_file = values_file[1:]
        if (values_file.endswith("'") or values_file.endswith('"')):
            values_file = values_file[:-1]

    # Validate the helm environment file for Dogfood.
    dp_endpoint_dogfood = None
    release_train_dogfood = None
    if cmd.cli_ctx.cloud.endpoints.resource_manager == consts.Dogfood_RMEndpoint:
        dp_endpoint_dogfood, release_train_dogfood = validate_env_file_dogfood(values_file, values_file_provided)

    # Loading the kubeconfig file in kubernetes client configuration
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                summary='Problem loading the kubeconfig file')
        raise CLIError("Problem loading the kubeconfig file." + str(e))
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster.
    # This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters
    # if the user had not logged in.
    check_kube_connection(configuration)

    # Get kubernetes cluster info for telemetry
    kubernetes_version = get_server_version(configuration)
    kubernetes_distro = get_kubernetes_distro(configuration)

    kubernetes_properties = {
        'Context.Default.AzureCLI.KubernetesVersion': kubernetes_version,
        'Context.Default.AzureCLI.KubernetesDistro': kubernetes_distro
    }
    telemetry.add_extension_event('connectedk8s', kubernetes_properties)

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

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        utils.add_helm_repo(kube_config, kube_context)

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else utils.get_helm_registry(cmd, connected_cluster.location, dp_endpoint_dogfood, release_train_dogfood)

    reg_path_array = registry_path.split(':')
    agent_version = reg_path_array[1]

    # Set agent version in registry path
    if connected_cluster.agent_version is not None:
        agent_version = connected_cluster.agent_version
        registry_path = reg_path_array[0] + ":" + connected_cluster.agent_version

    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': agent_version})

    # Get Helm chart path
    chart_path = utils.get_chart_path(registry_path, kube_config, kube_context)

    cmd_helm_upgrade = ["helm", "upgrade", "azure-arc", chart_path,
                        "--reuse-values",
                        "--set", "global.httpsProxy={}".format(https_proxy),
                        "--set", "global.httpProxy={}".format(http_proxy),
                        "--set", "global.noProxy={}".format(no_proxy),
                        "--wait", "--output", "json"]
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
        raise CLIError(str.format(consts.Update_Agent_Failure, error_helm_upgrade.decode("ascii")))

    return str.format(consts.Update_Agent_Success, connected_cluster.name)
