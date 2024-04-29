# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.command_modules.acr._format import registry_output_format
from azext_acrabac._client_factory import cf_acrabac


def load_command_table(self, _):

    acr_custom_util = CliCommandType(
        operations_tmpl='azext_acrabac.custom#{}',
        table_transformer=registry_output_format,
        client_factory=cf_acrabac
    )

    with self.command_group('acr', acr_custom_util) as g:
        g.command('create', 'acr_create_preview')
        # TODO: @m5i: consider add list (to show extra property)
        g.generic_update_command('update',
                                 getter_name='acr_update_get_preview',
                                 setter_name='acr_update_set_preview',
                                 custom_func_name='acr_update_custom_preview',
                                 custom_func_type=acr_custom_util,
                                 client_factory=cf_acrabac)
