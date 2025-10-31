import unittest
from azure.cli.testsdk import *

class DatadogTagRulesTestScenario(ScenarioTest):
    test_options = {
        "rg": "bhanu-rg",
        "monitor": "datadogtestresource"
    }

    @ResourceGroupPreparer(name_prefix='cli_test_datadog_tagrules', location='centraluseuap')
    def test_datadog_monitor_tag_rules(self, resource_group):
        email = self.cmd('account show').get_output_in_json()['user']['name']
        self.kwargs.update({
            'monitor': self.test_options["monitor"],
            'rg': self.test_options["rg"],
            'email': email
        })

        self.cmd('datadog tag-rule create -g {rg} --monitor-name {monitor} --rule-set-name default --log-rules "{{send-aad-logs:False,send-subscription-logs:True,send-resource-logs:True,filtering-tags:[{{name:Environment,value:Prod,action:Include}}]}}"', checks=[
            self.check('name', 'default'),
            self.check('resourceGroup', '{rg}'),
            self.check('properties.logRules.filteringTags[0].action', 'Include'),
            self.check('properties.logRules.filteringTags[0].name', 'Environment'),
            self.check('properties.logRules.filteringTags[0].value', 'Prod'),
            self.check('properties.logRules.sendAadLogs', False),
            self.check('properties.logRules.sendResourceLogs', True),
            self.check('properties.logRules.sendSubscriptionLogs', True)
        ])

        self.cmd('datadog tag-rule update --resource-group {rg} --monitor-name {monitor} --rule-set-name default --log-rules "{{send-aad-logs:False,send-subscription-logs:True,send-resource-logs:True,filtering-tags:[{{name:Environment,value:Prod,action:Exclude}}]}}"', checks=[
            self.check('name', 'default'),
            self.check('resourceGroup', '{rg}'),
            self.check('properties.logRules.filteringTags[0].action', 'Exclude'),
            self.check('properties.logRules.filteringTags[0].name', 'Environment'),
            self.check('properties.logRules.filteringTags[0].value', 'Prod'),
            self.check('properties.logRules.sendAadLogs', False),
            self.check('properties.logRules.sendResourceLogs', True),
            self.check('properties.logRules.sendSubscriptionLogs', True)
        ])

        self.cmd('datadog tag-rule list -g {rg} --monitor-name {monitor}', checks=[
            self.check('[0].name', 'default'),
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].properties.logRules.filteringTags[0].action', 'Exclude'),
            self.check('[0].properties.logRules.filteringTags[0].name', 'Environment'),
            self.check('[0].properties.logRules.filteringTags[0].value', 'Prod'),
            self.check('[0].properties.logRules.sendAadLogs', False),
            self.check('[0].properties.logRules.sendResourceLogs', True),
            self.check('[0].properties.logRules.sendSubscriptionLogs', True)
        ])
        self.cmd('datadog tag-rule show -n default -g {rg} --monitor-name {monitor} --rule-set-name default', checks=[
            self.check('name', 'default'),
            self.check('resourceGroup', '{rg}'),
            self.check('properties.logRules.filteringTags[0].action', 'Exclude'),
            self.check('properties.logRules.filteringTags[0].name', 'Environment'),
            self.check('properties.logRules.filteringTags[0].value', 'Prod'),
            self.check('properties.logRules.sendAadLogs', False),
            self.check('properties.logRules.sendResourceLogs', True),
            self.check('properties.logRules.sendSubscriptionLogs', True)
        ])
