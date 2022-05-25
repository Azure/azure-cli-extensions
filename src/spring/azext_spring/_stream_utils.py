# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order

import time
import colorama   # pylint: disable=import-error
from io import BytesIO
from random import uniform
from knack.util import CLIError
from knack.log import get_logger
from msrestazure.azure_exceptions import CloudError
from azure.multiapi.storage.v2018_11_09.blob import AppendBlobService
from azure.common import AzureHttpError
from ._utils import get_blob_info

logger = get_logger(__name__)

DEFAULT_CHUNK_SIZE = 1024 * 4
DEFAULT_LOG_TIMEOUT_IN_SEC = 60 * 30  # 30 minutes


def stream_logs(client,
                resource_group,
                service,
                app,
                deployment,
                no_format=False,
                raise_error_on_failure=True,
                logger_level_func=logger.warning):
    log_file_sas = None
    error_msg = "Could not get logs for Service: {}".format(service)

    try:
        log_file_sas = client.get_log_file_url(
            resource_group_name=resource_group,
            service_name=service,
            app_name=app,
            deployment_name=deployment).url
    except (AttributeError, CloudError) as e:
        logger.warning("%s Exception: %s", error_msg, e)
        raise CLIError(error_msg)

    if not log_file_sas:
        logger.warning("%s Empty SAS URL.", error_msg)
        raise CLIError(error_msg)

    account_name, endpoint_suffix, container_name, blob_name, sas_token = get_blob_info(
        log_file_sas)

    _stream_logs(no_format,
                 DEFAULT_CHUNK_SIZE,
                 DEFAULT_LOG_TIMEOUT_IN_SEC,
                 AppendBlobService(
                     account_name=account_name,
                     sas_token=sas_token,
                     endpoint_suffix=endpoint_suffix),
                 container_name,
                 blob_name,
                 raise_error_on_failure,
                 logger_level_func)


def _stream_logs(no_format,  # pylint: disable=too-many-locals, too-many-statements, too-many-branches
                 byte_size,
                 timeout_in_seconds,
                 blob_service,
                 container_name,
                 blob_name,
                 raise_error_on_failure,
                 logger_level_func):

    if not no_format:
        colorama.init()

    stream = BytesIO()
    metadata = {}
    start = 0
    end = byte_size - 1
    available = 0
    sleep_time = 1
    max_sleep_time = 15
    num_fails = 0
    num_fails_for_backoff = 3
    consecutive_sleep_in_sec = 0

    blob_exists = False

    def safe_get_blob_properties():
        '''
        In recent storage SDK, the get_blob_properties will output error logs on BlobNotFound (and also raise
        AzureHttpError(404)). There is no way to suppress the error logging from the callsite.
        However, in our scenario, such BlobNotFound error is expected before the build actually kicks off.
        To get rid of the error logging, we only call the get_blob_properties after the blob is created.
        '''
        nonlocal blob_exists
        if not blob_exists:
            blob_exists = blob_service.exists(
                container_name=container_name, blob_name=blob_name)
        if blob_exists:
            return blob_service.get_blob_properties(
                container_name=container_name, blob_name=blob_name)
        return None

    # Try to get the initial properties so there's no waiting.
    # If the storage call fails, we'll just sleep and try again after.
    try:
        props = safe_get_blob_properties()
        if props:
            metadata = props.metadata
            available = props.properties.content_length
    except (AttributeError, AzureHttpError):
        pass

    while (_blob_is_not_complete(metadata) or start < available):
        while start < available:
            # Success! Reset our polling backoff.
            sleep_time = 1
            num_fails = 0
            consecutive_sleep_in_sec = 0

            try:
                old_byte_size = len(stream.getvalue())
                blob_service.get_blob_to_stream(
                    container_name=container_name,
                    blob_name=blob_name,
                    start_range=start,
                    end_range=end,
                    stream=stream)

                curr_bytes = stream.getvalue()
                new_byte_size = len(curr_bytes)
                amount_read = new_byte_size - old_byte_size
                start += amount_read
                end = start + byte_size - 1

                # Only scan what's newly read. If nothing is read, default to 0.
                min_scan_range = max(new_byte_size - amount_read - 1, 0)
                for i in range(new_byte_size - 1, min_scan_range, -1):
                    if curr_bytes[i - 1:i + 1] == b'\r\n':
                        flush = curr_bytes[:i]  # won't logger.warning \n
                        stream = BytesIO()
                        stream.write(curr_bytes[i + 1:])
                        logger_level_func(flush.decode('utf-8', errors='ignore'))
                        break
                    if curr_bytes[i:i + 1] == b'\n':
                        flush = curr_bytes[:i + 1]  # won't logger.warning \n
                        stream = BytesIO()
                        stream.write(curr_bytes[i + 1:])
                        logger_level_func(flush.decode('utf-8', errors='ignore'))
                        break

            except AzureHttpError as ae:
                if ae.status_code != 404:
                    raise CLIError(ae)
            except KeyboardInterrupt:
                curr_bytes = stream.getvalue()
                if curr_bytes:
                    logger_level_func(curr_bytes.decode('utf-8', errors='ignore'))
                return

        try:
            props = safe_get_blob_properties()
            if props:
                metadata = props.metadata
                available = props.properties.content_length
        except AzureHttpError as ae:
            if ae.status_code != 404:
                raise CLIError(ae)
        except KeyboardInterrupt:
            if curr_bytes:
                logger_level_func(curr_bytes.decode('utf-8', errors='ignore'))
            return
        except Exception as err:
            raise CLIError(err)

        if consecutive_sleep_in_sec > timeout_in_seconds:
            # Flush anything remaining in the buffer - this would be the case
            # if the file has expired and we weren't able to detect any \r\n
            curr_bytes = stream.getvalue()
            if curr_bytes:
                logger_level_func(curr_bytes.decode('utf-8', errors='ignore'))

            return

        # If no new data available but not complete, sleep before trying to process additional data.
        if (_blob_is_not_complete(metadata) and start >= available):
            num_fails += 1

            if num_fails >= num_fails_for_backoff:
                num_fails = 0
                sleep_time = min(sleep_time * 2, max_sleep_time)

            rnd = uniform(1, 2)  # 1.0 <= x < 2.0
            total_sleep_time = sleep_time + rnd
            consecutive_sleep_in_sec += total_sleep_time
            time.sleep(total_sleep_time)

    # One final check to see if there's anything in the buffer to flush
    # E.g., metadata has been set and start == available, but the log file
    # didn't end in \r\n, so we were unable to flush out the final contents.
    curr_bytes = stream.getvalue()

    if curr_bytes:
        logger_level_func(curr_bytes.decode('utf-8', errors='ignore'))

    build_status = _get_run_status(metadata).lower()
    logger_level_func("Log status was: {}".format(build_status))

    if raise_error_on_failure:
        if build_status in ('internalerror', 'failed'):
            raise CLIError("Run failed")
        if build_status == 'timedout':
            raise CLIError("Run timed out")
        if build_status == 'canceled':
            raise CLIError("Run was canceled")


def _blob_is_not_complete(metadata):
    if not metadata:
        return True
    for key in metadata:
        if key.lower() == '__complete_status':
            return False
    return True


def _get_run_status(metadata):
    if metadata is None:
        return 'inprogress'
    for key in metadata:
        if key.lower() == '__complete_status':
            return metadata[key]
    return 'inprogress'
