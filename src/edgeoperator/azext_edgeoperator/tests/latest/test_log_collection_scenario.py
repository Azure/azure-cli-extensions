# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re
from unittest.mock import patch
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import RecordingProcessor

from ._recording_processors import ArmEndpointNormalizer, PrivateAuthRequestFilter

# Fixed values keep playback requests identical to the recording. Adjust them before recording live.
FROM_DATE = "2026-11-10T19:09:00Z"
TO_DATE = "2026-11-10T19:10:00Z"
SAVE_TO_PATH = "C:\\Logs\\IndirectCollection"
PASSWORD_PLACEHOLDER = "recording-placeholder"
_JOB_NAME = re.compile(r"/logCollections/([0-9a-fA-F-]{36})$")


def _scrub_operation_status_url(url):
    # RPaaS operation-status URLs carry signed query parameters; keep only api-version.
    if "operationstatuses/" not in url.lower():
        return url
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query) if key.lower() == "api-version"]
    return urlunsplit(parts._replace(query=urlencode(query)))


class OperationStatusUrlScrubber(RecordingProcessor):

    def process_request(self, request):
        request.uri = _scrub_operation_status_url(request.uri)
        return request

    def process_response(self, response):
        for name, values in response.get("headers", {}).items():
            if name.lower() in ("azure-asyncoperation", "location"):
                response["headers"][name] = [_scrub_operation_status_url(value) for value in values]
        return response


class PasswordBodyScrubber(RecordingProcessor):

    def process_request(self, request):
        if request.body and b"userPassword" in request.body:
            body = json.loads(request.body)
            body["userPassword"] = PASSWORD_PLACEHOLDER
            request.body = json.dumps(body).encode("utf-8")
        return request


class LogCollectionScenarioTest(ScenarioTest):

    def __init__(self, method_name, **kwargs):
        recording_processors = kwargs.pop("recording_processors", [])
        replay_processors = kwargs.pop("replay_processors", [])
        super().__init__(
            method_name,
            recording_processors=[
                PrivateAuthRequestFilter(), ArmEndpointNormalizer(),
                OperationStatusUrlScrubber(), PasswordBodyScrubber(),
            ] + recording_processors,
            replay_processors=[ArmEndpointNormalizer(), OperationStatusUrlScrubber()] + replay_processors,
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
        self.kwargs.update({"from": FROM_DATE, "to": TO_DATE, "path": SAVE_TO_PATH})

    def _assert_job(self, job):
        self.assertTrue(_JOB_NAME.search(job["id"]), job["id"])
        self.assertEqual(job["type"].lower(), "microsoft.edgeoperator/logcollections")
        self.assertIn(job["properties"]["provisioningState"], ("Succeeded", "Failed", "Canceled", "Running"))
        return _JOB_NAME.search(job["id"]).group(1)

    def test_log_collection_collect_show_and_list(self):
        job = self.cmd(
            "aldo log-collection collect --from-date {from} --to-date {to} --filter-roles Agents"
        ).get_output_in_json()
        self.kwargs["job"] = self._assert_job(job)

        self.cmd("aldo log-collection wait --job-id {job} --created --interval 5 --timeout 600")
        self.cmd("aldo log-collection show --job-id {job}", checks=[
            self.check("name", "{job}"),
            self.check("properties.provisioningState", "Succeeded"),
        ])
        jobs = self.cmd("aldo log-collection list --from-date {from}").get_output_in_json()
        self.assertIn(self.kwargs["job"], [item["name"] for item in jobs])
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)

    def test_log_collection_collect_indirect(self):
        self.kwargs["password"] = PASSWORD_PLACEHOLDER
        job = self.cmd(
            "aldo log-collection collect-indirect --from-date {from} --to-date {to} "
            "--save-to-path \"{path}\" --username operator --password {password} --filter-roles Agents"
        ).get_output_in_json()
        self._assert_job(job)

        body = json.loads(self.cassette.requests[0].body)
        self.assertEqual(body["userPassword"], PASSWORD_PLACEHOLDER)
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)

    def test_log_collection_show_rejects_unknown_job(self):
        self.cmd("aldo log-collection show --job-id 00000000-0000-0000-0000-000000000001", expect_failure=True)
        if not self.in_recording:
            self.assertTrue(self.cassette.all_played)
