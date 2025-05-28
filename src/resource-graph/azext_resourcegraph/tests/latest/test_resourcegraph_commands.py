# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests.const import MOCKED_SUBSCRIPTION_ID
from knack.util import CLIError
from six import string_types
import json


class ResourceGraphTests(ScenarioTest):
    def test_query(self):
        command = 'az graph query -q "project id, tags, properties | limit 2"'
        response = self.cmd(command).get_output_in_json()

        self.assertIsInstance(response, dict)
        self.assertTrue(len(response) == 4)  # first element is data, second element is skip_token (or None)

        data = response['data']
        skip_token = response['skip_token']
        self.assertTrue(data is not None)
        self.assertTrue(skip_token is None)
        self.assertTrue(response['count'] == 2)
        self.assertTrue(response['total_records'] == 2)

        self.assertIsInstance(data, list)
        self.assertTrue(len(data[0]) == 4)  # resourceGroup is auto-added after output
        self.assertIsInstance(data[0], dict)
        self.assertIsInstance(data[0]['id'], string_types)
        self.assertIsInstance(data[0]['tags'], dict)
        self.assertIsInstance(data[0]['properties'], dict)
        self.assertTrue(len(data[0]['properties']) > 0)

        self.assertTrue(len(data[1]) == 4)
        self.assertIsInstance(data[1], dict)
        self.assertIsInstance(data[1]['id'], string_types)
        self.assertIsInstance(data[1]['tags'], dict)
        self.assertIsInstance(data[1]['properties'], dict)

    def test_paged_query(self):
        # Page size was artificially set to 2 rows
        command = 'az graph query -q "project id" --first 3 --skip 2'
        response = self.cmd(command).get_output_in_json()

        self.assertIsInstance(response, dict)
        self.assertTrue(len(response) == 4)  # first element is data, second element is skip_token (or None)

        data = response['data']
        skip_token = response['skip_token']
        self.assertTrue(data is not None)
        self.assertTrue(skip_token is not None)

        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 3)
        self.assertIsInstance(data[0], dict)
        self.assertIsInstance(data[1], dict)
        self.assertIsInstance(data[2], dict)

        self.assertTrue(len(data[0]) == 2)  # resourceGroup is auto-added after output
        self.assertTrue(len(data[1]) == 2)
        self.assertTrue(len(data[2]) == 2)

        self.assertIsInstance(data[0]['id'], string_types)
        self.assertIsInstance(data[1]['id'], string_types)
        self.assertIsInstance(data[2]['id'], string_types)

        self.assertTrue(len(data[0]['id']) > 0)
        self.assertTrue(len(data[1]['id']) > 0)
        self.assertTrue(len(data[2]['id']) > 0)

    def test_management_groups_query(self):
        command = 'az graph query -q "ResourceContainers | where type contains \'management\' | project id, name, type | limit 2" -m 72f988bf-86f1-41af-91ab-2d7cd011db47 AzGovTest5 -a'
        response = self.cmd(command).get_output_in_json()

        self.assertIsInstance(response, dict)
        self.assertTrue(len(response) == 4)  # first element is data, second element is skip_token (or None)

        data = response['data']
        skip_token = response['skip_token']
        self.assertTrue(data is not None)
        self.assertTrue(skip_token is None)

        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], dict)
        self.assertIsInstance(data[0]['id'], string_types)
        self.assertIsInstance(data[0]['name'], string_types)
        self.assertIsInstance(data[0]['type'], string_types)

        self.assertTrue(len(data[1]) == 3)
        self.assertIsInstance(data[1], dict)
        self.assertIsInstance(data[1]['id'], string_types)
        self.assertIsInstance(data[1]['name'], string_types)
        self.assertIsInstance(data[1]['type'], string_types)

        self.assertTrue(len(data[0]['id']) > 0)
        self.assertTrue(len(data[1]['id']) > 0)

        self.assertTrue("management" in data[0]['type'])
        self.assertTrue("management" in data[1]['type'])

    def test_skip_token_query(self):
        command = 'az graph query -q "project id" --skip-token ew0KICAiJGlkIjogIjEiLA0KICAiTWF4Um93cyI6IDMsDQogICJSb3dzVG9Ta2lwIjogNSwNCiAgIkt1c3RvQ2x1c3RlclVybCI6ICJodHRwczovL2FyZy13ZXUtZm91ci1zZi5hcmcuY29yZS53aW5kb3dzLm5ldCINCn0='
        response = self.cmd(command).get_output_in_json()

        self.assertIsInstance(response, dict)
        self.assertTrue(len(response) == 4)  # first element is data, second element is skip_token (or None)

        data = response['data']
        skip_token = response['skip_token']
        self.assertTrue(data is not None)
        self.assertTrue(skip_token is not None)

        self.assertIsInstance(data, list)
        self.assertTrue(len(data) == 3)

        self.assertIsInstance(data[0], dict)
        self.assertIsInstance(data[1], dict)
        self.assertIsInstance(data[2], dict)

        self.assertTrue(len(data[0]) == 2)  # resourceGroup is auto-added after output
        self.assertTrue(len(data[1]) == 2)
        self.assertTrue(len(data[2]) == 2)

        self.assertIsInstance(data[0]['id'], string_types)
        self.assertIsInstance(data[1]['id'], string_types)
        self.assertIsInstance(data[2]['id'], string_types)

        self.assertTrue(len(data[0]['id']) > 0)
        self.assertTrue(len(data[1]['id']) > 0)
        self.assertTrue(len(data[2]['id']) > 0)

    def test_query_error(self):
        command = 'az graph query -q "where where"'

        with self.assertRaises(CLIError) as error:
            self.cmd(command)

        error_response = json.loads(error.exception.args[0])
        print(error_response)
        self.assertIsInstance(error_response, dict)
        self.assertTrue(len(error_response) == 3)

        self.assertIsInstance(error_response['code'], string_types)
        self.assertIsInstance(error_response['message'], string_types)
        self.assertIsInstance(error_response['details'], list)
        self.assertTrue(len(error_response['code']) > 0)
        self.assertTrue(len(error_response['message']) > 0)
        self.assertTrue(len(error_response['details']) == 2)

        self.assertIsInstance(error_response['details'][0], dict)
        self.assertTrue(len(error_response['details'][0]) == 2)

        self.assertIsInstance(error_response['details'][0]['code'], string_types)
        self.assertIsInstance(error_response['details'][0]['message'], string_types)
        self.assertIsInstance(error_response['details'][1]['additionalProperties'], dict)
        self.assertTrue(len(error_response['details'][0]['code']) > 0)
        self.assertTrue(len(error_response['details'][0]['message']) > 0)
        self.assertTrue(len(error_response['details'][1]['additionalProperties']) == 4)

    @ResourceGroupPreparer(location='eastus')
    def test_shared_query_scenario(self, resource_group):
        self.kwargs.update({
            'name': self.create_random_name('clitest', 20),
            'query': "project id, name, type, location, tags",
            'description': "AzureCliTest",
            'rg': resource_group
        })

        self.cmd('graph shared-query create -g {rg} -n {name} -q "{query}" -d {description} --tags a=b', checks=[
            self.check('location', 'global'),
            self.check('name', '{name}'),
            self.check('description', '{description}'),
            self.check('query', '{query}')
        ])

        self.cmd('graph shared-query show -g {rg} -n {name}', checks=[
            self.check('location', 'global'),
            self.check('name', '{name}'),
            self.check('description', '{description}'),
            self.check('query', '{query}')
        ])

        self.cmd('graph shared-query list -g {rg}', checks=[
            self.check('length(@)', 1)
        ])

        self.cmd('graph shared-query delete -g {rg} -n {name}')
        
        with self.assertRaises(SystemExit):
            self.cmd('graph shared-query show -g {rg} -n {name}')