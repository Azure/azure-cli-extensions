# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.util import CLIError


def validate_codespace_name_or_id(namespace):
    if bool(namespace.codespace_name) == bool(namespace.codespace_id):
        raise CLIError("usage error: --name | --id")
    return False


def validate_plan_name_or_id(cmd, namespace):
    from msrestazure.tools import is_valid_resource_id, parse_resource_id
    if namespace.plan_name and is_valid_resource_id(namespace.plan_name):
        if bool(namespace.resource_group_name):
            raise CLIError("usage error: --plan NAME --resource-group NAME | --plan ID")
        resource_id_parts = parse_resource_id(namespace.plan_name)
        namespace.resource_group_name = resource_id_parts['resource_group']
        namespace.plan_name = resource_id_parts['resource_name']
        cmd.cli_ctx.data['subscription_id'] = resource_id_parts['subscription']


def validate_secret_filter_list(namespace):
    """ Extracts multiple space-separated filters in type=value format """
    if isinstance(namespace.secret_filters, list):
        filters_list = []
        for item in namespace.secret_filters:
            filter_item = validate_secret_filter_item(item)
            if filter_item:
                filters_list.append(filter_item)
        namespace.secret_filters = filters_list


def validate_secret_filter_item(item):
    """ Extracts a single filter in type=value format """
    result = {}
    if item:
        comps = item.split('=', 1)
        if len(comps) != 2 or not comps[1]:
            raise CLIError("usage error: --filters type=value [type=value ...]")
        result = {'type': comps[0], 'value': comps[1]}
    return result
