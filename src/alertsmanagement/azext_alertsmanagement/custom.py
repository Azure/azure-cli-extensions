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


def _transform_condition(condition):
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
        'operator': condition[0],
        'values': condition[1:]
    }


def _alert_rule_id(subscription, resource_group, alert):
    """
    Transform alert rule name or ID to alert rule ID
    :param subscription:
    :param resource_group:
    :param alert:
    :return: alert rule ID
    """
    if alert is None:
        return None
    from msrestazure.tools import resource_id, is_valid_resource_id
    if not is_valid_resource_id(alert):
        return resource_id(subscription=subscription, resource_group=resource_group,
                           namespace='microsoft.insights', type='alertrules', name=alert)
    return alert


def create_alertsmanagement_processing_rule(cmd, client,
                                        resource_group_name,
                                        processing_rule_name,
                                        rule_type,
                                        description=None,
                                        scopes=None,
                                        alert_rule=None,
                                        alert_description=None,
                                        alert_context=None,
                                        signal_type=None,
                                        tags=None,
                                        enabled=None,
                                        severity=None,
                                        monitor_service=None,
                                        monitor_condition=None,
                                        resource_filter=None,
                                        resource_group_filter=None,
                                        resource_type_filter=None,
                                        schedule_recurrence_type='Always',
                                        schedule_start_date=None,
                                        schedule_end_date=None,
                                        schedule_start_time='00:00:00',
                                        schedule_end_time='00:00:00',
                                        schedule_recurrence=None,
                                        schedule_time_zone="UTC"):
    # body = {'location': location, 'tags': tags}
    body = {
        'location': 'Global'
        }
    properties = {}
    properties['actions'] = [
        #TODO currently support only one, need to support a list
        {
            'actionType': rule_type
        }
    ]
    properties['enabled'] = enabled if enabled is not None else 'True'
    properties['scopes'] = scopes.split()
    if description is not None:
        properties['description'] = description
        
    alert_context = _transform_condition(alert_context)
    alert_rule = _alert_rule_id(client._config.subscription_id, resource_group_name, alert_rule)
    alert_rule = _transform_condition(alert_rule)
    monitor_condition = _transform_condition(monitor_condition)
    monitor_service = _transform_condition(monitor_service)
    resource_filter = _transform_condition(resource_filter)
    resource_type_filter = _transform_condition(resource_type_filter)
    resource_group_filter = _transform_condition(resource_group_filter)
    severity = _transform_condition(severity)
    signal_type = _transform_condition(signal_type)
    alert_description = _transform_condition(alert_description)
    
    # conditions
    if any ([alert_context, alert_rule, monitor_condition, monitor_service, resource_filter,\
        resource_type_filter, resource_group_filter, severity, signal_type, alert_description]):
        properties['conditions'] = []    
    
    if alert_context is not None:
        properties['conditions']['AlertContext'] = alert_context
    if alert_rule is not None:
        properties['conditions']['AlertRuleId'] = alert_rule
    if monitor_condition is not None:
        properties['conditions']['MonitorCondition'] = monitor_condition
    if monitor_service is not None:
        properties['conditions']['MonitorService'] = monitor_service
    if resource_filter is not None:
        properties['conditions']['TargetResource'] = resource_filter
    if resource_type_filter is not None:
        properties['conditions']['TargetResourceType'] = resource_type_filter
    if resource_group_filter is not None:
        properties['conditions']['TargetResourceGroup'] = resource_group_filter
    if severity is not None:
        properties['conditions']['Severity'] = severity
    if signal_type is not None:
        properties['conditions']['SignalType'] = signal_type
    if alert_description is not None:
        properties['conditions']['Description'] = alert_description

    # schedule
    if schedule_recurrence_type in ['Always'] and schedule_start_date is not None:
        print('\033[93m' + 'Schedule start date will be ignored as the recurrence type is set to Always' + '\033[0m')
    if schedule_recurrence_type not in ['Always']:
        if schedule_start_date is not None:
            schedule_start_date = datetime.datetime.strptime(schedule_start_date, '%M/%d/%Y').strftime('%Y-%M-%d')
            effective_from = schedule_start_date + 'T' + schedule_start_time

        if schedule_end_date is not None:
            schedule_end_date = datetime.datetime.strptime(schedule_end_date, '%M/%d/%Y').strftime('%Y-%M-%d')
            effective_until = schedule_start_date + 'T' + schedule_start_time

        properties['schedule'] = {
            'effectiveFrom': effective_from,
            'timeZone' : schedule_time_zone
        }
        
        if (schedule_end_date is not None) and (schedule_end_time is not None):
                properties['schedule']['effectiveUntil'] = effective_until
        
        if schedule_recurrence_type == 'Daily':
            properties['recurrences'] = [
                {
                    'recurrenceType': schedule_recurrence_type,
                    'startTime': schedule_start_time,
                    'endTime' : schedule_end_time
                }
            ]
        elif schedule_recurrence_type in ['Weekly', 'Monthly']:
            #TODO currently support only one recurrence but need to support multiple recurrence
            type_of_days = 'daysOfWeek' if schedule_recurrence_type == 'Weekly' else 'daysOfMonth'
            properties['recurrences'] = [
                {
                    properties[type_of_days]: [
                        schedule_recurrence
                    ]
                }
            ]

    body['properties'] = properties

    return client.create_or_update(resource_group_name=resource_group_name, alert_processing_rule_name=processing_rule_name,
                                alert_processing_rule=body)


def update_alertsmanagement_action_rule(instance, client,
                                        location=None,
                                        tags=None,
                                        status=None):
    if location is not None:
        instance.location = location
    if tags is not None:
        instance.tags = tags
    if status is not None:
        instance.properties.status = status
    return instance


def delete_alertsmanagement_action_rule(cmd, client,
                                        resource_group_name,
                                        action_rule_name):
    return client.delete(resource_group_name=resource_group_name, action_rule_name=action_rule_name)


def get_alertsmanagement_processing_rule(cmd, client,
                                     resource_group_name,
                                     processing_rule_name):
    return client.get_by_name(resource_group_name=resource_group_name, alert_processing_rule_name=processing_rule_name)


def list_alertsmanagement_processing_rule(cmd, client,
                                      resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()
