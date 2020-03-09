# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def blueprint_validator(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    import json

    namespace.scope = '/providers/Microsoft.Management/managementGroups/{}'.format(
        namespace.management_group
    ) if namespace.management_group is not None else '/subscriptions/{}'.format(
        get_subscription_id(cmd.cli_ctx))

    if hasattr(namespace, 'parameters') and namespace.parameters is not None and isinstance(namespace.parameters, str):
        namespace.parameters = json.loads(namespace.parameters)

    if hasattr(namespace, 'template') and namespace.template is not None and isinstance(namespace.template, str):
        namespace.template = json.loads(namespace.template)
