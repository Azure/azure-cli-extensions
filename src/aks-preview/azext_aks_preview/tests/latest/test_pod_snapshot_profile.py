# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import inspect
import unittest
from unittest.mock import Mock, patch

from azure.cli.core.azclierror import MutuallyExclusiveArgumentError
from azure.cli.core.mock import DummyCli

from azext_aks_preview import ContainerServiceCommandsLoader, register_aks_preview_resource_type
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW
from azext_aks_preview.custom import aks_create, aks_update
from azext_aks_preview.managed_cluster_decorator import (
    AKSPreviewManagedClusterCreateDecorator,
    AKSPreviewManagedClusterModels,
    AKSPreviewManagedClusterUpdateDecorator,
)
from azext_aks_preview.tests.latest.mocks import MockCLI, MockClient, MockCmd


class PodSnapshotProfileTestCase(unittest.TestCase):
    def setUp(self):
        register_aks_preview_resource_type()
        self.cmd = MockCmd(MockCLI())
        self.client = MockClient()
        self.models = AKSPreviewManagedClusterModels(self.cmd, CUSTOM_MGMT_AKS_PREVIEW)

    def test_create_profile(self):
        for enabled in (None, False, True):
            with self.subTest(enabled=enabled):
                parameters = {} if enabled is None else {"enable_pod_snapshot_restore": enabled}
                decorator = AKSPreviewManagedClusterCreateDecorator(
                    self.cmd, self.client, parameters, CUSTOM_MGMT_AKS_PREVIEW
                )
                mc = self.models.ManagedCluster(location="eastus")
                decorator.context.attach_mc(mc)
                self.assertIs(decorator.set_up_pod_snapshot_profile(mc), mc)
                properties = mc.as_dict().get("properties", {})
                if enabled:
                    self.assertEqual(properties["podSnapshotProfile"], {"enabled": True})
                else:
                    self.assertNotIn("podSnapshotProfile", properties)

    def test_update_profile(self):
        for previous in (None, False, True):
            for requested in (None, False, True):
                with self.subTest(previous=previous, requested=requested):
                    parameters = {
                        "enable_pod_snapshot_restore": requested is True,
                        "disable_pod_snapshot_restore": requested is False,
                    }
                    decorator = AKSPreviewManagedClusterUpdateDecorator(
                        self.cmd, self.client, parameters, CUSTOM_MGMT_AKS_PREVIEW
                    )
                    mc = self.models.ManagedCluster(
                        location="eastus",
                        tags={"preserve": "me"},
                        agent_sandbox_profile=self.models.ManagedClusterAgentSandboxProfile(enabled=True),
                    )
                    if previous is not None:
                        mc.pod_snapshot_profile = self.models.ManagedClusterPodSnapshotProfile(
                            {"enabled": previous, "futureProperty": "preserve"}
                        )
                    before = mc.as_dict()
                    decorator.context.attach_mc(mc)
                    self.assertIs(decorator.update_pod_snapshot_profile(mc), mc)
                    if requested is None:
                        self.assertEqual(mc.as_dict(), before)
                    else:
                        self.assertIs(mc.pod_snapshot_profile.enabled, requested)
                        self.assertIs(
                            mc.as_dict()["properties"]["podSnapshotProfile"]["enabled"], requested
                        )
                        if previous is not None:
                            self.assertEqual(mc.pod_snapshot_profile.as_dict()["futureProperty"], "preserve")
                    self.assertEqual(mc.tags, {"preserve": "me"})
                    self.assertTrue(mc.agent_sandbox_profile.enabled)

    def test_conflicting_flags_do_not_mutate_profile(self):
        decorator = AKSPreviewManagedClusterUpdateDecorator(
            self.cmd, self.client,
            {"enable_pod_snapshot_restore": True, "disable_pod_snapshot_restore": True},
            CUSTOM_MGMT_AKS_PREVIEW,
        )
        mc = self.models.ManagedCluster(
            location="eastus",
            pod_snapshot_profile=self.models.ManagedClusterPodSnapshotProfile(enabled=True),
        )
        decorator.context.attach_mc(mc)
        before = mc.as_dict()
        with self.assertRaisesRegex(MutuallyExclusiveArgumentError, "--enable-pod-snapshot-restore"):
            decorator.update_pod_snapshot_profile(mc)
        self.assertEqual(mc.as_dict(), before)

    def test_argument_registration(self):
        for command in ("aks create", "aks update"):
            with self.subTest(command=command):
                cli = DummyCli()
                cli.invocation = Mock(
                    data={"command_string": command}, parser=argparse.ArgumentParser()
                )
                loader = ContainerServiceCommandsLoader(cli)
                loader.load_command_table(command.split())
                loader.command_table[command].load_arguments()
                loader.load_arguments(command)
                arguments = loader.argument_registry.arguments[command]
                parser = argparse.ArgumentParser()
                parser.add_argument(
                    *arguments["enable_pod_snapshot_restore"].settings["options_list"],
                    dest="enable_pod_snapshot_restore",
                    action=arguments["enable_pod_snapshot_restore"].settings["action"],
                )
                self.assertTrue(parser.parse_args(["--enable-pod-snapshot-restore"]).enable_pod_snapshot_restore)
                self.assertTrue(parser.parse_args(["--enable-pod-snapshot"]).enable_pod_snapshot_restore)
                self.assertFalse(parser.parse_args([]).enable_pod_snapshot_restore)
                if command == "aks update":
                    parser.add_argument(
                        *arguments["disable_pod_snapshot_restore"].settings["options_list"],
                        dest="disable_pod_snapshot_restore",
                        action=arguments["disable_pod_snapshot_restore"].settings["action"],
                    )
                    self.assertTrue(parser.parse_args(["--disable-pod-snapshot-restore"]).disable_pod_snapshot_restore)
                    self.assertTrue(parser.parse_args(["--disable-pod-snapshot"]).disable_pod_snapshot_restore)
                else:
                    self.assertNotIn("disable_pod_snapshot_restore", arguments)

    def test_create_command_pipeline(self):
        import paramiko

        key = paramiko.RSAKey.generate(2048)
        parameters = {
            name: param.default
            for name, param in inspect.signature(aks_create).parameters.items()
            if param.default is not inspect.Parameter.empty
        }
        parameters.update(
            resource_group_name="rg", name="cluster",
            ssh_key_value="{} {}".format(key.get_name(), key.get_base64()),
            enable_pod_snapshot_restore=True,
        )
        decorator = AKSPreviewManagedClusterCreateDecorator(
            self.cmd, self.client, parameters, CUSTOM_MGMT_AKS_PREVIEW
        )
        with patch(
            "azure.cli.command_modules.acs.managed_cluster_decorator.Profile",
            return_value=Mock(get_subscription_id=Mock(return_value="00000000-0000-0000-0000-000000000001")),
        ), patch(
            "azure.cli.command_modules.acs.managed_cluster_decorator.get_rg_location",
            return_value="eastus",
        ):
            result = decorator.construct_mc_profile_preview()
        self.assertEqual(result.as_dict()["properties"]["podSnapshotProfile"], {"enabled": True})

    def test_update_command_pipeline(self):
        for flag, expected in (("enable_pod_snapshot_restore", True), ("disable_pod_snapshot_restore", False)):
            with self.subTest(flag=flag):
                parameters = {
                    name: param.default
                    for name, param in inspect.signature(aks_update).parameters.items()
                    if param.default is not inspect.Parameter.empty
                }
                parameters.update(resource_group_name="rg", name="cluster", **{flag: True})
                mc = self.models.ManagedCluster(
                    location="eastus",
                    agent_pool_profiles=[self.models.ManagedClusterAgentPoolProfile(name="nodepool1")],
                    network_profile=self.models.ContainerServiceNetworkProfile(load_balancer_sku="standard"),
                    identity=self.models.ManagedClusterIdentity(type="SystemAssigned"),
                    identity_profile={
                        "kubeletidentity": self.models.UserAssignedIdentity(
                            resource_id="test_resource_id", client_id="test_client_id", object_id="test_object_id"
                        )
                    },
                )
                decorator = AKSPreviewManagedClusterUpdateDecorator(
                    self.cmd, self.client, parameters, CUSTOM_MGMT_AKS_PREVIEW
                )
                with patch.object(self.client, "get", return_value=mc), patch(
                    "azure.cli.command_modules.acs.managed_cluster_decorator.Profile",
                    return_value=Mock(get_subscription_id=Mock(return_value="00000000-0000-0000-0000-000000000001")),
                ), patch(
                    "azure.cli.command_modules.acs.managed_cluster_decorator.get_rg_location",
                    return_value="eastus",
                ):
                    result = decorator.update_mc_profile_preview()
                self.assertIs(result.as_dict()["properties"]["podSnapshotProfile"]["enabled"], expected)

    def test_command_forwards_flags(self):
        for command, decorator_name, flags, profile_method, request_method in (
            (aks_create, "AKSPreviewManagedClusterCreateDecorator",
             {"enable_pod_snapshot_restore": True}, "construct_mc_profile_preview", "create_mc"),
            (aks_update, "AKSPreviewManagedClusterUpdateDecorator",
             {"enable_pod_snapshot_restore": True}, "update_mc_profile_preview", "update_mc"),
            (aks_update, "AKSPreviewManagedClusterUpdateDecorator",
             {"disable_pod_snapshot_restore": True}, "update_mc_profile_preview", "update_mc"),
        ):
            with self.subTest(command=command.__name__, flags=flags):
                client = Mock()
                client.get.return_value = None
                args = {"ssh_key_value": "test-key"} if command is aks_create else {}
                with patch(
                    "azext_aks_preview.managed_cluster_decorator." + decorator_name
                ) as factory, patch("azext_aks_preview.custom.ensure_pis_managed_identity_permission_for_cluster"):
                    command(self.cmd, client, "rg", "cluster", **args, **flags)
                    for key, value in flags.items():
                        self.assertIs(factory.call_args.kwargs["raw_parameters"][key], value)
                    decorator = factory.return_value
                    getattr(decorator, request_method).assert_called_once_with(
                        getattr(decorator, profile_method).return_value
                    )
