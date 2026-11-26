# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from types import SimpleNamespace

from .common import AuthTokenReplacer, RegistryPasswordReplacer


def test_job_auth_token_replacer():
    response = {"body": {"string": json.dumps({"properties": {"token": "real-token", "expires": "later"}})}}

    result = AuthTokenReplacer().process_response(response)

    assert json.loads(result["body"]["string"]) == {"properties": {"token": "fake-token", "expires": "later"}}


def test_job_auth_token_replacer_preserves_non_json():
    response = {"body": {"string": "not json"}}

    assert AuthTokenReplacer().process_response(response) == response


def test_registry_password_replacer_redacts_later_requests_and_responses():
    processor = RegistryPasswordReplacer()
    response = {"body": {"string": json.dumps({"username": "registry", "passwords": [
        {"name": "password", "value": "real-password"},
        {"name": "password2", "value": "another-password"},
    ]})}}
    result = processor.process_response(response)
    assert "real-password" not in result["body"]["string"]
    assert "another-password" not in result["body"]["string"]
    request = SimpleNamespace(body=b'{"password": "real-password"}')
    assert processor.process_request(request).body == b'{"password": "fake-registry-password-1"}'
    later = {"body": {"string": '{"value": "real-password"}'}}
    assert processor.process_response(later)["body"]["string"] == '{"value": "fake-registry-password-1"}'
