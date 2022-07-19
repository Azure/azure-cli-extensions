# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_search_scenario._help import helps  # pylint: disable=unused-import


class SearchScenarioCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_search_scenario._client_factory import cf_search_scenario
        search_scenario_custom = CliCommandType(
            operations_tmpl='azext_search_scenario.custom#{}',
            client_factory=cf_search_scenario)
        super(SearchScenarioCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=search_scenario_custom)

    def load_command_table(self, args):
        from azext_search_scenario.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_search_scenario._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = SearchScenarioCommandsLoader
