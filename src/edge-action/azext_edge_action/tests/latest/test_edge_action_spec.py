# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path

import pytest
import yaml

from .spec_validation import API_VERSION, RecordingValidator, spec, url_key


RESOURCE_ID = ("/subscriptions/00000000-0000-0000-0000-000000000000"
               "/resourceGroups/rg/providers/Microsoft.Cdn/edgeActions/action")
RESOURCE_URL = "https://management.azure.com" + RESOURCE_ID


def resource(group):
    suffix, properties = {
        "": ("", {"attachments": []}),
        "version": ("/versions/v1", {
            "deploymentType": "file", "isDefaultVersion": "False", "validationStatus": "Succeeded",
        }),
        "execution_filter": ("/executionFilters/filter", {
            "versionId": RESOURCE_ID + "/versions/v1",
            "executionFilterIdentifierHeaderName": "x-cli-test",
            "executionFilterIdentifierHeaderValue": "initial",
        }),
    }[group]
    result = {
        "id": RESOURCE_ID + suffix, "name": "action", "location": "global",
        "tags": {"purpose": "initial"}, "properties": {"provisioningState": "Succeeded", **properties},
    }
    if not group:
        result["sku"] = {"name": "Standard", "tier": "Standard"}
    return result


def operation(method="GET", suffix=""):
    return spec().operation(method, f"{RESOURCE_URL}{suffix}?api-version={API_VERSION}")[0]


def test_snapshot_is_self_contained(monkeypatch):
    monkeypatch.setattr("azext_edge_action.tests.latest.spec_validation.urlopen",
                        lambda *a, **kw: pytest.fail("Validation must be offline"))
    snapshot = spec().snapshot
    assert snapshot["source"]["repository"] == "Azure/azure-rest-api-specs"
    assert len(snapshot["source"]["sha256"]) >= 2
    assert len(snapshot["paths"]) == 10
    for path in snapshot["paths"].values():
        for item in path.values():
            for response in item["responses"].values():
                if "schema" in response:
                    spec().check_schema(spec().prepare_schema(response["schema"]))

    def check_refs(value):
        if isinstance(value, dict):
            if "$ref" in value:
                assert value["$ref"].startswith("#/definitions/")
                spec().resolve(value)
            for item in value.values():
                check_refs(item)
        elif isinstance(value, list):
            for item in value:
                check_refs(item)
    check_refs(snapshot)


@pytest.mark.parametrize("schema,valid,invalid,rule", [
    ({"type": "integer"}, 1, True, "type"),
    ({"type": "string", "minLength": 1}, "a", "", "minLength"),
    ({"type": "string", "maxLength": 2}, "ab", "abc", "maxLength"),
    ({"type": "string", "pattern": "^[a-z]+$"}, "abc", "123", "pattern"),
    ({"type": "string", "enum": ["True", "False"]}, "False", "false", "enum"),
    ({"enum": [True]}, True, 1, "enum"),
    ({"type": "object", "additionalProperties": {"type": "string"}}, {"tag": "1"}, {"tag": 1}, "type"),
    ({"type": "array", "items": {"type": "string"}}, ["a"], [1], "type"),
    ({"allOf": [{"type": "object"}, {"required": ["name"]}]}, {"name": "a"}, {}, "required"),
    ({"type": "string", "format": "uuid"}, "00000000-0000-0000-0000-000000000000", "invalid", "format"),
    ({"type": "string", "format": "date-time"}, "2026-10-01T00:00:00Z", "2026-02-30T00:00:00Z", "format"),
    ({"type": "string", "format": "date-time"}, "2026-10-01T01:00:00+01:00", "2026-10-01", "format"),
    ({"type": "string", "format": "date-time"}, "2026-10-01T00:00:00Z", "2026-10-01T00:00:00+00:99", "format"),
    ({"type": "string", "format": "uri"}, "https://example.test/path", "not a URL", "format"),
    ({"type": "string", "format": "uri"}, "https://example.test/?x=%20", "https://example.test/?x=%zz", "format"),
    ({"type": "string", "format": "uri"}, "https://[::1]/path", "https://example.test/[invalid]", "format"),
])
def test_pinned_schema_constraints(schema, valid, invalid, rule):
    spec().validate_schema(valid, schema, "Constraint")
    with pytest.raises(AssertionError, match=rule):
        spec().validate_schema(invalid, schema, "Constraint")


@pytest.mark.parametrize("schema", [
    {"type": "integer", "minimum": 0},
    {"type": "object", "properties": {"optional": {"not": {"type": "string"}}}},
    {"type": "string", "format": "unknown"},
])
def test_new_schema_constraints_fail_closed(schema):
    with pytest.raises(AssertionError, match="Unsupported pinned schema"):
        spec().validate_schema(None, schema, "Constraint")


def test_schema_reference_preparation_retains_swagger_semantics():
    spec().validate_schema(None, {"type": "string", "x-nullable": True}, "Nullable")
    spec().validate_schema("new-value", {
        "type": "string", "enum": ["old-value"], "x-ms-enum": {"modelAsString": True},
    }, "Extensible enum")
    schema = {"type": "object", "required": ["id", "name"], "properties": {
        "id": {"type": "string", "readOnly": True}, "name": {"type": "string"},
    }}
    spec().validate_schema({"name": "a"}, schema, "Request", request=True)
    with pytest.raises(AssertionError, match="required"):
        spec().validate_schema({"name": "a"}, schema, "Response")


@pytest.mark.parametrize("group,suffix", [
    ("", ""), ("version", "/versions/v1"), ("execution_filter", "/executionFilters/filter"),
])
def test_resource_schema_accepts_valid_response(group, suffix):
    spec().validate_response(operation(suffix=suffix), 200, resource(group))


@pytest.mark.parametrize("field,value,rule", [
    ("location", 5, "type"),
    ("id", None, "type"),
    ("properties", [], "type"),
])
def test_schema_rejects_wrong_types(field, value, rule):
    body = resource("")
    body[field] = value
    with pytest.raises(AssertionError, match=rule):
        spec().validate_response(operation(), 200, body)


def test_schema_rejects_missing_required_field():
    body = resource("")
    del body["location"]
    with pytest.raises(AssertionError, match="required"):
        spec().validate_response(operation(), 200, body)


def test_deploy_result_must_be_full_version_resource():
    op = operation("POST", "/versions/v1/deployVersionCode")
    spec().validate_response(op, 200, resource("version"))
    with pytest.raises(AssertionError, match="required"):
        spec().validate_response(op, 200, resource("version")["properties"])


def test_get_code_requires_both_name_and_content():
    op = operation("POST", "/versions/v1/getVersionCode")
    spec().validate_response(op, 200, {"name": "v1", "content": "YQ=="})
    with pytest.raises(AssertionError, match="required"):
        spec().validate_response(op, 200, {"name": "v1"})


def test_explicit_false_is_a_string_not_a_boolean():
    body = resource("version")
    body["properties"]["isDefaultVersion"] = False
    with pytest.raises(AssertionError, match="type"):
        spec().validate_response(operation(suffix="/versions/v1"), 200, body)


@pytest.mark.parametrize("method,suffix,is_list", [
    ("GET", "/versions/v1", False),
    ("GET", "/versions", True),
    ("POST", "/versions/v1/deployVersionCode", False),
])
def test_null_version_validation_status_is_allowed(method, suffix, is_list):
    body = resource("version")
    body["properties"]["validationStatus"] = None
    spec().validate_response(operation(method, suffix), 200, {"value": [body]} if is_list else body)


@pytest.mark.parametrize("value", [False, 1, {}, []])
def test_non_null_validation_status_still_requires_string(value):
    body = resource("version")
    body["properties"]["validationStatus"] = value
    with pytest.raises(AssertionError, match="properties.validationStatus"):
        spec().validate_response(operation(suffix="/versions/v1"), 200, body)


def test_null_validation_status_allowance_does_not_change_requests_or_snapshot():
    snapshot_before = json.dumps(spec().snapshot, sort_keys=True)
    body = resource("version")
    body["properties"]["validationStatus"] = None
    spec().validate_response(operation(suffix="/versions/v1"), 200, body)
    with pytest.raises(AssertionError, match="properties.validationStatus"):
        spec().validate_request("PUT", f"{RESOURCE_URL}/versions/v1?api-version={API_VERSION}",
                                body, {"Content-Type": "application/json"})
    assert json.dumps(spec().snapshot, sort_keys=True) == snapshot_before


@pytest.mark.parametrize("status,body", [(200, {"status": "Succeeded"}), (204, {"status": "Succeeded"})])
def test_swap_default_initial_response_remains_strict(status, body):
    with pytest.raises(AssertionError, match="undocumented|must not contain"):
        spec().validate_response(operation("POST", "/versions/v1/swapDefault"), status, body)


def test_swap_default_accepts_empty_204():
    spec().validate_response(operation("POST", "/versions/v1/swapDefault"), 204, b"")


@pytest.mark.parametrize("headers", [
    {}, {"Location": "not-a-url"}, {"Location": "https://example.test/result", "Retry-After": "invalid"},
])
def test_accepted_response_rejects_invalid_polling_headers(headers):
    with pytest.raises(AssertionError):
        RecordingValidator(spec()).validate(
            "POST", f"{RESOURCE_URL}/versions/v1/getVersionCode?api-version={API_VERSION}",
            None, {}, 202, None, headers)


def test_request_schema_requires_sku_but_not_readonly_fields():
    url = f"{RESOURCE_URL}?api-version={API_VERSION}"
    body = {"location": "global", "sku": {"name": "Standard", "tier": "Standard"}}
    spec().validate_request("PUT", url, body, {"Content-Type": "application/json"})
    del body["sku"]
    with pytest.raises(AssertionError, match="required"):
        spec().validate_request("PUT", url, body, {"Content-Type": "application/json"})


def test_request_and_error_diagnostics_do_not_disclose_values():
    url = f"{RESOURCE_URL}/versions/v1/deployVersionCode?api-version={API_VERSION}"
    with pytest.raises(AssertionError) as error:
        spec().validate_request("POST", url, {"name": "v1", "content": {"secret": "do-not-log"}},
                                {"Content-Type": "application/json"})
    assert "do-not-log" not in str(error.value)
    assert "content" in str(error.value)


def test_undocumented_put_202_is_rejected():
    with pytest.raises(AssertionError, match="undocumented HTTP 202"):
        spec().validate_response(operation("PUT"), 202, None, {"Location": "https://example.test/result"})


def test_lro_location_uses_original_action_contract():
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/getVersionCode?api-version={API_VERSION}"
    status_url = "https://management.azure.com/opaque/status?c=Sanitized_token"
    result_url = "https://management.azure.com/opaque/result?c=Sanitized_token"
    validator.validate("POST", url, None, {}, 202, None, {
        "Azure-AsyncOperation": status_url, "Location": result_url,
    })
    validator.validate("GET", status_url, None, {}, 200, {"status": "Running"}, {})
    validator.validate("GET", status_url, None, {}, 200, {"status": "Succeeded"}, {})
    validator.validate("GET", result_url, None, {}, 200, {"name": "v1", "content": "YQ=="}, {})
    with pytest.raises(AssertionError, match="required"):
        validator.validate("GET", result_url, None, {}, 200, {"status": "Succeeded"}, {})


@pytest.mark.parametrize("status,body", [
    (200, {"status": "Succeeded", "error": 123, "properties": None}),
    (204, None),
    (204, {"status": "Succeeded"}),
    (204, "ignored body"),
])
def test_swap_default_location_does_not_require_204_or_empty_body(status, body):
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"
    result_url = "https://management.azure.com/opaque/swap-result"
    validator.validate("POST", url, None, {}, 202, None, {"Location": result_url})
    validator.validate("GET", result_url, None, {}, status, body, {})


def test_swap_default_resource_location_uses_resource_contract_for_later_gets():
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"
    result_url = f"{RESOURCE_URL}/versions/v1?api-version={API_VERSION}"
    status_url = "https://management.azure.com/opaque/status"
    validator.validate("POST", url, None, {}, 202, None, {
        "Azure-AsyncOperation": status_url, "Location": result_url})
    validator.validate("GET", status_url, None, {}, 200, {"status": "Succeeded"}, {})
    for _ in range(2):
        validator.validate("GET", result_url, None, {}, 200, resource("version"), {})
    with pytest.raises(AssertionError, match="required"):
        validator.validate("GET", result_url, None, {}, 200, {"status": "Succeeded"}, {})


@pytest.mark.parametrize("body", [None, {"status": "Succeeded"}])
def test_swap_default_resource_location_retains_204_allowance(body):
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"
    result_url = f"{RESOURCE_URL}/versions/v1?api-version={API_VERSION}"
    validator.validate("POST", url, None, {}, 202, None, {"Location": result_url})
    validator.validate("GET", result_url, None, {}, 204, body, {})


def test_swap_default_resource_location_rejects_api_version_drift():
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"
    result_url = f"{RESOURCE_URL}/versions/v1?api-version=2025-09-01-preview"
    validator.validate("POST", url, None, {}, 202, None, {"Location": result_url})
    with pytest.raises(AssertionError, match="API version mismatch"):
        validator.validate("GET", result_url, None, {}, 200, resource("version"), {})


def test_async_operation_resource_url_still_requires_status():
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"
    status_url = f"{RESOURCE_URL}/versions/v1?api-version={API_VERSION}"
    validator.validate("POST", url, None, {}, 202, None, {"Azure-AsyncOperation": status_url})
    with pytest.raises(AssertionError, match="Operation status"):
        validator.validate("GET", status_url, None, {}, 200, resource("version"), {})


@pytest.mark.parametrize("action,header", [
    ("getVersionCode", "Azure-AsyncOperation"),
    ("swapDefault", "Location"),
])
@pytest.mark.parametrize("value", ["InProgress", "Succeeded", "Failed", "Canceled"])
def test_async_polling_only_validates_status_field(action, header, value):
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/{action}?api-version={API_VERSION}"
    status_url = "https://management.azure.com/opaque/status"
    validator.validate("POST", url, None, {}, 202, None, {header: status_url})
    validator.validate("GET", status_url, None, {}, 200, {
        "status": value, "error": 123, "properties": None, "nextLink": "not-a-url",
    }, {})


@pytest.mark.parametrize("header", ["Azure-AsyncOperation", "Location"])
@pytest.mark.parametrize("body", [{}, {"status": None}, {"status": ""}, {"status": 1}])
def test_async_polling_still_requires_valid_status(header, body):
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"
    status_url = "https://management.azure.com/opaque/status"
    validator.validate("POST", url, None, {}, 202, None, {header: status_url})
    with pytest.raises(AssertionError, match="Operation status"):
        validator.validate("GET", status_url, None, {}, 200, body, {})


@pytest.mark.parametrize("header", ["Azure-AsyncOperation", "Location"])
def test_async_polling_does_not_accept_http_errors(header):
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/swapDefault?api-version={API_VERSION}"
    status_url = "https://management.azure.com/opaque/status"
    validator.validate("POST", url, None, {}, 202, None, {header: status_url})
    with pytest.raises(AssertionError, match="must return HTTP 200"):
        validator.validate("GET", status_url, None, {}, 500, {"status": "Succeeded"}, {})


def test_non_swap_location_no_content_contract_remains_strict():
    validator = RecordingValidator(spec())
    result_url = "https://management.azure.com/opaque/delete-result"
    validator.validate("DELETE", f"{RESOURCE_URL}?api-version={API_VERSION}",
                       None, {}, 202, None, {"Location": result_url})
    with pytest.raises(AssertionError, match="must not contain"):
        validator.validate("GET", result_url, None, {}, 204, {"status": "Succeeded"}, {})


def test_location_can_return_202_before_final_result():
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/getVersionCode?api-version={API_VERSION}"
    result_url = "https://management.azure.com/opaque/result"
    validator.validate("POST", url, None, {}, 202, None, {"Location": result_url})
    validator.validate("GET", result_url, None, {}, 202, None, {"Location": result_url})
    validator.validate("GET", result_url, None, {}, 200, {"name": "v1", "content": "YQ=="}, {})


def test_polling_api_version_drift_is_rejected():
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}/versions/v1/getVersionCode?api-version={API_VERSION}"
    result_url = "https://management.azure.com/opaque/result?api-version=2025-09-01-preview"
    validator.validate("POST", url, None, {}, 202, None, {"Location": result_url})
    with pytest.raises(AssertionError, match="API version mismatch"):
        validator.validate("GET", result_url, None, {}, 200, {"name": "v1", "content": "YQ=="}, {})


def test_subscription_list_is_in_stable_spec():
    url = RESOURCE_URL.split("/resourceGroups/")[0] + (
        f"/providers/Microsoft.Cdn/edgeActions?api-version={API_VERSION}")
    op = spec().validate_request("GET", url)
    assert op["operationId"] == "EdgeActions_ListBySubscription"
    spec().validate_response(op, 200, {"value": [resource("")]})


def test_opaque_urls_preserve_path_case_and_empty_query_parameters():
    assert url_key("https://example.test/status/A") != url_key("https://example.test/status/a")
    assert url_key("https://example.test/status?token=") != url_key("https://example.test/status")


def test_invalid_json_is_reported_without_contents():
    with pytest.raises(AssertionError, match="HTTP body is not valid JSON"):
        spec().validate_response(operation(), 200, "private malformed json")


def test_status_document_is_not_a_resource_response():
    validator = RecordingValidator(spec())
    url = f"{RESOURCE_URL}?api-version={API_VERSION}"
    validator.validate("DELETE", url, None, {}, 202, None, {
        "Azure-AsyncOperation": "https://management.azure.com/opaque/status"})
    with pytest.raises(AssertionError, match="required"):
        validator.validate("GET", "https://management.azure.com/opaque/status", None, {}, 200, resource(""), {})


@pytest.mark.parametrize("group,suffix", [
    ("", ""), ("version", "/versions"), ("execution_filter", "/executionFilters"),
])
def test_next_link_response_preserves_list_contract(group, suffix):
    validator = RecordingValidator(spec())
    collection_url = RESOURCE_URL + suffix if suffix else RESOURCE_URL.rsplit("/", 1)[0]
    url = collection_url + f"?api-version={API_VERSION}"
    next_link = "https://management.azure.com/opaque/page?$skiptoken=2"
    validator.validate("GET", url, None, {}, 200, {"value": [], "nextLink": next_link}, {})
    validator.validate("GET", next_link, None, {}, 200, {"value": [resource(group)]}, {})
    with pytest.raises(AssertionError, match="required"):
        validator.validate("GET", next_link, None, {}, 200, resource(group), {})


def test_preview_recording_cannot_validate_as_stable(tmp_path):
    path = tmp_path / "preview.yaml"
    path.write_text(yaml.safe_dump({"interactions": [{
        "request": {"uri": RESOURCE_URL + "?api-version=2025-09-01-preview",
                    "method": "GET", "headers": {}, "body": None},
        "response": {"status": {"code": 200}, "headers": {}, "body": {"string": json.dumps(resource(""))}},
    }]}), encoding="utf-8")
    with pytest.raises(AssertionError, match="interaction 1:.*expected api-version=2026-10-01"):
        RecordingValidator(spec()).validate_file(path)


@pytest.mark.parametrize("recording", sorted(Path(__file__).with_name("recordings").glob("*.yaml")),
                         ids=lambda path: path.stem)
def test_recording_matches_pinned_spec(recording):
    RecordingValidator(spec()).validate_file(recording)
