# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import mock
import requests
import json
from collections import defaultdict

from azext_ai_did_you_mean_this import check_if_up_to_date_in_background
from azext_ai_did_you_mean_this.custom import call_aladdin_service
from azext_ai_did_you_mean_this.failure_recovery_recommendation import FailureRecoveryRecommendation
from azext_ai_did_you_mean_this._check_for_updates import async_is_cli_up_to_date, is_cli_up_to_date, reset_cli_update_status, CliStatus
from azext_ai_did_you_mean_this.tests.latest._mock import MOCK_PIP_SEARCH_OUTPUT, MOCK_UUID
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from azure.cli.core import __version__ as core_version

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


def get_mock_recommendations():
    recommendation_data = [
        {
            "SuccessCommand": "account get-access-token",
            "SuccessCommand_Parameters": "--output,--resource,--subscription",
            "SuccessCommand_ArgumentPlaceholders": "json,{resource},00000000-0000-0000-0000-000000000000",
        },
        {
            "SuccessCommand": "account list",
            "SuccessCommand_Parameters": "",
            "SuccessCommand_ArgumentPlaceholders": "",
        },
        {
            "SuccessCommand": "ad signed-in-user show",
            "SuccessCommand_Parameters": "--output",
            "SuccessCommand_ArgumentPlaceholders": "json",
        }
    ]

    recommendations = [FailureRecoveryRecommendation(data) for data in recommendation_data]
    return recommendations


def get_mock_query():
    return 'account', ''


def get_mock_context():
    return MOCK_UUID, MOCK_UUID, '2.3.1'


class AiDidYouMeanThisScenarioTest(ScenarioTest):
    def test_ai_did_you_mean_this_aladdin_service_call(self):
        session_id, subscription_id, version = get_mock_context()

        with mock.patch('azure.cli.core.telemetry._session._get_base_properties', return_value={'Reserved.SessionId': session_id}):
            with mock.patch('azure.cli.core.telemetry._get_azure_subscription_id', return_value=subscription_id):
                command, parameters = get_mock_query()
                response = call_aladdin_service(command, parameters, version)
                self.assertEqual(200, response.status_code)

                recommendations = list(FailureRecoveryRecommendation(suggestion) for suggestion in json.loads(response.content))
                expected_recommendations = get_mock_recommendations()

                for expected_recommendation, recommendation in zip(recommendations, expected_recommendations):
                    self.assertEqual(expected_recommendation.command, recommendation.command)
                    self.assertEqual(expected_recommendation.parameters, recommendation.parameters)
                    self.assertEqual(expected_recommendation.placeholders, recommendation.placeholders)

    def test_ai_did_you_mean_this_cli_is_up_to_date(self):
        cmd_output = MOCK_PIP_SEARCH_OUTPUT.format(ver=core_version)
        with mock.patch('subprocess.check_output', return_value=cmd_output):
            check_if_up_to_date_in_background(use_cache=False)
            cli_status = async_is_cli_up_to_date(wait=True, use_cache=False)
            self.assertEqual(cli_status, CliStatus.UP_TO_DATE)
            self.assertTrue(getattr(async_is_cli_up_to_date, 'cached'))
            self.assertEqual(getattr(async_is_cli_up_to_date, 'cached_result'), cli_status)

    def test_ai_did_you_mean_this_cli_is_outdated(self):
        latest_version = '3.0.0'
        cmd_output = MOCK_PIP_SEARCH_OUTPUT.format(ver=latest_version)
        with mock.patch('subprocess.check_output', return_value=cmd_output):
            cli_status = is_cli_up_to_date(use_cache=False)
            self.assertEqual(cli_status, CliStatus.OUTDATED)

    def tearDown(self):
        # reset async indicators for whether the CLI is up to date.
        reset_cli_update_status()
