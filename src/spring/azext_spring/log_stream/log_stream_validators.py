# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


def validate_all_instances_and_instance_are_mutually_exclusive(namespace):
    if namespace.all_instances is True and namespace.instance is not None:
        raise InvalidArgumentValueError("--all-instances cannot be set together with --instance/-i.")


def validate_log_limit(namespace):
    temp_limit = None
    try:
        temp_limit = namespace.limit
    except:
        raise InvalidArgumentValueError('--limit must contains only digit')
    if temp_limit < 1:
        raise InvalidArgumentValueError('--limit must be in the range [1,2048]')
    if temp_limit > 2048:
        temp_limit = 2048
        logger.error("--limit can not be more than 2048, using 2048 instead")
    namespace.limit = temp_limit * 1024


def validate_log_lines(namespace):
    temp_lines = None
    try:
        temp_lines = namespace.lines
    except:
        raise InvalidArgumentValueError('--lines must contains only digit')
    if temp_lines < 1:
        raise InvalidArgumentValueError('--lines must be in the range [1,10000]')
    if temp_lines > 10000:
        temp_lines = 10000
        logger.error("--lines can not be more than 10000, using 10000 instead")
    namespace.lines = temp_lines


def validate_log_since(namespace):
    if namespace.since:
        last = namespace.since[-1:]
        try:
            namespace.since = int(
                namespace.since[:-1]) if last in ("hms") else int(namespace.since)
        except:
            raise InvalidArgumentValueError("--since contains invalid characters")
        namespace.since *= 60 if last == "m" else 1
        namespace.since *= 3600 if last == "h" else 1
        if namespace.since > 3600:
            raise InvalidArgumentValueError("--since can not be more than 1h")


def validate_max_log_requests(namespace):
    if namespace.max_log_requests < 1:
        raise InvalidArgumentValueError("--max-log-requests should be larger than 0.")


def validate_thread_number(follow, thread_number, max_log_requests):
    if (follow is True and thread_number > max_log_requests):
        raise CLIError("You are attempting to follow {} log streams, but maximum allowed concurrency is {}, "
                       "use --max-log-requests to increase the limit".format(thread_number, max_log_requests))
