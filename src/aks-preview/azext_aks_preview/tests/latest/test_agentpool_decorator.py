# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock, patch

from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview._consts import CONST_WORKLOAD_RUNTIME_OCI_CONTAINER, CONST_SSH_ACCESS_LOCALUSER, CONST_VIRTUAL_MACHINES
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
    CONST_DEFAULT_WINDOWS_NODE_VM_SIZE,
    CONST_DEFAULT_NODE_VM_SIZE,
)
from azext_aks_preview._consts import (
    CONST_DEFAULT_WINDOWS_NODE_VM_SIZE,
    CONST_DEFAULT_VMS_VM_SIZE,
    CONST_DEFAULT_WINDOWS_VMS_VM_SIZE,
    CONST_GPU_DRIVER_INSTALL,
    CONST_MANAGED_CLUSTER_SKU_NAME_BASE,
    CONST_MANAGED_CLUSTER_SKU_NAME_AUTOMATIC,
    CONST_GPU_DRIVER_NONE,
    CONST_NODEPOOL_MODE_MANAGEDSYSTEM,
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
from deepdiff import DeepDiff


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

    def common_get_pod_ip_allocation_mode(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"pod_ip_allocation_mode": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_pod_ip_allocation_mode(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            pod_ip_allocation_mode="StaticBlock"
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_pod_ip_allocation_mode(), None)

        # default to raw even if agentpool has different value
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"pod_ip_allocation_mode": "DynamicIndividual"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_pod_ip_allocation_mode(), "DynamicIndividual")
        agentpool_2 = self.create_initialized_agentpool_instance(
            pod_ip_allocation_mode="StaticBlock"
        )
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_pod_ip_allocation_mode(), "StaticBlock")

    def common_get_skip_gpu_driver_install(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"skip_gpu_driver_install": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_skip_gpu_driver_install(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            gpu_profile=self.models.GPUProfile(
                driver=CONST_GPU_DRIVER_NONE
            )
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_skip_gpu_driver_install(), True)

        # default
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"skip_gpu_driver_install": None}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_skip_gpu_driver_install(), None)
        agentpool_2 = self.create_initialized_agentpool_instance(
            artifact_streaming_profile=self.models.GPUProfile(
                driver=CONST_GPU_DRIVER_INSTALL
            )
        )
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_skip_gpu_driver_install(), None)

    def common_get_gpu_driver(self):
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"gpu_driver": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_gpu_driver(), None)
        agentpool = self.create_initialized_agentpool_instance(
            gpu_profile=self.models.GPUProfile(
                driver=CONST_GPU_DRIVER_INSTALL
            )
        )
        ctx_1.attach_agentpool(agentpool)
        self.assertEqual(ctx_1.get_gpu_driver(), CONST_GPU_DRIVER_INSTALL)

    def common_get_driver_type(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"driver_type": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_driver_type(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            gpu_profile=self.models.GPUProfile(
                driver_type="CUDA"
            )
        )

        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_driver_type(), "CUDA")

        # default
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"driver_type": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_driver_type(), None)
        agentpool_2 = self.create_initialized_agentpool_instance(
            gpu_profile=self.models.GPUProfile(
                driver_type="GRID"
            )
        )
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_driver_type(), "GRID")

        # custom
        ctx_0 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"driver_type": "CUDA"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_0.get_driver_type(), "CUDA")
        agentpool_0 = self.create_initialized_agentpool_instance(
            gpu_profile=self.models.GPUProfile(
                driver_type=None
            )
        )

        ctx_0.attach_agentpool(agentpool_0)
        self.assertEqual(ctx_0.get_driver_type(), "CUDA")

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

    def common_get_enable_secure_boot(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_secure_boot": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_enable_secure_boot(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=True
            )
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_enable_secure_boot(), True)

        # default
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_secure_boot": None}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_enable_secure_boot(), None)
        agentpool_2 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=True
            )
        )
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_enable_secure_boot(), None)

    def common_get_disable_secure_boot(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"disable_secure_boot": True}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_disable_secure_boot(), True)
        agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=True
            )
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_disable_secure_boot(), True)

    def common_get_enable_vtpm(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_vtpm": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_enable_vtpm(), None)
        agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=True
            )
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_enable_vtpm(), True)

        # default
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_vtpm": None}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_enable_vtpm(), None)
        agentpool_2 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=True
            )
        )
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_enable_vtpm(), None)

    def common_get_disable_vtpm(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"disable_vtpm": True}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_disable_vtpm(), True)
        agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=True
            )
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_disable_vtpm(), True)

    def common_get_enable_fips_image(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_fips_image": False}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_enable_fips_image(), False)
        agentpool = self.create_initialized_agentpool_instance(enable_fips=True)
        ctx_1.attach_agentpool(agentpool)
        self.assertEqual(ctx_1.get_enable_fips_image(), True)

        # default
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"enable_fips_image": False}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_enable_fips_image(), False)
        agentpool_2 = self.create_initialized_agentpool_instance(enable_fips=True)
        ctx_2.attach_agentpool(agentpool_2)
        # Update takes directly from flag value not from agentpool property
        self.assertEqual(ctx_2.get_enable_fips_image(), False)

    def common_get_disable_fips_image(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"disable_fips_image": True}),
            self.models,
            DecoratorMode.UPDATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_disable_fips_image(), True)
        agentpool_1 = self.create_initialized_agentpool_instance(enable_fips=True)
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_disable_fips_image(), True)

    def common_get_agentpool_windows_profile(self):
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({
                "os_type": "windows",
                "disable_windows_outbound_nat": True,
            }),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        # check all fields under windows_profile
        self.assertEqual(ctx_1.get_disable_windows_outbound_nat(), True)

        # check result when fields had been assigned values
        agentpool_1 = self.create_initialized_agentpool_instance(
            windows_profile=self.models.AgentPoolWindowsProfile(
                disable_outbound_nat=False
            )
        )
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(
            ctx_1.get_disable_windows_outbound_nat(),
            False,
        )

    def common_get_node_vm_size(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"node_vm_size": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_node_vm_size(), CONST_DEFAULT_NODE_VM_SIZE)
        agentpool = self.create_initialized_agentpool_instance(vm_size="Standard_ABCD_v2")
        ctx_1.attach_agentpool(agentpool)
        self.assertEqual(ctx_1.get_node_vm_size(), "Standard_ABCD_v2")

        # custom value
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"node_vm_size": None, "snapshot_id": "test_snapshot_id"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        mock_snapshot = Mock(vm_size="test_vm_size")
        with patch(
            "azure.cli.command_modules.acs.agentpool_decorator.get_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_2.get_node_vm_size(), "test_vm_size")

        # custom value
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {
                    "node_vm_size": "custom_node_vm_size",
                    "snapshot_id": "test_snapshot_id",
                }
            ),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        mock_snapshot = Mock(vm_size="test_vm_size")
        with patch(
            "azure.cli.command_modules.acs.agentpool_decorator.get_snapshot_by_snapshot_id",
            return_value=mock_snapshot,
        ):
            self.assertEqual(ctx_3.get_node_vm_size(), "custom_node_vm_size")

        # custom value
        ctx_4 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict(
                {
                    "node_vm_size": None,
                    "os_type": "WINDOWS",
                }
            ),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        if self.agentpool_decorator_mode == AgentPoolDecoratorMode.MANAGED_CLUSTER:
            # fail on windows os type for ManagedCluster mode (aks create)
            with self.assertRaises(InvalidArgumentValueError):
                ctx_4.get_node_vm_size()
        else:
            self.assertEqual(ctx_4.get_node_vm_size(), CONST_DEFAULT_WINDOWS_NODE_VM_SIZE)

        # if --node-vm-size is not specified, but --sku automatic is explicitly specified
        ctx_5 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"sku": "automatic", "os_type": "Linux"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_5.get_node_vm_size(), "")

    def common_get_gateway_prefix_size(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"gateway_prefix_size": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_gateway_prefix_size(), None)

        # custom value
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"gateway_prefix_size": 30}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_gateway_prefix_size(), 30)

    def common_get_vm_sizes(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"vm_sizes": None}),
            self.models,
            DecoratorMode.CREATE,
            AgentPoolDecoratorMode.STANDALONE, # windows node pool can't be system node pool
        )
        agentpool_1 = self.create_initialized_agentpool_instance(os_type="windows")
        ctx_1.attach_agentpool(agentpool_1)
        self.assertEqual(ctx_1.get_vm_sizes(), [CONST_DEFAULT_WINDOWS_VMS_VM_SIZE])

        # default
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"vm_sizes": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_2 = self.create_initialized_agentpool_instance(os_type="linux")
        ctx_2.attach_agentpool(agentpool_2)
        self.assertEqual(ctx_2.get_vm_sizes(), [CONST_DEFAULT_VMS_VM_SIZE], DeepDiff(ctx_2.get_vm_sizes(), [CONST_DEFAULT_VMS_VM_SIZE]))

        # custom
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"vm_sizes": "Standard_D4s_v3,Standard_D8s_v3"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance(os_type="linux")
        ctx_3.attach_agentpool(agentpool_3)
        self.assertEqual(ctx_3.get_vm_sizes(), ["Standard_D4s_v3", "Standard_D8s_v3"])

        # custom
        ctx_4 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"vm_sizes": None, "node_vm_size": "Standard_D4s_v3"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_4 = self.create_initialized_agentpool_instance(os_type="linux")
        ctx_4.attach_agentpool(agentpool_4)
        self.assertEqual(ctx_4.get_vm_sizes(), ["Standard_D4s_v3"])

    def common_get_upgrade_strategy(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"upgrade_strategy": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_upgrade_strategy(), None)

        # custom value from raw params
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"upgrade_strategy": "RollingUpdate"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_upgrade_strategy(), "RollingUpdate")

        # value from agentpool object in CREATE mode
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"upgrade_strategy": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance(upgrade_strategy="BlueGreen")
        ctx_3.attach_agentpool(agentpool_3)
        self.assertEqual(ctx_3.get_upgrade_strategy(), "BlueGreen")

    def common_get_drain_batch_size(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"drain_batch_size": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_drain_batch_size(), None)

        # custom value from raw params
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"drain_batch_size": "5"}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_drain_batch_size(), "5")

        # value from agentpool object in CREATE mode
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"drain_batch_size": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance()
        # Create a mock upgrade_settings_blue_green object
        upgrade_settings_bg = type('MockUpgradeSettingsBlueGreen', (), {})()
        upgrade_settings_bg.drain_batch_size = "3"
        agentpool_3.upgrade_settings_blue_green = upgrade_settings_bg
        ctx_3.attach_agentpool(agentpool_3)
        self.assertEqual(ctx_3.get_drain_batch_size(), "3")

    def common_get_drain_timeout_bg(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"drain_timeout_bg": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_drain_timeout_bg(), None)

        # custom value from raw params
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"drain_timeout_bg": 300}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_drain_timeout_bg(), 300)

        # value from agentpool object in CREATE mode
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"drain_timeout_bg": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance()
        # Create a mock upgrade_settings_blue_green object
        upgrade_settings_bg = type('MockUpgradeSettingsBlueGreen', (), {})()
        upgrade_settings_bg.drain_timeout_in_minutes = 120
        agentpool_3.upgrade_settings_blue_green = upgrade_settings_bg
        ctx_3.attach_agentpool(agentpool_3)
        self.assertEqual(ctx_3.get_drain_timeout_bg(), 120)

    def common_get_batch_soak_duration(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"batch_soak_duration": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_batch_soak_duration(), None)

        # custom value from raw params
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"batch_soak_duration": 180}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_batch_soak_duration(), 180)

        # value from agentpool object in CREATE mode
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"batch_soak_duration": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance()
        # Create a mock upgrade_settings_blue_green object
        upgrade_settings_bg = type('MockUpgradeSettingsBlueGreen', (), {})()
        upgrade_settings_bg.batch_soak_duration_in_minutes = 240
        agentpool_3.upgrade_settings_blue_green = upgrade_settings_bg
        ctx_3.attach_agentpool(agentpool_3)
        self.assertEqual(ctx_3.get_batch_soak_duration(), 240)

    def common_get_final_soak_duration(self):
        # default
        ctx_1 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"final_soak_duration": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_1.get_final_soak_duration(), None)

        # custom value from raw params
        ctx_2 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"final_soak_duration": 900}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        self.assertEqual(ctx_2.get_final_soak_duration(), 900)

        # value from agentpool object in CREATE mode
        ctx_3 = AKSPreviewAgentPoolContext(
            self.cmd,
            AKSAgentPoolParamDict({"final_soak_duration": None}),
            self.models,
            DecoratorMode.CREATE,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance()
        # Create a mock upgrade_settings_blue_green object
        upgrade_settings_bg = type('MockUpgradeSettingsBlueGreen', (), {})()
        upgrade_settings_bg.final_soak_duration_in_minutes = 1200
        agentpool_3.upgrade_settings_blue_green = upgrade_settings_bg
        ctx_3.attach_agentpool(agentpool_3)
        self.assertEqual(ctx_3.get_final_soak_duration(), 1200)


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

    def test_get_pod_ip_allocation_mode(self):
        self.common_get_pod_ip_allocation_mode()

    def test_get_os_sku(self):
        self.common_get_os_sku()

    def test_get_skip_gpu_driver_install(self):
        self.common_get_skip_gpu_driver_install()

    def test_get_gpu_driver(self):
        self.common_get_gpu_driver()

    def test_get_driver_type(self):
        self.common_get_driver_type()

    def test_get_enable_secure_boot(self):
        self.common_get_enable_secure_boot()

    def test_get_disable_secure_boot(self):
        self.common_get_disable_secure_boot()

    def test_get_enable_vtpm(self):
        self.common_get_enable_vtpm()

    def test_get_disable_vtpm(self):
        self.common_get_disable_vtpm()

    def common_get_enable_fips_image(self):
        self.common_get_enable_fips_image()

    def common_get_disable_fips_image(self):
        self.common_get_disable_fips_image()

    def test_get_agentpool_windows_profile(self):
        self.common_get_agentpool_windows_profile()

    def test_get_gateway_prefix_size(self):
        self.common_get_gateway_prefix_size()

    def test_get_vm_sizes(self):
        self.common_get_vm_sizes()

    def test_get_upgrade_strategy(self):
        self.common_get_upgrade_strategy()

    def test_get_drain_batch_size(self):
        self.common_get_drain_batch_size()

    def test_get_drain_timeout_bg(self):
        self.common_get_drain_timeout_bg()

    def test_get_batch_soak_duration(self):
        self.common_get_batch_soak_duration()

    def test_get_final_soak_duration(self):
        self.common_get_final_soak_duration()


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
        self.client = MockClient()

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

    def test_get_pod_ip_allocation_mode(self):
        self.common_get_pod_ip_allocation_mode()

    def test_get_os_sku(self):
        self.common_get_os_sku()

    def test_get_enable_artifact_streaming(self):
        self.common_get_enable_artifact_streaming()

    def test_get_enable_secure_boot(self):
        self.common_get_enable_secure_boot()

    def test_get_disable_secure_boot(self):
        self.common_get_disable_secure_boot()

    def test_get_enable_vtpm(self):
        self.common_get_enable_vtpm()

    def common_get_enable_fips_image(self):
        self.common_get_enable_fips_image()

    def test_get_agentpool_windows_profile(self):
        self.common_get_agentpool_windows_profile()

    def test_get_gateway_prefix_size(self):
        self.common_get_gateway_prefix_size()

    def test_get_vm_sizes(self):
        self.common_get_vm_sizes()

    def test_get_upgrade_strategy(self):
        self.common_get_upgrade_strategy()

    def test_get_drain_batch_size(self):
        self.common_get_drain_batch_size()

    def test_get_drain_timeout_bg(self):
        self.common_get_drain_timeout_bg()

    def test_get_batch_soak_duration(self):
        self.common_get_batch_soak_duration()

    def test_get_final_soak_duration(self):
        self.common_get_final_soak_duration()

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
        upgrade_settings_blue_green_1 = self.models.AgentPoolBlueGreenUpgradeSettings()
        # CLI will create sshAccess=localuser by default
        ground_truth_security_profile = self.models.AgentPoolSecurityProfile()
        ground_truth_security_profile.ssh_access = CONST_SSH_ACCESS_LOCALUSER
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            nodepool_name="nodepool1",
            orchestrator_version="",
            vm_size=CONST_DEFAULT_NODE_VM_SIZE,
            os_type=CONST_DEFAULT_NODE_OS_TYPE,
            enable_node_public_ip=False,
            enable_auto_scaling=False,
            count=3,
            node_taints=[],
            node_initialization_taints=[],
            os_disk_size_gb=0,
            upgrade_settings=upgrade_settings_1,
            upgrade_settings_blue_green=upgrade_settings_blue_green_1,
            type=CONST_VIRTUAL_MACHINE_SCALE_SETS,
            enable_encryption_at_host=False,
            enable_ultra_ssd=False,
            enable_fips=False,
            mode=CONST_NODEPOOL_MODE_SYSTEM,
            workload_runtime=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
            enable_custom_ca_trust=False,
            network_profile=self.models.AgentPoolNetworkProfile(),
            security_profile=ground_truth_security_profile,
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_1.context.raw_param.print_usage_statistics()


    def test_set_up_ssh_access_logs_warning_for_automatic(self):
        raw_param_dict = {
            "resource_group_name": "test_rg_name",
            "cluster_name": "test_cluster_name",
            "nodepool_name": "test_nodepool_name",
            "sku": "automatic",
        }

        dec = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Patch the SKU to be "automatic"
        dec.context.get_ssh_access = Mock(return_value=CONST_SSH_ACCESS_LOCALUSER)
        dec.context.get_sku_name = Mock(return_value=CONST_MANAGED_CLUSTER_SKU_NAME_AUTOMATIC)

        # Construct and attach the agentpool using the correct method
        with patch("azext_aks_preview.agentpool_decorator.cf_agent_pools", return_value=Mock(list=Mock(return_value=[]))):
            agentpool = dec.construct_agentpool_profile_preview()
        self.assertEqual(agentpool.security_profile, None)


    def test_set_up_ssh_access_logs_warning_for_base(self):
        raw_param_dict = {
            "resource_group_name": "test_rg_name",
            "cluster_name": "test_cluster_name",
            "nodepool_name": "test_nodepool_name",
            "sku": "base",
        }

        dec = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            raw_param_dict,
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Patch the SKU to be "base"
        dec.context.get_ssh_access = Mock(return_value=CONST_SSH_ACCESS_LOCALUSER)
        dec.context.get_sku_name = Mock(return_value=CONST_MANAGED_CLUSTER_SKU_NAME_BASE)

        # Construct and attach the agentpool
        with patch("azext_aks_preview.agentpool_decorator.cf_agent_pools", return_value=Mock(list=Mock(return_value=[]))):
            agentpool = dec.construct_agentpool_profile_preview()

        # Now run set_up_ssh_access and assert the expected log is emitted
        with self.assertLogs(level='WARNING') as log:
            dec.set_up_ssh_access(agentpool)
        self.assertIn("The new node pool will enable SSH access, recommended to use '--ssh-access disabled'", "\n".join(log.output))


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

    def common_set_up_skip_gpu_driver_install(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"skip_gpu_driver_install": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_skip_gpu_driver_install(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_skip_gpu_driver_install(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            gpu_profile=self.models.GPUProfile(
                driver=CONST_GPU_DRIVER_NONE,
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_gpu_profile(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"gpu_driver": "Install"},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_gpu_profile(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_gpu_profile(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            gpu_profile=self.models.GPUProfile(
                driver="Install",
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_secure_boot(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"enable_secure_boot": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_secure_boot(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_secure_boot(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=True
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_vtpm(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"enable_vtpm": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_vtpm(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_vtpm(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=True
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_agentpool_windows_profile(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {
                "os_type": "windows",
                "disable_windows_outbound_nat": True,
            },
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_agentpool_windows_profile(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)

        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            windows_profile=self.models.AgentPoolWindowsProfile(
                disable_outbound_nat=True
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_agentpool_gateway_profile(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"gateway_prefix_size": 30},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_agentpool_gateway_profile(None)
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_agentpool_gateway_profile(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            gateway_profile=self.models.AgentPoolGatewayProfile(
                public_ip_prefix_size=30
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

    def common_set_up_virtual_machines_profile(self):
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"vm_sizes": "Standard_D4s_v3", "node_count": 5},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_virtual_machines_profile(None)
        agentpool_1 = self.create_initialized_agentpool_instance(type=CONST_VIRTUAL_MACHINES, restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_virtual_machines_profile(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            type=CONST_VIRTUAL_MACHINES,
            count=None,
            vm_size=None,
            enable_auto_scaling=False,
            min_count=None,
            max_count=None,
            virtual_machines_profile=self.models.VirtualMachinesProfile(
                scale=self.models.ScaleProfile(
                    manual=[
                        self.models.ManualScaleProfile(
                            size="Standard_D4s_v3",
                            count=5,
                        )
                    ]
                )
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_2 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"vm_sizes": "Standard_D4s_v3, Standard_D2s_v3", "node-count": 5},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_2 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_2.context.attach_agentpool(agentpool_2)
        # fail if passing more than 1 vm_sizes
        with self.assertRaises(InvalidArgumentValueError):
            dec_2.set_up_virtual_machines_profile(agentpool_2)

    def common_set_up_managed_system_mode(self):
        """Test the set_up_managed_system_mode method in AKSPreviewAgentPoolAddDecorator"""

        # Test case 1: mode is ManagedSystem - should reset all properties except name and mode
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"mode": CONST_NODEPOOL_MODE_MANAGEDSYSTEM},
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_managed_system_mode(None)

        # Create an agentpool with various properties set
        agentpool_1 = self.create_initialized_agentpool_instance(
            restore_defaults=False,
            count=3,
            vm_size="Standard_D2s_v3",
            os_type="Linux",
            enable_auto_scaling=True,
            min_count=1,
            max_count=5,
        )

        # Store the original name for verification
        original_name = agentpool_1.name

        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_managed_system_mode(agentpool_1)

        # Verify that mode is set to ManagedSystem
        self.assertEqual(dec_agentpool_1.mode, CONST_NODEPOOL_MODE_MANAGEDSYSTEM)

        # Verify that name is preserved
        self.assertEqual(dec_agentpool_1.name, original_name)

        # Verify that all other properties are reset to None
        for attr_name in vars(dec_agentpool_1):
            if attr_name not in ['name', 'mode'] and not attr_name.startswith('_'):
                attr_value = getattr(dec_agentpool_1, attr_name)
                self.assertIsNone(attr_value,
                    f"Attribute '{attr_name}' should be None but was '{attr_value}'")

        # Test case 2: mode is not ManagedSystem - should return agentpool unchanged
        dec_2 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"mode": CONST_NODEPOOL_MODE_SYSTEM},
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        agentpool_2 = self.create_initialized_agentpool_instance(
            restore_defaults=False,
            count=3,
            vm_size="Standard_D2s_v3",
            mode=CONST_NODEPOOL_MODE_SYSTEM,
        )

        # Store reference to compare
        original_agentpool_2 = agentpool_2

        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.set_up_managed_system_mode(agentpool_2)

        # Verify that agentpool is returned unchanged
        self.assertEqual(dec_agentpool_2, original_agentpool_2)

        # Test case 3: mode is None (default) - should return agentpool unchanged
        dec_3 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {},  # No mode specified
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        agentpool_3 = self.create_initialized_agentpool_instance(
            restore_defaults=False,
            count=3,
            vm_size="Standard_D2s_v3",
        )

        original_agentpool_3 = agentpool_3

        dec_3.context.attach_agentpool(agentpool_3)
        dec_agentpool_3 = dec_3.set_up_managed_system_mode(agentpool_3)

        # Verify that agentpool is returned unchanged
        self.assertEqual(dec_agentpool_3, original_agentpool_3)

    def common_construct_agentpool_profile_preview_with_managed_system_mode(self):
        """Test that construct_agentpool_profile_preview properly handles ManagedSystem mode"""

        # Test that when mode is ManagedSystem, only name and mode are preserved,
        # and all other property setup methods are bypassed
        dec = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {
                "nodepool_name": "testnp",
                "mode": CONST_NODEPOOL_MODE_MANAGEDSYSTEM,
                # Add some parameters that would normally set properties
                "node_count": 3,
                "node_vm_size": "Standard_D2s_v3",
                "enable_custom_ca_trust": True,
                "crg_id": "test_crg_id",
                "enable_artifact_streaming": True,
            },
            self.resource_type,
            self.agentpool_decorator_mode,
        )

        # Construct the agentpool profile with mocked Azure API calls
        with patch(
            "azext_aks_preview.agentpool_decorator.cf_agent_pools",
            return_value=Mock(list=Mock(return_value=[])),
        ):
            agentpool = dec.construct_agentpool_profile_preview()

        # Verify that mode is set to ManagedSystem
        self.assertEqual(agentpool.mode, CONST_NODEPOOL_MODE_MANAGEDSYSTEM)

        # Verify that name is preserved
        self.assertEqual(agentpool.name, "testnp")

        # Verify that all other properties are None (bypassed)
        for attr_name in vars(agentpool):
            if attr_name not in ['name', 'mode'] and not attr_name.startswith('_'):
                attr_value = getattr(agentpool, attr_name)
                self.assertIsNone(attr_value,
                    f"Attribute '{attr_name}' should be None but was '{attr_value}' when mode is ManagedSystem")

    def common_set_up_upgrade_strategy(self):
        # Test case 1: No upgrade strategy provided
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.set_up_upgrade_strategy(None)
        
        agentpool_1 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_upgrade_strategy(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance()
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        # Test case 2: RollingUpdate upgrade strategy provided
        dec_2 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"upgrade_strategy": "RollingUpdate"},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_2 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.set_up_upgrade_strategy(agentpool_2)
        dec_agentpool_2 = self._restore_defaults_in_agentpool(dec_agentpool_2)
        ground_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            upgrade_strategy="RollingUpdate"
        )
        self.assertEqual(dec_agentpool_2, ground_truth_agentpool_2)

        # Test case 3: BlueGreen upgrade strategy provided
        dec_3 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {"upgrade_strategy": "BlueGreen"},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance(restore_defaults=False)
        dec_3.context.attach_agentpool(agentpool_3)
        dec_agentpool_3 = dec_3.set_up_upgrade_strategy(agentpool_3)
        dec_agentpool_3 = self._restore_defaults_in_agentpool(dec_agentpool_3)
        ground_truth_agentpool_3 = self.create_initialized_agentpool_instance(
            upgrade_strategy="BlueGreen"
        )
        self.assertEqual(dec_agentpool_3, ground_truth_agentpool_3)

    def common_set_up_blue_green_upgrade_settings(self):
        # scenario 1: no blue-green parameters
        dec_1 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_1 = self.create_initialized_agentpool_instance()
        agentpool_1 = self._remove_defaults_in_agentpool(agentpool_1)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.set_up_blue_green_upgrade_settings(agentpool_1)
        dec_agentpool_1 = self._restore_defaults_in_agentpool(dec_agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=self.models.AgentPoolBlueGreenUpgradeSettings()
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        # scenario 2: with all blue-green parameters
        dec_2 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {
                "drain_batch_size": "5",
                "drain_timeout_bg": 15,
                "batch_soak_duration": 30,
                "final_soak_duration": 60,
            },
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_2 = self.create_initialized_agentpool_instance()
        agentpool_2 = self._remove_defaults_in_agentpool(agentpool_2)
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.set_up_blue_green_upgrade_settings(agentpool_2)
        dec_agentpool_2 = self._restore_defaults_in_agentpool(dec_agentpool_2)
        
        ground_truth_blue_green_settings = self.models.AgentPoolBlueGreenUpgradeSettings()
        ground_truth_blue_green_settings.drain_batch_size = "5"
        ground_truth_blue_green_settings.drain_timeout_in_minutes = 15
        ground_truth_blue_green_settings.batch_soak_duration_in_minutes = 30
        ground_truth_blue_green_settings.final_soak_duration_in_minutes = 60
        
        ground_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=ground_truth_blue_green_settings
        )
        self.assertEqual(dec_agentpool_2, ground_truth_agentpool_2)

        # scenario 3: with partial blue-green parameters
        dec_3 = AKSPreviewAgentPoolAddDecorator(
            self.cmd,
            self.client,
            {
                "drain_timeout_bg": 20,
                "final_soak_duration": 45,
            },
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance()
        agentpool_3 = self._remove_defaults_in_agentpool(agentpool_3)
        dec_3.context.attach_agentpool(agentpool_3)
        dec_agentpool_3 = dec_3.set_up_blue_green_upgrade_settings(agentpool_3)
        dec_agentpool_3 = self._restore_defaults_in_agentpool(dec_agentpool_3)
        
        ground_truth_blue_green_settings_3 = self.models.AgentPoolBlueGreenUpgradeSettings()
        ground_truth_blue_green_settings_3.drain_timeout_in_minutes = 20
        ground_truth_blue_green_settings_3.final_soak_duration_in_minutes = 45
        
        ground_truth_agentpool_3 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=ground_truth_blue_green_settings_3
        )
        self.assertEqual(dec_agentpool_3, ground_truth_agentpool_3)


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

    def test_set_up_skip_gpu_driver_install(self):
        self.common_set_up_skip_gpu_driver_install()

    def test_set_up_gpu_profile(self):
        self.common_set_up_gpu_profile()

    def test_set_up_secure_boot(self):
        self.common_set_up_secure_boot()

    def test_set_up_vtpm(self):
        self.common_set_up_vtpm()

    def test_set_up_agentpool_windows_profile(self):
        self.common_set_up_agentpool_windows_profile()

    def test_set_up_agentpool_gateway_profile(self):
        self.common_set_up_agentpool_gateway_profile()

    def test_set_up_virtual_machines_profile(self):
        self.common_set_up_virtual_machines_profile()

    def test_set_up_managed_system_mode(self):
        self.common_set_up_managed_system_mode()

    def test_set_up_upgrade_strategy(self):
        self.common_set_up_upgrade_strategy()

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
        ground_truth_upgrade_settings_blue_green_1 = self.models.AgentPoolBlueGreenUpgradeSettings()
        # CLI will create sshAccess=localuser by default
        ground_truth_security_profile = self.models.AgentPoolSecurityProfile()
        ground_truth_security_profile.ssh_access = CONST_SSH_ACCESS_LOCALUSER
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            nodepool_name="test_nodepool_name",
            vm_size=CONST_DEFAULT_NODE_VM_SIZE,
            os_type=CONST_DEFAULT_NODE_OS_TYPE,
            enable_node_public_ip=False,
            enable_auto_scaling=False,
            count=3,
            node_taints=[],
            node_initialization_taints=[],
            os_disk_size_gb=0,
            upgrade_settings=ground_truth_upgrade_settings_1,
            upgrade_settings_blue_green=ground_truth_upgrade_settings_blue_green_1,
            type_properties_type=CONST_VIRTUAL_MACHINE_SCALE_SETS,
            enable_encryption_at_host=False,
            enable_ultra_ssd=False,
            enable_fips=False,
            mode=CONST_NODEPOOL_MODE_USER,
            scale_down_mode=CONST_SCALE_DOWN_MODE_DELETE,
            workload_runtime=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
            enable_custom_ca_trust=False,
            network_profile=self.models.AgentPoolNetworkProfile(),
            security_profile=ground_truth_security_profile,
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_1.context.raw_param.print_usage_statistics()

    def test_set_up_blue_green_upgrade_settings(self):
        self.common_set_up_blue_green_upgrade_settings()

    def test_construct_agentpool_profile_preview_with_managed_system_mode(self):
        self.common_construct_agentpool_profile_preview_with_managed_system_mode()


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

    def test_set_up_skip_gpu_driver_install(self):
        self.common_set_up_skip_gpu_driver_install()

    def test_set_up_secure_boot(self):
        self.common_set_up_secure_boot()

    def test_set_up_vtpm(self):
        self.common_set_up_vtpm()

    def test_set_up_agentpool_windows_profile(self):
        self.common_set_up_agentpool_windows_profile()

    def test_set_up_agentpool_gateway_profile(self):
        self.common_set_up_agentpool_gateway_profile()

    def test_set_up_virtual_machines_profile(self):
        self.common_set_up_virtual_machines_profile()

    def test_set_up_managed_system_mode(self):
        self.common_set_up_managed_system_mode()

    def test_set_up_upgrade_strategy(self):
        self.common_set_up_upgrade_strategy()

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
        upgrade_settings_blue_green_1 = self.models.AgentPoolBlueGreenUpgradeSettings()
        # CLI will create sshAccess=localuser by default
        ground_truth_security_profile = self.models.AgentPoolSecurityProfile()
        ground_truth_security_profile.ssh_access = CONST_SSH_ACCESS_LOCALUSER
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            nodepool_name="nodepool1",
            orchestrator_version="",
            vm_size=CONST_DEFAULT_NODE_VM_SIZE,
            os_type=CONST_DEFAULT_NODE_OS_TYPE,
            enable_node_public_ip=False,
            enable_auto_scaling=False,
            count=3,
            node_taints=[],
            node_initialization_taints=[],
            os_disk_size_gb=0,
            upgrade_settings=upgrade_settings_1,
            upgrade_settings_blue_green=upgrade_settings_blue_green_1,
            type=CONST_VIRTUAL_MACHINE_SCALE_SETS,
            enable_encryption_at_host=False,
            enable_ultra_ssd=False,
            enable_fips=False,
            mode=CONST_NODEPOOL_MODE_SYSTEM,
            workload_runtime=CONST_WORKLOAD_RUNTIME_OCI_CONTAINER,
            enable_custom_ca_trust=False,
            network_profile=self.models.AgentPoolNetworkProfile(),
            security_profile=ground_truth_security_profile,
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_1.context.raw_param.print_usage_statistics()

    def test_set_up_blue_green_upgrade_settings(self):
        self.common_set_up_blue_green_upgrade_settings()


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

    def common_update_secure_boot(self):
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_secure_boot": True, "disable_secure_boot": False},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.update_secure_boot(None)

        agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=False
            )
        )
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.update_secure_boot(agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=True
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_secure_boot": False, "disable_secure_boot": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_2.update_secure_boot(None)

        agentpool_2 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=True
            )
        )
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_secure_boot(agentpool_2)
        ground_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_secure_boot=False
            )
        )
        self.assertEqual(dec_agentpool_2, ground_truth_agentpool_2)

        # Should error if both set
        dec_3 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"disable_secure_boot": True, "enable_secure_boot": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        dec_3.context.attach_agentpool(agentpool_2)
        with self.assertRaises(MutuallyExclusiveArgumentError):
            dec_3.update_secure_boot(agentpool_2)

    def common_update_vtpm(self):
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_vtpm": True, "disable_vtpm": False},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.update_vtpm(None)

        agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=False
            )
        )
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.update_vtpm(agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=True
            )
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_vtpm": False, "disable_vtpm": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_2.update_vtpm(None)
        agentpool_2 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=True
            )
        )
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_vtpm(agentpool_2)
        ground_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            security_profile=self.models.AgentPoolSecurityProfile(
                enable_vtpm=False
            )
        )
        self.assertEqual(dec_agentpool_2, ground_truth_agentpool_2)

        # Should error if both set
        dec_3 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"disable_vtpm": True, "enable_vtpm": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        dec_3.context.attach_agentpool(agentpool_2)
        with self.assertRaises(MutuallyExclusiveArgumentError):
            dec_3.update_vtpm(agentpool_2)

    def common_update_fips_image(self):
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_fips_image": True, "disable_fips_image": False},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.update_fips_image(None)

        agentpool_1 = self.create_initialized_agentpool_instance(enable_fips=False)
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.update_fips_image(agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(enable_fips=True)
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_fips_image": False, "disable_fips_image": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_2.update_fips_image(None)

        agentpool_2 = self.create_initialized_agentpool_instance(enable_fips=True)
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_fips_image(agentpool_2)
        ground_truth_agentpool_2 = self.create_initialized_agentpool_instance(enable_fips=False)
        self.assertEqual(dec_agentpool_2, ground_truth_agentpool_2)

        # Should error if both set
        dec_3 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"enable_fips_image": True, "disable_fips_image": True},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        dec_3.context.attach_agentpool(agentpool_2)
        with self.assertRaises(MutuallyExclusiveArgumentError):
            dec_3.update_fips_image(agentpool_2)

    def common_update_upgrade_strategy(self):
        # Test case 1: No upgrade strategy provided (should not change agentpool)
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        # fail on passing the wrong agentpool object
        with self.assertRaises(CLIInternalError):
            dec_1.update_upgrade_strategy(None)
        
        agentpool_1 = self.create_initialized_agentpool_instance(
            upgrade_strategy="RollingUpdate"
        )
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.update_upgrade_strategy(agentpool_1)
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            upgrade_strategy="RollingUpdate"
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        # Test case 2: Update to BlueGreen upgrade strategy
        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"upgrade_strategy": "BlueGreen"},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_2 = self.create_initialized_agentpool_instance(
            upgrade_strategy="RollingUpdate"
        )
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_upgrade_strategy(agentpool_2)
        ground_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            upgrade_strategy="BlueGreen"
        )
        self.assertEqual(dec_agentpool_2, ground_truth_agentpool_2)

        # Test case 3: Update to RollingUpdate upgrade strategy
        dec_3 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {"upgrade_strategy": "RollingUpdate"},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance(
            upgrade_strategy="BlueGreen"
        )
        dec_3.context.attach_agentpool(agentpool_3)
        dec_agentpool_3 = dec_3.update_upgrade_strategy(agentpool_3)
        ground_truth_agentpool_3 = self.create_initialized_agentpool_instance(
            upgrade_strategy="RollingUpdate"
        )
        self.assertEqual(dec_agentpool_3, ground_truth_agentpool_3)

    def common_update_blue_green_upgrade_settings(self):
        # Test case 1: Update with no existing blue-green settings
        dec_1 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {
                "drain_batch_size": "3",
                "drain_timeout_bg": 10,
                "batch_soak_duration": 25,
                "final_soak_duration": 50,
            },
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_1 = self.create_initialized_agentpool_instance()
        dec_1.context.attach_agentpool(agentpool_1)
        dec_agentpool_1 = dec_1.update_blue_green_upgrade_settings(agentpool_1)
        
        expected_blue_green_settings_1 = self.models.AgentPoolBlueGreenUpgradeSettings()
        expected_blue_green_settings_1.drain_batch_size = "3"
        expected_blue_green_settings_1.drain_timeout_in_minutes = 10
        expected_blue_green_settings_1.batch_soak_duration_in_minutes = 25
        expected_blue_green_settings_1.final_soak_duration_in_minutes = 50
        
        ground_truth_agentpool_1 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=expected_blue_green_settings_1
        )
        self.assertEqual(dec_agentpool_1, ground_truth_agentpool_1)

        # Test case 2: Update with existing blue-green settings (partial update)
        existing_blue_green_settings = self.models.AgentPoolBlueGreenUpgradeSettings()
        existing_blue_green_settings.drain_batch_size = "5"
        existing_blue_green_settings.drain_timeout_in_minutes = 15
        existing_blue_green_settings.batch_soak_duration_in_minutes = 30
        existing_blue_green_settings.final_soak_duration_in_minutes = 60
        
        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {
                "drain_timeout_bg": 20,
                "final_soak_duration": 45,
            },
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_2 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=existing_blue_green_settings
        )
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_blue_green_upgrade_settings(agentpool_2)
        
        expected_blue_green_settings_2 = self.models.AgentPoolBlueGreenUpgradeSettings()
        expected_blue_green_settings_2.drain_batch_size = "5"  # unchanged
        expected_blue_green_settings_2.drain_timeout_in_minutes = 20  # updated
        expected_blue_green_settings_2.batch_soak_duration_in_minutes = 30  # unchanged
        expected_blue_green_settings_2.final_soak_duration_in_minutes = 45  # updated
        
        ground_truth_agentpool_2 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=expected_blue_green_settings_2
        )
        self.assertEqual(dec_agentpool_2, ground_truth_agentpool_2)

        # Test case 3: No blue-green parameters provided (no change)
        dec_3 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        agentpool_3 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=existing_blue_green_settings
        )
        dec_3.context.attach_agentpool(agentpool_3)
        dec_agentpool_3 = dec_3.update_blue_green_upgrade_settings(agentpool_3)
        ground_truth_agentpool_3 = self.create_initialized_agentpool_instance(
            upgrade_settings_blue_green=existing_blue_green_settings
        )
        self.assertEqual(dec_agentpool_3, ground_truth_agentpool_3)

    def common_update_localdns_profile(self):
        import tempfile
        import json
        import os
        
        # Test case 1: LocalDNS config provided - verify method is called
        localdns_config = {
            "mode": "Required",
            "kubeDNSOverrides": {
                ".": {
                    "cacheDurationInSeconds": 3600,
                    "protocol": "PreferUDP"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
            json.dump(localdns_config, f)
            f.flush()
            config_file_path = f.name

        try:
            dec_1 = AKSPreviewAgentPoolUpdateDecorator(
                self.cmd,
                self.client,
                {"localdns_config": config_file_path},
                self.resource_type,
                self.agentpool_decorator_mode,
            )
            
            agentpool_1 = self.create_initialized_agentpool_instance()
            dec_1.context.attach_agentpool(agentpool_1)
            dec_agentpool_1 = dec_1.update_localdns_profile(agentpool_1)
            
            # Verify that LocalDNS profile was created and assigned
            self.assertIsNotNone(dec_agentpool_1.local_dns_profile)
            self.assertEqual(dec_agentpool_1.local_dns_profile.mode, "Required")
            
        finally:
            os.unlink(config_file_path)

        # Test case 2: No LocalDNS config provided - no change
        dec_2 = AKSPreviewAgentPoolUpdateDecorator(
            self.cmd,
            self.client,
            {},
            self.resource_type,
            self.agentpool_decorator_mode,
        )
        
        agentpool_2 = self.create_initialized_agentpool_instance()
        original_local_dns_profile = agentpool_2.local_dns_profile
        dec_2.context.attach_agentpool(agentpool_2)
        dec_agentpool_2 = dec_2.update_localdns_profile(agentpool_2)
        
        # Verify LocalDNS profile wasn't changed
        self.assertEqual(dec_agentpool_2.local_dns_profile, original_local_dns_profile)

        # Test case 3: LocalDNS config with null values
        localdns_config_with_nulls = {
            "mode": "Required",
            "kubeDNSOverrides": None,
            "vnetDNSOverrides": {
                ".": {
                    "cacheDurationInSeconds": 1800,
                    "protocol": "ForceTCP"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as f:
            json.dump(localdns_config_with_nulls, f)
            f.flush()
            config_file_path = f.name

        try:
            dec_3 = AKSPreviewAgentPoolUpdateDecorator(
                self.cmd,
                self.client,
                {"localdns_config": config_file_path},
                self.resource_type,
                self.agentpool_decorator_mode,
            )
            
            agentpool_3 = self.create_initialized_agentpool_instance()
            dec_3.context.attach_agentpool(agentpool_3)
            dec_agentpool_3 = dec_3.update_localdns_profile(agentpool_3)
            
            # Verify that LocalDNS profile was created with null handling
            self.assertIsNotNone(dec_agentpool_3.local_dns_profile)
            self.assertEqual(dec_agentpool_3.local_dns_profile.mode, "Required")
            # kubeDNSOverrides should be empty dict due to null input
            self.assertEqual(len(dec_agentpool_3.local_dns_profile.kube_dns_overrides), 0)
            # vnetDNSOverrides should have one entry
            self.assertEqual(len(dec_agentpool_3.local_dns_profile.vnet_dns_overrides), 1)
            
        finally:
            os.unlink(config_file_path)

    def common_test_process_dns_overrides_helper(self):
        from azext_aks_preview._helpers import process_dns_overrides
        
        # Test the process_dns_overrides utility function functionality
        
        # Test case 1: Valid DNS overrides without nulls
        dns_overrides = {
            ".": {
                "cacheDurationInSeconds": 3600,
                "protocol": "PreferUDP"
            }
        }
        target_dict = {}
        
        def mock_build_override(override_dict):
            return self.models.LocalDNSOverride(
                cache_duration_in_seconds=override_dict.get("cacheDurationInSeconds"),
                protocol=override_dict.get("protocol")
            )
        
        process_dns_overrides(dns_overrides, target_dict, mock_build_override)
        self.assertEqual(len(target_dict), 1)
        self.assertIn(".", target_dict)
        
        # Test case 2: DNS overrides with null values (should handle gracefully)
        dns_overrides_with_nulls = {
            ".": {
                "cacheDurationInSeconds": 1800,
                "protocol": None
            }
        }
        target_dict_2 = {}
        
        process_dns_overrides(dns_overrides_with_nulls, target_dict_2, mock_build_override)
        self.assertEqual(len(target_dict_2), 1)
        
        # Test case 3: None input (should handle gracefully)
        target_dict_3 = {}
        process_dns_overrides(None, target_dict_3, mock_build_override)
        self.assertEqual(len(target_dict_3), 0)
        
        # Test case 4: Empty input (should handle gracefully)
        target_dict_4 = {}
        process_dns_overrides({}, target_dict_4, mock_build_override)
        self.assertEqual(len(target_dict_4), 0)


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

    def test_update_secure_boot(self):
        self.common_update_secure_boot()

    def test_update_vtpm(self):
        self.common_update_vtpm()

    def test_update_fips_image(self):
        self.common_update_fips_image()

    def test_update_upgrade_strategy(self):
        self.common_update_upgrade_strategy()

    def test_update_blue_green_upgrade_settings(self):
        self.common_update_blue_green_upgrade_settings()

    def test_update_localdns_profile(self):
        self.common_update_localdns_profile()

    def test_process_dns_overrides_helper(self):
        self.common_test_process_dns_overrides_helper()

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

    def test_update_secure_boot(self):
        self.common_update_secure_boot()

    def test_update_vtpm(self):
        self.common_update_vtpm()

    def test_update_fips_image(self):
        self.common_update_fips_image()

    def test_update_upgrade_strategy(self):
        self.common_update_upgrade_strategy()

    def test_update_blue_green_upgrade_settings(self):
        self.common_update_blue_green_upgrade_settings()

    def test_update_localdns_profile(self):
        self.common_update_localdns_profile()

    def test_process_dns_overrides_helper(self):
        self.common_test_process_dns_overrides_helper()

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
