# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import copy
import gzip
import logging
import os
import ssl
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import InvalidArgumentValueError, MutuallyExclusiveArgumentError
from knack.util import CLIError
from requests import Response
from requests.exceptions import ConnectionError as RequestsConnectionError, ReadTimeout
from urllib3.exceptions import ReadTimeoutError

from azext_logicapp import _execution_transport as transport, _run_execution as execution, custom
from azext_logicapp._runtime_client import SiteRuntimeClient, run_action_path

SITE = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"
PRIVATE = "do-not-print-provider-secret"


class Clock:
    def __init__(self):
        self.now = 100
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, amount):
        assert amount >= 0
        self.sleeps.append(amount)
        self.now += amount


class ExecutionFixture:
    def __init__(self):
        self.calls = []
        self.kind = "Stateful"
        self.statuses = ["Succeeded"]
        self.after_cancel = ["Cancelled"]
        self.reads = 0
        self.posts = 0
        self.history_pages = [{"value": [self.history()]}]
        self.pages = 0
        self.new_id = "new-run"
        self.receipt_status = None
        self.receipt_body = None
        self.failure = None
        self.run_override = None
        self.metadata_override = None
        self.trigger_override = None
        self.history_override = None
        self.read_status = 200

    @staticmethod
    def history(history="different-history", run="source-run", fired=True):
        return {"name": history, "properties": {
            "fired": fired, "run": {"id": "/workflows/hello/runs/" + run},
            "outputsLink": {"uri": "https://untrusted.invalid/?sig=" + PRIVATE}}}

    def request(self, method, path, deadline, params=None):
        self.calls.append((method, path, deadline, params))
        if self.failure:
            error = self.failure(method, path)
            if error:
                raise error
        if method == "POST":
            self.posts += 1
            if path.endswith("/cancel"):
                self.statuses = self.after_cancel
                self.reads = 0
                status, headers = self.receipt_status or 200, {}
            else:
                status, headers = self.receipt_status or 202, {
                    "Location": "https://untrusted.invalid/?sig=" + PRIVATE}
                if self.new_id is not None:
                    headers["X-Ms-Workflow-Run-Id"] = self.new_id
            return {"statusCode": status, "payload": self.receipt_body, "headers": headers}
        if path == "workflows/hello":
            payload = self.metadata_override if self.metadata_override is not None else {
                "name": "hello", "kind": self.kind, "isDisabled": False}
        elif path == "workflows/hello/runs/source-run":
            status = self.statuses[min(self.reads, len(self.statuses) - 1)]
            self.reads += 1
            payload = self.run_override if self.run_override is not None else {
                "name": "source-run", "properties": {"status": status, "trigger": {"name": "manual"},
                                                     "error": {"message": PRIVATE}, "outputs": {"secret": PRIVATE}}}
        elif path == "workflows/hello/triggers/manual":
            payload = self.trigger_override if self.trigger_override is not None else {"name": "manual"}
        elif path.endswith("/histories"):
            payload = self.history_pages[min(self.pages, len(self.history_pages) - 1)]
            self.pages += 1
        elif "/histories/" in path:
            payload = self.history_override if self.history_override is not None else self.history(path.rsplit("/", 1)[-1])
        else:
            raise AssertionError(path)
        return {"statusCode": self.read_status, "payload": payload, "headers": {}}


class ActionExecutionFixture(ExecutionFixture):
    def __init__(self):
        super().__init__()
        self.statuses = ["Failed"]
        self.selected = {"name": "Send_HTTP", "properties": {
            "status": "Failed", "code": "BadGateway", "canResubmit": True,
            "correlation": {"actionTrackingId": "action-tracking"},
            "error": {"message": PRIVATE}}}
        self.action_reads = 0
        self.bodies = []
        self.header_override = None

    def request(self, method, path, deadline, params=None, body=None):
        if method == "POST":
            self.bodies.append(copy.deepcopy(body))
        if method == "GET" and "/actions/" in path:
            self.calls.append((method, path, deadline, params))
            if self.failure:
                error = self.failure(method, path)
                if error:
                    raise error
            self.action_reads += 1
            selected = copy.deepcopy(self.selected)
            selected.setdefault("properties", {})["outputsLink"] = {
                "uri": "https://untrusted.invalid/?sig={}&read={}".format(PRIVATE, self.action_reads)}
            return {"statusCode": self.read_status, "payload": selected, "headers": {}}
        result = super().request(method, path, deadline, params)
        if method == "POST" and self.header_override is not None:
            result["headers"] = self.header_override
        return result


class _ExecutionTestCase(unittest.TestCase):
    fixture_type = ExecutionFixture

    def setUp(self):
        self.clock = Clock()
        self.fixture = self.fixture_type()
        self.cmd = SimpleNamespace(cli_ctx=get_default_cli())
        self.client = SiteRuntimeClient(self.cmd, SITE)
        for target, name, value in ((execution.time, "monotonic", self.clock.monotonic),
                                    (execution.time, "sleep", self.clock.sleep),
                                    (execution, "ExecutionTransport", Mock(return_value=self.fixture))):
            patcher = patch.object(target, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(execution, "user_confirmation")
        self.confirm = patcher.start()
        self.addCleanup(patcher.stop)

    def wait(self, **kwargs):
        return execution.wait_run(self.client, "hello", "source-run", **kwargs)

    def cancel(self, **kwargs):
        return execution.cancel_run(self.client, "hello", "source-run", **kwargs)

    def resubmit(self, history_name="different-history", **kwargs):
        return execution.resubmit_trigger_history(self.client, "hello", "manual", history_name, **kwargs)

    def assert_private(self, result):
        self.assertNotIn(PRIVATE, json.dumps(result))

    def assert_error(self, result, kind):
        self.assertIsInstance(result["error"], dict)
        self.assertEqual(kind, result["error"]["kind"])

    def set_history_reference(self, identifier, run_name="source-run"):
        def history(history="different-history", run="source-run", fired=True):
            payload = ExecutionFixture.history(history, run, fired)
            payload["properties"]["run"] = {"id": identifier}
            if run_name is not None:
                payload["properties"]["run"]["name"] = run_name
            return payload

        self.fixture.history = history
        self.fixture.history_pages = [{"value": [history()]}]
        self.fixture.pages = 0


class ActionResubmitTests(_ExecutionTestCase):
    fixture_type = ActionExecutionFixture

    def resubmit_action(self, **kwargs):
        return execution.resubmit_run_action(self.client, "hello", "source-run", "Send_HTTP", **kwargs)

    def assert_no_post(self):
        self.assertFalse(any(call[0] == "POST" for call in self.fixture.calls))

    def test_action_post_has_exact_run_route_and_body_without_history_fallback(self):
        result = self.resubmit_action(yes=True)
        self.assertEqual("accepted", result["outcome"])
        self.assertEqual("actionResubmit", result["operation"])
        self.assertEqual("Send_HTTP", result["actionName"])
        self.assertEqual("source-run", result["sourceRunId"])
        self.assertEqual("Failed", result["status"])
        self.assertEqual("new-run", result["newRunId"])
        self.assertIsNone(result["newRunStatus"])
        self.assertTrue(result["requestAcknowledged"])
        self.assertEqual([{"actionsToResubmit": [{"name": "Send_HTTP"}]}], self.fixture.bodies)
        self.assertEqual(["workflows/hello/runs/source-run/resubmit"],
                         [call[1] for call in self.fixture.calls if call[0] == "POST"])
        self.assertFalse(any("/histories" in call[1] for call in self.fixture.calls))
        self.assertEqual(2, self.fixture.action_reads)
        self.assert_private(result)

    def test_missing_or_untrusted_eligibility_refuses_without_confirmation_or_post(self):
        for value in (False, None, "true", 1, 1.0, {}, []):
            with self.subTest(value=value):
                self.fixture.selected["properties"]["canResubmit"] = value
                result = self.resubmit_action()
                self.assert_error(result, "actionNotEligible")
                self.assert_no_post()
                self.confirm.assert_not_called()
                self.assert_private(result)
        self.fixture.selected["properties"].pop("canResubmit")
        self.assert_error(self.resubmit_action(), "actionNotEligible")
        self.assert_no_post()

    def test_active_source_unknown_status_and_unexecuted_actions_refuse(self):
        for status in execution._ACTIVE + ("NotSpecified",):
            with self.subTest(source_status=status):
                self.fixture.statuses, self.fixture.reads = [status], 0
                result = self.resubmit_action()
                self.assert_error(result, "unknownStatus" if status == "NotSpecified" else "sourceNotCompleted")
                self.assert_no_post()
        self.fixture.statuses, self.fixture.reads = ["Failed"], 0
        for status in ("Skipped", "Ignored", "Running", None, "unknown"):
            with self.subTest(action_status=status):
                self.fixture.selected["properties"]["status"] = status
                self.assert_error(self.resubmit_action(), "actionNotEligible")
                self.assert_no_post()

    def test_stateless_decline_and_post_confirmation_eligibility_loss_do_not_post(self):
        self.fixture.kind = "Stateless"
        with self.assertRaises(InvalidArgumentValueError):
            self.resubmit_action()
        self.fixture.kind = "Stateful"
        self.confirm.side_effect = CLIError("Declined")
        with self.assertRaises(CLIError):
            self.resubmit_action()
        self.confirm.side_effect = lambda *_args: self.fixture.selected["properties"].update(canResubmit=False)
        self.assert_error(self.resubmit_action(), "actionNotEligible")
        self.assert_no_post()

    def test_source_and_action_stable_metadata_changes_refuse_including_scalar_types(self):
        for member, before, after in (("code", False, 0), ("endTime", "before", "after"),
                                      ("correlation", {"actionTrackingId": "old"},
                                       {"actionTrackingId": "new"})):
            with self.subTest(member=member):
                self.fixture.selected["properties"][member] = before
                self.confirm.side_effect = lambda *_args: self.fixture.selected["properties"].update({member: after})
                self.assert_error(self.resubmit_action(), "changed")
                self.assert_no_post()
        self.confirm.side_effect = None
        self.fixture.statuses, self.fixture.reads = ["Failed", "Succeeded"], 0
        self.assert_error(self.resubmit_action(), "changed")
        self.assert_no_post()

    def test_original_workflow_version_is_rechecked_without_reading_current_definition(self):
        self.fixture.run_override = {"name": "source-run", "properties": {
            "status": "Failed", "workflow": {"id": "/workflows/hello/versions/original"}}}
        self.confirm.side_effect = lambda *_args: self.fixture.run_override["properties"]["workflow"].update(
            id="/workflows/hello/versions/new")
        self.assert_error(self.resubmit_action(), "changed")
        self.assert_no_post()
        self.assertFalse(any("/versions/" in call[1] or call[1].endswith("workflow.json")
                             for call in self.fixture.calls))

    def test_optional_id_must_match_selected_site_workflow_run_and_action(self):
        path = run_action_path("hello", "source-run", "Send_HTTP")
        for identifier in ("/" + path, urlsplit(self.client._build_url(path)).path):
            with self.subTest(valid=identifier):
                self.fixture.selected["id"] = identifier
                self.assertEqual("accepted", self.resubmit_action()["outcome"])
        for identifier in ("/workflows/other/runs/source-run/actions/Send_HTTP",
                           "/" + path.replace("source-run", "another-run"),
                           urlsplit(self.client._build_url(path)).path.replace("/sites/app/", "/sites/other/"),
                           "https://untrusted.invalid/" + path, {}, "/" + path + "?sig=" + PRIVATE):
            with self.subTest(invalid=identifier):
                self.fixture.calls.clear()
                self.fixture.selected["id"] = identifier
                self.assert_error(self.resubmit_action(), "invalidResponse")
                self.assert_no_post()
        self.fixture.selected.pop("id")
        self.fixture.run_override = {"name": "source-run", "id": "/workflows/other/runs/source-run",
                                     "properties": {"status": "Failed"}}
        self.assert_error(self.resubmit_action(), "invalidResponse")

    def test_ambiguous_identity_and_eligibility_are_not_positive_evidence(self):
        for change in ({"Name": "Send_HTTP"}, {"name": "different"},
                       {"properties": {"status": "Failed", "canResubmit": True, "CanResubmit": True}}):
            with self.subTest(change=change):
                previous = copy.deepcopy(self.fixture.selected)
                self.fixture.selected.update(change)
                self.assert_error(self.resubmit_action(), "invalidResponse")
                self.assert_no_post()
                self.fixture.selected = previous

    def test_missing_new_identity_is_acknowledged_but_never_guessed(self):
        self.fixture.new_id = None
        result = self.resubmit_action()
        self.assertEqual("acceptedNewRunIdUnknown", result["outcome"])
        self.assertTrue(result["requestAcknowledged"])
        self.assertIsNone(result["newRunId"])
        self.assertEqual(2, self.fixture.reads)
        self.assert_private(result)

    def test_action_inspection_only_exposes_unambiguous_boolean_eligibility(self):
        cases = (
            ({"canResubmit": True}, True), ({"CanResubmit": False}, False),
            ({}, None), ({"canResubmit": "true"}, None), ({"canResubmit": 1}, None),
            ({"canResubmit": True, "CanResubmit": False}, None),
            ({"canResubmit": True, "CANRESUBMIT": True}, None),
        )
        for properties, expected in cases:
            for container in ("properties", "Properties"):
                with self.subTest(properties=properties, container=container):
                    result = custom._run_action_response(
                        {container: properties}, "hello", "source-run", False)
                    self.assertIs(expected, result["canResubmit"])
        result = custom._run_action_response(
            {"properties": {"canResubmit": True}, "Properties": {"canResubmit": True}},
            "hello", "source-run", False)
        self.assertIsNone(result["canResubmit"])

    def test_invalid_or_conflicting_new_identity_preserves_known_acknowledgement(self):
        for new_id in ("source-run", "", "new,other", "https://untrusted.invalid/" + PRIVATE, [], 1):
            with self.subTest(new_id=new_id):
                self.fixture.new_id = new_id
                result = self.resubmit_action()
                self.assert_error(result, "invalidResponse")
                self.assertTrue(result["requestAcknowledged"])
                self.assertIsNone(result["newRunId"])
                self.assertEqual("resubmitRequested", result["action"])
                self.assert_private(result)
        self.fixture.header_override = {"x-ms-workflow-run-id": "new",
                                        "X-Ms-Workflow-Run-Id": "other"}
        self.assert_error(self.resubmit_action(), "invalidResponse")

    def test_unexpected_receipts_and_failed_post_are_uncertain_without_retry(self):
        for status in (200, 201, 204, 202.0, "202"):
            with self.subTest(status=status):
                self.fixture.receipt_status = status
                self.fixture.calls.clear()
                result = self.resubmit_action()
                self.assert_error(result, "invalidResponse")
                self.assertFalse(result["requestAcknowledged"])
                self.assertEqual(1, sum(call[0] == "POST" for call in self.fixture.calls))
        self.fixture.receipt_status = 202
        self.fixture.receipt_body = {"secret": PRIVATE}
        self.assert_private(self.resubmit_action())
        self.fixture.receipt_body = None
        self.fixture.failure = lambda method, _path: transport.ExecutionError(
            "unavailable", "Request failed") if method == "POST" else None
        result = self.resubmit_action()
        self.assertFalse(result["requestAcknowledged"])
        self.assertEqual("observationFailed", result["outcome"])

    def test_pre_send_authentication_and_deadline_failures_do_not_claim_submission(self):
        for error in (transport.ExecutionError("authentication", "Credential unavailable", before_send=True),
                      transport.DeadlineExpired(before_send=True)):
            with self.subTest(error=type(error).__name__):
                self.fixture.failure = lambda method, _path: error if method == "POST" else None
                result = self.resubmit_action()
                self.assertIsNone(result["action"])
                self.assertFalse(result["requestAcknowledged"])
                self.assertIn("before submission", result["message"])

    def test_identifiers_are_validated_before_target_io_and_action_names_are_quoted(self):
        for action in (None, "", True, "a/b", "a%2fb", "a?sig=" + PRIVATE, ["a"], ".."):
            with self.subTest(action=action), patch.object(custom, "_client_from_target") as target:
                with self.assertRaises(InvalidArgumentValueError):
                    custom.run_resubmit(None, "hello", "source-run", action, local=True)
                target.assert_not_called()
        self.fixture.selected["name"] = "Send HTTP"
        result = execution.resubmit_run_action(self.client, "hello", "source-run", "Send HTTP")
        self.assertEqual("accepted", result["outcome"])
        self.assertTrue(any(call[1].endswith("/actions/Send%20HTTP") for call in self.fixture.calls))
        self.assertEqual({"actionsToResubmit": [{"name": "Send HTTP"}]}, self.fixture.bodies[-1])

    def test_real_prepared_transport_sends_json_body_and_selected_cloud_api_only(self):
        requests_sent = []
        fixture = self.fixture

        def send(_session, request, **_kwargs):
            requests_sent.append(request)
            path = "workflows/" + urlsplit(request.url).path.split("/workflows/", 1)[1]
            body = json.loads(request.body) if request.body else None
            receipt = fixture.request(request.method, path, self.clock.now + 60, body=body)
            response = Response()
            response.status_code = receipt["statusCode"]
            response._content = b"" if receipt["payload"] is None else json.dumps(receipt["payload"]).encode()
            response._content_consumed = True
            response.headers.update(receipt["headers"])
            return response

        with patch.object(execution, "ExecutionTransport", transport.ExecutionTransport), \
                patch("requests.Session.send", send), patch.object(transport, "Profile") as profile:
            profile.return_value.get_raw_token.return_value = (("Bearer", PRIVATE), None, None)
            self.assertEqual("accepted", self.resubmit_action()["outcome"])
        posts = [request for request in requests_sent if request.method == "POST"]
        self.assertEqual(1, len(posts))
        self.assertEqual({"actionsToResubmit": [{"name": "Send_HTTP"}]}, json.loads(posts[0].body))
        self.assertTrue(all(parse_qs(urlsplit(request.url).query)["api-version"] == ["2024-11-01"]
                            for request in requests_sent))
        self.assertTrue(all(request.body is None for request in requests_sent if request.method == "GET"))
        self.assertTrue(all(request.headers["Authorization"] == "Bearer " + PRIVATE for request in requests_sent))


class RunExecutionTests(_ExecutionTestCase):
    def test_wait_all_terminal_statuses_and_case_handling(self):
        for status in execution._TERMINAL:
            with self.subTest(status=status):
                self.fixture.statuses = [status.swapcase()]
                self.fixture.reads = 0
                result = self.wait()
                self.assertEqual(status, result["status"])
                self.assertEqual(0 if status == "Succeeded" else 4, result["exitCode"])
                self.assert_private(result)
                self.assertEqual(0, self.fixture.posts)

    def test_wait_sleeps_until_success_with_a_monotonic_deadline(self):
        self.fixture.statuses = ["Running", "Waiting", "Succeeded"]
        result = self.wait(timeout=10, interval=3)
        self.assertEqual("completed", result["outcome"])
        self.assertEqual([3, 3], self.clock.sleeps)
        self.assertTrue(all(call[2] == 110 for call in self.fixture.calls))

    def test_wait_timeout_does_not_cancel_or_sleep_past_deadline(self):
        self.fixture.statuses = ["Running"]
        result = self.wait(timeout=7, interval=3)
        self.assertEqual("waitTimedOut", result["outcome"])
        self.assertEqual(2, result["exitCode"])
        self.assertEqual("Running", result["status"])
        self.assertEqual([3, 3, 1], self.clock.sleeps)
        self.assertEqual(0, self.fixture.posts)

    def test_workflow_timed_out_is_not_cli_wait_timeout(self):
        self.fixture.statuses = ["TimedOut"]
        result = self.wait()
        self.assertEqual("terminalNotExpected", result["outcome"])
        self.assertEqual(4, result["exitCode"])

    def test_paused_and_suspended_remain_observable_not_success(self):
        for status in ("Paused", "Suspended"):
            with self.subTest(status=status):
                self.fixture.statuses = [status]
                result = self.wait(timeout=2, interval=1)
                self.assertEqual("waitTimedOut", result["outcome"])

    def test_unknown_missing_and_malformed_status_fail_immediately_without_echo(self):
        for status in (None, PRIVATE, "NotSpecified", {}, 5, ""):
            with self.subTest(status=status):
                self.fixture.statuses = [status]
                result = self.wait()
                self.assertEqual("unknownStatus", result["error"]["kind"])
                self.assertEqual(1, result["exitCode"])
                self.assert_private(result)
        self.assertFalse(self.clock.sleeps)

    def test_not_found_auth_conflict_network_errors_are_not_polled(self):
        for kind in ("notFound", "unauthorized", "conflict", "unavailable", "requestTimeout"):
            with self.subTest(kind=kind):
                self.fixture.failure = lambda _method, _path: transport.ExecutionError(kind, "Safe failure.")
                before = len(self.fixture.calls)
                result = self.wait()
                self.assertEqual(kind, result["error"]["kind"])
                self.assertEqual(before + 1, len(self.fixture.calls))
        self.assertFalse(self.clock.sleeps)

    def test_metadata_and_run_contract_errors_are_explicit(self):
        for metadata in ([], {"name": "other", "kind": "Stateful"}, {"name": "hello"},
                         {"name": "hello", "kind": PRIVATE}, {"error": {"message": PRIVATE}}):
            with self.subTest(metadata=metadata):
                self.fixture.metadata_override = metadata
                result = self.wait()
                self.assertEqual(1, result["exitCode"])
                self.assert_private(result)
        self.fixture.metadata_override = None
        for payload in ([], {}, {"name": "other", "properties": {"status": "Succeeded"}},
                        {"name": "source-run", "properties": []},
                        {"name": "source-run", "properties": {"status": "Succeeded", "STATUS": "Failed"}}):
            with self.subTest(payload=payload):
                self.fixture.run_override = payload
                self.assertEqual(1, self.wait()["exitCode"])

    def test_async_reads_are_not_terminal_receipts(self):
        self.fixture.read_status = 202
        self.assertEqual("invalidResponse", self.wait()["error"]["kind"])

    def test_ambiguous_workflow_metadata_blocks_all_execution_before_confirmation(self):
        for payload in (
                {"name": "hello", "kind": "Stateful", "KIND": "Stateless"},
                {"name": "hello", "kind": "Stateful", "KIND": "Stateful"},
                {"name": "hello", "kind": "Stateful", "isDisabled": False, "ISDISABLED": True},
                {"name": "hello", "kind": "Stateful", "properties": {
                    "isDisabled": False, "ISDISABLED": False}}):
            for operation in (self.wait, self.cancel, self.resubmit):
                with self.subTest(payload=payload, operation=operation.__name__):
                    self.fixture.metadata_override = payload
                    self.fixture.calls.clear()
                    result = operation()
                    self.assertEqual(1, result["exitCode"])
                    self.assertEqual("invalidResponse", result["error"]["kind"])
                    self.assertEqual(["GET"], [call[0] for call in self.fixture.calls])
                    self.assertEqual("workflows/hello", self.fixture.calls[0][1])
        self.assertEqual(0, self.fixture.posts)
        self.confirm.assert_not_called()

    def test_stateless_and_unknown_models_never_mutate_or_confirm(self):
        for kind in ("Stateless", PRIVATE):
            for operation in (self.wait, self.cancel, self.resubmit):
                with self.subTest(kind=kind, operation=operation):
                    self.fixture.kind = kind
                    if kind == "Stateless":
                        with self.assertRaisesRegex(InvalidArgumentValueError, "Stateful"):
                            operation()
                    else:
                        self.assertEqual(1, operation()["exitCode"])
        self.confirm.assert_not_called()
        self.assertEqual(0, self.fixture.posts)

    def test_option_validation_happens_before_transport_or_confirmation(self):
        cases = [(0, 1), (86401, 1), (True, 1), ("2", 1), (2, 0), (2, 3), (400, 301)]
        for timeout, interval in cases:
            with self.subTest(timeout=timeout, interval=interval):
                with self.assertRaises(InvalidArgumentValueError):
                    self.wait(timeout=timeout, interval=interval)
        for run in ("", "/", "..", "a/b", "a\\b", "a%2Fb", "a?sig=x", "a#x", "x\n", " x", 1):
            with self.subTest(run=run):
                with self.assertRaises(InvalidArgumentValueError):
                    execution.cancel_run(self.client, "hello", run)
        self.assertFalse(self.fixture.calls)
        self.confirm.assert_not_called()

    def test_cancel_confirms_and_distinguishes_acknowledgement_from_state(self):
        self.fixture.statuses = ["Running"]
        self.fixture.after_cancel = ["Running"]
        result = self.cancel(yes=True)
        self.assertEqual(("cancelRequested", "pending", "Running"),
                         (result["action"], result["outcome"], result["status"]))
        self.assertEqual(1, self.fixture.posts)
        self.confirm.assert_called_once()
        self.assertTrue(self.confirm.call_args.args[1])
        self.assertIn("does not roll back", self.confirm.call_args.args[0])

    def test_cancel_readback_observes_cancelled(self):
        self.fixture.statuses = ["Running"]
        result = self.cancel()
        self.assertEqual("cancelled", result["outcome"])
        self.assertEqual("Cancelled", result["status"])

    def test_cancel_terminal_run_is_noop_even_after_confirmation_race(self):
        for statuses in (["Succeeded"], ["Running", "Failed"]):
            with self.subTest(statuses=statuses):
                self.fixture.statuses = statuses
                self.fixture.reads = 0
                result = self.cancel()
                self.assertEqual("alreadyTerminal", result["action"])
                self.assertEqual("unchanged", result["outcome"])
        self.assertEqual(0, self.fixture.posts)

    def test_cancel_wait_requires_cancelled_not_successful_competing_completion(self):
        for states, expected_code in ((["Running", "Cancelled"], 0), (["Succeeded"], 4), (["Running"], 2)):
            with self.subTest(states=states):
                self.fixture.statuses = ["Running"]
                self.fixture.reads = 0
                self.fixture.after_cancel = states
                result = self.cancel(wait=True, timeout=2, interval=1)
                self.assertEqual(expected_code, result["exitCode"])
        self.assertEqual(3, self.fixture.posts)

    def test_cancel_confirmation_decline_never_mutates(self):
        self.fixture.statuses = ["Running"]
        self.confirm.side_effect = CLIError("Operation cancelled.")
        with self.assertRaises(CLIError):
            self.cancel()
        self.assertEqual(0, self.fixture.posts)

    def test_cancel_request_failure_or_invalid_receipt_is_not_retried(self):
        self.fixture.statuses = ["Running"]
        self.fixture.receipt_body = {"error": {"message": PRIVATE}}
        result = self.cancel()
        self.assertEqual("observationFailed", result["outcome"])
        self.assertEqual("cancelAttempted", result["action"])
        self.assertEqual(1, self.fixture.posts)
        self.assert_private(result)

    def test_cancel_async_acknowledgements_still_require_observed_state(self):
        for code in (202, 204):
            with self.subTest(code=code):
                self.fixture.statuses = ["Running"]
                self.fixture.reads = 0
                self.fixture.receipt_status = code
                self.fixture.after_cancel = ["Running"]
                result = self.cancel()
                self.assertEqual("pending", result["outcome"])
                self.assertTrue(result["requestAcknowledged"])

    def test_cancel_post_deadline_is_not_claimed_as_wait_timeout(self):
        self.fixture.statuses = ["Running"]
        self.fixture.failure = lambda method, _path: transport.DeadlineExpired() if method == "POST" else None
        result = self.cancel(wait=True)
        self.assertEqual("requestDeadlineExpired", result["outcome"])
        self.assertFalse(result["requestAcknowledged"])
        self.assertEqual("cancelAttempted", result["action"])

    def test_cancel_failed_readback_retains_truthful_requested_action(self):
        self.fixture.statuses = ["Running"]
        self.fixture.failure = lambda method, _path: (
            transport.ExecutionError("unauthorized", "Access denied.")
            if method == "GET" and self.fixture.posts else None)
        result = self.cancel()
        self.assertEqual("cancelRequested", result["action"])
        self.assertEqual("observationFailed", result["outcome"])
        self.assertEqual(1, result["exitCode"])

    def test_resubmit_selects_history_directly_without_source_run_or_search(self):
        result = self.resubmit(yes=True)
        self.assertEqual("different-history", result["triggerHistoryId"])
        self.assertEqual("new-run", result["newRunId"])
        self.assertIsNone(result["runId"])
        self.assertNotIn("sourceRunId", result)
        self.assertFalse(any("/runs/" in path or path.endswith("/histories")
                             for _, path, _, _ in self.fixture.calls))
        self.assertEqual("accepted", result["outcome"])
        self.assertEqual(1, self.fixture.posts)
        self.assertEqual("workflows/hello/triggers/manual/histories/different-history/resubmit",
                         next(path for method, path, _, _ in self.fixture.calls if method == "POST"))
        self.assertIn("duplicate external side effects", self.confirm.call_args.args[0])
        self.assert_private(result)
        self.assertTrue(result["requestAcknowledged"])
        self.assertEqual("1.0", result["schemaVersion"])
        self.assertIsNone(result["newRunStatus"])

    def test_resubmit_ack_without_new_id_never_uses_original_or_location(self):
        self.fixture.new_id = None
        result = self.resubmit()
        self.assertEqual("acceptedNewRunIdUnknown", result["outcome"])
        self.assertIsNone(result["newRunId"])
        self.assert_private(result)
        self.assertFalse(any("https://" in path for _, path, _, _ in self.fixture.calls))

    def test_trigger_resubmit_rejects_ambiguous_headers_without_losing_acknowledgement(self):
        headers = (
            {"x-ms-workflow-run-id": "new,other"},
            {"x-ms-workflow-run-id": "new other"},
            {"x-ms-workflow-run-id": "new", "X-Ms-Workflow-Run-Id": "other"},
            {"x-ms-workflow-run-id": "new", "X-Ms-Workflow-Run-Id": "new"},
        )
        original = self.fixture.request
        for values in headers:
            def response(method, *args, **kwargs):
                receipt = original(method, *args, **kwargs)
                if method == "POST":
                    receipt["headers"] = values
                return receipt

            with self.subTest(headers=values), patch.object(self.fixture, "request", response):
                before = self.fixture.posts
                result = self.resubmit()
                self.assert_error(result, "invalidResponse")
                self.assertTrue(result["requestAcknowledged"])
                self.assertEqual("resubmitRequested", result["action"])
                self.assertIsNone(result["newRunId"])
                self.assertEqual(before + 1, self.fixture.posts)

    def test_trigger_resubmit_requires_integer_accepted_status(self):
        for status in (202.0, "202"):
            with self.subTest(status=status):
                self.fixture.receipt_status = status
                before = self.fixture.posts
                result = self.resubmit()
                self.assert_error(result, "invalidResponse")
                self.assertFalse(result["requestAcknowledged"])
                self.assertEqual(before + 1, self.fixture.posts)

    def test_direct_history_accepts_missing_associated_run_in_local_and_cloud_targets(self):
        for target in (SITE, "http://localhost:17071"):
            with self.subTest(target=target):
                self.client = SiteRuntimeClient(self.cmd, target)
                self.fixture.history_override = {"name": "different-history", "properties": {"fired": True}}
                result = self.resubmit(yes=True)
                self.assertEqual("accepted", result["outcome"])
                self.assertIsNone(result["runId"])
                self.assert_private(result)
        self.assertEqual(2, self.fixture.posts)

    def test_resubmit_invalid_new_id_fails_after_single_request(self):
        for new_id in ("https://untrusted.invalid/?sig=" + PRIVATE, "", "a/b"):
            with self.subTest(new_id=new_id):
                self.fixture.new_id = new_id
                result = self.resubmit()
                self.assertEqual(1, result["exitCode"])
                self.assert_private(result)
        self.assertEqual(3, self.fixture.posts)

    def test_direct_history_missing_or_unfired_refuses_without_search_or_post(self):
        for error in (transport.ExecutionError("notFound", "Selected history was not found."), None):
            with self.subTest(error=error):
                self.fixture.failure = lambda method, path: error if "/histories/" in path else None
                self.fixture.history_override = {"name": "different-history", "properties": {"fired": False}}
                result = self.resubmit()
                self.assert_error(result, "notFound" if error else "historyNotFired")
                self.assertEqual(0, self.fixture.pages)
        self.assertEqual(0, self.fixture.posts)
        self.confirm.assert_not_called()

    def test_resubmit_confirmation_decline_and_changed_trigger_prevent_post(self):
        self.confirm.side_effect = CLIError("Operation cancelled.")
        with self.assertRaises(CLIError):
            self.resubmit()
        self.confirm.side_effect = lambda *_args: setattr(self.fixture, "trigger_override", {
            "name": "manual", "properties": {"workflowVersion": "changed"}})
        result = self.resubmit()
        self.assertEqual("changed", result["error"]["kind"])
        self.assertEqual(0, self.fixture.posts)

    def test_history_signed_links_rotate_without_invalidating_stable_evidence(self):
        self.fixture.trigger_override = {
            "name": "manual", "id": "/workflows/hello/triggers/manual",
            "properties": {"workflowVersion": "v1", "status": "Enabled",
                           "inputsLink": {"uri": "https://example.invalid/old"}}}
        self.fixture.history_override = self.fixture.history()

        def rotate(*_args):
            self.fixture.trigger_override["properties"]["inputsLink"]["uri"] = "https://example.invalid/new"
            self.fixture.history_override["properties"]["outputsLink"]["uri"] = "https://example.invalid/new"

        self.confirm.side_effect = rotate
        result = self.resubmit()
        self.assertEqual("accepted", result["outcome"])
        self.assertEqual(1, self.fixture.posts)
        self.assert_private(result)

    def test_history_stable_identity_execution_and_revision_changes_refuse_mutation(self):
        for target, field, before, after in (
                ("trigger", "status", "Enabled", "Disabled"),
                ("trigger", "state", "Enabled", "Disabled"),
                ("trigger", "changedTime", "2026-10-01", "2026-10-02"),
                ("trigger", "workflowVersion", "v1", "v2"),
                ("history", "status", "Succeeded", "Failed"),
                ("history", "etag", '"one"', '"two"'),
                ("history", "workflowVersion", "v1", "v2"),
                ("history", "run", {"id": "run1"}, {"id": "run2"}),
                ("history", "fired", True, False)):
            self.fixture.trigger_override = {"name": "manual", "properties": {}}
            self.fixture.history_override = self.fixture.history()
            selected = self.fixture.trigger_override if target == "trigger" else self.fixture.history_override
            selected["properties"][field] = before
            self.confirm.side_effect = lambda *_args: selected["properties"].update({field: after})
            with self.subTest(target=target, field=field):
                result = self.resubmit()
                self.assertEqual(1, result["exitCode"])
                self.assertEqual("historyNotFired" if field == "fired" else "changed", result["error"]["kind"])
                self.assertEqual(0, self.fixture.posts)
        for target in ("trigger", "history"):
            self.fixture.trigger_override = {"name": "manual", "properties": {}}
            self.fixture.history_override = self.fixture.history()
            selected = self.fixture.trigger_override if target == "trigger" else self.fixture.history_override
            self.confirm.side_effect = lambda *_args: selected.update(id="/workflows/other/triggers/manual")
            with self.subTest(target=target):
                result = self.resubmit()
                self.assertEqual(1, result["exitCode"])
                self.assertEqual(0, self.fixture.posts)

    def test_history_content_hash_snapshot_is_not_aliased_to_the_read_response(self):
        self.fixture.history_override = self.fixture.history()
        self.fixture.history_override["properties"]["outputsLink"]["contentHash"] = {
            "algorithm": "sha256", "value": "original"}

        def change(*_args):
            self.fixture.history_override["properties"]["outputsLink"]["contentHash"]["value"] = "changed"

        self.confirm.side_effect = change
        result = self.resubmit()
        self.assertEqual("changed", result["error"]["kind"])
        self.assertEqual(0, self.fixture.posts)

    def test_resubmit_malformed_ambiguous_and_mismatching_histories_fail_before_post(self):
        cases = [{}, {"name": "other", "properties": {"fired": True}},
                 {"name": "different-history", "properties": []},
                 {"name": "different-history", "properties": {"fired": False}},
                 {"name": "different-history", "properties": {"fired": "true"}},
                 {"name": "different-history", "Name": "other", "properties": {"fired": True}}]
        for payload in cases:
            with self.subTest(payload=payload):
                self.fixture.history_override = payload
                result = self.resubmit()
                self.assertEqual(1, result["exitCode"])
                self.assert_private(result)
        self.assertEqual(0, self.fixture.posts)
        self.confirm.assert_not_called()

    def test_explicit_history_is_verified_without_listing(self):
        result = self.resubmit(history_name="retained-history")
        self.assertEqual("retained-history", result["triggerHistoryId"])
        self.assertEqual(0, self.fixture.pages)

    def test_retention_change_after_confirmation_prevents_post(self):
        self.confirm.side_effect = lambda *_args: setattr(
            self.fixture, "history", lambda *_args: ExecutionFixture.history(run="different-run"))
        result = self.resubmit()
        self.assertEqual("changed", result["error"]["kind"])
        self.assertEqual(0, self.fixture.posts)

    def test_deadline_failures_do_not_trigger_mutation_retries(self):
        for operation in (self.wait, self.cancel, self.resubmit):
            self.fixture.failure = lambda *_args: transport.DeadlineExpired()
            result = operation()
            self.assertEqual(2, result["exitCode"])
        self.assertEqual(0, self.fixture.posts)

    def test_service_uuid_correlations_are_exposed_but_authored_prose_is_not(self):
        correlation = "c8067064-38d5-4c22-a303-520431b08814"
        self.fixture.run_override = {"name": "source-run", "properties": {
            "status": "Succeeded", "correlationId": correlation, "outputs": {"secret": PRIVATE}}}
        self.assertEqual(correlation, self.wait()["runCorrelationId"])
        self.fixture.run_override["properties"]["correlationId"] = PRIVATE
        result = self.wait()
        self.assertIsNone(result["runCorrelationId"])
        self.assert_private(result)

    def test_shared_target_conflicts_rejected_for_all_execution_handlers(self):
        for handler, arguments in ((custom.run_wait, ("hello", "source-run")),
                                   (custom.run_cancel, ("hello", "source-run")),
                                   (custom.trigger_history_resubmit, ("hello", "manual", "different-history"))):
            with self.subTest(handler=handler):
                with self.assertRaises(MutuallyExclusiveArgumentError):
                    handler(self.cmd, *arguments, local=True, resource_group_name="rg", name="app")
                with self.assertRaises(MutuallyExclusiveArgumentError):
                    handler(self.cmd, *arguments, context="saved", local=True)


class ExecutionTransportTests(unittest.TestCase):
    def setUp(self):
        self.cli = get_default_cli()
        self.cmd = SimpleNamespace(cli_ctx=self.cli)
        self.client = SiteRuntimeClient(self.cmd, "http://localhost:17071", host_key=PRIVATE)
        self.response = Response()
        self.response.status_code = 200
        self.response._content = b'{"name":"hello"}'
        self.response._content_consumed = True
        self.send_patch = patch("requests.Session.send", autospec=True, return_value=self.response)
        self.send = self.send_patch.start()
        self.addCleanup(self.send_patch.stop)

    def request(self, method="GET", path="workflows/hello"):
        return transport.ExecutionTransport(self.client).request(
            method, path, transport.time.monotonic() + 30)

    def test_deadline_pools_are_session_scoped_and_do_not_change_other_requests(self):
        standard = transport.PoolManager()
        self.addCleanup(standard.clear)
        before = dict(standard.pool_classes_by_scheme)
        adapter = transport._deadline_adapter(time.monotonic() + 5)
        self.addCleanup(adapter.close)
        proxy = adapter.proxy_manager_for("http://127.0.0.1:1")
        self.assertEqual(before, standard.pool_classes_by_scheme)
        self.assertIsNot(standard.pool_classes_by_scheme, adapter.poolmanager.pool_classes_by_scheme)
        self.assertIsNot(standard.pool_classes_by_scheme, proxy.pool_classes_by_scheme)
        self.assertEqual(0, adapter.max_retries.total)

    def test_proxy_pool_specializations_are_preserved_and_wrapped_only_once(self):
        standard = transport.PoolManager()
        self.addCleanup(standard.clear)
        base = standard.pool_classes_by_scheme["http"]

        class SpecializedConnection(base.ConnectionCls):
            pass

        class SpecializedPool(base):
            ConnectionCls = SpecializedConnection

        manager = SimpleNamespace(pool_classes_by_scheme={"http": SpecializedPool})
        adapter = transport._deadline_adapter(time.monotonic() + 5)
        self.addCleanup(adapter.close)
        with patch.object(transport.HTTPAdapter, "proxy_manager_for", return_value=manager):
            first = adapter.proxy_manager_for("http://127.0.0.1:1")
            wrapped = first.pool_classes_by_scheme["http"]
            self.assertTrue(issubclass(wrapped, SpecializedPool))
            self.assertTrue(issubclass(wrapped.ConnectionCls, SpecializedConnection))
            self.assertIs(wrapped, adapter.proxy_manager_for("http://127.0.0.1:1").pool_classes_by_scheme["http"])

    def test_local_header_key_timeout_no_redirect_no_proxy_or_login(self):
        with patch.object(transport, "Profile", side_effect=AssertionError("No local login")):
            receipt = self.request()
        self.assertEqual(200, receipt["statusCode"])
        session, prepared = self.send.call_args.args
        self.assertFalse(session.trust_env)
        self.assertEqual(PRIVATE, prepared.headers["x-functions-key"])
        self.assertEqual("identity", prepared.headers["Accept-Encoding"])
        self.assertNotIn(PRIVATE, prepared.url)
        self.assertFalse(self.send.call_args.kwargs["allow_redirects"])
        self.assertTrue(self.send.call_args.kwargs["stream"])
        timeout = self.send.call_args.kwargs["timeout"]
        self.assertEqual(5, timeout.total)
        self.assertEqual({"api-version": ["2024-11-01"]}, parse_qs(urlsplit(prepared.url).query))

    def test_cloud_reuses_selected_profile_token_and_arm_site_target(self):
        self.client = SiteRuntimeClient(self.cmd, SITE)
        with patch.object(transport, "Profile") as profile:
            profile.return_value.get_raw_token.return_value = (("Bearer", PRIVATE, None), None, None)
            self.request()
            profile.return_value.get_raw_token.assert_called_once_with(
                self.cli.cloud.endpoints.active_directory_resource_id, subscription="sub")
        prepared = self.send.call_args.args[1]
        self.assertEqual("Bearer " + PRIVATE, prepared.headers["Authorization"])
        self.assertNotIn("x-functions-key", prepared.headers)
        self.assertTrue(prepared.url.startswith(self.cli.cloud.endpoints.resource_manager.rstrip("/") + SITE))

    def test_netrc_cannot_replace_cloud_bearer_auth_but_environment_proxy_and_ca_survive(self):
        self.client = SiteRuntimeClient(self.cmd, SITE)
        with tempfile.TemporaryDirectory() as directory:
            netrc = Path(directory) / "credentials"
            ca_bundle = str(Path(directory) / "test-ca.pem")
            host = urlsplit(self.cli.cloud.endpoints.resource_manager).hostname
            for entry in ("machine " + host, "default"):
                netrc.write_text(entry + " login synthetic-user password synthetic-password\n", encoding="ascii")
                for method in ("GET", "POST"):
                    with self.subTest(entry=entry, method=method), \
                            patch.dict(os.environ, {"NETRC": str(netrc), "REQUESTS_CA_BUNDLE": ca_bundle,
                                                    "HTTPS_PROXY": "http://127.0.0.1:1",
                                                    "https_proxy": "http://127.0.0.1:1",
                                                    "NO_PROXY": "", "no_proxy": ""}), \
                            patch.object(transport, "Profile") as profile:
                        profile.return_value.get_raw_token.return_value = (("Bearer", PRIVATE, None), None, None)
                        self.send.reset_mock()
                        self.response._content = b"" if method == "POST" else b'{"name":"hello"}'
                        self.request(method)
                        session, prepared = self.send.call_args.args
                        self.assertTrue(session.trust_env)
                        self.assertEqual("Bearer " + PRIVATE, prepared.headers["Authorization"])
                        self.assertEqual("http://127.0.0.1:1", self.send.call_args.kwargs["proxies"]["https"])
                        self.assertEqual(ca_bundle, self.send.call_args.kwargs["verify"])
                        self.assertEqual(1, self.send.call_count)
                        self.assertFalse(self.send.call_args.kwargs["allow_redirects"])

    def test_nonempty_post_bodies_are_not_empty_receipts_or_decoded_json(self):
        for status in (200, 202, 204):
            for raw in (b"null", b" null \n", b" ", b"{}", b"[]", json.dumps(PRIVATE).encode()):
                with self.subTest(status=status, raw=raw):
                    self.response.status_code = status
                    self.response._content = raw
                    self.send.reset_mock()
                    with patch.object(transport, "strict_json_loads") as decode:
                        with self.assertRaises(transport.ExecutionError) as caught:
                            self.request("POST")
                    self.assertEqual("invalidResponse", caught.exception.kind)
                    self.assertFalse(caught.exception.before_send)
                    self.assertNotIn(PRIVATE, str(caught.exception))
                    decode.assert_not_called()
                    self.send.assert_called_once()
        self.response.status_code = 200
        self.response._content = b"null"
        self.assertIsNone(self.request("GET")["payload"])

    def test_raw_null_post_responses_leave_all_mutations_uncertain_without_retry(self):
        operations = (
            (execution.cancel_run, ("hello", "source-run"), {"wait": False}, (200, 202, 204), 4),
            (execution.cancel_run, ("hello", "source-run"), {"wait": True}, (200, 202, 204), 4),
            (execution.resubmit_trigger_history, ("hello", "manual", "different-history"), {}, (202,), 6),
            (execution.resubmit_run_action, ("hello", "source-run", "Send_HTTP"), {}, (202,), 6),
        )
        for operation, arguments, options, statuses, reads in operations:
            for status in statuses:
                for raw in (b"", b"null", b" null \n"):
                    with self.subTest(operation=operation.__name__, options=options, status=status, raw=raw):
                        fixture = ActionExecutionFixture()
                        if operation is execution.cancel_run:
                            fixture.statuses = ["Running"]
                        self.send.reset_mock()

                        def send(_session, prepared, **_kwargs):
                            path = urlsplit(prepared.url).path.split("/api/management/", 1)[1]
                            receipt = fixture.request(
                                prepared.method, path, time.monotonic() + 60,
                                body=json.loads(prepared.body) if prepared.body else None)
                            response = Response()
                            response.status_code = status if prepared.method == "POST" else receipt["statusCode"]
                            response._content = raw if prepared.method == "POST" else json.dumps(receipt["payload"]).encode()
                            response._content_consumed = True
                            response.headers.update(receipt["headers"])
                            return response

                        self.send.side_effect = send
                        with patch.object(transport, "Profile") as profile, \
                                patch.object(execution, "user_confirmation"):
                            profile.return_value.get_raw_token.return_value = (("Bearer", PRIVATE, None), None, None)
                            result = operation(SiteRuntimeClient(self.cmd, SITE), *arguments, yes=True, **options)
                        self.assertEqual(1, fixture.posts)
                        self.assertEqual(1, sum(call.args[1].method == "POST" for call in self.send.call_args_list))
                        self.assertNotIn(PRIVATE, json.dumps(result))
                        if not raw:
                            self.assertTrue(result["requestAcknowledged"])
                            self.assertEqual(0, result["exitCode"])
                            continue
                        self.assertEqual("observationFailed", result["outcome"])
                        self.assertEqual(1, result["exitCode"])
                        self.assertEqual("invalidResponse", (result["error"] or {}).get("kind"))
                        self.assertFalse(result["requestAcknowledged"])
                        self.assertEqual("cancelAttempted" if operation is execution.cancel_run else "resubmitAttempted",
                                         result["action"])
                        self.assertIn("may have been accepted", result["message"])
                        self.assertIn("No retry", result["message"])
                        self.assertIsNone(result.get("newRunId"))
                        self.assertEqual(reads + 1, self.send.call_count)

    def test_cloud_resubmit_matches_full_history_id_through_prepared_transport(self):
        fixture = ExecutionFixture()

        def history(history="different-history", run="source-run", fired=True):
            payload = ExecutionFixture.history(history, run, fired)
            payload["properties"]["run"] = {
                "name": "source-run",
                "id": SITE + "/hostruntime/runtime/webhooks/workflow/api/management/workflows/hello/runs/source-run"}
            return payload

        fixture.history = history
        fixture.history_pages = [{"value": [history()]}]

        def send(_session, prepared, **kwargs):
            self.assertFalse(kwargs["allow_redirects"])
            self.assertEqual("Bearer " + PRIVATE, prepared.headers["Authorization"])
            path = urlsplit(prepared.url).path.split("/api/management/", 1)[1]
            receipt = fixture.request(prepared.method, path, time.monotonic() + 60)
            response = Response()
            response.status_code = receipt["statusCode"]
            response._content = json.dumps(receipt["payload"]).encode() if receipt["payload"] is not None else b""
            response._content_consumed = True
            response.headers.update(receipt["headers"])
            return response

        self.send.side_effect = send
        with patch.object(transport, "Profile") as profile, patch.object(execution, "user_confirmation"):
            profile.return_value.get_raw_token.return_value = (("Bearer", PRIVATE, None), None, None)
            result = execution.resubmit_trigger_history(
                SiteRuntimeClient(self.cmd, SITE), "hello", "manual", "different-history", yes=True)
        self.assertEqual("accepted", result["outcome"])
        self.assertEqual("new-run", result["newRunId"])
        self.assertEqual(1, fixture.posts)
        self.assertNotIn(PRIVATE, json.dumps(result))

    def test_cloud_observation_reacquires_profile_tokens_across_long_polling(self):
        client = SiteRuntimeClient(self.cmd, SITE)
        execution_transport = transport.ExecutionTransport(client)
        clock = Clock()
        tokens = ("first-token", "refreshed-token", "latest-token")
        with patch.object(transport, "Profile") as profile, \
                patch.object(transport.time, "monotonic", clock.monotonic):
            profile.return_value.get_raw_token.side_effect = [
                (("Bearer", token, None), None, None) for token in tokens]
            for _ in tokens:
                execution_transport.request("GET", "workflows/hello/runs/run", 86500)
                clock.now += 3600
            self.assertEqual(3, profile.return_value.get_raw_token.call_count)
            for call in profile.return_value.get_raw_token.call_args_list:
                self.assertEqual((self.cli.cloud.endpoints.active_directory_resource_id,), call.args)
                self.assertEqual({"subscription": "sub"}, call.kwargs)
        self.assertEqual(["Bearer " + token for token in tokens],
                         [call.args[1].headers["Authorization"] for call in self.send.call_args_list])
        self.assertEqual(3, self.send.call_count)

    def test_later_token_acquisition_failure_never_reuses_stale_token_or_retries_post(self):
        execution_transport = transport.ExecutionTransport(SiteRuntimeClient(self.cmd, SITE))
        with patch.object(transport, "Profile") as profile:
            profile.return_value.get_raw_token.side_effect = [
                (("Bearer", PRIVATE, None), None, None), CLIError(PRIVATE)]
            execution_transport.request("GET", "workflows/hello", time.monotonic() + 30)
            with self.assertRaises(transport.ExecutionError) as caught:
                execution_transport.request("POST", "workflows/hello/runs/run/cancel", time.monotonic() + 30)
        self.assertEqual("authentication", caught.exception.kind)
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(1, self.send.call_count)
        self.assertEqual("GET", self.send.call_args.args[1].method)

    def test_token_acquisition_overall_deadline_is_rechecked_before_sending(self):
        execution_transport = transport.ExecutionTransport(SiteRuntimeClient(self.cmd, SITE))
        clock = Clock()

        def acquire(*_args, **_kwargs):
            clock.now += 31
            return (("Bearer", PRIVATE, None), None, None)

        with patch.object(transport, "Profile") as profile, \
                patch.object(transport.time, "monotonic", clock.monotonic):
            profile.return_value.get_raw_token.side_effect = acquire
            with self.assertRaises(transport.DeadlineExpired):
                execution_transport.request("POST", "workflows/hello/runs/run/cancel", 130)
        self.send.assert_not_called()

    def test_authentication_failure_is_safe_and_never_sends(self):
        self.client = SiteRuntimeClient(self.cmd, SITE)
        with patch.object(transport, "Profile") as profile:
            profile.return_value.get_raw_token.side_effect = CLIError(PRIVATE)
            with self.assertRaises(transport.ExecutionError) as caught:
                self.request("POST")
        self.assertEqual("authentication", caught.exception.kind)
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.send.assert_not_called()

    def test_mutation_token_failure_reports_no_submission_through_prepared_transport(self):
        for operation, preflight_reads in ((execution.cancel_run, 4), (execution.resubmit_trigger_history, 6)):
            with self.subTest(operation=operation.__name__):
                fixture = ExecutionFixture()
                fixture.statuses = ["Running"]
                self.send.reset_mock()

                def send(_session, prepared, **_kwargs):
                    path = urlsplit(prepared.url).path.split("/api/management/", 1)[1]
                    receipt = fixture.request(prepared.method, path, time.monotonic() + 60)
                    response = Response()
                    response.status_code = receipt["statusCode"]
                    response._content = json.dumps(receipt["payload"]).encode()
                    response._content_consumed = True
                    return response

                def token(*_args, **_kwargs):
                    if self.send.call_count == preflight_reads:
                        raise CLIError(PRIVATE)
                    return (("Bearer", PRIVATE, None), None, None)

                self.send.side_effect = send
                with patch.object(transport, "Profile") as profile, \
                        patch.object(execution, "user_confirmation"):
                    profile.return_value.get_raw_token.side_effect = token
                    arguments = ("hello", "source-run") if operation is execution.cancel_run else (
                        "hello", "manual", "different-history")
                    result = operation(SiteRuntimeClient(self.cmd, SITE), *arguments, yes=True)
                self.assertEqual("readFailed", result["outcome"])
                self.assertIsNone(result["action"])
                self.assertFalse(result["requestAcknowledged"])
                self.assertEqual(1, result["exitCode"])
                self.assertEqual("authentication", (result["error"] or {}).get("kind"))
                self.assertIn("No mutation request was sent", result["message"])
                self.assertEqual(0, fixture.posts)
                self.assertEqual(preflight_reads, self.send.call_count)
                self.assertTrue(all(call.args[1].method == "GET" for call in self.send.call_args_list))
                self.assertNotIn(PRIVATE, json.dumps(result))

    def test_observation_token_failure_preserves_acknowledged_cancellation(self):
        for wait in (False, True):
            with self.subTest(wait=wait):
                fixture = ExecutionFixture()
                fixture.statuses = ["Running"]
                self.send.reset_mock()

                def send(_session, prepared, **_kwargs):
                    path = urlsplit(prepared.url).path.split("/api/management/", 1)[1]
                    receipt = fixture.request(prepared.method, path, time.monotonic() + 60)
                    response = Response()
                    response.status_code = receipt["statusCode"]
                    response._content = (json.dumps(receipt["payload"]).encode()
                                         if receipt["payload"] is not None else b"")
                    response._content_consumed = True
                    return response

                def token(*_args, **_kwargs):
                    if fixture.posts:
                        raise CLIError(PRIVATE)
                    return (("Bearer", PRIVATE, None), None, None)

                self.send.side_effect = send
                with patch.object(transport, "Profile") as profile, \
                        patch.object(execution, "user_confirmation"):
                    profile.return_value.get_raw_token.side_effect = token
                    result = execution.cancel_run(
                        SiteRuntimeClient(self.cmd, SITE), "hello", "source-run", yes=True, wait=wait)
                self.assertEqual("observationFailed", result["outcome"])
                self.assertEqual("cancelRequested", result["action"])
                self.assertTrue(result["requestAcknowledged"])
                self.assertEqual("authentication", (result["error"] or {}).get("kind"))
                self.assertIn("was acknowledged", result["message"])
                self.assertNotIn("No mutation request was sent", result["message"])
                self.assertEqual(1, fixture.posts)
                self.assertEqual(5, self.send.call_count)
                self.assertNotIn(PRIVATE, json.dumps(result))

    def test_mutation_deadlines_before_send_do_not_report_attempts(self):
        real_adapter = transport._deadline_adapter
        for operation, reads, options in (
                (execution.cancel_run, 4, {"wait": False}),
                (execution.cancel_run, 4, {"wait": True}),
                (execution.resubmit_trigger_history, 6, {})):
            for stage in ("credential", "setup"):
                with self.subTest(operation=operation.__name__, options=options, stage=stage):
                    clock = Clock()
                    fixture = ExecutionFixture()
                    fixture.statuses = ["Running"]
                    self.send.reset_mock()

                    def send(_session, prepared, **_kwargs):
                        path = urlsplit(prepared.url).path.split("/api/management/", 1)[1]
                        receipt = fixture.request(prepared.method, path, clock.now + 60)
                        response = Response()
                        response.status_code = receipt["statusCode"]
                        response._content = json.dumps(receipt["payload"]).encode()
                        response._content_consumed = True
                        return response

                    def token(*_args, **_kwargs):
                        if stage == "credential" and self.send.call_count == reads:
                            clock.now += 61
                        return (("Bearer", PRIVATE, None), None, None)

                    def adapter(deadline):
                        if stage == "setup" and self.send.call_count == reads:
                            clock.now += 61
                        return real_adapter(deadline)

                    self.send.side_effect = send
                    with patch.object(transport, "Profile") as profile, \
                            patch.object(transport.time, "monotonic", clock.monotonic), \
                            patch.object(transport, "_deadline_adapter", side_effect=adapter), \
                            patch.object(execution, "user_confirmation"):
                        profile.return_value.get_raw_token.side_effect = token
                        arguments = ("hello", "source-run") if operation is execution.cancel_run else (
                            "hello", "manual", "different-history")
                        result = operation(
                            SiteRuntimeClient(self.cmd, SITE), *arguments, yes=True, **options)
                    self.assertEqual("requestDeadlineExpired", result["outcome"])
                    self.assertIsNone(result["action"])
                    self.assertFalse(result["requestAcknowledged"])
                    self.assertEqual(2, result["exitCode"])
                    self.assertNotIn("uncertain", result["message"])
                    self.assertEqual(0, fixture.posts)
                    self.assertEqual(reads, self.send.call_count)
                    self.assertNotIn(PRIVATE, json.dumps(result))

    def test_presend_observation_deadline_preserves_cancellation_ack(self):
        for wait in (False, True):
            with self.subTest(wait=wait):
                clock = Clock()
                fixture = ExecutionFixture()
                fixture.statuses = ["Running"]
                self.send.reset_mock()

                def send(_session, prepared, **_kwargs):
                    path = urlsplit(prepared.url).path.split("/api/management/", 1)[1]
                    receipt = fixture.request(prepared.method, path, clock.now + 60)
                    response = Response()
                    response.status_code = receipt["statusCode"]
                    response._content = (json.dumps(receipt["payload"]).encode()
                                         if receipt["payload"] is not None else b"")
                    response._content_consumed = True
                    return response

                def token(*_args, **_kwargs):
                    if fixture.posts:
                        clock.now += 301
                    return (("Bearer", PRIVATE, None), None, None)

                self.send.side_effect = send
                with patch.object(transport, "Profile") as profile, \
                        patch.object(transport.time, "monotonic", clock.monotonic), \
                        patch.object(execution, "user_confirmation"):
                    profile.return_value.get_raw_token.side_effect = token
                    result = execution.cancel_run(
                        SiteRuntimeClient(self.cmd, SITE), "hello", "source-run", yes=True, wait=wait)
                self.assertEqual("waitTimedOut" if wait else "requestDeadlineExpired", result["outcome"])
                self.assertEqual("cancelRequested", result["action"])
                self.assertTrue(result["requestAcknowledged"])
                self.assertEqual(1, fixture.posts)
                self.assertEqual(5, self.send.call_count)

    def test_expired_transport_entry_and_setup_budget_are_known_unsent(self):
        real_adapter = transport._deadline_adapter
        for stage in ("entry", "setup"):
            with self.subTest(stage=stage):
                clock = Clock()
                self.send.reset_mock()

                def adapter(deadline):
                    clock.now += 6
                    return real_adapter(deadline)

                error_type = transport.DeadlineExpired if stage == "entry" else transport.ExecutionError
                with patch.object(transport.time, "monotonic", clock.monotonic), \
                        patch.object(transport, "_deadline_adapter", side_effect=adapter):
                    with self.assertRaises(error_type) as caught:
                        transport.ExecutionTransport(self.client).request(
                            "POST", "workflows/hello", 100 if stage == "entry" else 130)
                self.assertTrue(caught.exception.before_send)
                self.send.assert_not_called()

    def test_route_names_are_percent_quoted_without_new_paths(self):
        from azext_logicapp._runtime_client import trigger_history_resubmit_path
        self.response._content = b""
        self.request("POST", trigger_history_resubmit_path("hello", "trigger space", "history space"))
        self.assertIn("/triggers/trigger%20space/histories/history%20space/resubmit?",
                      self.send.call_args.args[1].url)

    def test_untrusted_slots_paths_and_hosts_rejected_before_network(self):
        for target in (SITE + "/slots/x", SITE + "?sig=x", "http://evil.invalid:1234",
                       "http://localhost:1234/other", "http://secret@localhost:1234"):
            with self.subTest(target=target):
                with self.assertRaises(InvalidArgumentValueError):
                    transport.ExecutionTransport(SiteRuntimeClient(self.cmd, target))
        self.send.assert_not_called()

    def test_http_failures_have_safe_classification_without_body_or_location(self):
        for status, kind in ((401, "unauthorized"), (403, "unauthorized"), (404, "notFound"),
                             (409, "conflict"), (429, "service"), (500, "service"), (302, "redirect")):
            with self.subTest(status=status):
                self.response.status_code = status
                self.response._content = PRIVATE.encode()
                self.response.headers["Location"] = "https://untrusted.invalid/?sig=" + PRIVATE
                with self.assertRaises(transport.ExecutionError) as caught:
                    self.request("POST")
                self.assertEqual(kind, caught.exception.kind)
                self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(7, self.send.call_count)

    def test_timeout_and_connect_errors_no_retry_or_secret_messages(self):
        for error, kind in ((ReadTimeout(PRIVATE), "requestTimeout"),
                            (RequestsConnectionError(PRIVATE), "unavailable")):
            with self.subTest(kind=kind):
                self.send.side_effect = error
                with self.assertRaises(transport.ExecutionError) as caught:
                    self.request("POST")
                self.assertEqual(kind, caught.exception.kind)
                self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(2, self.send.call_count)

    def test_stream_read_timeout_wrapped_by_requests_is_classified(self):
        self.response.iter_content = Mock(side_effect=RequestsConnectionError(
            ReadTimeoutError(None, "https://untrusted.invalid/?sig=" + PRIVATE, PRIVATE)))
        with self.assertRaises(transport.ExecutionError) as caught:
            self.request()
        self.assertEqual("requestTimeout", caught.exception.kind)
        self.assertNotIn(PRIVATE, str(caught.exception))

    def test_trickling_response_is_bounded_by_request_budget(self):
        clock = Clock()

        def chunks(**_kwargs):
            for _ in range(20):
                clock.now += 1
                yield b" "

        self.response.iter_content = chunks
        with patch.object(transport.time, "monotonic", clock.monotonic):
            with self.assertRaises(transport.ExecutionError) as caught:
                self.request()
        self.assertEqual("requestTimeout", caught.exception.kind)
        self.assertLessEqual(clock.now, 105)

    def test_maximum_valid_response_uses_bounded_buffers_not_byte_iterations(self):
        self.response._content = b'"' + b"x" * (transport.MAX_RESPONSE_BYTES - 2) + b'"'
        original = self.response.iter_content
        self.response.iter_content = Mock(wraps=original)
        original_clock = transport.time.monotonic
        with patch.object(transport.time, "monotonic", wraps=original_clock) as clock:
            result = self.request()
        self.response.iter_content.assert_called_once_with(chunk_size=64 * 1024)
        self.assertEqual(transport.MAX_RESPONSE_BYTES - 2, len(result["payload"]))
        self.assertLess(clock.call_count, 64)

    def test_execution_rejects_duplicate_and_nonfinite_json_without_echoing_payload(self):
        samples = (
            b'{"status":"Running","status":"Succeeded"}', b'{"nested":{"x":1,"x":2}}',
            b'{"value":NaN}', b'{"value":Infinity}', b'{"value":-Infinity}', b'{"value":1e999}',
        )
        for raw in samples:
            with self.subTest(raw=raw):
                self.response._content = raw
                with self.assertRaises(transport.ExecutionError) as caught:
                    self.request()
                self.assertEqual("invalidResponse", caught.exception.kind)
                self.assertNotIn(raw.decode(), str(caught.exception))

    def test_encoded_responses_are_rejected_before_decoding_or_body_read_without_retry(self):
        for encoding in ("gzip", "deflate", "br", "gzip, identity", PRIVATE):
            for method in ("GET", "POST"):
                with self.subTest(encoding=encoding, method=method):
                    self.response.headers["Content-Encoding"] = encoding
                    self.response.iter_content = Mock(side_effect=AssertionError("Do not consume encoded bodies"))
                    self.send.reset_mock()
                    with self.assertRaises(transport.ExecutionError) as caught:
                        self.request(method)
                    self.assertEqual("invalidResponse", caught.exception.kind)
                    self.assertNotIn(PRIVATE, str(caught.exception))
                    self.response.iter_content.assert_not_called()
                    self.send.assert_called_once()

    def test_explicit_identity_encoding_preserves_json_and_empty_acknowledgements(self):
        for encoding in ("identity", "Identity", " identity ", ""):
            for status, body in ((200, b'{"name":"hello"}'), (202, b""), (204, b"")):
                with self.subTest(encoding=encoding, status=status):
                    self.response.headers["Content-Encoding"] = encoding
                    self.response.status_code = status
                    self.response._content = body
                    receipt = self.request("GET" if body else "POST")
                    self.assertEqual(status, receipt["statusCode"])
                    self.assertEqual({"name": "hello"} if body else None, receipt["payload"])

    def test_response_deadline_expired_before_empty_ack_is_not_success(self):
        clock = Clock()
        self.response._content = b""

        def send(*_args, **_kwargs):
            clock.now += 2
            return self.response

        self.send.side_effect = send
        with patch.object(transport.time, "monotonic", clock.monotonic):
            with self.assertRaises(transport.DeadlineExpired):
                transport.ExecutionTransport(self.client).request("POST", "workflows/hello", 101)

    def test_empty_post_ack_eof_rechecks_request_and_overall_deadlines_without_retry(self):
        for status in (202, 204):
            for deadline, elapsed, error_type in (
                    (130, 5, transport.ExecutionError), (130, 6, transport.ExecutionError),
                    (101, 1, transport.DeadlineExpired), (101, 6, transport.DeadlineExpired)):
                with self.subTest(status=status, deadline=deadline, elapsed=elapsed):
                    clock = Clock()
                    self.response.status_code = status
                    self.send.reset_mock()

                    def chunks(**_kwargs):
                        clock.now += elapsed
                        yield from ()

                    self.response.iter_content = chunks
                    with patch.object(transport.time, "monotonic", clock.monotonic):
                        with self.assertRaises(error_type) as caught:
                            transport.ExecutionTransport(self.client).request(
                                "POST", "workflows/hello", deadline)
                    if error_type is transport.ExecutionError:
                        self.assertEqual("requestTimeout", caught.exception.kind)
                    self.assertFalse(caught.exception.before_send)
                    self.send.assert_called_once()
                    self.assertEqual("POST", self.send.call_args.args[1].method)

    def test_empty_post_ack_before_deadlines_remains_valid(self):
        for status in (202, 204):
            with self.subTest(status=status):
                clock = Clock()
                self.response.status_code = status
                self.send.reset_mock()

                def chunks(**_kwargs):
                    clock.now += 4
                    yield from ()

                self.response.iter_content = chunks
                with patch.object(transport.time, "monotonic", clock.monotonic):
                    receipt = self.request("POST")
                self.assertEqual(status, receipt["statusCode"])
                self.assertIsNone(receipt["payload"])
                self.send.assert_called_once()

    def test_deferred_headers_and_empty_204_share_original_request_budget(self):
        clock = Clock()
        self.response.status_code = 204

        def send(*_args, **_kwargs):
            clock.now += 4
            return self.response

        def chunks(**_kwargs):
            clock.now += 2
            yield from ()

        self.send.side_effect = send
        self.response.iter_content = chunks
        with patch.object(transport.time, "monotonic", clock.monotonic):
            with self.assertRaises(transport.ExecutionError) as caught:
                self.request("POST")
        self.assertEqual("requestTimeout", caught.exception.kind)
        self.send.assert_called_once()

    def test_execution_never_acknowledges_late_empty_post_receipts(self):
        for operation, statuses in ((execution.cancel_run, (202, 204)), (execution.resubmit_trigger_history, (202,))):
            for status in statuses:
                for elapsed, exit_code in (
                        (transport.REQUEST_TIMEOUT + 1, 1), (execution._PREFLIGHT_TIMEOUT + 1, 2)):
                    with self.subTest(operation=operation.__name__, status=status, elapsed=elapsed):
                        clock = Clock()
                        fixture = ExecutionFixture()
                        fixture.statuses = ["Running"]
                        self.response.status_code = status
                        self.send.reset_mock()

                        def chunks(**_kwargs):
                            clock.now += elapsed
                            yield from ()

                        def request(method, path, deadline, params=None):
                            if method == "POST":
                                return transport.ExecutionTransport(self.client).request(method, path, deadline)
                            return fixture.request(method, path, deadline, params)

                        self.response.iter_content = chunks
                        with patch.object(transport.time, "monotonic", clock.monotonic), \
                                patch.object(execution, "ExecutionTransport",
                                             return_value=SimpleNamespace(request=request)), \
                                patch.object(execution, "user_confirmation"):
                            arguments = ("hello", "source-run") if operation is execution.cancel_run else (
                                "hello", "manual", "different-history")
                            result = operation(self.client, *arguments, yes=True)
                        self.assertEqual(exit_code, result["exitCode"])
                        self.assertFalse(result["requestAcknowledged"])
                        self.assertEqual(
                            "cancelAttempted" if operation is execution.cancel_run else "resubmitAttempted",
                            result["action"])
                        if exit_code == 1:
                            self.assertEqual("requestTimeout", result["error"]["kind"])
                        else:
                            self.assertEqual("requestDeadlineExpired", result["outcome"])
                        if operation is execution.resubmit_trigger_history:
                            self.assertIsNone(result["newRunId"])
                        self.send.assert_called_once()
                        self.assertEqual("POST", self.send.call_args.args[1].method)

    def test_final_eof_after_last_chunk_cannot_return_a_late_response(self):
        clock = Clock()

        def chunks(**_kwargs):
            yield b"{}"
            clock.now += 6

        self.response.iter_content = chunks
        with patch.object(transport.time, "monotonic", clock.monotonic):
            with self.assertRaises(transport.ExecutionError) as caught:
                self.request("POST")
        self.assertEqual("requestTimeout", caught.exception.kind)
        self.send.assert_called_once()

    def test_json_decoding_cannot_return_a_response_after_deadline(self):
        clock = Clock()
        original_loads = transport.strict_json_loads

        def decode(content):
            clock.now += 6
            return original_loads(content)

        with patch.object(transport.time, "monotonic", clock.monotonic), \
                patch.object(transport, "strict_json_loads", side_effect=decode):
            with self.assertRaises(transport.ExecutionError) as caught:
                self.request("GET")
        self.assertEqual("requestTimeout", caught.exception.kind)
        self.send.assert_called_once()

    def test_http_debug_filter_is_scoped_and_prevents_token_logging(self):
        logger = logging.getLogger("urllib3.connectionpool")
        records = []
        handler = logging.Handler()
        handler.emit = records.append
        prior = logger.level
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        before = list(logger.filters)
        self.addCleanup(logger.setLevel, prior)
        self.addCleanup(logger.removeHandler, handler)

        def send(*_args, **_kwargs):
            logger.debug(PRIVATE)
            return self.response

        self.send.side_effect = send
        self.request()
        self.assertEqual([], records)
        self.assertEqual(before, logger.filters)

    def test_invalid_json_and_oversized_responses_are_rejected(self):
        for body in (PRIVATE.encode(), b"x" * (transport.MAX_RESPONSE_BYTES + 1)):
            with self.subTest(length=len(body)):
                self.response._content = body
                with self.assertRaises(transport.ExecutionError) as caught:
                    self.request()
                self.assertEqual("invalidResponse", caught.exception.kind)
                self.assertNotIn(PRIVATE, str(caught.exception))

    def test_expired_deadline_never_sends(self):
        with self.assertRaises(transport.DeadlineExpired):
            transport.ExecutionTransport(self.client).request("POST", "workflows/hello",
                                                              transport.time.monotonic() - 1)
        self.send.assert_not_called()

    def test_small_remaining_budget_caps_network_timeout(self):
        transport.ExecutionTransport(self.client).request(
            "GET", "workflows/hello", transport.time.monotonic() + 0.25)
        self.assertLessEqual(self.send.call_args.kwargs["timeout"].total, 0.25)


class NativeExecutionStreamTests(unittest.TestCase):
    def test_proxy_connect_trickling_is_bounded_before_tls_or_target_requests(self):
        stop = threading.Event()
        finished = threading.Event()
        observed = []

        class Handler(BaseHTTPRequestHandler):
            def do_CONNECT(self):
                self.connection.settimeout(0.5)
                observed.append(self.headers.get("Authorization"))
                try:
                    for byte in b"HTTP/1.0 200 Connection established\r\n\r\n":
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        if stop.wait(0.08):
                            break
                except (BrokenPipeError, ConnectionResetError, TimeoutError):
                    pass
                finally:
                    finished.set()

            def log_message(self, *_args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.addCleanup(stop.set)
        endpoints = SimpleNamespace(resource_manager="https://localhost:16999",
                                    active_directory_resource_id="synthetic-audience")
        client = SiteRuntimeClient(SimpleNamespace(cli_ctx=SimpleNamespace(
            cloud=SimpleNamespace(endpoints=endpoints))), SITE)
        session_class = transport.requests.Session

        def session():
            result = session_class()
            result.trust_env = False
            result.proxies = {"https": "http://127.0.0.1:{}".format(server.server_port)}
            return result

        with patch.object(transport, "Profile") as profile, \
                patch.object(transport.requests, "Session", side_effect=session), \
                patch.object(transport, "REQUEST_TIMEOUT", 1):
            profile.return_value.get_raw_token.return_value = (("Bearer", PRIVATE, None), None, None)
            started = time.monotonic()
            with self.assertRaises(transport.ExecutionError) as caught:
                transport.ExecutionTransport(client).request("POST", "workflows/hello", started + 5)
        elapsed = time.monotonic() - started
        stop.set()
        self.assertEqual("requestTimeout", caught.exception.kind)
        self.assertGreater(elapsed, 0.8)
        self.assertLess(elapsed, 1.8)
        self.assertEqual([None], observed)
        self.assertTrue(finished.wait(2))

    def test_real_trickled_headers_obey_overall_and_request_budgets_without_retry(self):
        for overall in (True, False):
            with self.subTest(overall=overall):
                stop = threading.Event()
                finished = threading.Event()
                observed = []

                class Handler(BaseHTTPRequestHandler):
                    def do_POST(self):
                        self.connection.settimeout(0.5)
                        observed.append(self.path)
                        try:
                            for byte in b"HTTP/1.0 202 Accepted\r\nContent-Length: 0\r\n\r\n":
                                self.wfile.write(bytes([byte]))
                                self.wfile.flush()
                                if stop.wait(0.08):
                                    break
                        except (BrokenPipeError, ConnectionResetError, TimeoutError):
                            pass
                        finally:
                            finished.set()

                    def log_message(self, *_args):
                        pass

                server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                self.addCleanup(thread.join, 2)
                self.addCleanup(server.server_close)
                self.addCleanup(server.shutdown)
                self.addCleanup(stop.set)
                client = SiteRuntimeClient(SimpleNamespace(cli_ctx=get_default_cli()),
                                           "http://localhost:{}".format(server.server_port))
                started = time.monotonic()
                error_type = transport.DeadlineExpired if overall else transport.ExecutionError
                with patch.object(transport, "REQUEST_TIMEOUT", 1):
                    with self.assertRaises(error_type) as caught:
                        transport.ExecutionTransport(client).request(
                            "POST", "workflows/hello", started + (1 if overall else 5))
                elapsed = time.monotonic() - started
                stop.set()
                if not overall:
                    self.assertEqual("requestTimeout", caught.exception.kind)
                self.assertGreater(elapsed, 0.8)
                self.assertLess(elapsed, 1.8)
                self.assertEqual(1, len(observed))
                self.assertTrue(finished.wait(2))

    def test_native_https_preserves_certificate_verification_and_selected_profile(self):
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
        now = datetime.now(timezone.utc)
        certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                       .public_key(key.public_key()).serial_number(x509.random_serial_number())
                       .not_valid_before(now - timedelta(minutes=1))
                       .not_valid_after(now + timedelta(days=1))
                       .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), False)
                       .add_extension(x509.BasicConstraints(ca=True, path_length=0), True)
                       .sign(key, hashes.SHA256()))
        certificate_file = root / "certificate.pem"
        certificate_file.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        key_file = root / "key.pem"
        key_file.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                               serialization.PrivateFormat.PKCS8,
                                               serialization.NoEncryption()))
        observed = []
        trickle = threading.Event()
        stop = threading.Event()
        finished = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                observed.append((self.path, self.headers["Authorization"], self.headers["Accept-Encoding"]))
                if trickle.is_set():
                    self.connection.settimeout(0.5)
                    try:
                        for byte in b"HTTP/1.0 200 OK\r\nContent-Length: 0\r\n\r\n":
                            self.wfile.write(bytes([byte]))
                            self.wfile.flush()
                            if stop.wait(0.08):
                                break
                    except (BrokenPipeError, ConnectionResetError, TimeoutError):
                        pass
                    finally:
                        finished.set()
                    return
                body = b'{"name":"hello"}'
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(certificate_file), str(key_file))
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.addCleanup(stop.set)
        endpoints = SimpleNamespace(resource_manager="https://localhost:{}".format(server.server_port),
                                    active_directory_resource_id="synthetic-audience")
        client = SiteRuntimeClient(SimpleNamespace(cli_ctx=SimpleNamespace(
            cloud=SimpleNamespace(endpoints=endpoints))), SITE)
        session_class = transport.requests.Session

        def session(verify):
            result = session_class()
            result.trust_env = False
            result.verify = verify
            return result

        with patch.object(transport, "Profile") as profile:
            profile.return_value.get_raw_token.return_value = (("Bearer", PRIVATE, None), None, None)
            with patch.object(transport.requests, "Session", side_effect=lambda: session(str(certificate_file))):
                result = transport.ExecutionTransport(client).request(
                    "GET", "workflows/hello", time.monotonic() + 5)
            self.assertEqual({"name": "hello"}, result["payload"])
            self.assertEqual("Bearer " + PRIVATE, observed[0][1])
            self.assertEqual("identity", observed[0][2])
            profile.return_value.get_raw_token.assert_called_once_with("synthetic-audience", subscription="sub")
            with patch.object(transport.requests, "Session", side_effect=lambda: session(True)):
                with self.assertRaises(transport.ExecutionError) as caught:
                    transport.ExecutionTransport(client).request(
                        "GET", "workflows/hello", time.monotonic() + 5)
            self.assertEqual("unavailable", caught.exception.kind)
            self.assertNotIn(PRIVATE, str(caught.exception))
            self.assertEqual(1, len(observed))
            trickle.set()
            started = time.monotonic()
            with patch.object(transport.requests, "Session", side_effect=lambda: session(str(certificate_file))), \
                    patch.object(transport, "REQUEST_TIMEOUT", 1):
                with self.assertRaises(transport.ExecutionError) as caught:
                    transport.ExecutionTransport(client).request(
                        "GET", "workflows/hello", started + 5)
            elapsed = time.monotonic() - started
            stop.set()
            self.assertEqual("requestTimeout", caught.exception.kind)
            self.assertGreater(elapsed, 0.8)
            self.assertLess(elapsed, 1.8)
            self.assertEqual(2, len(observed))
            self.assertTrue(finished.wait(2))

    def test_real_trickled_gzip_is_rejected_without_waiting_for_decoder_output(self):
        observed = []
        stop = threading.Event()
        finished = threading.Event()
        body = gzip.compress(b'{"name":"hello","private":"do-not-expose"}')

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.connection.settimeout(0.5)
                observed.append(self.headers["Accept-Encoding"])
                try:
                    self.send_response(202)
                    self.send_header("Content-Encoding", "gzip")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    for byte in body:
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        if stop.wait(0.1):
                            break
                except (BrokenPipeError, ConnectionResetError, TimeoutError):
                    pass
                finally:
                    finished.set()

            def log_message(self, *_args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.addCleanup(stop.set)
        client = SiteRuntimeClient(SimpleNamespace(cli_ctx=get_default_cli()),
                                   "http://localhost:{}".format(server.server_port))
        started = time.monotonic()
        with self.assertRaises(transport.ExecutionError) as caught:
            transport.ExecutionTransport(client).request("POST", "workflows/hello", started + 1)
        elapsed = time.monotonic() - started
        stop.set()
        self.assertEqual("invalidResponse", caught.exception.kind)
        self.assertLess(elapsed, 0.9)
        self.assertEqual(["identity"], observed)
        self.assertNotIn("do-not-expose", str(caught.exception))
        self.assertTrue(finished.wait(2))


if __name__ == "__main__":
    unittest.main()
