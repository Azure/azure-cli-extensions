# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

# pylint: disable=unused-import
import azext_aks_preview._help
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW


def register_aks_preview_resource_type():
    register_resource_type(
        "latest",
        CUSTOM_MGMT_AKS_PREVIEW,
        None,
    )


class ContainerServiceCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        register_aks_preview_resource_type()

        acs_custom = CliCommandType(operations_tmpl='azext_aks_preview.custom#{}')
        super().__init__(
            cli_ctx=cli_ctx,
            custom_command_type=acs_custom,
            resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        )

    def load_command_table(self, args):
        super().load_command_table(args)

        # Load AAZ-generated commands from the preview API
        from azure.cli.core.aaz import load_aaz_command_table
        try:
            from . import aaz
        except ImportError:
            aaz = None
        if aaz:
            load_aaz_command_table(
                loader=self,
                aaz_pkg_name=aaz.__name__,
                args=args
            )

        # Load custom command implementations (will override AAZ commands)
        from azext_aks_preview.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super().load_arguments(command)
        from azext_aks_preview._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ContainerServiceCommandsLoader
