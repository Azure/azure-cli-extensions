# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _):

    with self.command_group('managementpartner'):

        from .aaz.latest.managementpartner import Create, Delete, Update
        self.command_table['managementpartner create'] = Create(loader=self)
        self.command_table['managementpartner delete'] = Delete(loader=self)
        self.command_table['managementpartner update'] = Update(loader=self)

        from .custom import Show
        self.command_table['managementpartner show'] = Show(loader=self)
