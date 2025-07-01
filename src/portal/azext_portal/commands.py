# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_command_table(self, _):

    with self.command_group('portal dashboard'):

        from .custom import Create, Update, Import
        self.command_table['portal dashboard create'] = Create(loader=self)
        self.command_table['portal dashboard update'] = Update(loader=self)
        self.command_table['portal dashboard import'] = Import(loader=self)
