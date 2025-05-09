# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import ScenarioTest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class WorkloadsScenario(ScenarioTest):

    def test_workloads_monitor_create(self):
        self.kwargs.update({
            'name': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'mrg': 'ams-test-cli-mrg',
            'location': 'eastus2euap',
            'applocation': 'eastus',
            'routingPreference': 'RouteAll',
            'subnet': '/subscriptions/49d64d54-e966-4c46-a868-1999802b762c/resourceGroups/looptest-rg/providers/Microsoft.Network/virtualNetworks/loop-test-rg-vnet/subnets/cli-testing-00',
        })

        self.cmd('az workloads monitor create -g {rg} -n {name} -l {location} --app-location {applocation} --managed-rg-name {mrg} --monitor-subnet {subnet} --routing-preference {routingPreference}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('location', '{location}'),
            self.check('appLocation', '{applocation}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('managedResourceGroupConfiguration.name', '{mrg}'),
            self.check('routingPreference', '{routingPreference}')
        ])

    def test_workloads_monitor_show(self):
        self.kwargs.update({
            'name': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'mrg': 'ams-test-cli-mrg'
        })

        self.cmd('az workloads monitor show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', 'CLI-TESTING'),
            self.check('location', 'eastus2euap'),
            self.check('appLocation', 'eastus'),
            self.check('provisioningState', 'Succeeded'),
            self.check('managedResourceGroupConfiguration.name', '{mrg}'),
            self.check('routingPreference', 'RouteAll')
        ])

    def test_workloads_monitor_update(self):
        self.kwargs.update({
            'name': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'mrg': 'ams-test-cli-mrg'
        })

        self.cmd('az workloads monitor show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', 'CLI-TESTING'),
            self.check('location', 'eastus2euap'),
            self.check('appLocation', 'eastus'),
            self.check('provisioningState', 'Succeeded'),
            self.check('managedResourceGroupConfiguration.name', '{mrg}'),
            self.check('routingPreference', 'RouteAll')
        ])

    def test_workloads_provider_instance_create(self):
        self.kwargs.update({
            'name': 'os-cli',
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'provider_settings': "{prometheusOS:{prometheusUrl:'http://10.1.0.4:9100/metrics'}}",
        })

        self.cmd('az workloads monitor provider-instance create --monitor-name {monitor} -g {rg} -n {name} --provider-settings "{provider_settings}"', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'microsoft.workloads/monitors/providerinstances'),
            self.check('provisioningState', 'Succeeded'),
            self.check('providerSettings.providerType', 'PrometheusOS'),
            self.check('providerSettings.sslPreference', 'Disabled')
        ])

    def test_workloads_provider_instance_show(self):
        self.kwargs.update({
            'name': 'os-cli',
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'provider_settings': "{prometheusOS:{prometheusUrl:'http://10.1.0.4:9100/metrics'}}"
        })

        self.cmd('az workloads monitor provider-instance show --monitor-name {monitor} -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'microsoft.workloads/monitors/providerinstances'),
            self.check('provisioningState', 'Succeeded'),
            self.check('providerSettings.providerType', 'PrometheusOS'),
            self.check('providerSettings.sslPreference', 'Disabled')
        ])

    def test_workloads_provider_instance_update(self):
        self.kwargs.update({
            'name': 'os-cli',
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'provider_settings': "{prometheusOS:{prometheusUrl:'http://10.1.0.4:9100/metrics',sapSid:X00}}"
        })

        self.cmd('az workloads monitor provider-instance create --monitor-name {monitor} -g {rg} -n {name} --provider-settings "{provider_settings}"', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'microsoft.workloads/monitors/providerinstances'),
            self.check('provisioningState', 'Succeeded'),
            self.check('providerSettings.providerType', 'PrometheusOS'),
            self.check('providerSettings.sapSid', 'X00'),
            self.check('providerSettings.sslPreference', 'Disabled')
        ])

    def test_workloads_provider_instance_remove(self):
        self.kwargs.update({
            'name': 'os-cli',
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING'
        })

        self.cmd('az workloads monitor provider-instance delete --monitor-name {monitor} -g {rg} -n {name} --yes')

    def test_workloads_spog_create(self):
        self.kwargs.update({
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'threshold': '[{name:Inscane,green:90,yellow:75,red:50}]',
            'grouping': "{landscape:[{name:Prod,topSid:[SID1,SID2]}],sapApplication:[{name:ERP1,topSid:[SID1,SID2]}]}"
        })

        self.cmd('az workloads monitor sap-landscape-monitor create --monitor-name {monitor} -g {rg} --grouping "{grouping}" --top-metrics-thresholds "{threshold}"', checks=[
            self.check('name', 'default'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'microsoft.workloads/monitors/saplandscapemonitor'),
            self.check('provisioningState', 'Succeeded'),
            self.check('grouping.landscape[0].name', 'Prod'),
            self.check('grouping.sapApplication[0].name', 'ERP1'),
            self.check('topMetricsThresholds[0].name', 'Inscane')
        ])

    def test_workloads_spog_update(self):
        self.kwargs.update({
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING',
            'threshold': '[{name:Inscane,green:90,yellow:25,red:50}]',
            'grouping': "{landscape:[{name:Prod,topSid:[SID1,SID2]}],sapApplication:[{name:ERP1,topSid:[SID1,SID2]}]}"
        })

        self.cmd('az workloads monitor sap-landscape-monitor update --monitor-name {monitor} -g {rg} --grouping "{grouping}" --top-metrics-thresholds "{threshold}"', checks=[
            self.check('name', 'default'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'microsoft.workloads/monitors/saplandscapemonitor'),
            self.check('provisioningState', 'Succeeded'),
            self.check('grouping.landscape[0].name', 'Prod'),
            self.check('grouping.sapApplication[0].name', 'ERP1'),
            self.check('topMetricsThresholds[0].name', 'Inscane'),
            self.check('topMetricsThresholds[0].yellow', '25.0')
        ])

    def test_workloads_spog_show(self):
        self.kwargs.update({
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING'
        })

        self.cmd('az workloads monitor sap-landscape-monitor show --monitor-name {monitor} -g {rg}', checks=[
            self.check('name', 'default'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'microsoft.workloads/monitors/saplandscapemonitor'),
            self.check('provisioningState', 'Succeeded'),
            self.check('grouping.landscape[0].name', 'Prod'),
            self.check('grouping.sapApplication[0].name', 'ERP1'),
            self.check('topMetricsThresholds[0].name', 'Inscane')
        ])

    def test_workloads_spog_list(self):
        self.kwargs.update({
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING'
        })

        self.cmd('az workloads monitor sap-landscape-monitor list --monitor-name {monitor} -g {rg}', checks=[
            self.check('[0].name', 'default'),
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].type', 'microsoft.workloads/monitors/saplandscapemonitor'),
            self.check('[0].provisioningState', 'Succeeded'),
            self.check('[0].grouping.landscape[0].name', 'Prod'),
            self.check('[0].grouping.sapApplication[0].name', 'ERP1'),
            self.check('[0].topMetricsThresholds[0].name', 'Inscane')
        ])

    def test_workloads_spog_remove(self):
        self.kwargs.update({
            'monitor': 'ams-test-cli-monitor',
            'rg': 'CLI-TESTING'
        })

        self.cmd('az workloads monitor sap-landscape-monitor delete --monitor-name {monitor} -g {rg} --yes', checks=[])
