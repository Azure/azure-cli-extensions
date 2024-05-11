# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azext_support._utils import is_technical_ticket, parse_support_area_path
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.tools import is_valid_resource_id, parse_resource_id
import os

logger = get_logger(__name__)

# file constants
MAX_FILE_NAME_LENGTH = 110
MIN_FILE_SIZE = 1
MAX_FILE_SIZE = 1024 * 1024 * 5
unsupported_file_extensions_set = {
    ".bat",
    ".cmd",
    ".exe",
    ".ps1",
    ".js",
    ".vbs",
    ".com",
    ".lnk",
    ".reg",
    ".bin",
    ".cpl",
    ".inf",
    ".ins",
    ".isu",
    ".job",
    ".jse",
    ".msi",
    ".msp",
    ".paf",
    ".pif",
    ".rgs",
    ".scr",
    ".sct",
    ".vbe",
    ".vb",
    ".ws",
    ".wsf",
    ".wsh",
}


def _validate_tickets_create(
    cli_ctx, problem_classification, ticket_name, technical_resource=None
):
    _validate_problem_classification_name(problem_classification)
    if is_technical_ticket(
        parse_support_area_path(problem_classification)["service_name"]
    ):
        _validate_resource_name(cli_ctx, technical_resource)
    _check_name_availability_subscription(
        cli_ctx, ticket_name, "Microsoft.Support/supportTickets"
    )


def _validate_tickets_create_no_subscription(
    cli_ctx, problem_classification, ticket_name, technical_resource=None
):
    _validate_problem_classification_name(problem_classification)
    if is_technical_ticket(
        parse_support_area_path(problem_classification)["service_name"]
    ):
        _validate_resource_name(cli_ctx, technical_resource)
    _check_name_availability_no_subscription(
        cli_ctx, ticket_name, "Microsoft.Support/supportTickets"
    )


def _validate_problem_classification_name(problem_classification_id):
    if parse_support_area_path(problem_classification_id) is None:
        raise CLIError(
            "Problem classification id is invalid. Please use 'az support services "
            + "problem-classifications list' to get the most recent set of problem classification "
            + "ids for your service."
        )


def _validate_resource_name(cli_ctx, resource_id):
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
        raise CLIError(
            "{0} {1} does not match with {2}".format(
                base_error_msg, subid, session_subid
            )
        )


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


def _check_name_availability_subscription(cli_ctx, resource_name, resource_type):
    from .aaz.latest.support.in_subscription import CheckNameAvailability

    check_name_availability_input = {"name": resource_name, "type": resource_type}
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(
        command_args=check_name_availability_input
    )
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])


def _check_name_availability_subscription_ticket(
    cli_ctx, ticket_name, resource_name, resource_type
):
    from .aaz.latest.support.in_subscription.tickets import CheckNameAvailability

    check_name_availability_input = {
        "support_ticket_name": ticket_name,
        "name": resource_name,
        "type": resource_type,
    }
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(
        command_args=check_name_availability_input
    )
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])


def _check_name_availability_no_subscription(cli_ctx, resource_name, resource_type):
    from .aaz.latest.support.no_subscription import CheckNameAvailability

    check_name_availability_input = {"name": resource_name, "type": resource_type}
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(
        command_args=check_name_availability_input
    )
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])


def _check_name_availability_no_subscription_ticket(
    cli_ctx, ticket_name, resource_name, resource_type
):
    from .aaz.latest.support.no_subscription.tickets import CheckNameAvailability

    check_name_availability_input = {
        "support_ticket_name": ticket_name,
        "name": resource_name,
        "type": resource_type,
    }
    resp = CheckNameAvailability(cli_ctx=cli_ctx)(
        command_args=check_name_availability_input
    )
    if not resp["nameAvailable"]:
        raise CLIError(resp["message"])


def _validate_file_path(file_path):
    if not os.path.exists(file_path):
        raise CLIError("File does not exist!")


def _validate_file_name(file_name):
    if len(file_name) > MAX_FILE_NAME_LENGTH:
        raise CLIError("File name should not be more than 110 characters.")


def _validate_file_size(file_size):
    if (file_size > MAX_FILE_SIZE) or (file_size < MIN_FILE_SIZE):
        raise CLIError("The file must be between 1 and 5242880 bytes")


def _validate_file_extension(file_extension):
    if file_extension in unsupported_file_extensions_set:
        raise CLIError("The file extension is not supported.")
