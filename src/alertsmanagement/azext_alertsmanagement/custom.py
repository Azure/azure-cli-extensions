# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
import json

from knack.util import CLIError


def list_alertsmanagement_operation(cmd, client):
    return client.list()


def change_state_alertsmanagement_alert(cmd, client,
                                        alert_id,
                                        new_state=None):
    return client.change_state(alert_id=alert_id, new_state=new_state)


def meta_data_alertsmanagement_alert(cmd, client,
                                     identifier=None):
    return client.meta_data(identifier=identifier)


def get_all_alertsmanagement_alert(cmd, client,
                                   target_resource=None,
                                   target_resource_type=None,
                                   target_resource_group=None,
                                   monitor_service=None,
                                   monitor_condition=None,
                                   severity=None,
                                   alert_state=None,
                                   alert_rule=None,
                                   smart_group_id=None,
                                   include_context=None,
                                   include_egress_config=None,
                                   page_count=None,
                                   sort_by=None,
                                   sort_order=None,
                                   select=None,
                                   time_range=None,
                                   custom_time_range=None):
    return client.get_all(target_resource=target_resource, target_resource_type=target_resource_type, target_resource_group=target_resource_group, monitor_service=monitor_service, monitor_condition=monitor_condition, severity=severity, alert_state=alert_state, alert_rule=alert_rule, smart_group_id=smart_group_id, include_context=include_context, include_egress_config=include_egress_config, page_count=page_count, sort_by=sort_by, sort_order=sort_order, select=select, time_range=time_range, custom_time_range=custom_time_range)


def get_by_id_alertsmanagement_alert(cmd, client,
                                     alert_id):
    return client.get_by_id(alert_id=alert_id)


def get_history_alertsmanagement_alert(cmd, client,
                                       alert_id):
    return client.get_history(alert_id=alert_id)


def get_summary_alertsmanagement_alert(cmd, client,
                                       groupby,
                                       include_smart_groups_count=None,
                                       target_resource=None,
                                       target_resource_type=None,
                                       target_resource_group=None,
                                       monitor_service=None,
                                       monitor_condition=None,
                                       severity=None,
                                       alert_state=None,
                                       alert_rule=None,
                                       time_range=None,
                                       custom_time_range=None):
    return client.get_summary(groupby=groupby, include_smart_groups_count=include_smart_groups_count, target_resource=target_resource, target_resource_type=target_resource_type, target_resource_group=target_resource_group, monitor_service=monitor_service, monitor_condition=monitor_condition, severity=severity, alert_state=alert_state, alert_rule=alert_rule, time_range=time_range, custom_time_range=custom_time_range)


def change_state_alertsmanagement_smart_group(cmd, client,
                                              smart_group_id,
                                              new_state=None):
    return client.change_state(smart_group_id=smart_group_id, new_state=new_state)


def get_all_alertsmanagement_smart_group(cmd, client,
                                         target_resource=None,
                                         target_resource_group=None,
                                         target_resource_type=None,
                                         monitor_service=None,
                                         monitor_condition=None,
                                         severity=None,
                                         smart_group_state=None,
                                         time_range=None,
                                         page_count=None,
                                         sort_by=None,
                                         sort_order=None):
    return client.get_all(target_resource=target_resource, target_resource_group=target_resource_group, target_resource_type=target_resource_type, monitor_service=monitor_service, monitor_condition=monitor_condition, severity=severity, smart_group_state=smart_group_state, time_range=time_range, page_count=page_count, sort_by=sort_by, sort_order=sort_order)


def get_by_id_alertsmanagement_smart_group(cmd, client,
                                           smart_group_id):
    return client.get_by_id(smart_group_id=smart_group_id)


def get_history_alertsmanagement_smart_group(cmd, client,
                                             smart_group_id):
    return client.get_history(smart_group_id=smart_group_id)


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


def create_alertsmanagement_action_rule(cmd, client,
                                        resource_group,
                                        name,
                                        location,
                                        type,
                                        description=None,
                                        scope_type=None,
                                        scope=None,
                                        severity=None,
                                        monitor_service=None,
                                        monitor_condition=None,
                                        target_resource_type=None,
                                        alert_rule_id=None,
                                        alert_description=None,
                                        alert_context=None,
                                        tags=None,
                                        status=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # unknown-primary[object]
    body['status'] = status  # str
    body['type'] = type
    body['description'] = description
    body['scope'] = {
        'scopeType': scope_type,
        'values': scope
    }
    severity = _transform_condition(severity)
    monitor_service = _transform_condition(monitor_service)
    monitor_condition = _transform_condition(monitor_condition)
    target_resource_type = _transform_condition(target_resource_type)
    alert_rule_id = _transform_condition(alert_rule_id)
    alert_description = _transform_condition(alert_description)
    alert_context = _transform_condition(alert_context)
    body['conditions'] = {}
    if severity is not None:
        body['conditions']['severity'] = severity
    if severity is not None:
        body['conditions']['monitorService'] = monitor_service
    if severity is not None:
        body['conditions']['monitorCondition'] = monitor_condition
    if severity is not None:
        body['conditions']['targetResourceType'] = target_resource_type
    if severity is not None:
        body['conditions']['alertRuleId'] = alert_rule_id
    if severity is not None:
        body['conditions']['description'] = alert_description
    if severity is not None:
        body['conditions']['alertContext'] = alert_context
    return client.create_update(resource_group_name=resource_group, action_rule_name=name, action_rule=body)


def update_alertsmanagement_action_rule(cmd, client,
                                        resource_group,
                                        name,
                                        location=None,
                                        tags=None,
                                        status=None):
    body = {}
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # unknown-primary[object]
    if status is not None:
        body['status'] = status  # str
    return client.create_update(resource_group_name=resource_group, action_rule_name=name, action_rule=body)


def delete_alertsmanagement_action_rule(cmd, client,
                                        resource_group,
                                        name):
    return client.delete(resource_group_name=resource_group, action_rule_name=name)


def get_alertsmanagement_action_rule(cmd, client,
                                     resource_group,
                                     name):
    return client.get_by_name(resource_group_name=resource_group, action_rule_name=name)


def list_alertsmanagement_action_rule(cmd, client,
                                      resource_group=None,
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
    if resource_group is not None and target_resource_group is not None and target_resource_type is not None and target_resource is not None and severity is not None and monitor_service is not None and impacted_scope is not None and description is not None and alert_rule_id is not None and action_group is not None and name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group, target_resource_group=target_resource_group, target_resource_type=target_resource_type, target_resource=target_resource, severity=severity, monitor_service=monitor_service, impacted_scope=impacted_scope, description=description, alert_rule_id=alert_rule_id, action_group=action_group, name=name)
    return client.list_by_subscription(target_resource_group=target_resource_group, target_resource_type=target_resource_type, target_resource=target_resource, severity=severity, monitor_service=monitor_service, impacted_scope=impacted_scope, description=description, alert_rule_id=alert_rule_id, action_group=action_group, name=name)


def create_alertsmanagement_smart_detector_alert_rule(cmd, client,
                                                      resource_group,
                                                      name,
                                                      location=None,
                                                      tags=None,
                                                      description=None,
                                                      state=None,
                                                      severity=None,
                                                      frequency=None,
                                                      action_groups=None,
                                                      throttling=None,
                                                      detector=None,
                                                      scope=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # unknown-primary[object]
    body['description'] = description  # str
    body['state'] = state  # str
    body['severity'] = severity  # str
    body['frequency'] = frequency  # unknown-primary[timeSpan]
    # body['action_groups'] = json.loads(action_groups) if isinstance(action_groups, str) else action_groups
    body['action_groups'] = {'groupIds': action_groups}
    body['throttling'] = json.loads(throttling) if isinstance(throttling, str) else throttling
    body['detector'] = {'id': detector}
    body['scope'] = scope
    return client.create_or_update(resource_group_name=resource_group, alert_rule_name=name, parameters=body)


def update_alertsmanagement_smart_detector_alert_rule(cmd, client,
                                                      resource_group,
                                                      name,
                                                      location=None,
                                                      tags=None,
                                                      description=None,
                                                      state=None,
                                                      severity=None,
                                                      frequency=None,
                                                      action_groups=None,
                                                      throttling=None):
    body = {}
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # unknown-primary[object]
    if description is not None:
        body['description'] = description  # str
    if state is not None:
        body['state'] = state  # str
    if severity is not None:
        body['severity'] = severity  # str
    if frequency is not None:
        body['frequency'] = frequency  # unknown-primary[timeSpan]
    if action_groups is not None:
        body['action_groups'] = json.loads(action_groups) if isinstance(action_groups, str) else action_groups
    if throttling is not None:
        body['throttling'] = json.loads(throttling) if isinstance(throttling, str) else throttling
    return client.create_or_update(resource_group_name=resource_group, alert_rule_name=name, parameters=body)


def delete_alertsmanagement_smart_detector_alert_rule(cmd, client,
                                                      resource_group,
                                                      name):
    return client.delete(resource_group_name=resource_group, alert_rule_name=name)


def get_alertsmanagement_smart_detector_alert_rule(cmd, client,
                                                   resource_group,
                                                   name,
                                                   expand_detector=None):
    return client.get(resource_group_name=resource_group, alert_rule_name=name, expand_detector=expand_detector)


def list_alertsmanagement_smart_detector_alert_rule(cmd, client,
                                                    resource_group=None,
                                                    expand_detector=None):
    if resource_group is not None and expand_detector is not None:
        return client.list_by_resource_group(resource_group_name=resource_group, expand_detector=expand_detector)
    return client.list(expand_detector=expand_detector)
