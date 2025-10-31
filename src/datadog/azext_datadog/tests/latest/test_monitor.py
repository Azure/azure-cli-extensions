import unittest
from azure.cli.testsdk import *

# resource creation is failing due to which tests whave been skipped. Will be fixed in the next release.
class DatadogMonitorsTestScenario(ScenarioTest):
    test_options = {
        "subscription": "b9aad304-baa9-4d2a-9404-dbdd3ab55ac5",
        "rg": "bhanu-test",
        "sku": "pro_testing_20200911_Monthly@TIDgmz7xq9ge3py"
    }

    '''
    @ResourceGroupPreparer(name_prefix='cli_test_datadog_monitor', location='centraluseuap')
    def test_datadog_monitor(self, resource_group):
        email = self.cmd('account show').get_output_in_json()['user']['name']
        self.kwargs.update({
            'monitor': self.create_random_name('monitor', 20),
            'rg': self.test_options["rg"],
            'email': email,
            'sku': self.test_options["sku"],
            'subscription': self.test_options["subscription"],
            'org_name': 'myorg'+self.create_random_name('', 5),
            'ruleSetId': '31d91b5afb6f4c2eaaf104c97b1991dd'
        })

        self.cmd('datadog monitor create '
                    '-n {monitor} '
                    '-g {rg} '
                    '--location centraluseuap '
                    '--monitoring-status Enabled '
                    '--subscription {subscription} '
                    '--org-properties name="{org_name}" '
                    '--sku name="{sku}" '
                    '--identity type="SystemAssigned" '
                    '--user-info name="Alice" email-address="alice@microsoft.com" --debug', checks=[
                     self.check('name', '{monitor}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('sku.name', '{sku}')
                 ])
        

        self.cmd('datadog monitor list -g {rg}', checks=[
            self.check('[0].name', '{monitor}'),
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].sku.name', '{sku}')
        ])

        self.cmd('datadog monitor show -n {monitor} -g {rg}', checks=[
            self.check('name', '{monitor}'),
            self.check('resourceGroup', '{rg}'),
            self.check('sku.name', '{sku}')
        ])

        self.cmd('datadog monitor get-billing-info --monitor-name {monitor} -g {rg}', checks=[
                 self.check('length(marketplaceSaasInfo)', 5)
                 ])

        self.cmd('datadog monitor get-default-key -g {rg} --monitor-name {monitor}')
        self.cmd('datadog monitor list-api-key -g {rg} --monitor-name {monitor}')
        self.cmd('datadog monitor list-host -g {rg} --monitor-name {monitor}')
        self.cmd('datadog monitor list-linked-resource -g {rg} --monitor-name {monitor}')
        self.cmd('datadog monitor list-host -g {rg} --monitor-name {monitor}')
        self.cmd('datadog monitor list-monitored-resource -g {rg} --monitor-name {monitor}')

        self.cmd('datadog monitor delete --name {monitor} --resource-group {rg} -y')
    '''