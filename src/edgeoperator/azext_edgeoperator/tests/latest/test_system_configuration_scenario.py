# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from azure.cli.testsdk import JMESPathCheck, ScenarioTest
from azure.cli.testsdk.scenario_tests import RecordingProcessor


_RESOURCE_PATH = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/providers/Microsoft.EdgeOperator/systemConfiguration/default"
)
_REDACTED_PROPERTIES = {
    "dnsForwarderIpAddress": "192.0.2.53",
    "connectionIntent": "Connected",
    "stampId": "11111111-1111-1111-1111-111111111111",
    "deviceResourceId": (
        "/subscriptions/00000000-0000-0000-0000-000000000000"
        "/resourceGroups/rg-test/providers/Microsoft.Edge/disconnectedOperations/test-device"
    ),
    "automaticUpdatePreparationStatus": "NotStarted",
    "telemetryOptOutStatus": "Disabled",
    "externalDomainSuffix": "example.test",
    "imageVersion": "1.0.0",
    "ingressNicPrefixLength": 24,
    "ingressNicIpAddress": "192.0.2.10",
    "ingressNicDefaultGateway": "192.0.2.1",
    "provisioningState": "Succeeded",
}


class SystemConfigurationRecordingProcessor(RecordingProcessor):

    def process_request(self, request):
        url = urlsplit(request.uri)
        if not re.fullmatch(
                r"/subscriptions/[^/]+/providers/Microsoft\.EdgeOperator/systemConfiguration/default",
                url.path):
            return None
        if request.method not in {"GET", "PUT"} or parse_qs(url.query) != {"api-version": ["2026-06-01-preview"]}:
            raise ValueError("Unexpected SystemConfiguration recording request")
        if request.method == "PUT" and json.loads(request.body) != {"properties": {}}:
            raise ValueError("Only an empty-properties PUT is allowed in this negative scenario")
        request.uri = "https://management.azure.com" + _RESOURCE_PATH + "?api-version=2026-06-01-preview"
        request.headers = {
            "Accept": "application/json",
            "CommandName": "aldo system-configuration " + ("create" if request.method == "PUT" else "show"),
            "User-Agent": "AZURECLI",
        }
        if request.method == "PUT":
            request.headers["Content-Type"] = "application/json"
        return request

    def process_response(self, response):
        data = json.loads(response["body"]["string"])
        if response["status"]["code"] == 400:
            self._sanitize_validation_error(data)
        else:
            if set(data) - {"id", "name", "type", "properties"}:
                raise ValueError("Review unexpected SystemConfiguration response fields before recording")
            if data.get("name") != "default" or data.get("type") != "Microsoft.EdgeOperator/systemConfiguration":
                raise ValueError("Unexpected SystemConfiguration resource identity")
            properties = data["properties"]
            if set(properties) - set(_REDACTED_PROPERTIES) - {"externalTimeServers"}:
                raise ValueError("Review unexpected SystemConfiguration properties before recording")
            for name, value in properties.items():
                if value is not None:
                    properties[name] = (
                        ["time.example.test" for server in value]
                        if name == "externalTimeServers" else _REDACTED_PROPERTIES[name]
                    )
            if "id" in data:
                data["id"] = _RESOURCE_PATH
        body = json.dumps(data)
        response["body"]["string"] = (
            body.encode("utf-8") if isinstance(response["body"]["string"], bytes) else body
        )
        response["headers"] = {
            "content-type": ["application/json; charset=utf-8"],
            "content-length": [str(len(body.encode("utf-8")))],
        }
        return response

    @staticmethod
    def _sanitize_validation_error(data):
        if set(data) != {"error"}:
            raise ValueError("Unexpected validation error response")
        error = data["error"]
        details = error.get("details", [])
        if error.get("code") != "InvalidRequest" or len(details) != 4:
            raise ValueError("Expected four missing-field validation errors")
        for detail in details:
            if set(detail) - {"code", "message", "target"}:
                raise ValueError("Review unexpected field validation details before recording")
            if detail.get("code") != "InvalidField" or "required" not in detail.get("message", "").lower():
                raise ValueError("Unexpected field validation error")
        allowed_targets = {
            "Properties.DnsForwarderIpAddress", "Properties.ConnectionIntent",
            "Properties.StampId", "Properties.DeviceResourceId",
        }
        for item in [error] + details:
            if set(item) - {"code", "message", "target", "details"}:
                raise ValueError("Review unexpected validation error fields before recording")
            if "target" in item and item["target"] not in allowed_targets:
                raise ValueError("Review unexpected validation error target before recording")
            if "message" in item:
                item["message"] = "The request contains missing required fields."


class SystemConfigurationScenarioTest(ScenarioTest):

    def __init__(self, method_name, **kwargs):
        recording_processors = kwargs.pop("recording_processors", [])
        replay_processors = kwargs.pop("replay_processors", [])
        super().__init__(
            method_name,
            recording_processors=[SystemConfigurationRecordingProcessor()] + recording_processors,
            replay_processors=[SystemConfigurationRecordingProcessor()] + replay_processors,
            **kwargs
        )

    def setUp(self):
        super().setUp()
        if not self.in_recording:
            token_patch = patch(
                "azure.cli.core._profile.Profile.get_raw_token",
                return_value=(("Bearer", "recording-placeholder", {}), None, None),
            )
            token_patch.start()
            self.addCleanup(token_patch.stop)

    def test_system_configuration_show(self):
        result = self.cmd("aldo system-configuration show").assert_with_checks([
            JMESPathCheck("name", "default"),
            JMESPathCheck("type", "Microsoft.EdgeOperator/systemConfiguration"),
        ]).get_output_in_json()

        self.assertIsInstance(result["properties"], dict)
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)

    def test_system_configuration_create_missing_fields(self):
        self.cmd("aldo system-configuration create", expect_failure=True)

        self.assertEqual(len(self.cassette.requests), 1)
        self.assertEqual(self.cassette.requests[0].method, "PUT")
        response = self.cassette.responses[0]
        self.assertEqual(response["status"]["code"], 400)
        error = json.loads(response["body"]["string"])["error"]
        self.assertEqual(error["code"], "InvalidRequest")
        self.assertEqual(len(error["details"]), 4)
        for detail in error["details"]:
            self.assertEqual(detail["code"], "InvalidField")
            self.assertIn("required", detail["message"].lower())
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)