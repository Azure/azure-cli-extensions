# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import unittest.mock as mock
import json
from http import HTTPStatus
from collections import defaultdict

import requests

from azext_ai_did_you_mean_this.custom import call_aladdin_service, get_recommendations_from_http_response
from azext_ai_did_you_mean_this._cmd_table import CommandTable
from azext_ai_did_you_mean_this.tests.latest._mock import (
    get_mock_recommendation_model_path,
    mock_aladdin_service_call,
    MockRecommendationModel,
    UserFaultType
)
from azext_ai_did_you_mean_this.tests.latest.aladdin_scenario_test_base import AladdinScenarioTest
from azext_ai_did_you_mean_this.tests.latest._commands import AzCommandType

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AiDidYouMeanThisScenarioTest(AladdinScenarioTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        MockRecommendationModel.load(get_mock_recommendation_model_path(TEST_DIR))
        cls.test_cases = MockRecommendationModel.get_test_cases()

    def setUp(self):
        super().setUp()

    def test_ai_did_you_mean_this_aladdin_service_call(self):
        for command, entity in self.test_cases:
            tokens = entity.arguments.split()
            parameters = [token for token in tokens if token.startswith('-')]

            with mock_aladdin_service_call(command):
                response = call_aladdin_service(command, parameters, self.cli_version)

            self.assertEqual(HTTPStatus.OK, response.status_code)
            recommendations = get_recommendations_from_http_response(response)
            expected_recommendations = MockRecommendationModel.get_recommendations(command)
            self.assertEquals(recommendations, expected_recommendations)

    def test_ai_did_you_mean_this_recommendations_for_user_fault_commands(self):
        for command, entity in self.test_cases:
            args = entity.arguments
            command_with_args = command if not args else f'{command} {args}'

            with mock_aladdin_service_call(command):
                self.cmd(command_with_args, expect_user_fault_failure=entity.user_fault_type)

            self.assert_cmd_table_not_empty()
            cmd_tbl = CommandTable.CMD_TBL

            _version, _command, _parameters, _extension = self.recommender_postional_arguments
            partial_command_match = command and any(cmd.startswith(command) for cmd in cmd_tbl.keys())
            self.assertEqual(_version, self.cli_version)
            self.assertEqual(_command, command if partial_command_match else '')
            self.assertEqual(bool(_extension), bool(entity.extension))

            if entity.recommendations:
                self.assert_recommendations_were_shown()
            elif partial_command_match and not entity.extension:
                self.assert_az_find_was_suggested()
            else:
                self.assert_nothing_is_shown()
