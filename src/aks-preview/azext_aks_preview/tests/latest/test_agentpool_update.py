# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock

from azext_aks_preview import ContainerServiceCommandsLoader, register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.agentpool_decorator import AKSPreviewAgentPoolModels
from azext_aks_preview.custom import aks_agentpool_update
from azext_aks_preview.tests.latest.mocks import MockCLI, MockCmd, MockClient
from azure.cli.command_modules.acs._consts import AgentPoolDecoratorMode
from azure.cli.core.parser import AzCliCommandParser


class TestAgentPoolUpdateGPUProfile(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cmd = MockCmd(MockCLI())
        self.models = AKSPreviewAgentPoolModels(
            self.cmd, CUSTOM_MGMT_AKS_PREVIEW, AgentPoolDecoratorMode.STANDALONE
        )
        self.client = MockClient()

    def _pool(self, gpu_profile, enable_auto_scaling=False):
        return self.models.UnifiedAgentPoolModel(
            name="gpunp",
            count=1,
            mode="User",
            type="VirtualMachineScaleSets",
            os_type="Linux",
            enable_auto_scaling=enable_auto_scaling,
            min_count=1 if enable_auto_scaling else None,
            max_count=2 if enable_auto_scaling else None,
            gpu_profile=gpu_profile,
        )

    def _update(self, pool, **kwargs):
        self.client.get = Mock(return_value=pool)
        self.client.begin_create_or_update = Mock(return_value=pool)
        aks_agentpool_update(
            self.cmd, self.client, "test-rg", "test-cluster", "gpunp",
            no_wait=True, **kwargs
        )
        self.client.begin_create_or_update.assert_called_once()
        args = self.client.begin_create_or_update.call_args.args
        self.assertEqual(args[:3], ("test-rg", "test-cluster", "gpunp"))
        return args[3]

    def test_autoscaler_updates_preserve_gpu_profile(self):
        gpu_configs = (
            ("Managed", "DevicePlugin", "None"),
            ("Managed", "DevicePlugin", "Single"),
            ("Managed", "DevicePlugin", "Mixed"),
            ("Managed", "DRA", "None"),
            ("Unmanaged", None, None),
        )
        updates = (
            (False, {"enable_cluster_autoscaler": True, "min_count": 1, "max_count": 3},
             (True, 1, 3)),
            (True, {"update_cluster_autoscaler": True, "min_count": 0, "max_count": 4},
             (True, 0, 4)),
            (True, {"disable_cluster_autoscaler": True}, (False, None, None)),
        )
        for management_mode, driver_mode, mig_strategy in gpu_configs:
            for enabled, parameters, expected_scaling in updates:
                with self.subTest(gpu=(management_mode, driver_mode, mig_strategy), update=parameters):
                    profile = self.models.GPUProfile(
                        driver="Install",
                        nvidia=self.models.NvidiaGPUProfile(
                            management_mode=management_mode,
                            driver_mode=driver_mode,
                            mig_strategy=mig_strategy,
                        ),
                    )
                    before = profile.as_dict()
                    submitted = self._update(self._pool(profile, enabled), **parameters)
                    self.assertEqual(submitted.gpu_profile.as_dict(), before)
                    self.assertEqual(
                        (submitted.enable_auto_scaling, submitted.min_count, submitted.max_count),
                        expected_scaling,
                    )

    def test_metadata_updates_preserve_gpu_profile(self):
        for parameters in ({"tags": {"purpose": "test"}}, {"labels": {"purpose": "test"}}):
            with self.subTest(update=parameters):
                profile = self.models.GPUProfile(
                    driver="Install",
                    nvidia=self.models.NvidiaGPUProfile(management_mode="Managed"),
                )
                before = profile.as_dict()
                submitted = self._update(self._pool(profile), **parameters)
                self.assertEqual(submitted.gpu_profile.as_dict(), before)
                if "tags" in parameters:
                    self.assertEqual(submitted.tags, parameters["tags"])
                else:
                    self.assertEqual(submitted.node_labels, parameters["labels"])

    def test_autoscaler_update_does_not_add_gpu_profile(self):
        submitted = self._update(
            self._pool(None), enable_cluster_autoscaler=True, min_count=1, max_count=3
        )
        self.assertIsNone(submitted.gpu_profile)
        self.assertTrue(submitted.enable_auto_scaling)

    def test_explicit_managed_gpu_setting_is_honored(self):
        for enabled, mode in ((True, "Managed"), (False, "Unmanaged")):
            with self.subTest(enable_managed_gpu=enabled):
                profile = self.models.GPUProfile(
                    driver="Install",
                    nvidia=self.models.NvidiaGPUProfile(
                        management_mode="Managed", driver_mode="DevicePlugin"
                    ),
                )
                submitted = self._update(self._pool(profile), enable_managed_gpu=enabled)
                self.assertEqual(submitted.gpu_profile.nvidia.management_mode, mode)

    def test_managed_gpu_command_argument_preserves_three_states(self):
        cli_ctx = self.cmd.cli_ctx
        parser = AzCliCommandParser(cli_ctx=cli_ctx)
        command_name = "aks nodepool update"
        cli_ctx.invocation = Mock(parser=parser, data={"command_string": command_name})
        cli_ctx.local_context = Mock(is_on=False)
        loader = ContainerServiceCommandsLoader(cli_ctx)
        loader.load_command_table(command_name.split())
        command = loader.command_table[command_name]
        command.load_arguments()
        loader.load_arguments(command_name)
        loader._apply_parameter_info(command_name, command)  # pylint: disable=protected-access
        loader.command_table = {command_name: command}
        parser.load_command_table(loader)

        args = command_name.split()
        for name, value in (
            ("resource_group_name", "test-rg"),
            ("cluster_name", "test-cluster"),
            ("nodepool_name", "gpunp"),
        ):
            args.extend([command.arguments[name].options_list[0], value])
        args.extend(["--enable-cluster-autoscaler", "--min-count", "1", "--max-count", "3"])
        for flags, expected in (
            ([], None),
            (["--enable-managed-gpu"], True),
            (["--enable-managed-gpu", "true"], True),
            (["--enable-managed-gpu", "false"], False),
        ):
            with self.subTest(flags=flags):
                parsed = parser.parse_args(args + flags)
                self.assertIs(parsed.enable_managed_gpu, expected)
                self.assertTrue(parsed.enable_cluster_autoscaler)
