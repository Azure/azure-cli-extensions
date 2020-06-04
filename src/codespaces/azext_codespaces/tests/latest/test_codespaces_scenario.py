# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class CodespacesScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_codespaces')
    def test_codespaces(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        # TODO: Add full scenario tests when we have support for 'codespace plan create' without needing userId.
        count = len(self.cmd('codespace plan list -g {rg}').get_output_in_json())
        self.assertEqual(count, 0)
