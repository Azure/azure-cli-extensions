# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azext_load.data_plane.utils.utils import (
    get_admin_data_plane_client)
from azext_load.data_plane.load_notifications import utils
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core.exceptions import ResourceNotFoundError

logger = get_logger(__name__)


def create_notification_rule(
    cmd,
    load_test_resource,
    action_groups,
    notification_rule_id,
    resource_group_name=None,
    event=None,
    display_name=None,
    test_ids=None,
    all_tests=False,
    all_events=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    body = None
    try:
        body = client.get_notification_rule(notification_rule_id)
    except ResourceNotFoundError:
        pass

    if body is not None:
        msg = "Notification rule with given ID: %s already exists." % notification_rule_id
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)

    logger.info("Creating notification rule.")
    notification_rule = utils.get_notification_rule_create_body(
        action_groups, event, display_name, test_ids, all_tests, all_events
    )
    logger.info("Notification rule object to be sent for create: %s", notification_rule)
    response = client.create_or_update_notification_rule(notification_rule_id, notification_rule)
    logger.info("Notification rule created successfully.")
    return response.as_dict()


def update_notification_rule(
    cmd,
    load_test_resource,
    notification_rule_id,
    resource_group_name=None,
    action_groups=None,
    add_event=None,
    remove_event=None,
    display_name=None,
    test_ids=None,
    all_tests=False,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Updating notification rule.")
    try:
        existing_notification_rule = client.get_notification_rule(notification_rule_id)
    except ResourceNotFoundError:
        msg = "Notification rule with given ID: %s does not exist." % notification_rule_id
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)
    logger.info("Existing notification rule: %s", existing_notification_rule)
    new_notification_rule = utils.get_notification_rule_update_body(
        existing_notification_rule,
        action_groups,
        add_event,
        remove_event,
        display_name,
        test_ids,
        all_tests,
    )
    logger.info("Incoming changes in notification rule: %s", new_notification_rule)
    response = client.create_or_update_notification_rule(notification_rule_id, new_notification_rule)
    logger.info("Notification rule updated successfully.")
    return response.as_dict()


def show_notification_rule(
    cmd,
    load_test_resource,
    notification_rule_id,
    resource_group_name=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info(
        "Getting notification rule with id: %s", notification_rule_id
    )
    response = client.get_notification_rule(notification_rule_id)
    logger.debug("Fetched notification rule: %s", response)
    return response.as_dict()


def list_notification_rules(
    cmd,
    load_test_resource,
    resource_group_name=None,
    test_ids=None,
):
    logger.info("Listing notification rules.")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    if test_ids:
        test_ids = ",".join(test_ids)
        logger.info("Filtering notification rules by test ids: %s", test_ids)
    responses = client.list_notification_rules(test_ids=test_ids)
    logger.info("Retrieved notification rules: %s", responses)
    return [response.as_dict() for response in responses]


def delete_notification_rule(
    cmd,
    load_test_resource,
    notification_rule_id,
    resource_group_name=None,
):
    logger.info(
        "Deleting notification rule with id: %s", notification_rule_id
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    client.delete_notification_rule(notification_rule_id)
    logger.info("Deleted notification rule.")
