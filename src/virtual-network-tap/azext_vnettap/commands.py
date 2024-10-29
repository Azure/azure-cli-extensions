# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    with self.command_group('network vnet tap'):
        from .custom import CreateVnetTap
        self.command_table['network vnet tap create'] = CreateVnetTap(loader=self)

    with self.command_group('network nic vtap-config'):
        from .custom import CreateVtapConfig
        self.command_table['network nic vtap-config create'] = CreateVtapConfig(loader=self)
