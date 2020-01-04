# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core import AzCommandsLoader

from azext_ai_examples._help import helps  # pylint: disable=unused-import


def inject_functions_into_core():
    # Replace the default examples from help calls
    from azure.cli.core._help import AzCliHelp
    from azext_ai_examples.custom import provide_examples
    AzCliHelp.example_provider = provide_examples


class AiExamplesCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        ai_examples_custom = CliCommandType(
            operations_tmpl='azext_ai_examples.custom#{}')
        super(AiExamplesCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                       custom_command_type=ai_examples_custom)
        inject_functions_into_core()

    def load_command_table(self, args):
        from azext_ai_examples.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        pass


COMMAND_LOADER_CLS = AiExamplesCommandsLoader
