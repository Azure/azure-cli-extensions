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
            'name': 'test1',
            'rg':'feng-cli-rg'
        })

        self.cmd('az notificationhubs namespace create '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--location "South Central US" '
                 '--sku-name "Standard" '
                 '--sku-tier "Standard"',
                 checks=[])

        self.cmd('az notificationhubs hub create '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--notification-hub-name "MyTestHub" '
                 '--location "South Central US" '
                 '--sku-name "Standard"',
                 checks=[])

        self.cmd('az notificationhubs namespace authorization_rule create'
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--name "MySpaceRule" '
                 '--rights "Listen,Send"',
                 checks=[])

        self.cmd('az notificationhubs namespace authorization_rule show'
            '--resource-group {rg} '
            '--namespace-name "MyTestSpace" '
            '--name "MySpaceRule"',
            checks=[])

        self.cmd('az notificationhubs namespace authorization_rule list_keys '
            '--resource-group {rg} '
            '--namespace-name "MyTestSpace" '
            '--name "MySpaceRule"',
            checks=[])

        self.cmd('az notificationhubs hub credential gcm update'
            '--resource-group {rg} '
            '--namespace-name "MyTestSpace" '
            '--notification-hub-name "MyTestHub" '
            '--google-api-key "AAAANgU-LAk:APA91bFs_MDVVfouFbeIHNx8p-y8ZHk3jLgxXr4CDZLbiCLKyRd9pnGSGI4BY9OeiZZXY3thSPN0Mh0_irhnymnhyWvauSgeCplUF1aDvDCB8lDiQngOgx6tOAbSohy1oZRLUXedgkWp"',
            checks=[])

        self.cmd('az notificationhubs hub get_pns_credentials '
            '--resource-group {rg} '
            '--namespace-name "MyTestSpace" '
            '--notification-hub-name "MyTestHub"',
            checks=[])

        self.cmd('az notificationhubs hub debug_send '
            '--resource-group {rg} '
            '--namespace-name "MyTestSpace" '
            '--notification-hub-name "MyTestHub" '
            '--notification-format gcm '
            '--payload "{\"data\":{\"message\":\"test notification\"}}"',
            checks=[])

        self.cmd('az notificationhubs hub authorization_rule create '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--notification-hub-name "MyTestHub" '
                 '--name "MyHubSendKey" '
                 '--rights "Send"',
                 checks=[])

        self.cmd('az notificationhubs hub authorization_rule show '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--notification-hub-name "MyTestHub" '
                 '--name "MyHubSendKey"',
                 checks=[])

        self.cmd('az notificationhubs hub authorization_rule list'
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--notification-hub-name "MyTestHub"',
                 checks=[])

        self.cmd('az notificationhubs hub authorization_rule list_keys '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--notification-hub-name "MyTestHub" '
                 '--name "MyHubSendKey"',
                 checks=[])   

        self.cmd('az notificationhubs hub show '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--notification-hub-name "MyTestHub"',
                 checks=[])

        self.cmd('az notificationhubs namespace authorization_rule list '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace"',
                 checks=[])

        self.cmd('az notificationhubs hub list '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace"',
                 checks=[])

        self.cmd('az notificationhubs namespace show '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace"',
                 checks=[])

        self.cmd('az notificationhubs namespace list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az notificationhubs hub authorization_rule regenerate_keys '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--notification-hub-name "MyTestHub" '
                 '--name "MyHubSendKey" '
                 '--policy-key "SecondaryKey"',
                 checks=[])

        self.cmd('az notificationhubs namespace authorization_rule regenerate_keys '
                 '--resource-group {rg} '
                 '--namespace-name "MyTestSpace" '
                 '--name "MySpaceRule"'
                 '--policy-key "SecondaryKey"',
                 checks=[])


