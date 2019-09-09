# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.validators import validate_tag
from azure.cli.core.util import CLIError
from msrestazure.tools import is_valid_resource_id
from re import match
from ._utils import ApiType


def example_name_or_id_validator(cmd, namespace):
    # Example of a storage account name or ID validator.
    # See: https://github.com/Azure/azure-cli/blob/dev/doc/authoring_command_modules/authoring_commands.md#supporting-name-or-id-parameters
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id


def validate_env(namespace):
    """ Extracts multiple space-separated envs in key[=value] format """
    if isinstance(namespace.env, list):
        env_dict = {}
        for item in namespace.env:
            env_dict.update(validate_tag(item))
        namespace.env = env_dict


def validate_key_type(namespace):
    key_type = namespace.type.lower()
    if key_type != 'primary' and key_type != 'secondary':
        raise CLIError('--key-type only accepts "Primary" or "Secondary"')
    key_type = key_type[:1].upper() + key_type[1:]
    namespace.type = key_type


def validate_name(namespace):
    namespace.name = namespace.name.lower()
    matchObj = match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])$', namespace.name)
    if matchObj is None:
        raise CLIError('--name can only contain numbers and lowercases')


def validate_app_name(namespace):
    if namespace.app is not None:
        namespace.app = namespace.app.lower()
        matchObj = match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])$', namespace.app)
        if matchObj is None:
            raise CLIError(
                'invalid app name, --app can only contain numbers and lowercases')


def validate_deployment_name(namespace):
    if namespace.deployment is not None:
        namespace.deployment = namespace.deployment.lower()
        if namespace.deployment is None:
            return
        from re import match
        matchObj = match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])$', namespace.deployment)
        if matchObj is None:
            raise CLIError(
                'invalid deployment name, --deployment can only contain numbers and lowercases')


def validate_resource_id(namespace):
    if not is_valid_resource_id(namespace.resource_id):
        raise CLIError("Invalid resource id %s", namespace.resource_id)


def validate_cosmos_type(namespace):
    if namespace.api_type is None:
        return
    type = ApiType(namespace.api_type)
    if type == ApiType.mongo or type == ApiType.sql or type == ApiType.gremlin:
        if namespace.database_name is None:
            raise CLIError(
                "Cosmosdb with type {} should specify database name".format(type))

    if type == ApiType.cassandra:
        if namespace.key_space is None:
            raise CLIError(
                "Cosmosdb with type {} should specify key space".format(type))

    if type == ApiType.gremlin:
        if namespace.key_space is None:
            raise CLIError(
                "Cosmosdb with type {} should specify collection name".format(type))

def validate_nodes_count(namespace):
    """Validate that cpu, memory and instance-count is set in a range"""
    if namespace.cpu is not None:
        if namespace.cpu < 1 or namespace.cpu > 4:
            raise CLIError('--cpu must be in the range [1,4]')
    if namespace.memory is not None:
        if namespace.memory < 1 or namespace.memory > 8:
            raise CLIError('--memory must be in the range [1,8]')
    if namespace.instance_count is not None:
        if namespace.instance_count < 1 or namespace.instance_count > 20:
            raise CLIError('--instance-count must be in the range [1,20]')
