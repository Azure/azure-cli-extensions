# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class CustomprovidersScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_custom_providers')
    def test_custom_providers(self, resource_group):

        self.cmd('az custom-providers association create '
                 '--scope "scope" '
                 '--name "associationName" '
                 '--target-resource-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.Solutions/applications/{{ application_name }}"',
                 checks=[])

        self.cmd('az custom-providers custom-resource-provider create '
                 '--resource-group {rg} '
                 '--name "newrp" '
                 '--location "eastus"',
                 checks=[])

        self.cmd('az custom-providers custom-resource-provider show '
                 '--resource-group {rg} '
                 '--name "newrp"',
                 checks=[])

        self.cmd('az custom-providers custom-resource-provider list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az custom-providers custom-resource-provider list',
                 checks=[])

        self.cmd('az custom-providers association show '
                 '--scope "scope" '
                 '--name "associationName"',
                 checks=[])

        self.cmd('az custom-providers association list '
                 '--scope "scope"',
                 checks=[])

        self.cmd('az custom-providers operation list',
                 checks=[])

        self.cmd('az custom-providers custom-resource-provider update '
                 '--resource-group {rg} '
                 '--name "newrp"',
                 checks=[])

        self.cmd('az custom-providers custom-resource-provider delete '
                 '--resource-group {rg} '
                 '--name "newrp"',
                 checks=[])

        self.cmd('az custom-providers association delete '
                 '--scope "scope" '
                 '--name "associationName"',
                 checks=[])
