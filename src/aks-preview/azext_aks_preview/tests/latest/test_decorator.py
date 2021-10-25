# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import importlib
import unittest
from unittest.mock import patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.decorator import (
    AKSPreviewContext,
    AKSPreviewCreateDecorator,
    AKSPreviewModels,
    AKSPreviewUpdateDecorator,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockClient, MockCmd
from azext_aks_preview.tests.latest.test_aks_commands import _get_test_data_file
from azure.cli.command_modules.acs._consts import DecoratorMode
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    NoTTYError,
    RequiredArgumentMissingError,
    UnknownError,
)
from azext_aks_preview._consts import (
    ADDONS,
    CONST_ACC_SGX_QUOTE_HELPER_ENABLED,
    CONST_AZURE_POLICY_ADDON_NAME,
    CONST_CONFCOM_ADDON_NAME,
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
    CONST_OPEN_SERVICE_MESH_ADDON_NAME,
    CONST_VIRTUAL_NODE_ADDON_NAME,
    CONST_VIRTUAL_NODE_SUBNET_NAME,
    CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME,
    CONST_GITOPS_ADDON_NAME,
    CONST_SECRET_ROTATION_ENABLED,
    CONST_MONITORING_USING_AAD_MSI_AUTH,
)


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


class AKSPreviewContextTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)

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
            "CONST_GITOPS_ADDON_NAME": CONST_GITOPS_ADDON_NAME,
            "CONST_SECRET_ROTATION_ENABLED": CONST_SECRET_ROTATION_ENABLED,
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

    def test_get_enable_secret_rotation(self):
        # default
        ctx_1 = AKSPreviewContext(
            self.cmd,
            {
                "enable_secret_rotation": False,
            },
            self.models,
            decorator_mode=DecoratorMode.CREATE,
        )
        self.assertEqual(ctx_1.get_enable_secret_rotation(), False)
        addon_profiles_1 = {
            CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={CONST_SECRET_ROTATION_ENABLED: "true"},
            )
        }
        mc = self.models.ManagedCluster(
            location="test_location", addon_profiles=addon_profiles_1
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_enable_secret_rotation(), True)


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
                "os_sku": "test_os_sku",
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
            },
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc_2 = self.models.ManagedCluster(location="test_location")
        dec_mc_2 = dec_2.set_up_agent_pool_profiles(mc_2)
        agent_pool_profile_2 = self.models.ManagedClusterAgentPoolProfile(
            # Must be 12 chars or less before ACS RP adds to it
            name="test_np_name",
            tags={"k1": "v1"},
            node_labels={"k1": "v1", "k2": "v2"},
            count=10,
            vm_size="Standard_DSx_vy",
            os_type="Linux",
            os_sku="test_os_sku",
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

    def test_build_azure_keyvault_secrets_provider_addon_profile(self):
        # default
        dec_1 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {"enable_secret_rotation": False},
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        azure_keyvault_secrets_provider_addon_profile = dec_1.build_azure_keyvault_secrets_provider_addon_profile()
        ground_truth_azure_keyvault_secrets_provider_addon_profile = (
            self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={CONST_SECRET_ROTATION_ENABLED: "false"}
            )
        )
        self.assertEqual(
            azure_keyvault_secrets_provider_addon_profile, ground_truth_azure_keyvault_secrets_provider_addon_profile
        )

        # custom value
        dec_2 = AKSPreviewCreateDecorator(
            self.cmd,
            self.client,
            {"enable_secret_rotation": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )

        azure_keyvault_secrets_provider_addon_profile = dec_2.build_azure_keyvault_secrets_provider_addon_profile()
        ground_truth_azure_keyvault_secrets_provider_addon_profile = (
            self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={CONST_SECRET_ROTATION_ENABLED: "true"}
            )
        )
        self.assertEqual(
            azure_keyvault_secrets_provider_addon_profile, ground_truth_azure_keyvault_secrets_provider_addon_profile
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
                "appgw_subnet_prefix": None,
                "enable_msi_auth_for_monitoring": False,
                "enable_secret_rotation": False,
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
                "enable_addons": "monitoring,ingress-appgw,gitops,azure-keyvault-secrets-provider",
                "workspace_resource_id": "test_workspace_resource_id",
                "enable_msi_auth_for_monitoring": True,
                "appgw_name": "test_appgw_name",
                "appgw_subnet_prefix": "test_appgw_subnet_prefix",
                "appgw_id": "test_appgw_id",
                "appgw_subnet_id": "test_appgw_subnet_id",
                "appgw_watch_namespace": "test_appgw_watch_namespace",
                "enable_secret_rotation": True,
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
            CONST_AZURE_KEYVAULT_SECRETS_PROVIDER_ADDON_NAME: self.models.ManagedClusterAddonProfile(
                enabled=True,
                config={CONST_SECRET_ROTATION_ENABLED: "true"},
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

    def test_construct_preview_mc_profile(self):
        pass


class AKSPreviewUpdateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()
