# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import base64
import socket
import os
import re
import isodate
from isodate import ISO8601Error

from azure.cli.core.commands.validators import \
    (validate_tags, get_default_location_from_resource_group)
from azure.cli.core.commands.template_create import get_folded_parameter_validator
from azure.cli.core.commands.client_factory import get_subscription_id, get_mgmt_service_client
from azure.cli.core.commands.validators import validate_parameter_set
from azure.cli.core.profiles import ResourceType

from knack.util import CLIError

# PARAMETER VALIDATORS

###### Queue Parameters

def _validate_maxSizeInMegabytes(namespace):
    if namespace.max_size_in_megabytes:
        if type(namespace.max_size_in_megabytes) == int:
            if namespace.max_size_in_megabytes not in [1024, 2048, 3072, 4096, 5120]:
                raise CLIError('--max-size-in-megabytes value error: {0} is not allowed,  allowed values are [1024, 2048, 3072, 4096, 5120]'.format(namespace.max_size_in_megabytes))
        else:
            raise CLIError('--max-size-in-megabytes Value Error: {} value is not in interger format'.format(namespace.max_size_in_megabytes))


def _validate_max_delivery_count(namespace):
    if namespace.max_delivery_count:
        if type(namespace.max_delivery_count) != int:
            raise CLIError('--max-delivery-count Value Error: {} value is not in interger format'.format(namespace.max_delivery_count))


### Type Boolean
def _validate_requiresDuplicateDetection(namespace):
    if namespace.requires_duplicate_detection:
        if type(namespace.requires_duplicate_detection) != bool:
            raise CLIError('--requires-duplicate-detection Value Error : {0} value is not in boolean format (True/False)'.format(namespace.requires_duplicate_detection))


def _validate_requires_session(namespace):
    if namespace.requires_session:
        if type(namespace.requires_session) != bool:
            raise CLIError('--requires-session Value Error : {0} value is not in boolean format (True/False)'.format(namespace.requires_session))


def _validate_dead_lettering_on_message_expiration(namespace):
    if namespace.dead_lettering_on_message_expiration:
        if type(namespace.dead_lettering_on_message_expiration) != bool:
            raise CLIError('--dead-lettering-on-message-expiration Type Error : {0} value is not in boolean format (True/False)'.format(namespace.dead_lettering_on_message_expiration))

def _validate_enable_partitioning(namespace):
    if namespace.enable_partitioning:
        if type(namespace.enable_partitioning) != bool:
            raise CLIError('--enable-partitioning Value Error : {0} value is not in boolean format (True/False)'.format(namespace.enable_partitioning))

def _validate_enable_express(namespace):
    if namespace.enable_express:
        if type(namespace.enable_express) != bool:
            raise CLIError('--enable-express Value Error : {0} value is not in boolean format (True/False)'.format(namespace.enable_express))


def _validate_support_ordering(namespace):
    if namespace.support_ordering:
        if type(namespace.support_ordering) != bool:
            raise CLIError('--support-ordering Value Error : {0} value is not in boolean format (True/False)'.format(namespace.support_ordering))

def _validate_enable_batched_operations(namespace):
    if namespace.enable_batched_operations:
        if type(namespace.enable_batched_operations) != bool:
            raise CLIError('--enable-batched-operations Value Error : {0} value is not in boolean format (True/False)'.format(namespace.enable_batched_operations))

def _validate_requires_session(namespace):
    if namespace.requires_session:
        if type(namespace.requires_session) != bool:
            raise CLIError('--requires-sessionValue Error : {0} value is not in boolean format (True/False)'.format(namespace.requires_session))

def _validate_dead_lettering_on_message_expiration(namespace):
    if namespace.dead_lettering_on_message_expiration:
        if type(namespace.dead_lettering_on_message_expiration) != bool:
            raise CLIError('--dead-lettering-on-message-expiration Value Error : {0} value is not in boolean format (True/False)'.format(namespace.dead_lettering_on_message_expiration))


### Type ISO 8061 duration

iso8601pattern = re.compile("^P(?!$)(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(?=\d)(\d+H)?(\d+M)?(\d+.)?(\d+S)?)?$")

def _validate_lock_duration(namespace):
    if namespace.lock_duration:
        if not iso8601pattern.match(namespace.lock_duration):
            raise CLIError('--lock-duration Value Error : {0} value is not in ISO 8601 timespan/duration format. e.g. PT10M for duration of 10 min'.format(namespace.lock_duration))

def _validate_default_message_time_to_live(namespace):
    if namespace.default_message_time_to_live:
        if not iso8601pattern.match(namespace.default_message_time_to_live):
            raise CLIError('--default-message-time-to-live Value Error : {0} value is not in ISO 8601 timespan/duration format. e.g. PT10M for duration of 10 min'.format(namespace.default_message_time_to_live))

def _validate_duplicate_detection_history_time_window(namespace):
    if namespace.duplicate_detection_history_time_window:
        if not iso8601pattern.match(namespace.duplicate_detection_history_time_window):
            raise CLIError('--duplicate-detection-history-time-window Value Error : {0} value is not in ISO 8601 timespan/duration format. e.g. PT10M for duration of 10 min'.format(namespace.duplicate_detection_history_time_window))

def _validate_auto_delete_on_idle(namespace):
    if namespace.auto_delete_on_idle:
        if not iso8601pattern.match(namespace.auto_delete_on_idle):
            raise CLIError('--auto-delete-on-idle Value Error : {0} value is not in ISO 8601 timespan/duration format. e.g. PT10M for duration of 10 min'.format(namespace.auto_delete_on_idle))





