# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shlex

from azure.cli.testsdk import ScenarioTest, live_only


class PodSnapshotExtensionScenarioTest(ScenarioTest):
    @live_only()
    def test_pod_snapshot_extension_fresh_create(self):
        """Create from a config file on an eligible, dedicated cluster, then delete."""
        resource_group = os.environ.get("AZURE_CLI_TEST_POD_SNAPSHOT_RESOURCE_GROUP")
        cluster = os.environ.get("AZURE_CLI_TEST_POD_SNAPSHOT_CLUSTER")
        config_file = os.environ.get("AZURE_CLI_TEST_POD_SNAPSHOT_CONFIG_FILE")
        if not resource_group or not cluster or not config_file:
            self.skipTest(
                "Set AZURE_CLI_TEST_POD_SNAPSHOT_RESOURCE_GROUP, "
                "AZURE_CLI_TEST_POD_SNAPSHOT_CLUSTER and "
                "AZURE_CLI_TEST_POD_SNAPSHOT_CONFIG_FILE for a dedicated cluster."
            )
        with open(config_file, encoding="utf-8") as config:
            settings = json.load(config)
        self.assertIsInstance(settings, dict)
        self.assertTrue(settings, "Supply nonempty configuration to verify file forwarding.")
        self.assertTrue(all(isinstance(key, str) and isinstance(value, str)
                            for key, value in settings.items()),
                        "Configuration must contain string keys and values.")
        self.kwargs.update(
            rg=resource_group,
            cluster=cluster,
            extension="pod-snapshot",
            config_file=shlex.quote(config_file),
            subscription=os.environ.get("AZURE_CLI_TEST_POD_SNAPSHOT_SUBSCRIPTION")
            or self.get_subscription_id(),
        )
        target = " -g {rg} --subscription {subscription}"
        self.cmd("aks show -n {cluster}" + target, checks=[
            self.check("provisioningState", "Succeeded"),
            self.check("agentSandboxProfile", None),
            self.check("podSnapshotProfile", None),
        ])
        extensions = self.cmd(
            "aks extension list --cluster-name {cluster}" + target
        ).get_output()
        self.assertFalse(any(
            extension["extensionType"].lower() == "microsoft.podsnapshot"
            or extension["name"] == self.kwargs["extension"]
            for extension in extensions
        ), "Use a dedicated cluster without an existing Pod Snapshot extension.")
        delete_command = (
            "aks extension delete --cluster-name {cluster} -n {extension} --yes"
        ) + target
        self.addCleanup(self.cmd, delete_command)
        self.cmd(
            "aks extension create --cluster-name {cluster} -n {extension} "
            "--extension-type Microsoft.PodSnapshot --scope cluster "
            "--release-namespace pod-snapshot-system --config-file {config_file}" + target,
            checks=[self.check("provisioningState", "Succeeded")],
        )
        result = self.cmd(
            "aks extension show --cluster-name {cluster} -n {extension}" + target,
            checks=[self.check("provisioningState", "Succeeded")],
        ).get_output()
        for key, value in settings.items():
            self.assertEqual(result["configurationSettings"][key], value)
        self.cmd("aks extension list --cluster-name {cluster}" + target, checks=[
            self.check("length([?name == '{extension}'])", 1),
        ])
        self.cmd(delete_command)
        self.cmd("aks extension list --cluster-name {cluster}" + target, checks=[
            self.check("length([?name == '{extension}'])", 0),
        ])
        self.cmd("aks show -n {cluster}" + target, checks=[
            self.check("agentSandboxProfile", None),
            self.check("podSnapshotProfile", None),
        ])
