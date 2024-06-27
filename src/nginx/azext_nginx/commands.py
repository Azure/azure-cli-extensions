# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

def load_command_table(self, _):  # pylint: disable=unused-argument
    with self.command_group('nginx deployment configuration') as g:
        from .custom import ConfigurationUpdate
        self.command_table["nginx deployment configuration update"] = ConfigurationUpdate(loader=self)
        
