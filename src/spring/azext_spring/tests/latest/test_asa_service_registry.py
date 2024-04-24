# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringAppNamePreparer)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum


# pylint: disable=line-too-long
# pylint: disable=too-many-lines


class ServiceRegistryTest(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    @SpringAppNamePreparer()
    def test_service_registry(self, resource_group, spring, app):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            "app": app
        })

        self.cmd('spring app create -g {rg} -s {serviceName} -n {app}')

        self.cmd('spring service-registry show -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring service-registry bind --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.addonConfigs.serviceRegistry.resourceId',
                       "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/serviceRegistries/default".format(
                           self.get_subscription_id(), resource_group, spring))
        ])
        self.cmd('spring app delete -n {app} -g {rg} -s {serviceName}')
        #self.cmd('spring service-registry unbind --app {app} -g {rg} -s {serviceName}')

        self.cmd('spring service-registry delete -g {rg} -s {serviceName} --yes')

        self.cmd('spring service-registry create -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])
