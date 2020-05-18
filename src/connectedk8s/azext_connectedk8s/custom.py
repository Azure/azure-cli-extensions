# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import time
import subprocess
from subprocess import Popen, PIPE
from base64 import b64encode
import requests

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait
from azure.cli.core._profile import Profile
from azure.cli.core import telemetry
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from msrestazure.azure_exceptions import CloudError
from kubernetes import client as kube_client, config, watch  # pylint: disable=import-error
from Crypto.IO import PEM  # pylint: disable=import-error
from Crypto.PublicKey import RSA  # pylint: disable=import-error
from Crypto.Util import asn1  # pylint: disable=import-error

from .vendored_sdks.models import ConnectedCluster, ConnectedClusterAADProfile, ConnectedClusterIdentity


logger = get_logger(__name__)

Invalid_Location_Fault_Type = 'location-validation-error'
Load_Kubeconfig_Fault_Type = 'kubeconfig-load-error'
Read_ConfigMap_Fault_Type = 'configmap-read-error'
Create_ConnectedCluster_Fault_Type = 'connected-cluster-create-error'
Delete_ConnectedCluster_Fault_Type = 'connected-cluster-delete-error'
Bad_DeleteRequest_Fault_Type = 'bad-delete-request-error'
Cluster_Already_Onboarded_Fault_Type = 'cluster-already-onboarded-error'
Resource_Already_Exists_Fault_Type = 'resource-already-exists-error'
Create_ResourceGroup_Fault_Type = 'resource-group-creation-error'
Add_HelmRepo_Fault_Type = 'helm-repo-add-error'
List_HelmRelease_Fault_Type = 'helm-list-release-error'
KeyPair_Generate_Fault_Type = 'keypair-generation-error'
PublicKey_Export_Fault_Type = 'publickey-export-error'
PrivateKey_Export_Fault_Type = 'privatekey-export-error'
Install_HelmRelease_Fault_Type = 'helm-release-install-error'
Delete_HelmRelease_Fault_Type = 'helm-release-delete-error'
Check_PodStatus_Fault_Type = 'check-pod-status-error'
Kubernetes_Connectivity_FaultType = 'kubernetes-cluster-connection-error'
Helm_Version_Fault_Type = 'helm-not-updated-error'
Check_HelmVersion_Fault_Type = 'helm-version-check-error'
Helm_Installation_Fault_Type = 'helm-not-installed-error'
Check_HelmInstallation_Fault_Type = 'check-helm-installed-error'
Get_HelmRegistery_Path_Fault_Type = 'helm-registry-path-fetch-error'
Pull_HelmChart_Fault_Type = 'helm-chart-pull-error'
Export_HelmChart_Fault_Type = 'helm-chart-export-error'
Get_Kubernetes_Version_Fault_Type = 'kubernetes-get-version-error'
Get_Kubernetes_Distro_Fault_Type = 'kubernetes-get-distribution-error'


# pylint:disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=line-too-long
def create_connectedk8s(cmd, client, resource_group_name, cluster_name, location=None,
                        kube_config=None, kube_context=None, no_wait=False, tags=None):
    logger.warning("Ensure that you have the latest helm version installed before proceeding.")
    logger.warning("This operation might take a while...\n")

    # Setting subscription id
    subscription_id = get_subscription_id(cmd.cli_ctx)

    # Setting user profile
    profile = Profile(cli_ctx=cmd.cli_ctx)

    # Fetching Tenant Id
    graph_client = _graph_client_factory(cmd.cli_ctx)
    onboarding_tenant_id = graph_client.config.tenant_id

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Removing quotes from kubeconfig path. This is necessary for windows OS.
    trim_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=Load_Kubeconfig_Fault_Type,
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

    # Validate location
    rp_locations = []
    resourceClient = _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)
    providerDetails = resourceClient.providers.get('Microsoft.Kubernetes')
    for resourceTypes in providerDetails.resource_types:
        if resourceTypes.resource_type == 'connectedClusters':
            rp_locations = [location.replace(" ", "").lower() for location in resourceTypes.locations]
            if location.lower() not in rp_locations:
                telemetry.set_user_fault()
                telemetry.set_exception(exception='Location not supported', fault_type=Invalid_Location_Fault_Type,
                                        summary='Provided location is not supported for creating connected clusters')
                raise CLIError("Connected cluster resource creation is supported only in the following locations: " +
                               ', '.join(map(str, rp_locations)) +
                               ". Use the --location flag to specify one of these locations.")
            break

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context)
    if release_namespace is not None:
        # Loading config map
        api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            telemetry.set_exception(exception=e, fault_type=Read_ConfigMap_Fault_Type,
                                    summary='Unable to read ConfigMap')
            raise CLIError("Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: %s\n" % e)
        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                # Re-put connected cluster
                public_key = client.get(configmap_rg_name,
                                        configmap_cluster_name).agent_public_key_certificate
                cc = generate_request_payload(configuration, location, public_key, tags)
                try:
                    return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name,
                                       cluster_name=cluster_name, connected_cluster=cc)
                except CloudError as ex:
                    telemetry.set_exception(exception=ex, fault_type=Create_ConnectedCluster_Fault_Type,
                                            summary='Unable to create connected cluster resource')
                    raise CLIError(ex)
            else:
                telemetry.set_user_fault()
                telemetry.set_exception(exception='The kubernetes cluster is already onboarded', fault_type=Cluster_Already_Onboarded_Fault_Type,
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
            telemetry.set_exception(exception='The connected cluster resource already exists', fault_type=Resource_Already_Exists_Fault_Type,
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
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=Create_ResourceGroup_Fault_Type,
                                    summary='Failed to create the resource group')
            raise CLIError("Failed to create the resource group {} :".format(resource_group_name) + str(e))

    # Adding helm repo
    if os.getenv('HELMREPONAME') and os.getenv('HELMREPOURL'):
        repo_name = os.getenv('HELMREPONAME')
        repo_url = os.getenv('HELMREPOURL')
        cmd_helm_repo = ["helm", "repo", "add", repo_name, repo_url, "--kubeconfig", kube_config]
        if kube_context:
            cmd_helm_repo.extend(["--kube-context", kube_context])
        response_helm_repo = Popen(cmd_helm_repo, stdout=PIPE, stderr=PIPE)
        _, error_helm_repo = response_helm_repo.communicate()
        if response_helm_repo.returncode != 0:
            telemetry.set_exception(exception=error_helm_repo.decode("ascii"), fault_type=Add_HelmRepo_Fault_Type,
                                    summary='Failed to add helm repository')
            raise CLIError("Unable to add repository {} to helm: ".format(repo_url) + error_helm_repo.decode("ascii"))

    # Retrieving Helm chart OCI Artifact location
    registry_path = os.getenv('HELMREGISTRY') if os.getenv('HELMREGISTRY') else get_helm_registry(profile, location)

    # Get azure-arc agent version for telemetry
    azure_arc_agent_version = registry_path.split(':')[1]
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AgentVersion': azure_arc_agent_version})

    # Pulling helm chart from registry
    os.environ['HELM_EXPERIMENTAL_OCI'] = '1'
    pull_helm_chart(registry_path, kube_config, kube_context)

    # Exporting helm chart
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')
    export_helm_chart(registry_path, chart_export_path, kube_config, kube_context)

    # Generate public-private key pair
    try:
        key_pair = RSA.generate(4096)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=KeyPair_Generate_Fault_Type,
                                summary='Failed to generate public-private key pair')
        raise CLIError("Failed to generate public-private key pair. " + str(e))
    try:
        public_key = get_public_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=PublicKey_Export_Fault_Type,
                                summary='Failed to export public key')
        raise CLIError("Failed to export public key." + str(e))
    try:
        private_key_pem = get_private_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=PrivateKey_Export_Fault_Type,
                                summary='Failed to export private key')
        raise CLIError("Failed to export private key." + str(e))

    # Helm Install
    helm_chart_path = os.path.join(chart_export_path, 'azure-arc-k8sagents')
    chart_path = os.getenv('HELMCHART') if os.getenv('HELMCHART') else helm_chart_path
    cmd_helm_install = ["helm", "upgrade", "--install", "azure-arc", chart_path,
                        "--set", "global.subscriptionId={}".format(subscription_id),
                        "--set", "global.kubernetesDistro={}".format(kubernetes_distro),
                        "--set", "global.resourceGroupName={}".format(resource_group_name),
                        "--set", "global.resourceName={}".format(cluster_name),
                        "--set", "global.location={}".format(location),
                        "--set", "global.tenantId={}".format(onboarding_tenant_id),
                        "--set", "global.onboardingPrivateKey={}".format(private_key_pem),
                        "--set", "systemDefaultValues.spnOnboarding=false",
                        "--kubeconfig", kube_config, "--output", "json"]
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])
    response_helm_install = Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    _, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        telemetry.set_exception(exception=error_helm_install.decode("ascii"), fault_type=Install_HelmRelease_Fault_Type,
                                summary='Unable to install helm release')
        raise CLIError("Unable to install helm release: " + error_helm_install.decode("ascii"))

    # Create connected cluster resource
    cc = generate_request_payload(configuration, location, public_key, tags)
    try:
        put_cc_response = sdk_no_wait(no_wait, client.create,
                                      resource_group_name=resource_group_name,
                                      cluster_name=cluster_name, connected_cluster=cc)
        if no_wait:
            return put_cc_response
    except CloudError as ex:
        telemetry.set_exception(exception=ex, fault_type=Create_ConnectedCluster_Fault_Type,
                                summary='Unable to create connected cluster resource')
        raise CLIError(ex)

    # Getting total number of pods scheduled to run in azure-arc namespace
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    pod_dict = get_pod_dict(api_instance)

    # Checking azure-arc pod statuses
    try:
        check_pod_status(pod_dict)
    except Exception as e:  # pylint: disable=broad-except
        telemetry.set_exception(exception=e, fault_type=Check_PodStatus_Fault_Type,
                                summary='Failed to check arc agent pods statuses')
        logger.warning("Failed to check arc agent pods statuses: %s", e)

    return put_cc_response


def set_kube_config(kube_config):
    if kube_config is None:
        kube_config = os.getenv('KUBECONFIG')
        if kube_config is None:
            kube_config = os.path.join(os.path.expanduser('~'), '.kube', 'config')
    return kube_config


def trim_kube_config(kube_config):
    if (kube_config.startswith("'") or kube_config.startswith('"')):
        kube_config = kube_config[1:]
    if (kube_config.endswith("'") or kube_config.endswith('"')):
        kube_config = kube_config[:-1]


def check_kube_connection(configuration):
    api_instance = kube_client.NetworkingV1Api(kube_client.ApiClient(configuration))
    try:
        api_instance.get_api_resources()
    except Exception as e:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=Kubernetes_Connectivity_FaultType,
                                summary='Unable to verify connectivity to the Kubernetes cluster')
        logger.warning("Unable to verify connectivity to the Kubernetes cluster: %s\n", e)
        raise CLIError("If you are using AAD Enabled cluster, " +
                       "verify that you are able to access the cluster. Learn more at " +
                       "https://aka.ms/arc/k8s/onboarding-aad-enabled-clusters")


def check_helm_install(kube_config, kube_context):
    cmd_helm_installed = ["helm", "--kubeconfig", kube_config, "--debug"]
    if kube_context:
        cmd_helm_installed.extend(["--kube-context", kube_context])
    try:
        response_helm_installed = Popen(cmd_helm_installed, stdout=PIPE, stderr=PIPE)
        _, error_helm_installed = response_helm_installed.communicate()
        if response_helm_installed.returncode != 0:
            if "unknown flag" in error_helm_installed.decode("ascii"):
                telemetry.set_user_fault()
                telemetry.set_exception(exception='Helm 3 not found', fault_type=Helm_Version_Fault_Type,
                                        summary='Helm3 not found on the machine')
                raise CLIError("Please install the latest version of Helm. " +
                               "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")
            telemetry.set_user_fault()
            telemetry.set_exception(exception=error_helm_installed.decode("ascii"), fault_type=Helm_Installation_Fault_Type,
                                    summary='Helm3 not installed on the machine')
            raise CLIError(error_helm_installed.decode("ascii"))
    except FileNotFoundError as e:
        telemetry.set_exception(exception=e, fault_type=Check_HelmInstallation_Fault_Type,
                                summary='Unable to verify helm installation')
        raise CLIError("Helm is not installed or requires elevated permissions. " +
                       "Ensure that you have the latest version of Helm installed on your machine. " +
                       "Learn more at https://aka.ms/arc/k8s/onboarding-helm-install")
    except subprocess.CalledProcessError as e2:
        e2.output = e2.output.decode("ascii")
        print(e2.output)


def check_helm_version(kube_config, kube_context):
    cmd_helm_version = ["helm", "version", "--short", "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_version.extend(["--kube-context", kube_context])
    response_helm_version = Popen(cmd_helm_version, stdout=PIPE, stderr=PIPE)
    output_helm_version, error_helm_version = response_helm_version.communicate()
    if response_helm_version.returncode != 0:
        telemetry.set_exception(exception=error_helm_version.decode('ascii'), fault_type=Check_HelmVersion_Fault_Type,
                                summary='Unable to determine helm version')
        raise CLIError("Unable to determine helm version: " + error_helm_version.decode("ascii"))
    if "v2" in output_helm_version.decode("ascii"):
        telemetry.set_user_fault()
        telemetry.set_exception(exception='Helm 3 not found', fault_type=Helm_Version_Fault_Type,
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
    except Exception as ex:
        if (('was not found' in str(ex)) or ('could not be found' in str(ex))):
            return False
        raise CLIError("Unable to determine if the connected cluster resource exists. " + str(ex))
    return True


def get_helm_registry(profile, location):
    cred, _, _ = profile.get_login_credentials(
        resource='https://management.core.windows.net/')
    token = cred._token_retriever()[2].get('accessToken')  # pylint: disable=protected-access

    get_chart_location_url = "https://{}.dp.kubernetesconfiguration.azure.com/{}/GetLatestHelmPackagePath?api-version=2019-11-01-preview".format(location, 'azure-arc-k8sagents')
    query_parameters = {}
    query_parameters['releaseTrain'] = os.getenv('RELEASETRAIN') if os.getenv('RELEASETRAIN') else 'stable'
    header_parameters = {}
    header_parameters['Authorization'] = "Bearer {}".format(str(token))
    try:
        response = requests.post(get_chart_location_url, params=query_parameters, headers=header_parameters)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=Get_HelmRegistery_Path_Fault_Type,
                                summary='Error while fetching helm chart registry path')
        raise CLIError("Error while fetching helm chart registry path: " + str(e))
    if response.status_code == 200:
        return response.json().get('repositoryPath')
    telemetry.set_exception(exception=str(response.json()), fault_type=Get_HelmRegistery_Path_Fault_Type,
                            summary='Error while fetching helm chart registry path')
    raise CLIError("Error while fetching helm chart registry path: {}".format(str(response.json())))


def pull_helm_chart(registry_path, kube_config, kube_context):
    cmd_helm_chart_pull = ["helm", "chart", "pull", registry_path, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_chart_pull.extend(["--kube-context", kube_context])
    response_helm_chart_pull = subprocess.Popen(cmd_helm_chart_pull, stdout=PIPE, stderr=PIPE)
    _, error_helm_chart_pull = response_helm_chart_pull.communicate()
    if response_helm_chart_pull.returncode != 0:
        telemetry.set_exception(exception=error_helm_chart_pull.decode("ascii"), fault_type=Pull_HelmChart_Fault_Type,
                                summary='Unable to pull helm chart from the registry')
        raise CLIError("Unable to pull helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_pull.decode("ascii"))


def export_helm_chart(registry_path, chart_export_path, kube_config, kube_context):
    chart_export_path = os.path.join(os.path.expanduser('~'), '.azure', 'AzureArcCharts')
    cmd_helm_chart_export = ["helm", "chart", "export", registry_path, "--destination", chart_export_path, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_chart_export.extend(["--kube-context", kube_context])
    response_helm_chart_export = subprocess.Popen(cmd_helm_chart_export, stdout=PIPE, stderr=PIPE)
    _, error_helm_chart_export = response_helm_chart_export.communicate()
    if response_helm_chart_export.returncode != 0:
        telemetry.set_exception(exception=error_helm_chart_export.decode("ascii"), fault_type=Export_HelmChart_Fault_Type,
                                summary='Unable to export helm chart from the registry')
        raise CLIError("Unable to export helm chart from the registry '{}': ".format(registry_path) + error_helm_chart_export.decode("ascii"))


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
        telemetry.set_exception(exception=e, fault_type=Get_Kubernetes_Version_Fault_Type,
                                summary='Unable to fetch kubernetes version')
        logger.warning("Unable to fetch kubernetes version: %s\n", e)


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
        telemetry.set_exception(exception=e, fault_type=Get_Kubernetes_Distro_Fault_Type,
                                summary='Unable to fetch kubernetes distribution')
        logger.warning("Exception while trying to fetch kubernetes distribution: %s\n", e)


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


def get_pod_dict(api_instance):
    pod_dict = {}
    timeout = time.time() + 60
    while not pod_dict:
        try:
            api_response = api_instance.list_namespaced_pod('azure-arc')
            for pod in api_response.items:
                pod_dict[pod.metadata.name] = 0
            return pod_dict
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error occurred when retrieving pod information: %s", e)
            time.sleep(5)
        if time.time() > timeout:
            logger.warning("Unable to fetch azure-arc agent pods.")
            return pod_dict


def check_pod_status(pod_dict):
    v1 = kube_client.CoreV1Api()
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, namespace='azure-arc', timeout_seconds=360):
        pod_status = event['raw_object'].get('status')
        pod_name = event['object'].metadata.name
        if pod_status.get('containerStatuses'):
            for container in pod_status.get('containerStatuses'):
                if container.get('state').get('running') is None:
                    pod_dict[pod_name] = 0
                    break
                else:
                    pod_dict[pod_name] = 1
                if container.get('state').get('terminated') is not None:
                    logger.warning("%s%s%s", "The pod {} was terminated. ".format(container.get('name')),
                                   "Please ensure it is in running state once the operation completes. ",
                                   "Run 'kubectl get pods -n azure-arc' to check the pod status.")
        if all(ele == 1 for ele in list(pod_dict.values())):
            return
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.ExitStatus': 'Timedout'})
    logger.warning("%s%s", 'The pods were unable to start before timeout. ',
                   'Please run "kubectl get pods -n azure-arc" to ensure if the pods are in running state.')


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

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Removing quotes from kubeconfig path. This is necessary for windows OS.
    trim_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        telemetry.set_user_fault()
        telemetry.set_exception(exception=e, fault_type=Load_Kubeconfig_Fault_Type,
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
    if release_namespace is None:
        delete_cc_resource(client, resource_group_name, cluster_name, no_wait)
        return

    # Loading config map
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
    except Exception as e:  # pylint: disable=broad-except
        telemetry.set_exception(exception=e, fault_type=Read_ConfigMap_Fault_Type,
                                summary='Unable to read ConfigMap')
        raise CLIError("Unable to read ConfigMap 'azure-clusterconfig' in 'azure-arc' namespace: %s\n" % e)

    if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and
            configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower()):
        delete_cc_resource(client, resource_group_name, cluster_name, no_wait)
    else:
        telemetry.set_user_fault()
        telemetry.set_exception(exception='Unable to delete connected cluster', fault_type=Bad_DeleteRequest_Fault_Type,
                                summary='The resource cannot be deleted as kubernetes cluster is onboarded with some other resource id')
        raise CLIError("The current context in the kubeconfig file does not correspond " +
                       "to the connected cluster resource specified. Agents installed on this cluster correspond " +
                       "to the resource group name '{}' ".format(configmap.data["AZURE_RESOURCE_GROUP"]) +
                       "and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_NAME"]))

    # Deleting the azure-arc agents
    delete_arc_agents(release_namespace, kube_config, kube_context, configuration)


def get_release_namespace(kube_config, kube_context):
    cmd_helm_release = ["helm", "list", "-a", "--all-namespaces", "--output", "json", "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_release.extend(["--kube-context", kube_context])
    response_helm_release = Popen(cmd_helm_release, stdout=PIPE, stderr=PIPE)
    output_helm_release, error_helm_release = response_helm_release.communicate()
    if response_helm_release.returncode != 0:
        telemetry.set_exception(exception=error_helm_release.decode("ascii"), fault_type=List_HelmRelease_Fault_Type,
                                summary='Unable to list helm release')
        raise CLIError("Helm list release failed: " + error_helm_release.decode("ascii"))
    output_helm_release = output_helm_release.decode("ascii")
    output_helm_release = json.loads(output_helm_release)
    for release in output_helm_release:
        if release['name'] == 'azure-arc':
            return release['namespace']
    return None


def delete_cc_resource(client, resource_group_name, cluster_name, no_wait):
    try:
        sdk_no_wait(no_wait, client.delete,
                    resource_group_name=resource_group_name,
                    cluster_name=cluster_name)
    except CloudError as ex:
        telemetry.set_exception(exception=ex, fault_type=Delete_ConnectedCluster_Fault_Type,
                                summary='Unable to create connected cluster resource')
        raise CLIError(ex)


def delete_arc_agents(release_namespace, kube_config, kube_context, configuration):
    cmd_helm_delete = ["helm", "delete", "azure-arc", "--namespace", release_namespace, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])
    response_helm_delete = Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
    _, error_helm_delete = response_helm_delete.communicate()
    if response_helm_delete.returncode != 0:
        telemetry.set_exception(exception=error_helm_delete.decode("ascii"), fault_type=Delete_HelmRelease_Fault_Type,
                                summary='Unable to delete helm release')
        raise CLIError("Error occured while cleaning up arc agents. " +
                       "Helm release deletion failed: " + error_helm_delete.decode("ascii"))
    ensure_namespace_cleanup(configuration)


def ensure_namespace_cleanup(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    timeout = time.time() + 120
    while True:
        if time.time() > timeout:
            logger.warning("Namespace 'azure-arc' still in terminating state")
            return
        try:
            api_response = api_instance.list_namespace(field_selector='metadata.name=azure-arc')
            if api_response.items:
                return
            time.sleep(5)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Exception while retrieving 'azure-arc' namespace: %s\n", e)


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance
