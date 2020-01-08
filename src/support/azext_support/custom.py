# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

import json
from datetime import date, timedelta

from knack.log import get_logger

logger = get_logger(__name__)


def list_support_tickets(cmd, client, filters=None):
    if filters is None:
        filters = "CreatedDate ge " + str(date.today() - timedelta(7))

    return client.list_by_subscription(top=100, filter=filters)


def get_support_tickets(cmd, client, ticket_name=None):
    return client.get_by_subscription(support_ticket_name=ticket_name)


def update_support_tickets(cmd, client,
                           ticket_name=None,
                           severity=None,
                           contact_first_name=None,
                           contact_last_name=None,
                           contact_method=None,
                           contact_email=None,
                           contact_additional_emails=None,
                           contact_phone_number=None,
                           contact_timezone=None,
                           contact_country=None,
                           contact_language=None):
    body = {}
    body["first_name"] = contact_first_name
    body["last_name"] = contact_last_name
    body["preferred_contact_method"] = contact_method
    body["primary_email_address"] = contact_email
    body["additional_email_addresses"] = contact_additional_emails
    body["phone_number"] = contact_phone_number
    body["preferred_time_zone"] = contact_timezone
    body["country"] = contact_country
    body["preferred_support_language"] = contact_language

    return client.update(support_ticket_name=ticket_name, severity=severity, contact_details=body)


def list_support_tickets_communications(cmd, client, ticket_name=None, filters=None):
    return client.list_by_subscription_ticket(support_ticket_name=ticket_name, filter=filters)


def get_support_tickets_communications(cmd, client, ticket_name=None, communication_name=None):
    return client.get_by_subscription_ticket(support_ticket_name=ticket_name, communication_name=communication_name)


def create_support_tickets(cmd, client,
                           ticket_name=None,
                           service=None,
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
                           quota_change_payload=None):
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
    body["problem_start_time"] = start_time if start_time is not None else date.today()

    if _is_quota_ticket(service):
        quotaBody = {}
        quotaBody["quota_change_request_sub_type"] = quota_change_subtype
        quotaBody["quota_change_request_version"] = quota_change_version
        quota_change_requests = []
        if quota_change_regions is not None and quota_change_payload is not None:
            for (region, payload) in zip(quota_change_regions, quota_change_payload):
                quota_change_requests.append({"region": region, "payload": payload})
        quotaBody["quota_change_requests"] = quota_change_requests

        body["quota_ticket_details"] = quotaBody

    if _is_technical_ticket(service):
        body["technical_ticket_details"] = {"resource_id": technical_resource}

    logger.debug("Sending create request with below payload: ")
    logger.debug(json.dumps(body, indent=4))

    custom_headers = {}
    # if partner_tenant_id is not None:
    #    custom_headers["x-ms-authorization-auxiliary"] = _get_bearer_token(cmd, partner_tenant_id)

    return client.create_support_ticket_for_subscription(support_ticket_name=ticket_name,
                                                         create_support_ticket_parameters=body,
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

    return client.create_support_ticket_communication(support_ticket_name=ticket_name,
                                                      communication_name=communication_name,
                                                      create_communication_parameters=body)


def _is_billing_ticket(service_name):
    return "517f2da6-78fd-0498-4e22-ad26996b1dfc" in service_name


def _is_quota_ticket(service_name):
    return "06bfd9d3-516b-d5c6-5802-169c800dec89" in service_name


def _is_subscription_mgmt_ticket(service_name):
    return "f3dc5421-79ef-1efa-41a5-42bf3cbb52c6" in service_name


def _is_technical_ticket(service_name):
    return (not _is_billing_ticket(service_name)) and \
           (not _is_quota_ticket(service_name)) and \
           (not _is_subscription_mgmt_ticket(service_name))


# def _get_bearer_token(cmd, common_id):
#    profile = Profile(cli_ctx=cmd.cli_ctx)

#    try:
#        creds, _, _ = profile.get_raw_token(subscription=common_id,
#                                            resource=cmd.cli_ctx.cloud.endpoints.active_directory_resource_id)
#    except CLIError:
#        logger.debug(traceback.format_exc())
#        raise CLIError("Can't find authorization for " + common_id +
#                        "Run \'az login -t <tenant_name> --allow-no-subscriptions\' and try again.")

#    return "Bearer " + creds[1]
