# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from azure.cli.testsdk import JMESPathCheck, ScenarioTest
from azure.cli.testsdk.scenario_tests import RecordingProcessor

# Fixed host used in the recording. The command derives the ARM endpoint from the
# active cloud, which differs between environments (ALDO locally, AzureCloud in CI),
# so both recording and playback requests are normalized to this host.
NORMALIZED_HOST = "https://management.azure.com"
_READINESS_PATH = re.compile(
    r"^https?://[^/]+(/subscriptions/.+?/providers/Microsoft\.EdgeOperator/systemReadiness/.*)$"
)


class PrivateAuthRequestFilter(RecordingProcessor):
    """Drop ALDO private-cloud token requests/responses when recording live."""

    def process_request(self, request):
        if "autonomous.cloud.private" in request.uri and "systemReadiness" not in request.uri:
            return None
        return request


class ArmEndpointNormalizer(RecordingProcessor):
    """Normalize the ARM host on the systemReadiness request to a fixed value."""

    def process_request(self, request):
        request.uri = _READINESS_PATH.sub(NORMALIZED_HOST + r"\1", request.uri)
        return request


class SystemReadinessScenarioTest(ScenarioTest):

    def __init__(self, method_name, **kwargs):
        recording_processors = kwargs.pop("recording_processors", [])
        replay_processors = kwargs.pop("replay_processors", [])
        super().__init__(
            method_name,
            recording_processors=[
                PrivateAuthRequestFilter(),
                ArmEndpointNormalizer(),
            ] + recording_processors,
            replay_processors=[ArmEndpointNormalizer()] + replay_processors,
            **kwargs
        )

    def test_system_readiness_show(self):
        result = self.cmd("aldo system-readiness show").assert_with_checks([
            JMESPathCheck("name", "default"),
            JMESPathCheck("type", "Microsoft.EdgeOperator/systemReadiness"),
        ]).get_output_in_json()

        self.assertIsInstance(result["properties"]["systemReady"], bool)
        self.assertIsInstance(result["properties"]["readinessStatusDetails"], list)
        self.assertIsInstance(result["properties"]["errorMessages"], list)
