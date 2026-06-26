# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest


class VIExtensionTests(ScenarioTest):
    def test_extension_show(self):
        name = "test-vi"
        extension_type = "microsoft.videoindexer"
        resource_group = f"{name}-rg"
        connected_cluster = f"{name}-connected-aks"
        command = f'az vi extension show -g "{resource_group}" -c "{connected_cluster}"'
        extension = self.cmd(command).get_output_in_json()
        self.assertIsInstance(extension, dict)
        self.assertIsInstance(extension['properties'], dict)
        self.assertTrue(extension['properties']['extensionType'] == extension_type)
        self.assertTrue(extension['resourceGroup'] == resource_group)
        self.assertTrue(extension['name'] == name)
        self.assertTrue(len(extension['id']) > 0)

