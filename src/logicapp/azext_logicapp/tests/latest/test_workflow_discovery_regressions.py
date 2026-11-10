# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import copy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import (
    ClientRequestError, FileOperationError, HTTPError, InvalidArgumentValueError,
    MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError,
    UnauthorizedError, ValidationError)
from requests.exceptions import ConnectionError as RequestsConnectionError

from azext_logicapp import (
    COMMAND_LOADER_CLS, _paging, _runtime_client, _workflow, _workflow_discovery,
    _workflow_mutation, _workflow_state, custom)


SITE = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"


def metadata(name="hello", kind="Stateful", disabled=False):
    # Captured from a real local Functions 4.15.2 / workflow bundle runtime.
    return {"name": name, "definition_href": "https://localhost/admin/vfs/hello/workflow.json",
            "href": "https://localhost/runtime/webhooks/workflow/api/management/workflows/hello",
            "kind": kind, "triggers": {"manual": {"type": "Request", "kind": "Http"}},
            "isDisabled": disabled, "health": {"state": "Healthy"}}


class Sender:
    def __init__(self, inventory=None, workflow=None, document=None):
        self.inventory = [metadata()] if inventory is None else inventory
        self.workflow = metadata() if workflow is None else workflow
        self.document = _workflow.workflow_json("Stateful") if document is None else document
        self.requests = []
        self.fail_suffix = None
        self.failure = None

    def __call__(self, cli_ctx, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        parsed = urlsplit(url)
        if self.fail_suffix and parsed.path.endswith(self.fail_suffix):
            raise self.failure
        if parsed.path.endswith("/workflows"):
            payload = self.inventory
            if callable(payload):
                payload = payload(parse_qs(parsed.query))
        elif parsed.path.endswith("/workflows/hello"):
            payload = self.workflow
        elif parsed.path.endswith("/hello/workflow.json"):
            payload = self.document
        else:
            raise AssertionError("Unexpected request {}".format(url))
        return SimpleNamespace(content=json.dumps(payload).encode("utf-8"),
                               json=lambda: copy.deepcopy(payload), headers={})


class WorkflowDiscoveryRegressions(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "hello" / "workflow.json"
        self.cmd = SimpleNamespace(cli_ctx=get_default_cli())
        self.sender = Sender()
        self.client = _runtime_client.SiteRuntimeClient(
            self.cmd, "http://localhost:17071", sender=self.sender, host_key="test-host-key")

    def show(self):
        return _workflow_discovery.show_workflow(self.client, "hello")

    def export(self, force=False):
        return _workflow_discovery.export_workflow(self.client, "hello", str(self.path), force)

    def test_actual_runtime_metadata_and_vfs_contract(self):
        shown = self.show()
        self.assertEqual({"name", "kind", "state", "health", "workflow", "etag"}, set(shown))
        self.assertEqual("hello", shown["name"])
        self.assertEqual("Enabled", shown["state"])
        self.assertEqual("Healthy", shown["health"])
        self.assertEqual(self.sender.document, shown["workflow"])
        self.assertEqual(2, len(self.sender.requests))
        for method, url, kwargs in self.sender.requests:
            self.assertEqual("GET", method)
            self.assertEqual("localhost:17071", urlsplit(url).netloc)
            self.assertNotIn("test-host-key", url)
            self.assertTrue(kwargs["skip_authorization_header"])
            self.assertIn("x-functions-key=test-host-key", kwargs["headers"])
        self.assertEqual("/admin/vfs/hello/workflow.json", urlsplit(self.sender.requests[-1][1]).path)
        self.assertEqual(["1"], parse_qs(urlsplit(self.sender.requests[-1][1]).query)["relativePath"])

    def test_cloud_routing_uses_same_contract_without_local_auth(self):
        client = _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=self.sender)
        shown = _workflow_discovery.show_workflow(client, "hello")
        self.assertEqual(self.sender.document, shown["workflow"])
        self.assertEqual(SITE + "/hostruntime/admin/vfs/hello/workflow.json",
                         urlsplit(self.sender.requests[-1][1]).path)
        for method, _, kwargs in self.sender.requests:
            self.assertEqual("GET", method)
            self.assertNotIn("skip_authorization_header", kwargs)
            self.assertFalse(any(header.startswith("x-functions-key") for header in kwargs["headers"]))

    def test_pascal_case_and_arm_envelope_metadata(self):
        self.sender.workflow = {
            "Name": "app/hello", "Kind": "Stateful",
            "Properties": {"FlowState": "Disabled", "Health": {"State": "Unhealthy"},
                           "Files": {"connections.json": {"secret": "must-not-leak"}}}}
        shown = self.show()
        self.assertEqual("Disabled", shown["state"])
        self.assertEqual("Unhealthy", shown["health"])
        self.assertNotIn("must-not-leak", json.dumps(shown))

    def test_missing_optional_state_and_health_are_not_invented(self):
        self.sender.workflow = {"name": "hello", "kind": "Stateful"}
        shown = self.show()
        self.assertIsNone(shown["state"])
        self.assertIsNone(shown["health"])

    def test_list_has_stable_shape_sorted_names_and_table_columns(self):
        self.sender.inventory = {"Value": [metadata("z", disabled=True), metadata("a")], "NextLink": None,
                                 "irrelevant": "do-not-echo"}
        result = _workflow_discovery.list_workflows(self.client)
        self.assertEqual({"value", "nextContinuationToken"}, set(result))
        self.assertEqual(["a", "z"], [item["name"] for item in result["value"]])
        self.assertEqual({"name", "kind", "state", "health"}, set(result["value"][0]))
        table = _workflow_discovery.workflow_list_table_format(result)
        self.assertEqual({"Name": "z", "Kind": "Stateful", "State": "Disabled", "Health": "Healthy"},
                         table[1])
        self.assertEqual("hello", _workflow_discovery.workflow_show_table_format(self.show())[0]["Name"])

    def test_list_collects_server_pages_before_cli_offset_paging(self):
        def inventory(query):
            if "$skiptoken" in query:
                self.assertEqual(["service-token"], query["$skiptoken"])
                return {"value": [metadata("b")], "nextLink": None}
            return {"value": [metadata("c"), metadata("a")],
                    "nextLink": "https://untrusted.invalid/workflows?%24skiptoken=service-token"}
        self.sender.inventory = inventory
        first = _workflow_discovery.list_workflows(self.client, max_items=2)
        self.assertEqual(["a", "b"], [item["name"] for item in first["value"]])
        second = _workflow_discovery.list_workflows(
            self.client, max_items=2, next_token=first["nextContinuationToken"])
        self.assertEqual(["c"], [item["name"] for item in second["value"]])
        self.assertIsNone(second["nextContinuationToken"])
        self.assertEqual(4, len(self.sender.requests))
        self.assertTrue(all(urlsplit(url).netloc == "localhost:17071" for _, url, _ in self.sender.requests))

    def test_inventory_page_limit_blocks_unique_continuations_despite_small_cli_page(self):
        self.assertEqual(100, _workflow_discovery.MAX_SERVICE_PAGES)
        self.sender.inventory = lambda _query: {
            "value": [], "nextContinuationToken": "page-{}".format(len(self.sender.requests))}
        with self.assertRaisesRegex(ClientRequestError, "page limit"):
            _workflow_discovery.list_workflows(self.client, max_items=1)
        self.assertEqual(100, len(self.sender.requests))

    def test_conflicting_or_invalid_service_continuations_fail_before_followup(self):
        variants = (
            {"nextContinuationToken": "private-first",
             "nextLink": "https://untrusted.invalid/workflows?$skiptoken=private-second"},
            {"nextContinuationToken": True,
             "nextLink": "https://untrusted.invalid/workflows?$skiptoken=private-second"},
            {"nextContinuationToken": [],
             "nextLink": "https://untrusted.invalid/workflows?$skiptoken=private-second"},
            {"nextLink": "https://untrusted.invalid/workflows?$skiptoken=private-first&skipToken=private-second"},
            {"nextLink": "https://untrusted.invalid/workflows?$skiptoken=private-first&$skiptoken=private-first"},
            {"nextLink": "https://untrusted.invalid/workflows?$skiptoken=private-first&$skiptoken="},
            {"nextLink": "https://untrusted.invalid/workflows?$skiptoken=private-first&skipToken="},
            {"nextLink": "https://untrusted.invalid/workflows?$skiptoken="},
        )
        for client in (self.client, _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=self.sender)):
            for fields in variants:
                with self.subTest(cloud=not client.is_local, fields=fields):
                    self.sender.requests.clear()
                    self.sender.inventory = {"value": [metadata()], **fields}
                    with self.assertRaises(ClientRequestError) as caught:
                        _workflow_discovery.list_workflows(client, max_items=1)
                    self.assertNotIn("private-first", str(caught.exception))
                    self.assertNotIn("private-second", str(caught.exception))
                    self.assertEqual(1, len(self.sender.requests))

    def test_matching_service_continuations_collect_complete_selected_target_inventory(self):
        links = (
            "https://untrusted.invalid/workflows?$skiptoken=service%2Ftoken%2B1",
            "https://untrusted.invalid/workflows?skipToken=service%2Ftoken%2B1",
            "https://untrusted.invalid/workflows?$skiptoken=service%2Ftoken%2B1&skipToken=service%2Ftoken%2B1",
        )
        for client in (self.client, _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=self.sender)):
            for link in links:
                for envelope_token in (None, "", "service/token+1"):
                    with self.subTest(cloud=not client.is_local, link=link, envelope_token=envelope_token):
                        self.sender.requests.clear()

                        def inventory(query):
                            if "$skiptoken" in query:
                                self.assertEqual(["service/token+1"], query["$skiptoken"])
                                return {"value": [metadata("a")]}
                            return {"value": [metadata("b")], "nextLink": link,
                                    "nextContinuationToken": envelope_token}

                        self.sender.inventory = inventory
                        result = _workflow_discovery.list_workflows(client)
                        self.assertEqual(["a", "b"], [item["name"] for item in result["value"]])
                        self.assertIsNone(result["nextContinuationToken"])
                        self.assertEqual(2, len(self.sender.requests))
                        expected_url = "{}{}/runtime/webhooks/workflow/api/management/workflows".format(
                            client.site_resource_id, "" if client.is_local else "/hostruntime")
                        self.assertTrue(all(url.partition("?")[0] == expected_url
                                            for _, url, _ in self.sender.requests))

    def test_invalid_json_offsets_fail_before_inventory_requests(self):
        samples = (
            '{"offset":1e999}', '{"offset":NaN}', '{"offset":Infinity}',
            '{"offset":true}', '{"offset":1.0}', '{"offset":1.5}',
            '{"offset":"private-token"}', '{"offset":null}', '{"offset":0,"offset":1}',
            '{"offset":' + "[" * 1100 + "0" + "]" * 1100 + "}",
        )
        for raw in samples:
            with self.subTest(raw=raw):
                token = base64.urlsafe_b64encode(raw.encode()).decode()
                with self.assertRaises(InvalidArgumentValueError) as caught:
                    _workflow_discovery.list_workflows(self.client, next_token=token)
                self.assertNotIn("private-token", str(caught.exception))
                self.assertEqual([], self.sender.requests)
        with patch("azext_logicapp._paging.strict_json_loads", side_effect=RecursionError("private-token")):
            with self.assertRaises(InvalidArgumentValueError) as caught:
                _workflow_discovery.list_workflows(self.client, next_token="e30=")
        self.assertNotIn("private-token", str(caught.exception))
        self.assertEqual([], self.sender.requests)

    def test_non_alphabet_continuations_fail_before_json_or_inventory_reads(self):
        valid = _paging.encode_token(1)
        for invalid in ("!", "?", "#", " ", "\n", "\r", "\t", "\0", "\x7f"):
            for token in (invalid + valid, valid + invalid, valid[:3] + invalid + valid[3:]):
                with self.subTest(token=token):
                    with patch.object(_paging, "strict_json_loads") as decoder:
                        with self.assertRaises(InvalidArgumentValueError):
                            _workflow_discovery.list_workflows(self.client, next_token=token)
                    decoder.assert_not_called()
                    self.assertEqual([], self.sender.requests)

    def test_valid_base64url_offsets_and_paging_round_trip(self):
        for offset in (0, 1, 2, 15, 16, 12345, 10 ** 40):
            with self.subTest(offset=offset):
                self.assertEqual(offset, _paging.decode_token(_paging.encode_token(offset)))
        values, first = _paging.slice_items(["a", "b", "c"], max_items=1)
        self.assertEqual(["a"], values)
        values, second = _paging.slice_items(["a", "b", "c"], first, max_items=1)
        self.assertEqual(["b"], values)
        values, last = _paging.slice_items(["a", "b", "c"], second, max_items=1)
        self.assertEqual(["c"], values)
        self.assertIsNone(last)

    def test_exact_inventory_page_limit_completes_without_partial_failure(self):
        self.sender.inventory = lambda _query: (
            {"value": [metadata()]} if len(self.sender.requests) == 100 else
            {"value": [], "nextContinuationToken": "page-{}".format(len(self.sender.requests))})
        result = _workflow_discovery.list_workflows(self.client)
        self.assertEqual(["hello"], [item["name"] for item in result["value"]])
        self.assertEqual(100, len(self.sender.requests))

    def test_oversized_inventory_page_is_rejected_before_metadata_conversion(self):
        self.assertEqual(10000, _workflow_discovery.MAX_INVENTORY_ITEMS)
        self.sender.inventory = [{}] * 10001
        with patch.object(_workflow_discovery, "workflow_metadata", side_effect=AssertionError("No oversized conversion")):
            with self.assertRaisesRegex(ClientRequestError, "item limit"):
                _workflow_discovery.list_workflows(self.client, max_items=1)
        self.assertEqual(1, len(self.sender.requests))

    def test_exact_inventory_item_limit_preserves_sorted_cli_paging(self):
        self.sender.inventory = [metadata("wf{:05d}".format(index)) for index in reversed(range(10000))]
        result = _workflow_discovery.list_workflows(self.client, max_items=1)
        self.assertEqual(["wf00000"], [item["name"] for item in result["value"]])
        self.assertIsNotNone(result["nextContinuationToken"])
        self.assertEqual(1, len(self.sender.requests))

    def test_inventory_item_limit_applies_across_pages(self):
        self.sender.inventory = lambda _query: (
            {"value": [metadata("wf{:05d}".format(index)) for index in range(9999)],
             "nextContinuationToken": "next"} if len(self.sender.requests) == 1 else
            {"value": [metadata("next-a"), metadata("next-b")]})
        with patch.object(_workflow_discovery, "workflow_metadata",
                          wraps=_workflow_discovery.workflow_metadata) as convert:
            with self.assertRaisesRegex(ClientRequestError, "item limit"):
                _workflow_discovery.list_workflows(self.client)
        self.assertEqual(9999, convert.call_count)
        self.assertEqual(2, len(self.sender.requests))

    def test_empty_inventory_is_valid_but_null_or_bad_envelopes_are_not(self):
        self.sender.inventory = []
        self.assertEqual({"value": [], "nextContinuationToken": None},
                         _workflow_discovery.list_workflows(self.client))
        for payload in (None, {}, {"value": None}, {"value": {}}, [None], {"value": [], "nextLink": 123},
                        {"value": [], "nextLink": "https://untrusted.invalid/next"},
                        {"value": [], "nextContinuationToken": True}):
            with self.subTest(payload=payload):
                self.sender.inventory = lambda _, payload=payload: payload
                with self.assertRaises(ClientRequestError):
                    _workflow_discovery.list_workflows(self.client)

    def test_repeated_service_tokens_and_duplicate_names_fail(self):
        for payload in ({"value": [], "nextContinuationToken": "repeat"},
                        [metadata(), metadata()]):
            with self.subTest(payload=payload):
                self.sender.inventory = payload
                with self.assertRaises(ClientRequestError):
                    _workflow_discovery.list_workflows(self.client)

    def test_malformed_continuation_url_is_sanitized_and_never_followed(self):
        for link in ("http://[bad/?$skiptoken=private-token",
                     "http://[::1/?$skiptoken=private-token"):
            with self.subTest(link=link):
                self.sender.requests.clear()
                self.sender.inventory = {"value": [], "nextLink": link}
                with self.assertRaisesRegex(ClientRequestError, "malformed workflow nextLink") as caught:
                    _workflow_discovery.list_workflows(self.client)
                self.assertNotIn("private-token", str(caught.exception))
                self.assertTrue(caught.exception.__suppress_context__)
                self.assertEqual(1, len(self.sender.requests))
                self.assertFalse(self.path.parent.exists())

    def test_case_duplicate_collection_fields_fail_before_followup_requests(self):
        for field, value in (
                ("value", []), ("nextLink", None), ("nextContinuationToken", "private-token")):
            with self.subTest(field=field):
                self.sender.requests.clear()
                self.sender.inventory = {"value": [], field: value, field.upper(): value}
                with self.assertRaisesRegex(ClientRequestError, "ambiguous workflow fields"):
                    _workflow_discovery.list_workflows(self.client)
                self.assertEqual(1, len(self.sender.requests))

    def test_invalid_paging_input_fails_before_request(self):
        for kwargs in ({"max_items": 0}, {"max_items": -1}, {"next_token": "bad-token"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(InvalidArgumentValueError):
                    _workflow_discovery.list_workflows(self.client, **kwargs)
        self.assertEqual([], self.sender.requests)

    def test_metadata_shape_errors_fail_explicitly(self):
        for payload in (None, [], {}, {"name": "hello", "kind": "Agentic"},
                        metadata("app/"), metadata("bad name"),
                        {"name": "wrong", "kind": "Stateful"}, metadata(disabled="false"),
                        dict(metadata(), health=[]), dict(metadata(), flowState="Disabled"),
                        dict(metadata(), properties=[]), dict(metadata(), flowState=123)):
            with self.subTest(payload=payload):
                self.sender.workflow = payload
                with self.assertRaises(ClientRequestError):
                    self.show()

    def test_case_duplicate_metadata_fields_fail_even_when_values_agree(self):
        for field, first, second in (
                ("name", "hello", "private-name"), ("kind", "Stateful", "Stateless"),
                ("isDisabled", False, True), ("flowState", "Enabled", "Disabled"),
                ("properties", {"isDisabled": False}, {"isDisabled": True}),
                ("health", {"state": "Healthy"}, {"state": "private-health"})):
            for same_value in (False, True):
                for reverse in (False, True):
                    with self.subTest(field=field, same_value=same_value, reverse=reverse):
                        payload = metadata()
                        payload[field] = first
                        payload[field.upper()] = first if same_value else second
                        self.sender.workflow = dict(reversed(list(payload.items()))) if reverse else payload
                        self.sender.requests.clear()
                        with self.assertRaisesRegex(ClientRequestError, "ambiguous workflow fields") as caught:
                            self.show()
                        self.assertNotIn("private-", str(caught.exception))
                        self.assertEqual(1, len(self.sender.requests))
                        self.assertFalse(self.path.parent.exists())
        for payload in (
                {"name": "hello", "kind": "Stateful", "properties": {"isDisabled": False, "ISDISABLED": False}},
                dict(metadata(), health={"state": "Healthy", "STATE": "Healthy"})):
            with self.subTest(payload=payload), self.assertRaises(ClientRequestError):
                _workflow_discovery.workflow_metadata(payload)

    def test_ambiguous_metadata_blocks_mutations_and_state_before_confirmation(self):
        self.sender.workflow = dict(metadata(), KIND="Stateless")
        file = Path(self.folder.name) / "candidate.json"
        file.write_text(json.dumps(self.sender.document), encoding="utf-8")
        with patch.object(_workflow_mutation, "user_confirmation") as mutation_confirmation, \
                patch.object(self.client, "vfs_client") as vfs_factory:
            for operation in (
                    lambda: _workflow_mutation.set_workflow(
                        self.client, "hello", str(file), yes=True, allow_non_atomic=True),
                    lambda: _workflow_mutation.delete_workflow(
                        self.client, "hello", yes=True, allow_non_atomic=True)):
                with self.assertRaisesRegex(ClientRequestError, "ambiguous workflow fields"):
                    operation()
            mutation_confirmation.assert_not_called()
            vfs_factory.assert_not_called()
        cloud = _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=self.sender)
        response = SimpleNamespace(status_code=200, json=lambda: copy.deepcopy(self.sender.workflow))
        with patch.object(_workflow_state, "_metadata_response", return_value=response), \
                patch.object(_workflow_state, "_settings") as settings, \
                patch.object(_workflow_state, "user_confirmation") as state_confirmation:
            with self.assertRaises(ClientRequestError):
                _workflow_state.set_workflow_state(
                    cloud, "hello", "Disabled", yes=True, allow_non_atomic=True)
            settings.assert_not_called()
            state_confirmation.assert_not_called()
        self.assertTrue(all(method == "GET" for method, _, _ in self.sender.requests))

    def test_missing_malformed_unsupported_or_changed_file_never_writes(self):
        payloads = (None, [], {}, {"kind": "Stateful"}, {"kind": "Agentic", "definition": {}},
                    {"kind": "Stateful", "definition": {}},
                    {"kind": "Stateless", "definition": _workflow.workflow_json("Stateless")["definition"]},
                    {"kind": "Stateful", "definition": {"triggers": [], "actions": {}}},
                    {"kind": "Stateful", "definition": {"triggers": {"manual": {}}, "actions": []}})
        for payload in payloads:
            with self.subTest(payload=payload):
                self.sender.document = payload
                with self.assertRaises(ClientRequestError):
                    self.export()
                self.assertFalse(self.path.exists())
                self.assertFalse(self.path.parent.exists())

    def test_not_found_and_auth_errors_propagate_without_file(self):
        for suffix in ("/workflows/hello", "/hello/workflow.json"):
            for status in (404, 401, 403):
                with self.subTest(suffix=suffix, status=status):
                    self.sender.fail_suffix = suffix
                    self.sender.failure = HTTPError(
                        "service failure", response=SimpleNamespace(status_code=status))
                    with self.assertRaises(ResourceNotFoundError if status == 404 else UnauthorizedError):
                        self.export()
                    self.assertFalse(self.path.exists())

    def test_unavailable_runtime_and_invalid_json_are_clear_errors(self):
        for failure in (RequestsConnectionError("offline"),):
            self.sender.fail_suffix = "/hello/workflow.json"
            self.sender.failure = failure
            with self.assertRaises(ClientRequestError):
                self.export()
        with patch.object(self.client, "_sender", return_value=SimpleNamespace(
                content=b"bad-json", json=lambda: json.loads("bad-json"))):
            with self.assertRaisesRegex(ClientRequestError, "invalid JSON"):
                self.show()

    def test_export_preserves_stateless_file_configuration_expressions_and_literals(self):
        self.sender.workflow = metadata(kind="Stateless")
        self.sender.document = _workflow.workflow_json("Stateless")
        self.sender.document["runtimeConfiguration"] = {"statelessRunMode": "Debug", "operationOptions": "WithStatelessRunHistory"}
        self.sender.document["definition"]["actions"]["Compose_greeting"]["inputs"]["literal"] = "authored-sensitive-literal"
        result = self.export()
        self.assertEqual("Stateless", result["workflowKind"])
        self.assertEqual("created", result["action"])
        self.assertEqual(self.path.stat().st_size, result["bytesWritten"])
        self.assertEqual(self.sender.document, json.loads(self.path.read_text(encoding="utf-8")))
        self.assertNotIn("authored-sensitive-literal", json.dumps(result))
        self.assertTrue(_workflow.static_validate(self.folder.name, workflow="hello")["valid"])
        self.assertEqual([self.path], list(self.path.parent.iterdir()))
        self.assertFalse((Path(self.folder.name) / "local.settings.json").exists())
        self.assertFalse((Path(self.folder.name) / "connections.json").exists())

    def test_nonforce_preserves_existing_file_and_makes_no_request(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"existing")
        with self.assertRaises(ValidationError):
            self.export()
        self.assertEqual(b"existing", self.path.read_bytes())
        self.assertEqual([], self.sender.requests)

    def test_force_atomically_replaces_existing_file(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"existing")
        result = self.export(force=True)
        self.assertEqual("updated", result["action"])
        self.assertEqual(self.sender.document, json.loads(self.path.read_text(encoding="utf-8")))
        self.assertEqual([self.path], list(self.path.parent.iterdir()))

    def test_write_failure_preserves_existing_file_and_cleans_temporary(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"existing")
        with patch.object(_workflow_discovery.os, "replace", side_effect=OSError("write failed")):
            with self.assertRaises(FileOperationError):
                self.export(force=True)
        self.assertEqual(b"existing", self.path.read_bytes())
        self.assertEqual([self.path], list(self.path.parent.iterdir()))

    def test_nonforce_race_does_not_clobber_competing_file(self):
        def competing_writer(source, target):
            Path(target).write_bytes(b"competing")
            raise FileExistsError("already exists")
        with patch.object(_workflow_discovery.os, "link", side_effect=competing_writer):
            with self.assertRaises(ValidationError):
                self.export()
        self.assertEqual(b"competing", self.path.read_bytes())
        self.assertEqual([self.path], list(self.path.parent.iterdir()))

    def test_nan_response_is_rejected_without_output(self):
        self.sender.document["definition"]["outputs"]["invalid"] = float("nan")
        with self.assertRaises(ClientRequestError):
            self.show()
        with self.assertRaises(ClientRequestError):
            self.export()
        self.assertFalse(self.path.parent.exists())

    def test_force_preserves_existing_file_when_service_definition_is_invalid(self):
        self.path.parent.mkdir()
        self.path.write_bytes(b"existing")
        self.sender.document = {}
        with self.assertRaises(ClientRequestError):
            self.export(force=True)
        self.assertEqual(b"existing", self.path.read_bytes())
        self.assertEqual([self.path], list(self.path.parent.iterdir()))

    def test_incomplete_temporary_write_is_not_published(self):
        with patch.object(_workflow_discovery.os, "fsync", side_effect=OSError("flush failed")):
            with self.assertRaises(FileOperationError):
                self.export()
        self.assertFalse(self.path.exists())
        self.assertEqual([], list(self.path.parent.iterdir()))

    def test_unsafe_or_missing_destinations_are_rejected(self):
        root_file = os.path.join(Path(self.folder.name).anchor, "workflow.json")
        directory = Path(self.folder.name) / "directory.json"
        directory.mkdir()
        for path in (None, "", " ", root_file, str(directory), str(self.path.with_suffix(".zip"))):
            with self.subTest(path=path):
                with self.assertRaises((InvalidArgumentValueError, ValidationError)):
                    _workflow_discovery.export_workflow(self.client, "hello", path, force=True)
        self.assertEqual([], self.sender.requests)
        with patch.object(_workflow_discovery.os.path, "islink", return_value=True):
            with self.assertRaises(ValidationError):
                self.export(force=True)

    def test_invalid_workflow_name_never_requests_service(self):
        for workflow in ("../hello", "bad/name", ".", "bad\\name"):
            with self.subTest(workflow=workflow):
                with self.assertRaises(InvalidArgumentValueError):
                    _workflow_discovery.show_workflow(self.client, workflow)
        self.assertEqual([], self.sender.requests)

    def test_target_resolution_local_cloud_named_and_active_contexts(self):
        contexts = {
            "local": {"target": {"kind": "local", "port": 17071, "path": self.folder.name}},
            "cloud": {"target": {"kind": "cloud", "resourceGroup": "rg", "logicAppName": "app"}}}
        for target, kwargs in (("local", {"local": True, "port": 17071, "host_key": "key"}),
                               ("cloud", {"resource_group_name": "rg", "name": "app"}),
                               ("local", {"context": "local", "host_key": "key"}),
                               ("cloud", {"context": "cloud"}), ("local", {}),
                               ("local", {"host_key": "key"})):
            with self.subTest(kwargs=kwargs), \
                    patch.object(custom, "get_context", side_effect=lambda name: (contexts[name or "local"], {})), \
                    patch.object(_runtime_client, "_site_resource_id", return_value=SITE), \
                    patch.object(_runtime_client, "send_raw_request", side_effect=self.sender):
                self.sender.requests.clear()
                result = custom.workflow_show(self.cmd, "hello", **kwargs)
                self.assertEqual("hello", result["name"])
                path = urlsplit(self.sender.requests[0][1]).path
                self.assertEqual(target == "cloud", path.startswith(SITE))
                if kwargs.get("host_key"):
                    self.assertIn("x-functions-key=key", self.sender.requests[-1][2]["headers"])

    def test_all_commands_reject_conflicting_targets_and_ignored_local_flags(self):
        cases = ({"local": True, "name": "app"},
                 {"context": "dev", "local": True}, {"context": "dev", "name": "app"},
                 {"context": "dev", "port": 17071},
                 {"resource_group_name": "rg", "name": "app", "port": 17071},
                 {"resource_group_name": "rg", "name": "app", "host_key": "key"},
                 {"resource_group_name": "rg"}, {"port": 17071})
        for function, required in ((custom.workflow_list, {}), (custom.workflow_show, {"workflow": "hello"}),
                                   (custom.workflow_export, {"workflow": "hello", "output_path": str(self.path)})):
            for kwargs in cases:
                with self.subTest(command=function.__name__, kwargs=kwargs):
                    with self.assertRaises((MutuallyExclusiveArgumentError, RequiredArgumentMissingError)):
                        function(self.cmd, **required, **kwargs)
        cloud_context = {"target": {"kind": "cloud", "resourceGroup": "rg", "logicAppName": "app"}}
        with patch.object(custom, "get_context", return_value=(cloud_context, {})):
            with self.assertRaises(RequiredArgumentMissingError):
                custom.workflow_show(self.cmd, "hello", context="cloud", host_key="key")
        with patch.object(custom, "get_context", return_value=(None, {})):
            with self.assertRaises(RequiredArgumentMissingError):
                custom.workflow_list(self.cmd)

    def test_new_commands_and_flags_are_registered_without_path_mode(self):
        for suffix in ("list", "show", "export"):
            command = "logicapp workflow " + suffix
            cli = get_default_cli()
            cli.invocation = SimpleNamespace(data={"command_string": command})
            loader = COMMAND_LOADER_CLS(cli_ctx=cli)
            table = loader.load_command_table(args=[])
            self.assertIn(command, table)
            loader.load_arguments(args=[])
            args = loader.argument_registry.arguments[command]
            self.assertTrue({"resource_group_name", "name", "local", "port", "host_key", "context"} <= set(args))
            self.assertNotIn("path", args)
            if suffix == "list":
                self.assertEqual(["--next-token", "--continuation-token"], args["next_token"].settings["options_list"])
            else:
                self.assertTrue(args["workflow"].settings["required"])
            if suffix == "export":
                self.assertTrue(args["output_path"].settings["required"])
                self.assertEqual(["--force"], args["force"].settings["options_list"])


if __name__ == "__main__":
    unittest.main()
