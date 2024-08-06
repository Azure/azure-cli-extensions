# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from knack.log import get_logger

logger = get_logger(__name__)


def update_load_balancer_profile(
    managed_outbound_ip_count,
    managed_outbound_ipv6_count,
    outbound_ips,
    outbound_ip_prefixes,
    outbound_ports,
    idle_timeout,
    backend_pool_type,
    health_probe_mode,
    profile,
    models,
):
    """parse and update an existing load balancer profile"""
    if not (
        is_load_balancer_profile_provided(
            managed_outbound_ip_count,
            managed_outbound_ipv6_count,
            outbound_ips,
            outbound_ip_prefixes,
            outbound_ports,
            idle_timeout,
            backend_pool_type,
            health_probe_mode,
        )
    ):
        return profile
    if not profile:
        if isinstance(models, SimpleNamespace):
            ManagedClusterLoadBalancerProfile = models.ManagedClusterLoadBalancerProfile
        else:
            ManagedClusterLoadBalancerProfile = models.get(
                "ManagedClusterLoadBalancerProfile"
            )
        profile = ManagedClusterLoadBalancerProfile()
    return configure_load_balancer_profile(
        managed_outbound_ip_count,
        managed_outbound_ipv6_count,
        outbound_ips,
        outbound_ip_prefixes,
        outbound_ports,
        idle_timeout,
        backend_pool_type,
        health_probe_mode,
        profile,
        models,
    )


def create_load_balancer_profile(
    managed_outbound_ip_count,
    managed_outbound_ipv6_count,
    outbound_ips,
    outbound_ip_prefixes,
    outbound_ports,
    idle_timeout,
    backend_pool_type,
    health_probe_mode,
    models,
):
    """parse and build load balancer profile"""
    if not (
        is_load_balancer_profile_provided(
            managed_outbound_ip_count,
            managed_outbound_ipv6_count,
            outbound_ips,
            outbound_ip_prefixes,
            outbound_ports,
            idle_timeout,
            backend_pool_type,
            health_probe_mode,
        )
    ):
        return None
    if isinstance(models, SimpleNamespace):
        ManagedClusterLoadBalancerProfile = models.ManagedClusterLoadBalancerProfile
    else:
        ManagedClusterLoadBalancerProfile = models.get(
            "ManagedClusterLoadBalancerProfile"
        )
    profile = ManagedClusterLoadBalancerProfile()
    return configure_load_balancer_profile(
        managed_outbound_ip_count,
        managed_outbound_ipv6_count,
        outbound_ips,
        outbound_ip_prefixes,
        outbound_ports,
        idle_timeout,
        backend_pool_type,
        health_probe_mode,
        profile,
        models,
    )


def configure_load_balancer_profile(
    managed_outbound_ip_count,
    managed_outbound_ipv6_count,
    outbound_ips,
    outbound_ip_prefixes,
    outbound_ports,
    idle_timeout,
    backend_pool_type,
    health_probe_mode,
    profile,
    models,
):
    """configure a load balancer with customer supplied values"""
    if any(
        [
            managed_outbound_ip_count is not None,
            managed_outbound_ipv6_count is not None,
            outbound_ips,
            outbound_ip_prefixes,
        ]
    ):
        outbound_ip_resources = _get_load_balancer_outbound_ips(outbound_ips, models)
        if outbound_ip_resources:
            if isinstance(models, SimpleNamespace):
                ManagedClusterLoadBalancerProfileOutboundIPs = (
                    models.ManagedClusterLoadBalancerProfileOutboundIPs
                )
            else:
                ManagedClusterLoadBalancerProfileOutboundIPs = models.get(
                    "ManagedClusterLoadBalancerProfileOutboundIPs"
                )
            # ips -> i_ps due to track 2 naming issue
            profile.outbound_i_ps = ManagedClusterLoadBalancerProfileOutboundIPs(
                public_i_ps=outbound_ip_resources
            )
        else:
            profile.outbound_i_ps = None
        outbound_ip_prefix_resources = _get_load_balancer_outbound_ip_prefixes(
            outbound_ip_prefixes, models
        )
        if outbound_ip_prefix_resources:
            if isinstance(models, SimpleNamespace):
                ManagedClusterLoadBalancerProfileOutboundIPPrefixes = (
                    models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes
                )
            else:
                ManagedClusterLoadBalancerProfileOutboundIPPrefixes = models.get(
                    "ManagedClusterLoadBalancerProfileOutboundIPPrefixes"
                )
            profile.outbound_ip_prefixes = (
                ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                    public_ip_prefixes=outbound_ip_prefix_resources
                )
            )
        else:
            profile.outbound_ip_prefixes = None
        if managed_outbound_ip_count is not None or managed_outbound_ipv6_count is not None:
            if profile.managed_outbound_i_ps is None:
                if isinstance(models, SimpleNamespace):
                    ManagedClusterLoadBalancerProfileManagedOutboundIPs = (
                        models.ManagedClusterLoadBalancerProfileManagedOutboundIPs
                    )
                else:
                    ManagedClusterLoadBalancerProfileManagedOutboundIPs = models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )
                profile.managed_outbound_i_ps = (
                    ManagedClusterLoadBalancerProfileManagedOutboundIPs()
                )
            if managed_outbound_ip_count is not None:
                profile.managed_outbound_i_ps.count = managed_outbound_ip_count
            if managed_outbound_ipv6_count is not None:
                profile.managed_outbound_i_ps.count_ipv6 = managed_outbound_ipv6_count
        else:
            profile.managed_outbound_i_ps = None

    if outbound_ports is not None:
        profile.allocated_outbound_ports = outbound_ports
    if idle_timeout:
        profile.idle_timeout_in_minutes = idle_timeout
    if backend_pool_type:
        profile.backend_pool_type = backend_pool_type
    if health_probe_mode:
        profile.cluster_service_load_balancer_health_probe_mode = health_probe_mode
    return profile


def is_load_balancer_profile_provided(
    managed_outbound_ip_count,
    managed_outbound_ipv6_count,
    outbound_ips,
    ip_prefixes,
    outbound_ports,
    idle_timeout,
    backend_pool_type,
    health_probe_mode,
):
    return any(
        [
            managed_outbound_ip_count is not None,
            managed_outbound_ipv6_count is not None,
            outbound_ips,
            ip_prefixes,
            outbound_ports is not None,
            idle_timeout,
            backend_pool_type,
            health_probe_mode,
        ]
    )


def _get_load_balancer_outbound_ips(load_balancer_outbound_ips, models):
    """parse load balancer profile outbound IP ids and return an array of references to the outbound IP resources"""
    load_balancer_outbound_ip_resources = None
    if isinstance(models, SimpleNamespace):
        ResourceReference = models.ResourceReference
    else:
        ResourceReference = models.get("ResourceReference")
    if load_balancer_outbound_ips is not None:
        if isinstance(load_balancer_outbound_ips, str):
            load_balancer_outbound_ip_resources = [
                ResourceReference(id=x.strip())
                for x in load_balancer_outbound_ips.split(",")
            ]
        else:
            load_balancer_outbound_ip_resources = load_balancer_outbound_ips
    return load_balancer_outbound_ip_resources


def _get_load_balancer_outbound_ip_prefixes(load_balancer_outbound_ip_prefixes, models):
    """parse load balancer profile outbound IP prefix ids and return an array \
    of references to the outbound IP prefix resources"""
    load_balancer_outbound_ip_prefix_resources = None
    if isinstance(models, SimpleNamespace):
        ResourceReference = models.ResourceReference
    else:
        ResourceReference = models.get("ResourceReference")
    if load_balancer_outbound_ip_prefixes:
        if isinstance(load_balancer_outbound_ip_prefixes, str):
            load_balancer_outbound_ip_prefix_resources = [
                ResourceReference(id=x.strip())
                for x in load_balancer_outbound_ip_prefixes.split(",")
            ]
        else:
            load_balancer_outbound_ip_prefix_resources = (
                load_balancer_outbound_ip_prefixes
            )
    return load_balancer_outbound_ip_prefix_resources
