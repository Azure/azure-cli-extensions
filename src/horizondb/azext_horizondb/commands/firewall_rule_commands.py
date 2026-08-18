# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument, line-too-long, too-many-locals

from datetime import datetime
from knack.log import get_logger
from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.util import user_confirmation
from ..utils.validators import validate_resource_group, _validate_start_and_end_ip_address_order
from ..utils._network import DEFAULT_POOL_NAME

logger = get_logger(__name__)


def _generate_firewall_rule_name(start_ip_address, end_ip_address):
    now = datetime.now()
    # Include microseconds so rapid/scripted creates within the same second do not collide
    # (begin_create_or_update is an upsert and would otherwise silently overwrite).
    suffix = '{}-{}-{}_{}-{}-{}-{}'.format(now.year, now.month, now.day, now.hour, now.minute,
                                           now.second, now.microsecond)
    if start_ip_address == '0.0.0.0' and end_ip_address == '255.255.255.255':
        logger.warning("Configuring firewall rule to accept connections from all IPs...")
        return 'AllowAll_{}'.format(suffix)
    if start_ip_address == end_ip_address:
        logger.warning("Configuring firewall rule to accept connections from '%s'...", start_ip_address)
    else:
        logger.warning("Configuring firewall rule to accept connections from '%s' to '%s'...",
                       start_ip_address, end_ip_address)
    return 'FirewallIPAddress_{}'.format(suffix)


def _build_firewall_rule(start_ip_address, end_ip_address, description=None):
    from azext_horizondb.vendored_sdks.models import (
        HorizonDbFirewallRule,
        HorizonDbFirewallRuleProperties,
    )
    return HorizonDbFirewallRule(
        properties=HorizonDbFirewallRuleProperties(
            start_ip_address=start_ip_address,
            end_ip_address=end_ip_address,
            description=description))


def create_firewall_rule(cmd, client, resource_group_name, cluster_name, start_ip_address,
                         end_ip_address, firewall_rule_name=None, description=None):
    """Create or update a firewall rule on the cluster's default pool. Shared by the firewall-rule
    create command and by ``horizondb create``/``update`` when a --public-access value produces an
    IP range."""
    if end_ip_address is None and start_ip_address is not None:
        end_ip_address = start_ip_address
    elif start_ip_address is None and end_ip_address is not None:
        start_ip_address = end_ip_address
    elif start_ip_address is None and end_ip_address is None:
        raise ArgumentUsageError(
            "Need to pass in a value for either '--start-ip-address' or '--end-ip-address'.")

    if firewall_rule_name is None:
        firewall_rule_name = _generate_firewall_rule_name(start_ip_address, end_ip_address)

    resource = _build_firewall_rule(start_ip_address, end_ip_address, description)

    return client.begin_create_or_update(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=DEFAULT_POOL_NAME,
        firewall_rule_name=firewall_rule_name,
        resource=resource)


def horizondb_firewall_rule_create(cmd, client, resource_group_name, cluster_name, firewall_rule_name=None,
                                   start_ip_address=None, end_ip_address=None, description=None):
    validate_resource_group(resource_group_name)
    return create_firewall_rule(cmd, client, resource_group_name, cluster_name,
                                start_ip_address=start_ip_address, end_ip_address=end_ip_address,
                                firewall_rule_name=firewall_rule_name, description=description)


def horizondb_firewall_rule_update(cmd, client, resource_group_name, cluster_name, firewall_rule_name,
                                   start_ip_address=None, end_ip_address=None, description=None):
    validate_resource_group(resource_group_name)

    existing = client.get(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=DEFAULT_POOL_NAME,
        firewall_rule_name=firewall_rule_name)
    existing_props = existing.properties

    new_start = start_ip_address if start_ip_address is not None else existing_props.start_ip_address
    new_end = end_ip_address if end_ip_address is not None else existing_props.end_ip_address
    new_description = description if description is not None else existing_props.description

    # Re-validate order against the effective (merged) range; a single-endpoint update can otherwise
    # invert the range and only fail late at the backend.
    _validate_start_and_end_ip_address_order(new_start, new_end)

    resource = _build_firewall_rule(new_start, new_end, new_description)

    return client.begin_create_or_update(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=DEFAULT_POOL_NAME,
        firewall_rule_name=firewall_rule_name,
        resource=resource)


def horizondb_firewall_rule_delete(cmd, client, resource_group_name, cluster_name, firewall_rule_name,
                                   yes=False):
    validate_resource_group(resource_group_name)
    if not yes:
        user_confirmation(
            "Are you sure you want to delete the firewall rule '{0}' in cluster '{1}', resource group "
            "'{2}'".format(firewall_rule_name, cluster_name, resource_group_name), yes=yes)
    return client.begin_delete(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=DEFAULT_POOL_NAME,
        firewall_rule_name=firewall_rule_name)


def horizondb_firewall_rule_get(cmd, client, resource_group_name, cluster_name, firewall_rule_name):
    validate_resource_group(resource_group_name)
    return client.get(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=DEFAULT_POOL_NAME,
        firewall_rule_name=firewall_rule_name)


def horizondb_firewall_rule_list(cmd, client, resource_group_name, cluster_name):
    validate_resource_group(resource_group_name)
    return client.list(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        pool_name=DEFAULT_POOL_NAME)
