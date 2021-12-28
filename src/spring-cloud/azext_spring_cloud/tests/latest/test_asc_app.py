# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


@record_only()
class BlueGreenTest(ScenarioTest):

    def test_blue_green_deployment(self):
        self.kwargs.update({
            'app': 'test-app-blue-green',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })

        self.cmd('spring-cloud app create -n {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'default')
        ])

        self.cmd('spring-cloud app deployment create --app {app} -n green -g {rg} -s {serviceName}', checks=[
            self.check('name', 'green'),
            self.check('properties.active', False)
        ])

        result = self.cmd('spring-cloud app deployment list --app {app} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) == 2)

        self.cmd('spring-cloud app set-deployment -d green -n {app} -g {rg} -s {serviceName}')

        self.cmd('spring-cloud app show -n {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{app}'),
            self.check('properties.activeDeployment.name', 'green')
        ])

        self.cmd('spring-cloud app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', False)
        ])

        self.cmd('spring-cloud app deployment show -n green --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', True)
        ])

        self.cmd('spring-cloud app unset-deployment -n {app} -g {rg} -s {serviceName}')

        self.cmd('spring-cloud app deployment show -n default --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', False)
        ])

        self.cmd('spring-cloud app deployment show -n green --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('properties.active', False)
        ])

        self.cmd('spring-cloud app delete -n {app} -g {rg} -s {serviceName}')