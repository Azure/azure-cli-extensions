# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_search_scenario._client_factory import cf_search_scenario


def load_command_table(self, _):

    with self.command_group('') as g:
        g.custom_command('search-scenario', 'search_scenario')

