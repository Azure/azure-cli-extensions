# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from copy import deepcopy
import json
from pathlib import Path

import pytest
from vcr import VCR
from vcr.request import Request
import yaml

from .recording_processors import (
    EdgeActionRecordingProcessor, PRIVATE_HEADERS, REDACTED, SENSITIVE_QUERY, sanitize_body,
    sanitize_json, sanitize_recording, sanitize_text,
)


URL = "https://management.azure.com/operationResults/one?api-version=2026-10-01&t=opaque-time&c=opaque-token"
PROCESSOR = EdgeActionRecordingProcessor()


@pytest.mark.parametrize("key", ["t", "c", "s", "h", "sig", "token", "access_token", "SIG"])
def test_signed_query_values_are_redacted_without_changing_url_structure(key):
    original = f"https://management.azure.com/status/one?api-version=2026-10-01&{key}=private%2Bvalue&retry=1"
    sanitized = sanitize_text(original)
    assert "private" not in sanitized
    assert sanitized.startswith(f"https://management.azure.com/status/one?api-version=2026-10-01&{key}=Sanitized_")
    assert sanitized.endswith("&retry=1")
    assert sanitize_text(sanitized) == sanitized


def test_distinct_polling_requests_do_not_collapse():
    first = sanitize_text(URL)
    second = sanitize_text(URL.replace("opaque-token", "different-token"))
    assert first != second
    assert sanitize_text(URL.replace("one", "two")) != first


@pytest.mark.parametrize("as_bytes", [False, True])
def test_json_sanitization_preserves_schema_and_code_content(as_bytes):
    body = {
        "systemData": {"createdBy": "user@example.test", "lastModifiedBy": "identity-id",
                       "createdByType": "User", "lastModifiedAt": "2026-10-01T00:00:00Z"},
        "properties": {"isDefaultVersion": "False", "count": 3, "enabled": True, "optional": None,
                       "content": "const url = 'https://example.test/?sig=sample';"},
        "nextLink": URL, "tags": {"purpose": "test"}, "access_token": "private-token",
    }
    encoded = json.dumps(body).encode("utf-8") if as_bytes else json.dumps(body)
    sanitized = sanitize_body(encoded)
    assert isinstance(sanitized, bytes) == as_bytes
    parsed = json.loads(sanitized)
    assert parsed["properties"] == body["properties"]
    assert parsed["tags"] == body["tags"]
    assert parsed["systemData"]["createdBy"] == "Sanitized"
    assert parsed["systemData"]["lastModifiedBy"] == "Sanitized"
    assert parsed["systemData"]["createdByType"] == "User"
    assert parsed["systemData"]["lastModifiedAt"] == body["systemData"]["lastModifiedAt"]
    assert parsed["access_token"] == "Sanitized"
    assert parsed["nextLink"] == sanitize_text(URL)
    assert sanitize_body(sanitized) == sanitized


@pytest.mark.parametrize("body", [None, "", b""])
def test_empty_body_preserves_type_and_no_content_semantics(body):
    assert sanitize_body(body) is body


def test_request_headers_body_and_uri_are_normalized():
    request = Request("POST", URL, json.dumps({"nextLink": URL}), {
        "Authorization": ["Bearer fake-token"], "Cookie": ["fake-cookie"],
        "Content-Type": ["application/json"], "Content-Length": ["999"],
        "x-ms-client-request-id": ["fake-request-id"],
    })
    sanitized = PROCESSOR.process_request(request)
    assert sanitized.uri == sanitize_text(URL)
    assert not PRIVATE_HEADERS.intersection(key.lower() for key in sanitized.headers)
    assert sanitized.headers["Content-Type"] == "application/json"
    assert int(sanitized.headers["Content-Length"]) == len(sanitized.body)
    assert json.loads(sanitized.body)["nextLink"] == sanitized.uri


def response():
    return {"status": {"code": 202}, "body": {"string": b""}, "headers": {
        "Azure-AsyncOperation": [URL.replace("operationResults", "operationStatuses")],
        "Location": [URL], "Retry-After": ["1"], "Content-Length": ["0"],
        "Set-Cookie": ["fake-cookie"], "X-MSEdge-Ref": ["fake-trace"],
        "x-ms-correlation-request-id": ["fake-correlation"],
    }}


def test_response_preserves_polling_headers_and_status():
    original = response()
    sanitized = PROCESSOR.process_response(deepcopy(original))
    assert sanitized["status"] == original["status"]
    assert sanitized["body"] == original["body"]
    assert not PRIVATE_HEADERS.intersection(key.lower() for key in sanitized["headers"])
    assert sanitized["headers"]["Location"] == [sanitize_text(URL)]
    assert sanitized["headers"]["Azure-AsyncOperation"] == [
        sanitize_text(URL.replace("operationResults", "operationStatuses"))]
    assert sanitized["headers"]["Retry-After"] == ["1"]
    assert PROCESSOR.process_response(deepcopy(sanitized)) == sanitized


def test_vcr_matches_original_and_sanitized_polling_requests_offline(tmp_path):
    recorder = VCR(before_record_request=PROCESSOR.process_request,
                   before_record_response=PROCESSOR.process_response,
                   match_on=["method", "scheme", "host", "port", "path", "query"])
    path = str(tmp_path / "sanitized.yaml")
    original = Request("GET", URL, None, {})
    with recorder.use_cassette(path, record_mode="all") as cassette:
        cassette.append(original, response())
    assert original.uri == URL
    assert "opaque-token" not in Path(path).read_text(encoding="utf-8")
    with recorder.use_cassette(path, record_mode="none") as cassette:
        for url in (URL, sanitize_text(URL)):
            actual = Request("GET", url, None, {})
            assert cassette.can_play_response_for(actual)
            result = cassette.play_response(actual)
            assert result["headers"]["Location"] == [sanitize_text(URL)]
            cassette.rewind()
        assert not cassette.can_play_response_for(Request("GET", URL.replace("opaque-token", "other"), None, {}))


def test_bulk_sanitization_preserves_recording_evidence(tmp_path):
    path = tmp_path / "recording.yaml"
    original = {"version": 1, "interactions": [{
        "request": {"uri": URL.replace("2026-10-01", "2025-09-01-preview"),
                    "method": "GET", "body": None, "headers": {}},
        "response": response(),
    }]}
    path.write_text(yaml.safe_dump(original), encoding="utf-8")
    sanitize_recording(path)
    sanitized = yaml.safe_load(path.read_text(encoding="utf-8"))
    first = path.read_bytes()
    sanitize_recording(path)
    assert path.read_bytes() == first
    assert sanitized["version"] == original["version"]
    assert len(sanitized["interactions"]) == 1
    assert "api-version=2025-09-01-preview" in sanitized["interactions"][0]["request"]["uri"]
    assert sanitized["interactions"][0]["response"]["status"]["code"] == 202


def test_scenario_keeps_defaults_and_registers_both_hooks():
    from .test_edge_action import EdgeActionScenarioTest
    scenario = EdgeActionScenarioTest("test_edge_action_crud")
    assert "body" in scenario.vcr.match_on
    for processors in (scenario.recording_processors, scenario.replay_processors):
        assert any(isinstance(item, EdgeActionRecordingProcessor) for item in processors)
        assert len(processors) > 1


def test_polling_delay_patch_is_playback_only_and_restored():
    from azure.cli.core.aaz._poller import AAZBasePolling
    from .test_edge_action import EdgeActionScenarioTest, _patch_playback_polling

    scenario = EdgeActionScenarioTest("test_edge_action_crud")
    assert _patch_playback_polling in scenario.replay_patches
    assert _patch_playback_polling not in scenario.recording_patches
    assert len(scenario.replay_patches) > 1
    original_delay = AAZBasePolling._delay
    try:
        _patch_playback_polling(scenario)
        assert AAZBasePolling._delay() is None
        AAZBasePolling._delay.assert_called_once_with()
    finally:
        scenario.doCleanups()
    assert AAZBasePolling._delay is original_delay


def test_scenario_playback_matches_request_bodies(tmp_path):
    from .test_edge_action import EdgeActionScenarioTest
    scenario = EdgeActionScenarioTest("test_edge_action_crud")
    path = str(tmp_path / "body-matching.yaml")
    headers = {"Content-Type": "application/json"}
    with scenario.vcr.use_cassette(path, record_mode="all") as cassette:
        cassette.append(Request("PUT", URL, '{"tags":{"purpose":"updated"}}', headers), response())
    with scenario.vcr.use_cassette(path, record_mode="none") as cassette:
        assert cassette.can_play_response_for(
            Request("PUT", URL, '{ "tags": { "purpose": "updated" } }', headers))
        for body in ('{"tags":{}}', '{"tags":{"purpose":false}}', '{"tags":{"purpose":"old"}}'):
            assert not cassette.can_play_response_for(Request("PUT", URL, body, headers))


@pytest.mark.parametrize("deployment_type,filename", [
    ("file", "sample_edge_action.js"), ("zip", "sample_edge_action.zip"),
])
def test_deployment_fixture_bytes_match_recording(deployment_type, filename):
    directory = Path(__file__).parent
    path = directory / "recordings" / f"test_edge_action_version_deploy_with_{deployment_type}.yaml"
    recording = yaml.safe_load(path.read_text(encoding="utf-8"))
    requests = [item["request"] for item in recording["interactions"]
                if "/deployVersionCode?" in item["request"]["uri"]]
    assert len(requests) == 1
    recorded = base64.b64decode(json.loads(requests[0]["body"])["content"], validate=True)
    assert (directory / "test_files" / filename).read_bytes() == recorded


@pytest.mark.parametrize("path", sorted(Path(__file__).with_name("recordings").glob("*.yaml")),
                         ids=lambda path: path.stem)
def test_checked_in_recordings_are_sanitized(path):
    recording = yaml.safe_load(path.read_text(encoding="utf-8"))
    for interaction in recording["interactions"]:
        for message in (interaction["request"], interaction["response"]):
            assert not PRIVATE_HEADERS.intersection(key.lower() for key in message["headers"])
            for values in message["headers"].values():
                for value in values:
                    assert all(REDACTED.fullmatch(match[2]) for match in SENSITIVE_QUERY.finditer(value))
        request = interaction["request"]
        assert request["uri"] == sanitize_text(request["uri"])
        for raw in (request.get("body"), interaction["response"]["body"].get("string")):
            parsed = json.loads(raw) if raw else None
            assert parsed == sanitize_json(parsed)
