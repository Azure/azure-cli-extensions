# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Pinned Swagger validation. Refresh is explicit; validation never accesses Azure or the network."""

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, parse_qsl, urldefrag, urljoin, urlsplit
from urllib.request import urlopen

from jsonschema import Draft4Validator, FormatChecker
import yaml


API_VERSION = "2026-10-01"
SPEC_PATH = "specification/cdn/resource-manager/Microsoft.Cdn/EdgeActions/stable/2026-10-01/openapi.json"
SNAPSHOT = Path(__file__).with_name("spec_snapshot.json")


def headers_dict(headers):
    return {key.lower(): value[0] if isinstance(value, list) else value
            for key, value in headers.items()}


def body_json(body):
    if body is None or body == "" or body == b"":
        return None
    if isinstance(body, (dict, list)):
        return body
    try:
        return json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise AssertionError("HTTP body is not valid JSON") from None


def url_key(url):
    parsed = urlsplit(url)
    return (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path,
            tuple(sorted(parse_qsl(parsed.query, keep_blank_values=True))))


class Spec:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        assert snapshot["api_version"] == API_VERSION, "Unexpected snapshot API version"
        self.definitions = snapshot["definitions"]

    def resolve(self, schema):
        while "$ref" in schema:
            ref = schema["$ref"]
            assert ref.startswith("#/definitions/"), "Only bundled local schema references are allowed"
            schema = self.definitions[ref.rsplit("/", 1)[-1]]
        return schema

    def operation(self, method, url):
        parsed = urlsplit(url)
        for path, methods in self.snapshot["paths"].items():
            pattern = "/".join("([^/]+)" if part.startswith("{") else re.escape(part)
                               for part in path.split("/"))
            match = re.fullmatch(pattern, parsed.path, re.IGNORECASE)
            if match:
                operation = methods.get(method.lower())
                assert operation is not None, f"Undocumented HTTP method: {method.upper()}"
                assert parse_qs(parsed.query).get("api-version") == [API_VERSION], (
                    f"{operation['operationId']}: expected api-version={API_VERSION}; re-record against the pinned API")
                names = re.findall(r"\{([^}]+)\}", path)
                return operation, dict(zip(names, match.groups()))
        raise AssertionError("No operation matches the request path in the pinned EdgeActions spec")

    def prepare_schema(self, schema, request=False):
        # Swagger readOnly required fields are not required in request bodies.
        def prepare(node):
            if isinstance(node, list):
                return [prepare(item) for item in node]
            if not isinstance(node, dict):
                return node
            result = {key: prepare(item) for key, item in node.items()}
            if isinstance(node.get("required"), bool):
                result.pop("required", None)
            if node.get("x-ms-enum", {}).get("modelAsString"):
                result.pop("enum", None)
            properties = node.get("properties", {})
            validation_status = properties.get("validationStatus", {})
            if not request and validation_status.get("$ref", "").endswith("_EdgeActionVersionValidationStatus"):
                # Test-only allowance for null version validationStatus; leave the pinned spec unchanged.
                result["properties"]["validationStatus"] = {
                    "anyOf": [result["properties"]["validationStatus"], {"type": "null"}],
                }
            if request and isinstance(node.get("required", []), list):
                result["required"] = [
                    key for key in node.get("required", [])
                    if not self.resolve(properties.get(key, {})).get("readOnly")
                ]
                if not result["required"]:
                    result.pop("required")
            if node.get("x-nullable"):
                return {"anyOf": [result, {"type": "null"}]}
            return result

        return prepare({**schema, "definitions": self.definitions})

    def validate_schema(self, value, schema, description, request=False):
        bundled = self.prepare_schema(schema, request=request)
        for error in Draft4Validator(bundled, format_checker=FormatChecker()).iter_errors(value):
            field = ".".join(str(part) for part in error.absolute_path) or "<body>"
            # Do not echo response values, URLs with signed queries, or validation-error reprs.
            raise AssertionError(f"{description}: {field} violates OpenAPI {error.validator}") from None

    def validate_request(self, method, url, body=None, headers=None):
        operation, path_values = self.operation(method, url)
        actual_headers = headers_dict(headers or {})
        query = parse_qs(urlsplit(url).query, keep_blank_values=True)
        payload = body_json(body)
        body_parameter = None
        for item in operation.get("parameters", []):
            parameter = self.resolve(item)
            name, location = parameter["name"], parameter["in"]
            if location == "body":
                body_parameter = parameter
                value = payload
                schema = parameter["schema"]
            elif location == "path":
                value = path_values.get(name)
                schema = parameter
            elif location == "query":
                value = query.get(name, [None])[0]
                schema = parameter
            elif location == "header":
                value = actual_headers.get(name.lower())
                schema = parameter
            else:
                raise AssertionError(f"Unsupported Swagger parameter location: {location}")
            if value is None:
                assert not parameter.get("required"), f"{operation['operationId']}: missing required {name}"
            else:
                self.validate_schema(value, schema, f"{operation['operationId']} request {name}", request=True)
        assert body_parameter or payload is None, f"{operation['operationId']}: request body is not declared"
        if payload is not None:
            assert actual_headers.get("content-type", "").split(";")[0] == "application/json", (
                f"{operation['operationId']}: expected application/json request")
        return operation

    def validate_response(self, operation, status, body=None, headers=None):
        name = operation["operationId"]
        response = operation["responses"].get(str(status))
        if response is None and status >= 400:
            response = operation["responses"].get("default")
        assert response is not None, f"{name}: undocumented HTTP {status}"
        response = self.resolve(response)
        payload = body_json(body)
        if "schema" in response:
            assert payload is not None, f"{name}: HTTP {status} requires a body"
            self.validate_schema(payload, response["schema"], f"{name} response")
        else:
            assert payload is None, f"{name}: HTTP {status} must not contain a body"
        actual_headers = headers_dict(headers or {})
        for key, schema in response.get("headers", {}).items():
            value = actual_headers.get(key.lower())
            if value is None:
                assert not schema.get("required"), f"{name}: missing {key} header"
                continue
            if schema.get("type") == "integer":
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    raise AssertionError(f"{name}: {key} must be an integer") from None
            self.validate_schema(value, schema, f"{name} header {key}")
        if status == 202 and operation.get("x-ms-long-running-operation"):
            assert actual_headers.get("azure-asyncoperation") or actual_headers.get("location"), (
                f"{name}: HTTP 202 requires a polling URL")


class RecordingValidator:
    """Associate opaque polling and pagination URLs with their initiating operation."""

    def __init__(self, spec):
        self.spec = spec
        self.links = {}

    def validate(self, method, url, request_body, request_headers, status, response_body, response_headers):
        link = self.links.get(url_key(url)) if method.upper() == "GET" else None
        if link:
            kind, operation = link
            version = parse_qs(urlsplit(url).query).get("api-version")
            assert version is None or version == [API_VERSION], "Polling/pagination API version mismatch"
            swap_result = kind in ("result", "resource") and operation["operationId"] == "EdgeActionVersions_SwapDefault"
            if swap_result and status == 204:
                # Do not assert an empty body for swapDefault's Location response.
                return
            if kind == "resource":
                resource_operation = self.spec.validate_request(method, url, request_body, request_headers)
                self.spec.validate_response(resource_operation, status, response_body, response_headers)
                return
            if kind == "status" or (swap_result and status != 202):
                assert status == 200, "Operation status endpoint must return HTTP 200"
                self.spec.validate_schema(body_json(response_body), {
                    "type": "object", "required": ["status"],
                    "properties": {"status": {"type": "string", "minLength": 1}},
                }, "Operation status")
                return
            self.spec.validate_response(operation, status, response_body, response_headers)
        else:
            operation = self.spec.validate_request(method, url, request_body, request_headers)
            self.spec.validate_response(operation, status, response_body, response_headers)

        headers = headers_dict(response_headers)
        if operation.get("x-ms-long-running-operation"):
            for header, kind in (("azure-asyncoperation", "status"), ("location", "result")):
                target = headers.get(header)
                if target:
                    parsed = urlsplit(target)
                    assert parsed.scheme == "https" and parsed.netloc, f"{header} must be an absolute HTTPS URL"
                    # A PUT's Location can identify the resource, not the final LRO result.
                    if header == "location" and status != 202:
                        continue
                    source = urlsplit(url)
                    if (header == "location" and operation["operationId"] == "EdgeActionVersions_SwapDefault"
                            and parsed.scheme.lower() == source.scheme.lower()
                            and parsed.netloc.lower() == source.netloc.lower()
                            and parsed.path.lower() == source.path.rsplit("/", 1)[0].lower()):
                        # A resource Location returns the version, not an operation-status document.
                        kind = "resource"
                    self.links[url_key(target)] = (kind, operation)
        payload = body_json(response_body)
        if isinstance(payload, dict) and payload.get("nextLink"):
            target = payload["nextLink"]
            assert urlsplit(target).scheme == "https" and urlsplit(target).netloc, "nextLink must be an HTTPS URL"
            self.links[url_key(target)] = ("page", operation)

    def validate_file(self, path):
        recording = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        interactions = recording.get("interactions", [])
        assert interactions, "Recording contains no HTTP interactions"
        for index, interaction in enumerate(interactions):
            request, response = interaction["request"], interaction["response"]
            try:
                self.validate(request["method"], request["uri"], request.get("body"), request["headers"],
                              response["status"]["code"], response["body"].get("string"), response["headers"])
            except AssertionError as error:
                raise AssertionError(f"{Path(path).name} interaction {index + 1}: {error}") from None
        return len(interactions)


@lru_cache
def spec():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert re.fullmatch(r"[0-9a-f]{40}", snapshot["source"]["commit"]), "Snapshot needs a full commit SHA"
    return Spec(snapshot)


def refresh_snapshot(commit):
    """Bundle actual Swagger references at one immutable upstream revision."""
    assert re.fullmatch(r"[0-9a-f]{40}", commit), "Supply a full commit SHA"
    root = f"https://raw.githubusercontent.com/Azure/azure-rest-api-specs/{commit}/"
    documents, definitions, references, hashes = {}, {}, {}, {}

    def document(url):
        assert url.startswith(root), "References must stay in the pinned specs repository"
        if url not in documents:
            with urlopen(url, timeout=30) as response:
                raw = response.read()
            hashes[url[len(root):]] = hashlib.sha256(raw).hexdigest()
            documents[url] = json.loads(raw)
        return documents[url]

    def bundle(value, source):
        if isinstance(value, list):
            return [bundle(item, source) for item in value]
        if not isinstance(value, dict):
            return value
        result = {}
        for key, item in value.items():
            if key != "$ref":
                result[key] = bundle(item, source)
                continue
            url, pointer = urldefrag(urljoin(source, item))
            ref = (url, pointer)
            if ref not in references:
                name = f"{len(references)}_{pointer.rsplit('/', 1)[-1]}"
                references[ref] = name
                target = document(url)
                for part in pointer.lstrip("/").split("/"):
                    target = target[part.replace("~1", "/").replace("~0", "~")]
                definitions[name] = bundle(target, url)
            result[key] = "#/definitions/" + references[ref]
        return result

    source_url = root + SPEC_PATH
    source = document(source_url)
    assert source["swagger"] == "2.0" and source["info"]["version"] == API_VERSION
    paths = {}
    for path, methods in source["paths"].items():
        paths[path] = {}
        for method, operation in methods.items():
            if not isinstance(operation, dict) or "operationId" not in operation:
                continue
            selected = {key: value for key, value in operation.items()
                        if key in ("operationId", "parameters", "responses", "x-ms-pageable",
                                   "x-ms-long-running-operation", "x-ms-long-running-operation-options")}
            selected["parameters"] = methods.get("parameters", []) + operation.get("parameters", [])
            paths[path][method] = bundle(selected, source_url)
    snapshot = {"source": {"repository": "Azure/azure-rest-api-specs", "commit": commit,
                           "path": SPEC_PATH, "sha256": hashes},
                "api_version": API_VERSION, "paths": paths, "definitions": definitions}
    SNAPSHOT.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Bundled {len(paths)} paths and {len(definitions)} definitions from {commit}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", metavar="COMMIT")
    group.add_argument("--recordings", type=Path)
    args = parser.parse_args()
    if args.refresh:
        refresh_snapshot(args.refresh)
        return 0
    files = sorted(args.recordings.glob("*.yaml"))
    if not files:
        parser.error("No YAML recordings found")
    failures = 0
    for path in files:
        try:
            count = RecordingValidator(spec()).validate_file(path)
            print(f"PASS {path.name}: {count} interactions")
        except AssertionError as error:
            failures += 1
            print(f"FAIL {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
