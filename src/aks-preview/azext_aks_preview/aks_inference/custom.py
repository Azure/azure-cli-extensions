# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Custom command implementations — the hand-written equivalent of functions in `custom.py`.

Compare with the AAZ approach: here YOU build the model, call the SDK method, and
return the (poller) result. LRO/paging come from the SDK, not from generated command files.
"""

from .vendored_sdk import models


def aks_inference_create(cmd, client, resource_group_name, ai_manager_name, location=None,
                         tags=None, delete_policy=None, no_wait=False):
    from azure.cli.core.commands import LongRunningOperation

    parameters = models.AIManager(
        location=location,
        tags=tags,
        properties=models.AIManagerProperties(delete_policy=delete_policy),
    )
    poller = client.begin_create_or_update(resource_group_name, ai_manager_name, parameters)
    if no_wait:
        return poller
    return LongRunningOperation(cmd.cli_ctx)(poller)


def aks_inference_show(cmd, client, resource_group_name, ai_manager_name):
    return client.get(resource_group_name, ai_manager_name)


def aks_inference_delete(cmd, client, resource_group_name, ai_manager_name, no_wait=False):
    from azure.cli.core.commands import LongRunningOperation

    poller = client.begin_delete(resource_group_name, ai_manager_name)
    if no_wait:
        return poller
    return LongRunningOperation(cmd.cli_ctx)(poller)


def aks_inference_list(cmd, client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


def aks_inference_namespace_create(cmd, client, resource_group_name, ai_manager_name,
                                   namespace_name, labels=None, annotations=None, no_wait=False):
    from azure.cli.core.commands import LongRunningOperation

    parameters = models.AIManagerNamespace(
        properties=models.AIManagerNamespaceProperties(labels=labels, annotations=annotations),
    )
    poller = client.begin_create_or_update(
        resource_group_name, ai_manager_name, namespace_name, parameters)
    if no_wait:
        return poller
    return LongRunningOperation(cmd.cli_ctx)(poller)


def aks_inference_namespace_show(cmd, client, resource_group_name, ai_manager_name, namespace_name):
    return client.get(resource_group_name, ai_manager_name, namespace_name)


def aks_inference_namespace_delete(cmd, client, resource_group_name, ai_manager_name,
                                   namespace_name, no_wait=False):
    from azure.cli.core.commands import LongRunningOperation

    poller = client.begin_delete(resource_group_name, ai_manager_name, namespace_name)
    if no_wait:
        return poller
    return LongRunningOperation(cmd.cli_ctx)(poller)


def aks_inference_namespace_list(cmd, client, resource_group_name, ai_manager_name):
    return client.list_by_ai_manager(resource_group_name, ai_manager_name)
