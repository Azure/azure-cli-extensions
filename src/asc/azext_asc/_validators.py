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
    key_type = namespace.key_type.lower()
    if key_type != 'primary' or type != 'secondary':
        raise CLIError('--key-type can only contain "Primary" or "Secondary"')
    key_type = key_type[:1].upper + key_type[1:]
    namespace.key_type = key_type

def validate_name(namespace):
    matchObj = match( r'^[a-z0-9]([-a-z0-9]*[a-z0-9])$', namespace.name)
    if matchObj == False:
        raise CLIError('--name can only contain numbers and lowercases')

def validate_app_name(namespace):
    matchObj = match( r'^[a-z0-9]([-a-z0-9]*[a-z0-9])$', namespace.app)
    if matchObj == False:
        raise CLIError('invalid app name, --app can only contain numbers and lowercases')

def validate_deployment_name(namespace):
    if namespace.deployment is None:
        return
    from re import match
    matchObj = match( r'^[a-z0-9]([-a-z0-9]*[a-z0-9])$', namespace.deployment)
    if matchObj == False:
        raise CLIError('invalid deployment name, --deployment can only contain numbers and lowercases')

def validate_resource_id(namespace):
    if not is_valid_resource_id(namespace.resource_id):
        raise CLIError("Invalid resource id %s", namespace.resource_id)

def validate_cosmos_type(namespace):
    if namespace.api_type is None:
            return
    type = namespace.api_type
    if type == ApiType.mongo or type == ApiType.sql or type == ApiType.gremlin:
        if namespace.database_name is None:
            raise CLIError("Cosmosdb with type %s should specify database name", type)
    
    if type == ApiType.cassandra:
        if namespace.key_space is None:
            raise CLIError("Cosmosdb with type %s should specify key space", type)

    if type == ApiType.cassandra:
        if namespace.key_space is None:
            raise CLIError("Cosmosdb with type %s should specify key space", type)

    if type == ApiType.gremlin:
        if namespace.key_space is None:
            raise CLIError("Cosmosdb with type %s should specify collection name", type)
