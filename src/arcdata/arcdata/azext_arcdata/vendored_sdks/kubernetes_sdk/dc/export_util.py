# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import base64
import datetime
import hashlib
import hmac
import json
import os
from enum import Enum
from http import HTTPStatus

import ndjson
import requests
from azext_arcdata.core.http_codes import http_status_codes
from azext_arcdata.core.prompt import prompt_for_input, prompt_y_n
from azext_arcdata.core.util import display, retry
from azext_arcdata.vendored_sdks.arm_sdk.azure import constants as azure_constants
from azext_arcdata.vendored_sdks.arm_sdk.azure.ad_auth_util import acquire_token
from azext_arcdata.dc.constants import (
    DEFAULT_LOG_QUERY_WINDOW_IN_MINUTE,
    DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE,
    DEFAULT_QUERY_WINDOW,
    DEFAULT_USAGE_QUERY_WINDOW_IN_MINUTE,
    INSTANCE_NAME,
    KIND,
    LAST_USAGE_UPLOAD_FLAG,
    NAMESPACE,
)
from azext_arcdata.dc.exceptions import RequestTimeoutError, ServerError

#######################
# TODO: refactor to this package
from azext_arcdata.dc.util import (
    get_config_file_path,
    get_resource_uri,
    write_file,
)
from azext_arcdata.sqlmi.constants import (
    SQLMI_LICENSE_TYPE_BASE_PRICE,
    SQLMI_LICENSE_TYPE_BASE_PRICE_AZURE,
    SQLMI_LICENSE_TYPE_LICENSE_INCLUDED,
    SQLMI_LICENSE_TYPE_LICENSE_INCLUDED_AZURE,
    SQLMI_LICENSE_TYPE_DISASTER_RECOVERY,
    SQLMI_LICENSE_TYPE_DISASTER_RECOVERY_AZURE,
    SQLMI_TIER_BUSINESS_CRITICAL_ALL,
    SQLMI_TIER_BUSINESS_CRITICAL_AZURE,
    SQLMI_TIER_GENERAL_PURPOSE_ALL,
    SQLMI_TIER_GENERAL_PURPOSE_AZURE,
)
from jsonschema import validate
from knack.cli import CLIError
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError, NewConnectionError, TimeoutError
from urllib3.util.retry import Retry

###################


CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5

log = get_logger(__name__)

################################################################################
# Export Types
################################################################################


class ExportType(Enum):
    metrics = "metrics"
    logs = "logs"
    usage = "usage"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @staticmethod
    def list():
        return list(map(lambda c: c.value, ExportType))


# #############################################################################
# Metric
# #############################################################################


class MetricsDataStructure(Enum):
    region_key = "region"
    resource_id_key = "resource_id"
    metrics_key = "metrics"


class AzureResource(object):
    hostname = ""
    location = ""
    resource_id = ""
    instance_type = ""

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AzureMetrics(object):
    location = ""
    resource_id = ""
    metrics = ""

    def __init__(self, **entries):
        self.__dict__.update(entries)


class MetricsQuery(object):
    def __init__(self, instance_type, metric, db, query):
        self.instance_type = instance_type
        self.metric = metric
        self.db = db
        self.query = query


# ##############################################################################
# Metric export/upload functions --
# ##############################################################################

ERROR_IGNORE = (
    "should not be older than 30 minutes and not more than 4 "
    "minutes in the future"
)
"""
Metric error msg could be ignored 
"""


def _post_metrics(url, body, headers):
    import time

    count = 0
    while count < 6:
        response = requests.post(url, data=body, headers=headers)

        log.info("Metrics upload reponse header: {}".format(response.headers))
        try:
            response.raise_for_status()
        except HTTPError as ex:
            if response.status_code == http_status_codes.request_timeout:
                raise RequestTimeoutError(ex)
            elif response.status_code >= 500:
                raise ServerError(ex)
            elif response.status_code == 404:
                count += 1
                if count < 6:
                    time.sleep(5)
                    continue
                else:
                    raise
            else:
                print(response.status_code)
                raise

        return response


def metrics_upload(metrics):

    if metrics is None:
        display("No metrics need to upload.")
    else:
        display("\n")
        for data in metrics:
            resource_id_value = data[MetricsDataStructure.resource_id_key.value]
            region_value = data[MetricsDataStructure.region_key.value]
            metrics = data["metrics"]
            if not resource_id_value or not metrics or not region_value:
                CLIError(
                    "{} is not valid. Please check the file contains {} and "
                    "metrics fields. Or export the data to file and try again."
                )

            current_time = datetime.datetime.utcnow()

            filtered_metrics = list(
                filter(
                    lambda metric: (
                        current_time
                        - datetime.datetime.strptime(
                            metric["time"], "%Y-%m-%dT%H:%M:%SZ"
                        )
                    ).total_seconds()
                    / 60
                    <= 30,
                    metrics,
                )
            )
            if filtered_metrics is None or not filtered_metrics:
                print(
                    "The metrics data are older than 30 minutes for {}, please"
                    " export and upload again.".format(resource_id_value)
                )
                continue
            log.info(
                "Metrics data in file has {} records. {} are in last 30 mins".format(
                    len(metrics), len(filtered_metrics)
                )
            )
            display("Azure resource_id: {}".format(resource_id_value))

            # Setup request header and url
            headers = _set_header()
            url = _set_url(region_value, resource_id_value)
            retry(
                lambda: _post_metrics(
                    url, body=ndjson.dumps(filtered_metrics), headers=headers
                ),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="post metrics data",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                    TimeoutError,
                    RequestTimeoutError,
                    ServerError,
                ),
            )

            display(
                "Metrics upload pushed {} data points successfully.\n".format(
                    len(filtered_metrics)
                )
            )


"""
# Given a resource registered in Azure, returns the k8s namespace and name.
def _parse_resource(resource):
    name = resource[INSTANCE_NAME]
    namespace = resource[NAMESPACE]

    # Resources deployed outside the controller's namespace are named in the
    # format 'namespace_name'
    parts = name.split("_")
    if len(parts) == 2:
        name = parts[1]
    elif len(parts) > 2:
        raise Exception(
            "Cannot parse resource '{}'. Acceptable formats are '"
            "namespace_name' or 'name'.".format(name)
        )
    return namespace, name
"""


def _set_header():
    """
    Authenticate using service principal w/ key.
    """

    headers = {
        "Authorization": "Bearer "
        + acquire_token(azure_constants.AZURE_METRICS_SCOPE),
        "Content-Type": "application/x-ndjson",
    }
    return headers


def _set_url(location, resource_id):
    url = "https://{}.monitoring.azure.com{}/metrics".format(
        location, resource_id
    )
    return url


# ##############################################################################
# Log export/upload functions
# ##############################################################################

LOGS_CONFIG_FILENAME = "logs-config.json"
"""
Log config file name
"""

LOGS_DEFAULT_DURATION = 14
"""
Default log export duration
"""

LOGS_FILE_PATH = "/var/opt/mssql/log/errorlog"
"""
filepath of sql error logs
"""

SQL_MI_CONTAINER_NAME = "arc-sqlmi"
"""
container name of SQL MI
"""

LOGS_MAXIMUM_POST_SIZE = 25 * 1024 * 1024
"""
Maximum post size to logs analytics workspace is 30M bytes. 5M for buffer
"""

LOGS_FILE_SIZE = 512 * 1024 * 1024
"""
Maximum log export file size
"""

LOGS_COLLECTION_COUNT_FROM_SERVER = 20
"""
Maximum logs collection count returned from server
"""

LOGS_BACKOFF_FACTOR = 1
"""
Upload backoff factor
"""

LOGS_POST_RETRY_CAP = 16
"""
Retry cap is 16 times for log analytics post request
"""

WORKSPACE_ENV_KEYS = {
    "customer_id": "WORKSPACE_ID",
    "shared_key": "WORKSPACE_SHARED_KEY",
}
"""
Environment variables' name of workspace for log upload
"""


def generate_export_file_name(file_path, index):
    file_name_with_ext = os.path.basename(file_path)  # eds_report.csv
    dir_name = os.path.dirname(file_path)
    file_name = os.path.splitext(file_name_with_ext)[0]
    filename_suffix = os.path.splitext(file_name_with_ext)[1]
    base_filename = file_name + "-" + str(index)

    export_file_name = os.path.join(dir_name, base_filename + filename_suffix)
    return export_file_name


"""
def _write_logs(data_controller, logs, file_name, resource, timestamp):

    resource_uri = get_resource_uri(resource, data_controller)
    if resource_uri is not None:
        content = []
        for log in logs:
            result = _convert_to_logs_format(
                log,
                resource[INSTANCE_NAME],
                azure_constants.RESOURCE_TYPE_FOR_KIND[resource[KIND]],
                resource_uri,
            )
            content.append(result)

    write_file(file_name, content, ExportType.logs.value, timestamp)
"""


def logs_upload(logs, customer_id, shared_key):
    import base64
    import zlib

    for log in logs:
        unzip = str(
            zlib.decompress(base64.b64decode(log["logs"]), -zlib.MAX_WBITS),
            "utf-8",
        )

        _post_logs_to_logs_analytics(
            customer_id,
            shared_key,
            log["instance_name"],
            unzip,
            log["log_type"],
            log["instance_type"],
            log["resource_id"],
        )


def _convert_to_logs_format(logs, instance, instance_type, resource_uri):
    result = ""
    if logs and instance and instance_type:
        result = {
            "instance_name": instance,
            "instance_type": instance_type,
            "resource_uri": resource_uri,
            "logs": logs,
        }
    return result


# ##############################################################################
# Log workspace functions
# ##############################################################################


def _get_log_workspace_credentials_from_env(client):
    """
    Get the shared key and customer id for the given
    client's log workspace
    """
    customer_id = None
    shared_key = None
    get_workspace_from_env = True

    # First try to get workspace info from ENV
    for workspace_env in WORKSPACE_ENV_KEYS.values():
        if workspace_env not in os.environ or os.environ[workspace_env] is None:
            get_workspace_from_env = False
            break
    if get_workspace_from_env:
        customer_id = os.environ[WORKSPACE_ENV_KEYS["customer_id"]]
        shared_key = os.environ[WORKSPACE_ENV_KEYS["shared_key"]]
    else:
        # Prompt user to provide workspace info
        succeed = False
        while not succeed:
            display("Please provide Azure Log Analytics workspace information")
            customer_id = prompt("Workspace ID: ")
            shared_key = prompt("Primary Key: ")
            try:
                succeed = _test_log_workspace_key(customer_id, shared_key)
            except Exception as e:
                client.stderr(
                    'Can\'t upload to the workspace: "{} Exception: {}". '
                    "Please try again".format(customer_id, e)
                )
                display("\n")

        _store_log_workspace_credentials_in_env(customer_id, shared_key)
    return customer_id, shared_key


def _store_log_workspace_credentials_in_env(customer_id, shared_key):
    """
    Stores logs workspace credentials in environment
    :param customer_id: string
    :param shared_key: string
    """
    if customer_id and shared_key:
        os.environ[WORKSPACE_ENV_KEYS["customer_id"]] = customer_id
        os.environ[WORKSPACE_ENV_KEYS["shared_key"]] = shared_key
    else:
        raise ValueError(
            "Failed to store one or more of the following: {}".format(
                list(WORKSPACE_ENV_KEYS)
            )
        )


def _build_log_request_header(
    customer_id, shared_key, content_length, log_type, resource_uri
):
    rfc1123date = datetime.datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    method = "POST"
    content_type = "application/json"

    signature = _build_log_request_signature(
        customer_id,
        shared_key,
        rfc1123date,
        content_length,
        method,
        content_type,
        azure_constants.API_LOG,
    )
    headers = {
        "content-type": content_type,
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
        "x-ms-AzureResourceId": resource_uri,
    }
    return headers


def _build_log_request_uri(customer_id):
    return (
        "https://"
        + customer_id
        + ".ods.opinsights.azure.com"
        + azure_constants.API_LOG
        + "?api-version=2016-04-01"
    )


# Build the API signature
def _build_log_request_signature(
    customer_id,
    shared_key,
    date,
    content_length,
    method,
    content_type,
    resource,
):
    x_headers = "x-ms-date:" + date
    string_to_hash = (
        method
        + "\n"
        + str(content_length)
        + "\n"
        + content_type
        + "\n"
        + x_headers
        + "\n"
        + resource
    )
    bytes_to_hash = bytes(string_to_hash, "UTF-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    )
    encoded_hash = encoded_hash.decode("utf-8")
    authorization = "SharedKey {}:{}".format(customer_id, encoded_hash)
    return authorization


def _test_log_workspace_key(customer_id, shared_key):
    uri = _build_log_request_uri(customer_id)
    body = '[{"Property 1": "test1"}]'
    table_name = "test_workspace_logs"
    headers = _build_log_request_header(
        customer_id, shared_key, len(body), table_name, uri
    )
    succeed = False
    try:
        response = requests.post(uri, data=body, headers=headers)
        if 200 <= response.status_code <= 299:
            succeed = True
    finally:
        return succeed


def _post_logs_to_logs_analytics(
    customer_id,
    shared_key,
    instance_name,
    body,
    log_type,
    instance_type,
    resource_uri,
):
    uri = _build_log_request_uri(customer_id)
    headers = _build_log_request_header(
        customer_id, shared_key, len(body), log_type, resource_uri
    )

    response = _requests_retry_session().post(uri, data=body, headers=headers)
    if 200 <= response.status_code <= 299:
        display(
            '\tSuccessfully upload "{}" records for resource type "{}", '
            'instance: "{}\'s" log to table: "{}" '.format(
                len(json.loads(body)), instance_type, instance_name, log_type
            )
        )
    else:
        raise Exception(
            '\tFail to upload "{}" to table: "{}" with status code: "{}" and '
            'error msg: "{}"'.format(
                instance_name, log_type, response.status_code, response.text
            )
        )


# https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html
# Explains how retry works
def _requests_retry_session(
    retries=LOGS_POST_RETRY_CAP,
    backoff_factor=LOGS_BACKOFF_FACTOR,
    session=None,
):
    """
    Get a retry request session
    :arg:
      - retries: number of retries
      - backoff_factor: for exponential backoff
      - status_forcelist: server error code list
        Now retry on three cases based on the following doc:
        https://docs.microsoft.com/en-us/azure/azure-monitor/platform/
        data-collector-api#return-codes
      - session: https request retry session
    :return: retry session
    """
    session = session or requests.Session()
    max_retries = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(
            HTTPStatus.TOO_MANY_REQUESTS,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.SERVICE_UNAVAILABLE,
        ),
        allowed_methods=frozenset(["POST"]),
    )
    adapter = HTTPAdapter(max_retries=max_retries)
    session.mount("https://", adapter)
    return session


# ##############################################################################
# Export data JSON schema
# ##############################################################################


EXPORT_DATA_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "exportType": {"type": "string"},
        "dataTimestamp": {"type": "string"},
        "dataController": {
            "type": "object",
            "properties": {
                "instanceName": {"type": "string"},
                "subscriptionId": {"type": "string"},
                "resourceGroupName": {"type": "string"},
                "location": {"type": "string"},
                "publicKey": {"type": "string"},
                "k8sRaw": {"type": "object"},
            },
            "required": [
                "instanceName",
                "subscriptionId",
                "resourceGroupName",
                "location",
                "publicKey",
                "k8sRaw",
            ],
        },
        "deletedInstances": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "uid": {"type": "string"},
                    "instanceName": {"type": "string"},
                    "instanceNamespace": {"type": "string"},
                    "kind": {"type": "string"},
                },
                "required": [
                    "uid",
                    "instanceName",
                    "instanceNamespace",
                    "kind",
                ],
            },
        },
        "instances": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "instanceName": {"type": "string"},
                    "instanceNamespace": {"type": "string"},
                    "kind": {"type": "string"},
                    "creationTimestamp": {"type": "string"},
                    "k8sRaw": {"type": "object"},
                },
                "required": [
                    "instanceName",
                    "instanceNamespace",
                    "kind",
                    "creationTimestamp",
                    "k8sRaw",
                ],
            },
        },
        "data": {"type": "array"},
    },
    "required": [
        "exportType",
        "dataTimestamp",
        "dataController",
        "deletedInstances",
        "instances",
    ],
}

EXPORT_FILE_DICT_KEY = {"exportType", "data", "dataTimestamp"}
"""
Export file dictionary keys
"""

EXPORT_SANITIZERS = []
"""
Export file sanitizer rules.  
example: SanitizerRule(".*externalEndpoint")
"""


# #############################################################################
# Upload status functions
# #############################################################################

UPLOAD_STATUS_FILENAME = "upload-status.json"
"""
Upload status file name
"""


def get_export_timestamp_from_file(export_type):
    """
    :param export_type: export type
    Returns the specified value from the upload status file and schema_valid,
    which represents whether or not the file schema was valid when checked.
    """
    try:
        upload_status_file_path = _get_upload_status_file_path(
            UPLOAD_STATUS_FILENAME
        )
        with open(
            upload_status_file_path, encoding="utf-8"
        ) as upload_status_file:
            upload_status_json = json.load(upload_status_file)

            if upload_status_json:
                str_timestamp = upload_status_json.get(export_type).get(
                    "data_timestamp"
                )
                stamp = datetime.datetime.strptime(
                    str_timestamp, "%Y-%m-%d %H:%M:%S.%f"
                )
                log.debug("Export timestamp from file: %s", stamp)
                return stamp
                # return datetime.datetime.fromisoformat(str_timestamp)

    except BaseException as e:
        log.info(e)
        print(e)
        raise ValueError("Could not retrieve data from the upload status file.")


def get_export_timestamp(export_type):
    start_time_from_status_file = get_export_timestamp_from_file(export_type)

    default_start_time = datetime.datetime.utcnow() - datetime.timedelta(
        minutes=DEFAULT_QUERY_WINDOW[export_type]
    )

    # Choose later time as start time to avoid export and upload dup records
    if start_time_from_status_file > default_start_time:
        return start_time_from_status_file
    else:
        return default_start_time


def update_upload_status_file(export_type, data_timestamp):
    """
    Update the status file with data timestamp uploaded.
    :param data_timestamp: string
    """
    try:
        upload_status_file_path = _get_upload_status_file_path(
            UPLOAD_STATUS_FILENAME
        )
        with open(
            upload_status_file_path, "r+", encoding="utf-8"
        ) as upload_status_file:
            upload_status_json = json.load(upload_status_file)

            if data_timestamp:
                upload_status_json[export_type][
                    "data_timestamp"
                ] = data_timestamp
                upload_status_json[export_type][
                    "upload_timestamp"
                ] = datetime.datetime.utcnow().isoformat(
                    sep=" ", timespec="milliseconds"
                )

            upload_status_file.seek(0)
            json.dump(upload_status_json, upload_status_file, indent=4)
            upload_status_file.truncate
            print(
                "Update status file {0} data_timestamp to {1}".format(
                    export_type, data_timestamp
                )
            )

    except BaseException:
        raise ValueError("Upload status file was not able to be updated.")


def _get_upload_status_file_path(filename):
    """
    Returns the upload status file's path and schema_valid, which represents
    whether or not the input file was valid. If the input file did not follow
    the expected schema, then the file will be rewritten with default values.
    """
    from datetime import datetime, timedelta

    status_file = get_config_file_path(filename)
    status_file_exists = os.path.exists(status_file)
    schema_valid = False

    if status_file_exists:
        schema_valid = validate_upload_status_file(status_file)

    log.info(
        "Upload status file={0} status_file_exists={1}, schema_valid={2}".format(
            status_file, status_file_exists, schema_valid
        )
    )

    if not status_file_exists or not schema_valid:
        upload_timestamp = datetime.utcnow()

        new_upload_status_file_content = {
            "metrics": {
                "upload_timestamp": upload_timestamp.isoformat(
                    sep=" ", timespec="milliseconds"
                ),
                "data_timestamp": (
                    upload_timestamp
                    - timedelta(minutes=DEFAULT_METRIC_QUERY_WINDOW_IN_MINUTE)
                ).isoformat(sep=" ", timespec="milliseconds"),
            },
            "logs": {
                "upload_timestamp": upload_timestamp.isoformat(
                    sep=" ", timespec="milliseconds"
                ),
                "data_timestamp": (
                    upload_timestamp
                    - timedelta(minutes=DEFAULT_LOG_QUERY_WINDOW_IN_MINUTE)
                ).isoformat(sep=" ", timespec="milliseconds"),
            },
            "usage": {
                "upload_timestamp": upload_timestamp.isoformat(
                    sep=" ", timespec="milliseconds"
                ),
                "data_timestamp": (
                    upload_timestamp
                    - timedelta(minutes=DEFAULT_USAGE_QUERY_WINDOW_IN_MINUTE)
                ).isoformat(sep=" ", timespec="milliseconds"),
            },
        }

        with open(
            status_file, mode="w", encoding="utf-8"
        ) as new_upload_status_file:
            json.dump(
                new_upload_status_file_content, new_upload_status_file, indent=4
            )
            print("Upload status file: {0} is saved.".format(status_file))

    return status_file


def validate_upload_status_file(path):
    """
    :param path: string value path of the upload status file
    Returns whether or not the input upload status file follows the expected
    JSON schema.
    """
    try:
        with open(path, encoding="utf-8") as input_file:
            data = json.load(input_file)
            validate(data, UPLOAD_STATUS_FILE_SCHEMA)
        return True
    except Exception as e:
        print(e)
        return False


UPLOAD_STATUS_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "metrics": {
            "type": "object",
            "properties": {
                "upload_timestamp": {
                    "type": "string",
                    "maxLength": 23,
                    "minLength": 23,
                },
                "data_timestamp": {
                    "type": "string",
                    "maxLength": 23,
                    "minLength": 23,
                },
            },
            "required": ["upload_timestamp", "data_timestamp"],
        },
        "logs": {
            "type": "object",
            "properties": {
                "upload_timestamp": {
                    "type": "string",
                    "maxLength": 23,
                    "minLength": 23,
                },
                "data_timestamp": {
                    "type": "string",
                    "maxLength": 23,
                    "minLength": 23,
                },
            },
            "required": ["upload_timestamp", "data_timestamp"],
        },
        "usage": {
            "type": "object",
            "properties": {
                "upload_timestamp": {
                    "type": "string",
                    "maxLength": 23,
                    "minLength": 23,
                },
                "data_timestamp": {
                    "type": "string",
                    "maxLength": 23,
                    "minLength": 23,
                },
            },
            "required": ["upload_timestamp", "data_timestamp"],
        },
    },
    "required": ["metrics", "logs", "usage"],
}


def add_last_upload_flag(path):
    """
    Updates the usage file at path with a flag to indicate last usage upload
    :param path: string value path of the usage file
    Returns: None, modifies usage file at path
    """
    try:
        if not os.path.exists(path):
            log.info("Unable to find usage file '{}'.".format(path))
            return

        with open(path, encoding="utf-8") as usage_file:
            data = json.load(usage_file)

        data[LAST_USAGE_UPLOAD_FLAG] = 1

        with open(path, "w") as usage_file:
            json.dump(data, usage_file)
    except BaseException:
        log.info("Failed to add last usage flag.")


def format_sqlmi_tier_for_azure(tier):
    """
    Given a tier, return it in a format expected by Azure (e.g: translate
    'bc' to 'BusinessCritical')
    """

    if tier.lower() in (t.lower() for t in SQLMI_TIER_GENERAL_PURPOSE_ALL):
        return SQLMI_TIER_GENERAL_PURPOSE_AZURE

    if tier.lower() in (t.lower() for t in SQLMI_TIER_BUSINESS_CRITICAL_ALL):
        return SQLMI_TIER_BUSINESS_CRITICAL_AZURE

    return tier


def format_sqlmi_license_type_for_azure(license_type):
    """
    Given a license type, return it in a format expected by Azure (e.g:
    translate 'licenseincluded' to 'LicenseIncluded')
    """

    if license_type.lower() == SQLMI_LICENSE_TYPE_BASE_PRICE.lower():
        return SQLMI_LICENSE_TYPE_BASE_PRICE_AZURE

    if license_type.lower() == SQLMI_LICENSE_TYPE_LICENSE_INCLUDED.lower():
        return SQLMI_LICENSE_TYPE_LICENSE_INCLUDED_AZURE

    if license_type.lower() == SQLMI_LICENSE_TYPE_DISASTER_RECOVERY.lower():
        return SQLMI_LICENSE_TYPE_DISASTER_RECOVERY_AZURE

    return license_type


def set_azure_upload_status(data_controller, data_controller_azure):
    """
    Set azure upload status in data_controller
    ("ksRaw.status.azure.upload_status"). Copy it from the azure resource, if
    any. Otherwise set it empty.
    """

    create_azure_status_key_if_missing(data_controller)

    if data_controller_azure is None:
        return

    try:
        azure_status = data_controller_azure["properties"]["k8sRaw"]["status"][
            "azure"
        ]["uploadStatus"]
    except KeyError:
        return

    data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"] = azure_status


def update_azure_upload_status(
    client, data_controller, export_type, last_upload_time, ex
):
    """
    Update the "uploadStatus" on the Azure resource.
    :param client: The client used to create/update the Azure resource.
    :param data_controller: The data_controller from the export file.
    :param export_type: The export type (e.g "usage", "logs", "metrics").
    :param last_upload_time: If upload was successful (no exception), this
           will be the "lastUploadTime" in Azure.
    :param ex: The exception for the upload, if any.
    """

    msg = "Success"
    if ex is not None:
        msg = ex

    upload_status = {
        "lastUploadTime": last_upload_time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": str(msg),
    }

    create_azure_status_key_if_missing(data_controller)

    data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"][
        "{export_type}".format(export_type=export_type)
    ] = upload_status

    client.create_dc_azure_resource(data_controller)


def create_azure_status_key_if_missing(data_controller):
    """
    Create "k8sRaw.status.azure" keys if missing.
    """

    if "k8sRaw" not in data_controller:
        data_controller["k8sRaw"] = {}

    if "status" not in data_controller["k8sRaw"]:
        data_controller["k8sRaw"]["status"] = {}

    if "azure" not in data_controller["k8sRaw"]["status"]:
        data_controller["k8sRaw"]["status"]["azure"] = {}

    if "uploadStatus" not in data_controller["k8sRaw"]["status"]["azure"]:
        data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"] = {}

    # Default to the minimum date possible, and empty message/state
    default_upload_status = {
        "lastUploadTime": datetime.date.min.strftime("%Y-%m-%d %H:%M:%S"),
        "message": "",
    }

    if (
        "metrics"
        not in data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"]
    ):
        data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"][
            "metrics"
        ] = default_upload_status

    if (
        "usage"
        not in data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"]
    ):
        data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"][
            "usage"
        ] = default_upload_status

    if (
        "logs"
        not in data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"]
    ):
        data_controller["k8sRaw"]["status"]["azure"]["uploadStatus"][
            "logs"
        ] = default_upload_status


def check_prompt_export_output_file(file_path, force):
    """
    Checks if export output file exists, and prompt if necessary.
    """
    # Check if file exists
    export_file_exists = True
    overwritten = False

    while export_file_exists and not overwritten:
        export_file_exists = os.path.exists(file_path)
        if not force and export_file_exists:
            try:
                yes = prompt_y_n(
                    "{} exists already, do you want to overwrite it?".format(
                        file_path
                    )
                )
            except NoTTYException as e:
                raise NoTTYException(
                    "{} Please make sure the file does not exist in a"
                    " non-interactive environment".format(e)
                )

            overwritten = True if yes else False

            if overwritten:
                os.remove(file_path)
            else:
                file_path = prompt_for_input(
                    "Please provide a file name with the path: "
                )
                export_file_exists = True
                overwritten = False

        elif force:
            overwritten = True
            if export_file_exists:
                os.remove(file_path)

    return file_path
