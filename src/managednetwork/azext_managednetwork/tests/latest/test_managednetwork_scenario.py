# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ManagedNetworkScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_managednetwork')
    def test_managednetwork(self, resource_group):

        self.kwargs.update({
            'sub': self.get_subscription_id()
        })

        self.cmd('az managednetwork create --resource-group "{rg}" --name "myManagedNetwork" --location "eastus" --scope-subscriptions {sub}')
