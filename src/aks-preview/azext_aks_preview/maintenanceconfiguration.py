# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.util import get_file_json
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW

logger = get_logger(__name__)


def getMaintenanceConfiguration(cmd, config_file, weekday, start_hour):
    if config_file is not None and weekday is not None:
        raise CLIError('either config-file or weekday can be supplied.')
    if weekday is None and start_hour is not None:
        raise CLIError('if maintenance-start-hour is supplied, maintenance-weekday must be supplied too.')
    # get models
    MaintenanceConfiguration = cmd.get_models('MaintenanceConfiguration', resource_type=CUSTOM_MGMT_AKS_PREVIEW, operation_group='maintenance_configurations')
    TimeInWeek = cmd.get_models('TimeInWeek', resource_type=CUSTOM_MGMT_AKS_PREVIEW, operation_group='maintenance_configurations')

    if weekday is not None:
        dict = {}
        dict["day"] = weekday
        if start_hour is not None:
            dict["hour_slots"] = [start_hour]
        timeInWeek = TimeInWeek(**dict)
        result = MaintenanceConfiguration()
        result.time_in_week = [timeInWeek]
        result.not_allowed_time = []
        return result

    return _get_maintenance_config(cmd, config_file)


def aks_maintenanceconfiguration_update_internal(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    config_name,
    config_file,
    weekday,
    start_hour
):
    logger.info('resource_group_name: %s, cluster_name: %s, config_name: %s, config_file: %s, weekday: %s, start_hour: %s ', resource_group_name, cluster_name, config_name, config_file, weekday, start_hour)

    config = getMaintenanceConfiguration(cmd, config_file, weekday, start_hour)
    return client.create_or_update(resource_group_name=resource_group_name, resource_name=cluster_name, config_name=config_name, parameters=config)


def _get_maintenance_config(cmd, file_path):
    # get models
    MaintenanceConfiguration = cmd.get_models('MaintenanceConfiguration', resource_type=CUSTOM_MGMT_AKS_PREVIEW, operation_group='maintenance_configurations')
    TimeInWeek = cmd.get_models('TimeInWeek', resource_type=CUSTOM_MGMT_AKS_PREVIEW, operation_group='maintenance_configurations')
    TimeSpan = cmd.get_models('TimeSpan', resource_type=CUSTOM_MGMT_AKS_PREVIEW, operation_group='maintenance_configurations')

    maintenance_config = get_file_json(file_path)
    logger.info(maintenance_config)
    if not isinstance(maintenance_config, dict):
        raise CLIError("Error reading maintenance configuration at {}.".format(file_path))
    time_in_week = maintenance_config["timeInWeek"]
    not_allowed_time = maintenance_config["notAllowedTime"]
    week_schedule = []
    if time_in_week is not None:
        for item in time_in_week:
            w = TimeInWeek(**item)
            logger.info('day: %s, time slots: %s ', w.day, w.hour_slots)
            week_schedule.append(w)
    not_allowed = []
    if not_allowed_time is not None:
        for item in not_allowed_time:
            t = TimeSpan(**item)
            logger.info('start: %s, end: %s ', t.start, t.end)
            not_allowed.append(t)
    result = MaintenanceConfiguration()
    result.time_in_week = week_schedule
    result.not_allowed_time = not_allowed
    return result
