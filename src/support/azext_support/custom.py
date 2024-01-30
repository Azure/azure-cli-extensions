# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

import json
from datetime import date, datetime, timedelta

from azext_support._utils import (get_bearer_token, is_quota_ticket,
                                  is_technical_ticket, parse_support_area_path)
from knack.log import get_logger

from .aaz.latest.support.in_subscription.tickets import Update as _Update
from .aaz.latest.support.in_subscription.tickets import Create as _CreateTicket
from .aaz.latest.support.in_subscription.communication import Create as _CreateCommunication

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

languages = {"en-us" : "en-us", "es-es": "es-es", "fr-fr" : "fr-fr", "de-de" : "de-de", "it-it" : "it-it",
             "ja-jp" : "ja-jp", "ko-kr":"ko-kr", "ru-ru": "ru-ru", "pt-br" : "pt-br", "zh-tw" : "zh-tw",
             "zh-hans" : "zh-hans"}

timezones = {"Afghanistan Standard Time" : "Afghanistan Standard Time", "Alaskan Standard Time" : "Alaskan Standard Time",
             "Arab Standard Time" : "Arab Standard Time", "Arabian Standard Time" : "Arabian Standard Time",
             "Arabic Standard Time" : "Arabic Standard Time", "Argentina Standard Time" : "Argentina Standard Time",
             "Atlantic Standard Time" : "Atlantic Standard Time", "AUS Central Standard Time" : "AUS Central Standard Time",
             "AUS Eastern Standard Time" : "AUS Eastern Standard Time", "Azerbaijan Standard Time" : "Azerbaijan Standard Time",
             "Azores Standard Time" : "Azores Standard Time", "Canada Central Standard Time" : "Canada Central Standard Time",
             "Cape Verde Standard Time" : "Cape Verde Standard Time", "Caucasus Standard Time" : "Caucasus Standard Time",
             "Cen. Australia Standard Time" : "Cen. Australia Standard Time", "Central America Standard Time" : "Central America Standard Time",
             "Central Asia Standard Time" : "Central Asia Standard Time", "Central Brazilian Standard Time" : "Central Brazilian Standard Time",
             "Central Europe Standard Time" : "Central Europe Standard Time", "Central European Standard Time" : "Central European Standard Time",
             "Central Pacific Standard Time" : "Central Pacific Standard Time", "Central Standard Time" : "Central Standard Time",
             "Central Standard Time (Mexico)" : "Central Standard Time (Mexico)", "China Standard Time" : "China Standard Time",
             "Dateline Standard Time" : "Dateline Standard Time", "E. Africa Standard Time" : "E. Africa Standard Time",
             "E. Australia Standard Time" : "E. Australia Standard Time", "E. Europe Standard Time" : "E. Europe Standard Time",
             "E. South America Standard Time" : "E. South America Standard Time", "Eastern Standard Time" : "Eastern Standard Time",
             "Eastern Standard Time (Mexico)" : "Eastern Standard Time (Mexico)", "Egypt Standard Time" : "Egypt Standard Time",
             "Ekaterinburg Standard Time" : "Ekaterinburg Standard Time", "Fiji Standard Time" : "Fiji Standard Time",
             "FLE Standard Time" : "FLE Standard Time", "Georgian Standard Time" : "Georgian Standard Time", "GMT Standard Time" : "GMT Standard Time",
             "Greenland Standard Time" : "Greenland Standard Time", "Greenwich Standard Time" : "Greenwich Standard Time",
             "GTB Standard Time" : "GTB Standard Time", "Hawaiian Standard Time" : "Hawaiian Standard Time", "India Standard Time" : "India Standard Time",
             "Iran Standard Time" : "Iran Standard Time", "Israel Standard Time" : "Israel Standard Time", "Jordan Standard Time" : "Jordan Standard Time",
             "Korea Standard Time" : "Korea Standard Time", "Mauritius Standard Time" : "Mauritius Standard Time",
             "Central Standard Time (Mexico)" : "Central Standard Time (Mexico)", "Mid-Atlantic Standard Time" : "Mid-Atlantic Standard Time",
             "Middle East Standard Time" : "Middle East Standard Time", "Montevideo Standard Time" : "Montevideo Standard Time",
             "Morocco Standard Time" : "Morocco Standard Time", "Mountain Standard Time" : "Mountain Standard Time",
             "Mountain Standard Time (Mexico)" : "Mountain Standard Time (Mexico)", "Myanmar Standard Time" : "Myanmar Standard Time",
             "N. Central Asia Standard Time" : "N. Central Asia Standard Time", "Namibia Standard Time" : "Namibia Standard Time",
             "Nepal Standard Time" : "Nepal Standard Time", "New Zealand Standard Time" : "New Zealand Standard Time",
             "Newfoundland Standard Time" : "Newfoundland Standard Time", "North Asia East Standard Time" : "North Asia East Standard Time",
             "North Asia Standard Time" : "North Asia Standard Time", "Pacific SA Standard Time" : "Pacific SA Standard Time",
             "Pacific Standard Time" : "Pacific Standard Time", "Pacific Standard Time (Mexico)" : "Pacific Standard Time (Mexico)",
             "Pakistan Standard Time" : "Pakistan Standard Time", "Romance Standard Time" : "Romance Standard Time",
             "Russian Standard Time" : "Russian Standard Time", "SA Eastern Standard Time" : "SA Eastern Standard Time",
             "SA Pacific Standard Time" : "SA Pacific Standard Time", "SA Western Standard Time" : "SA Western Standard Time",
             "Samoa Standard Time" : "Samoa Standard Time", "SE Asia Standard Time" : "SE Asia Standard Time",
             "Singapore Standard Time" : "Singapore Standard Time", "South Africa Standard Time" : "South Africa Standard Time",
             "Sri Lanka Standard Time" : "Sri Lanka Standard Time", "Taipei Standard Time" : "Taipei Standard Time",
             "Tasmania Standard Time" : "Tasmania Standard Time", "Tokyo Standard Time" : "Tokyo Standard Time", "Tonga Standard Time" : "Tonga Standard Time",
             "Turkey Standard Time" : "Turkey Standard Time", "US Eastern Standard Time" : "US Eastern Standard Time",
             "US Mountain Standard Time" : "US Mountain Standard Time", "UTC" : "UTC", "Venezuela Standard Time" : "Venezuela Standard Time",
             "Vladivostok Standard Time" : "Vladivostok Standard Time", "W. Australia Standard Time" : "W. Australia Standard Time",
             "W. Central Africa Standard Time" : "W. Central Africa Standard Time", "W. Europe Standard Time" : "W. Europe Standard Time",
             "West Asia Standard Time" : "West Asia Standard Time", "West Pacific Standard Time" : "West Pacific Standard Time",
             "Yakutsk Standard Time" : "Yakutsk Standard Time"}

class TicketUpdate(_Update):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.contact_language.enum = AAZArgEnum(languages)
        args_schema.contact_timezone.enum = AAZArgEnum(timezones)
        return args_schema

class TicketCreate(_CreateTicket):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZArgEnum
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.contact_language.enum = AAZArgEnum(languages)
        args_schema.contact_timezone.enum = AAZArgEnum(timezones)
        args_schema.diagnostic_consent._required = True
        args_schema.title._required = True
        args_schema.severity._required = True
        args_schema.problem_classification._required = True
        args_schema.description._required = True
        args_schema.contact_country._required = True
        args_schema.contact_email._required = True
        args_schema.contact_first_name._required = True
        args_schema.contact_last_name._required = True
        args_schema.contact_language._required = True
        args_schema.contact_method._required = True
        args_schema.contact_timezone._required = True
        
        return args_schema
    
    def pre_operations(self):
        from azext_support._validators import validate_tickets_create_new
        super().pre_operations()
        args = self.ctx.args
        if hasattr(args, 'technical_resource'):
            validate_tickets_create_new(self.cli_ctx, str(args.problem_classification), str(args.ticket_name), str(args.technical_resource))
        else:
            validate_tickets_create_new(self.cli_ctx, str(args.problem_classification), str(args.ticket_name))
            
    class SupportTicketsCreate(_CreateTicket.SupportTicketsCreate):
        @property
        def content(self):
            body = super().content
            service_name = parse_support_area_path(body["properties"]["problemClassificationId"])["service_name"]
            body["properties"]["serviceId"] = "/providers/Microsoft.Support/services/{0}".format(service_name)
            if "problemStartTime" not in body["properties"]: 
                start_time = datetime.utcnow().strftime(("%Y-%m-%dT%H:%M:%SZ"))
                body["properties"]["problemStartTime"] = start_time
            return body

class CommunicationCreate(_CreateCommunication):
    def pre_operations(self):
        from azext_support._validators import _check_name_availability_subscription
        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_subscription(self.cli_ctx, str(args.communication_name), "Microsoft.Support/communications")
