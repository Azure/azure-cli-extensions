# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import io
import json
import logging
import traceback
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from azure.cli.core import get_default_cli
from azure.cli.core import util as cli_util
from azure.cli.core.azclierror import (
    ClientRequestError, HTTPError, InvalidArgumentValueError, MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError, ResourceNotFoundError, UnauthorizedError)
from requests import Response
from requests.exceptions import (
    ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout, TooManyRedirects)
from knack.util import CLIError

from azext_logicapp import COMMAND_LOADER_CLS, _runtime_client, _workflow_state, custom

SITE = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"
PRIVATE = "test-only-private-value-never-print"
_UNSET = object()


def http_error(status):
    response = Response()
    response.status_code = status
    return HTTPError(PRIVATE, response=response)


class StateTransport:
    """Models whole-map App Service PUT separately from runtime propagation."""

    def __init__(self):
        self.settings = {"AppSecret": PRIVATE, "Workflows.keep.FlowState": "Enabled"}
        self.kind = "Stateful"
        self.state = "Enabled"
        self.calls = []
        self.gets = 0
        self.reads = 0
        self.puts = 0
        self.converge = True
        self.metadata_override = _UNSET
        self.read_override = _UNSET
        self.receipt_override = _UNSET
        self.metadata_failure = None
        self.read_failure = None
        self.after_put = None
        self.receipt_status = 200
        self.bad_read_json = False
        self.readback_override = _UNSET

    def __call__(self, _cli, method, url, **kwargs):
        cli_util.logger.debug(PRIVATE)
        self.calls.append((method, url, kwargs))
        self._check_url(url)
        path = urlsplit(url).path
        status = 200
        if path.endswith("/workflows/hello"):
            assert method == "GET"
            self.gets += 1
            if self.metadata_failure:
                failure = self.metadata_failure(self.gets)
                if failure:
                    raise failure
            payload = {"name": "hello", "kind": self.kind, "isDisabled": self.state == "Disabled",
                       "health": {"state": "Healthy"},
                       "href": "https://untrusted.invalid/?sig=" + PRIVATE}
            if self.metadata_override is not _UNSET:
                payload = self.metadata_override
        elif path == SITE + "/config/appsettings/list":
            assert method == "POST" and kwargs["body"] is None
            self.reads += 1
            if self.read_failure:
                failure = self.read_failure(self.reads)
                if failure:
                    raise failure
            payload = {"id": SITE + "/config/appsettings", "properties": copy.deepcopy(self.settings)}
            if self.read_override is not _UNSET:
                payload = self.read_override
            if self.reads == 3 and self.readback_override is not _UNSET:
                payload = self.readback_override
            if self.bad_read_json:
                return SimpleNamespace(status_code=200, json=lambda: (_ for _ in ()).throw(ValueError(PRIVATE)))
        elif path == SITE + "/config/appsettings":
            assert method == "PUT"
            self.puts += 1
            self.settings = json.loads(kwargs["body"])["properties"]
            if self.converge:
                key = next(key for key in self.settings if key.casefold() == "workflows.hello.flowstate")
                self.state = self.settings[key]
            payload = {"properties": copy.deepcopy(self.settings)}
            status = self.receipt_status
            if self.receipt_override is not _UNSET:
                payload = self.receipt_override
            if self.after_put:
                self.after_put()
        else:
            raise AssertionError(url)
        return SimpleNamespace(status_code=status, headers={},
                               content=payload if isinstance(payload, bytes) else json.dumps(payload).encode(),
                               json=lambda: payload)

    @staticmethod
    def _check_url(url):
        assert parse_qs(urlsplit(url).query) == {"api-version": ["2018-11-01"]}


class WorkflowStateRegressions(unittest.TestCase):
    def setUp(self):
        self.transport = StateTransport()
        self.cmd = SimpleNamespace(cli_ctx=get_default_cli())
        self.client = _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=self.transport)
        self.confirmation = patch.object(_workflow_state, "user_confirmation")
        self.confirm = self.confirmation.start()
        self.addCleanup(self.confirmation.stop)

    def change(self, state="Disabled", **kwargs):
        kwargs.setdefault("allow_non_atomic", True)
        return _workflow_state.set_workflow_state(self.client, "hello", state, **kwargs)

    def test_disable_preserves_other_settings_and_verifies_configuration_and_runtime(self):
        before = dict(self.transport.settings)
        result = self.change(yes=True)
        self.assertEqual({
            "workflow": "hello", "workflowKind": "Stateful", "action": "configured",
            "requestedState": "Disabled", "configuredState": "Disabled", "runtimeState": "Disabled",
            "runtimeConvergence": "converged", "runtimeObservationError": None,
            "verification": "appSettingsReadback"}, result)
        self.assertEqual(before, {key: value for key, value in self.transport.settings.items()
                                  if key != "Workflows.hello.FlowState"})
        self.assertEqual(1, self.transport.puts)
        self.assertEqual(7, len(self.transport.calls))
        self.confirm.assert_called_once()
        self.assertTrue(self.confirm.call_args.args[1])
        self.assertNotIn(PRIVATE, str(result) + self.confirm.call_args.args[0])
        self.assertTrue(all("skip_authorization_header" not in kwargs for _, _, kwargs in self.transport.calls))

    def test_enable_stateless_workflow_keeps_case_of_existing_setting(self):
        self.transport.kind = "Stateless"
        self.transport.state = "Disabled"
        self.transport.settings["workflows.HELLO.flowstate"] = "Disabled"
        result = self.change("Enabled")
        self.assertEqual("Stateless", result["workflowKind"])
        self.assertEqual("Enabled", self.transport.settings["workflows.HELLO.flowstate"])
        self.assertNotIn("Workflows.hello.FlowState", self.transport.settings)
        self.assertEqual("Enabled", result["runtimeState"])

    def test_arm_and_case_variant_metadata_keep_configuration_and_observation_separate(self):
        for payload, kind in (
                ({"name": "app/hello", "kind": "Stateful",
                  "properties": {"flowState": "Enabled", "health": {"state": "Healthy"}}}, "Stateful"),
                ({"Name": "app/hello", "Kind": "Stateless", "Properties": {"IsDisabled": False}}, "Stateless")):
            with self.subTest(kind=kind):
                self.set_transport(StateTransport())
                self.transport.metadata_override = payload
                with self.assertLogs(_workflow_state.logger.name, level="WARNING"):
                    result = self.change()
                self.assertEqual(kind, result["workflowKind"])
                self.assertEqual("Disabled", result["configuredState"])
                self.assertEqual("Enabled", result["runtimeState"])
                self.assertEqual("pending", result["runtimeConvergence"])

    def test_configured_but_not_propagated_is_pending_not_falsely_converged(self):
        self.transport.converge = False
        with self.assertLogs(_workflow_state.logger.name, level="WARNING") as logs:
            result = self.change()
        self.assertEqual("Disabled", result["configuredState"])
        self.assertEqual("Enabled", result["runtimeState"])
        self.assertEqual("pending", result["runtimeConvergence"])
        self.assertNotIn(PRIVATE, str(result) + str(logs.output))
        self.assertEqual(1, self.transport.puts)

    def test_verified_configuration_with_runtime_transport_failure_is_explicit_unknown(self):
        for failure, category in ((http_error(503), "unavailable"), (http_error(403), "unauthorized"),
                                  (http_error(404), "notFound"), (RequestsTimeout(PRIVATE), "unavailable"),
                                  (CLIError(PRIVATE), "unavailable"), (TooManyRedirects(PRIVATE), "unavailable")):
            with self.subTest(category=category):
                self.set_transport(StateTransport())
                self.transport.metadata_failure = lambda count, failure=failure: failure if count == 3 else None
                with self.assertLogs(_workflow_state.logger.name, level="WARNING") as logs:
                    result = self.change()
                self.assertEqual("Disabled", result["configuredState"])
                self.assertIsNone(result["runtimeState"])
                self.assertEqual("unknown", result["runtimeConvergence"])
                self.assertEqual(category, result["runtimeObservationError"])
                self.assertNotIn(PRIVATE, str(result) + str(logs.output))
                self.assertEqual(1, self.transport.puts)

    def set_transport(self, transport):
        self.transport = transport
        self.client = _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=transport)

    def test_repeated_state_change_is_a_true_noop_without_confirmation(self):
        self.change()
        self.confirm.reset_mock()
        self.transport.calls.clear()
        result = self.change()
        self.assertEqual("unchanged", result["action"])
        self.assertEqual("converged", result["runtimeConvergence"])
        self.assertEqual(1, self.transport.puts)
        self.assertEqual(["GET", "POST"], [method for method, _, _ in self.transport.calls])
        self.confirm.assert_not_called()

    def test_already_configured_pending_does_not_rewrite_settings(self):
        self.transport.settings["Workflows.hello.FlowState"] = "Disabled"
        with self.assertLogs(_workflow_state.logger.name, level="WARNING"):
            result = self.change()
        self.assertEqual("unchanged", result["action"])
        self.assertEqual("pending", result["runtimeConvergence"])
        self.assertEqual(0, self.transport.puts)
        self.confirm.assert_not_called()

    def test_missing_configured_state_is_not_invented_from_runtime_default(self):
        result = self.change("Enabled")
        self.assertEqual("configured", result["action"])
        self.assertEqual("Enabled", self.transport.settings["Workflows.hello.FlowState"])
        self.assertEqual(1, self.transport.puts)

    def test_acknowledgement_is_required_even_with_yes_before_any_request(self):
        with self.assertRaisesRegex(InvalidArgumentValueError, "--allow-non-atomic"):
            self.change(yes=True, allow_non_atomic=False)
        self.assertEqual([], self.transport.calls)

    def test_local_runtime_is_gated_without_any_read_write_or_prompt(self):
        self.client = _runtime_client.SiteRuntimeClient(
            self.cmd, "http://localhost:17071", sender=self.transport, host_key="private-local-key")
        for state in ("Enabled", "Disabled"):
            with self.subTest(state=state), self.assertRaisesRegex(
                    InvalidArgumentValueError, "not supported through the local runtime API"):
                self.change(state)
        self.assertEqual([], self.transport.calls)
        self.confirm.assert_not_called()

    def test_nested_slot_and_route_injection_targets_are_rejected_before_requests(self):
        for resource in (SITE + "/slots/staging", SITE + "?query=injected",
                         SITE.replace("/sites/app", "/sites/app%2fslots%2fstaging")):
            with self.subTest(resource=resource):
                with self.assertRaisesRegex(InvalidArgumentValueError, "not a slot or nested resource"):
                    self.client = _runtime_client.SiteRuntimeClient(self.cmd, resource, sender=self.transport)
                    self.change()
        self.assertEqual([], self.transport.calls)
        self.confirm.assert_not_called()

    def test_bad_name_and_state_reject_before_requests(self):
        for name, state in (("../hello", "Enabled"), ("", "Disabled"), ("hello", "Suspended")):
            with self.subTest(name=name, state=state), self.assertRaises(InvalidArgumentValueError):
                _workflow_state.set_workflow_state(self.client, name, state, allow_non_atomic=True)
        self.assertEqual([], self.transport.calls)

    def test_workflow_must_exist_before_app_settings_are_read_or_written(self):
        self.transport.metadata_failure = lambda _count: http_error(404)
        with self.assertRaises(ResourceNotFoundError) as caught:
            self.change()
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(0, self.transport.reads)
        self.assertEqual(0, self.transport.puts)

    def test_initial_auth_and_transport_errors_are_distinct_and_sanitized(self):
        for failure, expected in ((http_error(401), UnauthorizedError), (http_error(403), UnauthorizedError),
                                  (RequestsConnectionError(PRIVATE), ClientRequestError),
                                  (CLIError(PRIVATE), ClientRequestError), (TooManyRedirects(PRIVATE), ClientRequestError)):
            with self.subTest(expected=expected):
                self.transport.metadata_failure = lambda _count, failure=failure: failure
                with self.assertRaises(expected) as caught:
                    self.change()
                self.assertNotIn(PRIVATE, str(caught.exception))
                self.assertTrue(caught.exception.__suppress_context__)
        self.assertEqual(0, self.transport.puts)

    def test_settings_read_errors_are_sanitized_without_confirmation_or_put(self):
        for failure, expected in ((http_error(404), ResourceNotFoundError),
                                  (http_error(403), UnauthorizedError),
                                  (RequestsTimeout(PRIVATE), ClientRequestError)):
            with self.subTest(expected=expected):
                self.set_transport(StateTransport())
                self.transport.read_failure = lambda _count, failure=failure: failure
                with self.assertRaises(expected) as caught:
                    self.change()
                self.assertNotIn(PRIVATE, "".join(traceback.format_exception(caught.exception)))
                self.assertEqual(0, self.transport.puts)
                self.confirm.assert_not_called()

    def test_secret_and_key_vault_values_are_preserved_without_exposure(self):
        references = {
            "AzureWebJobsStorage": "AccountName=example;AccountKey=" + PRIVATE,
            "VaultReference": "@Microsoft.KeyVault(SecretUri=https://example.vault.azure.net/secrets/example/)",
            "ConnectionSetting": json.dumps({"credential": PRIVATE})}
        self.transport.settings.update(references)
        result = self.change()
        self.assertTrue(all(self.transport.settings[key] == value for key, value in references.items()))
        self.assertNotIn(PRIVATE, json.dumps(result))
        self.assertNotIn("vault.azure.net", json.dumps(result))

    def test_missing_unknown_conflicting_or_unsupported_runtime_metadata_fails(self):
        for payload in (None, {}, {"name": "hello", "kind": "Agentic", "isDisabled": False},
                        {"name": "different", "kind": "Stateful", "isDisabled": False},
                        {"name": "hello", "kind": "Stateful"},
                        {"name": "hello", "kind": "Stateful", "isDisabled": "false"},
                        {"name": "hello", "kind": "Stateful", "isDisabled": False,
                         "properties": {"flowState": "Suspended"}}):
            with self.subTest(payload=payload):
                self.transport.metadata_override = payload
                with self.assertRaises(ClientRequestError):
                    self.change()
        self.assertEqual(0, self.transport.reads)
        self.assertEqual(0, self.transport.puts)

    def test_malformed_or_masked_settings_are_never_resent(self):
        for payload in (None, {}, {"properties": []}, {"properties": {"bad": None}},
                        {"properties": {"Case": "one", "case": "two"}},
                        {"properties": {"secret": "*****"}},
                        {"properties": {"secret": _workflow_state.LOGICAPP_REDACTION_SENTINEL}},
                        {"id": SITE + "/different", "properties": {}}):
            with self.subTest(payload=payload):
                self.transport.read_override = payload
                with self.assertRaises(ClientRequestError):
                    self.change()
        self.transport.read_override = _UNSET
        self.transport.bad_read_json = True
        with self.assertRaises(ClientRequestError) as caught:
            self.change()
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(0, self.transport.puts)
        self.confirm.assert_not_called()

    def test_strict_raw_metadata_rejects_ambiguity_at_every_observation_stage(self):
        samples = (
            b'{"name":"hello","kind":"Stateful","kind":"Stateful","isDisabled":false}',
            b'{"name":"hello","kind":"Stateful","properties":{"flowState":"Enabled","flowState":"Enabled"}}',
            b'{"name":"hello","kind":"Stateful","properties":{},"properties":{"flowState":"Enabled"}}',
            b'{"name":"hello","kind":"Stateful","isDisabled":false,"ignored":NaN}',
            b'{"name":"hello","kind":"Stateful","isDisabled":false,"ignored":1e999}',
            b"[" * 1100 + b"0" + b"]" * 1100,
        )
        for stage in ("initial", "confirmation", "postwrite"):
            for raw in samples:
                with self.subTest(stage=stage, raw=raw[:100]):
                    self.set_transport(StateTransport())
                    self.confirm.side_effect = None
                    self.confirm.reset_mock()
                    if stage == "initial":
                        self.transport.metadata_override = raw
                    elif stage == "confirmation":
                        self.confirm.side_effect = lambda *_args: setattr(self.transport, "metadata_override", raw)
                    else:
                        self.transport.after_put = lambda: setattr(self.transport, "metadata_override", raw)
                    with self.assertRaises(ClientRequestError) as caught:
                        self.change()
                    self.assertNotIn(PRIVATE, "".join(traceback.format_exception(caught.exception)))
                    self.assertEqual(1 if stage == "postwrite" else 0, self.transport.puts)
                    if stage == "initial":
                        self.assertEqual(0, self.transport.reads)
                        self.confirm.assert_not_called()

    def test_strict_raw_settings_reject_ambiguity_before_and_after_mutation(self):
        for stage in ("initial", "confirmation", "receipt", "readback"):
            expected = dict(StateTransport().settings)
            if stage in ("receipt", "readback"):
                expected["Workflows.hello.FlowState"] = "Disabled"
            properties = json.dumps(expected)
            samples = [
                ('{"properties":' + properties + ',"properties":' + properties + '}').encode(),
                ('{"properties":' + properties.replace('"AppSecret":',
                 '"AppSecret":"' + PRIVATE + '","AppSecret":', 1) + '}').encode(),
            ]
            samples.extend(('{"properties":' + properties + ',"ignored":' + value + '}').encode()
                           for value in ("NaN", "Infinity", "-Infinity", "1e999"))
            for raw in samples:
                with self.subTest(stage=stage, raw=raw[:100]):
                    self.set_transport(StateTransport())
                    self.confirm.side_effect = None
                    self.confirm.reset_mock()
                    if stage == "initial":
                        self.transport.read_override = raw
                    elif stage == "confirmation":
                        self.confirm.side_effect = lambda *_args: setattr(self.transport, "read_override", raw)
                    elif stage == "receipt":
                        self.transport.receipt_override = raw
                    else:
                        self.transport.readback_override = raw
                    with self.assertRaises(ClientRequestError) as caught:
                        self.change()
                    self.assertNotIn(PRIVATE, "".join(traceback.format_exception(caught.exception)))
                    self.assertEqual(1 if stage in ("receipt", "readback") else 0, self.transport.puts)
                    if stage == "initial":
                        self.confirm.assert_not_called()

    def test_unknown_configured_state_fails_without_echoing_value(self):
        self.transport.settings["Workflows.hello.FlowState"] = PRIVATE
        with self.assertRaises(ClientRequestError) as caught:
            self.change()
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(0, self.transport.puts)

    def test_confirmation_cancellation_does_not_change_settings(self):
        before = dict(self.transport.settings)
        self.confirm.side_effect = ClientRequestError("cancelled")
        with self.assertRaises(ClientRequestError):
            self.change()
        self.assertEqual(before, self.transport.settings)
        self.assertEqual(0, self.transport.puts)

    def test_unrelated_settings_or_workflow_state_change_during_confirmation_blocks_put(self):
        for change in (lambda: self.transport.settings.update({"Another": PRIVATE}),
                       lambda: setattr(self.transport, "state", "Disabled"),
                       lambda: setattr(self.transport, "kind", "Stateless")):
            with self.subTest(change=change):
                self.set_transport(StateTransport())
                self.confirm.side_effect = lambda *_args, change=change: change()
                with self.assertRaisesRegex(ClientRequestError, "No settings update"):
                    self.change()
                self.assertEqual(0, self.transport.puts)

    def test_ambiguous_put_is_not_retried_or_rolled_back_and_error_has_no_provider_body(self):
        self.transport.after_put = lambda: (_ for _ in ()).throw(http_error(500))
        with self.assertRaisesRegex(ClientRequestError, "outcome may be uncertain") as caught:
            self.change()
        formatted = "".join(traceback.format_exception(caught.exception))
        self.assertNotIn(PRIVATE, formatted)
        self.assertEqual(1, self.transport.puts)
        self.assertEqual("Disabled", self.transport.settings["Workflows.hello.FlowState"])

    def test_bad_receipt_is_applied_but_not_reported_as_verified_success(self):
        for receipt in (None, {"error": {"message": PRIVATE}}, {"properties": {}}):
            with self.subTest(receipt=receipt):
                self.set_transport(StateTransport())
                self.transport.receipt_override = receipt
                with self.assertRaises(ClientRequestError) as caught:
                    self.change()
                self.assertNotIn(PRIVATE, str(caught.exception))
                self.assertEqual(1, self.transport.puts)
        self.set_transport(StateTransport())
        self.transport.receipt_status = 202
        with self.assertRaises(ClientRequestError):
            self.change()
        self.assertEqual(1, self.transport.puts)

    def test_configuration_readback_failure_is_error_not_configured_success(self):
        self.transport.read_failure = lambda count: http_error(403) if count == 3 else None
        with self.assertRaisesRegex(ClientRequestError, "configuration readback failed") as caught:
            self.change()
        self.assertNotIn(PRIVATE, str(caught.exception))
        self.assertEqual(1, self.transport.puts)

    def test_newer_settings_after_put_are_not_overwritten_by_rollback(self):
        self.transport.after_put = lambda: self.transport.settings.update({"Concurrent": "new"})
        with self.assertRaisesRegex(ClientRequestError, "potentially newer settings"):
            self.change()
        self.assertEqual("new", self.transport.settings["Concurrent"])
        self.assertEqual(1, self.transport.puts)

    def test_malformed_postwrite_metadata_is_error_not_unknown_success_fallback(self):
        self.transport.after_put = lambda: setattr(self.transport, "metadata_override", {})
        with self.assertRaisesRegex(ClientRequestError, "runtime metadata was invalid"):
            self.change()
        self.assertEqual(1, self.transport.puts)

    def test_changed_workflow_kind_after_put_is_not_a_claim_of_convergence(self):
        self.transport.after_put = lambda: setattr(self.transport, "kind", "Stateless")
        with self.assertRaisesRegex(ClientRequestError, "workflow kind changed"):
            self.change()
        self.assertEqual(1, self.transport.puts)

    def test_http_debug_payloads_are_suppressed_and_logging_is_restored(self):
        http_logger = cli_util.logger
        output = io.StringIO()
        handler = logging.StreamHandler(output)
        previous_level = http_logger.level
        http_logger.setLevel(logging.DEBUG)
        http_logger.addHandler(handler)
        try:
            self.change()
            http_logger.debug("visible-after-private-request")
        finally:
            http_logger.removeHandler(handler)
            http_logger.setLevel(previous_level)
        self.assertNotIn(PRIVATE, output.getvalue())
        self.assertIn("visible-after-private-request", output.getvalue())

    def test_real_cli_rest_helper_debug_request_response_and_provider_error_are_private(self):
        base = "http://localhost:17071"

        def rest_sender(cli_ctx, method, url, **kwargs):
            return cli_util.send_raw_request(
                cli_ctx, method, base + url, skip_authorization_header=True, **kwargs)

        def http_send(_session, request, **_kwargs):
            fixture = self.transport(
                self.cmd.cli_ctx, request.method, request.url[len(base):], body=request.body)
            response = Response()
            response.status_code = fixture.status_code
            response.reason = "OK" if fixture.status_code == 200 else PRIVATE
            response._content = fixture.content
            response.headers["Content-Type"] = "application/json"
            response.request = request
            return response

        output = io.StringIO()
        handler = logging.StreamHandler(output)
        http_logger = cli_util.logger
        previous_level = http_logger.level
        http_logger.setLevel(logging.DEBUG)
        http_logger.addHandler(handler)
        self.client = _runtime_client.SiteRuntimeClient(self.cmd, SITE, sender=rest_sender)
        try:
            with patch("requests.Session.send", autospec=True, side_effect=http_send):
                result = self.change()
                self.assertEqual("converged", result["runtimeConvergence"])
                self.transport.settings.pop("Workflows.hello.FlowState")
                self.transport.receipt_status = 500
                self.transport.receipt_override = {"error": {"code": "ProviderFailure", "message": PRIVATE}}
                with self.assertRaises(ClientRequestError) as caught:
                    self.change()
                self.assertNotIn(PRIVATE, "".join(traceback.format_exception(caught.exception)))
            http_logger.debug("real-rest-helper-filter-restored")
        finally:
            http_logger.removeHandler(handler)
            http_logger.setLevel(previous_level)
        self.assertNotIn(PRIVATE, output.getvalue())
        self.assertIn("real-rest-helper-filter-restored", output.getvalue())

    def test_public_commands_and_cloud_context_share_target_resolution(self):
        saved = {"name": "saved", "target": {"kind": "cloud", "resourceGroup": "rg", "logicAppName": "app"}}
        with patch.object(_runtime_client, "send_raw_request", side_effect=self.transport), \
                patch.object(_runtime_client, "_site_resource_id", return_value=SITE), \
                patch.object(custom, "get_context", return_value=(saved, {})):
            result = custom.workflow_disable(self.cmd, "hello", context="saved", yes=True, allow_non_atomic=True)
            self.assertEqual("Disabled", result["configuredState"])
            result = custom.workflow_enable(self.cmd, "hello", resource_group_name="rg", name="app",
                                            yes=True, allow_non_atomic=True)
            self.assertEqual("Enabled", result["configuredState"])
        for operation in (custom.workflow_enable, custom.workflow_disable):
            for kwargs in ({"local": True, "name": "app"}, {"context": "saved", "port": 17071},
                           {"resource_group_name": "rg", "name": "app", "host_key": "key"}):
                with self.subTest(operation=operation.__name__, kwargs=kwargs):
                    with self.assertRaises((MutuallyExclusiveArgumentError, RequiredArgumentMissingError)):
                        operation(self.cmd, "hello", **kwargs)

    def test_command_registration_requires_name_and_exposes_no_fake_concurrency_or_local_file_flags(self):
        for suffix in ("enable", "disable"):
            command = "logicapp workflow " + suffix
            cli = get_default_cli()
            cli.invocation = SimpleNamespace(data={"command_string": command})
            loader = COMMAND_LOADER_CLS(cli_ctx=cli)
            self.assertIn(command, loader.load_command_table([]))
            loader.load_arguments([])
            args = loader.argument_registry.arguments[command]
            self.assertTrue(args["workflow"].settings["required"])
            self.assertTrue({"resource_group_name", "name", "local", "port", "host_key", "context",
                             "yes", "allow_non_atomic"} <= set(args))
            self.assertFalse({"force", "if_match", "file", "path", "timeout"} & set(args))
            self.assertEqual(["--yes", "-y"], args["yes"].settings["options_list"])


if __name__ == "__main__":
    unittest.main()
