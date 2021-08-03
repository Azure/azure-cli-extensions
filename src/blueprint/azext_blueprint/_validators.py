# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
#
# pylint: disable=line-too-long

from azure.cli.core.commands.client_factory import get_subscription_id


def blueprint_validator(cmd, namespace):
    namespace.resource_scope = '/providers/Microsoft.Management/managementGroups/{}'.format(
        namespace.management_group
    ) if namespace.management_group else '/subscriptions/{}'.format(
        namespace.subscription if namespace.subscription else get_subscription_id(cmd.cli_ctx))


def blueprint_assignment_validator(cmd, namespace):
    from knack.util import CLIError
    if namespace.management_group:
        raise CLIError("The management group scope for blueprint assignment is not supported yet. Please use --subscription for subscription scope.")
    namespace.resource_scope = '/subscriptions/{}'.format(namespace.subscription if namespace.subscription else get_subscription_id(cmd.cli_ctx))
    try:
        if namespace.user_assigned_identity and not namespace.identity_type:
            namespace.identity_type = 'UserAssigned'
    except AttributeError:
        pass
