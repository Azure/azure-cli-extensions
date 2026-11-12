# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import JMESPathCheck, ResourceGroupPreparer, ScenarioTest


class StorageDiscoveryCapabilitiesScenario(ScenarioTest):
    @ResourceGroupPreparer(location="francecentral")
    def test_storage_discovery_workspace_capabilities(self):
        self.kwargs.update({
            "workspace_name": self.create_random_name("clitest", 18),
            "workspace_root": f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{self.kwargs['rg']}",
            "capabilities_enabled": "{azure-blob-storage:{capacity-details:{status:Enabled}}}",
            "capabilities_disabled": "{azure-blob-storage:{capacity-details:{status:Disabled}}}",
        })
        self.cmd(
            'storage-discovery workspace create -g {rg} -n {workspace_name} --location francecentral '
            '--workspace-roots "{workspace_root}" '
            '--scopes \'[{{"displayName":"testscope","resourceTypes":["Microsoft.Storage/storageAccounts"]}}]\' '
            '--capabilities "{capabilities_enabled}"',
            checks=JMESPathCheck("properties.capabilities.azureBlobStorage.capacityDetails.status", "Enabled"),
        )
        try:
            self.cmd(
                'storage-discovery workspace show -g {rg} -n {workspace_name}',
                checks=JMESPathCheck("properties.capabilities.azureBlobStorage.capacityDetails.status", "Enabled"),
            )
            for scope in ("", "-g {rg}"):
                self.cmd(
                    'storage-discovery workspace list ' + scope,
                    checks=self.check(
                        "[?name=='{workspace_name}'].properties.capabilities.azureBlobStorage.capacityDetails.status",
                        ["Enabled"],
                    ),
                )
            self.cmd(
                'storage-discovery workspace update -g {rg} -n {workspace_name} '
                '--capabilities "{capabilities_disabled}"',
                checks=JMESPathCheck("properties.capabilities.azureBlobStorage.capacityDetails.status", "Disabled"),
            )
            self.cmd(
                'storage-discovery workspace update -g {rg} -n {workspace_name} --description "updated"',
                checks=[
                    JMESPathCheck("properties.description", "updated"),
                    JMESPathCheck("properties.capabilities.azureBlobStorage.capacityDetails.status", "Disabled"),
                ],
            )
        finally:
            self.cmd('storage-discovery workspace delete -g {rg} -n {workspace_name} -y')
