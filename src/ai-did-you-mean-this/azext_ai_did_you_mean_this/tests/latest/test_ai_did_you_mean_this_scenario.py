# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import mock
import requests
import json
from http import HTTPStatus
from collections import defaultdict

from azext_ai_did_you_mean_this.custom import call_aladdin_service, get_recommendations_from_http_response
from azext_ai_did_you_mean_this.tests.latest._mock import (
    get_mock_recommendation_model_path,
    mock_aladdin_service_call,
    MockRecommendationModel
)
from azext_ai_did_you_mean_this.tests.latest.aladdin_scenario_test_base import AladdinScenarioTest
from azext_ai_did_you_mean_this.tests.latest._commands import AzCommandType

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AiDidYouMeanThisScenarioTest(AladdinScenarioTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        MockRecommendationModel.load(get_mock_recommendation_model_path(TEST_DIR))

    def setUp(self):
        super().setUp()

        self.command, self.parameters = (AzCommandType.ACCOUNT.command, '')
        self.invalid_cli_version = '0.0.0'

    def test_ai_did_you_mean_this_aladdin_service_call(self):
        with mock_aladdin_service_call(self.command):
            response = call_aladdin_service(self.command, self.parameters, self.cli_version)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        recommendations = get_recommendations_from_http_response(response)
        expected_recommendations = MockRecommendationModel.get_recommendations(self.command)
        self.assertEquals(recommendations, expected_recommendations)

    def test_ai_did_you_mean_this_arguments_required_user_fault(self):
        with mock_aladdin_service_call(self.command):
            self.cmd(self.command, expect_user_fault_failure=True)
