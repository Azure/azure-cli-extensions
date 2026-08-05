# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Custom command implementations for the AI Manager commands.

These build the vendored SDK models, call the operation-group methods and return the
result (or the poller when ``--no-wait`` is passed).
"""

from azure.cli.core.commands import LongRunningOperation

from .vendored_sdk import models


def _wait(cmd, poller, no_wait):
    if no_wait:
        return poller
    return LongRunningOperation(cmd.cli_ctx)(poller)


# region AI Manager

def aimanager_create(cmd, client, resource_group_name, ai_manager_name, location=None,
                     tags=None, delete_policy=None, no_wait=False):
    resource = models.AIManager(
        location=location,
        tags=tags,
        properties=models.AIManagerProperties(delete_policy=delete_policy),
    )
    poller = client.begin_create_or_update(resource_group_name, ai_manager_name, resource)
    return _wait(cmd, poller, no_wait)


def aimanager_update(cmd, client, resource_group_name, ai_manager_name, tags=None):
    properties = models.AIManagerPatch(tags=tags)
    return client.update(resource_group_name, ai_manager_name, properties)


def aimanager_show(cmd, client, resource_group_name, ai_manager_name):
    return client.get(resource_group_name, ai_manager_name)


def aimanager_delete(cmd, client, resource_group_name, ai_manager_name, no_wait=False):
    poller = client.begin_delete(resource_group_name, ai_manager_name)
    return _wait(cmd, poller, no_wait)


def aimanager_list(cmd, client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()

# endregion


# region AI Manager namespace

def aimanager_namespace_add(cmd, client, resource_group_name, ai_manager_name, namespace_name,
                            labels=None, annotations=None, no_wait=False):
    resource = models.AIManagerNamespace(
        properties=models.AIManagerNamespaceProperties(labels=labels, annotations=annotations),
    )
    poller = client.begin_create_or_update(
        resource_group_name, ai_manager_name, namespace_name, resource)
    return _wait(cmd, poller, no_wait)


def aimanager_namespace_update(cmd, client, resource_group_name, ai_manager_name, namespace_name,
                               labels=None, annotations=None, no_wait=False):
    existing = client.get(resource_group_name, ai_manager_name, namespace_name)
    properties = existing.properties or models.AIManagerNamespaceProperties()
    if labels is not None:
        properties.labels = labels
    if annotations is not None:
        properties.annotations = annotations
    resource = models.AIManagerNamespace(properties=properties)
    poller = client.begin_create_or_update(
        resource_group_name, ai_manager_name, namespace_name, resource)
    return _wait(cmd, poller, no_wait)


def aimanager_namespace_show(cmd, client, resource_group_name, ai_manager_name, namespace_name):
    return client.get(resource_group_name, ai_manager_name, namespace_name)


def aimanager_namespace_delete(cmd, client, resource_group_name, ai_manager_name,
                               namespace_name, no_wait=False):
    poller = client.begin_delete(resource_group_name, ai_manager_name, namespace_name)
    return _wait(cmd, poller, no_wait)


def aimanager_namespace_list(cmd, client, resource_group_name, ai_manager_name):
    return client.list_by_ai_manager(resource_group_name, ai_manager_name)

# endregion
