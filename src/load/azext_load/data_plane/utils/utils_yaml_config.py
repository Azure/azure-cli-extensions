# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azext_load.data_plane.utils.constants import LoadTestConfigKeys
from azext_load.data_plane.utils import validators
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
)
from azure.cli.core.commands.parameters import get_subscription_locations

from knack.log import get_logger

logger = get_logger(__name__)


def yaml_parse_autostop_criteria(data):
    if (isinstance(data[LoadTestConfigKeys.AUTOSTOP], str)):
        # pylint: disable-next=protected-access
        validators._validate_autostop_disable_configfile(data[LoadTestConfigKeys.AUTOSTOP])
        return {
            "autoStopDisabled": True,
        }
    error_rate = data[LoadTestConfigKeys.AUTOSTOP].get(LoadTestConfigKeys.AUTOSTOP_ERROR_RATE)
    time_window = data[LoadTestConfigKeys.AUTOSTOP].get(LoadTestConfigKeys.AUTOSTOP_ERROR_RATE_TIME_WINDOW)
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


def _yaml_parse_splitcsv(data):
    if not isinstance(data.get(LoadTestConfigKeys.SPLIT_CSV), bool):
        raise InvalidArgumentValueError(
            "Invalid value for splitAllCSVs. Allowed values are boolean true or false"
        )
    return data.get(LoadTestConfigKeys.SPLIT_CSV)


def _validate_failure_criteria(failure_criteria):
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


def _get_random_uuid():
    return str(uuid.uuid4())


def yaml_parse_failure_criteria(data):
    passfail_criteria = {}
    passfail_criteria["passFailMetrics"] = {}
    for items in data[LoadTestConfigKeys.FAILURE_CRITERIA]:
        metric_id = _get_random_uuid()
        # check if item is string or dict. if string then no name is provided
        name = None
        components = items
        if isinstance(items, dict):
            name = list(items.keys())[0]
            components = list(items.values())[0]
        # validate failure criteria
        try:
            _validate_failure_criteria(components)
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


def _parse_regionwise_loadtest_config(cmd, regionwise_loadtest_config):
    logger.debug("Parsing regionwise load test configuration")
    regional_load_test_config = []
    subscription_locations = get_subscription_locations(cmd.cli_ctx)
    location_names = [location.name for location in subscription_locations]
    for region_load in regionwise_loadtest_config:
        region_name = region_load.get(LoadTestConfigKeys.REGION)
        if region_name is None or not isinstance(region_name, str):
            raise InvalidArgumentValueError("Region name is required of type string")
        if region_name.lower() not in location_names:
            raise InvalidArgumentValueError(f"Invalid region: {region_name}. Expected Azure region")
        engine_instances = region_load.get(LoadTestConfigKeys.ENGINE_INSTANCES)
        if engine_instances is None or not isinstance(engine_instances, int):
            raise InvalidArgumentValueError("Engine instances is required of type integer")
        regional_load_test_config.append({"region": region_name.lower(), "engineInstances": engine_instances})
    logger.debug("Successfully parsed regionwise load test configuration: %s", regional_load_test_config)
    return regional_load_test_config


def yaml_parse_loadtest_configuration(cmd, data):
    load_test_configuration = {}
    load_test_configuration["engineInstances"] = data.get(LoadTestConfigKeys.ENGINE_INSTANCES)
    if data.get(LoadTestConfigKeys.REGIONAL_LOADTEST_CONFIG) is not None:
        load_test_configuration["regionalLoadTestConfig"] = _parse_regionwise_loadtest_config(
            cmd,
            data.get(LoadTestConfigKeys.REGIONAL_LOADTEST_CONFIG)
        )
    # quick test and split csv not supported currently in CLI
    load_test_configuration["quickStartTest"] = False
    if data.get(LoadTestConfigKeys.QUICK_START):
        logger.warning(
            "Quick start test is not supported currently in CLI. Please use portal to run quick start test"
        )
    if data.get(LoadTestConfigKeys.SPLIT_CSV) is not None:
        load_test_configuration["splitAllCSVs"] = _yaml_parse_splitcsv(data=data)
    return load_test_configuration
