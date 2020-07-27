# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Storage-blob-previewScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_storage-blob-preview')
    def test_storage-blob-preview(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('storage-blob-preview create -g {rg} -n {name} --tags foo=doo', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('storage-blob-preview update -g {rg} -n {name} --tags foo=boo', checks=[
            self.check('tags.foo', 'boo')
        ])
        count = len(self.cmd('storage-blob-preview list').get_output_in_json())
        self.cmd('storage-blob-preview show - {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'boo')
        ])
        self.cmd('storage-blob-preview delete -g {rg} -n {name}')
        final_count = len(self.cmd('storage-blob-preview list').get_output_in_json())
        self.assertTrue(final_count, count - 1)