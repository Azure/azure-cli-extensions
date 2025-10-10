# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------


import time
from azext_arcdata.core.util import retry
from azext_arcdata.failover_group.models.fog_cr import FogCustomResource
from azext_arcdata.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.core.constants import ARC_API_V1BETA2
from azext_arcdata.kubernetes_sdk.client import (
    K8sApiException,
    KubernetesClient,
    KubernetesError,
    http_status_codes,
)
from azext_arcdata.failover_group.constants import (
    DAG_ROLES_CREATE,
    DAG_ROLES_UPDATE,
    DAG_PARTNER_SYNC_MODE,
    FOG_API_GROUP,
    FOG_API_VERSION,
    FOG_RESOURCE_KIND_PLURAL,
)
from urllib3.exceptions import MaxRetryError, NewConnectionError

CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5


def get_valid_dag_roles(for_create):
    """
    Get the valid dag roles
    """
    if for_create:
        return DAG_ROLES_CREATE
    else:
        return DAG_ROLES_UPDATE


def validate_dag_roles(role_value, for_create):
    """
    returns True if role_value is valid
    """
    if role_value is None:
        return False
    if role_value.lower() in (
        t.lower() for t in get_valid_dag_roles(for_create)
    ):
        return True

    return False


def validate_dag_partner_sync_mode(mode_value):
    """
    returns True if mode_value is valid
    """
    if mode_value is None:
        return True
    if mode_value.lower() in (t.lower() for t in DAG_PARTNER_SYNC_MODE):
        return True

    return False


DAG_RESOURCE_KIND = "Dag"
DAG_RESOURCE_KIND_PLURAL = "dags"
DAG_API_GROUP = "sql.arcdata.microsoft.com"
DAG_API_VERSION = ARC_API_V1BETA2


def resolve_old_dag_items(namespace) -> list:

    client = KubernetesClient.resolve_k8s_client().CustomObjectsApi()

    try:
        response = client.list_namespaced_custom_object(
            namespace=namespace,
            group=DAG_API_GROUP,
            version=DAG_API_VERSION,
            plural=DAG_RESOURCE_KIND_PLURAL,
        )
        items = response.get("items")
        return items
    except K8sApiException as e:
        if e.status == http_status_codes.not_found:
            return []
        else:
            raise e


def get_failover_group_custom_resource(
    client: KubernetesClient, name, namespace, mi=None
):
    """
    Queries the kubernetes cluster and returns the custom resource for a Failover Group
    with the given name in the specified namespace
    :param client: KubernetesClient
    :param name: The name of the SQL Managed Instance
    :param namespace: Namespace where the SQL Managed Instance is deployed.
    :param mi: The name of the SQL Managed Instance (optional)
    :return: The k8s custom resource if one is found.
    An error will be raised if the instance is not found.
    """

    try:
        if mi:
            response = retry(
                lambda: client.list_namespaced_custom_object(
                    namespace,
                    group=FOG_API_GROUP,
                    version=FOG_API_VERSION,
                    plural=FOG_RESOURCE_KIND_PLURAL,
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="list namespaced custom object",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                    KubernetesError,
                ),
            )
            items = response.get("items")
            for item in items:
                if item["spec"]["sourceMI"] == mi:
                    cr = CustomResource.decode(FogCustomResource, item)
                    cr.metadata.namespace = namespace
                    return cr
        else:
            response = retry(
                lambda: client.get_namespaced_custom_object(
                    name,
                    namespace,
                    group=FOG_API_GROUP,
                    version=FOG_API_VERSION,
                    plural=FOG_RESOURCE_KIND_PLURAL,
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="get namespaced custom object",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                    KubernetesError,
                ),
            )
            cr = CustomResource.decode(FogCustomResource, response)
            cr.metadata.namespace = namespace
            return cr

    except K8sApiException as e:
        if e.status == http_status_codes.not_found:
            raise ValueError(
                "SQL managed instance failover group `{}` was not found in namespace `{}`.".format(
                    name, namespace
                )
            )


def poll_failover_group_state(client, name, namespace):
    """
    Queries the kubernetes cluster and returns state of the given Failover Group
    custom resource in the specified namespace
    :param client: KubernetesClient
    :param name: The name of the SQL Managed Instance
    :param namespace: Namespace where the SQL Managed Instance is deployed.
    :return: The k8s custom resource if one is found.
    An error will be raised if the instance is not found.
    """
    state = None
    while state != "succeeded" and state != "failed" or state is None:
        time.sleep(5)
        deployed_cr = get_failover_group_custom_resource(
            client, name, namespace
        )
        state = deployed_cr.status.state
        results = deployed_cr.status.results

        if state is not None:
            state = state.lower()

    return state, results


def _is_dag_ready(cr):
    """
    Verify that the SQL Mi DAG is ready
    :param cr: Instance to check the readiness of
    :return: True if the instance is ready, False otherwise
    """
    return (
        cr.status.state is not None and cr.status.state.lower() == "succeeded"
    )


def _is_dag_in_error(cr):
    """
    Check that the SQL Mi instance is in error state
    :param cr: Instance to check the readiness of
    :return: True if the instance is in error, False otherwise
    """
    return cr.status.state is not None and cr.status.state.lower() == "failed"


def _get_error_message(cr):
    """
    Get error message from the status of custom resource
    :param cr: Instance to get error message.
    """
    return cr.status.message
