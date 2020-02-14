# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class PowerBIDedicatedScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_powerbidedicated')
    def test_powerbidedicated(self, resource_group):

        self.cmd('az powerbi embedded-capacity create '
                 '--resource-group {rg} '
                 '--name "azsdktest" '
                 '--sku-name "A1" '
                 '--sku-tier "PBIE_Azure" '
                 '--administration-members "azsdktest@microsoft.com,azsdktest2@microsoft.com"',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list-skus-for-capacity '
                 '--resource-group {rg} '
                 '--name "azsdktest"',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list-skus',
                 checks=[])

        self.cmd('az powerbi embedded-capacity suspend '
                 '--resource-group {rg} '
                 '--name "azsdktest"',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list',
                 checks=[])

        self.cmd('az powerbi embedded-capacity update '
                 '--resource-group {rg} '
                 '--name "azsdktest" '
                 '--sku-name "A1" '
                 '--sku-tier "PBIE_Azure" '
                 '--administration-members "azsdktest@microsoft.com,azsdktest2@microsoft.com"',
                 checks=[])

        self.cmd('az powerbi embedded-capacity check-name-availability '
                 '--type "Microsoft.PowerBIDedicated/capacities"',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list',
                 checks=[])
