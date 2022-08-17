# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import is_valid_resource_id, resource_id


def get_resource_id(
    cmd,
    resource_group_name,
    provider_name_space,
    resource_type,
    resource,
    child_type_1=None,
    child_name_1=None,
):
    """
    Gets the resource id for the resource if name is given.
    """

    _resource_id = None
    if child_type_1 and child_name_1:
        if not is_valid_resource_id(child_name_1):
            resource = resource.split('/')[-1]
            _resource_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=resource_group_name,
                namespace=provider_name_space,
                type=resource_type,
                name=resource,
                child_type_1=child_type_1,
                child_name_1=child_name_1,
            )
        else:
            _resource_id = child_name_1
    else:
        if not is_valid_resource_id(resource):
            _resource_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=resource_group_name,
                namespace=provider_name_space,
                type=resource_type,
                name=resource,
            )
        else:
            _resource_id = resource
    return _resource_id


def create_dictionary_from_arg_string(values, option_string=None):
    """
    Creates and returns dictionary from a string containing params in KEY=VALUE format.
    """
    params_dict = {}
    for item in values:
        try:
            key, value = item.split('=', 1)
            params_dict[key.lower()] = value
        except ValueError as item_no_exist:
            raise CLIError(
                f'usage error: {option_string} KEY=VALUE [KEY=VALUE ...]'
            ) from item_no_exist
    return params_dict
