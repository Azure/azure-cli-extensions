# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def create_nat_gateway_profile(managed_outbound_ip_count, idle_timeout, models):
    """parse and build NAT gateway profile"""
    if not is_nat_gateway_profile_provided(managed_outbound_ip_count, idle_timeout):
        return None

    # profile = ManagedClusterNATGatewayProfile()
    profile = models.get("ManagedClusterNATGatewayProfile")
    return configure_nat_gateway_profile(managed_outbound_ip_count, idle_timeout, profile, models)


def update_nat_gateway_profile(managed_outbound_ip_count, idle_timeout, profile, models):
    """parse and update an existing NAT gateway profile"""
    if not is_nat_gateway_profile_provided(managed_outbound_ip_count, idle_timeout):
        return profile

    return configure_nat_gateway_profile(managed_outbound_ip_count, idle_timeout, profile, models)


def is_nat_gateway_profile_provided(managed_outbound_ip_count, idle_timeout):
    return any([managed_outbound_ip_count, idle_timeout])


def configure_nat_gateway_profile(managed_outbound_ip_count, idle_timeout, profile, models):
    """configure a NAT Gateway with customer supplied values"""
    if not profile:
        return profile

    if managed_outbound_ip_count:
        ManagedClusterManagedOutboundIPProfile = models.get("ManagedClusterManagedOutboundIPProfile")
        profile.managed_outbound_ip_profile = ManagedClusterManagedOutboundIPProfile(
            count=managed_outbound_ip_count
        )

    if idle_timeout:
        profile.idle_timeout_in_minutes = idle_timeout

    return profile
