# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands import CliCommandType
from azext_acrcache._client_factory import cf_acrcache, cf_acrreg
from ._format import import_pipeline_output_format, export_pipeline_output_format, pipeline_run_output_format


def load_command_table(self, _):

    acr_cache_util = CliCommandType(
        operations_tmpl='azext_acrcache.cache#{}',
        client_factory=cf_acrcache
    )

    with self.command_group('acr cache', acr_cache_util, is_preview=True) as g:
        g.show_command('show', 'acr_cache_show')
        g.command('create', 'acr_cache_create')
        g.command('list', 'acr_cache_list')
        g.command('delete', 'acr_cache_delete', confirmation=True)
        g.command('update', 'acr_cache_update_custom')
        g.command('sync', 'acr_cache_sync', client_factory=cf_acrreg)

        '''
        g.generic_update_command('update',
                                 getter_name='acr_cache_update_get',
                                 setter_name='acr_cache_update_set',
                                 custom_func_name='acr_cache_update_custom',
                                 custom_func_type=acr_cache_util,
                                 client_factory=cf_acrcache)'''


