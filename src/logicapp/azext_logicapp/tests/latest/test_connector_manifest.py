# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Synthetic metadata contracts, not recorded connector responses or live service tests."""

import copy
import json
from types import SimpleNamespace
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit

from azure.cli.core.azclierror import ClientRequestError, HTTPError, ResourceNotFoundError, UnauthorizedError

from azext_logicapp import _runtime_client, custom


def operation_payload(connector, operation):
    """Minimal synthetic values with runtime manifest binding/type shapes."""
    if connector == "AzureBlob":
        inputs = {
            "type": "object",
            "properties": {
                "containerName": {"type": "string", "minLength": 1},
                "blobName": {"type": "string", "minLength": 1},
                "content": {"description": "Synthetic unconstrained content"},
                "overrideIfExists": {"type": "string", "enum": ["true", "false"]},
            },
            "required": ["containerName", "blobName", "content"],
        }
    else:
        inputs = {
            "type": "object",
            "properties": {
                "entityName": {"type": "string"},
                "message": {
                    "type": "object",
                    "properties": {
                        "contentData": {"description": "Synthetic unconstrained content"},
                        "contentType": {"type": "string"},
                        "userProperties": {"type": "object", "additionalProperties": {"type": "string"}},
                    },
                },
            },
            "required": ["entityName", "message"],
        }
    return {
        "id": operation,
        "name": operation,
        "type": operation,
        "properties": {
            "api": {"id": "/serviceProviders/" + connector, "name": connector, "type": "ServiceProvider"},
            "operationType": "ServiceProvider",
            "summary": "Synthetic operation",
            "visibility": "Important",
            "manifest": {
                "inputs": inputs,
                "inputsLocation": ["inputs", "parameters"],
                "outputs": {"type": "object", "properties": {"result": {"type": "string"}}},
                "connection": {"required": True, "type": "ServiceProvider"},
            },
        },
    }


class ConnectorManifestTests(unittest.TestCase):
    def show(self, payload, connector="serviceBus", operation="sendMessage", local=True, **kwargs):
        requests = []

        def sender(_cli_ctx, method, url, **options):
            requests.append((method, url, options))
            return SimpleNamespace(content=json.dumps(payload).encode("utf-8"), headers={}, status_code=200)

        target = ("http://localhost:7071" if local else
                  "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app")
        client = _runtime_client.SiteRuntimeClient(SimpleNamespace(cli_ctx=object()), target,
                                                   sender=sender, host_key="synthetic-host-key")
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})):
            result = custom.connector_operation_show(None, connector, operation, **kwargs)
        return result, requests

    def test_expanded_show_preserves_both_action_input_contracts_exactly(self):
        for connector, operation in (("serviceBus", "sendMessage"), ("AzureBlob", "uploadBlob")):
            for local in (True, False):
                with self.subTest(connector=connector, local=local):
                    payload = operation_payload(connector, operation)
                    result, requests = self.show(payload, connector, operation, local, include_manifest=True)
                    self.assertEqual(payload, result)
                    manifest = result["properties"]["manifest"]
                    self.assertEqual(["inputs", "parameters"], manifest["inputsLocation"])
                    fields = manifest["inputs"]["properties"]
                    if connector == "AzureBlob":
                        self.assertEqual(["containerName", "blobName", "content"], manifest["inputs"]["required"])
                        self.assertEqual({"type": "string", "enum": ["true", "false"]}, fields["overrideIfExists"])
                        self.assertNotIn("type", fields["content"])
                    else:
                        self.assertEqual(["entityName", "message"], manifest["inputs"]["required"])
                        self.assertEqual("object", fields["message"]["type"])
                        self.assertNotIn("type", fields["message"]["properties"]["contentData"])
                    self.assertEqual(1, len(requests))
                    method, url, options = requests[0]
                    self.assertEqual("GET", method)
                    parsed = urlsplit(url)
                    prefix = ("/runtime/webhooks/workflow/api/management" if local else
                              "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app/"
                              "hostruntime/runtime/webhooks/workflow/api/management")
                    self.assertEqual(prefix + "/operationGroups/" + connector + "/operations/" + operation,
                                     parsed.path)
                    self.assertEqual({"api-version": ["2018-11-01"], "$expand": ["properties/manifest"]},
                                     parse_qs(parsed.query))
                    self.assertIsNone(options["body"])
                    self.assertNotIn("synthetic-host-key", url)
                    if local:
                        self.assertTrue(options["skip_authorization_header"])
                        self.assertIn("x-functions-key=synthetic-host-key", options["headers"])
                    else:
                        self.assertNotIn("skip_authorization_header", options)
                        self.assertNotIn("x-functions-key=synthetic-host-key", options["headers"])

    def test_default_show_stays_metadata_only_and_does_not_expand_or_fetch_again(self):
        payload = operation_payload("serviceBus", "sendMessage")
        del payload["properties"]["manifest"]
        result, requests = self.show(payload)
        self.assertEqual(payload, result)
        self.assertEqual(1, len(requests))
        self.assertEqual({"api-version": ["2018-11-01"]}, parse_qs(urlsplit(requests[0][1]).query))
        self.assertNotIn("manifest", result["properties"])

    def test_default_show_preserves_a_manifest_if_runtime_already_returns_it(self):
        payload = operation_payload("AzureBlob", "uploadBlob")
        result, _ = self.show(payload)
        self.assertEqual(payload, result)

    def test_expansion_normalizes_full_ids_and_quotes_route_segments(self):
        payload = operation_payload("serviceBus", "sendMessage")
        _, requests = self.show(payload, "/serviceProviders/serviceBus",
                                "/serviceProviders/serviceBus/operations/odd name?x=y", include_manifest=True)
        self.assertTrue(urlsplit(requests[0][1]).path.endswith(
            "/operationGroups/serviceBus/operations/odd%20name%3Fx%3Dy"))

    def test_unavailable_or_malformed_manifest_fails_without_echoing_runtime_values(self):
        private = "synthetic-private-provider-value"
        for payload in (
                None, [], private, {}, {"properties": None}, {"properties": []},
                {"properties": {}}, {"properties": {"manifest": None}},
                {"properties": {"manifest": {}}}, {"properties": {"manifest": []}},
                {"properties": {"manifest": private}}, {"properties": {"manifest": True}}):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(ClientRequestError, "manifest") as error:
                    self.show(payload, include_manifest=True)
                self.assertNotIn(private, str(error.exception))

    def test_inputless_and_dynamic_manifests_are_not_rewritten_or_resolved(self):
        for manifest in (
                {"inputs": {"type": "object", "properties": {}}},
                {"outputs": {"type": "string"}, "isInputsOptional": True},
                {"inputs": {"type": "object", "properties": {"parameters": {
                    "x-ms-dynamic-properties": {
                        "operationId": "getSchema",
                        "parameters": {"entity": {"parameterReference": "entityName"}},
                    },
                    "$ref": "#/definitions/Parameters",
                }}}, "definitions": {"Parameters": {"type": "object"}}}):
            with self.subTest(manifest=manifest):
                payload = operation_payload("serviceBus", "sendMessage")
                payload["properties"]["manifest"] = manifest
                result, requests = self.show(payload, include_manifest=True)
                self.assertEqual(payload, result)
                self.assertEqual(1, len(requests), "Must not invoke dynamic schema or connector operations")

    def test_constraints_defaults_and_unrecognized_manifest_fields_are_preserved(self):
        payload = operation_payload("serviceBus", "sendMessage")
        payload["properties"]["manifest"]["inputs"] = {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "minimum": 1, "maximum": 10, "default": 2},
                "labels": {"type": "array", "items": {"type": "string", "enum": ["a", "b"]}, "maxItems": 3},
            },
            "additionalProperties": False,
            "required": ["count"],
            "x-synthetic-extension": {"nullable": True},
        }
        result, requests = self.show(payload, include_manifest=True)
        self.assertEqual(payload, result)
        self.assertEqual(1, len(requests))

    def test_http_and_authentication_failures_propagate_without_fallback(self):
        for error in (ResourceNotFoundError("missing"), UnauthorizedError("denied"),
                      HTTPError("unsupported", SimpleNamespace(status_code=400))):
            with self.subTest(error=type(error).__name__):
                client = mock.Mock()
                client.get.side_effect = error
                with mock.patch.object(custom, "_client_from_target", return_value=(client, {})):
                    with self.assertRaises(type(error)):
                        custom.connector_operation_show(None, "serviceBus", "sendMessage", include_manifest=True)
                client.get.assert_called_once_with("operationGroups/serviceBus/operations/sendMessage",
                                                   params={"$expand": "properties/manifest"})
                client.post.assert_not_called()

    def test_list_still_filters_and_pages_without_expansion_or_extra_requests(self):
        action = operation_payload("serviceBus", "sendMessage")
        del action["properties"]["manifest"]
        trigger = copy.deepcopy(action)
        trigger["name"] = "whenMessageArrives"
        trigger["properties"]["trigger"] = "Single"
        client = mock.Mock()
        client.get.return_value = {"value": [trigger, action, copy.deepcopy(action)]}
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})):
            page = custom.connector_operation_list(None, "serviceBus", kind="action", max_items=1)
            final = custom.connector_operation_list(None, "serviceBus", kind="action", max_items=1,
                                                     next_token=page["nextContinuationToken"])
        self.assertEqual([action], page["value"])
        self.assertEqual([action], final["value"])
        self.assertIsNone(final["nextContinuationToken"])
        self.assertEqual([mock.call("operationGroups/serviceBus/operations")] * 2, client.get.call_args_list)
