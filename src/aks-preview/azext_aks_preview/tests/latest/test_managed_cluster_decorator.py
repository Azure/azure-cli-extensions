# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
import unittest
from unittest.mock import Mock, patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._consts import (
    ADDONS,
    CONST_ACC_SGX_QUOTE_HELPER_ENABLED,
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
    CONST_AZURE_POLICY_ADDON_NAME,
    CONST_CONFCOM_ADDON_NAME,
    CONST_DEFAULT_NODE_OS_TYPE,
    CONST_DEFAULT_NODE_VM_SIZE,
    CONST_DISK_DRIVER_V2,
    CONST_GITOPS_ADDON_NAME,
    CONST_HTTP_APPLICATION_ROUTING_ADDON_NAME,
    CONST_INGRESS_APPGW_ADDON_NAME,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_ID,
    CONST_INGRESS_APPGW_APPLICATION_GATEWAY_NAME,
    CONST_INGRESS_APPGW_SUBNET_CIDR,
    CONST_INGRESS_APPGW_SUBNET_ID,
    CONST_INGRESS_APPGW_WATCH_NAMESPACE,
    CONST_KUBE_DASHBOARD_ADDON_NAME,
    CONST_LOAD_BALANCER_SKU_STANDARD,
    CONST_MONITORING_ADDON_NAME,
    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID,
    CONST_MONITORING_USING_AAD_MSI_AUTH,
    CONST_NODEPOOL_MODE_SYSTEM,
    CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    CONST_ROTATION_POLL_INTERVAL,
    CONST_SECRET_ROTATION_ENABLED,
    CONST_VIRTUAL_MACHINE_SCALE_SETS,
    CONST_VIRTUAL_NODE_ADDON_NAME,
    CONST_VIRTUAL_NODE_SUBNET_NAME,
    CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
)
from azext_aks_preview.agentpool_decorator import AKSPreviewAgentPoolContext
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterContext,
    AKSPreviewManagedClusterCreateDecorator,
    AKSPreviewManagedClusterModels,
    AKSPreviewManagedClusterUpdateDecorator,
)
from azext_aks_preview.tests.latest.utils import get_test_data_file_path
from azure.cli.command_modules.acs._consts import (
    AgentPoolDecoratorMode,
    DecoratorEarlyExitException,
    DecoratorMode,
)
from azure.cli.command_modules.acs.managed_cluster_decorator import (
    AKSManagedClusterParamDict,
)
from azure.cli.command_modules.acs.tests.latest.mocks import (
    MockCLI,
    MockClient,
    MockCmd,
)
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
    UnknownError,
)


class AKSPreviewManagedClusterModelsTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)

    def test_models(self):
        models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)

        # load models directly (instead of through the `get_sdk` method provided by the cli component)
        from azure.cli.core.profiles._shared import AZURE_API_PROFILES

        sdk_profile = AZURE_API_PROFILES["latest"][CUSTOM_MGMT_AKS_PREVIEW]
        api_version = sdk_profile.default_api_version
        module_name = "azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.v{}.models".format(
            api_version.replace("-", "_")
        )
        module = importlib.import_module(module_name)

        # pod identity models
        self.assertEqual(
            models.pod_identity_models.ManagedClusterPodIdentityProfile,
            getattr(module, "ManagedClusterPodIdentityProfile"),
        )
        self.assertEqual(
            models.pod_identity_models.ManagedClusterPodIdentityException,
            getattr(module, "ManagedClusterPodIdentityException"),
        )


class AKSPreviewManagedClusterContextTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)

    def create_attach_agentpool_context(self, ctx: AKSPreviewManagedClusterContext, **kwargs):
        """Helper function to create an AKSPreviewAgentPoolContext based on AKSPreviewManagedClusterContext and
        attach it to the given context.

        :return: the AgentPool object
        """
        agentpool_ctx = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSManagedClusterParamDict(ctx.raw_param._BaseAKSParamDict__store),
            self.models,
            ctx.decorator_mode,
            AgentPoolDecoratorMode.MANAGED_CLUSTER,
        )
        ctx.attach_agentpool_context(agentpool_ctx)
        return agentpool_ctx

    def test_validate_pod_identity_with_kubenet(self):
        # custom value
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        network_profile_1 = self.models.ContainerServiceNetworkProfile(network_plugin="kubenet")
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_1,
        )
        # fail on enable_pod_identity_with_kubenet not specified
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_1._AKSPreviewManagedClusterContext__validate_pod_identity_with_kubenet(mc_1, True, False)

    def test_get_addon_consts(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
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
            "CONST_MONITORING_USING_AAD_MSI_AUTH": CONST_MONITORING_USING_AAD_MSI_AUTH,
            "CONST_OPEN_SERVICE_MESH_ADDON_NAME": CONST_OPEN_SERVICE_MESH_ADDON_NAME,
            "CONST_VIRTUAL_NODE_ADDON_NAME": CONST_VIRTUAL_NODE_ADDON_NAME,
            "CONST_VIRTUAL_NODE_SUBNET_NAME": CONST_VIRTUAL_NODE_SUBNET_NAME,
            "CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME": CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
            "CONST_SECRET_ROTATION_ENABLED": CONST_SECRET_ROTATION_ENABLED,
            "CONST_ROTATION_POLL_INTERVAL": CONST_ROTATION_POLL_INTERVAL,
            # new addon consts in aks-preview
            "CONST_GITOPS_ADDON_NAME": CONST_GITOPS_ADDON_NAME,
        }
        self.assertEqual(addon_consts, ground_truth_addon_consts)

    def test_get_http_proxy_config(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"http_proxy_config": None}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_http_proxy_config(), None)
        mc = self.models.ManagedCluster(
            location="test_location",
            http_proxy_config=self.models.ManagedClusterHTTPProxyConfig(http_proxy="test_http_proxy"),
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_http_proxy_config(),
            self.models.ManagedClusterHTTPProxyConfig(http_proxy="test_http_proxy"),
        )

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"http_proxy_config": "fake-path"}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_2.get_http_proxy_config()

        # custom value
        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"http_proxy_config": get_test_data_file_path("invalidconfig.json")}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_3.get_http_proxy_config()

    def test_get_pod_cidrs(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"pod_cidrs": None}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_pod_cidrs(), None)
        mc = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(pod_cidrs="test_pod_cidrs"),
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_pod_cidrs(),
            "test_pod_cidrs",
        )

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"pod_cidrs": ""}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_pod_cidrs(), [])

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"pod_cidrs": "10.244.0.0/16,2001:abcd::/64"}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_pod_cidrs(), ["10.244.0.0/16", "2001:abcd::/64"])

    def test_get_service_cidrs(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"service_cidrs": None}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_service_cidrs(), None)
        mc = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(service_cidrs="test_service_cidrs"),
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_service_cidrs(),
            "test_service_cidrs",
        )

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"service_cidrs": ""}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_service_cidrs(), [])

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"service_cidrs": "10.244.0.0/16,2001:abcd::/64"}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_service_cidrs(), ["10.244.0.0/16", "2001:abcd::/64"])

    def test_get_ip_families(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"ip_families": None}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_ip_families(), None)
        mc = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(ip_families="test_ip_families"),
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(
            ctx_1.get_ip_families(),
            "test_ip_families",
        )

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"ip_families": ""}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_ip_families(), [])

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"ip_families": "IPv4,IPv6"}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_ip_families(), ["IPv4", "IPv6"])

    def test_get_load_balancer_managed_outbound_ip_count(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "load_balancer_managed_outbound_ip_count": None,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_load_balancer_managed_outbound_ip_count(), None)
        load_balancer_profile = self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
            managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                count=10
            )
        )
        network_profile = self.models.ContainerServiceNetworkProfile(load_balancer_profile=load_balancer_profile)
        mc = self.models.ManagedCluster(location="test_location", network_profile=network_profile)
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_load_balancer_managed_outbound_ip_count(), 10)

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "load_balancer_managed_outbound_ip_count": None,
                    "load_balancer_outbound_ips": None,
                    "load_balancer_outbound_ip_prefixes": None,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        load_balancer_profile_2 = self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
            managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                count=10, count_ipv6=20
            ),
            outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPs(
                public_i_ps=[self.models.load_balancer_models.ResourceReference(id="test_public_ip")]
            ),
            outbound_ip_prefixes=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                public_ip_prefixes=[self.models.load_balancer_models.ResourceReference(id="test_public_ip_prefix")]
            ),
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(load_balancer_profile=load_balancer_profile_2)
        mc_2 = self.models.ManagedCluster(location="test_location", network_profile=network_profile_2)
        ctx_2.attach_mc(mc_2)
        self.assertEqual(ctx_2.get_load_balancer_managed_outbound_ip_count(), 10)

    def test_get_load_balancer_managed_outbound_ipv6_count(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "load_balancer_managed_outbound_ipv6_count": None,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_load_balancer_managed_outbound_ipv6_count(), None)
        load_balancer_profile = self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
            managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                count_ipv6=10
            )
        )
        network_profile = self.models.ContainerServiceNetworkProfile(load_balancer_profile=load_balancer_profile)
        mc = self.models.ManagedCluster(location="test_location", network_profile=network_profile)
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_load_balancer_managed_outbound_ipv6_count(), 10)

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"load_balancer_managed_outbound_ipv6_count": 0}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_load_balancer_managed_outbound_ipv6_count(), 0)

        # custom value
        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "load_balancer_managed_outbound_ipv6_count": None,
                    "load_balancer_outbound_ips": None,
                    "load_balancer_outbound_ip_prefixes": None,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        load_balancer_profile_3 = self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
            managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                count=10, count_ipv6=20
            ),
            outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPs(
                public_i_ps=[self.models.load_balancer_models.ResourceReference(id="test_public_ip")]
            ),
            outbound_ip_prefixes=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                public_ip_prefixes=[self.models.load_balancer_models.ResourceReference(id="test_public_ip_prefix")]
            ),
        )
        network_profile_3 = self.models.ContainerServiceNetworkProfile(load_balancer_profile=load_balancer_profile_3)
        mc_3 = self.models.ManagedCluster(location="test_location", network_profile=network_profile_3)
        ctx_3.attach_mc(mc_3)
        self.assertEqual(ctx_3.get_load_balancer_managed_outbound_ipv6_count(), 20)

    def test_get_enable_pod_security_policy(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_pod_security_policy": False}),
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
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_pod_security_policy": True,
                    "disable_pod_security_policy": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_pod_security_policy and disable_pod_security_policy
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_2.get_enable_pod_security_policy()

    def test_get_disable_pod_security_policy(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"disable_pod_security_policy": False}),
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
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_pod_security_policy": True,
                    "disable_pod_security_policy": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_pod_security_policy and disable_pod_security_policy
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_2.get_disable_pod_security_policy()

    def test_mc_get_network_plugin_mode(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "network_plugin_mode": "overlay",
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_network_plugin_mode(), "overlay")

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "network_plugin_mode": None,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_network_plugin_mode(), None)

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "network_plugin_mode": "",
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_network_plugin_mode(), "")

    def test_get_enable_managed_identity(self):
        # custom value
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_managed_identity": False, "enable_pod_identity": True}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        # fail on enable_managed_identity not specified
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_1.get_enable_managed_identity(), False)

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_pod_identity": True}),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
        )
        ctx_2.attach_mc(mc_2)
        # fail on managed identity not enabled
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_2.get_enable_managed_identity(), False)

    def test_get_enable_pod_identity(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_pod_identity": False}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_pod_identity(), False)
        pod_identity_profile = self.models.pod_identity_models.ManagedClusterPodIdentityProfile(enabled=True)
        mc = self.models.ManagedCluster(
            location="test_location",
            pod_identity_profile=pod_identity_profile,
        )
        ctx_1.attach_mc(mc)
        # fail on enable_managed_identity not specified
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_1.get_enable_pod_identity(), True)

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_managed_identity": True,
                    "enable_pod_identity": True,
                    "enable_pod_identity_with_kubenet": False,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(network_plugin="kubenet")
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_2,
        )
        ctx_2.attach_mc(mc_2)
        # fail on enable_pod_identity_with_kubenet not specified
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_2.get_enable_pod_identity(), True)

        # custom value
        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_pod_identity": True,
                    "disable_pod_identity": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        mc_3 = self.models.ManagedCluster(
            location="test_location",
            identity=self.models.ManagedClusterIdentity(type="SystemAssigned"),
        )
        ctx_3.attach_mc(mc_3)
        # fail on mutually exclusive enable_pod_identity and disable_pod_identity
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_3.get_enable_pod_identity()

        # custom value
        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_pod_identity": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        mc_4 = self.models.ManagedCluster(location="test_location")
        ctx_4.attach_mc(mc_4)
        # fail on managed identity not enabled
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_4.get_enable_pod_identity()

    def test_get_disable_pod_identity(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"disable_pod_identity": False}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_disable_pod_identity(), False)

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_pod_identity": True,
                    "disable_pod_identity": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_pod_identity and disable_pod_identity
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_2.get_disable_pod_identity()

    def test_get_enable_pod_identity_with_kubenet(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_pod_identity_with_kubenet": False}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_pod_identity_with_kubenet(), False)
        pod_identity_profile = self.models.pod_identity_models.ManagedClusterPodIdentityProfile(
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
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_managed_identity": True,
                    "enable_pod_identity": True,
                    "enable_pod_identity_with_kubenet": False,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(network_plugin="kubenet")
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_2,
        )
        ctx_2.attach_mc(mc_2)
        # fail on enable_pod_identity_with_kubenet not specified
        with self.assertRaises(RequiredArgumentMissingError):
            self.assertEqual(ctx_2.get_enable_pod_identity_with_kubenet(), False)

    def test_get_oidc_issuer_profile__create_not_set(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd, AKSManagedClusterParamDict({}), self.models, decorator_mode=DecoratorMode.CREATE
        )
        self.assertIsNone(ctx.get_oidc_issuer_profile())

    def test_get_oidc_issuer_profile__create_enable(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_oidc_issuer": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        profile = ctx.get_oidc_issuer_profile()
        self.assertIsNotNone(profile)
        self.assertTrue(profile.enabled)

    def test_get_oidc_issuer_profile__update_not_set(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd, AKSManagedClusterParamDict({}), self.models, decorator_mode=DecoratorMode.UPDATE
        )
        ctx.attach_mc(self.models.ManagedCluster(location="test_location"))
        self.assertIsNone(ctx.get_oidc_issuer_profile())

    def test_get_oidc_issuer_profile__update_not_set_with_previous_profile(
        self,
    ):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd, AKSManagedClusterParamDict({}), self.models, decorator_mode=DecoratorMode.UPDATE
        )
        mc = self.models.ManagedCluster(location="test_location")
        mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
        ctx.attach_mc(self.models.ManagedCluster(location="test_location"))
        self.assertIsNone(ctx.get_oidc_issuer_profile())

    def test_get_oidc_issuer_profile__update_enable_with_previous_profile(
        self,
    ):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_oidc_issuer": True}),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        mc = self.models.ManagedCluster(location="test_location")
        mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=False)
        ctx.attach_mc(mc)
        profile = ctx.get_oidc_issuer_profile()
        self.assertIsNotNone(profile)
        self.assertTrue(profile.enabled)

    def test_get_oidc_issuer_profile__update_enable(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_oidc_issuer": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        ctx.attach_mc(self.models.ManagedCluster(location="test_location"))
        profile = ctx.get_oidc_issuer_profile()
        self.assertIsNotNone(profile)
        self.assertTrue(profile.enabled)

    def test_get_workload_identity_profile__create_no_set(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd, AKSManagedClusterParamDict({}), self.models, decorator_mode=DecoratorMode.CREATE
        )
        self.assertIsNone(ctx.get_workload_identity_profile())

    def test_get_workload_identity_profile__create_enable_without_oidc_issuer(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_workload_identity": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx.get_workload_identity_profile()

    def test_get_workload_identity_profile__create_enable_with_oidc_issuer(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_oidc_issuer": True,
                    "enable_workload_identity": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        profile = ctx.get_workload_identity_profile()
        self.assertTrue(profile.enabled)

    def test_get_workload_identity_profile__update_not_set(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd, AKSManagedClusterParamDict({}), self.models, decorator_mode=DecoratorMode.UPDATE
        )
        ctx.attach_mc(self.models.ManagedCluster(location="test_location"))
        self.assertIsNone(ctx.get_workload_identity_profile())

    def test_get_workload_identity_profile__update_with_enable_without_oidc_issuer(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_workload_identity": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        ctx.attach_mc(self.models.ManagedCluster(location="test_location"))
        with self.assertRaises(RequiredArgumentMissingError):
            ctx.get_workload_identity_profile()

    def test_get_workload_identity_profile__update_with_enable(self):
        for previous_enablement_status in [
            None,  # preivous not set
            True,  # previous set to enabled=true
            False,  # previous set to enabled=false
        ]:
            ctx = AKSPreviewManagedClusterContext(
                self.cmd,
                AKSManagedClusterParamDict(
                    {
                        "enable_workload_identity": True,
                    }
                ),
                self.models,
                decorator_mode=DecoratorMode.UPDATE,
            )
            mc = self.models.ManagedCluster(location="test_location")
            mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
            if previous_enablement_status is None:
                mc.security_profile = None
            else:
                mc.security_profile = self.models.ManagedClusterSecurityProfile(
                    workload_identity=self.models.ManagedClusterSecurityProfileWorkloadIdentity(
                        enabled=previous_enablement_status
                    )
                )
            ctx.attach_mc(mc)
            profile = ctx.get_workload_identity_profile()
            self.assertTrue(profile.enabled)

    def test_get_workload_identity_profile__update_with_disable(self):
        for previous_enablement_status in [
            None,  # preivous not set
            True,  # previous set to enabled=true
            False,  # previous set to enabled=false
        ]:
            ctx = AKSPreviewManagedClusterContext(
                self.cmd,
                AKSManagedClusterParamDict(
                    {
                        "enable_workload_identity": False,
                    }
                ),
                self.models,
                decorator_mode=DecoratorMode.UPDATE,
            )
            mc = self.models.ManagedCluster(location="test_location")
            mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
            if previous_enablement_status is None:
                mc.security_profile = None
            else:
                mc.security_profile = self.models.ManagedClusterSecurityProfile(
                    workload_identity=self.models.ManagedClusterSecurityProfileWorkloadIdentity(
                        enabled=previous_enablement_status
                    )
                )
            ctx.attach_mc(mc)
            profile = ctx.get_workload_identity_profile()
            self.assertFalse(profile.enabled)

    def test_get_enable_azure_keyvault_kms(self):
        ctx_0 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertIsNone(ctx_0.get_enable_azure_keyvault_kms())

        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": False,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_azure_keyvault_kms(), False)

        key_id_1 = "https://fakekeyvault.vault.azure.net/secrets/fakekeyname/fakekeyversion"
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": False,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        security_profile = self.models.ManagedClusterSecurityProfile()
        security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_1,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile,
        )
        ctx_2.attach_mc(mc)
        self.assertEqual(ctx_2.get_enable_azure_keyvault_kms(), True)

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": False,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        security_profile = self.models.ManagedClusterSecurityProfile()
        security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_1,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile,
        )
        ctx_3.attach_mc(mc)
        self.assertEqual(ctx_3.get_enable_azure_keyvault_kms(), False)

        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_4.get_enable_azure_keyvault_kms()

        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "azure_keyvault_kms_key_id": "test_azure_keyvault_kms_key_id",
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_5.get_enable_azure_keyvault_kms()

    def test_get_azure_keyvault_kms_key_id(self):
        ctx_0 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertIsNone(ctx_0.get_azure_keyvault_kms_key_id())

        key_id_1 = "https://fakekeyvault.vault.azure.net/secrets/fakekeyname/fakekeyversion"
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": True,
                    "azure_keyvault_kms_key_id": key_id_1,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_azure_keyvault_kms_key_id(), key_id_1)

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": True,
                    "azure_keyvault_kms_key_id": key_id_1,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        key_id_2 = "https://fakekeyvault2.vault.azure.net/secrets/fakekeyname2/fakekeyversion2"
        security_profile = self.models.ManagedClusterSecurityProfile()
        security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_2,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile,
        )
        ctx_2.attach_mc(mc)
        self.assertEqual(ctx_2.get_azure_keyvault_kms_key_id(), key_id_2)

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": True,
                    "azure_keyvault_kms_key_id": key_id_1,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        security_profile = self.models.ManagedClusterSecurityProfile()
        security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_2,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile,
        )
        ctx_3.attach_mc(mc)
        self.assertEqual(ctx_3.get_azure_keyvault_kms_key_id(), key_id_1)

        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "azure_keyvault_kms_key_id": key_id_1,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_4.get_azure_keyvault_kms_key_id()

        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_azure_keyvault_kms": False,
                    "azure_keyvault_kms_key_id": key_id_1,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_5.get_azure_keyvault_kms_key_id()

    def test_get_azure_keyvault_kms_key_vault_network_access(self):
        key_vault_network_access_1 = "Public"
        key_vault_network_access_2 = "Private"

        ctx_0 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertIsNone(ctx_0.get_azure_keyvault_kms_key_vault_network_access())

        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": key_vault_network_access_1,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_azure_keyvault_kms_key_vault_network_access(), key_vault_network_access_1)

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": key_vault_network_access_2,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        security_profile = self.models.ManagedClusterSecurityProfile()
        security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_vault_network_access=key_vault_network_access_1,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile,
        )
        ctx_2.attach_mc(mc)
        self.assertEqual(ctx_2.get_azure_keyvault_kms_key_vault_network_access(), key_vault_network_access_2)

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "azure_keyvault_kms_key_vault_network_access": key_vault_network_access_2,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_3.get_azure_keyvault_kms_key_vault_network_access()

        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": False,
                "azure_keyvault_kms_key_vault_network_access": key_vault_network_access_2,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_4.get_azure_keyvault_kms_key_vault_network_access()

        # update scenario, backfill to default
        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        security_profile_5 = self.models.ManagedClusterSecurityProfile()
        mc_5 = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile_5,
        )
        ctx_5.attach_mc(mc_5)
        self.assertEqual(ctx_5.get_azure_keyvault_kms_key_vault_network_access(), key_vault_network_access_1)

        # update scenario, backfill from existing mc
        ctx_6 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        security_profile_6 = self.models.ManagedClusterSecurityProfile()
        security_profile_6.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_vault_network_access=key_vault_network_access_2,
        )
        mc_6 = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile_6,
        )
        ctx_6.attach_mc(mc_6)
        self.assertEqual(ctx_6.get_azure_keyvault_kms_key_vault_network_access(), key_vault_network_access_2)

    def test_get_azure_keyvault_kms_key_vault_resource_id(self):
        key_vault_resource_id_1 = "/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo"
        key_vault_resource_id_2 = "/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/bar/providers/Microsoft.KeyVault/vaults/bar"

        ctx_0 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertIsNone(ctx_0.get_azure_keyvault_kms_key_vault_resource_id())

        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": "Public",
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_azure_keyvault_kms_key_vault_resource_id(), None)

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": "Public",
                "azure_keyvault_kms_key_vault_resource_id": "",
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_2.get_azure_keyvault_kms_key_vault_resource_id(), "")

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": "Private",
                "azure_keyvault_kms_key_vault_resource_id": key_vault_resource_id_1,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_azure_keyvault_kms_key_vault_resource_id(), key_vault_resource_id_1)

        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": "Private",
                "azure_keyvault_kms_key_vault_resource_id": key_vault_resource_id_1,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        security_profile = self.models.ManagedClusterSecurityProfile()
        security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_vault_network_access="Private",
            key_vault_resource_id=key_vault_resource_id_2,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile,
        )
        ctx_4.attach_mc(mc)
        self.assertEqual(ctx_4.get_azure_keyvault_kms_key_vault_resource_id(), key_vault_resource_id_2)

        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": "Private",
                "azure_keyvault_kms_key_vault_resource_id": key_vault_resource_id_2,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        security_profile = self.models.ManagedClusterSecurityProfile()
        security_profile.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_vault_network_access="Private",
            key_vault_resource_id=key_vault_resource_id_1,
        )
        mc = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile,
        )
        ctx_5.attach_mc(mc)
        self.assertEqual(ctx_5.get_azure_keyvault_kms_key_vault_resource_id(), key_vault_resource_id_2)

        ctx_6 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "azure_keyvault_kms_key_vault_resource_id": key_vault_resource_id_1,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_6.get_azure_keyvault_kms_key_vault_resource_id()

        ctx_7 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": False,
                "azure_keyvault_kms_key_vault_resource_id": key_vault_resource_id_1,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_7.get_azure_keyvault_kms_key_vault_resource_id()

        ctx_8 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": "Public",
                "azure_keyvault_kms_key_vault_resource_id": key_vault_resource_id_1,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(ArgumentUsageError):
            ctx_8.get_azure_keyvault_kms_key_vault_resource_id()

        ctx_9 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_vault_network_access": "Private",
                "azure_keyvault_kms_key_vault_resource_id": "",
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(ArgumentUsageError):
            ctx_9.get_azure_keyvault_kms_key_vault_resource_id()

        # update scenario, backfill from existing mc
        ctx_10 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_azure_keyvault_kms": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        security_profile_10 = self.models.ManagedClusterSecurityProfile()
        security_profile_10.azure_key_vault_kms = self.models.AzureKeyVaultKms(
            enabled=True,
            key_vault_network_access="Private",
            key_vault_resource_id=key_vault_resource_id_1,
        )
        mc_10 = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile_10,
        )
        ctx_10.attach_mc(mc_10)
        self.assertEqual(ctx_10.get_azure_keyvault_kms_key_vault_resource_id(), key_vault_resource_id_1)

    def test_get_cluster_snapshot_id(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "cluster_snapshot_id": None,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_cluster_snapshot_id(), None)
        creation_data = self.models.CreationData(source_resource_id="test_source_resource_id")
        agent_pool_profile = self.models.ManagedClusterAgentPoolProfile(name="test_nodepool_name")
        mc = self.models.ManagedCluster(
            location="test_location",
            agent_pool_profiles=[agent_pool_profile],
            creation_data=creation_data,
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_cluster_snapshot_id(), "test_source_resource_id")

    def test_get_cluster_snapshot(self):
        # custom value
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "cluster_snapshot_id": "test_source_resource_id",
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mock_snapshot = Mock()
        with patch(
            "azext_aks_preview.managed_cluster_decorator.get_cluster_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_1.get_cluster_snapshot(), mock_snapshot)
        # test cache
        self.assertEqual(ctx_1.get_cluster_snapshot(), mock_snapshot)

    def test_get_kubernetes_version(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"kubernetes_version": ""}),
            self.models,
            DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_1)
        self.assertEqual(ctx_1.get_kubernetes_version(), "")
        mc_1 = self.models.ManagedCluster(location="test_location", kubernetes_version="test_kubernetes_version")
        ctx_1.attach_mc(mc_1)
        self.assertEqual(ctx_1.get_kubernetes_version(), "test_kubernetes_version")

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"kubernetes_version": "", "snapshot_id": "test_snapshot_id"}),
            self.models,
            DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_2)
        mock_snapshot = Mock(kubernetes_version="test_kubernetes_version")
        with patch(
            "azext_aks_preview.agentpool_decorator.get_nodepool_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_2.get_kubernetes_version(), "test_kubernetes_version")

        # custom value
        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "kubernetes_version": "custom_kubernetes_version",
                    "snapshot_id": "test_snapshot_id",
                }
            ),
            self.models,
            DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_3)
        mock_snapshot = Mock(kubernetes_version="test_kubernetes_version")
        with patch(
            "azext_aks_preview.agentpool_decorator.get_nodepool_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_3.get_kubernetes_version(), "custom_kubernetes_version")

        # custom value
        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "kubernetes_version": "",
                    "snapshot_id": "test_snapshot_id",
                    "cluster_snapshot_id": "test_cluster_snapshot_id",
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_4)
        mock_snapshot = Mock(managed_cluster_properties_read_only=Mock(kubernetes_version="test_kubernetes_version"))
        mock_mc_snapshot = Mock(
            managed_cluster_properties_read_only=Mock(kubernetes_version="test_cluster_kubernetes_version")
        )
        with patch(
            "azext_aks_preview.agentpool_decorator.get_nodepool_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ), patch(
            "azext_aks_preview.managed_cluster_decorator.get_cluster_snapshot_by_snapshot_id",
            return_value=mock_mc_snapshot,
        ):
            self.assertEqual(ctx_4.get_kubernetes_version(), "test_cluster_kubernetes_version")

        # custom value
        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "kubernetes_version": "custom_kubernetes_version",
                    "snapshot_id": "test_snapshot_id",
                    "cluster_snapshot_id": "test_cluster_snapshot_id",
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_5)
        mock_snapshot = Mock(managed_cluster_properties_read_only=Mock(kubernetes_version="test_kubernetes_version"))
        mock_mc_snapshot = Mock(
            managed_cluster_properties_read_only=Mock(kubernetes_version="test_cluster_kubernetes_version")
        )
        with patch(
            "azext_aks_preview.agentpool_decorator.get_nodepool_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ), patch(
            "azext_aks_preview.managed_cluster_decorator.get_cluster_snapshot_by_snapshot_id",
            return_value=mock_mc_snapshot,
        ):
            self.assertEqual(ctx_5.get_kubernetes_version(), "custom_kubernetes_version")

    def test_get_disk_driver(self):
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_disk_driver": True,
                    "disable_disk_driver": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_disk_driver and disable_disk_driver
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_1.get_disk_driver()

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_disk_driver": True,
                    "disk_driver_version": "v2",
                    "disable_disk_driver": False,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        storage_profile_2 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(
                enabled=False,
                version=None,
            ),
            file_csi_driver=None,
            snapshot_controller=None,
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            storage_profile=storage_profile_2,
        )
        ctx_2.attach_mc(mc_2)
        ground_truth_disk_csi_driver_2 = (
            self.models.ManagedClusterStorageProfileDiskCSIDriver(
                enabled=True,
                version="v2",
            )
        )
        self.assertEqual(
            ctx_2.get_disk_driver(), ground_truth_disk_csi_driver_2
        )

        # fail with enable-disk-driver as false and value passed for disk_driver_version
        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_disk_driver": True,
                "disk_driver_version": "v2",
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )

        # fail on argument usage error
        with self.assertRaises(ArgumentUsageError):
            ctx_3.get_disk_driver()

        # fail with enable-disk-driver as false and value passed for disk_driver_version
        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disk_driver_version": "v2",
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on argument usage error
        with self.assertRaises(ArgumentUsageError):
            ctx_4.get_disk_driver()

        # fail on prompt_y_n not specified when disabling disk driver
        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_disk_driver": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        with patch(
            "azext_aks_preview.managed_cluster_decorator.prompt_y_n",
            return_value=False,
        ), self.assertRaises(DecoratorEarlyExitException):
            ctx_5.get_disk_driver()

        ctx_6 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_disk_driver": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ground_truth_disk_csi_driver_6 = (
            self.models.ManagedClusterStorageProfileDiskCSIDriver(
                enabled=False,
            )
        )
        self.assertEqual(
            ctx_6.get_disk_driver(), ground_truth_disk_csi_driver_6
        )

        ctx_7 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disk_driver_version": CONST_DISK_DRIVER_V2,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ground_truth_disk_csi_driver_7 = (
            self.models.ManagedClusterStorageProfileDiskCSIDriver(
                enabled=True,
                version=CONST_DISK_DRIVER_V2,
            )
        )
        self.assertEqual(
            ctx_7.get_disk_driver(), ground_truth_disk_csi_driver_7
        )

    def test_get_file_driver(self):
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_file_driver": True,
                    "disable_file_driver": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_file_driver and disable_file_driver
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_1.get_file_driver()

        # fail on prompt_y_n not specified when disabling file driver
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_file_driver": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        with patch(
            "azext_aks_preview.managed_cluster_decorator.prompt_y_n",
            return_value=False,
        ), self.assertRaises(DecoratorEarlyExitException):
            ctx_2.get_file_driver()

    def test_get_snapshot_controller(self):
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_snapshot_controller": True,
                    "disable_snapshot_controller": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_snapshot_controller and disable_snapshot_controller
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_1.get_snapshot_controller()

        # fail on prompt_y_n not specified when disabling snapshot controller
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_snapshot_controller": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        with patch(
            "azext_aks_preview.managed_cluster_decorator.prompt_y_n",
            return_value=False,
        ), self.assertRaises(DecoratorEarlyExitException):
            ctx_2.get_snapshot_controller()

    def test_get_blob_driver(self):
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_blob_driver": True,
                    "disable_blob_driver": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        # fail on mutually exclusive enable_blob_driver and disable_blob_driver
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_1.get_blob_driver()

        # fail on prompt_y_n not specified when disabling blob driver
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_blob_driver": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        with patch(
            "azext_aks_preview.managed_cluster_decorator.prompt_y_n",
            return_value=False,
        ), self.assertRaises(DecoratorEarlyExitException):
            ctx_2.get_blob_driver()

        # fail on prompt_y_n not specified when enabling blob driver
        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_blob_driver": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        with patch(
            "azext_aks_preview.managed_cluster_decorator.prompt_y_n",
            return_value=False,
        ), self.assertRaises(DecoratorEarlyExitException):
            ctx_3.get_blob_driver()

        # create with blob driver enabled
        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_blob_driver": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        ctx_4.attach_mc(mc_1)
        storage_profile_1 = self.models.ManagedClusterStorageProfile(
            blob_csi_driver=self.models.ManagedClusterStorageProfileBlobCSIDriver(
                enabled=True,
            ),
        )
        self.assertEqual(ctx_4.get_storage_profile(), storage_profile_1)

        # create without blob driver enabled
        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        ctx_5.attach_mc(mc_1)
        storage_profile_2 = self.models.ManagedClusterStorageProfile(
            blob_csi_driver=None,
        )
        self.assertEqual(ctx_5.get_storage_profile(), storage_profile_2)

        # update blob driver enabled
        ctx_6 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_blob_driver": True,
                "yes": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        ctx_6.attach_mc(mc_1)
        storage_profile_3 = self.models.ManagedClusterStorageProfile(
            blob_csi_driver=self.models.ManagedClusterStorageProfileBlobCSIDriver(
                enabled=True,
            ),
        )
        self.assertEqual(ctx_6.get_storage_profile(), storage_profile_3)

        # update blob driver disabled
        ctx_7 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_blob_driver": True,
                "yes": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        ctx_7.attach_mc(mc_1)
        storage_profile_4 = self.models.ManagedClusterStorageProfile(
            blob_csi_driver=self.models.ManagedClusterStorageProfileBlobCSIDriver(
                enabled=False,
            ),
        )
        self.assertEqual(ctx_7.get_storage_profile(), storage_profile_4)

    def test_get_storage_profile(self):
        # create
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "disable_disk_driver": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        ctx_1.attach_mc(mc_1)
        ground_truth_storage_profile_1 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(
                enabled=False,
            ),
            file_csi_driver=None,
            snapshot_controller=None,
        )
        self.assertEqual(ctx_1.get_storage_profile(), ground_truth_storage_profile_1)

        # update
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_file_driver": True,
                "disable_snapshot_controller": True,
                "yes": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        storage_profile_2 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(
                enabled=True,
            ),
            file_csi_driver=self.models.ManagedClusterStorageProfileFileCSIDriver(
                enabled=False,
            ),
            snapshot_controller=self.models.ManagedClusterStorageProfileSnapshotController(
                enabled=True,
            ),
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            storage_profile=storage_profile_2,
        )
        ctx_2.attach_mc(mc_2)
        ground_truth_storage_profile_2 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=None,
            file_csi_driver=self.models.ManagedClusterStorageProfileFileCSIDriver(
                enabled=True,
            ),
            snapshot_controller=self.models.ManagedClusterStorageProfileSnapshotController(
                enabled=False,
            ),
        )
        self.assertEqual(ctx_2.get_storage_profile(), ground_truth_storage_profile_2)

    def test_get_enable_apiserver_vnet_integration(self):
        ctx_0 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertIsNone(ctx_0.get_enable_apiserver_vnet_integration())

        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": False,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_apiserver_vnet_integration(), False)

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": False,
                "enable_private_cluster": False,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.enable_vnet_integration = True
        api_server_access_profile.enable_private_cluster = True
        mc = self.models.ManagedCluster(
            location="test_location",
            api_server_access_profile=api_server_access_profile,
        )
        ctx_2.attach_mc(mc)
        self.assertEqual(ctx_2.get_enable_apiserver_vnet_integration(), True)

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": True,
                "enable_private_cluster": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_3.get_enable_apiserver_vnet_integration(), True)

        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_4.get_enable_apiserver_vnet_integration()

        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": True,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_5.get_enable_apiserver_vnet_integration()

    def test_get_apiserver_subnet_id(self):
        ctx_0 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_0)
        self.assertIsNone(ctx_0.get_apiserver_subnet_id())

        apiserver_subnet_id = "/subscriptions/fakesub/resourceGroups/fakerg/providers/Microsoft.Network/virtualNetworks/fakevnet/subnets/apiserver"
        vnet_subnet_id = "/subscriptions/fakesub/resourceGroups/fakerg/providers/Microsoft.Network/virtualNetworks/fakevnet/subnets/node"
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": True,
                "enable_private_cluster": True,
                "apiserver_subnet_id": apiserver_subnet_id,
                "vnet_subnet_id": vnet_subnet_id,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_1)
        self.assertEqual(ctx_1.get_apiserver_subnet_id(), apiserver_subnet_id)

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": True,
                "enable_private_cluster": True,
                "vnet_subnet_id": vnet_subnet_id
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_2)
        api_server_access_profile = self.models.ManagedClusterAPIServerAccessProfile()
        api_server_access_profile.subnet_id = apiserver_subnet_id
        mc = self.models.ManagedCluster(
            location="test_location",
            api_server_access_profile=api_server_access_profile,
        )
        ctx_2.attach_mc(mc)
        self.assertEqual(ctx_2.get_apiserver_subnet_id(), apiserver_subnet_id)

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": True,
                "apiserver_subnet_id": apiserver_subnet_id,
            }),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        self.create_attach_agentpool_context(ctx_3)
        self.assertEqual(ctx_3.get_apiserver_subnet_id(), apiserver_subnet_id)

        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_private_cluster": True,
                "apiserver_subnet_id": apiserver_subnet_id,
                "vnet_subnet_id": vnet_subnet_id,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_4)
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_4.get_apiserver_subnet_id()

        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "enable_apiserver_vnet_integration": False,
                "apiserver_subnet_id": apiserver_subnet_id,
                "vnet_subnet_id": vnet_subnet_id,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_5)
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_5.get_apiserver_subnet_id()

        ctx_6 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({
                "apiserver_subnet_id": apiserver_subnet_id,
            }),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.create_attach_agentpool_context(ctx_6)
        with self.assertRaises(RequiredArgumentMissingError):
            ctx_6.get_apiserver_subnet_id()

    def test_get_dns_zone_resource_id(self):
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "dns_zone_resource_id": "test_dns_zone_resource_id",
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_dns_zone_resource_id(), "test_dns_zone_resource_id")
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            ingress_profile=self.models.ManagedClusterIngressProfile(
                web_app_routing=self.models.ManagedClusterIngressProfileWebAppRouting(
                    enabled=True,
                    dns_zone_resource_id="test_mc_dns_zone_resource_id",
                )
            ),
        )
        ctx_1.attach_mc(mc_1)
        self.assertEqual(ctx_1.get_dns_zone_resource_id(), "test_mc_dns_zone_resource_id")

    def test_get_enable_keda(self):
        # Returns the value of enable_keda if keda is None in existing profile.
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertIsNone(ctx_1.get_enable_keda())

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_keda": False}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertFalse(ctx_2.get_enable_keda())

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_keda": True}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertTrue(ctx_3.get_enable_keda())

        keda_none_mc = self.models.ManagedCluster(
            location="test_location",
            workload_auto_scaler_profile=self.models.ManagedClusterWorkloadAutoScalerProfile(),
        )

        keda_false_mc = self.models.ManagedCluster(
            location="test_location",
            workload_auto_scaler_profile=self.models.ManagedClusterWorkloadAutoScalerProfile(
                keda=self.models.ManagedClusterWorkloadAutoScalerProfileKeda(
                    enabled=False
                )
            ),
        )

        keda_true_mc = self.models.ManagedCluster(
            location="test_location",
            workload_auto_scaler_profile=self.models.ManagedClusterWorkloadAutoScalerProfile(
                keda=self.models.ManagedClusterWorkloadAutoScalerProfileKeda(
                    enabled=True
                )
            ),
        )

        # Returns the value of keda in existing profile if enable_keda is None.
        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ctx_4.attach_mc(keda_none_mc)
        self.assertIsNone(ctx_4.get_enable_keda())

        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ctx_5.attach_mc(keda_false_mc)
        self.assertFalse(ctx_5.get_enable_keda())

        ctx_6 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ctx_6.attach_mc(keda_true_mc)
        self.assertTrue(ctx_6.get_enable_keda())

        # Ignores the value of keda in existing profile in update-mode.
        ctx_7 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        ctx_7.attach_mc(keda_true_mc)
        self.assertIsNone(ctx_7.get_enable_keda())

        # Throws exception when both enable_keda and disable_keda are True.
        ctx_8 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {"enable_keda": True, "disable_keda": True}
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_8.get_enable_keda()

        # Throws exception when disable_keda and the value of keda in existing profile are True.
        ctx_9 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"disable_keda": True}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ctx_9.attach_mc(keda_true_mc)
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_9.get_enable_keda()

    def test_get_disable_keda(self):
        # Returns the value of disable_keda.
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertIsNone(ctx_1.get_disable_keda())

        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"disable_keda": False}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertFalse(ctx_2.get_disable_keda())

        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"disable_keda": True}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertTrue(ctx_3.get_disable_keda())

        # Throws exception when both enable_keda and disable_keda are True.
        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {"enable_keda": True, "disable_keda": True}
            ),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_4.get_disable_keda()

        keda_true_mc = self.models.ManagedCluster(
            location="test_location",
            workload_auto_scaler_profile=self.models.ManagedClusterWorkloadAutoScalerProfile(
                keda=self.models.ManagedClusterWorkloadAutoScalerProfileKeda(
                    enabled=True
                )
            ),
        )

        # Throws exception when disable_keda and the value of keda in existing profile are True.
        ctx_5 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"disable_keda": True}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        ctx_5.attach_mc(keda_true_mc)
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_5.get_disable_keda()

    def test_get_defender_config(self):
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_defender": True,
                    "defender_config": get_test_data_file_path(
                        "defenderconfig.json"
                    ),
                }
            ),
            self.models,
            DecoratorMode.CREATE,
        )
        defender_config_1 = ctx_1.get_defender_config()
        ground_truth_defender_config_1 = self.models.ManagedClusterSecurityProfileDefender(
            log_analytics_workspace_resource_id="test_workspace_resource_id",
            security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                enabled=True
            ),
        )
        self.assertEqual(defender_config_1, ground_truth_defender_config_1)

        # custom value
        ctx_2 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {"enable_defender": True, "defender_config": "fake-path"}
            ),
            self.models,
            DecoratorMode.CREATE,
        )
        # fail on invalid file path
        with self.assertRaises(InvalidArgumentValueError):
            ctx_2.get_defender_config()

        # custom
        ctx_3 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"disable_defender": True}),
            self.models,
            DecoratorMode.UPDATE,
        )
        defender_config_3 = ctx_3.get_defender_config()
        ground_truth_defender_config_3 = self.models.ManagedClusterSecurityProfileDefender(
            security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                enabled=False,
            ),
        )
        self.assertEqual(defender_config_3, ground_truth_defender_config_3)

        # custom
        ctx_4 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"enable_defender": True}),
            self.models,
            DecoratorMode.UPDATE,
        )
        ctx_4.set_intermediate("subscription_id", "test_subscription_id")
        with patch(
            "azure.cli.command_modules.acs.managed_cluster_decorator.ensure_default_log_analytics_workspace_for_monitoring",
            return_value="test_workspace_resource_id",
        ):
            defender_config_4 = ctx_4.get_defender_config()
        ground_truth_defender_config_4 = self.models.ManagedClusterSecurityProfileDefender(
            log_analytics_workspace_resource_id="test_workspace_resource_id",
            security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                enabled=True,
            ),
        )
        self.assertEqual(defender_config_4, ground_truth_defender_config_4)


class AKSPreviewManagedClusterCreateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()

    def test_set_up_agentpool_profile(self):
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "nodepool_name": "test_np_name",
                "node_vm_size": "Standard_DSx_vy",
                "os_sku": None,
                "snapshot_id": "test_snapshot_id",
                "vnet_subnet_id": "test_vnet_subnet_id",
                "pod_subnet_id": "test_pod_subnet_id",
                "enable_node_public_ip": True,
                "node_public_ip_prefix_id": "test_node_public_ip_prefix_id",
                "enable_cluster_autoscaler": True,
                "min_count": 5,
                "max_count": 20,
                "node_count": 10,
                "nodepool_tags": {"k1": "v1"},
                "nodepool_labels": {"k1": "v1", "k2": "v2"},
                "node_osdisk_size": 100,
                "node_osdisk_type": "test_os_disk_type",
                "vm_set_type": None,
                "zones": ["tz1", "tz2"],
                "ppg": "test_ppg_id",
                "max_pods": 50,
                "enable_encryption_at_host": True,
                "enable_ultra_ssd": True,
                "enable_fips_image": True,
                "kubelet_config": None,
                "linux_os_config": None,
                "host_group_id": "test_host_group_id",
                "crg_id": "test_crg_id",
                "message_of_the_day": get_test_data_file_path("invalidconfig.json"),
                "gpu_instance_profile": "test_gpu_instance_profile",
                "workload_runtime": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        mock_snapshot = Mock(
            kubernetes_version="",
            os_sku="snapshot_os_sku",
            os_type=None,
            vm_size="snapshot_vm_size",
        )
        with patch(
            "azext_aks_preview.agentpool_decorator.get_nodepool_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            dec_mc_1 = dec_1.set_up_agentpool_profile(mc_1)
        ground_truth_agentpool_profile_1 = self.models.ManagedClusterAgentPoolProfile(
            name="test_np_name",
            orchestrator_version="",
            vm_size="Standard_DSx_vy",
            os_type=CONST_DEFAULT_NODE_OS_TYPE,
            os_sku="snapshot_os_sku",
            creation_data=self.models.CreationData(source_resource_id="test_snapshot_id"),
            vnet_subnet_id="test_vnet_subnet_id",
            pod_subnet_id="test_pod_subnet_id",
            enable_node_public_ip=True,
            node_public_ip_prefix_id="test_node_public_ip_prefix_id",
            enable_auto_scaling=True,
            min_count=5,
            max_count=20,
            count=10,
            node_labels={"k1": "v1", "k2": "v2"},
            tags={"k1": "v1"},
            node_taints=[],
            os_disk_size_gb=100,
            os_disk_type="test_os_disk_type",
            upgrade_settings=self.models.AgentPoolUpgradeSettings(),
            type=CONST_VIRTUAL_MACHINE_SCALE_SETS,
            availability_zones=["tz1", "tz2"],
            proximity_placement_group_id="test_ppg_id",
            max_pods=50,
            enable_encryption_at_host=True,
            enable_ultra_ssd=True,
            enable_fips=True,
            mode=CONST_NODEPOOL_MODE_SYSTEM,
            host_group_id="test_host_group_id",
            capacity_reservation_group_id="test_crg_id",
            message_of_the_day="W10=",  # base64 encode of "[]"
            gpu_instance_profile="test_gpu_instance_profile",
            workload_runtime=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
        )
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        ground_truth_mc_1.agent_pool_profiles = [ground_truth_agentpool_profile_1]
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_set_up_network_profile(self):
        # custom value
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
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
                "ip_families": "IPv4,IPv6",
                "pod_cidrs": "10.246.0.0/16,2001:abcd::/64",
                "service_cidrs": "10.0.0.0/16,2001:ffff::/108",
                "load_balancer_managed_outbound_ipv6_count": 3,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.set_up_network_profile(mc_1)

        network_profile_1 = self.models.ContainerServiceNetworkProfile(
            load_balancer_sku=CONST_LOAD_BALANCER_SKU_STANDARD,
            ip_families=["IPv4", "IPv6"],
            pod_cidrs=["10.246.0.0/16", "2001:abcd::/64"],
            service_cidrs=["10.0.0.0/16", "2001:ffff::/108"],
        )
        load_balancer_profile_1 = self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
            managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                count_ipv6=3,
            )
        )
        network_profile_1.load_balancer_profile = load_balancer_profile_1
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location", network_profile=network_profile_1)
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_set_up_api_server_access_profile(self):
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location"
        )
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.set_up_api_server_access_profile(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location"
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        apiserver_subnet_id = "/subscriptions/fakesub/resourceGroups/fakerg/providers/Microsoft.Network/virtualNetworks/fakevnet/subnets/apiserver"
        vnet_subnet_id = "/subscriptions/fakesub/resourceGroups/fakerg/providers/Microsoft.Network/virtualNetworks/fakevnet/subnets/node"
        dec_2 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_apiserver_vnet_integration": True,
                "enable_private_cluster": True,
                "apiserver_subnet_id": apiserver_subnet_id,
                "vnet_subnet_id": vnet_subnet_id,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.set_up_api_server_access_profile(mc_2)
        ground_truth_api_server_access_profile_2 = self.models.ManagedClusterAPIServerAccessProfile(
            enable_vnet_integration=True,
            subnet_id=apiserver_subnet_id,
            enable_private_cluster=True,
            authorized_ip_ranges=[],
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            api_server_access_profile=ground_truth_api_server_access_profile_2,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_build_gitops_addon_profile(self):
        # default
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
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
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
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
        dec_1.context.attach_mc(mc_1)
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
        dec_2 = AKSPreviewManagedClusterCreateDecorator(
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
                "appgw_subnet_cidr": "test_appgw_subnet_prefix",
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
        dec_2.context.attach_mc(mc_2)
        with patch(
            "azure.cli.command_modules.acs.managed_cluster_decorator.ensure_container_insights_for_monitoring",
            return_value=None,
        ):
            dec_mc_2 = dec_2.set_up_addon_profiles(mc_2)

        addon_profiles_2 = {
            CONST_MONITORING_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={
                    CONST_MONITORING_LOG_ANALYTICS_WORKSPACE_RESOURCE_ID: "/test_workspace_resource_id",
                    CONST_MONITORING_USING_AAD_MSI_AUTH: "True",
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
        self.assertEqual(dec_2.context.get_intermediate("monitoring_addon_enabled"), True)
        self.assertEqual(dec_2.context.get_intermediate("virtual_node_addon_enabled"), None)
        self.assertEqual(dec_2.context.get_intermediate("ingress_appgw_addon_enabled"), True)

    def test_set_up_http_proxy_config(self):
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {"http_proxy_config": get_test_data_file_path("httpproxyconfig.json")},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_http_proxy_config(None)
        dec_mc_1 = dec_1.set_up_http_proxy_config(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            http_proxy_config={
                "httpProxy": "http://cli-proxy-vm:3128/",
                "httpsProxy": "https://cli-proxy-vm:3129/",
                "noProxy": ["localhost", "127.0.0.1"],
                "trustedCa": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZHekNDQXdPZ0F3SUJBZ0lVT1FvajhDTFpkc2Vscjk3cnZJd3g1T0xEc3V3d0RRWUpLb1pJaHZjTkFRRUwKQlFBd0Z6RVZNQk1HQTFVRUF3d01ZMnhwTFhCeWIzaDVMWFp0TUI0WERUSXlNRE13T0RFMk5EUTBOMW9YRFRNeQpNRE13TlRFMk5EUTBOMW93RnpFVk1CTUdBMVVFQXd3TVkyeHBMWEJ5YjNoNUxYWnRNSUlDSWpBTkJna3Foa2lHCjl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUEvTVB0VjVCVFB0NmNxaTRSZE1sbXIzeUlzYTJ1anpjaHh2NGgKanNDMUR0blJnb3M1UzQxUEgwcmkrM3RUU1ZYMzJ5cndzWStyRDFZUnVwbTZsbUU3R2hVNUkwR2k5b3prU0YwWgpLS2FKaTJveXBVL0ZCK1FQcXpvQ1JzTUV3R0NibUtGVmw4VnVoeW5kWEs0YjRrYmxyOWJsL2V1d2Q3TThTYnZ6CldVam5lRHJRc2lJc3J6UFQ0S0FaTHFjdHpEZTRsbFBUN1lLYTMzaGlFUE9mdldpWitkcWthUUE5UDY0eFhTeW4KZkhYOHVWQUozdUJWSmVHeEQwcGtOSjdqT3J5YVV1SEh1Y1U4UzltSWpuS2pBQjVhUGpMSDV4QXM2bG1iMzEyMgp5KzF0bkVBbVhNNTBEK1VvRWpmUzZIT2I1cmRpcVhHdmMxS2JvS2p6a1BDUnh4MmE3MmN2ZWdVajZtZ0FKTHpnClRoRTFsbGNtVTRpemd4b0lNa1ZwR1RWT0xMbjFWRkt1TmhNWkN2RnZLZ25Lb0F2M0cwRlVuZldFYVJSalNObUQKTFlhTURUNUg5WnQycERJVWpVR1N0Q2w3Z1J6TUVuWXdKTzN5aURwZzQzbzVkUnlzVXlMOUpmRS9OaDdUZzYxOApuOGNKL1c3K1FZYllsanVyYXA4cjdRRlNyb2wzVkNoRkIrT29yNW5pK3ZvaFNBd0pmMFVsTXBHM3hXbXkxVUk0ClRGS2ZGR1JSVHpyUCs3Yk53WDVoSXZJeTVWdGd5YU9xSndUeGhpL0pkeHRPcjJ0QTVyQ1c3K0N0Z1N2emtxTkUKWHlyN3ZrWWdwNlk1TFpneTR0VWpLMEswT1VnVmRqQk9oRHBFenkvRkY4dzFGRVZnSjBxWS9yV2NMa0JIRFQ4Ugp2SmtoaW84Q0F3RUFBYU5mTUYwd0Z3WURWUjBSQkJBd0RvSU1ZMnhwTFhCeWIzaDVMWFp0TUJJR0ExVWRFd0VCCi93UUlNQVlCQWY4Q0FRQXdEd1lEVlIwUEFRSC9CQVVEQXdmbmdEQWRCZ05WSFNVRUZqQVVCZ2dyQmdFRkJRY0QKQWdZSUt3WUJCUVVIQXdFd0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dJQkFBb21qQ3lYdmFRT3hnWUs1MHNYTEIyKwp3QWZkc3g1bm5HZGd5Zmc0dXJXMlZtMTVEaEd2STdDL250cTBkWXkyNE4vVWJHN1VEWHZseUxJSkZxMVhQN25mCnBaRzBWQ2paNjlibXhLbTNaOG0wL0F3TXZpOGU5ZWR5OHY5a05CQ3dMR2tIYkE4WW85Q0lpUWdlbGZwcDF2VWgKYm5OQmhhRCtpdTZDZmlDTHdnSmIvaXc3ZW8vQ3lvWnF4K3RqWGFPMnpYdm00cC8rUUlmQU9ndEdRTEZVOGNmWgovZ1VyVHE1Z0ZxMCtQOUd5V3NBVEpGNnE3TDZXWlpqME91VHNlN2Y0Q1NpajZNbk9NTXhBK0pvYWhKejdsc1NpClRKSEl3RXA1ci9SeWhweWVwUXhGWWNVSDVKSmY5cmFoWExXWmkrOVRqeFNNMll5aHhmUlBzaVVFdUdEb2s3OFEKbS9RUGlDaTlKSmIxb2NtVGpBVjh4RFNob2NpdlhPRnlobjZMbjc3dkxqWStBYXZ0V0RoUXRocHVQeHNMdFZ6bQplMFNIMTFkRUxSdGI3NG1xWE9yTzdmdS8rSUJzM0pxTEUvVSt4dXhRdHZHOHZHMXlES0hIU1pxUzJoL1dzNGw0Ck5pQXNoSGdlaFFEUEJjWTl3WVl6ZkJnWnBPVU16ZERmNTB4K0ZTbFk0M1dPSkp6U3VRaDR5WjArM2t5Z3VDRjgKcm5NTFNjZXlTNGNpNExtSi9LQ1N1R2RmNlhWWXo4QkU5Z2pqanBDUDZxeTBVbFJlZldzL2lnL3djSysyYkYxVApuL1l2KzZnWGVDVEhKNzVxRElQbHA3RFJVVWswZmJNajRiSWthb2dXV2s0emYydThteFpMYTBsZVBLTktaTi9tCkdDdkZ3cjNlaSt1LzhjenA1RjdUCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K",
            },
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_set_up_pod_security_policy(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_security_policy": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_pod_security_policy(None)
        dec_mc_1 = dec_1.set_up_pod_security_policy(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location", enable_pod_security_policy=False)
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {"enable_pod_security_policy": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.set_up_pod_security_policy(mc_2)
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_set_up_pod_identity_profile(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_identity": False,
                "enable_pod_identity_with_kubenet": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_pod_identity_profile(None)
        dec_mc_1 = dec_1.set_up_pod_identity_profile(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_managed_identity": True,
                "enable_pod_identity": True,
                "enable_pod_identity_with_kubenet": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        network_profile_2 = self.models.ContainerServiceNetworkProfile(network_plugin="kubenet")
        mc_2 = self.models.ManagedCluster(location="test_location", network_profile=network_profile_2)
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.set_up_pod_identity_profile(mc_2)
        network_profile_2 = self.models.ContainerServiceNetworkProfile(network_plugin="kubenet")
        pod_identity_profile_2 = self.models.pod_identity_models.ManagedClusterPodIdentityProfile(
            enabled=True,
            allow_network_plugin_kubenet=True,
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=network_profile_2,
            pod_identity_profile=pod_identity_profile_2,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_set_up_oidc_issuer_profile__default_value(self):
        dec = AKSPreviewManagedClusterCreateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        updated_mc = dec.set_up_oidc_issuer_profile(mc)
        self.assertIsNone(updated_mc.oidc_issuer_profile)

    def test_set_up_oidc_issuer_profile__enabled(self):
        dec = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_oidc_issuer": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        updated_mc = dec.set_up_oidc_issuer_profile(mc)
        self.assertIsNotNone(updated_mc.oidc_issuer_profile)
        self.assertTrue(updated_mc.oidc_issuer_profile.enabled)

    def test_set_up_oidc_issuer_profile__enabled_mc_enabled(self):
        dec = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_oidc_issuer": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(location="test_location")
        mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
        dec.context.attach_mc(mc)
        updated_mc = dec.set_up_oidc_issuer_profile(mc)
        self.assertIsNotNone(updated_mc.oidc_issuer_profile)
        self.assertTrue(updated_mc.oidc_issuer_profile.enabled)

    def test_set_up_workload_identity_profile__default_value(self):
        dec = AKSPreviewManagedClusterCreateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        updated_mc = dec.set_up_workload_identity_profile(mc)
        self.assertIsNone(updated_mc.security_profile)

    def test_set_up_workload_identity_profile__default_value_with_security_profile(self):
        dec = AKSPreviewManagedClusterCreateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc = self.models.ManagedCluster(location="test_location")
        mc.security_profile = self.models.ManagedClusterSecurityProfile()
        dec.context.attach_mc(mc)
        updated_mc = dec.set_up_workload_identity_profile(mc)
        self.assertIsNone(updated_mc.security_profile.workload_identity)

    def test_set_up_workload_identity_profile__enabled(self):
        dec = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_oidc_issuer": True,
                "enable_workload_identity": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        updated_mc = dec.set_up_workload_identity_profile(mc)
        self.assertTrue(updated_mc.security_profile.workload_identity.enabled)

    def test_set_up_azure_keyvault_kms(self):
        key_id_1 = "https://fakekeyvault.vault.azure.net/secrets/fakekeyname/fakekeyversion"

        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.set_up_azure_keyvault_kms(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        dec_2 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_id": key_id_1,
                "azure_keyvault_kms_key_vault_network_access": "Public",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.set_up_azure_keyvault_kms(mc_2)

        ground_truth_azure_keyvault_kms_profile_2 = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_1,
            key_vault_network_access="Public",
        )
        ground_truth_security_profile_2 = self.models.ManagedClusterSecurityProfile(
            azure_key_vault_kms=ground_truth_azure_keyvault_kms_profile_2,
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            security_profile=ground_truth_security_profile_2,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

        dec_3 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_id": key_id_1,
                "azure_keyvault_kms_key_vault_network_access": "Private",
                "azure_keyvault_kms_key_vault_resource_id": "/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_3 = self.models.ManagedCluster(location="test_location")
        dec_3.context.attach_mc(mc_3)
        dec_mc_3 = dec_3.set_up_azure_keyvault_kms(mc_3)

        ground_truth_azure_keyvault_kms_profile_3 = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_1,
            key_vault_network_access="Private",
            key_vault_resource_id="/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo",
        )
        ground_truth_security_profile_3 = self.models.ManagedClusterSecurityProfile(
            azure_key_vault_kms=ground_truth_azure_keyvault_kms_profile_3,
        )
        ground_truth_mc_3 = self.models.ManagedCluster(
            location="test_location",
            security_profile=ground_truth_security_profile_3,
        )

        self.assertEqual(dec_mc_3, ground_truth_mc_3)

    def test_set_up_creationdata_of_cluster_snapshot(self):
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {
                "cluster_snapshot_id": "test_cluster_snapshot_id",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.set_up_creationdata_of_cluster_snapshot(mc_1)
        cd = self.models.CreationData(source_resource_id="test_cluster_snapshot_id")
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location", creation_data=cd)
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_set_up_storage_profile(self):
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {"disable_disk_driver": True, "disable_file_driver": True, "disable_snapshot_controller": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.set_up_storage_profile(mc_1)
        storage_profile_1 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(enabled=False),
            file_csi_driver=self.models.ManagedClusterStorageProfileFileCSIDriver(enabled=False),
            snapshot_controller=self.models.ManagedClusterStorageProfileSnapshotController(enabled=False),
        )
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location", storage_profile=storage_profile_1)
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_set_up_ingress_web_app_routing(self):
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {"enable_addons": "web_application_routing", "dns_zone_resource_id": "test_dns_zone_resource_id"},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.set_up_ingress_web_app_routing(mc_1)
        ground_truth_ingress_profile_1 = self.models.ManagedClusterIngressProfile(
            web_app_routing=self.models.ManagedClusterIngressProfileWebAppRouting(
                enabled=True,
                dns_zone_resource_id="test_dns_zone_resource_id",
            )
        )
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location", ingress_profile=ground_truth_ingress_profile_1
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_set_up_workload_auto_scaler_profile(self):
        # Throws exception when incorrect mc object is passed.
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW
        )
        with self.assertRaisesRegex(
            CLIInternalError,
            "^Unexpected mc object with type '<class 'NoneType'>'\.$",
        ):
            dec_1.set_up_workload_auto_scaler_profile(None)

        # Sets profile to None without raw parameters.
        dec_2 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW
        )
        mc_in = self.models.ManagedCluster(location="test_location")
        dec_2.context.attach_mc(mc_in)
        mc_out = dec_2.set_up_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertIsNone(mc_out.workload_auto_scaler_profile)

        # Sets profile to None if enable_keda is False.
        dec_3 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {"enable_keda": False},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_in = self.models.ManagedCluster(location="test_location")
        dec_3.context.attach_mc(mc_in)
        mc_out = dec_3.set_up_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertIsNone(mc_out.workload_auto_scaler_profile)

        # Sets profile with keda enabled if enable_keda is True.
        dec_4 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {"enable_keda": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_in = self.models.ManagedCluster(location="test_location")
        dec_4.context.attach_mc(mc_in)
        mc_out = dec_4.set_up_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile.keda)
        self.assertTrue(mc_out.workload_auto_scaler_profile.keda.enabled)

    def test_set_up_defender(self):
        dec_1 = AKSPreviewManagedClusterCreateDecorator(
            self.cmd,
            self.client,
            {"enable_defender": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        dec_1.context.set_intermediate("subscription_id", "test_subscription_id")

        with patch(
                "azure.cli.command_modules.acs.managed_cluster_decorator.ensure_default_log_analytics_workspace_for_monitoring",
                return_value="test_workspace_resource_id",
        ):
            dec_mc_1 = dec_1.set_up_defender(mc_1)

        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            security_profile=self.models.ManagedClusterSecurityProfile(
                defender=self.models.ManagedClusterSecurityProfileDefender(
                    log_analytics_workspace_resource_id="test_workspace_resource_id",
                    security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                        enabled=True
                    ),
                )
            ),
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_construct_mc_profile_preview(self):
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

        # default value in `aks_create`
        dec_1 = AKSPreviewManagedClusterCreateDecorator(self.cmd, self.client, raw_param_dict, CUSTOM_MGMT_AKS_PREVIEW)

        mock_profile = Mock(get_subscription_id=Mock(return_value="1234-5678-9012"))
        with patch(
            "azure.cli.command_modules.acs.managed_cluster_decorator.get_rg_location",
            return_value="test_location",
        ), patch(
            "azure.cli.command_modules.acs.managed_cluster_decorator.Profile",
            return_value=mock_profile,
        ):
            dec_mc_1 = dec_1.construct_mc_profile_preview()

        upgrade_settings_1 = self.models.AgentPoolUpgradeSettings()
        agent_pool_profile_1 = self.models.ManagedClusterAgentPoolProfile(
            name="nodepool1",
            orchestrator_version="",
            vm_size=CONST_DEFAULT_NODE_VM_SIZE,
            os_type=CONST_DEFAULT_NODE_OS_TYPE,
            enable_node_public_ip=False,
            enable_auto_scaling=False,
            count=3,
            node_taints=[],
            os_disk_size_gb=0,
            upgrade_settings=upgrade_settings_1,
            type=CONST_VIRTUAL_MACHINE_SCALE_SETS,
            enable_encryption_at_host=False,
            enable_ultra_ssd=False,
            enable_fips=False,
            mode=CONST_NODEPOOL_MODE_SYSTEM,
            workload_runtime=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
            enable_custom_ca_trust=False,
        )
        ssh_config_1 = self.models.ContainerServiceSshConfiguration(
            public_keys=[self.models.ContainerServiceSshPublicKey(key_data=public_key)]
        )
        linux_profile_1 = self.models.ContainerServiceLinuxProfile(admin_username="azureuser", ssh=ssh_config_1)
        network_profile_1 = self.models.ContainerServiceNetworkProfile(
            load_balancer_sku="standard",
        )
        identity_1 = self.models.ManagedClusterIdentity(type="SystemAssigned")
        storage_profile_1 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=None,
            file_csi_driver=None,
            snapshot_controller=None,
        )
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
            storage_profile=storage_profile_1,
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        dec_1.context.raw_param.print_usage_statistics()


class AKSPreviewManagedClusterUpdateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()

    def test_check_raw_parameters(self):
        # default value in `aks_create`
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        # fail on no updated parameter provided
        with patch(
            "azext_aks_preview.managed_cluster_decorator.prompt_y_n",
            return_value=False,
        ), self.assertRaises(RequiredArgumentMissingError):
            dec_1.check_raw_parameters()

        # unless user says they want to reconcile
        with patch(
            "azext_aks_preview.managed_cluster_decorator.prompt_y_n",
            return_value=True,
        ):
            dec_1.check_raw_parameters()

        # custom value
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "cluster_autoscaler_profile": {},
                "api_server_authorized_ip_ranges": "",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        self.assertIsNone(dec_2.check_raw_parameters())

    def test_update_load_balancer_profile(self):
        # default value in `aks_update`
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_sku": None,
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_managed_outbound_ipv6_count": None,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
                "load_balancer_outbound_ports": None,
                "load_balancer_idle_timeout": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(),
        )
        dec_1.context.attach_mc(mc_1)
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.update_load_balancer_profile(None)
        dec_mc_1 = dec_1.update_load_balancer_profile(mc_1)

        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(),
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value - outbound ip prefixes
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_managed_outbound_ipv6_count": None,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": "id3,id4",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    outbound_ip_prefixes=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                        public_ip_prefixes=[
                            self.models.load_balancer_models.ResourceReference(id="id1"),
                            self.models.load_balancer_models.ResourceReference(id="id2"),
                        ]
                    )
                )
            ),
        )
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.update_load_balancer_profile(mc_2)

        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    outbound_ip_prefixes=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                        public_ip_prefixes=[
                            self.models.load_balancer_models.ResourceReference(id="id3"),
                            self.models.load_balancer_models.ResourceReference(id="id4"),
                        ]
                    )
                )
            ),
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

        # custom value - outbound ip
        dec_3 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_managed_outbound_ipv6_count": None,
                "load_balancer_outbound_ips": "id3,id4",
                "load_balancer_outbound_ip_prefixes": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_3 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPs(
                        public_i_ps=[
                            self.models.load_balancer_models.ResourceReference(id="id1"),
                            self.models.load_balancer_models.ResourceReference(id="id2"),
                        ]
                    )
                )
            ),
        )
        dec_3.context.attach_mc(mc_3)
        dec_mc_3 = dec_3.update_load_balancer_profile(mc_3)

        ground_truth_mc_3 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPs(
                        public_i_ps=[
                            self.models.load_balancer_models.ResourceReference(id="id3"),
                            self.models.load_balancer_models.ResourceReference(id="id4"),
                        ]
                    )
                )
            ),
        )
        self.assertEqual(dec_mc_3, ground_truth_mc_3)

        # custom value - managed outbound ip, count only
        dec_4 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ip_count": 5,
                "load_balancer_managed_outbound_ipv6_count": None,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_4 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                        count=10, count_ipv6=20
                    ),
                )
            ),
        )
        dec_4.context.attach_mc(mc_4)
        dec_mc_4 = dec_4.update_load_balancer_profile(mc_4)

        ground_truth_mc_4 = self.models.ManagedCluster(
            location="test_location",
            network_profile=(
                self.models.ContainerServiceNetworkProfile(
                    load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                        managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                            count=5, count_ipv6=20
                        ),
                    )
                )
            ),
        )
        self.assertEqual(dec_mc_4, ground_truth_mc_4)

        # custom value - managed outbound ip, count_ipv6 only
        dec_5 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_managed_outbound_ipv6_count": 5,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_5 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                        count=10, count_ipv6=20
                    ),
                )
            ),
        )
        dec_5.context.attach_mc(mc_5)
        dec_mc_5 = dec_5.update_load_balancer_profile(mc_5)

        ground_truth_mc_5 = self.models.ManagedCluster(
            location="test_location",
            network_profile=(
                self.models.ContainerServiceNetworkProfile(
                    load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                        managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                            count=10, count_ipv6=5
                        ),
                    )
                )
            ),
        )
        self.assertEqual(dec_mc_5, ground_truth_mc_5)

        # custom value - managed outbound ip
        dec_6 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ip_count": 25,
                "load_balancer_managed_outbound_ipv6_count": 5,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_6 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                        count=10, count_ipv6=20
                    ),
                )
            ),
        )
        dec_6.context.attach_mc(mc_6)
        dec_mc_6 = dec_6.update_load_balancer_profile(mc_6)

        ground_truth_mc_6 = self.models.ManagedCluster(
            location="test_location",
            network_profile=(
                self.models.ContainerServiceNetworkProfile(
                    load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                        managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                            count=25, count_ipv6=5
                        ),
                    )
                )
            ),
        )
        self.assertEqual(dec_mc_6, ground_truth_mc_6)

        # custom value - from managed outbound ip to outbound ip
        dec_7 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ip_count": None,
                "load_balancer_managed_outbound_ipv6_count": None,
                "load_balancer_outbound_ips": "id1,id2",
                "load_balancer_outbound_ip_prefixes": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_7 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                    managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                        count=3, count_ipv6=2
                    )
                )
            ),
        )
        dec_7.context.attach_mc(mc_7)
        dec_mc_7 = dec_7.update_load_balancer_profile(mc_7)

        ground_truth_mc_7 = self.models.ManagedCluster(
            location="test_location",
            network_profile=(
                self.models.ContainerServiceNetworkProfile(
                    load_balancer_profile=self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
                        outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPs(
                            public_i_ps=[
                                self.models.load_balancer_models.ResourceReference(id="id1"),
                                self.models.load_balancer_models.ResourceReference(id="id2"),
                            ]
                        )
                    )
                )
            ),
        )
        self.assertEqual(dec_mc_7, ground_truth_mc_7)

        # custom value - from outbound ip prefix to managed outbound ip
        dec_8 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "load_balancer_managed_outbound_ip_count": 10,
                "load_balancer_managed_outbound_ipv6_count": 5,
                "load_balancer_outbound_ips": None,
                "load_balancer_outbound_ip_prefixes": None,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        load_balancer_profile_8 = self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
            outbound_ip_prefixes=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileOutboundIPPrefixes(
                public_ip_prefixes=[self.models.load_balancer_models.ResourceReference(id="test_public_ip_prefix")]
            ),
        )
        network_profile_8 = self.models.ContainerServiceNetworkProfile(load_balancer_profile=load_balancer_profile_8)
        mc_8 = self.models.ManagedCluster(location="test_location", network_profile=network_profile_8)
        dec_8.context.attach_mc(mc_8)
        dec_mc_8 = dec_8.update_load_balancer_profile(mc_8)

        ground_truth_load_balancer_profile_8 = self.models.load_balancer_models.ManagedClusterLoadBalancerProfile(
            managed_outbound_i_ps=self.models.load_balancer_models.ManagedClusterLoadBalancerProfileManagedOutboundIPs(
                count=10, count_ipv6=5
            ),
        )
        ground_truth_network_profile_8 = self.models.ContainerServiceNetworkProfile(
            load_balancer_profile=ground_truth_load_balancer_profile_8
        )
        ground_truth_mc_8 = self.models.ManagedCluster(
            location="test_location",
            network_profile=ground_truth_network_profile_8,
        )
        self.assertEqual(dec_mc_8, ground_truth_mc_8)

        # custom value
        dec_9 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_9 = self.models.ManagedCluster(location="test_location")
        dec_9.context.attach_mc(mc_9)
        # fail on incomplete mc object (no network profile)
        with self.assertRaises(UnknownError):
            dec_9.update_load_balancer_profile(mc_9)

    def test_update_api_server_access_profile(self):
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.update_api_server_access_profile(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        apiserver_subnet_id = "/subscriptions/fakesub/resourceGroups/fakerg/providers/Microsoft.Network/virtualNetworks/fakevnet/subnets/apiserver"
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_apiserver_vnet_integration": True,
                "apiserver_subnet_id": apiserver_subnet_id,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.update_api_server_access_profile(mc_2)
        ground_truth_api_server_access_profile_2 = self.models.ManagedClusterAPIServerAccessProfile(
            enable_vnet_integration=True,
            subnet_id=apiserver_subnet_id,
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            api_server_access_profile=ground_truth_api_server_access_profile_2,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_update_http_proxy_config(self):
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {"http_proxy_config": get_test_data_file_path("httpproxyconfig.json")},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.update_http_proxy_config(None)
        dec_mc_1 = dec_1.update_http_proxy_config(mc_1)

        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            http_proxy_config={
                "httpProxy": "http://cli-proxy-vm:3128/",
                "httpsProxy": "https://cli-proxy-vm:3129/",
                "noProxy": ["localhost", "127.0.0.1"],
                "trustedCa": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZHekNDQXdPZ0F3SUJBZ0lVT1FvajhDTFpkc2Vscjk3cnZJd3g1T0xEc3V3d0RRWUpLb1pJaHZjTkFRRUwKQlFBd0Z6RVZNQk1HQTFVRUF3d01ZMnhwTFhCeWIzaDVMWFp0TUI0WERUSXlNRE13T0RFMk5EUTBOMW9YRFRNeQpNRE13TlRFMk5EUTBOMW93RnpFVk1CTUdBMVVFQXd3TVkyeHBMWEJ5YjNoNUxYWnRNSUlDSWpBTkJna3Foa2lHCjl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUEvTVB0VjVCVFB0NmNxaTRSZE1sbXIzeUlzYTJ1anpjaHh2NGgKanNDMUR0blJnb3M1UzQxUEgwcmkrM3RUU1ZYMzJ5cndzWStyRDFZUnVwbTZsbUU3R2hVNUkwR2k5b3prU0YwWgpLS2FKaTJveXBVL0ZCK1FQcXpvQ1JzTUV3R0NibUtGVmw4VnVoeW5kWEs0YjRrYmxyOWJsL2V1d2Q3TThTYnZ6CldVam5lRHJRc2lJc3J6UFQ0S0FaTHFjdHpEZTRsbFBUN1lLYTMzaGlFUE9mdldpWitkcWthUUE5UDY0eFhTeW4KZkhYOHVWQUozdUJWSmVHeEQwcGtOSjdqT3J5YVV1SEh1Y1U4UzltSWpuS2pBQjVhUGpMSDV4QXM2bG1iMzEyMgp5KzF0bkVBbVhNNTBEK1VvRWpmUzZIT2I1cmRpcVhHdmMxS2JvS2p6a1BDUnh4MmE3MmN2ZWdVajZtZ0FKTHpnClRoRTFsbGNtVTRpemd4b0lNa1ZwR1RWT0xMbjFWRkt1TmhNWkN2RnZLZ25Lb0F2M0cwRlVuZldFYVJSalNObUQKTFlhTURUNUg5WnQycERJVWpVR1N0Q2w3Z1J6TUVuWXdKTzN5aURwZzQzbzVkUnlzVXlMOUpmRS9OaDdUZzYxOApuOGNKL1c3K1FZYllsanVyYXA4cjdRRlNyb2wzVkNoRkIrT29yNW5pK3ZvaFNBd0pmMFVsTXBHM3hXbXkxVUk0ClRGS2ZGR1JSVHpyUCs3Yk53WDVoSXZJeTVWdGd5YU9xSndUeGhpL0pkeHRPcjJ0QTVyQ1c3K0N0Z1N2emtxTkUKWHlyN3ZrWWdwNlk1TFpneTR0VWpLMEswT1VnVmRqQk9oRHBFenkvRkY4dzFGRVZnSjBxWS9yV2NMa0JIRFQ4Ugp2SmtoaW84Q0F3RUFBYU5mTUYwd0Z3WURWUjBSQkJBd0RvSU1ZMnhwTFhCeWIzaDVMWFp0TUJJR0ExVWRFd0VCCi93UUlNQVlCQWY4Q0FRQXdEd1lEVlIwUEFRSC9CQVVEQXdmbmdEQWRCZ05WSFNVRUZqQVVCZ2dyQmdFRkJRY0QKQWdZSUt3WUJCUVVIQXdFd0RRWUpLb1pJaHZjTkFRRUxCUUFEZ2dJQkFBb21qQ3lYdmFRT3hnWUs1MHNYTEIyKwp3QWZkc3g1bm5HZGd5Zmc0dXJXMlZtMTVEaEd2STdDL250cTBkWXkyNE4vVWJHN1VEWHZseUxJSkZxMVhQN25mCnBaRzBWQ2paNjlibXhLbTNaOG0wL0F3TXZpOGU5ZWR5OHY5a05CQ3dMR2tIYkE4WW85Q0lpUWdlbGZwcDF2VWgKYm5OQmhhRCtpdTZDZmlDTHdnSmIvaXc3ZW8vQ3lvWnF4K3RqWGFPMnpYdm00cC8rUUlmQU9ndEdRTEZVOGNmWgovZ1VyVHE1Z0ZxMCtQOUd5V3NBVEpGNnE3TDZXWlpqME91VHNlN2Y0Q1NpajZNbk9NTXhBK0pvYWhKejdsc1NpClRKSEl3RXA1ci9SeWhweWVwUXhGWWNVSDVKSmY5cmFoWExXWmkrOVRqeFNNMll5aHhmUlBzaVVFdUdEb2s3OFEKbS9RUGlDaTlKSmIxb2NtVGpBVjh4RFNob2NpdlhPRnlobjZMbjc3dkxqWStBYXZ0V0RoUXRocHVQeHNMdFZ6bQplMFNIMTFkRUxSdGI3NG1xWE9yTzdmdS8rSUJzM0pxTEUvVSt4dXhRdHZHOHZHMXlES0hIU1pxUzJoL1dzNGw0Ck5pQXNoSGdlaFFEUEJjWTl3WVl6ZkJnWnBPVU16ZERmNTB4K0ZTbFk0M1dPSkp6U3VRaDR5WjArM2t5Z3VDRjgKcm5NTFNjZXlTNGNpNExtSi9LQ1N1R2RmNlhWWXo4QkU5Z2pqanBDUDZxeTBVbFJlZldzL2lnL3djSysyYkYxVApuL1l2KzZnWGVDVEhKNzVxRElQbHA3RFJVVWswZmJNajRiSWthb2dXV2s0emYydThteFpMYTBsZVBLTktaTi9tCkdDdkZ3cjNlaSt1LzhjenA1RjdUCi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K",
            },
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

    def test_update_pod_security_policy(self):
        # default value in `aks_update`
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_security_policy": False,
                "disable_pod_security_policy": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        dec_1.context.attach_mc(mc_1)
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.update_pod_security_policy(None)

        dec_mc_1 = dec_1.update_pod_security_policy(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            enable_pod_security_policy=True,
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
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
        dec_3 = AKSPreviewManagedClusterUpdateDecorator(
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

    def test_update_pod_identity_profile(self):
        # default value in `aks_update`
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_identity": False,
                "disable_pod_identity": False,
                "enable_pod_identity_with_kubenet": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        # fail on passing the wrong mc object
        with self.assertRaises(CLIInternalError):
            dec_1.update_pod_identity_profile(None)

        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.update_pod_identity_profile(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # custom value
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_identity": True,
                "disable_pod_identity": False,
                "enable_pod_identity_with_kubenet": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_2 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                network_plugin="kubenet",
            ),
        )
        dec_2.context.attach_mc(mc_2)
        # fail on not a msi cluster
        with self.assertRaises(RequiredArgumentMissingError):
            dec_2.update_pod_identity_profile(mc_2)

        # custom value
        dec_3 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_identity": True,
                "disable_pod_identity": False,
                "enable_pod_identity_with_kubenet": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_3 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                network_plugin="kubenet",
            ),
            identity=self.models.ManagedClusterIdentity(
                type="SystemAssigned",
            ),
        )
        dec_3.context.attach_mc(mc_3)
        dec_mc_3 = dec_3.update_pod_identity_profile(mc_3)
        ground_truth_mc_3 = self.models.ManagedCluster(
            location="test_location",
            network_profile=self.models.ContainerServiceNetworkProfile(
                network_plugin="kubenet",
            ),
            pod_identity_profile=self.models.pod_identity_models.ManagedClusterPodIdentityProfile(
                enabled=True,
                allow_network_plugin_kubenet=True,
                user_assigned_identities=[],
                user_assigned_identity_exceptions=[],
            ),
            identity=self.models.ManagedClusterIdentity(
                type="SystemAssigned",
            ),
        )
        self.assertEqual(dec_mc_3, ground_truth_mc_3)

        # custom value
        dec_4 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_pod_identity": False,
                "disable_pod_identity": True,
                "enable_pod_identity_with_kubenet": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mc_4 = self.models.ManagedCluster(
            location="test_location",
            pod_identity_profile=self.models.pod_identity_models.ManagedClusterPodIdentityProfile(
                enabled=True,
                user_assigned_identities=[],
                user_assigned_identity_exceptions=[],
            ),
        )
        dec_4.context.attach_mc(mc_4)
        dec_mc_4 = dec_4.update_pod_identity_profile(mc_4)
        ground_truth_mc_4 = self.models.ManagedCluster(
            location="test_location",
            pod_identity_profile=self.models.pod_identity_models.ManagedClusterPodIdentityProfile(
                enabled=False,
            ),
        )
        self.assertEqual(dec_mc_4, ground_truth_mc_4)

    def test_update_oidc_issuer_profile__default_value(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        updated_mc = dec.update_oidc_issuer_profile(mc)
        self.assertIsNone(updated_mc.oidc_issuer_profile)

    def test_update_oidc_issuer_profile__default_value_mc_enabled(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc = self.models.ManagedCluster(location="test_location")
        mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
        dec.context.attach_mc(mc)
        updated_mc = dec.update_oidc_issuer_profile(mc)
        self.assertIsNone(updated_mc.oidc_issuer_profile)

    def test_update_oidc_issuer_profile__enabled(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_oidc_issuer": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        updated_mc = dec.update_oidc_issuer_profile(mc)
        self.assertIsNotNone(updated_mc.oidc_issuer_profile)
        self.assertTrue(updated_mc.oidc_issuer_profile.enabled)

    def test_update_oidc_issuer_profile__enabled_mc_enabled(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_oidc_issuer": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(location="test_location")
        mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
        dec.context.attach_mc(mc)
        updated_mc = dec.update_oidc_issuer_profile(mc)
        self.assertIsNotNone(updated_mc.oidc_issuer_profile)
        self.assertTrue(updated_mc.oidc_issuer_profile.enabled)

    def test_update_workload_identity_profile__default_value(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc = self.models.ManagedCluster(location="test_location")
        dec.context.attach_mc(mc)
        updated_mc = dec.update_workload_identity_profile(mc)
        self.assertIsNone(updated_mc.security_profile)

    def test_update_workload_identity_profile__default_value_mc_enabled(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc = self.models.ManagedCluster(location="test_location")
        mc.security_profile = self.models.ManagedClusterSecurityProfile(
            workload_identity=self.models.ManagedClusterSecurityProfileWorkloadIdentity(
                enabled=True,
            )
        )
        dec.context.attach_mc(mc)
        updated_mc = dec.update_workload_identity_profile(mc)
        self.assertIsNone(updated_mc.security_profile.workload_identity)

    def test_update_workload_identity_profile__enabled(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_workload_identity": True,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(location="test_location")
        mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
        dec.context.attach_mc(mc)
        updated_mc = dec.update_workload_identity_profile(mc)
        self.assertTrue(updated_mc.security_profile.workload_identity.enabled)

    def test_update_workload_identity_profile__disabled(self):
        dec = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_workload_identity": False,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(location="test_location")
        mc.oidc_issuer_profile = self.models.ManagedClusterOIDCIssuerProfile(enabled=True)
        dec.context.attach_mc(mc)
        updated_mc = dec.update_workload_identity_profile(mc)
        self.assertFalse(updated_mc.security_profile.workload_identity.enabled)

    def test_update_azure_keyvault_kms(self):
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.update_azure_keyvault_kms(mc_1)
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        key_id_1 = "https://fakekeyvault.vault.azure.net/secrets/fakekeyname/fakekeyversion"
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_id": key_id_1,
                "azure_keyvault_kms_key_vault_network_access": "Private",
                "azure_keyvault_kms_key_vault_resource_id": "/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo",
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
        )
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.update_azure_keyvault_kms(mc_2)

        ground_truth_azure_keyvault_kms_profile_2 = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_1,
            key_vault_network_access="Private",
            key_vault_resource_id="/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo",
        )
        ground_truth_security_profile_2 = self.models.ManagedClusterSecurityProfile(
            azure_key_vault_kms=ground_truth_azure_keyvault_kms_profile_2,
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            security_profile=ground_truth_security_profile_2,
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

        # partial update, backfill default network access
        dec_3 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_id": key_id_1,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_3 = self.models.ManagedCluster(
            location="test_location",
        )
        dec_3.context.attach_mc(mc_3)
        dec_mc_3 = dec_3.update_azure_keyvault_kms(mc_3)

        ground_truth_azure_keyvault_kms_profile_3 = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_1,
            key_vault_network_access="Public",
        )
        ground_truth_security_profile_3 = self.models.ManagedClusterSecurityProfile(
            azure_key_vault_kms=ground_truth_azure_keyvault_kms_profile_3,
        )
        ground_truth_mc_3 = self.models.ManagedCluster(
            location="test_location",
            security_profile=ground_truth_security_profile_3,
        )
        self.assertEqual(dec_mc_3, ground_truth_mc_3)

        # partial update, backfill network access and key vault id from existing mc
        dec_4 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_azure_keyvault_kms": True,
                "azure_keyvault_kms_key_id": key_id_1,
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        azure_keyvault_kms_profile_4 = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id="test_key_id",
            key_vault_network_access="Private",
            key_vault_resource_id="/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo",
        )
        security_profile_4 = self.models.ManagedClusterSecurityProfile(
            azure_key_vault_kms=azure_keyvault_kms_profile_4,
        )
        mc_4 = self.models.ManagedCluster(
            location="test_location",
            security_profile=security_profile_4,
        )
        dec_4.context.attach_mc(mc_4)
        dec_mc_4 = dec_4.update_azure_keyvault_kms(mc_4)

        ground_truth_azure_keyvault_kms_profile_4 = self.models.AzureKeyVaultKms(
            enabled=True,
            key_id=key_id_1,
            key_vault_network_access="Private",
            key_vault_resource_id="/subscriptions/8ecadfc9-d1a3-4ea4-b844-0d9f87e4d7c8/resourceGroups/foo/providers/Microsoft.KeyVault/vaults/foo",
        )
        ground_truth_security_profile_4 = self.models.ManagedClusterSecurityProfile(
            azure_key_vault_kms=ground_truth_azure_keyvault_kms_profile_4,
        )
        ground_truth_mc_4 = self.models.ManagedCluster(
            location="test_location",
            security_profile=ground_truth_security_profile_4,
        )
        self.assertEqual(dec_mc_4, ground_truth_mc_4)


    def test_update_storage_profile(self):
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {"disable_disk_driver": True, "disable_file_driver": True, "disable_snapshot_controller": True, "yes": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        storage_profile_1 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(enabled=True),
            file_csi_driver=self.models.ManagedClusterStorageProfileFileCSIDriver(enabled=True),
            snapshot_controller=self.models.ManagedClusterStorageProfileSnapshotController(enabled=True),
        )
        mc_1 = self.models.ManagedCluster(location="test_location", storage_profile=storage_profile_1)
        dec_1.context.attach_mc(mc_1)
        dec_mc_1 = dec_1.update_storage_profile(mc_1)
        ground_truth_storage_profile_1 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(enabled=False),
            file_csi_driver=self.models.ManagedClusterStorageProfileFileCSIDriver(enabled=False),
            snapshot_controller=self.models.ManagedClusterStorageProfileSnapshotController(enabled=False),
        )
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location", storage_profile=ground_truth_storage_profile_1
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_disk_driver": True, "enable_file_driver": True, "enable_snapshot_controller": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        storage_profile_2 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(enabled=False),
            file_csi_driver=self.models.ManagedClusterStorageProfileFileCSIDriver(enabled=False),
            snapshot_controller=self.models.ManagedClusterStorageProfileSnapshotController(enabled=False),
        )
        mc_2 = self.models.ManagedCluster(location="test_location", storage_profile=storage_profile_2)
        dec_2.context.attach_mc(mc_2)
        dec_mc_2 = dec_2.update_storage_profile(mc_2)
        ground_truth_storage_profile_2 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=self.models.ManagedClusterStorageProfileDiskCSIDriver(enabled=True),
            file_csi_driver=self.models.ManagedClusterStorageProfileFileCSIDriver(enabled=True),
            snapshot_controller=self.models.ManagedClusterStorageProfileSnapshotController(enabled=True),
        )
        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location", storage_profile=ground_truth_storage_profile_2
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_update_workload_auto_scaler_profile(self):
        # Throws exception when incorrect mc object is passed.
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        with self.assertRaisesRegex(CLIInternalError, "^Unexpected mc object with type '<class 'NoneType'>'\.$"):
            dec_1.update_workload_auto_scaler_profile(None)

        # Throws exception when the mc object passed does not match the one in context.
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        with self.assertRaisesRegex(CLIInternalError, "^Inconsistent state detected\. The incoming `mc` is not the same as the `mc` in the context\.$"):
            mc_in = self.models.ManagedCluster(location="test_location")
            dec_2.update_workload_auto_scaler_profile(mc_in)

        # Leaves profile as None without raw parameters.
        dec_3 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        mc_in = self.models.ManagedCluster(location="test_location")
        dec_3.context.attach_mc(mc_in)
        mc_out = dec_3.update_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertIsNone(mc_out.workload_auto_scaler_profile)

        # Leaves existing profile untouched without raw parameters.
        dec_4 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {}, CUSTOM_MGMT_AKS_PREVIEW)
        profile = self.models.ManagedClusterWorkloadAutoScalerProfile(
            keda = self.models.ManagedClusterWorkloadAutoScalerProfileKeda(enabled=True))
        mc_in = self.models.ManagedCluster(location="test_location", workload_auto_scaler_profile = profile)
        dec_4.context.attach_mc(mc_in)
        mc_out = dec_4.update_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertEqual(mc_out.workload_auto_scaler_profile, profile)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile.keda)
        self.assertTrue(mc_out.workload_auto_scaler_profile.keda.enabled)

        # Enables keda when enable_keda is True.
        dec_5 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {"enable_keda": True}, CUSTOM_MGMT_AKS_PREVIEW)
        mc_in = self.models.ManagedCluster(location="test_location")
        dec_5.context.attach_mc(mc_in)
        mc_out = dec_5.update_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile.keda)
        self.assertTrue(mc_out.workload_auto_scaler_profile.keda.enabled)

        # Enables keda in existing profile when enable_keda is True.
        dec_6 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {"enable_keda": True}, CUSTOM_MGMT_AKS_PREVIEW)
        profile = self.models.ManagedClusterWorkloadAutoScalerProfile(
            keda = self.models.ManagedClusterWorkloadAutoScalerProfileKeda(enabled=False))
        mc_in = self.models.ManagedCluster(location="test_location", workload_auto_scaler_profile = profile)
        dec_6.context.attach_mc(mc_in)
        mc_out = dec_6.update_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertEqual(mc_out.workload_auto_scaler_profile, profile)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile.keda)
        self.assertTrue(mc_out.workload_auto_scaler_profile.keda.enabled)

        # Disables keda when disable_keda is True.
        dec_7 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {"disable_keda": True}, CUSTOM_MGMT_AKS_PREVIEW)
        mc_in = self.models.ManagedCluster(location="test_location")
        dec_7.context.attach_mc(mc_in)
        mc_out = dec_7.update_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile.keda)
        self.assertFalse(mc_out.workload_auto_scaler_profile.keda.enabled)

        # Disables keda in existing profile when disable_keda is True.
        dec_8 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {"disable_keda": True}, CUSTOM_MGMT_AKS_PREVIEW)
        profile = self.models.ManagedClusterWorkloadAutoScalerProfile(
            keda = self.models.ManagedClusterWorkloadAutoScalerProfileKeda(enabled=True))
        mc_in = self.models.ManagedCluster(location="test_location", workload_auto_scaler_profile = profile)
        dec_8.context.attach_mc(mc_in)
        mc_out = dec_8.update_workload_auto_scaler_profile(mc_in)
        self.assertEqual(mc_out, mc_in)
        self.assertEqual(mc_out.workload_auto_scaler_profile, profile)
        self.assertIsNotNone(mc_out.workload_auto_scaler_profile.keda)
        self.assertFalse(mc_out.workload_auto_scaler_profile.keda.enabled)

        # Throws exception when both enable_keda and disable_keda are True.
        dec_9 = AKSPreviewManagedClusterUpdateDecorator(self.cmd, self.client, {"enable_keda": True, "disable_keda": True}, CUSTOM_MGMT_AKS_PREVIEW)
        mc_in = self.models.ManagedCluster(location="test_location")
        dec_9.context.attach_mc(mc_in)
        with self.assertRaises(MutuallyExclusiveArgumentError):
            mc_out = dec_9.update_workload_auto_scaler_profile(mc_in)

    def test_update_defender(self):
        # enable
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {
                "enable_defender": True,
                "defender_config": get_test_data_file_path(
                    "defenderconfig.json"
                ),
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_1 = self.models.ManagedCluster(location="test_location")
        dec_1.context.attach_mc(mc_1)
        dec_1.context.set_intermediate(
            "subscription_id", "test_subscription_id"
        )

        dec_mc_1 = dec_1.update_defender(mc_1)

        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            security_profile=self.models.ManagedClusterSecurityProfile(
                defender=self.models.ManagedClusterSecurityProfileDefender(
                    log_analytics_workspace_resource_id="test_workspace_resource_id",
                    security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                        enabled=True
                    ),
                )
            ),
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        # disable
        dec_2 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            {"disable_defender": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(
            location="test_location",
            security_profile=self.models.ManagedClusterSecurityProfile(
                defender=self.models.ManagedClusterSecurityProfileDefender(
                    log_analytics_workspace_resource_id="test_workspace_resource_id",
                    security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                        enabled=True
                    ),
                )
            ),
        )
        dec_2.context.attach_mc(mc_2)
        dec_2.context.set_intermediate(
            "subscription_id", "test_subscription_id"
        )

        dec_mc_2 = dec_2.update_defender(mc_2)

        ground_truth_mc_2 = self.models.ManagedCluster(
            location="test_location",
            security_profile=self.models.ManagedClusterSecurityProfile(
                defender=self.models.ManagedClusterSecurityProfileDefender(
                    security_monitoring=self.models.ManagedClusterSecurityProfileDefenderSecurityMonitoring(
                        enabled=False
                    ),
                )
            ),
        )
        self.assertEqual(dec_mc_2, ground_truth_mc_2)

    def test_update_mc_profile_preview(self):
        import inspect

        from azext_aks_preview.custom import aks_update

        optional_params = {}
        positional_params = []
        for _, v in inspect.signature(aks_update).parameters.items():
            if v.default != v.empty:
                optional_params[v.name] = v.default
            else:
                positional_params.append(v.name)
        ground_truth_positional_params = [
            "cmd",
            "client",
            "resource_group_name",
            "name",
        ]
        self.assertEqual(positional_params, ground_truth_positional_params)

        # prepare a dictionary of default parameters
        raw_param_dict = {
            "resource_group_name": "test_rg_name",
            "name": "test_name",
        }
        raw_param_dict.update(optional_params)

        # default value in `update`
        dec_1 = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        mock_profile = Mock(get_subscription_id=Mock(return_value="1234-5678-9012"))
        mock_existing_mc = self.models.ManagedCluster(
            location="test_location",
            agent_pool_profiles=[
                self.models.ManagedClusterAgentPoolProfile(
                    name="nodepool1",
                )
            ],
            network_profile=self.models.ContainerServiceNetworkProfile(
                load_balancer_sku="standard",
            ),
            identity=self.models.ManagedClusterIdentity(type="SystemAssigned"),
            identity_profile={
                "kubeletidentity": self.models.UserAssignedIdentity(
                    resource_id="test_resource_id",
                    client_id="test_client_id",
                    object_id="test_object_id",
                )
            },
        )
        with patch(
            "azure.cli.command_modules.acs.managed_cluster_decorator.get_rg_location",
            return_value="test_location",
        ), patch("azure.cli.command_modules.acs.managed_cluster_decorator.Profile", return_value=mock_profile,), patch(
            "azext_aks_preview.managed_cluster_decorator.AKSPreviewManagedClusterUpdateDecorator.check_raw_parameters",
            return_value=True,
        ), patch.object(
            self.client, "get", return_value=mock_existing_mc
        ):
            dec_mc_1 = dec_1.update_mc_profile_preview()

        ground_truth_agent_pool_profile_1 = self.models.ManagedClusterAgentPoolProfile(
            name="nodepool1",
        )
        ground_truth_network_profile_1 = self.models.ContainerServiceNetworkProfile(
            load_balancer_sku="standard",
        )
        ground_truth_identity_1 = self.models.ManagedClusterIdentity(type="SystemAssigned")
        ground_truth_identity_profile_1 = {
            "kubeletidentity": self.models.UserAssignedIdentity(
                resource_id="test_resource_id",
                client_id="test_client_id",
                object_id="test_object_id",
            )
        }
        ground_truth_storage_profile_1 = self.models.ManagedClusterStorageProfile(
            disk_csi_driver=None,
            file_csi_driver=None,
            snapshot_controller=None,
        )
        ground_truth_mc_1 = self.models.ManagedCluster(
            location="test_location",
            agent_pool_profiles=[ground_truth_agent_pool_profile_1],
            network_profile=ground_truth_network_profile_1,
            identity=ground_truth_identity_1,
            identity_profile=ground_truth_identity_profile_1,
            storage_profile=ground_truth_storage_profile_1,
        )
        self.assertEqual(dec_mc_1, ground_truth_mc_1)

        dec_1.context.raw_param.print_usage_statistics()


if __name__ == "__main__":
    unittest.main()
