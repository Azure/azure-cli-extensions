# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from azure.cli.testsdk import ScenarioTest, live_only

from azext_aks_preview.azuremanagedlustre import aml_ops
from azext_aks_preview.tests.latest.custom_preparers import AKSCustomResourceGroupPreparer
from azext_aks_preview.tests.latest.recording_processors import KeyReplacer


RELEASE_TRAIN_ENV = "AZURE_CLI_TEST_AMLFS_RELEASE_TRAIN"


class AzureManagedLustreScenarioTest(ScenarioTest):
    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[KeyReplacer()])
        # Live-only runs need no cassette, especially for the large subscription-wide SKU catalog.
        self.disable_recording = True
        # Temporarily default to dev: it passed live, while stable discovery returns InvalidResourceType.
        # TODO: Flip to stable once its availability in the test subscription/region is confirmed
        # and an explicit stable-train lifecycle run passes. The production CLI still defaults to stable.
        self.release_train = os.environ.get(RELEASE_TRAIN_ENV, "dev").strip().lower()
        if self.release_train not in ("stable", "dev"):
            raise ValueError(f"{RELEASE_TRAIN_ENV} must be 'stable' or 'dev'.")

    # Requires the selected train in the test subscription/region; no recording is available yet.
    @live_only()
    @AKSCustomResourceGroupPreparer(random_name_length=17, name_prefix="clilustre", location="centralus")
    def test_aks_azure_managed_lustre_lifecycle(self, resource_group, resource_group_location):
        # ScenarioTest invokes the CLI in-process; this override never changes the installed extension.
        with patch.object(aml_ops, "CONST_AMLFS_RELEASE_TRAIN", self.release_train):
            self._run_lifecycle(resource_group, resource_group_location)

    def _run_lifecycle(self, resource_group, resource_group_location):
        self.kwargs.update({
            "rg": resource_group,
            "location": resource_group_location,
            "name": self.create_random_name("lustre", 16),
        })

        # Deliberately omit --node-vm-size to exercise validation of the service-selected size.
        cluster = self.cmd(
            "aks create -g {rg} -n {name} -l {location} --node-count 1 --os-sku Ubuntu2404 "
            "--no-ssh-key --enable-azure-managed-lustre",
            checks=[self.check("provisioningState", "Succeeded")],
        ).get_output_in_json()
        self.assertTrue(cluster["agentPoolProfiles"][0]["vmSize"])
        self._check_lustre_extension()

        # This fresh, disposable cluster has no Lustre workloads or volumes to retire.
        self._disable_lustre()
        self.cmd(
            "aks update -g {rg} -n {name} --enable-azure-managed-lustre",
            checks=[self.check("provisioningState", "Succeeded")],
        )
        self._check_lustre_extension()
        self._disable_lustre()

    def _check_lustre_extension(self):
        self.cmd(
            "k8s-extension show -g {rg} -c {name} -n azurelustre --cluster-type managedClusters",
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check("extensionType", "microsoft.azuremanagedlustre"),
                self.check("releaseTrain", self.release_train),
                self.check("autoUpgradeMinorVersion", False),
            ],
        )
        self.cmd(
            "k8s-extension list -g {rg} -c {name} --cluster-type managedClusters",
            checks=[self.check("length([?extensionType=='microsoft.azuremanagedlustre'])", 1)],
        )

    def _disable_lustre(self):
        self.cmd(
            "aks update -g {rg} -n {name} --disable-azure-managed-lustre --yes",
            checks=[self.check("provisioningState", "Succeeded")],
        )
        self.cmd(
            "k8s-extension list -g {rg} -c {name} --cluster-type managedClusters",
            checks=[self.check("length([?name=='azurelustre'])", 0)],
        )


class AzureManagedLustreScenarioConfigurationTest(unittest.TestCase):
    def test_selected_train_is_used_for_both_installations_and_assertions(self):
        for configured_train, expected_train in [(None, "dev"), ("dev", "dev"), ("stable", "stable")]:
            with self.subTest(train=configured_train), patch.dict(os.environ):
                os.environ.pop(RELEASE_TRAIN_ENV, None)
                if configured_train is not None:
                    os.environ[RELEASE_TRAIN_ENV] = configured_train
                scenario = AzureManagedLustreScenarioTest("test_aks_azure_managed_lustre_lifecycle")
                scenario.kwargs = {}
                scenario.check = lambda query, expected: (query, expected)
                custom = Mock()
                original_train = aml_ops.CONST_AMLFS_RELEASE_TRAIN
                checked_trains = []

                def command(command_text, checks):
                    if "--enable-azure-managed-lustre" in command_text:
                        aml_ops.perform_enable_azure_managed_lustre(Mock(), "rg", "cluster")
                    checked_trains.extend(expected for query, expected in checks if query == "releaseTrain")
                    return Mock(get_output_in_json=lambda: {
                        "agentPoolProfiles": [{"vmSize": "Standard_D2s_v5"}],
                    })

                scenario.cmd = Mock(side_effect=command)
                with patch.object(aml_ops, "validate_no_other_installation"), \
                        patch.object(aml_ops, "get_azure_managed_lustre_extension_client",
                                     return_value=(Mock(), custom)), \
                        patch.object(aml_ops, "LongRunningOperation",
                                     return_value=Mock(return_value=SimpleNamespace(provisioning_state="Succeeded"))):
                    inspect.unwrap(AzureManagedLustreScenarioTest.test_aks_azure_managed_lustre_lifecycle)(
                        scenario, "rg", "centralus",
                    )
                self.assertEqual(custom.create_k8s_extension.call_count, 2)
                self.assertEqual(
                    [item.kwargs["release_train"] for item in custom.create_k8s_extension.call_args_list],
                    [expected_train, expected_train],
                )
                self.assertEqual(checked_trains, [expected_train, expected_train])
                self.assertEqual(aml_ops.CONST_AMLFS_RELEASE_TRAIN, original_train)

    def test_override_is_restored_on_failure(self):
        original_train = aml_ops.CONST_AMLFS_RELEASE_TRAIN
        with patch.dict(os.environ, {RELEASE_TRAIN_ENV: "dev"}):
            scenario = AzureManagedLustreScenarioTest("test_aks_azure_managed_lustre_lifecycle")
        with patch.object(scenario, "_run_lifecycle", side_effect=RuntimeError("Installation failed")):
            with self.assertRaisesRegex(RuntimeError, "Installation failed"):
                inspect.unwrap(AzureManagedLustreScenarioTest.test_aks_azure_managed_lustre_lifecycle)(
                    scenario, "rg", "centralus",
                )
        self.assertEqual(aml_ops.CONST_AMLFS_RELEASE_TRAIN, original_train)

    def test_unknown_train_is_rejected(self):
        with patch.dict(os.environ, {RELEASE_TRAIN_ENV: "typo"}):
            with self.assertRaisesRegex(ValueError, RELEASE_TRAIN_ENV):
                AzureManagedLustreScenarioTest("test_aks_azure_managed_lustre_lifecycle")
