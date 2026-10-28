# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Offline lifecycle regressions; runnable with unittest and Azure CLI Python."""

import asyncio
import copy
import hashlib
import json
import unittest
from types import SimpleNamespace
from unittest import mock
from urllib.parse import urlsplit

from azure.cli.core.azclierror import (
    CLIInternalError, ClientRequestError, HTTPError, ResourceNotFoundError, ValidationError)
from requests.exceptions import Timeout as RequestsTimeout

from azext_logicapp import _connection, _managed_connection as managed
from azext_logicapp._runtime_client import SiteVfsClient


CONNECTION_ID = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/connections/conn"
SITE_ID = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"
CONNECTOR_ID = "/subscriptions/sub/providers/Microsoft.Web/locations/eastus/managedApis/office365"
PRINCIPAL = {"objectId": "app-principal", "tenantId": "tenant"}
POLICY_NAME = "app-app-principal"
POLICY_ID = CONNECTION_ID + "/accessPolicies/" + POLICY_NAME
CALLER = {"objectId": "caller", "tenantId": "tenant"}
_MISSING = object()


class _Response:
    def __init__(self, payload=_MISSING, status=200):
        self.status_code = status
        self.headers = {}
        self.content = json.dumps({} if payload is _MISSING else payload).encode("utf-8")

    def json(self):
        return json.loads(self.content)


class _Arm:
    """Resource-aware ARM transport, including PUT updates and cascading DELETE."""

    def __init__(self, existing=False, policies=None):
        self.connection = None
        if existing:
            self.connection = {
                "id": CONNECTION_ID, "name": "conn", "kind": "V2", "location": "westus",
                "properties": {
                    "displayName": "original",
                    "api": {"id": CONNECTOR_ID},
                    "overallStatus": "Connected",
                    "statuses": [{"status": "Connected"}],
                },
            }
        self.policies = copy.deepcopy(policies or {})
        self.calls = []
        self.failures = {}
        self.responses = {}
        self.disconnected = False

    def fail(self, method, path, error, occurrence=1, after=False):
        self.failures[(method, path, occurrence)] = (error, after)

    def send(self, _context, method, url, body=None, **_kwargs):
        path = url.split("?", 1)[0]
        payload = json.loads(body) if body is not None else None
        self.calls.append((method, path, copy.deepcopy(payload)))
        occurrence = sum(1 for item in self.calls if item[:2] == (method, path))
        failure = self.failures.get((method, path, occurrence))
        if failure and not failure[1]:
            raise failure[0]
        key = (method, path, occurrence)
        result = self.responses[key] if key in self.responses else self._dispatch(method, path, payload)
        if failure:
            raise failure[0]
        return _Response(result)

    def _dispatch(self, method, path, payload):
        if path == CONNECTION_ID:
            if method == "GET":
                if self.connection is None:
                    raise HTTPError("Not found", _Response(status=404))
                result = copy.deepcopy(self.connection)
                if self.disconnected:
                    result["properties"]["statuses"] = [{"status": "Error"}]
                return result
            if method == "PUT":
                self.connection = copy.deepcopy(payload)
                self.connection.update({"id": CONNECTION_ID, "name": "conn", "type": "Microsoft.Web/connections"})
                self.connection["properties"].update({
                    "overallStatus": "Connected", "statuses": [{"status": "Connected"}],
                    "connectionRuntimeUrl": "https://connection.invalid/runtime",
                })
                return self.connection
            if method == "DELETE":
                if self.connection is None:
                    raise HTTPError("Not found", _Response(status=404))
                self.connection = None
                self.policies.clear()
                return {}
        if path == CONNECTION_ID + "/accessPolicies" and method == "GET":
            if self.connection is None:
                raise HTTPError("Not found", _Response(status=404))
            return {"value": copy.deepcopy(list(self.policies.values()))}
        if path.startswith(CONNECTION_ID + "/accessPolicies/"):
            name = path.rsplit("/", 1)[-1]
            if method == "GET":
                if name not in self.policies:
                    raise HTTPError("Not found", _Response(status=404))
                return copy.deepcopy(self.policies[name])
            if method == "PUT":
                if self.connection is None:
                    raise AssertionError("Cannot create a policy without its connection")
                self.policies[name] = dict(copy.deepcopy(payload), id=path, name=name)
                return self.policies[name]
            if method == "DELETE":
                if name not in self.policies:
                    raise HTTPError("Not found", _Response(status=404))
                del self.policies[name]
                return {}
        raise AssertionError("Unexpected ARM request: {} {}".format(method, path))

    @property
    def deletes(self):
        return [path for method, path, _ in self.calls if method == "DELETE"]

    @property
    def mutations(self):
        return [call for call in self.calls if call[0] != "GET"]


class _Vfs:
    """Byte-preserving VFS with failures before or after an applied PUT."""

    def __init__(self, payload=_MISSING, raw=None):
        self.content = (
            raw if raw is not None else
            None if payload is _MISSING else json.dumps(payload, indent=4).encode("utf-8") + b"\n"
        )
        self.calls = []
        self.reads = 0
        self.writes = 0
        self.read_failures = {}
        self.write_failures = {}
        self.on_write = None
        self.on_before_write = None
        self.on_read = None
        self.write_status = 204
        self.apply_write = True
        self.etag_override = _MISSING
        self.conditions = []

    @property
    def etag(self):
        return '"{}"'.format(hashlib.sha256(self.content).hexdigest()) if self.content is not None else None

    def get_raw(self, path):
        self.calls.append(("GET", path))
        self.reads += 1
        if self.reads in self.read_failures:
            raise self.read_failures[self.reads]
        if self.on_read:
            self.on_read(self)
        if self.content is None:
            raise ResourceNotFoundError("Not found")
        etag = self.etag if self.etag_override is _MISSING else self.etag_override
        return {"content": self.content, "headers": {"ETag": etag} if etag is not None else {}, "statusCode": 200}

    def get(self, path):
        return json.loads(self.get_raw(path)["content"])

    def put_raw(self, path, content, if_match=None):
        self.calls.append(("PUT", path))
        self.writes += 1
        self.conditions.append(if_match)
        self.pending_content = content
        if self.on_before_write:
            self.on_before_write(self)
        if if_match != self.etag:
            raise HTTPError("Revision conflict", _Response(status=412))
        failure = self.write_failures.get(self.writes)
        if failure and not failure[1]:
            raise failure[0]
        published_etag = self.etag
        if self.apply_write:
            self.content = content
            published_etag = self.etag
            if self.on_write:
                self.on_write(self)
        if failure:
            raise failure[0]
        return {"content": b"", "headers": {"ETag": published_etag} if published_etag else {},
                "statusCode": self.write_status}

    def delete(self, path):
        self.calls.append(("DELETE", path))
        if self.content is None:
            raise ResourceNotFoundError("Not found")
        self.content = None
        return {"content": b"", "headers": {}, "statusCode": 204}

    def send(self, _context, method, url, body=None, **kwargs):
        if not urlsplit(url).path.endswith("/admin/vfs/connections.json"):
            raise AssertionError("Unexpected VFS URL: " + url)
        try:
            if method == "GET":
                receipt = self.get_raw("connections.json")
            elif method == "PUT":
                headers = kwargs.get("headers") or []
                match = next((header.split("=", 1)[1] for header in headers
                              if header.lower().startswith("if-match=")), None)
                receipt = self.put_raw("connections.json", body.read(), if_match=match)
            elif method == "DELETE":
                receipt = self.delete("connections.json")
            else:
                raise AssertionError(method)
        except ResourceNotFoundError as error:
            raise HTTPError("Not found", _Response(status=404)) from error
        response = _Response(status=receipt["statusCode"])
        response.content = receipt["content"]
        response.headers = receipt["headers"]
        return response

    @property
    def payload(self):
        return None if self.content is None else json.loads(self.content)


class _DecodedVfs:
    """Injected get/put_raw interface without optional raw reads."""

    def __init__(self, payload):
        self.payload = copy.deepcopy(payload)
        self.written = None

    def get(self, _path):
        return copy.deepcopy(self.payload)

    def put_raw(self, _path, content):
        self.written = content
        self.payload = json.loads(content)
        return {"content": b"", "headers": {}, "statusCode": 204}


def _vfs_client(vfs, http):
    return SiteVfsClient(SimpleNamespace(cli_ctx=object()), SITE_ID, sender=vfs.send) if http else vfs


def _policy(name=POLICY_NAME, object_id="app-principal", location="westus", tenant_id="tenant"):
    body = managed.build_access_policy_body(location, tenant_id, object_id)
    return dict(body, id=CONNECTION_ID + "/accessPolicies/" + name, name=name)


class ManagedLifecycleRegressions(unittest.TestCase):
    def _create(self, arm, vfs, runner=None, auth_mode="oauth", force=False):
        with mock.patch.object(managed, "_resolve_connector", return_value=CONNECTOR_ID), \
                mock.patch.object(managed, "_resolve_app_principal", return_value=PRINCIPAL), \
                mock.patch.object(managed, "_connection_id", return_value=CONNECTION_ID):
            return managed.create_managed_connection(
                SimpleNamespace(cli_ctx=object()), "rg", "app", "conn", CONNECTOR_ID,
                "eastus", auth_mode, force=force, arm_sender=arm.send, vfs_client=vfs,
                consent_principal=CALLER,
                consent_runner=runner or (lambda *_args, **_kwargs: {"confirmed": True}))

    def _assert_retained_failure(self, arm, vfs, error, runner=None, **kwargs):
        with self.assertRaises(CLIInternalError) as caught:
            self._create(arm, vfs, runner=runner, force=True, **kwargs)
        self.assertIs(caught.exception.__cause__, error)
        self.assertIn("was retained, not deleted", str(caught.exception))
        self.assertIn("cannot be safely restored automatically", str(caught.exception))
        self.assertIsNotNone(arm.connection)
        self.assertNotIn(CONNECTION_ID, arm.deletes)

    def _assert_attempted_acl_retained(self, arm, previous=None):
        expected = managed.build_access_policy_body("eastus", PRINCIPAL["tenantId"], PRINCIPAL["objectId"])
        self.assertEqual(dict(expected, id=POLICY_ID, name=POLICY_NAME), arm.policies[POLICY_NAME])
        self.assertEqual({key: value for key, value in (previous or {}).items() if key != POLICY_NAME},
                         {key: value for key, value in arm.policies.items() if key != POLICY_NAME})
        self.assertEqual([], arm.deletes)

    def test_forced_existing_oauth_decline_and_timeout_never_delete_resource(self):
        for error in (ValidationError("Consent declined"), ValidationError("Consent timed out")):
            with self.subTest(error=str(error)):
                arm, vfs = _Arm(existing=True), _Vfs({"managedApiConnections": {"other": {"keep": True}}})
                before = vfs.content
                self._assert_retained_failure(
                    arm, vfs, error, runner=mock.Mock(side_effect=error))
                self.assertEqual(arm.calls[0][:2], ("GET", CONNECTION_ID))
                self.assertEqual(arm.deletes, [])
                self.assertEqual(vfs.content, before)
                self.assertEqual(arm.policies, {})

    def test_forced_existing_keyboard_interrupt_and_cancellation_are_preserved(self):
        for error in (KeyboardInterrupt(), SystemExit(130), asyncio.CancelledError()):
            with self.subTest(error=type(error).__name__):
                policies = {POLICY_NAME: _policy(), "other": _policy("other", "other-principal")}
                arm, vfs = _Arm(existing=True, policies=policies), _Vfs({})
                before = vfs.content
                with mock.patch("knack.log.get_logger") as logger:
                    with self.assertRaises(type(error)) as caught:
                        self._create(arm, vfs, force=True, runner=mock.Mock(side_effect=error))
                self.assertIs(caught.exception, error)
                self.assertIn("was retained, not deleted", logger.return_value.error.call_args.args[0])
                self.assertEqual(arm.deletes, [])
                self.assertEqual(arm.policies, policies)
                self.assertEqual(vfs.content, before)

    def test_new_oauth_decline_timeout_and_cancellation_retain_unconditionally_upserted_resource(self):
        for error in (ValidationError("Declined"), ValidationError("Timeout"), KeyboardInterrupt(),
                      SystemExit(130), asyncio.CancelledError()):
            with self.subTest(error=type(error).__name__):
                arm, vfs = _Arm(), _Vfs({})
                with self.assertRaises(type(error)) as caught:
                    self._create(arm, vfs, runner=mock.Mock(side_effect=error))
                self.assertIs(caught.exception, error)
                self.assertIsNotNone(arm.connection)
                self.assertEqual(arm.policies, {})
                self.assertEqual(arm.deletes, [])
                self.assertEqual(vfs.writes, 0)

    def test_force_on_absent_connection_does_not_authorize_compensating_delete(self):
        arm, vfs = _Arm(), _Vfs({})
        with self.assertRaises(ValidationError):
            self._create(arm, vfs, force=True, runner=mock.Mock(side_effect=ValidationError("Declined")))
        self.assertEqual(arm.calls[0][:2], ("GET", CONNECTION_ID))
        self.assertIsNotNone(arm.connection)
        self.assertEqual(arm.deletes, [])

    def test_existing_without_force_is_rejected_without_mutation(self):
        arm, vfs = _Arm(existing=True), _Vfs({})
        with self.assertRaisesRegex(ValidationError, "already exists") as caught:
            self._create(arm, vfs)
        self.assertIn("--name (connection managed create)", str(caught.exception))
        self.assertIn("--connection-name (legacy connection create)", str(caught.exception))
        self.assertEqual(arm.mutations, [])
        self.assertEqual(vfs.calls, [])

    def test_existence_probe_failure_never_creates_or_deletes_anything(self):
        for force in (False, True):
            with self.subTest(force=force):
                arm, vfs = _Arm(existing=True), _Vfs({})
                error = OSError("ARM unavailable")
                arm.fail("GET", CONNECTION_ID, error)
                with self.assertRaises(OSError) as caught:
                    self._create(arm, vfs, force=force)
                self.assertIs(caught.exception, error)
                self.assertEqual(arm.mutations, [])

    def test_invalid_successful_existence_response_is_not_treated_as_absent(self):
        for payload in (None, [], False):
            with self.subTest(payload=payload):
                arm, vfs = _Arm(existing=True), _Vfs({})
                arm.responses[("GET", CONNECTION_ID, 1)] = payload
                with self.assertRaisesRegex(CLIInternalError, "invalid existing-resource"):
                    self._create(arm, vfs, force=True)
                self.assertEqual(arm.mutations, [])
                self.assertIsNotNone(arm.connection)

    def test_ambiguous_initial_connection_put_never_authorizes_resource_deletion(self):
        for existing in (False, True):
            with self.subTest(existing=existing):
                arm, vfs = _Arm(existing=existing), _Vfs({})
                error = OSError("Connection PUT response lost")
                arm.fail("PUT", CONNECTION_ID, error, after=True)
                if existing:
                    self._assert_retained_failure(arm, vfs, error)
                else:
                    with self.assertRaisesRegex(CLIInternalError, "does not establish ownership") as caught:
                        self._create(arm, vfs)
                    self.assertIs(caught.exception.__cause__, error)
                    self.assertIsNotNone(arm.connection)
                    self.assertEqual(arm.deletes, [])
                    self.assertEqual(arm.policies, {})
                    self.assertEqual(vfs.writes, 0)

    def test_other_writers_connection_survives_rejected_initial_put_after_absence(self):
        for force in (False, True):
            with self.subTest(force=force):
                arm, vfs = _Arm(), _Vfs({"managedApiConnections": {"other": {"keep": True}}})
                competing = _Arm(existing=True).connection
                competing["kind"] = "V1"
                policies = {"other": _policy("other", "other-principal")}
                before = vfs.content
                original_send = arm.send
                error = HTTPError("Forbidden", _Response(status=403))
                arm.fail("PUT", CONNECTION_ID, error)

                def interleaved_send(context, method, url, **kwargs):
                    if method == "PUT" and url.split("?", 1)[0] == CONNECTION_ID:
                        arm.connection = copy.deepcopy(competing)
                        arm.policies = copy.deepcopy(policies)
                    return original_send(context, method, url, **kwargs)

                arm.send = interleaved_send
                with self.assertRaisesRegex(CLIInternalError, "preflight absence") as caught:
                    self._create(arm, vfs, force=force)
                self.assertIs(caught.exception.__cause__, error)
                self.assertEqual(arm.connection, competing)
                self.assertEqual(arm.policies, policies)
                self.assertEqual(arm.deletes, [])
                self.assertEqual(vfs.content, before)
                self.assertEqual(vfs.writes, 0)

    def test_unacknowledged_initial_put_interrupt_preserves_resource_and_reports_uncertainty(self):
        for error in (KeyboardInterrupt(), SystemExit(130), asyncio.CancelledError()):
            with self.subTest(error=type(error).__name__):
                arm, vfs = _Arm(), _Vfs({})
                arm.fail("PUT", CONNECTION_ID, error, after=True)
                with mock.patch("knack.log.get_logger") as logger:
                    with self.assertRaises(type(error)) as caught:
                        self._create(arm, vfs)
                self.assertIs(caught.exception, error)
                self.assertIn("does not establish ownership", logger.return_value.error.call_args.args[0])
                self.assertIsNotNone(arm.connection)
                self.assertEqual(arm.deletes, [])
                self.assertEqual(vfs.writes, 0)

    def test_competing_connection_and_acl_survive_acknowledged_upsert_then_declined_consent(self):
        for force in (False, True):
            with self.subTest(force=force):
                arm, vfs = _Arm(), _Vfs({})
                original_send = arm.send
                policies = {"other": _policy("other", "other-principal")}

                def interleaved_send(context, method, url, **kwargs):
                    if method == "PUT" and url.split("?", 1)[0] == CONNECTION_ID:
                        arm.connection = copy.deepcopy(_Arm(existing=True).connection)
                        arm.policies = copy.deepcopy(policies)
                    return original_send(context, method, url, **kwargs)

                arm.send = interleaved_send
                with mock.patch("knack.log.get_logger") as logger:
                    with self.assertRaises(ValidationError):
                        self._create(arm, vfs, force=force,
                                     runner=mock.Mock(side_effect=ValidationError("Declined")))
                self.assertIsNotNone(arm.connection)
                self.assertEqual(policies, arm.policies)
                self.assertEqual([], arm.deletes)
                self.assertEqual(1, len(arm.mutations))
                self.assertEqual(0, vfs.writes)
                self.assertIn("exclusive rollback ownership", logger.return_value.error.call_args.args[0])

    def test_competing_policy_replacement_survives_failed_acl_receipt(self):
        for previous in (None, _policy()):
            with self.subTest(previous=previous is not None):
                arm = _Arm(existing=True, policies={POLICY_NAME: previous} if previous else {})
                vfs = _Vfs({})
                replacement = _policy(object_id="other-writer-principal")
                error = OSError("ACL response lost")
                arm.fail("PUT", POLICY_ID, error, after=True)
                original_send = arm.send

                def interleaved_send(context, method, url, **kwargs):
                    try:
                        return original_send(context, method, url, **kwargs)
                    finally:
                        if method == "PUT" and url.split("?", 1)[0] == POLICY_ID:
                            arm.policies[POLICY_NAME] = copy.deepcopy(replacement)

                arm.send = interleaved_send
                self._assert_retained_failure(arm, vfs, error)
                self.assertEqual(replacement, arm.policies[POLICY_NAME])
                self.assertEqual([], arm.deletes)
                self.assertEqual(2, len(arm.mutations))
                self.assertEqual(0, vfs.writes)

    def test_new_acl_failure_retains_attempted_arm_state_for_all_auth_modes(self):
        for auth_mode in managed.AUTH_MODES:
            with self.subTest(auth_mode=auth_mode):
                arm, vfs = _Arm(), _Vfs({})
                error = ValidationError("ACL failure")
                arm.fail("PUT", POLICY_ID, error, after=True)
                # An explicit parameter set avoids a connector metadata request.
                with mock.patch.object(managed, "_managed_identity_parameter_set", return_value="mi"):
                    with self.assertRaises(ValidationError) as caught:
                        self._create(arm, vfs, auth_mode=auth_mode)
                self.assertIs(caught.exception, error)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)

    def test_forced_existing_failed_acl_put_does_not_replay_previous_policy(self):
        policies = {POLICY_NAME: _policy(), "other": _policy("other", "other-principal")}
        arm, vfs = _Arm(existing=True, policies=policies), _Vfs({})
        error = OSError("ACL response lost")
        arm.fail("PUT", POLICY_ID, error, after=True)
        self._assert_retained_failure(arm, vfs, error)
        self._assert_attempted_acl_retained(arm, policies)

    def test_forced_existing_failed_acl_put_does_not_delete_new_policy(self):
        policies = {"other": _policy("other", "other-principal")}
        arm, vfs = _Arm(existing=True, policies=policies), _Vfs({})
        error = OSError("ACL response lost")
        arm.fail("PUT", POLICY_ID, error, after=True)
        self._assert_retained_failure(arm, vfs, error)
        self._assert_attempted_acl_retained(arm, policies)

    def test_existing_uninterpretable_policy_stops_before_mutation(self):
        arm = _Arm(existing=True, policies={POLICY_NAME: {"name": POLICY_NAME, "properties": {}}})
        with self.assertRaisesRegex(ValidationError, "cannot be safely interpreted"):
            self._create(arm, _Vfs({}), force=True)
        self.assertEqual(arm.mutations, [])

    def test_duplicate_principal_stops_forced_update_before_mutation(self):
        arm = _Arm(existing=True, policies={"other": _policy("other")})
        with self.assertRaisesRegex(ValidationError, "at most one access policy"):
            self._create(arm, _Vfs({}), force=True)
        self.assertEqual(arm.mutations, [])

    def test_existing_policy_must_match_selected_principal_before_forced_connection_update(self):
        samples = [
            _policy(object_id="other-principal"), _policy(tenant_id="other-tenant"),
        ]
        other_type = _policy()
        other_type["properties"]["principal"]["type"] = "Other"
        samples.append(other_type)
        for field in ("type", "objectId", "tenantId"):
            for value in (False, "", {"unverified": "value"}):
                malformed = _policy()
                principal = malformed["properties"]["principal"]
                (principal if field == "type" else principal["identity"])[field] = value
                samples.append(malformed)
        for policy in samples:
            with self.subTest(policy=policy):
                arm = _Arm(existing=True, policies={POLICY_NAME: policy})
                vfs = _Vfs({})
                before_connection = copy.deepcopy(arm.connection)
                before_file = vfs.content
                with self.assertRaises(ValidationError):
                    self._create(arm, vfs, force=True)
                self.assertEqual([], arm.mutations)
                self.assertEqual(before_connection, arm.connection)
                self.assertEqual({POLICY_NAME: policy}, arm.policies)
                self.assertEqual(before_file, vfs.content)
                self.assertEqual(0, vfs.writes)

    def test_matching_policy_case_variants_remain_supported(self):
        policy = _policy(object_id=PRINCIPAL["objectId"].upper(), tenant_id=PRINCIPAL["tenantId"].upper())
        policy["properties"]["principal"]["type"] = "activedirectory"
        arm, vfs = _Arm(existing=True, policies={POLICY_NAME: policy}), _Vfs({})
        self.assertTrue(self._create(arm, vfs, force=True)["connectionsJson"]["updated"])
        self._assert_attempted_acl_retained(arm)

    def test_policy_principal_changed_during_consent_is_not_overwritten(self):
        for existing in (False, True):
            with self.subTest(existing=existing):
                arm = _Arm(existing=existing, policies={POLICY_NAME: _policy()} if existing else {})
                vfs = _Vfs({})
                replacement = _policy(object_id="other-principal")

                def replace_policy(*_args, **_kwargs):
                    arm.policies[POLICY_NAME] = replacement
                    return {"confirmed": True}

                with self.assertRaises(CLIInternalError if existing else ValidationError) as caught:
                    self._create(arm, vfs, force=existing, runner=replace_policy)
                error = caught.exception.__cause__ if existing else caught.exception
                self.assertIsInstance(error, ValidationError)
                self.assertIn("does not match the selected principal", str(error))
                self.assertEqual({POLICY_NAME: replacement}, arm.policies)
                self.assertEqual(1, len(arm.mutations))
                self.assertEqual("PUT", arm.mutations[0][0])
                self.assertEqual(CONNECTION_ID, arm.mutations[0][1])
                self.assertEqual(0, vfs.writes)
                self.assertEqual([], arm.deletes)

    def test_new_readback_failure_and_disconnected_oauth_retain_arm_state(self):
        for disconnected in (False, True):
            with self.subTest(disconnected=disconnected):
                arm, vfs = _Arm(), _Vfs({})
                arm.disconnected = disconnected
                if not disconnected:
                    arm.fail("GET", CONNECTION_ID, ValidationError("Readback failed"), occurrence=2)
                with self.assertRaises(ValidationError):
                    self._create(arm, vfs)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)
                self.assertEqual(vfs.writes, 0)

    def test_forced_existing_readback_failure_retains_attempted_acl(self):
        policies = {POLICY_NAME: _policy(), "other": _policy("other", "other-principal")}
        arm, vfs = _Arm(existing=True, policies=policies), _Vfs({})
        error = OSError("Readback failed")
        arm.fail("GET", CONNECTION_ID, error, occurrence=2)
        self._assert_retained_failure(arm, vfs, error)
        self._assert_attempted_acl_retained(arm, policies)

    def test_invalid_readback_response_unwinds_before_writing_file(self):
        arm, vfs = _Arm(), _Vfs({})
        arm.responses[("GET", CONNECTION_ID, 2)] = []
        with self.assertRaisesRegex(CLIInternalError, "invalid connection"):
            self._create(arm, vfs, auth_mode="raw")
        self.assertIsNotNone(arm.connection)
        self._assert_attempted_acl_retained(arm)
        self.assertEqual(vfs.writes, 0)

    def test_forced_existing_disconnected_readback_retains_resource(self):
        arm, vfs = _Arm(existing=True), _Vfs({})
        arm.disconnected = True
        with self.assertRaises(CLIInternalError) as caught:
            self._create(arm, vfs, force=True)
        self.assertIsInstance(caught.exception.__cause__, ValidationError)
        self.assertIsNotNone(arm.connection)
        self._assert_attempted_acl_retained(arm)
        self.assertNotIn("has been removed", str(caught.exception))

    def test_keyboard_interrupt_during_acl_write_retains_attempted_policy(self):
        policies = {POLICY_NAME: _policy()}
        arm, vfs = _Arm(existing=True, policies=policies), _Vfs({})
        error = KeyboardInterrupt()
        arm.fail("PUT", POLICY_ID, error, after=True)
        with mock.patch("knack.log.get_logger"):
            with self.assertRaises(KeyboardInterrupt):
                self._create(arm, vfs, force=True)
        self._assert_attempted_acl_retained(arm, policies)

    def test_initial_vfs_read_failure_stops_before_arm_mutation(self):
        for existing in (False, True):
            with self.subTest(existing=existing):
                arm, vfs = _Arm(existing=existing), _Vfs({})
                error = OSError("VFS unavailable")
                vfs.read_failures[1] = error
                with self.assertRaises(OSError) as caught:
                    self._create(arm, vfs, force=existing)
                self.assertIs(caught.exception, error)
                self.assertEqual(arm.mutations, [])

    def test_final_vfs_read_failure_retains_arm_state(self):
        arm, vfs = _Arm(), _Vfs({})
        error = OSError("VFS unavailable during wiring")
        vfs.read_failures[2] = error
        with self.assertRaises(OSError) as caught:
            self._create(arm, vfs)
        self.assertIs(caught.exception, error)
        self.assertIsNotNone(arm.connection)
        self._assert_attempted_acl_retained(arm)

    def test_vfs_write_failure_retains_arm_state_for_all_auth_modes(self):
        for auth_mode in managed.AUTH_MODES:
            with self.subTest(auth_mode=auth_mode):
                arm, vfs = _Arm(), _Vfs({})
                error = OSError("VFS write failed")
                vfs.write_failures[1] = (error, False)
                with mock.patch.object(managed, "_managed_identity_parameter_set", return_value="mi"):
                    with self.assertRaises(OSError) as caught:
                        self._create(arm, vfs, auth_mode=auth_mode)
                self.assertIs(caught.exception, error)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)
                self.assertEqual(vfs.payload, {})

    def test_forced_existing_vfs_failure_preserves_file_and_unrelated_policies(self):
        original = {
            "managedApiConnections": {"conn": {"original": True}, "other": {"keep": True}},
            "serviceProviderConnections": {"blob": {"keep": True}},
        }
        for has_policy in (False, True):
            with self.subTest(has_policy=has_policy):
                policies = {"other": _policy("other", "other-principal")}
                if has_policy:
                    policies[POLICY_NAME] = _policy()
                arm, vfs = _Arm(existing=True, policies=policies), _Vfs(original)
                before = vfs.content
                error = OSError("VFS write failed")
                vfs.write_failures[1] = (error, False)
                self._assert_retained_failure(arm, vfs, error)
                self._assert_attempted_acl_retained(arm, policies)
                self.assertEqual(vfs.content, before)

    def test_forced_existing_success_retains_unrelated_state_and_redacts_runtime_url(self):
        original = {
            "managedApiConnections": {"conn": {"old": True}, "other": {"keep": True}},
            "serviceProviderConnections": {"blob": {"keep": True}},
        }
        policies = {POLICY_NAME: _policy(), "other": _policy("other", "other-principal")}
        arm, vfs = _Arm(existing=True, policies=policies), _Vfs(original)
        result = self._create(arm, vfs, force=True)
        self.assertTrue(result["connectionsJson"]["updated"])
        self.assertEqual(result["connection"]["id"], CONNECTION_ID)
        self.assertNotIn("https://connection.invalid", json.dumps(result))
        self.assertEqual(arm.policies["other"], policies["other"])
        self.assertEqual(vfs.payload["managedApiConnections"]["other"], {"keep": True})
        self.assertEqual(vfs.payload["serviceProviderConnections"], original["serviceProviderConnections"])
        self.assertEqual(arm.deletes, [])

    def test_vfs_write_cancellation_retains_unowned_file_and_arm_state(self):
        for existing in (False, True):
            for error in (KeyboardInterrupt(), SystemExit(130), asyncio.CancelledError()):
                for after in (False, True):
                    with self.subTest(existing=existing, error=type(error).__name__, after=after):
                        policies = {POLICY_NAME: _policy()} if existing else {}
                        arm, vfs = _Arm(existing=existing, policies=policies), _Vfs(
                            {"managedApiConnections": {"conn": {"old": True}}})
                        before = vfs.content
                        vfs.write_failures[1] = (error, after)
                        with mock.patch("knack.log.get_logger"):
                            with self.assertRaises(type(error)) as caught:
                                self._create(arm, vfs, force=existing)
                        self.assertIs(caught.exception, error)
                        self.assertEqual(vfs.content == before, not after)
                        self._assert_attempted_acl_retained(arm, policies)
                        self.assertIsNotNone(arm.connection)
                        self.assertEqual(arm.deletes, [])

    def test_vfs_failed_response_after_applied_write_retains_unowned_revision(self):
        original = {
            "managedApiConnections": {"conn": {"old": True}, "other": {"keep": True}},
            "serviceProviderConnections": {"blob": {"keep": True}},
            "custom": {"unknown": [1, 2]},
        }
        for existing in (False, True):
            with self.subTest(existing=existing):
                arm, vfs = _Arm(existing=existing), _Vfs(original)
                before = vfs.content
                error = OSError("VFS response lost")
                vfs.write_failures[1] = (error, True)
                if existing:
                    self._assert_retained_failure(arm, vfs, error)
                else:
                    with self.assertRaisesRegex(CLIInternalError, "Could not restore"):
                        self._create(arm, vfs)
                    self.assertIsNotNone(arm.connection)
                    self._assert_attempted_acl_retained(arm)
                self.assertNotEqual(vfs.content, before)
                self.assertEqual(1, vfs.writes)

    def test_existing_file_and_unrelated_entries_are_preserved(self):
        for initial in ({}, {
                "managedApiConnections": {"other": {"keep": True}},
                "serviceProviderConnections": {"blob": {"keep": True}},
                "functionConnections": {"function": {"keep": True}},
                "custom": {"keep": [1, 2]},
        }):
            with self.subTest(initial=initial):
                arm, vfs = _Arm(), _Vfs(initial)
                result = self._create(arm, vfs)
                self.assertTrue(result["connectionsJson"]["updated"])
                self.assertEqual(vfs.payload["managedApiConnections"]["conn"]["connection"]["id"], CONNECTION_ID)
                for key, value in ({} if initial is _MISSING else initial).items():
                    if key == "managedApiConnections":
                        self.assertEqual(vfs.payload[key]["other"], value["other"])
                    else:
                        self.assertEqual(vfs.payload[key], value)
                self.assertNotIn("conn", ({} if initial is _MISSING else initial).get("managedApiConnections", {}))
                self.assertEqual(arm.deletes, [])

    def test_missing_file_blocks_creation_before_arm_mutation(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs()
                with self.assertRaisesRegex(ClientRequestError, "strong connections.json ETag"):
                    self._create(arm, _vfs_client(vfs, http))
                self.assertIsNone(vfs.content)
                self.assertEqual([], arm.mutations)
                self.assertEqual(0, vfs.writes)

    def test_malformed_file_and_wrong_json_shapes_are_never_overwritten(self):
        for raw in (b"{not-json", b"", b"[]", b"null", b'"text"',
                    b'{"managedApiConnections":[]}', b'{"managedApiConnections":null}'):
            for existing in (False, True):
                with self.subTest(raw=raw, existing=existing):
                    arm, vfs = _Arm(existing=existing), _Vfs(raw=raw)
                    with self.assertRaises(ValidationError):
                        self._create(arm, vfs, force=existing)
                    self.assertEqual(arm.mutations, [])
                    self.assertEqual(vfs.content, raw)
                    self.assertEqual(vfs.writes, 0)

    def test_duplicate_and_nonfinite_connection_json_is_preserved_before_arm_mutations(self):
        samples = (
            b'{"managedApiConnections":{},"managedApiConnections":{"conn":{"old":true}}}',
            b'{"managedApiConnections":{"conn":{"old":true},"conn":{"other":true}}}',
            b'{"custom":{"keep":true,"keep":false}}',
            b'{"custom":NaN}', b'{"custom":Infinity}', b'{"custom":-Infinity}', b'{"custom":1e999}',
        )
        for http in (False, True):
            for raw in samples:
                with self.subTest(http=http, raw=raw):
                    arm, vfs = _Arm(), _Vfs(raw=raw)
                    with self.assertRaisesRegex(ValidationError, "not valid JSON"):
                        self._create(arm, _vfs_client(vfs, http))
                    self.assertEqual(raw, vfs.content)
                    self.assertEqual([], arm.mutations)
                    self.assertEqual(0, vfs.writes)

    def test_ambiguous_final_reread_blocks_publication_without_compensating_arm(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({})
                raw = b'{"custom":{"keep":true,"keep":false}}'

                def competing_write(*_args, **_kwargs):
                    vfs.content = raw
                    return {"confirmed": True}

                with self.assertRaisesRegex(ValidationError, "not valid JSON"):
                    self._create(arm, _vfs_client(vfs, http), runner=competing_write)
                self.assertEqual(raw, vfs.content)
                self.assertEqual(0, vfs.writes)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)

    def test_malformed_file_on_final_read_unwinds_without_overwrite(self):
        arm, vfs = _Arm(), _Vfs({})

        def corrupt(*_args, **_kwargs):
            vfs.content = b"{bad"
            return {"confirmed": True}

        with self.assertRaises(ValidationError):
            self._create(arm, vfs, runner=corrupt)
        self.assertEqual(vfs.content, b"{bad")
        self.assertEqual(vfs.writes, 0)
        self.assertIsNotNone(arm.connection)
        self.assertEqual([], arm.deletes)

    def test_concurrent_unrelated_entries_survive_failed_write_rollback(self):
        for initial in ({}, {"managedApiConnections": {"other": {"keep": True}}}):
            with self.subTest(initial=initial):
                arm, vfs = _Arm(), _Vfs(initial)
                vfs.write_failures[1] = (OSError("VFS response lost"), True)

                def concurrent_edit(client):
                    payload = client.payload
                    payload["serviceProviderConnections"] = {"new-other": {"keep": True}}
                    client.content = json.dumps(payload).encode("utf-8")

                vfs.on_write = concurrent_edit
                with self.assertRaisesRegex(CLIInternalError, "Could not restore"):
                    self._create(arm, vfs)
                self.assertIn("conn", vfs.payload.get("managedApiConnections", {}))
                self.assertEqual(vfs.payload["serviceProviderConnections"], {"new-other": {"keep": True}})
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)

    def test_concurrent_target_entry_change_before_write_is_not_overwritten(self):
        arm, vfs = _Arm(), _Vfs({})

        def change_entry(*_args, **_kwargs):
            vfs.content = b'{"managedApiConnections":{"conn":{"concurrent":true}}}'
            return {"confirmed": True}

        with self.assertRaisesRegex(ValidationError, "entry changed"):
            self._create(arm, vfs, runner=change_entry)
        self.assertEqual(vfs.payload["managedApiConnections"]["conn"], {"concurrent": True})
        self.assertEqual(vfs.writes, 0)
        self.assertIsNotNone(arm.connection)
        self.assertEqual([], arm.deletes)

    def test_type_only_selected_entry_changes_block_publication_and_readback(self):
        for http in (False, True):
            for old, new in ((True, 1), (1, 1.0)):
                for stage in ("beforeWrite", "readback"):
                    with self.subTest(http=http, old=old, new=new, stage=stage):
                        original = {"metadata": {"values": [old]}}
                        vfs = _Vfs({"managedApiConnections": {"conn": original}})
                        wiring = managed._ConnectionsFile(None, "rg", "app", "conn", _vfs_client(vfs, http))

                        def change(client):
                            current = client.payload
                            current["managedApiConnections"]["conn"]["metadata"]["values"][0] = new
                            client.content = json.dumps(current).encode()

                        if stage == "beforeWrite":
                            change(vfs)
                            expected = ValidationError
                            attempted = {"replacement": True}
                        else:
                            vfs.on_write = change
                            expected = ClientRequestError
                            attempted = original
                        with self.assertRaises(expected):
                            wiring.write(attempted)
                        self.assertIs(type(new), type(vfs.payload["managedApiConnections"]["conn"]
                                                      ["metadata"]["values"][0]))
                        self.assertEqual(0 if stage == "beforeWrite" else 1, vfs.writes)

    def test_type_only_selected_changes_block_restoration_without_false_noop(self):
        for old, new in ((True, 1), (1, 1.0)):
            for stage in ("previous", "attempted"):
                with self.subTest(old=old, new=new, stage=stage):
                    previous = {"value": old} if stage == "previous" else {"original": True}
                    vfs = _Vfs({"managedApiConnections": {"conn": previous}})
                    wiring = managed._ConnectionsFile(None, "rg", "app", "conn", vfs)
                    wiring.write({"value": old})
                    vfs.content = json.dumps({"managedApiConnections": {"conn": {"value": new}}}).encode()
                    with self.assertRaisesRegex(ValidationError, "entry changed"):
                        wiring.restore()
                    self.assertIs(type(new), type(vfs.payload["managedApiConnections"]["conn"]["value"]))
                    self.assertEqual(1, vfs.writes)

    def test_type_only_unrelated_changes_block_restoration_of_another_revision(self):
        for old, new in ((True, 1), (1, 1.0)):
            with self.subTest(old=old, new=new):
                vfs = _Vfs({"custom": {"values": [old]}})
                wiring = managed._ConnectionsFile(None, "rg", "app", "conn", vfs)
                wiring.write({"created": True})
                current = vfs.payload
                current["custom"]["values"][0] = new
                vfs.content = json.dumps(current).encode()
                with self.assertRaisesRegex(ValidationError, "owned revision"):
                    wiring.restore()
                self.assertIn("managedApiConnections", vfs.payload)
                self.assertIs(type(new), type(vfs.payload["custom"]["values"][0]))
                self.assertEqual(1, vfs.writes)

    def test_uncertain_write_never_restores_an_identical_entry_owned_by_another_writer(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({})

                def competing_write(client):
                    current = client.payload
                    current["custom"] = {"concurrent": True}
                    client.content = json.dumps(current).encode()

                vfs.on_write = competing_write
                vfs.write_failures[1] = (OSError("Response lost"), True)
                with self.assertRaisesRegex(CLIInternalError, "Could not restore"):
                    self._create(arm, _vfs_client(vfs, http))
                self.assertIn("conn", vfs.payload["managedApiConnections"])
                self.assertEqual({"concurrent": True}, vfs.payload["custom"])
                self.assertEqual(1, vfs.writes)
                self._assert_attempted_acl_retained(arm)

    def test_completed_write_receipt_does_not_authorize_restoring_a_newer_revision(self):
        vfs = _Vfs({})
        wiring = managed._ConnectionsFile(None, "rg", "app", "conn", vfs)
        wiring.write({"created": True})
        current = vfs.payload
        current["custom"] = {"concurrent": True}
        vfs.content = json.dumps(current).encode()
        with self.assertRaisesRegex(ValidationError, "owned revision"):
            wiring.restore()
        self.assertEqual(current, vfs.payload)
        self.assertEqual(1, vfs.writes)

    def test_completed_write_requires_a_strong_receipt_revision_not_readback_revision(self):
        for etag in (None, "*", 'W/"weak"', '"a","b"', ""):
            with self.subTest(etag=etag):
                vfs = _Vfs({})
                send = vfs.put_raw

                def receipt(*args, **kwargs):
                    result = send(*args, **kwargs)
                    result["headers"] = {"ETag": etag} if etag is not None else {}
                    return result

                with mock.patch.object(vfs, "put_raw", side_effect=receipt):
                    wiring = managed._ConnectionsFile(None, "rg", "app", "conn", vfs)
                    with self.assertRaises(ClientRequestError):
                        wiring.write({"created": True})
                    with self.assertRaisesRegex(ValidationError, "No completed"):
                        wiring.restore()
                self.assertEqual(1, vfs.writes)

    def test_decline_logs_retained_arm_state_without_attempting_unsafe_cleanup(self):
        arm, vfs = _Arm(), _Vfs({})
        error = ValidationError("Declined")
        arm.fail("DELETE", CONNECTION_ID, OSError("Cleanup unavailable"))
        with mock.patch("knack.log.get_logger") as logger:
            with self.assertRaises(ValidationError) as caught:
                self._create(arm, vfs, runner=mock.Mock(side_effect=error))
        self.assertIs(caught.exception, error)
        self.assertIn("manual recovery", logger.return_value.error.call_args.args[0])
        self.assertEqual([], arm.deletes)
        self.assertIsNotNone(arm.connection)

    def test_failed_verification_and_cleanup_do_not_claim_resource_removal(self):
        arm, vfs = _Arm(), _Vfs({})
        arm.disconnected = True
        arm.fail("DELETE", CONNECTION_ID, OSError("Cleanup unavailable"))
        with mock.patch("knack.log.get_logger") as logger:
            with self.assertRaises(ValidationError) as caught:
                self._create(arm, vfs)
        self.assertNotIn("has been removed", str(caught.exception))
        self.assertIn("manual recovery", logger.return_value.error.call_args.args[0])
        self.assertEqual([], arm.deletes)
        self.assertIsNotNone(arm.connection)

    def test_file_restore_failure_retains_arm_state_and_reports_manual_recovery(self):
        arm, vfs = _Arm(), _Vfs({})
        error = OSError("VFS response lost")
        vfs.write_failures[1] = (error, True)
        vfs.write_failures[2] = (OSError("Restore unavailable"), False)
        with self.assertRaises(CLIInternalError) as caught:
            self._create(arm, vfs)
        self.assertIs(caught.exception.__cause__, error)
        self.assertIn("Could not restore connections.json entry", str(caught.exception))
        self.assertIsNotNone(arm.connection)
        self._assert_attempted_acl_retained(arm)

    def test_concurrent_target_entry_during_rollback_is_preserved_and_reported(self):
        arm, vfs = _Arm(existing=True), _Vfs({})
        error = OSError("VFS response lost")
        vfs.write_failures[1] = (error, True)

        def change_target(client):
            client.content = b'{"managedApiConnections":{"conn":{"concurrent":true}}}'

        vfs.on_write = change_target
        with self.assertRaises(CLIInternalError) as caught:
            self._create(arm, vfs, force=True)
        self.assertIs(caught.exception.__cause__, error)
        self.assertIn("manual recovery is required", str(caught.exception))
        self.assertEqual(vfs.payload["managedApiConnections"]["conn"], {"concurrent": True})
        self.assertEqual(arm.deletes, [])
        self.assertIsNotNone(arm.connection)

    def test_readback_failure_does_not_replay_an_unconditionally_updated_policy(self):
        arm, vfs = _Arm(existing=True, policies={POLICY_NAME: _policy()}), _Vfs({})
        error = OSError("Readback unavailable")
        arm.fail("GET", CONNECTION_ID, error, occurrence=2)
        arm.fail("PUT", POLICY_ID, OSError("Policy restore unavailable"), occurrence=2)
        self._assert_retained_failure(arm, vfs, error)
        self.assertEqual(arm.deletes, [])
        self.assertEqual(1, sum(method == "PUT" and path == POLICY_ID for method, path, _ in arm.calls))

    def test_retry_after_vfs_failure_requires_explicit_force_for_retained_resource(self):
        arm, vfs = _Arm(), _Vfs({})
        vfs.write_failures[1] = (OSError("Write failed"), False)
        with self.assertRaises(OSError):
            self._create(arm, vfs)
        before = copy.deepcopy(arm.mutations)
        with self.assertRaisesRegex(ValidationError, "already exists"):
            self._create(arm, vfs)
        self.assertEqual(before, arm.mutations)
        result = self._create(arm, vfs, force=True)
        self.assertTrue(result["connectionsJson"]["updated"])
        self.assertIsNotNone(arm.connection)
        self.assertIn(POLICY_NAME, arm.policies)

    def test_default_vfs_factory_is_used_without_changing_shared_helper(self):
        arm, vfs = _Arm(), _Vfs({})
        with mock.patch("azext_logicapp._connection._vfs_client", return_value=vfs) as factory:
            result = self._create(arm, None)
        factory.assert_called_once()
        self.assertTrue(result["connectionsJson"]["updated"])
        self.assertIn("conn", vfs.payload["managedApiConnections"])

    def test_standalone_writer_rejects_malformed_payload_and_does_not_mutate_input(self):
        for value in ([], None, {"managedApiConnections": "wrong"}):
            with self.subTest(value=value):
                client = SimpleNamespace(
                    get=lambda _path: value,
                    put_raw=mock.Mock(side_effect=AssertionError("Must not write malformed content")))
                with self.assertRaises(ValidationError):
                    managed.write_connections_entry(None, "rg", "app", "conn", {}, vfs_client=client)
        value = {"managedApiConnections": {"other": {"keep": True}}, "custom": {"keep": True}}
        before = copy.deepcopy(value)
        client = _DecodedVfs(value)
        with self.assertRaisesRegex(ClientRequestError, "strong connections.json ETag"):
            managed.write_connections_entry(None, "rg", "app", "conn", {"new": True}, vfs_client=client)
        self.assertIsNone(client.written)
        client = _Vfs(value)
        managed.write_connections_entry(None, "rg", "app", "conn", {"new": True}, vfs_client=client)
        self.assertEqual(value, before)
        self.assertEqual(client.payload["custom"], {"keep": True})
        self.assertEqual(client.payload["managedApiConnections"]["conn"], {"new": True})

    def test_incomplete_vfs_receipts_never_report_creation_success_or_delete_arm_state(self):
        for http in (False, True):
            for status in (202, 203, 206, None):
                for apply in (False, True):
                    with self.subTest(http=http, status=status, apply=apply):
                        arm, vfs = _Arm(), _Vfs({"custom": {"keep": True}})
                        vfs.write_status, vfs.apply_write = status, apply
                        before = vfs.content
                        with self.assertRaisesRegex(ClientRequestError, "completed receipt"):
                            self._create(arm, _vfs_client(vfs, http))
                        self.assertIsNotNone(arm.connection)
                        self._assert_attempted_acl_retained(arm)
                        self.assertEqual(1, vfs.writes)
                        self.assertEqual(2, vfs.reads)
                        if not apply:
                            self.assertEqual(before, vfs.content)

    def test_completed_vfs_receipt_without_publication_is_not_creation_success(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({"managedApiConnections": {"conn": {"old": True}},
                                        "custom": {"keep": True}})
                before = vfs.content
                vfs.apply_write = False
                with self.assertRaisesRegex(ClientRequestError, "selected entry did not match"):
                    self._create(arm, _vfs_client(vfs, http))
                self.assertEqual(before, vfs.content)
                self.assertEqual(1, vfs.writes)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)

    def test_mismatching_publication_readback_preserves_latest_target_and_unrelated_entries(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({})
                latest = {"managedApiConnections": {"conn": {"otherWriter": True}},
                          "serviceProviderConnections": {"latest": {"keep": True}}}
                vfs.on_write = lambda client: setattr(client, "content", json.dumps(latest).encode())
                with self.assertRaises(CLIInternalError) as caught:
                    self._create(arm, _vfs_client(vfs, http))
                self.assertIsInstance(caught.exception.__cause__, ClientRequestError)
                self.assertEqual(latest, vfs.payload)
                self.assertEqual(1, vfs.writes)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)

    def test_publication_readback_failure_is_sanitized_and_retains_arm_state(self):
        for http in (False, True):
            for persistent in (False, True):
                with self.subTest(http=http, persistent=persistent):
                    arm, vfs = _Arm(), _Vfs({"custom": {"keep": True}})
                    error = HTTPError("provider body https://private.invalid/?sig=private-token",
                                      _Response({"secret": "private-file-content"}, status=403))
                    vfs.read_failures[3] = error
                    if persistent:
                        vfs.read_failures[4] = error
                    with self.assertRaises((ClientRequestError, CLIInternalError)) as caught:
                        self._create(arm, _vfs_client(vfs, http))
                    for visible in (caught.exception, caught.exception.__cause__):
                        if visible is error:
                            continue
                        self.assertNotIn("private-token", str(visible))
                        self.assertNotIn("private-file-content", str(visible))
                        self.assertNotIn("provider body", str(visible))
                    self.assertIsNotNone(arm.connection)
                    self._assert_attempted_acl_retained(arm)

    def test_provider_write_errors_are_sanitized_and_do_not_compensate_arm_state(self):
        for http in (False, True):
            for after in (False, True):
                for error in (HTTPError("provider body https://private.invalid/?sig=private-token",
                                        _Response({"secret": "private-file-content"}, status=403)),
                              RequestsTimeout("https://private.invalid/?sig=private-token")):
                    with self.subTest(http=http, after=after, error=type(error).__name__):
                        arm, vfs = _Arm(), _Vfs({"custom": {"keep": True}})
                        before = vfs.content
                        vfs.write_failures[1] = (error, after)
                        expected = CLIInternalError if after else ClientRequestError
                        message = "Could not restore" if after else "publication could not be verified"
                        with self.assertRaisesRegex(expected, message) as caught:
                            self._create(arm, _vfs_client(vfs, http))
                        self.assertNotIn("private-token", str(caught.exception))
                        self.assertNotIn("private-file-content", str(caught.exception))
                        self.assertNotIn("provider body", str(caught.exception))
                        self.assertEqual(vfs.content == before, not after)
                        self.assertIsNotNone(arm.connection)
                        self._assert_attempted_acl_retained(arm)

    def test_real_vfs_completed_receipt_and_entry_readback_report_creation_success(self):
        for status in (200, 201, 204):
            with self.subTest(status=status):
                arm, vfs = _Arm(), _Vfs({"managedApiConnections": {"other": {"keep": True}}})
                vfs.write_status = status

                def latest_unrelated(client):
                    current = client.payload
                    current["serviceProviderConnections"] = {"latest": {"keep": True}}
                    client.content = json.dumps(current).encode()

                vfs.on_write = latest_unrelated
                result = self._create(arm, _vfs_client(vfs, True))
                self.assertTrue(result["connectionsJson"]["updated"])
                self.assertEqual(CONNECTION_ID, vfs.payload["managedApiConnections"]["conn"]["connection"]["id"])
                self.assertEqual({"keep": True}, vfs.payload["managedApiConnections"]["other"])
                self.assertEqual({"latest": {"keep": True}}, vfs.payload["serviceProviderConnections"])
                self.assertEqual(3, vfs.reads)
                self.assertEqual(1, vfs.writes)
                self.assertEqual([], arm.deletes)

    def test_latest_unrelated_entries_before_publication_are_merged_with_real_vfs(self):
        arm, vfs = _Arm(), _Vfs({"managedApiConnections": {"other": {"keep": True}}})

        def latest_unrelated(*_args, **_kwargs):
            current = vfs.payload
            current["custom"] = {"latest": True}
            vfs.content = json.dumps(current).encode()
            return {"confirmed": True}

        result = self._create(arm, _vfs_client(vfs, True), runner=latest_unrelated)
        self.assertTrue(result["connectionsJson"]["updated"])
        self.assertEqual({"latest": True}, vfs.payload["custom"])
        self.assertEqual({"keep": True}, vfs.payload["managedApiConnections"]["other"])
        self.assertIn("conn", vfs.payload["managedApiConnections"])

    def test_publication_conflict_preserves_concurrent_unrelated_change_and_retains_arm(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({"custom": {"before": True}})
                selected_etag = vfs.etag

                def competing_write(client):
                    client.content = b'{"custom":{"concurrent":true}}'

                vfs.on_before_write = competing_write
                with self.assertRaisesRegex(ClientRequestError, "revision changed before publication"):
                    self._create(arm, _vfs_client(vfs, http))
                self.assertEqual({"custom": {"concurrent": True}}, vfs.payload)
                self.assertEqual([selected_etag], vfs.conditions)
                self.assertEqual(1, vfs.writes)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)

    def test_creation_requires_strong_revision_before_any_arm_mutation(self):
        for http in (False, True):
            for etag in (None, "*", '"*"', 'W/"r1"', '"r1","r2"', '"r1"\r\nInjected: secret', ""):
                with self.subTest(http=http, etag=etag):
                    arm, vfs = _Arm(), _Vfs({})
                    vfs.etag_override = etag
                    with self.assertRaises(ClientRequestError):
                        self._create(arm, _vfs_client(vfs, http))
                    self.assertEqual([], arm.mutations)
                    self.assertEqual(0, vfs.writes)

    def test_rejected_publication_does_not_restore_another_writers_identical_selected_entry(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({})

                def competing_write(client):
                    current = json.loads(client.pending_content)
                    current["custom"] = {"concurrent": True}
                    client.content = json.dumps(current).encode()

                vfs.on_before_write = competing_write
                with self.assertRaisesRegex(ClientRequestError, "revision changed before publication"):
                    self._create(arm, _vfs_client(vfs, http))
                self.assertIn("conn", vfs.payload["managedApiConnections"])
                self.assertEqual({"concurrent": True}, vfs.payload["custom"])
                self.assertEqual(1, vfs.writes)
                self._assert_attempted_acl_retained(arm)

    def test_missing_revision_at_final_reread_blocks_publication_and_retains_arm(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({})

                def lose_revision(client):
                    if client.reads == 2:
                        client.etag_override = None

                vfs.on_read = lose_revision
                with self.assertRaisesRegex(ClientRequestError, "strong connections.json ETag"):
                    self._create(arm, _vfs_client(vfs, http))
                self.assertEqual(0, vfs.writes)
                self.assertIsNotNone(arm.connection)
                self._assert_attempted_acl_retained(arm)

    def test_publication_uses_final_reread_etag_not_initial_revision(self):
        arm, vfs = _Arm(), _Vfs({})
        before = vfs.etag
        expected = []

        def competing_write(*_args, **_kwargs):
            vfs.content = b'{"custom":{"concurrent":true}}'
            expected.append(vfs.etag)
            return {"confirmed": True}

        self._create(arm, _vfs_client(vfs, True), runner=competing_write)
        self.assertNotEqual(before, expected[0])
        self.assertEqual(expected, vfs.conditions)
        self.assertEqual({"concurrent": True}, vfs.payload["custom"])

    def test_conditional_restoration_refuses_concurrent_whole_file_revision(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm, vfs = _Arm(), _Vfs({})
                vfs.read_failures[3] = OSError("Readback lost after completed receipt")

                def arm_restoration_race(client):
                    def competing_write(target):
                        current = target.payload
                        current["custom"] = {"concurrent": True}
                        target.content = json.dumps(current).encode()
                    client.on_before_write = competing_write

                vfs.on_write = arm_restoration_race
                with self.assertRaisesRegex(CLIInternalError, "Could not restore connections.json entry"):
                    self._create(arm, _vfs_client(vfs, http))
                self.assertEqual({"concurrent": True}, vfs.payload["custom"])
                self.assertIn("conn", vfs.payload["managedApiConnections"])
                self.assertEqual(2, vfs.writes)
                self.assertTrue(all(tag and tag != "*" for tag in vfs.conditions))
                self._assert_attempted_acl_retained(arm)


class ConnectionRemovalPublicationRegressions(unittest.TestCase):
    def _payload(self):
        return {"managedApiConnections": {
            "conn": managed.build_connections_entry(CONNECTOR_ID, CONNECTION_ID, None)},
            "serviceProviderConnections": {"other": {"keep": True}}}

    def _delete(self, arm, vfs):
        with mock.patch.object(_connection, "_app_system_principal", return_value=PRINCIPAL), \
                mock.patch("azure.cli.core.commands.client_factory.get_subscription_id", return_value="sub"):
            return _connection.connection_delete(
                SimpleNamespace(cli_ctx=object()), "rg", "app", "conn",
                client=vfs, sender=arm.send)

    def test_conditional_removal_conflict_preserves_file_and_blocks_all_arm_mutations(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                vfs = _Vfs(self._payload())
                expected = vfs.etag

                def competing_write(client):
                    current = client.payload
                    current["serviceProviderConnections"]["latest"] = {"keep": True}
                    client.content = json.dumps(current).encode()

                vfs.on_before_write = competing_write
                with self.assertRaisesRegex(ClientRequestError, "revision changed before removal"):
                    self._delete(arm, _vfs_client(vfs, http))
                self.assertIn("conn", vfs.payload["managedApiConnections"])
                self.assertEqual({"keep": True}, vfs.payload["serviceProviderConnections"]["latest"])
                self.assertEqual([expected], vfs.conditions)
                self.assertEqual([], arm.mutations)
                self.assertEqual(1, vfs.writes)

    def test_ambiguous_or_nonfinite_connection_json_blocks_removal_before_arm_cleanup(self):
        entry = json.dumps(self._payload()["managedApiConnections"])
        samples = [
            ('{"managedApiConnections":{},"managedApiConnections":' + entry + '}').encode(),
            ('{"managedApiConnections":' + entry + ',"custom":{"keep":true,"keep":false}}').encode(),
        ]
        samples.extend(('{"managedApiConnections":' + entry + ',"custom":' + value + '}').encode()
                       for value in ("NaN", "Infinity", "-Infinity", "1e999"))
        for http in (False, True):
            for raw in samples:
                with self.subTest(http=http, raw=raw):
                    arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                    vfs = _Vfs(raw=raw)
                    with self.assertRaisesRegex(ValidationError, "not valid JSON"):
                        self._delete(arm, _vfs_client(vfs, http))
                    self.assertEqual(raw, vfs.content)
                    self.assertEqual([], arm.mutations)
                    self.assertEqual(0, vfs.writes)

    def test_missing_or_invalid_reread_etag_blocks_removal_and_arm_cleanup(self):
        for http in (False, True):
            for etag in (None, "*", '"*"', 'W/"r1"', '"r1","r2"', '"r1"\r\nInjected: secret', ""):
                with self.subTest(http=http, etag=etag):
                    arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                    vfs = _Vfs(self._payload())
                    before = vfs.content
                    vfs.etag_override = etag
                    with self.assertRaises(ClientRequestError):
                        self._delete(arm, _vfs_client(vfs, http))
                    self.assertEqual(before, vfs.content)
                    self.assertEqual([], arm.mutations)
                    self.assertEqual(0, vfs.writes)

    def test_incomplete_removal_receipt_never_deletes_or_revokes_arm_state(self):
        for http in (False, True):
            for status in (202, 203, 206, None):
                for apply in (False, True):
                    with self.subTest(http=http, status=status, apply=apply):
                        arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                        vfs = _Vfs(self._payload())
                        before = vfs.content
                        vfs.write_status, vfs.apply_write = status, apply
                        with self.assertRaisesRegex(ClientRequestError, "completed write receipt"):
                            self._delete(arm, _vfs_client(vfs, http))
                        self.assertEqual([], arm.mutations)
                        self.assertIsNotNone(arm.connection)
                        self.assertIn(POLICY_NAME, arm.policies)
                        self.assertEqual(1, vfs.writes)
                        self.assertEqual(2, vfs.reads)
                        if not apply:
                            self.assertEqual(before, vfs.content)

    def test_completed_removal_receipt_without_apply_is_not_success_or_arm_cleanup(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                vfs = _Vfs(self._payload())
                before = vfs.content
                vfs.apply_write = False
                with self.assertRaisesRegex(ClientRequestError, "removal could not be verified"):
                    self._delete(arm, _vfs_client(vfs, http))
                self.assertEqual(before, vfs.content)
                self.assertEqual([], arm.mutations)
                self.assertEqual(1, vfs.writes)
                self.assertEqual(3, vfs.reads)

    def test_mismatching_or_malformed_removal_readback_blocks_arm_cleanup(self):
        for http in (False, True):
            for latest in (self._payload(), [], {"managedApiConnections": []}):
                with self.subTest(http=http, latest=latest):
                    arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                    vfs = _Vfs(self._payload())
                    vfs.on_write = lambda client: setattr(client, "content", json.dumps(latest).encode())
                    with self.assertRaisesRegex(ClientRequestError, "removal (could not be verified|readback failed)"):
                        self._delete(arm, _vfs_client(vfs, http))
                    self.assertEqual(latest, vfs.payload)
                    self.assertEqual([], arm.mutations)
                    self.assertEqual(1, vfs.writes)

    def test_ambiguous_or_nonfinite_removal_readback_blocks_all_arm_cleanup(self):
        entry = json.dumps(self._payload()["managedApiConnections"])
        samples = [
            ('{"managedApiConnections":' + entry + ',"managedApiConnections":{}}').encode(),
            b'{"managedApiConnections":{},"custom":{"keep":true,"keep":false}}',
        ]
        samples.extend(('{"managedApiConnections":{},"custom":' + value + '}').encode()
                       for value in ("NaN", "Infinity", "-Infinity", "1e999"))
        for http in (False, True):
            for raw in samples:
                with self.subTest(http=http, raw=raw):
                    arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                    vfs = _Vfs(self._payload())
                    vfs.on_write = lambda client: setattr(client, "content", raw)
                    with self.assertRaisesRegex(ClientRequestError, "removal readback failed"):
                        self._delete(arm, _vfs_client(vfs, http))
                    self.assertEqual(raw, vfs.content)
                    self.assertEqual([], arm.mutations)
                    self.assertIsNotNone(arm.connection)
                    self.assertIn(POLICY_NAME, arm.policies)
                    self.assertEqual(1, vfs.writes)

    def test_missing_removal_readback_is_not_proof_for_arm_cleanup(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                vfs = _Vfs(self._payload())
                vfs.on_write = lambda client: setattr(client, "content", None)
                with self.assertRaisesRegex(ClientRequestError, "removal could not be verified"):
                    self._delete(arm, _vfs_client(vfs, http))
                self.assertIsNone(vfs.content)
                self.assertEqual([], arm.mutations)
                self.assertIsNotNone(arm.connection)
                self.assertIn(POLICY_NAME, arm.policies)
                self.assertEqual(1, vfs.writes)

    def test_removal_readback_failure_is_sanitized_and_blocks_arm_cleanup(self):
        for http in (False, True):
            with self.subTest(http=http):
                arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                vfs = _Vfs(self._payload())
                vfs.read_failures[3] = HTTPError(
                    "provider body https://private.invalid/?sig=private-token",
                    _Response({"secret": "private-file-content"}, status=403))
                with self.assertRaisesRegex(ClientRequestError, "removal readback failed") as caught:
                    self._delete(arm, _vfs_client(vfs, http))
                self.assertNotIn("private-token", str(caught.exception))
                self.assertNotIn("private-file-content", str(caught.exception))
                self.assertNotIn("provider body", str(caught.exception))
                self.assertEqual([], arm.mutations)
                self.assertEqual(1, vfs.writes)

    def test_reread_and_write_failures_are_sanitized_and_block_all_arm_mutations(self):
        for http in (False, True):
            for stage in ("reread", "writeBeforeApply", "writeAfterApply"):
                with self.subTest(http=http, stage=stage):
                    arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                    vfs = _Vfs(self._payload())
                    before = vfs.content
                    error = HTTPError("provider body https://private.invalid/?sig=private-token",
                                      _Response({"secret": "private-file-content"}, status=403))
                    if stage == "reread":
                        vfs.read_failures[2] = error
                    else:
                        vfs.write_failures[1] = (error, stage == "writeAfterApply")
                    with self.assertRaises(ClientRequestError) as caught:
                        self._delete(arm, _vfs_client(vfs, http))
                    self.assertNotIn("private-token", str(caught.exception))
                    self.assertNotIn("private-file-content", str(caught.exception))
                    self.assertNotIn("provider body", str(caught.exception))
                    self.assertEqual([], arm.mutations)
                    if stage != "writeAfterApply":
                        self.assertEqual(before, vfs.content)
                    self.assertEqual(0 if stage == "reread" else 1, vfs.writes)

    def test_latest_unrelated_entries_survive_completed_real_vfs_removal(self):
        for status in (200, 201, 204):
            with self.subTest(status=status):
                arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                vfs = _Vfs(self._payload())
                vfs.write_status = status

                def latest_unrelated(client):
                    if client.reads == 2:
                        current = client.payload
                        current["custom"] = {"latest": True}
                        client.content = json.dumps(current).encode()

                vfs.on_read = latest_unrelated
                result = self._delete(arm, _vfs_client(vfs, True))
                self.assertTrue(result["connectionsJson"]["removed"])
                self.assertTrue(result["resource"]["removed"])
                self.assertEqual([POLICY_ID, CONNECTION_ID], arm.deletes)
                self.assertNotIn("conn", vfs.payload["managedApiConnections"])
                self.assertEqual({"other": {"keep": True}}, vfs.payload["serviceProviderConnections"])
                self.assertEqual({"latest": True}, vfs.payload["custom"])
                self.assertEqual(1, vfs.writes)
                self.assertEqual(3, vfs.reads)

    def test_latest_shared_reference_retains_resource_and_all_access_policies(self):
        for observation in ("beforeWrite", "readback"):
            with self.subTest(observation=observation):
                arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                vfs = _Vfs(self._payload())

                def share(client):
                    current = client.payload
                    current["managedApiConnections"]["latest"] = managed.build_connections_entry(
                        CONNECTOR_ID, CONNECTION_ID, None)
                    client.content = json.dumps(current).encode()

                if observation == "beforeWrite":
                    vfs.on_read = lambda client: share(client) if client.reads == 2 else None
                else:
                    vfs.on_write = share
                result = self._delete(arm, _vfs_client(vfs, True))
                self.assertTrue(result["connectionsJson"]["removed"])
                self.assertFalse(result["resource"]["removed"])
                self.assertIn("Another connections.json entry", result["resource"]["reason"])
                self.assertEqual([], arm.mutations)
                self.assertIn("latest", vfs.payload["managedApiConnections"])

    def test_changed_selected_entry_before_removal_is_not_overwritten(self):
        arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
        vfs = _Vfs(self._payload())

        def change_selected(client):
            if client.reads == 2:
                current = client.payload
                current["managedApiConnections"]["conn"] = {"latest": True}
                client.content = json.dumps(current).encode()

        vfs.on_read = change_selected
        with self.assertRaisesRegex(ValidationError, "entry changed before removal"):
            self._delete(arm, _vfs_client(vfs, True))
        self.assertEqual({"latest": True}, vfs.payload["managedApiConnections"]["conn"])
        self.assertEqual(0, vfs.writes)
        self.assertEqual([], arm.mutations)

    def test_type_only_selected_entry_changes_block_removal_and_arm_cleanup(self):
        for http in (False, True):
            for old, new in ((True, 1), (1, 1.0)):
                with self.subTest(http=http, old=old, new=new):
                    arm = _Arm(existing=True, policies={POLICY_NAME: _policy()})
                    initial = self._payload()
                    initial["managedApiConnections"]["conn"]["metadata"] = {"values": [old]}
                    vfs = _Vfs(initial)

                    def change_selected(client):
                        if client.reads == 2:
                            current = client.payload
                            current["managedApiConnections"]["conn"]["metadata"]["values"][0] = new
                            client.content = json.dumps(current).encode()

                    vfs.on_read = change_selected
                    with self.assertRaisesRegex(ValidationError, "entry changed before removal"):
                        self._delete(arm, _vfs_client(vfs, http))
                    self.assertIs(type(new), type(vfs.payload["managedApiConnections"]["conn"]
                                                  ["metadata"]["values"][0]))
                    self.assertEqual(0, vfs.writes)
                    self.assertEqual([], arm.mutations)


if __name__ == "__main__":
    unittest.main(verbosity=2)
