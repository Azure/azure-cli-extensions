# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-locals

from knack.log import get_logger
from azure.cli.core.util import sdk_no_wait, user_confirmation

logger = get_logger(__name__)


def horizondb_firewall_rule_create(client, resource_group_name, cluster_name,
                                   firewall_rule_name, start_ip_address, end_ip_address,
                                   pool_name='default',
                                   rule_description=None, no_wait=False):
    from azext_horizondb.vendored_sdks.models import HorizonDbFirewallRule, HorizonDbFirewallRuleProperties

    properties = HorizonDbFirewallRuleProperties(
        start_ip_address=start_ip_address,
        end_ip_address=end_ip_address,
        description=rule_description,
    )

    resource = HorizonDbFirewallRule(
        properties=properties,
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       pool_name=pool_name,
                       firewall_rule_name=firewall_rule_name,
                       resource=resource)


def horizondb_firewall_rule_update(client, resource_group_name, cluster_name,
                                   firewall_rule_name, pool_name='default',
                                   start_ip_address=None, end_ip_address=None,
                                   rule_description=None, no_wait=False):
    from azext_horizondb.vendored_sdks.models import HorizonDbFirewallRule, HorizonDbFirewallRuleProperties

    existing = client.get(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=pool_name,
        firewall_rule_name=firewall_rule_name)

    props = existing.properties
    properties = HorizonDbFirewallRuleProperties(
        start_ip_address=start_ip_address if start_ip_address is not None else props.start_ip_address,
        end_ip_address=end_ip_address if end_ip_address is not None else props.end_ip_address,
        description=rule_description if rule_description is not None else props.description,
    )

    resource = HorizonDbFirewallRule(
        properties=properties,
    )

    return sdk_no_wait(no_wait, client.begin_create_or_update,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       pool_name=pool_name,
                       firewall_rule_name=firewall_rule_name,
                       resource=resource)


def horizondb_firewall_rule_delete(cmd, client, resource_group_name, cluster_name,
                                   firewall_rule_name, pool_name='default',
                                   no_wait=False, yes=False):
    if not yes:
        user_confirmation(
            "Are you sure you want to delete the firewall rule '{0}' for cluster '{1}' in resource group '{2}'".format(
                firewall_rule_name, cluster_name, resource_group_name), yes=yes)
    return sdk_no_wait(no_wait, client.begin_delete,
                       resource_group_name=resource_group_name,
                       cluster_name=cluster_name,
                       pool_name=pool_name,
                       firewall_rule_name=firewall_rule_name)


def horizondb_firewall_rule_list(client, resource_group_name, cluster_name, pool_name='default'):
    return client.list(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=pool_name)
