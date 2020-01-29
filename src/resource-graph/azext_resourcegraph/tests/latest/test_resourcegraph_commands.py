# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ScenarioTest
from azure_devtools.scenario_tests.const import MOCKED_SUBSCRIPTION_ID
from knack.util import CLIError
from six import string_types
import json


class ResourceGraphTests(ScenarioTest):
    def test_query(self):
        command = 'az graph query -q "project id, tags, properties | limit 2"'
        query_response = self.cmd(command).get_output_in_json()

        self.assertIsInstance(query_response, list)
        self.assertTrue(len(query_response) == 2)

        self.assertTrue(len(query_response[0]) == 4)  # resourceGroup is auto-added after output
        self.assertIsInstance(query_response[0], dict)
        self.assertIsInstance(query_response[0]['id'], string_types)
        self.assertIsInstance(query_response[0]['tags'], dict)
        self.assertIsInstance(query_response[0]['properties'], dict)
        self.assertTrue(len(query_response[0]['properties']) > 3)

        self.assertTrue(len(query_response[1]) == 4)
        self.assertIsInstance(query_response[1], dict)
        self.assertIsInstance(query_response[1]['id'], string_types)
        self.assertIsInstance(query_response[1]['tags'], dict)
        self.assertIsInstance(query_response[1]['properties'], dict)

    def test_paged_query(self):
        # Page size was artificially set to 2 rows
        command = 'az graph query -q "project id" --first 3 --skip 2'
        query_response = self.cmd(command).get_output_in_json()

        self.assertIsInstance(query_response, list)
        self.assertTrue(len(query_response) == 3)

        self.assertIsInstance(query_response[0], dict)
        self.assertIsInstance(query_response[1], dict)
        self.assertIsInstance(query_response[2], dict)

        self.assertTrue(len(query_response[0]) == 2)  # resourceGroup is auto-added after output
        self.assertTrue(len(query_response[1]) == 2)
        self.assertTrue(len(query_response[2]) == 2)

        self.assertIsInstance(query_response[0]['id'], string_types)
        self.assertIsInstance(query_response[1]['id'], string_types)
        self.assertIsInstance(query_response[2]['id'], string_types)

        self.assertTrue(len(query_response[0]['id']) > 0)
        self.assertTrue(len(query_response[1]['id']) > 0)
        self.assertTrue(len(query_response[2]['id']) > 0)

    def test_query_error(self):
        command = 'az graph query -q "where where"'

        with self.assertRaises(CLIError) as error:
            self.cmd(command)

        error_response = json.loads(error.exception.args[0])
        self.assertIsInstance(error_response, dict)
        self.assertTrue(len(error_response), 1)

        self.assertIsInstance(error_response['error'], dict)
        self.assertTrue(len(error_response['error']) == 3)

        self.assertIsInstance(error_response['error']['code'], string_types)
        self.assertIsInstance(error_response['error']['message'], string_types)
        self.assertIsInstance(error_response['error']['details'], list)
        self.assertTrue(len(error_response['error']['code']) > 0)
        self.assertTrue(len(error_response['error']['message']) > 0)
        self.assertTrue(len(error_response['error']['details']) == 2)

        self.assertIsInstance(error_response['error']['details'][0], dict)
        self.assertTrue(len(error_response['error']['details'][0]) == 2)

        self.assertIsInstance(error_response['error']['details'][0]['code'], string_types)
        self.assertIsInstance(error_response['error']['details'][0]['message'], string_types)
        self.assertIsInstance(error_response['error']['details'][1]['additionalProperties'], dict)
        self.assertTrue(len(error_response['error']['details'][0]['code']) > 0)
        self.assertTrue(len(error_response['error']['details'][0]['message']) > 0)
        self.assertTrue(len(error_response['error']['details'][1]['additionalProperties']) == 4)
