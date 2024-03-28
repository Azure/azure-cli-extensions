# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
from datetime import datetime

from azext_support._client_factory import cf_support_tickets, cf_communications
from azext_support._utils import is_technical_ticket, parse_support_area_path
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.tools import is_valid_resource_id, parse_resource_id

logger = get_logger(__name__)


def datetime_type(string):
    """ Validates UTC datetime. Examples of accepted forms:
    2017-12-31T01:11:59Z,2017-12-31T01:11Z or 2017-12-31T01Z or 2017-12-31 """
    accepted_date_formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%MZ', '%Y-%m-%dT%HZ', '%Y-%m-%d']
    for form in accepted_date_formats:
        try:
            return datetime.strptime(string, form)
        except ValueError:
            continue
    raise ValueError(f"Input '{string}' not valid. Valid example: 2017-02-11T23:59:59Z")


def validate_tickets_create(cmd, namespace):
    _validate_problem_classification_name(namespace.problem_classification)
    if is_technical_ticket(parse_support_area_path(namespace.problem_classification)["service_name"]):
        _validate_resource_name(cmd, namespace.technical_resource)
    _validate_ticket_name(cmd, namespace.ticket_name)


def validate_communication_create(cmd, namespace):
    _validate_communication_name(cmd, namespace.ticket_name, namespace.communication_name)


def _validate_communication_name(cmd, ticket_name, communication_name):
    client = cf_communications(cmd.cli_ctx)
    check_name_availability_input = {"name": communication_name, "type": "Microsoft.Support/communications"}
    rsp = client.check_name_availability(support_ticket_name=ticket_name,
                                         check_name_availability_input=check_name_availability_input)
    if not rsp.name_available:
        raise CLIError(rsp.message)


def _validate_ticket_name(cmd, ticket_name):
    client = cf_support_tickets(cmd.cli_ctx)
    check_name_availability_input = {"name": ticket_name, "type": "Microsoft.Support/supportTickets"}
    rsp = client.check_name_availability(check_name_availability_input=check_name_availability_input)
    if not rsp.name_available:
        raise CLIError(rsp.message)


def _validate_problem_classification_name(problem_classification_id):
    if parse_support_area_path(problem_classification_id) is None:
        raise CLIError("Problem classification id is invalid. Please use 'az support services " +
                       "problem-classifications list' to get the most recent set of problem classification " +
                       "ids for your service.")


def _validate_resource_name(cmd, resource_id):
    if resource_id is None:
        return

    base_error_msg = f"Technical resource argument {resource_id} is invalid."
    if not is_valid_resource_id(resource_id):
        raise CLIError(base_error_msg)

    parsed_resource = parse_resource_id(resource_id)
    subid = parsed_resource["subscription"]
    if not _is_guid(subid):
        raise CLIError(f"{base_error_msg} Subscription id {subid} is invalid.")

    session_subid = get_subscription_id(cmd.cli_ctx)
    if subid != session_subid:
        raise CLIError(f"{base_error_msg} {subid} does not match with {session_subid}")


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False
