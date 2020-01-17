# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AlertsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_alert_rule_')
    def test_alertsmanagement_alert_rule(self, resource_group):

        ag1_id = self.cmd('monitor action-group create -g {rg} -n ag1').get_output_in_json()['id']

        self.kwargs.update({
            'ag1_id': ag1_id
        })

        self.cmd('az alertsmanagement smart-detector-alert-rule create '
                 '--resource-group {rg} '
                 '--name "MyAlertRule" '
                 '--description "Sample smart detector alert rule description" '
                 '--state "Enabled" '
                 '--severity "Sev3" '
                 '--frequency "PT5M" '
                 '--detector aaa '
                 '--scope bbb '
                 '--action-groups {ag1_id}',
                 checks=[])

    @ResourceGroupPreparer()
    def test_alertsmanagement(self, resource_group):
        # self.cmd('az alertsmanagement action-rule create '
        #          '--resource-group {rg} '
        #          '--name "DailySuppression" '
        #          '--location "Global" '
        #          '--status "Enabled"',
        #          checks=[])



        self.cmd('az alertsmanagement smart-detector-alert-rule show '
                 '--resource-group {rg} '
                 '--name "MyAlertRule"',
                 checks=[])

        self.cmd('az alertsmanagement action-rule show '
                 '--resource-group {rg} '
                 '--name "DailySuppression"',
                 checks=[])

        self.cmd('az alertsmanagement smart-detector-alert-rule list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az alertsmanagement action-rule list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az alertsmanagement alert get-history '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement smart-group get-by-id '
                 '--smart-group-id "603675da-9851-4b26-854a-49fc53d32715"',
                 checks=[])

        self.cmd('az alertsmanagement alert get-history '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement smart-detector-alert-rule list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az alertsmanagement alert get-by-id '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement alert get-summary',
                 checks=[])

        self.cmd('az alertsmanagement smart-group get-all',
                 checks=[])

        self.cmd('az alertsmanagement action-rule list',
                 checks=[])

        self.cmd('az alertsmanagement alert get-all',
                 checks=[])

        self.cmd('az alertsmanagement alert meta-data',
                 checks=[])

        self.cmd('az alertsmanagement smart-detector-alert-rule update '
                 '--resource-group {rg} '
                 '--name "MyAlertRule" '
                 '--description "New description for patching" '
                 '--frequency "PT1M"',
                 checks=[])

        self.cmd('az alertsmanagement action-rule update '
                 '--resource-group {rg} '
                 '--name "WeeklySuppression" '
                 '--status "Disabled"',
                 checks=[])

        self.cmd('az alertsmanagement smart-group change-state '
                 '--smart-group-id "a808445e-bb38-4751-85c2-1b109ccc1059" '
                 '--new-state "Acknowledged"',
                 checks=[])

        self.cmd('az alertsmanagement alert get-history '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement smart-detector-alert-rule delete '
                 '--resource-group {rg} '
                 '--name "MyAlertRule"',
                 checks=[])

        self.cmd('az alertsmanagement action-rule delete '
                 '--resource-group {rg} '
                 '--name "DailySuppression"',
                 checks=[])
