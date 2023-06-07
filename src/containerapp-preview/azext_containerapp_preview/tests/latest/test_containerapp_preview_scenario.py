# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class containerappScenarioTest(ScenarioTest):

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(name_prefix='cli_test_containerapp_preview')
    def test_containerapp_preview(self, resource_group):
        self.cmd('az config set extension.use_dynamic_install=yes_without_prompt')
        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd("az containerapp create --name app --resource-group {} --environment my-environment --image 'mcr.microsoft.com/k8se/quickstart:latest' --environment-type connected".format(resource_group))