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
        g.custom_command('importpipeline create', 'create_importpipeline')
        g.custom_command('importpipeline delete', 'delete_importpipeline')
        g.custom_command('importpipeline list', 'list_importpipeline')
        g.custom_command('importpipeline show', 'get_importpipeline')
        g.custom_command('importpipeline update', 'update_importpipeline')

        g.custom_command('exportpipeline create', 'create_exportpipeline')
        g.custom_command('exportpipeline delete', 'delete_exportpipeline')
        g.custom_command('exportpipeline list', 'list_exportpipeline')
        g.custom_command('exportpipeline show', 'get_exportpipeline')
        g.custom_command('exportpipeline update', 'update_exportpipeline')

        g.custom_command('pipelinerun create', 'create_pipelinerun')
        g.custom_command('pipelinerun delete', 'delete_pipelinerun')
        g.custom_command('pipelinerun list', 'list_pipelinerun')
        g.custom_command('pipelinerun show', 'get_pipelinerun')
   
        #g.generic_update_command('update', setter_name='update', custom_func_name='update_acrtransfer')


    with self.command_group('acrtransfer', is_preview=True):
        pass

