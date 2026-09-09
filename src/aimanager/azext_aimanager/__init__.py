# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

# pylint: disable=unused-import
from azext_aimanager._help import helps
from azext_aimanager._client_factory import CUSTOM_MGMT_AIMANAGER


def register_aimanager_resource_type():
    # The vendored azure-mgmt-containerserviceaimanager SDK is a single-api (typespec)
    # package whose operation groups are instance attributes rather than client class
    # properties, so an SDKProfile-based lookup cannot resolve them. It is therefore
    # registered with api_version=None (no SDKProfile); the CustomResourceType import
    # prefix points at the versioned package so cmd.get_models resolves models from
    # `azext_aimanager.vendored_sdks.v2026_05_02_preview.models` directly.
    register_resource_type(
        "latest",
        CUSTOM_MGMT_AIMANAGER,
        None,
    )


class AIManagerCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        register_aimanager_resource_type()

        aimanager_custom = CliCommandType(operations_tmpl='azext_aimanager.custom#{}')
        super().__init__(cli_ctx=cli_ctx,
                         resource_type=CUSTOM_MGMT_AIMANAGER,
                         custom_command_type=aimanager_custom)

    def load_command_table(self, args):
        from azext_aimanager.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_aimanager._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AIManagerCommandsLoader
