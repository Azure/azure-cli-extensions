# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import hashlib
import json
from pathlib import Path
import re

from azure.cli.testsdk.scenario_tests.recording_processors import RecordingProcessor
from vcr.request import Request
import yaml


SENSITIVE_QUERY = re.compile(r'(?i)([?&](?:t|c|s|h|sig|token|access_token)=)([^&\s"\\#]+)')
REDACTED = re.compile(r"Sanitized_[0-9a-f]{16}$")
PRIVATE_HEADERS = {
    "authorization", "proxy-authorization", "x-ms-authorization-auxiliary", "cookie", "set-cookie",
    "x-ms-client-request-id", "x-ms-request-id", "x-ms-correlation-request-id", "x-ms-routing-request-id",
    "x-ms-operation-identifier", "x-ms-original-request-ids", "x-msedge-ref",
}
PRIVATE_FIELDS = {"access_token", "refresh_token", "id_token", "client_secret"}


def sanitize_text(value):
    def replace(match):
        secret = match[2]
        if REDACTED.fullmatch(secret):
            return match[0]
        # Keep distinct opaque polling tokens distinct, without preserving usable credentials.
        digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()[:16]
        return match[1] + "Sanitized_" + digest
    return SENSITIVE_QUERY.sub(replace, value)


def sanitize_json(value, system_data=False):
    if isinstance(value, dict):
        return {
            key: "Sanitized" if key.lower() in PRIVATE_FIELDS or (
                system_data and key.lower() in ("createdby", "lastmodifiedby")
            ) else item if key == "content" else sanitize_json(item, key.lower() == "systemdata")
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_json(item, system_data) for item in value]
    return sanitize_text(value) if isinstance(value, str) else value


def sanitize_body(body):
    if body is None or body == "" or body == b"":
        return body
    is_bytes = isinstance(body, bytes)
    text = body.decode("utf-8") if is_bytes else body
    try:
        value = json.loads(text)
    except ValueError:
        sanitized = sanitize_text(text)
    else:
        value = sanitize_json(value)
        sanitized = json.dumps(value, separators=(",", ":"), ensure_ascii=True)
    return sanitized.encode("utf-8") if is_bytes else sanitized


def sanitize_headers(headers):
    for key in list(headers):
        if key.lower() in PRIVATE_HEADERS:
            del headers[key]
        else:
            value = headers[key]
            headers[key] = [sanitize_text(item) for item in value] if isinstance(value, list) else sanitize_text(value)


def update_length(headers, body):
    if body is None:
        return
    size = len(body if isinstance(body, bytes) else body.encode("utf-8"))
    for key, value in headers.items():
        if key.lower() == "content-length":
            headers[key] = [str(size)] if isinstance(value, list) else str(size)


class EdgeActionRecordingProcessor(RecordingProcessor):
    """Extend ScenarioTest's default name/subscription/auth sanitizers."""

    def process_request(self, request):
        request.uri = sanitize_text(request.uri)
        sanitize_headers(request.headers)
        request.body = sanitize_body(request.body)
        update_length(request.headers, request.body)
        return request

    def process_response(self, response):
        sanitize_headers(response["headers"])
        response["body"]["string"] = sanitize_body(response["body"].get("string"))
        update_length(response["headers"], response["body"]["string"])
        return response


def sanitize_recording(path):
    processor = EdgeActionRecordingProcessor()
    recording = yaml.safe_load(path.read_text(encoding="utf-8"))
    for interaction in recording["interactions"]:
        original = interaction["request"]
        request = processor.process_request(Request(
            original["method"], original["uri"], original.get("body"), original["headers"]))
        original["uri"] = request.uri
        original["headers"] = {key: [value] if isinstance(value, str) else value
                               for key, value in request.headers.items()}
        original["body"] = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
        processor.process_response(interaction["response"])
    path.write_text(yaml.safe_dump(recording, sort_keys=False, allow_unicode=False), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sanitize existing cassettes offline; never re-record traffic.")
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    paths = sorted(args.directory.glob("*.yaml"))
    if not paths:
        parser.error("No YAML recordings found")
    for recording_path in paths:
        sanitize_recording(recording_path)
        print(f"Sanitized {recording_path.name}")
