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

    if is_quota_ticket(service):
        quotaBody = {}
        quotaBody["quota_change_request_sub_type"] = quota_change_subtype
        quotaBody["quota_change_request_version"] = quota_change_version
        quota_change_requests = []
        if quota_change_regions is not None and quota_change_payload is not None:
            for (region, payload) in zip(quota_change_regions, quota_change_payload):
                quota_change_requests.append({"region": region, "payload": payload})
        quotaBody["quota_change_requests"] = quota_change_requests
        body["quota_ticket_details"] = quotaBody

    if is_technical_ticket(service):
        body["technical_ticket_details"] = {"resource_id": technical_resource}

    logger.debug("Sending create request with below payload: ")
    logger.debug(json.dumps(body, indent=4))

    custom_headers = {}
    if partner_tenant_id is not None:
        custom_headers["x-ms-authorization-auxiliary"] = get_bearer_token(cmd, partner_tenant_id)

    return client.create(support_ticket_name=ticket_name, create_support_ticket_parameters=body,
                         custom_headers=custom_headers)


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

    return client.create(support_ticket_name=ticket_name, communication_name=communication_name,
                         create_communication_parameters=body)
