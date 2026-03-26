# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import json

from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.utilities import is_text_payload


class ApiKeyServiceAccountTokenReplacer(RecordingProcessor):
    """Replace API key or Service Account Token with a hard-coded value"""

    replacement = '"key":"fakeApiKeyOrServiceAccountToken"'
    pattern = r'"key":".*"'

    def process_response(self, response):
        if is_text_payload(response) and response["body"]["string"]:
            response["body"]["string"] = self._replace_api_key_or_service_account_token(response["body"]["string"])
        return response

    def _replace_api_key_or_service_account_token(self, value):
        value_lower = value.lower()
        if 'key' in value_lower:
            value = re.sub(r'"key":".*"',
                           r'"key":"{}"'.format('fakeApiKeyOrServiceAccountToken'),
                           value, flags=re.IGNORECASE)
        return value
