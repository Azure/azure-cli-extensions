# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)
from knack.testsdk import live_only

from .common import (TEST_LOCATION)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerAppSessionCodeInterperterFilesTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    @live_only()
    def test_containerapp_session_code_interpreter_files_e2e(self, resource_group):
        location = TEST_LOCATION
        self.cmd('configure --defaults location={}'.format(location))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)

        # Create JupyterPython SessionPool
        sessionpool_name_python = self.create_random_name(prefix='spjupyterpython', length=24)
        self.cmd('containerapp sessionpool create -g {} -n {} --cooldown-period {}'.format(
            resource_group, sessionpool_name_python, 300), checks=[
            JMESPathCheck('name', sessionpool_name_python),
            JMESPathCheck('properties.containerType', "PythonLTS"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.dynamicPoolConfiguration.cooldownPeriodInSeconds', 300)
        ])

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 1)

        # execute python code
        identifier_name = self.create_random_name(prefix='testidentifier', length=24)
        code = '\'print("'"Hello world"'")\''
        self.cmd("containerapp session code-interpreter execute -n {} -g {} --identifier {} --code {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            code),
            checks=[
            JMESPathCheck('status', 'Succeeded'),
            JMESPathCheck('result.stdout', 'Hello world\n')
        ])

        # upload a file also add session pool location
        txt_file_name = 'cert.txt'
        txt_file = os.path.join(TEST_DIR, txt_file_name)
        path = '/'
        self.cmd('containerapp session code-interpreter upload-file -n {} -g {} --identifier {} --filepath "{}" --path {} --session-pool-location {}'.format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            txt_file,
            path,
            TEST_LOCATION),
            checks=[
            JMESPathCheck('name', txt_file_name),
        ])

        # list files
        files_list = self.cmd("containerapp session code-interpreter list-files -n {} -g {} --identifier {} --path {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            path)).get_output_in_json()
        self.assertTrue(len(files_list["value"]) == 1)

        # check content
        file_content = self.cmd("containerapp session code-interpreter show-file-content -n {} -g {} --identifier {} --filename {} --path {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            txt_file_name,
            path)).get_output_in_json()
        self.assertTrue(file_content == '\"testing\"')

        # check metadata
        self.cmd("containerapp session code-interpreter show-file-metadata -n {} -g {} --identifier {} --filename {} --path {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            txt_file_name,
            path),
            checks=[
            JMESPathCheck('name', txt_file_name),
        ])

        # delete file
        self.cmd("containerapp session code-interpreter delete-file -n {} -g {} --identifier {} --filename {} --path {} --yes".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            txt_file_name,
            path
            ))
        files_list = self.cmd("containerapp session code-interpreter list-files -n {} -g {} --identifier {} --path {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            path
            )).get_output_in_json()
        self.assertTrue(len(files_list["value"]) == 0)

        # delete sessionpool to clean up test resources
        self.cmd("containerapp sessionpool delete -n {} -g {} --yes".format(
            sessionpool_name_python,
            resource_group,
            ))
        
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)