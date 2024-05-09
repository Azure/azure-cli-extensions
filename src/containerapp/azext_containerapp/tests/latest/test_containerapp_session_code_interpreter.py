# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .common import (TEST_LOCATION, STAGE_LOCATION, write_test_file,
                     clean_up_test_file,
                     )
from .utils import create_containerapp_env

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerAppSessionCodeInterperterTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_session_code_interpreter_e2e(self, resource_group):
        location = TEST_LOCATION
        self.cmd('configure --defaults location={}'.format(location))

        env_name = self.create_random_name(prefix='aca-sp-env', length=24)
        create_containerapp_env(self, env_name, resource_group, TEST_LOCATION)

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
            JMESPathCheck('properties.status', 'Success'),
            JMESPathCheck('properties.stdout', 'Hello world\n')
        ])

        # upload a file
        txt_file = os.path.join(TEST_DIR, 'cert.txt')
        self.cmd("containerapp session code-interpreter upload -n {} -g {} --identifier {} --filepath {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            txt_file
            ),
            checks=[
            JMESPathCheck('value[0].properties.filename', 'cert.txt'),
        ])

        # list files
        files_list = self.cmd("containerapp session code-interpreter list-files -n {} -g {} --identifier {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name
            )).get_output_in_json()
        self.assertTrue(len(files_list) == 1)

        # check content
        file_content = self.cmd("containerapp session code-interpreter show-file-content -n {} -g {} --identifier {} --filename {}".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            "cert.txt"
            )).get_output_in_json()
        print(file_content)
        self.assertTrue(file_content == '\"testing\"')

        # delete file
        delete_response = self.cmd("containerapp session code-interpreter delete-file -n {} -g {} --identifier {} --filename {} --yes".format(
            sessionpool_name_python,
            resource_group,
            identifier_name,
            "cert.txt"
            ))
        


        

