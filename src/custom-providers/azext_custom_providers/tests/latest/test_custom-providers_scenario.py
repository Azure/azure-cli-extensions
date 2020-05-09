# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class CustomProvidersScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_custom_providers')
    def test_custom_providers_common_scenario(self):

        rp_name = self.create_random_name('clitest-crp', 20)
        self.kwargs.update({
            'rp_name': rp_name
        })

        self.cmd('az custom-providers resource-provider create '
                 '--resource-group {rg} '
                 '--name {rp_name} '
                 '--location westus2 '
                 '--action '
                 'name=ping '
                 'endpoint=https://ayniadjso4lay.azurewebsites.net/api '
                 'routing_type=Proxy '
                 '--action '
                 'name=ping1 '
                 'endpoint=https://ayniadjso4lay.azurewebsites.net/api1 '
                 'routing_type=Proxy '
                 '--resource-type '
                 'name=users '
                 'endpoint=https://ayniadjso4lay.azurewebsites.net/api '
                 'routing_type="Proxy, Cache" '
                 '--validation '
                 'validation_type=swagger '
                 'specification=https://raw.githubusercontent.com/jsntcy/TestFixDelete/master/test.json',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', rp_name),
                     self.check('actions[0].name', 'ping'),
                     self.check('resourceTypes[0].name', 'users'),
                     self.check('validations[0].validationType', 'Swagger')
                 ])

        self.cmd('az custom-providers resource-provider show '
                 '--resource-group {rg} '
                 '--name {rp_name}',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', rp_name),
                     self.check('actions[0].name', 'ping'),
                     self.check('actions[0].endpoint', 'https://ayniadjso4lay.azurewebsites.net/api'),
                     self.check('actions[0].routingType', 'Proxy'),
                     self.check('resourceTypes[0].name', 'users'),
                     self.check('resourceTypes[0].endpoint', 'https://ayniadjso4lay.azurewebsites.net/api'),
                     self.check('resourceTypes[0].routingType', 'Proxy, Cache'),
                     self.check('validations[0].validationType', 'Swagger'),
                     self.check('validations[0].specification',
                                'https://raw.githubusercontent.com/jsntcy/TestFixDelete/master/test.json')
                 ])

        self.cmd('az custom-providers resource-provider list '
                 '--resource-group {rg}',
                 checks=[
                     self.check('length(@)', 1)
                 ])

        self.cmd('az custom-providers resource-provider update '
                 '--resource-group {rg} '
                 '--name {rp_name} '
                 '--tags a=b',
                 checks=[
                     self.check('tags.a', 'b'),
                 ])

        self.cmd('az custom-providers resource-provider delete '
                 '--resource-group {rg} '
                 '--name {rp_name} '
                 '-y',
                 checks=[])

        self.cmd('az custom-providers resource-provider show '
                 '--resource-group {rg} '
                 '--name {rp_name}',
                 expect_failure=True)
