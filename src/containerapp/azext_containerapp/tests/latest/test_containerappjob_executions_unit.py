# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from .test_containerappjob_executions import JobAuthTokenReplacer


def test_job_auth_token_replacer():
    response = {"body": {"string": json.dumps({"properties": {"token": "real-token", "expires": "later"}})}}

    result = JobAuthTokenReplacer().process_response(response)

    assert json.loads(result["body"]["string"]) == {"properties": {"token": "fake-token", "expires": "later"}}


def test_job_auth_token_replacer_preserves_non_json():
    response = {"body": {"string": "not json"}}

    assert JobAuthTokenReplacer().process_response(response) == response
