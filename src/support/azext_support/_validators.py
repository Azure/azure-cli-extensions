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
import os

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
    raise ValueError("Input '{0}' not valid. Valid example: 2017-02-11T23:59:59Z".format(string))


def validate_tickets_create(cmd, namespace):
    _validate_problem_classification_name(namespace.problem_classification)
    if is_technical_ticket(parse_support_area_path(namespace.problem_classification)["service_name"]):
        _validate_resource_name(cmd, namespace.technical_resource)
    _validate_ticket_name(cmd, namespace.ticket_name)

def validate_tickets_create_new(cli_ctx, problem_classification, ticket_name, technical_resource=None):
    _validate_problem_classification_name(problem_classification)
    if is_technical_ticket(parse_support_area_path(problem_classification)["service_name"]):
        _validate_resource_name_new(cli_ctx, technical_resource)
    _check_name_availability_subscription(cli_ctx, ticket_name, "Microsoft.Support/supportTickets")

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

    base_error_msg = "Technical resource argument {0} is invalid.".format(resource_id)
    if not is_valid_resource_id(resource_id):
        raise CLIError(base_error_msg)

    parsed_resource = parse_resource_id(resource_id)
    subid = parsed_resource["subscription"]
    if not _is_guid(subid):
        raise CLIError(base_error_msg + "Subscription id {0} is invalid.".format(subid))

    session_subid = get_subscription_id(cmd.cli_ctx)
    if subid != session_subid:
        raise CLIError("{0} {1} does not match with {2}".format(base_error_msg, subid, session_subid))
    
def _validate_resource_name_new(cli_ctx, resource_id):
    if resource_id is None:
        return

    base_error_msg = "Technical resource argument {0} is invalid.".format(resource_id)
    if not is_valid_resource_id(resource_id):
        raise CLIError(base_error_msg)

    parsed_resource = parse_resource_id(resource_id)
    subid = parsed_resource["subscription"]
    if not _is_guid(subid):
        raise CLIError(base_error_msg + "Subscription id {0} is invalid.".format(subid))

    session_subid = get_subscription_id(cli_ctx)
    if subid != session_subid:
        raise CLIError("{0} {1} does not match with {2}".format(base_error_msg, subid, session_subid))


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


def _check_name_availability_subscription(cli_ctx, resource_name, resource_type):
    from .aaz.latest.support.in_subscription import CheckNameAvailability
    check_name_availability_input = {"name": resource_name, "type": resource_type}
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(command_args=check_name_availability_input)
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])


def _check_name_availability_subscription_ticket(cli_ctx, ticket_name, resource_name, resource_type):
    from .aaz.latest.support.in_subscription.tickets import CheckNameAvailability
    check_name_availability_input = {"support_ticket_name": ticket_name, "name": resource_name, "type": resource_type}
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(command_args=check_name_availability_input)
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])


def _check_name_availability_no_subscription(cli_ctx, resource_name, resource_type):
    from .aaz.latest.support.no_subscription import CheckNameAvailability
    check_name_availability_input = {"name": resource_name, "type": resource_type}
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(command_args=check_name_availability_input)
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])

def _check_name_availability_no_subscription_ticket(cli_ctx, ticket_name, resource_name, resource_type):
    from .aaz.latest.support.no_subscription.tickets import CheckNameAvailability
    check_name_availability_input = {"support_ticket_name": ticket_name, "name": resource_name, "type": resource_type}
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(command_args=check_name_availability_input)
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])

def validate_file_path(file_path):
    if not os.path.exists(file_path):
        raise CLIError("File does not exist!")
    
def validate_file_name(file_name):
    max_file_name_length = 110
    if len(file_name) > max_file_name_length:
        raise CLIError("File name should not be more than 110 characters.")
    
def validate_file_size(file_size):
    max_file_size = 5242880
    min_file_size = 1
    if (file_size > max_file_size) or (file_size < min_file_size):
        raise CLIError("The file must be between 1 and 5242880 bytes")

def validate_file_extension(file_extension):
    unsupported_file_extensions = [".bat", ".cmd", ".exe", ".ps1", ".js", ".vbs", ".com", ".lnk", ".reg",
    ".bin", ".cpl", ".inf", ".ins", ".isu", ".job", ".jse", ".lnk", ".msi", ".msp", ".paf", ".pif", ".rgs", 
    ".scr", ".sct", ".svg", ".vbe", ".vb", ".ws", ".wsf", ".wsh", ".htm", ".html"]
    if file_extension in unsupported_file_extensions:
        raise CLIError("The file extension is not supported.")
