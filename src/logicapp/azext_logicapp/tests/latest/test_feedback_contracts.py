# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Cross-command contracts reported during maintainer review."""

import ast
import json
import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, ValidationError
from requests import Response

from azext_logicapp import _context, _runtime_client, _test_report, _testing, _workflow, custom


class FeedbackTargetContracts(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.local = {"target": {"kind": "local", "path": str(self.root), "port": 7079}}
        self.cloud = {"target": {"kind": "cloud", "resourceGroup": "rg", "logicAppName": "app"}}

    def test_explicit_cloud_authoring_never_falls_back_or_reads_secrets(self):
        with patch.object(custom, "get_context", return_value=(self.cloud, {})), \
                patch.object(custom, "create_workflow_file") as create, \
                patch.object(custom, "create_local_connection") as connect, \
                patch.object(custom, "_read_secret_from_stdin") as secret:
            for path in (None, str(self.root)):
                with self.subTest(path=path):
                    with self.assertRaises(MutuallyExclusiveArgumentError):
                        custom.workflow_create(None, path=path, workflow="hello", context="cloud")
                    with self.assertRaises(MutuallyExclusiveArgumentError):
                        custom.connection_create(None, "conn", "serviceBus", path=path,
                                                 context="cloud", secret="setting")
            create.assert_not_called()
            connect.assert_not_called()
            secret.assert_not_called()
        self.assertEqual([], list(self.root.iterdir()))

    def test_cloud_validation_can_use_explicit_authored_path_without_local_fallback(self):
        with patch.object(custom, "get_context", return_value=(self.cloud, {})) as select:
            self.assertEqual(str(self.root), custom._project_path_from_context(
                str(self.root), "cloud", allow_cloud=True))
            select.assert_called_once_with("cloud")
            with self.assertRaises(MutuallyExclusiveArgumentError):
                custom._project_path_from_context(None, "cloud", allow_cloud=True)

    def test_local_authoring_uses_named_or_active_target_and_explicit_path_wins(self):
        with patch.object(custom, "get_context", return_value=(self.local, {})):
            self.assertEqual(str(self.root), custom._project_path_from_context(None, "local"))
            self.assertEqual(str(self.root), custom._project_path_from_context(None, None))
            other = str(self.root / "other")
            self.assertEqual(other, custom._project_path_from_context(other, "local"))
        with patch.object(custom, "get_context", side_effect=AssertionError("Explicit path needs no active target")):
            self.assertEqual(str(self.root), custom._project_path_from_context(str(self.root), None))

    def test_explicit_empty_named_context_is_not_omission(self):
        with patch.object(_context, "load_store", return_value={"active": None, "contexts": {}}), \
                patch.object(custom, "build_runtime_client") as client:
            with self.assertRaises(ValidationError):
                custom._project_path_from_context(str(self.root), "")
            with self.assertRaises(ValidationError):
                custom._client_from_target(None, context="")
            client.assert_not_called()

    def test_lifecycle_saved_port_explicit_override_and_default(self):
        for context, expected in ((self.local, 7079), (None, 7071)):
            with self.subTest(context=context), \
                    patch.object(custom, "get_context", return_value=(context, {})), \
                    patch.object(custom, "start_runtime") as start, \
                    patch.object(custom, "show_runtime") as show, \
                    patch.object(custom, "stop_runtime") as stop:
                custom.runtime_start(None)
                custom.runtime_show(None)
                custom.runtime_stop(None)
                for seam in (start, show, stop):
                    self.assertEqual(expected, seam.call_args.kwargs["port"])
                custom.runtime_start(None, port=7081)
                self.assertEqual(7081, start.call_args.kwargs["port"])
                if context:
                    self.assertEqual(str(self.root), start.call_args.args[1])
                custom.runtime_show(None, port=7071)
                custom.runtime_stop(None, port=7071)
                self.assertEqual(7071, show.call_args.kwargs["port"])
                self.assertEqual(7071, stop.call_args.kwargs["port"])

    def test_active_cloud_refuses_bare_lifecycle_but_explicit_port_and_all_stop_are_scoped(self):
        with patch.object(custom, "get_context", return_value=(self.cloud, {})), \
                patch.object(custom, "start_runtime") as start, \
                patch.object(custom, "show_runtime") as show, \
                patch.object(custom, "stop_runtime") as stop:
            for operation in (custom.runtime_start, custom.runtime_show, custom.runtime_stop):
                with self.assertRaises(MutuallyExclusiveArgumentError):
                    operation(None)
            start.assert_not_called()
            show.assert_not_called()
            stop.assert_not_called()
            custom.runtime_start(None, path=str(self.root))
            self.assertEqual(7071, start.call_args.kwargs["port"])
            custom.runtime_show(None, port=7081)
            custom.runtime_stop(None, port=7081)
            self.assertEqual(7081, stop.call_args.kwargs["port"])
            custom.runtime_stop(None, all=True)
            stop.assert_called_with(port=None, all_records=True)

    def test_real_config_resolver_is_profile_isolated_in_independent_processes(self):
        script = """
import json
from azext_logicapp import _context, custom
import sys
if len(sys.argv) > 1:
    _context.create_context(sys.argv[1], path=sys.argv[2], port=7079, use=True)
context, _ = _context.get_context()
print(json.dumps({'store': _context.store_path(), 'data': _context.load_store(),
                  'project': custom._project_path_from_context(None, None),
                  'plan': custom.test_plan(None, workflow='Orders') if context else None}))
"""
        home = self.root / "home"
        home.mkdir()
        legacy = home / ".azure" / "logicapp" / "contexts.json"
        legacy.parent.mkdir(parents=True)
        sentinel = b'{"active":null,"contexts":{},"future":"preserved"}'
        legacy.write_bytes(sentinel)
        source = Path(_context.__file__).resolve().parent.parent
        environment = dict(os.environ, HOME=str(home), USERPROFILE=str(home),
                           PYTHONPATH=str(source), PYTHONDONTWRITEBYTECODE="1")
        profiles = [self.root / "a", self.root / "b"]
        for index, profile in enumerate(profiles):
            env = dict(environment, AZURE_CONFIG_DIR=str(profile))
            result = subprocess.run([sys.executable, "-c", script], env=env,
                                    cwd=str(self.root), capture_output=True, text=True, check=True)
            value = json.loads(result.stdout)
            self.assertEqual(str(profile / "logicapp" / "contexts.json"), value["store"])
            self.assertEqual({"active": None, "contexts": {}}, value["data"])
            self.assertEqual(str(self.root), value["project"])
            self.assertIsNone(value["plan"])
            self.assertFalse((profile / "logicapp").exists())
            project = self.root / ("App" + str(index))
            (project / "Orders").mkdir(parents=True)
            kind = "Stateful" if index == 0 else "Stateless"
            (project / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
            (project / "Orders" / "workflow.json").write_text(
                json.dumps(_workflow.workflow_json(kind)), encoding="utf-8")
            before = {str(path): path.read_bytes() for path in project.rglob("*") if path.is_file()}
            result = subprocess.run([sys.executable, "-c", script, "local-" + str(index), str(project)],
                                    env=env, cwd=str(self.root), capture_output=True, text=True, check=True)
            value = json.loads(result.stdout)
            self.assertEqual("local-" + str(index), value["data"]["active"])
            self.assertEqual(["local-" + str(index)], list(value["data"]["contexts"]))
            self.assertEqual(str(project), value["project"])
            self.assertEqual(kind, value["plan"]["workflow"]["kind"])
            self.assertEqual(0, value["plan"]["exitCode"])
            self.assertEqual("notExecuted", value["plan"]["businessTests"])
            self.assertEqual("blocked", value["plan"]["gates"]["sdkExecution"])
            self.assertEqual(before, {str(path): path.read_bytes() for path in project.rglob("*") if path.is_file()})
        self.assertEqual(sentinel, legacy.read_bytes())
        environment.pop("AZURE_CONFIG_DIR", None)
        result = subprocess.run([sys.executable, "-c", script], env=environment, cwd=str(self.root),
                                capture_output=True, text=True, check=True)
        self.assertEqual(str(legacy), json.loads(result.stdout)["store"])
        self.assertEqual(sentinel, legacy.read_bytes())


class FeedbackValidationContracts(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        (self.root / "hello").mkdir()
        (self.root / "hello" / "workflow.json").write_text(
            json.dumps(_workflow.workflow_json("Stateful")), encoding="utf-8")

    def validate(self, client):
        with patch.object(custom, "_client_from_target", return_value=(client, {})):
            return custom.workflow_validate(None, path=str(self.root), workflow="hello", with_runtime=True)

    def test_only_completed_receipts_claim_runtime_template_coverage(self):
        for target in ("http://localhost:17071", "/subscriptions/s/resourceGroups/r/providers/Microsoft.Web/sites/a"):
            client = _runtime_client.SiteRuntimeClient(Mock(), target)
            for status, raw, valid in ((200, b"", True), (200, b"{}", True), (204, b"", True),
                                       (202, b"", False), (201, b"{}", False),
                                       (200, b'{"error":{}}', False), (200, b"[]", False),
                                       (200, b'{"a":1,"a":2}', False), (200, b'{"a":1e999}', False)):
                with self.subTest(target=target, status=status, raw=raw):
                    response = Response()
                    response.status_code = status
                    response._content = raw
                    with patch.object(client, "_send", return_value=response) as send:
                        if valid:
                            self.assertTrue(self.validate(client)["coverage"]["checks"]["runtimeTemplate"])
                        else:
                            with self.assertRaises(ValidationError) as caught:
                                self.validate(client)
                            report = json.loads(str(caught.exception))
                            self.assertFalse(report["valid"])
                            self.assertFalse(report["coverage"]["checks"]["runtimeTemplate"])
                        send.assert_called_once()

    def test_missing_or_untyped_receipts_never_claim_completion(self):
        for receipt in (None, {}, {"statusCode": 200}, {"payload": None},
                        {"statusCode": 200.0, "payload": None}, {"statusCode": True, "payload": None}):
            with self.subTest(receipt=receipt):
                client = Mock()
                client.post_with_receipt.return_value = receipt
                with self.assertRaises(ValidationError):
                    self.validate(client)
                client.post.assert_not_called()

    def test_partial_multi_workflow_completion_is_not_full_template_coverage(self):
        (self.root / "other").mkdir()
        (self.root / "other" / "workflow.json").write_text(
            json.dumps(_workflow.workflow_json("Stateful")), encoding="utf-8")
        client = Mock()
        client.post_with_receipt.side_effect = [
            {"statusCode": 200, "payload": None}, {"statusCode": 202, "payload": None}]
        with patch.object(custom, "_client_from_target", return_value=(client, {})):
            with self.assertRaises(ValidationError) as caught:
                custom.workflow_validate(None, path=str(self.root), all=True, with_runtime=True)
        report = json.loads(str(caught.exception))
        self.assertFalse(report["coverage"]["checks"]["runtimeTemplate"])
        self.assertFalse(report["valid"])
        self.assertEqual(2, client.post_with_receipt.call_count)

    def test_new_policy_preserves_supported_v1_reports_without_reinterpreting_historical_exits(self):
        (self.root / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        report = _testing.plan_report(str(self.root), "hello")
        self.assertEqual(0, report["exitCode"])
        self.assertTrue(_test_report.validate_report(report))
        legacy = copy.deepcopy(report)
        legacy["schemaVersion"] = "1.0"
        del legacy["exitPolicy"]
        _test_report.finalize(legacy)
        for version in ("0.1.17", "0.1.18", "0.1.19", "0.1.20", "0.1.21", "1.0.0b1"):
            with self.subTest(version=version):
                earlier = copy.deepcopy(legacy)
                earlier["provenance"]["cliVersion"] = version
                self.assertTrue(_test_report.validate_report(earlier))
                self.assertEqual("notExecuted", earlier["executionState"])
                self.assertEqual(4, earlier["exitCode"])
        for version in ("0.1.22", "0.1.23", "0.1.24", "0.1.25", "0.1.26", "1.0.0b1"):
            for policy in ("planning", "strict"):
                with self.subTest(version=version, policy=policy):
                    earlier = copy.deepcopy(report)
                    earlier["provenance"]["cliVersion"] = version
                    earlier["exitPolicy"] = policy
                    _test_report.finalize(earlier)
                    original = copy.deepcopy(earlier)
                    self.assertTrue(_test_report.validate_report(earlier))
                    self.assertEqual(original, earlier)
                    self.assertEqual(0 if policy == "planning" else 4, earlier["exitCode"])
        for version in ("unknown", "99.0.0", None, [], {}):
            invalid = copy.deepcopy(report)
            invalid["provenance"]["cliVersion"] = version
            self.assertFalse(_test_report.validate_report(invalid))
        for change in ({"producer": "nativeSDK"}, {"extra": "untrusted"}):
            invalid = copy.deepcopy(report)
            invalid["provenance"].update(change)
            self.assertFalse(_test_report.validate_report(invalid))

    def test_known_public_reports_survive_a_later_package_version(self):
        module = ast.parse(Path(_test_report.__file__).read_text(encoding="utf-8"))
        version = next(node for node in module.body if isinstance(node, ast.Assign)
                       and any(isinstance(target, ast.Name) and target.id == "VERSION" for target in node.targets))
        version.value = ast.copy_location(ast.Constant(value="1.0.0b3"), version.value)
        namespace = {}
        exec(compile(module, "<future-report-producer>", "exec"), namespace)
        (self.root / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        report = _testing.plan_report(str(self.root), "hello")
        for schema, producers in (("1.0", ("1.0.0b1",)),
                                  ("2.0", ("0.1.22", "0.1.23", "0.1.24", "0.1.25", "0.1.26", "1.0.0b1"))):
            for producer in producers:
                with self.subTest(schema=schema, producer=producer):
                    saved = copy.deepcopy(report)
                    saved["schemaVersion"] = schema
                    saved["provenance"]["cliVersion"] = producer
                    if schema == "1.0":
                        del saved["exitPolicy"]
                    _test_report.finalize(saved)
                    original = copy.deepcopy(saved)
                    self.assertTrue(namespace["validate_report"](saved))
                    self.assertEqual(original, saved)
        source = _testing.plan_report(str(self.root), "")
        for schema, legacy in (("1.0", True), ("2.0", True), ("2.0", False)):
            saved = copy.deepcopy(source)
            saved["schemaVersion"] = schema
            saved["provenance"]["cliVersion"] = "1.0.0b1"
            if schema == "1.0":
                del saved["exitPolicy"]
            if legacy:
                row = next(item for item in saved["findings"] if item["rule"] == "input.options")
                row["message"] = "Explicit local paths and a bounded workflow name are required."
                row["recommendation"] = (
                    "Supply --path and --workflow; do not use URLs, device paths or target contexts.")
            _test_report.finalize(saved)
            with self.subTest(schema=schema, legacy=legacy):
                self.assertTrue(namespace["validate_report"](saved))
                saved["provenance"]["cliVersion"] = "1.0.0b3"
                self.assertEqual(schema == "2.0" and not legacy, namespace["validate_report"](saved))

        for schema, legacy in (("1.0", True), ("2.0", True), ("2.0", False)):
            saved = copy.deepcopy(report)
            saved["schemaVersion"] = schema
            saved["provenance"]["cliVersion"] = "1.0.0b1"
            if schema == "1.0":
                del saved["exitPolicy"]
            saved["findings"].append(_test_report.finding(
                "report.invalid", producer_version="1.0.0b1" if legacy else None))
            _test_report.finalize(saved)
            with self.subTest(schema=schema, legacy=legacy, rule="report.invalid"):
                self.assertTrue(namespace["validate_report"](saved))
                saved["provenance"]["cliVersion"] = "1.0.0b3"
                self.assertEqual(schema == "2.0" and not legacy, namespace["validate_report"](saved))

    def test_sdk_era_foundation_producers_retain_exact_error_catalogs_and_blocked_gates(self):
        (self.root / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        for version in ("0.1.25", "0.1.26", _test_report.VERSION):
            with self.subTest(version=version):
                report = _testing.plan_report(str(self.root), "hello")
                report["provenance"]["cliVersion"] = version
                finding = _test_report.finding(
                    "report.invalid", producer_version=None if version == _test_report.VERSION else version)
                self.assertIn("sanitized native test report", finding["message"])
                report["findings"].append(finding)
                _test_report.finalize(report)
                self.assertTrue(_test_report.validate_report(report))
                self.assertEqual("blocked", report["gates"]["sdkExecution"])
                self.assertEqual(0, report["summary"]["executed"])
