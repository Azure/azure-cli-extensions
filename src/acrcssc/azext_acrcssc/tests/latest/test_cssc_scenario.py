# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only


class AcrcsscScenarioTest(ScenarioTest):
    @live_only()
    @ResourceGroupPreparer()
    def test_acrcssc_workflow(self, resource_group):
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        self.kwargs.update({
            'registry_name': self.create_random_name('clireg', 20),
            'rg': resource_group,
            'location': 'eastus',
            'workflow_type': 'ContinuousPatchV1',
            'config': os.path.normpath(os.path.join(curr_dir, 'config', 'scenario_test_config.json')),
            'schedule': '7d'
        })

        self.cmd('acr create -n {registry_name} -g {rg} --sku Standard --location {location}',
                 checks=[self.check('name', '{registry_name}'),
                         self.check('provisioningState', 'Succeeded')])
        
        self.cmd('acr supply-chain workflow create -r {registry_name} -g {rg} -t {workflow_type} --config "{config}" --schedule {schedule}')

        self.cmd('acr supply-chain workflow list -r {registry_name} -g {rg} -t {workflow_type}')

        self.cmd('acr supply-chain workflow show -r {registry_name} -g {rg} -t {workflow_type}',
                 checks=[self.check('length(@)', 3)])

        self.cmd('acr supply-chain workflow update -r {registry_name} -g {rg} -t {workflow_type} --schedule 14d')

        self.cmd('acr supply-chain workflow delete -r {registry_name} -g {rg} -t {workflow_type} --yes')

        self.cmd('acr delete -n {registry_name} -g {rg} -y')
