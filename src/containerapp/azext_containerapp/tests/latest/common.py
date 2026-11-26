# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
from azure.cli.testsdk import (ScenarioTest)
from azure.cli.testsdk.scenario_tests import RecordingProcessor

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
STAGE_LOCATION = "northcentralusstage"
TEST_LOCATION = os.getenv("CLITestLocation") if os.getenv("CLITestLocation") else STAGE_LOCATION


class AuthTokenReplacer(RecordingProcessor):
    def process_response(self, response):
        body = response.get("body", {}).get("string")
        try:
            payload = json.loads(body)
        except (TypeError, ValueError):
            return response
        properties = payload.get("properties") if isinstance(payload, dict) else None
        if isinstance(properties, dict) and "token" in properties:
            properties["token"] = "fake-token"
            response["body"]["string"] = json.dumps(payload, separators=(",", ":"))
        return response


class RegistryPasswordReplacer(RecordingProcessor):
    def __init__(self):
        self._passwords = {}

    def _replace(self, body):
        if isinstance(body, bytes):
            for value, replacement in self._passwords.items():
                body = body.replace(value.encode(), replacement.encode())
        elif isinstance(body, str):
            for value, replacement in self._passwords.items():
                body = body.replace(value, replacement)
        return body

    def process_request(self, request):
        request.body = self._replace(request.body)
        return request

    def process_response(self, response):
        body = response.get("body", {}).get("string")
        try:
            payload = json.loads(body)
        except (TypeError, ValueError):
            payload = None
        if isinstance(payload, dict) and isinstance(payload.get("passwords"), list):
            for password in payload["passwords"]:
                if isinstance(password, dict) and isinstance(password.get("value"), str) and password["value"]:
                    value = password["value"]
                    if value not in self._passwords:
                        self._passwords[value] = "fake-registry-password-{}".format(len(self._passwords) + 1)
        if body is not None:
            response["body"]["string"] = self._replace(body)
        return response


def write_test_file(filename, content):
    test_file = open(filename, "w", encoding='utf-8')
    _ = test_file.write(content)
    test_file.close()


def clean_up_test_file(filename):
    if os.path.exists(filename):
        os.remove(filename)


class ContainerappComposePreviewScenarioTest(ScenarioTest):
    pass
