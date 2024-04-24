# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringAppNamePreparer,
                               SpringSubResourceWrapper)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum


# pylint: disable=line-too-long
# pylint: disable=too-many-lines

class TearDown(SpringSubResourceWrapper):
    def __init__(self,
                resource_group_parameter_name='resource_group',
                spring_parameter_name='spring'):
        super(TearDown, self).__init__()
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.spring_parameter_name = spring_parameter_name

    def create_resource(self, *_, **kwargs):
        self.resource_group = self._get_resource_group(**kwargs)
        self.spring = self._get_spring(**kwargs)
        try:
            self.live_only_execute(self.cli_ctx, 'spring application-configuration-service create -g {} -s {}'
                .format(self.resource_group, self.spring))
        except:
            pass
        
    def remove_resource(self, *_, **__):
        self.live_only_execute(self.cli_ctx, 'spring application-configuration-service delete -g {} -s {} --yes'
            .format(self.resource_group, self.spring))


class ApplicationConfigurationServiceTest(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    @SpringAppNamePreparer()
    @TearDown()
    def test_application_configuration_service(self, resource_group, spring, app):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'repo': "repo1",
            "label": "main",
            "patterns": "api-gateway,customers-service",
            "uri": "https://github.com/spring-petclinic/spring-petclinic-microservices-config",
            "app": app
        })

        self.cmd('spring app create -g {rg} -s {serviceName} -n {app}')

        self.cmd('spring application-configuration-service show -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-configuration-service git repo add -g {rg} -s {serviceName} '
                '-n {repo} --label {label} --patterns {patterns} --uri {uri}',
                checks=[self.check('properties.provisioningState', "Succeeded")])

        self.cmd('spring application-configuration-service git repo update -g {rg} -s {serviceName} '
                '-n {repo} --label {label}',
                checks=[self.check('properties.provisioningState', "Succeeded")])

        result = self.cmd(
            'spring application-configuration-service git repo list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring application-configuration-service git repo remove --name {repo} -g {rg} -s {serviceName}')
        result = self.cmd(
            'spring application-configuration-service git repo list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) == 0)

        self.cmd('spring application-configuration-service bind --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.addonConfigs.applicationConfigurationService.resourceId',
                "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/configurationServices/default".format(
                self.get_subscription_id(), resource_group, spring))
        ])

        self.cmd('spring app show -n {app} -g {rg} -s {serviceName}')

        #self.cmd('spring application-configuration-service unbind --app {app} -g {rg} -s {serviceName}')

        self.cmd('spring application-configuration-service clear -g {rg} -s {serviceName}', checks=[
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring application-configuration-service update -g {rg} -s {serviceName} --generation Gen2 --refresh-interval 10',
                checks=[
                    self.check('properties.provisioningState', "Succeeded"),
                    self.check('properties.generation', "Gen2"),
                    self.check('properties.settings.refreshIntervalInSeconds', 10)])

        self.cmd('spring app delete -n {app} -g {rg} -s {serviceName}')
        self.cmd('spring application-configuration-service delete -g {rg} -s {serviceName} --yes')

        self.cmd('spring application-configuration-service create -g {rg} -s {serviceName} --generation Gen1 --refresh-interval 20',
                checks=[
                    self.check('properties.provisioningState', "Succeeded"),
                    self.check('properties.generation', "Gen1"),
                    self.check('properties.settings.refreshIntervalInSeconds', 20)])
