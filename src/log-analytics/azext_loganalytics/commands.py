# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_command_table(self, _):

    with self.command_group('monitor log-analytics') as g:
        g.custom_command('query', 'execute_query')
