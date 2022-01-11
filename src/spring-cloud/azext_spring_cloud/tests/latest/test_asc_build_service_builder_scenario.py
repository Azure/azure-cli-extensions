# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

@record_only()
class BuildServiceBuilderTest(ScenarioTest):
    def test_Builder(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        builder_file = os.path.join(py_path, 'files/build_service_builder.json').replace("\\","/")

        self.kwargs.update({
            'serviceName': 'cli-unittest',
            'rg': 'cli',
            'name': 'test-builder',
            'builderFile': builder_file
        })

        self.cmd('spring-cloud build-service builder create -n {name} -g {rg} --service {serviceName} --builder-file {builderFile}', checks=[
            self.check('name', '{name}'),
            self.check('properties.buildpackGroups[0].buildpacks[0].id', 'tanzu-buildpacks/java-azure'),
            self.check('properties.buildpackGroups[0].name', 'mix'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.stack.id', 'io.buildpacks.stacks.bionic'),
            self.check('properties.stack.version', 'base'),
        ])
        
        self.cmd('spring-cloud build-service builder update -n test -g {rg} --service {serviceName} --builder-file {builderFile}', checks=[
            self.check('name', 'test'),
            self.check('properties.buildpackGroups[0].buildpacks[0].id', 'tanzu-buildpacks/java-azure'),
            self.check('properties.buildpackGroups[0].name', 'mix'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.stack.id', 'io.buildpacks.stacks.bionic'),
            self.check('properties.stack.version', 'base'),
        ])

        self.cmd('spring-cloud build-service builder show -n {name} -g {rg} --service {serviceName}', checks=[
            self.check('name', '{name}'),
            self.check('properties.buildpackGroups[0].buildpacks[0].id', 'tanzu-buildpacks/java-azure'),
            self.check('properties.buildpackGroups[0].name', 'mix'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.stack.id', 'io.buildpacks.stacks.bionic'),
            self.check('properties.stack.version', 'base'),
        ])

        self.cmd('spring-cloud build-service builder delete -n {name} -g {rg} --service {serviceName} -y')
