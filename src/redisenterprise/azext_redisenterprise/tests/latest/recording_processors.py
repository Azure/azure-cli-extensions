# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azure.cli.testsdk.scenario_tests import RecordingProcessor
from azure.cli.testsdk.scenario_tests.utilities import is_json_payload


class RedisEnterpriseKeyReplacer(RecordingProcessor):
    """Keep access keys out of list-keys and regenerate-key recordings."""

    def process_response(self, response):
        if not is_json_payload(response) or not response['body']['string']:
            return response
        body = json.loads(response['body']['string'])
        if not isinstance(body, dict):
            return response
        replacements = {'primaryKey': 'fake_primary_key', 'secondaryKey': 'fake_secondary_key'}
        changed = False
        for key, replacement in replacements.items():
            if isinstance(body.get(key), str) and body[key]:
                body[key] = replacement
                changed = True
        if changed:
            response['body']['string'] = json.dumps(body)
        return response
