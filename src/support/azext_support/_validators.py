# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import traceback
import uuid
from datetime import datetime

from azext_support._client_factory import cf_resource, cf_support_tickets, cf_communications
from azext_support._utils import is_technical_ticket, parse_support_area_path
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError
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
    raise ValueError("Input '{0}' not valid. Valid example: 2017-02-11T23:59:59Z".format(string))


def validate_tickets_create(cmd, namespace):
    _validate_problem_classification_name(namespace.problem_classification)
    if is_technical_ticket(parse_support_area_path(namespace.problem_classification)["service_name"]):
        _validate_resource_name(cmd, namespace.technical_resource)
    _validate_ticket_name(cmd, namespace.ticket_name)


def validate_communication_create(cmd, namespace):
    _validate_communication_name(cmd, namespace.ticket_name, namespace.communication_name)


def _validate_communication_name(cmd, ticket_name, communication_name):
    client = cf_communications(cmd.cli_ctx)
    rsp = client.check_name_availability(support_ticket_name=ticket_name, name=communication_name,
                                         type="Microsoft.Support/communications")
    if not rsp.name_available:
        raise CLIError("Support ticket communication name '{0}' not available. ".format(communication_name) +
                       "Please try again with another name.")


def _validate_ticket_name(cmd, ticket_name):
    client = cf_support_tickets(cmd.cli_ctx)
    rsp = client.check_name_availability(name=ticket_name, type="Microsoft.Support/supportTickets")
    if not rsp.name_available:
        raise CLIError("Support ticket name '{0}' not available. ".format(ticket_name) +
                       "Please try again with another name.")


def _validate_problem_classification_name(problem_classification_id):
    if parse_support_area_path(problem_classification_id) is None:
        raise CLIError("Problem classification id is invalid. Please use 'az support services " +
                       "problem-classifications list' to get the most recent set of problem classification " +
                       "ids for your service.")


def _validate_resource_name(cmd, resource_id):
    if resource_id is None:
        return
    client = cf_resource(cmd.cli_ctx)
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

    try:
        client.resources.get(resource_group_name=parsed_resource['resource_group'],
                             resource_provider_namespace=parsed_resource["namespace"],
                             parent_resource_path=parsed_resource["resource_parent"],
                             resource_type=parsed_resource["type"],
                             resource_name=parsed_resource["name"],
                             api_version="2019-08-01")
    except CloudError as e:
        logger.debug(traceback.format_exc())
        raise CLIError("{0} {1}".format(base_error_msg, e.error.message))


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False
