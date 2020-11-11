# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_acrtransfer._client_factory import cf_acrtransfer


def load_command_table(self, _):

    acrtransfer_sdk = CliCommandType(
        operations_tmpl='azext_acrtransfer.vendored_sdks.operations#ImportPipelinesOperations.{}',
        client_factory=cf_acrtransfer)


    with self.command_group('acrtransfer', acrtransfer_sdk, client_factory=cf_acrtransfer) as g:
        g.custom_command('create', 'create_acrtransfer')
        g.custom_command('delete', 'delete_acrtransfer')
        g.custom_command('list', 'list_acrtransfer')
        g.custom_command('show', 'get_acrtransfer')
        g.generic_update_command('update', setter_name='update', custom_func_name='update_acrtransfer')


    with self.command_group('acrtransfer', is_preview=True):
        pass

