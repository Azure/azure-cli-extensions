# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


@unittest.skip("Managed environment flaky")
class ContainerappScenarioTest(ScenarioTest):
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="centraluseuap")
    def test_containerapp_e2e(self, resource_group):
        containerapp_name = self.create_random_name(prefix='containerapp-e2e', length=24)
        env_name = self.create_random_name(prefix='containerapp-e2e-env', length=24)

        self.cmd('containerapp env create -g {} -n {}'.format(resource_group, env_name))

        # Sleep in case env create takes a while
        time.sleep(60)
        self.cmd('containerapp env list -g {}'.format(resource_group), checks=[
            JMESPathCheck('length(@)', 1),
            JMESPathCheck('[0].name', env_name),
        ])

        self.cmd('containerapp create -g {} -n {} --environment {}'.format(resource_group, containerapp_name, env_name), checks=[
            JMESPathCheck('name', containerapp_name)
        ])

        # Sleep in case containerapp create takes a while
        time.sleep(60)
        self.cmd('containerapp show -g {} -n {}'.format(resource_group, containerapp_name), checks=[
            JMESPathCheck('name', containerapp_name)
        ])
