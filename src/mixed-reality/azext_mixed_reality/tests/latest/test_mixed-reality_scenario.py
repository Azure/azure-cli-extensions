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

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az mixed-reality remote-rendering-account create '
                 '--resource-group {rg} '
                 '--name "alpha" '
                 '--location "EastUs2"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account create '
                 '--resource-group {rg} '
                 '--name "alpha" '
                 '--location "EastUs2"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account get_keys '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account get_keys '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account show '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account show '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account show '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account show '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account list',
                 checks=[])

        self.cmd('az mixed-reality spatial-anchors-account list',
                 checks=[])

        self.cmd('az mixed-reality operation list',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account regenerate_keys '
                 '--resource-group {rg} '
                 '--name "alpha" '
                 '--serial "1"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account regenerate_keys '
                 '--resource-group {rg} '
                 '--name "alpha" '
                 '--serial "1"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account update '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account update '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality location check-name-availability check_name_availability_local '
                 '--location "Global"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account delete '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])

        self.cmd('az mixed-reality remote-rendering-account delete '
                 '--resource-group {rg} '
                 '--name "alpha"',
                 checks=[])
