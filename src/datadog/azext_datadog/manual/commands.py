# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    datadog_link = CliCommandType(operations_tmpl='azure.cli.extension.datadog.link#{}')
    with self.command_group('datadog link', datadog_link, is_experimental=True) as g:
        g.custom_command('create', 'datadog_link_create')
