# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid

from azext_load.data_plane.utils.constants import LoadTestConfigKeys, LoadTestFailureCriteriaKeys
from azext_load.data_plane.utils import validators
from azext_load.data_plane.utils.models import EngineIdentityType
from azure.mgmt.core.tools import is_valid_resource_id
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
    max_vu_per_engine = data[LoadTestConfigKeys.AUTOSTOP].get(LoadTestConfigKeys.AUTOSTOP_MAX_VU_PER_ENGINE)
    # pylint: disable-next=protected-access
    validators._validate_autostop_criteria_configfile(error_rate, time_window, max_vu_per_engine)
    autostop_criteria = {
        "autoStopDisabled": False,
    }
    if error_rate is not None:
        autostop_criteria["errorRate"] = error_rate
    if time_window is not None:
        autostop_criteria["errorRateTimeWindowInSeconds"] = time_window
    if max_vu_per_engine is not None:
        autostop_criteria["maximumVirtualUsersPerEngine"] = max_vu_per_engine
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
        raise ValueError("Invalid failure criteria: {}, {}".format(failure_criteria, parts))
    _, condition_value = parts
    if (
        ")" not in condition_value
        or len(condition_value.split(")")) != 2
        or condition_value.endswith(")")
    ):
        raise ValueError("Invalid failure criteria: {}".format(failure_criteria))


def _validate_server_failure_criteria(failure_criteria):
    required_keys = [
        LoadTestConfigKeys.METRIC_NAME,
        LoadTestConfigKeys.RESOURCEID,
        LoadTestConfigKeys.AGGREGATION,
        LoadTestConfigKeys.CONDITION,
        LoadTestConfigKeys.VALUE
    ]
    if not isinstance(failure_criteria, dict):
        raise ValueError("Invalid failure criteria for server metrics: {}".format(failure_criteria))
    if any(failure_criteria.get(key) is None for key in required_keys):
        raise ValueError("Invalid failure criteria for server metrics: {}".format(failure_criteria))
    if failure_criteria.get(LoadTestConfigKeys.CONDITION) not in LoadTestFailureCriteriaKeys.CONDITION_ENUM_MAP:
        raise ValueError("Invalid failure criteria for server metrics: {}".format(failure_criteria))


def _get_random_uuid():
    return str(uuid.uuid4())


# pylint: disable=line-too-long
# Disabling this because dictionary key are too long
def yaml_parse_failure_criteria(data):
    passfail_criteria = {}
    passfail_criteria["passFailMetrics"] = {}
    passfail_criteria["passFailServerMetrics"] = {}
    if isinstance(data[LoadTestConfigKeys.FAILURE_CRITERIA], dict):
        pf_criteria_yaml_object = data[LoadTestConfigKeys.FAILURE_CRITERIA].get(LoadTestConfigKeys.CLIENT_METRICS_PF)
        pf_server_criteria_yaml_object = data[LoadTestConfigKeys.FAILURE_CRITERIA].get(LoadTestConfigKeys.SERVER_METRICS_PF)
    else:
        pf_criteria_yaml_object = data.get(LoadTestConfigKeys.FAILURE_CRITERIA)
        pf_server_criteria_yaml_object = None
    if pf_criteria_yaml_object is not None:
        for items in pf_criteria_yaml_object:
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
    if pf_server_criteria_yaml_object is not None:
        for items in pf_server_criteria_yaml_object:
            metric_id = _get_random_uuid()
            components = items
            try:
                _validate_server_failure_criteria(components)
            except InvalidArgumentValueError as e:
                logger.error("Invalid failure criteria for server metrics: %s", str(e))
            passfail_criteria["passFailServerMetrics"][metric_id] = {}
            passfail_criteria["passFailServerMetrics"][metric_id]["metricName"] = (
                components.get(LoadTestConfigKeys.METRIC_NAME)
            )
            passfail_criteria["passFailServerMetrics"][metric_id]["metricNameSpace"] = (
                components.get(LoadTestConfigKeys.METRIC_NAMESPACE) or
                get_resource_type_from_resource_id(
                    components.get(LoadTestConfigKeys.RESOURCEID)
                )
            )
            passfail_criteria["passFailServerMetrics"][metric_id]["resourceId"] = (
                components.get(LoadTestConfigKeys.RESOURCEID)
            )
            passfail_criteria["passFailServerMetrics"][metric_id]["aggregation"] = (
                components.get(LoadTestConfigKeys.AGGREGATION)
            )
            passfail_criteria["passFailServerMetrics"][metric_id]["condition"] = (
                LoadTestFailureCriteriaKeys.CONDITION_ENUM_MAP[components.get(LoadTestConfigKeys.CONDITION)]
            )
            passfail_criteria["passFailServerMetrics"][metric_id]["value"] = (
                components.get(LoadTestConfigKeys.VALUE)
            )
    return passfail_criteria


def get_resource_type_from_resource_id(resource_id):
    if resource_id and len(resource_id.split("/")) > 7:
        parts = resource_id.split("/")
        return "{}/{}".format(parts[6], parts[7])


def get_resource_name_from_resource_id(resource_id):
    if resource_id and len(resource_id.split("/")) > 8:
        parts = resource_id.split("/")
        return parts[8]


def get_resource_group_from_resource_id(resource_id):
    if resource_id and len(resource_id.split("/")) > 4:
        parts = resource_id.split("/")
        return parts[4]


def get_subscription_id_from_resource_id(resource_id):
    if resource_id and len(resource_id.split("/")) > 2:
        parts = resource_id.split("/")
        return parts[2]


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


# pylint: disable=line-too-long
# Disabling this because dictionary key are too long
def yaml_parse_engine_identities(data):
    engine_identities = []
    engine_reference_type = None
    metric_reference_identity = None
    keyvault_reference_identity = None
    reference_identities = data.get(LoadTestConfigKeys.REFERENCE_IDENTITIES)
    for identity in reference_identities:
        curr_ref_type = identity.get(LoadTestConfigKeys.TYPE)
        curr_ref_value = identity.get(LoadTestConfigKeys.VALUE)
        if curr_ref_type != EngineIdentityType.UserAssigned:
            if curr_ref_value:
                raise InvalidArgumentValueError(
                    "Reference identity value should be provided only for UserAssigned identity type."
                )
        else:
            if not is_valid_resource_id(curr_ref_value):
                raise InvalidArgumentValueError(
                    "{} is not a valid resource id".format(curr_ref_value)
                )
        if identity and identity.get(LoadTestConfigKeys.KIND) == LoadTestConfigKeys.ENGINE:
            if engine_reference_type and curr_ref_type != engine_reference_type:
                raise InvalidArgumentValueError(
                    "Engine identity type should be either None, SystemAssigned, or UserAssigned. A combination of identity types are not supported."
                )
            engine_identities.append(curr_ref_value)
            engine_reference_type = curr_ref_type
        elif identity.get(LoadTestConfigKeys.KIND) == LoadTestConfigKeys.METRICS:
            if metric_reference_identity is not None:
                raise InvalidArgumentValueError(
                    "Only one Metrics reference identity should be provided in the referenceIdentities array"
                )
            metric_reference_identity = identity
        elif identity.get(LoadTestConfigKeys.KIND) == LoadTestConfigKeys.KEY_VAULT:
            if keyvault_reference_identity is not None:
                raise InvalidArgumentValueError(
                    "Only one KeyVault reference identity should be provided in the referenceIdentities array"
                )
            keyvault_reference_identity = identity

    return (
        engine_reference_type,
        engine_identities,
        keyvault_reference_identity.get(LoadTestConfigKeys.VALUE) if keyvault_reference_identity else None,
        keyvault_reference_identity.get(LoadTestConfigKeys.TYPE) if keyvault_reference_identity else None,
        metric_reference_identity.get(LoadTestConfigKeys.VALUE) if metric_reference_identity else None,
        metric_reference_identity.get(LoadTestConfigKeys.TYPE) if metric_reference_identity else None,
    )


def update_reference_identities(new_body, data):
    if data.get(LoadTestConfigKeys.REFERENCE_IDENTITIES):
        (
            engine_reference_type, engine_identities,
            keyvault_reference_identity, key_vault_reference_type,
            metric_reference_identity, metrics_reference_type) = yaml_parse_engine_identities(data=data)
        new_body["engineBuiltinIdentityType"], new_body["engineBuiltinIdentityIds"] = engine_reference_type, engine_identities
        if new_body["engineBuiltinIdentityType"] in [EngineIdentityType.NoneValue, EngineIdentityType.SystemAssigned]:
            new_body.pop("engineBuiltinIdentityIds")
        if keyvault_reference_identity is not None:
            new_body["keyvaultReferenceIdentityId"] = keyvault_reference_identity
            new_body["keyvaultReferenceIdentityType"] = EngineIdentityType.UserAssigned
        elif key_vault_reference_type == EngineIdentityType.SystemAssigned:
            new_body["keyvaultReferenceIdentityType"] = EngineIdentityType.SystemAssigned
        if metric_reference_identity is not None:
            new_body["metricsReferenceIdentityId"] = metric_reference_identity
            new_body["metricsReferenceIdentityType"] = EngineIdentityType.UserAssigned
        elif metrics_reference_type == EngineIdentityType.SystemAssigned:
            new_body["metricsReferenceIdentityType"] = EngineIdentityType.SystemAssigned
# pylint: enable=line-too-long
