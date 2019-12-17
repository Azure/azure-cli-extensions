# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class NotificationHubsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_notificationhubs')
    def test_notificationhubs(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('az notificationhubs namespace create '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--location "South Central US" '
                 '--sku-name "Standard" '
                 '--sku-tier "Standard"',
                 checks=[])

        self.cmd('az notificationhubs hub create '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])
