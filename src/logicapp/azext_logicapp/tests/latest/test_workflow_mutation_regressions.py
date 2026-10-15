# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import (
    ClientRequestError, FileOperationError, HTTPError, InvalidArgumentValueError,
    MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError,
    UnauthorizedError, ValidationError)
from requests import Response
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout

from azext_logicapp import COMMAND_LOADER_CLS, _runtime_client, _workflow, _workflow_discovery, _workflow_mutation, custom

SITE = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"


def http_error(status):
    response = Response()
    response.status_code = status
    return HTTPError("service failed", response=response)


class VfsTransport:
    """Models observed VFS behavior, including its missing-file conditional PUT defect."""

    def __init__(self):
        self.document = _workflow.workflow_json("Stateful")
        self.content = json.dumps(self.document, indent=2).encode()
        self.revision = 1
        self.calls = []
        self.before_put = None
        self.before_delete = None
        self.after_put = None
        self.after_delete = None
        self.reject_validation = None
        self.validation_payload = None
        self.validation_status = 200
        self.validation_headers = {}
        self.metadata_payload = None
        self.omit_read_etag = False
        self.omit_write_etag = False
        self.put_status = None
        self.get_failure = None

    @property
    def etag(self):
        return '"r{}"'.format(self.revision)

    def change(self, content):
        self.content = content
        self.revision += 1

    def __call__(self, cli_ctx, method, url, **kwargs):
        if hasattr(kwargs.get("body"), "read"):
            kwargs["body"] = kwargs["body"].read()
        self.calls.append((method, url, kwargs))
        path = urlsplit(url).path
        headers = {}
        status = 200
        body = b""
        if path.endswith("/workflows/hello/validate"):
            if self.reject_validation:
                raise self.reject_validation
            status = self.validation_status
            headers = self.validation_headers
            body = (self.validation_payload if isinstance(self.validation_payload, bytes) else
                    json.dumps(self.validation_payload).encode() if self.validation_payload is not None else b"")
        elif path.endswith("/workflows/hello"):
            if self.content is None:
                raise http_error(404)
            body = json.dumps({"name": "hello", "kind": self.document["kind"],
                               "isDisabled": False, "health": {"state": "Healthy"}}).encode()
            if self.metadata_payload is not None:
                body = self.metadata_payload
        elif path.endswith("/hello/workflow.json"):
            if method == "GET":
                if self.get_failure:
                    raise self.get_failure
                if self.content is None:
                    raise http_error(404)
                body = self.content
                if not self.omit_read_etag:
                    headers["eTaG"] = self.etag
            elif method == "PUT":
                hook, self.before_put = self.before_put, None
                if hook:
                    hook()
                supplied = next(header.split("=", 1)[1] for header in kwargs["headers"]
                                if header.startswith("If-Match="))
                existed = self.content is not None
                if existed and supplied not in (self.etag, "*"):
                    raise http_error(412)
                self.change(kwargs["body"])
                status = self.put_status if self.put_status is not None else (204 if existed else 201)
                if not self.omit_write_etag:
                    headers["ETag"] = self.etag
                if self.after_put:
                    self.after_put()
            elif method == "DELETE":
                hook, self.before_delete = self.before_delete, None
                if hook:
                    hook()
                if self.content is None:
                    raise http_error(404)
                supplied = next(header.split("=", 1)[1] for header in kwargs["headers"]
                                if header.startswith("If-Match="))
                if supplied not in (self.etag, "*"):
                    raise http_error(412)
                self.change(None)
                if self.after_delete:
                    self.after_delete()
            else:
                raise AssertionError(method)
        else:
            raise AssertionError(url)
        return SimpleNamespace(content=body, json=lambda: json.loads(body), headers=headers, status_code=status)


class WorkflowMutationRegressions(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.file = Path(self.folder.name) / "workflow.json"
        self.transport = VfsTransport()
        self.before = self.transport.content
        self.candidate = copy.deepcopy(self.transport.document)
        self.candidate["definition"]["actions"]["Compose_greeting"]["inputs"]["greeting"] = "changed"
        self.write_input(self.candidate)
        self.cmd = SimpleNamespace(cli_ctx=get_default_cli())
        self.client = _runtime_client.SiteRuntimeClient(
            self.cmd, "http://localhost:17071", sender=self.transport, host_key="local-key")
        self.confirmation = patch.object(_workflow_mutation, "user_confirmation")
        self.confirm = self.confirmation.start()
        self.addCleanup(self.confirmation.stop)

    def write_input(self, document):
        self.file.write_text(json.dumps(document), encoding="utf-8")

    def update(self, **kwargs):
        kwargs.setdefault("allow_non_atomic", True)
        return _workflow_mutation.set_workflow(self.client, "hello", str(self.file), **kwargs)

    def delete(self, **kwargs):
        kwargs.setdefault("allow_non_atomic", True)
        return _workflow_mutation.delete_workflow(self.client, "hello", **kwargs)

    def mutations(self):
        return [call for call in self.transport.calls if call[0] in ("PUT", "DELETE")]

    def test_acknowledgement_is_required_before_any_request(self):
        for operation in (self.update, self.delete):
            with self.subTest(operation=operation.__name__):
                with self.assertRaisesRegex(InvalidArgumentValueError, "--allow-non-atomic"):
                    operation(allow_non_atomic=False, yes=True)
        self.assertEqual([], self.transport.calls)

    def test_duplicate_authored_workflow_members_fail_before_requests_or_confirmation(self):
        definition = json.dumps(self.candidate["definition"])
        samples = (
            '{"kind":"Stateful","kind":"Stateful","definition":' + definition + '}',
            '{"kind":"Stateful","definition":' + definition + ',"definition":' + definition + '}',
            '{"kind":"Stateful","definition":' + definition.replace('"actions":', '"actions":{},"actions":', 1) + '}',
        )
        for raw in samples:
            with self.subTest(raw=raw):
                self.file.write_text(raw, encoding="utf-8")
                with self.assertRaisesRegex(InvalidArgumentValueError, "valid JSON"):
                    self.update(yes=True)
                self.assertEqual([], self.transport.calls)
                self.assertEqual(self.before, self.transport.content)
                self.assertEqual(raw, self.file.read_text())
        self.confirm.assert_not_called()

    def test_duplicate_remote_workflow_members_block_update_and_delete(self):
        raw = self.before.replace(b'"kind": "Stateful"', b'"kind": "Stateful", "kind": "Stateful"', 1)
        self.assertNotEqual(raw, self.before)
        for operation in (self.update, self.delete):
            with self.subTest(operation=operation.__name__):
                self.transport.content = raw
                with self.assertRaisesRegex(ClientRequestError, "invalid JSON"):
                    operation(yes=True)
                self.assertEqual([], self.mutations())
                self.assertEqual(raw, self.transport.content)
        self.confirm.assert_not_called()

    def test_update_validates_full_file_then_conditionally_writes_and_reads_back(self):
        result = self.update(yes=True, if_match="r1")
        self.assertEqual({"workflow": "hello", "workflowKind": "Stateful", "action": "updated",
                          "etag": '"r2"', "verification": "fileReadback"}, result)
        self.assertEqual(self.candidate, json.loads(self.transport.content))
        self.assertEqual(1, len(self.mutations()))
        self.assertIn('If-Match="r1"', self.mutations()[0][2]["headers"])
        validation = [call for call in self.transport.calls if call[0] == "POST"]
        self.assertEqual(1, len(validation))
        self.assertEqual({"properties": {"definition": self.candidate["definition"], "kind": "Stateful"}},
                         json.loads(validation[0][2]["body"]))
        self.confirm.assert_called_once()
        self.assertTrue(self.confirm.call_args.args[1])
        self.assertEqual(self.candidate, json.loads(self.file.read_text()))

    def test_type_only_workflow_edits_are_published_instead_of_reported_unchanged(self):
        for old, new in ((True, 1), (1, 1.0), (1, True), (1.0, 1)):
            with self.subTest(old=old, new=new):
                self.transport = VfsTransport()
                self.client = _runtime_client.SiteRuntimeClient(
                    self.cmd, "http://localhost:17071", sender=self.transport)
                original = copy.deepcopy(self.transport.document)
                original["definition"]["actions"]["Compose_greeting"]["inputs"]["greeting"] = old
                self.transport.content = json.dumps(original).encode()
                candidate = copy.deepcopy(original)
                candidate["definition"]["actions"]["Compose_greeting"]["inputs"]["greeting"] = new
                self.write_input(candidate)
                authored = self.file.read_bytes()
                result = self.update(yes=True)
                self.assertEqual("updated", result["action"])
                self.assertEqual(1, len(self.mutations()))
                stored = json.loads(self.transport.content)
                self.assertIs(type(new), type(stored["definition"]["actions"]
                                              ["Compose_greeting"]["inputs"]["greeting"]))
                self.assertEqual(authored, self.file.read_bytes())
                self.assertEqual(self.mutations()[0][2]["body"], self.transport.content)

    def test_local_raw_get_put_delete_keep_key_in_headers_and_skip_azure_auth(self):
        self.update()
        self.delete()
        for method, url, kwargs in self.transport.calls:
            self.assertEqual("localhost:17071", urlsplit(url).netloc)
            self.assertNotIn("local-key", url)
            self.assertIn("x-functions-key=local-key", kwargs["headers"])
            self.assertTrue(kwargs["skip_authorization_header"])
            if method in ("PUT", "DELETE"):
                self.assertEqual("/admin/vfs/hello/workflow.json", urlsplit(url).path)
                self.assertNotIn("If-Match=*", kwargs["headers"])

    def test_cloud_operations_keep_arm_authorization_and_target_one_file(self):
        self.client = _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=self.transport)
        self.update()
        self.delete()
        for _, url, kwargs in self.transport.calls:
            self.assertTrue(url.startswith(SITE + "/hostruntime/"))
            self.assertNotIn("skip_authorization_header", kwargs)
            self.assertFalse(any(header.startswith("x-functions-key") for header in kwargs["headers"]))
        self.assertTrue(all(urlsplit(url).path == SITE + "/hostruntime/admin/vfs/hello/workflow.json"
                            for _, url, _ in self.mutations()))

    def test_real_azure_cli_sender_preserves_raw_vfs_write_bytes(self):
        content = b'{\n  "literal": "authored\\u00e9",\n  "kind": "Stateful"\n}\n'
        captured = []

        def send(_session, request, **_kwargs):
            captured.append((request.body.read(), request.headers))
            response = Response()
            response.status_code = 204
            response._content = b""
            response.headers["ETag"] = '"written"'
            return response
        client = _runtime_client.SiteRuntimeClient(self.cmd, "http://localhost:17071", host_key="local-key")
        with patch.dict(self.cmd.cli_ctx.data, {"command": "logicapp workflow set"}), \
                patch("requests.Session.send", new=send):
            result = client.vfs_client().put_raw("hello/workflow.json", content, if_match='"before"')
        self.assertEqual(content, captured[0][0])
        self.assertEqual('"before"', captured[0][1]["If-Match"])
        self.assertEqual("local-key", captured[0][1]["x-functions-key"])
        self.assertNotIn("Authorization", captured[0][1])
        self.assertEqual(204, result["statusCode"])

    def test_delete_removes_only_file_and_verifies_404(self):
        result = self.delete(yes=True, if_match='"r1"')
        self.assertEqual({"workflow": "hello", "workflowKind": "Stateful", "action": "deleted",
                          "etag": None, "verification": "fileNotFound"}, result)
        self.assertIsNone(self.transport.content)
        self.assertEqual(1, len(self.mutations()))
        self.assertNotIn("recursive", self.mutations()[0][1])
        self.assertIn('If-Match="r1"', self.mutations()[0][2]["headers"])

    def test_unchanged_input_is_validated_but_not_written_or_prompted(self):
        self.write_input(self.transport.document)
        result = self.update()
        self.assertEqual("unchanged", result["action"])
        self.assertEqual('"r1"', result["etag"])
        self.assertEqual([], self.mutations())
        self.confirm.assert_not_called()

    def test_invalid_full_file_rejects_before_target_requests(self):
        cases = (None, [], {}, self.candidate["definition"],
                 {"kind": "Agentic", "definition": self.candidate["definition"]},
                 {"kind": "Stateful", "definition": {"triggers": [], "actions": {}}},
                 {"kind": "Stateful", "definition": {"triggers": {"manual": None}, "actions": {}}},
                 {"kind": "Stateful", "definition": {"triggers": {"manual": {}}, "actions": []}})
        for document in cases:
            with self.subTest(document=document):
                self.write_input(document)
                with self.assertRaises((InvalidArgumentValueError, ValidationError)):
                    self.update()
        self.candidate["definition"]["outputs"]["invalid"] = float("nan")
        self.write_input(self.candidate)
        with self.assertRaises(InvalidArgumentValueError):
            self.update()
        self.assertEqual([], self.transport.calls)

    def test_invalid_json_missing_file_and_non_object_actions_have_clear_errors(self):
        self.file.write_bytes(b"not-json")
        with self.assertRaises(InvalidArgumentValueError):
            self.update()
        self.file.unlink()
        with self.assertRaises(FileOperationError):
            self.update()
        document = copy.deepcopy(self.candidate)
        del document["definition"]["actions"]
        self.write_input(document)
        with self.assertRaises(ValidationError) as raised:
            self.update()
        self.assertEqual("workflow.actions.invalid", json.loads(str(raised.exception))["findings"][0]["rule"])
        self.assertEqual([], self.transport.calls)

    def test_kind_conversion_is_not_an_implicit_update(self):
        self.candidate["kind"] = "Stateless"
        self.write_input(self.candidate)
        with self.assertRaisesRegex(InvalidArgumentValueError, "does not convert"):
            self.update()
        self.assertEqual(self.before, self.transport.content)
        self.assertEqual([], self.mutations())

    def test_stateless_update_preserves_authored_runtime_configuration(self):
        self.transport.document = _workflow.workflow_json("Stateless")
        self.transport.content = json.dumps(self.transport.document).encode()
        self.candidate = copy.deepcopy(self.transport.document)
        self.candidate["runtimeConfiguration"] = {"statelessRunMode": "Debug"}
        self.write_input(self.candidate)
        result = self.update()
        self.assertEqual("Stateless", result["workflowKind"])
        self.assertEqual(self.candidate, json.loads(self.transport.content))

    def test_non_object_runtime_configuration_is_not_uploaded(self):
        self.candidate["runtimeConfiguration"] = []
        self.write_input(self.candidate)
        with self.assertRaisesRegex(InvalidArgumentValueError, "runtimeConfiguration must be an object"):
            self.update()
        self.assertEqual([], self.transport.calls)

    def test_runtime_preflight_rejection_preserves_existing_bytes(self):
        for failure in (http_error(400), http_error(401), RequestsTimeout("timeout")):
            with self.subTest(failure=type(failure).__name__):
                self.transport.reject_validation = failure
                with self.assertRaisesRegex(ValidationError, "existing workflow was not written"):
                    self.update()
        self.transport.reject_validation = None
        self.transport.validation_payload = {"error": {"code": "InvalidTemplate"}}
        with self.assertRaises(ValidationError):
            self.update()
        self.assertEqual(self.before, self.transport.content)
        self.assertEqual([], self.mutations())
        self.confirm.assert_not_called()

    def test_ambiguous_runtime_metadata_blocks_update_and_delete_before_confirmation(self):
        samples = (
            b'{"name":"hello","kind":"Stateful","kind":"Stateful","isDisabled":false}',
            b'{"name":"hello","kind":"Stateful","properties":{},"properties":{"isDisabled":false}}',
            b'{"name":"hello","kind":"Stateful","isDisabled":false,"isDisabled":false}',
            b'{"name":"hello","kind":"Stateful","isDisabled":false,"ignored":NaN}',
            b'{"name":"hello","kind":"Stateful","isDisabled":false,"ignored":1e999}',
        )
        for target in ("http://localhost:17071", SITE):
            for operation in (self.update, self.delete):
                for raw in samples:
                    with self.subTest(target=target, operation=operation.__name__, raw=raw):
                        self.transport.calls.clear()
                        self.transport.metadata_payload = raw
                        self.client = _runtime_client.SiteRuntimeClient(self.cmd, target, sender=self.transport)
                        with self.assertRaisesRegex(ClientRequestError, "invalid JSON"):
                            operation(yes=True)
                        self.assertEqual(self.before, self.transport.content)
                        self.assertEqual(1, len(self.transport.calls))
                        self.assertEqual([], self.mutations())
                        self.confirm.assert_not_called()

    def test_ambiguous_or_nonfinite_runtime_validation_blocks_publication(self):
        samples = (
            b'{"validationErrors":[],"validationErrors":[]}',
            b'{"properties":{},"properties":{}}',
            b'{"nested":{"keep":true,"keep":false}}',
            b'{"ignored":NaN}', b'{"ignored":Infinity}', b'{"ignored":-Infinity}', b'{"ignored":1e999}',
            b"[" * 1100 + b"0" + b"]" * 1100,
        )
        for target in ("http://localhost:17071", SITE):
            for raw in samples:
                with self.subTest(target=target, raw=raw[:100]):
                    self.transport.calls.clear()
                    self.transport.validation_payload = raw
                    self.client = _runtime_client.SiteRuntimeClient(self.cmd, target, sender=self.transport)
                    with self.assertRaisesRegex(ValidationError, "existing workflow was not written") as caught:
                        self.update(yes=True)
                    self.assertNotIn(raw.decode(), str(caught.exception))
                    self.assertEqual(self.before, self.transport.content)
                    self.assertEqual(1, sum(call[0] == "POST" for call in self.transport.calls))
                    self.assertEqual([], self.mutations())
                    self.confirm.assert_not_called()

    def test_strict_runtime_receipts_preserve_finite_and_empty_response_contracts(self):
        for raw, expected in ((b"", None), (b"null", None), (b'{"value":0.125}', {"value": 0.125}),
                              (b'{"Alpha":1,"alpha":2}', {"Alpha": 1, "alpha": 2})):
            with self.subTest(raw=raw):
                response = Response()
                response.status_code = 200
                response._content = raw
                response.headers["x-contract"] = "preserved"
                with patch.object(self.client, "_send", return_value=response):
                    self.assertEqual(expected, self.client.get("workflows/hello"))
                    receipt = self.client.post_with_receipt("workflows/hello/validate")
                self.assertEqual(expected, receipt["payload"])
                self.assertEqual(200, receipt["statusCode"])
                self.assertEqual("preserved", receipt["headers"]["x-contract"])

    def test_uncompleted_validation_receipts_block_local_and_cloud_mutations(self):
        for target in ("http://localhost:17071", SITE):
            for status in (201, 202, 203, 205, 206, 207, 302, None):
                with self.subTest(target=target, status=status):
                    self.transport.calls.clear()
                    self.transport.validation_status = status
                    self.transport.validation_headers = {
                        "Location": "https://operation.invalid/poll?sig=private-token",
                        "Azure-AsyncOperation": "https://operation.invalid/status?sig=private-token",
                    }
                    self.client = _runtime_client.SiteRuntimeClient(
                        self.cmd, target, sender=self.transport)
                    with self.assertRaisesRegex(ValidationError, "existing workflow was not written") as caught:
                        self.update()
                    self.assertIn("completed validation receipt", str(caught.exception.__cause__))
                    self.assertNotIn("private-token", str(caught.exception))
                    self.assertEqual(self.before, self.transport.content)
                    self.assertEqual([], self.mutations())
                    self.assertEqual(1, sum(call[0] == "POST" for call in self.transport.calls))
                    self.assertEqual(3, len(self.transport.calls))
                    self.confirm.assert_not_called()

    def test_completed_validation_receipts_preserve_supported_payload_shapes(self):
        for target in ("http://localhost:17071", SITE):
            for status, payload in ((200, None), (200, {}), (204, None)):
                with self.subTest(target=target, status=status, payload=payload):
                    self.transport = VfsTransport()
                    self.transport.validation_status = status
                    self.transport.validation_payload = payload
                    self.client = _runtime_client.SiteRuntimeClient(
                        self.cmd, target, sender=self.transport)
                    self.confirm.reset_mock()
                    result = self.update()
                    self.assertEqual("updated", result["action"])
                    self.assertEqual(self.candidate, json.loads(self.transport.content))
                    self.assertEqual(1, len(self.mutations()))
                    self.confirm.assert_called_once()

    def test_validation_status_does_not_change_existing_public_post_results(self):
        self.transport.validation_status = 202
        self.transport.validation_headers = {"Location": "https://operation.invalid/status"}
        path = _runtime_client.workflow_validate_path("hello")
        self.assertIsNone(self.client.post(path))
        self.assertEqual({"payload": None, "headers": self.transport.validation_headers},
                         self.client.post_with_headers(path))
        self.assertEqual({"payload": None, "headers": self.transport.validation_headers, "statusCode": 202},
                         self.client.post_with_receipt(path))

    def test_completed_validation_still_rejects_failing_or_unsupported_payloads(self):
        for payload in ({"error": {"code": "InvalidTemplate"}}, [], "unrecognized", False):
            with self.subTest(payload=payload):
                self.transport.validation_payload = payload
                with self.assertRaises(ValidationError):
                    self.update()
        self.assertEqual(self.before, self.transport.content)
        self.assertEqual([], self.mutations())
        self.confirm.assert_not_called()

    def test_injected_validation_client_must_provide_an_explicit_receipt(self):
        for receipt in (None, {}, {"payload": None}, {"statusCode": 200}):
            with self.subTest(receipt=receipt):
                with patch.object(self.client, "post_with_receipt", return_value=receipt):
                    with self.assertRaises(ValidationError):
                        self.update()
        self.assertEqual(self.before, self.transport.content)
        self.assertEqual([], self.mutations())
        self.confirm.assert_not_called()

    def test_stale_if_match_rejects_before_prompt_or_mutation(self):
        for operation in (self.update, self.delete):
            with self.subTest(operation=operation.__name__):
                with self.assertRaisesRegex(ClientRequestError, "revision changed"):
                    operation(if_match='"older"', yes=True)
        self.confirm.assert_not_called()
        self.assertEqual([], self.mutations())

    def test_wildcard_weak_list_and_injected_etags_are_rejected(self):
        for token in ("*", '"*"', 'W/"r1"', '"r1","r2"', "", '"r1"\r\nx=injected', '"r1\x00"'):
            for operation in (self.update, self.delete):
                with self.subTest(token=token, operation=operation.__name__):
                    with self.assertRaises(InvalidArgumentValueError):
                        operation(if_match=token, yes=True)
        self.assertEqual([], self.transport.calls)

    def test_missing_target_etag_or_invalid_current_document_blocks_mutation(self):
        self.transport.omit_read_etag = True
        with self.assertRaises(ClientRequestError):
            self.update()
        with self.assertRaises(ClientRequestError):
            self.delete()
        self.transport.omit_read_etag = False
        self.transport.content = b"invalid-json"
        with self.assertRaises(ClientRequestError):
            self.update()
        with self.assertRaises(ClientRequestError):
            self.delete()
        self.assertEqual([], self.mutations())

    def test_confirmation_cancellation_preserves_file(self):
        self.confirm.side_effect = ClientRequestError("cancelled")
        for operation in (self.update, self.delete):
            with self.subTest(operation=operation.__name__):
                with self.assertRaisesRegex(ClientRequestError, "cancelled"):
                    operation()
        self.assertEqual(self.before, self.transport.content)
        self.assertEqual([], self.mutations())

    def test_changed_revision_during_confirmation_is_rejected_before_write(self):
        replacement = json.dumps(self.transport.document).encode()
        self.confirm.side_effect = lambda *args: self.transport.change(replacement)
        with self.assertRaises(ClientRequestError):
            self.update()
        self.assertEqual(replacement, self.transport.content)
        self.assertEqual([], self.mutations())

    def test_changed_content_with_reused_etag_during_confirmation_is_rejected(self):
        self.confirm.side_effect = lambda *args: setattr(
            self.transport, "content", json.dumps(self.transport.document).encode())
        with self.assertRaisesRegex(ClientRequestError, "without a new ETag"):
            self.update()
        self.assertEqual([], self.mutations())

    def test_concurrent_update_before_put_is_rejected_without_rollback(self):
        replacement = json.dumps(self.transport.document).encode()
        self.transport.before_put = lambda: self.transport.change(replacement)
        with self.assertRaisesRegex(ClientRequestError, "rejected the ETag"):
            self.update()
        self.assertEqual(replacement, self.transport.content)
        self.assertEqual(1, len(self.mutations()))

    def test_concurrent_update_before_delete_is_not_deleted(self):
        replacement = json.dumps(self.transport.document).encode()
        self.transport.before_delete = lambda: self.transport.change(replacement)
        with self.assertRaisesRegex(ClientRequestError, "rejected the ETag"):
            self.delete()
        self.assertEqual(replacement, self.transport.content)
        self.assertEqual(1, len(self.mutations()))

    def test_missing_file_during_put_201_is_a_failure_not_silent_creation_success(self):
        self.transport.before_put = lambda: self.transport.change(None)
        with self.assertRaisesRegex(ClientRequestError, "may have recreated"):
            self.update()
        self.assertEqual(self.candidate, json.loads(self.transport.content))
        self.assertEqual(["PUT"], [call[0] for call in self.mutations()])

    def test_ambiguous_failed_write_is_not_called_success_or_retried(self):
        self.transport.after_put = lambda: (_ for _ in ()).throw(http_error(500))
        with self.assertRaisesRegex(ClientRequestError, "outcome may be uncertain"):
            self.update()
        self.assertEqual(self.candidate, json.loads(self.transport.content))
        self.assertEqual(["PUT"], [call[0] for call in self.mutations()])

    def test_write_receipt_without_etag_reports_applied_but_unverified_state(self):
        self.transport.omit_write_etag = True
        with self.assertRaisesRegex(ClientRequestError, "acknowledged without a usable write ETag"):
            self.update()
        self.assertEqual(self.candidate, json.loads(self.transport.content))
        self.assertEqual(1, len(self.mutations()))

    def test_failed_readback_does_not_blindly_restore(self):
        self.transport.after_put = lambda: setattr(self.transport, "get_failure", http_error(403))
        with self.assertRaisesRegex(ClientRequestError, "readback failed"):
            self.update()
        self.assertEqual(1, len(self.mutations()))

    def test_newer_revision_after_update_is_preserved(self):
        newer = json.dumps(self.transport.document).encode()
        self.transport.after_put = lambda: self.transport.change(newer)
        with self.assertRaisesRegex(ClientRequestError, "newer revision was not overwritten"):
            self.update()
        self.assertEqual(newer, self.transport.content)
        self.assertEqual(1, len(self.mutations()))

    def test_mismatched_owned_readback_conditionally_restores_original_bytes(self):
        def corrupt_first_write():
            self.transport.content = b"partial-write"
            self.transport.after_put = None
        self.transport.after_put = corrupt_first_write
        with self.assertRaisesRegex(ClientRequestError, "previous workflow file was conditionally restored"):
            self.update()
        self.assertEqual(self.before, self.transport.content)
        self.assertEqual(2, len(self.mutations()))
        self.assertIn('If-Match="r2"', self.mutations()[1][2]["headers"])

    def test_rollback_race_never_overwrites_concurrent_edit(self):
        newer = json.dumps(self.transport.document).encode()

        def corrupt_first_write():
            self.transport.content = b"partial-write"
            self.transport.after_put = None
            self.transport.before_put = lambda: self.transport.change(newer)
        self.transport.after_put = corrupt_first_write
        with self.assertRaisesRegex(ClientRequestError, "Conditional restoration failed"):
            self.update()
        self.assertEqual(newer, self.transport.content)
        self.assertEqual(2, len(self.mutations()))

    def test_deleted_file_after_write_is_not_recreated_by_rollback(self):
        self.transport.after_put = lambda: self.transport.change(None)
        with self.assertRaisesRegex(ClientRequestError, "readback failed"):
            self.update()
        self.assertIsNone(self.transport.content)
        self.assertEqual(1, len(self.mutations()))

    def test_delete_readback_auth_failure_or_recreation_is_not_success(self):
        for callback, expected in (
            (lambda: setattr(self.transport, "get_failure", http_error(401)), "absence could not be verified"),
            (lambda: self.transport.change(self.before), "still exists or was recreated"),
        ):
            with self.subTest(expected=expected):
                self.transport = VfsTransport()
                self.client = _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=self.transport)
                self.transport.after_delete = callback
                with self.assertRaisesRegex(ClientRequestError, expected):
                    self.delete()
                self.assertEqual(1, len(self.mutations()))

    def test_initial_not_found_local_auth_and_connection_errors_remain_distinct(self):
        for failure, expected in ((http_error(404), ResourceNotFoundError),
                                  (http_error(401), UnauthorizedError),
                                  (http_error(403), UnauthorizedError),
                                  (RequestsConnectionError("offline"), ClientRequestError)):
            with self.subTest(failure=type(failure).__name__):
                self.transport.get_failure = failure
                with self.assertRaises(expected):
                    self.update()
        self.assertEqual([], self.mutations())

    def test_sensitive_literals_are_preserved_but_not_returned_in_mutation_result(self):
        self.candidate["definition"]["actions"]["Compose_greeting"]["inputs"]["literal"] = "sensitive-authored-literal"
        self.write_input(self.candidate)
        result = self.update()
        self.assertIn("sensitive-authored-literal", self.transport.content.decode())
        self.assertNotIn("sensitive-authored-literal", json.dumps(result))
        self.assertNotIn("sensitive-authored-literal", self.confirm.call_args.args[0])

    def test_show_and_export_expose_revision_for_edit_session_guard(self):
        shown = _workflow_discovery.show_workflow(self.client, "hello")
        self.assertEqual('"r1"', shown["etag"])
        exported = _workflow_discovery.export_workflow(
            self.client, "hello", str(Path(self.folder.name) / "export.json"))
        self.assertEqual('"r1"', exported["etag"])

    def test_legacy_vfs_default_wildcard_remains_for_existing_callers(self):
        self.client.vfs_client().put_raw("hello/workflow.json", self.before)
        self.assertIn("If-Match=*", self.mutations()[0][2]["headers"])

    def test_command_registration_required_flags_and_no_force_bypass(self):
        for suffix in ("set", "delete"):
            command = "logicapp workflow " + suffix
            cli = get_default_cli()
            cli.invocation = SimpleNamespace(data={"command_string": command})
            loader = COMMAND_LOADER_CLS(cli_ctx=cli)
            self.assertIn(command, loader.load_command_table([]))
            loader.load_arguments([])
            args = loader.argument_registry.arguments[command]
            self.assertTrue(args["workflow"].settings["required"])
            self.assertTrue({"resource_group_name", "name", "local", "port", "host_key", "context",
                             "if_match", "yes", "allow_non_atomic"} <= set(args))
            self.assertNotIn("force", args)
            self.assertNotIn("path", args)
            if suffix == "set":
                self.assertTrue(args["file"].settings["required"])

    def test_custom_commands_share_target_resolution_and_validation(self):
        with patch.object(_runtime_client, "send_raw_request", side_effect=self.transport), \
                patch.object(_runtime_client, "_site_resource_id", return_value=SITE):
            result = custom.workflow_set(self.cmd, "hello", str(self.file), local=True, port=17071,
                                         host_key="local-key", allow_non_atomic=True, yes=True)
            self.assertEqual("updated", result["action"])
            result = custom.workflow_delete(self.cmd, "hello", resource_group_name="rg", name="app",
                                            allow_non_atomic=True, yes=True)
            self.assertEqual("deleted", result["action"])
        for operation, required in ((custom.workflow_set, {"file": str(self.file)}), (custom.workflow_delete, {})):
            for kwargs in ({"local": True, "name": "app"}, {"context": "ctx", "port": 17071},
                           {"resource_group_name": "rg", "name": "app", "host_key": "key"}):
                with self.subTest(operation=operation.__name__, kwargs=kwargs):
                    with self.assertRaises((MutuallyExclusiveArgumentError, RequiredArgumentMissingError)):
                        operation(self.cmd, "hello", **required, **kwargs)


if __name__ == "__main__":
    unittest.main()
