# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

from knack.util import CLIError


def list_support_support_tickets(cmd, client,
                                 top=None,
                                 filters=None,
                                 skip_token=None):
    return client.list_by_subscription(top=top, filter=filters, skip_token=skip_token)


def get_support_tickets(cmd, client,
                        ticket_name=None):
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


def list_support_tickets_communications(cmd, client,
                                        ticket_name=None,
                                        top=None,
                                        filters=None,
                                        skip_token=None):
    return client.list_by_subscription_ticket(support_ticket_name=ticket_name,
                                              top=top, filter=filters, skip_token=skip_token)


def get_support_tickets_communications(cmd, client,
                                       ticket_name=None,
                                       communication_name=None):
    return client.get_by_subscription_ticket(support_ticket_name=ticket_name, communication_name=communication_name)


def create_support_tickets(cmd, client,
                           ticket_name=None,
                           service=None,
                           problem_classification=None,
                           title=None,
                           description=None,
                           severity=None,
                           contact_first_name=None,
                           contact_last_name=None,
                           contact_method=None,
                           contact_email=None,
                           contact_additional_emails=None,
                           contact_phone_number=None,
                           contact_timezone=None,
                           contact_country=None,
                           contact_language=None,
                           start_time=None,
                           require_24_by_7_response=None,
                           technical_resource=None,
                           quota_change_version=None,
                           quota_change_subtype=None,
                           quota_change_regions=None,
                           quota_change_payload=None):

    rsp = client.check_name_availability_with_subscription(name=ticket_name,
                                                           type="Microsoft.Support/supportTickets")
    if not rsp["name_available"]:
        raise CLIError('Support ticket name \'' + ticket_name + '\' not available. Please try again with another name!')

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

    quotaBody = {}
    quotaBody["quota_change_request_sub_type"] = quota_change_subtype
    quotaBody["quota_change_request_version"] = quota_change_version
    quota_change_requests = []
    for (region, payload) in zip(quota_change_regions, quota_change_payload):
        quota_change_requests.append({"region": region, "payload": payload})
    quotaBody["quota_change_requests"] = quota_change_requests

    body = {}
    body["description"] = description
    body["problem_classification_id"] = problem_classification
    body["severity"] = severity
    body["contact_details"] = contactBody
    body["title"] = title
    body["service_id"] = service
    body["require24_x7_response"] = require_24_by_7_response
    body["problem_start_time"] = start_time
    body["technical_ticket_details"] = {"resource_id": technical_resource}
    body["quota_ticket_details"] = quotaBody

    return client.create_support_ticket_for_subscription(support_ticket_name=ticket_name,
                                                         create_support_ticket_parameters=body)


def wait_support_tickets(cmd,
                         ticket_name=None):
    from azext_support._client_factory import cf_support_tickets
    return get_support_tickets(cmd, cf_support_tickets, ticket_name=ticket_name)


def create_support_tickets_communications(cmd, client,
                                          ticket_name=None,
                                          communication_name=None,
                                          communication_body=None,
                                          communication_subject=None,
                                          communication_sender=None):
    rsp = client.check_name_availability_for_support_ticket_communication(support_ticket_name=ticket_name,
                                                                          name=communication_name,
                                                                          type="Microsoft.Support/communications")
    if not rsp["name_available"]:
        raise CLIError('Support ticket communication name \'' + communication_name +
                       '\' not available. Please try again with another name!')

    body = {}
    body["sender"] = communication_sender
    body["subject"] = communication_subject
    body["body"] = communication_body

    return client.create_support_ticket_communication(support_ticket_name=ticket_name,
                                                      communication_name=communication_name,
                                                      create_communication_parameters=body)


def wait_support_tickets_communications(cmd,
                                        ticket_name=None,
                                        communication_name=None):
    from azext_support._client_factory import cf_communications
    return get_support_tickets_communications(cmd, cf_communications, ticket_name=ticket_name,
                                              communication_name=communication_name)
