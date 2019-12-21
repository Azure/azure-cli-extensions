# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


def create_ors_policy(cmd, client, resource_group_name, account_name, properties=None, source_account=None, destination_account=None,
                      policy_id="default", rule_id=None, source_container=None, destination_container=None, tag=None,
                      prefix_match=None):

    ObjectReplicationPolicy = cmd.get_models('ObjectReplicationPolicy')

    if properties is None:
        rules = []
        ObjectReplicationPolicyRule, ObjectReplicationPolicyFilter = \
            cmd.get_models('ObjectReplicationPolicyRule', 'ObjectReplicationPolicyFilter')
        if source_container and destination_container:
            rule = ObjectReplicationPolicyRule(
                rule_id=rule_id,
                source_container=source_container,
                destination_container=destination_container,
                filter=ObjectReplicationPolicyFilter(prefix_match=prefix_match, tag=tag)
            )
            rules.append(rule)
        ors_policy = ObjectReplicationPolicy(source_account=source_account,
                                             destination_account=destination_account,
                                             rules=rules)
    else:
        ors_policy = properties

    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   object_replication_policy_id=policy_id, properties=ors_policy)


def update_ors_policy(cmd, parameters, properties=None, source_account=None, destination_account=None,
                      rule_id=None, source_container=None, destination_container=None, tag=None,
                      prefix_match=None):

    ObjectReplicationPolicy = cmd.get_models('ObjectReplicationPolicy')

    if source_account is not None:
        parameters.source_account = source_account
    if destination_account is not None:
        parameters.destination_account = destination_account
    if rule_id:
        for i, rule in enumerate(parameters.rules):
            if rule.rule_id == rule_id:
                parameters.rules[i] = update_ors_rule(rule, source_container=source_container,
                                                      destination_container=destination_container,
                                                      tag=tag, prefix_match=prefix_match)
    if properties is not None:
        parameters = properties

    return parameters


def get_ors_policy(client, resource_group_name, account_name, policy_id='default'):
    return client.get(resource_group_name=resource_group_name, account_name=account_name,
                      object_replication_policy_id=policy_id)


def add_ors_rule(cmd, client, resource_group_name, account_name, policy_id,
                 source_container, destination_container, tag=None, prefix_match=None):
    """
    Initialize rule for ORS policy
    """
    policy_properties = client.get(resource_group_name, account_name, policy_id)

    ObjectReplicationPolicyRule, ObjectReplicationPolicyFilter = \
        cmd.get_models('ObjectReplicationPolicyRule', 'ObjectReplicationPolicyFilter')
    new_ors_rule = ObjectReplicationPolicyRule(
        source_container=source_container,
        destination_container=destination_container,
        filter=ObjectReplicationPolicyFilter(predix_match=prefix_match, tag=tag)
    )
    policy_properties.rules.append(new_ors_rule)
    return client.create_or_update(resource_group_name, account_name, policy_id, policy_properties)


def remove_ors_rule(client, resource_group_name, account_name, policy_id, rule_id):

    policy_properties = client.get(resource_group_name=resource_group_name,
                                   account_name=account_name,
                                   object_replication_policy_id=policy_id)
    n = len(policy_properties.rules)
    for i in range(n):
        if policy_properties.rules[i].rule_id == rule_id:
            policy_properties.rules.pop(i)
            break
    if i == n:
        raise CLIError("--rule-id is invalid.")

    return client.create_or_update(resource_group_name, account_name, policy_id, policy_properties)


def get_ors_rule(client, resource_group_name, account_name, policy_id, rule_id):
    policy_properties = client.get(resource_group_name, account_name, policy_id)
    for rule in policy_properties.rules:
        if rule.rule_id == rule_id:
            return rule
    raise CLIError("{} does not exist.".format(rule_id))


def list_ors_rules(client, resource_group_name, account_name, policy_id):
    policy_properties = client.get(resource_group_name, account_name, policy_id)
    return policy_properties.rules


def update_ors_rule(instance, source_container=None, destination_container=None, tag=None, prefix_match=None):
    if destination_container is not None:
        instance.destination_container = destination_container
    if source_container is not None:
        instance.source_container = source_container
    if tag is not None:
        instance.filter.tag = tag
    if prefix_match is not None:
        instance.filter.prefix_match = prefix_match
    return instance
