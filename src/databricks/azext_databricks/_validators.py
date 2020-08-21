# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import random
import string


def id_generator(size=13, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_network_id(parameter_name):
    def _validate(cmd, namespace):
        from msrestazure.tools import is_valid_resource_id, resource_id
        from azure.cli.core.commands.client_factory import get_subscription_id

        subscription_id = get_subscription_id(cmd.cli_ctx)
        if getattr(namespace, parameter_name) is not None \
           and not is_valid_resource_id(getattr(namespace, parameter_name)):
            setattr(namespace, parameter_name, resource_id(
                subscription=subscription_id,
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Network',
                type='virtualNetworks',
                name=getattr(namespace, parameter_name)))

    return _validate


def validate_workspace_values(cmd, namespace):
    """Parse managed resource_group which can be either resource group name or id"""
    from msrestazure.tools import is_valid_resource_id, resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id

    random_id = id_generator()
    subscription_id = get_subscription_id(cmd.cli_ctx)
    if not namespace.managed_resource_group:
        namespace.managed_resource_group = resource_id(
            subscription=subscription_id,
            resource_group='databricks-rg-' + namespace.workspace_name + '-' +
            random_id)
    elif not is_valid_resource_id(namespace.managed_resource_group):
        namespace.managed_resource_group = resource_id(
            subscription=subscription_id,
            resource_group=namespace.managed_resource_group)

    # name to resource id for virtual-network
    validate_network_id('custom_virtual_network_id')(cmd, namespace)


def validate_encryption_values(namespace):
    from knack.util import CLIError
    if namespace.encryption_key_source:
        if namespace.encryption_key_source == 'Default' and any(v is not None for v in [namespace.encryption_key_name, namespace.encryption_key_version, namespace.encryption_key_vault]):
            raise CLIError('--key-name, --key-version, --key-vault should not be provided when --key-source is Default')
        if namespace.encryption_key_source == 'Microsoft.Keyvault' and any(v is None for v in [namespace.encryption_key_name, namespace.encryption_key_version, namespace.encryption_key_vault]):
            raise CLIError('--key-name, --key-version, --key-vault are required when --key-source is Microsoft.Keyvault')
    elif any(v is not None for v in [namespace.encryption_key_name, namespace.encryption_key_version, namespace.encryption_key_vault]):
        raise CLIError('please specify --key-source for encryption')
