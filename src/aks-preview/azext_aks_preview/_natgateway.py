# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import ResourceType


def create_nat_gateway_profile(cmd, managed_outbound_ip_count, idle_timeout):
    """parse and build NAT gateway profile"""
    if not is_nat_gateway_profile_provided(managed_outbound_ip_count, idle_timeout):
        return None

    ManagedClusterNATGatewayProfile = cmd.get_models('ManagedClusterNATGatewayProfile',
                                                resource_type=ResourceType.MGMT_CONTAINERSERVICE,
                                                operation_group='managed_clusters')
    profile = ManagedClusterNATGatewayProfile()
    return configure_nat_gateway_profile(cmd, managed_outbound_ip_count, idle_timeout, profile)


def update_nat_gateway_profile(cmd, managed_outbound_ip_count, idle_timeout, profile):
    """parse and update an existing NAT gateway profile"""
    if not is_nat_gateway_profile_provided(managed_outbound_ip_count, idle_timeout):
        return profile

    return configure_nat_gateway_profile(cmd, managed_outbound_ip_count, idle_timeout, profile)


def is_nat_gateway_profile_provided(managed_outbound_ip_count, idle_timeout):
    return any([managed_outbound_ip_count, idle_timeout])


def configure_nat_gateway_profile(cmd, managed_outbound_ip_count, idle_timeout, profile):
    """configure a NAT Gateway with customer supplied values"""
    if not profile:
        return profile

    if managed_outbound_ip_count:
        ManagedClusterManagedOutboundIPProfile = cmd.get_models('ManagedClusterManagedOutboundIPProfile',
                                                resource_type=ResourceType.MGMT_CONTAINERSERVICE,
                                                operation_group='managed_clusters')
        profile.managed_outbound_ip_profile = ManagedClusterManagedOutboundIPProfile(
            count=managed_outbound_ip_count
        )

    if idle_timeout:
        profile.idle_timeout_in_minutes = idle_timeout

    return profile
