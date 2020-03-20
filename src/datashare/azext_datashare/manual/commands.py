# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_datashare.generated._client_factory import cf_account
    datashare_account = CliCommandType(
        operations_tmpl='azext_datashare.vendored_sdks.datashare.operations._account_operations#AccountOperations.{}',
        client_factory=cf_account)
    with self.command_group('datashare account', datashare_account, client_factory=cf_account) as g:
        g.custom_command('test', 'datashare_account_test')
        g.custom_show_command('show', 'datashare_account_show2')

