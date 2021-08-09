# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def get_action_group_validator(dest):
    def validate_action_groups(cmd, namespace):
        action_groups = getattr(namespace, dest, None)

        if not action_groups:
            return

        from msrestazure.tools import is_valid_resource_id, resource_id
        from azure.cli.core.commands.client_factory import get_subscription_id

        subscription = get_subscription_id(cmd.cli_ctx)
        resource_group = namespace.resource_group_name
        for group in action_groups:
            if not is_valid_resource_id(group.action_groups):
                group.action_groups = resource_id(
                    subscription=subscription,
                    resource_group=resource_group,
                    namespace='microsoft.insights',
                    type='actionGroups',
                    name=group.action_groups
                )
    return validate_action_groups
