# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.command_modules.acr._client_factory import cf_acr_registries
from azure.cli.command_modules.acr._format import endpoints_output_format, registry_output_format
from azext_acrregionalendpoint._client_factory import cf_acrregionalendpoint


def load_command_table_preview(self, _):
    acr_custom_util = CliCommandType(
        operations_tmpl='azext_acrregionalendpoint.custom#{}',
        table_transformer=registry_output_format,
        client_factory=cf_acrregionalendpoint
    )

    acr_login_util = CliCommandType(
        operations_tmpl='azext_acrregionalendpoint.custom#{}'
    )

    acr_import_util = CliCommandType(
        operations_tmpl='azext_acrregionalendpoint.import#{}',
        client_factory=cf_acr_registries
    )

    with self.command_group('acr', acr_custom_util) as g:
        g.command('create', 'acr_create_preview')
        g.show_command('show', 'acr_show_preview')
        g.generic_update_command('update',
                                 getter_name='acr_update_get_preview',
                                 setter_name='acr_update_set_preview',
                                 custom_func_name='acr_update_custom_preview',
                                 custom_func_type=acr_custom_util,
                                 client_factory=cf_acrregionalendpoint)
        g.command('show-endpoints', 'acr_show_endpoints_preview', table_transformer=endpoints_output_format)

    with self.command_group('acr', acr_login_util) as g:
        g.command('login', 'acr_login_preview')

    with self.command_group('acr', acr_import_util) as g:
        g.command('import', 'acr_import_preview', supports_no_wait=True)
