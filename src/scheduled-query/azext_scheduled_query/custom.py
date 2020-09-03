# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError

def create_scheduled_query(client, resource_group_name, rule_name, scopes, condition, disabled=False, description=None,
                           tags=None, location=None, actions=None, severity=2, window_size='5m', evaluation_frequency='1m',
                           target_resource_type=None, mute_actions_duration='PT30M', scheduled_query=None,
                           resource_id_column=None, number_of_evaluation_periods=1, min_failing_periods_to_alert=1):
    from .vendored_sdks.azure_mgmt_scheduled_query.models import (ScheduledQueryRuleResource,
                                                                  ScheduledQueryRuleCriteria,
                                                                  ConditionFailingPeriods)
    condition[0].query = scheduled_query
    condition[0].resource_id_column = resource_id_column
    condition[0].failing_periods = ConditionFailingPeriods(number_of_evaluation_periods=number_of_evaluation_periods,
                                                           min_failing_periods_to_alert=min_failing_periods_to_alert)

    criteria = ScheduledQueryRuleCriteria(all_of=condition)

    kwargs = {
        'description': description,
        'severity': severity,
        'enabled': not disabled,
        'scopes': scopes,
        'evaluation_frequency': evaluation_frequency,
        'window_size': window_size,
        'criteria': criteria,
        'target_resource_type': target_resource_type,
        'actions': actions,
        'tags': tags,
        'location': location,
        'mute_actions_duration': mute_actions_duration
    }
    return client.create_or_update(resource_group_name, rule_name, ScheduledQueryRuleResource(**kwargs))


def list_scheduled_query(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def update_scheduled_query(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance