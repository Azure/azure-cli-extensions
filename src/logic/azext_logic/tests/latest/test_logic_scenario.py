# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class LogicManagementClientScenarioTest(ScenarioTest):

    def current_subscription(self):
        subs = self.cmd('az account show').get_output_in_json()
        return subs['id']

    @ResourceGroupPreparer(name_prefix='cli_test_logic_test-resource-group'[:9], key='rg')
    @ResourceGroupPreparer(name_prefix='cli_test_logic_testResourceGroup'[:9], key='rg_2')
    def test_logic(self, resource_group):

        self.kwargs.update({
            'subscription_id': self.current_subscription()
        })

        self.kwargs.update({
            'test-integration-account': self.create_random_name(prefix='cli_test_integration_accounts'[:9], length=24),
            'IntegrationAccounts_2': self.create_random_name(prefix='cli_test_integration_accounts'[:9], length=24),
            'test-workflow': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'Workflows_2': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'Workflows_3': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
        })

        self.cmd('az logic integration-account create '
                 '--resource-group "{rg_2}" '
                 '--name "{IntegrationAccounts_2}" '
                 '--input-path "integration.json" ',
                 checks=[])

        self.cmd('az logic workflow create '
                 '--resource-group "{rg}" '
                 '--name "{test-workflow}" '
                 '--location "centralus" '
                 '--input-path "workflow.json" ',
                 checks=[])

        self.cmd('az logic integration-account show '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow show '
                 '--resource-group "{rg}" '
                 '--name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-account list '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow list '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az logic integration-account list',
                 checks=[])

        self.cmd('az logic workflow list',
                 checks=[])

        self.cmd('az logic integration-account update '
                 '--sku Basic '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])

        self.cmd('az logic workflow update '
                 '--resource-group "{rg}" '
                 '--tag atga=123 '
                 '--name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic workflow delete '
                 '--resource-group "{rg}" '
                 '--name "{test-workflow}"',
                 checks=[])

        self.cmd('az logic integration-account delete '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[])
