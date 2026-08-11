# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ClientRequestError
from azure.cli.core.util import sdk_no_wait
from azure.core.exceptions import ResourceNotFoundError

from azext_aimanager._client_factory import CUSTOM_MGMT_AIMANAGER
from azext_aimanager._helpers import get_aks_custom_headers, parse_key_value_list


def _get_model(cmd, name, operation_group):
    return cmd.get_models(
        name,
        resource_type=CUSTOM_MGMT_AIMANAGER,
        operation_group=operation_group,
    )


# region AI Manager

def _construct_aimanager(cmd, location, tags, delete_policy, identity=None):
    ai_manager_properties_model = _get_model(cmd, "AIManagerProperties", "ai_managers")
    ai_manager_model = _get_model(cmd, "AIManager", "ai_managers")

    ai_manager = ai_manager_model()
    ai_manager.location = location
    ai_manager.tags = tags
    ai_manager.properties = ai_manager_properties_model(delete_policy=delete_policy)
    if identity is not None:
        ai_manager.identity = identity
    return ai_manager


# pylint: disable=unused-argument
def create_aimanager(cmd,
                     client,
                     resource_group_name,
                     ai_manager_name,
                     location=None,
                     tags=None,
                     delete_policy=None,
                     aks_custom_headers=None,
                     no_wait=False):
    existing = None
    try:
        existing = client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        pass
    if existing:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' already exists. "
            "Please use 'az aimanager update' to update it.")

    headers = get_aks_custom_headers(aks_custom_headers)
    ai_manager = _construct_aimanager(cmd, location, tags, delete_policy)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        ai_manager,
        headers=headers,
    )


# pylint: disable=unused-argument
def update_aimanager(cmd,
                     client,
                     resource_group_name,
                     ai_manager_name,
                     tags=None,
                     delete_policy=None,
                     aks_custom_headers=None,
                     no_wait=False):
    try:
        existing = client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' doesn't exist. "
            "Please use 'az aimanager list' to get the current list of AI Managers.")

    if tags is None:
        tags = existing.tags
    existing_properties = existing.properties
    if delete_policy is None and existing_properties is not None:
        delete_policy = existing_properties.delete_policy

    headers = get_aks_custom_headers(aks_custom_headers)
    # Preserve the existing identity so a tags/delete-policy update does not drop a
    # managed identity configured through ARM or another client on the create-or-replace PUT.
    ai_manager = _construct_aimanager(
        cmd, existing.location, tags, delete_policy, identity=existing.identity)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        ai_manager,
        headers=headers,
    )


def show_aimanager(cmd, client, resource_group_name, ai_manager_name):  # pylint: disable=unused-argument
    return client.get(resource_group_name, ai_manager_name)


def list_aimanager(cmd, client, resource_group_name=None):  # pylint: disable=unused-argument
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


def delete_aimanager(cmd, client, resource_group_name, ai_manager_name, no_wait=False):  # pylint: disable=unused-argument
    try:
        client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' doesn't exist. "
            "Please use 'az aimanager list' to get the current list of AI Managers.")

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, ai_manager_name)

# endregion


# region AI Manager namespace

def _construct_namespace(cmd, labels, annotations):
    namespace_properties_model = _get_model(cmd, "AIManagerNamespaceProperties", "ai_manager_namespaces")
    namespace_model = _get_model(cmd, "AIManagerNamespace", "ai_manager_namespaces")

    namespace_config = namespace_model()
    namespace_config.properties = namespace_properties_model(labels=labels, annotations=annotations)
    return namespace_config


# pylint: disable=unused-argument
def add_aimanager_namespace(cmd,
                            client,
                            resource_group_name,
                            ai_manager_name,
                            namespace_name,
                            labels=None,
                            annotations=None,
                            aks_custom_headers=None,
                            no_wait=False):
    existing = None
    try:
        existing = client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        pass
    if existing:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' already exists. "
            "Please use 'az aimanager namespace update' to update it.")

    headers = get_aks_custom_headers(aks_custom_headers)
    namespace_config = _construct_namespace(
        cmd, parse_key_value_list(labels), parse_key_value_list(annotations))

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        namespace_name,
        namespace_config,
        headers=headers,
    )


# pylint: disable=unused-argument
def update_aimanager_namespace(cmd,
                               client,
                               resource_group_name,
                               ai_manager_name,
                               namespace_name,
                               labels=None,
                               annotations=None,
                               aks_custom_headers=None,
                               no_wait=False):
    try:
        existing = client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' doesn't exist. "
            "Please use 'az aimanager namespace list' to get the current list of namespaces.")

    existing_properties = existing.properties
    if labels is None:
        new_labels = existing_properties.labels if existing_properties is not None else None
    else:
        new_labels = parse_key_value_list(labels)
    if annotations is None:
        new_annotations = existing_properties.annotations if existing_properties is not None else None
    else:
        new_annotations = parse_key_value_list(annotations)

    headers = get_aks_custom_headers(aks_custom_headers)
    namespace_config = _construct_namespace(cmd, new_labels, new_annotations)

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        ai_manager_name,
        namespace_name,
        namespace_config,
        headers=headers,
    )


def show_aimanager_namespace(cmd, client, resource_group_name, ai_manager_name, namespace_name):  # pylint: disable=unused-argument
    return client.get(resource_group_name, ai_manager_name, namespace_name)


def list_aimanager_namespace(cmd, client, resource_group_name, ai_manager_name):  # pylint: disable=unused-argument
    return client.list_by_ai_manager(resource_group_name, ai_manager_name)


def delete_aimanager_namespace(cmd, client, resource_group_name, ai_manager_name, namespace_name, no_wait=False):  # pylint: disable=unused-argument
    try:
        client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' doesn't exist. "
            "Please use 'az aimanager namespace list' to get the current list of namespaces.")

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, ai_manager_name, namespace_name)

# endregion
