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
from azext_support.custom import TicketUpdate, TicketCreate
from azext_support.custom import (
    FileWorkspaceCreateNoSubscription,
    FileWorkspaceCreateSubscription,
)
from azext_support.custom import CommunicationCreate
from azext_support.custom import CommunicationNoSubscriptionCreate
from azext_support.custom import TicketUpdateNoSubscription
from azext_support.custom import TicketCreateNoSubscription
from azext_support.custom import TicketList
from azext_support.custom import TicketListNoSubscription


def load_command_table(self, _):
    support = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks#MicrosoftSupport.{}',
        client_factory=cf_support)
    support_tickets = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#SupportTicketsOperations.{}',
        client_factory=cf_support_tickets)
    support_communications = CliCommandType(
        operations_tmpl='azext_support.vendored_sdks.operations#CommunicationsOperations.{}',
        client_factory=cf_communications)

    self.command_group('support', support, client_factory=cf_support)

    with self.command_group('support services'):
        from .aaz.latest.support.services import List, Show;
        self.command_table['support services list'] = List(loader=self)
        self.command_table['support services show'] = Show(loader=self)

    with self.command_group('support services problem-classifications'):
        from .aaz.latest.support.services.problem_classifications import List, Show;
        self.command_table['support services problem-classifications list'] = List(loader=self)
        self.command_table['support services problem-classifications show'] = Show(loader=self)

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
    self.command_table['support no-subscription tickets update'] = TicketUpdateNoSubscription(loader=self)
    self.command_table['support no-subscription tickets create'] = TicketCreateNoSubscription(loader=self)
    self.command_table['support in-subscription tickets list'] = TicketList(loader=self)
    self.command_table['support no-subscription tickets list'] = TicketListNoSubscription(loader=self)
    
    with self.command_group("support no-subscription file") as g:
        g.custom_command("upload", "upload_files_no_subscription")

    with self.command_group("support in-subscription file") as g:
        g.custom_command("upload", "upload_files_in_subscription")

    self.command_table[
        "support in-subscription file-workspace create"
    ] = FileWorkspaceCreateSubscription(loader=self)
    self.command_table[
        "support no-subscription file-workspace create"
    ] = FileWorkspaceCreateNoSubscription(loader=self)
