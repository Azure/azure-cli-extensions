# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class WebPubSubIdentityTest(ScenarioTest):

    @ResourceGroupPreparer(random_name_length=20)
    def test_webpubsub_identity(self, resource_group):
        self.kwargs.update({
            'name': self.create_random_name('webpubsub', 16),
            'sku': 'Standard_S1',
            'location': 'eastus',
            'unit_count': 1,
        })

        # Test create
        self.cmd('webpubsub create -g {rg} -n {name} -l {location} --sku {sku} --unit-count {unit_count}', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}'),
            self.check('sku.capacity', '{unit_count}'),
        ])

        # Test assign identity
        self.cmd('webpubsub identity assign -g {rg} -n {name} --identity [system]', checks=[
            self.check('identity.type', 'SystemAssigned'),
            self.exists('identity.principalId'),
            self.exists('identity.tenantId'),
        ])

        # Test show identity
        self.cmd('webpubsub identity show -g {rg} -n {name}', checks=[
            self.check('type', 'SystemAssigned'),
            self.exists('principalId'),
            self.exists('tenantId'),
        ])

        # Test remove identity
        self.cmd('webpubsub identity remove -g {rg} -n {name}', checks=[
            self.check('identity', None),
        ])
