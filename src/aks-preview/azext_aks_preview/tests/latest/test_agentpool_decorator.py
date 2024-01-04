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
from azure.cli.command_modules.acs.agentpool_decorator import AKSAgentPoolParamDict
from azure.cli.command_modules.acs.tests.latest.mocks import (
    MockCLI,
    MockClient,
    MockCmd,
)
from azure.cli.core.azclierror import (
    CLIInternalError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
)


class AKSPreviewAgentPoolContextCommonTestCase(unittest.TestCase):
    def _remove_defaults_in_agentpool(self, agentpool):
        self.defaults_in_agentpool = {}
        for attr_name, attr_value in vars(agentpool).items():
            if (
                not attr_name.startswith("_")
                and attr_name != "name"
                and attr_value is not None
            ):
                self.defaults_in_agentpool[attr_name] = attr_value
                setattr(agentpool, attr_name, None)
        return agentpool

    def _restore_defaults_in_agentpool(self, agentpool):
        for key, value in self.defaults_in_agentpool.items():
            if getattr(agentpool, key, None) is None:
                setattr(agentpool, key, value)
        return agentpool

    def create_initialized_agentpool_instance(
        self,
        nodepool_name="nodepool1",
        remove_defaults=True,
        restore_defaults=True,
        **kwargs
    ):
        """Helper function to create a properly initialized agentpool instance.

        :return: the AgentPool object
        """
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            agentpool = self.models.UnifiedAgentPoolModel(name=nodepool_name)
        else:
            agentpool = self.models.UnifiedAgentPoolModel()
            agentpool.name = nodepool_name

        # remove defaults
        if remove_defaults:
            self._remove_defaults_in_agentpool(agentpool)

        # set properties
        for key, value in kwargs.items():
            setattr(agentpool, key, value)

        # resote defaults
        if restore_defaults:
            self._restore_defaults_in_agentpool(agentpool)
        return agentpool

    def common_get_zones(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"zone": None, "node_zones": "test_node_zones"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_zones(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            availability_zones=["test_mc_zones1", "test_mc_zones2"]
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_zones(), ["test_mc_zones1", "test_mc_zones2"])

        # custom value
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {"zones": "test_zones", "node_zones": "test_node_zones"}
            ),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_zones(), "test_zones")

    def common_get_crg_id(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"crg_id": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_crg_id(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            capacity_reservation_group_id="test_capacity_reservation_group_id"
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_crg_id(), "test_capacity_reservation_group_id")

    def common_get_message_of_the_day(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"message_of_the_day": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_message_of_the_day(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            message_of_the_day="test_message_of_the_day"
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_message_of_the_day(), "test_message_of_the_day")

        # custom
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {"message_of_the_day": get_test_data_file_path("motd.txt")}
            ),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(
            ctx_2.get_message_of_the_day(),
            "VU5BVVRIT1JJWkVEIEFDQ0VTUyBUTyBUSElTIERFVklDRSBJUyBQUk9ISUJJVEVECgpZb3UgbXVzdCBoYXZlIGV4cGxpY2l0LCBhdXRob3JpemVkIHBlcm1pc3Npb24gdG8gYWNjZXNzIG9yIGNvbmZpZ3VyZSB0aGlzIGRldmljZS4gVW5hdXRob3JpemVkIGF0dGVtcHRzIGFuZCBhY3Rpb25zIHRvIGFjY2VzcyBvciB1c2UgdGhpcyBzeXN0ZW0gbWF5IHJlc3VsdCBpbiBjaXZpbCBhbmQvb3IgY3JpbWluYWwgcGVuYWx0aWVzLiBBbGwgYWN0aXZpdGllcyBwZXJmb3JtZWQgb24gdGhpcyBkZXZpY2UgYXJlIGxvZ2dlZCBhbmQgbW9uaXRvcmVkLgo=",
        )

        # custom
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"message_of_the_day": "fake-path"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        with self.assertRaises(InvalidArgumentValueError):
            ctx_3.get_message_of_the_day()

    def common_get_gpu_instance_profile(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"gpu_instance_profile": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_gpu_instance_profile(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            gpu_instance_profile="test_gpu_instance_profile"
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_gpu_instance_profile(), "test_gpu_instance_profile")

    def common_get_workload_runtime(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"workload_runtime": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(
            ctx_1.get_workload_runtime(), CONST_WORKLOAD_RUNTIME_OCI_CONTAINER
        )
        agentpool_1 = self.create_initialized_agentpool_instance(
            workload_runtime="test_workload_runtime"
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_workload_runtime(), "test_workload_runtime")

    def common_get_enable_custom_ca_trust(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_custom_ca_trust": True}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_enable_custom_ca_trust(), True)
        agentpool_1 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=False
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_enable_custom_ca_trust(), False)

        # custom
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_custom_ca_trust": True}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_enable_custom_ca_trust(), True)
        agentpool_2 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=False
        )
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_enable_custom_ca_trust(), True)

        # custom
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {"enable_custom_ca_trust": True, "disable_custom_ca_trust": True}
            ),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_3.get_enable_custom_ca_trust()

    def common_get_disable_custom_ca_trust(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"disable_custom_ca_trust": True}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_disable_custom_ca_trust(), True)
        agentpool_1 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=True
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_disable_custom_ca_trust(), True)

        # custom
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {"enable_custom_ca_trust": True, "disable_custom_ca_trust": True}
            ),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        with self.assertRaises(MutuallyExclusiveArgumentError):
            ctx_2.get_disable_custom_ca_trust()

    def common_get_enable_artifact_streaming(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_artifact_streaming": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_enable_artifact_streaming(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            artifact_streaming_profile=self.models.AgentPoolArtifactStreamingProfile(
                enabled=True
            )
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_enable_artifact_streaming(), True)

        # default
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_artifact_streaming": None}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_enable_artifact_streaming(), None)
        agentpool_2 = self.create_initialized_agentpool_instance(
            artifact_streaming_profile=self.models.AgentPoolArtifactStreamingProfile(
                enabled=True
            )
        )
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_enable_artifact_streaming(), None)

    def common_get_os_sku(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"os_sku": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_os_sku(), None)
        agentpool = self.create_initialized_agentpool_instance(os_sku="test_os_sku")
        ctx_1.attach_agentpool(agentpool)
        self.assertEqual(ctx_1.get_os_sku(), "test_os_sku")

        # custom value
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"os_sku": None, "snapshot_id": "test_snapshot_id"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        mock_snapshot = Mock(os_sku="test_os_sku")
        with patch(
            "azext_aks_preview.agentpool_decorator.get_nodepool_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_2.get_os_sku(), "test_os_sku")

        # custom value
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {
                    "os_sku": "custom_os_sku",
                    "snapshot_id": "test_snapshot_id",
                }
            ),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        mock_snapshot = Mock(os_sku="test_os_sku")
        with patch(
            "azext_aks_preview.agentpool_decorator.get_nodepool_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_3.get_os_sku(), "custom_os_sku")

        # custom value
        ctx_4 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {
                    "os_sku": "custom_os_sku",
                }
            ),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        agentpool_4 = self.create_initialized_agentpool_instance(os_sku="test_os_sku")
        ctx_4.attach_agentpool(agentpool_4)
        self.assertEqual(ctx_4.get_os_sku(), "custom_os_sku")

        # custom value
        ctx_5 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"os_sku": None}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        agentpool_5 = self.create_initialized_agentpool_instance(os_sku="test_os_sku")
        ctx_5.attach_agentpool(agentpool_5)
        self.assertEqual(ctx_5.get_os_sku(), None)


class AKSPreviewAgentPoolContextStandaloneModeTestCase(
    AKSPreviewAgentPoolContextCommonTestCase
):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.resource_type = CUSTOM_MGMT_AKS_PREVIEW
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.STANDALONE
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )

    def test_get_zones(self):
        self.common_get_zones()

    def test_get_crg_id(self):
        self.common_get_crg_id()

    def test_get_message_of_the_day(self):
        self.common_get_message_of_the_day()

    def test_get_gpu_instance_profile(self):
        self.common_get_gpu_instance_profile()

    def test_get_workload_runtime(self):
        self.common_get_workload_runtime()

    def test_get_enable_custom_ca_trust(self):
        self.common_get_enable_custom_ca_trust()

    def test_get_disable_custom_ca_trust(self):
        self.common_get_disable_custom_ca_trust()

    def test_get_enable_artifact_streaming(self):
        self.common_get_enable_artifact_streaming()

    def test_get_os_sku(self):
        self.common_get_os_sku()


class AKSPreviewAgentPoolContextManagedClusterModeTestCase(
    AKSPreviewAgentPoolContextCommonTestCase
):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.resource_type = CUSTOM_MGMT_AKS_PREVIEW
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.MANAGED_CLUSTER
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )

    def test_get_zones(self):
        self.common_get_zones()

    def test_get_crg_id(self):
        self.common_get_crg_id()

    def test_get_message_of_the_day(self):
        self.common_get_message_of_the_day()

    def test_get_gpu_instance_profile(self):
        self.common_get_gpu_instance_profile()

    def test_get_workload_runtime(self):
        self.common_get_workload_runtime()

    def test_get_enable_custom_ca_trust(self):
        self.common_get_enable_custom_ca_trust()

    def test_get_disable_custom_ca_trust(self):
        self.common_get_disable_custom_ca_trust()

    def test_get_enable_artifact_streaming(self):
        self.common_get_enable_artifact_streaming()

    def test_get_os_sku(self):
        self.common_get_os_sku()


class AKSPreviewAgentPoolAddDecoratorCommonTestCase(unittest.TestCase):
    def _remove_defaults_in_agentpool(self, agentpool):
        self.defaults_in_agentpool = {}
        for attr_name, attr_value in vars(agentpool).items():
            if (
                not attr_name.startswith("_")
                and attr_name != "name"
                and attr_value is not None
            ):
                self.defaults_in_agentpool[attr_name] = attr_value
                setattr(agentpool, attr_name, None)
        return agentpool

    def _restore_defaults_in_agentpool(self, agentpool):
        for key, value in self.defaults_in_agentpool.items():
            if getattr(agentpool, key, None) is None:
                setattr(agentpool, key, value)
        return agentpool

    def create_initialized_agentpool_instance(
        self,
        nodepool_name="nodepool1",
        remove_defaults=True,
        restore_defaults=True,
        **kwargs
    ):
        """Helper function to create a properly initialized agentpool instance.

        :return: the AgentPool object
        """
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            agentpool = self.models.UnifiedAgentPoolModel(name=nodepool_name)
        else:
            agentpool = self.models.UnifiedAgentPoolModel()
            agentpool.name = nodepool_name

        # remove defaults
        if remove_defaults:
            self._remove_defaults_in_agentpool(agentpool)

        # set properties
        for key, value in kwargs.items():
            setattr(agentpool, key, value)

        # resote defaults
        if restore_defaults:
            self._restore_defaults_in_agentpool(agentpool)
        return agentpool

    def common_set_up_preview_vm_properties(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"crg_id": "test_crg_id"},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_preview_vm_properties(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_preview_vm_properties(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            capacity_reservation_group_id="test_crg_id"
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_motd(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"message_of_the_day": get_test_data_file_path("motd.txt")},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_motd(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_motd(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            message_of_the_day="VU5BVVRIT1JJWkVEIEFDQ0VTUyBUTyBUSElTIERFVklDRSBJUyBQUk9ISUJJVEVECgpZb3UgbXVzdCBoYXZlIGV4cGxpY2l0LCBhdXRob3JpemVkIHBlcm1pc3Npb24gdG8gYWNjZXNzIG9yIGNvbmZpZ3VyZSB0aGlzIGRldmljZS4gVW5hdXRob3JpemVkIGF0dGVtcHRzIGFuZCBhY3Rpb25zIHRvIGFjY2VzcyBvciB1c2UgdGhpcyBzeXN0ZW0gbWF5IHJlc3VsdCBpbiBjaXZpbCBhbmQvb3IgY3JpbWluYWwgcGVuYWx0aWVzLiBBbGwgYWN0aXZpdGllcyBwZXJmb3JtZWQgb24gdGhpcyBkZXZpY2UgYXJlIGxvZ2dlZCBhbmQgbW9uaXRvcmVkLgo=",
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_gpu_propertes(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {
                "gpu_instance_profile": "test_gpu_instance_profile",
                "workload_runtime": "test_workload_runtime",
            },
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_gpu_properties(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_gpu_properties(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            gpu_instance_profile="test_gpu_instance_profile",
            workload_runtime="test_workload_runtime",
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_custom_ca_trust(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"enable_custom_ca_trust": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_custom_ca_trust(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_custom_ca_trust(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=True,
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_artifact_streaming(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"enable_artifact_streaming": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_artifact_streaming(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_artifact_streaming(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            artifact_streaming_profile=self.models.AgentPoolArtifactStreamingProfile(
                enabled=True
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)


class AKSPreviewAgentPoolAddDecoratorStandaloneModeTestCase(
    AKSPreviewAgentPoolAddDecoratorCommonTestCase
):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.resource_type = CUSTOM_MGMT_AKS_PREVIEW
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.STANDALONE
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )
        self.client = MockClient()

    def test_set_up_preview_vm_properties(self):
        self.common_set_up_preview_vm_properties()

    def test_set_up_motd(self):
        self.common_set_up_motd()

    def test_set_up_gpu_propertes(self):
        self.common_set_up_gpu_propertes()

    def test_set_up_custom_ca_trust(self):
        self.common_set_up_custom_ca_trust()

    def test_set_up_artifact_streaming(self):
        self.common_set_up_artifact_streaming()

    def test_construct_agentpool_profile_preview(self):
        import inspect

        from azext_aks_preview.custom import aks_agentpool_add

        optional_params = {}
        positional_params = []
        for _, v in inspect.signature(aks_agentpool_add).parameters.items():
            if v.default != v.empty:
                optional_params[v.name] = v.default
            else:
                positional_params.append(v.name)
        ground_truth_positional_params = [
            "cmd",
            "client",
            "resource_group_name",
            "cluster_name",
            "nodepool_name",
        ]
        self.assertEqual(positional_params, ground_truth_positional_params)

        # prepare a dictionary of default parameters
        raw_param_dict = {
            "resource_group_name": "test_rg_name",
            "cluster_name": "test_cluster_name",
            "nodepool_name": "test_nodepool_name",
        }
        raw_param_dict.update(optional_params)

        # default value in `aks nodepool add`
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        with patch(
            "azext_aks_preview.agentpool_decorator.cf_agent_pools",
            return_value=Mock(list=Mock(return_value=[])),
        ):
            dec_agentpool_1 = dec_1.construct_agentpool_profile_preview()

        ground_truth_upgrade_settings_1 = self.models.AgentPoolUpgradeSettings()
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            nodepool_name="test_nodepool_name",
            vm_size=CONST_DEFAULT_NODE_VM_SIZE,
            os_type=CONST_DEFAULT_NODE_OS_TYPE,
            enable_node_public_ip=False,
            enable_auto_scaling=False,
            count=3,
            node_taints=[],
            os_disk_size_gb=0,
            upgrade_settings=ground_truth_upgrade_settings_1,
            type_properties_type=CONST_VIRTUAL_MACHINE_SCALE_SETS,
            enable_encryption_at_host=False,
            enable_ultra_ssd=False,
            enable_fips=False,
            mode=CONST_NODEPOOL_MODE_USER,
            scale_down_mode=CONST_SCALE_DOWN_MODE_DELETE,
            workload_runtime=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
            enable_custom_ca_trust=False,
            network_profile=self.models.AgentPoolNetworkProfile(),
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_1.context.raw_param.print_usage_statistics()


class AKSPreviewAgentPoolAddDecoratorManagedClusterModeTestCase(
    AKSPreviewAgentPoolAddDecoratorCommonTestCase
):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.resource_type = CUSTOM_MGMT_AKS_PREVIEW
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.MANAGED_CLUSTER
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )
        self.client = MockClient()

    def test_set_up_preview_vm_properties(self):
        self.common_set_up_preview_vm_properties()

    def test_set_up_motd(self):
        self.common_set_up_motd()

    def test_set_up_gpu_propertes(self):
        self.common_set_up_gpu_propertes()

    def test_set_up_custom_ca_trust(self):
        self.common_set_up_custom_ca_trust()

    def test_set_up_artifact_streaming(self):
        self.common_set_up_artifact_streaming()

    def test_construct_agentpool_profile_preview(self):
        import inspect

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

        # prepare a dictionary of default parameters
        raw_param_dict = {
            "resource_group_name": "test_rg_name",
            "name": "test_cluster_name",
            "ssh_key_value": None,
        }
        raw_param_dict.update(optional_params)

        # default value in `aks nodepool add`
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        with patch(
            "azure.cli.command_modules.acs.agentpool_decorator.cf_agent_pools",
            return_value=Mock(list=Mock(return_value=[])),
        ):
            dec_agentpool_1 = dec_1.construct_agentpool_profile_preview()

        upgrade_settings_1 = self.models.AgentPoolUpgradeSettings()
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            nodepool_name="nodepool1",
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
            network_profile=self.models.AgentPoolNetworkProfile(),
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_1.context.raw_param.print_usage_statistics()


class AKSPreviewAgentPoolUpdateDecoratorCommonTestCase(unittest.TestCase):
    def _remove_defaults_in_agentpool(self, agentpool):
        self.defaults_in_agentpool = {}
        for attr_name, attr_value in vars(agentpool).items():
            if (
                not attr_name.startswith("_")
                and attr_name != "name"
                and attr_value is not None
            ):
                self.defaults_in_agentpool[attr_name] = attr_value
                setattr(agentpool, attr_name, None)
        return agentpool

    def _restore_defaults_in_agentpool(self, agentpool):
        for key, value in self.defaults_in_agentpool.items():
            if getattr(agentpool, key, None) is None:
                setattr(agentpool, key, value)
        return agentpool

    def create_initialized_agentpool_instance(
        self,
        nodepool_name="nodepool1",
        remove_defaults=True,
        restore_defaults=True,
        **kwargs
    ):
        """Helper function to create a properly initialized agentpool instance.

        :return: the AgentPool object
        """
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            agentpool = self.models.UnifiedAgentPoolModel(name=nodepool_name)
        else:
            agentpool = self.models.UnifiedAgentPoolModel()
            agentpool.name = nodepool_name

        # remove defaults
        if remove_defaults:
            self._remove_defaults_in_agentpool(agentpool)

        # set properties
        for key, value in kwargs.items():
            setattr(agentpool, key, value)

        # resote defaults
        if restore_defaults:
            self._restore_defaults_in_agentpool(agentpool)
        return agentpool

    def common_update_custom_ca_trust(self):
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_custom_ca_trust": True, "disable_custom_ca_trust": False},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.update_custom_ca_trust(None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=False,
        )
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.update_custom_ca_trust(agentpool_1)
        grond_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=True,
        )
        self.assertEqual(dec_agentpool_1, grond_truth_agentpool_1)

        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_custom_ca_trust": False, "disable_custom_ca_trust": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_2.update_custom_ca_trust(None)
        agentpool_2 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=True,
        )
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_custom_ca_trust(agentpool_2)
        grond_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            enable_custom_ca_trust=False,
        )
        self.assertEqual(dec_agentpool_2, grond_truth_agentpool_2)

    def common_update_artifact_streaming(self):
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_artifact_streaming": None},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.update_artifact_streaming(None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            artifact_streaming_profile=self.models.AgentPoolArtifactStreamingProfile(
                enabled=True
            )
        )
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.update_artifact_streaming(agentpool_1)
        grond_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            artifact_streaming_profile=self.models.AgentPoolArtifactStreamingProfile(
                enabled=True
            )
        )
        self.assertEqual(dec_agentpool_1, grond_truth_agentpool_1)

        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_artifact_streaming": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_2.update_artifact_streaming(None)
        agentpool_2 = self.create_initialized_agentpool_instance()
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_artifact_streaming(agentpool_2)
        grond_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            artifact_streaming_profile=self.models.AgentPoolArtifactStreamingProfile(
                enabled=True
            )
        )
        self.assertEqual(dec_agentpool_2, grond_truth_agentpool_2)


class AKSPreviewAgentPoolUpdateDecoratorStandaloneModeTestCase(
    AKSPreviewAgentPoolUpdateDecoratorCommonTestCase
):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.resource_type = CUSTOM_MGMT_AKS_PREVIEW
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.STANDALONE
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )
        self.client = MockClient()

    def test_update_custom_ca_trust(self):
        self.common_update_custom_ca_trust()

    def test_update_artifact_streaming(self):
        self.common_update_artifact_streaming()

    def test_update_agentpool_profile_preview(self):
        import inspect

        from azext_aks_preview.custom import aks_agentpool_update

        optional_params = {}
        positional_params = []
        for _, v in inspect.signature(aks_agentpool_update).parameters.items():
            if v.default != v.empty:
                optional_params[v.name] = v.default
            else:
                positional_params.append(v.name)
        ground_truth_positional_params = [
            "cmd",
            "client",
            "resource_group_name",
            "cluster_name",
            "nodepool_name",
        ]
        self.assertEqual(positional_params, ground_truth_positional_params)

        # prepare a dictionary of default parameters
        raw_param_dict = {
            "resource_group_name": "test_rg_name",
            "cluster_name": "test_cluster_name",
            "nodepool_name": "test_nodepool_name",
        }
        raw_param_dict.update(optional_params)

        # default value in `aks nodepool update`
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        self.client.get = Mock(
            return_value=self.create_initialized_agentpool_instance(
                nodepool_name="test_nodepool_name"
            )
        )
        dec_agentpool_1 = dec_1.update_agentpool_profile_preview()
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            nodepool_name="test_nodepool_name",
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_1.context.raw_param.print_usage_statistics()


class AKSPreviewAgentPoolUpdateDecoratorManagedClusterModeTestCase(
    AKSPreviewAgentPoolUpdateDecoratorCommonTestCase
):
    def setUp(self):
        # manually register CUSTOM_MGMT_AKS_PREVIEW
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.resource_type = CUSTOM_MGMT_AKS_PREVIEW
        self.agentpool_decorator_mode = AgentPoolDecoratorMode.MANAGED_CLUSTER
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, self.resource_type, self.agentpool_decorator_mode
        )
        self.client = MockClient()

    def test_update_custom_ca_trust(self):
        self.common_update_custom_ca_trust()

    def test_update_artifact_streaming(self):
        self.common_update_artifact_streaming()

    def test_update_agentpool_profile_preview(self):
        import inspect

        from azure.cli.command_modules.acs.custom import aks_update

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
            "name": "test_cluster_name",
        }
        raw_param_dict.update(optional_params)

        # default value in `aks nodepool update`
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpools = [
            self.create_initialized_agentpool_instance(nodepool_name="test_nodepool_1"),
            self.create_initialized_agentpool_instance(nodepool_name="test_nodepool_2"),
        ]
        dec_agentpool_1 = dec_1.update_agentpool_profile_preview(agentpools)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            nodepool_name="test_nodepool_1",
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_1.context.raw_param.print_usage_statistics()


if __name__ == "__main__":
    unittest.main()
