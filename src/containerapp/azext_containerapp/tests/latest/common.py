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


def write_test_file(filename, content):
    test_file = open(filename, "w", encoding='utf-8')
    _ = test_file.write(content)
    test_file.close()


def clean_up_test_file(filename):
    if os.path.exists(filename):
        os.remove(filename)


class ContainerappComposePreviewScenarioTest(ScenarioTest):
    pass
