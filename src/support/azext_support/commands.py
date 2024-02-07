# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_support._client_factory import (cf_communications,
                                           cf_problem_classifications,
                                           cf_services, cf_support,
                                           cf_support_tickets,
                                           cf_files)
from azext_support._validators import validate_tickets_create
from azext_support._validators import _check_name_availability_no_subscription
from azure.cli.core.commands import CliCommandType
from azext_support.custom import TicketUpdate, TicketCreate
from azext_support.custom import FileWorkspaceCreateNoSubscription, FileWorkspaceCreateSubscription
from azext_support.custom import CommunicationCreate
from azext_support.custom import CommunicationNoSubscriptionCreate


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
    support_files = CliCommandType(
		operations_tmpl='azext_support.vendored_sdks.operations#FilesOperations.{}',
		client_factory=cf_files)

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
        g.custom_show_command('show', 'get_support_tickets')
        g.custom_command('create', 'create_support_tickets', supports_no_wait=False, validator=validate_tickets_create)
        g.custom_command('update', 'update_support_tickets')

    with self.command_group('support tickets communications', support_communications,
                            client_factory=cf_communications) as g:
        g.custom_command('list', 'list_support_tickets_communications')
        g.custom_show_command('show', 'get_support_tickets_communications')
        g.custom_command('create', 'create_support_tickets_communications', supports_no_wait=False)
     
    self.command_table['support in-subscription tickets update'] = TicketUpdate(loader=self)
    self.command_table['support in-subscription tickets create'] = TicketCreate(loader=self)
    self.command_table['support in-subscription communication create'] = CommunicationCreate(loader=self)
    self.command_table['support no-subscription communication create'] = CommunicationNoSubscriptionCreate(loader=self)
    
    with self.command_group('support no-subscription file') as g:
        g.custom_command('upload', 'upload_files_no_subscription')

    with self.command_group('support in-subscription file') as g:
        g.custom_command('upload', 'upload_files_in_subscription')

    self.command_table['support in-subscription file-workspace create'] = FileWorkspaceCreateSubscription(loader=self)
    self.command_table['support no-subscription file-workspace create'] = FileWorkspaceCreateNoSubscription(loader=self)

