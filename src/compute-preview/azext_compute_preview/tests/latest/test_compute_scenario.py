# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# class ComputeScenarioTest(ScenarioTest):
#
#     @ResourceGroupPreparer(name_prefix='cli_test_compute-preview')
#     def test_compute-preview(self, resource_group):
#
#         self.kwargs.update({
#             'name': 'test1'
#         })
#
#         self.cmd('compute-preview create -g {rg} -n {name} --tags foo=doo', checks=[
#             self.check('tags.foo', 'doo'),
#             self.check('name', '{name}')
#         ])
#         self.cmd('compute-preview update -g {rg} -n {name} --tags foo=boo', checks=[
#             self.check('tags.foo', 'boo')
#         ])
#         count = len(self.cmd('compute-preview list').get_output_in_json())
#         self.cmd('compute-preview show - {rg} -n {name}', checks=[
#             self.check('name', '{name}'),
#             self.check('resourceGroup', '{rg}'),
#             self.check('tags.foo', 'boo')
#         ])
#         self.cmd('compute-preview delete -g {rg} -n {name}')
#         final_count = len(self.cmd('compute-preview list').get_output_in_json())
#         self.assertTrue(final_count, count - 1)


class SharedVMExtensionScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_shared_vm_extension_')
    def test_shared_vm_extension(self, resource_group):
        self.kwargs.update({
            'ext': 'ext1'
        })
        self.cmd('vm extension publish create -g {rg} -n {ext}')

    @ResourceGroupPreparer(name_prefix='cli_test_shared_vm_extension_version_')
    def test_shared_vm_extension_version(self, resource_group):
        self.kwargs.update({
            'ext': 'ext1'
        })
        self.cmd('vm extension publish-version create -g {rg} -n {ext} --version 1.0.0')
