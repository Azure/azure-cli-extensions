# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azext_aks_preview import _loadbalancer as loadbalancer
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.managed_cluster_decorator import AKSPreviewManagedClusterModels
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd


class TestLoadBalancer(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # store all the models used by nat gateway
        self.load_balancer_models = AKSPreviewManagedClusterModels(
            self.cmd, CUSTOM_MGMT_AKS_PREVIEW
        ).load_balancer_models

    def test_configure_load_balancer_profile(self):
        managed_outbound_ip_count = 5
        managed_outbound_ipv6_count = 3
        outbound_ips = None
        outbound_ip_prefixes = None
        outbound_ports = 80
        idle_timeout = 3600
        backend_pool_type = "nodeIP"

        # store all the models used by load balancer
        ManagedClusterLoadBalancerProfile = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfile
        )
        ManagedClusterLoadBalancerProfileManagedOutboundIPs = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs
        )
        ManagedClusterLoadBalancerProfileOutboundIPs = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPs
        )
        ManagedClusterLoadBalancerProfileOutboundIPPrefixes = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes
        )

        profile = ManagedClusterLoadBalancerProfile()
        # ips -> i_ps due to track 2 naming issue
        profile.managed_outbound_i_ps = (
            ManagedClusterLoadBalancerProfileManagedOutboundIPs(count=2)
        )
        # ips -> i_ps due to track 2 naming issue
        profile.outbound_i_ps = ManagedClusterLoadBalancerProfileOutboundIPs(
            public_i_ps="public_ips"
        )
        profile.outbound_ip_prefixes = (
            ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                public_ip_prefixes="public_ip_prefixes"
            )
        )

        p = loadbalancer.configure_load_balancer_profile(
            managed_outbound_ip_count,
            managed_outbound_ipv6_count,
            outbound_ips,
            outbound_ip_prefixes,
            outbound_ports,
            idle_timeout,
            backend_pool_type,
            "",
            profile,
            self.load_balancer_models,
        )

        self.assertEqual(p.managed_outbound_i_ps.count, 5)
        self.assertEqual(p.managed_outbound_i_ps.count_ipv6, 3)
        self.assertEqual(p.outbound_i_ps, None)
        self.assertEqual(p.outbound_ip_prefixes, None)
        self.assertEqual(p.allocated_outbound_ports, 80)
        self.assertEqual(p.idle_timeout_in_minutes, 3600)
        self.assertEqual(p.backend_pool_type, "nodeIP")
        managed_outbound_ip_count = 0
        p = loadbalancer.configure_load_balancer_profile(
            managed_outbound_ip_count,
            managed_outbound_ipv6_count,
            outbound_ips,
            outbound_ip_prefixes,
            outbound_ports,
            idle_timeout,
            backend_pool_type,
            "",
            profile,
            self.load_balancer_models,
        )

        self.assertEqual(p.managed_outbound_i_ps.count, 0)
        self.assertEqual(p.managed_outbound_i_ps.count_ipv6, 3)
        self.assertEqual(p.outbound_i_ps, None)
        self.assertEqual(p.outbound_ip_prefixes, None)
        self.assertEqual(p.allocated_outbound_ports, 80)
        self.assertEqual(p.idle_timeout_in_minutes, 3600)
        self.assertEqual(p.backend_pool_type, "nodeIP")

    def test_configure_load_balancer_profile_error(self):
        managed_outbound_ip_count = 5
        managed_outbound_ipv6_count = 3
        outbound_ips = "testpip1,testpip2"
        outbound_ip_prefixes = None
        outbound_ports = 80
        idle_timeout = 3600
        backend_pool_type = "nodeIP"

        # store all the models used by load balancer
        ManagedClusterLoadBalancerProfile = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfile
        )
        ManagedClusterLoadBalancerProfileManagedOutboundIPs = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs
        )
        ManagedClusterLoadBalancerProfileOutboundIPs = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPs
        )
        ManagedClusterLoadBalancerProfileOutboundIPPrefixes = (
            self.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes
        )

        profile = ManagedClusterLoadBalancerProfile()
        # ips -> i_ps due to track 2 naming issue
        profile.managed_outbound_i_ps = (
            ManagedClusterLoadBalancerProfileManagedOutboundIPs(count=2)
        )
        # ips -> i_ps due to track 2 naming issue
        profile.outbound_i_ps = ManagedClusterLoadBalancerProfileOutboundIPs(
            public_i_ps="public_ips"
        )
        profile.outbound_ip_prefixes = (
            ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                public_ip_prefixes="public_ip_prefixes"
            )
        )
        p = loadbalancer.configure_load_balancer_profile(
            managed_outbound_ip_count,
            managed_outbound_ipv6_count,
            outbound_ips,
            outbound_ip_prefixes,
            outbound_ports,
            idle_timeout,
            backend_pool_type,
            "",
            profile,
            self.load_balancer_models,
        )
        self.assertEqual(p.managed_outbound_i_ps.count, 5)
        self.assertEqual(p.managed_outbound_i_ps.count_ipv6, 3)
        self.assertEqual(
            p.outbound_i_ps.public_i_ps,
            [
                self.load_balancer_models.ResourceReference(id=x.strip())
                for x in ["testpip1", "testpip2"]
            ],
        )
        self.assertEqual(p.outbound_ip_prefixes, None)
        self.assertEqual(p.allocated_outbound_ports, 80)
        self.assertEqual(p.idle_timeout_in_minutes, 3600)
        self.assertEqual(p.backend_pool_type, "nodeIP")


if __name__ == "__main__":
    unittest.main()
