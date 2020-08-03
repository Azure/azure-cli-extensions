# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from http import HTTPStatus

from azext_ai_did_you_mean_this.custom import call_aladdin_service, get_recommendations_from_http_response
from azext_ai_did_you_mean_this._cmd_table import CommandTable
from azext_ai_did_you_mean_this.tests.latest.aladdin_scenario_test_base import AladdinScenarioTest
from azext_ai_did_you_mean_this.tests.latest.mock.aladdin_service import mock_aladdin_service_call
from azext_ai_did_you_mean_this.tests.latest.data.scenarios import TEST_SCENARIOS


class AiDidYouMeanThisScenarioTest(AladdinScenarioTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_scenarios = TEST_SCENARIOS

    def test_ai_did_you_mean_this_aladdin_service_call(self):
        for scenario in self.test_scenarios:
            with mock_aladdin_service_call(scenario):
                response = call_aladdin_service(scenario.command, scenario.parameters, self.cli_version)

            self.assertEqual(HTTPStatus.OK, response.status_code)
            expected_suggestions = scenario.suggestions
            mock_command_table = {suggestion.command for suggestion in expected_suggestions}
            recommendations = get_recommendations_from_http_response(response, mock_command_table)
            self.assertEquals(recommendations, expected_suggestions)

    def test_ai_did_you_mean_this_recommendations_for_user_fault_commands(self):
        for scenario in self.test_scenarios:
            cli_command = scenario.cli_command
            command = scenario.command

            with mock_aladdin_service_call(scenario):
                self.cmd(cli_command, expect_user_fault_failure=scenario.expected_user_fault_type)

            self.assert_cmd_table_not_empty()
            cmd_tbl = CommandTable.CMD_TBL

            _version, _command, _parameters, _extension = self.recommender_postional_arguments
            partial_command_match = command and any(cmd.startswith(command) for cmd in cmd_tbl.keys())
            self.assertEqual(_version, self.cli_version)
            self.assertEqual(_command, command if partial_command_match else '')
            self.assertEqual(bool(_extension), bool(scenario.extension))

            if scenario.suggestions:
                self.assert_recommendations_were_shown()
            elif partial_command_match and not scenario.extension:
                self.assert_az_find_was_suggested()
            else:
                self.assert_nothing_is_shown()
