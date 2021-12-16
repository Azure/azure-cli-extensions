# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import JMESPathCheck
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
            'testIntegrationAccount': self.create_random_name(prefix='cli_test_integration_accounts'[:9], length=24),
            'IntegrationAccounts_2': self.create_random_name(prefix='cli_test_integration_accounts'[:9], length=24),
            'testWorkflow': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'Workflows_2': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'Workflows_3': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
        })

        self.cmd('az logic integration-account create '
                 '--location "centralus" '
                 '--sku Standard '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}" ',
                 checks=[JMESPathCheck('name', self.kwargs.get('IntegrationAccounts_2', ''))])

        self.cmd('az logic integration-account import '
                 '--location "centralus" '
                 '--input-path "src/logic/azext_logic/tests/latest/integration.json" '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}" ',
                 checks=[JMESPathCheck('name', self.kwargs.get('IntegrationAccounts_2', ''))])

        self.cmd('az logic workflow create '
                 '--resource-group "{rg}" '
                 '--location "centralus" '
                 '--definition "src/logic/azext_logic/tests/latest/workflow.json" '
                 '--name "{testWorkflow}"',
                 checks=[JMESPathCheck('name', self.kwargs.get('testWorkflow', ''))])

        self.cmd('az logic integration-account show '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[JMESPathCheck('name', self.kwargs.get('IntegrationAccounts_2', ''))])

        self.cmd('az logic workflow show '
                 '--resource-group "{rg}" '
                 '--name "{testWorkflow}"',
                 checks=[JMESPathCheck('name', self.kwargs.get('testWorkflow', ''))])

        self.cmd('az logic integration-account list '
                 '--resource-group "{rg_2}"',
                 checks=[JMESPathCheck('[0].name', self.kwargs.get('IntegrationAccounts_2', ''))])

        self.cmd('az logic workflow list '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheck('[0].name', self.kwargs.get('testWorkflow', ''))])

        self.cmd('az logic integration-account list',
                 checks=[JMESPathCheck('[0].name', self.kwargs.get('IntegrationAccounts_2', ''))])

        self.cmd('az logic workflow list',
                 checks=[JMESPathCheck('[0].name', self.kwargs.get('testWorkflow', ''))])

        self.cmd('az logic integration-account update '
                 '--sku Basic '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}"',
                 checks=[JMESPathCheck('sku.name', 'Basic')])

        self.cmd('az logic workflow update '
                 '--resource-group "{rg}" '
                 '--tag atag=123 '
                 '--definition "src/logic/azext_logic/tests/latest/workflowupdate.json" '
                 '--name "{testWorkflow}"',
                 checks=[JMESPathCheck('tags.atag', 123),
                         JMESPathCheck('definition.triggers.When_a_feed_item_is_published.recurrence.interval', 2)])

        self.cmd('az logic workflow update '
                 '--resource-group "{rg}" '
                 '--tag atag=foo '
                 '--name "{testWorkflow}"',
                 checks=[JMESPathCheck('tags.atag', 'foo'),
                         JMESPathCheck('definition.triggers.When_a_feed_item_is_published.recurrence.interval', 2)])

        self.cmd('az logic workflow delete '
                 '--resource-group "{rg}" '
                 '--name "{testWorkflow}" '
                 '-y',
                 checks=[])

        self.cmd('az logic integration-account delete '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}" '
                 '-y',
                 checks=[])
