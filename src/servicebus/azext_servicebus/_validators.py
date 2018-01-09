# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from knack.util import CLIError

# PARAMETER VALIDATORS
# Type ISO 8061 duration

iso8601pattern = re.compile("^P(?!$)(\\d+Y)?(\\d+M)?(\\d+W)?(\\d+D)?(T(?=\\d)(\\d+H)?(\\d+M)?(\\d+.)?(\\d+S)?)?$")


def _validate_lock_duration(namespace):
    if namespace.lock_duration and not iso8601pattern.match(namespace.lock_duration):
        raise CLIError('--lock-duration Value Error : {0} value is not in ISO 8601 timespan/duration format. e.g.'
                       ' PT10M for duration of 10 min'.format(namespace.lock_duration))


def _validate_default_message_time_to_live(namespace):
    if namespace.default_message_time_to_live and not iso8601pattern.match(namespace.default_message_time_to_live):
        raise CLIError('--default-message-time-to-live Value Error : {0} value is not in ISO 8601 timespan/duration'
                       ' format. e.g. PT10M for duration of 10 min'.format(namespace.default_message_time_to_live))


def _validate_duplicate_detection_history_time_window(namespace):
    if namespace.duplicate_detection_history_time_window and not \
            iso8601pattern.match(namespace.duplicate_detection_history_time_window):
        raise CLIError('--duplicate-detection-history-time-window Value Error : {0} value is not in ISO 8601 '
                       'timespan/duration format. e.g. PT10M for duration of 10 min'
                       .format(namespace.duplicate_detection_history_time_window))


def _validate_auto_delete_on_idle(namespace):
    if namespace.auto_delete_on_idle and not iso8601pattern.match(namespace.auto_delete_on_idle):
        raise CLIError('--auto-delete-on-idle Value Error : {0} value is not in ISO 8601 timespan/duration format.'
                       ' e.g. PT10M for duration of 10 min'.format(namespace.auto_delete_on_idle))
