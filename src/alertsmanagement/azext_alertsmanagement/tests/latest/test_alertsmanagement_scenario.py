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

    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement')
    def test_alertsmanagement(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az alertsmanagement create '
                 '--resource-group {rg} '
                 '--name "DailySuppression" '
                 '--location "Global" '
                 '--status "Enabled"',
                 checks=[])

        self.cmd('az alertsmanagement create '
                 '--resource-group {rg} '
                 '--name "MyAlertRule" '
                 '--description "Sample smart detector alert rule description" '
                 '--state "Enabled" '
                 '--severity "Sev3" '
                 '--frequency "PT5M"',
                 checks=[])

        self.cmd('az alertsmanagement show '
                 '--resource-group {rg} '
                 '--name "MyAlertRule"',
                 checks=[])

        self.cmd('az alertsmanagement show '
                 '--resource-group {rg} '
                 '--name "DailySuppression"',
                 checks=[])

        self.cmd('az alertsmanagement list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az alertsmanagement list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az alertsmanagement changestate get_history '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement change-state get_by_id '
                 '--smart-group-id "603675da-9851-4b26-854a-49fc53d32715"',
                 checks=[])

        self.cmd('az alertsmanagement changestate get_history '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az alertsmanagement changestate get_by_id '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement changestate get_summary',
                 checks=[])

        self.cmd('az alertsmanagement change-state get_all',
                 checks=[])

        self.cmd('az alertsmanagement list',
                 checks=[])

        self.cmd('az alertsmanagement changestate get_all',
                 checks=[])

        self.cmd('az alertsmanagement changestate meta_data',
                 checks=[])

        self.cmd('az alertsmanagement update '
                 '--resource-group {rg} '
                 '--name "MyAlertRule" '
                 '--description "New description for patching" '
                 '--frequency "PT1M"',
                 checks=[])

        self.cmd('az alertsmanagement update '
                 '--resource-group {rg} '
                 '--name "WeeklySuppression" '
                 '--status "Disabled"',
                 checks=[])

        self.cmd('az alertsmanagement change-state change_state '
                 '--smart-group-id "a808445e-bb38-4751-85c2-1b109ccc1059" '
                 '--new-state "Acknowledged"',
                 checks=[])

        self.cmd('az alertsmanagement changestate get_history '
                 '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
                 checks=[])

        self.cmd('az alertsmanagement delete '
                 '--resource-group {rg} '
                 '--name "MyAlertRule"',
                 checks=[])

        self.cmd('az alertsmanagement delete '
                 '--resource-group {rg} '
                 '--name "DailySuppression"',
                 checks=[])
