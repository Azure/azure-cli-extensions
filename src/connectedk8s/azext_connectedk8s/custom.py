# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import cf_resource_groups
from azext_connectedk8s._client_factory import _resource_client_factory
from msrest.serialization import TZ_UTC
from dateutil.relativedelta import relativedelta
from knack.log import get_logger
from azure.cli.core.api import get_config_dir
from azure.cli.core.util import sdk_no_wait
from msrestazure.azure_exceptions import CloudError
from kubernetes import client as kube_client, config, watch
from kubernetes.client.rest import ApiException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .vendored_sdks.models import ConnectedCluster, ConnectedClusterAADProfile, ConnectedClusterIdentity, LocationData

import os
import subprocess
from subprocess import Popen, PIPE
import json
import uuid
import datetime
import time
import base64
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from Crypto.Util.number import inverse
from pyasn1.codec.der.encoder import encode as der_encoder
from base64 import b64encode

logger = get_logger(__name__)


def create_connectedk8s(cmd, client, resource_group_name, cluster_name,
                        location=None, kube_config=None, kube_context=None, no_wait=False,
                        location_data_name=None, location_data_country_or_region=None,
                        location_data_district=None, location_data_city=None, tags=None):
    print("Ensure that you have the latest helm version installed before proceeding to avoid unexpected errors.")
    print("This operation might take a while...\n")

    # Checking location data info
    if location_data_name is None:
        if ((location_data_country_or_region is not None) or (location_data_district is not None) or (location_data_city is not None)):
            raise CLIError("--location-data-name is required when providing location data info.")

    # Setting subscription id
    subscription_id = get_subscription_id(cmd.cli_ctx) 

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
        raise CLIError("Problem loading the kubeconfig file." + str(e))
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster. This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters if the user had not logged in.
    check_kube_connection(configuration)
    
    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    check_helm_version(kube_config, kube_context)
    
    # Validate location
    resourceClient = _resource_client_factory(cmd.cli_ctx, subscription_id=subscription_id)
    if location is None:
        try:
            location = resourceClient.resource_groups.get(resource_group_name).location
        except:
            raise CLIError("The provided resource group does not exist. Please provide location to create the Resource Group")

    rp_locations = []
    providerDetails = resourceClient.providers.get('Microsoft.Kubernetes')
    for resourceTypes in providerDetails.resource_types:
        if resourceTypes.resource_type == 'connectedClusters':
            rp_locations = [location.replace(" ", "").lower() for location in resourceTypes.locations]
            if location.lower() not in rp_locations:
                raise CLIError("The connected cluster resource creation is supported only in the following locations: " + ', '.join(map(str, rp_locations)) + ". Please use the --location flag to specify right location.")
            break

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context) 
    if release_namespace is not None:
        # Loading config map
        api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except ApiException as e:
            raise CLIError("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)
        configmap_resource_group_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if connected_cluster_exists(client, configmap_resource_group_name, configmap_cluster_name):
            if (configmap_resource_group_name.lower() == resource_group_name.lower() and configmap_cluster_name.lower() == cluster_name.lower()):
                # Re-put connected cluster
                public_key = client.get(configmap_resource_group_name, configmap_cluster_name).agent_public_key_certificate
                cc = generate_request_payload(configuration, location, public_key, location_data_name, location_data_city, location_data_district, location_data_country_or_region, tags)
                try:
                    return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, cluster_name=cluster_name, connected_cluster=cc)
                except CloudError as ex:
                    raise CLIError(ex)
            else:
                raise CLIError("The kubernetes cluster you are trying to onboard is already onboarded to the resource group '{}' with resource name '{}'.".format(configmap_resource_group_name, configmap_cluster_name))
        else:
            # Cleanup agents and continue with put
            delete_arc_agents(release_namespace, kube_config, kube_context, configuration)
    else:
        if connected_cluster_exists(client, resource_group_name, cluster_name):
            raise CLIError("The connected cluster resource already exists and correspods to a different kubernetes cluster. To onboard this kubernetes cluster to azure, please provide a different resource name or resource group name.")
    
    # Resource group Creation
    if (resource_group_exists(cmd.cli_ctx, resource_group_name, subscription_id) is False):
        resource_group_params = {'location': location}
        try:
            resourceClient.resource_groups.create_or_update(resource_group_name, resource_group_params)
        except Exception as e:
            raise CLIError("Resource Group Creation Failed." + str(e.message))  
    
    # Adding helm repo
    repo_name = os.getenv('HELMREPONAME') if os.getenv('HELMREPONAME') else "azurearcfork8s"
    repo_url = os.getenv('HELMREPOURL') if os.getenv('HELMREPOURL') else "https://azurearcfork8s.azurecr.io/helm/v1/repo"
    cmd_helm_repo = ["helm", "repo", "add", repo_name, repo_url, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_repo.extend(["--kube-context", kube_context])
    response_helm_repo = subprocess.Popen(cmd_helm_repo, stdout=PIPE, stderr=PIPE)
    output_helm_repo, error_helm_repo = response_helm_repo.communicate()
    if response_helm_repo.returncode != 0:
        raise CLIError("Helm unable to add repository: " + error_helm_repo.decode("ascii"))

    # Generate public-private key pair
    key_pair = RSA.generate(4096)
    public_key = get_public_key(key_pair)
    private_key_pem = get_private_key(key_pair)

    # Helm Install
    chart_path = os.getenv('HELMCHART') if  os.getenv('HELMCHART') else "azurearcfork8s/azure-arc-k8sagents"
    cmd_helm_install = ["helm", "install", "azure-arc", chart_path, "--set", "global.subscriptionId={}".format(subscription_id), "--set", "global.resourceGroupName={}".format(resource_group_name), "--set", "global.resourceName={}".format(cluster_name), "--set", "global.location={}".format(location), "--set", "global.tenantId={}".format(onboarding_tenant_id), "--set", "global.connectPrivateKey={}".format(private_key_pem), "--set", "systemDefaultValues.spnOnboarding=false", "--kubeconfig", kube_config, "--output", "json"]
    if kube_context:
        cmd_helm_install.extend(["--kube-context", kube_context])
    response_helm_install = subprocess.Popen(cmd_helm_install, stdout=PIPE, stderr=PIPE)
    output_helm_install, error_helm_install = response_helm_install.communicate()
    if response_helm_install.returncode != 0:
        raise CLIError("Unable to install helm release: " + error_helm_install.decode("ascii"))

    # Create connected cluster resource
    cc = generate_request_payload(configuration, location, public_key, location_data_name, location_data_city, location_data_district, location_data_country_or_region, tags)
    try:
        put_cc_response = sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, cluster_name=cluster_name, connected_cluster=cc)
        if no_wait:
            return put_cc_response
    except CloudError as ex:
        raise CLIError(ex)

    # Getting total number of pods scheduled to run in azure-arc namespace
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    pod_dict = get_pod_dict(api_instance)

    # Checking azure-arc pod statuses
    check_pod_status(pod_dict)

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
        api_response = api_instance.get_api_resources()
    except ApiException as e:
        print("Exception when calling NetworkingV1Api->get_api_resources: %s\n" % e)
        raise CLIError("If you are using AAD Enabled cluster, check if you have logged in to the cluster properly and try again")


def check_helm_install(kube_config, kube_context):
    cmd_helm_installed = ["helm", "--kubeconfig", kube_config, "--debug"]
    if kube_context:
        cmd_helm_installed.extend(["--kube-context", kube_context])
    try:
        response_helm_installed = subprocess.Popen(cmd_helm_installed, stdout=PIPE, stderr=PIPE)
        output_helm_installed, error_helm_installed = response_helm_installed.communicate()
        if response_helm_installed.returncode != 0:
            if "unknown flag" in error_helm_installed.decode("ascii"):
                raise CLIError("Please install the latest version of helm")
            raise CLIError(error_helm_installed.decode("ascii"))
    except FileNotFoundError:
        raise CLIError("Helm is not installed or requires elevated permissions. Please ensure that you have the latest version of helm installed on your machine.")
    except subprocess.CalledProcessError as e2:
        e2.output = e2.output.decode("ascii")
        print(e2.output)


def check_helm_version(kube_config, kube_context):
    cmd_helm_version = ["helm", "version", "--short", "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_version.extend(["--kube-context", kube_context])
    response_helm_version = subprocess.Popen(cmd_helm_version, stdout=PIPE, stderr=PIPE)
    output_helm_version, error_helm_version = response_helm_version.communicate()
    if response_helm_version.returncode != 0:
        raise CLIError("Unable to determine helm version: " + error_helm_version.decode("ascii"))
    else:
        if "v2" in output_helm_version.decode("ascii"):
            raise CLIError("Please install the latest version of helm and then try again")


def resource_group_exists(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    try:
        rg = groups.get(resource_group_name)
        return True
    except:
        return False

def connected_cluster_exists(client, resource_group_name, cluster_name):
    try:
        client.get(resource_group_name, cluster_name)
    except Exception as ex:
        if (('was not found' in str(ex)) or ('could not be found' in str(ex))):
            return False
        else:
            raise CLIError("Unable to determine if the connected cluster resource exists. " + str(ex))
    return True


def get_public_key(key_pair):
    pubKey = key_pair.publickey()
    seq = asn1.DerSequence([pubKey.n, pubKey.e])
    enc = seq.encode()
    return b64encode(enc).decode('utf-8')


def get_private_key(key_pair):
    privKey_DER = key_pair.exportKey(format='DER')
    return PEM.encode(privKey_DER, "RSA PRIVATE KEY")


def get_node_count(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.list_node()
        return len(api_response.items)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_node: %s\n" % e)


def get_server_version(configuration):
    api_instance = kube_client.VersionApi(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.get_code()
        return api_response.git_version
    except ApiException as e:
        print("Exception when calling VersionApi->get_code: %s\n" % e)


def get_agent_version(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        return api_response.data["AZURE_ARC_AGENT_VERSION"]
    except ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)


def generate_request_payload(configuration, location, public_key, location_data_name, location_data_city, location_data_district, location_data_country_or_region, tags):
    # Fetch cluster info
    total_node_count = get_node_count(configuration)
    kubernetes_version = get_server_version(configuration)
    azure_arc_agent_version = get_agent_version(configuration)

    # Create connected cluster resource object
    aad_profile = ConnectedClusterAADProfile(
        tenant_id="",
        client_app_id="",
        server_app_id=""
    )
    identity = ConnectedClusterIdentity(
        type="SystemAssigned"
    )
    location_data = LocationData(
        name=location_data_name,
        city=location_data_city,
        district=location_data_district,
        country_or_region=location_data_country_or_region
    )
    cc = ConnectedCluster(
        location=location,
        identity=identity,
        agent_public_key_certificate=public_key,
        aad_profile=aad_profile,
        kubernetes_version=kubernetes_version,
        total_node_count=total_node_count,
        agent_version=azure_arc_agent_version,
        tags=tags
    )
    if location_data_name:
        cc.location_data=location_data
    return cc


def get_pod_dict(api_instance):
    pod_dict = {}
    timeout = time.time() + 60
    while(not pod_dict):
        try:
            api_response = api_instance.list_namespaced_pod('azure-arc')
            for pod in api_response.items:
                pod_dict[pod.metadata.name] = 0
            return pod_dict
        except ApiException as e:
            logger.warning("Exception when calling get pods: %s\n" % e)
            time.sleep(5)
        if time.time()>timeout:
            logger.warning("Unable to fetch azure-arc agent pods.")
            return pod_dict


def check_pod_status(pod_dict):
    v1 = kube_client.CoreV1Api()
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, namespace='azure-arc', timeout_seconds=60):
        pod_status = event['raw_object'].get('status')
        pod_name = event['object'].metadata.name
        #print(pod_status)
        if pod_status.get('containerStatuses'):
            for container in pod_status.get('containerStatuses'):
                if container.get('name') in pod_name:
                    if container.get('state').get('running') is None:
                        pod_dict[pod_name] = 0
                    else:
                        pod_dict[pod_name] = 1
                    if container.get('state').get('terminated') is not None:
                        logger.warning("The pod {} was terminated. Please ensure it is in running state once the operation completes. Run 'kubectl get pods -n azure-arc' to check the pod status.".format(container.get('name')))
        if all(ele == 1 for ele in list(pod_dict.values())):
            return
    logger.warning("The pods were unable to start before timeout. Please run 'kubectl get pods -n azure-arc' to ensure if the pods are in running state.")


def get_connectedk8s(cmd, client, resource_group_name, cluster_name):
    return client.get(resource_group_name, cluster_name)


def list_connectedk8s(cmd, client, resource_group_name=None):
    if resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def delete_connectedk8s(cmd, client, resource_group_name, cluster_name, kube_config=None, kube_context=None):
    print("Ensure that you have the latest helm version installed before proceeding to avoid unexpected errors.")
    print("This operation might take a while ...\n")

    # Setting kubeconfig
    kube_config = set_kube_config(kube_config)

    # Removing quotes from kubeconfig path. This is necessary for windows OS.
    trim_kube_config(kube_config)

    # Loading the kubeconfig file in kubernetes client configuration
    try:
        config.load_kube_config(config_file=kube_config, context=kube_context)
    except Exception as e:
        print("Problem loading the kubeconfig file." + str(e))
        raise CLIError(e)
    configuration = kube_client.Configuration()

    # Checking the connection to kubernetes cluster. This check was added to avoid large timeouts when connecting to AAD Enabled AKS clusters if the user had not logged in.
    check_kube_connection(configuration)

    # Checking helm installation
    check_helm_install(kube_config, kube_context)

    # Check helm version
    check_helm_version(kube_config, kube_context)

    # Check Release Existance
    release_namespace = get_release_namespace(kube_config, kube_context)
    if release_namespace is None:
        delete_cc_resource(client, resource_group_name, cluster_name)
        return 

    # Loading config map
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
    except ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)

    if (configmap.data["AZURE_RESOURCE_GROUP"].lower() == resource_group_name.lower() and configmap.data["AZURE_RESOURCE_NAME"].lower() == cluster_name.lower()):
        delete_cc_resource(client, resource_group_name, cluster_name)
    else:
        raise CLIError("The kube config does not correspond to the connected cluster resource provided. Agents installed on this cluster correspond to the resource group name '{}' and resource name '{}'.".format(configmap.data["AZURE_RESOURCE_GROUP"], configmap.data["AZURE_RESOURCE_NAME"]))

    # Deleting the azure-arc agents
    delete_arc_agents(release_namespace, kube_config, kube_context, configuration)


def get_release_namespace(kube_config, kube_context):
    cmd_helm_release = ["helm", "list", "-a", "--all-namespaces", "--output", "json", "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_release.extend(["--kube-context", kube_context])
    response_helm_release = subprocess.Popen(cmd_helm_release, stdout=PIPE, stderr=PIPE)
    output_helm_release, error_helm_release = response_helm_release.communicate()
    if response_helm_release.returncode != 0:
        raise CLIError("Helm list release failed: " + error_helm_release.decode("ascii"))
    else:
        output_helm_release = output_helm_release.decode("ascii")
        output_helm_release = json.loads(output_helm_release)
        for release in output_helm_release:
            if release['name'] == 'azure-arc':
                return release['namespace']
    return None


def delete_cc_resource(client, resource_group_name, cluster_name):
    try:
        client.delete(resource_group_name, cluster_name)
    except CloudError as ex:
        raise CLIError(ex)


def delete_arc_agents(release_namespace, kube_config, kube_context, configuration):
    cmd_helm_delete = ["helm", "delete", "azure-arc", "--namespace", release_namespace, "--kubeconfig", kube_config]
    if kube_context:
        cmd_helm_delete.extend(["--kube-context", kube_context])
    response_helm_delete = subprocess.Popen(cmd_helm_delete, stdout=PIPE, stderr=PIPE)
    output_helm_delete, error_helm_delete = response_helm_delete.communicate()
    if response_helm_delete.returncode != 0:
        raise CLIError("Error occured while cleaning up arc agents. Helm release deletion failed: " + error_helm_delete.decode("ascii"))
    ensure_namespace_cleanup(configuration)


def ensure_namespace_cleanup(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    timeout = time.time() + 120
    while(True):
        if time.time()>timeout:
            logger.warning("Namespace 'azure-arc' still in terminating state")
            return
        try:
            api_response = api_instance.list_namespace(field_selector='metadata.name=azure-arc')
            if len(api_response.items) == 0:
                return
            else:
                time.sleep(5)
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False
