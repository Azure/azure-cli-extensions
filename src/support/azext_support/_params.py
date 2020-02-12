# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_support._completers import (get_supported_languages_for_create,
                                       get_supported_languages_for_update,
                                       get_supported_timezones_for_create,
                                       get_supported_timezones_for_update)
from azext_support._validators import datetime_type
from azure.cli.core.commands.parameters import (get_enum_type,
                                                get_three_state_flag)
from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    load_services_argument(self, _)
    load_problem_classifications_argument(self, _)
    load_tickets_argument(self, _)
    load_communications_argument(self, _)


def load_services_argument(self, _):
    with self.argument_context('support services list') as c:
        pass

    with self.argument_context('support services show') as c:
        c.argument('service_name', help='Name of Azure service', required=True)


def load_problem_classifications_argument(self, _):
    with self.argument_context('support services problem-classifications list') as c:
        c.argument('service_name', help='Name of Azure service', required=True)

    with self.argument_context('support services problem-classifications show') as c:
        c.argument('service_name', help='Name of Azure service', required=True)
        c.argument('problem_classification_name', help='Name of problem classification', required=True)


def load_tickets_argument(self, _):

    language_type_for_create = CLIArgumentType(options_list=('--contact-language',),
                                               help='Preferred language of support from Azure. Support languages ' +
                                               'vary based on the severity you choose for your support ticket. This ' +
                                               'is the standard country-language code.',
                                               completer=get_supported_languages_for_create, required=True)
    language_type_for_update = CLIArgumentType(options_list=('--contact-language',),
                                               help='Preferred language of support from Azure. Support languages ' +
                                               'vary based on the severity you choose for your support ticket. This ' +
                                               'is the standard country-language code.',
                                               completer=get_supported_languages_for_update)
    timezone_type_for_create = CLIArgumentType(options_list=('--contact-timezone',), help='Time zone of the user. ' +
                                               'This is the name of the time zone from Microsoft Time Zone Index ' +
                                               'Values', completer=get_supported_timezones_for_create, required=True)
    timezone_type_for_update = CLIArgumentType(options_list=('--contact-timezone',), help='Time zone of the user. ' +
                                               'This is the name of the time zone from Microsoft Time Zone Index ' +
                                               'Values', completer=get_supported_timezones_for_update)

    with self.argument_context('support tickets list') as c:
        c.argument('filters', help='The filter to apply on the operation. We support OData v4.0 semtantics. ' +
                   'Filter can be specified on "Status" property using eq operator or on "CreatedDate" using gt/ge. ' +
                   'To combine both filters, use the logical and operator. Default is CreatedDate >= one week.')

    with self.argument_context('support tickets show') as c:
        c.argument('ticket_name', help='Support ticket name', required=True)

    with self.argument_context('support tickets update') as c:
        c.argument('ticket_name', help='Support ticket name', required=True)
        c.argument('severity', arg_type=get_enum_type(['minimal', 'moderate', 'critical']),
                   help='A value that indicates the urgency of the case, which in turn determines the response ' +
                   'time according to the service level agreement of the technical support plan you have with Azure.')

    with self.argument_context('support tickets update', arg_group="Contact") as c:
        c.argument('contact_first_name', help='First Name')
        c.argument('contact_last_name', help='Last Name')
        c.argument('contact_method', arg_type=get_enum_type(['email', 'phone']), help='Preferred contact method')
        c.argument('contact_email', help='Primary email address')
        c.argument('contact_additional_emails', nargs='+', help='Space seperated list of additional email addresses. ' +
                   'Additional email addresses will be copied on any correspondence about the support ticket.')
        c.argument('contact_phone_number', help='Phone number. This is required if preferred contact method is phone.')
        c.argument('contact_timezone', arg_type=timezone_type_for_update)
        c.argument('contact_country', help='Country of the user. This is the ISO Alpha-3 code')
        c.argument('contact_language', arg_type=language_type_for_update)

    with self.argument_context('support tickets create') as c:
        c.argument('ticket_name', help="Support ticket name", required=True)
        c.argument('problem_classification', help='Each Azure service has its own set of issue category called ' +
                   'problem classification that corresponds to the type of problem you are experiencing. ' +
                   'This parameter is the resource id of ProblemClassification resource.', required=True)
        c.argument('title', help="Title of the support ticket.", required=True)
        c.argument('description', help="Detailed description of the question or issue.", required=True)
        c.argument('severity', arg_type=get_enum_type(['minimal', 'moderate', 'critical']),
                   help='A value that indicates the urgency of the case, which in turn determines the response time ' +
                   'according to the service level agreement of the technical support plan you have with Azure.',
                   required=True)
        c.argument('start_time', type=datetime_type, help='Time in UTC datetime (Y-m-d\'T\'H:M:S\'Z\')' +
                   ' when the problem started. Default is today.')
        c.argument('require_24_by_7_response', arg_type=get_three_state_flag(invert=True),
                   help='Indicates if this requires a 24x7 response from Azure. Default is false.')
        c.argument('partner_tenant_id', help='Partner tenant id for Admin On Behalf ' +
                   'of (AOBO) scenario. In addition to logging in to the customer tenant, logging in to the partner ' +
                   'tenant (PT) using "az login -t PT --allow-no-subscriptions" is required.')

    with self.argument_context('support tickets create', arg_group="Contact") as c:
        c.argument('contact_first_name', help='First Name', required=True)
        c.argument('contact_last_name', help='Last Name', required=True)
        c.argument('contact_method', arg_type=get_enum_type(['email', 'phone']), help='Preferred contact method',
                   required=True)
        c.argument('contact_email', help='Primary email address', required=True)
        c.argument('contact_additional_emails', nargs='+', help='Space seperated list of additional email addresses. ' +
                   'Additional email addresses will be copied on any correspondence about the support ticket.')
        c.argument('contact_phone_number', help='Phone number. This is required if preferred contact method is phone.')
        c.argument('contact_timezone', arg_type=timezone_type_for_create)
        c.argument('contact_country', help='Country of the user. This is the ISO Alpha-3 code', required=True)
        c.argument('contact_language', arg_type=language_type_for_create)

    with self.argument_context('support tickets create', arg_group="Technical Ticket Details") as c:
        c.argument('technical_resource', help='This is the resource id of the Azure service resource ' +
                   'for which the support ticket is created.')

    with self.argument_context('support tickets create', arg_group="Quota Ticket Details") as c:
        c.argument('quota_change_version', help='Quota change request version.')
        c.argument('quota_change_subtype', help='Required for certain quota types when there is a sub type that ' +
                   'you are requesting quota increase for. Example: Batch')
        c.argument('quota_change_regions', nargs='+', help='Space seperated list of region for which ' +
                   'the quota increase request is being made.')
        c.argument('quota_change_payload', nargs='+', help='Space seperated list of serialized payload of the ' +
                   'quota increase request corresponding to regions. Visit ' +
                   'https://aka.ms/supportrpquotarequestpayload for details.')


def load_communications_argument(self, _):
    with self.argument_context('support tickets communications list') as c:
        c.argument('ticket_name', help="Support ticket name", required=True)
        c.argument('filters', help='The filter to apply on the operation. We support OData v4.0 semtantics. ' +
                   'Filter can be specified on "CommunicationType" using eq operator or on "CreatedDate" ' +
                   'using gt/ge. To combine both filters, use the logical and operator.')

    with self.argument_context('support tickets communications show') as c:
        c.argument('ticket_name', help='Support ticket name', required=True)
        c.argument('communication_name', help='Communication name', required=True)

    with self.argument_context('support tickets communications create') as c:
        c.argument('ticket_name', help='Support ticket name', required=True)
        c.argument('communication_name', help='Communication name', required=True)

    with self.argument_context('support tickets communications create', arg_group="Communication") as c:
        c.argument('communication_body', help='Text of the communication.', required=True)
        c.argument('communication_subject', help='Subject of the communication.', required=True)
        c.argument('communication_sender', help='Email address of the sender.')
