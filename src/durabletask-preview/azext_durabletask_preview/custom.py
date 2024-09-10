# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azext_durabletask_preview._client_factory import cf_durabletask_namespaces, cf_durabletask_taskhubs
from azext_durabletask_preview.vendored_sdks.models import Namespace, TaskHub


# Namespace Operations
def create_namespace(cmd, client, resource_group_name, namespace_name, location="northcentralus"):
    client = cf_durabletask_namespaces(cmd.cli_ctx)
    return client.begin_create_or_update(resource_group_name, namespace_name, resource=Namespace(location=location))


def list_namespace(cmd, client, resource_group_name=None):
    client = cf_durabletask_namespaces(cmd.cli_ctx)
    return client.list_by_resource_group(resource_group_name=resource_group_name)


def show_namespace(cmd, client, resource_group_name=None, namespace_name=None):
    client = cf_durabletask_namespaces(cmd.cli_ctx)
    return client.get(resource_group_name=resource_group_name, namespace_name=namespace_name)


def delete_namespace(cmd, client, resource_group_name=None, namespace_name=None):
    client = cf_durabletask_namespaces(cmd.cli_ctx)
    return client.begin_delete(resource_group_name, namespace_name)


def update_namespace(cmd, instance):
    raise CLIError('TODO: Implement `durabletask namespace update`')


# Taskhub Operations
def create_taskhub(cmd, client, resource_group_name, namespace_name, task_hub_name, location=None):
    client = cf_durabletask_taskhubs(cmd.cli_ctx)
    return client.create_or_update(resource_group_name, namespace_name, task_hub_name,
                                   resource=TaskHub(location=location))


def list_taskhub(cmd, client, resource_group_name, namespace_name=None):
    client = cf_durabletask_taskhubs(cmd.cli_ctx)
    return client.list_by_namespace(resource_group_name=resource_group_name, namespace_name=namespace_name)


def show_taskhub(cmd, client, resource_group_name, namespace_name=None, task_hub_name=None):
    client = cf_durabletask_taskhubs(cmd.cli_ctx)
    return client.get(resource_group_name=resource_group_name, namespace_name=namespace_name,
                      task_hub_name=task_hub_name)


def delete_taskhub(cmd, client, resource_group_name, namespace_name, task_hub_name):
    client = cf_durabletask_taskhubs(cmd.cli_ctx)
    return client.delete(resource_group_name, namespace_name, task_hub_name)


def update_taskhub(cmd, instance):
    raise CLIError('TODO: Implement `durabletask taskhub update`')
