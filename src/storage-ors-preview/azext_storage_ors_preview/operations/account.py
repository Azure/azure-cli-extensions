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


def create_ors_policies(cmd, client, resource_group_name, source_account, policy_name, destination_account, properties=None,
                        rules=None):
    ObjectReplicationPolicy = cmd.get_models('ObjectReplicationPolicy')
    if properties:
        if os.path.exists(properties):
            ors_policy = get_file_json(properties)
        else:
            ors_policy = shell_safe_json_parse(properties)
    else:
        ors_policy = ObjectReplicationPolicy(policy_id=policy_name, source_account=source_account,
                                             destination_account=destination_account, rules=rules)
    return client.create_or_update(resource_group_name, account_name=source_account,
                                   object_replication_policy_id=policy_name, properties=ors_policy)


def update_ors_policies(cmd, instance, destination_account=None, rules=None):
    with cmd.update_context(instance) as c:
        c.set_param('rules', rules)

    if rules:
        instance.rules = rules

    return instance


def add_ors_rule(cmd, client, resource_group_name, account_name, policy_name, rule_name,
                 source_container, destination_container, tag=None, prefix_match=None):
    """
    Initialize rule for ORS policy
    """
    policy_properties = client.get(resource_group_name, account_name, policy_name)

    ObjectReplicationPolicyRule, ObjectReplicationPolicyFilter = \
        cmd.get_models('ObjectReplicationPolicyRule', 'ObjectReplicationPolicyFilter')
    new_ors_rule = ObjectReplicationPolicyRule(
        rule_id=rule_name,
        source_container=source_container,
        destination_container=destination_container,
        filter=ObjectReplicationPolicyFilter(predix_match=prefix_match, tag=tag)
    )
    policy_properties.rules.append(new_ors_rule)
    return client.create_or_update(resource_group_name, account_name, policy_name, policy_properties)


def remove_ors_rule(client, resource_group_name, account_name, policy_name, rule_name):

    policy_properties = client.get(resource_group_name, account_name, policy_name, rule_name)

    for rule in policy_properties.rules:
        if rule.rule_id == rule_name:
            policy_properties.rules.remove(rule)
    return client.create_or_update(resource_group_name, account_name, policy_name, policy_properties)


def get_ors_rule(client, resource_group_name, account_name, policy_name, rule_name):
    policy_properties = client.get(resource_group_name, account_name, policy_name)
    for rule in policy_properties.rules:
        if rule.rule_id == rule_name:
            return rule
    raise CLIError("{} does not exist.".format(rule_name))


def list_ors_rules(client, resource_group_name, account_name, policy_name):
    policy_properties = client.get(resource_group_name, account_name, policy_name)
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
