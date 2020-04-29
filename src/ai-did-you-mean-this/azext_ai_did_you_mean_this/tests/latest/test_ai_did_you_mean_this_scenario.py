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

from azext_ai_did_you_mean_this.custom import (
    call_aladdin_service,
    get_recommendations_from_http_response,
    normalize_and_sort_parameters,
    recommend_recovery_options
)
from azext_ai_did_you_mean_this.failure_recovery_recommendation import FailureRecoveryRecommendation
from azext_ai_did_you_mean_this._check_for_updates import (
    is_cli_up_to_date,
    CliStatus,
)
from azext_ai_did_you_mean_this._cmd_table import CommandTable
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
    return MOCK_UUID, MOCK_UUID


# based on https://stackoverflow.com/questions/57299968/python-how-to-reuse-a-mock-to-avoid-writing-mock-patch-multiple-times
class PatchMixin():
    def patch(self, target, **kwargs):
        patch = mock.patch(target, **kwargs)
        patch.start()
        self.addCleanup(patch.stop)


class AiDidYouMeanThisScenarioTest(ScenarioTest, PatchMixin):
    def setUp(self):
        super().setUp()
        session_id, subscription_id = get_mock_context()
        self.patch('azure.cli.core.telemetry._session._get_base_properties', return_value={'Reserved.SessionId': session_id})
        self.patch('azure.cli.core.telemetry._get_azure_subscription_id', return_value=subscription_id)

    def test_ai_did_you_mean_this_aladdin_service_call(self):
        command, parameters = get_mock_query()
        version = '2.3.1'
        response = call_aladdin_service(command, parameters, version)
        self.assertEqual(200, response.status_code)

        recommendations = get_recommendations_from_http_response(response)
        expected_recommendations = get_mock_recommendations()
        self.assertEquals(recommendations, expected_recommendations)

    def test_ai_did_you_mean_this_aladdin_service_call_invalid_version(self):
        command, parameters = get_mock_query()
        invalid_version = '3.5.0'
        response = call_aladdin_service(command, parameters, invalid_version)
        self.assertEqual(200, response.status_code)

    def test_ai_did_you_mean_this_cli_is_up_to_date(self):
        cmd_output = MOCK_PIP_SEARCH_OUTPUT.format(ver=core_version)
        with mock.patch('subprocess.check_output', return_value=cmd_output):
            cli_status = is_cli_up_to_date(use_cache=False)
            self.assertEqual(cli_status, CliStatus.UP_TO_DATE)
            self.assertTrue(getattr(is_cli_up_to_date, 'cached'))
            self.assertEqual(getattr(is_cli_up_to_date, 'cached_result'), cli_status)

    def test_ai_did_you_mean_this_cli_is_outdated(self):
        latest_version = '3.0.0'
        cmd_output = MOCK_PIP_SEARCH_OUTPUT.format(ver=latest_version)
        with mock.patch('subprocess.check_output', return_value=cmd_output):
            cli_status = is_cli_up_to_date(use_cache=False)
            self.assertEqual(cli_status, CliStatus.OUTDATED)

    def test_ai_did_you_mean_this_arguments_required_user_fault(self):
        recommendation_buffer = []
        orig_func = recommend_recovery_options

        def hook_recommend_recovery_options(*args, **kwargs):
            recommendation_buffer.extend(orig_func(*args, **kwargs))
            return recommendation_buffer

        with mock.patch('azext_ai_did_you_mean_this.custom.recommend_recovery_options', wraps=hook_recommend_recovery_options):
            with self.assertRaises(SystemExit):
                self.cmd('account')

        self.assertIsNotNone(CommandTable.CMD_TBL)
        self.assertGreater(len(recommendation_buffer), 0)
