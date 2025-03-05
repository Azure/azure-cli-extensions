# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.data_plane.utils.utils import (
    get_admin_data_plane_client,
    )

from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger
from azext_load.vendored_sdks.loadtesting.models import ( _models as models, _enums as enums)
import azext_load.data_plane.load_trigger.utils as utils

logger = get_logger(__name__)

def create_trigger_schedule(
    cmd,
    load_test_resource,
    resource_group_name=None,
    trigger_id=None,
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
    logger.info("Creating trigger schedule")
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
        start_date_time= trigger_start_date_time,
        state=enums.TriggerState.ACTIVE,
        display_name=display_name,
        description=description,
    )
    logger.debug("Trigger schedule body: %s", trigger_body)
    try:
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=trigger_body)
        logger.debug("Created trigger schedule: %s", response)
        logger.info("Creating trigger schedule completed")
        return response
    except Exception as e:
        logger.error("Error occurred while creating trigger schedule: %s", str(e))


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
    logger.info("Updating trigger schedule with name")
    existing_trigger_schedule: models.ScheduleTestsTrigger = None
    try:
        existing_trigger_schedule = client.get_trigger(trigger_id)
    except Exception as e:
        logger.debug("Error occurred while fetching trigger schedule: %s", str(e))
        logger.error("Trigger schedule with id: %s not found.", trigger_id)
        return
    logger.debug("Existing trigger schedule: %s", existing_trigger_schedule)
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
    new_trigger_body = utils.get_schedule_trigger_body_for_update(
        existing_trigger_schedule,
        recurrence_body,
        display_name,
        description,
        trigger_start_date_time,
        test_ids,
    )
    
    logger.debug("Trigger schedule body: %s", new_trigger_body)
    logger.debug("Trigger schedule body to be sent for update: %s", existing_trigger_schedule)
    try:
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=new_trigger_body)
        logger.debug("Updated trigger schedule: %s", response)
        logger.info("Updating trigger schedule completed")
        return response
    except Exception as e:
        logger.error("Error occurred while updating trigger schedule: %s", str(e))

def delete_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Deleting trigger schedule with name"
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    client.delete_trigger(trigger_id)
    logger.info("Deleting trigger schedule completed.")


def get_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Getting trigger schedule with name"
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    response = client.get_trigger(trigger_id)
    logger.debug("Fetched trigger schedule: %s", response)
    return response


def pause_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Pausing trigger schedule with name"
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    result = None
    try:
        result = client.get_trigger(trigger_id=trigger_id)
    except Exception as e:
        logger.debug("Error occurred while fetching trigger schedule: %s", str(e))
        logger.error("Trigger schedule with id: %s not found.", trigger_id)
        return
    logger.debug("Existing trigger object: %s", result)
    if result.state == enums.TriggerState.ACTIVE:
        result.state = enums.TriggerState.PAUSED
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=result)
        logger.debug("Paused trigger schedule: %s", response)
        return response
    else:
        logger.error("Trigger schedule is not active. It is in %s state.", result.state.value)


def enable_trigger_schedule(
    cmd,
    load_test_resource,
    trigger_id,
    resource_group_name=None,
):
    logger.info(
        "Enabling trigger schedule with name"
    )
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    result = None
    try:
        result = client.get_trigger(trigger_id=trigger_id)
    except Exception as e:
        logger.debug("Error occurred while fetching trigger schedule: %s", str(e))
        logger.error("Trigger schedule with id: %s not found.", trigger_id)
        return
    logger.debug("Existing trigger object: %s", result)
    if result.state == enums.TriggerState.PAUSED:
        result.state = enums.TriggerState.ACTIVE
        response = client.create_or_update_trigger(trigger_id=trigger_id, body=result)
        logger.debug("Enabled trigger schedule: %s", response)
        return response
    else:
        logger.error("Trigger schedule is not paused. It is in %s state.", result.state.value)


def list_trigger_schedules(
    cmd,
    load_test_resource,
    resource_group_name=None,
    trigger_states=None,
    test_ids=None,
):
    logger.info("Listing trigger schedules")
    client = get_admin_data_plane_client(cmd, load_test_resource, resource_group_name)
    if trigger_states:
        trigger_states = ",".join(trigger_states)
    if test_ids:
        test_ids = ",".join(test_ids)
    logger.info("Trigger states: %s", trigger_states)
    response = client.list_trigger(test_ids=test_ids, states=trigger_states)
    logger.debug("Fetched list of trigger schedules: %s", response)
    return response