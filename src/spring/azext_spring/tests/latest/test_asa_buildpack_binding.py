# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringSubResourceWrapper)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

BINDING_NAME = "binding"


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

    def remove_resource(self, *_, **__):
        self._safe_exec(
            'spring build-service builder buildpack-binding delete --name {} -g {} -s {} --yes'.format(BINDING_NAME,
                                                                                                       self.resource_group,
                                                                                                       self.spring))
        self._safe_exec(
            'spring build-service builder buildpack-binding delete --name {}-0 -g {} -s {} --yes'.format(BINDING_NAME,
                                                                                                         self.resource_group,
                                                                                                         self.spring))


class BuildpackBindingTest(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    @TearDown()
    def test_buildpack_binding(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'bindingName': BINDING_NAME,
            'bindingType': "ApplicationInsights",
            'properties': "a=b b=c",
            'secrets': "x=y y=z",
            'builderName': "builder",
        })

        self.cmd('spring build-service builder buildpack-binding create --name {bindingName} --type {bindingType} \
            --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.bindingType', 'ApplicationInsights'),
                     self.check('properties.launchProperties.properties', {'a': 'b', 'b': 'c'}),
                     self.check('properties.launchProperties.secrets', {'x': '*', 'y': '*'}),
                 ])

        self.cmd('spring build-service builder buildpack-binding show --name {bindingName} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.bindingType', 'ApplicationInsights'),
                 ])

        self.cmd('spring build-service builder buildpack-binding create --name {bindingName}-0 --type NewRelic \
            --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.bindingType', 'NewRelic'),
                     self.check('properties.launchProperties.properties', {'a': 'b', 'b': 'c'}),
                     self.check('properties.launchProperties.secrets', {'x': '*', 'y': '*'}),
                 ])

        results = self.cmd(
            'spring build-service builder buildpack-binding list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(2, len(results))
