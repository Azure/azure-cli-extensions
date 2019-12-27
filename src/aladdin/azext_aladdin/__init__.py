# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_aladdin._help import helps  # pylint: disable=unused-import


class AladdinCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_aladdin._client_factory import cf_aladdin
        aladdin_custom = CliCommandType(
            operations_tmpl='azext_aladdin.custom#{}',
            client_factory=cf_aladdin)
        self.inject_functions_into_core()
        super(AladdinCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    custom_command_type=aladdin_custom)

    def load_command_table(self, args):
        from azext_aladdin.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_aladdin._params import load_arguments
        load_arguments(self, command)

    def inject_functions_into_core(self):
        # Replace the default examples from help calls
        from azure.cli.core._help import AzCliHelp
        from azext_aladdin.custom import provide_examples
        AzCliHelp.example_provider = provide_examples


COMMAND_LOADER_CLS = AladdinCommandsLoader
