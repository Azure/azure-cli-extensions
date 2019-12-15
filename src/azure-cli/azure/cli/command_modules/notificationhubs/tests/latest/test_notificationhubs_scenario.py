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

        self.cmd('az notificationhubs create '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--location "South Central US" '
                 '--tier "Standard"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub create '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs create_or_update_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--rights "Listen,Send"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub create_or_update_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub" '
                 '--rights "Listen,Send"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub get_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub list_authorization_rules '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs get_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub show '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs list_authorization_rules '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub list '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs show '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az notificationhubs list',
                 checks=[])

        self.cmd('az notificationhubs list',
                 checks=[])

        self.cmd('az notificationhubs notification-hub regenerate_keys '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub" '
                 '--policy-key "PrimaryKey"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub list_keys '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs regenerate_keys '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--policy-key "PrimaryKey"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub get_pns_credentials '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs list_keys '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub debug_send '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub update '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "sdk-notificationHubs-8708"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub check_notification_hub_availability '
                 '--resource-group {rg} '
                 '--namespace-name "locp-newns" '
                 '--name "sdktest" '
                 '--location "West Europe"',
                 checks=[])

        self.cmd('az notificationhubs update '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--tier "Standard"',
                 checks=[])

        self.cmd('az notificationhubs check_availability '
                 '--name "sdk-Namespace-2924"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub delete_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs delete_authorization_rule '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])

        self.cmd('az notificationhubs notification-hub delete '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns" '
                 '--notification-hub-name "nh-sdk-hub"',
                 checks=[])

        self.cmd('az notificationhubs delete '
                 '--resource-group {rg} '
                 '--namespace-name "nh-sdk-ns"',
                 checks=[])
