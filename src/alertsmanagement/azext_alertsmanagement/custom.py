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


def create_alertsmanagement_action_rule(cmd, client,
                                        resource_group_name,
                                        action_rule_name,
                                        rule_type,
                                        location=None,
                                        description=None,
                                        scope_type=None,
                                        scope=None,
                                        severity=None,
                                        monitor_service=None,
                                        monitor_condition=None,
                                        target_resource_type=None,
                                        alert_rule=None,
                                        alert_description=None,
                                        alert_context=None,
                                        tags=None,
                                        status=None,
                                        suppression_recurrence_type=None,
                                        suppression_start_date=None,
                                        suppression_end_date=None,
                                        suppression_start_time=None,
                                        suppression_end_time=None,
                                        suppression_recurrence=None):
    body = {'location': location, 'tags': tags}

    properties = {}
    if status is not None:
        properties['status'] = status
    properties['type'] = rule_type
    if description is not None:
        properties['description'] = description
    if scope is not None and scope_type is not None:
        properties['scope'] = {
            'scopeType': scope_type,
            'values': scope
        }
    severity = _transform_condition(severity)
    monitor_service = _transform_condition(monitor_service)
    monitor_condition = _transform_condition(monitor_condition)
    target_resource_type = _transform_condition(target_resource_type)
    alert_rule = _alert_rule_id(client.config.subscription_id, resource_group_name, alert_rule)
    alert_rule = _transform_condition(alert_rule)
    alert_description = _transform_condition(alert_description)
    alert_context = _transform_condition(alert_context)
    properties['conditions'] = {}
    if severity is not None:
        properties['conditions']['severity'] = severity
    if monitor_service is not None:
        properties['conditions']['monitorService'] = monitor_service
    if monitor_condition is not None:
        properties['conditions']['monitorCondition'] = monitor_condition
    if target_resource_type is not None:
        properties['conditions']['targetResourceType'] = target_resource_type
    if alert_rule is not None:
        properties['conditions']['alertRuleId'] = alert_rule
    if alert_description is not None:
        properties['conditions']['description'] = alert_description
    if alert_context is not None:
        properties['conditions']['alertContext'] = alert_context
    properties['suppressionConfig'] = {
        'recurrenceType': suppression_recurrence_type
    }
    if suppression_recurrence_type not in ['Always', 'Once']:
        properties['suppressionConfig']['schedule'] = {
            'startDate': suppression_start_date,
            'endDate': suppression_end_date,
            'startTime': suppression_start_time,
            'endTime': suppression_end_time,
            'recurrenceValues': suppression_recurrence
        }

    body['properties'] = properties

    return client.create_update(resource_group_name=resource_group_name, action_rule_name=action_rule_name,
                                action_rule=body)


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


def get_alertsmanagement_action_rule(cmd, client,
                                     resource_group_name,
                                     action_rule_name):
    return client.get_by_name(resource_group_name=resource_group_name, action_rule_name=action_rule_name)


def list_alertsmanagement_action_rule(cmd, client,
                                      resource_group_name=None,
                                      target_resource_group=None,
                                      target_resource_type=None,
                                      target_resource=None,
                                      severity=None,
                                      monitor_service=None,
                                      impacted_scope=None,
                                      description=None,
                                      alert_rule_id=None,
                                      action_group=None,
                                      name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(
            resource_group_name=resource_group_name,
            target_resource_group=target_resource_group,
            target_resource_type=target_resource_type,
            target_resource=target_resource,
            severity=severity,
            monitor_service=monitor_service,
            impacted_scope=impacted_scope,
            description=description,
            alert_rule_id=alert_rule_id,
            action_group=action_group,
            name=name)
    return client.list_by_subscription(
        target_resource_group=target_resource_group,
        target_resource_type=target_resource_type,
        target_resource=target_resource,
        severity=severity,
        monitor_service=monitor_service,
        impacted_scope=impacted_scope,
        description=description,
        alert_rule_id=alert_rule_id,
        action_group=action_group,
        name=name)
