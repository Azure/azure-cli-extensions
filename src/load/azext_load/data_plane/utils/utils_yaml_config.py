# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azext_load.data_plane.utils import validators
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
)

from knack.log import get_logger

logger = get_logger(__name__)


def yaml_parse_autostop_criteria(data):
    if (isinstance(data["autoStop"], str)):
        # pylint: disable-next=protected-access
        validators._validate_autostop_disable_configfile(data["autoStop"])
        return {
            "autoStopDisabled": True,
        }
    error_rate = data["autoStop"].get("errorPercentage")
    time_window = data["autoStop"].get("timeWindow")
    # pylint: disable-next=protected-access
    validators._validate_autostop_criteria_configfile(error_rate, time_window)
    autostop_criteria = {
        "autoStopDisabled": False,
    }
    if error_rate is not None:
        autostop_criteria["errorRate"] = error_rate
    if time_window is not None:
        autostop_criteria["errorRateTimeWindowInSeconds"] = time_window
    return autostop_criteria


def yaml_parse_splitcsv(data):
    if not isinstance(data.get("splitAllCSVs"), bool):
        raise InvalidArgumentValueError(
            "Invalid value for splitAllCSVs. Allowed values are boolean true or false"
        )
    return data.get("splitAllCSVs")


def validate_failure_criteria(failure_criteria):
    parts = failure_criteria.split("(")
    if len(parts) != 2:
        raise ValueError(f"Invalid failure criteria: {failure_criteria}")
    _, condition_value = parts
    if (
        ")" not in condition_value
        or len(condition_value.split(")")) != 2
        or condition_value.endswith(")")
    ):
        raise ValueError(f"Invalid failure criteria: {failure_criteria}")


def get_random_uuid():
    return str(uuid.uuid4())


def yaml_parse_failure_criteria(data):
    passfail_criteria = {}
    passfail_criteria["passFailMetrics"] = {}
    for items in data["failureCriteria"]:
        metric_id = get_random_uuid()
        # check if item is string or dict. if string then no name is provided
        name = None
        components = items
        if isinstance(items, dict):
            name = list(items.keys())[0]
            components = list(items.values())[0]
        # validate failure criteria
        try:
            validate_failure_criteria(components)
        except InvalidArgumentValueError as e:
            logger.error("Invalid failure criteria: %s", str(e))
        passfail_criteria["passFailMetrics"][metric_id] = {}
        passfail_criteria["passFailMetrics"][metric_id]["aggregate"] = (
            components.split("(")[0].strip()
        )
        passfail_criteria["passFailMetrics"][metric_id][
            "clientMetric"
        ] = (components.split("(")[1].split(")")[0].strip())
        passfail_criteria["passFailMetrics"][metric_id]["condition"] = (
            components.split(")")[1].strip()[0]
        )
        passfail_criteria["passFailMetrics"][metric_id]["value"] = (
            components.split(
                passfail_criteria["passFailMetrics"][metric_id]["condition"]
            )[1].strip()
        )
        if name is not None:
            passfail_criteria["passFailMetrics"][metric_id][
                "requestName"
            ] = name
    return passfail_criteria
