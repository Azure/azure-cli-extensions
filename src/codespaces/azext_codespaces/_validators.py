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
