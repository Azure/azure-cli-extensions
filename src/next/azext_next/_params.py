# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType  # pylint: disable=unused-import


def load_arguments(self, _):  # pylint: disable=unused-argument
    with self.argument_context('next') as c:
        c.argument('scenario_only', options_list=['--scenario', '-s'], action='store_true', help='recommend e2e scenarios only')
        c.argument('command_only', options_list=['--command', '-c'], action='store_true', help='recommend commands only')
