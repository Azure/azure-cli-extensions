# pylint: disable-all

# ---------------------------------------------------------------------------------
# The code for this extension file is pulled from the azure-cli repo and
# modified to run inside a cli extension.  Changes may cause incorrect behavior and
# will be lost if the code is regenerated. Please see the readme.md at the base of
# the keyvault extension for details.
# ---------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_keyvault._help  # pylint: disable=unused-import


class KeyVaultCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from ._client_factory import keyvault_client_factory
        from ._command_type import KeyVaultCommandGroup, KeyVaultArgumentContext
        keyvault_custom = CliCommandType(
            operations_tmpl='azext_keyvault.custom#{}',
            client_factory=keyvault_client_factory
        )
        super(KeyVaultCommandsLoader, self).__init__(cli_ctx=cli_ctx,
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
