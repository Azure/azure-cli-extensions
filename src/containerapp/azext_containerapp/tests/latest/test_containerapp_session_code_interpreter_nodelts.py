# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.command_modules.containerapp._utils import format_location

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)

from .common import (TEST_LOCATION)
from .utils import create_containerapp_env

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class ContainerAppSessionCodeInterperterNodeLTSTests(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer()
    def test_containerapp_session_code_interpreter_nodelts_e2e(self, resource_group):
        location = TEST_LOCATION
        self.cmd('configure --defaults location={}'.format(location))

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)

        # Create PythonLTS SessionPool with default container type which is PythonLTS
        sessionpool_name_pythonlts = self.create_random_name(prefix='sppythonlts', length=24)
        self.cmd('containerapp sessionpool create -g {} -n {} --cooldown-period {}'.format(
            resource_group, sessionpool_name_pythonlts, 300), checks=[
            JMESPathCheck('name', sessionpool_name_pythonlts),
            JMESPathCheck('properties.containerType', "PythonLTS"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.dynamicPoolConfiguration.cooldownPeriodInSeconds', 300)
        ])

        # Create NodeLTS SessionPool
        sessionpool_name_nodelts = self.create_random_name(prefix='spnodelts', length=24)
        self.cmd('containerapp sessionpool create -g {} -n {} --container-type NodeLTS --cooldown-period {}'.format(
            resource_group, sessionpool_name_nodelts, 300), checks=[
            JMESPathCheck('name', sessionpool_name_nodelts),
            JMESPathCheck('properties.containerType', "NodeLTS"),
            JMESPathCheck('properties.provisioningState', "Succeeded"),
            JMESPathCheck('properties.dynamicPoolConfiguration.cooldownPeriodInSeconds', 300)
        ])

        # List Session Pools
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 2)

        # execute nodejs code
        identifier_name = self.create_random_name(prefix='testidentifier', length=24)
        code = '\'console.log("'"Hello world"'")\''
        self.cmd("containerapp session code-interpreter execute -n {} -g {} --identifier {} --code {}".format(
            sessionpool_name_nodelts,
            resource_group,
            identifier_name,
            code),
            checks=[
            JMESPathCheck('properties.status', 'Success'),
            JMESPathCheck('properties.stdout', 'Hello world\n')
        ])

        # upload a file also add session pool location
        txt_file = os.path.join(TEST_DIR, 'cert.txt')
        self.cmd('containerapp session code-interpreter upload-file -n {} -g {} --identifier {} --filepath "{}" --session-pool-location {}'.format(
            sessionpool_name_nodelts,
            resource_group,
            identifier_name,
            txt_file,
            TEST_LOCATION),
            checks=[
            JMESPathCheck('value[0].properties.filename', 'cert.txt'),
        ])

        # list files
        files_list = self.cmd("containerapp session code-interpreter list-files -n {} -g {} --identifier {}".format(
            sessionpool_name_nodelts,
            resource_group,
            identifier_name)).get_output_in_json()
        self.assertTrue(len(files_list["value"]) == 1)

        # check content
        file_content = self.cmd("containerapp session code-interpreter show-file-content -n {} -g {} --identifier {} --filename {}".format(
            sessionpool_name_nodelts,
            resource_group,
            identifier_name,
            "cert.txt")).get_output_in_json()
        self.assertTrue(file_content == '\"testing\"')

        # check metadata
        self.cmd("containerapp session code-interpreter show-file-metadata -n {} -g {} --identifier {} --filename {}".format(
            sessionpool_name_nodelts,
            resource_group,
            identifier_name,
            "cert.txt"),
            checks=[
            JMESPathCheck('properties.filename', 'cert.txt'),
        ])

        # delete file
        self.cmd("containerapp session code-interpreter delete-file -n {} -g {} --identifier {} --filename {} --yes".format(
            sessionpool_name_nodelts,
            resource_group,
            identifier_name,
            "cert.txt"
            ))
        files_list = self.cmd("containerapp session code-interpreter list-files -n {} -g {} --identifier {}".format(
            sessionpool_name_nodelts,
            resource_group,
            identifier_name
            )).get_output_in_json()
        self.assertTrue(len(files_list["value"]) == 0)

        # delete sessionpool to clean up test resources
        self.cmd("containerapp sessionpool delete -n {} -g {} --yes".format(
            sessionpool_name_nodelts,
            resource_group,
            ))
        
        self.cmd("containerapp sessionpool delete -n {} -g {} --yes".format(
            sessionpool_name_pythonlts,
            resource_group,
            ))
        
        sessionpool_list = self.cmd("containerapp sessionpool list -g {}".format(resource_group)).get_output_in_json()
        self.assertTrue(len(sessionpool_list) == 0)