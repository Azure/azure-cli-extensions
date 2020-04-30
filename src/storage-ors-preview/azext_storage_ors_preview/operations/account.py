# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

from azure.cli.core.util import find_child_item

from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


def create_or_policy(cmd, client, resource_group_name, account_name, properties=None, source_account=None,
                     destination_account=None, policy_id="default", rule_id=None, source_container=None,
                     destination_container=None, min_creation_time=None, prefix_match=None):

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
                filters=ObjectReplicationPolicyFilter(prefix_match=prefix_match, min_creation_time=min_creation_time)
            )
            rules.append(rule)
        or_policy = ObjectReplicationPolicy(source_account=source_account,
                                            destination_account=destination_account,
                                            rules=rules)
    else:
        or_policy = properties

    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   object_replication_policy_id=policy_id, properties=or_policy)


def update_or_policy(client, parameters, resource_group_name, account_name, object_replication_policy_id=None,
                     properties=None, source_account=None, destination_account=None, ):

    if source_account is not None:
        parameters.source_account = source_account
    if destination_account is not None:
        parameters.destination_account = destination_account

    if properties is not None:
        parameters = properties
        if "policyId" in properties.keys() and properties["policyId"]:
            object_replication_policy_id = properties["policyId"]

    return client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                                   object_replication_policy_id=object_replication_policy_id, properties=parameters)


def get_or_policy(client, resource_group_name, account_name, policy_id='default'):
    return client.get(resource_group_name=resource_group_name, account_name=account_name,
                      object_replication_policy_id=policy_id)


def add_or_rule(cmd, client, resource_group_name, account_name, policy_id,
                source_container, destination_container, min_creation_time=None, prefix_match=None):

    """
    Initialize rule for or policy
    """
    policy_properties = client.get(resource_group_name, account_name, policy_id)

    ObjectReplicationPolicyRule, ObjectReplicationPolicyFilter = \
        cmd.get_models('ObjectReplicationPolicyRule', 'ObjectReplicationPolicyFilter')
    new_or_rule = ObjectReplicationPolicyRule(
        source_container=source_container,
        destination_container=destination_container,
        filters=ObjectReplicationPolicyFilter(prefix_match=prefix_match, min_creation_time=min_creation_time)
    )
    policy_properties.rules.append(new_or_rule)
    return client.create_or_update(resource_group_name, account_name, policy_id, policy_properties)


def remove_or_rule(client, resource_group_name, account_name, policy_id, rule_id):

    or_policy = client.get(resource_group_name=resource_group_name,
                           account_name=account_name,
                           object_replication_policy_id=policy_id)

    rule = find_child_item(or_policy, rule_id, path='rules', key_path='rule_id')
    or_policy.rules.remove(rule)

    return client.create_or_update(resource_group_name, account_name, policy_id, or_policy)


def get_or_rule(client, resource_group_name, account_name, policy_id, rule_id):
    policy_properties = client.get(resource_group_name, account_name, policy_id)
    for rule in policy_properties.rules:
        if rule.rule_id == rule_id:
            return rule
    raise CLIError("{} does not exist.".format(rule_id))


def list_or_rules(client, resource_group_name, account_name, policy_id):
    policy_properties = client.get(resource_group_name, account_name, policy_id)
    return policy_properties.rules


def update_or_rule(client, resource_group_name, account_name, policy_id, rule_id, source_container=None,
                   destination_container=None, min_creation_time=None, prefix_match=None):

    policy_properties = client.get(resource_group_name, account_name, policy_id)

    for i, rule in enumerate(policy_properties.rules):
        if rule.rule_id == rule_id:
            if destination_container is not None:
                policy_properties.rules[i].destination_container = destination_container
            if source_container is not None:
                policy_properties.rules[i].source_container = source_container
            if min_creation_time is not None:
                policy_properties.rules[i].filters.min_creation_time = min_creation_time
            if prefix_match is not None:
                policy_properties.rules[i].filters.prefix_match = prefix_match

    client.create_or_update(resource_group_name=resource_group_name, account_name=account_name,
                            object_replication_policy_id=policy_id, properties=policy_properties)

    return get_or_rule(client, resource_group_name=resource_group_name, account_name=account_name,
                       policy_id=policy_id, rule_id=rule_id)
