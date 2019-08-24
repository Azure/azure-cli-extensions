# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_services
    healthcare_services = CliCommandType(
        operations_tmpl='azext_healthcare.vendored_sdks.healthcareapis.operations.services_operations#ServicesOperations.{}',
        client_factory=cf_services)
    with self.command_group('healthcare', healthcare_services, client_factory=cf_services) as g:
        g.custom_command('create', 'create_healthcare')
        g.generic_update_command('update', custom_func_name='update_healthcare')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_healthcare')
        g.show_command('show', 'get')
