﻿# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands import CliCommandType
from ._client_factory import managementpartner_partner_client_factory
from ._exception_handler import managementpartner_exception_handler


def load_command_table(self, _):
    def managementpartner_type(*args, **kwargs):
        return CliCommandType(*args, exception_handler=managementpartner_exception_handler, **kwargs)

    managementpartner_partner_sdk = managementpartner_type(
        operations_tmpl='azext_managementpartner.managementpartner.operations.partner_operations#PartnerOperations.{}',
        client_factory=managementpartner_partner_client_factory
    )

    with self.command_group('managementpartner', managementpartner_partner_sdk) as g:
        g.custom_command('delete', 'delete_managementpartner')
        g.custom_command('create', 'create_managementpartner')
        g.custom_command('update', 'update_managementpartner')
        g.custom_show_command('show', 'get_managementpartner')
