import unittest
from azure.cli.testsdk import *

# resource creation is failing due to which tests whave been skipped. Will be fixed in the next release.
class DatadogMonitoredSubscriptionScenario(ScenarioTest):
    test_options = {
        "rg": "bhanu-rg",
        "subscription": "/SUBSCRIPTIONS/B16E4B4E-2ED8-4F32-BAC1-0E3EB56BEF5C",
        "monitor": "datadogtestresource",
    }

    @ResourceGroupPreparer(name_prefix='cli_test_datadog_monitored_subscription', location='centraluseuap')
    def test_datadog_monitor_monitored_subscription(self, resource_group):
        self.kwargs.update({
            'rg': self.test_options["rg"],
            'subscription': self.test_options["subscription"],
            'monitor': self.test_options["monitor"],
            'updated_status': 'InProgress',
            'status': 'Active'
        })

        self.cmd('datadog monitor monitored-subscription delete --resource-group {rg} --monitor-name {monitor} --configuration-name default -y')

        self.cmd('datadog monitor monitored-subscription create '
                 '--resource-group {rg} '
                 '--monitor-name {monitor} '
                 '--operation AddBegin '
                 '--configuration-name default '
                 '--mon-sub-list "[{{\\"subscription-id\\":\\"{subscription}\\",\\"status\\":\\"Active\\"}}]" ', checks=[
                     self.check('name', 'default'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('properties.monitoredSubscriptionList[0].subscriptionId', '{subscription}'),
                     self.check('properties.monitoredSubscriptionList[0].status', 'Active')
                 ])

        self.cmd('datadog monitor monitored-subscription show -n default -g {rg} --monitor-name {monitor}', checks=[
            self.check('name', 'default'),
            self.check('resourceGroup', '{rg}'),
            self.check('properties.monitoredSubscriptionList[0].subscriptionId', '{subscription}'),
            self.check('properties.monitoredSubscriptionList[0].status', 'Active'),
            self.check('properties.monitoredSubscriptionList[0].tagRules.provisioningState', 'Accepted')
        ])

        self.cmd('datadog monitor monitored-subscription update '
                 '-n default '
                 '--resource-group {rg} '
                 '--monitor-name {monitor} '
                 '--mon-sub-list "[{{\\"subscription-id\\":\\"{subscription}\\",\\"status\\":\\"{updated_status}\\"}}]" ', checks=[
                     self.check('name', 'default'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('properties.monitoredSubscriptionList[0].subscriptionId', '{subscription}'),
                     self.check('properties.monitoredSubscriptionList[0].status', '{updated_status}'),
                 ])

        self.cmd('datadog monitor monitored-subscription list -g {rg} --monitor-name {monitor}', checks=[
            self.check('[0].name', 'default'),
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].properties.monitoredSubscriptionList[0].subscriptionId', '{subscription}'),
            self.check('[0].properties.monitoredSubscriptionList[0].status', 'Active'),
            self.check('[0].properties.monitoredSubscriptionList[0].tagRules.provisioningState', 'Accepted')
        ])

        self.cmd('datadog monitor monitored-subscription delete --resource-group {rg} --monitor-name {monitor} --configuration-name default -y')