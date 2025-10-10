# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from os import stat
from typing import Tuple
from azext_arcdata.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.kubernetes_sdk.errors.K8sAdmissionReviewError import (
    K8sAdmissionReviewError,
)
from azext_arcdata.kubernetes_sdk.models.custom_resource_definition import (
    CustomResourceDefinition,
)
from azext_arcdata.kubernetes_sdk.HttpCodes import http_status_codes
from azext_arcdata.core.util import (
    check_and_set_kubectl_context,
    retry,
    retry_method,
)
from azext_arcdata.core.constants import (
    ARC_GROUP,
    DATA_CONTROLLER_CRD_VERSION,
    DATA_CONTROLLER_PLURAL,
    USE_K8S_EXCEPTION_TEXT,
)
from azext_arcdata.kubernetes_sdk.models.data_controller_custom_resource import (
    DataControllerCustomResource,
)

from kubernetes import client as k8sClient
from kubernetes.client.rest import ApiException as K8sApiException

from knack.log import get_logger
from functools import wraps
from pydash.utilities import memoize
from urllib3.exceptions import NewConnectionError, MaxRetryError

import json
import pydash as _

CONNECTION_RETRY_ATTEMPTS = 12
DELETE_CLUSTER_TIMEOUT_SECONDS = 300
RETRY_INTERVAL = 5
UPDATE_INTERVAL = (15 * 60) / RETRY_INTERVAL

logger = get_logger(__name__)

__all__ = ["KubernetesClient", "KubernetesError"]


def catch_admission_responses(f):
    """
    A decorator to add k8s admission review error handling
    to any method in this class. Checks if any raised exceptions
    are admission review errors and if so re raises appropriately.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            if K8sAdmissionReviewError.is_admission_review_error(e):
                raise K8sAdmissionReviewError(e)

            raise e

    return wrapper


class KubernetesClient(object):
    """
    Client for managing Kubernetes Resources, to be used by Arc partner
    command modules.
    """

    """
    Custom Resource Definition specification key.
    """
    CUSTOM_RESOURCE_DEFINITION = "CustomResourceDefinition"

    @staticmethod
    def get_service(ns: str, service_name: str):
        """
        Get the specified service in the given namespace.
        :param ns:
        :param service_name:
        :return:
        """
        try:
            return k8sClient.CoreV1Api().read_namespaced_service(
                service_name, ns
            )
        except K8sApiException as e:
            logger.debug(e.body)
            raise

    @staticmethod
    def service_exists(ns: str, service_name: str):
        """
        Get the specified service in the given namespace.
        :param ns:
        :param: service_name:
        :return:
        """
        try:
            service = k8sClient.CoreV1Api().read_namespaced_service(
                service_name, ns
            )
            return service_name == service.metadata.name
        except K8sApiException as e:
            logger.debug(e.body)
            return False

    @staticmethod
    def service_ready(ns: str, service_name: str):
        """
        Check if the specified service is ready
        :param ns:
        :param service_name:
        :return:
        """
        try:
            service = KubernetesClient.get_service(ns, service_name)

            if service.spec.type == "LoadBalancer":
                # Make sure that the load balancer has at least one host listed
                #
                ingress = service.status.load_balancer.ingress
                if ingress is not None and len(ingress) > 0:
                    for svc in ingress:
                        if svc.ip or svc.hostname:
                            return True
            elif service.spec.type == "NodePort":
                # No additional checks are required for NodePorts
                #
                return True

            return False
        except K8sApiException as e:
            return False

    @staticmethod
    def get_service_endpoint(
        ns: str, service: any, force_ip: bool = False, app: str = "controller"
    ):
        """
        Returns the endpoint of the service based on whether it is
        LoadBalancer or NodePort
        :param ns:
        :param service:
        :param force_ip:
        :param app:
        :return:
        """
        host = None
        port = None
        if service.spec.type == "LoadBalancer":
            ingress = service.status.load_balancer.ingress
            if ingress is not None and len(ingress) > 0:
                for svc in ingress:
                    host = svc.ip or svc.hostname
                    if host:
                        port = str(service.spec.ports[0].port)
                        break
        elif service.spec.type == "NodePort":
            # Get the IP of any pod in the controller replica set for NodePort
            # service
            controller_pods = KubernetesClient.list_pods(
                ns, "app={}".format(app)
            ).items
            if controller_pods and len(controller_pods) > 0:
                host = controller_pods[0].status.host_ip
                port = str(service.spec.ports[0].node_port)
        else:
            raise Exception(
                "Service type {0} for service "
                "{1} is not supported.".format(
                    service.spec.type, service.metadata.name
                )
            )

        if service.metadata.labels.get("dnsName", None) and not force_ip:
            host = service.metadata.labels["dnsName"]

        if not host:
            raise ValueError(
                "Failed to retrieve service endpoint. Host not found."
            )
        elif not port:
            raise ValueError(
                "Failed to retrieve service endpoint. Port not found."
            )

        return "https://" + host + ":" + port

    @staticmethod
    def list_pods(ns: str, label_selector=None):
        """
        List the pods in the given namespace
        :param ns: The namespace
        :param label_selector: The label to select the pods by.
        :return:
        """
        try:
            return k8sClient.CoreV1Api().list_namespaced_pod(
                ns, label_selector=label_selector
            )
        except K8sApiException as e:
            logger.error(e.body)
            raise

    @staticmethod
    def list_node(label_selector=None):
        """
        List the nodes
        :param label_selector: The label to select the nodes by.
        :return:
        """
        try:
            return k8sClient.CoreV1Api().list_node(
                label_selector=label_selector
            )
        except K8sApiException as e:
            logger.error(e.body)
            raise

    @staticmethod
    def pod_is_running(ns: str, app_label: str):
        """
        Returns true if the pod is a Running state
        :param ns:
        :param app_label:
        :return:
        """
        selector = "app=%s" % app_label
        pods = KubernetesClient.list_pods(ns, selector).items
        return (
            pods
            and len(pods) > 0
            and all(
                pod.status.phase.lower() == "running" and pod.status.host_ip
                for pod in pods
            )
        )

    @staticmethod
    def create_secret(ns: str, config, ignore_conflict: bool = False):
        """
        Creates a secret in Kubernetes
        :param ignore_conflict:
        :param ns:
        :param config:
        :return:
        """
        try:
            k8sClient.CoreV1Api().create_namespaced_secret(
                namespace=ns, body=config
            )
        except K8sApiException as e:
            if not (ignore_conflict and e.status == http_status_codes.conflict):
                raise

    @staticmethod
    def secret_exists(ns: str, secret_name: str):
        """
        Returns true if secret exists in the namespace
        :param ns:
        :param secret_name:
        :return:
        """
        try:
            secret = k8sClient.CoreV1Api().read_namespaced_secret(
                secret_name, ns
            )
            return secret_name == secret.metadata.name
        except K8sApiException as e:
            logger.debug(e.body)
            return False

    @staticmethod
    def get_secret(ns: str, secret_name: str):
        """
        Returns V1Secret in ns if it exists
        :param ns:
        :param secret_name:
        :return: V1Secret
        """
        try:
            return k8sClient.CoreV1Api().read_namespaced_secret(secret_name, ns)
        except K8sApiException as e:
            logger.debug(e.body)
            raise

    @staticmethod
    def storage_class_exists(class_name: str):
        """
        Checks if the provided storage class exists
        :param class_name:
        :return: True if class_name is an existing storage class,
        false otherwise
        """
        try:
            storage_class = k8sClient.StorageV1Api().read_storage_class(
                class_name
            )
            return storage_class and storage_class.metadata.name == class_name
        except K8sApiException as e:
            logger.debug(e.body)
            return False

    @staticmethod
    def patch_secret(ns: str, secret_name: str, body: dict):
        """
        Patches a secret in Kubernetes
        :param ns: The secret's namespace
        :param secret_name: The secret's name
        :param body: A dictionary of fields to patch
        :return: The patched secret
        """
        try:
            return k8sClient.CoreV1Api().patch_namespaced_secret(
                namespace=ns, name=secret_name, body=body
            )
        except K8sApiException as e:
            logger.debug(e.body)
            raise

    @staticmethod
    def create_replica_set(ns: str, spec: dict):
        """
        Creates a replica set in the given namespace
        :param ns:
        :param spec:
        :return:
        """
        try:
            k8sClient.AppsV1Api().create_namespaced_replica_set(ns, spec)
        except K8sApiException as e:
            logger.debug(e.body)
            raise e

    @staticmethod
    def replica_set_exists(ns: str, replica_set_name: str):
        """
        Returns true if replica set exists in the namespace
        :param ns:
        :param replica_set_name:
        :return:
        """
        try:
            replica_set = k8sClient.AppsV1Api().read_namespaced_replica_set(
                replica_set_name, ns
            )
            return replica_set_name == replica_set.metadata.name
        except K8sApiException as e:
            logger.debug(e.body)
            return False

    @staticmethod
    def create_namespaced_service_account(ns: str, spec: dict):
        """
        Creates namespaced service account
        :param ns:
        :param spec:
        :return:
        """
        try:
            k8sClient.CoreV1Api().create_namespaced_service_account(ns, spec)
        except K8sApiException as e:
            logger.debug(e.body)
            raise e

    @staticmethod
    def service_account_exists(ns: str, service_account_name: str):
        """
        Returns true if service account exists in the namespace
        :param ns:
        :param service_account_name:
        :return:
        """
        try:
            service_account = (
                k8sClient.CoreV1Api().read_namespaced_service_account(
                    service_account_name, ns
                )
            )
            return service_account_name == service_account.metadata.name
        except K8sApiException as e:
            logger.debug(e.body)
            return False

    @staticmethod
    def create_namespaced_role(ns: str, spec: dict):
        """
        Creates namespaced role binding
        :param ns:
        :param spec:
        :return:
        """
        try:
            k8sClient.RbacAuthorizationV1Api().create_namespaced_role(ns, spec)
        except K8sApiException as e:
            logger.debug(e.body)
            raise e

    @staticmethod
    def create_namespaced_job(ns: str, spec: dict):
        """
        Creates a namespaced k8s job
        :param ns:
        :param spec:
        :return:
        """
        try:
            k8sClient.BatchV1Api().create_namespaced_job(ns, spec)
        except K8sApiException as e:
            logger.debug(e.body)
            raise e

    @staticmethod
    def namespaced_role_exists(ns: str, role_name: str):
        """
        Returns true if role exists in the namespace
        :param ns:
        :param role_name:
        :return:
        """
        try:
            role = k8sClient.RbacAuthorizationV1Api().read_namespaced_role(
                role_name, ns
            )
            return role_name == role.metadata.name
        except K8sApiException as e:
            logger.debug(e.body)
            return False

    @staticmethod
    def create_namespaced_role_binding(ns: str, spec: dict):
        """
        Creates namespaced role binding
        :param ns:
        :param spec:
        :return:
        """
        try:
            k8sClient.RbacAuthorizationV1Api().create_namespaced_role_binding(
                ns, spec
            )
        except K8sApiException as e:
            logger.debug(e.body)
            raise e

    @staticmethod
    def create_mutating_webhook_configuration(spec: dict):
        """
        Creates a mutating webhook configuration for the given namespace
        :param spec: the mutating webhook configuration spec as a dict
        """
        try:
            k8sClient.AdmissionregistrationV1beta1Api().create_mutating_webhook_configuration(
                spec
            )
        except K8sApiException as e:
            logger.debug(e.body)
            raise e

    @staticmethod
    def get_config_map(cluster_name, config_map_name):
        """
        Retrieve the requested config map
        """
        try:
            config_map = k8sClient.CoreV1Api().read_namespaced_config_map(
                config_map_name, cluster_name
            )
            return config_map
        except k8sClient.rest.ApiException as e:
            logger.error(e.body)
            raise

    @staticmethod
    def namespaced_role_binding_exists(ns: str, role_binding_name: str):
        """
        Returns true if role binding exists in the namespace
        :param ns:
        :param role_binding_name:
        :return:
        """
        try:
            role_binding = (
                k8sClient.RbacAuthorizationV1Api().read_namespaced_role_binding(
                    role_binding_name, ns
                )
            )
            return role_binding_name == role_binding.metadata.name
        except K8sApiException as e:
            logger.debug(e.body)
            return False

    # ------------------------------
    # Custom Resource Methods
    # ------------------------------
    @staticmethod
    def delete_custom_resource_definition(crd: CustomResourceDefinition):
        """
        Delete the given crd.
        :param crd: The crd to create.
        :return:
        """
        try:
            api = k8sClient.ApiextensionsV1Api()
            current_crds = [
                x["spec"]["names"]["kind"].lower()
                for x in api.list_custom_resource_definition().to_dict()[
                    "items"
                ]
            ]
            if crd.kind.lower() in current_crds:
                return api.delete_custom_resource_definition(crd.name)

        except ValueError as e:
            # Kubernetes API bug with prior versions of Kubernetes
            # The CRD does get created but returns an erroneous value error
            # that we can safely ignore.
            # This is fixed in Kubernetes version 1.16
            # https://github.com/kubernetes-client/python/issues/1022
            # We can remove this condition when we upgrade to version 1.16,
            # server-side.
            if "Invalid value for `conditions`, must not be `None`" in str(e):
                return
            else:
                raise e
        except Exception as e:
            raise KubernetesError(e)

    @staticmethod
    @catch_admission_responses
    def create_namespaced_custom_object(
        cr: CustomResource, plural: str, ignore_conflict: bool = False
    ):
        """
        Creates a kubernetes custom resource object with the given crd and
        specification json
        :param cr: The custom resource instance to be deployed.
        :param plural: The plural name of the custom resource definition.
        :param ignore_conflict: ignore conflict
        :return:
        """
        try:
            api = k8sClient.CustomObjectsApi()
            return api.create_namespaced_custom_object(
                body=cr.encode(),
                namespace=cr.metadata.namespace,
                plural=plural,
                group=cr.group,
                version=cr.version,
            )

        except K8sApiException as e:
            if ignore_conflict and e.status == http_status_codes.conflict:
                return None
            else:
                raise KubernetesError(e)

    @staticmethod
    @catch_admission_responses
    def create_namespaced_custom_object_with_body(
        body: dict,
        cr: CustomResource,
        plural: str,
        ignore_conflict: bool = False,
    ):
        """
        Creates a kubernetes custom resource object with the given crd and
        specification json
        :param cr: The custom resource instance to be deployed.
        :param plural: The plural name of the custom resource definition.
        :param ignore_conflict: ignore conflict
        :return:
        """
        try:
            api = k8sClient.CustomObjectsApi()
            return api.create_namespaced_custom_object(
                body=body,
                namespace=cr.metadata.namespace,
                plural=plural,
                group=cr.group,
                version=cr.version,
            )

        except K8sApiException as e:
            if ignore_conflict and e.status == http_status_codes.conflict:
                return None
            else:
                raise KubernetesError(e)

    @staticmethod
    @catch_admission_responses
    @retry_method(
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method_description="Patch custom resource",
        retry_on_exceptions=(NewConnectionError, MaxRetryError),
    )
    def patch_namespaced_custom_object(cr: CustomResource, plural: str):
        """
        Patches a kubernetes custom resource object with the given crd and
        specification json
        :param cr: The custom resource instance to be deployed.
        :param plural: The plural name of the custom resource definition.
        :return:
        """
        try:
            api = k8sClient.CustomObjectsApi()
            return api.patch_namespaced_custom_object(
                body=cr.encode(),
                group=cr.group,
                version=cr.version,
                name=cr.metadata.name,
                namespace=cr.metadata.namespace,
                plural=plural,
            )

        except Exception as e:
            raise KubernetesError(e)

    @staticmethod
    @catch_admission_responses
    @retry_method(
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method_description="Merge data controller",
        retry_on_exceptions=(NewConnectionError, MaxRetryError),
    )
    def merge_namespaced_custom_object(
        body,
        cr=None,
        name=None,
        namespace=None,
        plural=None,
        group=None,
        version=None,
    ):
        """
        Merges a kubernetes custom resource object with the supplied body.

        >>> You can call this is one of 2 ways depending on which is most
        convenient for your scenario:
        >>> 1. Without an existing CR object, you may provide the body,
        and all kw arguments
        >>>    Example: merge_namespaced_custom_object(body,
        plural="datacontrollers", name=name, namespace=namespace,
        group=group, version=version)
        >>> 2. If you have an existing CR object, you may provide the body
        positional argument and plural=plural then pass the cr using the cr
        param
        >>>    Example: merge_namespaced_custom_object(body,
        plural="datacontrollers", **cr)

        :param body: the json document to be applied to the custom resource
        :namespace: the namespace of the cr
        :name: the name of the cr
        :param plural: The plural name of the custom resource definition.
        :param cr: Existing cr, if none is passed, the
        :param group: The api group for the custom resource use "kubectl
        api-resources" to see the appropriate group for a given resource type
        :param version: The api version
        :return:
        """
        if cr is not None:
            name = cr.metadata.name
            namespace = cr.metadata.name
            group = cr.group
            version = cr.version

        try:
            api = k8sClient.CustomObjectsApi()
            return api.patch_namespaced_custom_object(
                body=body,
                name=name,
                namespace=namespace,
                group=group,
                version=version,
                plural=plural,
            )

        except Exception as e:
            raise KubernetesError(e)

    @staticmethod
    @catch_admission_responses
    def replace_namespaced_custom_object(cr: CustomResource, plural: str):
        """
        Replaces a kubernetes custom resource object with the given crd and
        specification json
        :param cr: The custom resource instance to be deployed.
        :param plural: The plural name of the custom resource definition.
        :return:
        """
        try:
            api = k8sClient.CustomObjectsApi()
            return api.replace_namespaced_custom_object(
                body=cr.encode(),
                namespace=cr.metadata.namespace,
                plural=plural,
                group=cr.group,
                version=cr.version,
                name=cr.metadata.name,
            )

        except Exception as e:
            raise KubernetesError(e)

    @staticmethod
    def patch_namespace(ns_name: str, patch: dict):
        """
        Applies a patch to the specified namespace
        :param ns_name: The name of the namespace to patch
        :param patch: the patch to apply
        :return:
        """
        try:
            k8sClient.CoreV1Api().patch_namespace(name=ns_name, body=patch)
        except Exception as e:
            raise KubernetesError(e)

    @staticmethod
    @catch_admission_responses
    def delete_namespaced_custom_object(
        name: str,
        namespace: str,
        crd: CustomResourceDefinition = None,
        group: str = None,
        version: str = None,
        plural: str = None,
    ):
        """
        Deletes a custom resource object
        :param name: The name of the custom resource to be deleted.
        :param namespace: The namespace from which to delete the custom
        resource.
        :param crd: The definition of the custom resource to be deleted.
        :param group: The API version group.
        :param version: The kubernetes custom resource api version.
        :param plural: The plural name of the custom resource definition.
        :return:
        """
        if crd:
            group = crd.group
            version = crd.stored_version
            plural = crd.plural
        elif not group or not version or not plural:
            raise ValueError(
                "Please specify either a valid CRD or the group, version, "
                "and plural."
            )

        try:
            api = k8sClient.CustomObjectsApi()
            return api.delete_namespaced_custom_object(
                group=group,
                version=version,
                plural=plural,
                namespace=namespace,
                name=name,
                body=k8sClient.V1DeleteOptions(),
            )

        except Exception as e:
            raise KubernetesError(e)

    @staticmethod
    def get_namespaced_custom_object(
        name: str,
        namespace: str,
        crd: CustomResourceDefinition = None,
        group: str = None,
        version: str = None,
        plural=None,
    ):
        """
        Gets the custom resource object
        :param name: The name of the custom resource.
        :param namespace: The namespace of the custom resource.
        :param crd: The definition of the custom resource.
        :param group: The API version group.
        :param version: The kubernetes custom resource api version.
        :param plural: The plural name of the custom resource definition.
        :return:
        """
        try:
            api = k8sClient.CustomObjectsApi()

            if crd:
                group = crd.group
                version = crd.stored_version
                plural = crd.plural
            elif not group or not version or not plural:
                raise ValueError(
                    "Please specify either a valid CRD or the group, version, "
                    "and plural."
                )

            return api.get_namespaced_custom_object(
                group=group,
                version=version,
                name=name,
                namespace=namespace,
                plural=plural,
            )

        except K8sApiException as e:
            raise

    @staticmethod
    def namespaced_custom_object_exists(
        name: str,
        namespace: str,
        crd: CustomResourceDefinition = None,
        group: str = None,
        version: str = None,
        plural: str = None,
    ):
        """
        Check if the custom resource object exists
        :param name: The name of the custom resource.
        :param namespace: The namespace of the custom resource.
        :param crd: The definition of the custom resource.
        :param group: The API version group.
        :param version: The kubernetes custom resource api version.
        :param plural: The plural name of the custom resource definition.
        :return:
        """
        try:
            custom_object = KubernetesClient.get_namespaced_custom_object(
                name, namespace, crd, group, version, plural
            )
            return name == custom_object["metadata"]["name"]
        except K8sApiException as e:
            if e.status == http_status_codes.not_found:
                return False
            else:
                raise

    @staticmethod
    def persistent_volume_claim_exists(name: str, namespace: str):
        """
        Checks if the provided persistent volume claim exists
        :param name: the name of the persistent volume
        :param namespace: the namespace to search for it
        :return: True if the volume exists in namespace, False otherwise
        """
        try:
            k8sClient.CoreV1Api().read_namespaced_persistent_volume_claim(
                name=name, namespace=namespace
            )
            return True
        except K8sApiException as e:
            if e.status == http_status_codes.not_found:
                return False
            else:
                raise

    @staticmethod
    def list_namespaced_custom_object(
        namespace: str,
        crd: CustomResourceDefinition = None,
        group: str = None,
        version: str = None,
        plural: str = None,
    ):
        """
        Lists the custom resource object
        :param namespace: The namespace of the custom resource.
        :param crd: The definition of the custom resource.
        :param group: The API version group.
        :param version: The kubernetes custom resource api version.
        :param plural: The plural name of the custom resource definition.
        :return:
        """
        try:
            api = k8sClient.CustomObjectsApi()

            if crd:
                group = crd.group
                version = crd.stored_version
                plural = crd.plural
            elif not group or not version or not plural:
                raise ValueError(
                    "Please specify either a valid CRD or the group, version, "
                    "and plural."
                )

            return api.list_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
            )

        except K8sApiException as e:
            logger.debug(e.body)
            raise e

    @staticmethod
    def resolve_k8s_client() -> k8sClient:
        check_and_set_kubectl_context()

        return k8sClient

    @staticmethod
    def assert_use_k8s(use_k8s=None):
        if not use_k8s:
            raise ValueError(USE_K8S_EXCEPTION_TEXT)

    def patch_property(path: str, value, patch_array=None, operation="replace"):
        """
        adds a new replace patch operation to the array, or creates a new
        array with jsonPatch command
        """
        if patch_array is None:
            patch_array = []

        patch_array.append({"op": operation, "path": path, "value": value})
        return patch_array

    @staticmethod
    def get_arc_datacontroller(
        namespace: str, use_k8s: bool = True
    ) -> Tuple[CustomResource, str]:

        """
        Return the data controller custom resource for the given namespace.
        """
        try:
            # -- Check Kubectl Context --
            client = KubernetesClient.resolve_k8s_client().CustomObjectsApi()
            namespace = namespace

            response = retry(
                lambda: client.list_namespaced_custom_object(
                    namespace=namespace,
                    group=ARC_GROUP,
                    version=KubernetesClient.get_crd_version(
                        "datacontrollers.arcdata.microsoft.com"
                    ),
                    plural=DATA_CONTROLLER_PLURAL,
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="get data controller",
                retry_on_exceptions=(NewConnectionError, MaxRetryError),
            )

            dcs = response.get("items")

            dcs = _.find(
                dcs,
                lambda d: _.get(d, ["status", "state"], None) != ""
                and _.get(d, ["status", "state"]).lower() != "duplicateerror",
            )

            if not dcs:
                raise Exception(
                    "No data controller exists in Kubernetes namespace `{"
                    "}`.".format(namespace)
                )
            else:
                cr = CustomResource.decode(DataControllerCustomResource, dcs)
                return (cr, dcs)

        except Exception:
            raise

    @memoize
    def _get_crd():
        client = KubernetesClient.resolve_k8s_client().ApiextensionsV1Api()
        crds = client.list_custom_resource_definition()
        return crds

    @staticmethod
    def get_crd(
        crd_name="datacontrollers.arcdata.microsoft.com", reset_cache=False
    ):

        if reset_cache is True:
            KubernetesClient._get_crd.cache = {}

        crds = KubernetesClient._get_crd().items
        crd = _.head(_.filter_(crds, lambda crd: crd.metadata.name == crd_name))
        return crd

    @staticmethod
    def get_crd_version(
        crd_name="datacontrollers.arcdata.microsoft.com", reset_cache=False
    ):
        try:
            crd = KubernetesClient.get_crd(crd_name, reset_cache)
            version = _.head(
                _.filter_(crd.spec.versions, lambda v: v.storage is True)
            )
            return version.name
        except Exception as ex:
            raise Exception(
                "Unable to resolve Custom Resource Definition api_version for "
                "{0}.".format(crd_name)
            ) from ex


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class KubernetesError(Exception):
    """All errors related to Kubernetes APIS."""

    def __init__(self, api_exception):
        self.body = json.loads(api_exception.body)
        super().__init__(self.message)

    @property
    def reason(self):
        return self.body

    @property
    def body(self):
        """
        Returns the body of the kubernetes error
        :return:
        """
        return self._body

    @body.setter
    def body(self, b):
        """
        Sets the body of the kubernetes error
        :param b:
        :return:
        """
        self._body = b

    @property
    def message(self):
        """
        Returns the message of the kubernetes error.
        :return:
        """
        return self.body["message"]

    @property
    def status(self):
        """
        Returns the status of the kubernetes error.
        :return:
        """
        return self.body["status"]

    @property
    def code(self):
        """
        Returns the code of the kubernetes error.
        :return:
        """
        return self.body["code"]
