# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_ai_service._client_factory import cf_ai_service


def load_command_table(self, _):

    with self.command_group('ai_service') as g:
        g.custom_command('show capacity', 'capacity')

    with self.command_group('ai_service', is_preview=True):
        pass

