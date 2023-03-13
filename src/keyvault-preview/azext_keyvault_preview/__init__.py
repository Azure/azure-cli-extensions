# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type
import azext_keyvault_preview._help  # pylint: disable=unused-import
from .profiles import CUSTOM_MGMT_KEYVAULT


class KeyVaultCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from ._client_factory import keyvault_mgmt_client_factory
        from azure.cli.command_modules.keyvault._command_type import KeyVaultCommandGroup, KeyVaultArgumentContext

        register_resource_type('latest', CUSTOM_MGMT_KEYVAULT, '2021-12-01-preview')

        keyvault_custom = CliCommandType(
            operations_tmpl='azext_keyvault_preview.custom#{}',
            client_factory=keyvault_mgmt_client_factory
        )

        super(KeyVaultCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            resource_type=CUSTOM_MGMT_KEYVAULT,
            custom_command_type=keyvault_custom,
            command_group_cls=KeyVaultCommandGroup,
            argument_context_cls=KeyVaultArgumentContext)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = KeyVaultCommandsLoader
