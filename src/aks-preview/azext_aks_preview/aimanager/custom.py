# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Command handlers for the ``az aimanager`` command group.

These mirror the ``aks namespace`` (managed namespace) structure: each mutating handler
performs an existence check with a friendly error, snapshots the raw parameters via
``locals()`` and delegates model construction / SDK calls to ``aimanager.py``.
"""

from azure.cli.core.azclierror import ClientRequestError
from azure.core.exceptions import ResourceNotFoundError

from .aimanager import (
    aks_aimanager_create,
    aks_aimanager_update,
    aks_aimanager_namespace_add,
    aks_aimanager_namespace_update,
)


def _get_custom_headers(aks_custom_headers):
    from azext_aks_preview.custom import get_aks_custom_headers
    return get_aks_custom_headers(aks_custom_headers)


# region AI Manager

# pylint: disable=unused-argument
def aimanager_create(
    cmd,
    client,
    resource_group_name,
    ai_manager_name,
    location=None,
    tags=None,
    delete_policy=None,
    aks_custom_headers=None,
    no_wait=False,
):
    existedAIManager = None
    try:
        existedAIManager = client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        pass

    if existedAIManager:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' already exists. "
            "Please use 'az aimanager update' to update it."
        )

    # DO NOT MOVE: get all the original parameters and save them as a dictionary
    raw_parameters = locals()
    headers = _get_custom_headers(aks_custom_headers)
    return aks_aimanager_create(cmd, client, raw_parameters, headers, no_wait)


# pylint: disable=unused-argument
def aimanager_update(
    cmd,
    client,
    resource_group_name,
    ai_manager_name,
    tags=None,
    delete_policy=None,
    aks_custom_headers=None,
    no_wait=False,
):
    try:
        existedAIManager = client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' doesn't exist. "
            "Please use 'az aimanager list' to get the current list of AI Managers."
        )

    # DO NOT MOVE: get all the original parameters and save them as a dictionary
    raw_parameters = locals()
    headers = _get_custom_headers(aks_custom_headers)
    return aks_aimanager_update(cmd, client, raw_parameters, headers, existedAIManager, no_wait)


def aimanager_show(cmd, client, resource_group_name, ai_manager_name):  # pylint: disable=unused-argument
    return client.get(resource_group_name, ai_manager_name)


def aimanager_list(cmd, client, resource_group_name=None):  # pylint: disable=unused-argument
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


def aimanager_delete(cmd, client, resource_group_name, ai_manager_name, no_wait=False):  # pylint: disable=unused-argument
    from azure.cli.core.util import sdk_no_wait

    try:
        client.get(resource_group_name, ai_manager_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"AI Manager '{ai_manager_name}' doesn't exist. "
            "Please use 'az aimanager list' to get the current list of AI Managers."
        )

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, ai_manager_name)

# endregion


# region AI Manager namespace

# pylint: disable=unused-argument
def aimanager_namespace_add(
    cmd,
    client,
    resource_group_name,
    ai_manager_name,
    namespace_name,
    labels=None,
    annotations=None,
    aks_custom_headers=None,
    no_wait=False,
):
    existedNamespace = None
    try:
        existedNamespace = client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        pass

    if existedNamespace:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' already exists. "
            "Please use 'az aimanager namespace update' to update it."
        )

    # DO NOT MOVE: get all the original parameters and save them as a dictionary
    raw_parameters = locals()
    headers = _get_custom_headers(aks_custom_headers)
    return aks_aimanager_namespace_add(cmd, client, raw_parameters, headers, no_wait)


# pylint: disable=unused-argument
def aimanager_namespace_update(
    cmd,
    client,
    resource_group_name,
    ai_manager_name,
    namespace_name,
    labels=None,
    annotations=None,
    aks_custom_headers=None,
    no_wait=False,
):
    try:
        existedNamespace = client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' doesn't exist. "
            "Please use 'az aimanager namespace list' to get the current list of namespaces."
        )

    # DO NOT MOVE: get all the original parameters and save them as a dictionary
    raw_parameters = locals()
    headers = _get_custom_headers(aks_custom_headers)
    return aks_aimanager_namespace_update(cmd, client, raw_parameters, headers, existedNamespace, no_wait)


def aimanager_namespace_show(cmd, client, resource_group_name, ai_manager_name, namespace_name):  # pylint: disable=unused-argument
    return client.get(resource_group_name, ai_manager_name, namespace_name)


def aimanager_namespace_list(cmd, client, resource_group_name, ai_manager_name):  # pylint: disable=unused-argument
    return client.list_by_ai_manager(resource_group_name, ai_manager_name)


def aimanager_namespace_delete(cmd, client, resource_group_name, ai_manager_name, namespace_name, no_wait=False):  # pylint: disable=unused-argument
    from azure.cli.core.util import sdk_no_wait

    try:
        client.get(resource_group_name, ai_manager_name, namespace_name)
    except ResourceNotFoundError:
        raise ClientRequestError(
            f"Namespace '{namespace_name}' doesn't exist. "
            "Please use 'az aimanager namespace list' to get the current list of namespaces."
        )

    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, ai_manager_name, namespace_name)

# endregion
