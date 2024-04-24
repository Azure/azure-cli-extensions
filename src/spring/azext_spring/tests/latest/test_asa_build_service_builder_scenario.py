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


BUILDER_NAME = 'test-builder'


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
            'spring build-service builder delete -n {} -g {} -s {} --yes'.format(BUILDER_NAME, self.resource_group,
                                                                                 self.spring))


class BuildServiceBuilderTest(ScenarioTest):
    @SpringResourceGroupPreparer(
        dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    @TearDown()
    def test_Builder(self, resource_group, spring):
        py_path = os.path.abspath(os.path.dirname(__file__))
        builder_file = os.path.join(py_path, 'files/build_service_builder.json').replace("\\", "/")

        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'name': BUILDER_NAME,
            'builderFile': builder_file
        })

        self.cmd(
            'spring build-service builder create -n {name} -g {rg} --service {serviceName} --builder-file {builderFile}',
            checks=[
                self.check('name', '{name}'),
                self.check('properties.buildpackGroups[0].buildpacks[0].id', 'tanzu-buildpacks/java-azure'),
                self.check('properties.buildpackGroups[0].name', 'mix'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.stack.id', 'io.buildpacks.stacks.bionic'),
                self.check('properties.stack.version', 'base'),
            ])

        self.cmd('spring build-service builder show -n {name} -g {rg} --service {serviceName}', checks=[
            self.check('name', '{name}'),
            self.check('properties.buildpackGroups[0].buildpacks[0].id', 'tanzu-buildpacks/java-azure'),
            self.check('properties.buildpackGroups[0].name', 'mix'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.stack.id', 'io.buildpacks.stacks.bionic'),
            self.check('properties.stack.version', 'base'),
        ])

        results = self.cmd(
            'spring build-service builder show-deployments -n {name} -g {rg} --service {serviceName}').get_output_in_json()
        self.assertEqual(0, len(results['deployments']))
