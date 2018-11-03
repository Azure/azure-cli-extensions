# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

# pylint: disable=unused-import
import azext_aks_preview._help
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW


class ContainerServiceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        register_resource_type('latest', CUSTOM_MGMT_AKS_PREVIEW, '2018-08-01-preview')

        acs_custom = CliCommandType(operations_tmpl='azext_aks_preview.custom#{}')
        super(ContainerServiceCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                             custom_command_type=acs_custom,
                                                             resource_type=CUSTOM_MGMT_AKS_PREVIEW,
                                                             min_profile='2017-03-10-profile')

    def load_command_table(self, args):
        super(ContainerServiceCommandsLoader, self).load_command_table(args)
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        # super(ContainerServiceCommandsLoader, self).load_arguments(command)
        super().load_arguments(command)
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ContainerServiceCommandsLoader
