# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.testsdk.scenario_tests import RecordingProcessor


class TokenReplacer(RecordingProcessor):

    def process_response(self, response):
        import json

        body = response['body']['string']

        json_body = json.loads(body)
        if json_body and 'properties' in json_body:
            if json_body['properties'] and 'registrationInfo' in json_body['properties']:
                if json_body['properties']['registrationInfo'] and 'token' in json_body['properties']['registrationInfo']:
                    json_body['properties']['registrationInfo']['token'] = None
        if json_body and 'token' in json_body:
            json_body['token'] = None
        response['body']['string'] = json.dumps(json_body)

        return response
