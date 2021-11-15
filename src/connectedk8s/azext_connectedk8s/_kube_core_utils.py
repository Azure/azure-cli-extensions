# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

from knack.log import get_logger
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ClientRequestError, ArgumentUsageError
from azext_connectedk8s._helm_core_utils import HelmCoreUtils
import azext_connectedk8s._constants as consts
import azext_connectedk8s._kube_utils as kube_utils
import azext_connectedk8s._connected_cluster_utils as cc_utils
from kubernetes import client as kube_client

logger = get_logger(__name__)


def ensure_namespace_cleanup(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    timeout = time.time() + 180
    while True:
        if time.time() > timeout:
            telemetry.set_user_fault()
            logger.warning("Namespace 'azure-arc' still in terminating state. Please ensure" +
                           " that you delete the 'azure-arc' namespace before onboarding" +
                           " the cluster again.")
            return
        try:
            api_response = api_instance.list_namespace(field_selector='metadata.name=azure-arc')
            if not api_response.items:
                return
            time.sleep(5)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error while retrieving namespace information: " + str(e))
            kube_utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Namespace_Fault_Type,
                                                    'Unable to fetch kubernetes namespace',
                                                    raise_error=False)


def try_list_node_fix():
    try:
        from kubernetes.client.models.v1_container_image import V1ContainerImage

        def names(self, names):
            self._names = names

        V1ContainerImage.names = V1ContainerImage.names.setter(names)
    except Exception as ex: # pylint: disable=broad-except
        logger.debug("Error while trying to monkey patch the fix for list_node(): {}".format(str(ex)))


def check_kube_connection(configuration):
    api_instance = kube_client.NetworkingV1Api(kube_client.ApiClient(configuration))
    try:
        api_instance.get_api_resources()
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Unable to verify connectivity to the Kubernetes cluster.")
        kube_utils.kubernetes_exception_handler(e, consts.Kubernetes_Connectivity_FaultType,
                                                'Unable to verify connectivity to the Kubernetes cluster')


def get_server_version(configuration):
    api_instance = kube_client.VersionApi(kube_client.ApiClient(configuration))
    try:
        api_response = api_instance.get_code()
        return api_response.git_version
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Unable to fetch kubernetes version.")
        kube_utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Version_Fault_Type,
                                                'Unable to fetch kubernetes version', raise_error=False)


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
            if provider_id.startswith("kind://"):
                return "kind"
            if provider_id.startswith("k3s://"):
                return "k3s"
            if annotations.get("rke.cattle.io/external-ip") or annotations.get("rke.cattle.io/internal-ip"):
                return "rancher_rke"
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to fetch kubernetes distribution: " + str(e))
        kube_utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Distro_Fault_Type,
                                                'Unable to fetch kubernetes distribution',
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
            k8s_infra = validate_infrastructure_type(infra)
            if k8s_infra is not None:
                return k8s_infra
        return "generic"
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to fetch kubernetes infrastructure: " + str(e))
        kube_utils.kubernetes_exception_handler(e, consts.Get_Kubernetes_Infra_Fault_Type,
                                                'Unable to fetch kubernetes infrastructure',
                                                raise_error=False)
        return "generic"


def validate_infrastructure_type(infra):
    for s in consts.Infrastructure_Enum_Values[1:]:  # First value is "auto"
        if s.lower() == infra.lower():
            return s
    return "generic"


def check_linux_amd64_node(api_response):
    try:
        for item in api_response.items:
            node_arch = item.metadata.labels.get("kubernetes.io/arch")
            node_os = item.metadata.labels.get("kubernetes.io/os")
            if node_arch == "amd64" and node_os == "linux":
                return True
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Error occured while trying to find a linux/amd64 node: " + str(e))
        kube_utils.kubernetes_exception_handler(e, consts.Kubernetes_Node_Type_Fetch_Fault,
                                                'Unable to find a linux/amd64 node',
                                                raise_error=False)
    return False


def can_create_clusterrolebindings(configuration):
    try:
        api_instance = kube_client.AuthorizationV1Api(kube_client.ApiClient(configuration))
        access_review = kube_client.V1SelfSubjectAccessReview(spec={
            "resourceAttributes": {
                "verb": "create",
                "resource": "clusterrolebindings",
                "group": "rbac.authorization.k8s.io"
            }
        })
        response = api_instance.create_self_subject_access_review(access_review)
        return response.status.allowed
    except Exception as ex: # pylint: disable=broad-except
        logger.warning("Couldn't check for the permission to create clusterrolebindings" +
                       " on this k8s cluster. Error: {}".format(str(ex)))
        return "Unknown"


def validate_release_namespace(client, cluster_name, resource_group_name, configuration, kube_config, kube_context,
                               helm_client_location):

    helm_core_utils = HelmCoreUtils(kube_config, kube_context)
    # Check Release Existance
    release_namespace = helm_core_utils.get_release_namespace(helm_client_location)
    if release_namespace:
        # Loading config map
        api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
        try:
            configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
        except Exception as e:  # pylint: disable=broad-except
            kube_utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                                    error_message="Unable to read ConfigMap 'azure-clusterconfig'" +
                                                    " in 'azure-arc' namespace: ",
                                                    message_for_not_found="The helm release 'azure-arc' is present" +
                                                    " but the azure-arc namespace/configmap is missing. Please run" +
                                                    " 'helm delete azure-arc --no-hooks' to cleanup the release" +
                                                    " before onboarding the cluster again.")

        configmap_rg_name = configmap.data["AZURE_RESOURCE_GROUP"]
        configmap_cluster_name = configmap.data["AZURE_RESOURCE_NAME"]
        if cc_utils.connected_cluster_exists(client, configmap_rg_name, configmap_cluster_name):
            if not (configmap_rg_name.lower() == resource_group_name.lower() and
                    configmap_cluster_name.lower() == cluster_name.lower()):
                telemetry.set_exception(exception='The provided cluster name and rg correspond' +
                                        ' to different cluster', fault_type=consts.Operate_RG_Cluster_Name_Conflict,
                                        summary='The provided cluster name and resource group' +
                                        ' name do not correspond to the kubernetes cluster being operated on.')
                raise ArgumentUsageError("The provided cluster name and resource group name do not correspond" +
                                         " to the kubernetes cluster you are operating on.",
                                         recommendation="Please use the cluster, with correct resource group" +
                                         " and cluster name.")
        else:
            telemetry.set_exception(exception='The corresponding CC resource does not exist',
                                    fault_type=consts.Corresponding_CC_Resource_Deleted_Fault,
                                    summary='CC resource corresponding to this cluster has been' +
                                    ' deleted by the customer')
            raise ClientRequestError("There exist no ConnectedCluster resource corresponding to" +
                                     " this kubernetes Cluster.",
                                     recommendation="Please cleanup the helm release first using" +
                                     " 'az connectedk8s delete -n <connected-cluster-name> -g <resource-group-name>'" +
                                     " and re-onboard the cluster using " +
                                     "'az connectedk8s connect -n <connected-cluster-name> -g <resource-group-name>'")

    else:
        telemetry.set_exception(exception="The azure-arc release namespace couldn't be retrieved",
                                fault_type=consts.Release_Namespace_Not_Found,
                                summary="The azure-arc release namespace couldn't be retrieved," +
                                " which implies that the kubernetes cluster has not been onboarded to azure-arc.")
        raise ClientRequestError("The azure-arc release namespace couldn't be retrieved, which " +
                                 "implies that the kubernetes cluster has not been onboarded to azure-arc.",
                                 recommendation="Please run 'az connectedk8s connect -n <connected-cluster-name>" +
                                 " -g <resource-group-name>' to onboard the cluster")
    return release_namespace


def load_config_map(configuration):
    api_instance = kube_client.CoreV1Api(kube_client.ApiClient(configuration))
    try:
        configmap = api_instance.read_namespaced_config_map('azure-clusterconfig', 'azure-arc')
    except Exception as e:  # pylint: disable=broad-except
        kube_utils.kubernetes_exception_handler(e, consts.Read_ConfigMap_Fault_Type, 'Unable to read ConfigMap',
                                                error_message="Unable to read ConfigMap 'azure-clusterconfig' in" +
                                                " 'azure-arc' namespace: ", message_for_not_found="The helm release" +
                                                " 'azure-arc' is present but the azure-arc namespace/configmap is" +
                                                " missing. Please run 'helm delete azure-arc --no-hooks' to cleanup" +
                                                " the release before onboarding the cluster again.")
    return configmap
