# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType
from azext_acrtransfer._client_factory import cf_acrtransfer
from ._format import import_pipeline_output_format, export_pipeline_output_format, pipeline_run_output_format


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

    with self.command_group('acr import-pipeline', importpipeline_sdk, table_transformer=import_pipeline_output_format, is_preview=True) as g:
        g.custom_command('create', 'create_importpipeline')
        g.custom_command('delete', 'delete_importpipeline')
        g.custom_command('list', 'list_importpipeline')
        g.custom_show_command('show', 'get_importpipeline')

    with self.command_group('acr export-pipeline', exportpipeline_sdk, table_transformer=export_pipeline_output_format, is_preview=True) as g:
        g.custom_command('create', 'create_exportpipeline')
        g.custom_command('delete', 'delete_exportpipeline')
        g.custom_command('list', 'list_exportpipeline')
        g.custom_show_command('show', 'get_exportpipeline')

    with self.command_group('acr pipeline-run', pipelinerun_sdk, table_transformer=pipeline_run_output_format, is_preview=True) as g:
        g.custom_command('create', 'create_pipelinerun')
        g.custom_command('delete', 'delete_pipelinerun')
        g.custom_command('list', 'list_pipelinerun')
        g.custom_show_command('show', 'get_pipelinerun')
        g.custom_command('clean', 'clean_pipelinerun')
