# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._consts import CONST_WORKLOAD_RUNTIME_OCI_CONTAINER
from azext_aks_preview.agentpool_decorator import (
    AKSPreviewAgentPoolAddDecorator,
    AKSPreviewAgentPoolContext,
    AKSPreviewAgentPoolModels,
    AKSPreviewAgentPoolUpdateDecorator,
)
from azext_aks_preview.tests.latest.utils import get_test_data_file_path
from azure.cli.command_modules.acs._consts import (
    CONST_DEFAULT_NODE_OS_TYPE,
    CONST_DEFAULT_NODE_VM_SIZE,
    CONST_NODEPOOL_MODE_SYSTEM,
    CONST_NODEPOOL_MODE_USER,
    CONST_SCALE_DOWN_MODE_DELETE,
    CONST_VIRTUAL_MACHINE_SCALE_SETS,
    AgentPoolDecoratorMode,
    DecoratorMode,
)
from azure.cli.core.azclierror import (
    AzureInternalError,
    AzCLIError,
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    NoTTYError,
    RequiredArgumentMissingError,
    UnknownError,
)
from azure.cli.command_modules.acs.agentpool_decorator import AKSAgentPoolParamDict
from azure.cli.command_modules.acs.tests.latest.mocks import MockCLI, MockClient, MockCmd
from azure.cli.core.azclierror import CLIInternalError, InvalidArgumentValueError
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterModels,
    AKSPreviewManagedClusterContext,
    AKSPreviewAgentPoolAddDecorator,
)
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azure.cli.command_modules.acs.managed_cluster_decorator import AKSManagedClusterParamDict
import importlib
from azext_aks_preview.tests.latest.utils import get_test_data_file_path


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

    def test_get_node_resource_group(self):
        # default
        ctx_1 = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict({"node_resource_group": None}),
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_node_resource_group(), None)
        mc = self.models.ManagedCluster(
            location="test_location",
            node_resource_group="test_node_resource_group",
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_node_resource_group(), "test_node_resource_group")

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

    def test_get_workload_identity_profile__update_with_enable_and_disable(self):
        ctx = AKSPreviewManagedClusterContext(
            self.cmd,
            AKSManagedClusterParamDict(
                {
                    "enable_workload_identity": True,
                    "disable_workload_identity": True,
                }
            ),
            self.models,
            decorator_mode=DecoratorMode.UPDATE,
        )
        ctx.attach_mc(self.models.ManagedCluster(location="test_location"))
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx.get_workload_identity_profile()

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
                        "disable_workload_identity": True,
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
        agentpool_ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"kubernetes_version": ""}),
            self.models,
            DecoratorMode.CREATE,
            AgentPoolDecoratorMode.MANAGED_CLUSTER,
        )
        ctx_1.attach_agentpool_context(agentpool_ctx_1)
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
        agentpool_ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"kubernetes_version": "", "snapshot_id": "test_snapshot_id"}),
            self.models,
            DecoratorMode.CREATE,
            AgentPoolDecoratorMode.MANAGED_CLUSTER,
        )
        ctx_2.attach_agentpool_context(agentpool_ctx_2)
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
        agentpool_ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {
                    "kubernetes_version": "custom_kubernetes_version",
                    "snapshot_id": "test_snapshot_id",
                }
            ),
            self.models,
            DecoratorMode.CREATE,
            AgentPoolDecoratorMode.MANAGED_CLUSTER,
        )
        ctx_3.attach_agentpool_context(agentpool_ctx_3)
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
        agentpool_ctx_4 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {
                    "kubernetes_version": "",
                    "snapshot_id": "test_snapshot_id",
                    "cluster_snapshot_id": "test_cluster_snapshot_id",
                }
            ),
            self.models,
            DecoratorMode.CREATE,
            AgentPoolDecoratorMode.MANAGED_CLUSTER,
        )
        ctx_4.attach_agentpool_context(agentpool_ctx_4)
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
        agentpool_ctx_5 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {
                    "kubernetes_version": "custom_kubernetes_version",
                    "snapshot_id": "test_snapshot_id",
                    "cluster_snapshot_id": "test_cluster_snapshot_id",
                }
            ),
            self.models,
            DecoratorMode.CREATE,
            AgentPoolDecoratorMode.MANAGED_CLUSTER,
        )
        ctx_5.attach_agentpool_context(agentpool_ctx_5)
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


class AKSPreviewManagedClusterCreateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()


class AKSPreviewManagedClusterUpdateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()


if __name__ == "__main__":
    unittest.main()
