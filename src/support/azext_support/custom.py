# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

import json
from datetime import date, datetime, timedelta

from azext_support._utils import (get_bearer_token, is_quota_ticket,
                                  is_technical_ticket, parse_support_area_path, upload_file)
from knack.log import get_logger
from azext_support._completers import (
    _get_supported_languages as getLanguage,
    _get_supported_timezones as getTimeZone,
)
from .aaz.latest.support.in_subscription.tickets import Update as _Update
from .aaz.latest.support.in_subscription.tickets import Create as _CreateTicket
from .aaz.latest.support.in_subscription.communication import Create as _CreateCommunication
from .aaz.latest.support.no_subscription.communication import Create as _CreateNoSubscriptionCommunication
from .aaz.latest.support.no_subscription.tickets import Update as _UpdateNoSubscription
from .aaz.latest.support.no_subscription.tickets import Create as _CreateTicketNoSubscription
from .aaz.latest.support.in_subscription.tickets import List as _List
from .aaz.latest.support.no_subscription.tickets import List as _ListNoSubscription
from .aaz.latest.support.in_subscription.file_workspace import Create as _CreateFileWorkspace
from .aaz.latest.support.no_subscription.file_workspace import Create as _CreateNoSubscriptionFileWorkspace

logger = get_logger(__name__)

def list_support_tickets(cmd, client, filters=None):
    if filters is None:
        filters = "CreatedDate ge " + str(date.today() - timedelta(days=7))
    return client.list(top=100, filter=filters)


def get_support_tickets(cmd, client, ticket_name=None):
    return client.get(support_ticket_name=ticket_name)


def update_support_tickets(cmd, client,
                           ticket_name=None,
                           severity=None,
                           status=None,
                           contact_first_name=None,
                           contact_last_name=None,
                           contact_method=None,
                           contact_email=None,
                           contact_additional_emails=None,
                           contact_phone_number=None,
                           contact_timezone=None,
                           contact_country=None,
                           contact_language=None):
    contactBody = {}
    contactBody["first_name"] = contact_first_name
    contactBody["last_name"] = contact_last_name
    contactBody["preferred_contact_method"] = contact_method
    contactBody["primary_email_address"] = contact_email
    contactBody["additional_email_addresses"] = contact_additional_emails
    contactBody["phone_number"] = contact_phone_number
    contactBody["preferred_time_zone"] = contact_timezone
    contactBody["country"] = contact_country
    contactBody["preferred_support_language"] = contact_language

    body = {}
    body["severity"] = severity
    body["status"] = status
    if not all(x is None for x in contactBody.values()):
        body["contact_details"] = contactBody
    else:
        body["contact_details"] = None

    return client.update(support_ticket_name=ticket_name, update_support_ticket=body)


def list_support_tickets_communications(cmd, client, ticket_name=None, filters=None):
    return client.list(support_ticket_name=ticket_name, filter=filters)


def get_support_tickets_communications(cmd, client, ticket_name=None, communication_name=None):
    return client.get(support_ticket_name=ticket_name, communication_name=communication_name)


def create_support_tickets(cmd, client,
                           ticket_name=None,
                           problem_classification=None,
                           title=None,
                           description=None,
                           severity=None,
                           start_time=None,
                           require_24_by_7_response=None,
                           contact_first_name=None,
                           contact_last_name=None,
                           contact_method=None,
                           contact_email=None,
                           contact_additional_emails=None,
                           contact_phone_number=None,
                           contact_timezone=None,
                           contact_country=None,
                           contact_language=None,
                           technical_resource=None,
                           quota_change_version=None,
                           quota_change_subtype=None,
                           quota_change_regions=None,
                           quota_change_payload=None,
                           partner_tenant_id=None):
    service_name = parse_support_area_path(problem_classification)["service_name"]
    service = "/providers/Microsoft.Support/services/{0}".format(service_name)

    contactBody = {}
    contactBody["first_name"] = contact_first_name
    contactBody["last_name"] = contact_last_name
    contactBody["preferred_contact_method"] = contact_method
    contactBody["primary_email_address"] = contact_email
    contactBody["additional_email_addresses"] = contact_additional_emails
    contactBody["phone_number"] = contact_phone_number
    contactBody["preferred_time_zone"] = contact_timezone
    contactBody["country"] = contact_country
    contactBody["preferred_support_language"] = contact_language

    body = {}
    body["description"] = description
    body["problem_classification_id"] = problem_classification
    body["severity"] = severity
    body["contact_details"] = contactBody
    body["title"] = title
    body["service_id"] = service
    body["require24_x7_response"] = require_24_by_7_response if require_24_by_7_response is not None else False
    start_date_time = start_time if start_time is not None else datetime.now()
    start_date_time = start_date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    body["problem_start_time"] = start_date_time

    if is_quota_ticket(service) and quota_change_version is not None:
        quotaBody = {}
        quotaBody["quota_change_request_sub_type"] = quota_change_subtype
        quotaBody["quota_change_request_version"] = quota_change_version
        quota_change_requests = []
        if quota_change_regions is not None and quota_change_payload is not None:
            for (region, payload) in zip(quota_change_regions, quota_change_payload):
                quota_change_requests.append({"region": region, "payload": payload})
        quotaBody["quota_change_requests"] = quota_change_requests
        body["quota_ticket_details"] = quotaBody

    if is_technical_ticket(service) and technical_resource is not None:
        body["technical_ticket_details"] = {"resource_id": technical_resource}

    logger.debug("Sending create request with below payload: ")
    logger.debug(json.dumps(body, indent=4))

    if partner_tenant_id is not None:
        external_bearer_token = get_bearer_token(cmd, partner_tenant_id)
        return client.begin_create(support_ticket_name=ticket_name, create_support_ticket_parameters=body,
                                   headers={'x-ms-authorization-auxiliary': external_bearer_token})

    return client.begin_create(support_ticket_name=ticket_name, create_support_ticket_parameters=body)


def create_support_tickets_communications(cmd, client,
                                          ticket_name=None,
                                          communication_name=None,
                                          communication_body=None,
                                          communication_subject=None,
                                          communication_sender=None):
    body = {}
    body["sender"] = communication_sender
    body["subject"] = communication_subject
    body["body"] = communication_body

    return client.begin_create(support_ticket_name=ticket_name, communication_name=communication_name,
                               create_communication_parameters=body)


class TicketUpdate(_Update):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.contact_language.enum = AAZArgEnum(getLanguage())
        args_schema.contact_timezone.enum = AAZArgEnum(getTimeZone())
        return args_schema

class TicketCreate(_CreateTicket):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum, AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.enrollment_id = AAZStrArg(
            options=["--enrollment-id"],
            help="Enrollment Id associated with the support ticket.")
        args_schema.contact_language.enum = AAZArgEnum(getLanguage())
        args_schema.contact_timezone.enum = AAZArgEnum(getTimeZone())
        
        return args_schema
    
    def pre_operations(self):
        from azext_support._validators import validate_tickets_create_new
        from azure.cli.core.aaz import AAZUndefined
        super().pre_operations()
        args = self.ctx.args
        if args.technical_resource != AAZUndefined:
            validate_tickets_create_new(self.cli_ctx, str(args.problem_classification), str(args.ticket_name), str(args.technical_resource))
        else:
            validate_tickets_create_new(self.cli_ctx, str(args.problem_classification), str(args.ticket_name))
            
    class SupportTicketsCreate(_CreateTicket.SupportTicketsCreate):
        @property
        def content(self):
            from azure.cli.core.aaz import AAZUndefined
            body = super().content
            args = self.ctx.args
            if args.enrollment_id != AAZUndefined:
                enrollment_id = str(args.enrollment_id)
                body["properties"]["enrollmentId"] = enrollment_id
            service_name = parse_support_area_path(body["properties"]["problemClassificationId"])["service_name"]
            body["properties"]["serviceId"] = "/providers/Microsoft.Support/services/{0}".format(service_name)
            if args.start_time == AAZUndefined:
                start_time = datetime.utcnow().strftime(("%Y-%m-%dT%H:%M:%SZ"))
                body["properties"]["problemStartTime"] = start_time
            return body

class CommunicationCreate(_CreateCommunication):
    def pre_operations(self):
        from azext_support._validators import _check_name_availability_subscription_ticket
        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_subscription_ticket(self.cli_ctx, str(args.ticket_name), str(args.communication_name), "Microsoft.Support/communications")

class CommunicationNoSubscriptionCreate(_CreateNoSubscriptionCommunication):
    def pre_operations(self):
        from azext_support._validators import _check_name_availability_no_subscription_ticket
        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_no_subscription_ticket(self.cli_ctx, str(args.ticket_name), str(args.communication_name), "Microsoft.Support/communications")


class TicketUpdateNoSubscription(_UpdateNoSubscription):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.contact_language.enum = AAZArgEnum(getLanguage())
        args_schema.contact_timezone.enum = AAZArgEnum(getTimeZone())
        return args_schema


class TicketCreateNoSubscription(_CreateTicketNoSubscription):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum, AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.enrollment_id = AAZStrArg(
            options=["--enrollment-id"],
            help="Enrollment Id associated with the support ticket.")
        args_schema.contact_language.enum = AAZArgEnum(getLanguage())
        args_schema.contact_timezone.enum = AAZArgEnum(getTimeZone())

        return args_schema

    def pre_operations(self):
        from azext_support._validators import validate_tickets_create_no_subscription_new
        from azure.cli.core.aaz import AAZUndefined
        super().pre_operations()
        args = self.ctx.args
        if args.technical_resource != AAZUndefined:
            validate_tickets_create_no_subscription_new(self.cli_ctx, str(args.problem_classification), str(args.ticket_name),
                                        str(args.technical_resource))
        else:
            validate_tickets_create_no_subscription_new(self.cli_ctx, str(args.problem_classification), str(args.ticket_name))

    class SupportTicketsNoSubscriptionCreate(_CreateTicketNoSubscription.SupportTicketsNoSubscriptionCreate):
        @property
        def content(self):
            from azure.cli.core.aaz import AAZUndefined
            body = super().content
            args = self.ctx.args
            if args.enrollment_id != AAZUndefined:
                enrollment_id = str(args.enrollment_id)
                body["properties"]["enrollmentId"] = enrollment_id
            service_name = parse_support_area_path(body["properties"]["problemClassificationId"])["service_name"]
            body["properties"]["serviceId"] = "/providers/Microsoft.Support/services/{0}".format(service_name)
            if args.start_time == AAZUndefined:
                start_time = datetime.utcnow().strftime(("%Y-%m-%dT%H:%M:%SZ"))
                body["properties"]["problemStartTime"] = start_time
            return body


class TicketList(_List):
    class SupportTicketsList(_List.SupportTicketsList):
        @property
        def query_parameters(self):
            from azure.cli.core.aaz import AAZUndefined
            parameters = super().query_parameters
            args = self.ctx.args
            if args.filter == AAZUndefined and args.pagination_limit == AAZUndefined:
                parameters["$filter"] = "CreatedDate ge " + str(date.today() - timedelta(days=7))
            return parameters


class TicketListNoSubscription(_ListNoSubscription):
    class SupportTicketsNoSubscriptionList(_ListNoSubscription.SupportTicketsNoSubscriptionList):
        @property
        def query_parameters(self):
            from azure.cli.core.aaz import AAZUndefined
            parameters = super().query_parameters
            args = self.ctx.args
            if args.filter == AAZUndefined and args.pagination_limit == AAZUndefined:
                parameters["$filter"] = "CreatedDate ge " + str(date.today() - timedelta(days=7))
            return parameters


class FileWorkspaceCreateNoSubscription(_CreateNoSubscriptionFileWorkspace):
    def pre_operations(self):
        from azext_support._validators import _check_name_availability_no_subscription

        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_no_subscription(
            self.cli_ctx,
            str(args.file_workspace_name),
            "Microsoft.Support/fileWorkspaces",
        )


class FileWorkspaceCreateSubscription(_CreateFileWorkspace):
    def pre_operations(self):
        from azext_support._validators import _check_name_availability_subscription

        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_subscription(
            self.cli_ctx,
            str(args.file_workspace_name),
            "Microsoft.Support/fileWorkspaces",
        )


def upload_files_no_subscription(cmd, file_path, file_workspace_name):

    from .aaz.latest.support.no_subscription.file import (
        Create as Create,
        Upload as Upload,
    )

    upload_file(cmd, file_path, file_workspace_name, False, Create, Upload)


def upload_files_in_subscription(
    cmd, file_path, file_workspace_name, subscription_id=None
):
    from .aaz.latest.support.in_subscription.file import (
		Create as Create_Sub,
		Upload as Upload_Sub,
	)
    upload_file(
        cmd,
        file_path,
        file_workspace_name,
        True,
        Create_Sub,
        Upload_Sub,
        subscription_id,
    )