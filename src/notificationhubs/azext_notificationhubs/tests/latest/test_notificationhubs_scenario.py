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

        self.cmd('az notificationhubs namespace create_or_update_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--rights "Listen,Send"',
                 checks=[])

        self.cmd('az notificationhubs hub create_or_update_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub" '
                 '--rights "Listen,Send"',
                 checks=[])

        self.cmd('az notificationhubs hub get_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs hub list_authorization_rules '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs namespace get_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs hub show '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs namespace list_authorization_rules '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs hub list '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs namespace show '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs namespace list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az notificationhubs namespace list',
                 checks=[])

        self.cmd('az notificationhubs namespace list',
                 checks=[])

        self.cmd('az notificationhubs hub regenerate_keys '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub" '
                 '--policy-key "PrimaryKey"',
                 checks=[])

        self.cmd('az notificationhubs hub list_keys '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs namespace regenerate_keys '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--policy-key "PrimaryKey"',
                 checks=[])

        self.cmd('az notificationhubs hub get_pns_credentials '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])
