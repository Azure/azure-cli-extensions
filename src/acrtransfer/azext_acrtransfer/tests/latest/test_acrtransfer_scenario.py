# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class AcrTransferScenarioTest(ScenarioTest):
    @ResourceGroupPreparer()
    def test_acrtransfer_import_pipeline_list(self, resource_group):
        """Test listing import pipelines"""
        self.kwargs.update({
            'registry_name': self.create_random_name('acr', 20),
            'rg': resource_group,
            'location': 'eastus',
            'sku': 'Premium'
        })

        self.cmd('acr create -n {registry_name} -g {rg} -l {location} --sku {sku}', checks=[
            self.check('name', '{registry_name}'),
            self.check('location', '{location}'),
            self.check('sku.name', '{sku}')
        ])

        self.cmd('acr import-pipeline list -r {registry_name} -g {rg}', checks=[
            self.check('length(@)', 0)
        ])
        self.cmd('acr delete -n {registry_name} -g {rg} -y')

