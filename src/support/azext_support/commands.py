# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_support._client_factory import (cf_communications,
                                           cf_problem_classifications,
                                           cf_services, cf_support,
                                           cf_support_tickets)
from azext_support._validators import validate_tickets_create
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    support = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks#MicrosoftSupport.{}',
        client_factory=cf_support)
    support_services = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#ServicesOperations.{}',
        client_factory=cf_services)
    support_problem_classifications = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#ProblemClassificationsOperations.{}',
        client_factory=cf_problem_classifications)
    support_tickets = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#SupportTicketsOperations.{}',
        client_factory=cf_support_tickets)
    support_communications = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#CommunicationsOperations.{}',
        client_factory=cf_communications)

    self.command_group('support', support, client_factory=cf_support)

    with self.command_group('support services', support_services, client_factory=cf_services) as g:
        g.command('list', method_name='list')
        g.show_command('show', getter_name='get')

    with self.command_group('support services problem-classifications', support_problem_classifications,
                            client_factory=cf_problem_classifications) as g:
        g.command('list', method_name='list')
        g.show_command('show', getter_name='get')

    with self.command_group('support tickets', support_tickets,
                            client_factory=cf_support_tickets) as g:
        g.custom_command('list', 'list_support_tickets')
        g.custom_command('show', 'get_support_tickets')
        g.custom_command('create', 'create_support_tickets', supports_no_wait=False, validator=validate_tickets_create)
        g.custom_command('update', 'update_support_tickets')

    with self.command_group('support tickets communications', support_communications,
                            client_factory=cf_communications) as g:
        g.custom_command('list', 'list_support_tickets_communications')
        g.custom_command('show', 'get_support_tickets_communications')
        g.custom_command('create', 'create_support_tickets_communications', supports_no_wait=False)
