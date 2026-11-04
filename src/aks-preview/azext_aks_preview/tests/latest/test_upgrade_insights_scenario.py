# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azure.cli.testsdk import ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from azext_aks_preview.tests.latest.custom_preparers import AKSCustomResourceGroupPreparer


class UpgradeInsightsScenarioTest(ScenarioTest):
    @AllowLargeResponse()
    # Preview-only coverage has no recording; offline CI must not provision resources.
    @live_only()
    @AKSCustomResourceGroupPreparer(name_prefix="clitestui", random_name_length=20, location="eastus2")
    def test_aks_upgrade_insights_scopes(self, resource_group, resource_group_location):
        feature = self.cmd(
            "feature show --namespace Microsoft.ContainerService --name AKSUpgradeInsightsPreview -o json"
        ).get_output_in_json()
        self.assertEqual(
            feature["properties"]["state"], "Registered",
            "The live-test subscription must have AKSUpgradeInsightsPreview registered. "
            "This test does not register subscription-wide preview features.",
        )
        self.kwargs.update({
            "rg": resource_group,
            "location": resource_group_location,
            "cluster": self.create_random_name("cliui", 16),
            "pool": "nodepool1",
        })
        cluster = self.cmd(
            "aks create -g {rg} --name {cluster} --location {location} --nodepool-name {pool} "
            "--node-count 1 --node-vm-size Standard_D2s_v3 --no-ssh-key "
            "--kms-infrastructure-encryption Enabled -o json",
            checks=[self.check("provisioningState", "Succeeded")],
        ).get_output_in_json()
        upgrades = self.cmd(
            "aks get-upgrades -g {rg} --name {cluster} -o json"
        ).get_output_in_json()["controlPlaneProfile"].get("upgrades") or []
        target = next(
            (upgrade["kubernetesVersion"] for upgrade in upgrades if not upgrade.get("isPreview")),
            cluster.get("currentKubernetesVersion") or cluster["kubernetesVersion"],
        )
        self.kwargs["target"] = target
        cluster_command = "aks upgrade-insights"
        pool_command = "aks nodepool upgrade-insights"
        cluster_args = "-g {rg} --name {cluster}"
        pool_args = "-g {rg} --cluster-name {cluster} --name {pool}"
        names = set()
        for command, arguments, scope, flags in (
            (cluster_command, cluster_args, "ControlPlaneAndAgentPools", "--target-kubernetes-ver {target}"),
            (cluster_command, cluster_args, "ControlPlane",
             "--upgrade-type ControlPlane --target-kubernetes-ver {target}"),
            (pool_command, pool_args, "AgentPool", "--target-kubernetes-ver {target}"),
            (pool_command, pool_args, "NodeImage", "--upgrade-type NodeImage"),
        ):
            with self.subTest(upgrade_type=scope):
                created = self.cmd(f"{command} create {arguments} {flags} -o json").get_output_in_json()
                self._assert_insight(created, scope)
                names.add(created["name"])
                self.kwargs["insight"] = created["name"]
                stored = self.cmd(
                    f"{command} show {arguments} --insight-name {{insight}} -o json"
                ).get_output_in_json()
                self.assertEqual(stored["properties"], created["properties"])
                self.assertEqual(stored["id"], created["id"])
                if scope == "NodeImage":
                    self.kwargs["image"] = created["properties"]["targetNodeImageVersion"]
                    self.assertTrue(self.kwargs["image"])
                    explicit = self.cmd(
                        f"{pool_command} create {pool_args} --upgrade-type NodeImage "
                        "--target-node-image-ver {image} -o json"
                    ).get_output_in_json()
                    self._assert_insight(explicit, "NodeImage")
                    self.assertEqual(explicit["properties"]["targetNodeImageVersion"], self.kwargs["image"])
                    self.assertEqual(explicit["name"], created["name"])

        blocked = self.cmd(
            f"{cluster_command} create {cluster_args} --target-kubernetes-ver 1.99.0 -o json"
        ).get_output_in_json()
        self._assert_insight(blocked, "ControlPlaneAndAgentPools")
        names.add(blocked["name"])
        self.kwargs["insight"] = blocked["name"]
        pool = next(
            item for item in blocked["properties"]["agentPools"]
            if item["agentPoolName"] == self.kwargs["pool"]
        )
        self.assertEqual(pool["evaluation"]["status"], "Failed")
        self.assertTrue(any(
            issue["severity"] == "Blocking" and issue["message"]
            for issue in pool["evaluation"]["detectedIssues"]
        ))
        report = self.cmd(
            f"{cluster_command} show {cluster_args} --insight-name {{insight}}"
        ).output
        self.assertIn(f"  Agent pool: {self.kwargs['pool']} - FAILED\n", report)
        pool_report = report.split(f"  Agent pool: {self.kwargs['pool']} - FAILED\n", 1)[1]
        self.assertIn("\n    BLOCKING:", pool_report)
        self.assertIn("\n      Issue:", pool_report)

        listed = self.cmd(f"{cluster_command} list {cluster_args} -o json").get_output_in_json()
        self.assertTrue(names.issubset({item["name"] for item in listed}))
        list_report = self.cmd(f"{cluster_command} list {cluster_args}").output
        self.assertIn(f"Insight: {blocked['name']}", list_report)
        self.assertIn("\n    BLOCKING:", list_report)
        self.assertIn("\n      Issue:", list_report)

    def _assert_insight(self, data, scope):
        self.assertTrue(data["id"])
        self.assertTrue(data["name"])
        properties = data["properties"]
        self.assertEqual(properties["upgradeType"], scope)
        self.assertEqual(properties["provisioningState"], "Succeeded")
        if scope == "ControlPlaneAndAgentPools":
            diagnostic = (
                "The combined live response must include control-plane and agent-pool evaluations. "
                f"Response: {json.dumps(data, sort_keys=True)}"
            )
            self.assertIn("controlPlane", properties, diagnostic)
            self.assertIn("agentPools", properties, diagnostic)
            self.assertIsInstance(properties["agentPools"], list, diagnostic)
            self.assertTrue(properties["agentPools"], diagnostic)
            self.assertIn(
                self.kwargs["pool"],
                [pool["agentPoolName"] for pool in properties["agentPools"]],
                diagnostic,
            )
            results = [properties["controlPlane"]] + properties["agentPools"]
        else:
            results = [properties]
            if scope in ("AgentPool", "NodeImage"):
                self.assertEqual(properties["agentPoolName"], self.kwargs["pool"])
        for result in results:
            self.assertIn(result["evaluation"]["status"], ("Passed", "Warning", "Failed"))
            self.assertTrue(result["evaluation"]["evaluatedAt"])
