# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.core.http_codes import http_status_codes
from azext_arcdata.core.util import (
    display,
    retry,
)
from knack.log import get_logger
from azext_arcdata.core.constants import (
    DOCKER_USERNAME,
    DOCKER_PASSWORD,
    REGISTRY_USERNAME,
    REGISTRY_PASSWORD,
)
from kubernetes.client.exceptions import ApiException
from urllib3.exceptions import NewConnectionError, MaxRetryError
from http import HTTPStatus
from kubernetes import client as k8sClient
from kubernetes.client.rest import ApiException as K8sApiException
from knack.log import get_logger
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

import base64
import json
import os
import re
import yaml

logger = get_logger(__name__)

DEFAULT_DOCKER_IMAGE_PULL_SECRET_NAME = "arc-private-registry"


def validate_namespace(cluster_name):
    """
    Check if the requested namespace is one in which a cluster can
    be deployed into
    """
    namespaces = ["default", "kube-system"]

    if cluster_name.lower() in namespaces:
        raise Exception("Cluster name can not be '%s'." % cluster_name)

    if not re.match(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", cluster_name):
        raise Exception(
            "Cluster name '"
            + cluster_name
            + "' is invalid. The name must consist of lowercase alphanumeric "
            "characters or '-', and  must start and end with a alphanumeric "
            "character."
        )


def create_namespace(cluster_name, labels=None):
    """
    Create and label the namespace
    """
    # Cluster name has to be DNS compliant by having only lowercase alphanumeric
    # characters or '-', and must start with and end with a alphanumeric
    # character.
    #
    try:
        body = k8sClient.V1Namespace()
        body.metadata = k8sClient.V1ObjectMeta(name=cluster_name, labels=labels)

        k8sClient.CoreV1Api().create_namespace(body=body)
    except K8sApiException as e:
        logger.error(e.body)
        raise


def patch_namespace(cluster_name, body):
    """
    Patch the namespace
    :param cluster_name:
    :param body:
    :return:
    """
    # Cluster name has to be DNS compliant by having only lowercase alphanumeric characters or '-',
    # and must start with and end with a alphanumeric character.
    #
    try:
        k8sClient.CoreV1Api().patch_namespace(name=cluster_name, body=body)
    except K8sApiException as e:
        logger.error(e.body)
        raise


def wrap_404(func):
    """
    Wrap a call to a webservice and swallow 404
    """
    try:
        return func()
    except ApiException as ex:
        if ex.status == 404:
            return
        else:
            raise


def namespace_is_empty(cluster_name, label=None):
    """
    Returns True if K8s namespace is empty.
    """

    try:
        kwargs = {"label_selector": label} if label else {}

        if (
            len(
                k8sClient.AppsV1Api()
                .list_namespaced_stateful_set(namespace=cluster_name, **kwargs)
                .items
            )
            > 0
        ):
            return False
        elif (
            len(
                k8sClient.AppsV1Api()
                .list_namespaced_daemon_set(namespace=cluster_name, **kwargs)
                .items
            )
            > 0
        ):
            return False
        elif (
            len(
                k8sClient.AppsV1Api()
                .list_namespaced_deployment(namespace=cluster_name, **kwargs)
                .items
            )
            > 0
        ):
            return False
        elif (
            len(
                k8sClient.AppsV1Api()
                .list_namespaced_replica_set(namespace=cluster_name, **kwargs)
                .items
            )
            > 0
        ):
            return False
        elif (
            len(
                k8sClient.CoreV1Api()
                .list_namespaced_service(namespace=cluster_name, **kwargs)
                .items
            )
            > 0
        ):
            return False
        elif (
            len(
                k8sClient.CoreV1Api()
                .list_namespaced_persistent_volume_claim(
                    namespace=cluster_name, **kwargs
                )
                .items
            )
            > 0
        ):
            return False
        elif (
            len(
                k8sClient.CoreV1Api()
                .list_namespaced_pod(namespace=cluster_name, **kwargs)
                .items
            )
            > 0
        ):
            return False
        else:
            return True
    except K8sApiException as e:
        logger.error(e.body)
        return False


def delete_cluster_resources(cluster_name, label=None):
    """
    Delete cluster resources.
    """
    try:
        kwargs = {"label_selector": label} if label else {}

        logger.debug("Deleting secrets")
        wrap_404(
            lambda: k8sClient.CoreV1Api().delete_collection_namespaced_secret(
                namespace=cluster_name, **kwargs
            )
        )

        logger.debug("Deleting persistent volume claims")
        wrap_404(
            lambda: k8sClient.CoreV1Api().delete_collection_namespaced_persistent_volume_claim(
                namespace=cluster_name, **kwargs
            )
        )

        logger.debug("Deleting pods")
        wrap_404(
            lambda: k8sClient.CoreV1Api().delete_collection_namespaced_pod(
                namespace=cluster_name, **kwargs
            )
        )

        logger.debug("Deleting service accounts")
        wrap_404(
            lambda: k8sClient.CoreV1Api().delete_collection_namespaced_service_account(
                namespace=cluster_name, **kwargs
            )
        )

        logger.debug("Deleting roles")
        wrap_404(
            lambda: k8sClient.RbacAuthorizationV1Api().delete_collection_namespaced_role_binding(
                namespace=cluster_name, **kwargs
            )
        )

        wrap_404(
            lambda: k8sClient.RbacAuthorizationV1Api().delete_collection_namespaced_role(
                namespace=cluster_name, **kwargs
            )
        )

        logger.debug("Deleting config maps")
        wrap_404(
            lambda: k8sClient.CoreV1Api().delete_collection_namespaced_config_map(
                namespace=cluster_name, **kwargs
            )
        )

        return (namespace_is_empty(cluster_name, label=label), HTTPStatus.OK)

    except K8sApiException as e:
        # If a 403 Forbidden is returned by K8s
        #
        if e.status == HTTPStatus.FORBIDDEN:
            display(
                "Failed to delete the cluster resources using Kubernetes API. "
                "Ensure that the delete permissions are set for the current "
                "kubectl context."
            )
            logger.debug(e)
            # return True to avoid retries for a 403 error
            #
            return True, HTTPStatus.FORBIDDEN
        return False, e.status


def get_namespace(cluster_name):
    """
    Get k8s namespace.
    :param cluster_name: name of the cluster namespace
    :return:
    """
    try:
        ns = k8sClient.CoreV1Api().read_namespace(cluster_name)
        return ns
    except K8sApiException as e:
        logger.debug(e.body)
        raise


def namespace_exists(cluster_name):
    """
    Return true if K8s namespace exists.
    """
    try:
        ns = get_namespace(cluster_name)
        return ns and cluster_name == ns.metadata.name
    except K8sApiException as e:
        logger.debug(e.body)
        return False


def update_namespace_label(cluster_name):
    """
    Update K8s namespace label and add the MSSQL_CLUSTER if not already added.
    """
    try:
        namespaces_list = k8sClient.CoreV1Api().list_namespace().items
        for namespace in namespaces_list:

            # Find the namespace
            #
            if namespace.metadata.name == cluster_name:
                # Add MSSQL_CLUSTER label to existing labels
                #
                labels = namespace.metadata.labels or {}
                labels["MSSQL_CLUSTER"] = cluster_name
                body = k8sClient.V1Namespace()
                body.metadata = k8sClient.V1ObjectMeta(labels=labels)
                k8sClient.CoreV1Api().patch_namespace(
                    name=cluster_name, body=body
                )
                return
    except K8sApiException as e:
        logger.error(e.body)
        raise


def delete_namespace(cluster_name):
    """
    Delete K8s namespace.
    """
    try:
        namespacesList = (
            k8sClient.CoreV1Api()
            .list_namespace(label_selector="MSSQL_CLUSTER=" + cluster_name)
            .items
        )
        namespaces = [n.metadata.name for n in namespacesList]
        if cluster_name in namespaces:
            k8sClient.CoreV1Api().delete_namespace(
                name=cluster_name, body=k8sClient.V1DeleteOptions()
            )
            display("Cluster deleted.")
        else:
            display("Cluster does not exist or is not a SQL cluster.")
    except K8sApiException as e:
        logger.error(e.body)
        raise


def setup_private_registry(
    cluster_name,
    docker_registry,
    secret_name=DEFAULT_DOCKER_IMAGE_PULL_SECRET_NAME,
    ignore_conflict=False,
):
    """
    Setup private docker repository secret.
    """
    try:
        body = create_registry_secret(
            cluster_name, docker_registry, secret_name=secret_name
        )

        k8sClient.CoreV1Api().create_namespaced_secret(
            namespace=cluster_name, body=body
        )
    except K8sApiException as e:
        if not (ignore_conflict and e.status == http_status_codes.conflict):
            raise


def update_private_registry_secret(
    cluster_name,
    docker_registry,
    secret_name=DEFAULT_DOCKER_IMAGE_PULL_SECRET_NAME,
    user_name=None,
    password=None,
):
    """
    Update private docker repository secret.
    """
    try:
        body = create_registry_secret(
            cluster_name,
            docker_registry,
            secret_name=secret_name,
            user_name=user_name,
            password=password,
        )

        k8sClient.CoreV1Api().patch_namespaced_secret(
            name=secret_name, namespace=cluster_name, body=body
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            try:
                k8sClient.CoreV1Api().create_namespaced_secret(
                    namespace=cluster_name, body=body
                )
            except K8sApiException as e:
                logger.error(e.body)
                raise
        else:
            logger.error(e.body)
            raise


def create_registry_secret(
    cluster_name,
    docker_registry,
    secret_name=DEFAULT_DOCKER_IMAGE_PULL_SECRET_NAME,
    user_name=None,
    password=None,
):
    """
    Create the private docker repository secret.
    """
    # .dockerconfigjson field is a base64 encoded string of the private
    #  registry credentials, which has the following format :
    # {
    #    "auths":{
    #       "docker_server":{
    #          "username":"<username>",
    #          "password":"<password>",
    #          "email":"<email>",
    #          "auth":"<username>:<password>"
    #       }
    #    }
    # }
    #

    un = user_name
    pw = password

    # use env variables if parameters not supplied
    if not un:
        un = os.getenv(REGISTRY_USERNAME)
    if not pw:
        pw = os.getenv(REGISTRY_PASSWORD)

    # Fallback to old environment variables.
    if not un:
        un = os.getenv(DOCKER_USERNAME)
    if not pw:
        pw = os.getenv(DOCKER_PASSWORD)

    b64_auth = base64.b64encode((un + ":" + pw).encode("utf-8")).decode("utf-8")

    credentials = dict()
    credentials["username"] = un
    credentials["password"] = pw
    credentials["email"] = un
    credentials["auth"] = b64_auth
    credentials_registry_server = dict()
    credentials_registry_server[docker_registry] = credentials
    auths_dict = dict()
    auths_dict["auths"] = credentials_registry_server
    docker_config_json = json.dumps(auths_dict)
    b64_docker_config_json = base64.b64encode(
        docker_config_json.encode("utf-8")
    ).decode("utf-8")

    body = k8sClient.V1Secret()
    body.type = "kubernetes.io/dockerconfigjson"
    body.data = {".dockerconfigjson": b64_docker_config_json}
    body.kind = "Secret"
    body.metadata = k8sClient.V1ObjectMeta(
        name=secret_name,
        namespace=cluster_name,
        labels={"MSSQL_CLUSTER": cluster_name},
    )

    return body


def create_empty_secret(cluster_name, secret_name):
    """
    Creates an empty secret in Kubernetes
    """
    try:
        body = k8sClient.V1Secret()
        body.type = "Opaque"
        body.kind = "Secret"
        body.metadata = k8sClient.V1ObjectMeta(
            name=secret_name,
            namespace=cluster_name,
            labels={"MSSQL_CLUSTER": cluster_name},
        )
        k8sClient.CoreV1Api().create_namespaced_secret(
            namespace=cluster_name, body=body
        )
    except K8sApiException as e:
        logger.error(e.body)
        raise


def update_cluster_role(cluster_role_name, cluster_role_body):
    """
    Update the cluster role.
    """
    try:
        k8sClient.RbacAuthorizationV1Api().patch_cluster_role(
            name=cluster_role_name, body=cluster_role_body
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            k8sClient.RbacAuthorizationV1Api().create_cluster_role(
                body=cluster_role_body
            )
        else:
            raise


def delete_service_account(name, namespace):
    try:
        k8sClient.CoreV1Api().delete_namespaced_service_account(
            name=name, namespace=namespace
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            # already deleted
            pass
        else:
            logger.error(
                "Could not delete ServiceAccount {0} in namespace {1}.  Please delete manually.".format(
                    name, namespace
                )
            )
            raise


def delete_cluster_role(cluster_role_name):
    """
    Update the cluster role.
    """
    try:
        k8sClient.RbacAuthorizationV1Api().delete_cluster_role(
            name=cluster_role_name
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            # already deleted
            pass
        else:
            logger.error(
                "Could not delete ClusterRole {0}.  Please delete manually.".format(
                    cluster_role_name
                )
            )
            raise


def delete_cluster_role_binding(cluster_role_binding_name):
    """
    delete the cluster role.
    """
    try:
        k8sClient.RbacAuthorizationV1Api().delete_cluster_role_binding(
            name=cluster_role_binding_name
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            # already deleted
            pass
        else:
            logger.error(
                "Could not delete ClusterRoleBinding {0}.  Please delete manually.".format(
                    cluster_role_binding_name
                )
            )
            raise


def update_cluster_role_binding(
    cluster_role_binding_name, cluster_role_binding_body
):
    """
    Update the cluster role binding.
    """
    try:
        k8sClient.RbacAuthorizationV1Api().patch_cluster_role_binding(
            name=cluster_role_binding_name, body=cluster_role_binding_body
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            k8sClient.RbacAuthorizationV1Api().create_cluster_role_binding(
                body=cluster_role_binding_body
            )
        else:
            raise


def create_config_map(cluster_name, config_map_name, data):
    """
    Creates an empty config map in Kubernetes
    """
    try:
        body = k8sClient.V1ConfigMap(data=data)
        body.kind = "ConfigMap"
        body.metadata = k8sClient.V1ObjectMeta(
            name=config_map_name,
            namespace=cluster_name,
            labels={"MSSQL_CLUSTER": cluster_name},
        )
        k8sClient.CoreV1Api().create_namespaced_config_map(
            namespace=cluster_name, body=body
        )
    except K8sApiException as e:
        logger.error(e.body)
        raise


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


def patch_config_map(cluster_name, config_map_name, patch):
    """
    Patch the config map
    """
    try:
        k8sClient.CoreV1Api().patch_namespaced_config_map(
            config_map_name, cluster_name, patch
        )
    except K8sApiException as e:
        logger.error(e.body)
        raise


def create_secret(cluster_name, config):
    """
    Creates a secret in Kubernetes
    """

    try:
        body = yaml.safe_load(config)
        k8sClient.CoreV1Api().create_namespaced_secret(
            namespace=cluster_name, body=body
        )
    except K8sApiException as e:
        logger.error(e.body)
        raise


def service_account_exists(cluster_name, service_account_name):
    """
    Returns true if service account exists in the namespace
    """

    try:
        service_account = k8sClient.CoreV1Api().read_namespaced_service_account(
            service_account_name, cluster_name
        )
        return service_account_name == service_account.metadata.name
    except K8sApiException as e:
        logger.debug(e.body)
        return False


def update_service_account(namespace, name, service_account_body):
    """
    Create or update the service account
    :param namespace: the namespace of the cluster to create the service account
    :param name: the name of the service account
    :service_account_body: yaml definition of the service account
    """
    try:
        k8sClient.CoreV1Api().patch_namespaced_service_account(
            namespace=namespace, name=name, body=service_account_body
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            k8sClient.CoreV1Api().create_namespaced_service_account(
                namespace=namespace, body=service_account_body
            )
        else:
            raise


def namespaced_role_exists(cluster_name, role_name):
    """
    Returns true if role exists in the namespace
    """

    try:
        role = k8sClient.RbacAuthorizationV1Api().read_namespaced_role(
            role_name, cluster_name
        )
        return role_name == role.metadata.name
    except K8sApiException as e:
        logger.debug(e.body)
        return False


def namespaced_role_binding_exists(cluster_name, role_binding_name):
    """
    Returns true if role binding exists in the namespace
    """

    try:
        role_binding = (
            k8sClient.RbacAuthorizationV1Api().read_namespaced_role_binding(
                role_binding_name, cluster_name
            )
        )
        return role_binding_name == role_binding.metadata.name
    except K8sApiException as e:
        logger.debug(e.body)
        return False


def update_namespaced_role(namespace, role_name, role_body):
    """
    Update the namespaced role.
    """

    try:
        k8sClient.RbacAuthorizationV1Api().patch_namespaced_role(
            name=role_name, namespace=namespace, body=role_body
        )
    except K8sApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            k8sClient.RbacAuthorizationV1Api().create_namespaced_role(
                namespace=namespace, body=role_body
            )
        else:
            raise


def cluster_role_exists(role_name):
    """
    Returns true if cluster role exists
    """

    try:
        role = k8sClient.RbacAuthorizationV1Api().read_cluster_role(role_name)
        return role_name == role.metadata.name
    except K8sApiException as e:
        logger.debug(e.body)
        return False


def cluster_role_binding_exists(role_binding_name):
    """
    Returns true if cluster role binding exists
    """

    try:
        role_binding = (
            k8sClient.RbacAuthorizationV1Api().read_cluster_role_binding(
                role_binding_name
            )
        )
        return role_binding_name == role_binding.metadata.name
    except K8sApiException as e:
        logger.debug(e.body)
        return False


def is_instance_ready(cr):
    """
    Verify that the custom resource instance is ready
    :param cr: Instance to check the readiness of
    :return: True if the instance is ready, False otherwise
    """
    return cr.metadata.generation == cr.status.observed_generation and (
        cr.status.state is not None and cr.status.state.lower() == "ready"
    )


def create_namespace_with_retry(
    namespace: str, cluster_label_key: str = None, annotations: dict = None
):
    """
    Create kubernetes namespace
    """

    CONNECTION_RETRY_ATTEMPTS = 12
    RETRY_INTERVAL = 5

    validate_namespace(namespace)

    # Create namespace if it doesn't already exit
    #
    if not retry(
        namespace_exists,
        namespace,
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method="check if namespace exists",
        retry_on_exceptions=(NewConnectionError, MaxRetryError),
    ):
        labels = {cluster_label_key: namespace} if cluster_label_key else {}

        retry(
            create_namespace,
            namespace,
            labels,
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="create namespace",
            retry_on_exceptions=(NewConnectionError, MaxRetryError),
        )

    # Populate namespace required annotations
    #
    if retry(
        namespace_is_empty,
        namespace,
        retry_count=CONNECTION_RETRY_ATTEMPTS,
        retry_delay=RETRY_INTERVAL,
        retry_method="check if namespace is empty",
        retry_on_exceptions=(NewConnectionError, MaxRetryError),
    ):
        namespace_response = k8sClient.CoreV1Api().read_namespace(namespace)

        if cluster_label_key:
            if (
                namespace_response.metadata.labels is None
                or cluster_label_key not in namespace_response.metadata.labels
            ):
                display(
                    'NOTE: Namespace "%s" is already created and will '
                    'not be labeled with "%s" Kubernetes label.'
                    % (namespace, cluster_label_key)
                )
                display(
                    "This is an informational message only, no user "
                    "action is required."
                )
                display("")

        if annotations:
            body = k8sClient.V1Namespace()
            body.metadata = k8sClient.V1ObjectMeta(annotations=annotations)

            retry(
                lambda: patch_namespace(namespace, body),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="patch namespace",
                retry_on_exceptions=(NewConnectionError, MaxRetryError),
            )
    else:
        raise Exception(
            "Cluster creation not initiated because the existing "
            "namespace %s "
            'is not empty. Run "kubectl get all -n %s "'
            " to see the existing objects in the namespace"
            % (namespace, namespace)
        )


def validate_rwx_storage_class(name: str, type: str, instanceType: str):
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()
    storageClass = None
    for s in client.StorageV1Api().list_storage_class().items:
        if s.metadata.name == name:
            storageClass = s

    if storageClass is None:
        raise Exception("Storage class '{}' does not exist".format(name))
    # A generic expression to match storage from list https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes and usage examples.
    #
    # example references for storage class names:
    # csi-filestore (https://github.com/kubernetes-sigs/gcp-filestore-csi-driver/blob/45661732bea386a0275851fa5c5364a0486e6467/examples/kubernetes/demo-sc.yaml )
    # efs-sc (https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html , https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html )
    # quobyte-csi ( https://github.com/quobyte/quobyte-csi/blob/master/example/StorageClass.yaml ) <-- Should update this one in the list from 'quobyte'.
    # px-shared-sc (https://github.com/portworx/helm/blob/master/charts/portworx/templates/portworx-storageclasses.yaml  and many other places for 'portworx'.)
    # csi-rbd-sc - (https://docs.ceph.com/en/latest/rbd/rbd-kubernetes/ ) for'ceph'.
    # glusterfs - (https://docs.openshift.com/container-platform/3.11/install_config/persistent_storage/persistent_storage_glusterfs.html )
    #
    # example references for volume provisoner names:
    # vsphere - (https://docs.openshift.com/container-platform/3.11/install_config/persistent_storage/persistent_storage_vsphere.html)
    # portworx - (https://docs.portworx.com/portworx-install-with-kubernetes/storage-operations/kubernetes-storage-101/volumes/)
    # nfs - (https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner),
    # quobyte - (https://www.quobyte.com/kubernetes-storage/connect-k8s-storage-classes-with-quobyte-policy-engine),
    # gluster - (https://docs.openshift.com/container-platform/3.11/install_config/storage_examples/gluster_dynamic_example.html)
    # ceph - (https://docs.ceph.com/en/latest/rbd/rbd-kubernetes/)
    if (
        re.match(
            r".*(csi-filestore|efs-sc|quobyte-csi|px-shared-sc|csi-rbd-sc|azurefile|azurefile-csi|azurefile-csi-premium|azurefile-premium|nfs).*",
            storageClass.metadata.name,
        )
    ) is None:
        if (
            storageClass.provisioner is None
            or storageClass.provisioner == "kubernetes.io/no-provisioner"
        ):
            raise Exception(
                "Storage class '{}' doesn't have a dynamic provisioner configured.".format(
                    name
                )
            )
        else:
            # ToDo: update the list based on validation with dynamic provisioners
            if (
                re.match(
                    r".*(nfs|glusterfs|azure-file|file.csi.azure|ceph|quobyte|postworx|vsphere).*",
                    storageClass.provisioner,
                )
            ) is None:
                logger.warning(
                    "{1} creation will fail if the storage class specified for the '{0}' volume does not support the ReadWriteMany (RWX) access mode. Please check if the {0} storage class supports ReadWriteMany (RWX) access mode. Please see https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes".format(
                        type, instanceType
                    )
                )
