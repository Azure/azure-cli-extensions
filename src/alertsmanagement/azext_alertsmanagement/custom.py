# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
# pylint: disable=too-many-boolean-expressions

from knack.util import CLIError
from datetime import datetime
from .vendored_sdks.alertsmanagement.models import ActionType


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _transform_condition(condition, name_of_field):
    """
    ['Equals', 'Sev0', 'Sev2'] ->
    {
        "operator": "Equals",
        "values": [
            "Sev0",
            "Sev2"
        ]
    }
    :param condition: a list
    :return: a dict
    """
    if condition is None:
        return None
    if len(condition) < 2:
        raise CLIError('usage error: condition type should have at least two elements')
    return {
        'field': name_of_field,
        'operator': condition[0],
        'values': condition[1:]
    }


def _alert_rule_ids(subscription, resource_group, alert_ids):
    """
    Transform alert rule name or ID to alert rule ID
    :param subscription:
    :param resource_group:
    :param alert:
    :return: alert rule ID
    """
    if alert_ids is None:
        return None
    from msrestazure.tools import resource_id, is_valid_resource_id
    ids = []
    ids.append(alert_ids[0])
    for id in alert_ids[1:]:
        if not is_valid_resource_id(id):
            rid = resource_id(subscription=subscription, resource_group=resource_group,
                              namespace='microsoft.insights', type='alertrules', name=id)
            ids.append(rid)
        ids.append(id)

    return ids


def create_alertsmanagement_processing_rule(cmd, client,
                                            resource_group_name,
                                            processing_rule_name,
                                            rule_type,
                                            action_groups=None,
                                            description=None,
                                            scopes=None,
                                            enabled=None,
                                            tags=None,
                                            filter_severity=None,
                                            filter_monitor_service=None,
                                            filter_monitor_condition=None,
                                            filter_alert_rule_name=None,
                                            filter_alert_rule_id=None,
                                            filter_alert_rule_description=None,
                                            filter_alert_context=None,
                                            filter_signal_type=None,
                                            filter_target_resource=None,
                                            filter_resource_group=None,
                                            filter_resource_type=None,
                                            schedule_recurrence_type=None,
                                            schedule_start_datetime=None,
                                            schedule_end_datetime=None,
                                            schedule_recurrence_start_time=None,
                                            schedule_recurrence_end_time=None,
                                            schedule_recurrence=None,
                                            schedule_recurrence_2_type=None,
                                            schedule_recurrence_2_start_time=None,
                                            schedule_recurrence_2_end_time=None,
                                            schedule_recurrence_2=None,
                                            schedule_time_zone="UTC"):
    # body = {'location': location, 'tags': tags}
    body = {'location': 'Global'}
    properties = {}
    if rule_type == ActionType.REMOVE_ALL_ACTION_GROUPS:
        if action_groups is not None:
            print(bcolors.FAIL + 'Argument Conflict: --action-groups argument can\'t be used with RemoveAllActionGroups rule type' + bcolors.ENDC)
            return
        properties['actions'] = [
            {
                'actionType': rule_type
            }
        ]
    elif rule_type == ActionType.ADD_ACTION_GROUPS:
        if action_groups is None:
            print(bcolors.FAIL + 'Missing Argument: --action-groups must be used when using AddActionGroups' + bcolors.ENDC)
            return
        else:
            properties['actions'] = [
                {
                    'actionType': rule_type,
                    'actionGroupIds': [x.strip() for x in action_groups]
                }
            ]
    properties['enabled'] = enabled if enabled is not None else 'True'
    properties['scopes'] = [x.strip() for x in scopes]
    if description is not None:
        properties['description'] = description

    severity = _transform_condition(filter_severity, 'Severity')
    monitor_service = _transform_condition(filter_monitor_service, 'MonitorService')
    monitor_condition = _transform_condition(filter_monitor_condition, 'MonitorCondition')
    alert_rule_name = _transform_condition(filter_alert_rule_name, 'AlertRuleName')
    alert_rule_ids = None
    if filter_alert_rule_id is not None:
        alert_rule_ids = _alert_rule_ids(client._config.subscription_id, resource_group_name, filter_alert_rule_id)
        alert_rule_ids = _transform_condition(alert_rule_ids, 'AlertRuleId')
    alert_description = _transform_condition(filter_alert_rule_description, 'Description')
    alert_context = _transform_condition(filter_alert_context, 'AlertContext')
    signal_type = _transform_condition(filter_signal_type, 'SignalType')
    resource_filter = _transform_condition(filter_target_resource, 'TargetResource')
    resource_group_filter = _transform_condition(filter_resource_group, 'TargetResourceGroup')
    resource_type_filter = _transform_condition(filter_resource_type, 'TargetResourceType')

    # conditions
    if any([filter_severity, filter_monitor_service, filter_monitor_condition, filter_alert_rule_name,
            filter_alert_rule_id, filter_alert_rule_description, filter_alert_context, filter_signal_type,
            filter_target_resource, filter_resource_group, filter_resource_type]):
        properties['conditions'] = []

    if severity is not None:
        properties['conditions'].append(severity)
    if monitor_service is not None:
        properties['conditions'].append(monitor_service)
    if monitor_condition is not None:
        properties['conditions'].append(monitor_condition)
    if alert_rule_name is not None:
        properties['conditions'].append(alert_rule_name)
    if alert_rule_ids is not None:
        properties['conditions'].append(alert_rule_ids)
    if alert_description is not None:
        properties['conditions'].append(alert_description)
    if alert_context is not None:
        properties['conditions'].append(alert_context)
    if signal_type is not None:
        properties['conditions'].append(signal_type)
    if resource_filter is not None:
        properties['conditions'].append(resource_filter)
    if resource_group_filter is not None:
        properties['conditions'].append(resource_group_filter)
    if resource_type_filter is not None:
        properties['conditions'].append(resource_type_filter)

    # schedule
    if schedule_recurrence_type is not None or (schedule_start_datetime is not None or schedule_end_datetime is not None):
        properties['schedule'] = {}
        if schedule_start_datetime is not None:
            effective_from = schedule_start_datetime.replace(' ', 'T', 1)
            properties['schedule']['effectiveFrom'] = effective_from
        elif schedule_recurrence_type is not None:
            effective_from = datetime.strftime(datetime.now().date(), '%Y-%m-%d') + 'T00:00:00'
            print('effective_from: ' + effective_from)
            properties['schedule']['effectiveFrom'] = effective_from

        if schedule_end_datetime is not None:
            effective_until = schedule_end_datetime.replace(' ', 'T', 1)
            properties['schedule']['effectiveUntil'] = effective_until

        if schedule_time_zone is not None:
            properties['schedule']['timeZone'] = schedule_time_zone

        if schedule_recurrence_type == 'Daily':
            if schedule_recurrence is not None:
                print(bcolors.WARNING + 'WARNING: schedule-recurrence will be ignored as it can\'t be used while schedule-recurrence-type is set to Daily' + bcolors.ENDC)

            properties['schedule']['recurrences'] = [
                {
                    'recurrenceType': schedule_recurrence_type,
                    'startTime': schedule_recurrence_start_time,
                    'endTime': schedule_recurrence_end_time
                }
            ]
        elif schedule_recurrence_type in ['Weekly', 'Monthly']:
            type_of_days = 'daysOfWeek' if schedule_recurrence_type == 'Weekly' else 'daysOfMonth'
            properties['schedule']['recurrences'] = [
                {
                    'recurrenceType': schedule_recurrence_type,
                    'startTime': schedule_recurrence_start_time,
                    'endTime': schedule_recurrence_end_time,
                    type_of_days: schedule_recurrence
                }
            ]

        second_recurrence = None
        if any([schedule_recurrence_2_type, schedule_recurrence_2_start_time, schedule_recurrence_2_end_time, schedule_recurrence_2]) and \
                len(properties['schedule']['recurrences']) < 1:
            print(bcolors.FAIL + "second recurrence can't be used before using the first recurrence argument" + bcolors.ENDC)
            return

        if schedule_recurrence_2_type == 'Daily':
            if schedule_recurrence_2 is not None:
                print(bcolors.WARNING + 'WARNING: schedule-recurrence-2 will be ignored as it can\'t be used while schedule-recurrence-type-2 is set to Daily' + bcolors.ENDC)

            second_recurrence = {
                'recurrenceType': schedule_recurrence_2_type,
                'startTime': schedule_recurrence_2_start_time,
                'endTime': schedule_recurrence_2_end_time
            }
        elif schedule_recurrence_2_type in ['Weekly', 'Monthly']:
            type_of_days = 'daysOfWeek' if schedule_recurrence_2_type == 'Weekly' else 'daysOfMonth'
            second_recurrence = {
                'recurrenceType': schedule_recurrence_2_type,
                'startTime': schedule_recurrence_2_start_time,
                'endTime': schedule_recurrence_2_end_time,
                type_of_days: schedule_recurrence_2
            }

        if second_recurrence is not None:
            properties['schedule']['recurrences'].append(second_recurrence)

    body['properties'] = properties
    body['tags'] = tags

    return client.create_or_update(resource_group_name=resource_group_name, processing_rule_name=processing_rule_name,
                                   alert_processing_rule=body)


def update_alertsmanagement_processing_rule(instance, client,
                                            tags=None,
                                            enabled=None):
    if tags is not None:
        instance.tags = tags
    if enabled is not None:
        instance.properties.enabled = enabled
    return instance


def delete_alertsmanagement_processing_rule(cmd, client,
                                            resource_group_name,
                                            processing_rule_name):
    return client.delete(resource_group_name=resource_group_name, alert_processing_rule_name=processing_rule_name)


def get_alertsmanagement_processing_rule(cmd, client,
                                         resource_group_name,
                                         processing_rule_name):
    return client.get_by_name(resource_group_name=resource_group_name, processing_rule_name=processing_rule_name)


def list_alertsmanagement_processing_rule(cmd, client,
                                          resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()
