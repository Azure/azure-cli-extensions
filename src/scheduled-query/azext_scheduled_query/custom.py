# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError


def _build_criteria(condition, condition_query):
    from .vendored_sdks.azure_mgmt_scheduled_query.models import (ScheduledQueryRuleCriteria,
                                                                  ConditionFailingPeriods)
    for cond in condition:
        if condition_query and cond.query in condition_query:
            # replace query placeholder
            placeholder = cond.query
            cond.query = condition_query[placeholder]
        if cond.failing_periods is None:
            cond.failing_periods = ConditionFailingPeriods(
                min_failing_periods_to_alert=1,
                number_of_evaluation_periods=1
            )
        else:
            if cond.failing_periods.min_failing_periods_to_alert > cond.failing_periods.number_of_evaluation_periods:
                raise InvalidArgumentValueError('EvaluationPeriod must be greater than or equals to MinTimeToFail.')
    return ScheduledQueryRuleCriteria(all_of=condition)


def create_scheduled_query(client,
                           resource_group_name,
                           rule_name,
                           scopes,
                           condition,
                           action_groups=None,
                           custom_properties=None,
                           condition_query=None,
                           disabled=False,
                           description=None,
                           tags=None,
                           location=None,
                           severity=2,
                           window_size='5m',
                           evaluation_frequency='5m',
                           target_resource_type=None,
                           mute_actions_duration=None,
                           auto_mitigate=True,
                           skip_query_validation=False,
                           check_workspace_alerts_storage=False):
    criteria = _build_criteria(condition, condition_query)
    parameters = {}
    actions = {}
    actions['action_groups'] = action_groups if action_groups is not None else []
    actions['custom_properties'] = custom_properties if custom_properties is not None else {}
    parameters['actions'] = actions
    parameters['scopes'] = scopes
    parameters['criteria'] = criteria
    if actions is not None:
        parameters['actions'] = actions
    parameters['enabled'] = not disabled
    if description is not None:
        parameters['description'] = description
    if tags is not None:
        parameters['tags'] = tags
    if location is not None:
        parameters['location'] = location
    parameters['severity'] = severity
    parameters['window_size'] = window_size
    parameters['evaluation_frequency'] = evaluation_frequency
    parameters['target_resource_types'] = [target_resource_type] if target_resource_type else None
    parameters['mute_actions_duration'] = mute_actions_duration
    parameters['auto_mitigate'] = auto_mitigate
    parameters['skip_query_validation'] = skip_query_validation
    parameters['check_workspace_alerts_storage_configured'] = check_workspace_alerts_storage
    return client.create_or_update(resource_group_name=resource_group_name, rule_name=rule_name, parameters=parameters)


def list_scheduled_query(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def update_scheduled_query(cmd,
                           instance,
                           tags=None,
                           disabled=None,
                           condition=None,
                           action_groups=None,
                           custom_properties=None,
                           condition_query=None,
                           description=None,
                           severity=None,
                           window_size=None,
                           evaluation_frequency=None,
                           mute_actions_duration=None,
                           target_resource_type=None,
                           auto_mitigate=None,
                           skip_query_validation=None,
                           check_workspace_alerts_storage=None
                           ):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
        c.set_param('enabled', not disabled)
        c.set_param('description', description)
        if instance.actions is None:
            from azext_scheduled_query.vendored_sdks.azure_mgmt_scheduled_query.models import Actions
            c.set_param("actions", Actions())
        c.set_param('actions.action_groups', action_groups)
        c.set_param('actions.custom_properties', custom_properties)
        c.set_param('severity', severity)
        c.set_param('window_size', window_size)
        c.set_param('evaluation_frequency', evaluation_frequency)
        c.set_param('mute_actions_duration', mute_actions_duration)
        c.set_param('target_resource_type', target_resource_type)
        c.set_param('auto_mitigate', auto_mitigate)
        c.set_param('skip_query_validation', skip_query_validation)
        c.set_param('check_workspace_alerts_storage_configured', check_workspace_alerts_storage)
        if condition is not None:
            criteria = _build_criteria(condition, condition_query)
            c.set_param('criteria', criteria)
        if disabled is not None:
            c.set_param('enabled', not disabled)
        if auto_mitigate is not None:
            c.set_param('auto_mitigate', auto_mitigate)
    return instance
