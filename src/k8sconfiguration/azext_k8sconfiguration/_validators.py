# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def example_name_or_id_validator(cmd, namespace):
    # Example of a storage account name or ID validator.
    # See: https://github.com/Azure/azure-cli/blob/dev/doc/authoring_command_modules/
    # authoring_commands.md#supporting-name-or-id-parameters
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id
    if namespace.storage_account:
        if not is_valid_resource_id(namespace.RESOURCE):
            namespace.storage_account = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Storage',
                type='storageAccounts',
                name=namespace.storage_account
            )


def validate_configuration_type(namespace):
    if namespace.configuration_type.lower() != 'sourcecontrolconfiguration':
        raise CLIError('Invalid configuration-type.  Valid value is "sourceControlConfiguration"')


def validate_operator_scope(namespace):
    if namespace.cluster_scoped:
        namespace.operator_scope = 'cluster'
    else:
        # Operator Namespace is mandatory if the Operator Scope is 'namespace'
        if namespace.operator_namespace.string() is None:
            raise CLIError('Invalid operator-namespace.  Namespace is mandatory if the scope is "namespace"')
        namespace.operator_scope = 'namespace'
