# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
from collections import OrderedDict
from datetime import datetime

import yaml
from azure.cli.core.azclierror import InvalidArgumentValueError, FileOperationError
from azure.cli.core.commands.parameters import get_subscription_locations
from azure.mgmt.core.tools import is_valid_resource_id
from knack.log import get_logger

from . import utils
from .models import (
    AllowedFileTypes,
    AllowedIntervals,
    AllowedMetricNamespaces,
    AllowedTestTypes,
    AllowedTestPlanFileExtensions,
    EngineIdentityType,
)

logger = get_logger(__name__)


def validate_test_id(namespace):
    """Validates test-id"""
    if not isinstance(namespace.test_id, str):
        raise InvalidArgumentValueError(
            f"Invalid test-id type: {type(namespace.test_id)}"
        )
    if not re.match("^[a-z0-9_-]*$", namespace.test_id):
        raise InvalidArgumentValueError("Invalid test-id value")


def validate_test_run_id(namespace):
    """Validates test-run-id"""
    if namespace.test_run_id is None:
        namespace.test_run_id = utils.get_random_uuid()
    if not isinstance(namespace.test_run_id, str):
        raise InvalidArgumentValueError(
            f"Invalid test-run-id type: {type(namespace.test_run_id)}"
        )
    if not re.match("^[a-z0-9_-]*$", namespace.test_run_id):
        raise InvalidArgumentValueError("Invalid test-run-id value")


def _validate_akv_url(string, url_type="secrets|certificates|keys|storage"):
    """Validates Azure Key Vault URL"""
    # pylint: disable-next=line-too-long
    regex = f"^https://[a-zA-Z0-9_-]+\\.(?:vault|vault-int)\\.(?:azure|azure-int|usgovcloudapi|microsoftazure)\\.(?:net|cn|de)/(?:{url_type})/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+|$)$"
    return re.match(regex, string, re.IGNORECASE)


def validate_env_vars(namespace):
    """Extracts multiple space-separated env vars in key[=value] format"""
    if isinstance(namespace.env, list):
        env_vars_dict = {}
        for item in namespace.env:
            env_vars_dict.update(_validate_env_var(item))
        namespace.env = env_vars_dict


def _validate_env_var(string):
    """Extracts a single env var in key[=value] format"""
    result = {}
    if string:
        comps = string.split("=", 1)
        if len(comps) != 2:
            raise InvalidArgumentValueError(f"Invalid env argument: {string}")
        if comps[1] in ["null", ""]:
            result = {comps[0]: None}
        else:
            result = {comps[0]: comps[1]}
    return result


def validate_secrets(namespace):
    """Extracts multiple space-separated secrets in key[=value] format"""
    if isinstance(namespace.secrets, list):
        secrets_dict = {}
        for item in namespace.secrets:
            secrets_dict.update(_validate_secret(item))
        namespace.secrets = secrets_dict


def _validate_secret(string):
    """Extracts a single secret in key[=value] format"""
    result = {}
    if string:
        comps = string.split("=", 1)
        if len(comps) != 2:
            raise InvalidArgumentValueError(f"Invalid secret argument: {string}")
        if comps[1] in ["null", ""]:
            result = {comps[0]: None}
        elif not _validate_akv_url(comps[1], "secrets"):
            raise InvalidArgumentValueError(
                f"Invalid Azure Key Vault Secret URL: {comps[1]}"
            )
        else:
            result = {comps[0]: {"type": "AKV_SECRET_URI", "value": comps[1]}}
    return result


def validate_certificate(namespace):
    """Extracts single certificate in key[=value] format"""
    if namespace.certificate is None:
        return
    if isinstance(namespace.certificate, list):
        if len(namespace.certificate) > 1:
            raise InvalidArgumentValueError("Only one certificate is supported")
        certificate = namespace.certificate[0]
    elif isinstance(namespace.certificate, str):
        certificate = namespace.certificate
    else:
        raise InvalidArgumentValueError(
            f"Invalid certificate value type: {type(namespace.certificate)}"
        )
    comps = certificate.split("=", 1)
    if len(comps) != 2:
        raise InvalidArgumentValueError(f"Invalid certificate argument: {certificate}")
    if (comps[1] not in ["", "null"]) and not _validate_akv_url(comps[1], "certificates"):
        raise InvalidArgumentValueError(
            f"Invalid Azure Key Vault Certificate URL: {comps[1]}"
        )
    if comps[1] in ["null", ""]:
        namespace.certificate = "null"
    else:
        namespace.certificate = {
            "name": comps[0],
            "type": "AKV_CERT_URI",
            "value": comps[1],
        }


def validate_subnet_id(namespace):
    if namespace.subnet_id is None:
        return
    if namespace.subnet_id in ["null", ""]:
        namespace.subnet_id = "null"
        return
    if not is_valid_resource_id(namespace.subnet_id):
        raise InvalidArgumentValueError(
            f"{namespace.subnet_id} is not a valid Azure subnet resource ID."
        )


def validate_app_component_id(namespace):
    if not isinstance(namespace.app_component_id, str):
        raise InvalidArgumentValueError(
            f"Invalid app-component-id type: {type(namespace.app_component_id)}"
        )
    if not is_valid_resource_id(namespace.app_component_id):
        raise InvalidArgumentValueError(
            f"app-component-id is not a valid Azure Resource ID: {namespace.app_component_id}"
        )


def validate_app_component_type(namespace):
    provider_name = "/".join(namespace.app_component_id.split("/")[6:8]).casefold()
    if provider_name != namespace.app_component_type.casefold():
        raise InvalidArgumentValueError(
            "Type of app-component-id and app-component-type mismatch: "
            f"{provider_name} vs {namespace.app_component_type}"
        )


def validate_metric_id(namespace):
    if not isinstance(namespace.metric_id, str):
        raise InvalidArgumentValueError(
            f"Invalid metric-id type: {type(namespace.metric_id)}"
        )
    if not is_valid_resource_id(namespace.metric_id):
        raise InvalidArgumentValueError(
            f"metric-id is not a valid Azure Resource ID: {namespace.metric_id}"
        )
    if "metric" not in namespace.metric_id.casefold():
        raise InvalidArgumentValueError(
            f"Provided Azure Resource ID is not a valid server metrics resource: {namespace.metric_id}"
        )


def validate_download(namespace):
    if not isinstance(namespace.path, str):
        raise InvalidArgumentValueError(f"Invalid path type: {type(namespace.path)}")

    namespace.path = os.path.normpath(os.path.expanduser(namespace.path))

    # Create the directories if they do not exist
    if namespace.force:
        os.makedirs(namespace.path, exist_ok=True)
        logger.warning(
            "\"%s\" directory does not exist. Created as --force option is passed.",
            namespace.path,
        )
        return

    validate_dir_path(namespace)


def validate_load_test_config_file(namespace):
    if namespace.load_test_config_file is None:
        return
    if not isinstance(namespace.load_test_config_file, str):
        raise InvalidArgumentValueError(
            f"Invalid load-test-config-file type: {type(namespace.load_test_config_file)}"
        )
    namespace.load_test_config_file = _validate_path(
        namespace.load_test_config_file, is_dir=False
    )
    try:
        with open(namespace.load_test_config_file, "r", encoding="UTF-8") as file:
            yaml.safe_load(file)
    except Exception as e:
        raise FileOperationError(
            f"Failed to read YAML file: {namespace.load_test_config_file}. Error: {e}"
        ) from e


def validate_dir_path(namespace):
    namespace.path = _validate_path(namespace.path, is_dir=True)


def validate_file_path(namespace):
    namespace.path = _validate_path(namespace.path, is_dir=False)


def validate_test_plan_path(namespace):
    if namespace.test_plan is None:
        return
    namespace.test_plan = _validate_path(namespace.test_plan, is_dir=False)

    _, file_extension = os.path.splitext(namespace.test_plan)
    if file_extension.casefold() not in utils.get_enum_values(AllowedTestPlanFileExtensions):
        raise InvalidArgumentValueError(
            f"Invalid test plan file extension: {file_extension}. "
            f"Allowed values: {', '.join(AllowedTestPlanFileExtensions)} "
            f"for {', '.join(utils.get_enum_values(AllowedTestTypes))} test types respectively"
        )


def validate_test_type(namespace):
    if namespace.test_type is None:
        return
    if not isinstance(namespace.test_type, str):
        raise InvalidArgumentValueError(
            f"Invalid test-type type: {type(namespace.test_type)}"
        )
    allowed_test_types = utils.get_enum_values(AllowedTestTypes)
    if namespace.test_type not in allowed_test_types:
        raise InvalidArgumentValueError(
            f"Invalid test-type value: {namespace.test_type}. Allowed values: {', '.join(allowed_test_types)}"
        )


def _validate_path(path, is_dir=False):
    logger.info("path: %s", path)
    if not isinstance(path, str):
        raise InvalidArgumentValueError(f"Invalid path type: {type(path)}")

    path = os.path.normpath(os.path.expanduser(path))

    if not os.path.exists(path):
        raise InvalidArgumentValueError(f"Provided path '{path}' does not exist")
    if is_dir:
        if not os.path.isdir(path):
            raise InvalidArgumentValueError(
                f"Provided path '{path}' is not a directory"
            )
        if not os.access(path, os.W_OK | os.X_OK):
            raise FileOperationError(
                f"Provided path '{path}' is not writable or executable"
            )
    else:
        if not os.path.isfile(path):
            raise InvalidArgumentValueError(f"Provided path '{path}' is not a file")
        if not os.access(path, os.R_OK):
            raise FileOperationError(f"Provided path '{path}' is not readable")
    return path


def _validate_file_stats(path, file_type=None):
    if file_type == AllowedFileTypes.ZIPPED_ARTIFACTS and os.stat(path).st_size > 52428800:
        logger.info("zip artifact size %s", os.stat(path).st_size)
        raise FileOperationError(f"Provided ZIP artifact '{path}' exceeds size limit of 50 MB")


def validate_file_type(namespace):
    if namespace.file_type is None:
        return
    if not isinstance(namespace.file_type, str):
        raise InvalidArgumentValueError(
            f"Invalid file-type type: {type(namespace.file_type)}"
        )
    allowed_file_types = utils.get_enum_values(AllowedFileTypes)
    if namespace.file_type not in allowed_file_types:
        raise InvalidArgumentValueError(
            f"Invalid file-type value: {namespace.file_type}. Allowed values: {', '.join(allowed_file_types)}"
        )


def validate_start_iso_time(namespace):
    _validate_iso_time(namespace.start_time)


def validate_end_iso_time(namespace):
    _validate_iso_time(namespace.end_time)


def _validate_iso_time(string):
    if string is None:
        return
    if not isinstance(string, str):
        raise InvalidArgumentValueError(f"Invalid time type: {type(string)}")
    try:
        datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ")
        return
    except ValueError:
        pass
    try:
        datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
        return
    except ValueError:
        pass
    raise InvalidArgumentValueError(
        f"Invalid time format: '{string}'. Expected ISO 8601 format."
    )


def validate_interval(namespace):
    if namespace.interval is None:
        return
    if not isinstance(namespace.interval, str):
        raise InvalidArgumentValueError(
            f"Invalid interval type: {type(namespace.interval)}"
        )
    allowed_intervals = utils.get_enum_values(AllowedIntervals)
    if namespace.interval not in allowed_intervals:
        raise InvalidArgumentValueError(
            f"Invalid interval value: {namespace.interval}. Allowed values: {', '.join(allowed_intervals)}"
        )


def validate_metric_namespaces(namespace):
    if not isinstance(namespace.metric_namespace, str):
        raise InvalidArgumentValueError(
            f"Invalid metric-namespace type: {type(namespace.metric_namespace)}"
        )
    allowed_metric_namespaces = utils.get_enum_values(AllowedMetricNamespaces)
    if namespace.metric_namespace not in allowed_metric_namespaces:
        raise InvalidArgumentValueError(
            f"Invalid metric-namespace value: {namespace.metric_namespace}. "
            f"Allowed values: {', '.join(allowed_metric_namespaces)}"
        )


def validate_dimension_filters(namespace):
    """Extracts multiple space separated dimension filters in key1[=value1] key1[=value2] key2[=value3] format"""
    if isinstance(namespace.dimension_filters, list):
        filters_dict = OrderedDict()
        for item in namespace.dimension_filters:
            dimension_filter = _validate_dimension_filter(item)
            for key, value in dimension_filter.items():
                if key in filters_dict:
                    filters_dict[key].append(value)
                else:
                    filters_dict[key] = [value]
        filters_list = []
        for key, value in filters_dict.items():
            filters_list.append({"name": key, "values": value})
        namespace.dimension_filters = filters_list


def _validate_dimension_filter(string):
    """Extracts a single dimension filters in key1[=value1] format"""
    result = {}
    if string:
        comps = string.split("=", 1)
        result = {comps[0]: comps[1]} if len(comps) > 1 else {string: ""}
    return result


def validate_split_csv(namespace):
    if namespace.split_csv is None:
        return
    if not isinstance(namespace.split_csv, str):
        raise InvalidArgumentValueError(
            f"Invalid split-csv type: {type(namespace.split_csv)}"
        )
    if namespace.split_csv.casefold() not in [
        "true",
        "false",
        "yes",
        "no",
        "y",
        "n",
    ]:
        raise InvalidArgumentValueError(
            f"Invalid split-csv value: {namespace.split_csv}. Allowed values: true, false, yes, no, y, n"
        )
    if namespace.split_csv.casefold() in ["true", "yes", "y"]:
        namespace.split_csv = True
    else:
        namespace.split_csv = False


def validate_disable_public_ip(namespace):
    if namespace.disable_public_ip is None:
        return
    if not isinstance(namespace.disable_public_ip, str):
        raise InvalidArgumentValueError(
            f"Invalid disable-public-ip type: {type(namespace.disable_public_ip)}"
        )
    if namespace.disable_public_ip.casefold() not in [
        "true",
        "false",
    ]:
        raise InvalidArgumentValueError(
            f"Invalid disable-public-ip value: {namespace.disable_public_ip}. Allowed values: true, false"
        )
    if namespace.disable_public_ip.casefold() in ["true"]:
        namespace.disable_public_ip = True
    else:
        namespace.disable_public_ip = False


def validate_autostop_enable_disable(namespace):
    if namespace.autostop is None:
        return
    if not isinstance(namespace.autostop, str) or namespace.autostop.casefold() not in ["enable", "disable"]:
        raise InvalidArgumentValueError(
            f"Invalid autostop type: {type(namespace.autostop)}. Allowed values: enable, disable"
        )
    if namespace.autostop.casefold() not in ["disable"]:
        namespace.autostop = True
    else:
        namespace.autostop = False


def validate_autostop_error_rate_time_window(namespace):
    if namespace.autostop_error_rate_time_window is None:
        return
    if not isinstance(namespace.autostop_error_rate_time_window, int):
        raise InvalidArgumentValueError(
            f"Invalid autostop-time-window type: {type(namespace.autostop_error_rate_time_window)}"
        )
    if namespace.autostop_error_rate_time_window < 0:
        raise InvalidArgumentValueError(
            "Autostop error rate time window should be greater than or equal to 0"
        )


def validate_autostop_error_rate(namespace):
    if namespace.autostop_error_rate is None:
        return
    if not isinstance(namespace.autostop_error_rate, float):
        raise InvalidArgumentValueError(
            f"Invalid autostop-error-rate type: {type(namespace.autostop_error_rate)}"
        )
    if namespace.autostop_error_rate < 0.0 or namespace.autostop_error_rate > 100.0:
        raise InvalidArgumentValueError(
            "Autostop error rate should be in range of [0.0,100.0]"
        )


def _validate_autostop_disable_configfile(autostop):
    if autostop.casefold() not in ["disable"]:
        raise InvalidArgumentValueError(
            "Invalid value for autoStop. Valid values are 'disable' or an object with errorPercentage and timeWindow"
        )


def _validate_autostop_criteria_configfile(error_rate, time_window):
    if error_rate is not None:
        if isinstance(error_rate, float) and (error_rate < 0.0 or error_rate > 100.0):
            raise InvalidArgumentValueError(
                "Invalid value for errorPercentage. Value should be a number between 0.0 and 100.0"
            )
        if isinstance(error_rate, int) and (error_rate < 0 or error_rate > 100):
            raise InvalidArgumentValueError(
                "Invalid value for errorPercentage. Value should be a number between 0.0 and 100.0"
            )
    if time_window is not None and (not isinstance(time_window, int) or time_window < 0):
        raise InvalidArgumentValueError(
            "Invalid value for timeWindow. Value should be an integer greater than or equal to 0"
        )


def validate_regionwise_engines(cmd, namespace):
    if namespace.regionwise_engines is None:
        return
    if not isinstance(namespace.regionwise_engines, list):
        raise InvalidArgumentValueError(
            f"Invalid regionwise-engines type: {type(namespace.regionwise_engines)}. \
                Expected list in the format of region1=engineCount1 region2=engineCount2"
        )
    regionwise_engines = []
    subscription_locations = get_subscription_locations(cmd.cli_ctx)
    location_names = [location.name for location in subscription_locations]
    for item in namespace.regionwise_engines:
        if not isinstance(item, str) or "=" not in item:
            raise InvalidArgumentValueError(
                f"Invalid regionwise-engines item type: {type(item)}. Expected region=engineCount"
            )
        key, value = item.split("=", 1)
        if not key or not value:
            raise InvalidArgumentValueError(
                f"Invalid regionwise-engines item: {item}. Region or engine count cannot be empty"
            )
        if key.strip().lower() not in location_names:
            raise InvalidArgumentValueError(
                f"Invalid regionwise-engines item key: {key}. Expected Azure region"
            )
        try:
            value = int(value.strip())
        except ValueError:
            raise InvalidArgumentValueError(
                f"Invalid regionwise-engines item value: {value}. Expected integer"
            )
        regionwise_engines.append({"region": key.strip().lower(), "engineInstances": value})
    namespace.regionwise_engines = regionwise_engines


def validate_engine_ref_ids(namespace):
    """Extracts multiple space-separated identities"""
    if isinstance(namespace.engine_ref_ids, list):
        for item in namespace.engine_ref_ids:
            if not is_valid_resource_id(item):
                raise InvalidArgumentValueError(f"Invalid engine-ref-ids value: {item}")


# pylint: disable=line-too-long
# Disabling this because dictionary key are too long
def validate_keyvault_identity_ref_id(namespace):
    """Validates managed identity reference id"""
    if (
        isinstance(namespace.key_vault_reference_identity, str)
        and not namespace.key_vault_reference_identity.lower() in ["null", ""]
        and not is_valid_resource_id(namespace.key_vault_reference_identity)
    ):
        raise InvalidArgumentValueError("Invalid keyvault-ref-id value: {}".format(namespace.key_vault_reference_identity))


def validate_metrics_identity_ref_id(namespace):
    """Validates managed identity reference id"""
    if (
        isinstance(namespace.metrics_reference_identity, str)
        and not namespace.metrics_reference_identity.lower() in ["null", ""]
        and not is_valid_resource_id(namespace.metrics_reference_identity)
    ):
        raise InvalidArgumentValueError("Invalid metrics-ref-id value: {}".format(namespace.metrics_reference_identity))


def validate_engine_ref_ids_and_type(incoming_engine_ref_id_type, engine_ref_ids, exisiting_engine_ref_id_type=None):
    """Validates combination of engine-ref-id-type and engine-ref-ids"""

    # if engine_ref_id_type is None or SystemAssigned, then no value for engine_ref_ids is expected:
    engine_ref_id_type = incoming_engine_ref_id_type or exisiting_engine_ref_id_type
    if engine_ref_id_type != EngineIdentityType.UserAssigned and engine_ref_ids:
        raise InvalidArgumentValueError(
            "engine-ref-ids should not be provided when engine-ref-id-type is None or SystemAssigned"
        )

    # If engine_ref_id_type is UserAssigned, then engine_ref_ids is expected.
    if incoming_engine_ref_id_type == EngineIdentityType.UserAssigned and engine_ref_ids is None:
        raise InvalidArgumentValueError(
            "Atleast one engine-ref-ids should be provided when engine-ref-id-type is UserAssigned"
        )
