# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


@record_only()
class ServiceRegistryTest(ScenarioTest):

    def test_service_registry(self):
        
        self.kwargs.update({
            'serviceName': 'tx-enterprise',
            'rg': 'tx',
            "app": "app1"
        })
        
        self.cmd('spring-cloud service-registry show -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud service-registry bind --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.addonConfigs.serviceRegistry.resourceId',
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/serviceRegistries/default")
        ])
        self.cmd('spring-cloud service-registry unbind --app {app} -g {rg} -s {serviceName}')
