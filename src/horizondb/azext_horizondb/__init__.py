# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader


class HorizonDBCommandsLoader(AzCommandsLoader):

    def load_command_table(self, args):
        from azure.cli.core.aaz import load_aaz_command_table
        from . import aaz

        load_aaz_command_table(
            loader=self,
            aaz_pkg_name=aaz.__name__,
            args=args
        )
        from .custom import ClusterCreate
        self.command_table['horizondb cluster create'] = ClusterCreate(loader=self)
        return self.command_table

    def load_arguments(self, command):
        pass


COMMAND_LOADER_CLS = HorizonDBCommandsLoader
