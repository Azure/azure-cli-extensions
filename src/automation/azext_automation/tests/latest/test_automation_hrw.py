# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class AutomationHRWScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        # Exclude 'host' from matching to allow both GitHub and blob storage URLs for VM image aliases
        self.vcr.match_on = ['scheme', 'method', 'query']  # not 'host', 'port', 'path'
        super(AutomationHRWScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_automation_hrw', key='rg', location='westus2')
    @AllowLargeResponse(size_kb=9999)
    def test_automation_hrw(self, resource_group):
        self.kwargs.update({
            'account': self.create_random_name(prefix='test-account-', length=24),
            'vm': self.create_random_name('vm-', 15),
            'hrwg': self.create_random_name(prefix='hrwg-', length=10),
            'hrwg2': self.create_random_name(prefix='hrwg2-', length=10),
            'hrw': 'c010ad12-ef14-4a2a-aa9e-ef22c4745ddd',
            'vnet': 'vnet',
            'subnet': 'subnet'
        })
        self.cmd('automation account create --resource-group {rg} --name {account} --location "West US 2"',
                 checks=[self.check('name', '{account}')])

        self.cmd('automation hrwg create --resource-group {rg} --automation-account-name {account} --name {hrwg}',
                 checks=[self.check('name', '{hrwg}')])

        self.cmd('automation hrwg show --resource-group {rg} --automation-account-name {account} --name {hrwg}',
                 checks=[self.check('name', '{hrwg}')])

        self.cmd('automation hrwg list --resource-group {rg} --automation-account-name {account}',
                 checks=[self.check('length(@)', 1)])

        self.cmd('automation hrwg hrw list --automation-account-name {account} --hybrid-runbook-worker-group-name {hrwg} -g {rg}',
                 checks=[self.check('length(@)', 0)])

        self.kwargs['vm_id'] = self.cmd('vm create -g {rg} -n {vm} --image Ubuntu2204 --generate-ssh-key --subnet {subnet} --vnet-name {vnet} --nsg-rule NONE').get_output_in_json()['id']
        self.cmd('network vnet subnet update -g {rg} --vnet-name {vnet} -n {subnet} --default-outbound-access false')

        self.cmd('automation hrwg hrw create -g {rg} --automation-account-name {account} --hybrid-runbook-worker-group-name {hrwg} -n {hrw} --vm-resource-id {vm_id}', checks=[
            self.check('vmResourceId', '{vm_id}'),
            self.check('name', '{hrw}')
        ])
        self.cmd('automation hrwg hrw list --automation-account-name {account} --hybrid-runbook-worker-group-name {hrwg} -g {rg}', checks=[
            self.check('length(@)', 1)
        ])

        self.cmd('automation hrwg create --resource-group {rg} --automation-account-name {account} --name {hrwg2}',
                 checks=[self.check('name', '{hrwg2}')])

        self.cmd('automation hrwg hrw move -g {rg} --automation-account-name {account} --hybrid-runbook-worker-group-name {hrwg} -n {hrw} --target-hybrid-runbook-worker-group-name {hrwg2}')

        self.cmd('automation hrwg hrw list --automation-account-name {account} --hybrid-runbook-worker-group-name {hrwg} -g {rg}',
                 checks=[self.check('length(@)', 0)])
        self.cmd('automation hrwg hrw list --automation-account-name {account} --hybrid-runbook-worker-group-name {hrwg2} -g {rg}', checks=[
            self.check('length(@)', 1)
        ])
        self.cmd('automation hrwg delete --resource-group {rg} --automation-account-name {account} --name {hrwg} --yes')
