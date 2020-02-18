# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DatabricksClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_databricks')
    def test_databricks(self, resource_group):

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name "myWorkspace" '
                 '--location "westus" '
                 '--managed-resource-group-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}"',
                 checks=[])

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name "myWorkspace" '
                 '--location "westus" '
                 '--managed-resource-group-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}"',
                 checks=[])

        self.cmd('az databricks workspace show '
                 '--resource-group {rg} '
                 '--name "myWorkspace"',
                 checks=[])

        self.cmd('az databricks workspace show '
                 '--resource-group {rg} '
                 '--name "myWorkspace"',
                 checks=[])

        self.cmd('az databricks workspace list',
                 checks=[])

        self.cmd('az databricks workspace list',
                 checks=[])

        self.cmd('az databricks operation list',
                 checks=[])

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name "myWorkspace"',
                 checks=[])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name "myWorkspace"',
                 checks=[])
