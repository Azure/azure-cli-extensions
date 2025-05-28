# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType  # pylint: disable=unused-import


def load_arguments(self, _):  # pylint: disable=unused-argument
    with self.argument_context('next') as c:
        c.argument('scenario_only', options_list=['--scenario', '-s'], action='store_true', help='Specify this parameter will only recommend E2E scenarios')
        c.argument('command_only', options_list=['--command', '-c'], action='store_true', help='Specify this parameter will only recommend commands')
