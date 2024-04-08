# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys

from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.util import sdk_no_wait


from ._client_factory import network_client_factory


def _get_property(items, name):
    result = next((x for x in items if x.name.lower() == name.lower()), None)
    if not result:
        raise ArgumentUsageError(f"Property '{name}' does not exist")
    return result


def _set_param(item, prop, value):
    if value == '':
        setattr(item, prop, None)
    elif value is not None:
        setattr(item, prop, value)


def list_network_resource_property(resource, prop):
    """ Factory method for creating list functions. """

    def list_func(cmd, resource_group_name, resource_name):
        client = getattr(network_client_factory(cmd.cli_ctx), resource)
        return getattr(client.get(resource_group_name, resource_name), prop)

    func_name = f"list_network_resource_property_{resource}_{prop}"
    setattr(sys.modules[__name__], func_name, list_func)
    return func_name


def get_network_resource_property_entry(resource, prop):
    """ Factory method for creating get functions. """

    def get_func(cmd, resource_group_name, resource_name, item_name):
        client = getattr(network_client_factory(cmd.cli_ctx), resource)
        items = getattr(client.get(resource_group_name, resource_name), prop)

        result = next((x for x in items if x.name.lower() == item_name.lower()), None)
        if not result:
            raise ArgumentUsageError(f"Item '{item_name}' does not exist on {resource} '{resource_name}'")
        return result

    func_name = f"get_network_resource_property_entry_{resource}_{prop}"
    setattr(sys.modules[__name__], func_name, get_func)
    return func_name


def delete_network_resource_property_entry(resource, prop):
    """ Factory method for creating delete functions. """

    def delete_func(cmd, resource_group_name, resource_name, item_name, no_wait=False):  # pylint: disable=unused-argument
        client = getattr(network_client_factory(cmd.cli_ctx), resource)
        item = client.get(resource_group_name, resource_name)
        keep_items = \
            [x for x in getattr(item, prop) if x.name.lower() != item_name.lower()]
        _set_param(item, prop, keep_items)
        if no_wait:
            sdk_no_wait(no_wait, client.create_or_update, resource_group_name, resource_name, item)
        else:
            result = sdk_no_wait(no_wait, client.create_or_update, resource_group_name, resource_name, item).result()
            if next((x for x in getattr(result, prop) if x.name.lower() == item_name.lower()), None):
                raise ArgumentUsageError(f"Failed to delete '{item_name}' on '{resource_name}'")

    func_name = f"delete_network_resource_property_entry_{resource}_{prop}"
    setattr(sys.modules[__name__], func_name, delete_func)
    return func_name
