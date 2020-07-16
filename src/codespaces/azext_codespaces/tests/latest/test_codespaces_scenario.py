# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, live_only)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class CodespacesScenarioTest(ScenarioTest):
    plan_resource_type = 'Microsoft.Codespaces/plans'
    default_location = 'westus2'
    rg_name_prefix = 'azclitest_'

    @ResourceGroupPreparer(name_prefix=rg_name_prefix, location=default_location)
    def test_codespaces_plan(self, resource_group):
        self.kwargs.update({
            'name': 'azclitest-codespace-plan'
        })
        self.cmd('codespace plan create -g {rg} -n {name}')
        count = len(self.cmd('codespace plan list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1)
        self.cmd('codespace plan show -g {rg} -n {name}', checks=[
            self.check('type', self.plan_resource_type),
            self.check('name', '{name}'),
            self.check('location', self.default_location)
        ])
        self.cmd('codespace plan delete -g {rg} -n {name} --yes')
        count = len(self.cmd('codespace plan list -g {rg}').get_output_in_json())
        self.assertEqual(count, 0)

    def test_codespaces_location(self):
        self.cmd('codespace location list').get_output_in_json()
        self.cmd('codespace location show -n westus2')

    @live_only()  # do not save recordings for this test.
    @ResourceGroupPreparer(name_prefix=rg_name_prefix, location=default_location)
    def test_codespaces_codespace(self, resource_group):
        self.kwargs.update({
            'name': 'azclitest-codespace-plan',
            'codespace_name': 'codespace1',
            'instance_type': 'standardLinux',
            'suspend_after': '120'
        })
        plan_info = self.cmd('codespace plan create -g {rg} -n {name}').get_output_in_json()
        self.kwargs.update({
            'plan_id': plan_info['id']
        })
        self.cmd('codespace create --plan {plan_id} --name {name} --instance-type {instance_type} --suspend-after {suspend_after}')
        count = len(self.cmd('codespace list --plan {plan_id}').get_output_in_json())
        self.assertEqual(count, 1)
        self.cmd('codespace show --plan {plan_id} --name {name}', checks=[
            self.check('friendlyName', '{name}'),
            self.check('skuName', '{instance_type}'),
            self.check('autoShutdownDelayMinutes', '{suspend_after}')
        ])
        self.cmd('codespace delete --plan {plan_id} -n {name} --yes')
        count = len(self.cmd('codespace list  --plan {plan_id}').get_output_in_json())
        self.assertEqual(count, 0)
