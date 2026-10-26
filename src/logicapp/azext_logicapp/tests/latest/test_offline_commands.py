# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import socket
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import requests
from azure.cli.core.azclierror import CLIError, CLIInternalError, HTTPError, InvalidArgumentValueError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ResourceNotFoundError, ValidationError
from azure.cli.testsdk import ScenarioTest

from azext_logicapp import _connection, _context, _dependencies, _identity, _local, _managed_api, _managed_connection, _paging, _oauth_consent, _runtime_client, _workflow, commands
from azext_logicapp import custom


_SECRET_PATTERNS = (
    (re.compile(r"(?i)([?&](?:sig|code|se|sp|sv|access_token|client_secret)=)[^&\s\"']+"), r"\1Sanitized"),
    (re.compile(r'(?i)("(?:connectionString|access_token|client_secret|password)"\s*:\s*")[^"]*'), r"\1Sanitized"),
    (re.compile(r"(?i)((?:AccountKey|SharedAccessKey|SharedAccessSignature)=)[^;\s\"']+"), r"\1Sanitized"),
    (re.compile(r"(?i)(Authorization[:=]\s*Bearer\s+)[A-Za-z0-9._~+/=-]+"), r"\1Sanitized"),
)
_SECRET_MARKERS = ("AccountKey=", "SharedAccessKey=", "SharedAccessSignature=", "client_secret=", "Bearer token")


def _sanitize_text(value):
    text = str(value)
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _assert_no_secret_markers(testcase: unittest.TestCase, value):
    text = _sanitize_text(json.dumps(value, sort_keys=True) if not isinstance(value, str) else value)
    for marker in _SECRET_MARKERS:
        testcase.assertNotIn(marker, text)


def _workspace(name: str) -> Path:
    root = Path(__file__).resolve().parent / ".test-work" / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    return root


class _FakeCmd:
    cli_ctx = object()


class _FakeResponse:
    def __init__(self, payload=None, status_code=200, headers=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.content = json.dumps(payload or {}).encode("utf-8")


class _FakeVfsClient:
    def __init__(self, payload):
        self.payload = payload

    def get(self, _path):
        return self.payload


class _FakeRuntimeClient:
    def __init__(self, payload):
        self.payload = payload

    def get(self, _path):
        return self.payload


def _finished_host_process():
    process = mock.Mock(pid=999998)
    process.poll.return_value = 0
    process.wait.return_value = 0
    return process


class _RecordingVfsClient:
    """Revision-bearing VFS stub with completed receipts and persisted write bytes."""

    def __init__(self, payload):
        self.payload = payload
        self.written = None
        self.revision = 0

    @property
    def etag(self):
        return '"recording-{}"'.format(self.revision)

    def get(self, _path):
        if isinstance(self.payload, Exception):
            raise self.payload
        return json.loads(json.dumps(self.payload))

    def get_raw(self, path):
        return {"content": json.dumps(self.get(path)).encode("utf-8"), "headers": {"ETag": self.etag},
                "statusCode": 200}

    def put_raw(self, _path, content, params=None, if_match=None):
        if if_match != self.etag:
            raise AssertionError("Expected an exact file revision")
        self.written = content
        self.payload = json.loads(content)
        self.revision += 1
        return {"content": b"", "headers": {"ETag": self.etag}, "statusCode": 204}


@contextlib.contextmanager
def _fake_azure_context(subscription_id="sub1", tenant_id="tenant-1"):
    """Satisfy the ambient Azure lookups that resource-id building performs.

    Both ``get_subscription_id`` and ``Profile`` are imported inside the
    functions that use them, so patching the source module reaches every caller.
    """
    profile = mock.MagicMock()
    profile.return_value.get_subscription.return_value = {"tenantId": tenant_id}
    with mock.patch("azure.cli.core.commands.client_factory.get_subscription_id",
                    return_value=subscription_id), \
            mock.patch("azure.cli.core._profile.Profile", profile):
        yield


class _FakeCommandGroup:
    def __init__(self, loader, name):
        self.loader = loader
        self.name = name

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def custom_command(self, command_name, function_name, **kwargs):
        self.loader.record(self.name, command_name, function_name, kwargs)

    def custom_show_command(self, command_name, function_name, **kwargs):
        self.loader.record(self.name, command_name, function_name, kwargs)


class _FakeCommandLoader:
    def __init__(self):
        self.commands = {}

    def command_group(self, name):
        return _FakeCommandGroup(self, name)

    def record(self, group_name, command_name, function_name, kwargs):
        self.commands[(group_name, command_name)] = {"function": function_name, **kwargs}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class LogicAppOfflineCommandTests(ScenarioTest):
    def test_project_create_emits_measured_file_set_and_templates(self):
        root = _workspace("project-create") / "orders"
        result = custom.project_create(None, str(root), workflow="process-order")

        relative_files = sorted(Path(item["path"]).relative_to(root).as_posix() for item in result["files"])
        self.assertEqual(["host.json", "local.settings.json", "process-order/workflow.json"], relative_files)
        self.assertEqual("process-order", result["workflow"])
        self.assertEqual("Stateful", result["workflowKind"])

        host = json.loads((root / "host.json").read_text(encoding="utf-8"))
        self.assertEqual("Microsoft.Azure.Functions.ExtensionBundle.Workflows", host["extensionBundle"]["id"])
        self.assertEqual("[1.*, 2.0.0)", host["extensionBundle"]["version"])

        settings = json.loads((root / "local.settings.json").read_text(encoding="utf-8"))
        self.assertEqual("UseDevelopmentStorage=true", settings["Values"]["AzureWebJobsStorage"])
        self.assertEqual("node", settings["Values"]["FUNCTIONS_WORKER_RUNTIME"])

        workflow = json.loads((root / "process-order" / "workflow.json").read_text(encoding="utf-8"))
        self.assertEqual("Stateful", workflow["kind"])
        self.assertEqual("Request", workflow["definition"]["triggers"]["manual"]["type"])
        _assert_no_secret_markers(self, result)

    def test_workflow_validate_offline_passes_without_runtime_or_network(self):
        root = _workspace("workflow-validate-valid") / "orders"
        custom.project_create(None, str(root), workflow="process-order")

        def fail_if_runtime_client_is_built(*_args, **_kwargs):
            raise AssertionError("offline workflow validate must not build a runtime client")

        original = custom.build_runtime_client
        custom.build_runtime_client = fail_if_runtime_client_is_built
        try:
            result = custom.workflow_validate(None, path=str(root), workflow="process-order")
        finally:
            custom.build_runtime_client = original

        self.assertTrue(result["valid"])
        self.assertEqual({"errors": 0, "warnings": 0, "workflows": 1}, result["summary"])
        self.assertTrue(result["coverage"]["static"])
        self.assertFalse(result["coverage"]["runtime"])
        self.assertEqual([], result["findings"])

    def test_offline_workflow_validation_and_authoring_reject_ambiguous_json(self):
        root = _workspace("workflow-duplicate-json") / "orders"
        custom.project_create(None, str(root), workflow="process-order")
        path = root / "process-order" / "workflow.json"
        original = path.read_text()
        ambiguous = original.replace('"kind": "Stateful"', '"kind": "Stateful", "kind": "Stateful"', 1)
        self.assertNotEqual(original, ambiguous)
        path.write_text(ambiguous, encoding="utf-8")
        with self.assertRaises(CLIError) as caught:
            custom.workflow_validate(None, path=str(root), workflow="process-order")
        self.assertIn("json.invalid", str(caught.exception))
        with self.assertRaises(InvalidArgumentValueError):
            _workflow._load_definition_file(str(path))
        self.assertEqual(ambiguous, path.read_text())

    def test_runtime_validation_rejects_ambiguous_authored_json_before_post(self):
        root = _workspace("runtime-duplicate-json") / "orders"
        custom.project_create(None, str(root), workflow="process-order")
        path = root / "process-order" / "workflow.json"
        original = path.read_text()
        samples = [
            original.replace('"kind": "Stateful"', '"kind":"Stateful","kind":"Stateful"', 1),
            original.replace('"actions":', '"actions":{},"actions":', 1),
        ]
        samples.extend(original.replace('"kind": "Stateful"', '"ignored":' + value + ',"kind":"Stateful"', 1)
                       for value in ("NaN", "Infinity", "-Infinity", "1e999"))
        for raw in samples:
            with self.subTest(raw=raw[:100]):
                client = mock.Mock()
                path.write_text(raw, encoding="utf-8")
                with mock.patch.object(custom, "_client_from_target", return_value=(client, {"kind": "local"})):
                    with self.assertRaises(ValidationError) as caught:
                        custom.workflow_validate(
                            None, path=str(root), workflow="process-order", with_runtime=True, local=True)
                report = json.loads(str(caught.exception))
                self.assertFalse(report["coverage"]["checks"]["runtimeTemplate"])
                self.assertIn("json.invalid", {finding["rule"] for finding in report["findings"]})
                client.post.assert_not_called()
                self.assertEqual(raw, path.read_text())

    def test_runtime_validate_body_wraps_definition_in_properties_envelope(self):
        root = _workspace("runtime-validate-body") / "orders"
        custom.project_create(None, str(root), workflow="process-order")
        workflow_path = root / "process-order" / "workflow.json"
        raw = json.loads(workflow_path.read_text(encoding="utf-8"))

        body = custom._runtime_validate_body(str(workflow_path), "process-order", str(root))

        # The runtime deserializes this as EdgeFlowDefinition under 'properties'. Posting the
        # raw workflow.json instead fails every time with InvalidRequestContent.
        self.assertIn("properties", body)
        self.assertNotIn("definition", body)
        self.assertEqual(raw["definition"], body["properties"]["definition"])
        self.assertEqual(raw["kind"], body["properties"]["kind"])

    def test_runtime_validate_body_passes_through_existing_properties_envelope(self):
        root = _workspace("runtime-validate-body-envelope") / "orders"
        custom.project_create(None, str(root), workflow="process-order")
        workflow_path = root / "process-order" / "workflow.json"
        raw = json.loads(workflow_path.read_text(encoding="utf-8"))
        already_wrapped = {"properties": {"definition": raw["definition"], "kind": raw["kind"]}}
        workflow_path.write_text(json.dumps(already_wrapped, indent=2) + "\n", encoding="utf-8")

        body = custom._runtime_validate_body(str(workflow_path), "process-order", str(root))

        self.assertEqual(already_wrapped, body)

    def test_workflow_validate_offline_fails_broken_run_after_reference(self):
        root = _workspace("workflow-validate-broken") / "orders"
        custom.project_create(None, str(root), workflow="process-order")
        workflow_path = root / "process-order" / "workflow.json"
        payload = json.loads(workflow_path.read_text(encoding="utf-8"))
        payload["definition"]["actions"]["Response"]["runAfter"] = {"Missing_action": ["Succeeded"]}
        workflow_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        with self.assertRaises(ValidationError) as caught:
            custom.workflow_validate(None, path=str(root), workflow="process-order")
        report = json.loads(str(caught.exception))
        self.assertFalse(report["valid"])
        self.assertEqual(1, report["summary"]["errors"])
        self.assertEqual("graph.missing_action", report["findings"][0]["rule"])
        self.assertIn("Missing_action", report["findings"][0]["message"])

    def test_deployment_package_is_deterministic_and_manifest_hashes_entries(self):
        workspace = _workspace("deployment-package")
        root = workspace / "orders"
        custom.project_create(None, str(root), workflow="process-order")
        (root / "parameters.json").write_text('{"alpha": 1}\n', encoding="utf-8")
        out1 = workspace / "orders-1.zip"
        out2 = workspace / "orders-2.zip"
        manifest1 = workspace / "orders-1.manifest.json"
        manifest2 = workspace / "orders-2.manifest.json"

        result1 = custom.deployment_package(None, path=str(root), output_path=str(out1), manifest=str(manifest1))
        result2 = custom.deployment_package(None, path=str(root), output_path=str(out2), manifest=str(manifest2))

        self.assertEqual(_sha256_file(out1), _sha256_file(out2), "same input must produce byte-identical zip archives")
        self.assertEqual(result1["contentHash"], "sha256:" + _sha256_file(out1))
        self.assertEqual(result2["contentHash"], "sha256:" + _sha256_file(out2))
        manifest = json.loads(manifest1.read_text(encoding="utf-8"))
        self.assertTrue(manifest["deterministic"])
        self.assertGreaterEqual(len(manifest["included"]), 3)
        for entry in manifest["included"]:
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(entry["path"])
        self.assertIn({"path": "local.settings.json", "reason": "secret"}, result1["excluded"])
        _assert_no_secret_markers(self, result1)
        _assert_no_secret_markers(self, manifest)

    def test_context_create_and_use_round_trip_through_isolated_store(self):
        workspace = _workspace("context-store")
        fake_home = workspace / "home"
        fake_home.mkdir()
        old_userprofile = os.environ.get("USERPROFILE")
        old_home = os.environ.get("HOME")
        old_config = os.environ.get("AZURE_CONFIG_DIR")
        os.environ["USERPROFILE"] = str(fake_home)
        os.environ["HOME"] = str(fake_home)
        os.environ["AZURE_CONFIG_DIR"] = str(fake_home / ".azure")
        try:
            project = workspace / "orders"
            custom.project_create(None, str(project), workflow="process-order")
            created = custom.context_create(None, name="orders-local", path=str(project), port=7079, use=False)
            self.assertFalse(created["active"])
            self.assertTrue(Path(created["store"]).is_relative_to(fake_home))
            used = custom.context_use(None, name="orders-local")
            self.assertTrue(used["active"])
            self.assertEqual("local", used["target"]["kind"])
            self.assertEqual(str(project.resolve()), used["target"]["path"])
            self.assertEqual(7079, used["target"]["port"])
            persisted = json.loads(Path(_context.store_path()).read_text(encoding="utf-8"))
            self.assertEqual("orders-local", persisted["active"])
        finally:
            if old_config is None:
                os.environ.pop("AZURE_CONFIG_DIR", None)
            else:
                os.environ["AZURE_CONFIG_DIR"] = old_config
            if old_userprofile is None:
                os.environ.pop("USERPROFILE", None)
            else:
                os.environ["USERPROFILE"] = old_userprofile
            if old_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = old_home

    def test_runtime_stop_refuses_pid_creation_time_mismatch_without_killing(self):
        workspace = _workspace("runtime-stop")
        state_dir = workspace / "runtime-state"
        state_dir.mkdir()
        old_state_dir = _local.STATE_DIR
        _local.STATE_DIR = str(state_dir)
        terminate_calls = []
        old_terminate = _local._terminate
        old_is_running = _local._is_running
        old_create_time = _local.process_create_time_utc
        _local._terminate = lambda pid, expected=None: terminate_calls.append(pid)
        _local._is_running = lambda pid: True
        _local.process_create_time_utc = lambda pid: "2026-09-16T16:00:00.0000000Z"
        try:
            record = {
                "pid": 424242,
                "processCreateTimeUtc": "2026-09-16T15:00:00.0000000Z",
                "port": 7788,
                "projectPath": str(workspace),
                "logPath": str(workspace / "runtime.log"),
            }
            (state_dir / "runtime-7788.json").write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(CLIError) as caught:
                custom.runtime_stop(None, port=7788)
            self.assertIn("recorded process identity no longer matches", str(caught.exception))
            self.assertEqual([], terminate_calls, "runtime stop must not kill a mismatched pid")
        finally:
            _local.STATE_DIR = old_state_dir
            _local._terminate = old_terminate
            _local._is_running = old_is_running
            _local.process_create_time_utc = old_create_time

    def test_honesty_invariant_offline_guard_is_observed_to_fail(self):
        unsanitized = "https://example.test/path?sig=real-secret&ok=1 Authorization: Bearer token"
        sanitized = _sanitize_text(unsanitized)
        self.assertNotEqual(unsanitized, sanitized, "sanitizer guard must be observed changing a credential-shaped value")
        _assert_no_secret_markers(self, sanitized)

    def test_core_tools_under_managed_root_is_found_when_absent_from_path(self):
        # A tool installed under the managed dependency root is not on PATH.
        # Searching PATH alone reported it missing even though the CLI knew
        # exactly where it was, so discovery has to look under the root too.
        workspace = _workspace("dependency-managed-root")
        managed = workspace / "FuncCoreTools"
        managed.mkdir()
        executable = managed / ("func.cmd" if os.name == "nt" else "func")
        executable.write_text("", encoding="utf-8")
        if os.name != "nt":
            executable.chmod(0o755)

        empty_path = workspace / "empty-path"
        empty_path.mkdir()

        with mock.patch.dict(os.environ, {"LA_DEPENDENCIES_PATH": str(workspace), "PATH": str(empty_path)}):
            found, source = _local.find_tool("core-tools")
            self.assertEqual(_local.dependencies_root(), str(workspace))

        self.assertIsNotNone(found, "core tools under the managed root must be found when PATH does not contain them")
        self.assertEqual(source, "managed")
        self.assertEqual(Path(found).parent, managed)

    def test_runtime_start_error_names_the_managed_root_it_searched(self):
        workspace = _workspace("runtime-start-missing-core-tools")
        project = workspace / "orders"
        project.mkdir()
        (project / "host.json").write_text("{}", encoding="utf-8")
        empty_root = workspace / "deps"
        empty_root.mkdir()
        empty_path = workspace / "empty-path"
        empty_path.mkdir()

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            free_port = probe.getsockname()[1]

        with mock.patch.dict(os.environ, {"LA_DEPENDENCIES_PATH": str(empty_root), "PATH": str(empty_path)}):
            with self.assertRaises(ValidationError) as caught:
                _local.start_runtime(None, str(project), port=free_port)

        message = str(caught.exception)
        self.assertIn(str(empty_root), message, "the error must name the directory searched, not merely say the tool is missing")
        self.assertIn("dependency install", message, "the error must name a command that actually fixes it")

    def test_runtime_start_foreground_actually_launches_the_host(self):
        # Without --background the command used to return a payload hard-coded
        # to "running" without ever spawning a process, so it reported success
        # and exited 0 while nothing was serving. The test therefore has to
        # observe the launch itself, not just the reported status.
        workspace = _workspace("runtime-start-foreground")
        project = workspace / "orders"
        project.mkdir()
        (project / "host.json").write_text("{}", encoding="utf-8")

        managed = workspace / "FuncCoreTools"
        managed.mkdir()
        executable = managed / ("func.cmd" if os.name == "nt" else "func")
        executable.write_text("", encoding="utf-8")
        if os.name != "nt":
            executable.chmod(0o755)

        empty_path = workspace / "empty-path"
        empty_path.mkdir()

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            free_port = probe.getsockname()[1]

        with mock.patch.dict(os.environ, {"LA_DEPENDENCIES_PATH": str(workspace), "PATH": str(empty_path)}), \
                mock.patch.object(_local, "STATE_DIR", str(workspace / "state")), \
                mock.patch.object(_local.subprocess, "Popen", return_value=_finished_host_process()) as launched:
            result = _local.start_runtime(None, str(project), port=free_port)

        self.assertEqual(launched.call_count, 1, "foreground start must launch the host exactly once")
        argv = launched.call_args.args[0]
        self.assertEqual(Path(argv[0]).parent, managed)
        self.assertEqual(argv[1:], ["host", "start", "--port", str(free_port)])
        self.assertEqual(launched.call_args.kwargs.get("cwd"), str(project))
        self.assertEqual(launched.call_args.kwargs.get("creationflags", 0), 0)
        self.assertNotIn("stdout", launched.call_args.kwargs, "foreground output must stay attached")
        self.assertNotIn("stderr", launched.call_args.kwargs, "foreground output must stay attached")
        self.assertFalse(result["background"])
        self.assertNotEqual(result["status"], "running", "a foreground run that has already exited is not still running")

    def _project(self, label):
        workspace = _workspace(label)
        root = workspace / "app"
        root.mkdir()
        (root / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        (root / "local.settings.json").write_text(json.dumps(_workflow.LOCAL_SETTINGS_JSON), encoding="utf-8")
        return root

    def test_workflow_create_is_additive_and_leaves_project_files_untouched(self):
        # project create refuses to add a second workflow without --force, which
        # rewrites host.json and local.settings.json. Adding a workflow must not
        # put project-level files at risk, so this observes they are byte-identical.
        root = self._project("workflow-create-additive")
        before_host = (root / "host.json").read_bytes()
        before_settings = (root / "local.settings.json").read_bytes()

        result = _workflow.create_workflow_file(str(root), "ReceiveMessage")

        self.assertEqual(result["workflow"], "ReceiveMessage")
        self.assertEqual(result["workflowKind"], "Stateful")
        self.assertTrue((root / "ReceiveMessage" / "workflow.json").is_file())
        self.assertEqual((root / "host.json").read_bytes(), before_host, "host.json must not be touched when adding a workflow")
        self.assertEqual((root / "local.settings.json").read_bytes(), before_settings, "local.settings.json must not be touched when adding a workflow")
        self.assertEqual([item["path"] for item in result["files"]], [str(root / "ReceiveMessage" / "workflow.json")])

    def test_workflow_create_refuses_to_overwrite_without_force(self):
        root = self._project("workflow-create-collision")
        _workflow.create_workflow_file(str(root), "SendMessage")
        with self.assertRaises(ValidationError):
            _workflow.create_workflow_file(str(root), "SendMessage")
        forced = _workflow.create_workflow_file(str(root), "SendMessage", force=True)
        self.assertEqual(forced["files"][0]["action"], "updated")

    def test_workflow_create_requires_an_existing_project(self):
        workspace = _workspace("workflow-create-no-project")
        empty = workspace / "not-a-project"
        empty.mkdir()
        with self.assertRaises(ResourceNotFoundError):
            _workflow.create_workflow_file(str(empty), "SendMessage")

    def test_workflow_create_from_file_accepts_a_connector_definition(self):
        # The whole point of --file is authoring a workflow the fixed template
        # cannot express, such as one driven by a service provider connector.
        root = self._project("workflow-create-from-file")
        definition = {
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "triggers": {
                    "manual": {"type": "Request", "kind": "Http", "inputs": {}}
                },
                "actions": {
                    "Send_message": {
                        "type": "ServiceProvider",
                        "inputs": {
                            "parameters": {"entityName": "orders"},
                            "serviceProviderConfiguration": {
                                "connectionName": "serviceBus",
                                "operationId": "sendMessage",
                                "serviceProviderId": "/serviceProviders/serviceBus"
                            }
                        },
                        "runAfter": {}
                    }
                }
            },
            "kind": "Stateful"
        }
        source = root / "send.json"
        source.write_text(json.dumps(definition), encoding="utf-8")

        result = _workflow.create_workflow_file(str(root), "SendMessage", definition_file=str(source))

        self.assertEqual(result["source"], str(source))
        written = json.loads((root / "SendMessage" / "workflow.json").read_text(encoding="utf-8"))
        action = written["definition"]["actions"]["Send_message"]
        self.assertEqual(action["inputs"]["serviceProviderConfiguration"]["serviceProviderId"], "/serviceProviders/serviceBus")

    def test_workflow_create_rejects_a_definition_with_no_trigger(self):
        root = self._project("workflow-create-bad-file")
        source = root / "bad.json"
        source.write_text(json.dumps({"definition": {"actions": {}}}), encoding="utf-8")
        with self.assertRaises(InvalidArgumentValueError):
            _workflow.create_workflow_file(str(root), "Broken", definition_file=str(source))

    def test_connection_create_rejects_a_secret_passed_as_a_name(self):
        # D135: the value must never reach the command line. A Service Bus
        # connection string carries SharedAccessKey, which the pre-existing
        # context-level check does not look for.
        service_bus = "Endpoint=sb://demo.servicebus.windows.net/;SharedAccessKeyName=Root;SharedAccessKey=abc123="
        with self.assertRaises(InvalidArgumentValueError):
            _connection.reject_secret_shaped_name(service_bus, "--secret")
        # A plain setting name must still be accepted.
        _connection.reject_secret_shaped_name("serviceBus_connectionString", "--secret")

    def test_connection_create_indirects_the_secret_through_an_app_setting(self):
        root = self._project("connection-create")
        secret = "Endpoint=sb://demo.servicebus.windows.net/;SharedAccessKeyName=Root;SharedAccessKey=abc123="

        result = _connection.create_local_connection(
            str(root), "serviceBus", "serviceBus", "serviceBus_connectionString", secret)

        connections = json.loads((root / "connections.json").read_text(encoding="utf-8"))
        entry = connections["serviceProviderConnections"]["serviceBus"]
        self.assertEqual(entry["serviceProvider"]["id"], "/serviceProviders/serviceBus")
        self.assertEqual(entry["parameterValues"]["connectionString"], "@appsetting('serviceBus_connectionString')")
        _assert_no_secret_markers(self, (root / "connections.json").read_text(encoding="utf-8"))

        settings = json.loads((root / "local.settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["Values"]["serviceBus_connectionString"], secret)

        self.assertEqual(result["secretStore"], "local.settings.json")
        _assert_no_secret_markers(self, json.dumps(result))

    def test_connection_create_gitignores_the_file_that_holds_the_secret(self):
        root = self._project("connection-gitignore")
        _connection.create_local_connection(
            str(root), "serviceBus", "serviceBus", "sb_conn", "Endpoint=sb://x/;SharedAccessKey=k=")
        self.assertIn("local.settings.json", (root / ".gitignore").read_text(encoding="utf-8"))

    def test_connection_secret_does_not_reach_the_deployment_package(self):
        # The store chosen for the secret is only safe because deployment package
        # excludes it. That exclusion is the security boundary, so assert it on a
        # real archive rather than trusting the exclusion list.
        root = self._project("connection-package-exclusion")
        secret = "Endpoint=sb://demo.servicebus.windows.net/;SharedAccessKeyName=Root;SharedAccessKey=TOPSECRET123="
        _connection.create_local_connection(str(root), "serviceBus", "serviceBus", "sb_conn", secret)
        archive = root.parent / "app.zip"

        report = _workflow.deterministic_package(str(root), str(archive))

        excluded = {item["path"]: item["reason"] for item in report["excluded"]}
        self.assertEqual(excluded.get("local.settings.json"), "secret")
        with zipfile.ZipFile(str(archive)) as bundle:
            names = bundle.namelist()
            self.assertIn("connections.json", names)
            self.assertNotIn("local.settings.json", names)
            for name in names:
                self.assertNotIn("TOPSECRET123", bundle.read(name).decode("utf-8", errors="ignore"),
                                 "the secret must not appear anywhere in the package")

    def test_connection_create_refuses_to_replace_without_force(self):
        root = self._project("connection-collision")
        secret = "Endpoint=sb://x/;SharedAccessKey=k="
        _connection.create_local_connection(str(root), "serviceBus", "serviceBus", "sb_conn", secret)
        with self.assertRaises(ValidationError):
            _connection.create_local_connection(str(root), "serviceBus", "serviceBus", "sb_conn", secret)
        replaced = _connection.create_local_connection(
            str(root), "serviceBus", "serviceBus", "sb_conn", secret, force=True)
        self.assertTrue(replaced["appSettingReplaced"])

    def test_connection_create_nests_auth_provider_for_an_identity_connection(self):
        # This is the exact shape that was verified against a live runtime, locally
        # as the signed-in user and in Azure as a managed identity. A flat
        # "authProvider" key is accepted by the runtime and then ignored, so the
        # nesting is the whole point of the test.
        root = self._project("connection-identity")

        result = _connection.create_local_connection(
            str(root), "serviceBus", "serviceBus",
            parameter_set="ManagedServiceIdentity",
            parameters=["fullyQualifiedNamespace=@appsetting('serviceBus_fullyQualifiedNamespace')",
                        "authProvider.Type=ManagedServiceIdentity"],
            app_settings=["serviceBus_fullyQualifiedNamespace=contoso.servicebus.windows.net"])

        entry = json.loads((root / "connections.json").read_text(encoding="utf-8"))
        entry = entry["serviceProviderConnections"]["serviceBus"]
        self.assertEqual(entry["parameterSetName"], "ManagedServiceIdentity")
        self.assertEqual(entry["parameterValues"], {
            "fullyQualifiedNamespace": "@appsetting('serviceBus_fullyQualifiedNamespace')",
            "authProvider": {"Type": "ManagedServiceIdentity"},
        })

        settings = json.loads((root / "local.settings.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["Values"]["serviceBus_fullyQualifiedNamespace"],
                         "contoso.servicebus.windows.net")

        # No credential exists anywhere in an identity-based connection.
        self.assertIsNone(result["secretStore"])
        self.assertIsNone(result["appSetting"])
        local_settings_file = [f for f in result["files"] if f["class"] == "localSettings"][0]
        self.assertFalse(local_settings_file["containsSecret"])

    def test_connection_create_keeps_every_repeated_parameter_flag(self):
        # Declaring --parameter with nargs='+' but no action='append' made a
        # repeated flag overwrite the earlier one, so a two-parameter connection
        # was written with one parameter and exit code zero. argparse now yields
        # a list of lists, and every group has to survive into the file.
        root = self._project("connection-repeated-parameter")

        _connection.create_local_connection(
            str(root), "serviceBus", "serviceBus",
            parameter_set="ManagedServiceIdentity",
            parameters=[["fullyQualifiedNamespace=contoso.servicebus.windows.net"],
                        ["authProvider.Type=ManagedServiceIdentity"]],
            app_settings=[["alpha=one"], ["beta=two"]])

        entry = json.loads((root / "connections.json").read_text(encoding="utf-8"))
        entry = entry["serviceProviderConnections"]["serviceBus"]
        self.assertEqual(entry["parameterValues"], {
            "fullyQualifiedNamespace": "contoso.servicebus.windows.net",
            "authProvider": {"Type": "ManagedServiceIdentity"},
        })
        values = json.loads((root / "local.settings.json").read_text(encoding="utf-8"))["Values"]
        self.assertEqual(values["alpha"], "one")
        self.assertEqual(values["beta"], "two")

    def test_connection_create_rejects_a_secret_pasted_into_a_parameter(self):
        # --parameter values sit on the command line, so they must not carry credentials.
        root = self._project("connection-parameter-secret")
        with self.assertRaises(InvalidArgumentValueError):
            _connection.create_local_connection(
                str(root), "serviceBus", "serviceBus",
                parameters=["connectionString=Endpoint=sb://x/;SharedAccessKey=abc123="])

    def test_connection_create_rejects_a_secret_pasted_into_an_app_setting(self):
        root = self._project("connection-appsetting-secret")
        with self.assertRaises(InvalidArgumentValueError):
            _connection.create_local_connection(
                str(root), "serviceBus", "serviceBus",
                parameters=["fullyQualifiedNamespace=@appsetting('x')"],
                app_settings=["x=Endpoint=sb://x/;SharedAccessKey=abc123="])

    def test_connection_create_requires_either_a_secret_or_a_parameter(self):
        root = self._project("connection-empty")
        with self.assertRaises(ValidationError):
            _connection.create_local_connection(str(root), "serviceBus", "serviceBus")

    def test_connection_create_refuses_to_nest_underneath_a_scalar(self):
        root = self._project("connection-bad-nesting")
        with self.assertRaises(ValidationError):
            _connection.create_local_connection(
                str(root), "serviceBus", "serviceBus",
                parameters=["authProvider=ManagedServiceIdentity", "authProvider.Type=X"])

    def test_connection_create_requires_name_equals_value_for_parameters(self):
        root = self._project("connection-bad-pair")
        with self.assertRaises(ValidationError):
            _connection.create_local_connection(
                str(root), "serviceBus", "serviceBus", parameters=["fullyQualifiedNamespace"])


class RunObservationOfflineTests(unittest.TestCase):
    def test_run_list_continuation_token_comes_from_the_platform_next_link(self):
        payload = {"value": [], "nextLink": "https://host/runs?api-version=2019-10-01-edge-preview&%24skiptoken=abc123"}
        self.assertEqual(custom._skiptoken(payload), "abc123")

    def test_run_list_reports_no_continuation_token_on_the_last_page(self):
        self.assertIsNone(custom._skiptoken({"value": []}))

    def test_run_list_status_filter_is_normalized_to_platform_casing(self):
        self.assertEqual(custom._run_status_value("failed"), "Failed")

    def test_run_list_rejects_an_unknown_status(self):
        with self.assertRaises(InvalidArgumentValueError):
            custom._run_status_value("borked")

    def test_paging_size_must_be_a_positive_integer(self):
        self.assertEqual(custom._positive_int("5", "--max-items"), 5)
        for bad in ("0", "-1", "many", None):
            with self.assertRaises(InvalidArgumentValueError):
                custom._positive_int(bad, "--max-items")

    def _action(self):
        return {
            "name": "Send_message",
            "properties": {
                "status": "Failed",
                "code": "BadRequest",
                "error": {"message": "boom"},
                "startTime": "2026-01-01T00:00:00Z",
                "outputsLink": {"uri": "https://blob/outputs?sig=SECRETSIG", "contentSize": 42},
                "inputsLink": {"uri": "https://blob/inputs?sig=SECRETSIG"},
            },
        }

    def test_run_action_redacts_sas_bearing_content_links_by_default(self):
        shaped = custom._run_action_response(self._action(), "wf", "run1", show_content_urls=False)
        self.assertEqual(shaped["action"], "Send_message")
        self.assertEqual(shaped["status"], "Failed")
        self.assertNotIn("SECRETSIG", json.dumps(shaped))
        self.assertEqual(shaped["outputsLink"]["contentSize"], 42)

    def test_run_action_emits_content_links_only_when_asked(self):
        shaped = custom._run_action_response(self._action(), "wf", "run1", show_content_urls=True)
        self.assertIn("SECRETSIG", shaped["outputsLink"]["uri"])

    def test_expression_failure_preserves_provider_reason_without_recorded_outputs(self):
        error = {"code": "InvalidTemplate", "message": "The template language function 'int' cannot convert the value."}
        raw = {"name": "Convert_amount", "properties": {
            "status": "Failed", "code": "BadRequest", "error": error}}
        shaped = custom._run_action_response(raw, "wf", "run1", show_content_urls=False)
        self.assertEqual(shaped["status"], "Failed")
        self.assertEqual(shaped["code"], "BadRequest")
        self.assertEqual(shaped["error"], error)
        self.assertIsNone(shaped["outputsLink"])

    def test_action_list_keeps_http_failure_and_skipped_dependency_distinct(self):
        failed = self._action()
        failed["properties"]["error"] = None
        skipped = {"name": "After_success", "properties": {"status": "Skipped", "code": "ActionSkipped"}}
        client = mock.Mock()
        client.list.return_value = {"value": [failed, skipped], "nextContinuationToken": None}
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {"kind": "local"})):
            result = custom.run_action_list(None, "wf", "run1")
        self.assertEqual([item["status"] for item in result["value"]], ["Failed", "Skipped"])
        self.assertIsNone(result["value"][0]["error"])
        self.assertEqual(result["value"][1]["code"], "ActionSkipped")
        self.assertNotIn("SECRETSIG", json.dumps(result))

    def test_run_list_item_hoists_the_trigger_name(self):
        raw = {"name": "run1", "properties": {"status": "Succeeded", "trigger": {"name": "manual"}}}
        shaped = custom._run_list_item(raw, "wf")
        self.assertEqual(shaped["runId"], "run1")
        self.assertEqual(shaped["triggerName"], "manual")


class _StubClient:
    def __init__(self, action_payload, body=b""):
        self.action_payload = action_payload
        self.body = body
        self.requested_max_bytes = "unset"

    def get(self, _path, params=None):
        return self.action_payload

    def get_raw_url(self, _url, max_bytes=None):
        self.requested_max_bytes = max_bytes
        return {"content": self.body}


class ShowContentOfflineTests(unittest.TestCase):
    BODY = b'{"uri":"http://example/never","method":"GET"}'

    def _invoke(self, client, **kwargs):
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {"kind": "local"})):
            return custom.run_action_show_content(
                None, "wf", "run1", "Call_nowhere", **kwargs)

    def _payload(self, links):
        return {"name": "Call_nowhere", "properties": links}

    def test_full_read_parses_json_and_reports_no_truncation(self):
        client = _StubClient(self._payload({"outputsLink": {"uri": "https://blob/x?sig=S", "contentSize": len(self.BODY)}}), self.BODY)
        result = self._invoke(client)
        self.assertEqual(result["body"]["method"], "GET")
        self.assertFalse(result["truncated"])

    def test_failed_http_response_reason_is_available_without_metadata_error(self):
        body = {"statusCode": 400, "body": {"error": {
            "code": "DiagnosticDemoRejected", "message": "Diagnostic demo: amount must be positive."}}}
        encoded = json.dumps(body).encode("utf-8")
        client = _StubClient(self._payload({
            "status": "Failed", "code": "BadRequest", "error": None,
            "outputsLink": {"uri": "https://blob/x?sig=S", "contentSize": len(encoded)}}), encoded)
        result = self._invoke(client, max_bytes=4096)
        self.assertEqual(result["body"], body)
        self.assertFalse(result["truncated"])
        self.assertEqual(client.requested_max_bytes, 4096)

    def test_max_bytes_is_enforced_even_when_the_runtime_ignores_the_range_header(self):
        client = _StubClient(self._payload({"outputsLink": {"uri": "https://blob/x?sig=S", "contentSize": len(self.BODY)}}), self.BODY)
        result = self._invoke(client, max_bytes=10)
        self.assertEqual(client.requested_max_bytes, 10)
        self.assertEqual(result["body"], self.BODY[:10].decode("utf-8"))
        self.assertTrue(result["truncated"])

    def test_a_short_read_is_reported_as_truncated(self):
        client = _StubClient(self._payload({"outputsLink": {"uri": "https://blob/x?sig=S", "contentSize": 999}}), self.BODY)
        result = self._invoke(client)
        self.assertTrue(result["truncated"])

    def test_missing_content_link_points_at_the_command_that_has_the_error(self):
        client = _StubClient(self._payload({"outputsLink": None}))
        with self.assertRaises(ValidationError) as ctx:
            self._invoke(client)
        self.assertIn("az logicapp run action show", str(ctx.exception))

    def test_show_content_never_echoes_the_sas_uri(self):
        client = _StubClient(self._payload({"outputsLink": {"uri": "https://blob/x?sig=SECRETSIG", "contentSize": len(self.BODY)}}), self.BODY)
        self.assertNotIn("SECRETSIG", json.dumps(self._invoke(client)))

    def test_an_unsupplied_content_default_echoes_as_a_plain_string(self):
        """azure-cli passes a str subclass for a default the user did not type.

        It carries metadata and serializes as {"isDefault": true}, so echoing it
        straight back reports the requested content as an object.
        """
        class _DefaultStr(str):
            def __init__(self, *_args):
                self.isDefault = True

        client = _StubClient(self._payload({"outputsLink": {"uri": "https://blob/x?sig=S", "contentSize": len(self.BODY)}}), self.BODY)
        result = self._invoke(client, content=_DefaultStr("outputs"))
        self.assertEqual(result["content"], "outputs")
        self.assertIs(type(result["content"]), str)


class IdentityOfflineTests(unittest.TestCase):
    UA = "/subscriptions/0000/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mi"

    def test_missing_identity_reads_as_an_answer_not_an_omission(self):
        self.assertEqual(_identity.normalize_identity(None)["type"], "None")

    def test_assign_system_assigned(self):
        body = _identity.plan_assign({"type": "None"}, system_assigned=True)
        self.assertEqual(body, {"type": "SystemAssigned"})

    def test_assign_user_assigned_keeps_the_existing_system_assigned_identity(self):
        current = {"type": "SystemAssigned", "userAssignedIdentities": {}}
        body = _identity.plan_assign(current, user_assigned=[self.UA])
        self.assertEqual(body["type"], "SystemAssigned, UserAssigned")
        self.assertEqual(body["userAssignedIdentities"], {self.UA: {}})

    def test_assign_keeps_every_repeated_user_assigned_flag(self):
        # Same defect class as --parameter: without action='append' a repeated
        # --user-assigned dropped the earlier identity and still reported
        # success, so an app came back with fewer identities than requested.
        second = self.UA + "-2"
        body = _identity.plan_assign({"type": "None"}, user_assigned=[[self.UA], [second]])
        self.assertEqual(body["type"], "UserAssigned")
        self.assertEqual(set(body["userAssignedIdentities"]), {self.UA, second})

    def test_assign_requires_something_to_assign(self):
        with self.assertRaises(RequiredArgumentMissingError):
            _identity.plan_assign({"type": "None"})

    def test_assign_rejects_a_bare_identity_name(self):
        with self.assertRaises(ValidationError):
            _identity.plan_assign({"type": "None"}, user_assigned=["orders-identity"])

    def test_remove_system_assigned_leaves_user_assigned_in_place(self):
        current = {"type": "SystemAssigned, UserAssigned", "userAssignedIdentities": {self.UA: {}}}
        body = _identity.plan_remove(current, system_assigned=True)
        self.assertEqual(body["type"], "UserAssigned")
        self.assertNotIn("userAssignedIdentities", body)

    def test_removing_the_last_user_assigned_identity_drops_the_map(self):
        current = {"type": "UserAssigned", "userAssignedIdentities": {self.UA: {}}}
        body = _identity.plan_remove(current, user_assigned=[self.UA])
        self.assertEqual(body["type"], "None")
        # ARM rejects an identity map when the resulting type is not UserAssigned.
        self.assertNotIn("userAssignedIdentities", body)

    def test_removing_one_of_several_user_assigned_identities_sends_an_explicit_null(self):
        other = self.UA + "-2"
        current = {"type": "UserAssigned", "userAssignedIdentities": {self.UA: {}, other: {}}}
        body = _identity.plan_remove(current, user_assigned=[self.UA])
        self.assertEqual(body["type"], "UserAssigned")
        self.assertIsNone(body["userAssignedIdentities"][self.UA])
        self.assertEqual(body["userAssignedIdentities"][other], {})

    def test_removing_an_unassigned_identity_is_an_error_not_a_silent_no_op(self):
        with self.assertRaises(ValidationError):
            _identity.plan_remove({"type": "SystemAssigned"}, user_assigned=[self.UA])


class DependencyInstallOfflineTests(unittest.TestCase):
    """Cover the install/uninstall behaviours that are policy, not plumbing."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="dep-offline-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_check_and_install_agree_on_what_is_installable(self):
        # These were two hand-maintained lists. Making azurite installable updated one
        # of them, and 'dependency check' went on reporting installableByCli false for
        # a kind 'dependency install' would happily install.
        for kind in _local.DEPENDENCY_KINDS:
            row = _local._detect(kind)
            expected = kind in _dependencies.INSTALLABLE_KINDS
            self.assertEqual(expected, row["installableByCli"],
                             "{} disagrees between check and install".format(kind))
        self.assertIs(_local.INSTALLABLE_KINDS, _dependencies.INSTALLABLE_KINDS,
                      "a second copy of the installable set has been introduced")

    def test_dotnet_is_refused_with_guidance_not_a_bare_error(self):
        with self.assertRaises(InvalidArgumentValueError) as caught:
            custom._install_kinds(["dotnet"])
        self.assertIn("dotnet-install", str(caught.exception))

    def test_azurite_is_installable_and_ordered_after_node(self):
        # Azurite was refused on a VS Code-parity rationale, but a CLI user has no
        # Azurite extension to fall back on, so a local run needing the emulator had
        # nowhere to go. It is installed with npm, which ships with Node.js, so
        # installing every kind has to reach Node.js first.
        kinds = custom._install_kinds(["azurite"])
        self.assertEqual(kinds, ["azurite"])
        defaults = custom._install_kinds(None)
        self.assertIn("azurite", defaults)
        self.assertLess(defaults.index("node"), defaults.index("azurite"))

    def test_refused_kinds_are_not_silently_included_in_the_default_set(self):
        self.assertEqual(custom._install_kinds(None), list(_dependencies.INSTALLABLE_KINDS))
        self.assertNotIn("dotnet", custom._install_kinds(None))

    def test_repeated_kinds_collapse_but_keep_order(self):
        self.assertEqual(custom._install_kinds(["node", "core-tools", "node"]), ["node", "core-tools"])

    def test_node_uses_darwin_while_core_tools_uses_osx_on_mac(self):
        with mock.patch("azext_logicapp._dependencies.platform.system", return_value="Darwin"):
            self.assertEqual(_dependencies._os_tag("node"), "darwin")
            self.assertEqual(_dependencies._os_tag("core-tools"), "osx")

    def test_unsupported_architecture_is_refused(self):
        with mock.patch("azext_logicapp._dependencies.platform.machine", return_value="mips"):
            with self.assertRaises(ValidationError):
                _dependencies._arch_tag()

    def test_download_urls_match_each_publisher_layout(self):
        with mock.patch("azext_logicapp._dependencies.platform.system", return_value="Windows"), \
                mock.patch("azext_logicapp._dependencies.platform.machine", return_value="AMD64"):
            self.assertEqual(
                _dependencies.build_download_url("core-tools", "4.14.0"),
                "https://github.com/Azure/azure-functions-core-tools/releases/download/4.14.0/"
                "Azure.Functions.Cli.win-x64.4.14.0.zip")
            self.assertEqual(
                _dependencies.build_download_url("node", "24.15.0"),
                "https://nodejs.org/dist/v24.15.0/node-v24.15.0-win-x64.zip")

    def test_node_archive_is_a_tarball_off_windows(self):
        with mock.patch("azext_logicapp._dependencies.platform.system", return_value="Linux"), \
                mock.patch("azext_logicapp._dependencies.platform.machine", return_value="x86_64"):
            self.assertTrue(_dependencies.build_download_url("node", "24.15.0").endswith("-linux-x64.tar.gz"))

    def test_zip_entries_escaping_the_target_are_refused(self):
        archive = self.root / "evil.zip"
        with zipfile.ZipFile(archive, "w") as handle:
            handle.writestr("../escaped.txt", "nope")
        target = self.root / "out"
        target.mkdir()
        with self.assertRaises(CLIError):
            _dependencies._safe_extract(str(archive), str(target))
        self.assertFalse((self.root / "escaped.txt").exists())

    def test_a_single_container_folder_is_flattened(self):
        target = self.root / "stage"
        (target / "node-v24.15.0-win-x64").mkdir(parents=True)
        (target / "node-v24.15.0-win-x64" / "node.exe").write_text("bin", encoding="utf-8")
        _dependencies._flatten_container(str(target))
        self.assertTrue((target / "node.exe").is_file())
        self.assertFalse((target / "node-v24.15.0-win-x64").exists())

    def test_two_top_level_entries_are_left_alone(self):
        target = self.root / "stage2"
        target.mkdir()
        (target / "func.exe").write_text("a", encoding="utf-8")
        (target / "lib").mkdir()
        _dependencies._flatten_container(str(target))
        self.assertTrue((target / "func.exe").is_file())

    def test_manifest_records_files_and_detects_tampering(self):
        target = self.root / "FuncCoreTools"
        target.mkdir()
        (target / "func.exe").write_text("hello", encoding="utf-8")
        _dependencies.write_manifest(str(target), "core-tools", "4.14.0", "https://example/archive.zip")
        self.assertTrue(_dependencies.verify_manifest(str(target))["intact"])
        (target / "func.exe").write_text("hello-but-longer", encoding="utf-8")
        state = _dependencies.verify_manifest(str(target))
        self.assertFalse(state["intact"])
        self.assertEqual(state["problems"][0]["issue"], "size-mismatch")

    def test_the_manifest_never_lists_itself(self):
        target = self.root / "FuncCoreTools2"
        target.mkdir()
        (target / "func.exe").write_text("hello", encoding="utf-8")
        manifest = _dependencies.write_manifest(str(target), "core-tools", "4.14.0", "https://example/a.zip")
        self.assertEqual([entry["path"] for entry in manifest["files"]], ["func.exe"])

    def test_install_does_not_take_over_a_folder_it_did_not_create(self):
        target = self.root / "FuncCoreTools"
        target.mkdir()
        (target / "func.exe").write_text("someone else's", encoding="utf-8")
        result = _dependencies.install_dependency(
            "core-tools", version="4.14.0", root=str(self.root), source_url="https://example/a.zip")
        self.assertEqual(result["state"], "already-present-not-cli-managed")
        self.assertEqual((target / "func.exe").read_text(encoding="utf-8"), "someone else's")
        self.assertFalse((target / _dependencies.MANIFEST_NAME).exists())

    def test_uninstall_leaves_a_folder_this_cli_did_not_create(self):
        target = self.root / "NodeJs"
        target.mkdir()
        (target / "node.exe").write_text("hand-installed", encoding="utf-8")
        result = _dependencies.uninstall_dependency("node", root=str(self.root))
        self.assertEqual(result["state"], "not-cli-managed")
        self.assertTrue((target / "node.exe").is_file())

    def test_uninstall_ignores_a_manifest_written_by_something_else(self):
        target = self.root / "NodeJs"
        target.mkdir()
        (target / "node.exe").write_text("vscode", encoding="utf-8")
        with open(_dependencies.manifest_path(str(target)), "w", encoding="utf-8") as handle:
            json.dump({"dependencyName": "node", "installedBy": "vscode", "files": []}, handle)
        result = _dependencies.uninstall_dependency("node", root=str(self.root))
        self.assertEqual(result["state"], "not-cli-managed")
        self.assertTrue((target / "node.exe").is_file())

    def test_uninstall_removes_what_this_cli_recorded(self):
        target = self.root / "NodeJs"
        target.mkdir()
        (target / "node.exe").write_text("ours", encoding="utf-8")
        _dependencies.write_manifest(str(target), "node", "24.15.0", "https://example/node.zip")
        result = _dependencies.uninstall_dependency("node", root=str(self.root))
        self.assertEqual(result["state"], "removed")
        self.assertFalse(target.exists())

    def test_an_unreachable_checksum_downgrades_to_no_verification(self):
        with mock.patch("azext_logicapp._dependencies.requests.get", side_effect=requests.RequestException("down")):
            self.assertIsNone(_dependencies.expected_sha256("node", "https://nodejs.org/dist/v1/node-v1-win-x64.zip"))

    def test_version_falls_back_to_the_pin_when_the_feed_is_unreachable(self):
        with mock.patch("azext_logicapp._dependencies._get_json", side_effect=requests.RequestException("down")):
            version, source = _dependencies.resolve_version("core-tools")
            self.assertEqual(version, _dependencies.PINNED_VERSIONS["core-tools"])
            self.assertEqual(source, "pinned-fallback")

    def test_an_explicit_version_is_never_overridden_by_the_feed(self):
        with mock.patch("azext_logicapp._dependencies._get_json") as feed:
            self.assertEqual(_dependencies.resolve_version("node", version="20.0.0"), ("20.0.0", "explicit"))
            feed.assert_not_called()

    def test_bundle_version_failure_is_an_error_because_there_is_no_safe_pin(self):
        with mock.patch("azext_logicapp._dependencies._get_json", side_effect=requests.RequestException("down")):
            with self.assertRaises(CLIError):
                _dependencies.resolve_version("bundle")


class DependencySharedFolderTests(unittest.TestCase):
    """The shared dependency root only pays off if our folder names match VS Code's."""

    def test_managed_subdirs_match_the_vs_code_extension(self):
        self.assertEqual(_local.managed_subdir("core-tools"), "FuncCoreTools")
        self.assertEqual(_local.managed_subdir("node"), "NodeJs")
        self.assertEqual(_local.managed_subdir("dotnet"), "DotNetSDK")

    def test_dependency_root_honours_the_environment_override(self):
        override = tempfile.mkdtemp(prefix="dep-root-")
        self.addCleanup(shutil.rmtree, override, True)
        with mock.patch.dict(os.environ, {"LA_DEPENDENCIES_PATH": override}):
            report = _local.dependency_report(kind=["core-tools"])
            self.assertEqual(report["root"], _local.dependencies_root())
            self.assertEqual(report["root"], override)

    def test_managed_connector_list_pages_and_filters_without_network(self):
        calls = []

        def sender(_ctx, method, url, **_kwargs):
            calls.append((method, url))
            return _FakeResponse({"value": [
                {"name": "office365", "properties": {"displayName": "Office 365 Outlook"}},
                {"name": "azureblob", "properties": {"displayName": "Azure Blob"}},
            ]})

        result = _managed_api.connector_managed_list(
            _FakeCmd(), "eastus", subscription="sub1", search="office", max_items=1, sender=sender)

        self.assertEqual("office365", result["value"][0]["name"])
        self.assertIsNone(result["nextContinuationToken"])
        self.assertEqual("GET", calls[0][0])
        self.assertIn("/subscriptions/sub1/providers/Microsoft.Web/locations/eastus/managedApis", calls[0][1])

    def test_managed_connector_operation_show_uses_direct_route(self):
        urls = []

        def sender(_ctx, _method, url, **_kwargs):
            urls.append(url)
            return _FakeResponse({"name": "SendEmailV2", "properties": {"summary": "Send mail"}})

        result = _managed_api.connector_managed_operation_show(
            _FakeCmd(), "office365", "SendEmailV2", location="eastus", subscription="sub1", sender=sender)

        self.assertEqual("SendEmailV2", result["name"])
        self.assertEqual("SendEmailV2", result["operation"])
        self.assertIn("/managedApis/office365/apiOperations/SendEmailV2?api-version=2018-07-01-preview", urls[0])

    def test_connection_list_redacts_parameter_values_and_runtime_urls(self):
        payload = {"managedApiConnections": {"office": {
            "displayName": "Office",
            "parameterValues": {"token": "SharedAccessKey=secret"},
            "connectionRuntimeUrl": "https://example.test/runtime?sig=secret",
            "api": {"id": "/apis/office365"},
            "connection": {"id": "/connections/office"},
        }}}

        result = _connection.connection_list(_FakeCmd(), "rg", "app", client=_FakeVfsClient(payload))

        item = result["value"][0]
        self.assertEqual("managedApiConnections", item["class"])
        self.assertEqual("<redacted-by-az-logicapp-cli>", item["parameterValues"]["token"])
        self.assertEqual("<redacted-by-az-logicapp-cli>", item["connectionRuntimeUrl"])
        self.assertEqual("/apis/office365", _connection.connection_list_table_format(result)[0]["ProviderId"])
        _assert_no_secret_markers(self, result)

    def test_connection_table_transformers_are_registered_and_format_corrected_columns(self):
        loader = _FakeCommandLoader()
        commands.load_command_table(loader, None)
        list_transformer = loader.commands[("logicapp connection", "list")]["table_transformer"]
        show_transformer = loader.commands[("logicapp connection", "show")]["table_transformer"]

        self.assertTrue(callable(list_transformer))
        self.assertTrue(callable(show_transformer))

        payload = {
            "serviceProviderConnections": {
                "blob": {
                    "displayName": "Blob",
                    "parameterValues": {"connectionString": "AccountKey=secret"},
                    "serviceProvider": {"id": "/serviceProviders/AzureBlob"},
                },
            },
            "managedApiConnections": {
                "office": {
                    "displayName": "Office",
                    "parameterValues": {"token": "SharedAccessKey=secret"},
                    "api": {"id": "/managedApis/office365"},
                    "connection": {"id": "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/office"},
                },
            },
        }

        result = _connection.connection_list(_FakeCmd(), "rg", "app", client=_FakeVfsClient(payload))
        rows = list_transformer(result)

        self.assertEqual([
            {
                "Name": "blob",
                "Class": "serviceProviderConnections",
                "DisplayName": "Blob",
                "ProviderId": "/serviceProviders/AzureBlob",
                "ConnectionId": None,
            },
            {
                "Name": "office",
                "Class": "managedApiConnections",
                "DisplayName": "Office",
                "ProviderId": "/managedApis/office365",
                "ConnectionId": "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/office",
            },
        ], rows)

        show_result = _connection.connection_show(
            _FakeCmd(), "rg", "app", "office", client=_FakeVfsClient(payload))
        self.assertEqual([rows[1]], show_transformer(show_result))
        _assert_no_secret_markers(self, rows)
        _assert_no_secret_markers(self, show_transformer(show_result))

    def test_connection_show_requires_class_for_ambiguous_names(self):
        payload = {
            "serviceProviderConnections": {"shared": {"serviceProvider": {"id": "/serviceProviders/sql"}}},
            "managedApiConnections": {"shared": {"api": {"id": "/apis/sql"}}},
        }

        with self.assertRaises(ValidationError) as caught:
            _connection.connection_show(_FakeCmd(), "rg", "app", "shared", client=_FakeVfsClient(payload))

        self.assertIn("exists in multiple classes", str(caught.exception))

    def test_connection_test_no_test_available_exits_3_and_says_not_verified(self):
        arm_id = "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/no-test"

        def sender(_ctx, _method, _url, **_kwargs):
            return _FakeResponse({"id": arm_id, "name": "no-test", "properties": {}})

        result = _connection.connection_test(
            _FakeCmd(), "rg", "app", arm_id, sender=sender, exit_on_nonzero=False)

        self.assertEqual("noTestAvailable", result["outcome"])
        self.assertEqual("none", result["testPath"])
        self.assertIn("not verified", result["message"])
        with self.assertRaises(ResourceNotFoundError):
            _connection.connection_test(_FakeCmd(), "rg", "app", arm_id, sender=sender)

    def test_connection_test_unknown_bare_name_fails_from_connections_json_without_arm_lookup(self):
        calls = []
        cmd = mock.Mock()
        cmd.cli_ctx.data = {"subscription_id": "sub1"}

        def sender(_ctx, method, url, **_kwargs):
            calls.append((method, url))
            raise AssertionError("bare connection names must not fall through to ARM lookup")

        with self.assertRaises(ResourceNotFoundError) as caught:
            _connection.connection_test(
                cmd, "rg", "app", "doesNotExist123",
                vfs_client=_FakeVfsClient({"managedApiConnections": {}}), sender=sender)

        self.assertEqual("Connection 'doesNotExist123' was not found in connections.json.", str(caught.exception))
        self.assertEqual([], calls)

    def test_connection_test_2xx_passes_without_error(self):
        arm_id = "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/passes"

        def sender(_ctx, _method, url, **_kwargs):
            if url.startswith(arm_id):
                return _FakeResponse({"id": arm_id, "name": "passes", "properties": {
                    "testLinks": [{"method": "GET", "requestUri": "https://example.test/test"}],
                }})
            return _FakeResponse({}, status_code=204)

        result = _connection.connection_test(_FakeCmd(), "rg", "app", arm_id, sender=sender)

        self.assertEqual("passed", result["outcome"])
        self.assertEqual(204, result["httpStatus"])
        self.assertEqual("managedArmTestLink", result["testPath"])

    def test_connection_test_401_is_authorization_failed_and_still_exits_1(self):
        # 401/403 means the platform answered and refused the *test* operation, which
        # is a different fact from an unusable connection: a connector's generic test
        # routinely needs broader rights than the operations a workflow calls. It is
        # still not a pass, so it must still exit non-zero.
        arm_id = "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/unauthorized"

        def sender(_ctx, _method, url, **_kwargs):
            if url.startswith(arm_id):
                return _FakeResponse({"id": arm_id, "name": "unauthorized", "properties": {
                    "testLinks": [{"method": "GET", "requestUri": "https://example.test/test"}],
                }})
            return _FakeResponse({}, status_code=401)

        result = _connection.connection_test(
            _FakeCmd(), "rg", "app", arm_id, sender=sender, exit_on_nonzero=False)

        self.assertEqual("authorizationFailed", result["outcome"])
        self.assertEqual(401, result["httpStatus"])
        self.assertEqual("managedArmTestLink", result["testPath"])
        self.assertIn("may still work", result["message"])
        with self.assertRaises(CLIError):
            _connection.connection_test(_FakeCmd(), "rg", "app", arm_id, sender=sender)

    def test_connection_test_404_is_still_plain_failed(self):
        # Only 401/403 are reclassified; other 4xx must not be softened into an
        # authorization story they have no evidence for.
        arm_id = "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/missing"

        def sender(_ctx, _method, url, **_kwargs):
            if url.startswith(arm_id):
                return _FakeResponse({"id": arm_id, "name": "missing", "properties": {
                    "testLinks": [{"method": "GET", "requestUri": "https://example.test/test"}],
                }})
            return _FakeResponse({}, status_code=404)

        result = _connection.connection_test(
            _FakeCmd(), "rg", "app", arm_id, sender=sender, exit_on_nonzero=False)

        self.assertEqual("failed", result["outcome"])
        self.assertEqual(404, result["httpStatus"])

    def test_connection_test_5xx_is_failed_not_passed(self):
        arm_id = "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/fails"

        def sender(_ctx, _method, url, **_kwargs):
            if url.startswith(arm_id):
                return _FakeResponse({"id": arm_id, "name": "fails", "properties": {
                    "testLinks": [{"method": "GET", "requestUri": "https://example.test/test"}],
                }})
            return _FakeResponse({}, status_code=500)

        result = _connection.connection_test(
            _FakeCmd(), "rg", "app", arm_id, sender=sender, exit_on_nonzero=False)

        self.assertEqual("failed", result["outcome"])
        self.assertEqual(500, result["httpStatus"])
        self.assertEqual("managedArmTestLink", result["testPath"])
        with self.assertRaises(CLIError):
            _connection.connection_test(_FakeCmd(), "rg", "app", arm_id, sender=sender)

    def test_connection_test_429_is_could_not_reach_with_retry_after(self):
        arm_id = "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/throttle"

        def sender(_ctx, _method, url, **_kwargs):
            if url.startswith(arm_id):
                return _FakeResponse({"id": arm_id, "name": "throttle", "properties": {
                    "testLinks": [{"method": "GET", "requestUri": "https://example.test/test"}],
                }})
            return _FakeResponse({}, status_code=429, headers={"Retry-After": "30"})

        result = _connection.connection_test(
            _FakeCmd(), "rg", "app", arm_id, sender=sender, exit_on_nonzero=False)

        self.assertEqual("couldNotReach", result["outcome"])
        self.assertEqual(429, result["httpStatus"])
        self.assertEqual("30", result["retryAfter"])
        self.assertIn("throttled", result["message"])
        with self.assertRaises(CLIError):
            _connection.connection_test(_FakeCmd(), "rg", "app", arm_id, sender=sender)

    def test_connection_test_service_provider_without_test_url_is_no_test_available(self):
        payload = {"serviceProviderConnections": {"files": {
            "serviceProvider": {"id": "/serviceProviders/FileSystem"},
        }}}
        runtime_payload = {"value": [{"id": "/serviceProviders/FileSystem", "properties": {}}]}

        result = _connection.connection_test(
            _FakeCmd(), "rg", "app", "files", vfs_client=_FakeVfsClient(payload),
            runtime_client=_FakeRuntimeClient(runtime_payload), exit_on_nonzero=False)

        self.assertEqual("noTestAvailable", result["outcome"])
        self.assertEqual("serviceProviderConnections", result["connection"]["class"])
        self.assertIn("not verified", result["message"])
        with self.assertRaises(ResourceNotFoundError):
            _connection.connection_test(
                _FakeCmd(), "rg", "app", "files", vfs_client=_FakeVfsClient(payload),
                runtime_client=_FakeRuntimeClient(runtime_payload))


class ContractConsistencyTests(unittest.TestCase):
    """Guards for three defects that unit tests could not see before.

    Each was found by driving the real CLI, not the helpers: the helpers were
    individually correct, and the defect only existed in how two of them
    disagreed with each other.
    """

    def test_app_setting_reference_survives_redaction(self):
        # An @appsetting(...) value names a setting; it does not carry its value.
        # Redacting it left no way to see which setting a broken connection wanted.
        redacted = _connection._redact_parameter_values({
            "fullyQualifiedNamespace": "@appsetting('sb_namespace')",
            "interpolated": "@{appsetting('other_setting')}",
        })
        self.assertEqual("@appsetting('sb_namespace')", redacted["fullyQualifiedNamespace"])
        self.assertEqual("@{appsetting('other_setting')}", redacted["interpolated"])

    def test_real_secrets_are_still_redacted(self):
        redacted = _connection._redact_parameter_values({
            "connectionString": "DefaultEndpointsProtocol=https;AccountKey=abc123==",
            "plain": "contoso.servicebus.windows.net",
            "nested": {"key": "s3cret"},
            "listed": ["s3cret"],
        })
        sentinel = _connection.LOGICAPP_REDACTION_SENTINEL
        self.assertEqual(sentinel, redacted["connectionString"])
        self.assertEqual(sentinel, redacted["plain"])
        self.assertEqual(sentinel, redacted["nested"]["key"])
        self.assertEqual([sentinel], redacted["listed"])

    def test_value_merely_containing_a_reference_stays_redacted(self):
        # Anchored match only: a value that wraps a reference may also carry a
        # literal secret, so it must not be treated as a bare pointer.
        redacted = _connection._redact_parameter_values({
            "mixed": "Endpoint=@appsetting('ns');SharedAccessKey=abc123==",
        })
        self.assertEqual(_connection.LOGICAPP_REDACTION_SENTINEL, redacted["mixed"])

    def test_runtime_start_and_show_agree_on_field_names(self):
        # A script that starts the runtime then polls it used to read nothing,
        # because start emitted status/readiness.listening while show emitted
        # state/listening for the very same concepts.
        with mock.patch.object(_local, "_port_free", return_value=False), \
                mock.patch.object(_local, "probe_management_endpoint", return_value=(True, None)), \
                mock.patch.object(_local, "_read_record", return_value=None):
            started = _local._start_payload(
                "running", "/proj", 7099, True, 123, "t", "/rec", "/log", None)
            shown = _local.show_runtime(7099)

        for field in ("state", "status", "listening", "managementEndpoint"):
            self.assertIn(field, started, "runtime start lost '{}'".format(field))
            self.assertIn(field, shown, "runtime show lost '{}'".format(field))
            self.assertEqual(
                started[field], shown[field],
                "runtime start and show disagree on '{}'".format(field))

        for field in ("listening", "managementEndpointReachable", "managementEndpoint",
                      "lastProbeError"):
            self.assertIn(field, started["readiness"])
            self.assertIn(field, shown["readiness"])

    def test_runtime_show_distinguishes_bound_port_from_ready_host(self):
        # 'managementEndpointReachable' used to be an alias for "something is bound
        # to the port", so a host that had bound but was not yet serving -- or an
        # unrelated process squatting the port -- reported ready.
        with mock.patch.object(_local, "_port_free", return_value=False), \
                mock.patch.object(_local, "probe_management_endpoint",
                                  return_value=(False, "connection refused")), \
                mock.patch.object(_local, "_read_record", return_value=None):
            shown = _local.show_runtime(7099)

        self.assertTrue(shown["listening"])
        self.assertFalse(shown["readiness"]["managementEndpointReachable"])
        self.assertEqual("connection refused", shown["readiness"]["lastProbeError"])
        self.assertEqual("starting", shown["state"])

    def test_identity_translates_arm_404_to_resource_not_found(self):
        # 'identity show' reported a missing site as exit 3 because
        # custom_show_command maps it; 'assign' and 'remove' exited 1 on the
        # byte-identical ARM 404, so a caller could not detect "no such app".
        from azure.cli.core.azclierror import HTTPError

        def _sender(*_args, **_kwargs):
            raise HTTPError("Not Found", _FakeResponse(status_code=404))

        with self.assertRaises(ResourceNotFoundError):
            _identity._send(_FakeCmd(), "GET", "/subscriptions/s/sites/missing", sender=_sender)

    def test_identity_does_not_swallow_other_http_errors(self):
        from azure.cli.core.azclierror import HTTPError

        def _sender(*_args, **_kwargs):
            raise HTTPError("Forbidden", _FakeResponse(status_code=403))

        with self.assertRaises(HTTPError):
            _identity._send(_FakeCmd(), "GET", "/subscriptions/s/sites/app", sender=_sender)


class ManagedConnectionTests(unittest.TestCase):
    """Offline coverage for managed API connections and their access policies."""

    def test_connection_body_always_requests_v2(self):
        body = _managed_connection.build_connection_body(
            "eastus", "/subscriptions/s/providers/Microsoft.Web/locations/eastus/managedApis/azureblob",
            "blobProd", {}, "managedIdentityAuth")
        # V1 connections silently reject every access policy write and the kind
        # cannot be corrected afterwards, so this must never become conditional.
        self.assertEqual(body["kind"], "V2")
        self.assertEqual(body["properties"]["parameterValueSet"]["name"], "managedIdentityAuth")

    def test_parameters_become_value_entries_inside_a_parameter_set(self):
        body = _managed_connection.build_connection_body(
            "eastus", "/managedApis/azureblob", "n", {"accountName": "contoso"}, "keyBasedAuth")
        self.assertEqual(
            body["properties"]["parameterValueSet"]["values"], {"accountName": {"value": "contoso"}})

    def test_parameters_without_a_set_use_parameter_values(self):
        body = _managed_connection.build_connection_body(
            "eastus", "/managedApis/azureblob", "n", {"accountName": "contoso"}, None)
        self.assertEqual(body["properties"]["parameterValues"], {"accountName": "contoso"})
        self.assertNotIn("parameterValueSet", body["properties"])

    def test_access_policy_body_shape(self):
        body = _managed_connection.build_access_policy_body("eastus", "tenant-1", "object-1")
        principal = body["properties"]["principal"]
        self.assertEqual(principal["type"], "ActiveDirectory")
        self.assertEqual(principal["identity"], {"tenantId": "tenant-1", "objectId": "object-1"})
        self.assertEqual(body["location"], "eastus")

    def test_connections_entry_uses_system_identity_by_default(self):
        entry = _managed_connection.build_connections_entry("/api", "/conn", "https://runtime")
        self.assertEqual(entry["authentication"], {"type": "ManagedServiceIdentity"})
        self.assertEqual(entry["connectionRuntimeUrl"], "https://runtime")

    def test_connections_entry_names_a_user_assigned_identity(self):
        entry = _managed_connection.build_connections_entry("/api", "/conn", None, "/subscriptions/s/uami")
        self.assertEqual(
            entry["authentication"], {"type": "ManagedServiceIdentity", "identity": "/subscriptions/s/uami"})
        self.assertNotIn("connectionRuntimeUrl", entry)

    def test_writing_a_managed_entry_preserves_other_connection_classes(self):
        """The write is read-modify-write over a live file, so unrelated classes must survive."""
        existing = {
            "serviceProviderConnections": {"blob": {"serviceProvider": {"id": "/serviceProviders/AzureBlob"}}},
            "managedApiConnections": {"already": {"api": {"id": "/api/other"}}},
        }
        client = _RecordingVfsClient(existing)
        _managed_connection.write_connections_entry(
            _FakeCmd(), "rg", "app", "new", {"api": {"id": "/api/new"}}, vfs_client=client)
        written = json.loads(client.written.decode("utf-8"))
        self.assertIn("blob", written["serviceProviderConnections"])
        self.assertIn("already", written["managedApiConnections"])
        self.assertIn("new", written["managedApiConnections"])

    def test_writing_a_managed_entry_refuses_missing_file_without_a_revision(self):
        client = _RecordingVfsClient(ResourceNotFoundError("missing"))
        with self.assertRaisesRegex(CLIError, "strong connections.json ETag"):
            _managed_connection.write_connections_entry(
                _FakeCmd(), "rg", "app", "new", {"api": {"id": "/api/new"}}, vfs_client=client)
        self.assertIsNone(client.written)

    def test_unknown_auth_mode_is_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            _managed_connection.create_managed_connection(
                _FakeCmd(), "rg", "app", "conn", "azureblob", "eastus", "device-code")

    def test_managed_identity_parameter_set_is_read_from_connector_metadata(self):
        payload = {"properties": {"connectionParameterSets": {"values": [
            {"name": "keyBasedAuth", "parameters": {"accountKey": {"type": "securestring"}}},
            {"name": "managedIdentityAuth", "parameters": {"token": {"type": "managedIdentity"}}},
        ]}}}

        def _sender(*_args, **_kwargs):
            return _FakeResponse(payload)

        self.assertEqual(
            _managed_connection._managed_identity_parameter_set(_FakeCmd(), "/managedApis/azureblob", _sender),
            "managedIdentityAuth")

    def test_connector_without_a_managed_identity_set_is_refused(self):
        payload = {"properties": {"connectionParameterSets": {"values": [
            {"name": "oauth", "parameters": {"token": {"type": "oauthSetting"}}},
        ]}}}

        def _sender(*_args, **_kwargs):
            return _FakeResponse(payload)

        with self.assertRaises(ValidationError) as ctx:
            _managed_connection._managed_identity_parameter_set(_FakeCmd(), "/managedApis/office365", _sender)
        self.assertIn("no managed-identity parameter set", str(ctx.exception))

    def test_acl_add_refuses_a_v1_connection(self):
        def _sender(_ctx, method, _url, **_kwargs):
            self.assertEqual(method, "GET")
            return _FakeResponse({"kind": "V1", "location": "eastus"})

        with self.assertRaises(ValidationError) as ctx, _fake_azure_context():
            _managed_connection.acl_add(_FakeCmd(), "rg", "conn", "object-1", sender=_sender)
        self.assertIn("V1", str(ctx.exception))

    def test_acl_add_refuses_a_second_policy_for_the_same_principal(self):
        """The service answers this collision with an opaque 500, so it is caught first."""
        policies = {"value": [{
            "name": "existing-policy",
            "properties": {"principal": {"identity": {"objectId": "OBJECT-1"}}},
        }]}

        def _sender(_ctx, _method, url, **_kwargs):
            if "/accessPolicies" in url:
                return _FakeResponse(policies)
            return _FakeResponse({"kind": "V2", "location": "eastus"})

        with self.assertRaises(ValidationError) as ctx, _fake_azure_context():
            _managed_connection.acl_add(
                _FakeCmd(), "rg", "conn", "object-1", tenant_id="t", policy="new-name", sender=_sender)
        message = str(ctx.exception)
        self.assertIn("existing-policy", message)
        self.assertIn("at most one access policy per principal", message)

    def test_acl_add_allows_updating_the_same_policy_name(self):
        policies = {"value": [{
            "name": "same-name",
            "properties": {"principal": {"identity": {"objectId": "object-1"}}},
        }]}
        sent = []

        def _sender(_ctx, method, url, **kwargs):
            sent.append((method, url))
            if method == "GET" and "/accessPolicies?" in url:
                return _FakeResponse(policies)
            if method == "GET":
                return _FakeResponse({"kind": "V2", "location": "eastus"})
            return _FakeResponse({"name": "same-name", "properties": {
                "principal": {"type": "ActiveDirectory", "identity": {"objectId": "object-1"}}}})

        with _fake_azure_context():
            result = _managed_connection.acl_add(
                _FakeCmd(), "rg", "conn", "object-1", tenant_id="t", policy="same-name", sender=_sender)
        self.assertEqual(result["name"], "same-name")
        self.assertIn("PUT", [method for method, _ in sent])

    def test_missing_app_identity_stops_before_creating_anything(self):
        def _identity_sender(*_args, **_kwargs):
            return _FakeResponse({"identity": None})

        def _arm_sender(*_args, **_kwargs):
            raise AssertionError("no ARM connection may be created without an app identity")

        with self.assertRaises(ValidationError) as ctx, _fake_azure_context():
            _managed_connection.create_managed_connection(
                _FakeCmd(), "rg", "app", "conn",
                "/subscriptions/s/providers/Microsoft.Web/locations/eastus/managedApis/azureblob",
                "eastus", "raw", parameter_set="keyBasedAuth",
                identity_sender=_identity_sender, arm_sender=_arm_sender)
        message = str(ctx.exception)
        self.assertIn("requires a managed identity", message)
        self.assertIn("No ARM connection was created", message)

    def test_parameter_parsing_requires_name_equals_value(self):
        with self.assertRaises(InvalidArgumentValueError):
            _managed_connection._parse_parameters([["accountName"]])

    def test_parameters_accumulate_across_repeated_flags(self):
        parsed = _managed_connection._parse_parameters([["a=1", "b=2"], ["c=3"]])
        self.assertEqual(parsed, {"a": "1", "b": "2", "c": "3"})

    def test_policy_view_normalizes_principal_identity(self):
        view = _managed_connection._policy_view({
            "id": "/p", "name": "p", "location": "eastus",
            "properties": {"principal": {"type": "ActiveDirectory",
                                         "identity": {"objectId": "o", "tenantId": "t"}}},
        })
        self.assertEqual(view["principal"], {"type": "ActiveDirectory", "objectId": "o", "tenantId": "t"})

    def test_acl_table_format_flattens_principal(self):
        rows = _managed_connection.acl_list_table_format(
            {"value": [{"name": "p", "principal": {"objectId": "o", "tenantId": "t"}}]})
        self.assertEqual(rows, [{"Name": "p", "ObjectId": "o", "TenantId": "t"}])


class ConnectionDeleteTests(unittest.TestCase):
    """Deleting a connection from a deployed app."""

    SUB = "/subscriptions/sub1/resourceGroups/rg/providers/Microsoft.Web/connections/blobProd"

    def _payload(self, managed=True, extra=None):
        payload = {}
        if managed:
            payload["managedApiConnections"] = {
                "blobProd": {"api": {"id": "/x/managedApis/azureblob"},
                             "connection": {"id": self.SUB},
                             "authentication": {"type": "ManagedServiceIdentity"}}}
        if extra:
            payload.update(extra)
        return payload

    def _sender(self, policies, calls, identity_object_id="own-oid"):
        def send(_ctx, method, url, headers=None, body=None):  # pylint: disable=unused-argument
            calls.append((method, url.split("?")[0]))
            if "/providers/Microsoft.Web/sites/" in url and "connections" not in url:
                return _FakeResponse({"identity": {"type": "SystemAssigned",
                                                   "principalId": identity_object_id,
                                                   "tenantId": "tenant-1"}})
            if url.split("?")[0].endswith("/accessPolicies"):
                return _FakeResponse({"value": policies})
            return _FakeResponse({})
        return send

    @staticmethod
    def _policy(name, object_id):
        return {"name": name,
                "properties": {"principal": {"type": "ActiveDirectory",
                                             "identity": {"objectId": object_id,
                                                          "tenantId": "tenant-1"}}}}

    def test_sole_consumer_deletes_the_arm_resource(self):
        client = _RecordingVfsClient(self._payload())
        calls = []
        with _fake_azure_context():
            result = _connection.connection_delete(
                _FakeCmd(), "rg", "app", "blobProd", client=client,
                sender=self._sender([self._policy("app-own-oid", "own-oid")], calls))
        self.assertTrue(result["resource"]["removed"])
        self.assertEqual(result["accessPolicies"]["removed"], ["app-own-oid"])
        self.assertIn(("DELETE", self.SUB), calls)
        self.assertEqual(json.loads(client.written.decode("utf-8"))["managedApiConnections"], {})

    def test_shared_connection_keeps_the_resource_and_explains_why(self):
        client = _RecordingVfsClient(self._payload())
        calls = []
        with _fake_azure_context():
            result = _connection.connection_delete(
                _FakeCmd(), "rg", "app", "blobProd", client=client,
                sender=self._sender([self._policy("app-own-oid", "own-oid"),
                                     self._policy("other-app", "other-oid")], calls))
        self.assertFalse(result["resource"]["removed"])
        self.assertIn("shared", result["resource"]["reason"])
        self.assertEqual(result["accessPolicies"]["retained"], ["other-app"])
        self.assertNotIn(("DELETE", self.SUB), calls)

    def test_shared_connection_still_revokes_this_app_access(self):
        calls = []
        with _fake_azure_context():
            _connection.connection_delete(
                _FakeCmd(), "rg", "app", "blobProd", client=_RecordingVfsClient(self._payload()),
                sender=self._sender([self._policy("app-own-oid", "own-oid"),
                                     self._policy("other-app", "other-oid")], calls))
        self.assertIn(("DELETE", self.SUB + "/accessPolicies/app-own-oid"), calls)
        self.assertNotIn(("DELETE", self.SUB + "/accessPolicies/other-app"), calls)

    def test_keep_resource_retains_a_connection_this_app_solely_owns(self):
        calls = []
        with _fake_azure_context():
            result = _connection.connection_delete(
                _FakeCmd(), "rg", "app", "blobProd", keep_resource=True,
                client=_RecordingVfsClient(self._payload()),
                sender=self._sender([self._policy("app-own-oid", "own-oid")], calls))
        self.assertFalse(result["resource"]["removed"])
        self.assertIn("--keep-resource", result["resource"]["reason"])
        self.assertNotIn(("DELETE", self.SUB), calls)

    def test_connections_json_is_written_before_arm_mutations(self):
        """Read-only preflight precedes unlink; destructive ARM cleanup follows it."""
        order = []
        client = _RecordingVfsClient(self._payload())
        original_put = client.put_raw

        def tracking_put(path, content, params=None, if_match=None):
            order.append("connections.json")
            return original_put(path, content, params, if_match=if_match)

        client.put_raw = tracking_put
        calls = []

        def send(ctx, method, url, headers=None, body=None):
            if method == "DELETE":
                order.append("arm")
            return self._sender([self._policy("app-own-oid", "own-oid")], calls)(
                ctx, method, url, headers, body)

        with _fake_azure_context():
            _connection.connection_delete(_FakeCmd(), "rg", "app", "blobProd",
                                          client=client, sender=send)
        self.assertEqual(order[0], "connections.json")
        self.assertIn("arm", order)

    def test_service_provider_entry_reports_orphaned_app_settings(self):
        payload = {"serviceProviderConnections": {"sb": {
            "parameterValues": {"connectionString": "@appsetting('SB_CONN')"},
            "serviceProvider": {"id": "/serviceProviders/serviceBus"}}}}
        client = _RecordingVfsClient(payload)
        result = _connection.connection_delete(_FakeCmd(), "rg", "app", "sb", client=client)
        self.assertEqual(result["class"], "serviceProviderConnections")
        self.assertEqual(result["orphanedAppSettings"], ["SB_CONN"])
        self.assertEqual(json.loads(client.written.decode("utf-8"))["serviceProviderConnections"], {})

    def test_service_provider_delete_never_touches_arm(self):
        payload = {"serviceProviderConnections": {"sb": {"parameterValues": {}}}}
        calls = []
        _connection.connection_delete(
            _FakeCmd(), "rg", "app", "sb", client=_RecordingVfsClient(payload),
            sender=self._sender([], calls))
        self.assertEqual(calls, [])

    def test_missing_connection_raises_not_found(self):
        with self.assertRaises(ResourceNotFoundError):
            _connection.connection_delete(_FakeCmd(), "rg", "app", "nope",
                                          client=_RecordingVfsClient(self._payload()))

    def test_ambiguous_name_is_refused_rather_than_guessed(self):
        payload = self._payload(extra={"serviceProviderConnections": {"blobProd": {}}})
        with self.assertRaises(ValidationError) as ctx:
            _connection.connection_delete(_FakeCmd(), "rg", "app", "blobProd",
                                          client=_RecordingVfsClient(payload))
        self.assertIn("--class", str(ctx.exception))

    def test_class_filter_resolves_the_ambiguity(self):
        payload = self._payload(extra={"serviceProviderConnections": {"blobProd": {}}})
        client = _RecordingVfsClient(payload)
        result = _connection.connection_delete(
            _FakeCmd(), "rg", "app", "blobProd", connection_class="serviceProviderConnections",
            client=client)
        self.assertEqual(result["class"], "serviceProviderConnections")
        written = json.loads(client.written.decode("utf-8"))
        self.assertEqual(written["serviceProviderConnections"], {})
        self.assertIn("blobProd", written["managedApiConnections"])

    def test_invalid_class_is_rejected(self):
        with self.assertRaises(ValidationError):
            _connection.connection_delete(_FakeCmd(), "rg", "app", "blobProd",
                                          connection_class="nope",
                                          client=_RecordingVfsClient(self._payload()))

    def test_other_connections_survive_the_write(self):
        payload = self._payload(extra={"serviceProviderConnections": {"keep": {"parameterValues": {}}}})
        client = _RecordingVfsClient(payload)
        calls = []
        with _fake_azure_context():
            _connection.connection_delete(
                _FakeCmd(), "rg", "app", "blobProd", client=client,
                sender=self._sender([self._policy("app-own-oid", "own-oid")], calls))
        written = json.loads(client.written.decode("utf-8"))
        self.assertIn("keep", written["serviceProviderConnections"])

    def test_user_assigned_identity_retains_shared_access(self):
        """A UAMI assignment cannot establish exclusive ownership by this app."""
        def send(_ctx, method, url, headers=None, body=None):
            if "/providers/Microsoft.Web/sites/" in url and "connections" not in url:
                return _FakeResponse({"identity": {
                    "type": "UserAssigned", "tenantId": "tenant-1",
                    "userAssignedIdentities": {"/x/uami": {"principalId": "uami-oid"}}}})
            if url.split("?")[0].endswith("/accessPolicies"):
                return _FakeResponse({"value": [self._policy("uami-policy", "uami-oid")]})
            return _FakeResponse({})

        payload = self._payload()
        payload["managedApiConnections"]["blobProd"]["authentication"]["identity"] = "/x/uami"
        with _fake_azure_context():
            result = _connection.connection_delete(
                _FakeCmd(), "rg", "app", "blobProd",
                client=_RecordingVfsClient(payload), sender=send)
        self.assertFalse(result["resource"]["removed"])
        self.assertIn("shared", result["resource"]["reason"])
        self.assertEqual(result["accessPolicies"]["removed"], [])
        self.assertEqual(result["accessPolicies"]["retained"], ["uami-policy"])

    def test_already_absent_policy_does_not_abort_the_delete(self):
        def send(_ctx, method, url, headers=None, body=None):
            if "/providers/Microsoft.Web/sites/" in url and "connections" not in url:
                return _FakeResponse({"identity": {"type": "SystemAssigned",
                                                   "principalId": "own-oid",
                                                   "tenantId": "tenant-1"}})
            if url.split("?")[0].endswith("/accessPolicies"):
                return _FakeResponse({"value": [self._policy("gone", "own-oid")]})
            if method == "DELETE" and "/accessPolicies/" in url:
                raise ResourceNotFoundError("already gone")
            return _FakeResponse({})

        with _fake_azure_context():
            result = _connection.connection_delete(
                _FakeCmd(), "rg", "app", "blobProd",
                client=_RecordingVfsClient(self._payload()), sender=send)
        self.assertTrue(result["resource"]["removed"])
        self.assertEqual(result["accessPolicies"]["removed"], [])


if __name__ == "__main__":
    unittest.main()


class FreshMachineRegressionTests(unittest.TestCase):
    """Defects found by running the published wheel end to end on a clean machine."""

    def test_connector_id_from_connector_list_round_trips_into_connector_show(self):
        # 'connector list' reports id '/serviceProviders/serviceBus'. Quoting that with
        # safe="" produced '%2FserviceProviders%2FserviceBus' and the runtime answered
        # ApiNotFound, so the output of one command could not be fed to the next.
        expected = _runtime_client.operation_group_path("serviceBus")

        for form in ("/serviceProviders/serviceBus", "serviceProviders/serviceBus",
                     "/ServiceProviders/serviceBus", "serviceBus", "/serviceBus"):
            actual = _runtime_client.operation_group_path(form)
            self.assertEqual(expected, actual, "connector reference '{}' did not normalize".format(form))
            self.assertNotIn("%2F", actual)
            self.assertTrue(actual.endswith("/serviceBus"))

    def test_connector_normalization_still_quotes_unsafe_characters(self):
        # Normalizing must not become "stop quoting": a name with a slash or space
        # still has to be escaped into a single route segment.
        self.assertTrue(_runtime_client.operation_group_path("odd name").endswith("/odd%20name"))
        self.assertTrue(_runtime_client.operation_group_path("a/b").endswith("/a%2Fb"))

    def test_port_in_use_is_detected_even_when_the_server_set_so_reuseaddr(self):
        # _port_free decided by binding with SO_REUSEADDR. On Windows that option
        # means "bind even though this address is taken", so any server that also set
        # it -- the Functions host among them -- read as absent and 'runtime show'
        # reported 'stopped' for a runtime that was up and answering.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(("127.0.0.1", 0))
            server.listen(1)
            port = server.getsockname()[1]
            self.assertFalse(_local._port_free(port), "a listening server must read as in use")
        finally:
            server.close()

    def test_port_with_nothing_on_it_reads_as_free(self):
        # The detection must stay conditional: a genuinely free port must read free,
        # otherwise 'runtime start' would refuse every port.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        self.assertTrue(_local._port_free(port))

    def _storage_project(self, label, storage):
        root = _workspace(label) / "app"
        root.mkdir()
        (root / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        if storage is not None:
            (root / "local.settings.json").write_text(
                json.dumps({"IsEncrypted": False, "Values": {"AzureWebJobsStorage": storage}}),
                encoding="utf-8")
        return root

    def test_uses_development_storage_is_tri_state(self):
        # 'unknown' must not collapse into either answer: the CLI cannot read a
        # project it was never given, and must not assert anything about it.
        emulator = self._storage_project("stg-emulator", "UseDevelopmentStorage=true")
        real = self._storage_project(
            "stg-real", "DefaultEndpointsProtocol=https;AccountName=acct;AccountKey=k;")
        absent = self._storage_project("stg-absent", None)

        self.assertIs(True, _local.uses_development_storage(str(emulator)))
        self.assertIs(False, _local.uses_development_storage(str(real)))
        self.assertIsNone(_local.uses_development_storage(str(absent)))
        self.assertIsNone(_local.uses_development_storage(None))

    def test_azurite_is_required_only_when_the_project_uses_development_storage(self):
        # 'dependency check' hardcoded Azurite as optional, so a developer on
        # development storage was told a missing Azurite did not matter -- and then
        # the host refused to start against 127.0.0.1:10000.
        emulator = self._storage_project("req-emulator", "UseDevelopmentStorage=true")
        real = self._storage_project(
            "req-real", "DefaultEndpointsProtocol=https;AccountName=acct;AccountKey=k;")

        def azurite_row(project):
            report = _local.dependency_report(kind=["azurite"], project_path=project)
            return report["value"][0], report

        row, report = azurite_row(str(emulator))
        self.assertTrue(row["required"])
        self.assertIs(True, report["usesDevelopmentStorage"])

        row, report = azurite_row(str(real))
        self.assertFalse(row["required"])
        self.assertIs(False, report["usesDevelopmentStorage"])

        row, report = azurite_row(None)
        self.assertFalse(row["required"], "unknown storage keeps the historical answer")
        self.assertIsNone(report["usesDevelopmentStorage"])
        self.assertIsNotNone(row["requiredWhen"], "the condition must be stated, not implied")

    def test_dependency_install_skips_a_tool_already_on_path(self):
        # Installing a second Node.js over a working one wastes a long download and
        # leaves two copies whose precedence is not obvious.
        with mock.patch.object(custom, "find_tool", return_value=("/usr/bin/node", "path")):
            result = custom.dependency_install(None, kind=["node"])

        row = result["value"][0]
        self.assertEqual("skipped", row["result"])
        self.assertEqual("alreadyPresent", row["reason"])
        self.assertEqual("/usr/bin/node", row["path"])

    def test_dependency_install_force_overrides_the_skip(self):
        # --force must still reach the installer, otherwise the escape hatch is a lie.
        with mock.patch.object(custom, "find_tool", return_value=("/usr/bin/node", "path")):
            with mock.patch.object(custom, "install_dependency",
                                   return_value={"kind": "node", "result": "installed"}) as installer:
                result = custom.dependency_install(None, kind=["node"], force=True, yes=True)

        self.assertTrue(installer.called, "--force must not be swallowed by the skip")
        self.assertEqual("installed", result["value"][0]["result"])

    def test_dependency_install_installs_when_the_tool_is_absent(self):
        # The skip must be conditional on actually finding the tool.
        with mock.patch.object(custom, "find_tool", return_value=(None, None)):
            with mock.patch.object(custom, "install_dependency",
                                   return_value={"kind": "node", "result": "installed"}) as installer:
                result = custom.dependency_install(None, kind=["node"], yes=True)

        self.assertTrue(installer.called)
        self.assertEqual("installed", result["value"][0]["result"])

    def test_package_excludes_funcignore_patterns_and_metadata_files(self):
        # Every unrecognized file was packaged as class "other", so the only way to
        # keep a scratch payload out of a deployment was to move it out of the project.
        root = _workspace("pkg-ignore") / "app"
        root.mkdir()
        (root / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        (root / ".funcignore").write_text("scratch/\n*.sample\n# comment\n\n", encoding="utf-8")
        (root / ".gitignore").write_text("ignored\n", encoding="utf-8")
        (root / "payload.sample").write_text("test data", encoding="utf-8")
        (root / "keep.json").write_text("{}", encoding="utf-8")
        scratch = root / "scratch"
        scratch.mkdir()
        (scratch / "notes.txt").write_text("scratch", encoding="utf-8")

        archive = root.parent / "out.zip"
        report = _workflow.deterministic_package(str(root), str(archive))

        included = {item["path"] for item in report["included"]}
        reasons = {item["path"]: item["reason"] for item in report["excluded"]}

        self.assertIn("host.json", included)
        self.assertIn("keep.json", included)
        self.assertNotIn("payload.sample", included)
        self.assertNotIn("scratch/notes.txt", included)
        self.assertNotIn(".funcignore", included)
        self.assertNotIn(".gitignore", included)
        self.assertEqual("ignoreFile", reasons.get("payload.sample"))
        self.assertEqual("metadata", reasons.get(".gitignore"))
        self.assertEqual("metadata", reasons.get(".funcignore"))

        with zipfile.ZipFile(str(archive)) as bundle:
            names = set(bundle.namelist())
        self.assertNotIn("payload.sample", names, "an ignored file must not reach the archive")
        self.assertIn("keep.json", names)


class AzuriteInstallTests(unittest.TestCase):
    """Azurite is installed through npm rather than by unpacking an archive.

    npm is not run here: these cover the decisions around it -- which npm, whether the
    Node.js behind it can run Azurite, which registry, and whether a reported success
    actually leaves something 'dependency check' can find.
    """

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="azurite-install-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def _managed_node(self, executable="npm.cmd"):
        node_dir = self.root / _local.managed_subdir("node")
        node_dir.mkdir(parents=True, exist_ok=True)
        launcher = node_dir / executable
        launcher.write_text("", encoding="utf-8")
        os.chmod(str(launcher), 0o755)
        return launcher

    def test_npm_from_the_managed_node_is_preferred_over_path(self):
        # A CLI-installed Node.js is deliberately not on PATH, so resolving npm through
        # PATH alone would ignore the copy the user was just told to install.
        launcher = self._managed_node()
        with mock.patch("azext_logicapp._dependencies.shutil.which") as which:
            which.side_effect = lambda name, path=None: str(launcher) if path else "/usr/bin/npm"
            self.assertEqual(_dependencies._resolve_npm(str(self.root)), str(launcher))

    def test_missing_npm_names_the_command_that_provides_it(self):
        with mock.patch("azext_logicapp._dependencies._resolve_npm", return_value=None):
            with self.assertRaises(ValidationError) as caught:
                _dependencies._install_azurite(root=str(self.root))
        message = str(caught.exception)
        self.assertIn("npm", message)
        self.assertIn("dependency install --kind node", message)

    def test_node_older_than_azurite_requires_is_refused_before_installing(self):
        # npm treats engines as a warning, so without this the install "succeeds" and
        # Azurite then fails the first time it is run.
        calls = []
        with mock.patch("azext_logicapp._dependencies._resolve_npm", return_value="npm"), \
                mock.patch("azext_logicapp._dependencies._npm_node_major", return_value=18), \
                mock.patch("azext_logicapp._dependencies._run_npm",
                           side_effect=lambda *a, **k: calls.append(a) or (True, "")):
            with self.assertRaises(ValidationError) as caught:
                _dependencies._install_azurite(root=str(self.root))
        self.assertIn(str(_dependencies.AZURITE_MIN_NODE_MAJOR), str(caught.exception))
        self.assertEqual([], calls, "nothing should be installed once the engine check fails")

    def test_node_major_is_read_from_npms_object_literal_output(self):
        with mock.patch("azext_logicapp._dependencies._run_npm",
                        return_value=(True, "{\n  npm: '10.9.0',\n  node: '22.11.0',\n  v8: '12.4'\n}")):
            self.assertEqual(_dependencies._npm_node_major("npm"), 22)

    def test_public_registry_is_used_instead_of_the_machines_npm_config(self):
        # The corporate-mirror 401 is exactly how the documented 'npm install -g azurite'
        # route fails, and Node.js and Core Tools are fetched from their publisher too.
        _, captured = self._install_with_fake_npm()
        install = [args for args in captured if args and args[0] == "install"][0]
        self.assertIn("--registry", install)
        self.assertEqual(_dependencies.NPM_REGISTRY, install[install.index("--registry") + 1])

    def test_source_url_overrides_the_registry_and_drops_the_publisher_guarantee(self):
        report, captured = self._install_with_fake_npm(source_url="https://mirror.example/npm/")
        install = [args for args in captured if args and args[0] == "install"][0]
        self.assertEqual("https://mirror.example/npm/", install[install.index("--registry") + 1])
        self.assertFalse(report["checksumVerified"])

    def test_install_is_staged_outside_the_managed_folder(self):
        # npm writing straight into the target would leave a half-installed folder
        # behind if it failed partway, and stamp the manifest over the wreckage.
        _, captured = self._install_with_fake_npm()
        install = [args for args in captured if args and args[0] == "install"][0]
        self.assertIn("--prefix", install)
        prefix = Path(install[install.index("--prefix") + 1]).resolve()
        self.assertFalse(str(prefix).startswith(str(self.root.resolve())))

    def test_reported_success_means_dependency_check_can_find_azurite(self):
        # npm exiting 0 is not evidence the folder holds a runnable Azurite, and a
        # success that find_tool cannot then locate is the failure this guards.
        report, _ = self._install_with_fake_npm()
        self.assertEqual("installed", report["state"])
        with mock.patch.dict(os.environ, {"LA_DEPENDENCIES_PATH": str(self.root)}), \
                mock.patch("azext_logicapp._local.shutil.which",
                           side_effect=lambda name, path=None: None if path is None else next(
                               (str(Path(entry) / "azurite.cmd") for entry in path.split(os.pathsep)
                                if (Path(entry) / "azurite.cmd").is_file()), None)):
            found, source = _local.find_tool("azurite")
        self.assertEqual("managed", source)
        self.assertTrue(found)

    def test_npm_success_without_a_runnable_azurite_is_an_error_not_an_install(self):
        target = self.root / _local.managed_subdir("azurite")
        with self._fake_npm(populate=lambda staging: os.makedirs(staging, exist_ok=True)):
            with self.assertRaises(CLIError) as caught:
                _dependencies._install_azurite(root=str(self.root))
        self.assertIn("no runnable Azurite", str(caught.exception))
        self.assertFalse(target.exists(), "a failed install must not leave a half-written folder")

    def test_failed_npm_surfaces_its_output_and_writes_nothing(self):
        target = self.root / _local.managed_subdir("azurite")
        with mock.patch("azext_logicapp._dependencies._resolve_npm", return_value="npm"), \
                mock.patch("azext_logicapp._dependencies._npm_node_major", return_value=22), \
                mock.patch("azext_logicapp._dependencies._run_npm",
                           return_value=(False, "npm error code E401")):
            with self.assertRaises(CLIError) as caught:
                _dependencies._install_azurite(root=str(self.root), version="3.35.0")
        self.assertIn("E401", str(caught.exception))
        self.assertFalse(target.exists())

    def test_version_recorded_is_the_one_on_disk_not_the_one_requested(self):
        report, _ = self._install_with_fake_npm(version="3.35.0", package_version="3.36.1")
        self.assertEqual("3.36.1", report["version"])

    def test_manifest_is_written_so_uninstall_can_remove_the_install(self):
        # The manifest is folder-level provenance: it is the only evidence the CLI,
        # rather than the user or VS Code, created this folder in a shared root.
        report, _ = self._install_with_fake_npm()
        target = Path(report["path"])
        manifest = json.loads((target / _dependencies.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual("azurite", manifest["dependencyName"])
        self.assertEqual("az logicapp dependency install", manifest["installedBy"])
        self.assertGreater(manifest["fileCount"], 0)

        result = _dependencies.uninstall_dependency("azurite", root=str(self.root))
        self.assertEqual("removed", result["state"])
        self.assertFalse(target.exists())

    def test_uninstall_leaves_an_azurite_this_cli_did_not_install(self):
        target = self.root / _local.managed_subdir("azurite")
        target.mkdir(parents=True)
        (target / "someone-elses.txt").write_text("x", encoding="utf-8")
        result = _dependencies.uninstall_dependency("azurite", root=str(self.root))
        self.assertEqual("not-cli-managed", result["state"])
        self.assertTrue((target / "someone-elses.txt").is_file())

    def test_a_folder_this_cli_did_not_install_is_left_alone(self):
        target = self.root / _local.managed_subdir("azurite")
        target.mkdir(parents=True)
        (target / "someone-elses.txt").write_text("x", encoding="utf-8")
        with mock.patch("azext_logicapp._dependencies._resolve_npm", return_value="npm"), \
                mock.patch("azext_logicapp._dependencies._npm_node_major", return_value=22), \
                mock.patch("azext_logicapp._dependencies._run_npm", return_value=(True, "3.35.0")):
            report = _dependencies._install_azurite(root=str(self.root))
        self.assertEqual("already-present-not-cli-managed", report["state"])
        self.assertTrue((target / "someone-elses.txt").is_file())

    def test_unreachable_registry_falls_back_to_the_pinned_version(self):
        with mock.patch("azext_logicapp._dependencies._run_npm", return_value=(False, "ETIMEDOUT")):
            version, source = _dependencies._resolve_azurite_version("npm", _dependencies.NPM_REGISTRY, None)
        self.assertEqual(_dependencies.PINNED_VERSIONS["azurite"], version)
        self.assertEqual("pinned-fallback", source)

    # -- helpers -------------------------------------------------------------

    def _fake_npm(self, populate=None, captured=None, package_version="3.35.0"):
        """Stand in for npm, laying down the layout 'npm install -g --prefix' produces."""
        def default_populate(staging):
            package = Path(staging) / "node_modules" / "azurite"
            package.mkdir(parents=True, exist_ok=True)
            (package / "package.json").write_text(
                json.dumps({"name": "azurite", "version": package_version}), encoding="utf-8")
            launcher = Path(staging) / "azurite.cmd"
            launcher.write_text("@echo off", encoding="utf-8")

        write = populate or default_populate

        def run_npm(npm, args, timeout=None):
            del npm, timeout
            args = list(args)
            if captured is not None:
                captured.append(args)
            if args and args[0] == "install":
                write(args[args.index("--prefix") + 1])
                return True, ""
            return True, package_version

        return _StackedPatches([
            mock.patch("azext_logicapp._dependencies._resolve_npm", return_value="npm"),
            mock.patch("azext_logicapp._dependencies._npm_node_major", return_value=22),
            mock.patch("azext_logicapp._dependencies._run_npm", side_effect=run_npm),
            mock.patch("azext_logicapp._dependencies.shutil.which",
                       side_effect=lambda name, path=None: None if path is None else next(
                           (str(Path(entry) / "azurite.cmd") for entry in path.split(os.pathsep)
                            if (Path(entry) / "azurite.cmd").is_file()), None)),
        ])

    def _install_with_fake_npm(self, package_version="3.35.0", **kwargs):
        """Run the installer against a stand-in npm. Returns (report, npm_arg_lists)."""
        captured = []
        with self._fake_npm(captured=captured, package_version=package_version):
            report = _dependencies._install_azurite(root=str(self.root), **kwargs)
        return report, captured


class _StackedPatches:
    def __init__(self, patches):
        self._patches = patches

    def __enter__(self):
        for patch in self._patches:
            patch.start()
        return self

    def __exit__(self, *exc):
        for patch in reversed(self._patches):
            patch.stop()
        return False


# Distinguishes "the runtime omitted properties.trigger" from "it sent an explicit
# null", which are different wire shapes that must classify the same way.
_MISSING = object()


def _runtime_operation_is_trigger_for(trigger):
    return custom._runtime_operation_is_trigger({"name": "x", "properties": {"trigger": trigger}})


class ConnectorOperationTests(unittest.TestCase):
    """Built-in (service provider) connector operations: az logicapp connector operation."""

    class _Recorder(object):
        def __init__(self, payload):
            self.payload = payload
            self.paths = []

        def get(self, path, params=None):
            self.paths.append(path)
            return self.payload

    @staticmethod
    def _operation(name, trigger=_MISSING, summary=None, description=None):
        properties = {"api": {"name": "serviceBus"}, "operationType": "ServiceProvider"}
        if trigger is not _MISSING:
            properties["trigger"] = trigger
        if summary is not None:
            properties["summary"] = summary
        if description is not None:
            properties["description"] = description
        return {
            "name": name,
            "id": "/serviceProviders/serviceBus/operations/" + name,
            "type": "Microsoft.Web/locations/operationGroups/operations",
            "properties": properties,
        }

    def _catalog(self):
        # Mirrors what a live runtime actually returns, which is not quite what the C#
        # enum names suggest: triggers carry properties.trigger as PascalCase "Batch" or
        # "Single", and actions omit the field entirely. Observed on a deployed app:
        # serviceBus returns 41 operations, 6 Batch + 4 Single + 31 with no trigger key.
        # The lowercase and notSpecified forms are accepted defensively.
        return [
            self._operation("sendMessage", summary="Send message", description="Send a message to a queue"),
            self._operation("getMessage", trigger=None),
            self._operation("deleteMessage", trigger="notSpecified"),
            self._operation("whenMessagesArrive", trigger="Batch", summary="When messages arrive"),
            self._operation("whenOneMessageArrives", trigger="Single", summary="When one message arrives"),
        ]

    def _list(self, connector="/serviceProviders/serviceBus", payload=None, **kwargs):
        body = {"value": self._catalog()} if payload is None else payload
        recorder = self._Recorder(body)
        with mock.patch.object(custom, "_client_from_target", return_value=(recorder, {"kind": "local"})):
            return custom.connector_operation_list(None, connector, **kwargs), recorder

    @staticmethod
    def _names(result):
        return [item["name"] for item in result["value"]]

    def test_list_returns_every_operation_by_default(self):
        result, recorder = self._list()
        self.assertEqual(recorder.paths, ["operationGroups/serviceBus/operations"])
        self.assertEqual(self._names(result),
                         ["sendMessage", "getMessage", "deleteMessage",
                          "whenMessagesArrive", "whenOneMessageArrives"])
        self.assertEqual(result["kind"], "all")
        self.assertIsNone(result["nextContinuationToken"])

    def test_triggers_are_selected_by_the_runtime_trigger_field(self):
        result, _ = self._list(kind="trigger")
        self.assertEqual(self._names(result), ["whenMessagesArrive", "whenOneMessageArrives"])

    def test_absent_and_notspecified_triggers_both_count_as_actions(self):
        # TriggerType.NotSpecified is the enum default, so whether the runtime omits the
        # field or serializes it, the operation is an action either way. Reading only one
        # of the two forms would misfile the other as a trigger.
        result, _ = self._list(kind="action")
        self.assertEqual(self._names(result), ["sendMessage", "getMessage", "deleteMessage"])

    def test_kind_filter_is_not_the_managed_operation_type_heuristic(self):
        # Every operation here reports operationType "ServiceProvider". If the kind were
        # inferred from operationType, as the managed catalog has to do, the split would
        # collapse and every operation would land on one side.
        triggers, _ = self._list(kind="trigger")
        actions, _ = self._list(kind="action")
        self.assertTrue(triggers["value"])
        self.assertTrue(actions["value"])

    def test_search_matches_summary_and_description_not_just_name(self):
        by_description, _ = self._list(search="message to a queue")
        self.assertEqual(self._names(by_description), ["sendMessage"])
        by_summary, _ = self._list(search="when one message")
        self.assertEqual(self._names(by_summary), ["whenOneMessageArrives"])

    def test_search_is_case_insensitive_and_matches_the_operation_id(self):
        result, _ = self._list(search="SERVICEPROVIDERS/SERVICEBUS/OPERATIONS/DELETE")
        self.assertEqual(self._names(result), ["deleteMessage"])

    def test_filtering_happens_before_paging(self):
        # Paging the unfiltered catalog first would slice the page out of operations the
        # caller excluded: --kind trigger --max-items 1 would return an empty page here
        # because the first unfiltered item is an action.
        result, _ = self._list(kind="trigger", max_items=1)
        self.assertEqual(self._names(result), ["whenMessagesArrive"])
        self.assertIsNotNone(result["nextContinuationToken"])

    def test_continuation_token_walks_the_filtered_set_to_completion(self):
        seen = []
        token = None
        for _ in range(5):
            result, _ = self._list(kind="trigger", max_items=1, next_token=token)
            seen.extend(self._names(result))
            token = result["nextContinuationToken"]
            if token is None:
                break
        self.assertEqual(seen, ["whenMessagesArrive", "whenOneMessageArrives"])
        self.assertIsNone(token)

    def test_search_and_kind_apply_together(self):
        result, _ = self._list(search="message", kind="trigger")
        self.assertEqual(self._names(result), ["whenMessagesArrive", "whenOneMessageArrives"])

    def test_connector_reference_forms_all_reach_the_same_route(self):
        for form in ("/serviceProviders/serviceBus", "serviceProviders/serviceBus", "serviceBus"):
            _, recorder = self._list(connector=form)
            self.assertEqual(recorder.paths, ["operationGroups/serviceBus/operations"],
                             "connector reference '{}' did not normalize".format(form))

    def test_empty_catalog_is_reported_as_an_empty_page(self):
        result, _ = self._list(payload={"value": []}, kind="trigger")
        self.assertEqual(result["value"], [])
        self.assertIsNone(result["nextContinuationToken"])

    def test_list_reports_the_connector_and_kind_it_was_asked_for(self):
        result, _ = self._list(connector="serviceBus", kind="trigger")
        self.assertEqual(result["connector"], "serviceBus")
        self.assertEqual(result["kind"], "trigger")

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            self._list(kind="triggers")

    def test_trigger_casing_on_the_wire_is_pascal_case(self):
        # A live runtime serializes TriggerType as "Batch"/"Single", not the lowercase the
        # enum members suggest. Comparing without folding case classified every trigger as
        # an action, so 'connector operation list --kind trigger' returned nothing at all
        # against a real app while a lowercase fixture kept every test green.
        for wire in ("Batch", "Single", "batch", "single", "BATCH"):
            self.assertTrue(_runtime_operation_is_trigger_for(wire),
                            "trigger value '{}' was not recognised".format(wire))
        for wire in (None, "notSpecified", "NotSpecified", "", "none"):
            self.assertFalse(_runtime_operation_is_trigger_for(wire),
                             "value '{}' must not be a trigger".format(wire))

    def test_absent_trigger_field_is_an_action(self):
        # The live runtime omits the key entirely for actions -- 31 of serviceBus's 41
        # operations -- so absence, not a sentinel value, is the common case.
        self.assertFalse(custom._runtime_operation_is_trigger({"name": "x", "properties": {}}))
        self.assertFalse(custom._runtime_operation_is_trigger({"name": "x"}))

    def _show(self, operation, connector="serviceBus"):
        recorder = self._Recorder(self._operation("sendMessage"))
        with mock.patch.object(custom, "_client_from_target", return_value=(recorder, {"kind": "local"})):
            custom.connector_operation_show(None, connector, operation)
        return recorder.paths

    def test_operation_id_from_list_round_trips_into_show(self):
        # 'connector operation list' reports the full id. Quoting that whole value would
        # produce one percent-encoded segment and the runtime would answer not-found, so
        # the output of one command could not be fed into the next.
        self.assertEqual(self._show("/serviceProviders/serviceBus/operations/sendMessage"),
                         ["operationGroups/serviceBus/operations/sendMessage"])

    def test_bare_operation_name_still_works(self):
        self.assertEqual(self._show("sendMessage"),
                         ["operationGroups/serviceBus/operations/sendMessage"])

    def test_operation_normalization_still_quotes_unsafe_characters(self):
        # Normalizing must not become "stop quoting": a name with a space still has to be
        # escaped into a single route segment.
        self.assertEqual(self._show("odd name"),
                         ["operationGroups/serviceBus/operations/odd%20name"])


class PaginationSurfaceTests(unittest.TestCase):
    """The flag surface every paged command shares.

    The extension previously shipped three different spellings across seven commands --
    --continuation-token only, --next-token only, and both -- while every response came
    back keyed nextContinuationToken. A token copied out of one command's output was
    rejected by the next one the user tried.
    """

    TOKEN_OPTIONS = ["--next-token", "--continuation-token"]

    @staticmethod
    def _arguments_for(command):
        from types import SimpleNamespace
        from azure.cli.core import get_default_cli
        from azext_logicapp import COMMAND_LOADER_CLS

        cli = get_default_cli()
        # load_arguments resolves each argument_context against the command being invoked,
        # so the scope has to be primed before the registry is populated.
        cli.invocation = SimpleNamespace(data={"command_string": command})
        loader = COMMAND_LOADER_CLS(cli_ctx=cli)
        loader.load_command_table(args=[])
        loader.load_arguments(args=[])
        return loader.argument_registry.arguments.get(command, {})

    @classmethod
    def _command_names(cls):
        from types import SimpleNamespace
        from azure.cli.core import get_default_cli
        from azext_logicapp import COMMAND_LOADER_CLS

        cli = get_default_cli()
        cli.invocation = SimpleNamespace(data={"command_string": ""})
        return sorted(COMMAND_LOADER_CLS(cli_ctx=cli).load_command_table(args=[]))

    def _paged_commands(self):
        found = {}
        for name in self._command_names():
            arguments = self._arguments_for(name)
            if "next_token" in arguments or "continuation_token" in arguments:
                found[name] = arguments
        return found

    def test_every_paged_command_is_discovered(self):
        # Guards the rest of this class from silently testing nothing.
        self.assertEqual(len(self._paged_commands()), 8)

    def test_every_paged_command_accepts_both_token_spellings(self):
        for name, arguments in self._paged_commands().items():
            with self.subTest(command=name):
                self.assertIn("next_token", arguments)
                self.assertEqual(list(arguments["next_token"].settings["options_list"]), self.TOKEN_OPTIONS)

    def test_every_paged_command_groups_pagination_flags(self):
        for name, arguments in self._paged_commands().items():
            with self.subTest(command=name):
                self.assertEqual(arguments["next_token"].settings.get("arg_group"), "Pagination")
                self.assertEqual(arguments["max_items"].settings.get("arg_group"), "Pagination")

    def test_no_command_keeps_the_old_continuation_token_destination(self):
        for name, arguments in self._paged_commands().items():
            with self.subTest(command=name):
                self.assertNotIn("continuation_token", arguments)

    def test_text_filter_is_spelled_search_everywhere(self):
        for name in self._command_names():
            arguments = self._arguments_for(name)
            with self.subTest(command=name):
                self.assertNotIn("query_text", arguments)

    def test_query_text_survives_as_an_alias_on_managed_list(self):
        arguments = self._arguments_for("logicapp connector managed list")
        self.assertEqual(list(arguments["search"].settings["options_list"]), ["--search", "--query-text"])


class PagingTokenErrorTests(unittest.TestCase):
    """Malformed paging input is a user error, never an unhandled traceback.

    A bare ValueError escaping a command handler is reported by the CLI as "The command
    failed with an unexpected error", dumps a traceback, and invites the user to file an
    azure-cli bug. Every one of these inputs is something a user can type.
    """

    def test_malformed_token_raises_a_cli_user_error(self):
        with self.assertRaises(InvalidArgumentValueError) as caught:
            _paging.slice_items([1, 2, 3], next_token="NOT_A_TOKEN")
        self.assertNotIsInstance(caught.exception, ValueError)
        self.assertIn("--next-token", str(caught.exception))

    def test_token_carrying_a_negative_offset_is_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            _paging.slice_items([1, 2, 3], next_token=_paging.encode_token(-1))

    def test_non_numeric_max_items_is_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            _paging.slice_items([1, 2, 3], max_items="lots")

    def test_zero_max_items_is_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            _paging.slice_items([1, 2, 3], max_items=0)

    def test_connector_operation_list_rejects_a_bad_token_cleanly(self):
        recorder = ConnectorOperationTests._Recorder({"value": []})
        with mock.patch.object(custom, "_client_from_target", return_value=(recorder, {"kind": "local"})):
            with self.assertRaises(InvalidArgumentValueError):
                custom.connector_operation_list(None, "/serviceProviders/serviceBus", next_token="NOT_A_TOKEN")

    def test_runtime_client_page_items_shares_the_same_rejection(self):
        with self.assertRaises(InvalidArgumentValueError):
            _runtime_client.page_items([1, 2, 3], next_token="NOT_A_TOKEN")

    def test_tokens_are_interchangeable_across_the_two_catalog_paths(self):
        # One implementation backs both paths now; this fails the moment either one
        # grows a private copy again.
        items = list(range(10))
        _, token = _runtime_client.page_items(items, max_items=4)
        page, _ = _managed_api.slice_items(items, next_token=token, max_items=4)
        self.assertEqual(page, [4, 5, 6, 7])


class ManagedOperationKindFilterTests(unittest.TestCase):
    """--kind must mean the same thing on both operation list commands."""

    @staticmethod
    def _unclassifiable():
        return [{"name": "alpha", "properties": {}}, {"name": "beta", "properties": {}}]

    def test_kind_filter_does_not_fall_back_to_the_unfiltered_list(self):
        # The managed path used to return every operation when the kind filter matched
        # nothing, so --kind trigger answered with actions while the built-in command
        # answered with an empty page for the same request.
        filtered = _managed_api._filter_operations(self._unclassifiable(), "trigger", None)
        self.assertEqual(filtered, [])

    def test_empty_kind_result_matches_the_builtin_command(self):
        payload = {"value": [{"name": "alpha", "properties": {"operationType": "ServiceProvider"}}]}
        recorder = ConnectorOperationTests._Recorder(payload)
        with mock.patch.object(custom, "_client_from_target", return_value=(recorder, {"kind": "local"})):
            builtin = custom.connector_operation_list(None, "/serviceProviders/serviceBus", kind="trigger")
        managed = _managed_api._filter_operations(payload["value"], "trigger", None)
        self.assertEqual(builtin["value"], [])
        self.assertEqual(managed, [])


class ConnectorOperationOutputShapeTests(unittest.TestCase):
    """The response is an explicit contract, not a copy of whatever the runtime sent."""

    EXPECTED_KEYS = {"connector", "kind", "value", "nextContinuationToken"}

    def test_upstream_payload_fields_are_not_echoed(self):
        payload = {
            "value": [],
            "skipToken": None,
            "nextLink": "https://example.invalid/next",
            "somethingTheRuntimeAddedLater": {"a": 1},
        }
        recorder = ConnectorOperationTests._Recorder(payload)
        with mock.patch.object(custom, "_client_from_target", return_value=(recorder, {"kind": "local"})):
            result = custom.connector_operation_list(None, "/serviceProviders/serviceBus")
        self.assertEqual(set(result), self.EXPECTED_KEYS)

    def test_shape_is_stable_when_paging(self):
        recorder = ConnectorOperationTests._Recorder({"value": [{"name": str(i)} for i in range(5)], "skipToken": "x"})
        with mock.patch.object(custom, "_client_from_target", return_value=(recorder, {"kind": "local"})):
            result = custom.connector_operation_list(None, "/serviceProviders/serviceBus", max_items=2)
        self.assertEqual(set(result), self.EXPECTED_KEYS)
        self.assertIsNotNone(result["nextContinuationToken"])


class OAuthConsentProtocolTests(unittest.TestCase):
    """The pure protocol pieces of the consent leg, with no socket or browser."""

    def test_consent_request_carries_the_redirect_and_principal(self):
        body = _oauth_consent.build_consent_request(
            "http://127.0.0.1:9/callback", "object-1", "tenant-1")
        self.assertEqual(body, {"parameters": [{
            "parameterName": "token",
            "redirectUrl": "http://127.0.0.1:9/callback",
            "objectId": "object-1",
            "tenantId": "tenant-1",
        }]})

    def test_link_is_preferred_over_first_party_login_uri(self):
        payload = {"value": [{"link": "https://c/login?d=1",
                              "firstPartyLoginUri": "https://c/firstPartyLogin?d=1"}]}
        self.assertEqual(_oauth_consent.extract_consent_link(payload), "https://c/login?d=1")

    def test_first_party_uri_is_used_when_link_is_absent(self):
        payload = {"value": [{"firstPartyLoginUri": "https://c/firstPartyLogin?d=1"}]}
        self.assertEqual(_oauth_consent.extract_consent_link(payload),
                         "https://c/firstPartyLogin?d=1")

    def test_empty_consent_response_is_an_internal_error_not_a_crash(self):
        for payload in ({}, {"value": []}, {"value": [{}]}):
            with self.subTest(payload=payload):
                with self.assertRaises(CLIInternalError):
                    _oauth_consent.extract_consent_link(payload)

    def test_callback_without_a_code_means_consent_completed_server_side(self):
        # Proven live against office365: the consent service redeems the
        # authorization code itself and redirects here with a bare GET.
        self.assertEqual(_oauth_consent.interpret_callback({}), ("server_side", None))

    def test_callback_with_a_code_is_confirmed(self):
        self.assertEqual(_oauth_consent.interpret_callback({"code": "abc"}), ("code", "abc"))

    def test_callback_error_prefers_the_description(self):
        outcome, detail = _oauth_consent.interpret_callback(
            {"error": "access_denied", "error_description": "user refused"})
        self.assertEqual(outcome, "error")
        self.assertEqual(detail, "user refused")

    def test_callback_error_without_description_falls_back_to_the_code(self):
        self.assertEqual(_oauth_consent.interpret_callback({"error": "access_denied"}),
                         ("error", "access_denied"))


class OAuthConsentFlowTests(unittest.TestCase):
    """The orchestration, with a stub listener standing in for the browser."""

    class _StubListener:
        def __init__(self, result, port=9999):
            self.redirect_url = "http://127.0.0.1:{}/callback".format(port)
            self._result = result
            self.stopped = False

        def wait(self, _timeout):
            return self._result

        def stop(self):
            self.stopped = True

    def _arm(self, calls, link="https://consent/login?data=x"):
        def _sender(method, resource_id, payload=None):
            calls.append((method, resource_id, payload))
            if resource_id.endswith("/listConsentLinks"):
                return {"value": [{"link": link, "status": "Unauthenticated"}]}
            return {}
        return _sender

    def test_server_side_consent_does_not_call_confirm_consent_code(self):
        calls = []
        result = _oauth_consent.run_consent_flow(
            "/c", "object-1", "tenant-1", self._arm(calls), no_browser=True,
            listener=self._StubListener({"outcome": "server_side", "detail": None}))
        self.assertEqual(result, {"confirmed": False})
        self.assertEqual([resource for _, resource, _ in calls], ["/c/listConsentLinks"])

    def test_a_returned_code_is_confirmed_with_the_principal(self):
        calls = []
        result = _oauth_consent.run_consent_flow(
            "/c", "object-1", "tenant-1", self._arm(calls), no_browser=True,
            listener=self._StubListener({"outcome": "code", "detail": "the-code"}))
        self.assertEqual(result, {"confirmed": True})
        confirm = [c for c in calls if c[1].endswith("/confirmConsentCode")]
        self.assertEqual(len(confirm), 1)
        self.assertEqual(confirm[0][2],
                         {"code": "the-code", "objectId": "object-1", "tenantId": "tenant-1"})

    def test_declined_consent_raises_and_never_confirms(self):
        calls = []
        with self.assertRaises(ValidationError) as ctx:
            _oauth_consent.run_consent_flow(
                "/c", "object-1", "tenant-1", self._arm(calls), no_browser=True,
                listener=self._StubListener({"outcome": "error", "detail": "user refused"}))
        self.assertIn("user refused", str(ctx.exception))
        self.assertNotIn("/c/confirmConsentCode", [resource for _, resource, _ in calls])

    def test_timeout_names_the_flag_that_extends_it(self):
        with self.assertRaises(ValidationError) as ctx:
            _oauth_consent.run_consent_flow(
                "/c", "object-1", "tenant-1", self._arm([]), no_browser=True, timeout=7,
                listener=self._StubListener(None))
        message = str(ctx.exception)
        self.assertIn("--consent-timeout", message)
        self.assertIn("7s", message)
        self.assertNotIn("removed", message)

    def test_no_browser_suppresses_the_launch_but_still_waits(self):
        opened = []
        _oauth_consent.run_consent_flow(
            "/c", "o", "t", self._arm([]), no_browser=True,
            browser_opener=lambda url: opened.append(url) or True,
            listener=self._StubListener({"outcome": "server_side", "detail": None}))
        self.assertEqual(opened, [])

    def test_browser_is_launched_with_the_consent_link_by_default(self):
        opened = []
        _oauth_consent.run_consent_flow(
            "/c", "o", "t", self._arm([], link="https://consent/login?data=zz"),
            browser_opener=lambda url: opened.append(url) or True,
            listener=self._StubListener({"outcome": "server_side", "detail": None}))
        self.assertEqual(opened, ["https://consent/login?data=zz"])

    def test_a_browser_that_will_not_open_is_not_fatal(self):
        result = _oauth_consent.run_consent_flow(
            "/c", "o", "t", self._arm([]),
            browser_opener=lambda _url: False,
            listener=self._StubListener({"outcome": "server_side", "detail": None}))
        self.assertEqual(result, {"confirmed": False})


class OAuthConnectedVerificationTests(unittest.TestCase):
    def test_connected_status_passes(self):
        payload = {"properties": {"overallStatus": "Connected",
                                  "statuses": [{"status": "Connected"}]}}
        self.assertTrue(_oauth_consent.verify_connected(payload, "conn"))

    def test_status_comparison_is_case_insensitive(self):
        payload = {"properties": {"statuses": [{"status": "connected"}]}}
        self.assertTrue(_oauth_consent.verify_connected(payload, "conn"))

    def test_unauthenticated_connection_is_rejected_with_the_service_message(self):
        payload = {"properties": {"overallStatus": "Error", "statuses": [
            {"status": "Error", "error": {"code": "Unauthenticated",
                                          "message": "This connection is not authenticated."}}]}}
        with self.assertRaises(ValidationError) as ctx:
            _oauth_consent.verify_connected(payload, "conn")
        message = str(ctx.exception)
        self.assertIn("not authenticated", message)
        self.assertNotIn("removed", message)


class OAuthCreateIntegrationTests(unittest.TestCase):
    """create_managed_connection's oauth path, including the unwind contract."""

    CONNECTOR = "/subscriptions/s/providers/Microsoft.Web/locations/eastus/managedApis/office365"

    @staticmethod
    def _identity_sender(*_args, **_kwargs):
        return _FakeResponse({"identity": {"type": "SystemAssigned", "principalId": "object-1"}})

    def _run(self, consent_runner, connected=True):
        sent = []
        seen_put = {"done": False}

        def _arm_sender(_ctx, method, url, **_kwargs):
            sent.append((method, url))
            if method == "GET" and "/accessPolicies?" in url:
                return _FakeResponse({"value": []})
            if method == "GET" and "/accessPolicies/" in url:
                raise HTTPError("Not Found", _FakeResponse(status_code=404))
            if method == "GET":
                # The pre-create existence probe must report "absent", or the
                # command refuses before creating anything.
                if not seen_put["done"]:
                    raise HTTPError("Not Found", _FakeResponse(status_code=404))
                status = "Connected" if connected else "Error"
                return _FakeResponse({
                    "id": "/c", "name": "conn", "kind": "V2", "location": "eastus",
                    "properties": {"overallStatus": status, "statuses": [{"status": status}]}})
            if method == "PUT" and "/accessPolicies/" not in url:
                seen_put["done"] = True
            return _FakeResponse({"id": "/c", "name": "conn", "kind": "V2"})

        with _fake_azure_context():
            result = _managed_connection.create_managed_connection(
                _FakeCmd(), "rg", "app", "conn", self.CONNECTOR, "eastus", "oauth",
                identity_sender=self._identity_sender, arm_sender=_arm_sender,
                vfs_client=_RecordingVfsClient({}), consent_runner=consent_runner,
                consent_principal={"objectId": "caller-1", "tenantId": "tenant-1"})
        return result, sent

    def test_consent_is_requested_as_the_caller_not_the_app_identity(self):
        """A live run proved the service rejects any other objectId.

        'The client can only request consent links for their own identity' --
        passing the app's managed identity here fails with InvalidConsentLinkParameter,
        so the consent principal and the access-policy principal must stay distinct.
        """
        seen = {}

        def _runner(*_args, **kwargs):
            seen.update(kwargs)
            return {"confirmed": False}

        result, _ = self._run(_runner)
        self.assertEqual(seen["object_id"], "caller-1")
        self.assertNotEqual(seen["object_id"], "object-1")
        # ...while the access policy still names the app's managed identity.
        self.assertEqual(result["accessPolicy"]["principal"]["objectId"], "object-1")

    def test_oauth_is_no_longer_refused(self):
        result, _ = self._run(lambda *a, **k: {"confirmed": False})
        self.assertEqual(result["authMode"], "oauth")
        self.assertEqual(result["consent"], {"confirmed": False})

    def test_consent_runs_before_the_access_policy_is_written(self):
        order = []

        def _runner(*_args, **kwargs):
            order.append("consent")
            self.assertFalse(kwargs["no_browser"])
            return {"confirmed": False}

        _, sent = self._run(_runner)
        for method, url in sent:
            if method == "PUT" and "/accessPolicies/" in url:
                order.append("acl")
        self.assertEqual(order, ["consent", "acl"])

    def test_declined_consent_fails_without_claiming_compensation_ownership(self):
        def _runner(*_args, **_kwargs):
            raise ValidationError("Consent was not granted: user refused")

        with self.assertRaises(ValidationError):
            self._run(_runner)

    def test_declined_consent_does_not_delete_an_unconditionally_upserted_connection(self):
        deleted = []

        def _runner(*_args, **_kwargs):
            raise ValidationError("declined")

        sent = []
        seen_put = {"done": False}

        def _arm_sender(_ctx, method, url, **_kwargs):
            sent.append((method, url))
            if method == "DELETE":
                deleted.append(url)
                return _FakeResponse({})
            if method == "GET" and not seen_put["done"]:
                raise HTTPError("Not Found", _FakeResponse(status_code=404))
            if method == "PUT":
                seen_put["done"] = True
            return _FakeResponse({"id": "/c", "name": "conn", "kind": "V2"})

        with self.assertRaises(ValidationError), _fake_azure_context():
            _managed_connection.create_managed_connection(
                _FakeCmd(), "rg", "app", "conn", self.CONNECTOR, "eastus", "oauth",
                identity_sender=self._identity_sender, arm_sender=_arm_sender,
                vfs_client=_RecordingVfsClient({}), consent_runner=_runner,
                consent_principal={"objectId": "caller-1", "tenantId": "tenant-1"})
        self.assertEqual(deleted, [])

    def test_a_connection_that_never_connects_reports_the_original_failure(self):
        with self.assertRaises(ValidationError) as ctx:
            self._run(lambda *a, **k: {"confirmed": False}, connected=False)
        self.assertIn("did not reach a connected state", str(ctx.exception))

    def test_non_oauth_policy_failure_does_not_authorize_compensating_delete(self):
        sent = []
        seen_put = {"done": False}

        def _arm_sender(_ctx, method, url, **_kwargs):
            sent.append((method, url))
            if method == "PUT" and "/accessPolicies/" in url:
                raise ValidationError("policy write failed")
            if method == "GET" and "/accessPolicies?" in url:
                return _FakeResponse({"value": []})
            if method == "GET" and not seen_put["done"]:
                raise HTTPError("Not Found", _FakeResponse(status_code=404))
            if method == "PUT":
                seen_put["done"] = True
            return _FakeResponse({"id": "/c", "name": "conn", "kind": "V2"})

        with self.assertRaises(ValidationError), _fake_azure_context():
            _managed_connection.create_managed_connection(
                _FakeCmd(), "rg", "app", "conn", self.CONNECTOR, "eastus", "raw",
                parameter_set="keyBasedAuth",
                identity_sender=self._identity_sender, arm_sender=_arm_sender,
                vfs_client=_RecordingVfsClient({}))
        self.assertEqual([m for m, _ in sent if m == "DELETE"], [])


class ConsentPromptTests(unittest.TestCase):
    """The waiting message distinguishes 'did not try' from 'tried and failed'.

    A live --no-browser run reported "Could not open a browser", which reads as a
    malfunction when the launch was suppressed on purpose.
    """

    def _messages(self, **kwargs):
        with mock.patch("knack.log.get_logger") as get_logger:
            logger = mock.MagicMock()
            get_logger.return_value = logger
            _oauth_consent.emit_consent_prompt("https://consent/login", **kwargs)
        return " ".join(str(call[0][0]) for call in logger.warning.call_args_list)

    def test_no_browser_does_not_claim_a_failure(self):
        message = self._messages(opened=False, attempted=False)
        self.assertNotIn("Could not open", message)
        self.assertIn("Open this link", message)

    def test_a_genuine_launch_failure_still_says_so(self):
        self.assertIn("Could not open", self._messages(opened=False, attempted=True))

    def test_a_successful_launch_says_it_opened(self):
        self.assertIn("Opened the consent page", self._messages(opened=True))


class ConsentPrincipalTests(unittest.TestCase):
    """Resolving the caller's object id from the access token."""

    @staticmethod
    def _token(claims):
        import base64
        payload = base64.urlsafe_b64encode(json.dumps(claims).encode("utf-8")).decode("utf-8")
        return "header.{}.signature".format(payload.rstrip("="))

    def test_claims_survive_stripped_base64_padding(self):
        # JWT payloads are unpadded base64url; feeding that to b64decode raw
        # raises "Incorrect padding" on most real tokens.
        claims = _managed_connection._jwt_claims(self._token({"oid": "abc", "tid": "t"}))
        self.assertEqual(claims["oid"], "abc")

    def test_caller_object_id_is_used_not_the_app_identity(self):
        principal = _managed_connection._resolve_consent_principal(
            _FakeCmd(), claims_reader=lambda _cmd: {"oid": "caller-1", "tid": "tenant-9"})
        self.assertEqual(principal, {"objectId": "caller-1", "tenantId": "tenant-9"})

    def test_a_token_without_an_object_id_is_a_clear_error(self):
        with self.assertRaises(CLIInternalError) as ctx:
            _managed_connection._resolve_consent_principal(
                _FakeCmd(), claims_reader=lambda _cmd: {"tid": "t"})
        self.assertIn("az login", str(ctx.exception))

    def test_a_malformed_token_does_not_raise_a_traceback(self):
        with self.assertRaises(CLIInternalError):
            _managed_connection._jwt_claims("not-a-jwt")

    def test_tenant_falls_back_to_the_profile_when_absent_from_claims(self):
        with _fake_azure_context(tenant_id="tenant-from-profile"):
            principal = _managed_connection._resolve_consent_principal(
                _FakeCmd(), claims_reader=lambda _cmd: {"oid": "caller-1"})
        self.assertEqual(principal["tenantId"], "tenant-from-profile")


class OAuthFlagScopeTests(unittest.TestCase):
    """--no-browser and --consent-timeout are rejected where they cannot apply.

    Silently ignoring them would let a user believe a headless run was configured
    when it was not.
    """

    def test_no_browser_is_rejected_on_a_local_project_connection(self):
        with self.assertRaises(MutuallyExclusiveArgumentError) as ctx:
            custom.connection_create(_FakeCmd(), "conn", "serviceBus", no_browser=True)
        self.assertIn("--no-browser", str(ctx.exception))
        self.assertIn("--managed-api", str(ctx.exception))

    def test_consent_timeout_is_rejected_on_a_local_project_connection(self):
        with self.assertRaises(MutuallyExclusiveArgumentError) as ctx:
            custom.connection_create(_FakeCmd(), "conn", "serviceBus", consent_timeout=60)
        self.assertIn("--consent-timeout", str(ctx.exception))

    def test_no_browser_is_rejected_for_a_managed_mode_without_consent(self):
        with self.assertRaises(MutuallyExclusiveArgumentError) as ctx:
            custom.connection_create(
                _FakeCmd(), "conn", "office365", managed_api=True, resource_group_name="rg",
                connection_name="c", location="eastus", auth_mode="managed-identity",
                no_browser=True)
        self.assertIn("--no-browser", str(ctx.exception))
        self.assertIn("--auth-mode oauth", str(ctx.exception))

    def test_consent_timeout_is_rejected_for_a_managed_mode_without_consent(self):
        with self.assertRaises(MutuallyExclusiveArgumentError) as ctx:
            custom.connection_create(
                _FakeCmd(), "conn", "office365", managed_api=True, resource_group_name="rg",
                connection_name="c", location="eastus", auth_mode="raw",
                consent_timeout=60)
        self.assertIn("--consent-timeout", str(ctx.exception))
        self.assertIn("--auth-mode oauth", str(ctx.exception))


class OAuthListenerTests(unittest.TestCase):
    """The loopback listener, exercised over a real socket."""

    def test_listener_captures_a_bare_callback(self):
        import urllib.request
        with _oauth_consent.ConsentListener() as listener:
            urllib.request.urlopen(listener.redirect_url, timeout=5).read()
            self.assertEqual(listener.wait(5), {"outcome": "server_side", "detail": None})

    def test_listener_captures_a_code(self):
        import urllib.request
        with _oauth_consent.ConsentListener() as listener:
            urllib.request.urlopen(listener.redirect_url + "?code=xyz", timeout=5).read()
            self.assertEqual(listener.wait(5), {"outcome": "code", "detail": "xyz"})

    def test_listener_binds_ipv4_loopback_explicitly(self):
        # 'localhost' resolves to ::1 first on Windows, which would leave a
        # v4-only listener unreachable by the browser.
        with _oauth_consent.ConsentListener() as listener:
            self.assertTrue(listener.redirect_url.startswith("http://127.0.0.1:"))

    def test_each_listener_takes_a_free_port(self):
        with _oauth_consent.ConsentListener() as a, _oauth_consent.ConsentListener() as b:
            self.assertNotEqual(a.port, b.port)

    def test_wait_returns_none_when_nothing_arrives(self):
        with _oauth_consent.ConsentListener() as listener:
            self.assertIsNone(listener.wait(0.2))


class _AzuriteState:
    """Swap _local.STATE_DIR for a scratch directory so records never touch ~/."""

    def __init__(self, name):
        self.root = _workspace(name)
        self.state = self.root / "state"
        self.state.mkdir()
        self._previous = None

    def __enter__(self):
        self._previous = _local.STATE_DIR
        _local.STATE_DIR = str(self.state)
        return self

    def __exit__(self, *exc):
        _local.STATE_DIR = self._previous
        return False


def _project(root, name, storage=None):
    project = root / name
    project.mkdir()
    (project / "host.json").write_text("{}", encoding="utf-8")
    if storage is not None:
        (project / "local.settings.json").write_text(
            json.dumps({"IsEncrypted": False, "Values": {"AzureWebJobsStorage": storage}}), encoding="utf-8")
    return project


class AzuriteProbeTests(unittest.TestCase):
    def test_non_azurite_service_on_the_blob_port_is_not_reported_as_azurite(self):
        # "Something is listening on 10000" is a weaker claim than "Azurite is
        # running". If an unrelated service held the port we would skip starting the
        # emulator and the runtime would then fail against an endpoint that is not
        # storage at all, which is far harder to diagnose than a port conflict.
        response = mock.MagicMock()
        response.headers = {"Server": "nginx/1.25.3"}
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=False)
        with mock.patch.object(_local, "urlopen", return_value=response):
            self.assertIsNone(_local.probe_azurite(timeout=0.1))

    def test_azurite_banner_is_recognised_even_though_the_status_is_an_error(self):
        # Azurite answers the blob root with 400. Keying off the status code instead
        # of the Server header would report a healthy emulator as absent.
        error = _local.HTTPURLError(
            "http://127.0.0.1:10000/", 400, "Bad Request", {"Server": "Azurite-Blob/3.29.0"}, None)
        with mock.patch.object(_local, "urlopen", side_effect=error):
            self.assertEqual(_local.probe_azurite(timeout=0.1), "Azurite-Blob/3.29.0")

    def test_transport_failure_reads_as_absent_rather_than_raising(self):
        with mock.patch.object(_local, "urlopen", side_effect=OSError("refused")):
            self.assertIsNone(_local.probe_azurite(timeout=0.1))


class EnsureAzuriteTests(unittest.TestCase):
    def setUp(self):
        # probe_azurite is patched per test; the real urlopen must never be reached.
        self.started = []

    def _starter(self, server="Azurite-Blob/3.29.0"):
        def _start(azurite_path=None, timeout=None, prober=None):
            self.started.append({"path": azurite_path, "timeout": timeout})
            return {"pid": 4321, "server": server, "workspace": "ws", "logPath": "log"}
        return _start

    def test_real_storage_account_means_no_emulator_and_no_noise(self):
        with _AzuriteState("azurite-real-storage") as state:
            project = _project(state.root, "orders", storage="DefaultEndpointsProtocol=https;AccountName=x;AccountKey=y==")
            entry = _local.ensure_azurite(str(project), starter=self._starter(), prober=lambda: None)
        self.assertIsNone(entry, "a project pointed at a real storage account must not be told about Azurite")
        self.assertEqual(self.started, [])

    def test_development_storage_starts_the_emulator(self):
        with _AzuriteState("azurite-starts") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            with mock.patch.object(_local, "find_tool", return_value=("/tools/azurite", "managed")):
                with mock.patch.object(_local, "_port_free", return_value=True):
                    entry = _local.ensure_azurite(str(project), starter=self._starter(), prober=lambda: None, timeout=7)
        self.assertEqual(entry["state"], "started")
        self.assertTrue(entry["startedByCli"])
        self.assertEqual(entry["pid"], 4321)
        self.assertEqual(self.started, [{"path": "/tools/azurite", "timeout": 7}])

    def test_an_emulator_already_serving_is_reused_not_duplicated(self):
        # Azurite binds fixed ports, so a second instance cannot start. Reuse is the
        # only correct behaviour, and an emulator the developer owns must not be
        # claimed by the CLI or stop would later kill it.
        with _AzuriteState("azurite-reuse") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            with mock.patch.object(_local, "find_tool", return_value=("/tools/azurite", "managed")):
                entry = _local.ensure_azurite(str(project), starter=self._starter(), prober=lambda: "Azurite-Blob/3.29.0")
        self.assertEqual(entry["state"], "already-running")
        self.assertFalse(entry["startedByCli"])
        self.assertEqual(self.started, [], "a running emulator must not be started a second time")

    def test_reusing_an_emulator_this_cli_started_still_reports_it_as_owned(self):
        # Observed live: a second 'runtime start' said startedByCli=false about the
        # emulator the first start had launched, while 'runtime show' said true for
        # that same emulator. One name must not carry two meanings -- a developer
        # reading the second start would conclude nothing would stop it, moments
        # before 'runtime stop' did exactly that.
        with _AzuriteState("azurite-reuse-owned") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            (state.state / "azurite.json").write_text(
                json.dumps({"pid": 4321, "processCreateTimeUtc": "2026-01-01T00:00:00Z"}), encoding="utf-8")
            with mock.patch.object(_local, "find_tool", return_value=("/tools/azurite", "managed")):
                with mock.patch.object(_local, "_record_matches", return_value=True):
                    entry = _local.ensure_azurite(str(project), starter=self._starter(), prober=lambda: "Azurite-Blob/3.29.0")
                    view = _local._azurite_view()
        self.assertEqual(entry["state"], "already-running")
        self.assertTrue(entry["startedByCli"], "an emulator this CLI started is owned by it, however it is reached")
        self.assertEqual(entry["startedByCli"], view["startedByCli"],
                         "start and show must agree about who owns the emulator")
        self.assertEqual(self.started, [])

    def test_no_azurite_flag_suppresses_the_start(self):
        with _AzuriteState("azurite-optout") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            with mock.patch.object(_local, "find_tool", return_value=("/tools/azurite", "managed")):
                with mock.patch.object(_local, "_port_free", return_value=True):
                    entry = _local.ensure_azurite(str(project), enable=False, starter=self._starter(), prober=lambda: None)
        self.assertEqual(entry["state"], "skipped")
        self.assertEqual(self.started, [])

    def test_unknown_storage_configuration_reports_rather_than_guesses(self):
        # Spawning a background server process on a project whose storage setting
        # could not be read is a bigger imposition than saying so.
        with _AzuriteState("azurite-unknown") as state:
            project = _project(state.root, "orders")
            with mock.patch.object(_local, "find_tool", return_value=("/tools/azurite", "managed")):
                with mock.patch.object(_local, "_port_free", return_value=True):
                    entry = _local.ensure_azurite(str(project), starter=self._starter(), prober=lambda: None)
        self.assertEqual(entry["state"], "not-started")
        self.assertEqual(entry["severity"], "info")
        self.assertEqual(self.started, [])

    def test_missing_azurite_still_only_warns(self):
        with _AzuriteState("azurite-missing") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            with mock.patch.object(_local, "find_tool", return_value=(None, None)):
                entry = _local.ensure_azurite(str(project), starter=self._starter(), prober=lambda: None)
        self.assertEqual(entry["state"], "missing")
        self.assertEqual(entry["severity"], "warning")
        self.assertIn("dependency install", entry["remediation"])

    def test_foreign_process_on_the_ports_is_a_named_conflict(self):
        with _AzuriteState("azurite-conflict") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            with mock.patch.object(_local, "find_tool", return_value=("/tools/azurite", "managed")):
                with mock.patch.object(_local, "_port_free", side_effect=lambda port: port != 10000):
                    entry = _local.ensure_azurite(str(project), starter=self._starter(), prober=lambda: None)
        self.assertEqual(entry["state"], "port-conflict")
        self.assertEqual(entry["portsInUse"], [10000])
        self.assertIn("10000", entry["remediation"])
        self.assertEqual(self.started, [])

    def test_a_launch_that_never_answers_is_failed_not_started(self):
        with _AzuriteState("azurite-never-ready") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            with mock.patch.object(_local, "find_tool", return_value=("/tools/azurite", "managed")):
                with mock.patch.object(_local, "_port_free", return_value=True):
                    entry = _local.ensure_azurite(str(project), starter=self._starter(server=None), prober=lambda: None)
        self.assertEqual(entry["state"], "failed", "a process that spawned but never served is not a started emulator")
        self.assertIn("did not answer", entry["remediation"])


class AzuriteLifecycleTests(unittest.TestCase):
    def test_a_dead_process_is_not_rescued_by_another_emulators_banner(self):
        # Observed live: when the ports are already bound the spawned Azurite exits at
        # once, but the probe still sees the banner of the emulator that owns the
        # port. Accepting that wrote a state record naming a dead pid and told the
        # caller it had started something.
        with mock.patch.object(_local, "_is_running", return_value=False):
            self.assertIsNone(_local._wait_for_azurite(4321, 5, prober=lambda: "Azurite-Blob/3.36.0"))

    def test_a_live_process_that_answers_is_accepted(self):
        with mock.patch.object(_local, "_is_running", return_value=True):
            self.assertEqual(_local._wait_for_azurite(4321, 5, prober=lambda: "Azurite-Blob/3.36.0"),
                             "Azurite-Blob/3.36.0")

    def test_a_failed_launch_leaves_no_state_record_behind(self):
        with _AzuriteState("azurite-failed-launch") as state:
            proc = mock.Mock(pid=4321)
            with mock.patch.object(_local.subprocess, "Popen", return_value=proc), \
                    mock.patch.object(_local, "process_create_time_utc", return_value=None), \
                    mock.patch.object(_local, "_is_running", return_value=False):
                record = _local.start_azurite(azurite_path="/tools/azurite", timeout=0,
                                              prober=lambda: "Azurite-Blob/3.36.0")
            self.assertIsNone(record["server"])
            self.assertFalse((state.state / "azurite.json").exists(),
                             "a launch that never served must not leave a record stop would act on")

    def test_stop_never_touches_an_emulator_the_cli_did_not_start(self):
        with _AzuriteState("azurite-stop-foreign"):
            with mock.patch.object(_local, "_terminate", side_effect=AssertionError("must not terminate")):
                result = _local.stop_azurite()
        self.assertFalse(result["stopped"])
        self.assertEqual(result["reason"], "not-started-by-cli")

    def test_stop_refuses_when_the_recorded_identity_no_longer_matches(self):
        # A recycled pid would otherwise make the CLI kill an unrelated process.
        with _AzuriteState("azurite-stop-stale") as state:
            (state.state / "azurite.json").write_text(
                json.dumps({"pid": 999999, "processCreateTimeUtc": "2020-01-01T00:00:00Z"}), encoding="utf-8")
            with mock.patch.object(_local, "_record_matches", return_value=False):
                with mock.patch.object(_local, "_terminate", side_effect=AssertionError("must not terminate")):
                    result = _local.stop_azurite()
            self.assertFalse((state.state / "azurite.json").exists(), "a stale record must be cleared")
        self.assertEqual(result["reason"], "not-running")

    def test_stop_terminates_the_emulator_the_cli_started(self):
        with _AzuriteState("azurite-stop-own") as state:
            (state.state / "azurite.json").write_text(
                json.dumps({"pid": 4321, "processCreateTimeUtc": "2026-01-01T00:00:00Z", "ports": _local.AZURITE_PORTS}),
                encoding="utf-8")
            terminated = set()
            with mock.patch.object(_local, "_record_matches", side_effect=lambda record: bool(
                    record.get("pid") and record["pid"] not in terminated)):
                with mock.patch.object(_local, "_terminate",
                                       side_effect=lambda pid, expected=None: terminated.add(pid)) as killed:
                    with mock.patch.object(_local, "probe_azurite", return_value=None):
                        result = _local.stop_azurite()
            self.assertFalse((state.state / "azurite.json").exists())
        killed.assert_called_once_with(4321, expected="2026-01-01T00:00:00Z")
        self.assertTrue(result["stopped"])

    def test_stop_reports_failure_when_the_emulator_is_still_answering(self):
        # A kill that returns cleanly is not proof the emulator is gone: on Windows the
        # .cmd shim dies while the node process it spawned keeps the ports bound.
        with _AzuriteState("azurite-stop-orphan") as state:
            (state.state / "azurite.json").write_text(
                json.dumps({"pid": 4321, "processCreateTimeUtc": "2026-01-01T00:00:00Z"}), encoding="utf-8")
            with mock.patch.object(_local, "_record_matches", return_value=True):
                with mock.patch.object(_local, "_terminate"):
                    with mock.patch.object(_local, "probe_azurite", return_value="Azurite-Blob/3.36.0"):
                        result = _local.stop_azurite()
        self.assertFalse(result["stopped"], "an emulator still answering has not been stopped")
        self.assertEqual(result["reason"], "still-serving")

    def test_terminate_kills_the_child_the_cmd_shim_spawned(self):
        # The recorded pid is the .cmd shim; the server is its node child. Killing only
        # the shim left the ports bound with the parent gone.
        if os.name != "nt":
            self.skipTest("process-tree termination is a Windows concern")
        created = "2026-10-06T15:00:00.1234560Z"
        snapshot = [(4321, 1, created), (5555, 4321, created),
                    (6666, 5555, created), (7777, 1, created)]
        stopped = []
        with mock.patch.object(_local, "_process_tree_snapshot", return_value=snapshot), \
                mock.patch.object(_local, "process_create_time_utc", return_value=created), \
                mock.patch.object(_local, "_is_running", return_value=True), \
                mock.patch.object(_local, "_stop_process",
                                  side_effect=lambda pid, check, expected=None: stopped.append(pid)):
            _local._terminate(4321, expected=created)
        self.assertEqual(stopped[0], 4321, "the recorded process must be stopped first, while the tree is known")
        self.assertEqual(sorted(stopped), [4321, 5555, 6666])
        self.assertNotIn(7777, stopped, "unrelated processes must never be touched")

    def test_a_recycled_pid_cycle_does_not_spin_forever(self):
        # Windows recycles pids, so a snapshot can contain a parent chain that loops
        # back on itself. Walking it without tracking visited pids never terminates --
        # in code whose job is to kill processes.
        if os.name != "nt":
            self.skipTest("process-tree termination is a Windows concern")
        created = "2026-10-06T15:00:00.1234560Z"
        snapshot = [(200, 100, created), (100, 200, created)]
        stopped = []
        with mock.patch.object(_local, "_process_tree_snapshot", return_value=snapshot), \
                mock.patch.object(_local, "process_create_time_utc", return_value=created), \
                mock.patch.object(_local, "_is_running", return_value=True), \
                mock.patch.object(_local, "_stop_process",
                                  side_effect=lambda pid, check, expected=None: stopped.append(pid)):
            _local._terminate(100, expected=created)
        self.assertEqual(sorted(stopped), [100, 200])

    def test_runtime_stop_leaves_the_emulator_up_while_another_runtime_needs_it(self):
        # The emulator is shared. Releasing it with the first runtime would pull
        # storage out from under every other one still running.
        with _AzuriteState("azurite-shared") as state:
            (state.state / "azurite.json").write_text(
                json.dumps({"pid": 4321, "processCreateTimeUtc": "2026-01-01T00:00:00Z"}), encoding="utf-8")
            (state.state / "runtime-7071.json").write_text(
                json.dumps({"pid": 111, "processCreateTimeUtc": "2026-01-01T00:00:00Z", "port": 7071}), encoding="utf-8")
            (state.state / "runtime-7072.json").write_text(
                json.dumps({"pid": 222, "processCreateTimeUtc": "2026-01-01T00:00:00Z", "port": 7072}), encoding="utf-8")
            terminated = set()
            with mock.patch.object(_local, "_record_matches", side_effect=lambda record: bool(
                    record.get("pid") and record["pid"] not in terminated)):
                with mock.patch.object(_local, "_terminate",
                                       side_effect=lambda pid, expected=None: terminated.add(pid)) as killed:
                    result = _local.stop_runtime(port=7071)
            self.assertTrue((state.state / "azurite.json").exists(), "the emulator record must survive")
        self.assertEqual(result["azurite"], {"stopped": False, "reason": "runtimes-still-running", "ports": [7072]})
        self.assertEqual([call.args[0] for call in killed.call_args_list], [111])

    def test_runtime_stop_releases_the_emulator_once_nothing_is_left(self):
        with _AzuriteState("azurite-last-out") as state:
            (state.state / "azurite.json").write_text(
                json.dumps({"pid": 4321, "processCreateTimeUtc": "2026-01-01T00:00:00Z"}), encoding="utf-8")
            (state.state / "runtime-7071.json").write_text(
                json.dumps({"pid": 111, "processCreateTimeUtc": "2026-01-01T00:00:00Z", "port": 7071}), encoding="utf-8")
            terminated = set()
            with mock.patch.object(_local, "_record_matches", side_effect=lambda record: bool(
                    record.get("pid") and record["pid"] not in terminated)):
                with mock.patch.object(_local, "_terminate",
                                       side_effect=lambda pid, expected=None: terminated.add(pid)) as killed:
                    with mock.patch.object(_local, "probe_azurite", return_value=None):
                        result = _local.stop_runtime(port=7071)
            self.assertFalse((state.state / "azurite.json").exists())
        self.assertTrue(result["azurite"]["stopped"])
        self.assertEqual([call.args[0] for call in killed.call_args_list], [111, 4321])


class RuntimeStartAzuriteIntegrationTests(unittest.TestCase):
    def test_starting_a_development_storage_project_starts_the_emulator(self):
        with _AzuriteState("azurite-runtime-start") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            managed = state.root / "FuncCoreTools"
            managed.mkdir()
            executable = managed / ("func.cmd" if os.name == "nt" else "func")
            executable.write_text("", encoding="utf-8")
            if os.name != "nt":
                executable.chmod(0o755)
            azurite_dir = state.root / "Azurite"
            azurite_dir.mkdir()
            azurite_exe = azurite_dir / ("azurite.cmd" if os.name == "nt" else "azurite")
            azurite_exe.write_text("", encoding="utf-8")
            if os.name != "nt":
                azurite_exe.chmod(0o755)
            empty_path = state.root / "empty-path"
            empty_path.mkdir()

            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                free_port = probe.getsockname()[1]

            launched = {}

            def _fake_start(azurite_path=None, timeout=None, prober=None):
                launched["path"] = azurite_path
                return {"pid": 4321, "server": "Azurite-Blob/3.29.0", "workspace": "ws", "logPath": "log"}

            env = {"LA_DEPENDENCIES_PATH": str(state.root), "PATH": str(empty_path)}
            with mock.patch.dict(os.environ, env), \
                    mock.patch.object(_local, "probe_azurite", return_value=None), \
                    mock.patch.object(_local, "_port_free", return_value=True), \
                    mock.patch.object(_local, "start_azurite", side_effect=_fake_start), \
                    mock.patch.object(_local.subprocess, "Popen", return_value=_finished_host_process()):
                result = _local.start_runtime(None, str(project), port=free_port)

        self.assertEqual(Path(launched["path"]).parent, azurite_dir)
        entry = next(item for item in result["dependencies"] if item["kind"] == "azurite")
        self.assertEqual(entry["state"], "started")

    def test_no_azurite_is_honoured_by_runtime_start(self):
        with _AzuriteState("azurite-runtime-optout") as state:
            project = _project(state.root, "orders", storage="UseDevelopmentStorage=true")
            managed = state.root / "FuncCoreTools"
            managed.mkdir()
            executable = managed / ("func.cmd" if os.name == "nt" else "func")
            executable.write_text("", encoding="utf-8")
            if os.name != "nt":
                executable.chmod(0o755)
            empty_path = state.root / "empty-path"
            empty_path.mkdir()

            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                free_port = probe.getsockname()[1]

            env = {"LA_DEPENDENCIES_PATH": str(state.root), "PATH": str(empty_path)}
            with mock.patch.dict(os.environ, env):
                with mock.patch.object(_local, "probe_azurite", return_value=None):
                    with mock.patch.object(_local, "start_azurite", side_effect=AssertionError("--no-azurite must not start one")):
                        with mock.patch.object(_local.subprocess, "Popen", return_value=_finished_host_process()):
                            result = _local.start_runtime(None, str(project), port=free_port, no_azurite=True)

        entry = next(item for item in result["dependencies"] if item["kind"] == "azurite")
        self.assertEqual(entry["state"], "skipped")
