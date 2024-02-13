# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    with self.command_group('databricks workspace'):
        from azext_databricks.custom import DatabricksWorkspaceCreate, DatabricksWorkspaceUpdate
        self.command_table['databricks workspace create'] = DatabricksWorkspaceCreate(loader=self)
        self.command_table['databricks workspace update'] = DatabricksWorkspaceUpdate(loader=self)

    with self.command_group('databricks workspace vnet-peering'):
        from azext_databricks.custom import WorkspaceVnetPeeringCreate
        self.command_table['databricks workspace vnet-peering create'] = WorkspaceVnetPeeringCreate(loader=self)
