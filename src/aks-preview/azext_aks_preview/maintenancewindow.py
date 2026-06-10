# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.core.azclierror import RequiredArgumentMissingError

# Reuse the schedule construction + cross-arg validation helpers from the
# sibling maintenanceconfiguration module. The peer MaintenanceWindow
# resource uses the exact same Schedule / DailySchedule / WeeklySchedule /
# AbsoluteMonthlySchedule / RelativeMonthlySchedule models — only the
# outer wrapper (Properties + Location + Tags) differs.
from azext_aks_preview.maintenanceconfiguration import constructSchedule
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW

logger = get_logger(__name__)


def constructMaintenanceWindowResource(cmd, raw_parameters):
    """Build a MaintenanceWindowResource ready to be passed to
    MaintenanceWindowsOperations.begin_create_or_update.

    Expects raw_parameters to be a dict (typically `locals()` from a custom
    command) carrying: location, tags, schedule_type, interval_days,
    interval_weeks, interval_months, day_of_week, day_of_month, week_index,
    duration_hours, utc_offset, start_date, start_time.

    `location` is required by the SDK model (TrackedResource); callers
    should fall back to `get_rg_location(cmd.cli_ctx, resource_group_name)`
    when the user did not pass --location, matching how
    `aks_nodepool_snapshot_create` handles location.
    """
    location = raw_parameters.get("location")
    tags = raw_parameters.get("tags")
    start_date = raw_parameters.get("start_date")
    start_time = raw_parameters.get("start_time")
    duration_hours = raw_parameters.get("duration_hours")
    utc_offset = raw_parameters.get("utc_offset")

    if start_time is None:
        raise RequiredArgumentMissingError(
            "Please specify --start-time for the maintenance window."
        )
    if duration_hours is None:
        raise RequiredArgumentMissingError(
            "Please specify --duration for the maintenance window."
        )

    schedule = constructSchedule(cmd, raw_parameters)

    MaintenanceWindowResource = cmd.get_models(
        "MaintenanceWindowResource",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="maintenance_windows",
    )
    MaintenanceWindowResourceProperties = cmd.get_models(
        "MaintenanceWindowResourceProperties",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="maintenance_windows",
    )

    properties = MaintenanceWindowResourceProperties(
        schedule=schedule,
        start_date=start_date,
        start_time=start_time,
        duration_hours=duration_hours,
        utc_offset=utc_offset,
    )
    return MaintenanceWindowResource(
        location=location,
        tags=tags,
        properties=properties,
    )


def hasAnyScheduleArg(raw_parameters):
    """Return True if any schedule-shaping arg is present. Used by `update`
    to decide between the sync tags-only PATCH path and the LRO full-PUT path.
    """
    keys = (
        "schedule_type",
        "interval_days",
        "interval_weeks",
        "interval_months",
        "day_of_week",
        "day_of_month",
        "week_index",
        "duration_hours",
        "utc_offset",
        "start_date",
        "start_time",
    )
    return any(raw_parameters.get(k) is not None for k in keys)
