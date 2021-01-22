# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json
import unittest
import mock
import requests

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azext_ai_examples.custom import (call_aladdin_service, ping_aladdin_service,
                                      clean_from_http_answer, get_generated_examples)


def create_valid_http_response():
    mock_response = requests.Response()
    mock_response.status_code = 200
    data = [{
        'title': 'RunTestAutomation',
        'snippet': 'az find',
        'source': 'crawler-example'
    }, {
        'title': 'az test',
        'snippet': 'The title',
        'source': 'crawler-crafted'
    }]
    mock_response._content = json.dumps(data)
    return mock_response


def create_empty_http_response():
    mock_response = requests.Response()
    mock_response.status_code = 200
    data = []
    mock_response._content = json.dumps(data)
    return mock_response


def create_failed_http_response():
    mock_response = requests.Response()
    mock_response.status_code = 500
    data = []
    mock_response._content = json.dumps(data)
    return mock_response


class AiExamplesCustomCommandTest(unittest.TestCase):

    # Test the Aladdin check connection command
    def test_ai_examples_ping_aladdin_service_success(self):
        mock_response = create_empty_http_response()

        with mock.patch('requests.get', return_value=(mock_response)):
            response = ping_aladdin_service()

            self.assertEqual(200, response.status_code)

    def test_ai_examples_ping_aladdin_service_failed(self):
        mock_response = create_failed_http_response()

        with mock.patch('requests.get', return_value=(mock_response)):
            response = ping_aladdin_service()

            self.assertEqual(500, response.status_code)

    # Test the Aladdin examples
    def test_ai_examples_call_aladdin_service(self):
        mock_response = create_valid_http_response()

        with mock.patch('requests.get', return_value=(mock_response)):
            response = call_aladdin_service('RunTestAutomation')
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(json.loads(response.content)))

    def test_ai_examples_example_clean_from_http_answer(self):
        cleaned_responses = []
        mock_response = create_valid_http_response()

        for response in json.loads(mock_response.content):
            cleaned_responses.append(clean_from_http_answer(response))

        self.assertEqual('RunTestAutomation', cleaned_responses[0].short_summary)
        self.assertEqual('az find\n', cleaned_responses[0].command)
        self.assertEqual('The title', cleaned_responses[1].short_summary)
        self.assertEqual('az test\n', cleaned_responses[1].command)

    def test_ai_examples_get_generated_examples_full(self):
        examples = []
        mock_response = create_valid_http_response()

        with mock.patch('requests.get', return_value=(mock_response)):
            examples = get_generated_examples('RunTestAutomation')

            self.assertEqual('RunTestAutomation', examples[0].short_summary)
            self.assertEqual('az find\n', examples[0].command)
            self.assertEqual('The title', examples[1].short_summary)
            self.assertEqual('az test\n', examples[1].command)

    def test_ai_examples_get_generated_examples_empty(self):
        examples = []
        mock_response = create_empty_http_response()

        with mock.patch('requests.get', return_value=(mock_response)):
            examples = get_generated_examples('RunTestAutomation')

            self.assertEqual(0, len(examples))
