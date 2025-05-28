# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals


def load_command_table(self, _):

    with self.command_group('monitor log-analytics solution'):
        from .custom import SolutionCreate, SolutionUpdate, SolutionDelete, SolutionShow
        self.command_table['monitor log-analytics solution create'] = SolutionCreate(loader=self)
        self.command_table['monitor log-analytics solution update'] = SolutionUpdate(loader=self)
        self.command_table['monitor log-analytics solution delete'] = SolutionDelete(loader=self)
        self.command_table['monitor log-analytics solution show'] = SolutionShow(loader=self)
