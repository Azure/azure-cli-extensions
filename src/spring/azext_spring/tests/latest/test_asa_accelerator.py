# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
'''
Since the scenarios covered here depend on a Azure Spring service instance creation. 
It cannot support live run. So mark it as record_only. 
'''

class ApidAcceleratorTest(ScenarioTest):

    @SpringResourceGroupPreparer()
    @SpringPreparer(dev_setting_name='AZURE_CLI_TEST_DEV_SPRING_NAME_TANZU_ENABLED', additional_params='--sku Enterprise --disable-app-insights --enable-application-accelerator')
    def test_predefined_accelerator(self, resource_group, spring):
        
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'name': 'asa-java-rest-service'
        })

        result = self.cmd('spring application-accelerator predefined-accelerator list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring application-accelerator predefined-accelerator show -n {name} -g {rg} -s {serviceName}', 
        checks=[
            self.check('properties.provisioningState', "Succeeded"),
            self.check('properties.state', "Enabled")
        ])

        self.cmd('spring application-accelerator predefined-accelerator disable -n {name} -g {rg} -s {serviceName}')

        self.cmd('spring application-accelerator predefined-accelerator show -n {name} -g {rg} -s {serviceName}', 
        checks=[
            self.check('properties.provisioningState', "Succeeded"),
            self.check('properties.state', "Disabled")
        ])

        self.cmd('spring application-accelerator predefined-accelerator enable -n {name} -g {rg} -s {serviceName}')

        self.cmd('spring application-accelerator predefined-accelerator show -n {name} -g {rg} -s {serviceName}', 
        checks=[
            self.check('properties.provisioningState', "Succeeded"),
            self.check('properties.state', "Enabled")
        ])

    @SpringResourceGroupPreparer()
    @SpringPreparer(dev_setting_name='AZURE_CLI_TEST_DEV_SPRING_NAME_TANZU_ENABLED', additional_params='--sku Enterprise --disable-app-insights --enable-application-accelerator')
    def test_customized_accelerator(self, resource_group, spring):
        
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'name': 'acc-name',
            'displayName': 'acc-name',
            'gitUrl': 'https://github.com/Azure-Samples/piggymetrics-config',
            'gitBranch': 'master',
        })

        self.cmd('spring application-accelerator customized-accelerator create -n {name} -g {rg} -s {serviceName} --display-name {displayName} --git-url {gitUrl} --git-branch {gitBranch} --git-interval 10', 
        checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-accelerator customized-accelerator update -n {name} -g {rg} -s {serviceName} --display-name {displayName} --git-url {gitUrl} --git-branch {gitBranch} --description desc', 
        checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        result = self.cmd('spring application-accelerator customized-accelerator list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) == 1)

        self.cmd('spring application-accelerator customized-accelerator show -n {name} -g {rg} -s {serviceName}', 
        checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-accelerator customized-accelerator delete -n {name} -g {rg} -s {serviceName}')

        result = self.cmd('spring application-accelerator customized-accelerator list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) == 0)