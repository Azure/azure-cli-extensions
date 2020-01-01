# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_support._client_factory import cf_services
    support_services = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#ServicesOperations.{}',
        client_factory=cf_services)
    with self.command_group('support services', support_services, client_factory=cf_services, is_preview=True) as g:
        g.command('list', method_name='list')
        g.show_command('show', getter_name='get')

    from azext_support._client_factory import cf_problem_classifications
    support_problem_classifications = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#ProblemClassificationsOperations.{}',
        client_factory=cf_problem_classifications)
    with self.command_group('support services problem-classifications', support_problem_classifications,
                            client_factory=cf_problem_classifications, is_preview=True) as g:
        g.command('list', method_name='list')
        g.show_command('show', getter_name='get')

    from azext_support._client_factory import cf_support_tickets
    support_support_tickets = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#SupportTicketsOperations.{}',
        client_factory=cf_support_tickets)
    with self.command_group('support tickets', support_support_tickets,
                            client_factory=cf_support_tickets, is_preview=True) as g:
        g.custom_command('list', 'list_support_support_tickets')
        g.custom_command('show', 'get_support_tickets')

    from azext_support._client_factory import cf_support_ticket_subscription
    support_support_ticket_subscription = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#SupportTicketSubscriptionOperations.{}',
        client_factory=cf_support_ticket_subscription)
    with self.command_group('support tickets', support_support_ticket_subscription,
                            client_factory=cf_support_ticket_subscription, is_preview=True) as g:
        g.custom_command('update', 'update_support_tickets')

    from azext_support._client_factory import cf_communications
    support_communications = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#CommunicationsOperations.{}',
        client_factory=cf_communications)
    with self.command_group('support tickets communications', support_communications,
                            client_factory=cf_communications, is_preview=True) as g:
        g.custom_command('list', 'list_support_tickets_communications')
        g.custom_command('show', 'get_support_tickets_communications')

    from azext_support._client_factory import cf_support
    support = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks#MicrosoftSupport.{}',
        client_factory=cf_support)
    self.command_group('support', support, client_factory=cf_support, is_preview=True)
    with self.command_group('support tickets', support, client_factory=cf_support, is_preview=True) as g:
        g.custom_command('create', 'create_support_tickets', supports_no_wait=True)
        g.custom_wait_command('wait', 'wait_support_tickets')
    with self.command_group('support tickets communications', support, client_factory=cf_support, is_preview=True) as g:
        g.custom_command('create', 'create_support_tickets_communications', supports_no_wait=True)
        g.custom_wait_command('wait', 'wait_support_tickets_communications')
