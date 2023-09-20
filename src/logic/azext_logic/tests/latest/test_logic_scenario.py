# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import JMESPathCheck
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer, record_only


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class LogicManagementClientScenarioTest(ScenarioTest):

    def current_subscription(self):
        subs = self.cmd('az account show').get_output_in_json()
        return subs['id']

    @ResourceGroupPreparer(name_prefix='cli_test_logic_test-resource-group'[:9], key='rg')
    @ResourceGroupPreparer(name_prefix='cli_test_logic_testResourceGroup'[:9], key='rg_2')
    def test_logic(self, resource_group):
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        self.kwargs.update({
            'testIntegrationAccount': self.create_random_name(prefix='cli_test_integration_accounts'[:9], length=24),
            'IntegrationAccounts_2': self.create_random_name(prefix='cli_test_integration_accounts'[:9], length=24),
            'testWorkflow': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'Workflows_2': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'Workflows_3': self.create_random_name(prefix='cli_test_workflows'[:9], length=24),
            'input_path': os.path.join(curr_dir, 'integration.json'),
            'definition_path': os.path.join(curr_dir, 'workflow.json'),
            'definition_path_2': os.path.join(curr_dir, 'workflowupdate.json'),
        })

        self.cmd('az logic integration-account create '
                 '--location "centralus" '
                 '--sku Standard '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}" ',
                 checks=[JMESPathCheck('name', self.kwargs.get('IntegrationAccounts_2', ''))])

        self.cmd('az logic integration-account import '
                 '--location "centralus" '
                 '--input-path "{input_path}" '
                 '--name "{IntegrationAccounts_2}" '
                 '--resource-group "{rg_2}" ',
                 checks=[JMESPathCheck('name', self.kwargs.get('IntegrationAccounts_2', ''))])

        self.cmd('az logic workflow create '
                 '--resource-group "{rg}" '
                 '--location "centralus" '
                 '--definition "{definition_path}" '
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
                 '--definition "{definition_path_2}" '
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

    @ResourceGroupPreparer()
    def test_integration_account_map(self):
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        map_content = os.path.join(curr_dir, 'map_content.txt').replace('\\', '\\\\')
        self.kwargs.update({
            'account': self.create_random_name('acc', 10),
            'map': self.create_random_name('map', 10),
            'content': map_content
        })
        self.cmd('logic integration-account create -g {rg} -n {account} --sku standard')
        self.cmd('logic integration-account map create -g {rg} -n {map} --integration-account {account} --map-type Xslt --content-type application/xml --map-content {content}', checks=[
            self.check('name', '{map}'),
            self.check('mapType', 'Xslt'),
            self.exists('contentLink.uri')
        ])
        self.cmd('logic integration-account map update -g {rg} -n {map} --integration-account {account}', checks=[
            self.check('name', '{map}'),
            self.check('mapType', 'Xslt'),
            self.exists('contentLink.uri')
        ])
        self.cmd('logic integration-account map show -g {rg} -n {map} --integration-account {account}', checks=[
            self.check('name', '{map}'),
            self.check('mapType', 'Xslt'),
            self.exists('contentLink.uri')
        ])
        self.cmd('logic integration-account map list -g {rg} --integration-account {account}', checks=[
            self.check('[0].name', '{map}'),
            self.check('[0].mapType', 'Xslt'),
            self.exists('[0].contentLink.uri')
        ])
        self.cmd('logic integration-account map delete -g {rg} -n {map} --integration-account {account} -y')
