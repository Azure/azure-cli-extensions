# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from distutils import log as logger
from azure.cli.testsdk import (ScenarioTest)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringSubResourceWrapper)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum

class ApplicationConfigurationServiceTest(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    def test_asa_config_server_e0(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group
        })

        if(self.is_live):
            try:
                self.cmd('az spring config-server delete -g {rg} --service {serviceName} --yes')
            except:
                pass

        self.cmd('az spring config-server create -g {rg} --service {serviceName}', checks=[
            self.check('name', 'default'),
            self.check('type', 'Microsoft.AppPlatform/Spring/configServers'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.resourceRequests.cpu', '500m'),
            self.check('properties.resourceRequests.memory', '1Gi'),
            self.check('properties.resourceRequests.instanceCount', '2'),
            self.check('length(properties.instances)', '2'),
        ])

        self.cmd('az spring config-server git set -g {rg} --name {serviceName} --uri https://github.com/azure-samples/spring-petclinic-microservices-config', checks=[
            self.check('name', 'default'),
            self.check('type', 'Microsoft.AppPlatform/Spring/configServers'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.resourceRequests.cpu', '500m'),
            self.check('properties.resourceRequests.memory', '1Gi'),
            self.check('properties.resourceRequests.instanceCount', '2'),
            self.check('length(properties.instances)', '2'),
            self.check('properties.configServer.gitProperty.uri', 'https://github.com/azure-samples/spring-petclinic-microservices-config'),
        ])

        self.cmd('az spring config-server delete -g {rg} --service {serviceName} --yes')