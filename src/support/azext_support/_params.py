# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_support._validators import datetime_type
from azure.cli.core.commands.parameters import (get_enum_type,
                                                get_three_state_flag)


def load_arguments(self, _):

    load_services_argument(self, _)
    load_problem_classifications_argument(self, _)
    load_tickets_argument(self, _)
    load_communications_argument(self, _)


def load_services_argument(self, _):
    with self.argument_context('support services list') as c:
        pass

    with self.argument_context('support services show') as c:
        c.argument('service_name', help="Name of Azure service available for support", required=True)


def load_problem_classifications_argument(self, _):
    with self.argument_context('support services problem-classifications list') as c:
        c.argument('service_name', help="Name of Azure service available for support", required=True)

    with self.argument_context('support services problem-classifications show') as c:
        c.argument('service_name', help="Name of Azure service available for support", required=True)
        c.argument('problem_classification_name', help="Name of problem classification", required=True)


def load_tickets_argument(self, _):
    with self.argument_context('support tickets list') as c:
        c.argument('filters', help='The odata filters to apply on the operation. ' +
                   'By default past one week filter is applied.')

    with self.argument_context('support tickets show') as c:
        c.argument('ticket_name', help="Name of the ticket.", required=True)

    with self.argument_context('support tickets update') as c:
        c.argument('ticket_name', help="Name of the ticket.", required=True)
        c.argument('severity', arg_type=get_enum_type(['minimal', 'moderate', 'critical']),
                   help='The severity for support ticket.')

    with self.argument_context('support tickets update', arg_group="Contact") as c:
        c.argument('contact_first_name', help='The first name in contact details.')
        c.argument('contact_last_name', help='The last name in contact details.')
        c.argument('contact_method', arg_type=get_enum_type(['email', 'phone']), help='The preferred contact method.')
        c.argument('contact_email', help='The primary email address.')
        c.argument('contact_additional_emails', nargs='+', help='Space seperated list of additional email addresses.')
        c.argument('contact_phone_number', help='The phone number. Required when contact method is \'phone\'.')
        c.argument('contact_timezone', help='The name of the time zone from \'Microsoft Time Zone Index Values\'. ' +
                   'e.g. Pacific Standard Time')
        c.argument('contact_country', help='The ISO 3166-1 alpha-3 country code. e.g. USA')
        c.argument('contact_language', help='The standard language-country code. e.g. en-US')

    with self.argument_context('support tickets create') as c:
        c.argument('ticket_name', help="Name for the ticket.", required=True)
        c.argument('service', help="Arm resource id of the service.", required=True)
        c.argument('problem_classification', help="Arm resource id of the problem classification.", required=True)
        c.argument('title', help="Title for the ticket.", required=True)
        c.argument('description', help="Description for the ticket.", required=True)
        c.argument('severity', arg_type=get_enum_type(['minimal', 'moderate', 'critical']),
                   help='The severity for support ticket.', required=True)
        c.argument('start_time', type=datetime_type, help='Time in UTC datetime (Y-m-d\'T\'H:M:S\'Z\')' +
                   ' when the problem started. Default is today.')
        c.argument('require_24_by_7_response', arg_type=get_three_state_flag(invert=True),
                   help='Flag to indicate 24x7 response requirement on ticket. Default is false.')

    with self.argument_context('support tickets create', arg_group="Contact") as c:
        c.argument('contact_first_name', help='The first name in contact details.', required=True)
        c.argument('contact_last_name', help='The last name in contact details.', required=True)
        c.argument('contact_method', arg_type=get_enum_type(['email', 'phone']), help='The preferred contact method.',
                   required=True)
        c.argument('contact_email', help='The primary email address.', required=True)
        c.argument('contact_additional_emails', nargs='+', help='Space seperated list of additional email addresses.')
        c.argument('contact_phone_number', help='The phone number. Required when contact method is \'phone\'.')
        c.argument('contact_timezone', help='The name of the time zone from \'Microsoft Time Zone Index Values\'. ' +
                   'e.g. Pacific Standard Time', required=True)
        c.argument('contact_country', help='The ISO 3166-1 alpha-3 country code. e.g. USA', required=True)
        c.argument('contact_language', help='The standard language-country code. e.g. en-US', required=True)

    with self.argument_context('support tickets create', arg_group="Technical Ticket Details") as c:
        c.argument('technical_resource', help='Arm resource id for the ticket. Required for technical ticket.')

    with self.argument_context('support tickets create', arg_group="Quota Ticket Details") as c:
        c.argument('quota_change_version', help='Quota change request version. Required for quota ticket.')
        c.argument('quota_change_subtype', help='Quota change request subtype. Required for some of the quota ticket.')
        c.argument('quota_change_regions', nargs='+', help='Space seperated list of quota change request regions.' +
                   ' Required for quota ticket.')
        c.argument('quota_change_payload', nargs='+', help='Space seperated list of quota change request payload(s)' +
                   ' for corresponding region(s). Required for quota ticket.')

    with self.argument_context('support tickets wait') as c:
        c.argument('ticket_name', help="Name of the ticket.", required=True)


def load_communications_argument(self, _):
    with self.argument_context('support tickets communications list') as c:
        c.argument('ticket_name', help="Name of the ticket.", required=True)
        c.argument('filters', help='The odata filters to apply on the operation.')

    with self.argument_context('support tickets communications show') as c:
        c.argument('ticket_name', help="Name of the ticket.", required=True)
        c.argument('communication_name', help="Name of the ticket communication.", required=True)

    with self.argument_context('support tickets communications create') as c:
        c.argument('ticket_name', help="Name of the ticket.", required=True)
        c.argument('communication_name', help="Name for the ticket communication.", required=True)

    with self.argument_context('support tickets communications create', arg_group="Communication") as c:
        c.argument('communication_body', help="Body of the ticket communication.", required=True)
        c.argument('communication_subject', help="Subject of the ticket communication.", required=True)
        c.argument('communication_sender', help="Email of the ticket communication sender.")

    with self.argument_context('support tickets communications wait') as c:
        c.argument('ticket_name', help="Name of the ticket.", required=True)
        c.argument('communication_name', help="Name of the ticket communication.", required=True)
