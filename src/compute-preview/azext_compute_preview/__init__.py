# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type
from azext_compute_preview._client_factory import CUSTOM_MGMT_COMPUTE

from azext_compute_preview._help import helps  # pylint: disable=unused-import


class ComputePreviewCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        register_resource_type('latest', CUSTOM_MGMT_COMPUTE, '2019-12-01')
        compute_preview_custom = CliCommandType(
            operations_tmpl='azext_compute_preview.custom#{}'
        )
        super(ComputePreviewCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                           resource_type=CUSTOM_MGMT_COMPUTE,
                                                           custom_command_type=compute_preview_custom)

    def load_command_table(self, args):
        from azext_compute_preview.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_compute_preview._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ComputePreviewCommandsLoader
