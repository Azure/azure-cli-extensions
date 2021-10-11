# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.command_modules.acs._consts import (
    DecoratorMode,
)
from azure.cli.core.azclierror import (
    ArgumentUsageError,
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    NoTTYError,
    RequiredArgumentMissingError,
    UnknownError,
)
from azext_aks_preview.decorator import (
    AKSPreviewContext,
    AKSPreviewCreateDecorator,
    AKSPreviewModels,
    AKSPreviewUpdateDecorator,
)
from azext_aks_preview.tests.latest.mocks import (
    MockCLI,
    MockClient,
    MockCmd,
)
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.__init__ import register_aks_preview_resource_type

class AKSPreviewModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)

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
            name="test_nodepool_name", enable_fips=True,
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
            name="test_nodepool_name", workload_runtime="test_mc_workload_runtime",
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_workload_runtime(), "test_mc_workload_runtime")

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
            name="test_nodepool_name", gpu_instance_profile="test_mc_gpu_instance_profile",
        )
        mc = self.models.ManagedCluster(
            location="test_location", agent_pool_profiles=[agent_pool_profile]
        )
        ctx_1.attach_mc(mc)
        self.assertEqual(ctx_1.get_gpu_instance_profile(), "test_mc_gpu_instance_profile")

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
                "enable_fips_image": False,
                "enable_node_public_ip": False,
                "node_public_ip_prefix_id": None,
                "enable_encryption_at_host": False,
                "enable_ultra_ssd": False,
                "max_pods": 0,
                "node_osdisk_size": 0,
                "node_osdisk_type": None,
                "enable_cluster_autoscaler": False,
                "min_count": None,
                "max_count": None,
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
            vnet_subnet_id=None,
            proximity_placement_group_id=None,
            availability_zones=None,
            enable_node_public_ip=False,
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
        )
        ground_truth_mc_1 = self.models.ManagedCluster(location="test_location")
        ground_truth_mc_1.agent_pool_profiles = [agent_pool_profile_1]
        self.assertEqual(dec_mc_1, ground_truth_mc_1)


class AKSPreviewUpdateDecoratorTestCase(unittest.TestCase):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.models = AKSPreviewModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)
        self.client = MockClient()
