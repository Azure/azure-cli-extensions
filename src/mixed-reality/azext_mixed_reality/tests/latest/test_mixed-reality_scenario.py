# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class MixedRealityClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_mixed_reality')
    def test_mixed_reality(self, resource_group):

        self.cmd('az mixed-reality spatial-anchors-account create '
                 '--resource-group {rg} '
                 '--name "MyAccount" '
                 '--location "eastus2euap"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account create '
                 '--resource-group {rg} '
                 '--name "MyAccount" '
                 '--location "eastus2euap"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account get-keys '
                 '--resource-group {rg} '
                 '--name "MyAccount"',
                 checks=[])

        self.cmd('az mixed-reality spatial-anchors-account get-keys '
                 '--resource-group {rg} '
                 '--name "MyAccount"',
                 checks=[])

        self.cmd('az mixed-reality spatial-anchors-account list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az mixed-reality spatial-anchors-account show '
                 '--resource-group {rg} '
                 '--name "MyAccount"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account show '
                 '--resource-group {rg} '
                 '--name "MyAccount"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account list',
                 checks=[])

        self.cmd('az mixed-reality spatial-anchors-account list',
                 checks=[])

        # self.cmd('az mixed-reality operation list',
        #          checks=[])

        self.cmd('az mixed-reality remote-rendering-account regenerate-keys '
                 '--resource-group {rg} '
                 '--name "MyAccount" '
                 '--serial "1"',
                 checks=[])

        self.cmd('az mixed-reality spatial-anchors-account regenerate-keys '
                 '--resource-group {rg} '
                 '--name "MyAccount" '
                 '--serial "1"',
                 checks=[])

        # self.cmd('az mixed-reality remote-rendering-account update '
        #          '--resource-group {rg} '
        #          '--name "MyAccount"',
        #          checks=[])

        # self.cmd('az mixed-reality spatial-anchors-account update '
        #          '--resource-group {rg} '
        #          '--name "MyAccount"',
        #          checks=[])

        # self.cmd('az mixed-reality location check-name-availability check-name-availability-local '
        #          '--location "eastus2euap" '
        #          '--name "MyAccount" '
        #          '--type "SpatialAnchorsAccount"',
        #          checks=[])

        self.cmd('az mixed-reality spatial-anchors-account delete '
                 '--resource-group {rg} '
                 '--name "MyAccount"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account delete '
                 '--resource-group {rg} '
                 '--name "MyAccount"',
                 checks=[])
