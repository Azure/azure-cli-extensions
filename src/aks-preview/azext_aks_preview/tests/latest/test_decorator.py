# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
import unittest
from unittest.mock import Mock, patch

import requests
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._consts import (
    ADDONS,
    CONST_ACC_SGX_QUOTE_HELPER_ENABLED,
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
    CONST_AZURE_POLICY_ADDON_NAME,
    CONST_CONFCOM_ADDON_NAME,
    CONST_GITOPS_ADDON_NAME,
    CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    CONST_INGRESS_APPGW_ADDON_NAME,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME,
    CONST_INGRESS_APPGW_SUBNET_CIDR,
    CONST_INGRESS_APPGW_SUBNET_ID,
    CONST_INGRESS_APPGW_WATCH_NAMESPACE,
    CONST_KUBE_DASHBOARD_ADDON_NAME,
    CONST_MONITORING_ADDON_NAME,
    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID,
    CONST_MONITORING_USING_AAD_MSI_AUTH,
    CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
    CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
    CONST_ROTATION_POLL_INTERVAL,
    CONST_SECRET_ROTATION_ENABLED,
    CONST_VIRTUAL_NODE_ADDON_NAME,
    CONST_VIRTUAL_NODE_SUBNET_NAME,
)
from azext_aks_preview.decorator import (
    AKSPreviewContext,
    AKSPreviewCreateDecorator,
    AKSPreviewModels,
    AKSPreviewUpdateDecorator,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockClient, MockCmd
from azext_aks_preview.tests.latest.test_aks_commands import _get_test_data_file
from azure.cli.command_modules.acs._consts import (
    DecoratorEarlyExitException,
    DecoratorMode,
)
from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
    UnknownError,
)
from msrestazure.azure_exceptions import CloudError


class AKSPreviewModelsTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)

    def test_models(self):
        models = AKSPreviewModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)

        # load models directly (instead of through the `get_sdk` method provided by the cli component)
        from azure.cli.core.profiles._shared import AZURE_API_PROFILES

        sdk_profile = AZURE_API_PROFILES["latest"][CUSTOM_MGMT_AKS_PREVIEW]
        api_version = sdk_profile.default_api_version
        module_name = "azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.v{}.models".format(
            api_version.replace("-", "_")
        )
        module = importlib.import_module(module_name)

        self.assertEqual(models.KubeletConfig, getattr(module, "KubeletConfig"))
        self.assertEqual(models.LinuxOSConfig, getattr(module, "LinuxOSConfig"))
        self.assertEqual(
            models.ManagedClusterHTTPProxyConfig,
            getattr(module, "ManagedClusterHTTPProxyConfig"),
        )
        self.assertEqual(
            models.ManagedClusterPodIdentityProfile,
            getattr(module, "ManagedClusterPodIdentityProfile"),
        )
        self.assertEqual(
            models.WindowsGmsaProfile, getattr(module, "WindowsGmsaProfile")
        )
        self.assertEqual(models.CreationData, getattr(module, "CreationData"))
        # nat gateway models
        self.assertEqual(
            models.nat_gateway_models.get("ManagedClusterNATGatewayProfile"),
            getattr(module, "ManagedClusterNATGatewayProfile"),
        )
        self.assertEqual(
            models.nat_gateway_models.get(
                "ManagedClusterManagedOutboundIPProfile"
            ),
            getattr(module, "ManagedClusterManagedOutboundIPProfile"),
        )


class AKSPreviewContextTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)

    def test__get_vm_set_type(self):
        # default & dynamic completion
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "vm_set_type": None,
                "kubernetes_version": "",
                "enable_vmss": False,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1._get_vm_set_type(read_only=True), None)
        self.assertEqual(ctx_1.get_vm_set_type(), "VirtualMachineScaleSets")
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_ap_name", type="test_mc_vm_set_type"
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_vm_set_type(), "test_mc_vm_set_type")

        # custom value & dynamic completion
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {
                "vm_set_type": "availabilityset",
                "kubernetes_version": "",
                "enable_vmss": True,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid vm_set_type when enable_vmss is specified
        with self.assertRaises(InvalidArgumentValueError):
            self.assertEqual(ctx_2.get_vm_set_type(), "AvailabilitySet")

        # custom value & dynamic completion
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {
                "vm_set_type": None,
                "kubernetes_version": "",
                "enable_vmss": True,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid vm_set_type when enable_vmss is specified
        self.assertEqual(ctx_3.get_vm_set_type(), "VirtualMachineScaleSets")

    def test_get_zones(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"node_zones": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_zones(), None)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name",
            availability_zones=["test_mc_zones1", "test_mc_zones2"],
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_zones(), ["test_mc_zones1", "test_mc_zones2"]
        )

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"node_zones": ["test_zones1", "test_zones2"]},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_zones(), ["test_zones1", "test_zones2"])

    def test_get_pod_subnet_id(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"pod_subnet_id": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_pod_subnet_id(), None)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name", pod_subnet_id="test_mc_pod_subnet_id"
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_pod_subnet_id(), "test_mc_pod_subnet_id")

    def test_get_pod_cidrs(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"pod_cidrs": "10.244.0.0/16,2001:abcd::/64"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(
            ctx_1.get_pod_cidrs(), ["10.244.0.0/16", "2001:abcd::/64"]
        )

        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"pod_cidrs": ""},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_pod_cidrs(), [])

        ctx_3 = AKSPreviewContext(
            self.cmd,
            {"pod_cidrs": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_pod_cidrs(), None)

    def test_get_service_cidrs(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"service_cidrs": "10.244.0.0/16,2001:abcd::/64"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(
            ctx_1.get_service_cidrs(), ["10.244.0.0/16", "2001:abcd::/64"]
        )

        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"service_cidrs": ""},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_service_cidrs(), [])

        ctx_3 = AKSPreviewContext(
            self.cmd,
            {"service_cidrs": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_service_cidrs(), None)

    def test_get_ip_families(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"ip_families": "IPv4,IPv6"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_ip_families(), ["IPv4", "IPv6"])

        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"ip_families": ""},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_ip_families(), [])

        ctx_3 = AKSPreviewContext(
            self.cmd,
            {"ip_families": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_ip_families(), None)

    def test_get_load_balancer_managed_outbound_ipv6_count(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "load_balancer_managed_outbound_ipv6_count": None,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(
            ctx_1.get_load_balancer_managed_outbound_ipv6_count(), None
        )
        load_balancer_profile = self.models.lb_models.get(
            "ManagedClusterLoadBalancerProfile"
        )(
            managed_outbound_i_ps=self.models.lb_models.get(
                "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
            )(count_ipv6=10)
        )
        network_profile = self.models.ContainerServiceNetworkProfile(
            load_balancer_profile=load_balancer_profile
        )
        mc = self.models.ManagedCluster(
            location="test_location", network_profile=network_profile
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_load_balancer_managed_outbound_ipv6_count(), 10
        )

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"load_balancer_managed_outbound_ipv6_count": 4},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(
            ctx_2.get_load_balancer_managed_outbound_ipv6_count(), 4
        )

        # custom value
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {"load_balancer_managed_outbound_ipv6_count": 0},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(
            ctx_3.get_load_balancer_managed_outbound_ipv6_count(), 0
        )

    def test_get_enable_fips_image(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"enable_fips_image": False},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_fips_image(), False)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name",
            enable_fips=True,
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_enable_fips_image(), True)

    def test_get_workload_runtime(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"workload_runtime": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_workload_runtime(), None)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name",
            workload_runtime="test_mc_workload_runtime",
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_workload_runtime(), "test_mc_workload_runtime"
        )

    def test_get_gpu_instance_profile(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"gpu_instance_profile": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_gpu_instance_profile(), None)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name",
            gpu_instance_profile="test_mc_gpu_instance_profile",
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_gpu_instance_profile(), "test_mc_gpu_instance_profile"
        )

    def test_get_kubelet_config(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"kubelet_config": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_kubelet_config(), None)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name",
            kubelet_config=self.models.KubeletConfig(pod_max_pids=100),
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_kubelet_config(),
            self.models.KubeletConfig(pod_max_pids=100),
        )

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"kubelet_config": "fake-path"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_2.get_kubelet_config()

        # custom value
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {"kubelet_config": _get_test_data_file("invalidconfig.json")},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_3.get_kubelet_config()

    def test_get_linux_os_config(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"linux_os_config": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_linux_os_config(), None)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name",
            linux_os_config=self.models.LinuxOSConfig(swap_file_size_mb=200),
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_linux_os_config(),
            self.models.LinuxOSConfig(swap_file_size_mb=200),
        )

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"linux_os_config": "fake-path"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_2.get_linux_os_config()

        # custom value
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {"linux_os_config": _get_test_data_file("invalidconfig.json")},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_3.get_linux_os_config()

    def test_get_http_proxy_config(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"http_proxy_config": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_http_proxy_config(), None)
        mc = self.models.ManagedCluster(
            location="test_location",
            http_proxy_config=self.models.ManagedClusterHTTPProxyConfig(
                http_proxy="test_http_proxy"
            ),
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_http_proxy_config(),
            self.models.ManagedClusterHTTPProxyConfig(
                http_proxy="test_http_proxy"
            ),
        )

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"http_proxy_config": "fake-path"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_2.get_http_proxy_config()

        # custom value
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {"http_proxy_config": _get_test_data_file("invalidconfig.json")},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_3.get_http_proxy_config()

    def test_get_node_resource_group(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"node_resource_group": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_node_resource_group(), None)
        mc = self.models.ManagedCluster(
            location="test_location",
            node_resource_group="test_node_resource_group",
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_node_resource_group(), "test_node_resource_group"
        )

    def test_get_nat_gateway_managed_outbound_ip_count(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"nat_gateway_managed_outbound_ip_count": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(
            ctx_1.get_nat_gateway_managed_outbound_ip_count(), None
        )
        nat_gateway_profile = self.models.nat_gateway_models.get(
            "ManagedClusterNATGatewayProfile"
        )(
            managed_outbound_ip_profile=self.models.nat_gateway_models.get(
                "ManagedClusterManagedOutboundIPProfile"
            )(count=10)
        )
        network_profile = self.models.ContainerServiceNetworkProfile(
            nat_gateway_profile=nat_gateway_profile
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile,
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_nat_gateway_managed_outbound_ip_count(), 10)

    def test_get_nat_gateway_idle_timeout(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"nat_gateway_idle_timeout": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_nat_gateway_idle_timeout(), None)
        nat_gateway_profile = self.models.nat_gateway_models.get(
            "ManagedClusterNATGatewayProfile"
        )(
            idle_timeout_in_minutes=20,
        )
        network_profile = self.models.ContainerServiceNetworkProfile(
            nat_gateway_profile=nat_gateway_profile
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile,
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_nat_gateway_idle_timeout(), 20)

    def test_get_enable_pod_security_policy(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"enable_pod_security_policy": False},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_pod_security_policy(), False)
        mc = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_enable_pod_security_policy(), True)

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {
                "enable_pod_security_policy": True,
                "disable_pod_security_policy": True,
            },
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_pod_security_policy and disable_pod_security_policy
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_2.get_enable_pod_security_policy()

    def test_get_disable_pod_security_policy(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"disable_pod_security_policy": False},
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        self.assertEqual(ctx_1.get_disable_pod_security_policy(), False)
        mc = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=False,
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_disable_pod_security_policy(), False)

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {
                "enable_pod_security_policy": True,
                "disable_pod_security_policy": True,
            },
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_pod_security_policy and disable_pod_security_policy
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_2.get_disable_pod_security_policy()

    def test_get_enable_managed_identity(self):
        # custom value
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"enable_managed_identity": False, "enable_pod_identity": True},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_1.get_enable_managed_identity(), False)

    def test_get_enable_pod_identity(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"enable_pod_identity": False},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_pod_identity(), False)
        pod_identity_profile = self.models.ManagedClusterPodIdentityProfile(
            enabled=True
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            pod_identity_profile=pod_identity_profile,
        )
        ctx_1.attach_mc(mc)
        # fail on enable_managed_identity not specified
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_1.get_enable_pod_identity(), True)

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {
                "enable_managed_identity": True,
                "enable_pod_identity": True,
                "enable_pod_identity_with_kubenet": False,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(
            network_plugin="kubenet"
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_2,
        )
        ctx_2.attach_mc(mc_2)
        # fail on enable_pod_identity_with_kubenet not specified
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_2.get_enable_pod_identity(), True)

    def test_get_enable_pod_identity_with_kubenet(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"enable_pod_identity_with_kubenet": False},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_pod_identity_with_kubenet(), False)
        pod_identity_profile = self.models.ManagedClusterPodIdentityProfile(
            enabled=True,
            allow_network_plugin_kubenet=True,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            pod_identity_profile=pod_identity_profile,
        )
        ctx_1.attach_mc(mc)
        # fail on enable_managed_identity not specified
        # with self.assertRaises(RequiredArgumentMissingError):
        self.assertEqual(ctx_1.get_enable_pod_identity_with_kubenet(), True)

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {
                "enable_managed_identity": True,
                "enable_pod_identity": True,
                "enable_pod_identity_with_kubenet": False,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(
            network_plugin="kubenet"
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_2,
        )
        ctx_2.attach_mc(mc_2)
        # fail on enable_pod_identity_with_kubenet not specified
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(
                ctx_2.get_enable_pod_identity_with_kubenet(), False
            )

    def test_get_addon_consts(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        addon_consts = ctx_1.get_addon_consts()
        ground_truth_addon_consts = {
            "ADDONS": ADDONS,
            "CONST_ACC_SGX_QUOTE_HELPER_ENABLED": CONST_ACC_SGX_QUOTE_HELPER_ENABLED,
            "CONST_AZURE_POLICY_ADDON_NAME": CONST_AZURE_POLICY_ADDON_NAME,
            "CONST_CONFCOM_ADDON_NAME": CONST_CONFCOM_ADDON_NAME,
            "CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME": CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
            "CONST_INGRESS_APPGW_ADDON_NAME": CONST_INGRESS_APPGW_ADDON_NAME,
            "CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID": CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID,
            "CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME": CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME,
            "CONST_INGRESS_APPGW_SUBNET_CIDR": CONST_INGRESS_APPGW_SUBNET_CIDR,
            "CONST_INGRESS_APPGW_SUBNET_ID": CONST_INGRESS_APPGW_SUBNET_ID,
            "CONST_INGRESS_APPGW_WATCH_NAMESPACE": CONST_INGRESS_APPGW_WATCH_NAMESPACE,
            "CONST_KUBE_DASHBOARD_ADDON_NAME": CONST_KUBE_DASHBOARD_ADDON_NAME,
            "CONST_MONITORING_ADDON_NAME": CONST_MONITORING_ADDON_NAME,
            "CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID": CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID,
            "CONST_OPEN_SERVICE_MESH_ADDON_NAME": CONST_OPEN_SERVICE_MESH_ADDON_NAME,
            "CONST_VIRTUAL_NODE_ADDON_NAME": CONST_VIRTUAL_NODE_ADDON_NAME,
            "CONST_VIRTUAL_NODE_SUBNET_NAME": CONST_VIRTUAL_NODE_SUBNET_NAME,
            "CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME": CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
            "CONST_SECRET_ROTATION_ENABLED": CONST_SECRET_ROTATION_ENABLED,
            "CONST_ROTATION_POLL_INTERVAL": CONST_ROTATION_POLL_INTERVAL,
            # new addon consts in aks-preview
            "CONST_GITOPS_ADDON_NAME": CONST_GITOPS_ADDON_NAME,
            "CONST_MONITORING_USING_AAD_MSI_AUTH": CONST_MONITORING_USING_AAD_MSI_AUTH,
        }
        self.assertEqual(addon_consts, ground_truth_addon_consts)

    def test_get_appgw_subnet_prefix(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "appgw_subnet_prefix": None,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_appgw_subnet_prefix(), None)
        addon_profiles_1 = {
            CONST_INGRESS_APPGW_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={
                    CONST_INGRESS_APPGW_SUBNET_CIDR: "test_appgw_subnet_prefix"
                },
            )
        }
        mc = self.models.ManagedCluster(
            location="test_location", addon_profiles=addon_profiles_1
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_appgw_subnet_prefix(), "test_appgw_subnet_prefix"
        )

    def test_get_enable_msi_auth_for_monitoring(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "enable_msi_auth_for_monitoring": False,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_msi_auth_for_monitoring(), False)
        addon_profiles_1 = {
            CONST_MONITORING_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={CONST_MONITORING_USING_AAD_MSI_AUTH: True},
            )
        }
        mc = self.models.ManagedCluster(
            location="test_location", addon_profiles=addon_profiles_1
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_enable_msi_auth_for_monitoring(), True)

    def test_get_no_wait(self):
        # custom value
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "no_wait": True,
                "enable_msi_auth_for_monitoring": True,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ctx_1.set_intermediate("monitoring", True, overwrite_exists=True)
        self.assertEqual(ctx_1.get_no_wait(), False)

    def test_validate_gmsa_options(self):
        # default
        ctx = AKSPreviewContext(
            self.cmd,
            {},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ctx._AKSPreviewContext__validate_gmsa_options(False, None, None, False)
        ctx._AKSPreviewContext__validate_gmsa_options(True, None, None, True)

        # fail on yes & prompt_y_n not specified
        with patch(
            "azext_aks_preview.decorator.prompt_y_n",
            return_value=False,
        ), self.assertRaises(DecoratorEarlyExitException):
            ctx._AKSPreviewContext__validate_gmsa_options(
                True, None, None, False
            )

        # fail on gmsa_root_domain_name not specified
        with self.assertRaises(RequiredArgumentMissingError):
            ctx._AKSPreviewContext__validate_gmsa_options(
                True, "test_gmsa_dns_server", None, False
            )

        # fail on enable_windows_gmsa not specified
        with self.assertRaises(RequiredArgumentMissingError):
            ctx._AKSPreviewContext__validate_gmsa_options(
                False, None, "test_gmsa_root_domain_name", False
            )

    def test_get_enable_windows_gmsa(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "enable_windows_gmsa": False,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_windows_gmsa(), False)
        windows_gmsa_profile_1 = self.models.WindowsGmsaProfile(enabled=True)
        windows_profile_1 = self.models.ManagedClusterWindowsProfile(
            admin_username="test_admin_username",
            gmsa_profile=windows_gmsa_profile_1,
        )
        mc = self.models.ManagedCluster(
            location="test_location", windows_profile=windows_profile_1
        )
        ctx_1.attach_mc(mc)
        with patch(
            "azext_aks_preview.decorator.prompt_y_n",
            return_value=True,
        ):
            self.assertEqual(ctx_1.get_enable_windows_gmsa(), True)

    def test_get_gmsa_dns_server_and_root_domain_name(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "enable_windows_gmsa": False,
                "gmsa_dns_server": None,
                "gmsa_root_domain_name": None,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(
            ctx_1.get_gmsa_dns_server_and_root_domain_name(), (None, None)
        )
        windows_gmsa_profile_1 = self.models.WindowsGmsaProfile(
            enabled=True,
            dns_server="test_dns_server",
            root_domain_name="test_root_domain_name",
        )
        windows_profile_1 = self.models.ManagedClusterWindowsProfile(
            admin_username="test_admin_username",
            gmsa_profile=windows_gmsa_profile_1,
        )
        mc = self.models.ManagedCluster(
            location="test_location", windows_profile=windows_profile_1
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_gmsa_dns_server_and_root_domain_name(),
            ("test_dns_server", "test_root_domain_name"),
        )

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {
                "enable_windows_gmsa": True,
                "gmsa_dns_server": "test_gmsa_dns_server",
                "gmsa_root_domain_name": "test_gmsa_root_domain_name",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        windows_gmsa_profile_2 = self.models.WindowsGmsaProfile(
            enabled=True,
            dns_server="test_dns_server",
            root_domain_name=None,
        )
        windows_profile_2 = self.models.ManagedClusterWindowsProfile(
            admin_username="test_admin_username",
            gmsa_profile=windows_gmsa_profile_2,
        )
        mc = self.models.ManagedCluster(
            location="test_location", windows_profile=windows_profile_2
        )
        ctx_2.attach_mc(mc)
        # fail on inconsistent state
        with self.assertRaises(CLIInternalError):
            ctx_2.get_gmsa_dns_server_and_root_domain_name()

    def test_get_snapshot_id(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "snapshot_id": None,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_snapshot_id(), None)
        creation_data = self.models.CreationData(
            source_resource_id="test_source_resource_id"
        )
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name", creation_data=creation_data
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_snapshot_id(), "test_source_resource_id")

    def test_get_snapshot(self):
        # custom value
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "snapshot_id": "test_source_resource_id",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock()
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_1.get_snapshot(), mock_snapshot)
        # test cache
        self.assertEqual(ctx_1.get_snapshot(), mock_snapshot)

    def test_get_kubernetes_version(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"kubernetes_version": ""},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_kubernetes_version(), "")
        mc = self.models.ManagedCluster(
            location="test_location",
            kubernetes_version="test_mc_kubernetes_version",
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_kubernetes_version(), "test_mc_kubernetes_version"
        )

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"kubernetes_version": "", "snapshot_id": "test_snapshot_id"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock(kubernetes_version="test_kubernetes_version")
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            self.assertEqual(
                ctx_2.get_kubernetes_version(), "test_kubernetes_version"
            )

        # custom value
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {
                "kubernetes_version": "custom_kubernetes_version",
                "snapshot_id": "test_snapshot_id",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock(kubernetes_version="test_kubernetes_version")
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            self.assertEqual(
                ctx_3.get_kubernetes_version(), "custom_kubernetes_version"
            )

    def test_get_os_sku(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"os_sku": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_os_sku(), None)
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name", os_sku="test_mc_os_sku"
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_os_sku(), "test_mc_os_sku")

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"os_sku": None, "snapshot_id": "test_snapshot_id"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock(os_sku="test_os_sku")
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_2.get_os_sku(), "test_os_sku")

        # custom value
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {
                "os_sku": "custom_os_sku",
                "snapshot_id": "test_snapshot_id",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock(os_sku="test_os_sku")
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_3.get_os_sku(), "custom_os_sku")

    def test_get_node_vm_size(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {"node_vm_size": None},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_node_vm_size(), "Standard_DS2_v2")
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(
            name="test_nodepool_name", vm_size="Standard_ABCD_v2"
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_node_vm_size(), "Standard_ABCD_v2")

        # custom value
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {"node_vm_size": None, "snapshot_id": "test_snapshot_id"},
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock(vm_size="test_vm_size")
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_2.get_node_vm_size(), "test_vm_size")

        # custom value
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {
                "node_vm_size": "custom_node_vm_size",
                "snapshot_id": "test_snapshot_id",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock(vm_size="test_vm_size")
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_3.get_node_vm_size(), "custom_node_vm_size")

    def test_test_get_outbound_type(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "outbound_type": None,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1._get_outbound_type(read_only=True), None)
        self.assertEqual(ctx_1.get_outbound_type(), "loadBalancer")
        network_profile_1 = self.models.ContainerServiceNetworkProfile(
            outbound_type="test_outbound_type"
        )
        mc = self.models.ManagedCluster(
            location="test_location", network_profile=network_profile_1
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_outbound_type(), "test_outbound_type")

        # invalid parameter
        ctx_2 = AKSPreviewContext(
            self.cmd,
            {
                "outbound_type": CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY,
                "load_balancer_sku": "basic",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid load_balancer_sku (basic) when outbound_type is CONST_OUTBOUND_TYPE_MANAGED_NAT_GATEWAY
        with self.assertRaises(InvalidArgumentValueError):
            ctx_2.get_outbound_type()

        # invalid parameter
        ctx_3 = AKSPreviewContext(
            self.cmd,
            {
                "outbound_type": CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
                "load_balancer_sku": "basic",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid load_balancer_sku (basic) when outbound_type is CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY
        with self.assertRaises(InvalidArgumentValueError):
            ctx_3.get_outbound_type()

        # invalid parameter
        ctx_4 = AKSPreviewContext(
            self.cmd,
            {
                "outbound_type": CONST_OUTBOUND_TYPE_USER_ASSIGNED_NAT_GATEWAY,
                "vnet_subnet_id": None,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on vnet_subnet_id not specified
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_4.get_outbound_type()

        # invalid parameter
        ctx_5 = AKSPreviewContext(
            self.cmd,
            {
                "outbound_type": CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
                "vnet_subnet_id": None,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on vnet_subnet_id not specified
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_5.get_outbound_type()

        # invalid parameter
        ctx_6 = AKSPreviewContext(
            self.cmd,
            {
                "outbound_type": CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
                "vnet_subnet_id": "test_vnet_subnet_id",
                "load_balancer_managed_outbound_ip_count": 10,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on mutually exclusive outbound_type and managed_outbound_ip_count/outbound_ips/outbound_ip_prefixes of
        # load balancer
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_6.get_outbound_type()

        # invalid parameter
        ctx_7 = AKSPreviewContext(
            self.cmd,
            {
                "outbound_type": CONST_OUTBOUND_TYPE_USER_DEFINED_ROUTING,
                "vnet_subnet_id": "test_vnet_subnet_id",
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        load_balancer_profile = self.models.lb_models.get(
            "ManagedClusterLoadBalancerProfile"
        )(
            outbound_ip_prefixes=self.models.lb_models.get(
                "ManagedClusterLoadBalancerProfileOutboundIPPrefixes"
            )(
                public_ip_prefixes=[
                    self.models.lb_models.get("ResourceReference")(
                        id="test_public_ip_prefix"
                    )
                ]
            )
        )
        # fail on mutually exclusive outbound_type and managed_outbound_ip_count/outbound_ips/outbound_ip_prefixes of
        # load balancer
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_7.get_outbound_type(
                load_balancer_profile=load_balancer_profile,
            )


class AKSPreviewCreateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()

    def test_set_up_agent_pool_profiles(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "nodepool_name": "nodepool1",
                "nodepool_tags": None,
                "nodepool_labels": None,
                "node_count": 3,
                "node_vm_size": "Standard_DS2_v2",
                "os_sku": None,
                "vnet_subnet_id": None,
                "pod_subnet_id": None,
                "ppg": None,
                "zones": None,
                "enable_node_public_ip": False,
                "enable_fips_image": False,
                "node_public_ip_prefix_id": None,
                "enable_encryption_at_host": False,
                "enable_ultra_ssd": False,
                "max_pods": 0,
                "node_osdisk_size": 0,
                "node_osdisk_type": None,
                "enable_cluster_autoscaler": False,
                "min_count": None,
                "max_count": None,
                "workload_runtime": None,
                "gpu_instance_profile": None,
                "kubelet_config": None,
                "snapshot_id": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_agent_pool_profiles(None)
        dec_mc_1 = dec_1.set_up_agent_pool_profiles(mc_1)
        agent_pool_profile_1 = self.models.ManagedClusterAgentPoolProfile(
            # Must be 12 chars or less before ACS RP adds to it
            name="nodepool1",
            tags=None,
            node_labels=None,
            count=3,
            vm_size="Standard_DS2_v2",
            os_type="Linux",
            os_sku=None,
            vnet_subnet_id=None,
            pod_subnet_id=None,
            proximity_placement_group_id=None,
            availability_zones=None,
            enable_node_public_ip=False,
            enable_fips=False,
            node_public_ip_prefix_id=None,
            enable_encryption_at_host=False,
            enable_ultra_ssd=False,
            max_pods=None,
            type="VirtualMachineScaleSets",
            mode="System",
            os_disk_size_gb=None,
            os_disk_type=None,
            enable_auto_scaling=False,
            min_count=None,
            max_count=None,
            workload_runtime=None,
            gpu_instance_profile=None,
            kubelet_config=None,
            creation_data=None,
        )
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        ground_truth_mc_1.agent_pool_profiles = [agent_pool_profile_1]
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "nodepool_name": "test_np_name1234",
                "nodepool_tags": {"k1": "v1"},
                "nodepool_labels": {"k1": "v1", "k2": "v2"},
                "node_count": 10,
                "node_vm_size": "Standard_DSx_vy",
                "os_sku": None,
                "vnet_subnet_id": "test_vnet_subnet_id",
                "pod_subnet_id": "test_pod_subnet_id",
                "ppg": "test_ppg_id",
                "zones": ["tz1", "tz2"],
                "enable_node_public_ip": True,
                "enable_fips_image": True,
                "node_public_ip_prefix_id": "test_node_public_ip_prefix_id",
                "enable_encryption_at_host": True,
                "enable_ultra_ssd": True,
                "max_pods": 50,
                "node_osdisk_size": 100,
                "node_osdisk_type": "test_os_disk_type",
                "enable_cluster_autoscaler": True,
                "min_count": 5,
                "max_count": 20,
                "workload_runtime": "test_workload_runtime",
                "gpu_instance_profile": "test_gpu_instance_profile",
                "kubelet_config": _get_test_data_file("kubeletconfig.json"),
                "linux_os_config": _get_test_data_file("linuxosconfig.json"),
                "snapshot_id": "test_snapshot_id",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        mock_snapshot = Mock(
            kubernetes_version="",
            os_sku="snapshot_os_sku",
            vm_size="snapshot_vm_size",
        )
        with patch(
            "azext_aks_preview.decorator._get_snapshot",
            return_value=mock_snapshot,
        ):
            dec_mc_2 = dec_2.set_up_agent_pool_profiles(mc_2)
        agent_pool_profile_2 = self.models.ManagedClusterAgentPoolProfile(
            # Must be 12 chars or less before ACS RP adds to it
            name="test_np_name",
            tags={"k1": "v1"},
            node_labels={"k1": "v1", "k2": "v2"},
            count=10,
            vm_size="Standard_DSx_vy",
            os_type="Linux",
            os_sku="snapshot_os_sku",
            vnet_subnet_id="test_vnet_subnet_id",
            pod_subnet_id="test_pod_subnet_id",
            proximity_placement_group_id="test_ppg_id",
            availability_zones=["tz1", "tz2"],
            enable_node_public_ip=True,
            enable_fips=True,
            node_public_ip_prefix_id="test_node_public_ip_prefix_id",
            enable_encryption_at_host=True,
            enable_ultra_ssd=True,
            max_pods=50,
            type="VirtualMachineScaleSets",
            mode="System",
            os_disk_size_gb=100,
            os_disk_type="test_os_disk_type",
            enable_auto_scaling=True,
            min_count=5,
            max_count=20,
            workload_runtime="test_workload_runtime",
            gpu_instance_profile="test_gpu_instance_profile",
            kubelet_config={
                "cpuManagerPolicy": "static",
                "cpuCfsQuota": True,
                "cpuCfsQuotaPeriod": "200ms",
                "imageGcHighThreshold": 90,
                "imageGcLowThreshold": 70,
                "topologyManagerPolicy": "best-effort",
                "allowedUnsafeSysctls": ["kernel.msg*", "net.*"],
                "failSwapOn": False,
                "containerLogMaxFiles": 10,
                "podMaxPids": 120,
                "containerLogMaxSizeMB": 20,
            },
            linux_os_config={
                "transparentHugePageEnabled": "madvise",
                "transparentHugePageDefrag": "defer+madvise",
                "swapFileSizeMB": 1500,
                "sysctls": {
                    "netCoreSomaxconn": 163849,
                    "netIpv4TcpTwReuse": True,
                    "netIpv4IpLocalPortRange": "32000 60000",
                },
            },
            creation_data=self.models.CreationData(
                source_resource_id="test_snapshot_id"
            ),
        )
        ground_truth_mc_2 = self.models.ManagedCluster(location="test_location")
        ground_truth_mc_2.agent_pool_profiles = [agent_pool_profile_2]
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_set_up_http_proxy_config(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "http_proxy_config": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_http_proxy_config(None)
        dec_mc_1 = dec_1.set_up_http_proxy_config(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {"http_proxy_config": _get_test_data_file("httpproxyconfig.json")},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_mc_2 = dec_2.set_up_http_proxy_config(mc_2)
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            http_proxy_config={
                "httpProxy": "http://myproxy.server.com:8080/",
                "httpsProxy": "https://myproxy.server.com:8080/",
                "noProxy": ["localhost", "127.0.0.1"],
            },
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_set_up_node_resource_group(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "node_resource_group": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_node_resource_group(None)
        dec_mc_1 = dec_1.set_up_node_resource_group(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {"node_resource_group": "test_node_resource_group"},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_mc_2 = dec_2.set_up_node_resource_group(mc_2)
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            node_resource_group="test_node_resource_group",
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_set_up_network_profile(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_sku": None,
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
                "load_balancer_outbound_ports": None,
                "load_balancer_idle_timeout": None,
                "outbound_type": None,
                "network_plugin": None,
                "pod_cidr": None,
                "service_cidr": None,
                "dns_service_ip": None,
                "docker_bridge_cidr": None,
                "network_policy": None,
                "nat_gateway_managed_outbound_ip_count": None,
                "nat_gateway_idle_timeout": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_network_profile(None)
        dec_mc_1 = dec_1.set_up_network_profile(mc_1)

        network_profile_1 = self.models.ContainerServiceNetworkProfile(
            network_plugin="kubenet",  # default value in SDK
            pod_cidr="10.244.0.0/16",  # default value in SDK
            service_cidr="10.0.0.0/16",  # default value in SDK
            dns_service_ip="10.0.0.10",  # default value in SDK
            docker_bridge_cidr="172.17.0.1/16",  # default value in SDK
            load_balancer_sku="standard",
            outbound_type="loadBalancer",
        )
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location", network_profile=network_profile_1
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_sku": None,
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
                "load_balancer_outbound_ports": None,
                "load_balancer_idle_timeout": None,
                "outbound_type": None,
                "network_plugin": "kubenet",
                "pod_cidr": "10.246.0.0/16",
                "service_cidr": None,
                "dns_service_ip": None,
                "docker_bridge_cidr": None,
                "network_policy": None,
                "nat_gateway_managed_outbound_ip_count": 10,
                "nat_gateway_idle_timeout": 20,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_mc_2 = dec_2.set_up_network_profile(mc_2)

        nat_gateway_profile_2 = self.models.nat_gateway_models.get(
            "ManagedClusterNATGatewayProfile"
        )(
            managed_outbound_ip_profile=self.models.nat_gateway_models.get(
                "ManagedClusterManagedOutboundIPProfile"
            )(count=10),
            idle_timeout_in_minutes=20,
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(
            network_plugin="kubenet",
            pod_cidr="10.246.0.0/16",
            service_cidr=None,  # overwritten to None
            dns_service_ip=None,  # overwritten to None
            docker_bridge_cidr=None,  # overwritten to None
            load_balancer_sku="standard",
            outbound_type="loadBalancer",
            nat_gateway_profile=nat_gateway_profile_2,
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location", network_profile=network_profile_2
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

        # dual-stack
        dec_3 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_sku": None,
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_managed_outbound_ipv6_count": 3,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
                "load_balancer_outbound_ports": None,
                "load_balancer_idle_timeout": None,
                "outbound_type": None,
                "network_plugin": "kubenet",
                "pod_cidr": None,
                "service_cidr": None,
                "pod_cidrs": "10.246.0.0/16,2001:abcd::/64",
                "service_cidrs": "10.0.0.0/16,2001:ffff::/108",
                "ip_families": "IPv4,IPv6",
                "dns_service_ip": None,
                "docker_bridge_cidr": None,
                "network_policy": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_3 = self.models.ManagedCluster(location="test_location")
        dec_mc_3 = dec_3.set_up_network_profile(mc_3)

        network_profile_3 = self.models.ContainerServiceNetworkProfile(
            network_plugin="kubenet",
            pod_cidr=None,  # overwritten to None
            service_cidr=None,  # overwritten to None
            dns_service_ip=None,  # overwritten to None
            docker_bridge_cidr=None,  # overwritten to None
            load_balancer_sku="standard",
            outbound_type="loadBalancer",
            ip_families=["IPv4", "IPv6"],
            pod_cidrs=["10.246.0.0/16", "2001:abcd::/64"],
            service_cidrs=["10.0.0.0/16", "2001:ffff::/108"],
        )
        load_balancer_profile = self.models.lb_models.get(
            "ManagedClusterLoadBalancerProfile"
        )(
            managed_outbound_i_ps=self.models.lb_models.get(
                "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
            )(
                count=1,
                count_ipv6=3,
            )
        )

        network_profile_3.load_balancer_profile = load_balancer_profile

        ground_truth_mc_3 = self.models.ManagedCluster(
            location="test_location", network_profile=network_profile_3
        )
        self.assertEqual(dec_mc_3, ground_truth_mc_3)

    def test_set_up_pod_security_policy(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_security_policy": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_pod_security_policy(None)
        dec_mc_1 = dec_1.set_up_pod_security_policy(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location", enable_pod_security_policy=False
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {"enable_pod_security_policy": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_mc_2 = dec_2.set_up_pod_security_policy(mc_2)
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_set_up_pod_identity_profile(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_identity": False,
                "enable_pod_identity_with_kubenet": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_pod_identity_profile(None)
        dec_mc_1 = dec_1.set_up_pod_identity_profile(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_managed_identity": True,
                "enable_pod_identity": True,
                "enable_pod_identity_with_kubenet": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(
            network_plugin="kubenet"
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location", network_profile=network_profile_2
        )
        dec_mc_2 = dec_2.set_up_pod_identity_profile(mc_2)
        network_profile_2 = self.models.ContainerServiceNetworkProfile(
            network_plugin="kubenet"
        )
        pod_identity_profile_2 = self.models.ManagedClusterPodIdentityProfile(
            enabled=True,
            allow_network_plugin_kubenet=True,
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_2,
            pod_identity_profile=pod_identity_profile_2,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_build_monitoring_addon_profile(self):
        # default
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "resource_group_name": "test_rg_name",
                "name": "test_name",
                "location": "test_location",
                "enable_addons": "monitoring",
                "workspace_resource_id": "test_workspace_resource_id",
                "enable_msi_auth_for_monitoring": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        dec_1.context.set_intermediate(
            "subscription_id", "test_subscription_id"
        )

        with patch(
            "azext_aks_preview.decorator.ensure_container_insights_for_monitoring",
            return_value=None,
        ):
            self.assertEqual(dec_1.context.get_intermediate("monitoring"), None)
            monitoring_addon_profile = dec_1.build_monitoring_addon_profile()
            ground_truth_monitoring_addon_profile = self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={
                    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID: "/test_workspace_resource_id",
                    CONST_MONITORING_USING_AAD_MSI_AUTH: False,
                },
            )
            self.assertEqual(
                monitoring_addon_profile, ground_truth_monitoring_addon_profile
            )
            self.assertEqual(dec_1.context.get_intermediate("monitoring"), True)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "resource_group_name": "test_rg_name",
                "name": "test_name",
                "location": "test_location",
                "enable_addons": "monitoring",
                "workspace_resource_id": "test_workspace_resource_id",
                "enable_msi_auth_for_monitoring": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        dec_2.context.set_intermediate(
            "subscription_id", "test_subscription_id"
        )

        with patch(
            "azext_aks_preview.decorator.ensure_container_insights_for_monitoring",
            return_value=None,
        ):
            self.assertEqual(dec_2.context.get_intermediate("monitoring"), None)
            monitoring_addon_profile = dec_2.build_monitoring_addon_profile()
            ground_truth_monitoring_addon_profile = self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={
                    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID: "/test_workspace_resource_id",
                    CONST_MONITORING_USING_AAD_MSI_AUTH: True,
                },
            )
            self.assertEqual(
                monitoring_addon_profile, ground_truth_monitoring_addon_profile
            )
            self.assertEqual(dec_2.context.get_intermediate("monitoring"), True)

    def test_build_ingress_appgw_addon_profile(self):
        # default
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        self.assertEqual(
            dec_1.context.get_intermediate("ingress_appgw_addon_enabled"), None
        )
        ingress_appgw_addon_profile = dec_1.build_ingress_appgw_addon_profile()
        ground_truth_ingress_appgw_addon_profile = (
            self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={},
            )
        )
        self.assertEqual(
            ingress_appgw_addon_profile,
            ground_truth_ingress_appgw_addon_profile,
        )
        self.assertEqual(
            dec_1.context.get_intermediate("ingress_appgw_addon_enabled"), True
        )

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "appgw_name": "test_appgw_name",
                "appgw_subnet_prefix": "test_appgw_subnet_prefix",
                "appgw_id": "test_appgw_id",
                "appgw_subnet_id": "test_appgw_subnet_id",
                "appgw_watch_namespace": "test_appgw_watch_namespace",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        self.assertEqual(
            dec_2.context.get_intermediate("ingress_appgw_addon_enabled"), None
        )
        ingress_appgw_addon_profile = dec_2.build_ingress_appgw_addon_profile()
        ground_truth_ingress_appgw_addon_profile = self.models.ManagedClusterAddonProfile(
            enabled=True,
            config={
                CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME: "test_appgw_name",
                CONST_INGRESS_APPGW_SUBNET_CIDR: "test_appgw_subnet_prefix",
                CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID: "test_appgw_id",
                CONST_INGRESS_APPGW_SUBNET_ID: "test_appgw_subnet_id",
                CONST_INGRESS_APPGW_WATCH_NAMESPACE: "test_appgw_watch_namespace",
            },
        )
        self.assertEqual(
            ingress_appgw_addon_profile,
            ground_truth_ingress_appgw_addon_profile,
        )
        self.assertEqual(
            dec_2.context.get_intermediate("ingress_appgw_addon_enabled"), True
        )

        # custom value
        dec_3 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "appgw_name": "test_appgw_name",
                "appgw_subnet_prefix": "test_appgw_subnet_prefix",
                "appgw_subnet_cidr": "test_appgw_subnet_cidr",
                "appgw_id": "test_appgw_id",
                "appgw_subnet_id": "test_appgw_subnet_id",
                "appgw_watch_namespace": "test_appgw_watch_namespace",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        self.assertEqual(
            dec_3.context.get_intermediate("ingress_appgw_addon_enabled"), None
        )
        ingress_appgw_addon_profile = dec_3.build_ingress_appgw_addon_profile()
        ground_truth_ingress_appgw_addon_profile = self.models.ManagedClusterAddonProfile(
            enabled=True,
            config={
                CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME: "test_appgw_name",
                CONST_INGRESS_APPGW_SUBNET_CIDR: "test_appgw_subnet_cidr",
                CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID: "test_appgw_id",
                CONST_INGRESS_APPGW_SUBNET_ID: "test_appgw_subnet_id",
                CONST_INGRESS_APPGW_WATCH_NAMESPACE: "test_appgw_watch_namespace",
            },
        )
        self.assertEqual(
            ingress_appgw_addon_profile,
            ground_truth_ingress_appgw_addon_profile,
        )
        self.assertEqual(
            dec_3.context.get_intermediate("ingress_appgw_addon_enabled"), True
        )

    def test_build_gitops_addon_profile(self):
        # default
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        gitops_addon_profile = dec_1.build_gitops_addon_profile()
        ground_truth_gitops_addon_profile = (
            self.models.ManagedClusterAddonProfile(
                enabled=True,
            )
        )
        self.assertEqual(
            gitops_addon_profile, ground_truth_gitops_addon_profile
        )

    def test_set_up_addon_profiles(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_addons": None,
                "workspace_resource_id": None,
                "aci_subnet_name": None,
                "appgw_name": None,
                "appgw_subnet_cidr": None,
                "appgw_id": None,
                "appgw_subnet_id": None,
                "appgw_watch_namespace": None,
                "enable_sgxquotehelper": False,
                "enable_secret_rotation": False,
                "rotation_poll_interval": None,
                "appgw_subnet_prefix": None,
                "enable_msi_auth_for_monitoring": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_addon_profiles(None)
        dec_mc_1 = dec_1.set_up_addon_profiles(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location", addon_profiles={}
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)
        self.assertEqual(dec_1.context.get_intermediate("monitoring"), None)
        self.assertEqual(
            dec_1.context.get_intermediate("enable_virtual_node"), None
        )
        self.assertEqual(
            dec_1.context.get_intermediate("ingress_appgw_addon_enabled"), None
        )

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_name",
                "resource_group_name": "test_rg_name",
                "location": "test_location",
                "vnet_subnet_id": "test_vnet_subnet_id",
                "enable_addons": "monitoring,ingress-appgw,gitops",
                "workspace_resource_id": "test_workspace_resource_id",
                "enable_msi_auth_for_monitoring": True,
                "appgw_name": "test_appgw_name",
                "appgw_subnet_prefix": "test_appgw_subnet_prefix",
                "appgw_id": "test_appgw_id",
                "appgw_subnet_id": "test_appgw_subnet_id",
                "appgw_watch_namespace": "test_appgw_watch_namespace",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        dec_2.context.set_intermediate(
            "subscription_id", "test_subscription_id"
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        with patch(
            "azext_aks_preview.decorator.ensure_container_insights_for_monitoring",
            return_value=None,
        ):
            dec_mc_2 = dec_2.set_up_addon_profiles(mc_2)

        addon_profiles_2 = {
            CONST_MONITORING_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={
                    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID: "/test_workspace_resource_id",
                    CONST_MONITORING_USING_AAD_MSI_AUTH: True,
                },
            ),
            CONST_INGRESS_APPGW_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={
                    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME: "test_appgw_name",
                    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID: "test_appgw_id",
                    CONST_INGRESS_APPGW_SUBNET_ID: "test_appgw_subnet_id",
                    CONST_INGRESS_APPGW_SUBNET_CIDR: "test_appgw_subnet_prefix",
                    CONST_INGRESS_APPGW_WATCH_NAMESPACE: "test_appgw_watch_namespace",
                },
            ),
            CONST_GITOPS_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
            ),
        }
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location", addon_profiles=addon_profiles_2
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)
        self.assertEqual(dec_2.context.get_intermediate("monitoring"), True)
        self.assertEqual(
            dec_2.context.get_intermediate("enable_virtual_node"), None
        )
        self.assertEqual(
            dec_2.context.get_intermediate("ingress_appgw_addon_enabled"), True
        )

    def test_set_up_windows_profile(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "windows_admin_username": None,
                "windows_admin_password": None,
                "enable_ahub": False,
                "enable_windows_gmsa": False,
                "gmsa_dns_server": None,
                "gmsa_root_domain_name": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_windows_profile(None)
        dec_mc_1 = dec_1.set_up_windows_profile(mc_1)

        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="fake secrets in unit test")]
                "windows_admin_username": "test_win_admin_name",
                "windows_admin_password": "test_win_admin_password",
                "enable_ahub": True,
                "enable_windows_gmsa": True,
                "gmsa_dns_server": "test_gmsa_dns_server",
                "gmsa_root_domain_name": "test_gmsa_root_domain_name",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_mc_2 = dec_2.set_up_windows_profile(mc_2)

        windows_gmsa_profile_2 = self.models.WindowsGmsaProfile(
            enabled=True,
            dns_server="test_gmsa_dns_server",
            root_domain_name="test_gmsa_root_domain_name",
        )
        windows_profile_2 = self.models.ManagedClusterWindowsProfile(
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="fake secrets in unit test")]
            admin_username="test_win_admin_name",
            admin_password="test_win_admin_password",
            license_type="Windows_Server",
            gmsa_profile=windows_gmsa_profile_2,
        )

        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location", windows_profile=windows_profile_2
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_construct_mc_preview_profile(self):
        import inspect

        import paramiko
        from azext_aks_preview.custom import aks_create

        optional_params = {}
        positional_params = []
        for _, v in inspect.signature(aks_create).parameters.items():
            if v.default != v.empty:
                optional_params[v.name] = v.default
            else:
                positional_params.append(v.name)
        ground_truth_positional_params = [
            "cmd",
            "client",
            "resource_group_name",
            "name",
            "ssh_key_value",
        ]
        self.assertEqual(positional_params, ground_truth_positional_params)

        # prepare ssh key
        key = paramiko.RSAKey.generate(2048)
        public_key = "{} {}".format(key.get_name(), key.get_base64())

        # prepare a dictionary of default parameters
        raw_param_dict = {
            "resource_group_name": "test_rg_name",
            "name": "test_name",
            "ssh_key_value": public_key,
        }
        raw_param_dict.update(optional_params)
        from azure.cli.command_modules.acs.decorator import AKSParamDict

        raw_param_dict = AKSParamDict(raw_param_dict)

        # default value in `aks_create`
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd, self.client, raw_param_dict, CUSTOM_MGMT_AKS_PREVIEW
        )

        mock_profile = Mock(
            get_subscription_id=Mock(return_value="1234-5678-9012")
        )
        with patch(
            "azure.cli.command_modules.acs.decorator.get_rg_location",
            return_value="test_location",
        ), patch(
            "azure.cli.command_modules.acs.decorator.Profile",
            return_value=mock_profile,
        ):
            dec_mc_1 = dec_1.construct_mc_preview_profile()

        agent_pool_profile_1 = self.models.ManagedClusterAgentPoolProfile(
            # Must be 12 chars or less before ACS RP adds to it
            name="nodepool1",
            # tags=None,
            # node_labels=None,
            count=3,
            vm_size="Standard_DS2_v2",
            os_type="Linux",
            enable_node_public_ip=False,
            enable_encryption_at_host=False,
            enable_ultra_ssd=False,
            type="VirtualMachineScaleSets",
            mode="System",
            enable_auto_scaling=False,
            enable_fips=False,
        )
        ssh_config_1 = self.models.ContainerServiceSshConfiguration(
            public_keys=[
                self.models.ContainerServiceSshPublicKey(key_data=public_key)
            ]
        )
        linux_profile_1 = self.models.ContainerServiceLinuxProfile(
            admin_username="azureuser", ssh=ssh_config_1
        )
        network_profile_1 = self.models.ContainerServiceNetworkProfile(
            load_balancer_sku="standard",
        )
        identity_1 = self.models.ManagedClusterIdentity(type="SystemAssigned")
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            dns_prefix="testname-testrgname-1234-5",
            kubernetes_version="",
            addon_profiles={},
            enable_rbac=True,
            agent_pool_profiles=[agent_pool_profile_1],
            linux_profile=linux_profile_1,
            network_profile=network_profile_1,
            identity=identity_1,
            disable_local_accounts=False,
            enable_pod_security_policy=False,
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)
        raw_param_dict.print_usage_statistics()

    def test_create_mc_preview(self):
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            addon_profiles={
                CONST_MONITORING_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                    enabled=True,
                    config={
                        CONST_MONITORING_USING_AAD_MSI_AUTH: True,
                    },
                )
            },
        )
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {
                "resource_group_name": "test_rg_name",
                "name": "test_name",
                "enable_managed_identity": True,
                "no_wait": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        dec_1.context.attach_mc(mc_1)
        dec_1.context.set_intermediate(
            "monitoring", True, overwrite_exists=True
        )
        dec_1.context.set_intermediate(
            "subscription_id", "test_subscription_id", overwrite_exists=True
        )
        resp = requests.Response()
        resp.status_code = 500
        err = CloudError(resp)
        err.message = "not found in Active Directory tenant"
        # fail on mock CloudError
        with self.assertRaises(CloudError), patch("time.sleep"), patch(
            "azure.cli.command_modules.acs.decorator.AKSCreateDecorator.create_mc"
        ), patch(
            "azext_aks_preview.decorator.ensure_container_insights_for_monitoring",
            side_effect=err,
        ) as ensure_monitoring:
            dec_1.create_mc_preview(mc_1)
        ensure_monitoring.assert_called_with(
            self.cmd,
            mc_1.addon_profiles[CONST_MONITORING_ADDON_NAME],
            "test_subscription_id",
            "test_rg_name",
            "test_name",
            "test_location",
            remove_monitoring=False,
            aad_route=True,
            create_dcr=False,
            create_dcra=True,
        )


class AKSPreviewUpdateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()

    def test_update_load_balancer_profile(self):
        # default value in `aks_update`
        dec_1 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_sku": None,
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
                "load_balancer_outbound_ports": None,
                "load_balancer_idle_timeout": None,
                "load_balancer_managed_outbound_ipv6_count": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.update_load_balancer_profile(None)

        network_profile_1 = self.models.ContainerServiceNetworkProfile()
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_1,
        )
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.update_load_balancer_profile(mc_1)

        ground_truth_network_profile_1 = (
            self.models.ContainerServiceNetworkProfile()
        )
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=ground_truth_network_profile_1,
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ipv6_count": 4,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    "ManagedClusterLoadBalancerProfile"
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=3,
                        count_ipv6=7,
                    )
                )
            ),
        )
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.update_load_balancer_profile(mc_2)
        self.assertEqual(
            dec_mc_2.network_profile.load_balancer_profile.managed_outbound_i_ps.count,
            3,
        )
        self.assertEqual(
            dec_mc_2.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6,
            4,
        )

    def test_update_outbound_ip_prefixes(self):
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    outbound_ip_prefixes=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileOutboundIPPrefixes"
                    )(
                        public_ip_prefixes=["id1", "id2"],
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_1)
        dec_1 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_outbound_ip_prefixes": "id3,id4",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_1.fetch_mc()
        mc = dec_1.update_load_balancer_profile(mc)
        self.assertListEqual(
            [pip.id for pip in mc.network_profile.load_balancer_profile.outbound_ip_prefixes.public_ip_prefixes], ["id3", "id4"])
        self.assertIsNone(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps)
        self.assertIsNone(
            mc.network_profile.load_balancer_profile.outbound_i_ps)

    def test_update_outbound_ips(self):
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileOutboundIPs"
                    )(
                        public_i_ps=["id1", "id2"],
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_1)
        dec_1 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_outbound_ips": "id3,id4",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_1.fetch_mc()
        mc = dec_1.update_load_balancer_profile(mc)
        self.assertListEqual(
            [pip.id for pip in mc.network_profile.load_balancer_profile.outbound_i_ps.public_i_ps], ["id3", "id4"])
        self.assertIsNone(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps)
        self.assertIsNone(
            mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

    def test_update_ipv6_count(self):
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=3,
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_1)
        dec_1 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_managed_outbound_ip_count": 7,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_1.fetch_mc()
        mc = dec_1.update_load_balancer_profile(mc)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count, 7)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6, 0)
        self.assertIsNone(
            mc.network_profile.load_balancer_profile.outbound_i_ps)
        self.assertIsNone(
            mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

        # test 2
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=3,
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_2)
        dec_2 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_managed_outbound_ip_count": 2,
                "load_balancer_managed_outbound_ipv6_count": 4,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_2.fetch_mc()
        mc = dec_2.update_load_balancer_profile(mc)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count, 2)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6, 4)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_i_ps)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

        # test 3 update only count_ipv6, count should remain the same
        mc_3 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=5,
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_3)
        dec_3 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_managed_outbound_ipv6_count": 12,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_3.fetch_mc()
        mc = dec_3.update_load_balancer_profile(mc)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count, 5)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6, 12)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_i_ps)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

        # test 4 - existing dual-stack, update count only
        mc_4 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=3,
                        count_ipv6=2
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_4)

        dec_4 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_managed_outbound_ip_count": 8,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_4.fetch_mc()
        mc = dec_4.update_load_balancer_profile(mc)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count, 8)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6, 2)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_i_ps)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

        # test 5 - dual-stack mc update count_ipv6 only
        mc_5 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=3,
                        count_ipv6=2
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_5)

        dec_5 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_managed_outbound_ipv6_count": 5,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_5.fetch_mc()
        mc = dec_5.update_load_balancer_profile(mc)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count, 3)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6, 5)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_i_ps)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

        # test 6 - dual-stack mc update count and count_ipv6
        mc_6 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=3,
                        count_ipv6=2
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_6)

        dec_6 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_managed_outbound_ipv6_count": 5,
                "load_balancer_managed_outbound_ip_count": 7,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_6.fetch_mc()
        mc = dec_6.update_load_balancer_profile(mc)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count, 7)
        self.assertEquals(
            mc.network_profile.load_balancer_profile.managed_outbound_i_ps.count_ipv6, 5)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_i_ps)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

        # test 7 - dual-stack mc update to outbound_ips from managed
        mc_7 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.lb_models.get(
                    'ManagedClusterLoadBalancerProfile'
                )(
                    managed_outbound_i_ps=self.models.lb_models.get(
                        "ManagedClusterLoadBalancerProfileManagedOutboundIPs"
                    )(
                        count=3,
                        count_ipv6=2
                    )
                )
            )
        )
        self.client.get = Mock(return_value=mc_7)

        dec_7 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "name": "test_cluster",
                "resource_group_name": "test_rg_name",
                "load_balancer_outbound_ips": "id1,id2",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc = dec_7.fetch_mc()
        mc = dec_7.update_load_balancer_profile(mc)
        self.assertIsNone(mc.network_profile.load_balancer_profile.managed_outbound_i_ps)
        self.assertIsNotNone(mc.network_profile.load_balancer_profile.outbound_i_ps)
        self.assertIsNone(mc.network_profile.load_balancer_profile.outbound_ip_prefixes)

    def test_update_pod_security_policy(self):
        # default value in `aks_update`
        dec_1 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_security_policy": False,
                "disable_pod_security_policy": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.update_pod_security_policy(None)

        mc_1 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.update_pod_security_policy(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_security_policy": True,
                "disable_pod_security_policy": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=False,
        )
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.update_pod_security_policy(mc_2)
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

        # custom value
        dec_3 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_security_policy": False,
                "disable_pod_security_policy": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_3 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        dec_3.context.attach_mc(mc_3)
        dec_mc_3 = dec_3.update_pod_security_policy(mc_3)
        ground_truth_mc_3 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=False,
        )
        self.assertEqual(dec_mc_3, ground_truth_mc_3)

    def test_update_windows_profile(self):
        # default value in `aks_update`
        dec_1 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_ahub": False,
                "disable_ahub": False,
                "windows_admin_password": None,
                "enable_windows_gmsa": False,
                "gmsa_dns_server": None,
                "gmsa_root_domain_name": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.update_windows_profile(None)

        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.update_windows_profile(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_windows_gmsa": True,
                "gmsa_dns_server": "test_gmsa_dns_server",
                "gmsa_root_domain_name": "test_gmsa_root_domain_name",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        windows_profile_2 = self.models.ManagedClusterWindowsProfile(
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="fake secrets in unit test")]
            admin_username="test_win_admin_name",
            admin_password="test_win_admin_password",
            license_type="Windows_Server",
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            windows_profile=windows_profile_2,
        )
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.update_windows_profile(mc_2)

        ground_truth_gmsa_profile_2 = self.models.WindowsGmsaProfile(
            enabled=True,
            dns_server="test_gmsa_dns_server",
            root_domain_name="test_gmsa_root_domain_name",
        )
        ground_truth_windows_profile_2 = self.models.ManagedClusterWindowsProfile(
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="fake secrets in unit test")]
            admin_username="test_win_admin_name",
            admin_password="test_win_admin_password",
            license_type="Windows_Server",
            gmsa_profile=ground_truth_gmsa_profile_2,
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            windows_profile=ground_truth_windows_profile_2,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

        # custom value
        dec_3 = AKSPreviewUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_windows_gmsa": True,
                "gmsa_dns_server": "test_gmsa_dns_server",
                "gmsa_root_domain_name": "test_gmsa_root_domain_name",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_3 = self.models.ManagedCluster(
            location="test_location",
        )
        dec_3.context.attach_mc(mc_3)
        # fail on incomplete mc object (no windows profile)
        with self.assertRaises(UnknownError):
            dec_3.update_windows_profile(mc_3)
