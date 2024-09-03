# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azext_durabletask._client_factory import cf_durabletask, cf_durabletask_namespaces, cf_durabletask_taskhubs
from azext_durabletask.vendored_sdks.models import Namespace, TrackedResource


def create_durabletask(cmd, client, resource_group_name, durabletask_name, location=None, tags=None):
    # client = cf_durabletask(cmd.cli_ctx, None)
    raise CLIError('TODO: Implement `durabletask create`')


def list_durabletask(cmd, client, resource_group_name=None):
    # client = cf_durabletask(cmd.cli_ctx, None)
    return client.namespaces.list_by_subscription()


def update_durabletask(cmd, instance, tags=None):
    # client = cf_durabletask(cmd.cli_ctx, None)
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


# Namespace Operations
def create_namespace(cmd, client, resource_group_name, namespace_name, location="northcentralus"):
    client = cf_durabletask_namespaces(cmd.cli_ctx, None)
    return client.begin_create_or_update(resource_group_name, namespace_name, resource=Namespace(location=location))


def list_namespace(cmd, client, resource_group_name=None):
    client = cf_durabletask_namespaces(cmd.cli_ctx, None)
    return client.list_by_resource_group(resource_group_name=resource_group_name)


def show_namespace(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask namespace show`')


def delete_namespace(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask namespace delete`')


def update_namespace(cmd, instance):
    raise CLIError('TODO: Implement `durabletask namespace update`')


# Taskhub Operations
def create_taskhub(cmd, client, resource_group_name, durabletask_name, location=None):
    raise CLIError('TODO: Implement `durabletask taskhub create`')


def list_taskhub(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask taskhub list`')


def show_taskhub(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask taskhub show`')


def update_taskhub(cmd, instance):
    raise CLIError('TODO: Implement `durabletask taskhub update`')
