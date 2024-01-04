# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    with self.command_group('powerbi embedded-capacity', is_preview=True):
        from azext_powerbidedicated.custom import EmbeddedCapacityCreate
        self.command_table['powerbi embedded-capacity create'] = EmbeddedCapacityCreate(loader=self)
