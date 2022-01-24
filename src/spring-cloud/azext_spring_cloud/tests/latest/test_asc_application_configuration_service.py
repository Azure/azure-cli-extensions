# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


@record_only()
class ApplicationConfigurationServiceTest(ScenarioTest):

    def test_application_configuration_service(self):
        
        self.kwargs.update({
            'serviceName': 'tx-enterprise',
            'rg': 'tx',
            'repo': 'repo1',
            "label": "master",
            "patterns": "api-gateway,customers-service",
            "uri": "https://github.com/spring-petclinic/spring-petclinic-microservices-config",
            "app": "app1"
        })
        
        self.cmd('spring-cloud application-configuration-service show -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud application-configuration-service git repo add -g {rg} -s {serviceName} '
                 '-n {repo} --label {label} --patterns {patterns} --uri {uri}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud application-configuration-service git repo update -g {rg} -s {serviceName} '
                 '-n {repo} --label {label}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        result = self.cmd('spring-cloud application-configuration-service git repo list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)
        
        self.cmd('spring-cloud application-configuration-service git repo remove --name {repo} -g {rg} -s {serviceName}')
        result = self.cmd('spring-cloud application-configuration-service git repo list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) == 0)

        self.cmd('spring-cloud application-configuration-service bind --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.addonConfigs.applicationConfigurationService.resourceId',
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/configurationServices/default")
        ])
        self.cmd('spring-cloud application-configuration-service unbind --app {app} -g {rg} -s {serviceName}')

        self.cmd('spring-cloud application-configuration-service clear -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])
