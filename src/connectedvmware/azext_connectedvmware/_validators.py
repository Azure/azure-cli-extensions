# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from operator import and_, xor
from azure.cli.core.azclierror import (
    ValidationError
)
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import is_valid_resource_id


def process_missing_vm_resource_parameters(cmd, namespace):
    err_msg = (
        "Invalid machine id provided. "
        "Expected format: '/subscriptions/01234567-0123-0123-0123-0123456789ab"
        "/resourceGroups/contoso-rg/providers/Microsoft.HybridCompute/machines/contoso-vm'."
    )

    def exists(val):
        return val is not None

    if not and_(
        xor(
            exists(namespace.machine_id),
            and_(exists(namespace.resource_group_name), exists(namespace.resource_name))
        ),
        not xor(
            exists(namespace.resource_group_name),
            exists(namespace.resource_name)
        )
    ):
        raise ValidationError(
            "Please specify either (--machine-id) or (--resource-group-name and --resource-name) but not both."
        )

    if not exists(namespace.machine_id):
        return

    if not is_valid_resource_id(namespace.machine_id):
        raise ValidationError(err_msg)
    import re
    machine_id_pattern = re.compile(r"^/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.HybridCompute/machines/([^/]+)$")  # noqa: E501 pylint: disable=line-too-long
    match = machine_id_pattern.match(namespace.machine_id)
    if not match:
        raise ValidationError(err_msg)
    subscription_id = match.group(1)
    resource_group_name = match.group(2)
    resource_name = match.group(3)

    cli_sub = get_subscription_id(cmd.cli_ctx)
    if subscription_id != cli_sub:
        raise ValidationError(
            f"Subscription id of the machine, '{subscription_id}', "
            f"does not match the current subscription, '{cli_sub}'. "
            f"Please use or switch to the correct subscription."
        )

    namespace.resource_group_name = resource_group_name
    namespace.resource_name = resource_name
