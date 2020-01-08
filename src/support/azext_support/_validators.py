# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import traceback
import uuid
from datetime import datetime

from azext_support._client_factory import (cf_problem_classifications,
                                           cf_resource, cf_services,
                                           cf_support)
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError
from msrestazure.tools import (is_valid_resource_id, parse_resource_id)

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
    raise ValueError("Input '{}' not valid. Valid example: 2017-02-11T23:59:59Z".format(string))


def validate_tickets_create(cmd, namespace):
    _validate_service_name(cmd, namespace.service)
    _validate_problem_classification_name(cmd, namespace.service, namespace.problem_classification)
    _validate_resource_name(cmd, namespace.technical_resource)
    _validate_ticket_name(cmd, namespace.ticket_name)


def validate_communication_create(cmd, namespace):
    _validate_communication_name(cmd, namespace.ticket_name, namespace.communication_name)


def _validate_communication_name(cmd, ticket_name, communication_name):
    client = cf_support(cmd.cli_ctx)
    rsp = client.check_name_availability_for_support_ticket_communication(support_ticket_name=ticket_name,
                                                                          name=communication_name,
                                                                          type="Microsoft.Support/communications")
    if not rsp.name_available:
        raise CLIError('Support ticket communication name \'' + communication_name +
                       '\' not available. Please try again with another name!')


def _validate_ticket_name(cmd, ticket_name):
    client = cf_support(cmd.cli_ctx)
    rsp = client.check_name_availability_with_subscription(name=ticket_name,
                                                           type="Microsoft.Support/supportTickets")
    if not rsp.name_available:
        raise CLIError('Support ticket name \'' + ticket_name + '\' not available. ' +
                       'Please try again with another name!')


def _validate_service_name(cmd, service_id):
    client = cf_services(cmd.cli_ctx)
    service_id_prefix = "/providers/Microsoft.Support/services/"
    service_id_prefix_lowered = service_id_prefix.lower()
    service_id_lowered = service_id.lower()

    # Check validaity of prefix
    if not service_id_lowered.startswith(service_id_prefix_lowered):
        raise CLIError('Service id parameter value is invalid. It should start with ' + service_id_prefix)

    # Check validity of name type
    service_name = service_id_lowered.split(service_id_prefix_lowered)[1]
    if not _is_guid(service_name):
        raise CLIError('Service name ' + service_name + ' is not a valid guid.')

    # Check validity of service name
    try:
        client.get(service_name=service_name)
    except:
        logger.debug(traceback.format_exc())
        raise CLIError('Service name ' + service_name + ' is not valid. ' +
                       'Please run \'az support services list\' to find valid service names.')


def _validate_problem_classification_name(cmd, service_id, problem_classification_id):
    client = cf_problem_classifications(cmd.cli_ctx)
    problem_classification_id_prefix = service_id + "/problemClassifications/"
    problem_classification_id_prefix_lowered = problem_classification_id_prefix.lower()
    problem_classification_id_lowered = problem_classification_id.lower()

    # Check validaity of prefix
    if not problem_classification_id_lowered.startswith(problem_classification_id_prefix_lowered):
        raise CLIError('Problem Classification id parameter value is invalid. It should start with ' +
                       problem_classification_id_prefix)

    # Check validity of name type
    service_id_prefix = "/providers/Microsoft.Support/services/".lower()
    service_name = service_id.lower().split(service_id_prefix)[1]
    problem_classification_name = problem_classification_id_lowered.split(problem_classification_id_prefix_lowered)[1]
    if not _is_guid(problem_classification_name):
        raise CLIError('Problem Classification name ' + problem_classification_name + ' is not a valid guid.')

    # Check validity of problem classification name
    try:
        client.get(service_name=service_name, problem_classification_name=problem_classification_name)
    except:
        logger.debug(traceback.format_exc())
        raise CLIError('Problem classification name ' + problem_classification_name + ' is not valid. ' +
                       'Please run \'az support services problem-classifications list --service-name ' +
                       service_name + '\' to find valid problem classification names.')


def _validate_resource_name(cmd, resource_id):
    client = cf_resource(cmd.cli_ctx)
    base_error_msg = 'Technical resource argument ' + resource_id + ' is not valid. '
    if not is_valid_resource_id(resource_id):
        raise CLIError(base_error_msg)

    parsed_resource = parse_resource_id(resource_id)
    subid = parsed_resource["subscription"]
    if not _is_guid(subid):
        raise CLIError(base_error_msg + "Subscription id " + subid + " is not valid.")

    session_subid = get_subscription_id(cmd.cli_ctx)
    if subid != session_subid:
        raise CLIError(base_error_msg + subid + " does not match with " + session_subid)

    try:
        client.resources.get(resource_group_name=parsed_resource['resource_group'],
                             resource_provider_namespace=parsed_resource["namespace"],
                             parent_resource_path=parsed_resource["resource_parent"],
                             resource_type=parsed_resource["type"],
                             resource_name=parsed_resource["name"],
                             api_version="2019-08-01")
    except CloudError as e:
        logger.debug(traceback.format_exc())
        raise CLIError(base_error_msg + e.error.message)


def _is_guid(guid):
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False
