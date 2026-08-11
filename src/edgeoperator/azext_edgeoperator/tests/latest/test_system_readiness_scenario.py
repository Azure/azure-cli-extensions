# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import JMESPathCheck, ScenarioTest


class SystemReadinessScenarioTest(ScenarioTest):

    def test_system_readiness_show(self):
        result = self.cmd("aldo system-readiness show").assert_with_checks([
            JMESPathCheck("name", "default"),
            JMESPathCheck("type", "Microsoft.EdgeOperator/systemReadiness"),
        ]).get_output_in_json()

        self.assertIsInstance(result["properties"]["systemReady"], bool)
        self.assertIsInstance(result["properties"]["readinessStatusDetails"], list)
        self.assertIsInstance(result["properties"]["errorMessages"], list)
