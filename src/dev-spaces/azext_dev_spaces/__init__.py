# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_dev_spaces._help  # pylint: disable=unused-import
import azext_dev_spaces.custom  # pylint: disable=unused-import


class DevspacesExtCommandLoader(AzCommandsLoader):  # pylint:disable=too-few-public-methods

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        dev_spaces_custom = CliCommandType(
            operations_tmpl='azext_dev_spaces.custom#{}')
        super(DevspacesExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                        custom_command_type=dev_spaces_custom)


COMMAND_LOADER_CLS = DevspacesExtCommandLoader
