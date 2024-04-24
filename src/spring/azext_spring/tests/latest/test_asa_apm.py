# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
import os

from azure.cli.testsdk import (ScenarioTest)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)

from .custom_dev_setting_constant import SpringTestEnvironmentEnum
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringSubResourceWrapper)


APM_NAME = "apm-test"


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
            'spring apm delete --name {} -g {} -s {} --yes'.format(APM_NAME, self.resource_group, self.spring))
        self._safe_exec(
            'spring apm delete --name {}-0 -g {} -s {} --yes'.format(APM_NAME, self.resource_group, self.spring))


class ApmTest(ScenarioTest):

    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    @TearDown()
    def test_apm(self, resource_group, spring):

        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'apmName': APM_NAME,
            'type': "ApplicationInsights",
            'properties': "a=b b=c",
            'secrets': "x=y y=z",
        })

        self.cmd('spring apm create --name {apmName} --type {type} \
            --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.type', 'ApplicationInsights'),
                     self.check('properties.properties', {'a': 'b', 'b': 'c'}),
                     self.check('properties.secrets', None),
                 ])

        self.cmd('spring apm show --name {apmName} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.type', 'ApplicationInsights'),
                     self.check('properties.properties', {'a': 'b', 'b': 'c'}),
                     self.check('properties.secrets', {'x': '*', 'y': '*'}),
                 ])

        self.cmd('spring apm create --name {apmName}-0 --type NewRelic \
            --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.type', 'NewRelic'),
                     self.check('properties.properties', {'a': 'b', 'b': 'c'}),
                     self.check('properties.secrets', None),
                 ])

        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'apmName': APM_NAME,
            'type': "ApplicationInsights",
            'properties': "c=d d=e",
            'secrets': "o=p p=q",
        })

        self.cmd('spring apm update --name {apmName}-0 --type NewRelic \
                    --properties {properties} --secrets {secrets} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.type', 'NewRelic'),
                     self.check('properties.properties', {'c': 'd', 'd': 'e'}),
                     self.check('properties.secrets', None),
                 ])

        self.cmd('spring apm show --name {apmName}-0 -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.provisioningState', 'Succeeded'),
                     self.check('properties.type', 'NewRelic'),
                     self.check('properties.properties', {'c': 'd', 'd': 'e'}),
                     self.check('properties.secrets', {'o': '*', 'p': '*'}),
                 ])

        results = self.cmd('spring apm list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(2, len(results))

        results = self.cmd('spring apm list-enabled-globally -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(0, len(results['value']))

        self.cmd('spring apm enable-globally --name {apmName}-0 -g {rg} -s {serviceName}')

        results = self.cmd('spring apm list-enabled-globally -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(1, len(results['value']))

        self.cmd('spring apm disable-globally --name {apmName}-0 -g {rg} -s {serviceName}')

        results = self.cmd('spring apm list-enabled-globally -g {rg} -s {serviceName}').get_output_in_json()
        self.assertEqual(0, len(results['value']))
