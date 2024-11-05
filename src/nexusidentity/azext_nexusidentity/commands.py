# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=unused-import
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    with self.command_group('nexusidentity') as g:
        g.custom_command('gen-keys', 'generate_nexus_identity_keys')
