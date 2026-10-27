# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import ScenarioTest, live_only


class AgentSandboxExtensionScenarioTest(ScenarioTest):
    @live_only()
    def test_agent_sandbox_extension_lifecycle(self):
        """Run against an eligible, dedicated cluster with no Agent Sandbox installation."""
        resource_group = os.environ.get("AZURE_CLI_TEST_AGENT_SANDBOX_RESOURCE_GROUP")
        cluster = os.environ.get("AZURE_CLI_TEST_AGENT_SANDBOX_CLUSTER")
        if not resource_group or not cluster:
            self.skipTest(
                "Set AZURE_CLI_TEST_AGENT_SANDBOX_RESOURCE_GROUP and "
                "AZURE_CLI_TEST_AGENT_SANDBOX_CLUSTER to an eligible dedicated cluster."
            )
        self.kwargs.update(
            rg=resource_group,
            cluster=cluster,
            extension="aks-managed-agent-sandbox",
            subscription=os.environ.get("AZURE_CLI_TEST_AGENT_SANDBOX_SUBSCRIPTION")
            or self.get_subscription_id(),
        )
        target = " -g {rg} --subscription {subscription}"
        self.cmd("aks show -n {cluster}" + target, checks=[
            self.check("provisioningState", "Succeeded"),
            self.check("agentSandboxProfile", None),
            self.check("podSnapshotProfile", None),
        ])
        self.cmd("aks extension list --cluster-name {cluster}" + target, checks=[
            self.check("length([?extensionType == 'microsoft.agentsandbox' || "
                       "extensionType == 'Microsoft.AgentSandbox'])", 0),
        ])
        delete_command = (
            "aks extension delete --cluster-name {cluster} "
            "-n {extension} --yes"
        ) + target
        self.addCleanup(self.cmd, delete_command)
        self.cmd(
            "aks extension create --cluster-name {cluster} -n {extension} "
            "--extension-type Microsoft.AgentSandbox --scope cluster "
            "--release-namespace agent-sandbox-system --config replicaCount=1" + target,
            checks=[self.check("provisioningState", "Succeeded")],
        )
        self.cmd(
            "aks extension show --cluster-name {cluster} -n {extension}" + target,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check('configurationSettings."replicaCount"', "1"),
            ],
        )
        self.cmd("aks extension list --cluster-name {cluster}" + target, checks=[
            self.check("length([?name == '{extension}'])", 1),
        ])
        self.cmd(
            "aks extension update --cluster-name {cluster} -n {extension} "
            "--config replicaCount=2 --yes" + target,
            checks=[
                self.check("provisioningState", "Succeeded"),
                self.check('configurationSettings."replicaCount"', "2"),
            ],
        )
        self.cmd(
            "aks extension show --cluster-name {cluster} -n {extension}" + target,
            checks=[self.check('configurationSettings."replicaCount"', "2")],
        )
        self.cmd(delete_command)
        self.cmd("aks extension list --cluster-name {cluster}" + target, checks=[
            self.check("length([?name == '{extension}'])", 0),
        ])
        self.cmd("aks show -n {cluster}" + target, checks=[
            self.check("agentSandboxProfile", None),
            self.check("podSnapshotProfile", None),
        ])
