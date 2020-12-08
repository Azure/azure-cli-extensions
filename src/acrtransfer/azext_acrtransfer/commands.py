# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_acrtransfer._client_factory import cf_acrtransfer


def load_command_table(self, _):
    importpipeline_sdk = CliCommandType(
        operations_tmpl='azext_acrtransfer.vendored_sdks.containerregistry.v2019_12_01_preview.operations#ImportPipelinesOperations.{}',
        client_factory=cf_acrtransfer,
        min_api='2019-12-01-preview'
    )

    exportpipeline_sdk = CliCommandType(
        operations_tmpl='azext_acrtransfer.vendored_sdks.containerregistry.v2019_12_01_preview.operations#ExportPipelinesOperations.{}',
        client_factory=cf_acrtransfer,
        min_api='2019-12-01-preview'
    )

    pipelinerun_sdk = CliCommandType(
        operations_tmpl='azext_acrtransfer.vendored_sdks.containerregistry.v2019_12_01_preview.operations#PipelineRunsOperations.{}',
        client_factory=cf_acrtransfer,
        min_api='2019-12-01-preview'
    )

    with self.command_group('acrtransfer import-pipeline', importpipeline_sdk) as g:
        g.custom_command('create', 'create_importpipeline')
        g.custom_command('delete', 'delete_importpipeline')
        g.custom_command('list', 'list_importpipeline')
        g.custom_command('show', 'get_importpipeline')

    with self.command_group('acrtransfer export-pipeline', exportpipeline_sdk) as g:
        g.custom_command('create', 'create_exportpipeline')
        g.custom_command('delete', 'delete_exportpipeline')
        g.custom_command('list', 'list_exportpipeline')
        g.custom_command('show', 'get_exportpipeline')

    with self.command_group('acrtransfer pipeline-run', pipelinerun_sdk) as g:
        g.custom_command('create', 'create_pipelinerun')
        g.custom_command('delete', 'delete_pipelinerun')
        g.custom_command('list', 'list_pipelinerun')
        g.custom_command('show', 'get_pipelinerun')

    with self.command_group('acrtransfer', is_preview=True):
        pass
