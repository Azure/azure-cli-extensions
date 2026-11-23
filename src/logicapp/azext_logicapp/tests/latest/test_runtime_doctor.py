# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from io import BytesIO
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import psutil
from knack.events import EVENT_CLI_POST_EXECUTE, EVENT_CLI_SUCCESSFUL_EXECUTE

from azext_logicapp import _context, _local, _runtime_doctor as doctor, _workflow, custom


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.state = self.root / "state"
        self.patch(_local, "STATE_DIR", str(self.state))
        self.patch(_context, "store_path", return_value=str(self.root / "contexts.json"))
        self.patch(_local, "bundle_install_root", return_value=str(self.root / "cache"))
        self.write("host.json", _workflow.HOST_JSON)
        self.write("local.settings.json", _workflow.LOCAL_SETTINGS_JSON)
        self.write("hello\\workflow.json" if os.name == "nt" else "hello/workflow.json",
                   _workflow.workflow_json("Stateful"))
        self.patch(doctor, "_port_listening", return_value="free")
        self.http = self.patch(doctor, "_http_probe", return_value={
            "reachable": True, "httpStatus": 400, "identity": "azurite", "service": "blob", "hostState": None})
        self.patch(_local, "find_tool", return_value=(None, "not-found"))
        self.patch(doctor.shutil, "which", return_value=None)
        self.run = self.patch(doctor.subprocess, "run",
                              side_effect=AssertionError("version probes must be explicitly stubbed"))
        self.patch(_local, "process_create_time_utc", return_value=None)

    def patch(self, target, name, *args, **kwargs):
        patcher = mock.patch.object(target, name, *args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def write(self, name, content):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content), encoding="utf-8")
        return path

    def report(self, **kwargs):
        return doctor.doctor_report(path=str(self.project), **kwargs)

    def row(self, report, check):
        return next(row for row in report["findings"] if row["check"] == check)

    def test_well_formed_project_has_passing_configuration_not_business_claim(self):
        result = self.report()
        self.assertEqual("pass", self.row(result, "configuration.workflow.0.structure")["status"])
        self.assertEqual("pass", self.row(result, "configuration.host-version")["status"])
        self.assertEqual("not-tested", result["businessBehavior"])
        self.assertTrue(result["readOnly"])
        self.assertEqual("unknown", self.row(result, "compatibility.tool-bundle")["status"])
        self.assertEqual("skipped", self.row(result, "host.status")["status"])

    def test_required_missing_tools_and_storage_have_actionable_failure(self):
        result = self.report()
        self.assertEqual(1, result["exitCode"])
        for check in ("tools.core-tools", "tools.node", "storage.blob", "storage.queue", "storage.table"):
            row = self.row(result, check)
            self.assertEqual("fail", row["status"])
            self.assertTrue(row["recommendation"])
        self.http.assert_not_called()

    def test_missing_malformed_and_nonobject_files_are_findings_without_values(self):
        secret = "PRIVATE-CONTENT-DO-NOT-PRINT"
        for name in ("host.json", "local.settings.json", os.path.join("hello", "workflow.json")):
            path = self.project / name
            original = path.read_text()
            for content in (None, '{"secret":"' + secret, "[]", '"' + secret + '"'):
                with self.subTest(name=name, content=content):
                    if content is None:
                        path.unlink()
                    else:
                        path.write_text(content, encoding="utf-8")
                    result = self.report()
                    self.assertEqual(1, result["exitCode"])
                    self.assertNotIn(secret, json.dumps(result))
                    self.assertNotIn("Traceback", json.dumps(result))
                    path.write_text(original, encoding="utf-8")

    def test_malformed_optional_files_do_not_become_empty_healthy_defaults(self):
        for name, check in (("connections.json", "configuration.connections"),
                            ("parameters.json", "configuration.parameters")):
            self.write(name, ["private"])
            result = self.report()
            self.assertEqual("fail", self.row(result, check)["status"])
            self.assertEqual(1, result["exitCode"])
            (self.project / name).unlink()

    def test_permission_and_size_failures_are_explicit(self):
        rows = []
        with mock.patch("builtins.open", side_effect=PermissionError("private content")):
            self.assertIsNone(doctor._read_json("unused", rows, "file"))
        self.assertEqual("fail", rows[0]["status"])
        self.assertNotIn("private content", json.dumps(rows))
        with mock.patch.object(doctor, "_MAX_JSON", 2):
            rows = []
            self.assertIsNone(doctor._read_json(str(self.project / "host.json"), rows, "file"))
        self.assertEqual("unknown", rows[0]["status"])
        payload = {}
        for _ in range(130):
            payload = {"nested": payload}
        self.write("host.json", payload)
        self.assertEqual("unknown", self.row(self.report(), "configuration.host-json")["status"])

    def test_duplicate_json_members_are_not_silently_healthy(self):
        (self.project / "local.settings.json").write_text(
            '{"IsEncrypted":false,"Values":{"Secret":"private","Secret":"other"}}', encoding="utf-8")
        result = self.report()
        self.assertEqual("fail", self.row(result, "configuration.local-settings")["status"])
        self.assertNotIn("private", json.dumps(result))
        (self.project / "host.json").write_text('{"version":"2.0","extra":NaN}', encoding="utf-8")
        self.assertEqual("fail", self.row(self.report(), "configuration.host-json")["status"])

    def test_settings_shape_encryption_and_absent_storage(self):
        for values in (None, [], {"AzureWebJobsStorage": 12}):
            self.write("local.settings.json", {"IsEncrypted": False, "Values": values})
            self.assertEqual("fail", self.row(self.report(), "configuration.settings-values")["status"])
        self.write("local.settings.json", {"IsEncrypted": True, "Values": {"secret": "encrypted-private"}})
        result = self.report()
        self.assertEqual("unknown", self.row(result, "configuration.settings-encryption")["status"])
        self.assertNotIn("encrypted-private", json.dumps(result))
        self.write("local.settings.json", {"IsEncrypted": False, "Values": {}})
        self.assertEqual("fail", self.row(self.report(), "storage.configuration")["status"])
        self.write("local.settings.json", {"IsEncrypted": False, "Values": {
            "AzureWebJobsStorage__accountName": "private"}})
        self.assertEqual("unknown", self.row(self.report(), "storage.configuration")["status"])

    def test_literal_references_names_only_and_parameter_defaults(self):
        values = dict(_workflow.LOCAL_SETTINGS_JSON["Values"], PRESENT="hidden-value")
        self.write("local.settings.json", {"IsEncrypted": False, "Values": values})
        self.write("parameters.json", {"project": {"type": "String", "value": "hidden-value"}})
        document = _workflow.workflow_json("Stateful")
        document["definition"]["parameters"] = {
            "default": {"type": "String", "defaultValue": "hidden-value"}}
        document["definition"]["actions"]["Compose_greeting"]["inputs"] = [
            "@appsetting('PRESENT')", "@appsetting('ABSENT')", "@parameters('project')",
            "@parameters('default')", "@parameters('missing')"]
        self.write(os.path.join("hello", "workflow.json"), document)
        result = self.report()
        row = self.row(result, "references.workflow.0")
        self.assertEqual("fail", row["status"])
        self.assertEqual(["ABSENT"], row["evidence"]["missingAppSettings"])
        self.assertEqual(["missing"], row["evidence"]["missingParameters"])
        self.assertNotIn("hidden-value", json.dumps(result))

    def test_plain_escaped_composite_and_dynamic_expressions_not_falsely_missing(self):
        for text, expected in (
            ("ordinary appsetting('ABSENT') text", "pass"), ("@@appsetting('ABSENT')", "pass"),
            ("@concat('appsetting(''ABSENT'')', 'literal')", "unknown"),
            ("@{appsetting('ABSENT')}", "unknown"), ("@appsetting(variables('name'))", "unknown"),
                ("@appsetting('A''B')", "unknown"), ("@concat(appsetting('ABSENT'), 'x')", "unknown")):
            with self.subTest(text=text):
                rows = []
                doctor._references(rows, {"input": text}, "ref", {}, set())
                self.assertEqual(expected, rows[0]["status"])
                self.assertEqual([], rows[0]["evidence"]["missingAppSettings"])
        rows = []
        doctor._references(rows, {"input": "@appsetting('present')"}, "ref", {"PRESENT": "value"}, set())
        self.assertEqual("unknown", rows[0]["status"])
        self.assertEqual([], rows[0]["evidence"]["missingAppSettings"])

    def test_connection_and_parameter_value_references(self):
        self.write("parameters.json", {"assigned": {"type": "String", "value": "@appsetting('MISSING')"}})
        self.write("connections.json", {"serviceProviderConnections": {
            "connection": {"parameterValues": {"secret": "@parameters('assigned')",
                                               "other": "@parameters('ABSENT')"}}}})
        result = self.report()
        self.assertEqual(["MISSING"], self.row(result, "references.project-parameters")["evidence"]["missingAppSettings"])
        self.assertEqual(["ABSENT"], self.row(result, "references.connections")["evidence"]["missingParameters"])

    def test_inherited_app_setting_names_are_not_falsely_missing(self):
        document = _workflow.workflow_json("Stateful")
        document["definition"]["actions"]["Compose_greeting"]["inputs"] = "@appsetting('INHERITED')"
        self.write(os.path.join("hello", "workflow.json"), document)
        with mock.patch.dict(os.environ, {"INHERITED": "private-environment-value"}):
            result = self.report()
        self.assertEqual("pass", self.row(result, "references.workflow.0")["status"])
        self.assertNotIn("private-environment-value", json.dumps(result))

    def test_structural_validator_reused_without_secret_bearing_messages(self):
        document = _workflow.workflow_json("Stateful")
        document["definition"]["actions"]["Compose_greeting"]["runAfter"] = {"hidden-value": ["Succeeded"]}
        self.write(os.path.join("hello", "workflow.json"), document)
        result = self.report()
        row = self.row(result, "configuration.workflow.0.structure")
        self.assertEqual(["graph.missing_action"], row["evidence"]["rules"])
        self.assertNotIn("hidden-value", json.dumps(result))

    def test_structure_requires_actions_object_but_allows_empty_actions(self):
        for kind in ("Stateful", "Stateless"):
            for value in ("missing", None, [], {}):
                with self.subTest(kind=kind, actions=value):
                    document = _workflow.workflow_json(kind)
                    if value == "missing":
                        document["definition"].pop("actions")
                    else:
                        document["definition"]["actions"] = value
                    path = self.write(os.path.join("hello", "workflow.json"), document)
                    before = path.read_bytes()
                    row = self.row(self.report(), "configuration.workflow.0.structure")
                    self.assertEqual("pass" if isinstance(value, dict) else "fail", row["status"])
                    self.assertEqual([] if isinstance(value, dict) else ["workflow.actions.invalid"],
                                     row["evidence"]["rules"])
                    self.assertEqual(before, path.read_bytes())
        self.http.assert_not_called()

    def test_cache_matching_range_and_missing_downloads(self):
        (self.root / "cache" / "v1.2.3").mkdir(parents=True)
        manifest = self.root / "cache" / "1.2.3" / "bin" / "extensions.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("{}")
        result = self.report()
        self.assertEqual("pass", self.row(result, "bundle.cache")["status"])
        self.assertEqual(["1.2.3"], self.row(result, "bundle.cache")["evidence"]["versions"])
        host = dict(_workflow.HOST_JSON, extensionBundle={"id": _local.BUNDLE_ID, "version": "[2.*, 3.0.0)"})
        self.write("host.json", host)
        self.assertEqual("unknown", self.row(self.report(), "bundle.cache")["status"])
        host["extensionBundle"]["version"] = "dynamic-hidden-value"
        self.write("host.json", host)
        result = self.report()
        self.assertEqual("unknown", self.row(result, "bundle.cache")["status"])
        self.assertNotIn("dynamic-hidden-value", json.dumps(result))

    def test_bundle_overrides_are_unknown_and_never_scan_the_default_cache(self):
        self.write("host.json", {"version": "2.0", "extensionBundle": {"id": "overridden", "version": "unknown"}})
        values = dict(_workflow.LOCAL_SETTINGS_JSON["Values"],
                      AzureFunctionsJobHost__extensionBundle__downloadPath="private-override")
        self.write("local.settings.json", {"IsEncrypted": False, "Values": values})
        with mock.patch.object(doctor.os, "listdir", wraps=os.listdir) as listing:
            result = self.report()
        self.assertEqual("unknown", self.row(result, "configuration.bundle")["status"])
        self.assertEqual("skipped", self.row(result, "bundle.cache")["status"])
        self.assertNotIn("private-override", json.dumps(result))
        self.assertNotIn(mock.call(str(self.root / "cache")), listing.call_args_list)

    def test_selected_child_paths_and_launcher_specific_node(self):
        func = str(self.root / "func" / "func.cmd")
        azurite = str(self.root / "azurite" / "azurite.cmd")
        node = str(self.root / "func" / "node.exe")
        azurite_node = str(self.root / "azurite" / "node.exe")
        self.patch(_local, "find_tool", side_effect=lambda kind: (
            {"core-tools": func, "azurite": azurite}.get(kind), "path"))
        environments = {func: {"PATH": "HOST-PATH"}, azurite: {"PATH": "AZURITE-PATH"}}
        self.patch(_local, "dependency_environment", side_effect=lambda path: environments[path])
        self.patch(doctor.shutil, "which", side_effect=lambda exe, path: (
            azurite_node if exe == "node" and path == "AZURITE-PATH" else node if exe == "node" else None))
        self.run.side_effect = lambda args, **_kwargs: subprocess.CompletedProcess(args, 0, "v4.15.2\n", "secret-stderr")
        result = self.report()
        self.assertEqual(func, self.row(result, "tools.core-tools")["evidence"]["path"])
        self.assertEqual(node, self.row(result, "tools.node")["evidence"]["path"])
        self.assertEqual(azurite, self.row(result, "tools.azurite")["evidence"]["path"])
        self.assertEqual(azurite_node, self.row(result, "tools.azurite-node")["evidence"]["path"])
        self.assertNotIn("secret-stderr", json.dumps(result))
        for call in self.run.call_args_list:
            self.assertEqual(["--version"], call.args[0][1:])
            self.assertEqual(2, call.kwargs["timeout"])
            self.assertEqual("1", call.kwargs["env"]["DOTNET_CLI_TELEMETRY_OPTOUT"])
            self.assertNotEqual(str(self.project), call.kwargs["cwd"])

    def test_real_child_environment_path_selection_is_not_parent_path(self):
        managed = self.root / "managed"
        for kind, exe in (("core-tools", "func"), ("node", "node"), ("dotnet", "dotnet"), ("azurite", "azurite")):
            directory = managed / _local.managed_subdir(kind)
            directory.mkdir(parents=True)
            tool = directory / (exe + ".CMD" if os.name == "nt" else exe)
            tool.write_text("")
            tool.chmod(0o755)
        with mock.patch.object(_local, "find_tool", wraps=type(self)._find_tool), \
                mock.patch.object(doctor.shutil, "which", wraps=type(self)._which), \
                mock.patch.dict(os.environ, {"PATH": "", "LA_DEPENDENCIES_PATH": str(managed)}):
            self.run.side_effect = lambda args, **_kwargs: subprocess.CompletedProcess(args, 0, "4.15.2", "")
            before = os.environ.copy()
            result = self.report()
            self.assertIn(str(managed / "NodeJs"), self.row(result, "tools.node")["evidence"]["path"])
            self.assertEqual(before, os.environ.copy())

    _find_tool = staticmethod(_local.find_tool)
    _which = staticmethod(shutil.which)

    def test_version_failure_timeout_unknown_output_and_unsupported_major(self):
        for value in (subprocess.TimeoutExpired("tool", 2), OSError("secret-error"),
                      subprocess.CompletedProcess([], 1, "secret-stdout"),
                      subprocess.CompletedProcess([], 0, "secret-stdout")):
            with self.subTest(value=value):
                self.run.side_effect = value if isinstance(value, Exception) else None
                self.run.return_value = value
                version, reason = doctor._probe_version("tool", {"PATH": ""}, 2)
                self.assertIsNone(version)
                self.assertNotIn("secret", reason)
        self.patch(_local, "find_tool", return_value=("tool", "path"))
        self.run.side_effect = None
        self.run.return_value = subprocess.CompletedProcess([], 0, "3.0.0")
        self.assertEqual("fail", self.row(self.report(), "compatibility.functions-major")["status"])
        self.assertEqual((None, "PowerShell-only launcher was not executed."),
                         doctor._probe_version("tool.ps1", {}, 2))

    def test_cloud_missing_and_corrupt_contexts_are_structured_failures(self):
        self.write_context({"active": "cloud", "contexts": {
            "cloud": {"name": "cloud", "target": {"kind": "cloud", "logicAppName": "private-value"}}}})
        for kwargs in ({}, {"context": "cloud"}, {"context": "missing"}):
            result = doctor.doctor_report(**kwargs)
            self.assertEqual(1, result["exitCode"])
            self.assertNotIn("private-value", json.dumps(result))
        (self.root / "contexts.json").write_text("invalid-private-content")
        self.assertEqual(1, doctor.doctor_report()["exitCode"])
        self.assertEqual("pass", self.row(self.report(), "target.local")["status"])
        result = doctor.doctor_report(context="cloud")
        self.assertFalse(result["coverage"]["toolSelection"])
        self.assertFalse(result["coverage"]["localHostInspection"])

    def write_context(self, content):
        (self.root / "contexts.json").write_text(json.dumps(content), encoding="utf-8")

    def test_local_context_port_and_explicit_target_conflicts(self):
        self.write_context({"active": "local", "contexts": {
            "local": {"name": "local", "target": {"kind": "local", "path": str(self.project), "port": 17071}}}})
        result = doctor.doctor_report(context="local")
        self.assertEqual(17071, result["target"]["port"])
        self.assertEqual(str(self.project), result["target"]["projectPath"])
        for kwargs in ({"context": "local", "port": 7071}, {"context": "local", "path": str(self.project)},
                       {"port": 0}, {"probe_timeout": 0}, {"probe_timeout": 11}):
            self.assertEqual(1, doctor.doctor_report(**kwargs)["exitCode"])

    def test_explicit_empty_context_cannot_be_combined_with_explicit_target(self):
        for target in ({"path": str(self.project)}, {"port": 17071},
                       {"path": str(self.project), "port": 17071}):
            with self.subTest(target=target), \
                    mock.patch.object(_context, "get_context", return_value=(None, {})) as select, \
                    mock.patch.object(_local, "find_tool", return_value=(None, "not-found")) as tool:
                result = doctor.doctor_report(context="", **target)
                self.assertEqual(1, result["exitCode"])
                row = self.row(result, "target.local")
                self.assertEqual("fail", row["status"])
                self.assertIn("--context cannot be combined", row["reason"])
                self.assertFalse(result["coverage"]["toolSelection"])
                self.assertFalse(result["coverage"]["localHostInspection"])
                select.assert_not_called()
                tool.assert_not_called()
        self.http.assert_not_called()
        self.run.assert_not_called()

    def test_explicit_empty_context_does_not_select_active_context(self):
        self.write_context({"active": "local", "contexts": {
            "local": {"name": "local", "target": {"kind": "local", "path": str(self.project), "port": 17071}}}})
        before = (self.root / "contexts.json").read_bytes()
        result = doctor.doctor_report(context="")
        self.assertEqual("fail", self.row(result, "target.local")["status"])
        self.assertFalse(result["coverage"]["toolSelection"])
        self.assertEqual(before, (self.root / "contexts.json").read_bytes())
        self.http.assert_not_called()

    def test_storage_endpoint_policy_never_contacts_external_or_ambiguous_urls(self):
        endpoints, reason = doctor._storage_endpoints({"AzureWebJobsStorage": "true"})
        self.assertIsNone(reason)
        self.assertEqual([10000, 10001, 10002], [endpoint[2] for endpoint in endpoints])
        synthetic_credentials = ":".join(("user", "secret"))
        for storage in ("AccountName=private;AccountKey=secret", "UseDevelopmentStorage=true;ProxyUri=http://external",
                        "BlobEndpoint=http://example.com;QueueEndpoint=http://localhost:2;TableEndpoint=http://localhost:3",
                        "BlobEndpoint=http://localhost:1;QueueEndpoint=http://localhost:2;TableEndpoint=http://localhost:3?sig=secret",
                        "BlobEndpoint=http://{}@localhost;QueueEndpoint=http://localhost:2;TableEndpoint=http://localhost:3".format(synthetic_credentials),
                        "UseDevelopmentStorage=true;UseDevelopmentStorage=false",
                        "BlobEndpoint=http://localhost:70000;QueueEndpoint=http://localhost:2;TableEndpoint=http://localhost:3",
                        "BlobEndpoint=https://localhost:1;QueueEndpoint=http://localhost:2;TableEndpoint=http://localhost:3"):
            with self.subTest(storage=storage):
                self.http.reset_mock()
                rows = []
                doctor._storage(rows, {"AzureWebJobsStorage": storage}, 1)
                self.http.assert_not_called()
                self.assertEqual("unknown", rows[0]["status"])
                self.assertNotIn("secret", json.dumps(rows))
        endpoints, reason = doctor._storage_endpoints({"AzureWebJobsStorage":
                                                       "AccountKey=secret;BlobEndpoint=http://localhost:1234/account;"
                                                       "QueueEndpoint=http://127.0.0.1:1235/account;TableEndpoint=http://[::1]:1236/account"})
        self.assertIsNone(reason)
        self.assertEqual([("blob", "127.0.0.1", 1234), ("queue", "127.0.0.1", 1235), ("table", "::1", 1236)], endpoints)

    def test_inherited_storage_used_only_without_ambiguous_project_precedence(self):
        with mock.patch.dict(os.environ, {"AzureWebJobsStorage": "UseDevelopmentStorage=true"}):
            endpoints, reason = doctor._storage_endpoints({})
            self.assertIsNone(reason)
            self.assertEqual(3, len(endpoints))
            self.http.reset_mock()
            rows = []
            doctor._storage(rows, {"AzureWebJobsStorage": "AccountKey=private-different-value"}, 1)
            self.assertEqual("unknown", rows[0]["status"])
            self.http.assert_not_called()
            self.assertNotIn("private-different-value", json.dumps(rows))

    def test_storage_listening_identity_and_occupied_port_are_distinct(self):
        for occupancy, identity, expected in (("free", None, "fail"), ("occupied", None, "unknown"),
                                              ("listening", None, "unknown"), ("listening", "azurite", "pass")):
            with self.subTest(occupancy=occupancy, identity=identity):
                self.patch(doctor, "_port_listening", return_value=occupancy)
                self.http.return_value = {"reachable": True, "httpStatus": 400, "identity": identity, "service": "blob"}
                rows = []
                doctor._storage(rows, _workflow.LOCAL_SETTINGS_JSON["Values"], 2)
                self.assertEqual(expected, self.row({"findings": rows}, "storage.blob")["status"])
                if identity == "azurite":
                    self.assertEqual("fail", self.row({"findings": rows}, "storage.queue")["status"])

    def test_owned_stale_unknown_pid_and_other_project_fail_closed(self):
        self.state.mkdir()
        record_path = Path(_local._record_file(7071))
        record = {"pid": 321, "processCreateTimeUtc": "known", "port": 7071,
                  "projectPath": str(self.project), "secret": "hidden-value"}
        record_path.write_text(json.dumps(record))
        for verified, project, expected in ((True, str(self.project), "pass"),
                                            (False, str(self.project), "unknown"),
                                            (True, str(self.root / "other"), "unknown")):
            with self.subTest(verified=verified, project=project):
                record["projectPath"] = project
                record_path.write_text(json.dumps(record))
                with mock.patch.object(_local, "_record_matches", return_value=verified):
                    result = self.report()
                self.assertEqual(expected, self.row(result, "host.ownership")["status"])
                self.assertNotIn("hidden-value", json.dumps(result))
                self.assertNotIn('"pid"', json.dumps(result))
        record_path.write_text("broken-private")
        result = self.report()
        self.assertEqual("fail", self.row(result, "host.ownership.record")["status"])
        self.assertNotIn("broken-private", json.dumps(result))

    def test_host_requires_live_record_listener_ownership_and_running_state(self):
        self.patch(doctor, "_port_listening", return_value="listening")
        self.patch(doctor, "_ownership", return_value={"pid": 321})
        for owner, state, expected in ((True, "Running", "pass"), (True, "Error", "warn"),
                                       (False, "Running", "unknown"), (True, None, "unknown")):
            with self.subTest(owner=owner, state=state):
                with mock.patch.object(doctor, "_port_owner", return_value=owner):
                    self.http.return_value = {"reachable": True, "httpStatus": 200, "hostState": state}
                    rows = []
                    doctor._host(rows, str(self.project), 7071, 1)
                self.assertEqual(expected, self.row({"findings": rows}, "host.status")["status"])

    def test_listener_owner_rechecks_every_port_holder_identity(self):
        record = {"pid": 123, "childProcesses": [{"pid": 456}]}
        with mock.patch.object(_local, "_record_matches", side_effect=[False, True, True]), \
                mock.patch.object(doctor.psutil, "Process") as process:
            process.return_value.net_connections.return_value = [
                SimpleNamespace(status=psutil.CONN_LISTEN, laddr=SimpleNamespace(port=7071, ip="127.0.0.1"))]
            self.assertTrue(doctor._port_owner(record, 7071))
            process.assert_called_once_with(456)
        with mock.patch.object(_local, "_record_matches", return_value=True), \
                mock.patch.object(doctor.psutil, "Process", side_effect=psutil.AccessDenied(123)):
            self.assertFalse(doctor._port_owner(record, 7071))

    def test_nonloopback_listener_and_identity_recycled_during_probe_are_not_owned(self):
        for address, matches in (("192.0.2.1", [True]), ("127.0.0.1", [True, False])):
            with self.subTest(address=address), \
                    mock.patch.object(_local, "_record_matches", side_effect=matches), \
                    mock.patch.object(doctor.psutil, "Process") as process:
                process.return_value.net_connections.return_value = [
                    SimpleNamespace(status=psutil.CONN_LISTEN, laddr=SimpleNamespace(port=7071, ip=address))]
                self.assertFalse(doctor._port_owner({"pid": 123}, 7071))

    def test_listener_probe_supports_psutil_five_compatibility_api(self):
        owner = SimpleNamespace(connections=mock.Mock(return_value=[
            SimpleNamespace(status=psutil.CONN_LISTEN, laddr=SimpleNamespace(port=7071, ip="127.0.0.1"))]))
        with mock.patch.object(_local, "_record_matches", return_value=True), \
                mock.patch.object(doctor.psutil, "Process", return_value=owner):
            self.assertTrue(doctor._port_owner({"pid": 123}, 7071))
        owner.connections.assert_called_once_with(kind="inet")

    def test_no_state_config_environment_or_process_side_effects(self):
        before = {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        environment = os.environ.copy()
        with mock.patch.object(_local, "_write_record", side_effect=AssertionError("write")), \
                mock.patch.object(_local, "_terminate", side_effect=AssertionError("terminate")), \
                mock.patch.object(_local, "start_runtime", side_effect=AssertionError("start")), \
                mock.patch.object(_context, "save_store", side_effect=AssertionError("context write")):
            self.report()
        self.assertEqual(before, {str(path): path.read_bytes() for path in self.root.rglob("*") if path.is_file()})
        self.assertEqual(environment, os.environ.copy())
        self.assertFalse(self.state.exists())

    def test_exit_zero_two_one_and_strict_optional_semantics(self):
        def known_configuration(rows, _root):
            doctor._finding(rows, "config", "pass", True, "known", "none")
            return {}

        with mock.patch.object(doctor, "_configuration", side_effect=known_configuration), \
                mock.patch.object(doctor, "_storage", return_value=False), \
                mock.patch.object(doctor, "_tools"), mock.patch.object(doctor, "_host"):
            self.assertEqual(0, self.report()["exitCode"])
            for status, required, normal, strict in (("unknown", True, 2, 2), ("fail", True, 1, 1),
                                                     ("warn", False, 0, 2), ("fail", False, 0, 2),
                                                     ("skipped", False, 0, 0)):
                with self.subTest(status=status, required=required):
                    with mock.patch.object(doctor, "_host", side_effect=lambda rows, *_:
                                           doctor._finding(rows, "host", status, required, "reason", "action")):
                        self.assertEqual(normal, self.report()["exitCode"])
                        self.assertEqual(strict, self.report(strict=True)["exitCode"])

    def test_command_exit_hook_is_post_format_and_removes_itself(self):
        events = {}
        cli = SimpleNamespace(
            register_event=lambda event, handler: events.setdefault(event, []).append(handler),
            unregister_event=lambda event, handler: events[event].remove(handler))
        cmd = SimpleNamespace(cli_ctx=cli)
        with mock.patch.object(doctor, "doctor_report", return_value={"exitCode": 2, "findings": []}):
            result = custom.runtime_doctor(cmd, path=str(self.project))
        self.assertEqual(2, result["exitCode"])
        with self.assertRaises(SystemExit) as raised:
            events[EVENT_CLI_SUCCESSFUL_EXECUTE][0](cli, result=result)
        self.assertEqual(2, raised.exception.code)
        self.assertEqual([], events[EVENT_CLI_SUCCESSFUL_EXECUTE])
        self.assertEqual([], events[EVENT_CLI_POST_EXECUTE])
        doctor.finish_doctor_command(cmd, {"exitCode": 1})
        events[EVENT_CLI_POST_EXECUTE][0](cli)
        self.assertEqual([], events[EVENT_CLI_SUCCESSFUL_EXECUTE])

    def test_table_has_actionable_status_not_raw_evidence(self):
        rows = doctor.doctor_table_format(self.report())
        self.assertEqual(["Check", "Status", "Required", "Reason", "Action"], list(rows[0]))
        self.assertNotIn("evidence", rows[0])
        findings = []
        doctor._finding(findings, "ref", "fail", True, "Missing literal names.", "Define them.",
                        missingAppSettings=["SETTING"], missingParameters=["PARAM"])
        doctor._finding(findings, "tool", "pass", True, "Version read.", "No action.",
                        path="selected-tool", version="4.15.2")
        rows = doctor.doctor_table_format({"findings": findings})
        self.assertIn("SETTING", rows[0]["Reason"])
        self.assertIn("PARAM", rows[0]["Reason"])
        self.assertIn("selected-tool", rows[1]["Reason"])
        self.assertIn("4.15.2", rows[1]["Reason"])


class LocalProbeTests(unittest.TestCase):
    def test_invalid_host_receipts_never_establish_running(self):
        bodies = (
            b'{"state":"Error","state":"Running"}',
            b'{"state":"Running","state":"Error"}',
            b'{"state":"Running","ignored":{"duplicate":1,"duplicate":2}}',
            b'{"state":"Running","ignored":NaN}',
            b'{"state":"Running","ignored":Infinity}',
            b'{"state":"Running","ignored":-Infinity}',
            b'{"state":"Running","ignored":1e999}',
            b'{"state":"Running","ignored":-1e999}',
            b'{"state":"Running","ignored":"\xff"}',
            b'{"state":"Running"',
        )
        for body in bodies:
            with self.subTest(body=body):
                response = BytesIO(body)
                response.code = 200
                response.headers = {}
                with mock.patch.object(doctor, "build_opener") as opener, \
                        mock.patch.object(doctor.time, "monotonic", return_value=100):
                    opener.return_value.open.return_value = response
                    result = doctor._http_probe("http://127.0.0.1:17071/admin/host/status", 2, host=True)
                self.assertTrue(result["reachable"])
                self.assertEqual(200, result["httpStatus"])
                self.assertIsNone(result["hostState"])
                self.assertEqual({"reachable", "httpStatus", "identity", "service", "hostState"}, set(result))

    def test_valid_finite_host_receipts_preserve_recognized_states_and_status_gate(self):
        for status in (200, 503):
            for state in ("Running", "Starting", "Error", "Offline"):
                with self.subTest(status=status, state=state):
                    response = BytesIO(json.dumps({"state": state, "ignored": 1.25}).encode())
                    response.code = status
                    response.headers = {}
                    with mock.patch.object(doctor, "build_opener") as opener, \
                            mock.patch.object(doctor.time, "monotonic", return_value=100):
                        opener.return_value.open.return_value = response
                        result = doctor._http_probe("http://127.0.0.1:17071/admin/host/status", 2, host=True)
                    self.assertTrue(result["reachable"])
                    self.assertEqual(status, result["httpStatus"])
                    self.assertEqual(state if status == 200 else None, result["hostState"])

    def test_authored_numeric_overflow_uses_the_same_strict_decoder(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "host.json"
            for number in ("1e999", "-1e999"):
                with self.subTest(number=number):
                    path.write_text('{"version":"2.0","ignored":' + number + "}", encoding="utf-8")
                    before = path.read_bytes()
                    rows = []
                    self.assertIsNone(doctor._read_json(str(path), rows, "test"))
                    self.assertEqual("fail", rows[0]["status"])
                    self.assertEqual(before, path.read_bytes())

    def server(self, behavior):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                behavior(self)

            def log_message(self, *_args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server

    def test_real_port_free_bound_and_listening(self):
        with socket.socket() as bound:
            bound.bind(("127.0.0.1", 0))
            port = bound.getsockname()[1]
            self.assertEqual("occupied", doctor._port_listening("127.0.0.1", port, 1))
            bound.listen()
            self.assertEqual("listening", doctor._port_listening("127.0.0.1", port, 1))
        self.assertEqual("free", doctor._port_listening("127.0.0.1", port, 1))

    def test_real_http_error_banner_and_upstream_secrets_are_not_echoed(self):
        def behavior(handler):
            handler.send_response(400)
            handler.send_header("Server", "Azurite-Blob/3.35.0")
            handler.end_headers()
            handler.wfile.write(b"private-upstream")

        server = self.server(behavior)
        # BaseHTTPRequestHandler adds its own Server header; emulate Azurite's single header.
        with mock.patch.object(BaseHTTPRequestHandler, "send_response", BaseHTTPRequestHandler.send_response_only):
            result = doctor._http_probe("http://127.0.0.1:{}/".format(server.server_port), 1)
        self.assertTrue(result["reachable"])
        self.assertEqual("azurite", result["identity"])
        self.assertEqual("blob", result["service"])
        self.assertEqual(400, result["httpStatus"])
        self.assertNotIn("private-upstream", json.dumps(result))

    def test_redirect_and_proxy_are_not_followed(self):
        def behavior(handler):
            handler.send_response(302)
            handler.send_header("Location", "http://external.invalid/?sig=private")
            handler.end_headers()

        server = self.server(behavior)
        with mock.patch.dict(os.environ, {"http_proxy": "http://external.invalid:9999", "no_proxy": ""}):
            result = doctor._http_probe("http://127.0.0.1:{}/".format(server.server_port), 1)
        self.assertEqual(302, result["httpStatus"])
        self.assertIsNone(result["identity"])
        self.assertNotIn("private", json.dumps(result))

    def test_host_body_only_returns_recognized_enum(self):
        def behavior(handler):
            handler.send_response(200)
            handler.end_headers()
            handler.wfile.write(b'{"state":"Running","masterKey":"private"}')

        server = self.server(behavior)
        result = doctor._http_probe("http://127.0.0.1:{}/".format(server.server_port), 1, host=True)
        self.assertEqual("Running", result["hostState"])
        self.assertNotIn("private", json.dumps(result))

    def test_unsuccessful_http_status_cannot_report_running_host(self):
        for status in (401, 403, 500, 503):
            with self.subTest(status=status):
                def behavior(handler):
                    handler.send_response(status)
                    handler.end_headers()
                    handler.wfile.write(b'{"state":"Running","secret":"private"}')

                server = self.server(behavior)
                result = doctor._http_probe(
                    "http://127.0.0.1:{}/".format(server.server_port), 1, host=True)
                self.assertEqual(status, result["httpStatus"])
                self.assertIsNone(result["hostState"])
                self.assertNotIn("private", json.dumps(result))

    def test_trickled_body_is_bounded_before_buffering_and_cannot_report_running(self):
        body = b'{"state":"Running","secret":"private-padding"}'
        finished = threading.Event()
        stop = threading.Event()
        self.addCleanup(stop.set)

        def behavior(handler):
            handler.connection.settimeout(0.5)
            handler.send_response(200)
            handler.send_header("Content-Length", str(len(body)))
            handler.end_headers()
            try:
                for byte in body:
                    handler.wfile.write(bytes([byte]))
                    handler.wfile.flush()
                    if stop.wait(0.08):
                        break
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
            finally:
                finished.set()

        server = self.server(behavior)
        started = time.monotonic()
        result = doctor._http_probe("http://127.0.0.1:{}/".format(server.server_port), 1, host=True)
        elapsed = time.monotonic() - started
        stop.set()
        self.assertGreater(elapsed, 0.8)
        self.assertLess(elapsed, 1.8)
        self.assertTrue(result["reachable"])
        self.assertEqual(200, result["httpStatus"])
        self.assertIsNone(result["hostState"])
        self.assertNotIn("private", json.dumps(result))
        self.assertTrue(finished.wait(2))

    def test_trickled_headers_share_the_same_probe_budget(self):
        finished = threading.Event()
        stop = threading.Event()
        self.addCleanup(stop.set)

        def behavior(handler):
            handler.connection.settimeout(0.5)
            try:
                for byte in b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\n{}":
                    handler.wfile.write(bytes([byte]))
                    handler.wfile.flush()
                    if stop.wait(0.08):
                        break
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
            finally:
                finished.set()

        server = self.server(behavior)
        started = time.monotonic()
        result = doctor._http_probe("http://127.0.0.1:{}/".format(server.server_port), 1, host=True)
        stop.set()
        self.assertGreater(time.monotonic() - started, 0.8)
        self.assertLess(time.monotonic() - started, 1.8)
        self.assertFalse(result["reachable"])
        self.assertIsNone(result["hostState"])
        self.assertTrue(finished.wait(2))

    def test_transport_failure_has_no_exception_or_response_dump(self):
        with mock.patch.object(doctor, "build_opener") as opener:
            opener.return_value.open.side_effect = OSError("private")
            result = doctor._http_probe("http://127.0.0.1:1/", 1)
        self.assertFalse(result["reachable"])
        self.assertNotIn("private", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
