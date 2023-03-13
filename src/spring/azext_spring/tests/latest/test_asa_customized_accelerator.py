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
class ApiCustomizedAcceleratorTest(ScenarioTest):

    def test_customized_accelerator(self):
        
        self.kwargs.update({
            'serviceName': 'acc-test',
            'rg': 'acc',
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

