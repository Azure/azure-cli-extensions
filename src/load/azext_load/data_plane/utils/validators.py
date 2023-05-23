import os
import re
from collections import OrderedDict
from datetime import datetime

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import CLIError
from msrestazure.tools import is_valid_resource_id
import yaml

from . import utils

logger = utils.get_logger(__name__)


def validate_test_id(namespace):
    if not isinstance(namespace.test_id, str):
        raise InvalidArgumentValueError(
            f"Invalid test-id type: {type(namespace.test_id)}"
        )
    if not re.match("^[a-z0-9_-]*$", namespace.test_id):
        raise InvalidArgumentValueError("Invalid test-id value")


def validate_test_run_id(namespace):
    if namespace.test_run_id is None:
        namespace.test_run_id = utils.get_random_uuid()
    if not isinstance(namespace.test_run_id, str):
        raise InvalidArgumentValueError(
            f"Invalid test-run-id type: {type(namespace.test_run_id)}"
        )
    if not re.match("^[a-z0-9_-]*$", namespace.test_run_id):
        raise InvalidArgumentValueError("Invalid test-run-id value")


def _validate_akv_url(string, type="secrets|certificates|keys|storage"):
    regex = f"^https://[a-zA-Z0-9_-]+\\.(?:vault|vault-int)\\.(?:azure|azure-int|usgovcloudapi|microsoftazure)\\.(?:net|cn|de)/(?:{type})/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+|$)$"
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
        result = {comps[0]: comps[1]} if len(comps) > 1 else {string: ""}
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
        if not _validate_akv_url(comps[1], "secrets"):
            raise InvalidArgumentValueError(f"Invalid AKV Secret URL: {string}")
        result = (
            {comps[0]: {"type": "AKV_SECRET_URI", "value": comps[1]}}
            if len(comps) > 1
            else {string: ""}
        )
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
    if not _validate_akv_url(comps[1], "certificates"):
        raise InvalidArgumentValueError(f"Invalid AKV Certificate URL: {comps[1]}")
    namespace.certificate = {
        "name": comps[0],
        "type": "AKV_CERT_URI",
        "value": comps[1],
    }


def validate_subnet_id(namespace):
    if namespace.subnet_id is None:
        return
    if not is_valid_resource_id(namespace.subnet_id):
        raise InvalidArgumentValueError(
            f"{namespace.subnet_id} is not a valid Azure resource ID."
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
            f"Type of app-component-id and app-component-type mismatch: {provider_name} vs {namespace.app_component_type}"
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
        logger.debug(
            "Directory does not exist. Created as --force is passed - %s",
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
    namespace.path = _validate_path(namespace.load_test_config_file, is_dir=False)
    try:
        with open(namespace.path, "r") as file:
            yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise InvalidArgumentValueError(
            f"Invalid YAML file: {namespace.path}. Error: {e}"
        )


def validate_dir_path(namespace):
    namespace.path = _validate_path(namespace.path, is_dir=True)


def validate_file_path(namespace):
    namespace.path = _validate_path(namespace.path, is_dir=False)


def _validate_path(path, is_dir=False):
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
            raise InvalidArgumentValueError(
                f"Provided path '{path}' is not writable or executable"
            )
    else:
        if not os.path.isfile(path):
            raise InvalidArgumentValueError(f"Provided path '{path}' is not a file")
        if not os.access(path, os.R_OK):
            raise InvalidArgumentValueError(f"Provided path '{path}' is not readable")
    return path


allowed_file_types = ["ADDITIONAL_ARTIFACTS", "JMX_FILE", "USER_PROPERTIES"]


def validate_file_type(namespace):
    if namespace.file_type is None:
        return
    if not isinstance(namespace.file_type, str):
        raise InvalidArgumentValueError(
            f"Invalid file-type type: {type(namespace.file_type)}"
        )
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
    except CLIError:
        pass
    try:
        datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
        return
    except CLIError:
        pass
    raise InvalidArgumentValueError(
        f"Invalid time format: '{string}'. Expected ISO 8601 format."
    )


allowed_intervals = ["PT10S", "PT1H", "PT1M", "PT5M", "PT5S"]


def validate_interval(namespace):
    if namespace.interval is None:
        return
    if not isinstance(namespace.interval, str):
        raise InvalidArgumentValueError(
            f"Invalid interval type: {type(namespace.interval)}"
        )
    if namespace.interval not in allowed_intervals:
        raise InvalidArgumentValueError(
            f"Invalid interval value: {namespace.interval}. Allowed values: {', '.join(allowed_intervals)}"
        )


allowed_metric_namespaces = ["LoadTestRunMetrics", "EngineHealthMetrics"]


def validate_metric_namespaces(namespace):
    if not isinstance(namespace.metric_namespace, str):
        raise InvalidArgumentValueError(
            f"Invalid metric-namespace type: {type(namespace.metric_namespace)}"
        )
    if namespace.metric_namespace not in allowed_metric_namespaces:
        raise InvalidArgumentValueError(
            f"Invalid metric-namespace value: {namespace.metric_namespace}. Allowed values: {', '.join(allowed_metric_namespaces)}"
        )


def validate_dimension_filters(namespace):
    """Extracts multiple space and comma-separated dimension filters in key1[=value1,value2] [key2[=value3, value4]] format"""
    if isinstance(namespace.dimension_filters, list):
        filters_dict = OrderedDict()
        for item in namespace.dimension_filters:
            filter = _validate_dimension_filter(item)
            for key, value in filter.items():
                if key in filters_dict:
                    filters_dict[key].extend(value)
                else:
                    filters_dict[key] = value
        filters_list = []
        for key, value in filters_dict.items():
            filters_list.append({"name": key, "values": value})
        namespace.dimension_filters = filters_list


def _validate_dimension_filter(string):
    """Extracts a single comma-separated dimension filters in key1[=value1,value2] format"""
    result = {}
    if string:
        comps = string.split("=", 1)
        result = {comps[0]: comps[1].split(",")} if len(comps) > 1 else {string: ""}
    return result
