# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from knack.log import get_logger
from azure.cli.command_modules.acs._loadbalancer import (
    is_load_balancer_profile_provided as _is_load_balancer_profile_provided,
    configure_load_balancer_profile as _configure_load_balancer_profile,
)
logger = get_logger(__name__)


def update_load_balancer_profile(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                 outbound_ip_prefixes, outbound_ports, idle_timeout, backend_pool_type, profile, models):
    """parse and update an existing load balancer profile"""
    if not (_is_load_balancer_profile_provided(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                               outbound_ip_prefixes, outbound_ports, idle_timeout) or backend_pool_type):
        return profile
    if profile is None:
        if isinstance(models, SimpleNamespace):
            ManagedClusterLoadBalancerProfile = models.ManagedClusterLoadBalancerProfile
        else:
            ManagedClusterLoadBalancerProfile = models.get("ManagedClusterLoadBalancerProfile")
        profile = ManagedClusterLoadBalancerProfile()
    return configure_load_balancer_profile(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                           outbound_ip_prefixes, outbound_ports, idle_timeout, backend_pool_type, profile, models)


def create_load_balancer_profile(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                 outbound_ip_prefixes, outbound_ports, idle_timeout, backend_pool_type, models):
    """parse and build load balancer profile"""
    if not (_is_load_balancer_profile_provided(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                               outbound_ip_prefixes, outbound_ports, idle_timeout) or backend_pool_type):
        return None

    if isinstance(models, SimpleNamespace):
        ManagedClusterLoadBalancerProfile = models.ManagedClusterLoadBalancerProfile
    else:
        ManagedClusterLoadBalancerProfile = models.get("ManagedClusterLoadBalancerProfile")
    profile = ManagedClusterLoadBalancerProfile()
    return configure_load_balancer_profile(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                           outbound_ip_prefixes, outbound_ports, idle_timeout, backend_pool_type, profile, models)


def configure_load_balancer_profile(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                    outbound_ip_prefixes, outbound_ports, idle_timeout, backend_pool_type, profile, models):
    """configure a load balancer with customer supplied values"""

    profile = _configure_load_balancer_profile(managed_outbound_ip_count, managed_outbound_ipv6_count, outbound_ips,
                                               outbound_ip_prefixes, outbound_ports, idle_timeout, profile, models)
    if backend_pool_type:
        profile.backend_pool_type = backend_pool_type
    return profile
