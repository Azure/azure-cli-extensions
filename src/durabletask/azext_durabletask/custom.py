# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azext_durabletask._client_factory import cf_durabletask, cf_durabletask_namespaces, cf_durabletask_taskhubs
from azext_durabletask.vendored_sdks.models import Namespace, TrackedResource

def create_durabletask(cmd, client, resource_group_name, durabletask_name, location=None, tags=None):
    client = cf_durabletask(cmd.cli_ctx, None)
    raise CLIError('TODO: Implement `durabletask create`')


def list_durabletask(cmd, client, resource_group_name=None):
    client = cf_durabletask(cmd.cli_ctx, None)
    return client.namespaces.list_by_subscription()
    # raise CLIError('TODO: Implement `durabletask list`')


def update_durabletask(cmd, instance, tags=None):
    client = cf_durabletask(cmd.cli_ctx, None)
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


# Namespace Operations
def create_namespace(cmd, client, resource_group_name, durabletask_name, location=None, tags=None):
    namespace = TrackedResource(location='eastus')
    client = cf_durabletask_namespaces(cmd.cli_ctx, None)
    return client.begin_create_or_update(resource_group_name, "test-namespace-api", resource=Namespace(location="eastus"))
    raise CLIError('TODO: Implement `durabletask namespace create`')

def list_namespace(cmd, client, resource_group_name=None):
    client = cf_durabletask_namespaces(cmd.cli_ctx, None)
    return client.list_by_resource_group(resource_group_name="test-rp-rg-eastus")
    raise CLIError('TODO: Implement `durabletask namespace list`')

def show_namespace(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask namespace show`')

def delete_namespace(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask namespace delete`')

def update_namespace(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance


# Taskhub Operations
def create_taskhub(cmd, client, resource_group_name, durabletask_name, location=None, tags=None):
    raise CLIError('TODO: Implement `durabletask taskhub create`')


def list_taskhub(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask taskhub list`')

def show_taskhub(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `durabletask taskhub show`')

def update_taskhub(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance