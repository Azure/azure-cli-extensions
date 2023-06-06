# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_custom_location_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id

    if not namespace.custom_location or not namespace.resource_group_name:
        return

    if not is_valid_resource_id(namespace.custom_location):
        namespace.custom_location = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.ExtendedLocation',
            type='customLocations',
            name=namespace.custom_location
        )
