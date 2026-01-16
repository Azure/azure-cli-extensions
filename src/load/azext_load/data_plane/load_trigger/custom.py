# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.core.exceptions import ResourceNotFoundError
from azure.cli.core.azclierror import InvalidArgumentValueError, ValidationError
from knack.log import get_logger
from azext_load.data_plane.utils.utils import (
    get_admin_data_plane_client)
from azext_load.vendored_sdks.loadtesting.models import (_models as models, _enums as enums)
from azext_load.data_plane.load_trigger import utils

logger = get_logger(__name__)


def create_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
    description=None,
    display_name=None,
    trigger_start_date_time=None,
    recurrence_type=None,
    recurrence_interval=None,
    recurrence_index=None,
    recurrence_cron_expression=None,
    recurrence_dates_in_month=None,
    recurrence_week_days=None,
    end_after_occurrence=None,
    end_after_date_time=None,
    test_ids=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Creating schedule trigger.")
    try:
        client.get_trigger(trigger_id)
        msg = "Trigger schedule with id: {} already exists.".format(trigger_id)
        logger.error(msg)
        raise InvalidArgumentValueError(msg)
    except ResourceNotFoundError:
        pass
    recurrence_end_body = utils.get_recurrence_end_body(
        end_after_occurrence,
        end_after_date_time,
    )
    logger.debug("Recurrence end object: %s", recurrence_end_body)
    recurrence_body = utils.get_recurrence_body(
        recurrence_type,
        recurrence_interval,
        recurrence_index,
        recurrence_cron_expression,
        recurrence_dates_in_month,
        recurrence_week_days,
        recurrence_end_body,
    )
    logger.debug("Recurrence object: %s", recurrence_body)
    trigger_body = models.ScheduleTestsTrigger(
        test_ids=test_ids,
        recurrence=recurrence_body,
        start_date_time=trigger_start_date_time,
        state=enums.TriggerState.ACTIVE,
        display_name=display_name,
        description=description,
    )
    logger.debug("Trigger schedule body: %s", trigger_body)
    try:
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=trigger_body)
        logger.debug("Created trigger schedule: %s", response)
        logger.info("Creating trigger schedule completed")
        return response.as_dict()
    except Exception:
        logger.error("Error occurred while creating schedule trigger.")
        raise


def update_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
    description=None,
    display_name=None,
    trigger_start_date_time=None,
    recurrence_type=None,
    recurrence_interval=None,
    recurrence_index=None,
    recurrence_cron_expression=None,
    recurrence_dates_in_month=None,
    recurrence_week_days=None,
    end_after_occurrence=None,
    end_after_date_time=None,
    test_ids=None,
):
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    logger.info("Updating schedule trigger with id: %s", trigger_id)
    existing_trigger_schedule: models.ScheduleTestsTrigger = None
    try:
        existing_trigger_schedule = client.get_trigger(trigger_id)
    except ResourceNotFoundError:
        msg = "Schedule trigger with id: {} does not exists.".format(trigger_id)
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)
    logger.debug("Existing schedule trigger: %s", existing_trigger_schedule)
    recurrence_end_body = utils.get_recurrence_end_body(
        end_after_occurrence,
        end_after_date_time,
        existing_trigger_schedule.recurrence.recurrence_end if existing_trigger_schedule.recurrence else None
    )
    logger.debug("Recurrence end object: %s", recurrence_end_body)
    recurrence_body = utils.get_recurrence_body_for_update(
        recurrence_type,
        recurrence_interval,
        recurrence_index,
        recurrence_cron_expression,
        recurrence_dates_in_month,
        recurrence_week_days,
        recurrence_end_body,
        existing_trigger_schedule.recurrence
    )
    logger.debug("Recurrence object: %s", recurrence_body)
    new_trigger_body = models.ScheduleTestsTrigger(
        test_ids=test_ids,
        recurrence=recurrence_body,
        start_date_time=trigger_start_date_time,
        display_name=display_name,
        description=description,
    )
    new_trigger_body.state = existing_trigger_schedule.state
    logger.debug("Schedule trigger body to be sent for update: %s", new_trigger_body)
    try:
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=new_trigger_body)
        logger.debug("Updated schedule trigger: %s", response)
        logger.info("Updating schedule trigger completed")
        return response.as_dict()
    except Exception:
        logger.error("Error occurred while updating schedule trigger.")
        raise


def delete_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Deleting schedule trigger with id: %s", trigger_id
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    client.delete_trigger(trigger_id)
    logger.info("Deleting schedule trigger completed.")


def get_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Getting schedule trigger with id: %s", trigger_id
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.get_trigger(trigger_id)
    logger.debug("Fetched schedule trigger: %s", response)
    return response.as_dict()


def pause_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Pausing schedule trigger with id: %s", trigger_id
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    existing_trigger_schedule: models.ScheduleTestsTrigger = None
    try:
        existing_trigger_schedule = client.get_trigger(trigger_id)
    except ResourceNotFoundError:
        msg = "Schedule trigger with id: {} does not exists.".format(trigger_id)
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)
    logger.debug("Existing schedule trigger object: %s", existing_trigger_schedule)
    if existing_trigger_schedule.state == enums.TriggerState.ACTIVE:
        existing_trigger_schedule.state = enums.TriggerState.PAUSED
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=existing_trigger_schedule)
        logger.debug("Paused schedule trigger: %s", response)
        return response.as_dict()
    if existing_trigger_schedule.state == enums.TriggerState.COMPLETED:
        msg = "Schedule trigger with id: {} is already completed. A completed schedule cannot be paused.".format(trigger_id)
        logger.error(msg)
        raise ValidationError(msg)
    logger.warning("Schedule trigger is not active. It is in %s state. Enable the schedule before performing pause action.", existing_trigger_schedule.state.value)


def enable_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Enabling schedule trigger with id: %s", trigger_id
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    existing_trigger_schedule: models.ScheduleTestsTrigger = None
    try:
        existing_trigger_schedule = client.get_trigger(trigger_id)
    except ResourceNotFoundError:
        msg = "Schedule trigger with id: {} does not exists.".format(trigger_id)
        logger.debug(msg)
        raise InvalidArgumentValueError(msg)
    logger.debug("Existing trigger object: %s", existing_trigger_schedule)
    if existing_trigger_schedule.state != enums.TriggerState.COMPLETED:
        existing_trigger_schedule.state = enums.TriggerState.ACTIVE
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=existing_trigger_schedule)
        logger.debug("Enabled schedule trigger: %s", response)
        return response.as_dict()
    msg = "Schedule trigger with id: {} is already completed. A completed schedule cannot be enabled.".format(trigger_id)
    logger.debug(msg)
    raise ValidationError(msg)


def list_trigger_schedules(
    cmd,
    load_test_resource,
    resource_group_name=None,
    trigger_states=None,
    test_ids=None,
):
    logger.info("Listing schedule triggers.")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    if trigger_states:
        trigger_states = ",".join(trigger_states)
    if test_ids:
        test_ids = ",".join(test_ids)
    logger.info("Schedule trigger states: %s", trigger_states)
    response_list = client.list_triggers(test_ids=test_ids, states=trigger_states)
    logger.debug("Fetched list of schedule triggers: %s", response_list)
    return [response.as_dict() for response in response_list]
