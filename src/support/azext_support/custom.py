# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

import json
import base64
import os
import requests
import math
from azext_support._validators import *

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

def encode_string_content(chunk_content):
    return str(base64.b64encode(chunk_content).decode('utf-8'))

def get_file_content(file_path):
    with open(file_path, 'rb') as file:
        content_bytes = file.read()
    return content_bytes

def get_file_name_info(file_path):
    directory, full_file_name = os.path.split(file_path)
    file_name_without_extension, file_extension = os.path.splitext(full_file_name)
    return full_file_name, file_name_without_extension, file_extension

def upload_files_no_subscription(cmd, file_path, file_workspace_name):
    from .aaz.latest.support.no_subscription.file import Create
    from .aaz.latest.support.no_subscription.file import Upload

    ##costants for file upload
    max_chunk_size= 2621440

    validate_file_path(file_path)

    full_file_name, file_extension, file_name_without_extension = get_file_name_info(file_path)
    content = get_file_content(file_path)

    validate_file_extension(file_extension)
    validate_file_name(file_name_without_extension)
    
    file_size = len(content)
    validate_file_size(file_size)
    
    chunk_size = min(max_chunk_size, file_size)
    number_of_chunks = math.ceil(file_size / chunk_size)

    create_input  = { "file_name": full_file_name, "file_workspace_name": file_workspace_name, "file_size": file_size,"chunk_size" : chunk_size, "number_of_chunks" : number_of_chunks }
    resp_create = Create(cli_ctx = cmd.cli_ctx)(command_args=create_input)
    
    for chunk_index in range(number_of_chunks):
        chunk_content = content[chunk_index * chunk_size: (chunk_index + 1) * chunk_size]
        string_encoded_content = encode_string_content(chunk_content)
        upload_input = { "file_name": full_file_name, "file_workspace_name": file_workspace_name, "chunk_index": chunk_index, "content": string_encoded_content, "--file-name": full_file_name, "--file-workspace-name": file_workspace_name }
        resp_upload = Upload(cli_ctx = cmd.cli_ctx)(command_args=upload_input)
        print("DONE")

def upload_files_in_subscription(cmd, file_path, file_workspace_name, subscription_id = None):
    from .aaz.latest.support.in_subscription.file import Create as Create_Sub
    from .aaz.latest.support.in_subscription.file import Upload as Upload_Sub

    print(cmd.cli_ctx)
    ##costants for file upload
    max_chunk_size= 2621440

    validate_file_path(file_path)

    full_file_name, file_extension, file_name_without_extension = get_file_name_info(file_path)
    content = get_file_content(file_path)

    validate_file_extension(file_extension)
    validate_file_name(file_name_without_extension)
    
    file_size = len(content)
    validate_file_size(file_size)
    
    chunk_size = min(max_chunk_size, file_size)
    number_of_chunks = math.ceil(file_size / chunk_size)

    print(bool(subscription_id))
    if (subscription_id):
        create_input  = { "file_name": full_file_name, "file_workspace_name": file_workspace_name, "file_size": file_size,"chunk_size" : chunk_size, "number_of_chunks" : number_of_chunks, "subscription" : subscription_id}
    else:
        create_input  = { "file_name": full_file_name, "file_workspace_name": file_workspace_name, "file_size": file_size,"chunk_size" : chunk_size, "number_of_chunks" : number_of_chunks }
    resp_create = Create_Sub(cli_ctx = cmd.cli_ctx)(command_args=create_input)

    for chunk_index in range(number_of_chunks):
        chunk_content = content[chunk_index * chunk_size: (chunk_index + 1) * chunk_size]
        string_encoded_content = encode_string_content(chunk_content)
        if (subscription_id):
            upload_input = { "file_name": full_file_name, "file_workspace_name": file_workspace_name, "chunk_index": chunk_index, "content": string_encoded_content, "--file-name": full_file_name, "--file-workspace-name": file_workspace_name, "subscription" : subscription_id  }
        else: 
            upload_input = { "file_name": full_file_name, "file_workspace_name": file_workspace_name, "chunk_index": chunk_index, "content": string_encoded_content, "--file-name": full_file_name, "--file-workspace-name": file_workspace_name }
        resp_upload = Upload_Sub(cli_ctx = cmd.cli_ctx)(command_args=upload_input)

