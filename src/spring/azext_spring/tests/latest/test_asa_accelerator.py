# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
'''
Since the scenarios covered here depend on a Azure Spring service instance creation.
It cannot support live run. So mark it as record_only.
'''


class ApidAcceleratorTest(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    def test_predefined_accelerator(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'name': 'asa-java-rest-service'
        })

        result = self.cmd(
            'spring application-accelerator predefined-accelerator list -g {rg} -s {serviceName}').get_output_in_json()
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

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    def test_customized_accelerator(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'name': 'acc-name',
            'displayName': 'acc-name',
            'gitUrl': 'https://github.com/Azure-Samples/piggymetrics-config',
            'gitBranch': 'master',
        })

        result = self.cmd(
            'spring application-accelerator customized-accelerator list -g {rg} -s {serviceName}').get_output_in_json()
        originalCount = len(result)

        self.cmd(
            'spring application-accelerator customized-accelerator create -n {name} -g {rg} -s {serviceName} --display-name {displayName} --git-url {gitUrl} --git-branch {gitBranch} --git-interval 10',
            checks=[
                self.check('properties.provisioningState', "Succeeded")
            ])

        self.cmd(
            'spring application-accelerator customized-accelerator update -n {name} -g {rg} -s {serviceName} --display-name {displayName} --git-url {gitUrl} --git-branch {gitBranch} --description desc',
            checks=[
                self.check('properties.provisioningState', "Succeeded")
            ])

        result = self.cmd(
            'spring application-accelerator customized-accelerator list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(len(result), originalCount + 1)

        self.cmd('spring application-accelerator customized-accelerator show -n {name} -g {rg} -s {serviceName}',
                checks=[
                    self.check('properties.provisioningState', "Succeeded")
                ])

        self.cmd('spring application-accelerator customized-accelerator delete -n {name} -g {rg} -s {serviceName}')

        result = self.cmd(
            'spring application-accelerator customized-accelerator list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(len(result), originalCount)

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    def test_customized_accelerator_of_fragment_type(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'name': 'fragment-name',
            'displayName': 'fragment-name',
            'gitUrl': 'https://github.com/sample-accelerators/fragments.git',
            'gitSubPath': 'java-version',
            'gitBranch': 'main',
        })

        self.cmd(
            'spring application-accelerator customized-accelerator create -n {name} -g {rg} -s {serviceName} --type Fragment --display-name {displayName} --git-sub-path {gitSubPath} --git-url {gitUrl} --git-branch {gitBranch} --git-interval 10',
            checks=[
                self.check('properties.acceleratorType', "Fragment"),
                self.check('properties.gitRepository.subPath', "java-version"),
                self.check('properties.provisioningState', "Succeeded")
            ])

        self.cmd(
            'spring application-accelerator customized-accelerator update -n {name} -g {rg} -s {serviceName} --type Fragment --display-name {displayName} --git-sub-path {gitSubPath} --git-url {gitUrl} --git-branch {gitBranch} --description desc',
            checks=[
                self.check('properties.acceleratorType', "Fragment"),
                self.check('properties.gitRepository.subPath', "java-version"),
                self.check('properties.provisioningState', "Succeeded")
            ])

        self.cmd('spring application-accelerator customized-accelerator show -n {name} -g {rg} -s {serviceName}',
             checks=[
                 self.check('properties.acceleratorType', "Fragment"),
                 self.check('properties.gitRepository.subPath', "java-version"),
                 self.check('properties.provisioningState', "Succeeded")
             ])
