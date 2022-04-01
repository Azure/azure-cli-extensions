# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime

from azure.cli.core.azclierror import ValidationError, InvalidArgumentValueError, RequiredArgumentMissingError


def validate_datetime_format(namespace):
    format = '%Y-%m-%d %H:%M:%S'
    if namespace.schedule_start_datetime:
        datetime.strptime(namespace.schedule_start_datetime, format)
    if namespace.schedule_end_datetime:
        datetime.strptime(namespace.schedule_end_datetime, format)
        if namespace.schedule_start_datetime:
            if namespace.schedule_end_datetime < namespace.schedule_start_datetime:
                raise ValidationError('Argument Error: end-date is before start-date')


def validate_time_format(namespace):
    format = '%H:%M:%S'
    if namespace.schedule_recurrence_start_time:
        datetime.strptime(namespace.schedule_recurrence_start_time, format)
    if namespace.schedule_recurrence_end_time:
        datetime.strptime(namespace.schedule_recurrence_end_time, format)


def validate_severity(namespace):
    if namespace.filter_severity:
        validate_only_equals_operator(namespace.filter_severity)
        for x in namespace.filter_severity[1:]:
            if x not in ['Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4']:
                raise InvalidArgumentValueError('Argument Error: filter-severity values have to be one of [Equals, NotEquals, Sev0, Sev1, Sev2, Sev3, Sev4]')


def validate_monitor_condition(namespace):
    if namespace.filter_monitor_condition:
        validate_only_equals_operator(namespace.filter_monitor_condition)
        for x in namespace.filter_monitor_condition[1:]:
            if x not in ['Fired', 'Resolved']:
                raise InvalidArgumentValueError('Argument Error: filter-monitor-condition values have to be one of [Equals, NotEquals, Fired, Resolved]')


def validate_signal_type(namespace):
    if namespace.filter_signal_type:
        validate_only_equals_operator(namespace.filter_signal_type)
        for x in namespace.filter_signal_type[1:]:
            if x not in ['Metric', 'Log', 'Unknown']:
                raise InvalidArgumentValueError('Argument Error: filter-signal-type values have to be one of [Equals, NotEquals, Metric, Log, Unknown]')


def validate_monitor_service(namespace):
    if namespace.filter_monitor_service:
        validate_only_equals_operator(namespace.filter_monitor_service)


def validate_alert_rule_name(namespace):
    if namespace.filter_alert_rule_name:
        validate_full_operator(namespace.filter_alert_rule_name)


def validate_alert_rule_id(namespace):
    if namespace.filter_alert_rule_id:
        validate_full_operator(namespace.filter_alert_rule_id)


def validate_alert_rule_description(namespace):
    if namespace.filter_alert_rule_description:
        validate_full_operator(namespace.filter_alert_rule_description)


def validate_alert_context(namespace):
    if namespace.filter_alert_context:
        validate_full_operator(namespace.filter_alert_context)


def validate_target_resource(namespace):
    if namespace.filter_target_resource:
        validate_full_operator(namespace.filter_target_resource)


def validate_resource_group(namespace):
    if namespace.filter_resource_group:
        validate_full_operator(namespace.filter_resource_group)


def validate_resource_type(namespace):
    if namespace.filter_resource_type:
        validate_full_operator(namespace.filter_resource_type)


def validate_full_operator(args):
    if len(args) < 2:
        raise RequiredArgumentMissingError('Filter Argument Error: values length can\'t be smaller than 2')
    if args[0].lower() not in ['equals', 'notequals', 'contains', 'doesnotcontain']:
        raise InvalidArgumentValueError('Filter Argument Error: operator must be one of the follows: Equals, NotEquals, Contains, DoesNotContain')


def validate_only_equals_operator(args):
    if len(args) < 2:
        raise RequiredArgumentMissingError('Filter Argument Error: values length can\'t be smaller than 2')
    if args[0].lower() not in ['equals', 'notequals']:
        raise InvalidArgumentValueError('Filter Argument Error: operator must be one of the follows: Equals, NotEquals')
