# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


@record_only()
class BuildServiceBuildTest(ScenarioTest):
    def test_build(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-e',
            'rg': 'cli',
            'name': 'test',
            'result': '1',
        })

        self.cmd('spring build-service build show -n {name} -g {rg} --service {serviceName}', checks=[
            self.check('name', '{name}'),
            self.check('properties.resourceRequests.cpu', '1'),
            self.check('properties.resourceRequests.memory', '2Gi'),
            self.check('properties.provisioningState', 'Succeeded'),
        ])
        self.cmd('spring build-service build result show -n {result} --build-name {name} -g {rg} --service {serviceName}', checks=[
            self.check('name', '{result}'),
            self.check('properties.provisioningState', 'Succeeded'),
        ])
        self.cmd('spring build-service build delete -n {name} -g {rg} --service {serviceName} -y')

    def test_container_registry(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-e',
            'rg': 'cli',
            'name': 'default',
            'server': 'clitest1.azurecr.io',
            'username': 'clitest1',
        })

        self.cmd('spring container-registry show -n {name} -g {rg} --service {serviceName}', checks=[
            self.check('name', '{name}'),
            self.check('properties.credentials.server', '{server}'),
            self.check('properties.credentials.username', '{username}'),
        ])

        self.cmd('spring container-registry delete -n {name} -g {rg} --service {serviceName} -y')

    def test_build_service(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-e',
            'rg': 'cli',
            'registry': 'my-acr',
        })

        self.cmd('spring build-service show -g {rg} --service {serviceName}', checks=[
            self.check('name', 'default'),
            self.check('properties.provisioningState', 'Succeeded'),
        ])
