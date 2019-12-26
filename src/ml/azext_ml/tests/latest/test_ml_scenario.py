# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AzureMLScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_ml')
    def test_ml(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az ml create '
                 '--resource-group {rg} '
                 '--name "testworkspace" '
                 '--location "West Europe"',
                 checks=[])

        self.cmd('az ml show '
                 '--resource-group {rg} '
                 '--name "testworkspace"',
                 checks=[])

        self.cmd('az ml list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az ml list',
                 checks=[])

        self.cmd('az ml list_workspace_keys '
                 '--resource-group {rg} '
                 '--name "testworkspace"',
                 checks=[])

        self.cmd('az ml resync_storage_keys '
                 '--resource-group {rg} '
                 '--name "testworkspace"',
                 checks=[])

        self.cmd('az ml update '
                 '--resource-group {rg} '
                 '--name "testworkspace" '
                 '--key-vault-identifier-id "kvidnew"',
                 checks=[])

        self.cmd('az ml delete '
                 '--resource-group {rg} '
                 '--name "testworkspace"',
                 checks=[])
