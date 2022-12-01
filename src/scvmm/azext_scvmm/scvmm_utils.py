# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import is_valid_resource_id, resource_id
from azext_scvmm.scvmm_constants import (
    EXTENDED_LOCATION_TYPE,
)
from .vendored_sdks.models import (
    ExtendedLocation,
)


def get_resource_id(
    cmd,
    resource_group_name: str,
    provider_name_space: str,
    resource_type: str,
    resource: str,
):
    """
    Gets the resource id for the resource if name is given.
    """

    if resource is None or is_valid_resource_id(resource):
        return resource
    return resource_id(
        subscription=get_subscription_id(cmd.cli_ctx),
        resource_group=resource_group_name,
        namespace=provider_name_space,
        type=resource_type,
        name=resource,
    )


def create_dictionary_from_arg_string(values, option_string=None):
    """
    Creates and returns dictionary from a string containing params in KEY=VALUE format.
    """
    params_dict = {}
    for item in values:
        try:
            key, value = item.split('=', 1)
            params_dict[key.lower()] = value
        except ValueError as err:
            raise InvalidArgumentValueError(
                f'usage error: {option_string} KEY=VALUE [KEY=VALUE ...]'
            ) from err
    return params_dict


def get_extended_location(custom_location):
    return ExtendedLocation(
        type=EXTENDED_LOCATION_TYPE,
        name=custom_location,
    )
