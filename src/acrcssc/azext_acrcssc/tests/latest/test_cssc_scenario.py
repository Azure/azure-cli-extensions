# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from os import path
import os
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

# TO DO: Need to see runtime issue with login
# class AcrcsscScenarioTest(ScenarioTest):
#     TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
#     @ResourceGroupPreparer(name_prefix='cli_test_acrcssc')
#     def test_create_supplychain_workflow(self, resource_group):
#         currdir = path.dirname(__file__)
#         print(currdir)
#         print(os.path.abspath(os.path.join(os.path.abspath(__file__), '..')))
#         file_name = os.path.join(currdir, 'artifact.json')
#         file_name = file_name.replace("\\", "\\\\")
#         self.kwargs.update({
#             'taskType': 'continuouspatchv1',
#             'configpath': file_name,
#             'cadence': '1d',
#             'registry':self.create_random_name(prefix='cli', length=24),
#         })

#         self.cmd('az acr create -g {rg} -n {registry} --sku Basic')
#         self.cmd('az acr supply-chain workflow create -g {rg} -t {taskType} -r {registry} --config {configpath} --cadence {cadence} --defer-immediate-run'.format(**self.kwargs))
#         cssc_tasks = self.cmd('az acr supply-chain workflow show -g {rg} -t {taskType} -r {registry}').get_output_in_json()
#         # Verify all the cssc tasks are created
#         assert len(cssc_tasks) == 3
#         cssc_trigger_scan_task = next((task for task in cssc_tasks if task['name'] == 'cssc-trigger-scan'), None)
#         # Verify cssc_trigger_scan_task properties
#         assert cssc_trigger_scan_task is not None
#         assert cssc_trigger_scan_task['cadence'] == '1d'