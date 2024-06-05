# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# import os
# import unittest

# from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

# TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

# class AcrcsscScenarioTest(ScenarioTest):

#     @ResourceGroupPreparer(name_prefix='cli_test_acrcssc')
#     def test_acrcssc(self, resource_group):

#         self.kwargs.update({
#             'taskType': 'ContinuousPatchV1',
#             'rg': 'test-rg',
#             'registry': 'testregistry',
#             'configpath': 'testconfigpath',
#             'cadence': '1d'
#         })

#         self.cmd('acr supply-chain task create -g {rg} -t {taskType} -r {registry} --config {configpath} --cadence {cadence}', checks=[
#             self.check('rg', '{rg}')
#         ])
#         self.cmd('acrcssc update -g {rg} -n {name} --tags foo=boo', checks=[
#             self.check('tags.foo', 'boo')
#         ])
#         count = len(self.cmd('acrcssc list').get_output_in_json())
#         self.cmd('acrcssc show - {rg} -n {name}', checks=[
#             self.check('name', '{name}'),
#             self.check('resourceGroup', '{rg}'),
#             self.check('tags.foo', 'boo')
#         ])
#         self.cmd('acrcssc delete -g {rg} -n {name}')
#         final_count = len(self.cmd('acrcssc list').get_output_in_json())
#         self.assertTrue(final_count, count - 1)