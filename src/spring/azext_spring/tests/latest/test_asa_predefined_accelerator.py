# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
'''
Since the scenarios covered here depend on a Azure Spring service instance creation. 
It cannot support live run. So mark it as record_only. 
'''

@record_only()
class ApiPredefinedAcceleratorTest(ScenarioTest):

    def test_predefined_accelerator(self):
        
        self.kwargs.update({
            'serviceName': 'acc-test',
            'rg': 'acc',
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