# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_subscription_id


def get_network_resource_name_or_id(dest, res_type):

    def validate_name_or_id(cmd, namespace):

        dest_val = getattr(namespace, dest, None)
        if not dest_val:
            return

        is_list = isinstance(dest_val, list)
        if not is_list:
            dest_val = [dest_val]

        id_list = []

        from msrestazure.tools import is_valid_resource_id, resource_id
        for item in dest_val:
            if not is_valid_resource_id(item):
                item = resource_id(
                    subscription=get_subscription_id(cmd.cli_ctx),
                    resource_group=namespace.resource_group_name,
                    namespace='Microsoft.Network',
                    type=res_type,
                    name=item
                )
            id_list.append(item)
        setattr(namespace, dest, id_list if is_list else id_list[0])

    return validate_name_or_id
